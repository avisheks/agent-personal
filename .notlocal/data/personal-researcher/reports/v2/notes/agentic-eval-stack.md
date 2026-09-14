# Agent Evaluation Stack: Evolution & Reading Roadmap

> **Last Updated:** 2026-09-13 | **Read time:** ~28 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[evaluation-safety]] — LLM Evaluation & Safety (standard format with Design Flow, Cost Model, Q&A)
> - [[self-improving-agents--notes]] — Self-improving agents evolution (study-notes format)

---

## Quick Catchup

> **Quick Catchup (Sep 2026):** Agent evaluation has evolved from single-output model benchmarks (MMLU, HELM) to multi-layer stacks that evaluate trajectories, not just answers. The canonical stack: unit tests → deterministic evals → benchmarks → trajectory evaluation → LLM judge → human calibration → online metrics [1][2][7].
> Key players: AgentBench [2], SWE-bench [3], GAIA [5], MT-Bench/Chatbot Arena [1], τ-bench [6]. Main open problem: evaluating safety of multi-step agents where individual steps are safe but trajectories are harmful.
> Recent breakthrough: AgentDojo (2024) introduced the first adversarial evaluation framework specifically for prompt injection in tool-using agents [14]. Trend: trajectory-level evaluation + adversarial safety testing as first-class stack layers.

## State of the Art

### Current Best Approaches

- **Multi-environment agent benchmarks (AgentBench)** — 8 environments covering OS, DB, web, games; evaluates agentic capabilities holistically rather than per-task [2]
- **LLM-as-Judge with debiasing (MT-Bench)** — Cross-family judging with position-randomization achieves >80% agreement with human preferences; scalable proxy for human eval [1]
- **Trajectory-level evaluation** — Scoring the full sequence of agent decisions, tool calls, and observations — not just the final answer. ARC Evals [8] pioneered this for autonomous tasks.
- **Adversarial agent safety testing (AgentDojo)** — Dynamic environments that test prompt injection defenses across diverse attack strategies and tool sets [14]
- **Human preference ranking (Chatbot Arena)** — Elo-based ranking from 1M+ pairwise human comparisons; the gold standard for aligning automated metrics with human judgment [1]

### Recent Breakthroughs (last 12 months)

- **AgentDojo** (2024): First adversarial benchmark for prompt injection in tool-using agents — tests whether defenses hold across diverse injection strategies [14]
- **τ-bench** (2024): First benchmark evaluating the full agent↔user↔tool interaction loop with simulated users [6]
- **OSWorld** (2024): Most challenging computer-use benchmark — full desktop environment, success rates under 15% for frontier models [10]
- **SWE-bench Verified** (2024): Human-validated subset of SWE-bench, addressing concerns about benchmark contamination and ambiguous test cases [3]

#### 2025-2026 Developments

- **TheAgentCompany** (Dec 2024, updated Sep 2025): Workplace agent benchmark simulating a full software company environment — web browsing, coding, program execution, and inter-colleague communication. ~30% solve rate for frontier models on professional tasks [21]
- **PaperBench** (Apr 2025): 8,316-task benchmark from OpenAI requiring agents to replicate 20 ICML 2024 papers from scratch. Claude 3.5 Sonnet achieved only 21% replication score — underperforming top ML PhDs [22]
- **50%-task-completion time horizon** (Mar 2025, updated Jul 2026): METR/ARC framework measuring agent capability by the task duration at which AI succeeds 50% of the time. Frontier models at ~50-minute horizon, doubling every 7 months [23]
- **AgentAudit** (Sep 2026): Open framework assessing 10 dimensions (planning, tool selection, security) across full agent execution traces with automated failure attribution [24]
- **BenchShield** (Sep 2026): Formal instrumentation layer detecting reward hacking in agent evaluations through taint analysis and runtime evidence tracking — addresses the meta-evaluation problem [25]
- **BenchMIRT** (Sep 2026): HuggingFace analysis examining what LLM benchmarks are actually measuring — reliability and construct validity of current evaluation methodology [26]
- **Anthropic multi-agent safety** (Aug 2026): Frontier red team examination of challenges in multi-agent AI architectures — the first published safety evaluation framework specifically for multi-agent systems [27]
- **DriftNet** (Sep 2026): Dual-head Transformer achieving 0.983 F1 on detecting prompt injection in agent trajectories — moving injection detection from heuristics to learned classifiers [28]

