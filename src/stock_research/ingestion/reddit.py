"""Reddit sentiment ingestion via Google search scraping.

Scrapes Google for Reddit posts mentioning a ticker across key investing
subreddits, then applies keyword-based sentiment classification.

Uses httpx (async) with retry and 2-second delay between Google requests
to avoid rate limiting.

Usage:
    python -m stock_research.ingestion.reddit AAPL
"""

from __future__ import annotations

import asyncio
import logging
import re
import sys
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

_GENERAL_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "StockMarket", "options"]
_MAX_RESULTS_PER_SUBREDDIT = 5

# Common patterns for ticker-dedicated subreddits.
# Checked via Google search; only subreddits that return results are used.
_DEDICATED_SUB_PATTERNS = [
    "{ticker}",            # r/CRWV, r/NVDA
    "{ticker}_Stock",      # r/CRWV_Stock
    "{ticker}stock",       # r/CRWVstock, r/VRTstock
    "{ticker}Discussion",  # r/CRWVDiscussion
    "{ticker}_investors",  # r/TSLA_investors
]
_REQUEST_TIMEOUT = 15
_RETRY_ATTEMPTS = 3
_RETRY_BACKOFF_BASE = 2.0  # exponential: 2, 4, 8 seconds
_GOOGLE_DELAY = 2.0  # seconds between Google requests

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_POSITIVE_KEYWORDS = [
    "moon", "rocket", "bullish", "calls", "buy", "long",
    "tendies", "gains", "breakout", "rally", "pump",
    "undervalued", "gem", "opportunity", "strong", "beat",
    "upgrade", "upside", "growth", "accumulate",
]

_NEGATIVE_KEYWORDS = [
    "crash", "dump", "puts", "sell", "short", "bearish",
    "overvalued", "bubble", "bagholding", "loss", "down",
    "warning", "concern", "risk", "avoid", "miss",
    "downgrade", "downside", "decline", "red",
]


def fetch_reddit_posts(
    ticker: str,
    days: int = 30,
    extra_subreddits: list[str] | None = None,
) -> list[dict]:
    """Fetch Reddit posts mentioning *ticker* from the last *days* days.

    Searches both general investing subreddits AND ticker-dedicated subreddits
    (e.g., r/CRWV, r/CRWV_Stock, r/CRWVstock for CRWV).

    Args:
        ticker: Stock ticker symbol.
        days: Lookback window in days.
        extra_subreddits: Additional subreddits from tickers.yaml config.

    Returns a list of dicts matching the ``sentiment_observations`` DuckDB schema.
    """
    return asyncio.run(_fetch_all(ticker.upper(), days, extra_subreddits or []))


def discover_dedicated_subreddits(ticker: str) -> list[str]:
    """Generate candidate dedicated subreddit names for a ticker.

    Returns candidate names like ['CRWV', 'CRWV_Stock', 'CRWVstock', ...].
    Actual existence is verified during search (Google returns 0 results
    for non-existent subreddits).
    """
    candidates = []
    for pattern in _DEDICATED_SUB_PATTERNS:
        candidates.append(pattern.format(ticker=ticker.upper()))
    return candidates


async def _fetch_all(
    ticker: str, days: int, extra_subreddits: list[str]
) -> list[dict]:
    """Async coordinator: search general + dedicated + extra subreddits."""
    try:
        import httpx  # noqa: F811
    except ImportError:
        raise ImportError(
            "httpx is required for Reddit ingestion. "
            "Install it with: pip install httpx"
        )

    # Build the full subreddit list: general + dedicated + config extras
    dedicated = discover_dedicated_subreddits(ticker)
    all_subs = list(_GENERAL_SUBREDDITS) + dedicated
    if extra_subreddits:
        all_subs.extend(extra_subreddits)
    # Deduplicate while preserving order
    seen: set[str] = set()
    subreddits: list[str] = []
    for s in all_subs:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            subreddits.append(s)

    logger.info(
        "Searching %d subreddits for %s: %s",
        len(subreddits), ticker,
        ", ".join(f"r/{s}" for s in subreddits),
    )

    posts: list[dict] = []
    errors: list[str] = []

    async with httpx.AsyncClient(
        timeout=_REQUEST_TIMEOUT,
        headers={"User-Agent": _USER_AGENT},
        follow_redirects=True,
    ) as client:
        for i, subreddit in enumerate(subreddits):
            if i > 0:
                await asyncio.sleep(_GOOGLE_DELAY)
            try:
                sub_posts = await _search_subreddit(client, ticker, subreddit, days)
                if sub_posts:
                    logger.info(
                        "  r/%s: %d posts found", subreddit, len(sub_posts)
                    )
                posts.extend(sub_posts)
            except Exception as exc:
                logger.warning("Failed to search r/%s for %s: %s", subreddit, ticker, exc)
                errors.append(f"r/{subreddit}: {exc}")

    if errors and not posts:
        logger.warning("All subreddit searches failed: %s", "; ".join(errors))

    return posts


