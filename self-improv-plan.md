# Self-Improving Agents: Design Plan for `agent-personal`

## Current State

The project has **3 skills** (markdown SOPs) that are invoked directly:
- **tour-planner-v2** — generates family travel itineraries through a multi-layer pipeline
- **options-pnl** — computes options trading PnL across brokers
- **news-summarizer** — produces weekly AI research briefings

These are supported by Python code in `src/` and data in `.local/data/`. Each skill is invoked manually, and they produce outputs. There is no feedback loop, no execution memory, and no cross-skill learning.

## Goal

Add a self-improvement layer that:
1. Observes skill executions and captures what happened
2. Reflects on quality and identifies improvement opportunities
3. Generalizes learnings across skills
4. Validates proposed changes won't regress
5. Deploys improvements to skills/shared code

**Constraint:** Skills remain directly usable exactly as they are today.

---

## Design Alternatives

### Alternative A: Post-Execution Hooks (Event-Driven)

```
┌─────────────────────────────────────────────────┐
│  Invoke skill normally (no change)              │
│  ↓                                              │
│  Skill executes → produces output               │
│  ↓                                              │
│  Hook captures trajectory (async, non-blocking) │
│  ↓                                              │
│  Improvement loop runs on-demand or scheduled   │
└─────────────────────────────────────────────────┘
```

**How it works:**
- After each skill run, a hook runs `python3 src/self_improvement/capture.py --skill <name> --output <path>`
- This logs the execution trace (inputs, outputs, duration, any errors, feedback)
- Periodically, run `python3 src/self_improvement/improve.py` which: reflects → generalizes → validates → proposes changes
- Human approves/rejects proposed changes (human-in-the-loop gate)

**New files:**
```
agent-personal/
├── skills/                        # UNCHANGED
├── src/
│   └── self_improvement/
│       ├── capture.py             # Logs trajectory after execution
│       ├── reflector.py           # Analyzes trajectories for patterns
│       ├── generalizer.py         # Extracts cross-skill improvements
│       ├── validator.py           # Tests proposed changes don't regress
│       ├── proposer.py            # Generates improvement PRs/diffs
│       └── config.yaml            # Which skills to track, thresholds
├── memory/
│   ├── trajectories/              # Raw execution logs
│   ├── reflections/               # Analysis output
│   ├── improvements/              # Proposed + applied improvements
│   └── policies/                  # Cross-skill shared policies
└── shared/
    ├── prompts/                   # Reusable prompt fragments
    ├── evaluation/                # Quality rubrics per skill
    └── templates/                 # Shared output templates
```

**Pros:**
- Zero change to existing skills — fully backward compatible
- Simple to implement incrementally (start with capture, add reflection later)
- Human stays in the loop for deployment
- Low risk — worst case, just don't run the improvement loop

**Cons:**
- Requires remembering to capture after each run (unless hooked into Claude Code)
- Improvement quality depends on trajectory quality (garbage in, garbage out)
- No real-time adaptation during execution

---

### Alternative B: Skill Wrapper / Middleware

```
┌──────────────────────────────────────────────────────┐
│  skill-runner.py wraps execution:                    │
│  1. Load skill SOP                                   │
│  2. Load relevant improvements from memory/policies/ │
│  3. Inject into context (appended policies section)  │
│  4. Execute skill                                    │
│  5. Capture trajectory                               │
│  6. Optionally trigger reflection                    │
└──────────────────────────────────────────────────────┘
```

**How it works:**
- A `skill-runner.py` script wraps skill invocation
- Before execution, it appends learned policies/guidelines to the skill SOP dynamically
- After execution, it auto-captures the trajectory
- Direct invocation of the skill markdown still works (without enhancements)

**New files (additions to Alt A):**
```
src/self_improvement/
├── runner.py                      # Wraps skill invocation
├── enricher.py                    # Injects learned policies before execution
└── ...
```

**Pros:**
- Automated capture (no need to remember)
- Skills get smarter at runtime via injected policies without changing the source SOP
- Still backward compatible (skills work without the wrapper)

**Cons:**
- Adds a layer of indirection — harder to debug
- "Injected policies" can drift from the source SOP, creating confusion about what's authoritative
- Requires maintaining the runner alongside direct invocation

---

### Alternative C: Shared Memory + Periodic Distillation (Batch-Oriented)

```
┌───────────────────────────────────────────────────┐
│  Skills execute normally (no change)              │
│  ↓                                                │
│  Manually log feedback: "that trip was great"     │
│  or "the PnL missed AMZN trades"                  │
│  ↓                                                │
│  Weekly/monthly: run distill.py                   │
│  → Reads all feedback + prior outputs             │
│  → Produces improvement candidates                │
│  → Review and apply to skill SOPs                 │
└───────────────────────────────────────────────────┘
```

**How it works:**
- Keep a `memory/feedback.jsonl` file for quick notes after using a skill
- A distillation script periodically analyzes accumulated feedback + outputs
- It proposes concrete SOP edits (diffs) for review and application
- Cross-skill patterns get extracted into `shared/policies/` which any skill can reference

**Pros:**
- Simplest implementation — just a feedback log + a reflection script
- No runtime changes at all
- Natural for someone who already iterates on SOPs manually (tour-planner went from v1 to v2)
- Batched reflection produces higher-quality insights than per-execution

**Cons:**
- Entirely manual capture (must remember to log feedback)
- No real-time adaptation
- Lower resolution — reflecting on vibes rather than full trajectories

