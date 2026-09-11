#!/usr/bin/env python3
"""
Super-Agent Session Evaluator — orchestrates Tier 1 (deterministic) and
Tier 2 (LLM-judge) evaluation.

Both tiers derive their rules from constitution.yaml. Tier 1 always runs.
Tier 2 runs when --tier2 is passed (or --all). Results are persisted as
JSON with the constitution version and hash for reproducibility.

Usage:
    # Tier 1 only (fast, no LLM cost):
    python3 src/evals/evaluate.py \
        --session 2026-09-11

    # Tier 1 + Tier 2:
    python3 src/evals/evaluate.py \
        --session 2026-09-11 --tier2

    # All sessions, Tier 1 only:
    python3 src/evals/evaluate.py --all-sessions

    # Dry-run Tier 2 (print LLM prompt without calling):
    python3 src/evals/evaluate.py \
        --session 2026-09-11 --tier2 --dry-run

    # Custom paths:
    python3 src/evals/evaluate.py \
        --session 2026-09-11 \
        --events .local/logs/super-agent/events.jsonl \
        --constitution src/evals/constitution.yaml \
        --catalog skills/skills-catalog.yaml \
        --output-dir .local/logs/super-agent/evals/
"""

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

from deterministic_tests_tier1 import run_tier1
from llm_judge_tier2 import run_tier2


# ── Defaults ──────────────────────────────────────────────────────

DEFAULT_EVENTS = ".local/logs/super-agent/events.jsonl"
DEFAULT_CONSTITUTION = "src/evals/constitution.yaml"
DEFAULT_CATALOG = "skills/skills-catalog.yaml"
DEFAULT_OUTPUT_DIR = ".local/logs/super-agent/evals"
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"
DEFAULT_REGION = "us-west-2"
DEFAULT_PROFILE = "default"


# ── Loaders ───────────────────────────────────────────────────────

def load_events(path: Path, session_date: str | None = None) -> dict[str, list[dict]]:
    sessions: dict[str, list[dict]] = defaultdict(list)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            sessions[event["session"]].append(event)
    if session_date:
        if session_date not in sessions:
            print(f"❌ No events found for session {session_date}", file=sys.stderr)
            sys.exit(1)
        return {session_date: sessions[session_date]}
    return dict(sessions)


def load_constitution(path: Path) -> tuple[dict, str, str]:
    raw = path.read_text()
    data = yaml.safe_load(raw)
    h = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return data, data["version"], h


def load_catalog(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    return {s["id"]: s for s in data["skills"]}


# ── Evaluation ────────────────────────────────────────────────────

def evaluate_session(
    session_date: str,
    events: list[dict],
    constitution: dict,
    const_version: str,
    const_hash: str,
    catalog: dict,
    run_tier2_flag: bool = False,
    dry_run: bool = False,
    model_id: str = DEFAULT_MODEL,
    region: str = DEFAULT_REGION,
    profile: str = DEFAULT_PROFILE,
) -> dict:
    """Run evaluation for a single session. Returns the full eval dict."""

    # ── Tier 1: Deterministic ──
    tier1_results, tier2_deferred = run_tier1(events, constitution, catalog)

    tier1_counts = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0})
    for r in tier1_results:
        dim = r.get("dimension", "unknown")
        tier1_counts[dim][r["verdict"].lower()] += 1

    eval_data = {
        "session": session_date,
        "evaluated_at": datetime.utcnow().isoformat() + "Z",
        "constitution_version": const_version,
        "constitution_hash": const_hash,
        "tier1": {
            "rules_evaluated": len(tier1_results),
            "pass": sum(1 for r in tier1_results if r["verdict"] == "PASS"),
            "fail": sum(1 for r in tier1_results if r["verdict"] == "FAIL"),
            "skip": sum(1 for r in tier1_results if r["verdict"] == "SKIP"),
            "by_dimension": dict(tier1_counts),
            "results": tier1_results,
            "failures": [r for r in tier1_results if r["verdict"] == "FAIL"],
        },
        "tier2": {
            "deferred_rules": [d["rule"] for d in tier2_deferred],
            "rubrics": {d["rule"]: d for d in tier2_deferred},
            "completed": False,
        },
    }

    # ── Tier 2: LLM-Judge ──
    if run_tier2_flag and tier2_deferred:
        result = run_tier2(
            tier2_deferred, events, tier1_results, catalog,
            model_id=model_id, region=region, profile=profile,
            dry_run=dry_run,
        )
        if dry_run:
            eval_data["tier2"]["dry_run_prompt"] = result
        else:
            tier2_results = result
            eval_data["tier2"]["completed"] = True
            eval_data["tier2"]["evaluated_at"] = datetime.utcnow().isoformat() + "Z"
            eval_data["tier2"]["results"] = tier2_results
            eval_data["tier2"]["pass"] = sum(1 for r in tier2_results if r.get("verdict") == "PASS")
            eval_data["tier2"]["fail"] = sum(1 for r in tier2_results if r.get("verdict") == "FAIL")
            eval_data["tier2"]["minor"] = sum(1 for r in tier2_results if r.get("verdict") == "MINOR")
            eval_data["tier2"]["skip"] = sum(1 for r in tier2_results if r.get("verdict") == "SKIP")

    # ── Combined Summary ──
    t1 = eval_data["tier1"]
    t2 = eval_data["tier2"]
    all_failures = t1["failures"].copy()
    if t2.get("completed") and "results" in t2:
        all_failures += [r for r in t2["results"] if r.get("verdict") == "FAIL"]

    all_gaps = [f["gap"] for f in all_failures if f.get("gap")]
    eval_data["combined"] = {
        "total_rules": t1["rules_evaluated"] + len(t2.get("results", [])),
        "total_pass": t1["pass"] + t2.get("pass", 0),
        "total_fail": t1["fail"] + t2.get("fail", 0),
        "total_minor": t2.get("minor", 0),
        "total_skip": t1["skip"] + t2.get("skip", 0),
        "all_gaps": all_gaps,
        "gap_summary": {g: all_gaps.count(g) for g in set(all_gaps)} if all_gaps else {},
    }

    return eval_data


