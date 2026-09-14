# RL for LLMs: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-28 | **Read time:** ~20 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (July 2026):** RL for LLMs has evolved from RLHF/PPO (2020-2022) through preference optimization (DPO, 2023) and reasoning RL (GRPO/DeepSeek-R1, 2025) to self-improving agent loops (RHO, 2026) and nascent world-model planning.
> Key players: OpenAI (InstructGPT), Anthropic (Constitutional AI), DeepSeek (R1/GRPO), Microsoft (RHO). Main open problem: a unified Reflection Router that automatically routes each reflection to harness patches, SFT data, or RL signal.
> Recent breakthrough: GRPO eliminates the critic network — training reasoning with only verifiable rewards (Jan 2025) [1]. Trend: from human-in-the-loop alignment toward fully autonomous self-improvement.

## State of the Art

### Current Best Approaches

- **GRPO (Group Relative Policy Optimization)** — removes value function; uses group-sampled baselines; powers DeepSeek-R1 reasoning [1]
- **DPO and variants (SimPO, ORPO, KTO)** — replace PPO with closed-form preference objectives; no reward model needed [4][5][6][7][8]
- **RLVR (RL with Verifiable Rewards)** — replaces noisy human feedback with deterministic verification (math, code, proofs) [11]
- **Retrospective Harness Optimization (RHO)** — improves the surrounding system (prompts, workflows) rather than model weights [19]
- **Self-training loops (ReST, Re-ReST)** — models generate, filter, and train on their own outputs with reflection-corrected trajectories [16][17]

### Recent Breakthroughs (last 12 months)

- **Jan 2025:** DeepSeek-R1 demonstrates pure RL reasoning without SFT warmup via GRPO [1]
- **2025:** RLVR establishes that verifiable reward signals produce more reliable reasoning than human preferences [11]
- **2026:** Retrospective Harness Optimization enables self-improving agents without weight updates [19]
- **2025-2026:** SCFT + RLERR integrates self-critique directly into the RL reward signal [22]

### Open Problems

- **Reflection routing**: No published system unifies routing of reflections to harness + SFT + RL targets simultaneously
- **Reward hacking at scale**: Models exploit verifiable reward functions in unanticipated ways as capabilities grow
- **Sample efficiency**: GRPO and PPO both require large trajectory batches; world-model-based planning for LLMs remains nascent [24][25]
- **Long-horizon credit assignment**: Multi-step agent tasks lack dense reward signals; process rewards vs outcome rewards remain debated

## Executive Summary

RL for LLMs is the set of techniques that optimize language model behavior beyond supervised training — from human alignment (RLHF) through reasoning improvement (GRPO) to autonomous self-improvement (harness optimization + self-training).

The central architectural question is **what provides the reward signal**: humans (RLHF), preferences (DPO), verification (RLVR), or self-reflection (ReST/RHO).

- **Choose DPO/SimPO** when you have preference data but limited compute for PPO infrastructure
- **Choose GRPO/RLVR** when you have verifiable tasks (math, code) and want reasoning depth
- **Choose Harness optimization** when you cannot fine-tune the model but control the surrounding system
- **Choose Self-training** when you need continuous improvement and have a reliable verifier

**The killer insight:** "The field's trajectory is a single arc: removing humans from the reward loop. Each stage automates one more piece — but each automation introduces new failure modes the next technique must address."

```
Improvement Channel (where RL signal routes to)
────────────────────────────────────────────────
Stage         Reward Source       Optimization Target    Human Involvement
─────         ────────────       ───────────────────    ─────────────────
RLHF          Human prefs        Model weights (PPO)    Every example
DPO           Static pairs       Model weights (loss)   Data collection only
GRPO/RLVR     Verifier           Model weights (RL)     None (design verifier)
Self-Train    Self-generated      Model weights (SFT)    None
Harness Opt   Reflection          System config          None
World Model   Imagination         Planning policy        None
```

---

## Evolutionary Stages

The field evolved through 9 identifiable stages. Each builds on the prior, adding a new mechanism for using RL signal to improve LLMs.

### Stage 1 — RLHF: Teaching Models to Follow Instructions

