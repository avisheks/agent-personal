# Evolution of LLMs for Planning & Orchestration: Reading Roadmap

> **Last Updated:** 2026-08-02 | **Read time:** ~20 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[orc-physical-systems--notes]] — LLM planning for physical systems (robotics, AV, manufacturing, healthcare)
> - [[self-improving-agents--notes]] — Self-improvement loops (reflection → self-training → harness optimization)
> - [[ai-applied-search-retrieval--notes]] — Agentic search pipelines
> - [[harness-engineering--notes]] — Maturity model for system-level optimization

---

## Quick Catchup

> **Quick Catchup (August 2026):** LLM planning has evolved through 13 identifiable phases: from prompt-based reasoning (CoT, 2022) through tool use (ReAct, 2023), search-based planning (ToT, 2023), hierarchical decomposition, planner-executor-verifier loops, multi-agent systems, memory, workflow orchestration, deep research agents, agentic search, agentic advertising, world models, to self-improving agent operating systems (2025-2026).
> Key players: OpenAI (Deep Research), Google (Gemini agents, ADK), Anthropic (Claude tool use, MCP), Microsoft (AutoGen), LangChain (LangGraph), Amazon (Bedrock AgentCore). Main open problem: building agent OS that continuously self-improve while remaining safe and verifiable.
> Recent breakthrough: frontier systems now resemble distributed operating systems rather than standalone models — with planning, memory, tool orchestration, verification, and self-improvement as core subsystems. Trend: from "better prompts" to "better systems."

## State of the Art

### Current Best Approaches

- **Hierarchical planning + tool orchestration** — decompose goals into subgoals, route to specialist executors, verify outcomes, replan on failure [1][2]
- **Deep research agents** — multi-iteration plan-search-browse-verify-replan loops spanning hours of autonomous research [3]
- **Workflow DAG orchestration** — dependency-managed parallel execution with synchronization, retry, and cost optimization (LangGraph, AutoGen) [4][5]
- **World-model-guided planning** — simulate future states before acting; select actions by predicted outcomes [6][7]
- **Self-improving agent OS** — observe → evaluate → plan → execute → verify → learn → improve policy → repeat [8]

### Recent Breakthroughs (last 12 months)

- **2025-2026:** Deep Research agents (OpenAI, Google, Anthropic) demonstrate multi-hour autonomous research with iterative retrieval and evidence aggregation [3]
- **2025-2026:** Agentic search replaces single-shot RAG with plan-search-verify loops (Perplexity, ChatGPT Search, Bing Copilot)
- **2025-2026:** World models enable planning by imagination — predict consequences before executing (INTACT, FeelWorld, Cosmos) [6][7]
- **2026:** Self-improving agent loops (RHO, SPEAR) demonstrate harness optimization without weight changes [8]
- **2026:** Agentic advertising emerges — autonomous campaign planning, budget optimization, creative generation, performance monitoring

### Open Problems

- **Safety of autonomous planning**: How to bound the actions an agent can take; formal verification of plans before execution
- **Long-horizon coherence**: Maintaining goal alignment over 50+ step plans with branching and replanning
- **Cost of orchestration**: Each planning step costs inference; orchestrating 100 tools over 50 steps costs $1-$10 per task
- **Evaluation of agents**: No consensus on how to measure planning quality beyond task completion rate
- **Catastrophic actions**: Agents with real-world tool access can take irreversible actions (send emails, delete data, spend money)

## Executive Summary

The evolution of LLM planning is one of the fastest-moving areas in AI — progressing from single-chain reasoning (2022) to autonomous self-improving agent systems (2026) in just four years. The trajectory:

```
Reasoning (what to think) → Acting (what to do) → Orchestrating (how to coordinate) → Self-Improving (how to get better)
```

The core architectural question has shifted: it's no longer "how to get the LLM to reason well" but "how to build an entire system that plans, executes, verifies, remembers, and improves."

- **Choose prompt-based planning** (CoT) when tasks are simple, single-turn, no tools needed
- **Choose ReAct loops** when iterative exploration with tools is needed
- **Choose hierarchical planning** when tasks decompose into independent subtasks
- **Choose workflow orchestration** when tasks have dependencies, parallelism, and retry requirements
- **Choose world-model planning** when actions have consequences that should be simulated first
- **Choose agent OS** when continuous improvement over many sessions is the goal

