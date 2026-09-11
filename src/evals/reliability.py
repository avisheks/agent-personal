#!/usr/bin/env python3
"""
Reliability scoring for super-agent evaluation.

Fires the same trace input through the evaluation pipeline N times
(default: 5) and computes reliability metrics from the score distribution.
Individual trial results are NOT persisted — only the aggregate report.

Tier 1 (deterministic) is run once — it's deterministic by definition, so
repeated runs produce identical results. Tier 2 (LLM-judge) is run N times
to measure LLM scoring variance.

Metrics:
  pass@k    — P(at least 1 of k trials passes a rule). Estimates whether
              the rule CAN pass for this trace, even if it doesn't always.
              Formula: 1 - C(n-c, k) / C(n, k) where c = pass count, n = trials.
  pass^k    — P(all k trials pass a rule). Estimates whether the rule
              RELIABLY passes for this trace.
              Formula: (c/n)^k where c = pass count, n = trials.
  consistency — % of rules where all N trials produced the same verdict.
  verdict_entropy — per-rule Shannon entropy over verdict distribution.
              0 = perfectly consistent, higher = more variance.

Usage:
    # Default (5 trials, Tier 2 only — Tier 1 is deterministic):
    python3 src/evals/reliability.py --session 2026-09-11

    # 10 trials:
    python3 src/evals/reliability.py --session 2026-09-11 --trials 10

    # Save report (but not individual trial data):
    python3 src/evals/reliability.py --session 2026-09-11 \
        --output .local/logs/super-agent/evals/2026-09-11-reliability.json

    # Custom paths:
    python3 src/evals/reliability.py \
        --session 2026-09-11 \
        --events .local/logs/super-agent/events.jsonl \
        --constitution src/evals/constitution.yaml \
        --catalog skills/skills-catalog.yaml
"""

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

from deterministic_tests_tier1 import run_tier1
from llm_judge_tier2 import run_tier2


# ── Defaults ──────────────────────────────────────────────────────

DEFAULT_EVENTS = ".local/logs/super-agent/events.jsonl"
DEFAULT_CONSTITUTION = "src/evals/constitution.yaml"
DEFAULT_CATALOG = "skills/skills-catalog.yaml"
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"
DEFAULT_REGION = "us-west-2"
DEFAULT_PROFILE = "default"
DEFAULT_TRIALS = 5


# ── Math Helpers ──────────────────────────────────────────────────

def comb(n: int, k: int) -> int:
    """Binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def pass_at_k(n: int, c: int, k: int) -> float:
    """
    P(at least 1 pass in k trials).
    n = total trials, c = number of passes, k = sample size.
    Formula: 1 - C(n-c, k) / C(n, k)
    """
    if n == 0 or k == 0:
        return 0.0
    if c == 0:
        return 0.0
    if c == n:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_power_k(n: int, c: int, k: int) -> float:
    """
    P(all k trials pass).
    Estimated as (c/n)^k.
    """
    if n == 0:
        return 0.0
    p = c / n
    return p ** k


def shannon_entropy(counts: dict[str, int]) -> float:
    """Shannon entropy over verdict distribution (base 2)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


# ── Loaders ───────────────────────────────────────────────────────

def load_session_events(path: Path, session_date: str) -> list[dict]:
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if event.get("session") == session_date:
                events.append(event)
    if not events:
        print(f"❌ No events found for session {session_date}", file=sys.stderr)
        sys.exit(1)
    return events


def load_constitution(path: Path) -> tuple[dict, str, str]:
    raw = path.read_text()
    data = yaml.safe_load(raw)
    h = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return data, data["version"], h