**Goal:** Understand why SFT alone is insufficient — it imitates demonstrations but cannot learn relative quality.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Learning to Summarize from Human Feedback [2] | 2020 | First modern RLHF paper: human preference collection → reward models → PPO for language models |
| InstructGPT [3] | 2022 | Established the three-stage recipe: SFT → Reward Model → PPO. The canonical RLHF pipeline |
| Constitutional AI [4] | 2022 | AI-generated critiques replace human annotation; self-critique + RLAIF at scale |

**Key transition:** Models move from imitating demonstrations to optimizing for human-judged quality. The three-stage post-training recipe (SFT → RM → PPO) becomes standard.

### Stage 2 — Preference Optimization: Removing PPO

**Goal:** Eliminate PPO's complexity (critic network, on-policy sampling, reward model serving) while retaining preference alignment.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| DPO [5] | 2023 | The policy IS the reward model implicitly; closed-form preference loss eliminates PPO entirely |
| IPO [6] | 2023 | Fixes DPO's saturation pathology via squared hinge loss |
| ORPO [7] | 2024 | Eliminates the reference model — folds preference optimization into the SFT loss |
| SimPO [8] | 2024 | Reference-free reward using average log-probability; simplest formulation |
| KTO [9] | 2024 | Prospect theory for preferences — losses loom larger than gains; asymmetric weighting |

**Key transition:** RL infrastructure collapses from 3 stages (SFT + RM + PPO) to a single supervised loss. The insight: the KL-constrained RLHF objective has a closed-form solution that doesn't require explicit reward modeling [5].

### Stage 3 — RL for Reasoning

**Goal:** Shift RL from alignment (making models polite/helpful) to reasoning (making models solve hard problems).

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| DeepSeek-R1 [1] | 2025 | GRPO: removes critic network, uses group-sampled baselines. Pure RL produces emergent long-chain reasoning |
| Qwen Reasoning Reports [10] | 2025 | GRPO at scale; reasoning data generation and scaling laws for reasoning models |
| RLVR (community) [11] | 2024-2025 | Replace human feedback with deterministic verification — math correctness, code execution, proof checking |

**Key transition:** RL reward signal shifts from subjective human preference to objective verification. Models discover reasoning strategies (self-verification, backtracking, "aha moments") through RL alone — without human demonstrations of reasoning [1].

#### Deep Dive: Why the Value Function Exists, and How GRPO Removes It

The value function V(s) in actor-critic methods (PPO, A2C) serves primarily as a **variance-reducing baseline** for policy gradients. The raw policy gradient (REINFORCE, 1992) uses total return R directly — this has prohibitively high variance for LLMs (32K+ token sequences, 100K vocab action space). Subtracting V(s) gives the advantage A(s,a) = Q(s,a) - V(s), reducing variance without bias.

**What breaks without it:**

| Algorithm | Without Value Function |
|-----------|----------------------|
| PPO | Cannot compute GAE advantages; reverts to high-variance REINFORCE; training destabilizes |
| A2C/A3C | Completely non-functional — the critic IS the value function |
| SAC | Cannot compute soft Bellman backup |

**GRPO was NOT the first to remove it.** The lineage of critic-free policy optimization:

| Method | Year | Baseline Strategy |
|--------|------|-------------------|
| REINFORCE | 1992 | None (raw returns) — impractical variance |
| REINFORCE + running avg | 1992+ | Non-state-dependent mean return |
| Reward-weighted regression | 2007 | Weights samples by reward |
| RLOO (Leave-One-Out) | 2024 | Leave-one-out mean of K samples |
| **GRPO** | 2025 | Group mean/std of G samples per prompt |

GRPO's innovation is making critic-free optimization **practical for LLMs** by replacing the learned neural critic with an empirical group statistic: `A_i = (r_i - mean(r_group)) / std(r_group)`. This eliminates ~50% memory overhead (no critic network), has zero approximation error (exact for the sampled group), and normalizes across varying prompt difficulty (the `/std` term). The tradeoff: G forward passes per prompt (compute) instead of one critic pass (memory + learned approximation) [1].

### Stage 4 — Reflection

