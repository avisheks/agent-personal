"""Build a structured research packet JSON from DuckDB data.

The research packet is consumed by the LLM analyst agents (Bull, Contrarian,
Adjudicator) and must contain all quantitative data they need so they never
have to calculate metrics themselves.

CLI usage::

    python -m stock_research.packet_builder TICKER [--db PATH] [--peers T1,T2,T3]

The output is a JSON object written to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from stock_research import db as research_db


# ---------------------------------------------------------------------------
# JSON serialisation helper
# ---------------------------------------------------------------------------

def _json_serial(obj: Any) -> Any:
    """Fallback serialiser for datetime / date / Path objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not JSON serialisable")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_packet(
    ticker: str,
    db_path: Optional[str] = None,
    peers: Optional[list[str]] = None,
) -> dict:
    """Assemble a full research packet for *ticker*.

    Args:
        ticker: Stock ticker symbol (e.g. ``"AAPL"``).
        db_path: Override path to the DuckDB file.
        peers: List of peer ticker symbols for comparison. If ``None``,
               the packet will skip the peer_comparison section.

    Returns:
        A dict matching the research packet spec from SKILL.md.
    """
    conn = research_db.get_connection(db_path)
    ticker = ticker.upper()

    packet: dict[str, Any] = {
        "ticker": ticker,
        "generated_at": datetime.utcnow().isoformat(),
        "snapshot": _build_snapshot(conn, ticker),
        "fundamentals_10y": _build_fundamentals_10y(conn, ticker),
        "earnings_history": _build_earnings_history(conn, ticker),
        "peer_comparison": _build_peer_comparison(conn, ticker, peers or []),
        "valuation_models": _build_valuation_models(conn, ticker),
        "risk_metrics": _build_risk_metrics(conn, ticker),
        "recent_sentiment": _build_sentiment_summary(conn, ticker),
        "historical_sentiment_returns": _build_sentiment_returns(conn, ticker),
        "investor_claims": _build_claims(conn, ticker),
        "data_quality": _build_data_quality(conn, ticker),
    }

    conn.close()
    return packet


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_snapshot(conn: Any, ticker: str) -> dict:
    """Latest fundamentals + valuation combined into a single snapshot.

    Returns a dict with the most recent quarter's fundamentals and the most
    recent valuation metrics.
    """
    fundamentals = research_db.query_fundamentals(conn, ticker, limit=1)
    valuations = research_db.query_valuation(conn, ticker, limit=1)
    prices = research_db.query_prices(conn, ticker)

    snapshot: dict[str, Any] = {}

    if fundamentals:
        f = fundamentals[0]
        snapshot["latest_quarter"] = f.get("period")
        snapshot["period_end"] = f.get("period_end")
        snapshot["revenue"] = f.get("revenue")
        snapshot["revenue_yoy_growth"] = f.get("revenue_yoy_growth")
        snapshot["gross_margin"] = f.get("gross_margin")
        snapshot["operating_margin"] = f.get("operating_margin")
        snapshot["net_income"] = f.get("net_income")
        snapshot["eps"] = f.get("eps")
        snapshot["operating_cash_flow"] = f.get("operating_cash_flow")
        snapshot["capex"] = f.get("capex")
        snapshot["free_cash_flow"] = f.get("free_cash_flow")
        snapshot["cash"] = f.get("cash")
        snapshot["debt"] = f.get("debt")
        snapshot["shares_outstanding"] = f.get("shares_outstanding")
        snapshot["sbc"] = f.get("sbc")
        snapshot["roe"] = f.get("roe")
        snapshot["roic"] = f.get("roic")

    if valuations:
        v = valuations[0]
        snapshot["valuation_date"] = v.get("date")
        snapshot["market_cap"] = v.get("market_cap")
        snapshot["pe"] = v.get("pe")
        snapshot["forward_pe"] = v.get("forward_pe")
        snapshot["ev_sales"] = v.get("ev_sales")
        snapshot["ev_ebitda"] = v.get("ev_ebitda")
        snapshot["price_sales"] = v.get("price_sales")
        snapshot["fcf_yield"] = v.get("fcf_yield")
        snapshot["enterprise_value"] = v.get("enterprise_value")

    if prices:
        latest = prices[0]  # Already sorted desc.
        snapshot["latest_price_date"] = latest.get("date")
        snapshot["latest_close"] = latest.get("adjusted_close") or latest.get("close")
        snapshot["latest_volume"] = latest.get("volume")

    return snapshot


