# Self-Improving Agents: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-29 | **Read time:** ~20 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[auto-agents-frameworks]] — Hermes Agent vs OpenClaw: specific framework comparison (standard format with Q&A, DE Probes, Cost Model)
> - [[harness-engineering--notes]] — Maturity model (Level 0-7) for improving agent performance without weight changes

---

## Quick Catchup

> **Quick Catchup (July 2026):** Self-improving agents have evolved from RL-based planning (AlphaZero) through chain-of-thought reasoning, reflection, memory, tool use, and skill acquisition, to the current frontier: harness optimization (RHO [27]) and self-improving agent platforms that unify execution, reflection, and improvement routing.
> Key players: Reflexion [11], Voyager [21], SWE-agent [29], DSPy [28], RHO [27]. Main open problem: safe deployment of improvements without regression or reward hacking.
> Recent breakthrough: Retrospective Harness Optimization (2026) enables agents to improve prompts, planning, and workflows without weight changes [27]. Trend: optimizing the *system* (harness), not just the *model*.

## State of the Art

### Current Best Approaches

- **Retrospective Harness Optimization (RHO)** — Reflects on trajectories to patch prompts, planning, workflows, and routing; validated by regression tests before deployment [27]
- **Voyager-style lifelong learning** — Agents write code skills to a library, reuse them on future tasks via curriculum-driven exploration [21]
- **Reflexion** — Verbal self-critique stored in memory, enabling retry without weight updates; foundational for in-context self-improvement [11]
- **Self-training loops (ReST/Re-ReST/Agent-R)** — Reflections become fine-tuning data: generate → filter/correct → SFT [24][25][26]
- **DSPy** — Programmatic optimization of prompts, demonstrations, and multi-step pipelines via automated search [28]

### Recent Breakthroughs (last 12 months)

- **RHO** (2026): First systematic framework for improving agent harnesses (prompts, planning, memory, tools) via trajectory reflection with regression testing [27]
- **SWE-agent** (2024): Demonstrated autonomous issue resolution on SWE-bench (~50% on Verified), combining planning, editing, testing, and retry [29]
- **DeepSeek-R1** (2024): RL-trained reasoning model where reflection improves policy weights directly [37]
- **Teaching LRMs Effective Reflection** (2026): Introduced SCFT and RLERR — reflection as an RL signal rather than a prompt technique [38]

### Open Problems

- **Compounding errors in long-horizon loops**: Each self-improvement cycle can introduce subtle regressions; automated regression testing is necessary but not sufficient
- **Safe deployment of self-generated patches**: How to validate that a harness change doesn't degrade performance on out-of-distribution tasks
- **Safety-utility trade-off in self-evolution**: Benign experience can compromise safety — execution-oriented memory reinforces acting over refusing (Zhao et al., ACL 2026 [45])
- **Reward hacking in self-training**: When reflections become training data, the model can learn to produce "reflective-looking" text without genuine improvement
- **Unifying harness optimization with weight updates**: Current approaches treat prompt/workflow optimization and SFT/RL as separate tracks; combining them is an open architecture question
- **Co-improvement vs. autonomous self-improvement**: Weston & Foerster (2025) argue that fully autonomous self-improvement is both less safe and less practical than human-AI collaborative improvement ("co-superintelligence") — integrating human researchers into the improvement loop acts as both a safety mechanism and a research accelerator [46]

### Benchmark Standings

| Benchmark | SOTA Agent | Score | Date |
|-----------|-----------|-------|------|
| SWE-bench Verified [29] | Claude 3.5 Sonnet | ~49% resolve | Oct 2024 |
| HumanEval (Devin) [32] | Devin (Cognition AI) | 86.4% | 2024 |
| Minecraft exploration (Voyager) [21] | Voyager (GPT-4) | 3.3x items vs. ReAct baseline | 2023 |
| WebArena | GPT-4 + SoM | ~35% task success | 2024 |

## Executive Summary

