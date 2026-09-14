"""Peer comparison analytics -- rank a ticker against its peer group.

Compares a ticker's fundamental metrics against peer medians and produces
percentile rankings, strengths, and weaknesses.

Pure computation -- no API calls.  Stdlib only (no numpy/pandas).
"""

from __future__ import annotations

import logging
import statistics
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Metrics to compare and whether higher is better
_METRIC_CONFIG: List[Tuple[str, bool]] = [
    ("pe", False),                # lower PE is better (cheaper)
    ("pb", False),                # lower PB is better
    ("ps", False),                # lower P/S is better
    ("peg_ratio", False),         # lower PEG is better
    ("eps_growth", True),         # higher earnings growth is better
    ("revenue_growth", True),     # higher revenue growth is better
    ("profit_margin", True),      # higher margins are better
    ("operating_margin", True),
    ("roe", True),                # higher return on equity is better
    ("roa", True),                # higher return on assets is better
    ("debt_equity", False),       # lower leverage is better
    ("current_ratio", True),      # higher liquidity is better
    ("dividend_yield", True),     # higher yield is better (for income)
    ("free_cash_flow_yield", True),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_float(val: Any) -> Optional[float]:
    """Convert a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        v = float(val)
        return v if not (v != v) else None  # NaN check without math import
    except (TypeError, ValueError):
        return None


def _rank_metric(
    ticker_val: Optional[float],
    peer_vals: List[float],
    metric_name: str,
    higher_is_better: bool = True,
) -> dict:
    """Rank a single metric value against peer values.

    Parameters
    ----------
    ticker_val : Optional[float]
        The ticker's value for this metric. None if unavailable.
    peer_vals : list[float]
        Peer values for this metric (only valid floats, no Nones).
    metric_name : str
        Name of the metric (for labeling).
    higher_is_better : bool
        If True, higher values rank better. If False, lower is better.

    Returns
    -------
    dict
        Keys: ``metric``, ``value``, ``peer_median``, ``percentile``,
        ``verdict`` ("above_median" / "at_median" / "below_median"),
        ``higher_is_better``.
    """
    if ticker_val is None or not peer_vals:
        return {
            "metric": metric_name,
            "value": ticker_val,
            "peer_median": statistics.median(peer_vals) if peer_vals else None,
            "percentile": None,
            "verdict": "no_data",
            "higher_is_better": higher_is_better,
        }

    median_val = statistics.median(peer_vals)

    # Compute percentile: what fraction of peers does this ticker beat?
    all_vals = peer_vals + [ticker_val]
    sorted_vals = sorted(all_vals)
    # Position-based percentile
    rank_idx = sorted_vals.index(ticker_val)
    percentile = round(rank_idx / max(len(sorted_vals) - 1, 1) * 100.0, 1)

    # If lower is better, invert the percentile for "goodness"
    if not higher_is_better:
        percentile = round(100.0 - percentile, 1)

    # Verdict
    if higher_is_better:
        if ticker_val > median_val * 1.05:
            verdict = "above_median"
        elif ticker_val < median_val * 0.95:
            verdict = "below_median"
        else:
            verdict = "at_median"
    else:
        if ticker_val < median_val * 0.95:
            verdict = "above_median"  # lower is better, so below median value = good
        elif ticker_val > median_val * 1.05:
            verdict = "below_median"
        else:
            verdict = "at_median"

    return {
        "metric": metric_name,
        "value": round(ticker_val, 4),
        "peer_median": round(median_val, 4),
        "percentile": percentile,
        "verdict": verdict,
        "higher_is_better": higher_is_better,
    }


def _compute_medians(peer_fundamentals: List[Dict]) -> Dict[str, Optional[float]]:
    """Compute median for each metric across peer fundamentals.

    Parameters
    ----------
    peer_fundamentals : list[dict]
        List of fundamentals dicts for peer companies.

    Returns
    -------
    dict
        Metric name -> median value (or None if insufficient data).
    """
    medians: Dict[str, Optional[float]] = {}

    for metric_name, _ in _METRIC_CONFIG:
        vals: List[float] = []
        for pf in peer_fundamentals:
            v = _safe_float(pf.get(metric_name))
            if v is not None:
                vals.append(v)
        if vals:
            medians[metric_name] = round(statistics.median(vals), 4)
        else:
            medians[metric_name] = None

    return medians


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compare_peers(
    ticker_fundamentals: dict,
    peer_fundamentals: List[Dict],
) -> dict:
    """Compare a ticker's fundamentals against its peer group.

    Parameters
    ----------
    ticker_fundamentals : dict
        Fundamentals dict for the target ticker.
    peer_fundamentals : list[dict]
        List of fundamentals dicts for peer companies.

    Returns
    -------
    dict
        Keys: ``peer_medians`` (per metric median), ``ticker_vs_median``
        (per metric: value, median, percentile, verdict), ``strengths``
        (where ticker beats peers), ``weaknesses`` (where it lags),
        ``peer_count``.
    """
    if not peer_fundamentals:
        return {
            "peer_medians": {},
            "ticker_vs_median": {},
            "strengths": [],
            "weaknesses": [],
            "peer_count": 0,
            "error": "no peer data provided",
        }

    # Compute medians
    peer_medians = _compute_medians(peer_fundamentals)

    # Rank each metric
    ticker_vs_median: Dict[str, dict] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []

    for metric_name, higher_is_better in _METRIC_CONFIG:
        ticker_val = _safe_float(ticker_fundamentals.get(metric_name))

        # Collect valid peer values for this metric
        peer_vals: List[float] = []
        for pf in peer_fundamentals:
            v = _safe_float(pf.get(metric_name))
            if v is not None:
                peer_vals.append(v)

        ranking = _rank_metric(ticker_val, peer_vals, metric_name, higher_is_better)
        ticker_vs_median[metric_name] = ranking

        if ranking["verdict"] == "above_median":
            strengths.append(metric_name)
        elif ranking["verdict"] == "below_median":
            weaknesses.append(metric_name)

    return {
        "peer_medians": peer_medians,
        "ticker_vs_median": ticker_vs_median,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "peer_count": len(peer_fundamentals),
    }
