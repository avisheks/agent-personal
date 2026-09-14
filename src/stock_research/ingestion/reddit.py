"""Reddit sentiment ingestion via multi-engine search fallback.

Searches for Reddit posts mentioning a ticker across key investing
subreddits using a three-engine fallback strategy:
  1. DuckDuckGo HTML (primary — less aggressive rate limiting)
  2. Reddit JSON API (direct — most reliable, occasional 429s)
  3. Google search (last resort — frequently CAPTCHAd)

Then applies keyword-based sentiment classification.

Uses httpx (async) with retry and delays between requests to avoid
rate limiting.

Usage:
    python -m stock_research.ingestion.reddit AAPL
"""

from __future__ import annotations

import asyncio
import json
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
# Checked via search; only subreddits that return results are used.
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
_SEARCH_DELAY = 2.0  # seconds between search requests

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Reddit JSON API needs a descriptive but non-bot User-Agent
_REDDIT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "StockResearchApp/1.0"
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

# Engine names for logging
_ENGINE_RSS = "reddit_rss"
_ENGINE_DDG = "duckduckgo"
_ENGINE_REDDIT = "reddit_api"
_ENGINE_GOOGLE = "google"


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
    Actual existence is verified during search (search engines return 0 results
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
                await asyncio.sleep(_SEARCH_DELAY)
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
    """Search a subreddit for ticker mentions using multi-engine fallback.

    Tries engines in order: Reddit RSS -> DuckDuckGo -> Reddit JSON API -> Google.
    Returns results from the first engine that produces non-empty results.
    RSS is the most reliable — no CAPTCHA, no rate-limit issues for low-volume.
    """
    engines = [
        (_ENGINE_RSS, _search_subreddit_rss),
        (_ENGINE_DDG, _search_subreddit_ddg),
        (_ENGINE_REDDIT, _search_subreddit_reddit_api),
        (_ENGINE_GOOGLE, _search_subreddit_google),
    ]

    last_exc: Optional[Exception] = None
    for engine_name, engine_func in engines:
        try:
            results = await engine_func(client, ticker, subreddit, days)
            if results:
                logger.info(
                    "  r/%s: engine=%s returned %d results",
                    subreddit, engine_name, len(results),
                )
                return results
            else:
                logger.debug(
                    "  r/%s: engine=%s returned 0 results, trying next",
                    subreddit, engine_name,
                )
        except Exception as exc:
            logger.debug(
                "  r/%s: engine=%s failed: %s, trying next",
                subreddit, engine_name, exc,
            )
            last_exc = exc

    # All engines returned empty or failed
    if last_exc:
        logger.debug(
            "  r/%s: all engines exhausted (last error: %s)",
            subreddit, last_exc,
        )
    return []


# ---------------------------------------------------------------------------
# Engine 0: Reddit RSS feed (most reliable — no CAPTCHA, no auth needed)
# ---------------------------------------------------------------------------

async def _search_subreddit_rss(
    client,  # httpx.AsyncClient
    ticker: str,
    subreddit: str,
    days: int,
) -> list[dict]:
    """Fetch posts from a subreddit via RSS feed.

    For dedicated ticker subs (e.g., r/CRWV): fetches /new.rss (all posts relevant).
    For general subs (e.g., r/wallstreetbets): fetches /search.rss with ticker query.
    """
    is_dedicated = subreddit.upper() == ticker.upper() or ticker.upper() in subreddit.upper()

    if is_dedicated:
        url = f"https://www.reddit.com/r/{subreddit}/new.rss?limit=25"
    else:
        query = quote_plus(f"{ticker} OR {ticker.lower()}")
        url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={query}&sort=new&t=month&restrict_sr=on&limit=10"

    resp = await _get_with_retry(client, url)

    if resp.status_code != 200 or "<entry>" not in resp.text:
        return []

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("beautifulsoup4 required: pip install beautifulsoup4")

    soup = BeautifulSoup(resp.text, "xml")
    entries = soup.find_all("entry")

    posts: list[dict] = []
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    for entry in entries[:_MAX_RESULTS_PER_SUBREDDIT * 2]:  # take more from RSS since it's cheap
        title_el = entry.find("title")
        content_el = entry.find("content")
        link_el = entry.find("link")
        updated_el = entry.find("updated")

        title = title_el.text.strip() if title_el else ""
        snippet = ""
        if content_el:
            # RSS content is HTML — extract text
            content_soup = BeautifulSoup(content_el.text, "html.parser")
            snippet = content_soup.get_text()[:500]
        url_val = link_el.get("href", "") if link_el else ""
        post_date = updated_el.text[:10] if updated_el else ""

        # For general subs, filter out posts that don't mention the ticker
        if not is_dedicated:
            combined = f"{title} {snippet}".upper()
            if ticker.upper() not in combined:
                continue

        direction, strength = _classify_sentiment(title, snippet)

        posts.append({
            "ticker": ticker,
            "date": post_date or now_iso[:10],
            "source": "reddit",
            "source_id": url_val.split("/")[-2] if "/" in url_val else "",
            "author": "",
            "title": title,
            "snippet": snippet[:500],
            "engagement_score": 0.0,  # RSS doesn't include score
            "sentiment_direction": direction,
            "sentiment_strength": strength,
            "narrative_label": "",
            "bull_bear": direction if direction != "neutral" else "",
            "source_url": url_val,
            "updated_at": now_iso,
        })

    return posts


# ---------------------------------------------------------------------------
# Engine 1: DuckDuckGo HTML search
# ---------------------------------------------------------------------------

async def _search_subreddit_ddg(
    client,  # httpx.AsyncClient
    ticker: str,
    subreddit: str,
    days: int,
) -> list[dict]:
    """Search DuckDuckGo HTML for ``site:reddit.com/r/{sub} {ticker}``.

    DuckDuckGo HTML is less aggressive about rate limiting than Google.
    No date filtering is available in DDG HTML mode.
    """
    query = f"site:reddit.com/r/{subreddit} {ticker}"
    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

    resp = await _get_with_retry(client, search_url)
    return _parse_ddg_results(resp.text, ticker, subreddit)


def _parse_ddg_results(html: str, ticker: str, subreddit: str) -> list[dict]:
    """Parse DuckDuckGo HTML search results into sentiment observation dicts."""
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

    # DuckDuckGo HTML results use class="result" containers
    results = soup.select("div.result, div.results_links")[:_MAX_RESULTS_PER_SUBREDDIT]

    for result in results:
        try:
            # Title link
            link_elem = result.select_one("a.result__a")
            if not link_elem:
                continue
            url = link_elem.get("href", "")
            if "reddit.com" not in url:
                continue
            title = link_elem.get_text(strip=True)

            # Snippet
            snippet_elem = result.select_one("a.result__snippet")
            if not snippet_elem:
                # Fallback: try the snippet class without the <a> tag
                snippet_elem = result.select_one(".result__snippet")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

            direction, strength = _classify_sentiment(title, snippet)

            posts.append({
                "ticker": ticker,
                "source": "reddit",
                "platform": "reddit",
                "subreddit": subreddit,
                "title": title,
                "snippet": snippet[:500],
                "url": url,
                "sentiment_direction": direction,
                "sentiment_strength": strength,
                "observed_at": now_iso,
                "source_type": "social_media",
                "updated_at": now_iso,
            })
        except Exception as parse_err:
            logger.debug("Failed to parse DDG result: %s", parse_err)
            continue

    return posts


# ---------------------------------------------------------------------------
# Engine 2: Reddit JSON API (direct)
# ---------------------------------------------------------------------------

async def _search_subreddit_reddit_api(
    client,  # httpx.AsyncClient
    ticker: str,
    subreddit: str,
    days: int,
) -> list[dict]:
    """Search Reddit's JSON API directly for ticker mentions.

    URL: /r/{subreddit}/search.json?q={ticker}&sort=new&t=month&limit=10
    Most reliable source but Reddit occasionally rate-limits with 429.
    """
    # Map days to Reddit time filter parameter
    if days <= 1:
        time_filter = "day"
    elif days <= 7:
        time_filter = "week"
    elif days <= 30:
        time_filter = "month"
    elif days <= 365:
        time_filter = "year"
    else:
        time_filter = "all"

    search_url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={quote_plus(ticker)}&sort=new&t={time_filter}&limit=10"
        f"&restrict_sr=on"
    )

    # Use Reddit-specific User-Agent
    resp = await _get_with_retry(
        client, search_url,
        extra_headers={"User-Agent": _REDDIT_USER_AGENT},
    )

    return _parse_reddit_json(resp.text, ticker, subreddit)