Self-improving agents are AI systems that enhance their own capabilities through experience — without (or in addition to) human-driven retraining. The core architectural question is **where to route improvements**: to the harness (prompts, planning, memory, tools), to the weights (SFT/RL), or both.

- **Choose harness optimization** when you need fast iteration, reversibility, and no retraining cost
- **Choose self-training (SFT/RL)** when you have verifiable rewards and need the improvement baked into the model
- **Choose both (the platform approach)** when building a production system that must improve continuously at multiple timescales

**The killer insight:** "Self-improvement isn't one mechanism — it's a *router*. Reflections that improve a prompt land in minutes; reflections that improve weights land in days. The architecture is the routing table."

```
Improvement Router (where reflections go)
──────────────────────────────────────────
Timescale     Target          Mechanism         Reversibility
─────────     ──────          ─────────         ─────────────
Seconds       Working memory  In-context retry  Ephemeral
Minutes       Prompt/plan     Harness patch     Git revert
Hours         Skill library   Code gen + test   Delete skill
Days          Model weights   SFT on trajs      Checkpoint rollback
Weeks         Architecture    Human review      Full redesign
```

---

## Evolutionary Stages

The field evolved through 14 identifiable stages. Each builds on the prior, adding a new self-improvement mechanism.

### Stage 1 — Foundations: Planning Before LLMs

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Sutton & Barto [1] | 1998/2018 | Agent-environment interaction, policies, delayed rewards, credit assignment |
| AlphaGo [2] | 2016 | Combined planning + search + RL + neural nets; agents improve through environment interaction |
| AlphaZero [3] | 2018 | Pure self-play → improved policy → repeat; autonomous improvement without human demonstrations |
| MuZero [4] | 2020 | Learned internal world model; planning without known environment dynamics |

**Key transition:** Agents can improve by interacting with environments, without human-supplied demonstrations.

### Stage 2 — Chain-of-Thought & Deliberate Reasoning

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Chain-of-Thought [5] | 2022 | Explicit intermediate reasoning steps before acting |
| Self-Consistency [6] | 2022 | Generate multiple reasoning paths, select the best — simple search over reasoning |
| Least-to-Most [7] | 2022 | Automatic decomposition of complex tasks into subtasks |

**Key transition:** Reasoning becomes explicit and decomposable.

### Stage 3 — Search-Based Reasoning

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Tree of Thoughts [8] | 2023 | Explicit search over multiple reasoning branches |
| Graph of Thoughts [9] | 2023 | Reasoning as a DAG — merging and refining thought branches |
| RAP [10] | 2023 | LLMs plan over reasoning trajectories using MCTS |

**Key transition:** Instead of one reasoning path, search over many — bringing planning back into LLM agents.

### Stage 4 — Reflection

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Reflexion [11] | 2023 | Run → Reflect → Retry; reflections stored for future tasks. Foundational self-improvement paper. |
| Self-Refine [12] | 2023 | Generate → Critique → Improve; iterative improvement without training |
| CRITIC [13] | 2023 | External tools verify LLM outputs; verifier-guided improvement |

**Key transition:** Agents critique their own output and improve it — the first explicit self-improvement loop.

### Stage 5 — Memory

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Generative Agents [14] | 2023 | Long-term memory + reflection over memory + planning from memory |
| MemGPT [15] | 2023 | OS-inspired working/long-term memory separation |
| MemoryBank [16] | 2023 | Persistent memory across conversations |

**Key transition:** Learning persists across tasks — agents carry forward lessons from prior experience.

### Stage 6 — Tool Use

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| ReAct [17] | 2023 | Reason → Act → Observe → Repeat; the canonical agent loop |
| Toolformer [18] | 2023 | LLMs learn when to call tools autonomously |
| Gorilla [19] | 2023 | API selection via retrieval; scaling tool use to large API surfaces |

**Key transition:** Agents interact with software — the environment becomes the digital world.

### Stage 7 — Skill Learning

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Voyager [21] | 2023 | Task → Code Skill → Skill Library → Reuse; lifelong learning + curriculum |
| AdaPlanner [22] | 2023 | Adaptive planning through accumulated experience |