### Open Problems

- **Trajectory-level safety**: Individual steps can be safe while the full trajectory is harmful (e.g., information gathering that enables an attack). No standard metric exists for trajectory safety.
- **Evaluator reliability at scale**: LLM judges exhibit position bias, verbosity preference, and self-enhancement that degrade measurement quality [1]. Meta-evaluation (evaluating the evaluator) remains ad-hoc.
- **Benchmark saturation and gaming**: As agents optimize for benchmarks, scores lose signal. The field needs continuously renewed evaluation (like Chatbot Arena) rather than static test sets.
- **Bridging offline-to-online eval**: Strong benchmark performance doesn't guarantee production reliability. The connection between offline metrics and online business outcomes is poorly understood.

### Benchmark Standings

| Benchmark | SOTA Agent | Score | Date |
|-----------|-----------|-------|------|
| SWE-bench Verified [3] | Claude Sonnet 4 | ~72% resolve | Jun 2025 |
| WebArena [9] | GPT-4o + SoM agent | ~35% task success | 2024 |
| GAIA [5] | GPT-4 + tools | ~15% (human ~92%) | 2024 |
| OSWorld [10] | Claude 3.5 Sonnet | ~22% task success | 2024 |
| AgentBench [2] | GPT-4 | 4.01 / 5.0 overall | 2024 |

## Executive Summary

Agent evaluation is the discipline of measuring whether an AI agent accomplishes goals correctly, safely, and efficiently across multi-step interactions with tools and environments. The core architectural question is **at which layer to invest evaluation effort**: cheap deterministic checks catch formatting errors but miss reasoning failures; expensive human evaluation catches everything but doesn't scale.

- **Choose deterministic evals** when outputs have verifiable structure (tool call schemas, code execution results, API responses)
- **Choose benchmark suites** when comparing agent architectures or model backbones at a capability level [2][3]
- **Choose LLM-as-Judge** when evaluating nuanced quality at scale (>100 trajectories per eval cycle) and human eval is too slow [1]
- **Choose human calibration** when establishing ground truth for a new domain or validating that automated metrics haven't drifted [1]
- **Choose online metrics** when the question is "does this work in production?" not "does this work on benchmarks?"

**The killer insight:** "The eval stack is a funnel — each layer filters a different failure class. Unit tests catch syntax errors. Benchmarks catch capability gaps. LLM judges catch quality issues. Humans catch the failures that the judges themselves have. Online metrics catch everything the offline stack missed. No single layer is sufficient; the stack IS the evaluation system."

```
Agent Evaluation Stack (progressive cost & fidelity)
─────────────────────────────────────────────────────
Layer 1: Unit tests / assertions     ← $0.00/eval, milliseconds, catches: format errors, schema violations
Layer 2: Deterministic evals         ← $0.00/eval, seconds, catches: tool call correctness, code execution
Layer 3: Benchmarks                  ← $0.01/eval, minutes, catches: capability gaps across environments
Layer 4: Trajectory evaluation       ← $0.05/eval, minutes, catches: plan quality, efficiency, safety
Layer 5: LLM-as-Judge                ← $0.10/eval, seconds, catches: nuanced quality, reasoning coherence
Layer 6: Human calibration           ← $5-50/eval, hours, catches: judge drift, novel failure modes
Layer 7: Online metrics              ← varies, continuous, catches: production failures the stack missed
```

## Evolutionary Stages

The agent evaluation field evolved from **model-centric** (score the output) to **trajectory-centric** (score the journey) to **adversarial** (score the defenses). Each stage introduced a new evaluation primitive.

