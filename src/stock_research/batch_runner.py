#!/usr/bin/env python3
"""Batch report generator — runs the data pipeline for all configured tickers.

Reads tickers from config/tickers.yaml, ingests data, builds packets, and
writes research packet JSONs. The LLM report generation (bull/contrarian/
adjudicator) is NOT done here — that requires the super-agent orchestrator.

This script handles Stage 1 (deterministic data pipeline) only:
  - SEC XBRL fundamentals
  - Yahoo Finance prices + valuation
  - Reddit sentiment (RSS → DDG → Reddit API → Google fallback)
  - Research packet JSON assembly

Usage:
    # All tickers with 10-min throttle (default)
    python -m stock_research.batch_runner

    # Specific tickers
    python -m stock_research.batch_runner CRWV VRT NVDA

    # Custom throttle (seconds between tickers)
    python -m stock_research.batch_runner --delay 300

    # Dry run (show what would be processed)
    python -m stock_research.batch_runner --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DELAY_SECONDS = 600  # 10 minutes between tickers
_REPORTS_DIR = _PROJECT_ROOT / ".notlocal" / "data" / "personal-investor" / "reports"
_EVENT_LOG = _PROJECT_ROOT / ".local" / "logs" / "super-agent" / "events.jsonl"


def _load_tickers(config_path: Path, specific: list[str] | None = None) -> list[dict]:
    """Load ticker configs from tickers.yaml."""
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required: pip install pyyaml")

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    tickers_section = cfg.get("tickers", {})
    result = []
    for ticker, info in tickers_section.items():
        if specific and ticker not in [s.upper() for s in specific]:
            continue
        result.append({
            "ticker": ticker,
            "name": info.get("name", ticker),
            "sector": info.get("sector", ""),
            "peers": info.get("peers", []),
            "subreddits": info.get("subreddits", []),
        })
    return result


def _emit_event(event: dict) -> None:
    """Append a JSON event to the event log."""
    _EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event.setdefault("ts", datetime.now(tz=timezone.utc).isoformat())
    event.setdefault("session", datetime.now().strftime("%Y-%m-%d"))
    with open(_EVENT_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")


def _ingest_ticker(ticker: str, subreddits: list[str]) -> dict:
    """Run full data ingestion for a single ticker. Returns a status dict."""
    from stock_research import db
    from stock_research.ingestion import sec, market_data, reddit

    conn = db.get_connection()
    status = {
        "ticker": ticker,
        "sources_refreshed": [],
        "sources_failed": [],
        "record_counts": {},
    }

    # SEC XBRL
    try:
        fund = sec.fetch_fundamentals(ticker)
        if fund:
            db.upsert_fundamentals(conn, fund)
            db.update_freshness(conn, ticker, "sec_xbrl", len(fund))
            status["sources_refreshed"].append("sec_xbrl")
            status["record_counts"]["sec_xbrl"] = len(fund)
            logger.info("  SEC: %d quarterly records", len(fund))
    except Exception as e:
        status["sources_failed"].append(f"sec_xbrl: {e}")
        logger.warning("  SEC failed: %s", e)

    # Yahoo Finance
    try:
        prices = market_data.fetch_prices(ticker, years=10)
        info = market_data.fetch_info(ticker)
        if prices:
            db.upsert_prices(conn, prices)
            db.update_freshness(conn, ticker, "yahoo_finance", len(prices))
            status["sources_refreshed"].append("yahoo_finance")
            status["record_counts"]["yahoo_finance"] = len(prices)
            logger.info("  Yahoo: %d price records", len(prices))
        if info:
            db.upsert_valuation(conn, [info])
    except Exception as e:
        status["sources_failed"].append(f"yahoo_finance: {e}")
        logger.warning("  Yahoo failed: %s", e)

    # Reddit
    try:
        posts = reddit.fetch_reddit_posts(ticker, days=30, extra_subreddits=subreddits)
        db.update_freshness(conn, ticker, "reddit", len(posts) if posts else 0)
        if posts:
            db.upsert_sentiment(conn, posts)
            status["sources_refreshed"].append("reddit")
            status["record_counts"]["reddit"] = len(posts)
            logger.info("  Reddit: %d posts", len(posts))
        else:
            logger.info("  Reddit: 0 posts")
    except Exception as e:
        status["sources_failed"].append(f"reddit: {e}")
        logger.warning("  Reddit failed: %s", e)

    conn.close()
    return status


def _build_packet(ticker: str, peers: list[str]) -> str | None:
    """Build research packet and write JSON. Returns the file path."""
    from stock_research.packet_builder import build_packet

    try:
        packet = build_packet(ticker, peers=peers)
        ticker_dir = _REPORTS_DIR / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        json_path = ticker_dir / f"{ticker}_{date_str}.json"
        with open(json_path, "w") as f:
            json.dump(packet, f, indent=2, default=str)

        logger.info("  Packet written: %s", json_path.name)
        return str(json_path)
    except Exception as e:
        logger.error("  Packet build failed: %s", e)
        return None


def run_batch(
    tickers: list[dict],
    delay_seconds: int = _DEFAULT_DELAY_SECONDS,
    dry_run: bool = False,
) -> dict:
    """Run the full batch pipeline for all tickers with throttling.

    Returns a summary dict with per-ticker results.
    """
    summary = {
        "start_time": datetime.now(tz=timezone.utc).isoformat(),
        "tickers_total": len(tickers),
        "tickers_succeeded": 0,
        "tickers_failed": 0,
        "results": [],
    }

    _emit_event({
        "turn": 0,
        "event": "batch_start",
        "skill": "personal-stock-research",
        "tickers": [t["ticker"] for t in tickers],
        "delay_seconds": delay_seconds,
        "dry_run": dry_run,
    })

    for i, ticker_cfg in enumerate(tickers):
        ticker = ticker_cfg["ticker"]
        logger.info("\n[%d/%d] Processing %s (%s)...",
                     i + 1, len(tickers), ticker, ticker_cfg.get("name", ""))

        if dry_run:
            logger.info("  DRY RUN — skipping")
            summary["results"].append({"ticker": ticker, "status": "dry_run"})
            continue

        # Throttle between tickers (skip first)
        if i > 0:
            logger.info("  Throttling %d seconds before next ticker...", delay_seconds)
            time.sleep(delay_seconds)

        start = time.time()

        # Stage 1A: Ingest
        ingest_status = _ingest_ticker(ticker, ticker_cfg.get("subreddits", []))

        # Stage 1B: Build packet
        packet_path = _build_packet(ticker, ticker_cfg.get("peers", []))

        elapsed_ms = int((time.time() - start) * 1000)

        result = {
            "ticker": ticker,
            "status": "success" if packet_path else "partial",
            "ingest": ingest_status,
            "packet_path": packet_path,
            "duration_ms": elapsed_ms,
        }
        summary["results"].append(result)

        if packet_path:
            summary["tickers_succeeded"] += 1
        else:
            summary["tickers_failed"] += 1

        _emit_event({
            "turn": i + 1,
            "event": "batch_ticker_complete",
            "skill": "personal-stock-research",
            "ticker": ticker,
            "sources_refreshed": ingest_status["sources_refreshed"],
            "sources_failed": ingest_status["sources_failed"],
            "record_counts": ingest_status["record_counts"],
            "packet_path": packet_path,
            "duration_ms": elapsed_ms,
        })

    summary["end_time"] = datetime.now(tz=timezone.utc).isoformat()

    _emit_event({
        "turn": len(tickers) + 1,
        "event": "batch_end",
        "skill": "personal-stock-research",
        "tickers_succeeded": summary["tickers_succeeded"],
        "tickers_failed": summary["tickers_failed"],
        "tickers_total": summary["tickers_total"],
    })

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Batch stock research data pipeline — ingests + builds packets for all tickers"
    )
    parser.add_argument(
        "tickers", nargs="*",
        help="Specific tickers to process (default: all from tickers.yaml)"
    )
    parser.add_argument(
        "--delay", type=int, default=_DEFAULT_DELAY_SECONDS,
        help=f"Seconds between tickers (default: {_DEFAULT_DELAY_SECONDS})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be processed without running"
    )
    parser.add_argument(
        "--config", type=str,
        default=str(_PROJECT_ROOT / "config" / "tickers.yaml"),
        help="Path to tickers.yaml"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Require EDGAR_USER_AGENT
    if not os.environ.get("EDGAR_USER_AGENT"):
        logger.error("EDGAR_USER_AGENT env var required for SEC data")
        sys.exit(1)

    tickers = _load_tickers(
        Path(args.config),
        specific=args.tickers if args.tickers else None,
    )

    if not tickers:
        logger.error("No tickers found in config")
        sys.exit(1)

    logger.info("Batch runner: %d tickers, %ds delay, dry_run=%s",
                len(tickers), args.delay, args.dry_run)
    for t in tickers:
        logger.info("  %s — %s [%s]", t["ticker"], t["name"], t["sector"])

    summary = run_batch(tickers, delay_seconds=args.delay, dry_run=args.dry_run)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Batch complete: {summary['tickers_succeeded']}/{summary['tickers_total']} succeeded")
    if summary["tickers_failed"]:
        print(f"  Failed: {summary['tickers_failed']}")
    for r in summary["results"]:
        status_icon = "✓" if r["status"] == "success" else "⚠" if r["status"] == "partial" else "—"
        dur = f" ({r.get('duration_ms', 0) / 1000:.0f}s)" if "duration_ms" in r else ""
        print(f"  {status_icon} {r['ticker']}{dur}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
