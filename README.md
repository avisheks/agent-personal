# Agent Personal

A collection of AI agent skills (SOPs) for personal productivity and professional work. Each skill is a standalone markdown file that instructs an LLM agent how to perform a specific task domain.

Skills are organized into two categories:

- **`personal-*`** — Personal productivity skills (career, travel, finance, news)
- **`coworker-*`** — Professional/work skills (TPM, document writing, interviewing, code analysis, research)

## Quick Start

### Using the Super-Agent (recommended)

The **super-agent** is a unified orchestrator that routes any question to the right skill(s) automatically. Just ask your question in natural language:

```
"What's the status of campaign-intent and help me prep for Friday's interview"
"Generate my weekly AI briefing"
"Review this design doc and then write a progress report"
"Plan a family trip to Japan for next summer"
```

The super-agent will:
1. Read the [skills catalog](skills/skills-catalog.yaml) to determine which skill(s) to invoke
2. Present an execution plan for your approval
3. On your signoff, execute the plan autonomously — no repeated consent needed
4. If a new skill is needed mid-session that wasn't in the original plan, it will ask before using it

The orchestrator SOP lives at [skills/super-agent.md](skills/super-agent.md). Point your agent at this file as the entry point.

### Using skills directly

You can also invoke any skill directly by pointing your agent at its SOP file:

```
skills/personal-career.md          # Career counseling, job search, interview prep
skills/coworker-tpm.md             # Technical project management
skills/personal-news-summarizer.md # Weekly AI research briefings
```

### Configuration

Coworker skills reference a runtime config for org-specific values (internal URLs, project IDs, etc.):

| File | Purpose | Committed? |
|------|---------|------------|
| [skills/sample-config.yaml](skills/sample-config.yaml) | Template with placeholder values | Yes |
| `.local/skills-config.yaml` | Your real config (sensitive) | No (gitignored) |

To set up: copy [skills/sample-config.yaml](skills/sample-config.yaml) to `.local/skills-config.yaml` and fill in your values.

---

## Skills Overview

### Personal Skills

| Skill | File | What It Does |
|-------|------|-------------|
| **Career Advisor** | [personal-career.md](skills/personal-career.md) | Career strategy, job sourcing, interview prep with 3 personas and persistent state |
| **News Summarizer** | [personal-news-summarizer.md](skills/personal-news-summarizer.md) | Weekly 23-section AI research briefings with topic specializations |
| **Options PnL** | [personal-options-pnl-v3.md](skills/personal-options-pnl-v3.md) | Wheel trading PnL reporting + trade recommendations across 3 brokerages |
| **Tour Planner** | [personal-tour-planner-v3.md](skills/personal-tour-planner-v3.md) | Family travel itinerary generation with day-by-day timing and booking links |

### Coworker Skills

| Skill | File | What It Does |
|-------|------|-------------|
| **TPM** | [coworker-tpm.md](skills/coworker-tpm.md) | Project status, daily plans, Asana ticket updates, drift detection |
| **Interviewer** | [coworker-interviewer.md](skills/coworker-interviewer.md) | Interview question generation + post-interview feedback writing |
| **Doc Writer** | [coworker-doc-writer.md](skills/coworker-doc-writer.md) | Narrative documents, roadmaps, science docs in 6-pager tradition |
| **Doc Reviewer** | [coworker-doc-reviewer.md](skills/coworker-doc-reviewer.md) | Review PRFAQ, design docs, PRDs, OP narratives, runbooks, COEs |
| **Paper Reviewer** | [coworker-paper-reviewer.md](skills/coworker-paper-reviewer.md) | Academic paper review with rubric evaluation and consistency verification |
| **Code Cracker** | [coworker-code-cracker.md](skills/coworker-code-cracker.md) | Deep technical analysis of unfamiliar codebases |
| **Scientist** | [coworker-scientist.md](skills/coworker-scientist.md) | ML experiment strategy — patterns, suggestions, run comparisons |

