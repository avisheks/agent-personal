# Super-Agent Evaluation: Research Proposal

**Date:** 2026-09-10
**Branch:** `super-agent`
**Status:** RFC
**Depends on:** [super-agent.md](../skills/super-agent.md), [skills-catalog.yaml](../skills/skills-catalog.yaml)
**Companion:** [super-agent-self-improvement.md](super-agent-self-improvement.md) (improvement follows evaluation)

---

## 1. Problem Statement

Before we can improve the super-agent, we need to measure how well it performs. Today, the super-agent produces session logs (`.local/logs/super-agent/{date}-session.md`) that record the plan, approved skills, and execution status. But these logs capture *what happened* — not *how well it happened*.

We need a systematic evaluation framework that, after every conversation session (single-turn or multi-turn), can:

1. **Score** the session across multiple quality dimensions
2. **Identify gaps** — specific failure modes and their root causes
3. **Track trends** — whether the super-agent is getting better or worse over time
4. **Prioritize** — which gaps matter most and should be fixed first

This proposal addresses the evaluation and gap-identification step. The companion proposal ([super-agent-self-improvement.md](super-agent-self-improvement.md)) addresses what to do with the evaluation results.

---

## 2. Literature Survey

Agent evaluation is a rapidly evolving field. The literature reveals a fundamental tension: **outcome-only evaluation misses how the agent got there, while process-level evaluation is expensive and hard to scale.** The papers below span both approaches, plus meta-critiques of current evaluation practices.

### 2.1 Outcome-Level Evaluation (Did the Agent Succeed?)

