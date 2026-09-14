---
name: personal-researcher
description: Knowledge-base research agent — ingest sources, discover related material, compile into knowledge pages, generate and update reports. Handles queries by checking existing knowledge first, then augmenting with web research.
---

# Personal Researcher — Operating Instructions

> **Observability gate:** If invoked outside the super-agent orchestrator, pause before doing any work and print:
>
> `Warning: This session will NOT be logged — events, decisions, and gaps won't be tracked.`
> `Tip: For full observability, re-run your request through super-agent.md instead.`
> `Proceed without logging? [yes / switch to super-agent]`
>
> Wait for the user's response. If they say "switch" (or similar), stop and instruct them to route through [super-agent.md](super-agent.md). If they say "yes" (or similar), proceed — and at session end print: `Warning: Untraced session — no events written.`

## Purpose

This document defines how the personal-researcher should handle queries against its knowledge base, and when/how to augment answers with web research. All workflows follow the canonical pipeline: **Ingest -> Discover -> Compile -> Report -> Verify**.

## Environment

This skill operates primarily through Claude Code's native capabilities (WebFetch, WebSearch, Read, Write, Edit). Three helper scripts in `src/skills/researcher/` handle tasks that require deterministic computation or external API calls:

| Script | Purpose | When Used |
|--------|---------|-----------|
| `compile_state.py` | SHA-256 hashing, state.json change detection | Before and after `/compile` |
| `cross_model_verify.py` | Cross-model claim verification via Bedrock | During `/verify-report` |
| `anki_sync.py` | AnkiConnect HTTP sync to Anki Desktop | During `/anki-sync` |

Configuration is loaded from `.local/skills-config.yaml` under the `researcher` section.

## Health Check Gate

**On every invocation**, before starting any work:

1. Check if `.local/data/personal-researcher/.health-check-last-run` exists
2. If it does NOT exist, or the timestamp inside is older than 7 days:
   - Inform the user: "KB health check hasn't been run in over a week. Running a health check is recommended to catch inconsistencies."
   - Offer to run it now
3. If the last run is recent (<7 days), proceed without interruption

### Health Check Pipeline

The full health check follows this pipeline:

```
Diagnose -> Fix (staging) -> Re-check -> Verify (content) -> Report -> Log -> HITL Review -> Promote
```

| Phase | What Happens | Who Acts |
|-------|-------------|----------|
| 1. Diagnose | Read `index.md`, scan for orphaned pages, check frontmatter, validate topic index | Claude Code (direct) |
| 2. Fix (staging) | Auto-fixable issues written to `/tmp` staging dir — live KB untouched | Claude Code (direct) |
| 3. Re-check | Health check re-runs on staged fixes to confirm improvement | Claude Code (direct) |
| 4. Verify (content) | **Mandatory** — run `/verify-report` on all reports with stale-vs-knowledge drift | Claude Code + cross_model_verify.py |
| 5. Report & Log | Summary generated, stored in `.local/data/personal-researcher/.logs/` (capped at 12 logs) | Claude Code (direct) |
| 6. HITL Review | User reviews the diff of staged changes + verification results | **User (manual)** |
| 7. Promote | Staged fixes applied to live KB as a versioned update (v2.x or v3.x) | User confirms promotion |

### Phase 4 (Verify) Details — Mandatory During Health Check

The health check's verify phase runs the **full verification engine** on any report flagged as stale (knowledge pages newer than the report). This is NOT the same as skipping only the staleness detection — Phase 4 specifically runs verification on each stale topic:

```bash
# For each topic where knowledge is newer than report:
python3 src/skills/researcher/cross_model_verify.py \
    --claims /tmp/researcher-claims.json \
    --kb-context /tmp/researcher-kb-context.json \
    --output /tmp/researcher-verification.json
```

**What it checks:**
1. Consistency audit: contradictions across knowledge pages within each topic
2. Claim extraction: verifiable claims from the report
3. Claim verification: each claim scored against knowledge base / Facts Manifest
4. Correction suggestions: flagged claims get proposed fixes