**Key transition:** Agents accumulate reusable capabilities — improvement compounds over time.

### Stage 8 — Self-Training

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| ReST [24] | 2023 | Generate → Filter → Train; reflections become SFT data |
| Re-ReST [25] | 2024 | Trajectory → Reflection → Corrected Trajectory → SFT |
| Agent-R [26] | 2024 | Automatic trajectory repair → creates supervision signal |

**Key transition:** Reflections become training data — the loop closes between inference-time and train-time improvement.

### Stage 9 — Harness Optimization

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| RHO [27] | 2026 | Trajectory → Reflection → Harness Patch → Regression Tests → Deploy |
| DSPy [28] | 2023+ | Programmatic optimization of prompts, demonstrations, and workflows |

**Key transition:** Improve the system around the model (prompts, planning, memory, tools) rather than the model weights.

### Stage 10 — Autonomous Software Engineering

| System | Year | Core Contribution |
|--------|------|-------------------|
| SWE-agent [29] | 2024 | Issue → Plan → Edit → Test → Retry; autonomous GitHub issue resolution |
| OpenHands [30] | 2024 | General-purpose software engineering agent |
| MetaGPT [31] | 2023 | Multi-agent software company: PM + Architect + Engineer + QA |
| Devin [32] | 2024 | End-to-end autonomous software engineering workflows |

**Key transition:** Agents improve code (including potentially their own code) — self-modification becomes tractable.

### Stage 11 — Multi-Agent Collaboration

| System | Year | Core Contribution |
|--------|------|-------------------|
| AutoGen [33] | 2023 | Conversation-driven multi-agent collaboration |
| CAMEL [34] | 2023 | Role-playing agents for cooperative task solving |
| CrewAI [35] | 2024 | Production multi-agent orchestration |
| LangGraph [36] | 2024 | Graph-based agent orchestration with memory, planning, reflection |

**Key transition:** Improvement through cooperation and specialization rather than single-agent loops.

### Stage 12 — Self-Improving Reasoning Models

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| DeepSeek-R1 [37] | 2024 | RL-trained reasoning — reflection baked into policy via GRPO |
| Teaching LRMs Reflection [38] | 2026 | SCFT + RLERR — reflection as RL training signal; outperforms baselines on AIME2024/2025 |
| Reflect, Retry, Reward [39] | 2025 | Fail → Reflect → Retry → Reward reflection tokens; +34.7% math, +18.1% function calling |

**Key transition:** Reflection moves from prompt technique to training objective — improvement gets into the weights.

### Stage 13 — World Models

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| DreamerV3 [40] | 2023 | Latent world models for planning in imagination |
| Genie [41] | 2024 | Interactive world models from video |
| SIMA [42] | 2024 | General game-playing via natural language; bridging LLM agents and embodied environments |

**Key transition:** Agents learn predictive environment models — enabling improvement through simulated experience.

### Stage 14 — Self-Evolving Agent Platforms (Emerging)

Two comprehensive surveys — Gao et al. (2025) "What, When, How, Where to Evolve" [43] and Fang et al. (2025) "A Comprehensive Survey of Self-Evolving AI Agents" [44] — formalize this frontier into a taxonomy:

| Evolution Strength | What Changes | Example Systems | Performance |
|-------------------|-------------|-----------------|-------------|
| **Weak** (no weight updates) | Prompts, skill libraries, memory | Voyager [21], FORGE, Reflexion [11], PACE | Voyager: 3.3x items, 15.3x faster milestones |
| **Medium** (RL on scaffolding) | Experience extraction policies, base model frozen | CODESKILL, Evolving-RL | CODESKILL: +9.69% over no-skill baseline |
| **Strong** (weight updates) | Model parameters via meta-learning | SOLAR, Self-Rewarding LMs | Self-Rewarding: Llama 2 70B outperforms GPT-4 0613 after 3 iterations |

The unified architecture routes improvements across all three strengths:

