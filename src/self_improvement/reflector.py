"""Reflector: analyzes trajectories and feedback to identify patterns.

Reads captured trajectories and feedback for a skill (or all skills),
produces structured reflections identifying:
- What went well (keep)
- What went wrong (fix)
- What's missing (add)
- Cross-skill patterns (generalize)
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory"
TRAJECTORIES_DIR = MEMORY_DIR / "trajectories"
FEEDBACK_DIR = MEMORY_DIR / "feedback"
REFLECTIONS_DIR = MEMORY_DIR / "reflections"


def load_trajectories(skill: str | None = None) -> list[dict]:
    trajectories = []
    if skill:
        skill_dir = TRAJECTORIES_DIR / skill
        if skill_dir.exists():
            for f in sorted(skill_dir.glob("*.jsonl")):
                for line in open(f):
                    trajectories.append(json.loads(line.strip()))
    else:
        for skill_dir in TRAJECTORIES_DIR.iterdir():
            if skill_dir.is_dir():
                for f in sorted(skill_dir.glob("*.jsonl")):
                    for line in open(f):
                        trajectories.append(json.loads(line.strip()))
    return trajectories


def load_feedback(skill: str | None = None) -> list[dict]:
    feedback = []
    if skill:
        filepath = FEEDBACK_DIR / f"{skill}.jsonl"
        if filepath.exists():
            for line in open(filepath):
                feedback.append(json.loads(line.strip()))
    else:
        for f in FEEDBACK_DIR.glob("*.jsonl"):
            for line in open(f):
                feedback.append(json.loads(line.strip()))
    return feedback


def generate_reflection(
    skill: str | None = None,
    trajectories: list[dict] | None = None,
    feedback: list[dict] | None = None,
) -> dict:
    if trajectories is None:
        trajectories = load_trajectories(skill)
    if feedback is None:
        feedback = load_feedback(skill)

    errors = [t for t in trajectories if t.get("errors")]
    bugs = [f for f in feedback if f.get("type") == "bug"]
    improvements = [f for f in feedback if f.get("type") == "improvement"]
    praises = [f for f in feedback if f.get("type") == "praise"]

    reflection = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill": skill or "all",
        "trajectory_count": len(trajectories),
        "feedback_count": len(feedback),
        "summary": {
            "keep": [f["note"] for f in praises],
            "fix": [f["note"] for f in bugs]
            + [f"Execution error: {e['errors']}" for e in errors],
            "add": [f["note"] for f in improvements],
        },
        "error_rate": len(errors) / max(len(trajectories), 1),
        "skills_involved": list(set(t["skill"] for t in trajectories)),
    }

    return reflection


def save_reflection(reflection: dict) -> Path:
    REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.fromisoformat(reflection["timestamp"])
    skill_tag = reflection["skill"]
    filename = f"{skill_tag}-{ts.strftime('%Y-%m-%d-%H%M%S')}.json"
    filepath = REFLECTIONS_DIR / filename

    with open(filepath, "w") as f:
        json.dump(reflection, f, indent=2)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Reflect on skill executions")
    parser.add_argument("--skill", default=None, help="Skill to reflect on (all if omitted)")
    args = parser.parse_args()

    reflection = generate_reflection(skill=args.skill)
    filepath = save_reflection(reflection)

    print(f"Reflection saved: {filepath}")
    print(f"  Trajectories analyzed: {reflection['trajectory_count']}")
    print(f"  Feedback entries: {reflection['feedback_count']}")
    print(f"  Error rate: {reflection['error_rate']:.1%}")
    if reflection["summary"]["fix"]:
        print(f"  Issues to fix: {len(reflection['summary']['fix'])}")
    if reflection["summary"]["add"]:
        print(f"  Improvements suggested: {len(reflection['summary']['add'])}")


if __name__ == "__main__":
    main()