**Phase 4 enforcement rules:**
- Health check MUST NOT be marked "passed" if any report has unverified content
- The `--skip-verify` option skips Phase 4 for speed but the health check log MUST record: `"Phase 4: SKIPPED — reports remain unverified"`
- A health check with `--skip-verify` does NOT reset the 7-day gate timer — only a full run (with verification) counts as a valid health check
- If verification finds issues (correctness < 0.7 threshold from config), the health check log MUST list them and the promote step MUST NOT proceed until corrections are applied

### Health Check Execution (Direct)

Since there is no shell script, Claude Code performs the health check directly:

**Diagnose only (no fixes, no verification):**
1. Read `.notlocal/data/personal-researcher/knowledge/index.md`
2. Scan all topic directories under `.notlocal/data/personal-researcher/knowledge/` for orphaned pages (pages not listed in index)
3. Check frontmatter on all knowledge pages and sources
4. Validate `.notlocal/data/personal-researcher/topics.md` against actual topic directories
5. Report findings

**Full pipeline (diagnose + fix + verify):**
1. Run diagnose steps above
2. Write fixes to `/tmp/kb-health-check-staging/` — do NOT touch live KB
3. Re-run checks on staged fixes
4. Run `/verify-report` on all reports where knowledge pages are newer than the report
5. Write summary to `.local/data/personal-researcher/.logs/`
6. Present diff to user for review

**Promote (after user review):**
1. Apply staged fixes from `/tmp/kb-health-check-staging/` to live KB
2. Update `.local/data/personal-researcher/.health-check-last-run` with current timestamp

### Versioning

When fixes are promoted:
- Back up the current state to `.local/data/personal-researcher/.versions/v{current}/`
- Apply the staged changes
- Bump the version (minor for <100 lines changed, major for >100 lines)
- Record the promotion in `.local/data/personal-researcher/.versions/changelog.md`

The KB version tracks structural changes only (index, topics). Report content has its own versioning (see Report Update Rules).

## Topic Management

**Before creating any new topic**, consult the topic index at `.notlocal/data/personal-researcher/topics.md`:

1. **Read the index** — scan all existing topics grouped by domain
2. **Check for overlap** — if the query relates to an existing topic (even partially), route the work to that topic rather than creating a new one
3. **If the user explicitly asks to create a new topic**, check similarity with existing topics and ask the user whether they want to:
   - Add to an existing related topic instead
   - Merge with one or more existing topics
   - Proceed with a genuinely new topic
4. **When a new topic IS created**, update `.notlocal/data/personal-researcher/topics.md` — place it in the correct domain group with slug and description

The goal is to keep topics consolidated and discoverable. Fragmentation (e.g., separate topics for "LoRA" and "QLoRA" or "agentic-systems" and "auto-agents") makes the knowledge base harder to navigate. When in doubt, widen an existing topic rather than creating a narrow new one.

5. **Directory prerequisite for new topics:** The topic directories (`.notlocal/data/personal-researcher/knowledge/{topic-slug}/` and `.notlocal/data/personal-researcher/sources/{topic-slug}/`) MUST exist on disk before running discovery or report generation with that topic name. These workflows resolve topics by scanning existing directories — they will fail with "No knowledge pages found" if the directory doesn't exist yet. When creating a new topic, create both directories first, then proceed with discovery and ingestion.

## Query Resolution Workflow

### Step 1: Check the knowledge base

Look in `.notlocal/data/personal-researcher/knowledge/` and `.notlocal/data/personal-researcher/reports/v2/notes/` and `.notlocal/data/personal-researcher/reports/v2/faqs/` for existing compiled information that answers the query. Also consult `.notlocal/data/personal-researcher/topics.md` to identify the relevant topic for filing.

### Step 2: If the answer is NOT found — Discover & Ingest

When existing knowledge is insufficient, run the full discovery and ingestion pipeline:

**Discover**: Generate 3-5 varied search queries covering different angles of the question (architecture, benchmarks, methodology, deployment, etc.). Search the web using each query to find relevant sources.

**Ingest**: For each useful source found, save it as a markdown file with frontmatter in `.notlocal/data/personal-researcher/sources/{topic}/`:
- Filename: kebab-case slug of the source title
- Frontmatter: `title`, `url` (or `path`), `ingestedAt`, `type` (article, paper, benchmark, discussion)
- Body: Extracted content in clean markdown