**Goal:** Can models critique themselves and improve at inference time, without any training?

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Reflexion [12] | 2023 | Run → Reflect → Retry; verbal reflections stored in episodic memory. "Verbal reinforcement learning" |
| Self-Refine [13] | 2023 | Generate → Critique → Improve; iterative refinement without any training |
| Tree of Thoughts [14] | 2023 | Search over reasoning branches — deliberate planning with backtracking |
| Graph of Thoughts [15] | 2023 | Reasoning as a DAG — merging and refining thought branches |

**Key transition:** Improvement moves from training-time to inference-time. Models critique their own outputs and improve them in-context — no weight updates needed. This makes self-improvement applicable to API-only models [12].

### Stage 5 — Self-Training: Reflections Become Training Data

**Goal:** Close the loop — make reflection outputs into supervised training signal.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| ReST [16] | 2023 | Generate → Filter → Train loop: self-generated datasets with quality filtering |
| Re-ReST [17] | 2024 | Trajectory → Reflection → Corrected Trajectory → SFT; recovers value from failures |
| Agent-R [18] | 2024 | Automatic failure localization + trajectory repair → creates supervision signal |

**Key transition:** Reflections are no longer ephemeral (context-only) — they become permanent model improvements via SFT. The model's self-critique generates its own training data, closing the feedback loop [16][17].

### Stage 6 — Harness Optimization: Improving the System, Not the Model

**Goal:** What if you can't change the weights? Improve prompts, tools, and workflows instead.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Retrospective Harness Optimization (RHO) [19] | 2026 | Trajectory → Reflection → Prompt Patch → Regression Test → Deploy |
| Voyager [20] | 2023 | Skill libraries built through exploration; lifelong learning + automatic curriculum |
| Generative Agents [21] | 2023 | Memory + reflection + planning; agent architectures that improve through experience |

**Key transition:** The optimization target expands beyond model weights to the entire agent system. RHO shows agents can self-improve by patching their own orchestration, validated by regression tests [19].

**Counterpoint — Compiling Harnesses Back Into Weights:** While Stage 6 improves the harness around a frozen model, Dennis et al. (2026) show the reverse is also viable: compile procedural workflows directly into small fine-tuned model weights ("subterranean agents"), achieving near-frontier quality at ~100x less cost than frontier models + external orchestration [29]. This suggests a future convergence: harness optimization discovers the right workflow → self-training compiles it into weights → smaller, cheaper models replace complex orchestration stacks.

### Stage 7 — Reflection Meets RL: Reflection as Training Signal

**Goal:** Make reflection quality itself a learnable skill, not just a prompting technique.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Teaching Large Reasoning Models Effective Reflection [22] | 2025 | SCFT (Self-Critique Fine-Tuning) + RLERR (RL with Effective Reflection Rewards) |
| Reflect, Retry, Reward [23] | 2025 | Failure → Reflection → Retry → Reward → RL; reflection-based reward shaping |

**Key transition:** Reflection moves from a prompt technique to a training objective. The model learns *when* and *how* to reflect, with RL reward signal based on whether reflection actually improved the output [22][23].

### Stage 8 — World Models & Long-Horizon Agents

**Goal:** Plan by imagining consequences rather than trial-and-error — the frontier of sample-efficient RL for agents.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| DreamerV3 [24] | 2023 | General world model agent: learn latent dynamics → plan in imagination |
| MuZero [25] | 2020 | Planning without explicit environment models; learned dynamics + MCTS |
| EfficientZero [26] | 2021 | Sample-efficient world-model planning (achieve human-level Atari from 2 hours of play) |
| Genie [27] | 2024 | Interactive world models from video; agent simulation environments |

**Key transition:** From model-free (act → observe → reflect) to model-based (imagine → plan → act). For LLM agents, this means predicting consequences of actions internally before executing — orders-of-magnitude more sample efficient [24][25].

### Stage 9 — Reflection Router (Open Research Direction)

No published paper currently proposes a unified architecture that automatically routes each reflection to the optimal improvement channel:

```
Trajectory
 ↓
Reflection
 ↓
Reflection Router
 ↓
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │              │
Harness        SFT            RL
(prompts,      (corrected     (reward signal
 tools,        demos for      for policy
 workflow)     fine-tuning)   optimization)
```

Existing work routes reflections into **one** pathway:

| Paper | Harness | SFT | RL |
|-------|:-------:|:---:|:--:|
| InstructGPT [3] | — | Yes | Yes |
| Constitutional AI [4] | — | Yes | Yes |
| DPO [5] | — | Yes | — |
| ORPO [7] | — | Yes | — |
| SimPO [8] | — | Yes | — |
| DeepSeek-R1 [1] | — | — | Yes |
| Reflexion [12] | Yes | — | — |
| Self-Refine [13] | Yes | — | — |
| ReST [16] | — | Yes | — |
| Re-ReST [17] | — | Yes | — |
| Agent-R [18] | — | Yes | — |
| Voyager [20] | Yes | — | — |
| Generative Agents [21] | Yes | — | — |
| RHO [19] | Yes | — | — |
| SCFT + RLERR [22] | — | Yes | Yes |
| Reflect, Retry, Reward [23] | — | — | Yes |

**Key insight:** The natural next step is a meta-classifier that, given a reflection, predicts which channel will yield the highest improvement ROI. Features: reproducibility across prompts (harness issue), intermittent success (elicitation gap → harness), never succeeds (capability gap → SFT/RL).

#### Emerging: Multi-Agent RL Optimization for LLMs

A parallel frontier extends single-agent RL (PPO, GRPO) to optimize entire multi-agent workflows end-to-end:

| System | Year | Core Contribution |
|--------|------|-------------------|
| UnityMAS-O [28] | 2026 | General RL framework for LLM-based multi-agent systems — treats workflows (not isolated responses) as the optimization unit; role-specific credit assignment; distributed PPO across agent roles |

UnityMAS-O addresses a critical gap: existing RL post-training frameworks (veRL, NeMo) optimize single policies, but production agents increasingly use multi-agent workflows (planner + retriever + coder + reviewer). The framework introduces four abstractions: logical agent roles, graph trajectories, multi-level rewards (role/turn/trajectory), and flexible parameter sharing (full/partial/none across agents). Built on Ray with a star-topology runtime, it shows gains over manually-specified workflows on retrieval QA, agentic search, and code generation — especially for smaller models [28].

**Key transition:** RL for LLMs evolves from optimizing one model's responses to optimizing entire collaborative workflows — credit assignment becomes the central challenge.

---

## Key Themes & Connections

### Theme 1: The Reward Signal Gets Cheaper Over Time

```
Human annotators ($1/comparison)
 → Learned reward models ($0.01/score)
  → Deterministic verifiers ($0.001/check)
   → Self-generated reflections ($0/reflection)
    → World-model imagination ($0/simulation)
```

Each stage removes a cost bottleneck. The current frontier (RLVR, self-training, harness optimization) requires zero marginal human input per improvement cycle.

### Theme 2: Simplification as Progress

The field's trajectory is consistently toward simpler objectives:

| Era | Method | What it Requires |
|-----|--------|-----------------|
| 2020-2022 | PPO + Reward Model | Critic network, replay buffer, KL tuning, reward model serving |
| 2023 | DPO | Single supervised loss, reference model |
| 2024 | SimPO/ORPO | Single supervised loss, NO reference model |
| 2025 | GRPO | No critic, no reward model, only a verifier |

Each simplification reduces infrastructure, compute cost, and failure modes — while maintaining or improving outcomes.

### Theme 3: Harness vs. Weights — Complementary Timescales

| Dimension | Harness Optimization | Weight Updates (SFT/RL) |
|-----------|---------------------|------------------------|
| Speed | Minutes to deploy | Days to train |
| Cost | ~$0 (config change) | $1K–$1M (GPU time) |
| Reversibility | Git revert | Checkpoint rollback |
| Ceiling | Bounded by model capability | Can exceed prior ceiling |
| Risk | Low (sandboxed, regression-tested) | High (catastrophic forgetting, reward hacking) |

The most capable systems will use both — harness changes for fast iteration, weight updates for permanent capability gains.

### Theme 4: The Verification Bottleneck

Self-improvement without verification is self-delusion. Every stage depends on a verification mechanism:

| Stage | Verification Approach | Limitation |
|-------|----------------------|-----------|
| RLHF | Human judgment | Expensive, noisy, doesn't scale |
| DPO | Static preference dataset | Can't adapt to policy changes |
| GRPO/RLVR | Deterministic verifiers | Only works for verifiable domains |
| Self-training (ReST) | Reward model filter | Filter errors compound over iterations |
| Harness (RHO) | Regression test suite | Tests only cover known scenarios |
| Reflection-RL | Outcome improvement | Circular if reflection quality degrades |