**AgentBench — Evaluating LLMs as Agents**
Liu et al. (Tsinghua/OSU), 2023. [[arXiv:2308.03688](https://arxiv.org/abs/2308.03688)] (ICLR 2024)

Evaluates LLMs across 8 diverse environments (OS, database, web, games, etc.) using task completion as the primary metric. Key finding: "poor long-term reasoning, decision-making, and instruction following abilities are the main obstacles" for LLM agents. Open-source models lag significantly behind commercial ones.

**Relevance:** AgentBench's multi-environment approach maps to our multi-skill setting. But it evaluates single-task completion, not orchestration quality. A super-agent that routes to the correct skill and completes the task is a richer evaluation target than any single environment.

**tau-bench — A Benchmark for Tool-Agent-User Interaction**
Yao et al. (Princeton), 2024. [[arXiv:2406.12045](https://arxiv.org/abs/2406.12045)]

Evaluates agents on dynamic multi-turn conversations with simulated users in real-world domains (retail, airline). Uses database state comparison as the evaluation method — checking whether the agent's actions produced the correct final state. Even GPT-4o succeeds on less than 50% of tasks.

**Relevance:** Very high. tau-bench evaluates exactly what we need: multi-turn conversations where the agent must follow rules, use tools correctly, and satisfy user intent. Their database-state-comparison approach maps to our "did the session log reflect the correct plan and execution?" The <50% success rate of frontier models on rule-following is a sobering baseline.

**MMAU — A Holistic Benchmark of Agent Capabilities Across Diverse Domains**
Yin et al., 2024. [[arXiv:2407.18961](https://arxiv.org/abs/2407.18961)]

Benchmarks 5 core agent competencies across 3,000+ prompts: understanding, reasoning, planning, problem-solving, and self-correction. Uses offline tasks that don't require complex environment setup.

**Relevance:** The 5-competency decomposition is useful for our evaluation rubric. A super-agent failure in "planning" (wrong decomposition) is qualitatively different from a failure in "understanding" (misinterpreted the question) — and needs different fixes.

### 2.2 Process-Level Evaluation (How Did the Agent Get There?)

**Let's Verify Step by Step**
Lightman et al. (OpenAI), 2023. [[arXiv:2305.20050](https://arxiv.org/abs/2305.20050)]

Compares outcome supervision (evaluating final answers) vs. process supervision (evaluating intermediate steps) for mathematical reasoning. Process supervision significantly outperforms outcome supervision, achieving 78% on MATH dataset. Released PRM800K — 800,000 step-level human labels.

**Relevance:** Foundational. This paper establishes that **evaluating intermediate steps catches errors that outcome evaluation misses**. For our super-agent, evaluating only "did the final skill produce the right output?" misses routing errors, unnecessary turns, and poor decomposition. We need process-level evaluation: was each step in the plan correct?

**Agent-as-a-Judge: Evaluate Agents with Agents**
Zhuge et al. (Meta/KAUST), 2024. [[arXiv:2410.10934](https://arxiv.org/abs/2410.10934)]

Introduces a framework where AI agents evaluate other agents by examining the full execution trajectory, not just the final output. Tested on DevAI (55 development tasks, 365 hierarchical requirements). Agent-as-a-Judge "dramatically outperforms LLM-as-a-Judge" because it provides intermediate feedback throughout execution.

**Relevance:** Very high. This is the closest analog to our setting. The key insight: **evaluation must look at the trajectory (session log), not just the outcome (final output)**. An LLM judge reading only the final answer can't assess routing quality, turn efficiency, or escalation appropriateness. An agent-judge reading the full session log can.

**Autonomous Evaluation and Refinement of Digital Agents**
Pan et al. (UC Berkeley), 2024. [[arXiv:2404.06474](https://arxiv.org/abs/2404.06474)]

Builds automatic evaluator models that achieve 74-93% alignment with oracle metrics on web navigation and device control tasks. Uses evaluators for both scoring (post-hoc) and guidance (inference-time). Achieves 29% improvement on WebArena through evaluator-guided refinement.

**Relevance:** Demonstrates that LLM-based evaluators can be highly accurate for agent tasks and that evaluation + refinement is more powerful than evaluation alone. Their dual-use evaluator (scoring + guidance) is relevant to our combined evaluation + improvement pipeline.

### 2.3 LLM-as-Judge for Conversations

**Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena**
Zheng et al. (UC Berkeley/LMSYS), 2023. [[arXiv:2306.05685](https://arxiv.org/abs/2306.05685)]

Validates that strong LLMs (GPT-4) can evaluate chat assistants with >80% agreement with human judges — comparable to human-human agreement. Identifies biases: position bias (prefers first response), verbosity bias (prefers longer responses), and self-enhancement bias (prefers its own outputs).

**Relevance:** Establishes that LLM-as-judge is viable for conversational evaluation, which is our core setting. The bias catalog is critical — our evaluator must be designed to mitigate these. Particularly relevant: verbosity bias means an LLM judge might rate a 5-turn session higher than a 2-turn session even if the 2-turn session was more efficient.

**AgentEval — Assessing and Verifying Task Utility in LLM-Powered Applications**
Arabzadeh et al. (Microsoft), 2024. [[arXiv:2405.02178](https://arxiv.org/abs/2405.02178)]

Proposes automatic generation of evaluation criteria tailored to each application's purpose, rather than using generic metrics. The framework generates criteria, evaluates against them, and verifies results. Addresses the gap between benchmark performance and real-world utility.

**Relevance:** High. Our super-agent has a unique purpose (skill orchestration) that generic agent benchmarks don't cover. AgentEval's approach of auto-generating application-specific criteria is exactly what we need — but we can do it manually given our clear requirements.

### 2.4 Meta-Critique: What's Wrong with Current Evaluation

**AI Agents That Matter**
Kapoor et al. (Princeton), 2024. [[arXiv:2407.01502](https://arxiv.org/abs/2407.01502)]

A sharp critique of current agent benchmarking: "a narrow focus on accuracy without attention to other metrics" leads to unnecessarily complex systems. Proposes joint optimization of cost and accuracy, clearer separation of model vs. application developer needs, and robust holdout practices.

**Relevance:** Essential reading. Their central argument — that **accuracy alone is insufficient** and must be paired with cost, latency, and complexity metrics — directly applies. A super-agent that routes correctly but takes 6 turns is worse than one that routes correctly in 2 turns. Our evaluation must be multi-dimensional.

**Measuring AI Ability to Complete Long Software Tasks**
Kwa et al. (METR), 2025. [[arXiv:2503.14499](https://arxiv.org/abs/2503.14499)]

Introduces "50%-task-completion time horizon" as a metric — measuring how long humans spend on tasks that models complete at 50% success rate. Finds current frontier models operate at ~50-minute horizons.

**Relevance:** The time-horizon framing is useful. Our sessions vary in complexity — a single-skill routing is a "5-minute" task, a multi-skill decomposition with escalation is a "30-minute" task. Evaluation should be complexity-aware, not apply the same bar to trivial and complex sessions.

### 2.5 Summary: What the Literature Tells Us About Evaluation

| Principle | Source | Implication for Our Evaluator |
|-----------|--------|-----------------------------|
| Process supervision beats outcome supervision | Let's Verify Step by Step | Evaluate each step (routing, decomposition, execution), not just the final output |
| Agent-judge beats LLM-judge for trajectory evaluation | Agent-as-a-Judge | The evaluator must read the full session log, not just the final answer |
| LLM judges achieve >80% human agreement on conversations | MT-Bench | LLM-based evaluation is viable for our conversational setting |
| Accuracy alone is insufficient — must include cost and efficiency | AI Agents That Matter | Track turns, latency, skill count — not just "right answer" |
| Application-specific criteria outperform generic ones | AgentEval | Define evaluation dimensions specific to orchestration quality |
| Evaluation must be complexity-aware | METR | Score simple and complex sessions differently — a 1-skill routing shouldn't be graded like a 4-skill decomposition |
| LLM judges have biases (verbosity, position, self-enhancement) | MT-Bench | Design rubric to counter these — explicitly reward brevity and efficiency |
| Multi-turn rule-following is hard — even GPT-4o fails >50% | tau-bench | Set realistic expectations; focus on systematic gap identification, not perfection |

---

## 3. Evaluation Dimensions

Based on the literature, our evaluation framework should score sessions across these dimensions:

| Dimension | What It Measures | Grounded In |
|-----------|-----------------|-------------|
| **Routing Accuracy** | Did the agent select the correct skill(s) for the user's intent? | AgentBench, MMAU |
| **Decomposition Quality** | For multi-skill requests: were tasks correctly decomposed, ordered, and with right dependencies? | tau-bench, MMAU |
| **Turn Efficiency** | How many turns before first execution? Were any turns unnecessary? | AI Agents That Matter |
| **Plan Precision** | Was the correct command selected for each skill? Were inputs identified correctly? | Agent-as-a-Judge |
| **Escalation Appropriateness** | Were mid-session escalations warranted? Were any missed (should have escalated but didn't)? | tau-bench |
| **Ambiguity Handling** | When the query was ambiguous, did the agent clarify correctly vs. guess wrong? | MMAU |
| **Error Recovery** | When something went wrong (missing config, wrong skill), did the agent recover gracefully? | Autonomous Eval |
| **User Satisfaction Proxy** | Did the user accept the plan as-is, edit it, or reject it? Did they need to correct the agent? | MT-Bench, AgentEval |

---

## 4. Proposed Options

### Option A: LLM-as-Judge Post-Session Scorecard

After each session, an LLM judge reads the full session log and produces a structured scorecard using a fixed rubric.

**Mechanism:**

```
Session ends → session log exists at .local/data/super-agent/{date}-session.md
    ↓
Evaluator reads:
  - Session log (plan, approved skills, execution log, any errors)
  - The user's original question
  - Any plan edits or mid-session escalations
    ↓
Evaluator produces a scorecard:

## Session Evaluation: 2026-09-10
| Dimension | Score (1-5) | Evidence | Gap Identified |
|-----------|-------------|----------|----------------|
| Routing Accuracy | 5 | Correct: tpm for status, interviewer for prep | — |
| Decomposition | 4 | Correct order, but missed dependency: prep needs files in inp/ | GAP: Prerequisites check incomplete |
| Turn Efficiency | 3 | 3 turns to first execution; 1 unnecessary clarification | GAP: Could infer skill from "prep for interview" without asking |
| Plan Precision | 5 | /status campaign-intent, /prep both correct | — |
| Escalation | N/A | No escalation needed or occurred | — |
| Ambiguity Handling | N/A | Query was unambiguous | — |
| Error Recovery | N/A | No errors occurred | — |
| User Satisfaction | 4 | Plan accepted without edits, but user had to specify input files | GAP: Should have checked data_dir proactively |

**Overall: 4.2/5**
**Gaps identified: 2** (prerequisites check, unnecessary clarification)
**Complexity class: Medium** (2-skill decomposition)
    ↓
Appends scorecard to .local/data/super-agent/evaluations.md
```

**Rubric (embedded in the evaluator prompt):**

```
Scoring guide per dimension:
  5 = Perfect — no room for improvement
  4 = Good — minor issue that didn't affect outcome
  3 = Acceptable — noticeable inefficiency or small error, but task completed
  2 = Poor — significant error that required user correction
  1 = Failure — wrong skill, broken execution, or user had to abandon

Complexity classes (affects expectations):
  Simple = single skill, unambiguous query → expect score >= 4.5
  Medium = 2 skills, some parameter inference → expect score >= 3.5
  Complex = 3+ skills, ambiguity, dependencies → expect score >= 3.0
```

**Implementation:**

| Artifact | What |
|----------|------|
| Evaluator prompt (section in `super-agent.md` or separate `super-agent-eval.md`) | ~80 lines |
| `.local/data/super-agent/evaluations.md` | Append-only scorecard log |

**Pros:**
- Simple — one LLM call after each session produces a structured scorecard
- Grounded in MT-Bench (>80% human agreement for LLM-as-judge on conversations)
- Directly produces gap identification with evidence
- Scorecard format enables trend tracking over time
- No code — pure prompt-based

**Cons:**
- Single-pass evaluation — the judge sees the session once and scores it. No verification of its own judgments. Agent-as-a-Judge paper shows this underperforms trajectory-aware evaluation.
- Prone to LLM-judge biases (verbosity, leniency). An LLM evaluating its own session output has self-enhancement bias (MT-Bench finding).
- Scores are subjective 1-5 ratings — hard to compare across sessions with different complexity
- No ground truth — the evaluator doesn't know what the "right" plan was, only what happened
- Can't detect "unknown unknowns" — if the agent didn't know a skill existed, neither will the evaluator

---

### Option B: Dual-Judge with Ground-Truth Anchoring

Two-phase evaluation: first, reconstruct what the *ideal* session would have looked like (ground truth); second, compare the actual session against the ideal and score the delta.

**Mechanism:**

```
Session ends → session log exists
    ↓
Phase 1: Ideal Reconstruction (Judge A)
  Reads: user's original question + skills-catalog.yaml
  Does NOT read: the session log (to avoid anchoring bias)
  Produces: the ideal plan — which skills, which commands, what order, expected turns
    ↓
Phase 2: Delta Scoring (Judge B)
  Reads: ideal plan (from Phase 1) + actual session log
  Produces: dimension-by-dimension comparison

## Session Evaluation: 2026-09-10

### Ideal Plan (reconstructed independently)
| # | Skill | Command | Notes |
|---|-------|---------|-------|
| 1 | coworker-tpm | /status campaign-intent | Direct match |
| 2 | coworker-interviewer | /prep | Needs files in inp/ — should flag as prerequisite |

Expected turns to first execution: 2 (plan + approve)
Expected escalations: 0

### Actual vs. Ideal Comparison
| Dimension | Ideal | Actual | Score | Gap |
|-----------|-------|--------|-------|-----|
| Routing | tpm + interviewer | tpm + interviewer | 5 | — |
| Decomposition | 2 steps, interviewer depends on inp/ files | 2 steps, no prerequisite flagged | 4 | Missing prerequisite check |
| Turn Efficiency | 2 turns | 3 turns (extra clarification) | 3 | Unnecessary "which project?" when query named it |
| Commands | /status campaign-intent, /prep | /status campaign-intent, /prep | 5 | — |

**Delta score: 4.2/5**
**Root causes: 2**
  1. Prerequisites section doesn't check data_dir for input readiness → SECTION: Step 2 (Build Plan)
  2. Clarification triggered despite unambiguous query → SECTION: Step 1 (Understand the Question)
    ↓
Appends to evaluations.md
```

**Key difference from Option A:** The ideal plan is reconstructed *without seeing the actual session*, preventing the evaluator from being anchored by what happened. This counters the self-enhancement bias identified in MT-Bench.

**Implementation:**

| Artifact | What |
|----------|------|
| Ideal reconstruction prompt (Judge A) | ~40 lines |
| Delta scoring prompt (Judge B) | ~60 lines |
| Evaluation protocol (section in `super-agent.md`) | ~30 lines |
| `.local/data/super-agent/evaluations.md` | Append-only with ideal + delta |

**Pros:**
- Anchoring-free ideal reconstruction eliminates self-enhancement bias (MT-Bench's key finding)
- Delta scoring produces precise, actionable gaps tied to specific SOP sections
- Ground-truth anchoring means scores are calibrated: a "4" means "one deviation from ideal," not a subjective impression
- Directly maps gaps to SOP sections — feeds directly into the improvement pipeline
- Detects "unknown unknowns" — if Judge A identifies a skill the agent didn't consider, that's a gap

**Cons:**
- Two LLM calls per session (Judge A + Judge B) — doubles evaluation cost
- Ideal reconstruction is itself imperfect — Judge A may propose a different-but-equally-valid plan, creating false gaps
- Requires careful prompt engineering to prevent Judge A from being too rigid (there are often multiple valid plans)
- More complex to implement and maintain than Option A

---

### Option C: Process-Level Trace Evaluation with Gap Taxonomy (Recommended)

Evaluate the session at the **step level** (inspired by process reward models), classify each gap into a taxonomy of failure modes, and aggregate into a session scorecard. The evaluator reads the full execution trace and scores each decision point independently.

**Mechanism:**

```
Session ends → session log exists
    ↓
Step 1: Extract Decision Points from the session log
  Every session has a sequence of decision points:
  - D1: Question interpretation (what did the agent understand?)
  - D2: Skill selection (which skill(s) were chosen?)
  - D3: Command selection (which command per skill?)
  - D4: Dependency ordering (what sequence?)
  - D5: Prerequisite identification (what inputs/config needed?)
  - D6: Plan presentation (was the plan clear and complete?)
  - D7: Execution per step (did each step run correctly?)
  - D8: Escalation decisions (any mid-session skill additions?)
  - D9: Follow-up handling (how were post-plan questions handled?)
    ↓
Step 2: Score Each Decision Point
  For each decision point that occurred in this session:
  - PASS: Decision was correct and efficient
  - MINOR: Decision was acceptable but suboptimal (e.g., extra turn, verbose plan)
  - FAIL: Decision was wrong and required user correction or caused an error
  - SKIP: Decision point didn't occur in this session (e.g., no escalation needed)
    ↓
Step 3: Classify Each MINOR/FAIL into the Gap Taxonomy

  GAP TAXONOMY (8 failure modes):

  | Code | Gap Type | Description | Example |
  |------|----------|-------------|---------|
  | G1 | MISROUTE | Wrong skill selected | Routed to doc-writer when tpm was correct |
  | G2 | OVER-DECOMPOSE | Split into too many steps | Single-skill task split into 2 steps |
  | G3 | UNDER-DECOMPOSE | Missed a necessary skill | Multi-skill request handled by only 1 skill |
  | G4 | WRONG-COMMAND | Right skill, wrong command | Used /review-project when /status was asked |
  | G5 | MISSED-PREREQ | Failed to identify required inputs/config | Didn't flag missing inp/ files for interviewer |
  | G6 | UNNECESSARY-TURN | Extra clarification that could have been inferred | Asked "which project?" when query named it |
  | G7 | MISSED-ESCALATION | Needed a new skill mid-session but didn't ask | Used tpm for a question that needed doc-writer |
  | G8 | FALSE-ESCALATION | Asked to use a skill that wasn't needed | Proposed career skill when user just asked about project |

    ↓
Step 4: Produce the Session Evaluation

## Session Evaluation: 2026-09-10

**Query:** "What's the status of campaign-intent and help me prep for Friday's interview"
**Complexity:** Medium (2-skill decomposition)

### Decision Trace
| # | Decision Point | Verdict | Gap | Evidence |
|---|---------------|---------|-----|----------|
| D1 | Question interpretation | PASS | — | Correctly identified 2 intents: project status + interview prep |
| D2 | Skill selection | PASS | — | coworker-tpm + coworker-interviewer |
| D3 | Command selection | PASS | — | /status campaign-intent + /prep |
| D4 | Dependency ordering | PASS | — | tpm first (independent), interviewer second |
| D5 | Prerequisite identification | MINOR | G5 | Did not flag that /prep needs JD + resume in inp/ |
| D6 | Plan presentation | MINOR | G6 | Asked "which project?" despite "campaign-intent" in query |
| D7a | Execution: tpm /status | PASS | — | Completed successfully |
| D7b | Execution: interviewer /prep | PASS | — | Completed after user provided input files |
| D8 | Escalation | SKIP | — | No escalation needed |
| D9 | Follow-up | SKIP | — | No follow-up questions |

### Summary
| Metric | Value |
|--------|-------|
| Decision points evaluated | 8 |
| PASS | 6 |
| MINOR | 2 |
| FAIL | 0 |
| Score | 6/8 = 75% (adjusted: 87.5% with MINOR as half-credit) |
| Gaps | G5 (missed prereq), G6 (unnecessary turn) |
| Turns to first execution | 3 (ideal: 2) |
| Turn overhead | +1 |

### Gap Details
**G5: MISSED-PREREQ** — /prep requires JD, resume, and competencies in .local/data/interviewer/inp/. The plan should have listed these as prerequisites.
→ SOP section affected: "Step 2: Build the Execution Plan" — add: check data_dir contents for skills with required input files.

**G6: UNNECESSARY-TURN** — Query explicitly said "campaign-intent" but agent asked "which project?". The catalog has campaign-intent as a known project slug.
→ SOP section affected: "Step 1: Understand the Question" — add: when query contains a known project slug from the catalog, use it directly.
    ↓
Appends to .local/data/super-agent/evaluations.md
```

**Trend tracking** (aggregated across sessions):

```markdown
# Evaluation Trends — Last 10 Sessions

| Gap Code | Occurrences | Trend | Priority |
|----------|-------------|-------|----------|
| G6 | 4 | ↑ increasing | HIGH — most frequent, easiest to fix |
| G5 | 3 | → stable | MEDIUM — prereq checking needs improvement |
| G1 | 1 | ↓ decreasing | LOW — routing is generally accurate |
| G4 | 0 | — | — |
```

**Implementation:**

| Artifact | What |
|----------|------|
| Evaluation protocol + gap taxonomy (section in `super-agent.md`) | ~100 lines |
| `.local/data/super-agent/evaluations.md` | Append-only decision traces + gap details |
| `.local/data/super-agent/gap-trends.md` | Aggregated gap counts (updated each evaluation) |

**Pros:**
- Process-level evaluation catches intermediate errors that outcome-only evaluation misses (Let's Verify Step by Step)
- Typed gap taxonomy (G1-G8) enables structured trend tracking — you can see which failure mode is most common and prioritize fixes
- Each gap maps directly to an SOP section — feeds cleanly into the improvement pipeline
- Decision trace is exhaustive and auditable — a human can disagree with any specific verdict
- Complexity-aware — simple sessions have fewer decision points, complex ones have more. Scoring is proportional.
- Gap trends surface systemic issues (e.g., "G6 has occurred 4 times in 10 sessions — the clarification logic needs work")
- No code required — the evaluator is a prompt, the taxonomy is a reference table
- Counters verbosity bias by explicitly scoring turn efficiency as a decision point

**Cons:**
- More LLM tokens per evaluation than Option A (longer prompt, more structured output)
- Single-evaluator (no anchoring-free ideal like Option B) — still subject to self-enhancement bias, though the structured decision-point format mitigates this
- Gap taxonomy is fixed at 8 types — novel failure modes may not fit cleanly. (Mitigated by allowing a G0: "OTHER" category with free-text description)
- Requires the session log to be detailed enough to reconstruct decision points. If the session log is sparse, the evaluator has less to work with.
- Initial taxonomy may need calibration — the first 5-10 evaluations will reveal whether the 8 gap types cover real failure modes

---

## 5. Comparison Matrix

| Dimension | A: LLM-as-Judge Scorecard | B: Dual-Judge + Ground Truth | C: Process-Level Trace Eval (Recommended) |
|-----------|--------------------------|-----------------------------|-----------------------------------------|
| **Evaluation depth** | Outcome-level (holistic scores) | Outcome + ideal comparison | Process-level (per-decision-point) |
| **Bias resistance** | Low (single judge, self-enhancement) | High (anchoring-free ideal) | Medium (structured format mitigates bias) |
| **Gap identification** | Free-text (unstructured) | Delta-based (structured) | Taxonomy-based (G1-G8, highly structured) |
| **Trend tracking** | Difficult (subjective scores) | Moderate (delta counts) | Easy (gap codes aggregate naturally) |
| **Maps to SOP sections** | Loosely | Directly (delta → section) | Directly (gap → section) |
| **LLM cost per session** | 1 call | 2 calls | 1 call (longer) |
| **Implementation effort** | 1 hour | 2-3 hours | 1.5 hours |
| **Code required** | None | None | None |
| **Handles novel failures** | Yes (free-text) | Yes (ideal may differ) | Partially (G0: OTHER for novel types) |
| **Literature grounding** | MT-Bench, AgentEval | MT-Bench (bias), Agent-as-Judge | Let's Verify Step by Step, Agent-as-Judge, AI Agents That Matter |

---

## 6. Recommendation: Option C (Process-Level Trace Evaluation)

Option C is the right choice for three reasons:

### 1. Process supervision beats outcome supervision — the literature is clear.

Let's Verify Step by Step showed a decisive advantage for step-level evaluation over outcome-only evaluation in mathematical reasoning. Agent-as-a-Judge confirmed this for agent tasks: "dramatically outperforms LLM-as-a-Judge." Our super-agent has 9 distinct decision points per session. Evaluating each one independently catches errors that a holistic "4.2/5" score from Option A would miss.

### 2. A typed gap taxonomy enables structured improvement.

Option A produces free-text gaps ("the agent asked an unnecessary question"). Option C produces typed gaps (G6: UNNECESSARY-TURN, 4 occurrences in 10 sessions, trending up). The typed taxonomy makes gaps:
- **Countable** — how often does each failure mode occur?
- **Trendable** — is it getting better or worse?
- **Prioritizable** — fix the most frequent gap first
- **Actionable** — each gap code maps to a specific SOP section

This structured output feeds directly into the improvement pipeline from the companion proposal.

### 3. Single-pass is sufficient when the format is structured.

Option B's dual-judge approach elegantly solves the anchoring bias problem, but at 2x cost. Option C mitigates bias differently: by forcing the evaluator to score each decision point independently against a specific rubric (PASS/MINOR/FAIL), rather than producing a holistic impression. The structured format constrains the evaluator's freedom to be vague or biased. This is the same insight behind process reward models — structured per-step evaluation is inherently more calibrated than holistic scoring.

### Trade-off acknowledged

Option C is weaker than Option B on one dimension: it doesn't reconstruct an independent ideal plan. This means it can't detect "unknown unknowns" — cases where a completely different approach would have been better. For the first version of the evaluation framework, this is acceptable. If evaluation data reveals that "unknown unknowns" are a real problem (e.g., the agent consistently misses a skill that should be obvious), we can add Option B's ideal reconstruction as a periodic audit (every 10 sessions) without replacing the per-session process evaluation.

---

## 7. Implementation Plan (if approved)

| Step | What | Effort |
|------|------|--------|
| 1 | Add "Post-Session Evaluation" section to `super-agent.md` with the decision-point extraction, scoring rubric, and gap taxonomy | 45 min |
| 2 | Create `.local/data/super-agent/evaluations.md` template with the decision trace format | 10 min |
| 3 | Create `.local/data/super-agent/gap-trends.md` template with the aggregation table | 10 min |
| 4 | Run 3-5 test sessions and evaluate each to calibrate the taxonomy | 1-2 hours |
| 5 | Add G0: OTHER category and refine taxonomy based on calibration results | 30 min |
| 6 | Add trend aggregation instructions (update gap-trends.md after each evaluation) | 15 min |

**Total estimated effort:** 2.5-4 hours.

**Integration with improvement pipeline:** The evaluation framework (this proposal) produces structured gaps. The improvement framework ([companion proposal](super-agent-self-improvement.md)) consumes those gaps as input to the reflection and consolidation process. Together they form a closed loop: **Evaluate → Identify Gaps → Generate Lessons → Consolidate into SOP Edits → Evaluate Again.**

---

## 8. References

| # | Paper | Authors | Year | Key Contribution |
|---|-------|---------|------|-----------------|
| 1 | [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) | Liu et al. (Tsinghua/OSU) | 2023 | Multi-environment agent benchmark; identifies reasoning and instruction-following as main obstacles |
| 2 | [Judging LLM-as-a-Judge (MT-Bench)](https://arxiv.org/abs/2306.05685) | Zheng et al. (UC Berkeley) | 2023 | LLM judges achieve >80% human agreement; identifies position, verbosity, and self-enhancement biases |
| 3 | [tau-bench: Tool-Agent-User Interaction](https://arxiv.org/abs/2406.12045) | Yao et al. (Princeton) | 2024 | Multi-turn real-world agent evaluation; even GPT-4o <50% success on rule-following tasks |
| 4 | [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) | Lightman et al. (OpenAI) | 2023 | Process supervision significantly outperforms outcome supervision; released PRM800K |
| 5 | [Agent-as-a-Judge: Evaluate Agents with Agents](https://arxiv.org/abs/2410.10934) | Zhuge et al. (Meta/KAUST) | 2024 | Trajectory-aware agent evaluation dramatically outperforms LLM-as-judge |
| 6 | [Autonomous Evaluation and Refinement of Digital Agents](https://arxiv.org/abs/2404.06474) | Pan et al. (UC Berkeley) | 2024 | Automatic evaluators achieve 74-93% oracle alignment; 29% WebArena improvement via eval-guided refinement |
| 7 | [AI Agents That Matter](https://arxiv.org/abs/2407.01502) | Kapoor et al. (Princeton) | 2024 | Critiques accuracy-only benchmarking; advocates joint cost-accuracy optimization |
| 8 | [MMAU: Holistic Benchmark of Agent Capabilities](https://arxiv.org/abs/2407.18961) | Yin et al. | 2024 | 5-competency evaluation framework (understanding, reasoning, planning, problem-solving, self-correction) |
| 9 | [AgentEval: Assessing Task Utility](https://arxiv.org/abs/2405.02178) | Arabzadeh et al. (Microsoft) | 2024 | Auto-generates application-specific evaluation criteria |
| 10 | [Measuring AI Ability to Complete Long Tasks](https://arxiv.org/abs/2503.14499) | Kwa et al. (METR) | 2025 | Time-horizon metric for task complexity; current models at ~50-minute horizons |
