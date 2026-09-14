"""SEC EDGAR XBRL fundamentals ingestion.

Pulls quarterly financial data from the EDGAR Company Facts API:
    https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json

SEC requires a real contact string in the User-Agent header. Set the
``EDGAR_USER_AGENT`` env var before calling:
    export EDGAR_USER_AGENT='Your Name you@example.com'

Usage:
    python -m stock_research.ingestion.sec AAPL
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_REQUEST_TIMEOUT = 20  # seconds

# XBRL concept name priority per metric -- try each in order, use the first
# one the filer actually reports.
_CONCEPTS: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
    ],
    "net_income": ["NetIncomeLoss"],
    "assets": ["Assets"],
    "liabilities": ["Liabilities"],
    "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "shares_outstanding": [
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding",
    ],
}

# Cache the ticker map across calls within the same process.
_ticker_map_cache: Optional[dict[str, tuple[str, str, str]]] = None
_ticker_map_loaded_at: Optional[datetime] = None


def fetch_fundamentals(ticker: str) -> list[dict]:
    """Return quarterly fundamental records for *ticker*.

    Each record matches the ``company_fundamentals`` DuckDB schema:
    ticker, period, period_end, revenue, net_income, eps,
    operating_cash_flow, capex, free_cash_flow, shares_outstanding,
    revenue_yoy_growth, source, updated_at.
    """
    ticker = ticker.upper()
    user_agent = _get_user_agent()
    cik, company_name, sic = _lookup_cik(ticker, user_agent)
    facts = _fetch_company_facts(cik, user_agent)
    return _parse_quarterly_facts(facts, ticker, cik)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get_user_agent() -> str:
    ua = os.environ.get("EDGAR_USER_AGENT", "").strip()
    if not ua:
        raise RuntimeError(
            "EDGAR_USER_AGENT env var is empty. SEC EDGAR requires a real "
            "contact string like 'Your Name you@example.com'. Set it before "
            "calling: export EDGAR_USER_AGENT='Your Name you@example.com'"
        )
    return ua


def _get_json(url: str, user_agent: str) -> dict[str, Any]:
    """GET a JSON endpoint with the required User-Agent header."""
    req = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"EDGAR HTTP {exc.code} on {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"EDGAR network error on {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"EDGAR response was not JSON: {exc}") from exc


def _lookup_cik(ticker: str, user_agent: str) -> tuple[str, str, str]:
    """Look up (cik, company_name, sic) for a ticker.

    Downloads the SEC ticker map (cached for 24 h) and then fetches
    the submissions endpoint for the SIC code.
    """
    global _ticker_map_cache, _ticker_map_loaded_at

    now = datetime.now(tz=timezone.utc)
    stale = (
        _ticker_map_cache is None
        or _ticker_map_loaded_at is None
        or (now - _ticker_map_loaded_at).total_seconds() > 86400
    )

    if stale:
        raw = _get_json(_TICKER_MAP_URL, user_agent)
        _ticker_map_cache = {}
        for entry in raw.values():
            t = str(entry.get("ticker", "")).upper()
            if not t:
                continue
            cik_int = int(entry["cik_str"])
            cik_str = f"{cik_int:010d}"
            _ticker_map_cache[t] = (cik_str, entry.get("title", ""), "")
        _ticker_map_loaded_at = now

    assert _ticker_map_cache is not None
    hit = _ticker_map_cache.get(ticker)
    if not hit:
        raise ValueError(f"Ticker {ticker!r} not found in EDGAR ticker map")

    cik, title, _ = hit

    # Fetch submissions for SIC code.
    sic = ""
    try:
        time.sleep(0.12)  # rate-limit courtesy
        sub = _get_json(f"https://data.sec.gov/submissions/CIK{cik}.json", user_agent)
        sic = str(sub.get("sic", ""))
    except RuntimeError:
        pass

    return cik, title, sic


def _fetch_company_facts(cik: str, user_agent: str) -> dict[str, Any]:
    """Fetch the XBRL Company Facts JSON for a given CIK."""
    time.sleep(0.12)  # SEC asks for <= 10 req/s
    return _get_json(_COMPANY_FACTS_URL.format(cik=cik), user_agent)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_quarterly_facts(
    facts: dict[str, Any], ticker: str, cik: str
) -> list[dict]:
    """Extract quarterly records from XBRL Company Facts.

    Returns a list of dicts matching the company_fundamentals schema.
    Calculates derived fields: free_cash_flow, revenue_yoy_growth.
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    dei = facts.get("facts", {}).get("dei", {})
    source_groups = (us_gaap, dei)

    def _get_quarterly_points(concept_names: list[str]) -> dict[str, float]:
        """Return {period_end: value} for quarterly datapoints."""
        for name in concept_names:
            for group in source_groups:
                entry = group.get(name)
                if not entry:
                    continue
                units = entry.get("units", {})
                # Prefer USD, then shares, then whatever
                unit_keys = sorted(
                    units.keys(),
                    key=lambda k: 0 if k == "USD" else (1 if k == "shares" else 2),
                )
                for unit in unit_keys:
                    points = units[unit]
                    if not points:
                        continue
                    # Filter to quarterly filings (10-Q with fp like Q1/Q2/Q3,
                    # or 10-K for Q4-equivalent annual).
                    quarterly: dict[str, float] = {}
                    for p in points:
                        form = p.get("form", "")
                        fp = p.get("fp") or ""
                        end = p.get("end") or ""
                        val = p.get("val")
                        if not end or not isinstance(val, (int, float)):
                            continue
                        # Accept 10-Q quarterly filings and 10-K annual
                        if form in ("10-Q", "10-K"):
                            quarterly[end] = float(val)
                    if quarterly:
                        return quarterly
        return {}

    # Gather all metrics keyed by period_end date.
    revenue_pts = _get_quarterly_points(_CONCEPTS["revenue"])
    net_income_pts = _get_quarterly_points(_CONCEPTS["net_income"])
    eps_pts = _get_quarterly_points(_CONCEPTS["eps"])
    ocf_pts = _get_quarterly_points(_CONCEPTS["operating_cash_flow"])
    capex_pts = _get_quarterly_points(_CONCEPTS["capex"])
    shares_pts = _get_quarterly_points(_CONCEPTS["shares_outstanding"])

    # Collect all unique period_end dates across metrics.
    all_dates: set[str] = set()
    for pts in (revenue_pts, net_income_pts, eps_pts, ocf_pts, capex_pts, shares_pts):
        all_dates.update(pts.keys())

    now_iso = datetime.now(tz=timezone.utc).isoformat()
    records: list[dict] = []

    for period_end in sorted(all_dates):
        revenue = revenue_pts.get(period_end)
        ocf = ocf_pts.get(period_end)
        capex_val = capex_pts.get(period_end)

        # free_cash_flow = operating_cash_flow - abs(capex)
        fcf: Optional[float] = None
        if ocf is not None and capex_val is not None:
            fcf = ocf - abs(capex_val)
        elif ocf is not None:
            fcf = ocf  # proxy when capex unavailable

        # Determine fiscal period label from the date (approximate).
        try:
            dt = datetime.strptime(period_end, "%Y-%m-%d")
            month = dt.month
            if month <= 3:
                period = f"Q1 {dt.year}"
            elif month <= 6:
                period = f"Q2 {dt.year}"
            elif month <= 9:
                period = f"Q3 {dt.year}"
            else:
                period = f"Q4 {dt.year}"
        except ValueError:
            period = period_end

        records.append({
            "ticker": ticker,
            "period": period,
            "period_end": period_end,
            "revenue": revenue,
            "net_income": net_income_pts.get(period_end),
            "eps": eps_pts.get(period_end),
            "operating_cash_flow": ocf,
            "capex": capex_val,
            "free_cash_flow": fcf,
            "shares_outstanding": shares_pts.get(period_end),
            "revenue_yoy_growth": None,  # filled below
            "source": "sec_xbrl",
            "updated_at": now_iso,
        })

    # Calculate revenue_yoy_growth: compare to same quarter prior year.
    # Build a lookup by (quarter_label_without_year, year) for matching.
    by_quarter: dict[tuple[str, int], dict] = {}
    for rec in records:
        try:
            dt = datetime.strptime(rec["period_end"], "%Y-%m-%d")
            quarter_key = f"Q{(dt.month - 1) // 3 + 1}"
            by_quarter[(quarter_key, dt.year)] = rec
        except ValueError:
            continue

    for (qk, year), rec in by_quarter.items():
        prior = by_quarter.get((qk, year - 1))
        if prior and prior.get("revenue") and rec.get("revenue") and prior["revenue"] != 0:
            rec["revenue_yoy_growth"] = (rec["revenue"] - prior["revenue"]) / abs(prior["revenue"])

    return records


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m stock_research.ingestion.sec TICKER", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1].upper()
    try:
        results = fetch_fundamentals(ticker)
    except (RuntimeError, ValueError) as exc:
        logger.error("%s", exc)
        sys.exit(1)

    print(f"Fetched {len(results)} quarterly records for {ticker}")
    for rec in results[-4:]:
        print(
            f"  {rec['period']:>8s}  "
            f"rev={rec['revenue']!s:>15s}  "
            f"ni={rec['net_income']!s:>15s}  "
            f"eps={rec['eps']!s:>8s}  "
            f"fcf={rec['free_cash_flow']!s:>15s}  "
            f"yoy={rec['revenue_yoy_growth']!s:>8s}"
        )
