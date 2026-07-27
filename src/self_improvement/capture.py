"""Trajectory capture for skill executions.

Records inputs, outputs, duration, errors, and optional feedback
into append-only JSONL files organized by skill name.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "trajectories"


def build_trajectory(
    skill: str,
    inputs: dict | None = None,
    outputs: list[str] | None = None,
    duration_sec: float | None = None,
    errors: list[str] | None = None,
    feedback: str | None = None,
) -> dict:
    return {
        "skill": skill,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": inputs or {},
        "outputs": outputs or [],
        "duration_sec": duration_sec,
        "errors": errors or [],
        "feedback": feedback,
    }


def save_trajectory(trajectory: dict) -> Path:
    skill = trajectory["skill"]
    skill_dir = MEMORY_DIR / skill
    skill_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.fromisoformat(trajectory["timestamp"])
    filename = ts.strftime("%Y-%m-%d-%H%M%S") + ".jsonl"
    filepath = skill_dir / filename

    with open(filepath, "a") as f:
        f.write(json.dumps(trajectory) + "\n")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Capture a skill execution trajectory")
    parser.add_argument("--skill", required=True, help="Skill name (e.g., tour-planner-v2)")
    parser.add_argument("--inputs", type=str, default=None, help="JSON string of inputs")
    parser.add_argument("--outputs", nargs="*", default=[], help="Output file paths")
    parser.add_argument("--duration", type=float, default=None, help="Execution duration in seconds")
    parser.add_argument("--errors", nargs="*", default=[], help="Error messages")
    parser.add_argument("--feedback", type=str, default=None, help="Quick feedback note")
    args = parser.parse_args()

    inputs = json.loads(args.inputs) if args.inputs else {}

    trajectory = build_trajectory(
        skill=args.skill,
        inputs=inputs,
        outputs=args.outputs,
        duration_sec=args.duration,
        errors=args.errors,
        feedback=args.feedback,
    )

    filepath = save_trajectory(trajectory)
    print(f"Trajectory saved: {filepath}")


if __name__ == "__main__":
    main()
