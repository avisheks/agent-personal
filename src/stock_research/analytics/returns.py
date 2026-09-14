"""Returns analytics -- forward, historical, and rolling return calculations.

Computes from daily price history:

- **CAGR** at 1Y, 3Y, 5Y, 10Y horizons.
- **YTD return**.
- **Forward returns** at 1M, 3M, 6M, 12M from a given date index.
- **Relative returns** vs a peer price series.
- **Rolling returns** with a configurable trailing window.

Pure computation -- no API calls.  Stdlib only (no numpy/pandas).
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Approximate trading days for each period
_PERIOD_DAYS: Dict[str, int] = {
    "1m": 21,
    "3m": 63,
    "6m": 126,
    "1y": 252,
    "3y": 756,
    "5y": 1260,
    "10y": 2520,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_date(d: str) -> Optional[datetime]:
    """Parse a date string, trying common formats."""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(d, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _extract_closes(prices: List[Dict]) -> List[Tuple[str, float]]:
    """Extract (date, close) pairs from price dicts."""
    result: List[Tuple[str, float]] = []
    for p in prices:
        date_str = p.get("date", "")
        val = p.get("adjusted_close") or p.get("close") or p.get("price")
        if val is not None and date_str:
            try:
                result.append((str(date_str), float(val)))
            except (TypeError, ValueError):
                continue
    return result


def _cagr(start_val: float, end_val: float, years: float) -> float:
    """Compound Annual Growth Rate.

    Parameters
    ----------
    start_val : float
        Starting value (must be positive).
    end_val : float
        Ending value (must be positive).
    years : float
        Number of years (must be positive).

    Returns
    -------
    float
        CAGR as a decimal (e.g. 0.10 for 10%).

    Raises
    ------
    ValueError
        If any input is non-positive.
    """
    if start_val <= 0 or end_val <= 0 or years <= 0:
        raise ValueError(
            f"CAGR requires positive inputs: start={start_val}, "
            f"end={end_val}, years={years}"
        )
    return (end_val / start_val) ** (1.0 / years) - 1.0


def _forward_returns(
    prices: List[Tuple[str, float]],
    date_idx: int,
    periods: Optional[List[int]] = None,
) -> Dict[str, Optional[float]]:
    """Compute forward returns from a given date index.

    Parameters
    ----------
    prices : list[tuple[str, float]]
        Chronologically ordered (date, close) pairs.
    date_idx : int
        Index into prices from which to compute forward returns.
    periods : list[int], optional
        Forward periods in trading days. Defaults to [21, 63, 126, 252]
        representing 1M, 3M, 6M, 12M.

    Returns
    -------
    dict
        Period labels mapped to returns (decimal) or None if insufficient data.
    """
    if periods is None:
        periods = [21, 63, 126, 252]

    labels = {21: "1m", 63: "3m", 126: "6m", 252: "12m"}
    result: Dict[str, Optional[float]] = {}
    base_price = prices[date_idx][1]

    if base_price <= 0:
        return {labels.get(p, f"{p}d"): None for p in periods}

    for period in periods:
        label = labels.get(period, f"{period}d")
        target_idx = date_idx + period
        if target_idx < len(prices):
            future_price = prices[target_idx][1]
            if future_price > 0:
                result[label] = round((future_price / base_price) - 1.0, 4)
            else:
                result[label] = None
        else:
            result[label] = None

    return result


def _relative_returns(
    ticker_prices: List[Tuple[str, float]],
    peer_prices: List[Tuple[str, float]],
    periods: Optional[List[int]] = None,
) -> Dict[str, Optional[float]]:
    """Compute relative performance vs a peer over multiple periods.

    Calculates the difference in returns (ticker - peer) for each period,
    measured from the end of the series looking backward.

    Parameters
    ----------
    ticker_prices : list[tuple[str, float]]
        Ticker's (date, close) pairs.
    peer_prices : list[tuple[str, float]]
        Peer's (date, close) pairs (same date alignment assumed).
    periods : list[int], optional
        Lookback periods in trading days. Defaults to [21, 63, 126, 252].

    Returns
    -------
    dict
        Period labels mapped to relative returns (ticker - peer), or None.
    """
    if periods is None:
        periods = [21, 63, 126, 252]

    labels = {21: "1m", 63: "3m", 126: "6m", 252: "12m"}
    result: Dict[str, Optional[float]] = {}

    min_len = min(len(ticker_prices), len(peer_prices))

    for period in periods:
        label = labels.get(period, f"{period}d")
        if period >= min_len or min_len < 2:
            result[label] = None
            continue

        # Use the last data point as "now" and look back
        t_end = ticker_prices[-1][1]
        t_start = ticker_prices[-(period + 1)][1] if period < len(ticker_prices) else None
        p_end = peer_prices[-1][1]
        p_start = peer_prices[-(period + 1)][1] if period < len(peer_prices) else None

        if (
            t_start is not None and t_start > 0
            and t_end > 0
            and p_start is not None and p_start > 0
            and p_end > 0
        ):
            t_ret = (t_end / t_start) - 1.0
            p_ret = (p_end / p_start) - 1.0
            result[label] = round(t_ret - p_ret, 4)
        else:
            result[label] = None

    return result


def _rolling_returns(
    prices: List[Tuple[str, float]], window: int = 252
) -> List[Dict[str, Any]]:
    """Compute trailing returns for each date using a rolling window.

    Parameters
    ----------
    prices : list[tuple[str, float]]
        Chronologically ordered (date, close) pairs.
    window : int
        Rolling window in trading days. Defaults to 252 (1 year).

    Returns
    -------
    list[dict]
        Each entry: ``{"date": str, "trailing_return": float}``.
    """
    result: List[Dict[str, Any]] = []
    for i in range(window, len(prices)):
        start_price = prices[i - window][1]
        end_price = prices[i][1]
        if start_price > 0 and end_price > 0:
            ret = (end_price / start_price) - 1.0
            result.append({
                "date": prices[i][0],
                "trailing_return": round(ret, 4),
            })
    return result


def _ytd_return(prices: List[Tuple[str, float]]) -> Optional[float]:
    """Year-to-date return from the first trading day of the current year.

    Parameters
    ----------
    prices : list[tuple[str, float]]
        Chronologically ordered (date, close) pairs.

    Returns
    -------
    Optional[float]
        YTD return as a decimal, or None if no same-year data.
    """
    if not prices:
        return None

    # Find the last date's year
    last_date = _parse_date(prices[-1][0])
    if last_date is None:
        return None
    current_year = last_date.year

    # Find the first trading day of that year
    for date_str, close in prices:
        dt = _parse_date(date_str)
        if dt is not None and dt.year == current_year and close > 0:
            end_price = prices[-1][1]
            if end_price > 0:
                return round((end_price / close) - 1.0, 4)
            break

    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_returns(prices: List[Dict], ticker: str = "") -> dict:
    """Compute comprehensive return metrics from daily price history.

    Parameters
    ----------
    prices : list[dict]
        List of dicts with ``date`` (str) and ``adjusted_close`` (float) keys,
        in chronological order.
    ticker : str
        Ticker symbol (for labeling only).

    Returns
    -------
    dict
        Keys: ``cagr_1y``, ``cagr_3y``, ``cagr_5y``, ``cagr_10y``,
        ``ytd_return``, ``rolling_returns``, ``ticker``.
    """
    if not prices:
        return {
            "ticker": ticker,
            "cagr_1y": None,
            "cagr_3y": None,
            "cagr_5y": None,
            "cagr_10y": None,
            "ytd_return": None,
            "rolling_returns": [],
            "data_points": 0,
            "error": "no price data provided",
        }

    data = _extract_closes(prices)
    if not data:
        return {
            "ticker": ticker,
            "cagr_1y": None,
            "cagr_3y": None,
            "cagr_5y": None,
            "cagr_10y": None,
            "ytd_return": None,
            "rolling_returns": [],
            "data_points": 0,
            "error": "no valid price data extracted",
        }

    n = len(data)
    end_price = data[-1][1]

    # CAGR calculations (lookback from the end)
    cagrs: Dict[str, Optional[float]] = {}
    for label, days in [("cagr_1y", 252), ("cagr_3y", 756), ("cagr_5y", 1260), ("cagr_10y", 2520)]:
        years = days / 252.0
        if n > days and end_price > 0:
            start_price = data[-(days + 1)][1]
            if start_price > 0:
                try:
                    cagrs[label] = round(_cagr(start_price, end_price, years), 4)
                except ValueError:
                    cagrs[label] = None
            else:
                cagrs[label] = None
        else:
            cagrs[label] = None

    # YTD
    ytd = _ytd_return(data)

    # Rolling 1Y returns
    rolling = _rolling_returns(data, window=252)

    return {
        "ticker": ticker,
        "cagr_1y": cagrs.get("cagr_1y"),
        "cagr_3y": cagrs.get("cagr_3y"),
        "cagr_5y": cagrs.get("cagr_5y"),
        "cagr_10y": cagrs.get("cagr_10y"),
        "ytd_return": ytd,
        "rolling_returns": rolling,
        "data_points": n,
    }
