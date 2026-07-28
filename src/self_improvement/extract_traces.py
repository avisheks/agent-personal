"""Extract execution traces from Claude Code session logs and pair with skill outputs.

Reads JSONL session files from Claude Code's project directory,
identifies skill invocations (by matching user prompts to known skills),
and pairs them with output files from agent-personal/.local/data/.

Produces structured trace bundles in .local/traces/ for the self-improvement pipeline.
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CLAUDE_SESSION_DIRS = [
    Path.home() / ".claude" / "projects" / "-Users-avisaha-work-side-agents-agent-personal",
    Path.home() / ".claude" / "projects" / "-Users-avisaha-work-side-agents",
]
AGENT_OUTPUT_DIR = Path("/Users/avisaha/work-side/agents/agent-personal/.local/data")


def get_input_dir(date_str: str | None = None) -> Path:
    """Get the .local/input/YYYY-MM-DD directory for a given date."""
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return PROJECT_ROOT / ".local" / "input" / date_str


def get_traces_dir(date_str: str | None = None) -> Path:
    return get_input_dir(date_str) / "traces"


def get_outputs_dir(date_str: str | None = None) -> Path:
    return get_input_dir(date_str) / "outputs"

SKILL_PATTERNS = {
    "tour-planner-v2": [
        r"itinerary", r"tour.?planner", r"trip", r"vienna", r"prague",
        r"travel", r"trip-slug",
    ],
    "options-pnl": [
        r"pnl", r"options", r"compute_pnl", r"render_report",
        r"thinkorswim", r"tastytrade", r"fidelity", r"validate_pnl",
    ],
    "news-summarizer": [
        r"news.?summar", r"weekly.?report", r"ai.?research",
        r"WK\d+", r"briefing",
    ],
}


def detect_skill(text: str) -> str | None:
    text_lower = text.lower()
    scores = {}
    for skill, patterns in SKILL_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text_lower))
        if score > 0:
            scores[skill] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def parse_session(filepath: Path) -> list[dict]:
    """Parse a JSONL session file into conversation turns."""
    turns = []
    with open(filepath) as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry.get("type") in ("user", "assistant") and "message" in entry:
                turns.append(entry)
    return turns


def extract_text_from_content(content) -> str:
    """Extract text from message content, handling both string and block formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return ""


def extract_skill_invocations(turns: list[dict], session_id: str) -> list[dict]:
    """Identify skill invocations from user turns."""
    invocations = []
    current_skill = None
    current_start_idx = None

    for i, turn in enumerate(turns):
        if turn["type"] == "user":
            content = turn["message"].get("content", [])
            content_text = extract_text_from_content(content)

            skill = detect_skill(content_text)
            if skill and skill != current_skill:
                if current_skill and current_start_idx is not None:
                    invocations.append({
                        "skill": current_skill,
                        "session_id": session_id,
                        "start_turn": current_start_idx,
                        "end_turn": i - 1,
                        "prompt_preview": extract_text_from_content(turns[current_start_idx]["message"].get("content", ""))[:200],
                    })
                current_skill = skill
                current_start_idx = i

    if current_skill and current_start_idx is not None:
        invocations.append({
            "skill": current_skill,
            "session_id": session_id,
            "start_turn": current_start_idx,
            "end_turn": len(turns) - 1,
            "prompt_preview": extract_text_from_content(turns[current_start_idx]["message"].get("content", ""))[:200],
        })

    return invocations


def get_skill_outputs(skill: str) -> list[dict]:
    """Find output files for a skill from agent-personal/.local/data/."""
    outputs = []
    skill_dirs = {
        "tour-planner-v2": AGENT_OUTPUT_DIR / "tour-planner",
        "options-pnl": AGENT_OUTPUT_DIR / "options-pnl" / "out",
        "news-summarizer": AGENT_OUTPUT_DIR / "news-summarizer",
    }

    skill_dir = skill_dirs.get(skill)
    if not skill_dir or not skill_dir.exists():
        return outputs

    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".html", ".json", ".docx"):
            stat = f.stat()
            outputs.append({
                "path": str(f),
                "filename": f.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })

    outputs.sort(key=lambda x: x["modified"], reverse=True)
    return outputs


