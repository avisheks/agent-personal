# Super-Agent: Unified Orchestrator Proposal

**Date:** 2026-09-10
**Branch:** `super-agent`
**Status:** RFC

---

## Problem

Today, each skill is invoked independently. The user must know which skill handles their question, what command to use, and what parameters to pass. For cross-cutting questions ("What's the status of my projects and are there any interviews this week?"), the user manually sequences multiple skill invocations. There is no unified entry point.

## Requirements

1. **Single master command** — one entry point for any user question
2. **Question decomposition** — break complex questions into sub-tasks mapped to specific skills
3. **Skill catalog awareness** — use [README.md](../README.md) (or a derived catalog) to understand which skills exist, what they do, and what commands they expose
4. **Plan-then-execute** — present the execution plan to the user before running it
5. **First-turn signoff only** — once the user approves the plan, execute all planned steps without re-asking
6. **Mid-session escalation** — if execution reveals a need for a skill NOT in the original plan, pause and ask for signoff before using it
7. **No repeated consent** — approved skills remain approved for the rest of the session

---

## Options

### Option A: Pure Skill File (Prompt-Only Orchestrator)

A single `skills/super-agent.md` file containing all orchestration logic as LLM instructions. No code. The agent reads [README.md](../README.md) as its skill catalog, decomposes questions, builds a plan, presents it, and executes.

**How it works:**

```
User: "What's the status of campaign-intent and help me prep for Friday's L6 interview"

Agent reads super-agent.md → reads README.md → produces:

Plan:
  Step 1: [coworker-tpm] /status campaign-intent
  Step 2: [coworker-interviewer] /prep (needs: JD, resume, competencies in inp/)
  Skills requiring approval: coworker-tpm, coworker-interviewer

User: "Approved"

Agent executes Step 1, then Step 2, no further signoff needed.
```

**Session state:** A markdown file (`.local/data/super-agent/{date}-session.md`) logs the approved plan and tracks execution progress. The orchestrator reads this file at each turn to know which skills are pre-approved.

**Signoff gating:** The skill file instructs the agent: "Before invoking any skill not listed in the approved plan, STOP and ask: 'To answer this, I need to use [skill]. This wasn't in the original plan. Proceed?'"

**Implementation:**

| Artifact | What |
|----------|------|
| `skills/super-agent.md` | Orchestrator SOP (~200 lines) |
| `.local/data/super-agent/` | Session logs |

**Pros:**
- Zero code — just a well-crafted prompt. Fastest to build and ship.
- Easy to iterate — edit the .md, no build step.
- Works with any LLM runtime (Claude Code, Claude API, etc.) — no Python dependency.
- Skill catalog (README) already exists and is maintained.

**Cons:**
- Signoff gating is advisory, not enforced. The LLM might invoke an unapproved skill if instructions aren't followed precisely. Risk is low but non-zero.
- Catalog parsing relies on the LLM correctly reading markdown tables from README. If README drifts in format, routing accuracy degrades.
- No programmatic session tracking — if the conversation context is compressed, the agent might lose track of which skills were approved.

**Estimated effort:** 1-2 hours.

---

### Option B: Python Orchestrator with Programmatic Gating

A Python script (`src/super_agent.py`) that programmatically manages the orchestration lifecycle: catalog lookup, plan generation (via LLM), approval tracking, and skill dispatch. The LLM is called for reasoning (decomposition, plan generation) but the gating logic is in code.

**How it works:**

```
User: "What's the status of campaign-intent and help me prep for Friday's L6 interview"

super_agent.py:
  1. Loads skills-catalog.yaml (structured catalog)
  2. Sends question + catalog to LLM → gets back structured plan JSON
  3. Presents plan to user, waits for approval
  4. Records approved skill IDs in session.yaml
  5. For each step: checks session.yaml → if approved, loads skill .md → dispatches
  6. If Step N needs a new skill: checks session.yaml → NOT approved → prompts user
```

**Session state:** A YAML file (`.local/data/super-agent/session.yaml`) with:
```yaml
session_id: "2026-09-10-14"
approved_skills: ["coworker-tpm", "coworker-interviewer"]
plan:
  - step: 1
    skill: coworker-tpm
    command: "/status campaign-intent"
    status: completed
  - step: 2
    skill: coworker-interviewer
    command: "/prep"
    status: pending
```

