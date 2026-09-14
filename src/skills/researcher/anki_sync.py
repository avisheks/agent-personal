#!/usr/bin/env python3
"""
Anki Sync -- Synchronize flashcard CSVs to Anki Desktop via AnkiConnect.

Reads topic-grouped TSV files (ID, Front, Back, Tags) and creates/updates/deletes
notes in Anki via the AnkiConnect plugin (HTTP POST to localhost:8765).

Usage:
    python3 src/skills/researcher/anki_sync.py \
        --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
        --state .local/data/personal-researcher/.anki-sync-state.json \
        [--topic TOPIC] [--dry-run] [--delete] [--status]
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ANKICONNECT_URL = "http://localhost:8765"
DECK_PREFIX = "Research"
MODEL_NAME = "Research-Card"
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 3, 7]


def ankiconnect_request(action: str, **params) -> dict:
    """Send a request to AnkiConnect with retry logic."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(
        ANKICONNECT_URL, data=payload,
        headers={"Content-Type": "application/json"},
    )
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                response = json.loads(resp.read())
            if response.get("error"):
                raise RuntimeError(f"AnkiConnect error: {response['error']}")
            return response.get("result")
        except urllib.error.URLError as e:
            if attempt == MAX_RETRIES - 1:
                print(f"ERROR: Cannot connect to AnkiConnect at {ANKICONNECT_URL}")
                print(f"  Cause: {e}")
                print("  Fix: Ensure Anki Desktop is running with AnkiConnect plugin (code: 2055492159)")
                sys.exit(1)
            last_err = e
        except RuntimeError:
            raise  # Don't retry application-level errors
        except Exception as e:
            last_err = e
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF[attempt])
    raise RuntimeError(f"AnkiConnect request failed after {MAX_RETRIES} attempts: {last_err}")


def ensure_model_exists():
    """Create the Research-Card note type if it doesn't exist."""
    models = ankiconnect_request("modelNames")
    if MODEL_NAME in models:
        return
    print(f"  Creating note type '{MODEL_NAME}'...")
    ankiconnect_request(
        "createModel",
        modelName=MODEL_NAME,
        inOrderFields=["CardID", "Front", "Back"],
        css=".card { font-family: system-ui, sans-serif; font-size: 16px; text-align: left; padding: 20px; }",
        isCloze=False,
        cardTemplates=[{
            "Name": "Card 1",
            "Front": "{{Front}}",
            "Back": "{{FrontSide}}<hr id=answer>{{Back}}",
        }],
    )