```
Model benchmarks → LLM-as-Judge → Agent benchmarks → Trajectory eval → Adversarial eval → Interactive eval → Online monitoring
     (2020)          (2023)          (2023)           (2023)           (2024)             (2024)           (ongoing)
```

### Stage 1 — Static Model Benchmarks

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Hendrycks et al. — "Measuring Massive Multitask Language Understanding" (MMLU) [11] | 2021 | 57-task multiple-choice benchmark spanning STEM, humanities, social science — became the default model comparison metric |
| Liang et al. — "Holistic Evaluation of Language Models" (HELM) [7] | 2022 | Multi-dimensional evaluation (accuracy, calibration, robustness, fairness, efficiency) in a single framework — shifted eval from single-number to multi-axis |
| Srivastava et al. — "Beyond the Imitation Game" (BIG-Bench) [12] | 2023 | 204 collaborative tasks probing emergent capabilities — crowd-sourced task design for discovering unexpected model abilities |

**Key transition:** Moved evaluation from accuracy-on-one-task to multi-dimensional profiling, establishing that models have uneven capability landscapes.

### Stage 2 — LLM-as-Judge

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Zheng et al. — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" [1] | 2023 | Demonstrated GPT-4 as a judge achieves >80% agreement with human preferences; identified position bias, verbosity bias, and self-enhancement bias |
| Kim et al. — "Prometheus: Inducing Fine-grained Evaluation Capability in Language Models" [13] | 2024 | Trained a dedicated judge model with rubric-based scoring; showed fine-tuned judges outperform general-purpose models given explicit criteria |
| Shankar et al. — "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs" [17] | 2024 | Proposed validation protocols for LLM judges — the meta-evaluation problem of ensuring the judge itself is calibrated |

**Key transition:** Made scalable quality evaluation possible by replacing human annotators with model judges — but introduced a new reliability problem (evaluating the evaluator).

### Stage 3 — Agent Benchmarks (Multi-Environment)

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Liu et al. — "AgentBench: Evaluating LLMs as Agents" [2] | 2024 | First comprehensive multi-environment benchmark (8 environments); revealed that even GPT-4 scores far below human performance on agentic tasks |
| Jimenez et al. — "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" [3] | 2024 | Real-world coding tasks as agent benchmarks; the "Verified" subset (human-validated) became the standard for coding agent evaluation |
| Mialon et al. — "GAIA: A Benchmark for General AI Assistants" [5] | 2023 | Multi-step reasoning + tool use + web browsing; designed to be trivial for humans (~92%) but hard for agents (~15%) |

**Key transition:** Shifted evaluation from "can the model answer questions?" to "can the agent accomplish tasks in realistic environments?" — the birth of trajectory-aware evaluation.

### Stage 4 — Trajectory-Level Evaluation

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Kinniment et al. — "Evaluating Language-Model Agents on Realistic Autonomous Tasks" (ARC Evals) [8] | 2023 | Most rigorous framework for multi-step autonomous agent evaluation; introduced evaluating the trajectory (decision sequence), not just the final output |
| Zhou et al. — "WebArena: A Realistic Web Environment for Building Autonomous Agents" [9] | 2024 | Self-hosted realistic websites with functional backends; evaluated web agents on the full navigate→interact→verify trajectory |

**Key transition:** Evaluation primitive expanded from "single output" to "sequence of decisions" — requiring new metrics (trajectory efficiency, plan quality, recovery from errors).

### Stage 5 — Adversarial & Safety Evaluation

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Greshake et al. — "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" [15] | 2023 | Defined the taxonomy of indirect prompt injection attacks against tool-using agents — showed untrusted content can hijack agent behavior |
| Debenedetti et al. — "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents" [14] | 2024 | First adversarial benchmark for tool-using agents; tests whether defenses hold across diverse injection strategies and tool sets |
| Ruan et al. — "Identifying the Risks of LM Agents with an LM-Emulated Sandbox" [16] | 2023 | Proposed emulating the entire environment with LLMs for cheap, scalable agent safety testing — bridging offline eval and production monitoring |