**Requires a structured catalog** — a new `skills/skills-catalog.yaml`:
```yaml
skills:
  - id: coworker-tpm
    name: "TPM"
    file: skills/coworker-tpm.md
    description: "Project status, daily plans, ticket updates, drift detection"
    commands: ["/review-project", "/plan-today", "/status", "/status-all", ...]
    triggers: ["project status", "what's blocked", "daily plan", "asana", ...]
    requires_config: true
  - id: personal-career
    name: "Career Advisor"
    file: skills/personal-career.md
    description: "Career strategy, job search, interview prep"
    commands: ["kickoff", "evaluate", "trajectory", "search", "mock", ...]
    triggers: ["career", "job search", "interview prep", "resume", ...]
    requires_config: false
```

**Implementation:**

| Artifact | What |
|----------|------|
| `src/super_agent.py` | Orchestrator script (~300-400 lines) |
| `skills/skills-catalog.yaml` | Structured skill catalog (~100 lines) |
| `.local/data/super-agent/` | Session state files |

**Pros:**
- Programmatic enforcement of signoff gating — code checks `approved_skills` before every dispatch. The LLM cannot bypass it.
- Structured catalog enables deterministic skill routing for common patterns (keyword triggers) before falling back to LLM reasoning.
- Session state is durable YAML — survives context compression, can be resumed across sessions.
- Testable — can unit test catalog loading, plan parsing, approval gating.

**Cons:**
- More code to build and maintain (~400 lines of Python).
- Catalog must stay in sync with skill files. Two sources of truth (README for humans, catalog for code) — risk of drift.
- Adds a Python dependency to what is currently a pure-markdown skill collection.
- Skill dispatch is the hard part: how does a Python script "invoke" a skill .md? It either (a) calls the LLM API directly (couples to a specific provider), or (b) shells out to `claude` CLI (couples to Claude Code). Either way, it's more opinionated about the runtime.

**Estimated effort:** 4-6 hours.

---

### Option C: Hybrid — Skill File + Structured Catalog (Recommended)

A `skills/super-agent.md` orchestrator SOP (like Option A) backed by a `skills/skills-catalog.yaml` (from Option B) for structured skill metadata. No Python orchestrator code. The LLM reads the catalog for routing decisions and the skill file for behavioral rules. Session state in a structured markdown log.

**How it works:**

```
User: "What's the status of campaign-intent and help me prep for Friday's L6 interview"

Agent reads super-agent.md → reads skills-catalog.yaml → produces:

┌─────────────────────────────────────────────────────┐
│ Execution Plan                                      │
├────┬──────────────────┬─────────────────────────────┤
│  # │ Skill            │ Action                      │
├────┼──────────────────┼─────────────────────────────┤
│  1 │ coworker-tpm     │ /status campaign-intent     │
│  2 │ coworker-interviewer │ /prep (inputs needed)   │
├────┴──────────────────┴─────────────────────────────┤
│ Skills requiring approval: coworker-tpm,            │
│ coworker-interviewer                                │
│                                                     │
│ Approve this plan? [yes / edit / reject]            │
└─────────────────────────────────────────────────────┘

User: "yes"

Agent records approved skills in session log → executes sequentially.

--- Later in the session ---

Agent: "To cross-reference your project deadlines with your interview schedule,
I'd need to use personal-career (not in the original plan). Approve?"
```

**Key insight:** The catalog gives the LLM structured data to reason over (instead of parsing markdown tables from README), while the skill file gives it behavioral rules (plan format, signoff protocol, escalation rules). No code sits in between — the LLM does the orchestration directly, but with better inputs than Option A.

**Session state:** `.local/data/super-agent/{date}-session.md`

```markdown
# Super-Agent Session — 2026-09-10

## Approved Plan
| # | Skill | Command | Status |
|---|-------|---------|--------|
| 1 | coworker-tpm | /status campaign-intent | completed |
| 2 | coworker-interviewer | /prep | in-progress |

## Approved Skills
- coworker-tpm (plan step 1)
- coworker-interviewer (plan step 2)

## Mid-Session Approvals
(none yet)
```

