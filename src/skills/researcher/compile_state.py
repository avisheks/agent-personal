#!/usr/bin/env python3
"""State management for researcher knowledge base incremental compilation.

Tracks SHA-256 content hashes of source files and detects changes.
Claude Code does the actual LLM compilation; this script just tracks what changed.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_state(state_path: Path) -> dict:
    """Load state.json, returning empty state if missing."""
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {"version": 1, "sources": {}}


def save_state(state_path: Path, state: dict) -> None:
    """Write state.json atomically via tmp+rename."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    tmp.rename(state_path)


def hash_file(path: Path) -> str:
    """Return SHA-256 hex digest of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_sources(sources_dir: Path) -> dict[str, str]:
    """Recursively find .md files and return {relative_key: sha256_hash}."""
    result = {}
    for path in sorted(sources_dir.rglob("*.md")):
        key = str(path.relative_to(sources_dir))
        result[key] = hash_file(path)
    return result


def check(state_path: Path, sources_dir: Path) -> None:
    """Compare current sources against saved state; output diff as JSON."""
    state = load_state(state_path)
    saved = state.get("sources", {})
    current = scan_sources(sources_dir)

    new = [k for k in current if k not in saved]
    changed = [k for k in current if k in saved and current[k] != saved[k]["hash"]]
    deleted = [k for k in saved if k not in current]
    unchanged = len(current) - len(new) - len(changed)

    json.dump(
        {"new": sorted(new), "changed": sorted(changed),
         "deleted": sorted(deleted), "unchanged": unchanged},
        sys.stdout, indent=2,
    )
    sys.stdout.write("\n")


def update(state_path: Path, sources_dir: Path, compiled_concepts: dict | None) -> None:
    """Update state.json with current hashes and optional compiled concepts."""
    state = load_state(state_path)
    saved = state.get("sources", {})
    current = scan_sources(sources_dir)
    now = datetime.now(timezone.utc).isoformat()

    # Remove deleted sources
    for key in list(saved):
        if key not in current:
            del saved[key]

    # Update/add sources
    for key, file_hash in current.items():
        entry = saved.get(key, {})
        if entry.get("hash") != file_hash:
            entry["hash"] = file_hash
            entry["compiled_at"] = now
        # Merge compiled concepts if provided
        if compiled_concepts and key in compiled_concepts:
            entry["concepts"] = compiled_concepts[key]
        elif "concepts" not in entry:
            entry["concepts"] = []
        saved[key] = entry

    state["sources"] = saved
    save_state(state_path, state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Researcher KB state tracker")
    parser.add_argument("mode", choices=["--check", "--update"])
    parser.add_argument("--state", required=True, type=Path, help="Path to state.json")
    parser.add_argument("--sources", required=True, type=Path, help="Sources directory")
    parser.add_argument("--compiled-concepts", type=str, default=None,
                        help="JSON map of source key -> concept slugs (--update only)")

    # argparse won't treat --check/--update as positional, so parse manually
    args = sys.argv[1:]
    if "--check" in args:
        mode = "check"
        args.remove("--check")
    elif "--update" in args:
        mode = "update"
        args.remove("--update")
    else:
        parser.print_help()
        sys.exit(1)

    p2 = argparse.ArgumentParser()
    p2.add_argument("--state", required=True, type=Path)
    p2.add_argument("--sources", required=True, type=Path)
    p2.add_argument("--compiled-concepts", type=str, default=None)
    opts = p2.parse_args(args)

    if mode == "check":
        check(opts.state, opts.sources)
    else:
        concepts = json.loads(opts.compiled_concepts) if opts.compiled_concepts else None
        update(opts.state, opts.sources, concepts)


if __name__ == "__main__":
    main()