Supported source types: `.md`, `.txt`, `.pdf`, `.xlsx`, `.xls`, `.csv`, and URLs (HTML, PDF).

### Step 3: Compile

After ingesting new sources, compile them into knowledge pages under `.notlocal/data/personal-researcher/knowledge/{topic}/`:
- Each knowledge page synthesizes one or more sources into a focused, interlinked page
- Include frontmatter: `title`, `summary`, `sources` (list of source files used), `createdAt`, `updatedAt`
- Link related pages using `[[Page Name]]` wiki-link syntax
- Update `.notlocal/data/personal-researcher/knowledge/index.md` with any new entries

This step transforms raw ingested material into structured, queryable knowledge. Do NOT skip it — writing directly to knowledge pages without going through sources breaks traceability.

**Compilation state management:** Before and after compiling, run the state tracker to detect changes:

```bash
python3 src/skills/researcher/compile_state.py --check \
    --state .local/data/personal-researcher/.researcher/state.json \
    --sources .notlocal/data/personal-researcher/sources/
```

### Step 4: File the query

Synthesize the answer from compiled knowledge pages and save it under `.notlocal/data/personal-researcher/knowledge/queries/` (see Query Filing Format below).

### Step 5: Update the report

This step is **mandatory** — the report is the canonical long-form reference and must always reflect the latest knowledge. Regardless of whether the answer was found in the existing knowledge base or via new discovery:

1. Identify the relevant report in `.notlocal/data/personal-researcher/reports/v2/notes/` (standard reports) or `.notlocal/data/personal-researcher/reports/v2/faqs/` (FAQ-format reports)
2. Add a new section or update an existing section with the query findings
3. Update the report's changelog with the date and description of what was added
4. If no relevant report exists, create one:
   - **First, determine format** — classify the source material using the Report Generation Standards table below:
     - Literature survey / reading roadmap / field evolution -> `_study-notes-template.md` (filename: `{topic-slug}--notes.md`)
     - System or technique to design/operate -> `_template.md` (standard) (filename: `{topic-slug}.md`)
     - Discrete questions with seniority contrast -> `v2/faqs/_template.md` (filename: `{topic-slug}.md`)
   - **Then, read the matching `_generation-guide.md`** for the chosen format before writing anything
   - **Then, use the matching `_template.md`** as the structural skeleton

**Versioning**: When updating a report, assess the magnitude of the change:
- **Minor update** (magnitude < 0.6): Update the report in-place
- **New version** (magnitude >= 0.6 or contradiction >= 0.3): Create a new version of the report

**No query is complete until the report is updated.**

### Step 6: Verify (Mandatory)

After creating or updating a report, run the verification pipeline.

**Full verification on new/updated report:**
1. Extract verifiable claims from the report and write to `/tmp/researcher-claims.json`
2. Gather relevant KB context and write to `/tmp/researcher-kb-context.json`
3. Run cross-model verification:
   ```bash
   python3 src/skills/researcher/cross_model_verify.py \
       --claims /tmp/researcher-claims.json \
       --kb-context /tmp/researcher-kb-context.json \
       --output /tmp/researcher-verification.json
   ```
4. Read the verification results and apply corrections

**What verification does:**
1. **Consistency audit** (Phase 0): Extracts entity-attribute facts from knowledge pages -> detects contradictions across pages -> resolves conflicts -> produces a Facts Manifest
2. **Claim extraction** (Phase 3): Extracts verifiable claims from the report sections
3. **Claim verification** (Phase 4): Checks each claim against the knowledge base / Facts Manifest -> scores factual correctness
4. **Correction** (Phase 5): Applies corrections for flagged claims **in-place** — overwrites the original report

**Verification output rules:**
- **DO NOT** create separate `-verified.md` files. The verified content replaces the original report in-place.
- After verification, update the report's changelog with a before/after score:
  ```markdown
  | 2026-06-09 | Verified | Score: 60% -> 85% (20 claims corrected across 8 sections) |
  ```
- If the report was already at 100% (no corrections needed), still record it:
  ```markdown
  | 2026-06-09 | Verified | Score: 92% (no corrections needed) |
  ```

**Post-verification sanity checks (MANDATORY):**