def extract_conversation_segment(turns: list[dict], start: int, end: int) -> list[dict]:
    """Extract a simplified conversation segment."""
    segment = []
    for turn in turns[start:end + 1]:
        simplified = {
            "role": turn["type"],
            "content_preview": extract_text_from_content(
                turn.get("message", {}).get("content", "")
            )[:500],
        }
        segment.append(simplified)
    return segment


def build_trace_bundle(invocation: dict, turns: list[dict], outputs: list[dict]) -> dict:
    """Build a complete trace bundle for one skill invocation."""
    segment = extract_conversation_segment(
        turns, invocation["start_turn"], invocation["end_turn"]
    )

    return {
        "skill": invocation["skill"],
        "session_id": invocation["session_id"],
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "turn_range": [invocation["start_turn"], invocation["end_turn"]],
        "prompt_preview": invocation["prompt_preview"],
        "conversation_turns": len(segment),
        "conversation": segment,
        "outputs": outputs,
    }


def save_trace_bundle(bundle: dict, date_str: str | None = None) -> Path:
    traces_dir = get_traces_dir(date_str)
    traces_dir.mkdir(parents=True, exist_ok=True)
    skill = bundle["skill"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    filename = f"{skill}--{bundle['session_id'][:8]}--{ts}.json"
    filepath = traces_dir / filename

    with open(filepath, "w") as f:
        json.dump(bundle, f, indent=2)

    return filepath


def copy_latest_outputs(skill: str, date_str: str | None = None) -> list[Path]:
    """Copy the latest outputs to .local/input/YYYY-MM-DD/outputs/ for local reference."""
    outputs = get_skill_outputs(skill)
    if not outputs:
        return []

    dest_dir = get_outputs_dir(date_str) / skill
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for out in outputs[:5]:
        src = Path(out["path"])
        dest = dest_dir / src.name
        if src.suffix != ".docx":
            shutil.copy2(src, dest)
            copied.append(dest)

    return copied


def main():
    parser = argparse.ArgumentParser(description="Extract execution traces from Claude Code sessions")
    parser.add_argument("--session", default=None, help="Specific session ID (default: all)")
    parser.add_argument("--skill", default=None, help="Filter to specific skill")
    parser.add_argument("--date", default=None, help="Date folder name (default: today, YYYY-MM-DD)")
    parser.add_argument("--copy-outputs", action="store_true", help="Copy latest outputs to .local/input/YYYY-MM-DD/outputs/")
    args = parser.parse_args()

    date_str = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if args.session:
        session_files = []
        for d in CLAUDE_SESSION_DIRS:
            candidate = d / f"{args.session}.jsonl"
            if candidate.exists():
                session_files.append(candidate)
                break
        if not session_files:
            print(f"Session {args.session} not found.")
            return
    else:
        session_files = []
        for d in CLAUDE_SESSION_DIRS:
            if d.exists():
                session_files.extend(sorted(d.glob("*.jsonl")))

    if not session_files:
        print("No session files found.")
        return

    print(f"Extracting to: .local/input/{date_str}/\n")

    total_bundles = 0
    for session_file in session_files:
        session_id = session_file.stem
        print(f"Processing session: {session_id}")

        turns = parse_session(session_file)
        invocations = extract_skill_invocations(turns, session_id)

        if args.skill:
            invocations = [inv for inv in invocations if inv["skill"] == args.skill]

        print(f"  Found {len(invocations)} skill invocation(s)")

        for inv in invocations:
            outputs = get_skill_outputs(inv["skill"])
            bundle = build_trace_bundle(inv, turns, outputs)
            path = save_trace_bundle(bundle, date_str=date_str)
            print(f"  [{inv['skill']}] Trace saved: {path.name}")
            total_bundles += 1

            if args.copy_outputs:
                copied = copy_latest_outputs(inv["skill"], date_str=date_str)
                if copied:
                    print(f"    Copied {len(copied)} output file(s)")

    print(f"\nDone. {total_bundles} trace bundle(s) extracted to .local/input/{date_str}/")


if __name__ == "__main__":
    main()