---

### Alternative D: Hybrid (Recommended)

Combine the best of A and C:

```
┌────────────────────────────────────────────────────────────────┐
│ Layer 0: Skills (UNCHANGED)                                    │
│   skills/tour-planner-v2.md, options-pnl.md, news-summarizer.md│
│                                                                │
│ Layer 1: Capture (lightweight, per-execution)                  │
│   Auto-logs: inputs, outputs, duration, errors                 │
│   Manual: add 1-line feedback ("good" / "missed X")            │
│                                                                │
│ Layer 2: Reflect (on-demand or scheduled)                      │
│   Analyzes trajectories → identifies patterns                  │
│   Generates structured reflections                             │
│                                                                │
│ Layer 3: Generalize (cross-skill)                              │
│   Extracts shared improvements → shared/policies/              │
│   Identifies skill-specific improvements                       │
│                                                                │
│ Layer 4: Validate (before deployment)                          │
│   Runs improvement against test cases / benchmarks             │
│   Compares output quality before vs. after                     │
│                                                                │
│ Layer 5: Deploy (human-approved)                               │
│   Applies changes to skill SOPs or src/ code                   │
│   Versions the improvement (improvement log)                   │
└────────────────────────────────────────────────────────────────┘
```

**Key design decisions:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Capture trigger | Claude Code hook (post-skill) | Automatic, no manual step |
| Feedback format | JSONL append-only log | Simple, grep-able, git-friendly |
| Reflection trigger | On-demand (`/improve`) or after N executions | Control when reflection happens |
| Improvement format | Git-style diffs to skill SOPs | Easy to review, approve, reject |
| Cross-skill sharing | `shared/policies/*.md` files | Skills can optionally `#include` them |
| Validation | Re-run skill on past inputs, compare outputs | Regression detection |
| Deployment | Human reviews diff, applies manually or via script | Safety gate |

---

## Recommended Implementation Plan

### Phase 1: Trajectory Capture (1-2 hours)

Add minimal infrastructure to start collecting data:

```
agent-personal/
├── memory/
│   └── trajectories/
│       └── {skill-name}/{YYYY-MM-DD-HHMMSS}.jsonl
```

**Trajectory schema:**
```json
{
  "skill": "tour-planner-v2",
  "timestamp": "2026-07-27T10:30:00",
  "inputs": {"trip_slug": "2026-08-vienna-prague"},
  "outputs": ["v2-trip-itinerary-final.md"],
  "duration_sec": 180,
  "errors": [],
  "feedback": null
}
```

A simple `capture.py` that runs after each skill (or hooked into Claude Code settings as a post-execution hook).

### Phase 2: Feedback & Reflection (2-3 hours)

Add a feedback mechanism and a reflection agent:

- `memory/feedback.jsonl` — append quick notes: `{"skill": "options-pnl", "date": "2026-07-27", "note": "missed AMZN assignment from tasty", "type": "bug"}`
- `src/self_improvement/reflector.py` — reads trajectories + feedback, outputs structured reflections:
  - What went well (keep)
  - What went wrong (fix)
  - What's missing (add)
  - What's repeated across skills (generalize)

### Phase 3: Improvement Proposal (2-3 hours)

- `src/self_improvement/proposer.py` — takes reflections, generates concrete improvement candidates as diffs to skill SOPs or code
- Each improvement gets an ID, rationale, affected files, and confidence score
- Stored in `memory/improvements/{id}.md`

### Phase 4: Validation (3-4 hours)

- `src/self_improvement/validator.py` — re-runs skill with past inputs using the proposed improvement, compares output quality
- For `options-pnl`: run against reference xlsx, check validation still passes
- For `tour-planner`: check output against layer-2 validation rules
- For `news-summarizer`: check structural completeness (all sections present, links valid)

### Phase 5: Shared Policies (ongoing)

- Extract recurring improvements into `shared/policies/`:
  - `shared/policies/output-quality.md` — cross-skill output standards
  - `shared/policies/error-handling.md` — how all skills should handle failures
  - `shared/policies/data-validation.md` — input validation patterns
- Skills can reference these (e.g., "See also: shared/policies/output-quality.md") but don't have to — backward compatible.

---

## What This Gets You

| Capability | Without Self-Improvement | With Self-Improvement |
|-----------|-------------------------|----------------------|
| Skill iteration | Manual (rewrite SOPs) | Semi-automated (system proposes, you approve) |
| Cross-skill learning | Ad-hoc (notice patterns manually) | Systematic (generalizer extracts shared policies) |
| Regression detection | Manual testing | Automated validation against past inputs |
| Feedback memory | In your head | Persistent, searchable, actionable |
| Improvement history | Git log (if committed) | Structured log with rationale + validation results |

---

## What NOT to Build (Yet)

- **Vector DB / embeddings** — overkill for 3 skills. A simple JSONL + grep is sufficient until 50+ trajectories accumulate.
- **LangGraph / DSPy / Mem0** — heavy dependencies for a personal project. Start with plain Python + Claude API calls.
- **Automatic deployment** — always keep a human gate. Auto-deploy sounds great until it silently breaks a PnL report.
- **Real-time adaptation** — skills run infrequently (weekly/monthly). Batch reflection is fine.

---

## Suggested Starting Point

Start with **Phase 1 only** — just capture trajectories. Once 5-10 executions are logged with feedback, there's enough signal to build a meaningful reflector. The rest builds naturally from there.