# ── Output ────────────────────────────────────────────────────────

def print_summary(eval_data: dict):
    t1 = eval_data["tier1"]
    t2 = eval_data["tier2"]
    combined = eval_data["combined"]

    print(f"\n{'='*60}")
    print(f"📋 Session: {eval_data['session']}  |  Constitution: v{eval_data['constitution_version']} ({eval_data['constitution_hash']})")
    print(f"{'─'*60}")
    print(f"🔧 Tier 1 (deterministic): {t1['pass']}✅ {t1['fail']}❌ {t1['skip']}⏭️")

    if t1["failures"]:
        for f in t1["failures"]:
            gap = f" → {f['gap']}" if "gap" in f else ""
            print(f"   [{f['severity'].upper()}] {f['rule']}: {f['evidence']}{gap}")

    if t2.get("completed"):
        print(f"🤖 Tier 2 (LLM-judge):    {t2['pass']}✅ {t2['fail']}❌ {t2.get('minor', 0)}⚠️  {t2['skip']}⏭️")
        if "results" in t2:
            for r in t2["results"]:
                if r.get("verdict") in ("FAIL", "MINOR"):
                    gap = f" → {r['gap']}" if r.get("gap") else ""
                    print(f"   [{r['verdict']}] {r['rule']}: {r.get('evidence', '')}{gap}")
    elif t2.get("dry_run_prompt"):
        print(f"🤖 Tier 2: DRY RUN (prompt length: {len(t2['dry_run_prompt'])} chars)")
    else:
        print(f"🤖 Tier 2: skipped ({len(t2['deferred_rules'])} rules deferred)")

    print(f"{'─'*60}")
    print(f"📊 Combined: {combined['total_pass']}✅ {combined['total_fail']}❌ {combined['total_minor']}⚠️  {combined['total_skip']}⏭️")
    if combined["gap_summary"]:
        gaps_str = ", ".join(f"{k}×{v}" for k, v in sorted(combined["gap_summary"].items()))
        print(f"🔍 Gaps: {gaps_str}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate super-agent sessions (Tier 1 deterministic + Tier 2 LLM-judge)")
    parser.add_argument("--session", help="Session date (YYYY-MM-DD). Omit with --all-sessions for all.")
    parser.add_argument("--all-sessions", action="store_true", help="Evaluate all sessions in events.jsonl")
    parser.add_argument("--tier2", action="store_true", help="Also run Tier 2 LLM-judge evaluation")
    parser.add_argument("--dry-run", action="store_true", help="Print Tier 2 prompt without calling LLM")
    parser.add_argument("--events", default=DEFAULT_EVENTS, help="Path to events.jsonl")
    parser.add_argument("--constitution", default=DEFAULT_CONSTITUTION, help="Path to constitution.yaml")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG, help="Path to skills-catalog.yaml")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory for eval JSONs")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Bedrock model ID for Tier 2")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region for Tier 2")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="AWS profile for Tier 2")
    args = parser.parse_args()

    if not args.session and not args.all_sessions:
        parser.error("Either --session YYYY-MM-DD or --all-sessions is required")

    constitution, version, c_hash = load_constitution(Path(args.constitution))
    catalog = load_catalog(Path(args.catalog))
    sessions = load_events(Path(args.events), args.session)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for session_date, events in sorted(sessions.items()):
        eval_data = evaluate_session(
            session_date, events, constitution, version, c_hash, catalog,
            run_tier2_flag=args.tier2, dry_run=args.dry_run,
            model_id=args.model, region=args.region, profile=args.profile,
        )

        out_path = output_dir / f"{session_date}-eval.json"
        out_path.write_text(json.dumps(eval_data, indent=2) + "\n")

        print_summary(eval_data)
        print(f"💾 Saved → {out_path}")


if __name__ == "__main__":
    main()
