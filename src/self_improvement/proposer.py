"""Proposer: generates improvement candidates from reflections.

Reads reflections and produces structured improvement proposals
with IDs, rationale, affected files, confidence scores, and
suggested diffs or actions.
"""

import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory"
REFLECTIONS_DIR = MEMORY_DIR / "reflections"
IMPROVEMENTS_DIR = MEMORY_DIR / "improvements"


def load_latest_reflection(skill: str | None = None) -> dict | None:
    if not REFLECTIONS_DIR.exists():
        return None

    files = sorted(REFLECTIONS_DIR.glob("*.json"), reverse=True)
    if skill:
        files = [f for f in files if f.name.startswith(skill)]

    if not files:
        return None

    with open(files[0]) as f:
        return json.load(f)


def generate_improvement_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def propose_improvements(reflection: dict) -> list[dict]:
    proposals = []

    for issue in reflection["summary"]["fix"]:
        proposal = {
            "id": generate_improvement_id(issue + reflection["timestamp"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill": reflection["skill"],
            "type": "fix",
            "description": issue,
            "rationale": f"Identified from execution errors/feedback in {reflection['skill']}",
            "affected_files": [],
            "confidence": "medium",
            "status": "proposed",
            "validation_result": None,
        }
        proposals.append(proposal)

    for suggestion in reflection["summary"]["add"]:
        proposal = {
            "id": generate_improvement_id(suggestion + reflection["timestamp"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill": reflection["skill"],
            "type": "enhancement",
            "description": suggestion,
            "rationale": f"User-suggested improvement for {reflection['skill']}",
            "affected_files": [],
            "confidence": "medium",
            "status": "proposed",
            "validation_result": None,
        }
        proposals.append(proposal)

    return proposals


def save_proposals(proposals: list[dict]) -> list[Path]:
    IMPROVEMENTS_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    for proposal in proposals:
        filepath = IMPROVEMENTS_DIR / f"{proposal['id']}.json"
        with open(filepath, "w") as f:
            json.dump(proposal, f, indent=2)
        paths.append(filepath)

    return paths


def main():
    parser = argparse.ArgumentParser(description="Propose improvements from reflections")
    parser.add_argument("--skill", default=None, help="Skill to propose for (latest reflection if omitted)")
    args = parser.parse_args()

    reflection = load_latest_reflection(skill=args.skill)
    if not reflection:
        print("No reflections found. Run reflector.py first.")
        return

    proposals = propose_improvements(reflection)
    if not proposals:
        print("No improvements to propose — everything looks good.")
        return

    paths = save_proposals(proposals)
    print(f"Generated {len(proposals)} improvement proposal(s):")
    for p, path in zip(proposals, paths):
        print(f"  [{p['type']}] {p['description'][:60]}... → {path.name}")


if __name__ == "__main__":
    main()