After verification writes the report in-place, the following checks MUST pass before considering verification complete. If ANY check fails, the write must be rolled back (restore from pre-verification content):

| Check | Condition | What It Catches |
|-------|-----------|-----------------|
| Line count | Output lines >= 80% of input lines | Sections silently dropped during reassembly |
| Section count | Output `## ` headings >= input `## ` headings | Custom sections lost by hardcoded section list |
| File size | Output bytes >= 70% of input bytes | Catastrophic content loss |
| Non-empty body | Content between header and References > 100 lines | Body wiped, only metadata remains |

If verification reduces the report by >20% in size or drops any `## ` sections, it is a **verification engine bug**, not a legitimate correction. The pre-verification content must be restored and the bug investigated.

**Implementation:** The verification engine MUST:
1. Read and store the full original content before making changes
2. After writing the corrected report, compare output vs input on the checks above
3. If any check fails: restore original content, log the failure, return error to user

**Historical incident (2026-06-09):** The verification engine's reassembly loop only iterated over `REPORT_SECTIONS` (a hardcoded 12-item list), silently dropping all custom sections. This wiped the `rl.md` report body. Fix: reassembly now preserves all sections (canonical order first, then custom sections). The sanity checks above prevent recurrence regardless of future reassembly bugs.

**When to verify:**
| Trigger | Verification Mode | Rationale |
|---------|-------------------|-----------|
| New report created | Full | Ensures new content is factually grounded in sources |
| Existing report updated (new section) | Targeted (specific claim) | Faster; only checks the new content |
| New topic created with 3+ knowledge pages | Full | Catches contradictions before they compound |
| Periodic (weekly via health check) | Full on stale reports | Catches drift between knowledge and reports |

**Report path resolution:** The verification engine searches across subdirectories (`v2/notes/`, `v2/faqs/`, `v1/`, `.`) and filename patterns (`{topic}.md`, `{topic}-ref.md`). No hardcoded paths — adding new report locations requires only a config change.

**Verification is NOT optional.** If the cross-model verification script is unavailable, document the unverified state in the report's changelog:

```markdown
| 2026-06-09 | Added X section | [UNVERIFIED] — run verification when runtime available |
```

This ensures no report is silently assumed to be verified when it hasn't been.

**For health checks:** Verification is mandatory for the health check to be considered valid. A health check run with `--skip-verify` does NOT reset the 7-day gate timer. See "Phase 4 (Verify) Details" in the Health Check Pipeline section above.

## Compound Workflows

### Check-and-Integrate: Verify paper coverage in a report and bake it in

Use when you want to ensure a specific paper/source is covered in an existing report. This is a repeatable pattern:

**Steps:**

1. **Check report coverage:** Search the target report for the paper title/key term
2. **Check KB/sources:** Search `.notlocal/data/personal-researcher/knowledge/` and `.notlocal/data/personal-researcher/sources/` for existing compiled content
3. **If in KB but not report:** Read the compiled knowledge page -> identify where it fits in the report's flow (which stage/theme) -> add it with inline citations -> update References + Changelog
4. **If not in KB at all:** Run the full pipeline: Ingest source -> Compile knowledge page -> Then integrate into report (Step 3)
5. **Validate:** Ensure the new content flows naturally with surrounding sections — don't just append; weave it into the narrative

**Integration rules:**
- Place the paper where it fits chronologically/thematically in the report structure
- Add to the References section with a `[N]` citation number
- **Practitioner Appendix rule (study-notes format only):** If the source contains practical observations, heuristics, or anecdotes (from talks, blogs, industry posts) that are useful but NOT citable research findings, add them to a `## Practitioner Appendix` section at the end of the report (before Changelog). Each entry: one-line insight + source URL. Do NOT weave informal heuristics into the main evolutionary stages — those require peer-reviewed or formally published content.
- If the paper introduces a new concept not covered by any existing stage/theme, create a subsection rather than forcing it into an ill-fitting section
- Update Reading Schedule if the paper is important enough to warrant inclusion
- Update Changelog with date and description

## Anki Flashcard Generation

### Purpose