**Key transition:** Evaluation expanded from "does the agent succeed?" to "can the agent be attacked?" — making adversarial robustness a first-class evaluation dimension.

### Stage 6 — Interactive & Simulated-User Evaluation

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Yao et al. — "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" [6] | 2024 | First benchmark evaluating the full agent↔user↔tool interaction loop with simulated users — captures conversational dynamics static benchmarks miss |
| Xie et al. — "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments" [10] | 2024 | Full desktop environment with multi-application tasks; most challenging agent benchmark with frontier model success rates under 15% |
| Park et al. — "Generative Agents: Interactive Simulacra of Human Behavior" [18] | 2023 | Simulated 25 agents with memory, reflection, and social interaction — pioneered using simulated users as evaluation environments |

**Key transition:** Evaluation moved from static input→output to **dynamic interaction** — agents evaluated in conversations with simulated users and in environments that respond to agent actions.

### Stage 7 — Human Calibration at Scale

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| LMSYS — Chatbot Arena [1] | 2023-ongoing | Elo-based ranking from 1M+ pairwise human comparisons; proved that crowdsourced pairwise comparison scales better than absolute scoring |
| Anthropic — "Measuring Model Capabilities and Safety" (Responsible Scaling Policy) [19] | 2024 | Structured human evaluation for dangerous capabilities with explicit deployment thresholds — the eval→red-team→deploy framework |

**Key transition:** Human eval moved from "expensive quality check" to **the calibration anchor** that all automated metrics are validated against. Pairwise comparison proved more reliable than absolute scoring.

### Stage 8 — Online Monitoring & Production Eval (emerging)

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| OpenAI — "A Practical Guide to Building Agents" [4] | 2025 | Defined production agent metrics: task completion rate, tool call success rate, cost per task, latency per step, user intervention rate |
| LangChain — "LangSmith Agent Evaluation" [20] | 2024 | Most complete open-source framework for agent observability + eval in production; traces every step, connects offline evals to online metrics |

**Key transition:** Evaluation became **continuous** rather than point-in-time — production metrics feed back into offline eval design, creating a flywheel where online failures generate new test cases.

## Key Themes & Connections

### Theme 1: The Evaluation Fidelity / Cost Tradeoff

Every layer in the stack trades cost for fidelity. The art is knowing which layer to invest in for your failure mode.

| Layer | Cost per Eval | Latency | Catches | Misses |
|-------|---------------|---------|---------|--------|
| Unit tests | $0 | ms | Schema violations, format errors | Reasoning failures, quality issues |
| Deterministic evals | $0 | sec | Tool call correctness, code bugs | Subtle quality, nuanced safety |
| Benchmarks | $0.01 | min | Capability gaps across tasks | Domain-specific failures, production dynamics |
| Trajectory eval | $0.05 | min | Plan quality, efficiency, recovery | Adversarial attacks, user interaction issues |
| LLM-as-Judge | $0.10 | sec | Nuanced quality, coherence | Novel failures the judge hasn't seen |
| Human calibration | $5-50 | hrs | Everything above + novel failures | Doesn't scale; sampling bias |
| Online metrics | varies | continuous | Real production failures | Slow feedback; post-hoc only |

**Why it matters:** Practitioners who default to "just use GPT-4 as a judge for everything" waste money on failures that a $0 regex check would catch. Practitioners who only use unit tests miss everything above the format layer. The stack exists because **each failure class has a cost-optimal detection layer**.

### Theme 2: The Meta-Evaluation Problem

At every layer above unit tests, the evaluator itself can be wrong. LLM judges have biases [1]. Benchmarks can be gamed [3]. Human annotators disagree. This creates a recursive problem: who evaluates the evaluator?

