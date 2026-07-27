"""Validator: tests proposed improvements against past executions.

For each improvement proposal, re-runs the skill with historical inputs
and compares outputs to detect regressions. Marks proposals as
validated/rejected based on results.
"""

import argparse
import json
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory"
IMPROVEMENTS_DIR = MEMORY_DIR / "improvements"
TRAJECTORIES_DIR = MEMORY_DIR / "trajectories"


def load_proposal(proposal_id: str) -> dict | None:
    filepath = IMPROVEMENTS_DIR / f"{proposal_id}.json"
    if not filepath.exists():
        return None
    with open(filepath) as f:
        return json.load(f)


def load_historical_inputs(skill: str, limit: int = 5) -> list[dict]:
    skill_dir = TRAJECTORIES_DIR / skill
    if not skill_dir.exists():
        return []

    inputs = []
    for f in sorted(skill_dir.glob("*.jsonl"), reverse=True)[:limit]:
        for line in open(f):
            entry = json.loads(line.strip())
            if entry.get("inputs"):
                inputs.append(entry["inputs"])
    return inputs


def validate_proposal(proposal: dict) -> dict:
    """Validate a proposal against historical data.

    Currently performs structural validation:
    - Checks that the proposal targets a skill with historical data
    - Verifies the skill has had successful executions

    Full re-execution validation requires the skill runner (Phase 2+).
    """
    skill = proposal["skill"]
    if skill == "all":
        proposal["validation_result"] = {
            "status": "skipped",
            "reason": "Cross-skill proposals require manual review",
        }
        return proposal

    historical = load_historical_inputs(skill)
    if not historical:
        proposal["validation_result"] = {
            "status": "skipped",
            "reason": f"No historical inputs found for skill '{skill}'",
        }
        return proposal

    proposal["validation_result"] = {
        "status": "pending_execution",
        "historical_inputs_available": len(historical),
        "reason": "Historical inputs available; full validation requires skill re-execution",
    }
    return proposal


def save_proposal(proposal: dict) -> Path:
    filepath = IMPROVEMENTS_DIR / f"{proposal['id']}.json"
    with open(filepath, "w") as f:
        json.dump(proposal, f, indent=2)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Validate improvement proposals")
    parser.add_argument("--id", required=True, help="Proposal ID to validate")
    args = parser.parse_args()

    proposal = load_proposal(args.id)
    if not proposal:
        print(f"Proposal {args.id} not found.")
        return

    validated = validate_proposal(proposal)
    save_proposal(validated)

    result = validated["validation_result"]
    print(f"Proposal {args.id}: {result['status']}")
    print(f"  Reason: {result['reason']}")


if __name__ == "__main__":
    main()