Every report in `.notlocal/data/personal-researcher/reports/v2/notes/` has a corresponding Anki-importable CSV in `.notlocal/data/personal-researcher/reports/v2/notes/anki/`, organized by topic folder. This enables spaced-repetition study with topic-based Anki deck imports.

### Output Location

`.notlocal/data/personal-researcher/reports/v2/notes/anki/{topic}/{report-filename-without-extension}.csv`

Reports are grouped into topic folders:

| Topic Folder | Reports | Description |
|-------------|---------|-------------|
| `rl/` | `rl-for-llms--notes`, `genai-rl-applications`, `rl`, `sft-vs-rl`, `sft-vs-dpo`, `sft` | Reinforcement learning, RLHF, DPO, GRPO, preference optimization |
| `training/` | `policy-dist--notes`, `fine-tuning-noisy-labels`, `lora` | Post-training techniques: distillation, fine-tuning, adapters |
| `agents/` | `self-improving-agents--notes`, `harness-engineering--notes`, `auto-agents-frameworks`, `agentic-systems`, `memory-agentic-systems` | Agent architectures, self-improvement, harness optimization |
| `systems/` | `orc-evolution--notes`, `orc-physical-systems--notes`, `system-design` | Orchestration, planning, system design |
| `models/` | `transformers`, `reasoning-llms`, `open-weight-fms`, `numerical-representation`, `anthropic`, `claude-code` | Model architectures, reasoning, foundation models |
| `search-ads/` | `ai-applied-search-retrieval--notes`, `ai-applied-search-ranking--notes`, `genai-search-ads`, `search-retrieval`, `recommendation-ranking`, `ai-applied-search-ads` | Search, ads, ranking, retrieval, recommendations |
| `applications/` | `ai-applied-robotics--notes`, `ai-applied-enterprise-work--notes`, `content-generation`, `enterprise-rag`, `semantic-graph` | Domain applications: robotics, enterprise, content |
| `foundations/` | `constitutional-ai--notes`, `evaluation-safety`, `world-models`, `recursive-self-improvement` | Safety, alignment, world models, foundational concepts |
| `career/` | `cto-to-ic`, `investing` | Career, professional development |
| `research/` | `ai-assisted-paper-research`, `auto-research-karpathy`, `claude-code-config-karpathy` | Research methodology, tooling |

**Examples:**
- `rl-for-llms--notes.md` -> `anki/rl/rl-for-llms--notes.csv`
- `policy-dist--notes.md` -> `anki/training/policy-dist--notes.csv`
- `self-improving-agents--notes.md` -> `anki/agents/self-improving-agents--notes.csv`
- `ai-applied-search-ranking--notes.md` -> `anki/search-ads/ai-applied-search-ranking--notes.csv`
- `constitutional-ai--notes.md` -> `anki/foundations/constitutional-ai--notes.csv`

**When a new report is created:** assign it to the most relevant topic folder. If none fits, create a new topic folder and add it to the table above.

### Batch Generation: One Topic Per Batch

When generating CSVs in bulk, process **one topic folder per batch** (all reports in that topic are handled by one sub-agent). This:
- Groups related content for coherent card generation
- Produces one Anki-importable folder per topic
- Makes incremental imports easy (import just the `rl/` folder for RL study)

Batch execution order (suggested):
1. `rl/` — 6 reports
2. `training/` — 3 reports
3. `agents/` — 5 reports
4. `systems/` — 3 reports
5. `models/` — 6 reports
6. `search-ads/` — 6 reports
7. `applications/` — 5 reports
8. `foundations/` — 4 reports
9. `career/` — 2 reports
10. `research/` — 3 reports

### CSV Format (Tab-Separated)

```
ID	Front	Back	Tags
```

- **Delimiter:** TAB character (standard Anki import format)
- **Quoting:** none (fields must not contain tabs; use semicolons for internal lists)
- **Encoding:** UTF-8
- **First row:** header (`ID\tFront\tBack\tTags`) — Anki can skip it on import
- **ID field:** unique stable identifier per card (see ID scheme below)
- **Tags field:** comma-separated structured tags using the multi-dimensional tagging system (see below)
- **File extension:** `.csv` (despite being TSV — Anki accepts both)

### Card ID Scheme

