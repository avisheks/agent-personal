"""Unified CLI for the self-improvement pipeline.

Usage:
    python -m self_improvement capture --skill <name> [--feedback "note"]
    python -m self_improvement feedback --skill <name> --note "..." --type bug
    python -m self_improvement reflect [--skill <name>]
    python -m self_improvement propose [--skill <name>]
    python -m self_improvement validate --id <proposal-id>
    python -m self_improvement status
"""

import argparse
import json
import sys
from pathlib import Path

from self_improvement.capture import build_trajectory, save_trajectory
from self_improvement.feedback import log_feedback
from self_improvement.reflector import generate_reflection, save_reflection, load_trajectories, load_feedback
from self_improvement.proposer import load_latest_reflection, propose_improvements, save_proposals
from self_improvement.validator import load_proposal, validate_proposal, save_proposal

MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory"


def cmd_capture(args):
    inputs = json.loads(args.inputs) if args.inputs else {}
    trajectory = build_trajectory(
        skill=args.skill,
        inputs=inputs,
        outputs=args.outputs or [],
        duration_sec=args.duration,
        errors=args.errors or [],
        feedback=args.feedback,
    )
    path = save_trajectory(trajectory)
    print(f"Trajectory saved: {path}")


def cmd_feedback(args):
    path = log_feedback(
        skill=args.skill,
        note=args.note,
        feedback_type=args.type,
        trajectory_ref=args.ref,
    )
    print(f"Feedback logged: {path}")


def cmd_reflect(args):
    reflection = generate_reflection(skill=args.skill)
    path = save_reflection(reflection)
    print(f"Reflection saved: {path}")
    print(f"  Trajectories: {reflection['trajectory_count']}")
    print(f"  Feedback: {reflection['feedback_count']}")
    print(f"  Error rate: {reflection['error_rate']:.1%}")
    if reflection["summary"]["fix"]:
        print(f"  To fix ({len(reflection['summary']['fix'])}):")
        for item in reflection["summary"]["fix"]:
            print(f"    - {item}")
    if reflection["summary"]["add"]:
        print(f"  To add ({len(reflection['summary']['add'])}):")
        for item in reflection["summary"]["add"]:
            print(f"    - {item}")


def cmd_propose(args):
    reflection = load_latest_reflection(skill=args.skill)
    if not reflection:
        print("No reflections found. Run 'reflect' first.")
        return
    proposals = propose_improvements(reflection)
    if not proposals:
        print("No improvements to propose.")
        return
    paths = save_proposals(proposals)
    print(f"{len(proposals)} proposal(s) generated:")
    for p, path in zip(proposals, paths):
        print(f"  [{p['type']}] {p['description'][:70]}")
        print(f"    ID: {p['id']} | Confidence: {p['confidence']}")


def cmd_validate(args):
    proposal = load_proposal(args.id)
    if not proposal:
        print(f"Proposal {args.id} not found.")
        return
    validated = validate_proposal(proposal)
    save_proposal(validated)
    result = validated["validation_result"]
    print(f"Proposal {args.id}: {result['status']}")
    print(f"  {result['reason']}")


def cmd_status(args):
    print("=== Self-Improvement Pipeline Status ===\n")

    # Trajectories
    traj_dir = MEMORY_DIR / "trajectories"
    if traj_dir.exists():
        for skill_dir in sorted(traj_dir.iterdir()):
            if skill_dir.is_dir():
                count = sum(1 for f in skill_dir.glob("*.jsonl") for _ in open(f))
                print(f"  Trajectories [{skill_dir.name}]: {count}")
    else:
        print("  Trajectories: none")

    # Feedback
    fb_dir = MEMORY_DIR / "feedback"
    if fb_dir.exists():
        for f in sorted(fb_dir.glob("*.jsonl")):
            count = sum(1 for _ in open(f))
            print(f"  Feedback [{f.stem}]: {count} entries")
    else:
        print("  Feedback: none")

    # Reflections
    ref_dir = MEMORY_DIR / "reflections"
    if ref_dir.exists():
        count = len(list(ref_dir.glob("*.json")))
        print(f"  Reflections: {count}")
    else:
        print("  Reflections: none")

    # Proposals
    imp_dir = MEMORY_DIR / "improvements"
    if imp_dir.exists():
        proposals = list(imp_dir.glob("*.json"))
        statuses = {}
        for p in proposals:
            data = json.loads(p.read_text())
            s = data.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
        print(f"  Proposals: {len(proposals)} ({statuses})")
    else:
        print("  Proposals: none")


def main():
    parser = argparse.ArgumentParser(prog="self_improvement", description="Self-improvement pipeline CLI")
    subparsers = parser.add_subparsers(dest="command")

    # capture
    p_cap = subparsers.add_parser("capture", help="Capture a skill execution trajectory")
    p_cap.add_argument("--skill", required=True)
    p_cap.add_argument("--inputs", default=None)
    p_cap.add_argument("--outputs", nargs="*")
    p_cap.add_argument("--duration", type=float, default=None)
    p_cap.add_argument("--errors", nargs="*")
    p_cap.add_argument("--feedback", default=None)

    # feedback
    p_fb = subparsers.add_parser("feedback", help="Log feedback")
    p_fb.add_argument("--skill", required=True)
    p_fb.add_argument("--note", required=True)
    p_fb.add_argument("--type", default="observation", choices=["bug", "improvement", "observation", "praise"])
    p_fb.add_argument("--ref", default=None)

    # reflect
    p_ref = subparsers.add_parser("reflect", help="Generate reflection from trajectories/feedback")
    p_ref.add_argument("--skill", default=None)

    # propose
    p_prop = subparsers.add_parser("propose", help="Generate improvement proposals")
    p_prop.add_argument("--skill", default=None)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a proposal")
    p_val.add_argument("--id", required=True)

    # status
    subparsers.add_parser("status", help="Show pipeline status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "capture": cmd_capture,
        "feedback": cmd_feedback,
        "reflect": cmd_reflect,
        "propose": cmd_propose,
        "validate": cmd_validate,
        "status": cmd_status,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