**The killer insight:** "Frontier AI systems increasingly resemble distributed operating systems rather than standalone language models. Planning is the scheduler; tools are the syscalls; memory is the filesystem; verification is the test suite; self-improvement is the update mechanism."

```
Evolution: From Reasoning to Operating Systems
──────────────────────────────────────────────────────────────────
2022         2023          2024           2025          2026
────         ────          ────           ────          ────
CoT          ReAct         Hierarchical   Deep Research Self-Improving
Zero-shot    Tool use      Plan-Execute   Workflow DAG  Agent OS
No tools     Function call Verify-Replan  Memory+Search World Models
Single turn  Multi-step    Multi-agent    Long-horizon  Continuous
```

---

## Evolutionary Stages

### Phase 1 — Prompt-Based Planning (2022)

**Goal:** Elicit multi-step reasoning from LLMs through prompting alone — no tools, no memory, no verification.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Chain-of-Thought Prompting (Wei et al.) [1] | 2022 | Explicit intermediate reasoning steps improve accuracy on math/logic tasks |
| Zero-Shot Reasoners (Kojima et al.) | 2022 | "Let's think step by step" — zero-shot CoT without demonstrations |

**Key transition:** Proves LLMs can reason multi-step when prompted correctly. But planning is implicit, fragile, and bounded by context window. No external action, no correction, no memory.

### Phase 2 — Tool-Augmented Planning (2023)

**Goal:** LLMs interact with the world by calling tools — transitioning from reasoning to acting.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| ReAct (Yao et al.) [2] | 2023 | Think → Act → Observe → Repeat; the canonical agent loop |
| Toolformer (Schick et al.) | 2023 | LLMs learn WHEN to call tools autonomously during generation |
| OpenAI Function Calling | 2023 | Structured JSON output triggers API calls |
| Anthropic Tool Use | 2023 | Same pattern; model selects from tool schemas |

**Key transition:** LLMs gain the ability to ACT — not just reason. This is the birth of the modern AI agent. But still linear (one tool at a time), no parallelism, no complex control flow, no replanning on failure.

### Phase 3 — Search-Based Planning (2023-2024)

**Goal:** Instead of one reasoning chain, explore multiple candidate plans and select the best.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Tree of Thoughts (Yao et al.) [9] | 2023 | Explicit tree search over reasoning branches with evaluation |
| Graph of Thoughts (Besta et al.) [10] | 2023 | Reasoning as a DAG — merge and refine branches; reuse partial solutions |
| RAP (Hao et al.) | 2023 | LLM plans over reasoning trajectories using MCTS |
| Plan-and-Solve (Wang et al.) | 2023 | Decompose → solve subproblems → combine |

**Key transition:** Planning becomes search — exploring alternatives, evaluating, backtracking. Brings classical AI planning (A*, MCTS) into LLM agents. But computationally expensive (many LLM calls per plan) and still single-agent.

### Phase 4 — Hierarchical Planning (2024)

**Goal:** Decompose goals into subgoals at multiple levels of abstraction; plan at each level independently.

| Concept/System | Year | Core Contribution |
|----------------|------|-------------------|
| SayCan hierarchical planning | 2022-2024 | High-level LLM planner → mid-level skill selection → low-level execution |
| HuggingGPT | 2023 | LLM decomposes task → routes subtasks to specialist models |
| TaskWeaver | 2023 | Code-first hierarchical orchestration with dependency management |

**Key transition:** Planning becomes decomposable — different levels of the hierarchy can be solved by different methods (LLM for strategic, classical for tactical, controller for execution). Enables long-horizon tasks, parallel execution, and domain-specific optimization at each level.

### Phase 5 — Planner-Executor-Verifier (2024)

**Goal:** Separate planning from execution from verification — the planner proposes, the executor acts, the verifier checks.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| Reflexion (Shinn et al.) [11] | 2023 | Run → Reflect → Retry; verbal self-critique improves next attempt |
| Self-Refine (Madaan et al.) [12] | 2023 | Generate → Critique → Improve; iterative refinement loop |
| CRITIC (Gou et al.) | 2023 | External tools verify LLM outputs; tool-interactive critiquing |