Each card gets a stable, unique ID formatted as: `{REPORT-PREFIX}-{NNN}`

- **REPORT-PREFIX:** uppercase abbreviation derived from the report slug (2-4 chars). Examples:
  - `rl-for-llms--notes` -> `RFL`
  - `policy-dist--notes` -> `PD`
  - `harness-engineering--notes` -> `HE`
  - `constitutional-ai--notes` -> `CAI`
  - `self-improving-agents--notes` -> `SIA`
  - `ai-applied-search-ranking--notes` -> `ASR`
  - `ai-applied-robotics--notes` -> `ARB`
  - `ai-applied-enterprise-work--notes` -> `AEW`
  - `orc-evolution--notes` -> `OE`
  - `orc-physical-systems--notes` -> `OPS`
- **NNN:** zero-padded sequential number starting at 001 within each file

**ID stability rules:**
- IDs are permanent — once assigned, a card keeps its ID even if content is updated
- When regenerating a CSV, preserve existing IDs for cards whose Front is unchanged or semantically equivalent
- New cards added during updates get the next available number
- Deleted cards leave gaps (do NOT renumber remaining cards)
- This enables Anki to detect duplicates and update existing cards on re-import

Example:
```
ID	Front	Back	Tags
RFL-001	What does GRPO eliminate?	The value function (critic network); uses group mean/std as baseline instead	topic:grpo,type:definition,level:beginner,paper:deepseek-r1,source:research-summary
RFL-002	Compare DPO vs PPO	DPO: single supervised loss, no RL infrastructure, offline. PPO: on-policy, reward model needed, more flexible reward shaping.	topic:dpo,topic:ppo,type:comparison,level:intermediate,source:research-summary
```

### Card Types to Generate

For each report, produce a mix of:

1. **Basic cards** — Front: question/term. Back: definition/explanation.
2. **Cloze cards** — Front: sentence with `{{c1::hidden part}}`. Back: full sentence. (Tag: `cloze`)
3. **Compare/contrast cards** — Front: "Compare X vs Y on dimension Z." Back: table or key differences.
4. **One fact per card** — never combine multiple facts into one card. Split aggressively.

### Tagging System (Structured Multi-Dimensional)

Every card MUST have tags from at least 3 of the following 5 dimensions:

| Dimension | Prefix | Values (examples) | Required? |
|-----------|--------|-------------------|-----------|
| Topic | `topic:` | `topic:rlhf`, `topic:dpo`, `topic:grpo`, `topic:world-models`, `topic:harness-engineering`, `topic:opd` | Yes (1+) |
| Paper | `paper:` | `paper:deepseek-r1`, `paper:constitutional-ai`, `paper:rank-gpt`, `paper:dpo` | If card references a specific paper |
| Level | `level:` | `level:beginner`, `level:intermediate`, `level:advanced` | Yes (exactly 1) |
| Type | `type:` | `type:definition`, `type:comparison`, `type:why`, `type:algorithm`, `type:paper`, `type:formula`, `type:tradeoff` | Yes (exactly 1) |
| Source | `source:` | `source:research-summary`, `source:lecture`, `source:blog`, `source:practitioner` | Yes (exactly 1) |

**Rules:**
- A card can have MULTIPLE `topic:` tags (e.g., a card comparing OPD and DPO gets `topic:opd,topic:dpo`)
- `level:` assignment: beginner = definitions, basic facts; intermediate = trade-offs, mechanisms, comparisons; advanced = math, formulas, emergent properties, open research
- `type:` pick the ONE that best describes what's being tested
- `paper:` only when the card is specifically about a paper's contribution
- `source:research-summary` is the default for cards from study-notes reports
- Use kebab-case for all tag values
- Tags are comma-separated within the Tags field (no spaces after commas)

**Examples:**

Card comparing OPD and DPO:
```
topic:opd,topic:dpo,type:comparison,level:advanced,source:research-summary
```

Basic definition card about GRPO:
```
topic:grpo,type:definition,level:beginner,paper:deepseek-r1,source:research-summary
```

Formula card about DPO loss:
```
topic:dpo,type:formula,level:advanced,paper:dpo,source:research-summary
```

Practitioner insight from a blog:
```
topic:rlhf,type:tradeoff,level:intermediate,source:practitioner
```

