"""Earnings data ingestion from Financial Modeling Prep (FMP) API.

Fetches historical earnings (actual vs estimate, surprise) for a ticker.
Requires env var ``FMP_API_KEY``. If not set, returns an empty list with
a warning (this source is optional).

Usage:
    python -m stock_research.ingestion.earnings AAPL
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_BASE_URL = "https://financialmodelingprep.com/api/v3"
_REQUEST_TIMEOUT = 20


def fetch_earnings(ticker: str, years: int = 10) -> list[dict]:
    """Fetch historical earnings records for *ticker*.

    Returns a list of dicts matching the ``earnings`` DuckDB schema:
    ticker, date, fiscal_period, eps_actual, eps_estimate,
    eps_surprise, eps_surprise_pct, revenue_actual, revenue_estimate,
    revenue_surprise_pct, source, updated_at.

    If FMP_API_KEY is not set, logs a warning and returns [].
    """
    ticker = ticker.upper()
    apikey = os.environ.get("FMP_API_KEY", "").strip()

    if not apikey:
        logger.warning(
            "FMP_API_KEY env var is not set. Earnings data will be unavailable. "
            "Get a free key at https://financialmodelingprep.com/"
        )
        return []

    raw = _fetch_earnings_calendar(ticker, apikey)
    return _parse_earnings(raw, ticker, years)


def _fetch_earnings_calendar(ticker: str, apikey: str) -> list[dict]:
    """Fetch historical earnings calendar from FMP API.

    Endpoint: GET /api/v3/historical/earning_calendar/{ticker}?apikey=...
    """
    url = f"{_BASE_URL}/historical/earning_calendar/{ticker}?apikey={apikey}"

    req = Request(
        url,
        headers={
            "User-Agent": "personal-investor-agent/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 401:
            logger.warning("FMP API key is invalid or expired (HTTP 401)")
            return []
        if exc.code == 403:
            logger.warning("FMP API access forbidden (HTTP 403) -- check plan limits")
            return []
        raise RuntimeError(f"FMP HTTP {exc.code} on {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"FMP network error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"FMP response was not JSON: {exc}") from exc

    if isinstance(data, dict) and "Error Message" in data:
        logger.warning("FMP error: %s", data["Error Message"])
        return []

    if not isinstance(data, list):
        logger.warning("Unexpected FMP response type: %s", type(data).__name__)
        return []

    return data


def _parse_earnings(
    raw: list[dict], ticker: str, years: int
) -> list[dict]:
    """Parse FMP earnings calendar response into schema-aligned records.

    Filters to the last *years* of data and computes surprise percentages.
    """
    now = datetime.now(tz=timezone.utc)
    now_iso = now.isoformat()
    cutoff_year = now.year - years

    records: list[dict] = []

    for entry in raw:
        date_str = entry.get("date") or ""
        if not date_str:
            continue

        # Filter by year
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.year < cutoff_year:
                continue
        except ValueError:
            continue

        eps_actual = _safe_float(entry.get("eps"))
        eps_estimate = _safe_float(entry.get("epsEstimated"))
        revenue_actual = _safe_float(entry.get("revenue"))
        revenue_estimate = _safe_float(entry.get("revenueEstimated"))

        # Compute surprise values
        eps_surprise: Optional[float] = None
        eps_surprise_pct: Optional[float] = None
        if eps_actual is not None and eps_estimate is not None:
            eps_surprise = eps_actual - eps_estimate
            if eps_estimate != 0:
                eps_surprise_pct = eps_surprise / abs(eps_estimate)

        revenue_surprise_pct: Optional[float] = None
        if revenue_actual is not None and revenue_estimate is not None and revenue_estimate != 0:
            revenue_surprise_pct = (revenue_actual - revenue_estimate) / abs(revenue_estimate)

        # Determine fiscal period from the entry or approximate from date.
        fiscal_period = entry.get("fiscalDateEnding") or ""
        if not fiscal_period:
            # Approximate quarter from date
            try:
                month = dt.month
                if month <= 3:
                    fiscal_period = f"Q1 {dt.year}"
                elif month <= 6:
                    fiscal_period = f"Q2 {dt.year}"
                elif month <= 9:
                    fiscal_period = f"Q3 {dt.year}"
                else:
                    fiscal_period = f"Q4 {dt.year}"
            except Exception:
                fiscal_period = date_str

        records.append({
            "ticker": ticker,
            "date": date_str,
            "fiscal_period": fiscal_period,
            "eps_actual": eps_actual,
            "eps_estimate": eps_estimate,
            "eps_surprise": eps_surprise,
            "eps_surprise_pct": eps_surprise_pct,
            "revenue_actual": revenue_actual,
            "revenue_estimate": revenue_estimate,
            "revenue_surprise_pct": revenue_surprise_pct,
            "source": "fmp",
            "updated_at": now_iso,
        })

    # Sort by date ascending
    records.sort(key=lambda r: r["date"])
    return records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val: Any) -> Optional[float]:
    """Convert to float or return None."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m stock_research.ingestion.earnings TICKER", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1].upper()
    results = fetch_earnings(ticker, years=10)

    if not results:
        print(f"No earnings data for {ticker} (check FMP_API_KEY)")
        sys.exit(0)

    print(f"Fetched {len(results)} earnings records for {ticker}")
    for rec in results[-8:]:
        surprise_str = ""
        if rec["eps_surprise_pct"] is not None:
            surprise_str = f" ({rec['eps_surprise_pct']:+.1%})"
        print(
            f"  {rec['date']}  "
            f"EPS: {rec['eps_actual']} vs {rec['eps_estimate']}{surprise_str}  "
            f"Rev: {rec['revenue_actual']}"
        )