**Key transition:** Planning gains a verification loop — the system no longer trusts its first plan. Failed plans are diagnosed and repaired. This dramatically improves robustness in coding, enterprise automation, and research tasks. Architecture becomes: Plan → Execute → Verify → Repair → Continue.

### Phase 6 — Multi-Agent Systems (2024)

**Goal:** Multiple specialized agents collaborate on complex tasks — each with distinct roles, tools, and expertise.

| System | Year | Core Contribution |
|--------|------|-------------------|
| AutoGen (Wu et al.) [4] | 2023 | Conversation-driven multi-agent collaboration with tool access per agent |
| MetaGPT (Hong et al.) | 2023 | Role-specialized agents (PM, Architect, Engineer, QA) |
| CAMEL (Li et al.) | 2023 | Role-playing agents for cooperative task solving |
| CrewAI | 2024 | Production multi-agent orchestration with task delegation |

**Key transition:** Planning scales beyond single-agent. An orchestrator assigns subtasks to specialists (research agent, coding agent, reviewer); each plans independently within their domain. Mirrors human team structures. Challenges: coordination overhead, credit assignment, conflict resolution.

### Phase 7 — Memory-Augmented Agents (2024-2025)

**Goal:** Agents persist knowledge across sessions — learning from experience, building context over time.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| Generative Agents (Park et al.) [13] | 2023 | Long-term memory + reflection + planning from accumulated experience |
| MemGPT (Packer et al.) [14] | 2023 | OS-inspired working/long-term memory paging for LLM agents |
| OpenAI persistent memory | 2024-2025 | Cross-session memory in ChatGPT |
| Anthropic long-context agents | 2025 | 200K context + tool use + memory management |

**Key transition:** Planning becomes informed by history — past successes, failures, user preferences, and accumulated knowledge shape future plans. Without memory, every session starts from scratch. With memory, agents compound learning across interactions.

### Phase 8 — Workflow Orchestration (2025)

**Goal:** Coordinate many models, tools, and services through dependency-managed execution graphs with parallelism, retry, and cost optimization.

| System | Year | Core Contribution |
|--------|------|-------------------|
| LangGraph [5] | 2024 | Graph-based agent orchestration with cycles, state, and parallel branches |
| AutoGen v2 | 2025 | Enhanced multi-agent workflows with scheduling and cost management |
| Amazon Bedrock AgentCore | 2025 | Managed agent infrastructure with built-in orchestration |
| Google Agent Development Kit (ADK) | 2025 | Framework for building orchestrated multi-agent applications |

**Key transition:** Attention shifts from model quality to system quality. The orchestration layer handles: scheduling, context routing, dependency graphs, retry policies, cost optimization, latency management. The agent becomes a software system, not just a model.

### Phase 9 — Deep Research Agents (2025-2026)

**Goal:** Agents conduct multi-hour autonomous research — planning searches, browsing results, synthesizing evidence, verifying claims, iterating until the answer is complete.

| System | Year | Core Contribution |
|--------|------|-------------------|
| OpenAI Deep Research [3] | 2025 | Multi-iteration plan-search-browse-summarize-verify loops |
| Google Gemini Deep Research | 2025 | Autonomous research with citation verification |
| Anthropic Claude Research | 2025-2026 | Extended research sessions with tool use and evidence aggregation |

**Key transition:** Planning spans HOURS, not seconds. The agent maintains a research plan, executes it iteratively, adjusts based on findings, and produces a comprehensive synthesis. This is the first production demonstration of truly long-horizon autonomous planning.

### Phase 10 — Agentic Search (2025-2026)

**Goal:** Search becomes planning-centric — instead of "query → retrieve → rank," the agent plans what to search, how to evaluate results, and when to search again.

| System | Year | Core Contribution |
|--------|------|-------------------|
| Perplexity | 2024-2026 | Decompose → search → evaluate → reformulate → synthesize with citations |
| ChatGPT Search (OpenAI) | 2025 | Conversational search with agentic planning |
| Microsoft Copilot Search | 2025 | Multi-turn planned search with synthesis |

