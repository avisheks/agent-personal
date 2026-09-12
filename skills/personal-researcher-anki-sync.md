# Anki Sync — Operating Instructions

> **🔕 Observability gate:** If invoked outside the super-agent orchestrator, pause before doing any work and print:
>
> `⚠️ This session will NOT be logged — events, decisions, and gaps won't be tracked.`
> `💡 For full observability, re-run your request through super-agent.md instead.`
> `👉 Proceed without logging? [yes / switch to super-agent]`
>
> Wait for the user's response. If they say "switch" (or similar), stop and instruct them to route through [super-agent.md](super-agent.md). If they say "yes" (or similar), proceed — and at session end print: `⚠️ Untraced session — no events written.`

## Purpose

This companion skill synchronizes flashcard CSVs (produced by the personal-researcher skill) to Anki Desktop via the AnkiConnect plugin. It handles creation of new cards, updating changed cards, and optionally removing deleted cards — using the stable card ID as the sync key.

## Prerequisites

1. **Anki Desktop** must be running with the **AnkiConnect** plugin installed
   - Install: Tools → Add-ons → Get Add-ons → Code: `2055492159`
   - AnkiConnect listens on `http://localhost:8765`
2. **CSV source**: `.notlocal/data/personal-researcher/reports/v2/notes/anki/{topic}/*.csv`

## Architecture

```
personal-researcher skill          anki-sync                          Anki Desktop
────────────────────────          ─────────                          ────────────
Markdown reports                  Read CSVs                          AnkiConnect plugin
 ↓ LLM generation                 ↓ Parse ID/Front/Back/Tags         ↓ localhost:8765
CSV files with stable IDs          ↓ Compare with Anki state          ↓
(anki/{topic}/*.csv)                ↓ Compute diff                     ↓
                                   ↓ Apply changes                   Notes updated
                                   ↓ Write sync state log
```

## Deck Naming Convention

Each topic folder maps to an Anki deck:

```
anki/rl/          → Deck: "Research::Rl"
anki/training/    → Deck: "Research::Training"
anki/agents/      → Deck: "Research::Agents"
anki/systems/     → Deck: "Research::Systems"
anki/models/      → Deck: "Research::Models"
anki/search-ads/  → Deck: "Research::Search-Ads"
anki/applications/→ Deck: "Research::Applications"
anki/foundations/ → Deck: "Research::Foundations"
anki/career/      → Deck: "Research::Career"
anki/research/    → Deck: "Research::Research"
```

Parent deck `Research` is created automatically. Sub-decks map 1:1 to topic folders.

## Note Type (Model)

The sync creates/uses a custom note type called `Research-Card` with fields:

| Field | Source | Purpose |
|-------|--------|---------|
| `CardID` | CSV `ID` column | Stable sync key (not shown on card) |
| `Front` | CSV `Front` column | Question shown during review |
| `Back` | CSV `Back` column | Answer shown on flip |
| `Tags` | CSV `Tags` column | Applied as Anki tags |

Template:
- Front: `{{Front}}`
- Back: `{{FrontSide}}<hr id=answer>{{Back}}`

## Commands

```bash
# Full sync — all topics, create+update (no delete)
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json

# Sync a single topic
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json \
    --topic rl

# Dry run — show what would change without applying
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json \
    --dry-run

# Sync with deletion — also remove cards whose IDs are no longer in CSVs
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json \
    --delete

# Status — show sync state without connecting to Anki
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json \
    --status
```

## Sync State

After each sync, the state file at `.local/data/personal-researcher/.anki-sync-state.json` is updated:

```json
{
  "lastSync": "2026-07-30T14:30:00Z",
  "decks": {
    "Research::RL": {
      "deck": "Research::Rl",
      "cardsTotal": 275,
      "added": 275,
      "updated": 0,
      "deleted": 0,
      "unchanged": 0
    }
  },
  "totalCards": 275,
  "errors": []
}
```

## Safety Rules

1. **Never delete without explicit `--delete` flag** — default is create+update only
2. **Dry-run first for bulk operations** — always recommend `--dry-run` before first sync or after large regeneration
3. **Sync state tracks errors** — any AnkiConnect failures are logged; partial sync is safe (idempotent via IDs)
4. **AnkiConnect must be reachable** — fail fast with clear error if Anki isn't running
5. **Back up before first sync** — recommend user exports their Anki collection before first automated sync

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Connection refused (localhost:8765) | Anki not running or AnkiConnect not installed | Print setup instructions; exit |
| Model "Research-Card" not found | First run | Create the model automatically |
| Deck not found | First run for that topic | Create the deck automatically |
| Note with duplicate ID | Bug in CSV generation | Skip and log; investigate CSV |
| Partial sync failure | Network/Anki crash mid-sync | Log last successful ID; re-run is safe (idempotent) |

## Integration with Researcher Skill

The researcher skill's **Mandatory Co-Update Rule** generates CSVs. This skill consumes them:

1. User asks a question → researcher updates report `.md`
2. Researcher regenerates `anki/{topic}/{report}.csv`
3. User runs `/anki-sync --topic {topic}`
4. Anki desktop receives updated cards