def parse_csv(filepath: Path) -> list:
    """Parse a tab-separated Anki CSV file into a list of card dicts."""
    cards = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return cards
    # Skip header if present
    start = 1 if lines[0].strip().split("\t")[0] == "ID" else 0
    for line_num, line in enumerate(lines[start:], start=start + 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            print(f"  WARNING: {filepath.name}:{line_num} has {len(parts)} fields (expected 4), skipping")
            continue
        cards.append({
            "id": parts[0].strip(),
            "front": parts[1].strip(),
            "back": parts[2].strip(),
            "tags": [t.strip() for t in parts[3].split(",") if t.strip()],
        })
    return cards


def get_existing_notes(deck_name: str) -> dict:
    """Get all existing notes in a deck, keyed by CardID field."""
    note_ids = ankiconnect_request("findNotes", query=f'"deck:{deck_name}"')
    if not note_ids:
        return {}
    notes_info = ankiconnect_request("notesInfo", notes=note_ids)
    existing = {}
    for note in notes_info:
        card_id = note["fields"].get("CardID", {}).get("value", "")
        if card_id:
            existing[card_id] = {
                "note_id": note["noteId"],
                "front": note["fields"].get("Front", {}).get("value", ""),
                "back": note["fields"].get("Back", {}).get("value", ""),
                "tags": note.get("tags", []),
            }
    return existing


def compute_diff(all_cards: dict, existing: dict, delete: bool):
    """Compute add/update/delete sets between CSV cards and Anki notes."""
    to_add = {cid: c for cid, c in all_cards.items() if cid not in existing}
    to_update = {
        cid: c for cid, c in all_cards.items()
        if cid in existing and (
            c["front"] != existing[cid]["front"] or c["back"] != existing[cid]["back"]
        )
    }
    to_delete = {cid: existing[cid] for cid in existing if cid not in all_cards} if delete else {}
    unchanged = len(all_cards) - len(to_add) - len(to_update)
    return to_add, to_update, to_delete, unchanged


def sync_topic(topic: str, csv_dir: Path, delete: bool = False, dry_run: bool = False) -> dict:
    """Sync all CSVs in a topic folder to the corresponding Anki deck."""
    topic_dir = csv_dir / topic
    deck_name = f"{DECK_PREFIX}::{topic.replace('-', ' ').title().replace(' ', '-')}"

    if not topic_dir.exists():
        print(f"  SKIP: {topic_dir} does not exist")
        return {"error": f"Directory not found: {topic_dir}"}

    csv_files = sorted(topic_dir.glob("*.csv"))
    if not csv_files:
        print(f"  SKIP: No CSV files in {topic_dir}")
        return {"error": "No CSV files"}

    # Parse all CSVs
    all_cards = {}
    for csv_file in csv_files:
        for card in parse_csv(csv_file):
            if card["id"] in all_cards:
                print(f"  WARNING: Duplicate ID '{card['id']}' in {csv_file.name}, skipping")
                continue
            all_cards[card["id"]] = card

    print(f"  Topic '{topic}' -> Deck '{deck_name}': {len(all_cards)} cards from {len(csv_files)} files")

    if dry_run:
        try:
            existing = get_existing_notes(deck_name)
        except (RuntimeError, SystemExit):
            existing = {}
        to_add, to_update, to_delete, unchanged = compute_diff(all_cards, existing, delete)
        print(f"    DRY RUN: +{len(to_add)} add, ~{len(to_update)} update, -{len(to_delete)} delete, ={unchanged} unchanged")
        return {"deck": deck_name, "cardsTotal": len(all_cards), "added": len(to_add),
                "updated": len(to_update), "deleted": len(to_delete), "unchanged": unchanged, "dry_run": True}

    # Real sync
    ankiconnect_request("createDeck", deck=deck_name)
    ensure_model_exists()
    existing = get_existing_notes(deck_name)
    to_add, to_update, to_delete, unchanged = compute_diff(all_cards, existing, delete)

    # Add new notes
    added = 0
    if to_add:
        notes = [{
            "deckName": deck_name, "modelName": MODEL_NAME,
            "fields": {"CardID": cid, "Front": c["front"], "Back": c["back"]},
            "tags": c["tags"], "options": {"allowDuplicate": False},
        } for cid, c in to_add.items()]
        try:
            results = ankiconnect_request("addNotes", notes=notes)
            failed = sum(1 for r in results if r is None)
            added = len(notes) - failed
            if failed:
                print(f"    WARNING: {failed}/{len(notes)} notes skipped (duplicates or errors)")
        except RuntimeError as e:
            if "duplicate" in str(e).lower():
                for note in notes:
                    try:
                        if ankiconnect_request("addNote", note=note):
                            added += 1
                    except RuntimeError:
                        pass
            else:
                raise

    # Update changed notes
    for cid, card in to_update.items():
        nid = existing[cid]["note_id"]
        ankiconnect_request("updateNoteFields", note={"id": nid, "fields": {"Front": card["front"], "Back": card["back"]}})
        old_tags = existing[cid]["tags"]
        if old_tags:
            ankiconnect_request("removeTags", notes=[nid], tags=" ".join(old_tags))
        if card["tags"]:
            ankiconnect_request("addTags", notes=[nid], tags=" ".join(card["tags"]))

    # Delete removed notes
    if to_delete:
        ankiconnect_request("deleteNotes", notes=[info["note_id"] for info in to_delete.values()])

    result = {"deck": deck_name, "cardsTotal": len(all_cards), "added": added,
              "updated": len(to_update), "deleted": len(to_delete), "unchanged": unchanged}
    print(f"    +{added} add, ~{len(to_update)} update, -{len(to_delete)} delete, ={unchanged} unchanged")
    return result


def save_sync_state(results: dict, state_path: Path):
    """Save sync state to JSON file."""
    state = {
        "lastSync": datetime.now(timezone.utc).isoformat(),
        "decks": results,
        "totalCards": sum(r.get("cardsTotal", 0) for r in results.values() if isinstance(r, dict) and "cardsTotal" in r),
        "errors": [f"{t}: {r['error']}" for t, r in results.items() if isinstance(r, dict) and "error" in r],
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"\nSync state saved to {state_path}")


def show_status(state_path: Path):
    """Display last sync state."""
    if not state_path.exists():
        print("No sync state found. Run a sync first.")
        return
    with open(state_path, "r") as f:
        state = json.load(f)
    print(f"Last sync: {state.get('lastSync', 'unknown')}")
    print(f"Total cards: {state.get('totalCards', 0)}")
    if state.get("errors"):
        print(f"Errors: {len(state['errors'])}")
        for err in state["errors"]:
            print(f"  - {err}")
    print("\nDecks:")
    for topic, info in state.get("decks", {}).items():
        if isinstance(info, dict) and "cardsTotal" in info:
            print(f"  {topic}: {info['cardsTotal']} cards "
                  f"(+{info.get('added', 0)} ~{info.get('updated', 0)} -{info.get('deleted', 0)})")


def get_all_topics(csv_dir: Path) -> list:
    """Get all topic directories that contain CSV files."""
    if not csv_dir.exists():
        return []
    return sorted(d.name for d in csv_dir.iterdir() if d.is_dir() and list(d.glob("*.csv")))


def main():
    parser = argparse.ArgumentParser(description="Sync Anki flashcards from CSV files via AnkiConnect")
    parser.add_argument("--csv-dir", type=Path, required=True, help="Directory containing topic subdirs with CSV files")
    parser.add_argument("--state", type=Path, required=True, help="Path to sync state JSON file")
    parser.add_argument("--topic", type=str, help="Sync only this topic folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without applying")
    parser.add_argument("--delete", action="store_true", help="Delete cards whose IDs are no longer in CSVs")
    parser.add_argument("--status", action="store_true", help="Show last sync state and exit")
    args = parser.parse_args()

    if args.status:
        show_status(args.state)
        return

    topics = [args.topic] if args.topic else get_all_topics(args.csv_dir)
    if not topics:
        print(f"No topics with CSV files found in {args.csv_dir}")
        sys.exit(1)

    print(f"Anki Sync {'(DRY RUN) ' if args.dry_run else ''}")
    print(f"Source: {args.csv_dir}")
    print(f"Topics: {', '.join(topics)}")
    if args.delete:
        print("DELETE mode: cards not in CSVs will be removed from Anki")
    print()

    if not args.dry_run:
        try:
            version = ankiconnect_request("version")
            print(f"AnkiConnect v{version} connected.\n")
        except SystemExit:
            raise

    results = {}
    for topic in topics:
        results[topic] = sync_topic(topic, args.csv_dir, delete=args.delete, dry_run=args.dry_run)

    if not args.dry_run:
        save_sync_state(results, args.state)

    # Summary
    print("\n" + "=" * 50)
    total = {k: sum(r.get(k, 0) for r in results.values() if isinstance(r, dict)) for k in ("added", "updated", "deleted")}
    total_cards = sum(r.get("cardsTotal", 0) for r in results.values() if isinstance(r, dict) and "cardsTotal" in r)
    print(f"TOTAL: {total_cards} cards | +{total['added']} added | ~{total['updated']} updated | -{total['deleted']} deleted")


if __name__ == "__main__":
    main()