```
Task
 ↓
Execution
 ↓
Trajectory Store
 ↓
Reflection
 ↓
Improvement Router
 ├── Harness (prompts, planning, memory, tools)  →  minutes  [weak]
 ├── Skill Library (new code skills)             →  hours    [weak]
 ├── SFT (corrected demonstrations)              →  days     [strong]
 └── RL (reward signals / preferences)           →  weeks    [medium/strong]
 ↓
Regression Testing
 ↓
Safe Deployment
```

**Dominant design pattern** (from [44]): Skill accumulation + retrieval — generate executable solution → store with retrieval key → compose for future tasks. This pattern recurs from Voyager (2023) through CODESKILL and EvoMaster (2026).

**Safety finding** (Zhao et al., ACL 2026 [45]): Experience gathered from benign tasks can compromise safety in high-risk scenarios — execution-oriented memory reinforces tendency to act rather than refuse, creating a fundamental safety-utility trade-off.

**Characteristics:** Automatic trajectory collection, multi-channel improvement routing, continuous evaluation, regression gating, safe deployment.

---

## Key Themes & Connections

### Theme 1: The Improvement Surface Expands Over Time

```
Weights only (RL era)
 → Reasoning traces (CoT era)
  → Memory (reflection era)
   → Tools and skills (agentic era)
    → The full harness (current era)
```

Each era adds a new target for improvement. Modern systems can improve at every layer simultaneously.

### Theme 2: Verification Is the Bottleneck

Self-improvement without verification is self-delusion. The field's key constraint is always: **how do you know the change was actually an improvement?**

| Mechanism | Verification Approach |
|-----------|---------------------|
| AlphaZero [3] | Win rate in self-play |
| Reflexion [11] | Task success on retry |
| ReST [24] | Binary correctness filter |
| RHO [27] | Regression test suite |
| Self-Rewarding [38] | LLM-as-judge (risky — circular) |

### Theme 3: Harness vs. Weights — Complementary, Not Competing

| Dimension | Harness Optimization | Weight Updates |
|-----------|---------------------|---------------|
| Speed | Minutes to deploy | Days to train |
| Cost | ~$0 (config change) | $1K–$1M (GPU time) |
| Reversibility | Git revert | Checkpoint rollback |
| Ceiling | Bounded by model capability | Can exceed prior ceiling |
| Risk | Low (sandboxed) | High (catastrophic forgetting) |

The most capable systems will use both — harness changes for fast iteration, weight updates for permanent capability gains.

### Theme 4: From Single-Loop to Multi-Agent Improvement

Early work (Reflexion, Self-Refine) is single-agent, single-loop. The field is moving toward:
- Multiple agents that improve each other (debate, red-teaming)
- Specialist improvers (one agent finds bugs, another proposes fixes, a third validates)
- Hierarchical improvement (meta-agent decides *what* to improve)

---

## Reading Schedule

| Week | Papers | Central Question |
|------|--------|-----------------|
| 1 | Sutton & Barto, AlphaGo, AlphaZero, MuZero [1-4] | What is an intelligent agent? |
| 2 | CoT, Self-Consistency, Least-to-Most [5-7] | How do LLMs reason? |
| 3 | Tree of Thoughts, Graph of Thoughts, RAP [8-10] | How do agents search over reasoning? |
| 4 | Reflexion, Self-Refine, CRITIC [11-13] | How do agents critique themselves? |
| 5 | Generative Agents, MemGPT, MemoryBank [14-16] | How do agents learn over time? |
| 6 | ReAct, Toolformer, Gorilla [17-19] | How do agents interact with tools? |
| 7 | Voyager, AdaPlanner [21-22] | How do agents accumulate skills? |
| 8 | ReST, Re-ReST, Agent-R [24-26] | How do reflections become training data? |
| 9 | RHO, DSPy [27-28] | How do agents improve without weight changes? |
| 10 | SWE-agent, OpenHands, MetaGPT, Devin [29-32] | How do autonomous coding agents work? |
| 11 | AutoGen, CAMEL, CrewAI, LangGraph [33-36] | How do agents collaborate? |
| 12 | DeepSeek-R1, SCFT/RLERR, Reflect-Retry-Reward [37-39] | How does reflection improve policies? |
| 13 | DreamerV3, Genie, SIMA [40-42] | How do agents learn world models? |
| 14 | Self-Evolving Surveys [43-44], Safety Risks [45] | What is the taxonomy of self-evolution, and what are the safety risks? |