### Generation Rules

- Extract cards from ALL sections of the report (Quick Catchup, Stages, Themes, Reading Schedule, Practitioner Appendix)
- Prioritize: key transitions, paper contributions, comparison tables, definitions, trade-offs, decision frameworks
- Target: 40-70 cards per report (more for longer reports)
- Skip: changelog entries, navigation/metadata, and references (keep cards about content not structure)

### Mandatory Co-Update Rule

**Whenever a report `.md` file is created or updated, the corresponding `.csv` MUST also be regenerated.** This applies to:
- New report generation (Step 5)
- check-and-integrate updates
- Follow-up query bake-ins
- Any manual report edit

If the CSV cannot be generated in the same turn (e.g., context limits), add a note to the report's Changelog: `[CSV STALE — regenerate anki/{topic}/{filename}.csv]`.

### Anki Sync

To sync generated CSVs to Anki Desktop via AnkiConnect:

```bash
python3 src/skills/researcher/anki_sync.py \
    --csv-dir .notlocal/data/personal-researcher/reports/v2/notes/anki/ \
    --state .local/data/personal-researcher/.anki-sync-state.json
```

## File Locations

| Content | Path | Pipeline Stage |
|---------|------|----------------|
| Topic index | `.notlocal/data/personal-researcher/topics.md` | Topic Management |
| Ingested sources | `.notlocal/data/personal-researcher/sources/{topic}/` | Ingest |
| Knowledge base index | `.notlocal/data/personal-researcher/knowledge/index.md` | Compile |
| Knowledge pages | `.notlocal/data/personal-researcher/knowledge/{topic}/` | Compile |
| Query answers | `.notlocal/data/personal-researcher/knowledge/queries/` | File Query |
| Reports (notes) | `.notlocal/data/personal-researcher/reports/v2/notes/` | Report |
| Reports (FAQs) | `.notlocal/data/personal-researcher/reports/v2/faqs/` | Report |
| Anki CSVs | `.notlocal/data/personal-researcher/reports/v2/notes/anki/{topic}/` | Anki |
| Report versions | `.notlocal/data/personal-researcher/reports/.versions/` | Report |
| Seed topics | `.notlocal/data/personal-researcher/seeds/` | --- |
| Compilation state | `.local/data/personal-researcher/.researcher/state.json` | Compile |
| Health check stamp | `.local/data/personal-researcher/.health-check-last-run` | Health Check |
| Anki sync state | `.local/data/personal-researcher/.anki-sync-state.json` | Anki Sync |

## Query Filing Format

Queries are stored as markdown files in `.notlocal/data/personal-researcher/knowledge/queries/` with:
- Filename: kebab-case slug of the question
- Frontmatter: title (the question), summary (short answer), type: "query", createdAt
- Body: Full synthesized answer with section headers, links to knowledge pages via `[[Page Name]]`

## Source Ingestion Rules

