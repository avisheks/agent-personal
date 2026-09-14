"""Sentiment-return analytics -- quantitative sentiment to forward return analysis.

The killer feature: maps historical sentiment observations to forward price
returns, enabling data-driven answers to "when Reddit was this bullish before,
what happened next?"

Takes a time series of sentiment observations (from Reddit, news, etc.) and
a price series, then:

1. Buckets historical sentiment into very_bearish/bearish/neutral/bullish/very_bullish.
2. For each bucket, computes what the forward returns were at 1M/3M/6M/12M.
3. Reports whether extreme sentiment has historically been predictive.
4. Summarises current sentiment state.

Pure computation -- no API calls.  Stdlib only (no numpy/pandas).
"""

from __future__ import annotations

import logging
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Sentiment score thresholds (scores expected on -1.0 to +1.0 scale)
_BUCKET_THRESHOLDS: List[Tuple[str, float, float]] = [
    ("very_bearish", -1.0, -0.6),
    ("bearish", -0.6, -0.2),
    ("neutral", -0.2, 0.2),
    ("bullish", 0.2, 0.6),
    ("very_bullish", 0.6, 1.0),
]

_FORWARD_DAYS_DEFAULT: List[int] = [21, 63, 126, 252]
_FORWARD_LABELS: Dict[int, str] = {21: "1m", 63: "3m", 126: "6m", 252: "12m"}

_MIN_OBSERVATIONS_PER_BUCKET: int = 5
_MIN_TOTAL_OBSERVATIONS: int = 10


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


def _classify_bucket(score: float) -> str:
    """Map a sentiment score (-1 to +1) to a named bucket.

    Parameters
    ----------
    score : float
        Sentiment score in [-1.0, +1.0].

    Returns
    -------
    str
        One of ``"very_bearish"``, ``"bearish"``, ``"neutral"``,
        ``"bullish"``, ``"very_bullish"``.
    """
    for label, low, high in _BUCKET_THRESHOLDS:
        if low <= score <= high:
            return label
    # Edge cases: clamp
    if score < -0.6:
        return "very_bearish"
    if score > 0.6:
        return "very_bullish"
    return "neutral"


def _build_price_index(prices: List[Dict]) -> Dict[str, float]:
    """Build a date -> close price lookup from price list."""
    index: Dict[str, float] = {}
    for p in prices:
        date_str = p.get("date", "")
        val = p.get("adjusted_close") or p.get("close") or p.get("price")
        if val is not None and date_str:
            try:
                index[str(date_str)] = float(val)
            except (TypeError, ValueError):
                continue
    return index


def _sorted_price_dates(prices: List[Dict]) -> List[Tuple[str, float]]:
    """Extract sorted (date_str, close) pairs."""
    pairs: List[Tuple[str, float]] = []
    for p in prices:
        date_str = p.get("date", "")
        val = p.get("adjusted_close") or p.get("close") or p.get("price")
        if val is not None and date_str:
            try:
                pairs.append((str(date_str), float(val)))
            except (TypeError, ValueError):
                continue
    # Sort by date string (works for YYYY-MM-DD format)
    pairs.sort(key=lambda x: x[0])
    return pairs


def _find_forward_price(
    date_str: str,
    sorted_prices: List[Tuple[str, float]],
    forward_days: int,
) -> Optional[float]:
    """Find the price approximately forward_days trading days after date_str.

    Uses calendar-day approximation (forward_days * 365/252) then finds the
    closest available trading date.
    """
    target_dt = _parse_date(date_str)
    if target_dt is None:
        return None

    # Convert trading days to approximate calendar days
    calendar_days = int(forward_days * 365.0 / 252.0)
    target_date = target_dt + timedelta(days=calendar_days)
    target_str = target_date.strftime("%Y-%m-%d")

    # Find closest date in sorted_prices at or after target
    best_price: Optional[float] = None
    best_diff: Optional[int] = None

    for pdate, pclose in sorted_prices:
        pdt = _parse_date(pdate)
        if pdt is None:
            continue
        diff = abs((pdt - target_date).days)
        if diff <= 10:  # within 10 calendar days tolerance
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_price = pclose

    return best_price


def _bucket_sentiment(
    observations: List[Dict],
    periods: Optional[List[str]] = None,
) -> Dict[str, List[Dict]]:
    """Aggregate sentiment observations per time period into buckets.

    Parameters
    ----------
    observations : list[dict]
        Each dict should have ``date`` (str), ``sentiment_score`` (float in
        [-1, 1]), and optionally ``source``, ``ticker``.
    periods : list[str], optional
        Aggregation periods. Defaults to ["1m", "3m", "6m"].

    Returns
    -------
    dict
        Keys are bucket names, values are lists of observation dicts
        with their bucket classification added.
    """
    if periods is None:
        periods = ["1m", "3m", "6m"]

    # Classify each observation
    bucketed: Dict[str, List[Dict]] = {
        "very_bearish": [],
        "bearish": [],
        "neutral": [],
        "bullish": [],
        "very_bullish": [],
    }

    for obs in observations:
        score = obs.get("sentiment_score")
        if score is None:
            continue
        try:
            score = float(score)
        except (TypeError, ValueError):
            continue

        bucket = _classify_bucket(score)
        bucketed[bucket].append({
            "date": obs.get("date", ""),
            "sentiment_score": score,
            "source": obs.get("source", "unknown"),
            "bucket": bucket,
        })

    return bucketed