async def _search_subreddit(
    client,  # httpx.AsyncClient
    ticker: str,
    subreddit: str,
    days: int,
) -> list[dict]:
    """Scrape Google for ``site:reddit.com/r/{sub} {ticker}`` and parse results.

    Retries up to 3 times with exponential backoff on transient failures.
    """
    query = f"site:reddit.com/r/{subreddit} {ticker}"
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:m"

    # tbs=qdr:m limits results to last month. For custom days:
    if days <= 7:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:w"
    elif days <= 1:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:d"

    resp = await _get_with_retry(client, search_url)
    return _parse_google_results(resp.text, ticker, subreddit)


async def _get_with_retry(client, url: str, attempts: int = _RETRY_ATTEMPTS):
    """HTTP GET with exponential backoff retry."""
    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            if attempt < attempts - 1:
                delay = _RETRY_BACKOFF_BASE ** (attempt + 1)
                logger.debug(
                    "Retry %d/%d for %s after %.1fs: %s",
                    attempt + 1, attempts, url, delay, exc,
                )
                await asyncio.sleep(delay)
    raise RuntimeError(f"All {attempts} attempts failed for {url}: {last_exc}")


def _parse_google_results(html: str, ticker: str, subreddit: str) -> list[dict]:
    """Parse Google search result HTML into sentiment observation dicts."""
    try:
        from bs4 import BeautifulSoup  # noqa: F811
    except ImportError:
        raise ImportError(
            "beautifulsoup4 is required for Reddit ingestion. "
            "Install it with: pip install beautifulsoup4"
        )

    soup = BeautifulSoup(html, "html.parser")
    posts: list[dict] = []
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    for result in soup.select("div.g")[:_MAX_RESULTS_PER_SUBREDDIT]:
        try:
            link_elem = result.select_one("a")
            if not link_elem:
                continue
            url = link_elem.get("href", "")
            if "reddit.com" not in url:
                continue

            title_elem = result.select_one("h3")
            title = title_elem.text.strip() if title_elem else ""

            snippet_elem = result.select_one("div.VwiC3b")
            snippet = snippet_elem.text.strip() if snippet_elem else ""

            direction, strength = _classify_sentiment(title, snippet)

            posts.append({
                "ticker": ticker,
                "source": "reddit",
                "platform": "reddit",
                "subreddit": subreddit,
                "title": title,
                "snippet": snippet[:500],  # truncate long snippets
                "url": url,
                "sentiment_direction": direction,
                "sentiment_strength": strength,
                "observed_at": now_iso,
                "source_type": "social_media",
                "updated_at": now_iso,
            })
        except Exception as parse_err:
            logger.debug("Failed to parse search result: %s", parse_err)
            continue

    return posts


def _classify_sentiment(title: str, snippet: str) -> tuple[str, float]:
    """Keyword-based sentiment classification.

    Returns:
        (direction, strength) where direction is 'bullish', 'bearish', or
        'neutral', and strength is a float in [0.0, 1.0].
    """
    text = f"{title} {snippet}".lower()

    pos = sum(1 for kw in _POSITIVE_KEYWORDS if kw in text)
    neg = sum(1 for kw in _NEGATIVE_KEYWORDS if kw in text)
    total = pos + neg

    if total == 0:
        return "neutral", 0.0

    if pos > neg:
        return "bullish", min(1.0, pos / max(total, 1))
    elif neg > pos:
        return "bearish", min(1.0, neg / max(total, 1))
    else:
        return "neutral", 0.5


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m stock_research.ingestion.reddit TICKER", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1].upper()

    try:
        posts = fetch_reddit_posts(ticker, days=30)
    except ImportError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    print(f"Fetched {len(posts)} Reddit posts for {ticker}")
    for post in posts:
        print(
            f"  [{post['sentiment_direction']:>7s} {post['sentiment_strength']:.2f}] "
            f"r/{post['subreddit']:15s} {post['title'][:60]}"
        )