All coworker skills load org-specific values from `.local/skills-config.yaml`. See [Configuration](#configuration) above.

---

## Project Structure

```
agent-personal/
├── skills/                        # Skill SOPs (markdown)
│   ├── super-agent.md             # Unified orchestrator (entry point)
│   ├── skills-catalog.yaml        # Machine-readable skill index
│   ├── sample-config.yaml         # Config template (safe to commit)
│   ├── coworker-*.md              # Professional/work skills
│   ├── personal-*.md              # Personal productivity skills
│   └── news-topics/               # Topic configs for news-summarizer
├── src/                           # Supporting Python scripts
│   ├── compute_pnl.py             # Options PnL computation
│   ├── validate_pnl.py            # PnL validation against reference
│   ├── render_report.py           # PnL report rendering (md + html)
│   ├── matcher.py                 # Trade filtering and FIFO matching
│   ├── parsers.py                 # Broker CSV parsers
│   ├── analyze_insights.py        # Portfolio insight generation
│   ├── recommend_trades.py        # Wheel trade recommendations
│   ├── news-report/
│   │   └── render_html.py         # News report HTML renderer
│   └── tour-planner/
│       ├── generate_itinerary.py  # Itinerary generation
│       ├── generate_annotated.py  # Annotated docx generation
│       ├── align_body.py          # Body alignment post-processing
│       ├── insert_summary.py      # Summary insertion
│       ├── lookup_hours.py        # Opening hours lookup
│       ├── compact_docx.py        # Docx compaction
│       └── fix_html_colwidths.py  # HTML table column width fixes
├── tst/                           # Tests
├── proposals/                     # Design proposals
├── .notlocal/                     # Non-sensitive skill data (committable)
│   └── data/
│       ├── news/                  # AI news briefing reports
│       ├── personal-career/       # Career state, study plans, mock sessions
│       └── tour-planner/          # Trip itineraries by slug
├── .local/                        # Sensitive runtime data (gitignored)
│   ├── skills-config.yaml         # Org-specific config (sensitive)
│   ├── data/options-pnl/          # Brokerage CSVs, PnL reports (financial PII)
│   └── logs/super-agent/          # Event log (events.jsonl)
└── README.md                      # This file
```

---

## Appendix: Skill Catalog

Detailed command reference for each skill. For machine-readable metadata, see [skills/skills-catalog.yaml](skills/skills-catalog.yaml).

### A.1 Career Advisor — [personal-career.md](skills/personal-career.md)

Multi-persona career advisor with persistent session state. Activates one of three personas based on user intent.

**Persona: Career Counselor** — Career strategy, trajectory analysis, offer negotiation

| Command | Description |
|---------|-------------|
| `kickoff` | Initialize career profile — collect background, goals, constraints |
| `evaluate [move]` | Analyze a specific career move (new role, pivot, promotion, lateral) |
| `trajectory` | Assess current career trajectory and recommend course corrections |
| `pivot` | Design a career pivot strategy with bridge-building steps |
| `promote` | Assess promotion readiness and build a promotion case |
| `compare` | Side-by-side comparison of two or more career options |
| `skill-gap` | Identify skill gaps for a target role and build a development plan |
| `negotiate-offer` | Coach on offer evaluation and negotiation strategy |

**Persona: Job Sourcer** — Opportunity sourcing, market intelligence, JD analysis

| Command | Description |
|---------|-------------|
| `search [criteria]` | Source opportunities matching criteria from job boards and market signals |
| `market-scan [role/domain]` | Analyze the job market for a role or domain — demand, comp, trends |
| `company-research [company]` | Deep-dive research on a specific company as a potential employer |
| `decode [JD]` | Analyze a job description — fit assessment, red flags, hidden requirements |
| `batch-triage` | Rank and triage multiple JDs the user is considering |
| `track` | Review and update the applications tracker |

**Persona: Interview Buddy** — Interview prep, mock sessions, story coaching

| Command | Description |
|---------|-------------|
| `study-plan [company] [role]` | Generate a structured study plan with timeline, topics, and resources |
| `stories` | Build and manage the STAR storybank |
| `practice [type]` | Run targeted practice drills (behavioral, technical, case study) |
| `mock [format]` | Run a full simulated interview (4-6 questions) with holistic debrief |
| `analyze` | Score and analyze a real interview transcript |
| `prep [company]` | Company + role prep brief with predicted questions |
| `concerns` | Generate likely interviewer concerns + counter-strategies |
| `hype` | Pre-interview confidence coaching and day-of game plan |
| `debrief` | Post-interview rapid capture and reflection |
| `progress` | Review trends across practice sessions and interviews |

Practice drills follow an 8-stage progression (`practice ladder` → `practice pushback` → ... → `practice technical`), each unlocking when the prior stage scores >= 3 on all dimensions.

**Data:** `.notlocal/data/personal-career/` (session state, study plans, mock transcripts, job search results)

---

### A.2 News Summarizer — [personal-news-summarizer.md](skills/personal-news-summarizer.md)

Weekly AI research briefing generator. Produces structured 23-section reports covering technical developments, research papers, open-source projects, business intelligence, and strategic analysis. Output is both `.md` and `.html` (self-contained, styled).

| Invocation | Description |
|------------|-------------|
| `Run news-summarizer` | Default broad AI landscape report |
| `Run news-summarizer with topic: agentic-ai` | Topic-specific report |
| `Run news-summarizer with topic: rl-in-ai` | RL for LLM post-training |
| `Run news-summarizer with topic: rl-in-agentic-ai` | RL for agentic AI |
| `Run news-summarizer with topic: ai-for-tpm-pm` | AI for TPMs and PMs |
| `Run news-summarizer with topic: world-models` | World models research |
| `Run news-summarizer with topic: jobs-in-ai` | Senior AI job market intelligence |

Topic configs live in [skills/news-topics/](skills/news-topics/). See [news-topics/README.md](skills/news-topics/README.md) for the schema and how to add new topics.

**Rendering:** HTML reports are generated via [src/news-report/render_html.py](src/news-report/render_html.py).

**Data:** `.notlocal/data/news/` (generated reports by topic)

---

### A.3 Options PnL — [personal-options-pnl-v3.md](skills/personal-options-pnl-v3.md)

Options wheel trading PnL reporter and trade recommendation engine. Computes realized PnL for Cash-Secured Puts and Covered Calls across three brokerages (Fidelity, Tastytrade, Thinkorswim). Produces consolidated reports with monthly/weekly breakdowns, trendline charts, and trade-level detail. v3 adds forward-looking trade recommendations.

| Phase | What It Does | Key Script |
|-------|-------------|------------|
| Phase 1 | SOP self-validation against known-good data | [src/compute_pnl.py](src/compute_pnl.py), [src/validate_pnl.py](src/validate_pnl.py) |
| Phase 2 | Data-format validation of new broker CSVs | [src/parsers.py](src/parsers.py) |
| Phase 3 | Standalone PnL computation on new data | [src/compute_pnl.py](src/compute_pnl.py) |
| Phase 4 | Combined computation (validated + new) | [src/compute_pnl.py](src/compute_pnl.py) |
| Phase 5 | Cross-validation of combined output | [src/validate_pnl.py](src/validate_pnl.py) |
| Phase 6 | Report rendering (md + html + charts) | [src/render_report.py](src/render_report.py) |

Supporting code: [src/matcher.py](src/matcher.py) (trade filtering, spread detection, FIFO matching), [src/analyze_insights.py](src/analyze_insights.py) (portfolio insights), [src/recommend_trades.py](src/recommend_trades.py) (wheel trade recommendations).

Prior versions: [v1](skills/personal-options-pnl.md), [v2](skills/personal-options-pnl-v2.md).

**Data:** `.local/options-pnl/` (broker CSVs in `inp/`, reports in `out/`, reference spreadsheets in `ref/`)

---

### A.4 Tour Planner — [personal-tour-planner-v3.md](skills/personal-tour-planner-v3.md)

Family travel itinerary generator. Reads trip parameters, accommodation details, traveler composition, and optional preferences from structured input files. Produces detailed day-by-day itineraries with timing, booking links, weather-appropriate dress codes, and transit routing. Output is `.docx`.

**Input:** `{TRIP-SLUG}/input/input.txt` (required), `input/preferences.md` (optional, authoritative overrides), `input/samples.txt` (optional, reference itinerary URLs).

**Output:** `{TRIP-SLUG}/output/trip-itinerary-latest.docx`

Supporting code: [src/tour-planner/](src/tour-planner/) — `generate_itinerary.py`, `generate_annotated.py`, `align_body.py`, `insert_summary.py`, `lookup_hours.py`, `compact_docx.py`, `fix_html_colwidths.py`.

Prior versions: [v1](skills/personal-tour-planner-v1.md), [v2](skills/personal-tour-planner-v2.md).

---

### A.5 TPM — [coworker-tpm.md](skills/coworker-tpm.md)

AI Technical Project Manager. Aggregates signals from Asana, Slack, Git, meeting notes, and design docs to produce project status reports, daily plans, and ticket updates. Detects drift between planned and actual state.

| Command | Description | Requires LLM? |
|---------|-------------|----------------|
| `/review-project` | Categorized status report (on-track / at-risk / needs-escalation / drift) | Optional |
| `/plan-today` | Prioritized daily plan with actionable steps | Optional |
| `/update-asana` | Propose and apply Asana ticket updates | Yes |
| `/detail-ticket [ID]` | Generate detailed ticket description with acceptance criteria | Yes |
| `/status [SLUG]` | Run daily status questions for a project | Yes |
| `/status-all` | Run daily status for ALL projects | Yes |
| `/weekly-status [SLUG]` | Pull weekly status from Asana Overview tab | No |
| `/weekly-status-all` | Pull weekly status for ALL projects | No |
| `/progress-report [SLUG]` | Comprehensive progress report (md + html) | Yes |
| `/refresh` | Re-aggregate context from all sources | No |

Also supports free-form questions (e.g., "Why is the auth service blocked?").

**Config keys:** `tpm.projects`, `tpm.user_gid`, `tpm.notification_email`, `tpm.cron`

**Data:** `.local/data/tpm/{project-slug}/` (daily/weekly status files, deep-dives, progress reports)

---

### A.6 Interviewer — [coworker-interviewer.md](skills/coworker-interviewer.md)

Interview assistant operating in two modes: pre-interview question generation and post-interview feedback writing.

| Command | Mode | Description |
|---------|------|-------------|
| `/prep` | Pre-Interview | Generate tailored questions + evaluation rubrics from JD, resume, and competencies |
| `/write-feedback` | Post-Interview | Transform raw interview notes into polished, professional feedback |

**Config keys:** `interviewer.interview_resources` (question bank URLs), `interviewer.terminology` (bar language, recommendation terms), `interviewer.level_expectations`

**Data:** `.local/data/interviewer/inp/` (inputs per candidate), `.local/data/interviewer/out/` (generated plans/feedback), `.local/data/interviewer/ref_docs/` (reference samples)

---

### A.7 Doc Writer — [coworker-doc-writer.md](skills/coworker-doc-writer.md)

Document generator with multiple personas. Produces narrative prose documents following the 6-pager tradition. Output is `.md` + `.docx` (via pandoc).

| Command | Persona | Description |
|---------|---------|-------------|
| `/write-doc` | Doc Writer | Generate a document from a prompt and input materials |
| `/plan` | Planner | Generate a project roadmap with milestones (`.xlsx` output) |
| `/science-strategy` | Science Strategy | High-level multi-stage strategy doc (~5 pages) |
| `/science-doc` | Science Design | Detailed science design doc with appendices |
| `/science-deep-dive` | Science Deep-Dive | Landscape analysis with literature grounding (`.html` output) |

Companion file: [coworker-doc-writer-style-guide.md](skills/coworker-doc-writer-style-guide.md) — reusable writing style rules (tone, structure, bullet-narrative format, verbiage, anti-patterns).

**Config keys:** `doc-writer.writing_convention`, `doc-writer.example_systems`

**Data:** `.local/data/doc-writer/{project-name}/` (inputs in `inp/`, references in `ref/`, output in `out/`)

---

### A.8 Doc Reviewer — [coworker-doc-reviewer.md](skills/coworker-doc-reviewer.md)

Document reviewer that auto-detects document type and applies the matching reviewer persona.

| Document Type | Detection Signals |
|---------------|-------------------|
| PRFAQ | "Press Release" + "FAQ" sections |
| Design Doc / 1-Pager | "Design", "Architecture", "Components" sections |
| PRD | "Requirements", "User Stories", "Acceptance Criteria" |
| OP1/OP2 Narrative | "Goals", "Tenets", "State of the Business" |
| Runbook / Playbook | "Steps", "Procedures", "Troubleshooting" |
| Post-Mortem / COE | "Timeline", "Root Cause", "Corrective Actions" |

**Data:** `.local/data/doc-reviewer/inp/` (documents to review), `.local/data/doc-reviewer/out/` (review output)

---

### A.9 Paper Reviewer — [coworker-paper-reviewer.md](skills/coworker-paper-reviewer.md)

Academic paper reviewer. Reads research paper PDFs, evaluates them against a provided rubric, and produces structured review output (`.md` + `.html`). Includes a 3-phase pipeline: draft review, consistency verification against source paper, then fix and finalize. Supports parallel multi-paper review with region-based load distribution.

```
/review-papers --input <path/to/papers/> --rubric <path/to/rubric.md> --output <path/to/reviews/>
```

**Config keys:** `paper-reviewer.llm.region_pool`, `paper-reviewer.llm.model_id`

---

### A.10 Code Cracker — [coworker-code-cracker.md](skills/coworker-code-cracker.md)

Deep technical analysis of unfamiliar codebases. Produces structured intelligence reports answering: what does it do, how does it do it, and how does it compare to the ecosystem. Designed for fast ramp-up on new repos, vendor evaluations, and technology scouting.

| Command | Description |
|---------|-------------|
| `/crack` | Full analysis of a codebase (report + ecosystem comparison) |
| `/compare` | Ecosystem comparison only (requires prior `/crack` or manual context) |

Output: `report.md` + `report.html` in `.local/data/code-cracker/{project-name}/`

---

### A.11 Scientist — [coworker-scientist.md](skills/coworker-scientist.md)

Experiment strategy agent for iterative ML research. Analyzes experiment history, detects patterns, generates next-experiment suggestions, and provides run comparisons.

| Command | Description | Requires LLM? |
|---------|-------------|----------------|
| `/analyze-experiments` | Full analysis: patterns, best/worst runs, narrative, gaps | Optional |
| `/suggest-next` | 3-5 ranked next experiment suggestions based on history and feedback | Optional |
| `/compare-runs <A> <B>` | Side-by-side comparison of specified runs | No |
| `/patterns` | Rule-based pattern extraction (no LLM needed) | No |
| `/feedback <id> <outcome>` | Record feedback on a past suggestion (useful / not_useful / partially_useful) | No |

Pattern detection includes: hyperparameter sensitivity (Pearson correlation), diminishing returns, metric tradeoffs, and top configuration clustering.

**Data:** `data/scientist/results/` (experiment JSONs), `data/scientist/notebooks/` (Jupyter files), `data/scientist/tracking/` (MLflow/W&B exports)