def load_catalog(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    return {s["id"]: s for s in data["skills"]}


# ── Reliability Evaluation ────────────────────────────────────────

def run_reliability(
    session_date: str,
    events: list[dict],
    constitution: dict,
    catalog: dict,
    n_trials: int,
    model_id: str,
    region: str,
    profile: str,
) -> dict:
    """
    Run Tier 1 once (deterministic) + Tier 2 N times (stochastic).
    Returns aggregate reliability metrics without persisting individual trials.
    """

    # ── Tier 1: Run once (deterministic = identical every time) ──
    tier1_results, tier2_deferred = run_tier1(events, constitution, catalog)

    tier1_verdicts = {}
    for r in tier1_results:
        tier1_verdicts[r["rule"]] = {
            "verdict": r["verdict"],
            "evidence": r.get("evidence", ""),
            "dimension": r.get("dimension", ""),
            "severity": r.get("severity", ""),
            "gap": r.get("gap"),
            "consistency": 1.0,
            "entropy": 0.0,
            "pass_at_1": 1.0 if r["verdict"] == "PASS" else 0.0,
            "pass_at_k": 1.0 if r["verdict"] == "PASS" else 0.0,
            "pass_power_k": 1.0 if r["verdict"] == "PASS" else 0.0,
            "tier": "deterministic",
            "trials": 1,
            "verdict_distribution": {r["verdict"]: 1},
        }

    if not tier2_deferred:
        return _build_report(session_date, tier1_verdicts, {}, n_trials)

    # ── Tier 2: Run N times ──
    print(f"🔄 Running {n_trials} Tier 2 trials for session {session_date}...")

    trial_results: dict[str, list[str]] = defaultdict(list)

    for i in range(n_trials):
        print(f"   Trial {i+1}/{n_trials}...", end=" ", flush=True)
        try:
            results = run_tier2(
                tier2_deferred, events, tier1_results, catalog,
                model_id=model_id, region=region, profile=profile,
                dry_run=False,
            )
            for r in results:
                trial_results[r["rule"]].append(r.get("verdict", "ERROR"))
            print("✅")
        except Exception as e:
            print(f"❌ ({e})")
            for d in tier2_deferred:
                trial_results[d["rule"]].append("ERROR")

    # ── Compute Tier 2 reliability metrics ──
    tier2_metrics = {}
    for rule_info in tier2_deferred:
        rule_id = rule_info["rule"]
        verdicts = trial_results.get(rule_id, [])
        n = len(verdicts)
        verdict_counts = Counter(verdicts)
        c_pass = verdict_counts.get("PASS", 0)

        tier2_metrics[rule_id] = {
            "dimension": rule_info["dimension"],
            "severity": rule_info["severity"],
            "fail_maps_to": rule_info.get("fail_maps_to"),
            "tier": "llm_judge",
            "trials": n,
            "verdict_distribution": dict(verdict_counts),
            "pass_at_1": pass_at_k(n, c_pass, 1),
            "pass_at_k": pass_at_k(n, c_pass, n_trials),
            "pass_power_k": pass_power_k(n, c_pass, n_trials),
            "consistency": max(verdict_counts.values()) / n if n > 0 else 0.0,
            "entropy": shannon_entropy(verdict_counts),
            "dominant_verdict": verdict_counts.most_common(1)[0][0] if verdict_counts else "UNKNOWN",
        }

    return _build_report(session_date, tier1_verdicts, tier2_metrics, n_trials)


def _build_report(
    session_date: str,
    tier1_verdicts: dict,
    tier2_metrics: dict,
    n_trials: int,
) -> dict:
    """Build the final reliability report from per-rule metrics."""

    all_rules = {**tier1_verdicts, **tier2_metrics}

    # ── Aggregate metrics ──
    t2_rules = {k: v for k, v in all_rules.items() if v["tier"] == "llm_judge"}
    t2_consistencies = [v["consistency"] for v in t2_rules.values()] if t2_rules else []
    t2_entropies = [v["entropy"] for v in t2_rules.values()] if t2_rules else []

    # Fully consistent = all trials gave the same verdict
    fully_consistent = sum(1 for v in t2_rules.values() if v["consistency"] == 1.0)
    total_t2 = len(t2_rules)

    # Session-level pass@k: treat each rule independently, aggregate
    session_pass_at_1 = [v["pass_at_1"] for v in all_rules.values()]
    session_pass_at_k = [v["pass_at_k"] for v in all_rules.values()]
    session_pass_power_k = [v["pass_power_k"] for v in all_rules.values()]

    # Flag unreliable rules (consistency < 0.8 or entropy > 0.8)
    unreliable = [
        {"rule": k, "consistency": v["consistency"], "entropy": v["entropy"],
         "distribution": v["verdict_distribution"]}
        for k, v in t2_rules.items()
        if v["consistency"] < 0.8 or v["entropy"] > 0.8
    ]

    return {
        "session": session_date,
        "evaluated_at": datetime.utcnow().isoformat() + "Z",
        "n_trials": n_trials,
        "summary": {
            "total_rules": len(all_rules),
            "tier1_rules": len(tier1_verdicts),
            "tier2_rules": total_t2,
            "tier2_fully_consistent": fully_consistent,
            "tier2_consistency_rate": fully_consistent / total_t2 if total_t2 > 0 else 1.0,
            "tier2_mean_consistency": sum(t2_consistencies) / len(t2_consistencies) if t2_consistencies else 1.0,
            "tier2_mean_entropy": sum(t2_entropies) / len(t2_entropies) if t2_entropies else 0.0,
            "session_mean_pass_at_1": sum(session_pass_at_1) / len(session_pass_at_1) if session_pass_at_1 else 0.0,
            "session_mean_pass_at_k": sum(session_pass_at_k) / len(session_pass_at_k) if session_pass_at_k else 0.0,
            "session_mean_pass_power_k": sum(session_pass_power_k) / len(session_pass_power_k) if session_pass_power_k else 0.0,
        },
        "unreliable_rules": unreliable,
        "per_rule": all_rules,
    }


# ── Output ────────────────────────────────────────────────────────

def print_report(report: dict):
    s = report["summary"]
    n = report["n_trials"]

    print(f"\n{'='*65}")
    print(f"🎯 Reliability Report — Session: {report['session']} ({n} trials)")
    print(f"{'─'*65}")

    print(f"\n📊 Aggregate Metrics:")
    print(f"   Rules evaluated:        {s['total_rules']} ({s['tier1_rules']} deterministic + {s['tier2_rules']} LLM-judge)")
    print(f"   Tier 2 consistency rate: {s['tier2_consistency_rate']:.0%} ({s['tier2_fully_consistent']}/{s['tier2_rules']} fully consistent)")
    print(f"   Tier 2 mean consistency: {s['tier2_mean_consistency']:.2f}")
    print(f"   Tier 2 mean entropy:     {s['tier2_mean_entropy']:.3f} bits")

    print(f"\n📈 Reliability Scores (across all rules):")
    print(f"   mean pass@1:   {s['session_mean_pass_at_1']:.2f}")
    print(f"   mean pass@{n}:  {s['session_mean_pass_at_k']:.2f}")
    print(f"   mean pass^{n}:  {s['session_mean_pass_power_k']:.2f}")

    print(f"\n📋 Per-Rule Breakdown:")
    print(f"   {'Rule':<6} {'Tier':<14} {'Verdict Dist':<30} {'Consist':>8} {'H(bits)':>8} {'p@1':>6} {'p@{0}':>6} {'p^{0}':>6}".format(n, n))
    print(f"   {'─'*6} {'─'*14} {'─'*30} {'─'*8} {'─'*8} {'─'*6} {'─'*6} {'─'*6}")

    for rule_id in sorted(report["per_rule"].keys()):
        m = report["per_rule"][rule_id]
        dist_str = " ".join(f"{v}:{c}" for v, c in sorted(m["verdict_distribution"].items()))
        tier_label = "deterministic" if m["tier"] == "deterministic" else "llm-judge"
        print(f"   {rule_id:<6} {tier_label:<14} {dist_str:<30} {m['consistency']:>7.2f} {m['entropy']:>7.3f} {m['pass_at_1']:>5.2f} {m['pass_at_k']:>5.2f} {m['pass_power_k']:>5.2f}")

    unreliable = report["unreliable_rules"]
    if unreliable:
        print(f"\n⚠️  Unreliable Rules (consistency < 0.8 or entropy > 0.8):")
        for u in unreliable:
            dist_str = " ".join(f"{v}:{c}" for v, c in sorted(u["distribution"].items()))
            print(f"   {u['rule']}: consistency={u['consistency']:.2f}, entropy={u['entropy']:.3f}, dist=[{dist_str}]")
        print(f"   → These rules produce inconsistent scores. Consider tightening the rubric in constitution.yaml.")
    else:
        print(f"\n✅ All Tier 2 rules are reliable (consistency ≥ 0.8, entropy ≤ 0.8)")

    print(f"\n{'='*65}")


def main():
    parser = argparse.ArgumentParser(
        description="Reliability scoring: run evaluation N times and compute pass@k, pass^k, consistency")
    parser.add_argument("--session", required=True, help="Session date (YYYY-MM-DD)")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help=f"Number of Tier 2 trials (default: {DEFAULT_TRIALS})")
    parser.add_argument("--events", default=DEFAULT_EVENTS, help="Path to events.jsonl")
    parser.add_argument("--constitution", default=DEFAULT_CONSTITUTION, help="Path to constitution.yaml")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG, help="Path to skills-catalog.yaml")
    parser.add_argument("--output", help="Save report JSON (only aggregate, not individual trials)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Bedrock model ID")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="AWS profile")
    args = parser.parse_args()

    if args.trials < 2:
        parser.error("--trials must be >= 2 for reliability measurement")
    if args.trials > 10:
        parser.error("--trials capped at 10 to limit LLM cost")

    constitution, version, c_hash = load_constitution(Path(args.constitution))
    catalog = load_catalog(Path(args.catalog))
    events = load_session_events(Path(args.events), args.session)

    report = run_reliability(
        args.session, events, constitution, catalog,
        n_trials=args.trials,
        model_id=args.model, region=args.region, profile=args.profile,
    )
    report["constitution_version"] = version
    report["constitution_hash"] = c_hash

    print_report(report)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n")
        print(f"💾 Report saved → {out_path}")
    else:
        print(f"ℹ️  Use --output to save the report JSON")


if __name__ == "__main__":
    main()