---

## References

### Foundational (Planning & RL)

- [1] Sutton & Barto (2018) — *Reinforcement Learning: An Introduction* — Core framework for agent-environment interaction and policy optimization
- [2] Silver et al. (2016) — *Mastering the game of Go with deep neural networks and tree search* — Nature — Combined planning, search, RL, and neural networks
- [3] Silver et al. (2018) — *A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play* — Science — Pure self-play without human demonstrations
- [4] Schrittwieser et al. (2020) — *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model* — Nature — Planning with learned world models

### Reasoning & Search

- [5] Wei et al. (2022) — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* — NeurIPS — Explicit intermediate reasoning
- [6] Wang et al. (2022) — *Self-Consistency Improves Chain of Thought Reasoning in Language Models* — Search over reasoning paths
- [7] Zhou et al. (2022) — *Least-to-Most Prompting Enables Complex Reasoning in Large Language Models* — Automatic task decomposition
- [8] Yao et al. (2023) — *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* — NeurIPS — Explicit tree search over reasoning
- [9] Besta et al. (2023) — *Graph of Thoughts: Solving Elaborate Problems with Large Language Models* — Reasoning as graph manipulation
- [10] Hao et al. (2023) — *Reasoning with Language Model is Planning with World Model* — MCTS-based reasoning

### Reflection & Self-Critique

- [11] Shinn et al. (2023) — *Reflexion: Language Agents with Verbal Reinforcement Learning* — NeurIPS — Verbal reflection stored in memory
- [12] Madaan et al. (2023) — *Self-Refine: Iterative Refinement with Self-Feedback* — NeurIPS — Generate-critique-improve loop
- [13] Gou et al. (2023) — *CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing* — External-tool verification

### Memory

- [14] Park et al. (2023) — *Generative Agents: Interactive Simulacra of Human Behavior* — CHI Best Paper — Long-term memory + reflection + planning
- [15] Packer et al. (2023) — *MemGPT: Towards LLMs as Operating Systems* — OS-inspired memory management
- [16] Zhong et al. (2023) — *MemoryBank: Enhancing Large Language Models with Long-Term Memory* — Persistent cross-conversation memory

### Tool Use

- [17] Yao et al. (2023) — *ReAct: Synergizing Reasoning and Acting in Language Models* — ICLR — Canonical reason-act-observe loop
- [18] Schick et al. (2023) — *Toolformer: Language Models Can Teach Themselves to Use Tools* — NeurIPS — Autonomous tool invocation learning
- [19] Patil et al. (2023) — *Gorilla: Large Language Model Connected with Massive APIs* — Retrieval-augmented API selection

### Skill Learning

- [21] Wang et al. (2023) — *Voyager: An Open-Ended Embodied Agent with Large Language Models* — Lifelong skill acquisition and curriculum learning
- [22] Sun et al. (2023) — *AdaPlanner: Adaptive Planning from Feedback with Language Models* — Experience-driven planning adaptation

### Self-Training

- [24] Gulcehre et al. (2023) — *Reinforced Self-Training (ReST) for Language Modeling* — Generate-filter-train loop
- [25] Singh et al. (2024) — *Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models* — Reflection-corrected trajectories as SFT data
- [26] Yuan et al. (2024) — *Agent-R: Training Language Model Agents to Reflect via Iterative Self-Training* — Automatic trajectory repair for supervision

### Harness Optimization

- [27] Microsoft Research (2026) — *Retrospective Harness Optimization* — Trajectory reflection → harness patches with regression testing
- [28] Khattab et al. (2023+) — *DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines* — Programmatic prompt and pipeline optimization

### Autonomous Software Engineering