The fundamental constraint: *how do you know the change was actually an improvement?* Each technique is limited by the reliability of its verification mechanism.

### Theme 5: From Single-Channel to Multi-Channel Improvement

Early work optimizes ONE thing (either weights OR harness OR context). The field is converging on systems that optimize ALL channels simultaneously:

- Seconds: working memory (in-context retry)
- Minutes: prompts/tools (harness patches)
- Hours: skill libraries (code generation + tests)
- Days: model weights (SFT on accumulated trajectories)
- Weeks: architecture (human review + redesign)

The Reflection Router (Stage 9) is the missing piece that coordinates these channels.

### Theme 6: Traditional RL → LLM-RL — Each Innovation Solves a Domain-Specific Failure

Traditional RL (Q-learning, REINFORCE, TD-learning) was built for small action spaces, dense rewards, and free simulators. LLMs break every assumption: 100K-token action space, sparse end-of-sequence rewards, no simulator, and $0.01-$1.00 per episode. Each LLM-RL innovation removes one piece of traditional infrastructure that becomes a liability in this setting:

| Traditional RL Assumption | Breaks for LLMs Because... | Innovation That Solves It |
|--------------------------|---------------------------|--------------------------|
| Q(s,a) over all actions | 100K vocab → intractable | Policy gradients (PPO) — no explicit Q |
| Low-variance gradients | 1000+ token sequences | Critic baseline (PPO) → Group baseline (GRPO) |
| Dense rewards per step | Human judges see only final output | Reward model (RLHF) or verifier (RLVR) |
| Free simulator for data | LLM generation is expensive | DPO — train on static dataset, no generation |
| Human reward scales | $0.50/comparison × millions | RLAIF — AI generates preferences |

The evolutionary lineage: `Q-learning → DQN → REINFORCE → PPO → PPO-for-LLMs (RLHF) → DPO → GRPO → RLVR`. Each step removes complexity that's necessary for games/robotics but a liability for text.

**Key insight:** RLHF/DPO/GRPO are NOT different algorithms from PPO/REINFORCE at the math level — they're the same policy gradient principle with domain-specific adaptations that trade off generality for practicality in the LLM setting.

### Theme 7: On/Off-Policy and Model-Free/Based Are Orthogonal Axes

A common misconception: "on-policy = model-free" and "off-policy = model-based." These are two **independent** classification dimensions:

