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
    """Load tickers from BOTH tickers: and sectors: sections of tickers.yaml.

    The tickers: section has rich per-ticker config (peers, subreddits).
    The sectors: section has tickers grouped by sector but no per-ticker detail.
    This function merges both: tickers: entries take priority, and any ticker
    in sectors: that isn't in tickers: gets a default config derived from its
    sector (sector peers = other tickers in the same sector).
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required: pip install pyyaml")

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    tickers_section = cfg.get("tickers", {})
    sectors_section = cfg.get("sectors", {})

    # Build sector lookup: ticker → (sector_key, label, peer_tickers)
    ticker_to_sector: dict[str, dict] = {}
    for sector_key, sector_info in sectors_section.items():
        label = sector_info.get("label", sector_key)
        sector_tickers = sector_info.get("tickers", [])
        for t in sector_tickers:
            ticker_to_sector[t] = {
                "sector": sector_key,
                "label": label,
                "sector_peers": [p for p in sector_tickers if p != t][:5],
            }

    # Start with explicit tickers: entries (rich config)
    seen: set[str] = set()
    result: list[dict] = []

    for ticker, info in tickers_section.items():
        if specific and ticker.upper() not in [s.upper() for s in specific]:
            continue
        seen.add(ticker.upper())
        sector_info = ticker_to_sector.get(ticker, {})
        result.append({
            "ticker": ticker,
            "name": info.get("name", ticker),
            "sector": info.get("sector", sector_info.get("sector", "")),
            "peers": info.get("peers", sector_info.get("sector_peers", [])),
            "subreddits": info.get("subreddits", []),
        })

    # Add tickers from sectors: that aren't in tickers: (default config)
    for ticker, sector_info in ticker_to_sector.items():
        if ticker.upper() in seen:
            continue
        if specific and ticker.upper() not in [s.upper() for s in specific]:
            continue
        seen.add(ticker.upper())
        result.append({
            "ticker": ticker,
            "name": ticker,  # no human name available
            "sector": sector_info["sector"],
            "peers": sector_info["sector_peers"],
            "subreddits": [],  # auto-discovery will handle dedicated subs
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

def _load_weekly_batch(batch_path: Path, tickers_path: Path) -> tuple[list[dict], int]:
    """Load tickers from weekly-batch.yaml, enrich with tickers.yaml metadata.

    Returns (ticker_configs, delay_seconds).
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required: pip install pyyaml")

    with open(batch_path) as f:
        batch_cfg = yaml.safe_load(f)

    batch_tickers = batch_cfg.get("tickers", [])
    delay = batch_cfg.get("delay_seconds", _DEFAULT_DELAY_SECONDS)

    # Load full ticker config for enrichment
    all_tickers = _load_tickers(tickers_path, specific=batch_tickers)

    # Ensure every batch ticker is included even if not in tickers.yaml/sectors
    found = {t["ticker"] for t in all_tickers}
    for ticker in batch_tickers:
        if ticker not in found:
            all_tickers.append({
                "ticker": ticker,
                "name": ticker,
                "sector": "",
                "peers": [],
                "subreddits": [],
            })

    # Preserve the order from weekly-batch.yaml
    order = {t: i for i, t in enumerate(batch_tickers)}
    all_tickers.sort(key=lambda x: order.get(x["ticker"], 999))

    return all_tickers, delay


def main():
    parser = argparse.ArgumentParser(
        description="Batch stock research data pipeline — ingests + builds packets for all tickers"
    )
    parser.add_argument(
        "tickers", nargs="*",
        help="Specific tickers to process (default: all from tickers.yaml)"
    )
    parser.add_argument(
        "--weekly", action="store_true",
        help="Use config/weekly-batch.yaml for ticker list and delay (the weekly cron mode)"
    )
    parser.add_argument(
        "--delay", type=int, default=None,
        help=f"Seconds between tickers (default: {_DEFAULT_DELAY_SECONDS}, or from weekly-batch.yaml)"
    )
    parser.add_argument(
        "--max", type=int, default=25,
        help="Max tickers to process (safety cap, default: 25). Use --max 0 for no limit."
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
    parser.add_argument(
        "--batch-config", type=str,
        default=str(_PROJECT_ROOT / "config" / "weekly-batch.yaml"),
        help="Path to weekly-batch.yaml (used with --weekly)"
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

    # Determine ticker list and delay
    if args.weekly:
        tickers, batch_delay = _load_weekly_batch(
            Path(args.batch_config), Path(args.config)
        )
        delay = args.delay if args.delay is not None else batch_delay
        logger.info("Weekly mode: loaded %d tickers from %s", len(tickers), args.batch_config)
    elif args.tickers:
        tickers = _load_tickers(Path(args.config), specific=args.tickers)
        delay = args.delay if args.delay is not None else _DEFAULT_DELAY_SECONDS
    else:
        tickers = _load_tickers(Path(args.config))
        delay = args.delay if args.delay is not None else _DEFAULT_DELAY_SECONDS

    if not tickers:
        logger.error("No tickers found")
        sys.exit(1)

    # Safety cap
    if args.max > 0 and len(tickers) > args.max:
        logger.warning(
            "Found %d tickers but --max is %d. Processing first %d only. "
            "Pass specific tickers or use --max 0 to override.",
            len(tickers), args.max, args.max,
        )
        tickers = tickers[:args.max]

    logger.info("Batch runner: %d tickers, %ds delay, dry_run=%s",
                len(tickers), delay, args.dry_run)
    for t in tickers:
        logger.info("  %s — %s [%s]", t["ticker"], t["name"], t["sector"])

    summary = run_batch(tickers, delay_seconds=delay, dry_run=args.dry_run)

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
