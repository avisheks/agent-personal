"""Yahoo Finance market data ingestion via yfinance.

Fetches daily OHLCV prices and current valuation snapshot for a ticker.

Usage:
    python -m stock_research.ingestion.market_data AAPL
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _ensure_yfinance():
    """Import yfinance with a helpful error if not installed."""
    try:
        import yfinance  # noqa: F811
        return yfinance
    except ImportError:
        raise ImportError(
            "yfinance is required for market data ingestion. "
            "Install it with: pip install yfinance"
        )


def fetch_prices(ticker: str, years: int = 10) -> list[dict]:
    """Fetch daily OHLCV price history for *ticker*.

    Returns a list of dicts matching the ``prices`` DuckDB schema:
    ticker, date, open, high, low, close, adjusted_close, volume, source, updated_at.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL').
        years: Number of years of history to fetch (default 10).
    """
    yf = _ensure_yfinance()
    ticker = ticker.upper()

    stock = yf.Ticker(ticker)
    period = f"{years}y"

    logger.info("Fetching %s price history (%s)", ticker, period)
    hist = stock.history(period=period, auto_adjust=False)

    if hist.empty:
        logger.warning("No price history returned for %s", ticker)
        return []

    now_iso = datetime.now(tz=timezone.utc).isoformat()
    records: list[dict] = []

    for date_idx, row in hist.iterrows():
        # date_idx is a Timestamp from pandas
        date_str = date_idx.strftime("%Y-%m-%d")
        records.append({
            "ticker": ticker,
            "date": date_str,
            "open": _safe_float(row.get("Open")),
            "high": _safe_float(row.get("High")),
            "low": _safe_float(row.get("Low")),
            "close": _safe_float(row.get("Close")),
            "adjusted_close": _safe_float(row.get("Adj Close")),
            "volume": _safe_int(row.get("Volume")),
            "source": "yahoo_finance",
            "updated_at": now_iso,
        })

    return records


def fetch_info(ticker: str) -> dict:
    """Fetch current fundamentals/valuation snapshot for *ticker*.

    Returns a dict matching the ``valuation`` DuckDB schema:
    ticker, date, market_cap, pe_ratio, forward_pe, pb_ratio, ps_ratio,
    peg_ratio, ev_to_ebitda, dividend_yield, beta, fifty_two_week_high,
    fifty_two_week_low, avg_volume, source, updated_at.
    """
    yf = _ensure_yfinance()
    ticker = ticker.upper()

    stock = yf.Ticker(ticker)
    logger.info("Fetching %s info snapshot", ticker)
    info: dict[str, Any] = stock.info or {}

    if not info:
        logger.warning("No info returned for %s", ticker)
        return {}

    now_iso = datetime.now(tz=timezone.utc).isoformat()
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    return {
        "ticker": ticker,
        "date": today,
        "market_cap": _safe_float(info.get("marketCap")),
        "pe": _safe_float(info.get("trailingPE")),
        "forward_pe": _safe_float(info.get("forwardPE")),
        "ev_sales": _safe_float(info.get("enterpriseToRevenue")),
        "ev_ebitda": _safe_float(info.get("enterpriseToEbitda")),
        "price_sales": _safe_float(info.get("priceToSalesTrailing12Months")),
        "fcf_yield": None,
        "enterprise_value": _safe_float(info.get("enterpriseValue")),
        "source": "yahoo_finance",
        "updated_at": now_iso,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val: Any) -> Optional[float]:
    """Convert to float or return None."""
    if val is None:
        return None
    try:
        f = float(val)
        # pandas can produce NaN; treat as None
        if f != f:  # NaN check
            return None
        return f
    except (TypeError, ValueError):
        return None


def _safe_int(val: Any) -> Optional[int]:
    """Convert to int or return None."""
    if val is None:
        return None
    try:
        f = float(val)
        if f != f:
            return None
        return int(f)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m stock_research.ingestion.market_data TICKER", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1].upper()

    try:
        prices = fetch_prices(ticker, years=10)
        info = fetch_info(ticker)
    except ImportError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    print(f"Fetched {len(prices)} daily price records for {ticker}")
    if prices:
        latest = prices[-1]
        print(
            f"  Latest: {latest['date']}  "
            f"O={latest['open']}  H={latest['high']}  "
            f"L={latest['low']}  C={latest['close']}  "
            f"V={latest['volume']}"
        )

    if info:
        print(f"\nValuation snapshot for {ticker}:")
        print(f"  Market Cap:  {info.get('market_cap')}")
        print(f"  P/E:         {info.get('pe_ratio')}")
        print(f"  P/B:         {info.get('pb_ratio')}")
        print(f"  Div Yield:   {info.get('dividend_yield')}")
        print(f"  Beta:        {info.get('beta')}")
        print(f"  52w Hi/Lo:   {info.get('fifty_two_week_high')} / {info.get('fifty_two_week_low')}")