def _build_fundamentals_10y(conn: Any, ticker: str) -> list[dict]:
    """Quarterly fundamentals history (up to ~40 quarters / 10 years).

    Returns a list of dicts sorted oldest-first for charting convenience.
    """
    rows = research_db.query_fundamentals(conn, ticker, limit=40)
    # query_fundamentals returns descending; reverse for chronological.
    rows.reverse()

    cleaned = []
    for r in rows:
        cleaned.append({
            "period": r.get("period"),
            "period_end": r.get("period_end"),
            "revenue": r.get("revenue"),
            "revenue_yoy_growth": r.get("revenue_yoy_growth"),
            "gross_margin": r.get("gross_margin"),
            "operating_margin": r.get("operating_margin"),
            "net_income": r.get("net_income"),
            "eps": r.get("eps"),
            "operating_cash_flow": r.get("operating_cash_flow"),
            "free_cash_flow": r.get("free_cash_flow"),
            "sbc": r.get("sbc"),
            "roe": r.get("roe"),
            "roic": r.get("roic"),
        })
    return cleaned


def _build_earnings_history(conn: Any, ticker: str) -> list[dict]:
    """Beat/miss history with guidance changes and post-announcement returns.

    Returns a list sorted oldest-first.
    """
    rows = research_db.query_earnings(conn, ticker, limit=40)
    rows.reverse()

    result = []
    for r in rows:
        eps_surprise = r.get("eps_surprise_pct")
        rev_surprise = r.get("revenue_surprise_pct")

        # Derive a simple beat/miss label.
        if eps_surprise is not None:
            if eps_surprise > 0:
                verdict = "beat"
            elif eps_surprise < 0:
                verdict = "miss"
            else:
                verdict = "inline"
        else:
            verdict = "unknown"

        result.append({
            "fiscal_period": r.get("fiscal_period"),
            "announcement_date": r.get("announcement_date"),
            "eps_actual": r.get("eps_actual"),
            "eps_estimate": r.get("eps_estimate"),
            "eps_surprise_pct": eps_surprise,
            "revenue_actual": r.get("revenue_actual"),
            "revenue_estimate": r.get("revenue_estimate"),
            "revenue_surprise_pct": rev_surprise,
            "verdict": verdict,
            "guidance": r.get("guidance"),
            "guidance_change": r.get("guidance_change"),
            "stock_return_1d": r.get("stock_return_1d"),
            "stock_return_5d": r.get("stock_return_5d"),
            "stock_return_20d": r.get("stock_return_20d"),
        })
    return result