| Evaluation Layer | Known Failure Modes | Mitigation |
|-----------------|--------------------|-|
| LLM-as-Judge | Position bias, verbosity preference, self-enhancement [1] | Cross-family judging, position randomization, rubric grounding [13] |
| Benchmarks | Contamination, gaming, saturation | Continuously renewed sets (Chatbot Arena), human-validated subsets (SWE-bench Verified) |
| Human eval | Annotator disagreement, fatigue, anchoring | Pairwise comparison (not absolute scoring), calibration rounds, inter-annotator agreement tracking |
| Online metrics | Goodhart's Law (optimizing the metric degrades the goal) | Multiple complementary metrics, qualitative review alongside quantitative |

**Why it matters:** A Principal-level answer doesn't just describe the eval stack — it also describes how you validate each layer. "We use LLM-as-Judge" is an L5 answer. "We use LLM-as-Judge with monthly κ measurement against human labels and cross-family judging to mitigate self-enhancement bias" is a Principal answer.

### Theme 3: From Model Eval to Agent Eval (the trajectory shift)

The deepest conceptual transition in the field: model evaluation scores a **single output**; agent evaluation scores a **trajectory** (sequence of decisions, observations, and actions). This changes everything — metrics, baselines, annotation, and cost.

| Dimension | Model Eval | Agent Eval |
|-----------|-----------|-----------|
| Unit of evaluation | Single output (text, code, classification) | Trajectory (N steps × M tool calls × K observations) |
| Success metric | Accuracy, F1, BLEU, human preference | Task completion + trajectory quality + safety + efficiency |
| Annotation cost | ~$0.10 per output | ~$5-50 per trajectory (must review full sequence) |
| Failure diagnosis | "The output was wrong" | "Step 3 was correct but step 7 used wrong context from step 4" |
| Safety evaluation | "Is this output harmful?" | "Is this trajectory harmful even though each step looks safe?" |

**Why it matters:** Teams that apply model eval techniques to agents (scoring the final output only) miss the most important signal — **why** the agent succeeded or failed. Trajectory evaluation is the new primitive.

### Theme 4: Adversarial Testing as a First-Class Layer

Agent safety can't be an afterthought bolted onto capability eval. Prompt injection [15], permission escalation, and cascading failures in agent chains are **architecturally different** from model-level safety (harmful text generation). They require dedicated evaluation infrastructure.

| Attack Surface | Model-Level | Agent-Level |
|---------------|------------|------------|
| Prompt injection | User input manipulation | **Indirect injection via untrusted content** (emails, web pages, tool outputs) [15] |
| Permission escalation | N/A | Agent acquires capabilities not in its initial scope over a trajectory |
| Cascading failure | N/A | One agent's compromised output becomes another agent's trusted input |
| Self-propagating attacks | N/A | Adversarial content that replicates across connected agents |

**Why it matters:** At frontier labs (Anthropic, OpenAI, DeepMind), the ability to design adversarial evaluations for tool-using agents is a **differentiator**. Candidates who can only discuss model-level safety (RLHF, constitutional AI) but not agent-level safety (trajectory-level threat models, sandboxing, blast radius) reveal a gap.

## Reading Schedule

| Week | Papers | Central Question |
|------|--------|-----------------|
| 1 | HELM [7], MMLU [11], BIG-Bench [12] | How did model evaluation evolve from single-metric to multi-dimensional? What are the limitations of static benchmarks? |
| 2 | MT-Bench / Chatbot Arena [1], Prometheus [13] | When and why did the field move to LLM-as-Judge? What biases does it introduce, and how are they mitigated? |
| 3 | AgentBench [2], SWE-bench [3], GAIA [5] | What changes when you evaluate agents instead of models? Why do frontier models score so poorly on agent benchmarks? |
| 4 | ARC Evals [8], WebArena [9], τ-bench [6] | What does trajectory-level evaluation look like in practice? How do you score a sequence of decisions, not just a final answer? |
| 5 | Greshake [15], AgentDojo [14], Ruan [16] | How do you evaluate agent safety? What attack surfaces exist that model-level safety doesn't cover? |
| 6 | OSWorld [10], Generative Agents [18], Who Validates the Validators [17] | How do simulated environments and simulated users change evaluation? How do you validate your evaluation system itself? |
| 7 | Chatbot Arena methodology [1], Anthropic RSP [19], OpenAI agents guide [4], LangSmith [20] | How does the full stack connect — from offline benchmarks to human calibration to production monitoring? |