def _sentiment_forward_returns(
    buckets: Dict[str, List[Dict]],
    prices: List[Dict],
    forward_days: Optional[List[int]] = None,
) -> Dict[str, Dict[str, Optional[float]]]:
    """For each sentiment bucket, compute average forward returns.

    Parameters
    ----------
    buckets : dict
        Output of ``_bucket_sentiment``: bucket_name -> list of observations.
    prices : list[dict]
        Daily price data with ``date`` and ``adjusted_close``.
    forward_days : list[int], optional
        Forward periods in trading days. Defaults to [21, 63, 126, 252].

    Returns
    -------
    dict
        For each bucket: dict of forward period -> average return.
        Example: ``{"bullish": {"1m": 0.02, "3m": 0.05, ...}}``.
    """
    if forward_days is None:
        forward_days = _FORWARD_DAYS_DEFAULT

    sorted_prices = _sorted_price_dates(prices)
    price_index = _build_price_index(prices)
    result: Dict[str, Dict[str, Optional[float]]] = {}

    for bucket_name, obs_list in buckets.items():
        period_returns: Dict[str, List[float]] = {
            _FORWARD_LABELS.get(fd, f"{fd}d"): [] for fd in forward_days
        }

        for obs in obs_list:
            obs_date = obs.get("date", "")
            obs_price_val = price_index.get(obs_date)

            if obs_price_val is None or obs_price_val <= 0:
                # Try to find closest trading date
                obs_dt = _parse_date(obs_date)
                if obs_dt is None:
                    continue
                # Search within 5 days
                for delta in range(0, 6):
                    check_date = (obs_dt + timedelta(days=delta)).strftime("%Y-%m-%d")
                    if check_date in price_index:
                        obs_price_val = price_index[check_date]
                        break
                if obs_price_val is None or obs_price_val <= 0:
                    continue

            for fd in forward_days:
                label = _FORWARD_LABELS.get(fd, f"{fd}d")
                future_price = _find_forward_price(obs_date, sorted_prices, fd)
                if future_price is not None and future_price > 0:
                    ret = (future_price / obs_price_val) - 1.0
                    period_returns[label].append(ret)

        # Average returns per period
        avg_returns: Dict[str, Optional[float]] = {}
        for label, returns in period_returns.items():
            if returns:
                avg_returns[label] = round(statistics.mean(returns), 4)
            else:
                avg_returns[label] = None

        result[bucket_name] = avg_returns

    return result


def _current_sentiment(
    observations: List[Dict], days: int = 30
) -> Dict[str, Any]:
    """Summarise the current sentiment state from recent observations.

    Parameters
    ----------
    observations : list[dict]
        Sentiment observations with ``date`` and ``sentiment_score``.
    days : int
        Lookback window in calendar days. Defaults to 30.

    Returns
    -------
    dict
        Keys: ``direction`` ("bullish"/"bearish"/"neutral"),
        ``strength`` (0-1 absolute value of avg score),
        ``confidence`` (based on observation count),
        ``avg_score``, ``observation_count``.
    """
    if not observations:
        return {
            "direction": "neutral",
            "strength": 0.0,
            "confidence": 0.0,
            "avg_score": 0.0,
            "observation_count": 0,
        }

    # Find the cutoff date
    # Use the most recent observation date as reference
    latest_date: Optional[datetime] = None
    for obs in observations:
        dt = _parse_date(obs.get("date", ""))
        if dt is not None:
            if latest_date is None or dt > latest_date:
                latest_date = dt

    if latest_date is None:
        # No parseable dates; use all observations
        recent = observations
    else:
        cutoff = latest_date - timedelta(days=days)
        recent = []
        for obs in observations:
            dt = _parse_date(obs.get("date", ""))
            if dt is not None and dt >= cutoff:
                recent.append(obs)

    # Extract scores
    scores: List[float] = []
    for obs in recent:
        s = obs.get("sentiment_score")
        if s is not None:
            try:
                scores.append(float(s))
            except (TypeError, ValueError):
                continue

    if not scores:
        return {
            "direction": "neutral",
            "strength": 0.0,
            "confidence": 0.0,
            "avg_score": 0.0,
            "observation_count": 0,
        }

    avg_score = statistics.mean(scores)
    strength = abs(avg_score)

    # Direction
    if avg_score > 0.1:
        direction = "bullish"
    elif avg_score < -0.1:
        direction = "bearish"
    else:
        direction = "neutral"

    # Confidence based on sample size
    # 5 observations = 0.3, 20 = 0.7, 50+ = 0.95
    count = len(scores)
    if count >= 50:
        confidence = 0.95
    elif count >= 20:
        confidence = 0.7 + 0.25 * ((count - 20) / 30.0)
    elif count >= 5:
        confidence = 0.3 + 0.4 * ((count - 5) / 15.0)
    else:
        confidence = count * 0.06

    return {
        "direction": direction,
        "strength": round(strength, 4),
        "confidence": round(min(confidence, 1.0), 4),
        "avg_score": round(avg_score, 4),
        "observation_count": count,
    }


