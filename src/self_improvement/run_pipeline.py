"""Run the full self-improvement pipeline end-to-end.

Steps:
1. Extract traces from Claude Code sessions → .local/input/YYYY-MM-DD/
2. Reflect on traces + outputs → generate reflections
3. Propose improvements from reflections
4. Validate proposals
5. Save all pipeline output to .local/outputs/YYYY-MM-DD-runN/
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_next_run_dir(date_str: str) -> Path:
    """Find the next available run directory (.local/outputs/YYYY-MM-DD-runN/)."""
    outputs_root = PROJECT_ROOT / ".local" / "outputs"
    outputs_root.mkdir(parents=True, exist_ok=True)

    run_num = 1
    while True:
        candidate = outputs_root / f"{date_str}-run{run_num}"
        if not candidate.exists():
            candidate.mkdir(parents=True)
            return candidate
        run_num += 1


def load_traces(date_str: str) -> list[dict]:
    """Load all trace bundles from .local/input/YYYY-MM-DD/traces/."""
    traces_dir = PROJECT_ROOT / ".local" / "input" / date_str / "traces"
    if not traces_dir.exists():
        return []

    traces = []
    for f in sorted(traces_dir.glob("*.json")):
        with open(f) as fh:
            traces.append(json.load(fh))
    return traces


def load_outputs(date_str: str) -> dict[str, list[dict]]:
    """Load output file metadata from .local/input/YYYY-MM-DD/outputs/."""
    outputs_dir = PROJECT_ROOT / ".local" / "input" / date_str / "outputs"
    if not outputs_dir.exists():
        return {}

    results = {}
    for skill_dir in outputs_dir.iterdir():
        if skill_dir.is_dir():
            files = []
            for f in skill_dir.iterdir():
                if f.is_file():
                    files.append({
                        "filename": f.name,
                        "path": str(f),
                        "size_bytes": f.stat().st_size,
                    })
            results[skill_dir.name] = files
    return results


def reflect_on_traces(traces: list[dict], outputs: dict) -> list[dict]:
    """Generate reflections from traces grouped by skill."""
    skills = {}
    for t in traces:
        skill = t["skill"]
        if skill not in skills:
            skills[skill] = []
        skills[skill].append(t)

    reflections = []
    for skill, skill_traces in skills.items():
        total_turns = sum(t.get("conversation_turns", 0) for t in skill_traces)
        session_count = len(skill_traces)
        skill_outputs = outputs.get(skill, [])

        patterns = analyze_patterns(skill_traces)

        reflection = {
            "skill": skill,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessions_analyzed": session_count,
            "total_conversation_turns": total_turns,
            "output_files": len(skill_outputs),
            "patterns": patterns,
            "quality_signals": extract_quality_signals(skill_traces, skill_outputs),
        }
        reflections.append(reflection)

    return reflections


def analyze_patterns(traces: list[dict]) -> dict:
    """Identify patterns across multiple trace executions of the same skill."""
    patterns = {
        "recurring_topics": [],
        "common_errors": [],
        "session_lengths": [],
        "observations": [],
    }

    for t in traces:
        patterns["session_lengths"].append(t.get("conversation_turns", 0))

        prompt = t.get("prompt_preview", "").lower()
        if "fix" in prompt or "bug" in prompt or "wrong" in prompt:
            patterns["common_errors"].append(t["prompt_preview"][:100])
        if "update" in prompt or "modify" in prompt or "change" in prompt:
            patterns["recurring_topics"].append("iterative refinement")
        if "generate" in prompt or "create" in prompt or "run" in prompt:
            patterns["recurring_topics"].append("generation")

    patterns["recurring_topics"] = list(set(patterns["recurring_topics"]))
    patterns["avg_session_length"] = (
        sum(patterns["session_lengths"]) / max(len(patterns["session_lengths"]), 1)
    )

    if patterns["avg_session_length"] > 200:
        patterns["observations"].append(
            "Sessions are very long — skill may benefit from better upfront specification or sub-task decomposition"
        )
    if len(patterns["common_errors"]) > 0:
        patterns["observations"].append(
            f"Found {len(patterns['common_errors'])} session(s) involving fixes/bugs — recurring quality issue likely"
        )

    return patterns


def extract_quality_signals(traces: list[dict], outputs: list[dict]) -> dict:
    """Extract quality signals from traces and outputs."""
    signals = {
        "has_outputs": len(outputs) > 0,
        "output_count": len(outputs),
        "multi_session_skill": len(traces) > 1,
        "iteration_count": len(traces),
    }

    if len(traces) > 3:
        signals["high_iteration"] = True
        signals["suggestion"] = "Skill required many sessions — may need SOP clarification or better defaults"

    return signals


def generate_proposals(reflections: list[dict]) -> list[dict]:
    """Generate improvement proposals from reflections."""
    proposals = []

    for reflection in reflections:
        skill = reflection["skill"]
        patterns = reflection["patterns"]
        quality = reflection["quality_signals"]

        if patterns.get("observations"):
            for obs in patterns["observations"]:
                proposals.append({
                    "id": f"{skill}--{len(proposals)+1}",
                    "skill": skill,
                    "type": "observation",
                    "description": obs,
                    "source": "pattern_analysis",
                    "confidence": "medium",
                    "status": "proposed",
                    "action_required": "human_review",
                })

        if quality.get("high_iteration"):
            proposals.append({
                "id": f"{skill}--iteration-{len(proposals)+1}",
                "skill": skill,
                "type": "improvement",
                "description": quality["suggestion"],
                "source": "iteration_analysis",
                "confidence": "high",
                "status": "proposed",
                "action_required": "human_review",
            })

        if patterns.get("common_errors"):
            proposals.append({
                "id": f"{skill}--errors-{len(proposals)+1}",
                "skill": skill,
                "type": "fix",
                "description": f"Recurring error patterns detected across {len(patterns['common_errors'])} session(s). Review error-triggering prompts for SOP gaps.",
                "source": "error_analysis",
                "evidence": patterns["common_errors"],
                "confidence": "high",
                "status": "proposed",
                "action_required": "human_review",
            })

    return proposals


def validate_proposals(proposals: list[dict]) -> list[dict]:
    """Basic validation of proposals (structural, not execution-based)."""
    for p in proposals:
        p["validation"] = {
            "status": "structurally_valid",
            "has_skill": bool(p.get("skill")),
            "has_description": bool(p.get("description")),
            "has_evidence": bool(p.get("evidence") or p.get("source")),
        }
    return proposals


def main():
    parser = argparse.ArgumentParser(description="Run the full self-improvement pipeline")
    parser.add_argument("--date", default=None, help="Input date folder (default: today)")
    parser.add_argument("--extract", action="store_true", help="Run extraction step first")
    args = parser.parse_args()

    date_str = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_dir = get_next_run_dir(date_str)

    print(f"=== Self-Improvement Pipeline ===")
    print(f"  Input: .local/input/{date_str}/")
    print(f"  Output: {run_dir.relative_to(PROJECT_ROOT)}/")
    print()

    # Step 0: Optional extraction
    if args.extract:
        print("Step 0: Extracting traces...")
        from self_improvement.extract_traces import main as extract_main
        import sys
        sys.argv = ["extract_traces", "--date", date_str, "--copy-outputs"]
        extract_main()
        print()

    # Step 1: Load input data
    print("Step 1: Loading traces and outputs...")
    traces = load_traces(date_str)
    outputs = load_outputs(date_str)
    print(f"  Loaded {len(traces)} trace(s) across {len(outputs)} skill(s)")

    if not traces:
        print("\n  No traces found. Run with --extract or run extract_traces.py first.")
        return

    # Step 2: Reflect
    print("\nStep 2: Reflecting on execution patterns...")
    reflections = reflect_on_traces(traces, outputs)
    reflections_path = run_dir / "reflections.json"
    with open(reflections_path, "w") as f:
        json.dump(reflections, f, indent=2)
    print(f"  Generated {len(reflections)} reflection(s)")
    for r in reflections:
        print(f"    [{r['skill']}] {r['sessions_analyzed']} sessions, {r['total_conversation_turns']} turns")
        if r["patterns"]["observations"]:
            for obs in r["patterns"]["observations"]:
                print(f"      → {obs}")

    # Step 3: Propose
    print("\nStep 3: Generating improvement proposals...")
    proposals = generate_proposals(reflections)
    print(f"  Generated {len(proposals)} proposal(s)")

    # Step 4: Validate
    print("\nStep 4: Validating proposals...")
    validated = validate_proposals(proposals)
    proposals_path = run_dir / "proposals.json"
    with open(proposals_path, "w") as f:
        json.dump(validated, f, indent=2)

    # Step 5: Summary
    summary = {
        "run_dir": str(run_dir.relative_to(PROJECT_ROOT)),
        "date": date_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": {
            "traces": len(traces),
            "skills_with_outputs": list(outputs.keys()),
        },
        "results": {
            "reflections": len(reflections),
            "proposals": len(proposals),
            "proposals_by_type": {},
        },
    }
    for p in proposals:
        ptype = p["type"]
        summary["results"]["proposals_by_type"][ptype] = (
            summary["results"]["proposals_by_type"].get(ptype, 0) + 1
        )

    summary_path = run_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n=== Pipeline Complete ===")
    print(f"  Output: {run_dir.relative_to(PROJECT_ROOT)}/")
    print(f"  Files:")
    for f in sorted(run_dir.iterdir()):
        print(f"    {f.name} ({f.stat().st_size} bytes)")
    print(f"\n  Proposals requiring review: {len(proposals)}")
    for p in proposals:
        print(f"    [{p['type']:12s}] [{p['skill']}] {p['description'][:70]}")


if __name__ == "__main__":
    main()
