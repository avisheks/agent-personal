# Super-Agent Self-Improvement: Research Proposal

**Date:** 2026-09-10
**Branch:** `super-agent`
**Status:** RFC
**Depends on:** [super-agent.md](../skills/super-agent.md), [skills-catalog.yaml](../skills/skills-catalog.yaml)

---

## 1. Problem Statement

The super-agent orchestrator ([super-agent.md](../skills/super-agent.md)) routes user questions to skills, decomposes multi-skill requests, and manages approval workflows. Its effectiveness depends on the quality of its instructions: routing accuracy, plan decomposition quality, turn efficiency, and error recovery.

Today, improving the super-agent requires manual prompt editing based on intuition. There is no systematic way to:
- Capture what went well or poorly in each session
- Identify recurring failure patterns (wrong skill routed, unnecessary turns, poor decomposition)
- Propose and validate targeted improvements
- Measure whether changes actually helped

**Goal:** After every conversation session, systematically improve `super-agent.md` so that it becomes more accurate, efficient, and requires fewer turns over time.

---

## 2. Literature Survey

The academic landscape for prompt and agent self-improvement has matured rapidly since 2022. The approaches fall into five families, each with distinct trade-offs for our use case.

### 2.1 Automatic Prompt Engineering

**APE — Large Language Models Are Human-Level Prompt Engineers**
Zhou et al., 2022. [[arXiv:2211.01910](https://arxiv.org/abs/2211.01910)]

APE treats instructions as programs and uses an LLM to generate candidate prompts, then evaluates each candidate on a held-out set. Automatically generated instructions matched or outperformed human-written ones on 19 of 24 NLP tasks. Key insight: an LLM can propose better prompts than a human, given a clear evaluation signal.

**Relevance:** Foundational — shows that prompt optimization is tractable. However, APE targets single-turn classification prompts, not multi-step orchestrator SOPs. Our super-agent.md is ~200 lines of structured instructions, not a one-liner.

**OPRO — Large Language Models as Optimizers**
Yang et al. (Google DeepMind), 2023. [[arXiv:2309.03409](https://arxiv.org/abs/2309.03409)]

OPRO iteratively generates candidate solutions from a prompt containing prior attempts and their scores, achieving up to 8% improvement on GSM8K and 50% on Big-Bench Hard. The optimization loop is simple: generate → evaluate → feed scores back → generate again.

**Relevance:** High. OPRO's "meta-prompt" pattern (show the optimizer previous attempts + scores) maps directly to showing an LLM previous super-agent sessions + quality metrics. The challenge is defining what "score" means for an orchestrator.

### 2.2 Evolutionary Prompt Optimization

**EvoPrompt — Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers**
Guo et al., 2023. [[arXiv:2309.08532](https://arxiv.org/abs/2309.08532)]

Combines evolutionary algorithms (genetic crossover, mutation) with LLM-based generation to evolve prompt populations. Achieves up to 25% improvement on Big-Bench Hard. Maintains a population of prompt variants and selects the fittest.

**Relevance:** Moderate. Population-based approaches work well when you can run hundreds of evaluations cheaply. Our setting has expensive evaluation (each "eval" is a full multi-turn session), making large populations impractical. But the mutation operators (targeted edits to specific sections) are useful.

**PromptBreeder — Self-Referential Self-Improvement Via Prompt Evolution**
Fernando et al. (DeepMind), 2023. [[arXiv:2309.16797](https://arxiv.org/abs/2309.16797)]

PromptBreeder evolves both task-prompts and the mutation-prompts that generate new task-prompts — a self-referential loop. Outperforms Chain-of-Thought on arithmetic and commonsense reasoning.

**Relevance:** The self-referential idea is powerful — the improvement process itself can improve. But the approach requires a population and many generations, which is expensive for our long-form orchestrator setting.

### 2.3 Verbal Reinforcement and Reflection

**Reflexion — Language Agents with Verbal Reinforcement Learning**
Shinn et al. (Princeton), 2023. [[arXiv:2303.11366](https://arxiv.org/abs/2303.11366)]

Agents verbally reflect on task feedback and store reflections in memory to improve future decisions. Achieved 91% pass@1 on HumanEval (vs. GPT-4's 80% at the time). No weight updates — the "learning" is stored as natural-language lessons in a memory buffer.

**Relevance:** Very high. This is the closest match to our setting. The super-agent can reflect on each session, generate lessons ("I routed 'write something about the project' to doc-writer when it should have been TPM"), and store them. The key question is where to store them: in the SOP itself, or in a separate memory file.

**Self-Refine — Iterative Refinement with Self-Feedback**
Madaan et al., 2023. [[arXiv:2303.17651](https://arxiv.org/abs/2303.17651)]

A single LLM generates output, critiques it, and refines it — achieving ~20% improvement across seven tasks with no additional training. The generate→critique→refine loop runs at inference time.

**Relevance:** Moderate. Self-Refine operates within a single session (refine the current output). We need cross-session improvement (make the next session better). But the critique mechanism is useful as a building block.

### 2.4 Gradient-Inspired Text Optimization

**TextGrad — Automatic "Differentiation" via Text**
Yuksekgonul et al. (Stanford), 2024. [[arXiv:2406.07496](https://arxiv.org/abs/2406.07496)]

Treats LLM outputs as variables in a computation graph and uses textual feedback as "gradients" to update prompts. Improved GPT-4o accuracy from 51% to 55% on question-answering, and achieved 20% relative gains on coding tasks.

**Relevance:** High conceptually. The idea of treating each section of super-agent.md as an optimizable variable, and session feedback as a gradient signal, maps well. The framework is designed for compound AI systems — exactly what we have.

**Trace — Generative Optimization with Rich Feedback, Execution Traces, and LLMs**
Cheng et al. (Microsoft), 2024. [[arXiv:2406.16218](https://arxiv.org/abs/2406.16218)]

Extends the gradient analogy by using execution traces (the full log of what happened during a run) as the optimization signal. Proposes OptoPrime, an LLM-based optimizer that reads traces and proposes parameter updates.

**Relevance:** High. Our session logs are execution traces. An optimizer that reads the session log and proposes edits to super-agent.md is exactly the Trace/OptoPrime pattern.

### 2.5 Meta-Agent Search (Agent Architecture Optimization)

**ADAS — Automated Design of Agentic Systems**
Hu et al. (UBC), 2024. [[arXiv:2408.08435](https://arxiv.org/abs/2408.08435)]

A meta-agent discovers novel agent designs by programming improved agents in code. Because it searches in the space of code (Turing-complete), it can theoretically discover any possible agent architecture. Discovered agents outperform hand-designed ones across coding, science, and math domains.

**Relevance:** Aspirational. ADAS searches over agent architectures (prompts + tools + control flow), not just prompt text. Full ADAS is overkill for improving a single orchestrator SOP, but the principle — that the improvement process should search broadly, not just tweak wording — is important. It suggests that the most impactful improvements may be structural (adding a new section to the SOP, changing the plan format) rather than textual (rewording a sentence).

### 2.6 Multi-Stage Pipeline Optimization

**MIPRO — Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs**
Opsahl-Ong et al. (Stanford/DSPy team), 2024. [[arXiv:2406.11695](https://arxiv.org/abs/2406.11695)]

Optimizes prompts across multi-stage pipelines (like our plan→approve→execute flow) by treating each stage's prompt as a modular component. Achieves up to 13% accuracy improvement using the DSPy framework.

**Relevance:** High. Our super-agent has multiple stages (routing, decomposition, plan presentation, execution). MIPRO's insight is that optimizing each stage independently is suboptimal — you need to optimize the pipeline end-to-end. This suggests that improving the routing section might require corresponding changes in the execution section.

**FireAct — Toward Language Agent Fine-tuning**
Chen et al. (Princeton), 2023. [[arXiv:2310.05915](https://arxiv.org/abs/2310.05915)]

Shows that fine-tuning LMs on agent trajectories yields consistent improvements, with just 500 GPT-4 trajectories boosting Llama2-7B by 77% on HotpotQA. Diverse training data (from multiple tasks and prompting methods) further improves agents.

**Relevance:** Lower for our setting (we're not fine-tuning weights), but the insight about trajectory diversity is important: our improvement process should draw from diverse session types, not just the most recent failure.

### 2.7 Summary: What the Literature Tells Us

| Principle | Source | Implication for Us |
|-----------|--------|--------------------|
| LLMs can optimize prompts better than humans when given evaluation signal | APE, OPRO | Use an LLM to propose SOP edits, don't just edit manually |
| Verbal reflection stored in memory improves future performance without weight updates | Reflexion | Store session lessons and feed them into the improvement process |
| Execution traces are the richest optimization signal | Trace, TextGrad | Our session logs are the key input — not just outcomes, but the full trace of decisions |
| Multi-stage pipelines need end-to-end optimization | MIPRO, DSPy | Improving routing may require coordinated changes to execution instructions |
| Structural changes (new sections, new control flow) can matter more than textual tweaks | ADAS | The improvement process should be able to propose adding/removing sections, not just rewording |
| Population-based approaches are expensive for long-form evaluation | EvoPrompt, PromptBreeder | We can't run 50 variants per cycle — need low-shot optimization |
| Diverse trajectories improve generalization | FireAct | Draw from varied session types, not just the latest failure |

---

## 3. Proposed Options

### Option A: Reflexion-Style Session Lessons (Append-and-Consolidate)

After each session, the agent reflects on what went well and poorly, generates structured "lessons," and appends them to a lessons file. Periodically, lessons are consolidated into targeted edits to `super-agent.md`.

**Mechanism:**

```
Session ends
    ↓
Agent reads session log + user's implicit feedback (plan edits, mid-session escalations, errors)
    ↓
Agent generates 1-3 structured lessons:
  - LESSON: "When user says 'write something about X', always clarify doc-writer vs. tpm before planning"
  - EVIDENCE: "Session 2026-09-10: routed to doc-writer, user edited plan to tpm"
  - SECTION: "Step 1: Understand the Question" (which section of super-agent.md to improve)
    ↓
Appends to .local/data/super-agent/lessons.md
    ↓
Every N sessions (e.g., 5), run consolidation:
  - Read all lessons
  - Group by section of super-agent.md
  - Generate targeted edits
  - Present diff to user for approval
  - Apply approved edits
  - Archive consumed lessons
```

**Quality signals (extracted automatically from session logs):**

| Signal | What It Means | Where It Comes From |
|--------|-------------|---------------------|
| Plan edit rate | User changed the plan → routing or decomposition was wrong | User responded "edit" instead of "yes" |
| Mid-session escalation count | Unanticipated skill needed → decomposition was incomplete | "Mid-Session Approvals" section in session log |
| Turns to first execution | More turns = more clarification needed → ambiguity handling is weak | Count turns before "Step 1 complete" |
| Skill invocation errors | Skill file not found, config missing → prerequisites check failed | "Execution Log" section in session log |
| Session duration (steps) | More steps than expected → over-decomposition | Step count vs. question complexity |

**Implementation:**

| Artifact | What | Lines |
|----------|------|-------|
| Post-session reflection prompt (in `super-agent.md`) | Instructions for end-of-session reflection | ~30 |
| `.local/data/super-agent/lessons.md` | Accumulated lessons | Grows, consolidated periodically |
| Consolidation protocol (in `super-agent.md`) | How to apply lessons to the SOP | ~40 |

**Pros:**
- Lowest effort — no code, no frameworks, just prompt additions to `super-agent.md`
- Grounded in Reflexion (proven effective — 91% on HumanEval)
- Human-readable lessons file — easy to audit and override
- Gradual improvement — each consolidation is a small, reviewable diff
- Works with any LLM runtime

**Cons:**
- Lessons can accumulate noise — not every session has a real lesson
- Consolidation quality depends on the LLM correctly mapping lessons to SOP sections
- No quantitative evaluation — improvements are judged qualitatively
- Risk of "lesson drift" — over time, lessons may push the SOP in contradictory directions if not carefully curated
- Manual trigger for consolidation (every N sessions) — easy to forget

---

### Option B: OPRO-Style Metric-Driven Optimization with Test Suite

Define quantitative metrics, build a test suite of representative queries with expected plans, and run an optimization loop that proposes SOP variants and evaluates them against the test suite.

**Mechanism:**

```
Build test suite (one-time):
  - 15-20 representative queries spanning single-skill, multi-skill, ambiguous, escalation
  - Each query has an expected plan (skill IDs, commands, sequence)
  - Each query has quality criteria (max turns, correct routing, no unnecessary escalation)
    ↓
After each session, add the session as a new test case if it reveals a new pattern
    ↓
Optimization cycle (triggered manually or every 10 sessions):
  1. Run current super-agent.md against the full test suite (simulated, not live)
  2. Score: routing accuracy, plan match rate, turns to execution
  3. Feed scores + failing test cases to optimizer LLM (OPRO-style meta-prompt)
  4. Optimizer proposes 2-3 candidate edits to super-agent.md
  5. Re-run test suite with each candidate
  6. Present best-scoring candidate to user as a diff
  7. User approves → apply edit, archive test results
```

**Test suite format** (`.local/data/super-agent/test-suite.yaml`):

```yaml
tests:
  - id: t001
    query: "What's the status of campaign-intent?"
    expected:
      skills: ["coworker-tpm"]
      commands: ["/status campaign-intent"]
      max_turns: 2
    tags: ["single-skill", "direct"]

  - id: t002
    query: "What's the project status and help me prep for my interview"
    expected:
      skills: ["coworker-tpm", "coworker-interviewer"]
      commands: ["/status", "/prep"]
      max_turns: 3
    tags: ["multi-skill", "decomposition"]

  - id: t003
    query: "Help me write something about the project"
    expected:
      clarification_needed: true
      candidate_skills: ["coworker-doc-writer", "coworker-tpm"]
    tags: ["ambiguous"]
```

**Metrics:**

| Metric | Definition | Target |
|--------|-----------|--------|
| Routing accuracy | % of test cases where correct skill(s) are selected | >= 95% |
| Plan match rate | % of test cases where the plan matches expected commands | >= 90% |
| Turns to execution | Average turns before first step executes | <= 2.0 |
| False escalation rate | % of sessions with unnecessary mid-session escalations | <= 5% |
| Clarification precision | % of ambiguous queries that correctly trigger clarification | >= 90% |

**Implementation:**

| Artifact | What | Lines |
|----------|------|-------|
| `.local/data/super-agent/test-suite.yaml` | Test cases with expected plans | ~200 |
| `src/super_agent_eval.py` | Test runner + scoring + OPRO meta-prompt | ~300 |
| `.local/data/super-agent/eval-history/` | Historical scores per optimization cycle | Grows |
| Optimization protocol (in proposals or a separate SOP) | How to run the optimization cycle | ~50 |

**Pros:**
- Quantitative — improvements are measured, not guessed
- Grounded in OPRO (up to 50% improvement on Big-Bench Hard) and MIPRO (13% on multi-stage)
- Test suite prevents regressions — a change that fixes one case can't break another unnoticed
- The test suite itself is a valuable artifact — documents expected behavior
- Optimization is repeatable and auditable

**Cons:**
- Highest setup cost — building the initial test suite + eval script is ~4-6 hours
- Simulated evaluation ≠ real sessions — a test case runs the plan step only, not full execution
- Test suite maintenance — as skills evolve, expected plans change
- Requires Python code (eval script) — adds a runtime dependency
- Risk of overfitting to the test suite — SOP gets great at the 20 test cases but doesn't generalize

---

### Option C: Hybrid — Reflexion Lessons + Lightweight Eval (Recommended)

Combine Option A's low-cost session reflection with a small, manually curated eval set for regression checking. No optimization code — the eval is run by the agent itself as part of the consolidation protocol.

**Mechanism:**

```
After each session:
  ↓
  Agent reflects → appends lessons to lessons.md (same as Option A)
  Agent extracts the session as a test case → appends to golden-cases.md (lightweight)
    ↓

Every 5 sessions (or on-demand via "/improve"):
  ↓
  1. Read all accumulated lessons, grouped by super-agent.md section
  2. Read golden-cases.md (the regression set)
  3. Propose specific edits to super-agent.md as a diff
  4. For each golden case, mentally trace whether the proposed edit would
     change the routing/plan — flag any regressions
  5. Present to user:
     - Proposed diff
     - Lessons consumed
     - Regression check results (pass/fail per golden case)
     - Confidence level (high/medium/low)
  6. User approves → apply diff, archive consumed lessons
  7. Agent updates golden-cases.md if the approved change redefines expected behavior
```

**Session reflection prompt (added to super-agent.md):**

```
## End-of-Session Reflection

After the user's last message (or when the session naturally concludes):

1. Re-read today's session log.
2. For each plan step, assess:
   - Was the skill routing correct? (Did the user edit the plan?)
   - Was the command appropriate? (Did the user override it?)
   - Were there unnecessary turns? (Clarification that could have been avoided?)
   - Were there mid-session escalations? (Skills that should have been in the original plan?)
3. Generate 0-3 lessons. Each lesson has:
   - LESSON: One-sentence improvement statement
   - EVIDENCE: What happened in this session (with session date)
   - SECTION: Which section of super-agent.md this affects
   - SEVERITY: high (wrong skill) / medium (extra turn) / low (minor UX)
4. If lessons exist, append to .local/data/super-agent/lessons.md
5. If this session revealed a novel routing pattern (not already in golden-cases.md),
   append it as a new golden case.
6. If no lessons, note: "Session {date}: clean — no improvements identified."
```

**Golden cases format** (`.local/data/super-agent/golden-cases.md`):

```markdown
# Golden Cases — Regression Set

## G001: Single-skill direct routing
**Query:** "What's the status of campaign-intent?"
**Expected:** coworker-tpm → /status campaign-intent
**Source:** Session 2026-09-10

## G002: Multi-skill decomposition
**Query:** "Project status and interview prep for Friday"
**Expected:** coworker-tpm → /status, then coworker-interviewer → /prep
**Source:** Session 2026-09-11

## G003: Ambiguous — requires clarification
**Query:** "Help me write something about the project"
**Expected:** Clarify: doc-writer vs. tpm
**Source:** Session 2026-09-12
```

**Consolidation protocol ("/improve" command):**

The agent reads `lessons.md` + `golden-cases.md` + current `super-agent.md`, then:

1. Groups lessons by target section
2. Proposes a minimal diff (fewest changes that address the highest-severity lessons)
3. Traces each golden case through the proposed changes — flags if any routing would change
4. Presents the diff + regression results to the user
5. On approval, applies the diff and archives consumed lessons
6. Logs the improvement cycle to `.local/data/super-agent/improvement-log.md`

**Implementation:**

| Artifact | What | Lines |
|----------|------|-------|
| End-of-session reflection (added to `super-agent.md`) | Reflection protocol | ~30 |
| Consolidation protocol (added to `super-agent.md`) | `/improve` command | ~50 |
| `.local/data/super-agent/lessons.md` | Accumulated lessons | Grows, archived on consolidation |
| `.local/data/super-agent/golden-cases.md` | Regression set | Grows slowly (~1-2 cases per week) |
| `.local/data/super-agent/improvement-log.md` | History of applied improvements | Append-only |

**Pros:**
- Low setup cost — just prompt additions, no code (1-2 hours to implement)
- Quantitative regression checking without a test runner — the agent traces golden cases mentally
- Lessons accumulate naturally from real sessions (Reflexion pattern)
- Golden cases grow organically — every novel failure becomes a regression guard
- The `/improve` command gives user control over when optimization happens
- All artifacts are human-readable markdown — easy to audit, edit, override
- No runtime dependency — works anywhere the super-agent works
- Improvement history is preserved in `improvement-log.md` — can see what changed and why
- Addresses the literature's key insight: use execution traces (session logs) as the optimization signal (Trace, TextGrad), store verbal reflections (Reflexion), and check for regressions (OPRO test suite) — but without the engineering overhead

**Cons:**
- Regression "tracing" is mental simulation by the LLM, not actual execution — it can miss subtle interactions
- No quantitative scoring (unlike Option B) — improvements are assessed qualitatively with regression guards
- Golden cases file must be maintained — stale cases can block valid improvements
- Consolidation quality still depends on the LLM — a poorly generated diff could degrade the SOP
- The "every 5 sessions" cadence is a heuristic — may be too frequent (not enough signal) or too infrequent (lessons go stale)

---

## 4. Comparison Matrix

| Dimension | A: Reflexion Only | B: OPRO + Test Suite | C: Hybrid (Recommended) |
|-----------|-------------------|---------------------|------------------------|
| **Setup cost** | 1 hour | 4-6 hours | 1-2 hours |
| **Ongoing cost per session** | ~2 min (reflection) | ~2 min (reflection) + periodic eval runs | ~3 min (reflection + golden case check) |
| **Regression safety** | None — lessons can conflict | High — full test suite | Medium — golden cases as lightweight guards |
| **Improvement signal** | Qualitative (lessons) | Quantitative (scores) | Qualitative + regression guards |
| **Code required** | None | ~300 lines Python | None |
| **Runtime coupling** | None | Python + LLM API | None |
| **Audit trail** | Lessons file | Eval history + scores | Lessons + golden cases + improvement log |
| **Handles structural changes** | Partially (ADAS insight) | No (only textual changes scored) | Yes (diff can add/remove sections) |
| **Overfitting risk** | Low (no fixed eval set) | Medium (can overfit to test suite) | Low (golden cases grow organically) |
| **Literature grounding** | Reflexion | OPRO, MIPRO, DSPy | Reflexion + Trace + lightweight OPRO |

---

## 5. Recommendation: Option C (Hybrid)

Option C provides the best balance of rigor and practicality for our setting:

1. **Our evaluation is expensive.** Each "test" is a multi-turn conversation, not a single-turn classification. Option B's test suite can only simulate the planning step, not full execution. Option C's golden cases serve the same regression-prevention purpose without the false precision of simulated scores.

2. **Real sessions are the richest signal.** The literature consistently shows that execution traces (Trace, TextGrad) and verbal reflections (Reflexion) are more informative than synthetic benchmarks. Option C feeds directly from real sessions, while Option B's test suite is static and synthetic.

3. **Structural improvements matter.** ADAS shows that the highest-impact changes are often structural (adding a routing heuristic, changing the plan format) rather than textual (rewording a sentence). Option C's diff-based consolidation can propose structural changes; Option B's scoring framework only measures whether fixed test cases pass.

4. **Zero code keeps the system portable.** This skill collection works across runtimes. Adding a Python eval script (Option B) couples it to a specific invocation pattern. Option C stays pure markdown — the agent itself does the evaluation.

5. **The improvement cadence matches our usage.** With ~5 sessions per week, we accumulate enough signal for a meaningful consolidation every 1-2 weeks. Option B's infrastructure is designed for rapid iteration (50+ eval runs per cycle) that we don't need.

---

## 6. Implementation Plan (if approved)

| Step | What | Effort |
|------|------|--------|
| 1 | Add "End-of-Session Reflection" section to `super-agent.md` | 30 min |
| 2 | Add `/improve` consolidation protocol to `super-agent.md` | 45 min |
| 3 | Create initial `golden-cases.md` with 5-8 seed cases covering the core patterns (single-skill, multi-skill, ambiguous, escalation) | 30 min |
| 4 | Create empty `lessons.md` and `improvement-log.md` templates | 5 min |
| 5 | Run 3-5 test sessions and trigger `/improve` to validate the loop | 1-2 hours |
| 6 | Iterate on reflection prompt quality based on test session results | 30 min |

**Total estimated effort:** 3-4 hours.

---

## 7. References

| # | Paper | Authors | Year | Key Contribution |
|---|-------|---------|------|-----------------|
| 1 | [Large Language Models Are Human-Level Prompt Engineers (APE)](https://arxiv.org/abs/2211.01910) | Zhou et al. | 2022 | LLMs auto-generate prompts matching human quality on 19/24 tasks |
| 2 | [Large Language Models as Optimizers (OPRO)](https://arxiv.org/abs/2309.03409) | Yang et al. (Google DeepMind) | 2023 | Iterative prompt optimization using prior attempts + scores as meta-prompt |
| 3 | [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) | Shinn et al. (Princeton) | 2023 | Agents store verbal reflections in memory to improve future decisions |
| 4 | [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) | Madaan et al. | 2023 | Single-LLM generate→critique→refine loop, ~20% improvement |
| 5 | [EvoPrompt: Connecting LLMs with Evolutionary Algorithms](https://arxiv.org/abs/2309.08532) | Guo et al. | 2023 | Evolutionary prompt optimization, up to 25% on Big-Bench Hard |
| 6 | [Promptbreeder: Self-Referential Self-Improvement](https://arxiv.org/abs/2309.16797) | Fernando et al. (DeepMind) | 2023 | Evolves both task-prompts and mutation-prompts in a self-referential loop |
| 7 | [TextGrad: Automatic "Differentiation" via Text](https://arxiv.org/abs/2406.07496) | Yuksekgonul et al. (Stanford) | 2024 | Textual feedback as gradients for compound AI system optimization |
| 8 | [Trace is the Next AutoDiff](https://arxiv.org/abs/2406.16218) | Cheng et al. (Microsoft) | 2024 | Execution traces as optimization signals, OptoPrime LLM-based optimizer |
| 9 | [Optimizing Multi-Stage Language Model Programs (MIPRO/DSPy)](https://arxiv.org/abs/2406.11695) | Opsahl-Ong et al. (Stanford) | 2024 | End-to-end optimization of multi-stage LM pipelines, up to 13% accuracy gain |
| 10 | [DSPy: Compiling Declarative LM Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714) | Khattab et al. (Stanford) | 2023 | Programming model for LM pipelines with automatic prompt optimization |
| 11 | [Automated Design of Agentic Systems (ADAS)](https://arxiv.org/abs/2408.08435) | Hu et al. (UBC) | 2024 | Meta-agent discovers novel agent architectures in code, outperforms hand-designed agents |
| 12 | [FireAct: Toward Language Agent Fine-tuning](https://arxiv.org/abs/2310.05915) | Chen et al. (Princeton) | 2023 | Fine-tuning on diverse agent trajectories yields consistent improvements |