def _is_predictive(
    forward_returns: Dict[str, Dict[str, Optional[float]]],
    sample_sizes: Dict[str, int],
) -> bool:
    """Determine if extreme sentiment historically correlates with returns.

    Checks whether very_bullish and very_bearish buckets show meaningfully
    different forward returns (at any horizon) and have enough observations.

    Parameters
    ----------
    forward_returns : dict
        Output of ``_sentiment_forward_returns``.
    sample_sizes : dict
        Observation count per bucket.

    Returns
    -------
    bool
        True if there is evidence of predictive power.
    """
    bull_returns = forward_returns.get("very_bullish", {})
    bear_returns = forward_returns.get("very_bearish", {})

    bull_n = sample_sizes.get("very_bullish", 0)
    bear_n = sample_sizes.get("very_bearish", 0)

    # Need minimum observations in both tails
    if bull_n < _MIN_OBSERVATIONS_PER_BUCKET or bear_n < _MIN_OBSERVATIONS_PER_BUCKET:
        return False

    # Check if there is a meaningful difference at any horizon
    for period in ["1m", "3m", "6m", "12m"]:
        bull_ret = bull_returns.get(period)
        bear_ret = bear_returns.get(period)
        if bull_ret is not None and bear_ret is not None:
            diff = abs(bull_ret - bear_ret)
            if diff > 0.05:  # 5% difference threshold
                return True

    return False


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyze_sentiment_returns(
    sentiment_obs: List[Dict],
    prices: List[Dict],
) -> dict:
    """Analyse how historical sentiment maps to forward price returns.

    Parameters
    ----------
    sentiment_obs : list[dict]
        Sentiment observations. Each dict should have:
        - ``date`` (str, YYYY-MM-DD)
        - ``sentiment_score`` (float, -1.0 to +1.0)
        - ``source`` (str, optional)
    prices : list[dict]
        Daily price data. Each dict should have:
        - ``date`` (str, YYYY-MM-DD)
        - ``adjusted_close`` (float)

    Returns
    -------
    dict
        Keys:
        - ``current_sentiment``: direction, strength, confidence
        - ``historical_pattern``: per bucket, avg forward return at each horizon
        - ``sample_sizes``: observation count per bucket
        - ``is_predictive``: bool, whether extreme sentiment correlates with returns
        - ``warning``: str or None, if sample sizes are too small
    """
    if not sentiment_obs:
        return {
            "current_sentiment": _current_sentiment([]),
            "historical_pattern": {},
            "sample_sizes": {},
            "is_predictive": False,
            "warning": "no sentiment observations provided",
        }

    if not prices:
        return {
            "current_sentiment": _current_sentiment(sentiment_obs),
            "historical_pattern": {},
            "sample_sizes": {},
            "is_predictive": False,
            "warning": "no price data provided -- cannot compute forward returns",
        }

    # Step 1: Bucket observations
    buckets = _bucket_sentiment(sentiment_obs)

    # Step 2: Compute forward returns per bucket
    historical_pattern = _sentiment_forward_returns(buckets, prices)

    # Step 3: Sample sizes
    sample_sizes: Dict[str, int] = {
        name: len(obs_list) for name, obs_list in buckets.items()
    }

    # Step 4: Current sentiment
    current = _current_sentiment(sentiment_obs, days=30)

    # Step 5: Predictiveness check
    predictive = _is_predictive(historical_pattern, sample_sizes)

    # Step 6: Warning generation
    total_obs = sum(sample_sizes.values())
    warning: Optional[str] = None
    if total_obs < _MIN_TOTAL_OBSERVATIONS:
        warning = (
            f"only {total_obs} observations -- results may be unreliable "
            f"(recommend {_MIN_TOTAL_OBSERVATIONS}+)"
        )
    else:
        # Check individual buckets
        small_buckets = [
            name for name, count in sample_sizes.items()
            if 0 < count < _MIN_OBSERVATIONS_PER_BUCKET
        ]
        if small_buckets:
            warning = (
                f"small sample sizes in buckets: {', '.join(small_buckets)} -- "
                f"forward returns for these buckets may be unreliable"
            )

    return {
        "current_sentiment": current,
        "historical_pattern": historical_pattern,
        "sample_sizes": sample_sizes,
        "is_predictive": predictive,
        "warning": warning,
    }