- **On/off-policy** = whose data do you learn from? (current policy only vs. any policy's data)
- **Model-free/based** = do you learn environment dynamics? (no internal model vs. plan in imagination)

All four combinations exist:

| | Model-Free | Model-Based |
|---|-----------|-------------|
| **On-Policy** | PPO, GRPO, A2C, REINFORCE | Dyna, MBPO |
| **Off-Policy** | DQN, SAC, TD3, CQL | MuZero, DreamerV3, AlphaZero |

**For LLM RL specifically:**

| Method | On/Off-Policy | Model-Free/Based |
|--------|--------------|-----------------|
| PPO (InstructGPT) | On-policy | Model-free |
| GRPO (DeepSeek-R1) | On-policy | Model-free |
| DPO | Off-policy (static dataset) | Model-free |
| MCTS + LLM (RAP) | On-policy | Model-based (LLM as world model) |

The confusion arises because LLM RL is dominated by one quadrant (on-policy, model-free) — but DPO is a counterexample (off-policy, model-free) and RAP/Tree-of-Thoughts-with-planning hints at the model-based frontier. Understanding these as independent switches clarifies which techniques can be combined.

---

## Reading Schedule

| Week | Papers | Central Question |
|------|--------|-----------------|
| **1** | Learning to Summarize [2], InstructGPT [3], Constitutional AI [4] | How do we align language models with human preferences? |
| **2** | DPO [5], IPO [6], ORPO [7], SimPO [8], KTO [9] | Can we replace PPO entirely with a single loss function? |
| **3** | DeepSeek-R1 [1], Qwen Reasoning [10], RLVR [11] | How do we use RL to improve reasoning (not just alignment)? |
| **4** | Reflexion [12], Self-Refine [13], Tree of Thoughts [14], Graph of Thoughts [15] | How can models critique themselves and improve at inference time? |
| **5** | ReST [16], Re-ReST [17], Agent-R [18] | How do reflections become permanent training data? |
| **6** | RHO [19], Voyager [20], Generative Agents [21] | How do agents improve without changing model weights? |
| **7** | Teaching LRMs Reflection [22], Reflect-Retry-Reward [23] | How does reflection integrate with RL as a training signal? |
| **8** | DreamerV3 [24], MuZero [25], EfficientZero [26], Genie [27] | How do agents learn world models and plan over long horizons? |

---

## References

### Stage 1 — RLHF

- [1] DeepSeek AI (2025) — *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning* — https://arxiv.org/abs/2501.12948 — Introduces GRPO; RL-first reasoning
- [2] Stiennon et al. (2020) — *Learning to Summarize from Human Feedback* — NeurIPS — First modern RLHF paper
- [3] Ouyang et al. (2022) — *Training Language Models to Follow Instructions with Human Feedback* — https://arxiv.org/abs/2203.02155 — InstructGPT; SFT → RM → PPO pipeline
- [4] Bai et al. (2022) — *Constitutional AI: Harmlessness from AI Feedback* — https://arxiv.org/abs/2212.08073 — AI-generated critiques for RLAIF

### Stage 2 — Preference Optimization

- [5] Rafailov et al. (2023) — *Direct Preference Optimization: Your Language Model Is Secretly a Reward Model* — https://arxiv.org/abs/2305.18290 — Closed-form preference loss
- [6] Azar et al. (2023) — *A General Theoretical Paradigm to Understand Learning from Human Feedback (IPO)* — https://arxiv.org/abs/2310.12036 — Fixes DPO saturation
- [7] Hong et al. (2024) — *ORPO: Monolithic Preference Optimization without Reference Model* — https://arxiv.org/abs/2403.07691 — Removes reference model
- [8] Meng et al. (2024) — *SimPO: Simple Preference Optimization with a Reference-Free Reward* — https://arxiv.org/abs/2405.14734 — Simplest preference objective
- [9] Ethayarajh et al. (2024) — *KTO: Model Alignment as Prospect Theoretic Optimization* — https://arxiv.org/abs/2402.01306 — Prospect theory for preferences

### Stage 3 — Reasoning RL

- [10] Qwen Team (2025) — *Qwen Reasoning Reports* — GRPO at scale; reasoning data generation
- [11] Lambert et al. (2024) — *Reinforcement Learning with Verifiable Rewards* — Deterministic verification replaces human feedback

### Stage 4 — Reflection

- [12] Shinn et al. (2023) — *Reflexion: Language Agents with Verbal Reinforcement Learning* — https://arxiv.org/abs/2303.11366 — Verbal reflection + episodic memory
- [13] Madaan et al. (2023) — *Self-Refine: Iterative Refinement with Self-Feedback* — NeurIPS — Generate-critique-improve loop
- [14] Yao et al. (2023) — *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* — NeurIPS — Search over reasoning branches
- [15] Besta et al. (2023) — *Graph of Thoughts: Solving Elaborate Problems with Large Language Models* — Reasoning as DAG

### Stage 5 — Self-Training

- [16] Gulcehre et al. (2023) — *Reinforced Self-Training (ReST) for Language Modeling* — https://arxiv.org/abs/2308.08998 — Generate → Filter → Train loop
- [17] Yang et al. (2024) — *Re-ReST: Reflection-Reinforced Self-Training for Language Agents* — Reflection-corrected trajectories as SFT data
- [18] Yuan et al. (2024) — *Agent-R: Training Language Model Agents to Reflect via Iterative Self-Training* — Automatic trajectory repair

### Stage 6 — Harness Optimization

- [19] Microsoft Research (2026) — *Retrospective Harness Optimization* — Trajectory reflection → harness patches with regression testing
- [20] Wang et al. (2023) — *Voyager: An Open-Ended Embodied Agent with Large Language Models* — Lifelong skill acquisition
- [21] Park et al. (2023) — *Generative Agents: Interactive Simulacra of Human Behavior* — Memory + reflection + planning architectures

### Stage 7 — Reflection + RL

- [22] Qu et al. (2025) — *Teaching Large Reasoning Models Effective Reflection* — SCFT + RLERR: reflection as RL training signal
- [23] Havrilla et al. (2025) — *Reflect, Retry, Reward: Self-Improving LLMs via Reinforced Reflection* — Closed-loop reflection-RL

### Stage 8 — World Models

- [24] Hafner et al. (2023) — *Mastering Diverse Domains through World Models (DreamerV3)* — https://arxiv.org/abs/2301.04104 — Latent world models for planning
- [25] Schrittwieser et al. (2020) — *MuZero: Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model* — https://arxiv.org/abs/1911.08265 — Planning without explicit env models
- [26] Ye et al. (2021) — *Mastering Atari Games with Limited Data (EfficientZero)* — https://arxiv.org/abs/2111.00210 — Sample-efficient world-model planning
- [27] Bruce et al. (2024) — *Genie: Generative Interactive Environments* — https://arxiv.org/abs/2402.15391 — Interactive world models from video

### Multi-Agent RL for LLMs

- [28] Chen et al. (2026) — *UnityMAS-O: A General RL Optimization Framework for LLM-Based Multi-Agent Systems* — https://arxiv.org/abs/2605.26646 — Extends PPO to multi-agent workflows with role-specific credit assignment and flexible parameter sharing

### Workflow Compilation

- [29] Dennis et al. (2026) — *Compiling Agentic Workflows into LLM Weights: Near-Frontier Quality at Two Orders of Magnitude Less Cost* — https://arxiv.org/abs/2605.22502 — Embeds orchestration workflows into fine-tuned weights ("subterranean agents"); ~100x cost reduction vs frontier + external orchestration

---

## Practitioner Appendix

Informal heuristics and practical observations from talks, blogs, and industry posts — useful context but not peer-reviewed findings.

| Insight | Source |
|---------|--------|
| SFT stage can be skipped when few-shot prompting is already competitive — saves data collection cost with minimal quality loss | https://arize.com/blog/openai-on-rlhf/ |
| As models become more capable, human evaluation becomes infeasible — complex tasks (code review, research) take too long for labelers, creating a fundamental scalability bottleneck | https://arize.com/blog/openai-on-rlhf/ |
| The solution to evaluation scalability is "ML systems that help people evaluate" other ML systems — foreshadowing RLAIF and Constitutional AI | https://arize.com/blog/openai-on-rlhf/ |
| Powerful models may find "deceptive ways to generate outputs at a high score" — optimizing what sounds good to humans rather than actual quality (early reward hacking warning) | https://arize.com/blog/openai-on-rlhf/ |
| Process-level supervision (decomposing tasks into observable steps) is more robust than end-to-end outcome rewards for complex tasks | https://arize.com/blog/openai-on-rlhf/ |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-29 | Added "Compiling Agentic Workflows into LLM Weights" [29] to Stage 6 | check-and-integrate: counterpoint showing harness workflows can be compiled back into model weights at 100x cost reduction |
| 2026-07-29 | Added UnityMAS-O [28] — multi-agent RL for LLM workflows | check-and-integrate: extends RL-for-LLMs from single-agent to multi-agent workflow optimization |
| 2026-07-29 | Added Practitioner Appendix with OpenAI RLHF talk insights | Practical observations from Arize blog (OpenAI talk recap) on skipping SFT, evaluation scalability, reward hacking |
| 2026-07-28 | Initial v2 generation (study-notes format) | Generated from seed: chatgpt-rl-for-llms.md reading roadmap; covers RLHF → DPO → GRPO → Self-improvement → World Models → Reflection Router |
| 2026-07-28 | Added Theme 6: Traditional RL → LLM-RL lineage + Theme 7: On/Off-Policy orthogonality | Follow-up queries on taxonomy and how Q-learning/REINFORCE relate to RLHF/DPO/GRPO |
| 2026-07-28 | Added "Why the Value Function / How GRPO Removes It" deep dive to Stage 3 | Follow-up query: value function role, GRPO historical context, what breaks without critic |
| 2026-07-28 | Filed | [UNVERIFIED] — run /verify-report --topic rl-for-llms when runtime available |
