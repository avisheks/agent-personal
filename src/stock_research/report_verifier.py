#!/usr/bin/env python3
"""
Report Verifier — validates numeric values in individual ticker .md reports.

Runs AFTER individual report generation, BEFORE master report compilation.
Three validation layers:
  1. DuckDB source-of-truth: report values match research packet / DB
  2. Live spot-check: current price via yfinance vs report-stated price
  3. Sanity bounds: flag obviously wrong values

Usage:
  python -m stock_research.report_verifier --date 2026-09-13
  python -m stock_research.report_verifier --date 2026-09-13 --tickers RDDT,TSLA
  python -m stock_research.report_verifier --date 2026-09-13 --fix  # auto-fix price in reports
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / ".notlocal" / "data" / "personal-investor" / "reports"
DB_PATH = REPO_ROOT / ".notlocal" / "data" / "personal-investor" / "db" / "research.duckdb"
EVENTS_LOG = REPO_ROOT / ".local" / "logs" / "super-agent" / "events.jsonl"
TOLERANCE = 0.05  # 5% threshold


def _emit_event(event_type: str, data: dict):
    EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event_type,
        **data,
    }
    with open(EVENTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _parse_dollar(s: str) -> float | None:
    if not s or s.strip() in ("N/A", "—", "-"):
        return None
    m = re.search(r"\$?([\d,]+\.?\d*)", s.replace(",", ""))
    if m:
        return float(m.group(1))
    return None


def _parse_multiple(s: str) -> float | None:
    if not s or s.strip() in ("N/A", "—", "-"):
        return None
    m = re.search(r"([-\d,]+\.?\d*)\s*x", s.replace(",", ""))
    if m:
        return float(m.group(1))
    return None


def _parse_pct(s: str) -> float | None:
    if not s or s.strip() in ("N/A", "—", "-"):
        return None
    m = re.search(r"([-\d.]+)\s*%", s)
    if m:
        return float(m.group(1))
    return None


def _extract_report_metrics(md_path: Path) -> dict:
    """Extract key metrics from the first ~40 lines + dashboard of a .md report."""
    text = md_path.read_text()
    lines = text.split("\n")
    header = "\n".join(lines[:40])

    metrics = {}

    # Price — multiple header formats across reports
    for pattern in [
        r"\*\*Market Price\*\*\s*\|\s*~?\$?([\d,]+\.?\d*)",
        r"\*\*Price at Report[:\s]*\*?\*?\s*\|?\s*~?\$?([\d,]+\.?\d*)",
        r"\*\*Price\*\*[:\s|]*~?\$?([\d,]+\.?\d*)",
        r"[Pp]rice[:\s]*~?\$?([\d,]+\.?\d*)",
        r"Price at Report[:\s]*\$?([\d,]+\.?\d*)",
    ]:
        m = re.search(pattern, header)
        if m:
            metrics["price"] = float(m.group(1).replace(",", ""))
            break

    # Market Cap — handles both inline and table formats
    for mcap_pat in [
        r"[Mm]arket [Cc]ap[:\s|]*~?\$?([\d,.]+)\s*([BMT])",
        r"\*\*Market Cap\*\*\s*\|\s*~?\$?([\d,.]+)\s*([BMT])",
    ]:
        m = re.search(mcap_pat, header)
        if m:
            val = float(m.group(1).replace(",", ""))
            suffix = m.group(2)
            if suffix == "B":
                metrics["mcap_b"] = val
            elif suffix == "T":
                metrics["mcap_b"] = val * 1000
            elif suffix == "M":
                metrics["mcap_b"] = val / 1000
            break

    # Dashboard composite
    m = re.search(r"[Cc]omposite[:\s]*([\d.]+)\s*/\s*10", text)
    if m:
        metrics["dashboard"] = float(m.group(1))

    # Volatility
    m = re.search(r"[Vv]olatility[:\s]*([\d.]+)\s*%", text)
    if m:
        metrics["vol_pct"] = float(m.group(1))

    # 52-week from Technical Price Signals section
    m = re.search(r"52-[Ww]eek [Hh]igh[^|]*\|\s*\$?([\d,.]+)", text)
    if m:
        metrics["hi52"] = float(m.group(1).replace(",", ""))
    m = re.search(r"52-[Ww]eek [Ll]ow[^|]*\|\s*\$?([\d,.]+)", text)
    if m:
        metrics["lo52"] = float(m.group(1).replace(",", ""))

    return metrics


def _get_db_price(ticker: str, report_date: str) -> float | None:
    """Get the most recent price from DuckDB on or before report_date."""
    try:
        import duckdb
        db = duckdb.connect(str(DB_PATH), read_only=True)
        row = db.execute(f"""
            SELECT COALESCE(adjusted_close, close, high) as price
            FROM prices
            WHERE ticker = '{ticker}'
              AND COALESCE(adjusted_close, close, high) IS NOT NULL
              AND date <= '{report_date}'
            ORDER BY date DESC LIMIT 1
        """).fetchone()
        db.close()
        return float(row[0]) if row else None
    except Exception:
        return None


def _get_live_price(ticker: str) -> float | None:
    """Get current price via yfinance."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
        info = t.info
        return info.get("currentPrice") or info.get("regularMarketPrice")
    except Exception:
        return None


def _get_db_latest_price(ticker: str) -> float | None:
    """Get the absolute latest price from DuckDB."""
    try:
        import duckdb
        db = duckdb.connect(str(DB_PATH), read_only=True)
        row = db.execute(f"""
            SELECT COALESCE(adjusted_close, close, high) as price, date
            FROM prices
            WHERE ticker = '{ticker}'
              AND COALESCE(adjusted_close, close, high) IS NOT NULL
            ORDER BY date DESC LIMIT 1
        """).fetchone()
        db.close()
        return float(row[0]) if row else None
    except Exception:
        return None