Sources are the raw material. They go into `.notlocal/data/personal-researcher/sources/{topic}/` and must:
- Be saved as markdown files with frontmatter: `title`, `url` (or `path`), `ingestedAt`, `type`
- Preserve the original content faithfully (extract, don't summarize)
- Use kebab-case filenames derived from the source title
- Never be edited after creation — they are immutable records

## Knowledge Base Update Rules (Compile Stage)

Knowledge pages are the compiled, interlinked layer. They are derived FROM sources, not written directly:

- Each page must include frontmatter: `title`, `summary`, `sources` (list of source file paths used), `createdAt`, `updatedAt`
- Link related pages using `[[Page Name]]` wiki-link syntax
- Always update `.notlocal/data/personal-researcher/knowledge/index.md` when adding new entries
- Sources field must trace back to files in `.notlocal/data/personal-researcher/sources/` — this maintains the provenance chain
- When sources change, update the corresponding knowledge pages (update `updatedAt`)

## Report Update Rules

Every query resolution MUST end with a report update. The steps are:

1. Identify which report in `.notlocal/data/personal-researcher/reports/v2/notes/` or `.notlocal/data/personal-researcher/reports/v2/faqs/` is most relevant to the query topic
2. Add a new section (or update an existing one) with:
   - A clear heading describing the comparison/topic
   - Date added and sources used
   - Structured data (tables, benchmark comparisons) where applicable
   - A decision framework or key takeaways
3. Update the report's `## Changelog` table with the date and a short description
4. If no matching report exists, create a new report file following the generation guide and template

**Versioning** (applies to updates of existing reports):
- Assess novelty, contradiction, and importance of the new information
- Minor update (magnitude < 0.6): overwrite the current report in-place
- New version (magnitude >= 0.6 or contradiction >= 0.3): create a new version (v2, v3, etc.) under `.notlocal/data/personal-researcher/reports/.versions/{report-name}/`
- Always update `.notlocal/data/personal-researcher/reports/.versions/manifest.json` when creating new versions

**No query is complete until the report is updated.** The knowledge base stores atomic facts; the report synthesizes them into actionable context.

## Report Generation Standards

When creating or updating reports, you MUST follow the generation guide and template for the target folder:

| Folder | Generation Guide | Template | Format |
|--------|-----------------|----------|--------|
| `.notlocal/data/personal-researcher/reports/v1/` | `_generation-guide.md` in that folder | `_template.md` in that folder | Legacy |
| `.notlocal/data/personal-researcher/reports/v2/notes/` | `_generation-guide.md` in that folder | `_template.md` in that folder | Standard (Quick Catchup -> DE Probes -> Cost -> Seniority) |
| `.notlocal/data/personal-researcher/reports/v2/notes/` (study notes) | `_study-notes-generation-guide.md` in that folder | `_study-notes-template.md` in that folder | Study Notes (Quick Catchup -> Evolutionary Stages -> Themes -> Reading Schedule). **Filename:** `{topic-slug}--notes.md` |
| `.notlocal/data/personal-researcher/reports/v2/faqs/` | `_generation-guide.md` in that folder | `_template.md` in that folder | FAQ (Question -> Principal+ Answer -> Seniority Contrast) |

**Rules:**
- Before creating a new report, read the `_generation-guide.md` in the target subfolder for tone, structure, depth, and formatting expectations
- Use the `_template.md` in the target subfolder as the structural skeleton for new reports
- **Choose the right format**:
  - Use `notes/` (standard) for comprehensive topic deep-dives on systems/techniques
  - Use `notes/` (study notes) for literature surveys, reading roadmaps, and historical evolutions
  - Use `faqs/` for concise QnA with seniority-level differentiation
- **Format selection heuristic**: If the source material is a paper list, reading roadmap, or field evolution -> study notes. If it's a system to design/operate -> standard. If it's discrete questions -> FAQ.
- **Filename convention for study notes**: Always suffix study-notes output files with `--notes` (e.g., `rl-for-llms--notes.md`, `harness-engineering--notes.md`). Standard notes and FAQs use the topic slug without suffix (e.g., `rl-for-llms.md`).
- When updating an existing report, match the style and section conventions already established in that report (which should already conform to the guide/template)
- Never deviate from the generation guide's instructions on section ordering, citation style, or content depth
- If a new report subfolder is introduced, expect corresponding `_generation-guide.md` and `_template.md` files and follow them

## Code vs Data Separation

**All helper scripts live in `src/skills/researcher/`. All data lives under `.notlocal/data/personal-researcher/` (shared) and `.local/data/personal-researcher/` (local state).**

| Content Type | Location | Rule |
|-------------|----------|------|
| Helper scripts (compile, verify, sync) | `src/skills/researcher/` | Deterministic computation, external API calls |
| Reports, templates, generation guides | `.notlocal/data/personal-researcher/reports/` | Output artifacts + formatting instructions |
| Sources, knowledge, queries | `.notlocal/data/personal-researcher/` | Research data (immutable sources, compiled knowledge) |
| Local state (compilation, sync, health check) | `.local/data/personal-researcher/` | Machine-local state files |
| Config | `.local/skills-config.yaml` | Runtime settings (models, paths, thresholds) |

**Never put executable code (`.py`, `.sh`) inside data directories.** Data directories contain only:
- Markdown files (`.md`)
- JSON files (for metadata: `_jury_results.json`, `manifest.json`)
- Spreadsheets/PDFs (ingested sources)