**Key transition:** Search becomes a planning problem. Traditional: query → retrieve → rank → answer. Agentic: Goal → Plan searches → Execute → Evaluate evidence quality → Reformulate if insufficient → Synthesize → Cite. Outperforms single-shot RAG by 30-50% on complex queries.

### Phase 11 — Agentic Advertising (2025-2026 — Emerging)

**Goal:** Autonomous agents plan, execute, and optimize advertising campaigns end-to-end.

| System/Pattern | Year | Core Contribution |
|----------------|------|-------------------|
| Google AI Max | 2025 | Gemini-powered keywordless campaign optimization |
| Meta Advantage+ | 2024-2025 | AI-driven audience, creative, bid, and placement optimization |
| Amazon Ads automation | 2025-2026 | Automated campaign creation and budget optimization |

**Key transition:** Advertising becomes a multi-agent planning problem: Business Goal → Campaign Planner → Audience Planner → Budget Planner → Creative Generator → Experiment Planner → Performance Monitor → Replanner. Currently most systems automate portions of this loop; fully autonomous campaign planning remains an active frontier.

### Phase 12 — World Models for Planning (2025-2026)

**Goal:** Plan by simulating consequences — predict future states before acting, select actions with best predicted outcomes.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| DreamerV3 (Hafner et al.) [6] | 2023 | General world model agent: learn latent dynamics → plan in imagination |
| Genie (Google DeepMind) | 2024 | Interactive world models from video |
| SIMA (Google DeepMind) | 2024 | General game-playing via natural language + world model |
| NVIDIA Cosmos [7] | 2026 | Hybrid classical physics (1,300 Hz) + generative world model (60 Hz) for robotics |

**Key transition:** Planning shifts from reactive ("what should I do next?") to predictive ("what will happen IF I do X?"). World models enable: counterfactual reasoning, safer planning (simulate before acting), sample-efficient learning (practice in imagination). Critical for physical systems where trial-and-error is dangerous or expensive.

### Phase 13 — Self-Improving Agent Operating Systems (2026 — Emerging)

**Goal:** Autonomous systems that continuously observe, evaluate, plan, execute, verify, learn, and improve their own policies — without human intervention.

| System/Concept | Year | Core Contribution |
|----------------|------|-------------------|
| RHO (Microsoft) [8] | 2026 | Self-improving harness via trajectory reflection + self-preference |
| SPEAR | 2026 | Autonomous prompt optimization agent |
| DSPy optimization | 2023+ | Programmatic pipeline optimization via automated search |
| Online policy distillation | 2025-2026 | Distill improved behavior back into efficient models |

**Key transition:** The agent becomes a self-improving system — an "operating system" with planning as scheduler, tools as syscalls, memory as filesystem, verification as test suite, and self-improvement as the update mechanism. The frontier vision: agents that improve with every interaction, accumulating skill and knowledge indefinitely.

---

## Key Themes & Connections

### Theme 1: The Capability Stack Grows Over Time

```
2022: Reasoning only (CoT)
 → 2023: + Tools (ReAct) + Search (ToT)
  → 2024: + Verification (Reflexion) + Multi-agent + Hierarchy
   → 2025: + Memory + Workflow orchestration + Deep research
    → 2026: + World models + Self-improvement + Agent OS
```

Each year adds ~2-3 new capabilities to the stack. Modern agents combine ALL prior capabilities simultaneously.

### Theme 2: Cross-Cutting Evolution

| Capability | Early LLMs (2022) | Frontier Agents (2026) |
|------------|-------------------|------------------------|
| Planning | Single reasoning chain | Hierarchical + world-model-guided |
| Search | Static retrieval | Iterative agentic search |
| Execution | None | Multi-tool orchestration |
| Memory | Context window only | Persistent multi-tier memory |
| Coordination | Single model | Multi-agent collaboration |
| Verification | None | Critic + verifier loops |
| Learning | Static weights | Online adaptation + policy improvement |
| Environment | Passive text | Interactive external world |
| Optimization | Prompt engineering | Agent operating systems |

### Theme 3: The Application Domains Follow the Same Arc

The same planning evolution applies to EVERY domain — with domain-specific adaptations:

| Domain | Current Planning State | Domain-Specific Constraint |
|--------|----------------------|---------------------------|
| Software engineering | Phase 9 (Deep Research + coding) | Code correctness is verifiable |
| Search | Phase 10 (Agentic search) | Latency (users expect <5s) |
| Advertising | Phase 11 (emerging) | Revenue optimization + regulatory compliance |
| Robotics | Phase 4-5 (Hierarchical + world model) | Physical safety, real-time (10-100Hz) |
| Autonomous driving | Phase 4-5 (Hierarchical + world model) | Safety-critical certification required |
| Scientific discovery | Phase 6-9 (Multi-agent + deep research) | Experiment cost, reproducibility |
| Enterprise | Phase 8 (Workflow orchestration) | Governance, compliance, approval flows |

### Theme 4: From Better Models to Better Systems

The field's center of gravity has shifted:

```
2022-2023: "How do we make the MODEL reason better?"
 → Prompt engineering, CoT, fine-tuning

2024: "How do we make the SYSTEM work better?"
 → Tool use, verification, multi-agent, memory

2025-2026: "How does the SYSTEM improve itself?"
 → Self-improving harnesses, world models, agent OS
```

Model quality is necessary but no longer sufficient. The system architecture (orchestration, memory, verification, self-improvement) determines agent performance as much as the underlying model.

### Theme 5: Six Dimensions of Tool-Use Research

From the Xu et al. survey (arXiv:2603.22862) [15], the field organizes across:

| Dimension | Core Question |
|-----------|--------------|
| Inference-time planning/execution | How does the agent decide which tools to use and in what order? |
| Training/trajectory construction | How do we train models for multi-tool use? (SFT on trajectories, RL on outcomes) |
| Safety/control | How do we prevent harmful actions and ensure reversibility? |
| Resource efficiency | How do we reduce cost, latency, and token usage? |
| Capability completeness | Can the agent handle ALL tools in its domain, or only a subset? |
| Benchmark design | How do we measure multi-tool orchestration quality? |

Advanced orchestration patterns:
- **RL-optimized workflows (UnityMAS-O [16])** — extends PPO to multi-agent workflows with role-specific credit assignment
- **Compiled planning (Subterranean agents [17])** — distill proven orchestration workflows into model weights for 100x cost reduction

### Theme 6: The Convergence of Search, Ads, and Agents

Agentic search, agentic advertising, and general agent systems are converging on the same architecture:

| Component | General Agent | Agentic Search | Agentic Advertising |
|-----------|--------------|----------------|---------------------|
| Planner | Goal decomposition | Query planning | Campaign planning |
| Executor | Tool calls | Search + browse | Bid + target + create |
| Verifier | Output validation | Evidence quality check | Performance metrics |
| Memory | Session + long-term | Search history | Campaign history |
| Self-improvement | Harness optimization | Query reformulation | Budget reallocation |
| World model | Predict consequences | Predict relevance | Predict conversions |

---

## Reading Schedule

| Week | Papers/Systems | Central Question |
|------|---------------|-----------------|
| **1** | Chain-of-Thought [1], Zero-Shot Reasoners | How do LLMs reason step-by-step through prompting alone? |
| **2** | ReAct [2], Toolformer, Function Calling | How do LLMs interact with tools and the external world? |
| **3** | Tree of Thoughts [9], Graph of Thoughts [10], RAP | How does search over reasoning improve planning quality? |
| **4** | SayCan, HuggingGPT, TaskWeaver | How does hierarchical decomposition enable long-horizon planning? |
| **5** | Reflexion [11], Self-Refine [12], CRITIC | How does verification and repair make plans more robust? |
| **6** | AutoGen [4], MetaGPT, CAMEL, CrewAI | How do multiple specialized agents collaborate on complex tasks? |
| **7** | Generative Agents [13], MemGPT [14] | How does persistent memory enable cross-session learning? |
| **8** | LangGraph [5], Bedrock AgentCore, Google ADK | What does production-grade workflow orchestration look like? |
| **9** | OpenAI Deep Research [3], Gemini Deep Research | How do agents conduct autonomous multi-hour research? |
| **10** | Perplexity, agentic search surveys | How does search become a planning problem? |
| **11** | DreamerV3 [6], NVIDIA Cosmos [7], INTACT, FeelWorld | How do world models enable planning by imagination? |
| **12** | RHO [8], SPEAR, DSPy, agent OS concepts | How do agent systems continuously improve themselves? |