def _build_peer_comparison(
    conn: Any,
    ticker: str,
    peers: list[str],
) -> dict:
    """Relative ranking of *ticker* against *peers* on key metrics.

    If no peers are provided, returns an empty structure with a note.
    """
    if not peers:
        return {"note": "No peers configured; skipping peer comparison."}

    all_tickers = [ticker] + [p.upper() for p in peers]
    comparison: dict[str, Any] = {"tickers": all_tickers, "metrics": {}}

    # Gather the latest fundamentals and valuation for each ticker.
    data_rows: list[dict] = []
    for t in all_tickers:
        fund = research_db.query_fundamentals(conn, t, limit=1)
        val = research_db.query_valuation(conn, t, limit=1)
        row: dict[str, Any] = {"ticker": t}
        if fund:
            f = fund[0]
            row["revenue"] = f.get("revenue")
            row["revenue_yoy_growth"] = f.get("revenue_yoy_growth")
            row["gross_margin"] = f.get("gross_margin")
            row["operating_margin"] = f.get("operating_margin")
            row["roe"] = f.get("roe")
            row["roic"] = f.get("roic")
            row["free_cash_flow"] = f.get("free_cash_flow")
        if val:
            v = val[0]
            row["pe"] = v.get("pe")
            row["forward_pe"] = v.get("forward_pe")
            row["ev_sales"] = v.get("ev_sales")
            row["ev_ebitda"] = v.get("ev_ebitda")
            row["fcf_yield"] = v.get("fcf_yield")
        data_rows.append(row)

    comparison["data"] = data_rows

    # Compute rank for key metrics (1 = best).
    rank_metrics = [
        ("revenue_yoy_growth", True),   # higher is better
        ("gross_margin", True),
        ("operating_margin", True),
        ("roe", True),
        ("roic", True),
        ("fcf_yield", True),
        ("forward_pe", False),           # lower is better
        ("ev_sales", False),
    ]

    rankings: dict[str, dict[str, int]] = {}
    for metric, higher_is_better in rank_metrics:
        vals = [(r["ticker"], r.get(metric)) for r in data_rows]
        valid = [(t, v) for t, v in vals if v is not None]
        valid.sort(key=lambda x: x[1], reverse=higher_is_better)
        rankings[metric] = {t: rank + 1 for rank, (t, _) in enumerate(valid)}

    comparison["rankings"] = rankings

    # Where does the target ticker rank?
    target_ranks = {m: rankings[m].get(ticker) for m in rankings}
    comparison["target_ranks"] = target_ranks

    return comparison


def _build_valuation_models(conn: Any, ticker: str) -> dict:
    """Run valuation models from analytics/valuation.py.

    Attempts to import the valuation module. If it is not yet implemented,
    returns a placeholder noting the gap.
    """
    try:
        from stock_research.analytics import valuation as val_mod
        funds = research_db.query_fundamentals(conn, ticker)
        if not funds:
            return {"note": "no fundamental data for valuation", "models": []}
        latest = funds[-1]
        col_names = ["ticker","period","period_end","revenue","revenue_yoy_growth",
                     "gross_margin","operating_margin","net_income","eps",
                     "operating_cash_flow","capex","free_cash_flow","cash","debt",
                     "shares_outstanding","sbc","roe","roic","source","updated_at"]
        fund_dict = latest if isinstance(latest, dict) else dict(zip(col_names, latest))
        prices = research_db.query_prices(conn, ticker)
        market_price = float(prices[-1]["close"]) if prices else None
        if market_price is None:
            return {"note": "no market price for valuation", "models": []}
        return val_mod.compute_valuation(fund_dict, market_price)
    except (ImportError, AttributeError, Exception) as exc:
        return {
            "note": f"valuation calculation error: {exc}",
            "models": [],
        }


def _build_risk_metrics(conn: Any, ticker: str) -> dict:
    """Compute risk metrics from analytics/risk.py.

    Attempts to import the risk module. If it is not yet implemented,
    returns a placeholder noting the gap.
    """
    try:
        from stock_research.analytics import risk as risk_mod
        prices = research_db.query_prices(conn, ticker)
        if not prices:
            return {"note": "no price data for risk calculation", "metrics": {}}
        price_dicts = [{"date": str(r["date"]), "adjusted_close": r["adjusted_close"]} for r in prices if r.get("adjusted_close") is not None]
        return risk_mod.compute_risk(price_dicts)
    except (ImportError, AttributeError, Exception) as exc:
        return {
            "note": f"risk calculation error: {exc}",
            "metrics": {},
        }


