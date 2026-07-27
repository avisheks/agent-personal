"""Feedback logging for skill executions.

Appends structured feedback entries to a per-skill JSONL file.
Feedback is lightweight — a one-liner note with a type tag.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

FEEDBACK_DIR = Path(__file__).resolve().parent.parent.parent / "memory" / "feedback"


def log_feedback(
    skill: str,
    note: str,
    feedback_type: str = "observation",
    trajectory_ref: str | None = None,
) -> Path:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    filepath = FEEDBACK_DIR / f"{skill}.jsonl"

    entry = {
        "skill": skill,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": note,
        "type": feedback_type,
        "trajectory_ref": trajectory_ref,
    }

    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Log feedback for a skill execution")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--note", required=True, help="Feedback note")
    parser.add_argument(
        "--type",
        default="observation",
        choices=["bug", "improvement", "observation", "praise"],
        help="Feedback type",
    )
    parser.add_argument("--ref", default=None, help="Reference to trajectory file")
    args = parser.parse_args()

    filepath = log_feedback(
        skill=args.skill,
        note=args.note,
        feedback_type=args.type,
        trajectory_ref=args.ref,
    )
    print(f"Feedback logged: {filepath}")


if __name__ == "__main__":
    main()