The orchestrator reads this file at the start of each turn. If context gets compressed, the session file preserves the approval state.

**Implementation:**

| Artifact | What |
|----------|------|
| `skills/super-agent.md` | Orchestrator SOP (~250 lines) |
| `skills/skills-catalog.yaml` | Structured skill metadata (~120 lines) |
| `.local/data/super-agent/` | Session logs |

**Pros:**
- Structured catalog improves routing accuracy over raw README parsing (Option A's weakness) without adding code (Option B's cost).
- Catalog is a single flat YAML — easy to maintain, easy to validate, easy to read.
- Session log in markdown is both human-readable and LLM-parseable — good for debugging.
- README remains the human-facing docs; catalog is the machine-facing index. Clear separation of concerns. README can evolve freely without breaking routing.
- No Python dependency, no runtime coupling — works anywhere a skill .md works.
- Catalog can be auto-generated from README if they drift (a one-liner script, not a runtime dependency).

**Cons:**
- Signoff gating is still advisory (same as Option A). The LLM is instructed to check the session log, but it's not programmatically enforced.
- Two catalog artifacts (README + skills-catalog.yaml) — but the catalog is small, stable, and only changes when skills are added/removed.
- Session log fidelity depends on the LLM reliably writing/reading the markdown table. A structured format (YAML) in Option B is more robust, but markdown is good enough in practice.

**Estimated effort:** 2-3 hours.

---

## Comparison Matrix

| Dimension | A: Pure Prompt | B: Python | C: Hybrid (Recommended) |
|-----------|---------------|-----------|------------------------|
| **Routing accuracy** | Medium (parses README tables) | High (structured catalog + keyword triggers) | High (structured catalog) |
| **Signoff enforcement** | Advisory (prompt-based) | Programmatic (code-enforced) | Advisory (prompt-based) |
| **Build effort** | 1-2 hours | 4-6 hours | 2-3 hours |
| **Maintenance burden** | Low (one .md file) | Medium (code + catalog + README sync) | Low (one .md + one .yaml) |
| **Runtime coupling** | None | Python + LLM API or CLI | None |
| **Session durability** | Medium (markdown, may compress) | High (YAML, durable) | Medium-High (markdown, refreshed each turn) |
| **Testability** | Manual only | Unit-testable | Manual only |
| **Extensibility** | Add to README | Add to catalog + code | Add to catalog |

---

## Recommendation: Option C (Hybrid)

Option C hits the best tradeoff for this project:

1. **Routing accuracy matters more than programmatic gating.** The primary risk isn't the LLM ignoring approval rules (it won't — the instruction is clear and the session log reinforces it). The primary risk is the LLM picking the wrong skill. A structured catalog with `triggers` and `description` fields directly addresses this.

2. **No code means no runtime coupling.** This skill collection works across Claude Code, Claude API, and potentially other runtimes. Adding a Python orchestrator (Option B) locks it to a specific invocation pattern. The hybrid approach preserves portability.

3. **The maintenance cost is minimal.** The catalog only changes when skills are added or removed — maybe once a month. And it can be validated with a one-liner: `diff <(grep '^  - id:' skills-catalog.yaml) <(ls skills/*.md)`.

4. **Option A is too fragile for skill routing.** README tables are written for humans, not machines. Column formats, section nesting, and prose descriptions will evolve. A purpose-built catalog YAML is a small upfront cost that pays for itself in routing reliability.

5. **Option B is overbuilt for the risk.** Programmatic gating solves a problem that hasn't manifested — LLMs follow "ask before using an unapproved skill" instructions reliably, especially when reinforced by a session log they read each turn. The Python code would add real maintenance cost for marginal safety gain.

---

## Next Steps (if approved)

1. Create `skills/skills-catalog.yaml` — structured metadata for all 10 active skills (latest version only)
2. Create `skills/super-agent.md` — the orchestrator SOP with plan/approve/execute protocol
3. Test with 3-4 representative queries:
   - Single-skill direct hit ("Generate my weekly AI briefing")
   - Multi-skill decomposition ("Status of campaign-intent + prep for Friday's interview")
   - Mid-session escalation (start with TPM status, then ask a career question)
   - Ambiguous routing ("Help me write something about the project")
4. Iterate on the catalog's `triggers` fields based on test results