def _build_sentiment_summary(conn: Any, ticker: str) -> dict:
    """Summarise sentiment in 6-month, 3-month, and 1-month buckets.

    For each bucket:
    - total observations
    - bullish / bearish / neutral counts
    - average sentiment_strength
    - top narrative labels by frequency
    """
    buckets = {
        "6m": 180,
        "3m": 90,
        "1m": 30,
    }

    summary: dict[str, Any] = {}
    for label, days in buckets.items():
        rows = research_db.query_sentiment(conn, ticker, days_back=days)
        if not rows:
            summary[label] = {
                "count": 0,
                "bullish": 0,
                "bearish": 0,
                "neutral": 0,
                "avg_strength": None,
                "top_narratives": [],
            }
            continue

        bullish = sum(1 for r in rows if r.get("bull_bear") == "bull")
        bearish = sum(1 for r in rows if r.get("bull_bear") == "bear")
        neutral = len(rows) - bullish - bearish

        strengths = [r["sentiment_strength"] for r in rows if r.get("sentiment_strength") is not None]
        avg_strength = sum(strengths) / len(strengths) if strengths else None

        # Top narrative labels by frequency.
        narr_counts: dict[str, int] = {}
        for r in rows:
            lbl = r.get("narrative_label")
            if lbl:
                narr_counts[lbl] = narr_counts.get(lbl, 0) + 1
        top_narrs = sorted(narr_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        summary[label] = {
            "count": len(rows),
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "avg_strength": round(avg_strength, 3) if avg_strength is not None else None,
            "top_narratives": [{"label": n, "count": c} for n, c in top_narrs],
        }

    return summary


def _build_sentiment_returns(conn: Any, ticker: str) -> dict:
    """Historical analysis: sentiment bucket vs. subsequent stock returns.

    Attempts to import the sentiment_returns module from analytics.
    If it is not yet implemented, returns a placeholder.
    """
    try:
        from stock_research.analytics import sentiment_returns as sr_mod
        return sr_mod.compute_sentiment_returns(conn, ticker)
    except (ImportError, AttributeError):
        return {
            "note": "analytics/sentiment_returns.py not yet implemented",
            "buckets": [],
        }


def _build_claims(conn: Any, ticker: str) -> list[dict]:
    """Return active (non-resolved) investor claims for the ticker.

    Each claim includes its verification status and supporting evidence.
    """
    rows = research_db.query_claims(conn, ticker)
    result = []
    for r in rows:
        result.append({
            "claim_id": r.get("claim_id"),
            "date": r.get("date"),
            "claim": r.get("claim"),
            "claim_type": r.get("claim_type"),
            "bull_bear": r.get("bull_bear"),
            "source": r.get("source"),
            "source_url": r.get("source_url"),
            "evidence_text": r.get("evidence_text"),
            "evidence_strength": r.get("evidence_strength"),
            "verification_status": r.get("verification_status"),
        })
    return result


def _build_data_quality(conn: Any, ticker: str) -> dict:
    """Report data freshness and coverage gaps.

    Checks each expected source and flags any that are missing or stale.
    """
    expected_sources = [
        "sec_fundamentals",
        "yahoo_prices",
        "fmp_earnings",
        "reddit_sentiment",
        "valuation",
    ]

    freshness_rows = research_db.query_freshness_all(conn, ticker)
    freshness_map = {r["source_name"]: r for r in freshness_rows}

    sources: list[dict[str, Any]] = []
    for src in expected_sources:
        info = freshness_map.get(src)
        if info:
            sources.append({
                "source": src,
                "last_updated": info.get("last_updated"),
                "record_count": info.get("record_count"),
                "status": info.get("status", "ok"),
            })
        else:
            sources.append({
                "source": src,
                "last_updated": None,
                "record_count": 0,
                "status": "missing",
            })

    # Count records in core tables for a quick coverage check.
    table_counts: dict[str, int] = {}
    for table in ["company_fundamentals", "earnings", "prices", "valuation", "sentiment_observations"]:
        try:
            row = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE ticker = ?", [ticker]
            ).fetchone()
            table_counts[table] = row[0] if row else 0
        except Exception:
            table_counts[table] = 0

    return {
        "sources": sources,
        "table_record_counts": table_counts,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point: ``python -m stock_research.packet_builder TICKER``."""
    parser = argparse.ArgumentParser(
        description="Build a stock research packet from DuckDB data.",
    )
    parser.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    parser.add_argument("--db", default=None, help="Path to DuckDB file")
    parser.add_argument(
        "--peers",
        default=None,
        help="Comma-separated peer tickers (e.g. MSFT,GOOG,AMZN)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    peers = [p.strip() for p in args.peers.split(",")] if args.peers else None

    packet = build_packet(
        ticker=args.ticker,
        db_path=args.db,
        peers=peers,
    )

    indent = 2 if args.pretty else None
    json.dump(packet, sys.stdout, default=_json_serial, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