def _parse_reddit_json(raw_json: str, ticker: str, subreddit: str) -> list[dict]:
    """Parse Reddit JSON API response into sentiment observation dicts."""
    try:
        data = json.loads(raw_json)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.debug("Failed to parse Reddit JSON: %s", exc)
        return []

    posts: list[dict] = []
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    children = data.get("data", {}).get("children", [])

    for child in children[:_MAX_RESULTS_PER_SUBREDDIT]:
        try:
            post_data = child.get("data", {})
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "")
            permalink = post_data.get("permalink", "")
            score = post_data.get("score", 0)
            num_comments = post_data.get("num_comments", 0)
            created_utc = post_data.get("created_utc", 0)

            url = f"https://www.reddit.com{permalink}" if permalink else ""

            # Use selftext as snippet (truncated)
            snippet = selftext[:500] if selftext else ""

            direction, strength = _classify_sentiment(title, snippet)

            # Build the post created timestamp
            if created_utc:
                post_time = datetime.fromtimestamp(
                    created_utc, tz=timezone.utc
                ).isoformat()
            else:
                post_time = now_iso

            posts.append({
                "ticker": ticker,
                "source": "reddit",
                "platform": "reddit",
                "subreddit": post_data.get("subreddit", subreddit),
                "title": title,
                "snippet": snippet,
                "url": url,
                "sentiment_direction": direction,
                "sentiment_strength": strength,
                "observed_at": post_time,
                "source_type": "social_media",
                "updated_at": now_iso,
                "score": score,
                "num_comments": num_comments,
            })
        except Exception as parse_err:
            logger.debug("Failed to parse Reddit API result: %s", parse_err)
            continue

    return posts