def _pct_diff(a: float, b: float) -> float:
    if b == 0:
        return float("inf")
    return abs(a - b) / abs(b)


def _check_sanity(ticker: str, metrics: dict) -> list[str]:
    """Layer 3: sanity bounds."""
    issues = []
    if "price" in metrics and metrics["price"] <= 0:
        issues.append(f"Price is non-positive: ${metrics['price']}")
    if "mcap_b" in metrics and metrics["mcap_b"] <= 0:
        issues.append(f"Market cap is non-positive: ${metrics['mcap_b']}B")
    if "vol_pct" in metrics and metrics["vol_pct"] > 200:
        issues.append(f"Volatility implausibly high: {metrics['vol_pct']}%")
    if "dashboard" in metrics and (metrics["dashboard"] < 0 or metrics["dashboard"] > 10):
        issues.append(f"Dashboard score out of range: {metrics['dashboard']}")
    if "hi52" in metrics and "lo52" in metrics:
        if metrics["hi52"] < metrics["lo52"]:
            issues.append(f"52wk high ({metrics['hi52']}) < low ({metrics['lo52']})")
    if "price" in metrics and "hi52" in metrics:
        if metrics["price"] > metrics["hi52"] * 1.5:
            issues.append(f"Price ${metrics['price']} is >50% above 52wk high ${metrics['hi52']}")
    return issues


def verify_ticker(ticker: str, report_date: str, use_live: bool = True) -> dict:
    """Run all 3 validation layers for one ticker."""
    md_path = REPORTS_DIR / ticker / f"{ticker}_{report_date}.md"
    if not md_path.exists():
        return {"ticker": ticker, "status": "SKIP", "reason": "report not found"}

    metrics = _extract_report_metrics(md_path)
    if not metrics:
        return {"ticker": ticker, "status": "SKIP", "reason": "no metrics extracted"}

    result = {
        "ticker": ticker,
        "status": "PASS",
        "report_metrics": metrics,
        "issues": [],
    }

    # Layer 1: DuckDB source-of-truth
    db_price = _get_db_latest_price(ticker)
    if db_price and "price" in metrics:
        diff = _pct_diff(metrics["price"], db_price)
        result["db_price"] = db_price
        result["db_price_diff_pct"] = round(diff * 100, 1)
        if diff > TOLERANCE:
            result["issues"].append(
                f"PRICE vs DB: report=${metrics['price']:.2f}, db=${db_price:.2f} ({diff*100:.1f}% off)"
            )

    # Layer 2: Live spot-check
    if use_live:
        live_price = _get_live_price(ticker)
        if live_price and "price" in metrics:
            diff = _pct_diff(metrics["price"], live_price)
            result["live_price"] = live_price
            result["live_price_diff_pct"] = round(diff * 100, 1)
            if diff > TOLERANCE:
                result["issues"].append(
                    f"PRICE vs LIVE: report=${metrics['price']:.2f}, live=${live_price:.2f} ({diff*100:.1f}% off)"
                )

    # Layer 3: Sanity bounds
    sanity = _check_sanity(ticker, metrics)
    result["issues"].extend(sanity)

    if result["issues"]:
        result["status"] = "FAIL"

    return result


def run_verification(report_date: str, tickers: list[str] | None = None,
                     use_live: bool = True) -> dict:
    """Run verification across all tickers. Returns summary."""
    if tickers is None:
        tickers = sorted([
            d.name for d in REPORTS_DIR.iterdir()
            if d.is_dir() and (d / f"{d.name}_{report_date}.md").exists()
        ])

    results = []
    for t in tickers:
        print(f"  Verifying {t}...", end=" ", flush=True)
        r = verify_ticker(t, report_date, use_live=use_live)
        status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}.get(r["status"], "?")
        issues_str = f" — {'; '.join(r['issues'])}" if r.get("issues") else ""
        print(f"{status_icon}{issues_str}")
        results.append(r)

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    skip_count = sum(1 for r in results if r["status"] == "SKIP")

    summary = {
        "date": report_date,
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
        "skip": skip_count,
        "gate": "PASS" if fail_count == 0 else "FAIL",
        "results": results,
    }

    # Emit event
    _emit_event("report_verification", {
        "date": report_date,
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
        "skip": skip_count,
        "gate": summary["gate"],
        "failed_tickers": [r["ticker"] for r in results if r["status"] == "FAIL"],
    })

    print(f"\n{'='*60}")
    print(f"Verification: {pass_count} PASS | {fail_count} FAIL | {skip_count} SKIP")
    if fail_count > 0:
        print(f"⛔ GATE: FAIL — fix {fail_count} ticker(s) before master report generation")
        for r in results:
            if r["status"] == "FAIL":
                for issue in r["issues"]:
                    print(f"   {r['ticker']}: {issue}")
    else:
        print(f"✅ GATE: PASS — master report generation may proceed")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Verify report numeric values")
    parser.add_argument("--date", required=True, help="Report date YYYY-MM-DD")
    parser.add_argument("--tickers", help="Comma-separated ticker list (default: all)")
    parser.add_argument("--no-live", action="store_true", help="Skip yfinance live check")
    parser.add_argument("--tolerance", type=float, default=0.05, help="Max allowed deviation (default 0.05 = 5%%)")
    args = parser.parse_args()

    global TOLERANCE
    TOLERANCE = args.tolerance

    tickers = args.tickers.split(",") if args.tickers else None
    summary = run_verification(args.date, tickers, use_live=not args.no_live)
    sys.exit(0 if summary["gate"] == "PASS" else 1)


if __name__ == "__main__":
    main()