- [29] Yang et al. (2024) — *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering* — Princeton NLP — Autonomous GitHub issue resolution
- [30] Wang et al. (2024) — *OpenHands (OpenDevin): An Open Platform for AI Software Developers* — General-purpose coding agent
- [31] Hong et al. (2023) — *MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework* — Role-specialized multi-agent programming
- [32] Cognition AI (2024) — *Devin: AI Software Engineer* — End-to-end autonomous software development

### Multi-Agent Systems

- [33] Wu et al. (2023) — *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation* — Microsoft — Conversation-driven collaboration
- [34] Li et al. (2023) — *CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society* — Role-playing cooperation
- [35] CrewAI (2024) — Production multi-agent orchestration framework
- [36] LangGraph (2024) — Graph-based agent orchestration with memory and planning

### Self-Improving Reasoning

- [37] DeepSeek-AI (2024) — *DeepSeek-R1* — RL-trained reasoning with GRPO self-play
- [38] Wang et al. (2026) — *Teaching Large Reasoning Models Effective Reflection* — https://arxiv.org/abs/2601.12720 — SCFT (self-critique fine-tuning) + RLERR (RL with effective reflection rewards); outperforms baselines on AIME2024/2025
- [39] Bensal et al. (2025) — *Reflect, Retry, Reward: Self-Improving LLMs via Reinforcement Learning* — https://arxiv.org/abs/2505.24726 — Two-stage reflection-RL: fail → reflect → retry → reward reflection tokens on success; +34.7% math, +18.1% function calling; smaller models (1.5-7B) outperform larger family members

### World Models

- [40] Hafner et al. (2023) — *Mastering Diverse Domains through World Models (DreamerV3)* — Latent world models for general RL
- [41] Bruce et al. (2024) — *Genie: Generative Interactive Environments* — DeepMind — World models from video
- [42] Reed et al. (2024) — *SIMA: A Generalist AI Agent for 3D Virtual Environments* — DeepMind — Language-grounded game agent

### Self-Evolving Agent Surveys & Safety

- [43] Gao et al. (2025) — *What, When, How, Where to Evolve: A Survey on Self-Evolving Agents* — TMLR, 77 pages — https://arxiv.org/abs/2507.21046 — Comprehensive taxonomy of self-evolution (what/when/how/where)
- [44] Fang et al. (2025) — *A Comprehensive Survey of Self-Evolving AI Agents* — https://arxiv.org/abs/2508.07407 — Weak/medium/strong spectrum; dominant design patterns; industry landscape
- [45] Zhao et al. (2026) — *Safety Risks in Self-Evolving Agents* — ACL Findings — https://arxiv.org/abs/2604.16968 — Benign experience can compromise safety; fundamental safety-utility trade-off
- [46] Weston & Foerster (2025) — *AI & Human Co-Improvement for Safer Co-Superintelligence* — https://arxiv.org/abs/2512.05356 — Argues co-improvement (human-AI collaboration) is safer and more practical than autonomous self-improvement; positions human-in-the-loop as both safety mechanism and research accelerator

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-29 | Added Weston & Foerster [46] co-improvement perspective to Open Problems | check-and-integrate: arXiv:2512.05356 — counterpoint to autonomous self-improvement |
| 2026-07-29 | Fixed [38] attribution: Wang et al. 2026 (not Qu et al. 2024); added arXiv link + AIME benchmark results | check-and-integrate: arXiv:2601.12720 |
| 2026-07-29 | Fixed [39] attribution: Bensal et al. 2025 (not Havrilla 2024); added arXiv link + concrete results (+34.7% math, +18.1% function calling) | check-and-integrate: arXiv:2505.24726 |
| 2026-07-29 | Added Fang et al. (2025) survey + Gao et al. (2025) + Zhao safety findings to Stage 14 | Follow-up query: "Comprehensive Survey of Self-Evolving AI Agents" was missing from report; now integrated with weak/medium/strong taxonomy and safety findings |
| 2026-07-28 | Initial v2 generation | Compiled from seed: chatgpt-self-improving.md reading roadmap |