---

## References

### Foundations

- [1] Wei et al. (2022) — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* — NeurIPS — Explicit intermediate reasoning
- [2] Yao et al. (2023) — *ReAct: Synergizing Reasoning and Acting in Language Models* — ICLR — Canonical reason-act-observe loop

### Deep Research & Orchestration

- [3] OpenAI (2025) — *Deep Research* — Multi-iteration autonomous research with plan-search-verify loops
- [4] Wu et al. (2023) — *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation* — Microsoft
- [5] LangGraph (2024) — Graph-based agent orchestration with cycles, state, parallel execution

### World Models

- [6] Hafner et al. (2023) — *Mastering Diverse Domains through World Models (DreamerV3)* — https://arxiv.org/abs/2301.04104
- [7] NVIDIA (2026) — *Cosmos: Hybrid Classical Physics + Generative World Model* — 1,300 Hz physics + 60 Hz generative for robotics

### Self-Improvement

- [8] Pan et al. (2026) — *Evolving Agents in the Dark: Retrospective Harness Optimization via Self-Preference* — https://arxiv.org/abs/2606.05922 — SWE-Bench Pro 59%→78% in one unsupervised cycle

### Search-Based Planning

- [9] Yao et al. (2023) — *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* — NeurIPS
- [10] Besta et al. (2023) — *Graph of Thoughts: Solving Elaborate Problems with Large Language Models*

### Verification & Reflection

- [11] Shinn et al. (2023) — *Reflexion: Language Agents with Verbal Reinforcement Learning* — NeurIPS
- [12] Madaan et al. (2023) — *Self-Refine: Iterative Refinement with Self-Feedback* — NeurIPS

### Memory

- [13] Park et al. (2023) — *Generative Agents: Interactive Simulacra of Human Behavior* — CHI Best Paper
- [14] Packer et al. (2023) — *MemGPT: Towards LLMs as Operating Systems*

### Tool-Use Surveys & Advanced Orchestration

- [15] Xu et al. (2026) — *The Evolution of Tool Use in LLM Agents: From Single-Tool Call to Multi-Tool Orchestration* — https://arxiv.org/abs/2603.22862 — Unified six-dimension framework
- [16] Chen et al. (2026) — *UnityMAS-O: A General RL Optimization Framework for LLM-Based Multi-Agent Systems* — https://arxiv.org/abs/2605.26646 — RL for multi-agent workflow optimization
- [17] Dennis et al. (2026) — *Compiling Agentic Workflows into LLM Weights* — https://arxiv.org/abs/2605.22502 — Embeds orchestration into fine-tuned weights; 100x cost reduction

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| The planning architecture that matters most depends on your latency budget: <1s → ReAct loop; <10s → hierarchical + parallel; <60s → deep research with iteration; hours → full agent OS | Architecture pattern across industry deployments |
| World models are the biggest unlock for physical domains (robotics, AV) — they convert expensive real-world trials into cheap simulated planning | NVIDIA Cosmos, DreamerV3, INTACT results |
| Multi-agent systems add coordination overhead (2-5x more LLM calls); only justified when tasks genuinely require different expertise domains | AutoGen, CrewAI deployment observations |
| Fully autonomous campaign planning (Phase 11) remains aspirational — most production ad systems automate 60-70% of the loop with human oversight on budget and creative approval | Google AI Max, Meta Advantage+ current capabilities |
| The self-improving agent OS vision (Phase 13) works today for harness optimization (prompts, tools, workflows) but NOT for weight updates — the practical frontier is RHO-style improvement | Microsoft RHO, SPEAR results |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-08-02 | Initial v2 generation (study-notes format) | Generated from seed covering 13-phase evolution of LLM planning: CoT → ReAct → ToT → Hierarchical → Verifier → Multi-Agent → Memory → Workflow → Deep Research → Agentic Search → Agentic Ads → World Models → Self-Improving OS |
| 2026-08-02 | Filed | [UNVERIFIED] — run /verify-report --topic evo-ai-orc when runtime available |