## References

### LLM-as-Judge & Human Evaluation

[1] Zheng et al. (2023) — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" — NeurIPS 2023 — Foundational paper on using LLMs as scalable evaluators; introduces position bias, verbosity bias, self-enhancement bias

[13] Kim et al. (2024) — "Prometheus: Inducing Fine-grained Evaluation Capability in Language Models" — ICLR 2024 — Dedicated judge model with rubric-based scoring outperforms general-purpose models

[17] Shankar et al. (2024) — "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs" — Validation protocols for LLM judges; the meta-evaluation problem

### Agent Benchmarks

[2] Liu et al. (2024) — "AgentBench: Evaluating LLMs as Agents" — ICLR 2024 — First comprehensive 8-environment agent benchmark; frontier models far below human performance

[3] Jimenez et al. (2024) — "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" — ICLR 2024 — Real GitHub issues as coding agent benchmark; Verified subset is the gold standard

[5] Mialon et al. (2023) — "GAIA: A Benchmark for General AI Assistants" — Multi-step reasoning + tools + web; trivial for humans (~92%), hard for agents (~15%)

[6] Yao et al. (2024) — "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" — First benchmark with simulated users for the full agent↔user↔tool loop

[9] Zhou et al. (2024) — "WebArena: A Realistic Web Environment for Building Autonomous Agents" — ICLR 2024 — Self-hosted realistic websites with functional backends

[10] Xie et al. (2024) — "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments" — Full desktop environment; most challenging agent benchmark (<15% success)

### Trajectory & Autonomous Task Evaluation

[8] Kinniment et al. (2023) — "Evaluating Language-Model Agents on Realistic Autonomous Tasks" — ARC Evals — Most rigorous framework for evaluating multi-step autonomous agent behavior

[18] Park et al. (2023) — "Generative Agents: Interactive Simulacra of Human Behavior" — UIST 2023 — Simulated agents with memory, reflection, and social interaction; pioneered simulated-user evaluation environments

### Agent Safety & Adversarial Evaluation

[14] Debenedetti et al. (2024) — "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents" — First adversarial benchmark for tool-using agents

[15] Greshake et al. (2023) — "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" — Definitive taxonomy of indirect prompt injection attacks against agents

[16] Ruan et al. (2023) — "Identifying the Risks of LM Agents with an LM-Emulated Sandbox" — LLM-emulated environments for scalable agent safety testing

### Static Model Benchmarks

[7] Liang et al. (2022) — "Holistic Evaluation of Language Models (HELM)" — Multi-dimensional evaluation framework (accuracy, calibration, robustness, fairness, efficiency)

[11] Hendrycks et al. (2021) — "Measuring Massive Multitask Language Understanding (MMLU)" — 57-task multiple-choice benchmark that became the default model comparison metric

[12] Srivastava et al. (2023) — "Beyond the Imitation Game Benchmark (BIG-Bench)" — 204 collaborative tasks for probing emergent model capabilities

### Production & Industry

[4] OpenAI (2025) — "A Practical Guide to Building Agents" — Defines production agent metrics: task completion, tool success rate, cost, latency, intervention rate

[19] Anthropic (2024) — "Measuring Model Capabilities and Safety" (Responsible Scaling Policy) — Structured human evaluation with explicit deployment thresholds

[20] LangChain (2024) — "LangSmith: Agent Evaluation & Observability" — Open-source framework connecting offline evals to production monitoring

### Recent (last 12 months)

[21] Xu et al. (2024, updated 2025) — "TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks" — arXiv:2412.14161 — Simulated workplace benchmark; ~30% solve rate reveals the gap between task-level and job-level agent competence