# ---------------------------------------------------------------------------
# Engine 3: Google search (last resort)
# ---------------------------------------------------------------------------

async def _search_subreddit_google(
    client,  # httpx.AsyncClient
    ticker: str,
    subreddit: str,
    days: int,
) -> list[dict]:
    """Scrape Google for ``site:reddit.com/r/{sub} {ticker}`` and parse results.

    Last resort engine — Google frequently CAPTCHAs automated requests.
    Retries up to 3 times with exponential backoff on transient failures.
    """
    query = f"site:reddit.com/r/{subreddit} {ticker}"
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:m"

    # tbs=qdr:m limits results to last month. For custom days:
    if days <= 1:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:d"
    elif days <= 7:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10&tbs=qdr:w"

    resp = await _get_with_retry(client, search_url)
    return _parse_google_results(resp.text, ticker, subreddit)


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


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _get_with_retry(
    client,
    url: str,
    attempts: int = _RETRY_ATTEMPTS,
    extra_headers: dict | None = None,
):
    """HTTP GET with exponential backoff retry.

    Args:
        client: httpx.AsyncClient instance.
        url: URL to fetch.
        attempts: Number of retry attempts.
        extra_headers: Additional headers to merge for this request only.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            kwargs: dict = {}
            if extra_headers:
                kwargs["headers"] = extra_headers
            resp = await client.get(url, **kwargs)
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
