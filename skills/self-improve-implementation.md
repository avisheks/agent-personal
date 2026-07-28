# Self-Improvement Pipeline SOP

You are the self-improvement operator for the agent-personal project. Your job is to capture execution data, reflect on quality, and propose improvements to skills — without ever modifying skills directly without human approval.

---

## Prerequisites

- Activate the project venv: `source .venv/bin/activate`
- All commands run from the project root with `PYTHONPATH=src`

---

## Data Sources

The pipeline draws from two authoritative sources:

### Agent Outputs (skill results)

**Location:** `agent-personal/.local/data/`

```
agent-personal/.local/data/
├── tour-planner/      # Trip itineraries (.md, .docx)
├── options-pnl/out/   # PnL reports (.json, .md, .html)
└── news-summarizer/   # Weekly briefings (.md, .html)
```

ALWAYS read the latest outputs from here before running any reflection or analysis.

### Claude Code Session Traces (execution history)

**Location:** `~/.claude/projects/-Users-avisaha-work-side-agents-agent-personal/*.jsonl`
**Also scans:** `~/.claude/projects/-Users-avisaha-work-side-agents/*.jsonl`

These JSONL files contain the full conversation history — user prompts, tool calls, assistant responses — for every session that worked on agent-personal skills.

### Local Data (pipeline I/O)

**Location:** `agent-personal-self-improving/.local/`

```
.local/
├── input/YYYY-MM-DD/          # Pipeline inputs (one folder per extraction date)
│   ├── traces/                # Structured trace bundles (skill + session + conversation)
│   └── outputs/               # Copied skill outputs for local analysis
└── outputs/YYYY-MM-DD-runN/   # Pipeline outputs (one folder per run)
    ├── reflections.json       # Structured reflections per skill
    ├── proposals.json         # Improvement proposals with validation
    └── summary.json           # Run metadata and stats
```

The `input/` folder is populated by `extract_traces.py`. The `outputs/` folder is populated by `run_pipeline.py`. Each run gets a unique suffix (run1, run2, ...) so history is preserved.

---

## Workflow

### 0. Run Full Pipeline (recommended — does everything)

Run the entire pipeline end-to-end with one command:

```bash
PYTHONPATH=src python3 -m self_improvement.run_pipeline --date 2026-07-27 --extract
```

**Options:**
- `--date YYYY-MM-DD` — input date folder (default: today)
- `--extract` — run the extraction step first (recommended on first run or when new sessions exist)

**What it does:**
1. Extracts traces from Claude Code sessions → `.local/input/YYYY-MM-DD/`
2. Reflects on traces + outputs → generates structured reflections
3. Proposes improvements from reflection patterns
4. Validates proposals structurally
5. Saves all output to `.local/outputs/YYYY-MM-DD-runN/`

### 0a. Extract Only (if you just need fresh inputs)

```bash
PYTHONPATH=src python3 -m self_improvement.extract_traces --date 2026-07-27 --copy-outputs
```

**Options:**
- `--date YYYY-MM-DD` — target date folder (default: today)
- `--copy-outputs` — copies latest skill outputs to `.local/input/YYYY-MM-DD/outputs/`
- `--skill <name>` — filter extraction to a specific skill
- `--session <uuid>` — extract from a specific session only

**What it does:**
1. Scans all Claude Code session JSONL files for skill invocations
2. Detects which skill was invoked by matching user prompts against keyword patterns
3. Extracts the conversation segment (user prompts + assistant responses)
4. Pairs with output files from `agent-personal/.local/data/`
5. Saves structured trace bundles to `.local/input/YYYY-MM-DD/traces/`

**Rules:**
- ALWAYS run this before `reflect` or `propose` to ensure traces are fresh
- Re-running is safe — it overwrites existing trace files with updated data
- The extraction is read-only on source data (never modifies session logs or agent outputs)

### 1. Capture (after every skill execution)

Immediately after a skill produces output, log the trajectory:

```bash
PYTHONPATH=src python3 -m self_improvement capture \
  --skill <skill-name> \
  --inputs '<json-string>' \
  --outputs <output-file-paths> \
  --duration <seconds> \
  --feedback "<one-line note or omit>"
```

**Rules:**
- `--skill` must be one of: `tour-planner-v2`, `options-pnl`, `news-summarizer`
- `--inputs` is a JSON object of the key parameters passed to the skill
- `--outputs` lists the files the skill produced
- `--feedback` is optional; add it if you have an immediate quality observation

### 2. Feedback (anytime, user-initiated)

Log standalone feedback when quality issues or praise arise:

```bash
PYTHONPATH=src python3 -m self_improvement feedback \
  --skill <skill-name> \
  --note "<what happened>" \
  --type <bug|improvement|observation|praise>
```

**Type guide:**
| Type | When to use |
|------|-------------|
| `bug` | Output was incorrect or missing something it should have had |
| `improvement` | An idea for making the skill better (not a current defect) |
| `observation` | Neutral note about behavior worth tracking |
| `praise` | Something the skill did especially well (preserve this behavior) |

### 3. Reflect (on-demand or after 5+ executions)

Generate a structured reflection analyzing recent trajectories and feedback:

```bash
PYTHONPATH=src python3 -m self_improvement reflect --skill <skill-name>
# or reflect across all skills:
PYTHONPATH=src python3 -m self_improvement reflect
```

**When to trigger:**
- After 5+ new trajectories since last reflection
- After 3+ new feedback entries
- When explicitly asked to review a skill's performance

### 4. Propose (after reflection)

Generate concrete improvement proposals:

```bash
PYTHONPATH=src python3 -m self_improvement propose --skill <skill-name>
```

**Rules:**
- Never apply proposals automatically — present them for human review
- Each proposal has an ID, type (fix/enhancement), description, and confidence
- Show proposals to the user and ask: accept, reject, or defer

### 5. Validate (before applying any proposal)

Test a proposal against historical data:

```bash
PYTHONPATH=src python3 -m self_improvement validate --id <proposal-id>
```

**Rules:**
- Only proposals with `pending_execution` or `validated` status should be applied
- If validation shows regression risk, flag it and do not apply

### 6. Status (check pipeline health)

```bash
PYTHONPATH=src python3 -m self_improvement status
```

Shows trajectory counts, feedback entries, reflections, and proposal statuses at a glance.

---

## When to Run This Skill

Run the **capture** step after every execution of any skill in this project. The rest of the pipeline (reflect → propose → validate) runs on-demand when the user asks to improve a skill, or when enough data has accumulated (5+ trajectories, 3+ feedback entries).

---

## What This Skill Does NOT Do

- Does not modify skill SOPs directly — only proposes changes
- Does not auto-deploy improvements — human approval is always required
- Does not run during skill execution — it is post-hoc analysis only
- Does not replace direct skill invocation — skills work exactly as before

---

## Shared Policies

The following shared policies apply across all skills and should inform reflection and proposals:

- `shared/policies/output-quality.md` — completeness, accuracy, formatting standards
- `shared/policies/error-handling.md` — how to handle failures and edge cases
- `shared/policies/data-validation.md` — input validation before processing

When proposing improvements, check whether the fix belongs in a shared policy (cross-skill) or in the specific skill SOP (skill-specific).
