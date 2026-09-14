"""Risk analytics -- price-return risk metrics from daily close history.

Computes from a list of daily price observations:

- **Annualized volatility** from stdev of daily log returns, scaled by sqrt(252).
- **Maximum drawdown** as the largest peak-to-trough decline.
- **Value at Risk (95% daily)** -- the 5th-percentile worst daily return.
- **Risk rating** bucketed by annualized vol.

Pure computation -- no API calls.  Stdlib only (no numpy).
"""

from __future__ import annotations

import logging
import math
import statistics
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_MIN_DATA_POINTS: int = 30
_TRADING_DAYS_PER_YEAR: int = 252


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _daily_log_returns(closes: List[float]) -> List[float]:
    """Compute ln(close_i / close_{i-1}) for each consecutive pair.

    Skips any pair where the prior close is non-positive to avoid math
    domain errors.

    Parameters
    ----------
    closes : list[float]
        Daily adjusted close prices in chronological order.

    Returns
    -------
    list[float]
        Daily log returns.
    """
    returns: List[float] = []
    for i in range(1, len(closes)):
        if closes[i - 1] <= 0 or closes[i] <= 0:
            continue
        returns.append(math.log(closes[i] / closes[i - 1]))
    return returns


def _annualized_volatility(returns: List[float]) -> float:
    """Annualized volatility: stdev(daily_returns) * sqrt(252).

    Parameters
    ----------
    returns : list[float]
        Daily log returns.

    Returns
    -------
    float
        Annualized volatility as a decimal (e.g. 0.25 for 25%).

    Raises
    ------
    statistics.StatisticsError
        If fewer than 2 data points.
    """
    return statistics.stdev(returns) * math.sqrt(_TRADING_DAYS_PER_YEAR)


def _max_drawdown(closes: List[float]) -> float:
    """Largest peak-to-trough decline as a positive fraction (0-1).

    Parameters
    ----------
    closes : list[float]
        Daily adjusted close prices in chronological order.

    Returns
    -------
    float
        Maximum drawdown as a positive fraction (e.g. 0.30 for 30%).
    """
    if not closes:
        return 0.0
    peak = closes[0]
    max_dd = 0.0
    for close in closes:
        if close > peak:
            peak = close
        if peak > 0:
            dd = (peak - close) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd


def _var_95(returns: List[float]) -> float:
    """5th-percentile daily return (Value at Risk).

    Returns a negative number for losses.  Uses floor indexing so boundary
    cases round toward the loss tail.

    Parameters
    ----------
    returns : list[float]
        Daily log returns.

    Returns
    -------
    float
        5th-percentile return value.
    """
    sorted_returns = sorted(returns)
    idx = max(0, int(len(sorted_returns) * 0.05) - 1)
    idx = min(idx, len(sorted_returns) - 1)
    return sorted_returns[idx]


def _risk_rating(vol: float) -> str:
    """Bucket annualized volatility into a qualitative rating.

    Parameters
    ----------
    vol : float
        Annualized volatility as a decimal.

    Returns
    -------
    str
        One of ``"low"``, ``"medium"``, ``"high"``, ``"very_high"``.
    """
    if vol < 0.15:
        return "low"
    if vol < 0.25:
        return "medium"
    if vol < 0.40:
        return "high"
    return "very_high"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_risk(prices: List[Dict]) -> dict:
    """Compute price-return risk metrics from daily price observations.

    Parameters
    ----------
    prices : list[dict]
        List of dicts with at least ``date`` (str) and ``adjusted_close``
        (float) keys, in chronological order.

    Returns
    -------
    dict
        Keys: ``annualized_volatility``, ``max_drawdown``, ``var_95_daily``,
        ``risk_rating``, ``data_points``.  On insufficient data, returns
        dict with ``error`` and available fields set to None.
    """
    if not prices:
        return {
            "annualized_volatility": None,
            "max_drawdown": None,
            "var_95_daily": None,
            "risk_rating": None,
            "data_points": 0,
            "error": "no price data provided",
        }

    # Extract closes
    closes: List[float] = []
    for p in prices:
        val = p.get("adjusted_close") or p.get("close") or p.get("price")
        if val is not None:
            try:
                closes.append(float(val))
            except (TypeError, ValueError):
                continue

    if len(closes) < _MIN_DATA_POINTS:
        return {
            "annualized_volatility": None,
            "max_drawdown": None,
            "var_95_daily": None,
            "risk_rating": None,
            "data_points": len(closes),
            "error": f"insufficient data: {len(closes)} points (need {_MIN_DATA_POINTS})",
        }

    # Compute log returns
    daily_returns = _daily_log_returns(closes)

    if len(daily_returns) < _MIN_DATA_POINTS:
        return {
            "annualized_volatility": None,
            "max_drawdown": None,
            "var_95_daily": None,
            "risk_rating": None,
            "data_points": len(daily_returns),
            "error": (
                f"insufficient return data: {len(daily_returns)} points "
                f"(need {_MIN_DATA_POINTS})"
            ),
        }

    # Compute metrics
    vol = _annualized_volatility(daily_returns)
    drawdown = _max_drawdown(closes)
    var95 = _var_95(daily_returns)
    rating = _risk_rating(vol)

    return {
        "annualized_volatility": round(vol, 4),
        "max_drawdown": round(drawdown, 4),
        "var_95_daily": round(var95, 4),
        "risk_rating": rating,
        "data_points": len(daily_returns),
    }