[22] Starace et al. (2025) — "PaperBench: Evaluating AI's Ability to Replicate AI Research" — arXiv:2504.01848 — 8,316-task research replication benchmark; frontier agents underperform ML PhDs, revealing limits of current agent reasoning

[23] Kwa et al. (2025, updated 2026) — "Measuring AI Ability to Complete Long Software Tasks" — arXiv:2503.14499 — Introduced 50%-task-completion time horizon metric; doubling every 7 months; projects month-long task automation within 5 years

[24] Nag et al. (2026) — "AgentAudit: An Open, Extensible Framework for Full-Lifecycle Trust Evaluation of AI Agents" — arXiv:2609.09875 — 10-dimension trust evaluation across full execution traces with automated failure attribution

[25] Zheng et al. (2026) — "BenchShield: Formal Model-Backed Instrumentation for Reward Integrity in LLM-Agent Evaluation" — arXiv:2609.11028 — Taint analysis and runtime evidence tracking to detect reward hacking in agent benchmarks

[26] HuggingFace (2026) — "BenchMIRT: What are LLM benchmarks actually measuring?" — HuggingFace blog — Psychometric analysis of benchmark reliability and what scores actually indicate about model capabilities

[27] Anthropic (2026) — "Patterns and problems in emerging multiagent systems" — anthropic.com/research/multiagent-systems — Frontier red team analysis of safety challenges specific to multi-agent architectures

[28] Pinjari & Paul (2026) — "DriftNet: Detecting and Localizing Prompt Injection in LLM Agents" — arXiv:2609.10892 — Learned injection detection achieving 0.983 F1, replacing heuristic-based approaches

[29] Anthropic (2025) — "Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet" — anthropic.com — 49% on SWE-bench Verified; detailed methodology on tool design and eval challenges (token costs, grading complications, false success detection)

<!-- RECENCY GAP: OpenAI agent evaluation announcements 2025-2026 — search for:
     "BrowseComp" (web browsing benchmark), "Preparedness Framework" updates,
     "OpenAI evals" framework updates, and any new agent safety evaluation
     publications. OpenAI research page returns 403; check openai.com/index/ or
     arxiv for OpenAI-authored eval papers from 2025-2026. -->

<!-- RECENCY GAP: Google DeepMind agent evaluation 2025-2026 — search for:
     "Agent Hospital" benchmark, Gemini agent evaluation methodology,
     Google DeepMind safety evaluation publications, and any SWE-bench/WebArena
     results for Gemini models. -->

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| "The most reliable evaluations tend to be simple and focused" — start with deterministic evals before reaching for LLM judges | Anthropic, "Building Effective Agents" (blog, 2024) |
| "Your AI Product Needs Evals" — best practitioner guide to building eval suites from assertions up through model-graded evals | Hamel Husain / Braintrust (blog, 2024) |
| Pairwise comparison is far more reliable than absolute scoring for human eval — Chatbot Arena proved this at 1M+ comparisons | LMSYS team, various blog posts (2023-2024) |
| "Safety is a constraint (binary pass/fail), not a dimension to trade off against quality" — frame safety as a gate, not a score | Common framing in Anthropic RSP and industry safety discourse |
| No single paper covers the full eval stack end-to-end — the closest are Anthropic's "Building Effective Agents" (practitioner) and AgentBench (academic) | Field observation as of Sep 2026 |
| The eval stack is a funnel: each layer filters a different failure class, and no single layer is sufficient | Synthesis across [1][2][4][7][8] |
| Teams that apply model eval techniques to agents (scoring final output only) miss the most important signal — WHY the agent succeeded or failed | Derived from ARC Evals [8] and τ-bench [6] methodology |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-09-12 | Initial v2 generation | Filed from conversation on agent eval stack literature |
| 2026-09-13 | Added 2025-2026 references (additive) | Recency gate: 8 recent breakthroughs, 9 recent references, 2 RECENCY GAP comments for OpenAI/DeepMind |
