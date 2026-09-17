"""Valuation analytics -- 5-model weighted intrinsic value estimate.

Combines five independent valuation models with configurable weights:

1. **Owner-earnings** (weight 0.25): Buffett/Graham formula with 25% margin
   of safety haircut.
2. **DCF 3-scenario** (weight 0.30): 5-year projected FCF at bear/base/bull
   growth rates, discounted at estimated WACC, plus Gordon-growth terminal value.
3. **EV/EBITDA relative** (weight 0.20): Backs out EBITDA from PE and EPS,
   applies sector-typical multiple, converts to per-share equity value.
4. **Graham number** (weight 0.15): Classic sqrt(22.5 * EPS * BVPS) formula.
5. **PEG value** (weight 0.10): PEG-ratio-based fair value estimate.

Pure computation -- no API calls.  Every model tolerates missing inputs and
returns ``None`` when it cannot compute; the weighted average is built from
whichever models succeed, with weights renormalised proportionally.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model weights -- must sum to 1.0.  When a model returns None its weight
# is redistributed proportionally among the models that succeeded.
# ---------------------------------------------------------------------------
WEIGHT_OE: float = 0.25
WEIGHT_DCF: float = 0.30
WEIGHT_EV_EBITDA: float = 0.20
WEIGHT_GRAHAM: float = 0.15
WEIGHT_PEG: float = 0.10

# ---------------------------------------------------------------------------
# Default assumptions
# ---------------------------------------------------------------------------
RISK_FREE: float = 0.043           # 10-yr US Treasury proxy
EQUITY_PREMIUM: float = 0.05       # long-run equity risk premium
TERMINAL_GROWTH: float = 0.025     # perpetuity growth for Gordon model
DCF_YEARS: int = 5

_BETA: float = 1.0                 # market beta (no ticker-level beta in v1)
_DEFAULT_EV_EBITDA_MULTIPLE: float = 12.0
_GRAHAM_BASE_MULTIPLIER: float = 8.5
_OWNER_EARNINGS_MOS_DISCOUNT: float = 0.25  # 25% haircut


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_get(d: dict, *keys: str) -> Optional[float]:
    """Retrieve a nested numeric value from a dict, returning None on miss."""
    for key in keys:
        val = d.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


def _growth_rate(f: dict) -> Optional[float]:
    """Best available growth rate from fundamentals (decimal fraction).

    Prefers eps_growth, falls back to revenue_growth.
    """
    g = _safe_get(f, "eps_growth", "eps_cagr_3y", "earnings_growth")
    if g is not None:
        return g
    return _safe_get(f, "revenue_growth", "revenue_cagr_3y")


def _wacc() -> float:
    """Simplified WACC via CAPM: Rf + beta * ERP."""
    return RISK_FREE + _BETA * EQUITY_PREMIUM


def _shares_outstanding(f: dict, market_price: float) -> Optional[float]:
    """Derive share count from fundamentals for total-to-per-share conversion."""
    shares = _safe_get(f, "shares_outstanding", "shares")
    if shares is not None and shares > 0:
        return shares
    # Fallback: market_cap / price
    mcap = _safe_get(f, "market_cap")
    if mcap is not None and mcap > 0 and market_price > 0:
        return mcap / market_price
    return None


def _to_per_share(
    total_value: float, f: dict, market_price: float
) -> Optional[float]:
    """Convert a total-firm value to per-share."""
    if total_value <= 0 or market_price <= 0:
        return None
    shares = _shares_outstanding(f, market_price)
    if shares is not None and shares > 0:
        return total_value / shares
    return None


# ---------------------------------------------------------------------------
# Model 1 -- Owner-earnings value (Buffett / Graham adapted)
# ---------------------------------------------------------------------------

def _owner_earnings_value(f: dict, market_price: float) -> Optional[float]:
    """Estimate intrinsic per-share value using Buffett's owner-earnings concept.

    Owner earnings are approximated as trailing FCF.  The fair value is then
    derived from Graham's adapted formula:

        value = owner_earnings * (8.5 + 2 * g)

    where g is expected annual growth as a percentage (e.g. 7 for 7%).
    A 25% margin-of-safety discount is applied.

    Parameters
    ----------
    f : dict
        Fundamentals dict. Expected keys: ``fcf_ttm`` or ``free_cash_flow``,
        a growth metric, ``shares_outstanding`` or ``market_cap``.
    market_price : float
        Current market price per share.

    Returns
    -------
    Optional[float]
        Per-share fair value, or None when inputs are insufficient.
    """
    fcf = _safe_get(f, "fcf_ttm", "free_cash_flow", "fcf")
    if fcf is None or fcf <= 0:
        logger.debug("owner-earnings: skipped -- FCF unavailable or non-positive")
        return None

    growth = _growth_rate(f)
    if growth is None:
        logger.debug("owner-earnings: skipped -- no growth rate available")
        return None

    growth_pct = growth * 100.0
    multiplier = _GRAHAM_BASE_MULTIPLIER + 2.0 * growth_pct
    if multiplier <= 0:
        logger.debug("owner-earnings: Graham multiplier non-positive (%.2f)", multiplier)
        return None

    raw_value = fcf * multiplier
    discounted = raw_value * (1.0 - _OWNER_EARNINGS_MOS_DISCOUNT)

    per_share = _to_per_share(discounted, f, market_price)
    if per_share is not None:
        return per_share

    # Fallback: if FCF looks per-share already (small magnitude)
    eps = _safe_get(f, "eps", "earnings_per_share")
    if eps is not None and eps > 0:
        # Use EPS-based Graham formula directly
        raw_eps = eps * multiplier
        return raw_eps * (1.0 - _OWNER_EARNINGS_MOS_DISCOUNT)

    return None


# ---------------------------------------------------------------------------
# Model 2 -- DCF 3-scenario
# ---------------------------------------------------------------------------

def _dcf_three_scenario(f: dict) -> Optional[dict]:
    """Discounted cash-flow model with bear/base/bull scenarios.

    Projects trailing FCF forward for 5 years at three growth rates, then
    adds a terminal value (Gordon growth model).

    Parameters
    ----------
    f : dict
        Fundamentals dict. Expected keys: ``fcf_ttm`` or ``free_cash_flow``,
        a growth metric.

    Returns
    -------
    Optional[dict]
        Dict with keys ``bear``, ``base``, ``bull``, ``weighted`` (total firm
        values), or None when inputs are insufficient.
    """
    fcf = _safe_get(f, "fcf_ttm", "free_cash_flow", "fcf")
    if fcf is None or fcf <= 0:
        logger.debug("DCF: skipped -- FCF unavailable or non-positive")
        return None

    growth = _growth_rate(f)
    if growth is None:
        logger.debug("DCF: skipped -- no growth rate available")
        return None

    wacc = _wacc()

    scenarios: Dict[str, float] = {}
    for label, multiplier in [("bear", 0.5), ("base", 1.0), ("bull", 1.5)]:
        g = growth * multiplier
        pv_fcfs = 0.0
        projected_fcf = fcf
        for year in range(1, DCF_YEARS + 1):
            projected_fcf *= (1.0 + g)
            pv_fcfs += projected_fcf / ((1.0 + wacc) ** year)

        # Terminal value via Gordon growth model
        if wacc <= TERMINAL_GROWTH:
            terminal_pv = 0.0
        else:
            terminal_value = (
                projected_fcf * (1.0 + TERMINAL_GROWTH) / (wacc - TERMINAL_GROWTH)
            )
            terminal_pv = terminal_value / ((1.0 + wacc) ** DCF_YEARS)

        scenarios[label] = pv_fcfs + terminal_pv

    scenarios["weighted"] = (
        scenarios["bear"] + scenarios["base"] + scenarios["bull"]
    ) / 3.0
    return scenarios


# ---------------------------------------------------------------------------
# Model 3 -- EV/EBITDA relative valuation
# ---------------------------------------------------------------------------

def _ev_ebitda_relative(f: dict, market_price: float) -> Optional[float]:
    """Approximate intrinsic per-share value via EV/EBITDA multiple.

    Back-solves EBITDA from PE and market price, applies a sector-typical
    multiple, and subtracts estimated debt per share.

    Parameters
    ----------
    f : dict
        Fundamentals dict. Expected keys: ``pe`` or ``pe_ratio``,
        optionally ``pb`` or ``price_to_book``, ``debt_equity``.
    market_price : float
        Current market price per share.

    Returns
    -------
    Optional[float]
        Per-share equity fair value, or None.
    """
    pe = _safe_get(f, "pe", "pe_ratio", "trailing_pe")
    if pe is None or pe <= 0:
        logger.debug("EV/EBITDA: skipped -- PE unavailable or non-positive")
        return None
    if market_price <= 0:
        return None

    eps = market_price / pe
    if eps <= 0:
        return None

    # Approximate EBITDA per share (EBITDA typically ~1.5x net income)
    ebitda_per_share = eps * 1.5
    ev_per_share = ebitda_per_share * _DEFAULT_EV_EBITDA_MULTIPLE

    # Subtract debt per share if possible
    debt_per_share = 0.0
    pb = _safe_get(f, "pb", "price_to_book", "pb_ratio")
    de = _safe_get(f, "debt_equity", "debt_to_equity")
    if pb is not None and pb > 0 and de is not None:
        bvps = market_price / pb
        debt_per_share = bvps * de

    equity_value = ev_per_share - debt_per_share
    if equity_value <= 0:
        logger.debug("EV/EBITDA: equity value per share non-positive (%.2f)", equity_value)
        return None

    return equity_value


# ---------------------------------------------------------------------------
# Model 4 -- Graham number
# ---------------------------------------------------------------------------

def _graham_number(f: dict) -> Optional[float]:
    """Classic Graham number: sqrt(22.5 * EPS * BVPS).

    Parameters
    ----------
    f : dict
        Fundamentals dict. Expected keys: ``eps`` or ``earnings_per_share``,
        ``book_value_per_share`` or ``bvps``.

    Returns
    -------
    Optional[float]
        Graham number (fair value per share), or None.
    """
    eps = _safe_get(f, "eps", "earnings_per_share")
    bvps = _safe_get(f, "book_value_per_share", "bvps")

    if eps is None or eps <= 0:
        logger.debug("Graham: skipped -- EPS unavailable or non-positive")
        return None
    if bvps is None or bvps <= 0:
        logger.debug("Graham: skipped -- BVPS unavailable or non-positive")
        return None

    product = 22.5 * eps * bvps
    if product <= 0:
        return None

    return math.sqrt(product)


# ---------------------------------------------------------------------------
# Model 5 -- PEG value
# ---------------------------------------------------------------------------

def _peg_value(f: dict, market_price: float) -> Optional[float]:
    """PEG-ratio-based fair value estimate.

    A PEG of 1.0 is considered fair value.  Fair price is therefore:
        fair_price = EPS * growth_pct * 1.0

    where growth_pct is the expected earnings growth rate as a percentage.

    Parameters
    ----------
    f : dict
        Fundamentals dict. Expected keys: ``eps``, a growth metric.
    market_price : float
        Current market price per share.

    Returns
    -------
    Optional[float]
        PEG-implied fair value per share, or None.
    """
    eps = _safe_get(f, "eps", "earnings_per_share")
    if eps is None or eps <= 0:
        logger.debug("PEG: skipped -- EPS unavailable or non-positive")
        return None

    growth = _growth_rate(f)
    if growth is None or growth <= 0:
        logger.debug("PEG: skipped -- growth rate unavailable or non-positive")
        return None

    growth_pct = growth * 100.0
    if growth_pct <= 0:
        return None

    # Fair PEG = 1.0 => fair PE = growth_pct => fair price = EPS * growth_pct
    fair_value = eps * growth_pct
    return fair_value


# ---------------------------------------------------------------------------
# Verdict helper
# ---------------------------------------------------------------------------

def _verdict(margin_of_safety: float) -> str:
    """Classify valuation based on margin of safety.

    Parameters
    ----------
    margin_of_safety : float
        1 - (market_price / intrinsic_value). Positive means undervalued.

    Returns
    -------
    str
        One of ``"undervalued"``, ``"fairly valued"``, ``"overvalued"``.
    """
    if margin_of_safety > 0.15:
        return "undervalued"
    elif margin_of_safety < -0.15:
        return "overvalued"
    return "fairly valued"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def compute_valuation(fundamentals: dict, market_price: float) -> dict:
    """Compute a weighted-average intrinsic value from five valuation models.

    Each model runs independently and tolerates missing inputs by returning
    None.  The weighted average is built from whichever models succeed,
    with weights renormalised proportionally.

    Parameters
    ----------
    fundamentals : dict
        Point-in-time fundamentals for a single ticker.  Expected keys vary
        by model but may include: ``fcf_ttm``, ``eps``, ``pe``, ``pb``,
        ``book_value_per_share``, ``debt_equity``, ``eps_growth``,
        ``revenue_growth``, ``shares_outstanding``, ``market_cap``.
    market_price : float
        Current market price per share.

    Returns
    -------
    dict
        Keys: ``intrinsic_value``, ``market_price``, ``margin_of_safety``,
        ``models`` (per-model results), ``verdict``
        ("undervalued"/"fairly valued"/"overvalued").
    """
    f = fundamentals
    models: Dict[str, Any] = {}
    weighted_parts: List[Tuple[str, float, float]] = []  # (name, weight, value)

    # -- Model 1: Owner-earnings --
    oe = _owner_earnings_value(f, market_price)
    if oe is not None and oe > 0:
        models["owner_earnings"] = {"value": round(oe, 2), "weight": WEIGHT_OE}
        weighted_parts.append(("owner_earnings", WEIGHT_OE, oe))
    else:
        models["owner_earnings"] = {"value": None, "error": "insufficient inputs"}

    # -- Model 2: DCF 3-scenario --
    dcf_result = _dcf_three_scenario(f)
    dcf_per_share: Optional[float] = None
    if dcf_result is not None:
        dcf_per_share = _to_per_share(dcf_result["weighted"], f, market_price)
        scenario_ps: Dict[str, Optional[float]] = {}
        for key in ("bear", "base", "bull", "weighted"):
            ps = _to_per_share(dcf_result[key], f, market_price)
            scenario_ps[key] = round(ps, 2) if ps is not None else None

        if dcf_per_share is not None and dcf_per_share > 0:
            models["dcf"] = {
                "value": round(dcf_per_share, 2),
                "scenarios": scenario_ps,
                "weight": WEIGHT_DCF,
            }
            weighted_parts.append(("dcf", WEIGHT_DCF, dcf_per_share))
        else:
            models["dcf"] = {"value": None, "error": "per-share conversion failed"}
    else:
        models["dcf"] = {"value": None, "error": "insufficient inputs"}

    # -- Model 3: EV/EBITDA relative --
    ev = _ev_ebitda_relative(f, market_price)
    if ev is not None and ev > 0:
        models["ev_ebitda"] = {"value": round(ev, 2), "weight": WEIGHT_EV_EBITDA}
        weighted_parts.append(("ev_ebitda", WEIGHT_EV_EBITDA, ev))
    else:
        models["ev_ebitda"] = {"value": None, "error": "insufficient inputs"}

    # -- Model 4: Graham number --
    gn = _graham_number(f)
    if gn is not None and gn > 0:
        models["graham_number"] = {"value": round(gn, 2), "weight": WEIGHT_GRAHAM}
        weighted_parts.append(("graham_number", WEIGHT_GRAHAM, gn))
    else:
        models["graham_number"] = {"value": None, "error": "insufficient inputs"}

    # -- Model 5: PEG value --
    peg = _peg_value(f, market_price)
    if peg is not None and peg > 0:
        models["peg"] = {"value": round(peg, 2), "weight": WEIGHT_PEG}
        weighted_parts.append(("peg", WEIGHT_PEG, peg))
    else:
        models["peg"] = {"value": None, "error": "insufficient inputs"}

    # -- Weighted average --
    if not weighted_parts:
        return {
            "intrinsic_value": None,
            "market_price": market_price,
            "margin_of_safety": None,
            "models": models,
            "verdict": "insufficient data",
            "models_succeeded": 0,
        }

    total_weight = sum(w for _, w, _ in weighted_parts)
    intrinsic_value = sum(w * v for _, w, v in weighted_parts) / total_weight
    intrinsic_value = round(intrinsic_value, 2)

    mos = round(1.0 - (market_price / intrinsic_value), 4) if intrinsic_value > 0 else None

    models["_meta"] = {
        "total_weight": round(total_weight, 4),
        "models_succeeded": len(weighted_parts),
        "models_used": [name for name, _, _ in weighted_parts],
    }

    # -- Reverse DCF --
    reverse_dcf = compute_reverse_dcf(fundamentals, market_price)

    return {
        "intrinsic_value": intrinsic_value,
        "market_price": market_price,
        "margin_of_safety": mos,
        "models": models,
        "reverse_dcf": reverse_dcf,
        "verdict": _verdict(mos) if mos is not None else "insufficient data",
    }


# ---------------------------------------------------------------------------
# Reverse DCF -- what growth does the current price imply?
# ---------------------------------------------------------------------------

def compute_reverse_dcf(
    fundamentals: dict,
    market_price: float,
    wacc: float = _WACC,
    terminal_growth: float = _TERMINAL_GROWTH,
    projection_years: int = _DCF_PROJECTION_YEARS,
) -> dict:
    """Reverse DCF: given current price, solve for the implied FCF growth rate.

    Instead of projecting growth → fair value, this starts from the market price
    and works backward to find what growth rate the market is implying. This is
    more actionable than forward DCF because it converts valuation into a testable
    hypothesis.

    Returns:
        dict with implied_fcf_cagr, implied_revenue_cagr, market_assumptions,
        and a verdict on whether those assumptions are realistic.
    """
    fcf = fundamentals.get("free_cash_flow")
    shares = fundamentals.get("shares_outstanding")
    revenue = fundamentals.get("revenue")
    ev_sales = fundamentals.get("ev_sales")
    market_cap = fundamentals.get("market_cap")
    enterprise_value = fundamentals.get("enterprise_value")

    result: dict = {
        "implied_fcf_cagr": None,
        "implied_revenue_cagr": None,
        "current_fcf": fcf,
        "market_assumptions": None,
        "verdict": None,
    }

    if not market_price or market_price <= 0:
        result["verdict"] = "insufficient data (no market price)"
        return result

    # Use enterprise value if available, else market cap
    ev = enterprise_value or market_cap
    if not ev or ev <= 0:
        result["verdict"] = "insufficient data (no EV or market cap)"
        return result

    # --- Implied FCF CAGR ---
    if fcf and fcf > 0:
        # Solve: EV = Σ(FCF₀ × (1+g)^t / (1+wacc)^t) + TV
        # TV = FCF₀ × (1+g)^n × (1+terminal_g) / (wacc - terminal_g) / (1+wacc)^n
        # Use binary search for g
        def _ev_at_growth(g: float) -> float:
            pv = 0.0
            for t in range(1, projection_years + 1):
                pv += fcf * ((1 + g) ** t) / ((1 + wacc) ** t)
            terminal_fcf = fcf * ((1 + g) ** projection_years) * (1 + terminal_growth)
            tv = terminal_fcf / (wacc - terminal_growth)
            pv += tv / ((1 + wacc) ** projection_years)
            return pv

        # Binary search for implied growth rate
        lo, hi = -0.30, 1.00  # -30% to +100% growth
        for _ in range(100):
            mid = (lo + hi) / 2
            if _ev_at_growth(mid) < ev:
                lo = mid
            else:
                hi = mid

        implied_fcf_cagr = round((lo + hi) / 2, 4)
        result["implied_fcf_cagr"] = implied_fcf_cagr

        # Historical FCF for comparison
        historical_cagr = fundamentals.get("fcf_cagr_3y") or fundamentals.get("revenue_cagr_3y")

        result["market_assumptions"] = {
            "implied_annual_fcf_growth": f"{implied_fcf_cagr*100:.1f}%",
            "for_years": projection_years,
            "terminal_growth": f"{terminal_growth*100:.1f}%",
            "wacc": f"{wacc*100:.1f}%",
        }

        # Verdict
        if implied_fcf_cagr > 0.30:
            result["verdict"] = f"Market implies {implied_fcf_cagr*100:.0f}% annual FCF growth — aggressive, requires exceptional execution"
        elif implied_fcf_cagr > 0.15:
            result["verdict"] = f"Market implies {implied_fcf_cagr*100:.0f}% annual FCF growth — optimistic but achievable for strong growers"
        elif implied_fcf_cagr > 0.05:
            result["verdict"] = f"Market implies {implied_fcf_cagr*100:.0f}% annual FCF growth — moderate, reasonable for established companies"
        elif implied_fcf_cagr > 0:
            result["verdict"] = f"Market implies {implied_fcf_cagr*100:.0f}% annual FCF growth — conservative, potential upside if growth exceeds this"
        else:
            result["verdict"] = f"Market implies {implied_fcf_cagr*100:.0f}% FCF decline — priced for deterioration"

    else:
        result["verdict"] = "insufficient data (negative or zero FCF — reverse DCF requires positive FCF)"

    # --- Implied Revenue CAGR (from EV/Sales) ---
    if revenue and revenue > 0 and ev_sales:
        # If EV/Sales stays constant, implied revenue CAGR = price return
        # More useful: what revenue is needed to justify current EV at a target EV/Sales
        target_ev_sales = 5.0  # mature company target
        implied_revenue_at_maturity = ev / target_ev_sales
        if revenue > 0:
            implied_rev_cagr = ((implied_revenue_at_maturity / revenue) ** (1.0 / projection_years)) - 1
            result["implied_revenue_cagr"] = round(implied_rev_cagr, 4)

    return result
