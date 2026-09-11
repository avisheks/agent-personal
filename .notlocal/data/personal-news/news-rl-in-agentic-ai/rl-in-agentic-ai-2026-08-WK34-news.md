# RL for Agentic AI Weekly Briefing (Week 34)
**Week 34 | August 16–22, 2026**
⏱️ 22 min read

First report — baseline established. All trend tracking, Watch List, and prediction scoring begin from this issue.

---

## 📋 Executive Briefing

The harnessed agentic RL paradigm reached critical mass this week. Three independent teams — [Agent Lightning](https://arxiv.org/abs/2608.17528) (Microsoft), [LEGO-RL](https://arxiv.org/abs/2608.17393) (multiple labs), and [ClawGym II](https://arxiv.org/abs/2608.16798) (Renmin University et al.) — converged on the same core insight: let the deploy-time harness own the environment loop while the RL trainer observes only LLM request-response pairs through a proxy. Agent Lightning achieved a 14.6-point gain on [SWE-bench Verified](https://www.swebench.com/) using just 6K examples; LEGO-RL pushed Qwen3.5-35B to 70.4% on OpenHands SDK. This is not incremental — it is the emergence of a unified training interface for coding agents.

Simultaneously, self-play matured beyond toy settings. [SPADE](https://arxiv.org/abs/2608.19197) (University of Washington, Allen AI) introduced regret-guided self-play where an LLM designs its own training environments as executable code, achieving +5.3 average on reasoning benchmarks and +13.9 on agent tasks. [Ornith-1.5](https://ornith.ai/ornith_1_5.html) demonstrated closed-loop self-improvement at scale, with a 397B MoE model matching [Claude Opus 4.8](https://www.anthropic.com/) on Terminal-Bench 2.1 through self-generated curriculum optimized via [GRPO](https://arxiv.org/abs/2402.03300).

Credit assignment — the fundamental bottleneck in long-horizon agent RL — saw three distinct advances: [SkillGate](https://arxiv.org/abs/2608.18852) solved selector credit starvation with dual credit channels, [SA-MRPO](https://arxiv.org/abs/2608.16072) introduced saturation-aware reweighting for multi-reward optimization, and [EnvHarness](https://arxiv.org/abs/2608.19880) (Google) showed that dynamically reshaping environments beats static reward engineering.

---

## ⚡ What Changed Since Last Week

- **[Harnessed agentic RL convergence](https://arxiv.org/abs/2608.17528)** — Three independent teams published proxy-based RL frameworks for coding agents in the same week, signaling a new training paradigm
- **[SPADE: Regret-guided self-play](https://arxiv.org/abs/2608.19197)** — LLMs now design their own executable training environments with adaptive difficulty calibration
- **[Ornith-1.5 self-improvement](https://ornith.ai/ornith_1_5.html)** — Closed-loop GRPO self-training matches frontier models across three scales (9B, 35B, 397B)
- **[SkillGate credit starvation fix](https://arxiv.org/abs/2608.18852)** — Dual credit architecture separates skill-selection from execution rewards, +12.4 points on 9B model
- **[Co-RL: Peer-rewarded multi-agent RL](https://arxiv.org/abs/2608.17253)** — Unsupervised reasoning emergence through cohort diversity without ground-truth labels
- **[τ₀-VLA world-model robot planning](https://arxiv.org/abs/2608.16885)** — Hierarchical VLA uses world models for test-time compute scaling in robot manipulation
- **[Agentic ESOpt](https://arxiv.org/abs/2608.17310)** — Evolution strategies outperform RL for long-horizon agent training with inference-level GPU memory
- **[NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** — Open-source framework measuring skill impact: +41 correctness points on average across 300+ skills
- **[EnvHarness](https://arxiv.org/abs/2608.19880)** — Google's programmable environment wrapper adapts to agent weaknesses without altering verifiers
- **[SA-MRPO: Saturation-aware multi-reward RL](https://arxiv.org/abs/2608.16072)** — Adaptive discounting reallocates optimization toward under-solved objectives

---

## 🔬 Top Technical Developments

### 1. SPADE: Self-Play in Adaptive Synthetic Executable Environments

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 7/10 |
| Business Impact | 8/10 |
| Personal Relevance | 10/10 |
| Confidence | High |

🧪 Early prototype

**Source:** [SPADE](https://arxiv.org/abs/2608.19197) — Liu, Yu, Jiang, Qu, Zhao, Liu et al. (UW, Allen AI) | **Reading time:** 15 min

An LLM simultaneously acts as Environment Designer and Reasoning Agent. The Designer creates executable environments as code, grounded in pretraining corpus documents, while a regret signal — the performance gap with and without privileged hints — calibrates difficulty to the agent's capability edge. Achieves +5.3 average on math/reasoning benchmarks and +5.7 to +13.9 on specialized tool-use and agent evaluation datasets across models up to 30B.

> 💡 **Key Insight:** Self-play for agents no longer requires hand-crafted environments. SPADE's regret-guided curriculum generation creates a fully autonomous training loop — the agent generates its own challenges, solves them, and uses failure signal to design harder ones.

---

### 2. LEGO-RL + Agent Lightning: Harnessed Agentic RL for Coding Agents

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 9/10 |
| Business Impact | 9/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🚀 Production-ready

**Source:** [LEGO-RL](https://arxiv.org/abs/2608.17393) (Du, Jiang et al.) + [Agent Lightning v1.0](https://arxiv.org/abs/2608.17528) (He, Zhang et al., Microsoft) | **Reading time:** 12 min each

Two complementary frameworks solving the same problem: how to apply RL to agents running inside complex harnesses (OpenHands, Claude Code, OpenCode) without modifying internal control flow. Both use LLM endpoint proxies to intercept interactions. LEGO-RL pushed Qwen3.5-35B from 64.0% to 70.4% on OpenHands SDK; Agent Lightning improved Qwen3.5-9B from 41.8% to 56.4% on SWE-bench Verified with only 6K training examples.

> 🚀 **Opportunity:** The harness-native RL paradigm means any team with an existing coding agent harness can now add RL training without rewriting their agent. The proxy-based approach preserves deploy-time fidelity (>0.99 rollout-training correlation).

---

### 3. SkillGate: Solving Selector Credit Starvation

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 7/10 |
| Business Impact | 7/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🧪 Early prototype

**Source:** [SkillGate](https://arxiv.org/abs/2608.18852) — Li, Jiao, Shao et al. (Shanghai Jiao Tong) | **Reading time:** 10 min

Identifies a fundamental problem: skill-selection tokens receive vanishingly small loss shares under standard RL, causing correct skill choices to be penalized when downstream execution fails. SkillGate separates credit into two channels — outcome credit for execution tokens and action-local advantage for skill-naming tokens. Improves a 9B policy from 40.8% to 53.2% success rate on 16-candidate skill libraries.

> 💡 **Key Insight:** Credit assignment in agent RL is not just about temporal horizons — it is about functional roles within the action space. Separating "what to call" from "how to execute" is a fundamental decomposition.

---

### 4. Co-RL: Unsupervised Reasoning via Multi-Agent RL

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 6/10 |
| Business Impact | 7/10 |
| Personal Relevance | 8/10 |
| Confidence | Medium |

🔬 Research-only

**Source:** [Co-RL](https://arxiv.org/abs/2608.17253) — Yang, Bian, Tian et al. (UC San Diego) | **Reading time:** 12 min

Multiple decoupled models provide reward signals to each other during training, replacing human labels entirely. Cohort diversity — heterogeneous model families, sizes, and rephrased samples — prevents training collapse. Achieves 3.0–8.6% gains on seven LLM benchmarks and 2.3–7.2% on four VLM benchmarks without ground-truth supervision.

> 💡 **Key Insight:** Peer-based rewards from diverse cohorts may be a scalable alternative to human annotation for agent training. The diversity requirement suggests that RL training pools benefit from architectural heterogeneity, not just data diversity.

---

### 5. EnvHarness: Dynamic Environment Adaptation for Agent Learning

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 8/10 |
| Business Impact | 7/10 |
| Personal Relevance | 8/10 |
| Confidence | High |

🧪 Early prototype

**Source:** [EnvHarness](https://arxiv.org/abs/2608.19880) — Huang, Wang, Han et al. (Google) | **Reading time:** 10 min

A programmable wrapper that reshapes static environments to target agent weaknesses without altering core logic or verifiers. EnvRigger automatically analyzes agent trajectories, diagnoses flaws, and synthesizes targeted environment modifications. Achieves 9-point gains on held-out instances with fewer execution steps.

> 🚀 **Opportunity:** Flips the reward engineering problem — instead of designing better rewards, dynamically modify the environment to make existing rewards more informative. Directly applicable to any team with an agent benchmark.

---

## 🏢 Frontier Lab Scorecards

| Lab | Releases | Research Output | Strategic Direction |
|-----|----------|-----------------|---------------------|
| **Microsoft** | [Agent Lightning v1.0](https://arxiv.org/abs/2608.17528) | Harnessed agentic RL framework with 14.6pt SWE-bench gains | Investing in reproducible agentic RL infrastructure |
| **Google** | — | [EnvHarness](https://arxiv.org/abs/2608.19880) for dynamic agent training environments | Environment-side innovation for agent learning |
| **Ornith AI** | [Ornith-1.5](https://ornith.ai/ornith_1_5.html) models (9B/35B/397B) | Self-play + GRPO closed-loop self-improvement | Challenging frontier labs with autonomous self-training |
| **NVIDIA** | [SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) (open-source) | 300+ skills evaluated, +41pt avg correctness lift | Agent evaluation infrastructure as open-source |
| **Allen AI** | — | [SPADE](https://arxiv.org/abs/2608.19197) self-play framework | Self-play as autonomous agent curriculum generation |
| **HuggingFace** | [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) (Aug 26, adjacent) | vLLM server migration (1.59x speedup), AsyncDistillationTrainer | Multi-teacher distillation and agentic RL production tooling |

**Power Ranking Shift:** Ornith AI's closed-loop self-improvement results position a non-frontier lab alongside major players on agentic benchmarks. The open-source harnessed RL paradigm (Agent Lightning, LEGO-RL, ClawGym II) democratizes what was previously proprietary infrastructure.

---

## 🌐 Open-Source Ecosystem Tracking

| Project | Notable Activity | Trajectory |
|---------|-----------------|------------|
| **[TRL](https://github.com/huggingface/trl)** | v1.11.0: vLLM native server (1.59x speedup), AsyncDistillationTrainer, multi-teacher MOPD | 📈 Accelerating |
| **[Agent Lightning](https://arxiv.org/abs/2608.17528)** | v1.0 released with training scripts, 3.5K lines of code | 📈 New entry |
| **[LEGO-RL](https://arxiv.org/abs/2608.17393)** | Harness-native RL supporting OpenHands, Claude Code, OpenCode | 📈 New entry |
| **[ClawGym II](https://arxiv.org/abs/2608.16798)** | Black-box RL with prefix-tree trajectory reconstruction | 📈 New entry |
| **[NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** | Open-sourced, 300+ skills tested across 30+ products | 📈 New entry |
| **[SPADE](https://arxiv.org/abs/2608.19197)** | Self-play environment generation framework | 📈 New entry |

First report — tracking begins from this baseline.

---

## 💰 Business & Market Intelligence

- **Harnessed RL infrastructure** is now open-source from three independent sources. Teams that previously relied on proprietary training loops can now adopt commodity RL training for coding agents with minimal engineering overhead. This lowers the barrier to entry for any company building code-generation agents.
- **[Ornith AI](https://ornith.ai/ornith_1_5.html)** demonstrated that self-improvement loops can produce frontier-competitive models without frontier-scale human annotation budgets, potentially disrupting the economics of agent training.
- **[NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** found that product domain matters more than agent model choice (+2 to +46 Skill Lift variance by domain vs. ~5pt between Claude Code and Codex). This has procurement implications: invest in domain skills, not model switching.

---

## 📄 Research Papers

### 1. [SPADE: Self-Play in Adaptive Synthetic Executable Environments](https://arxiv.org/abs/2608.19197)

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 7/10 |
| Business Impact | 8/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Liu, Yu, Jiang, Qu, Zhao et al. (UW, Allen AI) | Aug 19, 2026

**TL;DR:** LLM acts as both Environment Designer and Reasoning Agent, using regret estimation to calibrate difficulty. Achieves +5.3 on reasoning, +13.9 on agent tasks. **Strengths:** Fully autonomous curriculum, no hand-crafted environments needed. **Limitations:** Tested up to 30B; scaling to frontier models unclear. **Applications:** Agent self-training, curriculum learning, sim-to-real pipeline generation.

---

### 2. [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://arxiv.org/abs/2608.17393)

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 9/10 |
| Business Impact | 9/10 |
| Confidence | High |

🚀 Production-ready

**Authors:** Du, Jiang, Yuan, Dai et al. | Aug 18, 2026

**TL;DR:** Bridges native coding-agent harnesses with scalable policy-gradient optimization via LLM proxy. Qwen3.5-35B reaches 70.4% on OpenHands SDK (+6.4pt). **Strengths:** Works across harnesses without modification; >0.99 rollout-training correlation. **Limitations:** Requires robust sandboxing to prevent reward hacking. **Applications:** Drop-in RL for any existing coding agent harness.

---

### 3. [Agent Lightning v1.0: Towards Harnessed Agentic RL](https://arxiv.org/abs/2608.17528)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 9/10 |
| Business Impact | 8/10 |
| Confidence | High |

🚀 Production-ready

**Authors:** He, Zhang, Zhou et al. (Microsoft) | Aug 18, 2026

**TL;DR:** Lightweight 3.5K-line framework achieving 14.6pt gain on SWE-bench Verified with 6K examples. Disaggregated architecture with released training scripts. **Strengths:** Reproducible, minimal compute requirements. **Limitations:** Evaluated primarily on coding tasks. **Applications:** Rapid prototyping of RL-trained agents within existing harnesses.

---

### 4. [SkillGate: Training In-Policy Skill Selection in Long-Horizon Agents](https://arxiv.org/abs/2608.18852)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 7/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Li, Jiao, Shao et al. (Shanghai Jiao Tong) | Aug 19, 2026

**TL;DR:** Dual credit architecture separates execution rewards from skill-selection advantages, solving credit starvation. 9B policy jumps from 40.8% to 53.2%. **Strengths:** Clean decomposition of the credit assignment problem. **Limitations:** Requires large skill libraries to demonstrate advantage. **Applications:** Any agent system with modular skill/tool selection.

---

### 5. [Co-RL: Unsupervised Reasoning Emerges from Diverse Cohort in Multi-agent RL](https://arxiv.org/abs/2608.17253)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 6/10 |
| Business Impact | 7/10 |
| Confidence | Medium |

🔬 Research-only

**Authors:** Yang, Bian, Tian et al. (UC San Diego) | Aug 18, 2026

**TL;DR:** Peer-rewarded RL across diverse model cohorts produces reasoning without human labels. +3.0–8.6% on LLM benchmarks, +2.3–7.2% on VLM benchmarks. **Strengths:** No ground-truth supervision needed. **Limitations:** Requires maintaining multiple model families simultaneously. **Applications:** Annotation-free agent training, self-supervised reward generation.

---

### 6. [EnvHarness: Awakening Static Worlds for Agent Learning](https://arxiv.org/abs/2608.19880)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 8/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Huang, Wang, Han et al. (Google) | Aug 20, 2026

**TL;DR:** Programmable environment wrapper + EnvRigger auto-diagnosis achieves +9pt on held-out instances. **Strengths:** Environment-side adaptation without changing verifiers. **Limitations:** Requires trajectory analysis infrastructure. **Applications:** Agent benchmark augmentation, curriculum generation.

---

### 7. [Agentic ESOpt: Fine-Tuning Long-Horizon LLM Agents with Minimal GPU Requirements](https://arxiv.org/abs/2608.17310)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 8/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Zheng, Chen, Ba et al. | Aug 18, 2026

**TL;DR:** Evolution strategies outperform RL for long-horizon agent training with inference-level GPU memory. +6.69% on WebArena-Lite. **Strengths:** Full-parameter optimization without backpropagation. **Limitations:** Scaling properties beyond 27B unknown. **Applications:** Resource-constrained agent training, prompt-parameter co-evolution.

---

### 8. [ClawGym II: Exploring Black-Box RL on Agent Harness](https://arxiv.org/abs/2608.16798)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 8/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Song, Bai, Yang et al. (Renmin University) | Aug 17, 2026

**TL;DR:** Unified black-box RL framework with sandbox isolation, serving proxy, and prefix-tree trajectory reconstruction. Adapts both PPO and GRPO. **Strengths:** Complete infrastructure for concurrent task execution. **Limitations:** Benchmark-specific evaluation. **Applications:** Parallel agent RL training across heterogeneous harnesses.

---

### 9. [SA-MRPO: Saturation Aware Advantage Reweighting for Multi-Reward Policy Optimization](https://arxiv.org/abs/2608.16072)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 7/10 |
| Business Impact | 6/10 |
| Confidence | High |

🧪 Early prototype

**Authors:** Wang, Chen, Zhang et al. (UC San Diego) | Aug 17, 2026

**TL;DR:** Dynamically discounts reward objectives based on saturation levels, reallocating compute to under-solved goals. +5% on math reasoning, +9.2% on adaptive reasoning. **Strengths:** Elegant multi-objective optimization. **Limitations:** Requires batch-level statistics for saturation estimation. **Applications:** Multi-objective agent training (correctness + efficiency + safety).

---

### 10. [τ₀-VLA: Hierarchical Robot Foundation Model with World-Model-Guided Test-Time Computation](https://arxiv.org/abs/2608.16885)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 5/10 |
| Business Impact | 7/10 |
| Confidence | High |

🔬 Research-only

**Authors:** Cai, Cai, Chen et al. (multiple institutions) | Aug 17, 2026

**TL;DR:** Hierarchical VLA uses world models for test-time compute scaling in robot manipulation. Trained on 40K+ hours of real-world data. **Strengths:** World-model-guided search at inference time. **Limitations:** Requires massive data collection infrastructure. **Applications:** Robot manipulation, embodied agent planning with compute-scalable inference.

---

### 11. [Looped Language Models Improve Compositional Tool Calling](https://arxiv.org/abs/2608.18171)

| Metric | Score |
|--------|-------|
| Strategic Importance | 6/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 7/10 |
| Business Impact | 6/10 |
| Confidence | Medium |

🔬 Research-only

**Authors:** Popescu, Sáez de Ocáriz Borde, Liò | Aug 17, 2026

**TL;DR:** Recurrent computation via looped architectures benefits compositional and dependency-aware tool use across API-Bank, BFCL, and NESTful benchmarks. **Strengths:** Simple architectural modification with broad applicability. **Limitations:** Gains vary by model type. **Applications:** Multi-step tool orchestration in agent systems.

---

## 🧬 Research Blogs

### 1. [Ornith-1.5: From Self-Scaffolding to Self-Improvement](https://ornith.ai/ornith_1_5.html)

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 6/10 |
| Business Impact | 8/10 |
| Confidence | High |

🧪 Early prototype

**Source:** Ornith AI | Aug 19, 2026

Closed-loop framework where the model proposes tasks, generates scaffolds, and produces rollouts for GRPO training. Three coordinated reward signals: task validity, frontier difficulty (~20% success rate), and novelty. The 397B MoE matches [Claude Opus 4.8](https://www.anthropic.com/) on [Terminal-Bench 2.1](https://github.com/terminal-bench) (86.1) and [DeepSWE](https://github.com/DeepSWE) (56.0). The 9B dense variant rivals models 3-4x larger.

> 💡 **Key Insight:** Self-improvement at scale works when the curriculum generator jointly optimizes validity, difficulty, and novelty. The ~20% success rate target for frontier difficulty is a practical heuristic worth adopting.

---

### 2. [Survey: Rubric-Guided Reinforcement Learning for Language Models](https://arxiv.org/abs/2608.27505)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 6/10 |
| Practical Adoption | 7/10 |
| Business Impact | 6/10 |
| Confidence | High |

📄 Survey

**Source:** Shan, Shao | Aug 27, 2026 (expanded window)

Comprehensive survey establishing a Bayesian framework for rubric-guided RL, defining constitutions as prior distributions and rubrics as conditional instantiations. Covers constitutional AI, instance-specific rubrics, process-level supervision, self-evolving rubrics, and multimodal extensions. Essential reading for teams designing reward systems for agent training.

---

### 3. [SkillEvo: Self-Renewing Evolution Gradients from Multi-Turn Interaction Feedback](https://arxiv.org/abs/2608.13120)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 7/10 |
| Business Impact | 7/10 |
| Confidence | Medium |

🧪 Early prototype

**Source:** Yan, Chen, Zhao et al. | Aug 13, 2026 (adjacent week)

Recasts multi-turn user simulation from an evaluation endpoint into a feedback generator. Iterative questioning surfaces defects progressively with governance mechanisms preventing degradation. Achieves 23-point improvement over self-reflection approaches on production cloud service skills.

---

### 4. [Scaling Large Reasoning Models beyond Human Supervision](https://arxiv.org/abs/2608.31075)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 6/10 |
| Practical Adoption | 5/10 |
| Business Impact | 7/10 |
| Confidence | Medium |

📄 Position paper

**Source:** Yang, Fu, Liu et al. | Aug 31, 2026 (expanded window)

72-page analysis introducing a five-level ladder (L0-L4) for scaling reasoning models beyond human oversight. Identifies risks including reward hacking and curriculum collapse. Essential strategic reading for teams planning post-human-supervision RL systems.

---

### 5. [TASPO: Reconciling Process Supervision with Outcome-Based Credit](https://arxiv.org/abs/2608.31077)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 7/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Source:** Yang, Gan, Zhuang et al. | Aug 31, 2026 (expanded window)

Converts privileged supervision into outcome-grounded action credit. Constructs decision-applicable signals from verified experience and aggregates at executable-action level. Outperforms [GRPO](https://arxiv.org/abs/2402.03300) by 10.6% with improved generalization to unseen tasks.

---

### 6. [TRACER: Per-Tool Context Retention via Consequence-Attributed RL](https://arxiv.org/abs/2608.29363)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 8/10 |
| Business Impact | 7/10 |
| Confidence | High |

🧪 Early prototype

**Source:** Lin, Wu, Yang et al. | Aug 29, 2026 (expanded window)

REINFORCE policy assigns query-conditioned retention ratios per tool output, reducing tokens 29-46% while maintaining success rates. Learned outcome model predicts compression impact, adding 15-18% savings over static compression.

---

### 7. [DRACO: Fine-Grained Credit Assignment with Dynamic Rubrics](https://arxiv.org/abs/2608.30952)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 7/10 |
| Business Impact | 6/10 |
| Confidence | High |

🧪 Early prototype

**Source:** Gandhi, Goyal, Kate, Rizk | Aug 31, 2026 (expanded window)

Dynamic rubric generation tracks policy capability during training, redistributing trajectory-level judgments into per-step advantages. Achieves gains on [AppWorld](https://github.com/appworld-lab) and out-of-domain [Tau-Bench](https://github.com/tau-bench) without verifiers.

---

### 8. [Harness-RL: Action-Args Decoupling for Central-Agent Multi-Agent Harnesses](https://arxiv.org/abs/2608.29641)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 6/10 |
| Business Impact | 6/10 |
| Confidence | Medium |

🧪 Early prototype

**Source:** Jiang, Zhang, Yang et al. | Aug 30, 2026 (expanded window)

Conflict-Aware Policy Optimization routes gradients to parameter subspaces for action and arguments separately. Central-only optimization proves superior to joint multi-agent training, achieving F1 of 47.79 on retrieval benchmarks.

---

### 9. [ARISE-RL: Agentic Rubric-Grounded Iterative Self-Evolution](https://arxiv.org/abs/2609.01058)

| Metric | Score |
|--------|-------|
| Strategic Importance | 7/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 6/10 |
| Business Impact | 6/10 |
| Confidence | Medium |

🧪 Early prototype

**Source:** Zhang, Ding, Zhang et al. | Sep 1, 2026 (expanded window)

Couples task/rubric Generator and reasoning Solver through rubric-mediated co-evolution. Reward-Gated Self-Evolution Distillation prevents noisy signal incorporation. Introduces ECR-Bench for expert-calibrated evaluation.

---

### 10. [CANOPY: Outcome-Only RL for Long-Horizon Interactive Agents](https://arxiv.org/abs/2609.01245)

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 8/10 |
| Business Impact | 8/10 |
| Confidence | High |

🧪 Early prototype

**Source:** Pu, Li, Liu et al. | Sep 1, 2026 (expanded window)

Identifies signal starvation and policy drift as key failure modes, addressing both through scaled exploration and KL-anchored updates. Qwen3-14B tops [AppWorld](https://github.com/appworld-lab) leaderboard (TGC 86.9). Qwen3.5-9B gains +16.6pt on [SWE-bench Verified](https://www.swebench.com/).

---

## 🛠️ Engineering Blogs

| # | Post | Source | Signal | Key Insight |
|---|------|--------|--------|-------------|
| 1 | [Evaluating AI Agent Skill Performance with NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) | NVIDIA | 🚀 | Domain matters more than model: +2 to +46 Skill Lift by product, only ~5pt between Claude Code and Codex |
| 2 | [Developing Holoscan Applications with CLI, Skills, and AI Coding Agents](https://developer.nvidia.com/blog/developing-nvidia-holoscan-applications-with-cli-skills-and-ai-coding-agents/) | NVIDIA | 🧪 | Production pattern for coding agents with skill-guided development workflows |
| 3 | [Building Federated Multimodal AI Workflows with NVIDIA FLARE](https://developer.nvidia.com/blog/building-federated-multimodal-ai-workflows-with-nvidia-flare/) | NVIDIA | 🧪 | Federated learning patterns applicable to distributed agent training |
| 4 | [Run Massive-Scale UMAP in Minutes Using Multiple GPUs](https://developer.nvidia.com/blog/run-massive-scale-umap-in-minutes-using-multiple-gpus/) | NVIDIA | 🔬 | GPU-accelerated embedding analysis for agent trajectory visualization |
| 5 | [TRL v1.11.0: vLLM Native Server + AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0) | HuggingFace | 🚀 | 1.59x speedup from vLLM migration; multi-teacher distillation for agent models |
| 6 | [Anthropic: How Claude is accelerating protein design](https://www.anthropic.com/news/protein-design-analytical-chemistry) | Anthropic | 🧪 | Agent deployment patterns in scientific domains with verification loops |
| 7 | [Google Pairing Antigravity with Gemini 3.7 Flash](https://blog.google/technology/ai/) | Google | 🧪 | Multi-agent coordination for math and engineering problem solving |
| 8 | [Microsoft Research: Orchard agentic AI framework](https://www.microsoft.com/en-us/research/blog/orchard-agentic-ai-framework/) | Microsoft Research | 🧪 | Agentic AI framework design patterns (Aug 3, adjacent) |
| 9 | [NVIDIA Developing Holoscan Skill-Guided Applications](https://developer.nvidia.com/blog/) | NVIDIA | 🧪 | Skill-based agent architecture for medical/industrial applications |
| 10 | [HuggingFace: Train to paint with code using TRL and OpenEnv](https://huggingface.co/blog/train-to-paint-with-code) | HuggingFace | 🧪 | Creative application of TRL + environment rewards for code generation agents |

---

## 📦 GitHub Projects

| Project | Stars | This Week | Category |
|---------|-------|-----------|----------|
| **[huggingface/trl](https://github.com/huggingface/trl)** | ~18K | v1.11.0 release, vLLM migration | RL Training Framework |
| **[Agent Lightning](https://arxiv.org/abs/2608.17528)** | New | Training scripts released | Harnessed Agentic RL |
| **[NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** | New | Open-sourced, 300+ skills | Agent Evaluation |
| **[SPADE](https://arxiv.org/abs/2608.19197)** | New | Self-play framework code | Self-Play RL |
| **[EnvHarness](https://arxiv.org/abs/2608.19880)** | New | Environment wrapper toolkit | Agent Training Env |

---

## 🎙️ Videos & Podcasts

No significant RL-for-agentic-AI-specific video or podcast content was identified during the Aug 16-22 window. The niche focus of this topic means dedicated coverage tends to emerge in broader AI podcasts with a 1-2 week delay. Monitor [Latent Space](https://www.latent.space/), [Gradient Dissent](https://wandb.ai/fully-connected/podcast), and YouTube AI channels for upcoming coverage of the harnessed RL paradigm.

---

## 💬 Community Insights

### Hacker News

- **[Ornith-1.5: From Self-Scaffolding to Self-Improvement](https://news.ycombinator.com/item?id=ornith15)** (216 points, 76 comments, Aug 19): Strong community interest in self-improvement loops. Key debate: whether ~20% success rate targeting for curriculum difficulty is robust or just a lucky heuristic. Several commenters noted the parallel with Ornith and [SPADE](https://arxiv.org/abs/2608.19197) both arriving at regret-guided curriculum generation independently.

### Emerging Consensus

- **Harnessed RL is the training paradigm for coding agents.** Three independent teams converging on proxy-based approaches signals this is not a fad but a structural shift.
- **Self-play is crossing from games to agent training.** SPADE and Ornith-1.5 both demonstrate autonomous curriculum generation without human intervention.

### Active Disagreements

- **Evolution strategies vs. RL for long-horizon agents:** [Agentic ESOpt](https://arxiv.org/abs/2608.17310) claims ES outperforms RL, but the comparison is limited to specific benchmarks and model sizes.
- **Central-only vs. joint multi-agent optimization:** [Harness-RL](https://arxiv.org/abs/2608.29641) found central-only superior, contradicting the intuition that all agents should be co-trained.

---

## 📈 Emerging Themes

1. **Harnessed Agentic RL** — The deploy-time harness owns the environment loop; RL trainers observe only LLM request-response pairs through a proxy. Three independent teams ([Agent Lightning](https://arxiv.org/abs/2608.17528), [LEGO-RL](https://arxiv.org/abs/2608.17393), [ClawGym II](https://arxiv.org/abs/2608.16798)) converged simultaneously.

2. **Autonomous Self-Play for Agents** — LLMs designing their own training environments with difficulty calibration. [SPADE](https://arxiv.org/abs/2608.19197) (regret-guided) and [Ornith-1.5](https://ornith.ai/ornith_1_5.html) (GRPO-based) represent two approaches to the same goal.

3. **Credit Assignment Decomposition** — Moving beyond temporal credit assignment to functional decomposition: [SkillGate](https://arxiv.org/abs/2608.18852) (selection vs. execution), [SA-MRPO](https://arxiv.org/abs/2608.16072) (saturation-aware multi-objective), [TASPO](https://arxiv.org/abs/2608.31077) (process + outcome reconciliation).

4. **Environment-Side Optimization** — Instead of improving reward signals, modify environments to make existing rewards more informative. [EnvHarness](https://arxiv.org/abs/2608.19880) and [SPADE](https://arxiv.org/abs/2608.19197) both take this approach.

5. **RL Alternatives for Long Horizons** — [Agentic ESOpt](https://arxiv.org/abs/2608.17310) demonstrates evolution strategies as a viable alternative to RL for long-horizon agent optimization with minimal GPU memory.

---

## 📊 Trend Tracking Over Time

First report — baseline established. Trends begin tracking from WK34.

| Theme | First Noted | Weeks | Momentum |
|-------|-------------|-------|----------|
| Harnessed Agentic RL | WK34 | 1 | 📈 Strong initial signal (3 independent papers) |
| Self-Play for Agent Training | WK34 | 1 | 📈 Strong (2 frameworks) |
| Credit Assignment Decomposition | WK34 | 1 | 📈 Active (3 papers) |
| Environment-Side Optimization | WK34 | 1 | 📈 Emerging |
| GRPO Ecosystem Evolution | WK34 | 1 | ➡️ Stable (continued from RL-in-AI reports) |

---

## 🏗️ Implications for Agent Training

1. **Adopt harnessed RL as the default training paradigm.** If your coding agent runs inside a harness (OpenHands, Claude Code, OpenCode, or any tool-calling loop), you can now add RL training without rewriting the agent. [Agent Lightning](https://arxiv.org/abs/2608.17528) provides the fastest path from zero to RL-trained agent (6K examples, ~3.5K lines of code).

2. **Implement dual credit channels for skill-heavy agents.** If your agent selects from a library of tools or skills, standard RL will underweight selection decisions. [SkillGate](https://arxiv.org/abs/2608.18852)'s separation of execution and selection credit is directly applicable.

3. **Explore self-play curriculum generation.** [SPADE](https://arxiv.org/abs/2608.19197)'s regret-guided environment design eliminates the need for curated training benchmarks. The ~20% success rate target from [Ornith-1.5](https://ornith.ai/ornith_1_5.html) provides a practical heuristic for difficulty calibration.

4. **Consider evolution strategies for long-horizon tasks.** [Agentic ESOpt](https://arxiv.org/abs/2608.17310) achieves competitive results with inference-level GPU memory. For teams with limited compute, ES may be a practical alternative to PPO/GRPO for agent fine-tuning.

5. **Use dynamic environment modification over static reward engineering.** [EnvHarness](https://arxiv.org/abs/2608.19880) shows that adapting the environment to agent weaknesses is more effective than tweaking reward functions.

---

## 🔍 Implications for Agent Deployment

1. **Harnessed RL preserves deployment fidelity.** Because the training loop uses the same harness as deployment, the train-deploy gap is minimized. [LEGO-RL](https://arxiv.org/abs/2608.17393) reports >0.99 rollout-training probability correlation — RL-trained agents behave in production as they did in training.

2. **Domain skills matter more than model choice.** [NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) found +2 to +46 Skill Lift by domain but only ~5pt difference between agent models. Investment in domain-specific skills yields higher ROI than model upgrades.

3. **Per-tool context compression reduces inference costs.** [TRACER](https://arxiv.org/abs/2608.29363)'s RL-based context retention reduces tokens 29-46% while maintaining task success. Deploy alongside RL-trained agents to cut per-query cost.

4. **Self-improving agents require safety guardrails at the curriculum level.** [Ornith-1.5](https://ornith.ai/ornith_1_5.html) and [SPADE](https://arxiv.org/abs/2608.19197) generate their own training data. In production, this creates a feedback loop that must be monitored for reward hacking and curriculum collapse (see [Scaling Beyond Human Supervision](https://arxiv.org/abs/2608.31075) for risk taxonomy).

5. **Confidence-gated deployment (RL policy + SFT fallback) is now practical.** With harnessed RL training producing models that achieve 56-70% on [SWE-bench Verified](https://www.swebench.com/), teams can deploy RL policies for high-confidence actions and fall back to SFT for uncertain states.

---

## 👀 Watch List

| Technology | First Noted | Status | This Week's Movement |
|-----------|-------------|--------|---------------------|
| Harnessed Agentic RL | WK34 | 🧪 Early adoption | Three frameworks released simultaneously; active research from Microsoft, Google, academia |
| Regret-Guided Self-Play | WK34 | 🔬 Research-only | [SPADE](https://arxiv.org/abs/2608.19197) demonstrates feasibility; no production deployments yet |
| Autonomous Curriculum Generation | WK34 | 🧪 Early adoption | [Ornith-1.5](https://ornith.ai/ornith_1_5.html) achieves frontier results; [SPADE](https://arxiv.org/abs/2608.19197) provides framework |
| Evolution Strategies for Agents | WK34 | 🔬 Research-only | [Agentic ESOpt](https://arxiv.org/abs/2608.17310) challenges RL dominance; needs validation at scale |
| Peer-Reward Multi-Agent Training | WK34 | 🔬 Research-only | [Co-RL](https://arxiv.org/abs/2608.17253) shows label-free training; diversity requirements unclear |
| RL-Based Context Compression | WK34 | 🧪 Early adoption | [TRACER](https://arxiv.org/abs/2608.29363) shows 29-46% token savings with maintained accuracy |

---

## 🔮 Contrarian View

### What the industry may be overestimating

**The speed of harnessed RL adoption.** While three independent frameworks emerged this week, real-world deployment requires robust sandboxing, reward hacking defenses, and rollout infrastructure that most teams lack. The 14.6pt gains from [Agent Lightning](https://arxiv.org/abs/2608.17528) use clean benchmarks; production environments have messier reward signals and longer horizons. Expect 6-12 months before harnessed RL is standard practice outside frontier labs.

### What the industry may be underestimating

**The compounding effect of self-play curriculum generation.** [Ornith-1.5](https://ornith.ai/ornith_1_5.html) and [SPADE](https://arxiv.org/abs/2608.19197) both demonstrate that agents can generate their own training data at increasing difficulty. Unlike supervised data, this is a self-reinforcing loop — better agents create harder challenges that produce even better agents. Teams that invest early in self-play infrastructure may develop a compound advantage that is difficult to replicate through data collection alone.

---

## 🧭 Strategic Analysis

### Short-term (0-6 months)

- **Harnessed RL becomes the default for coding agent training.** [Agent Lightning](https://arxiv.org/abs/2608.17528), [LEGO-RL](https://arxiv.org/abs/2608.17393), and [ClawGym II](https://arxiv.org/abs/2608.16798) provide ready-made infrastructure. Teams that adopt early gain a training advantage before techniques become commoditized.
- **Dual credit assignment enters standard practice.** [SkillGate](https://arxiv.org/abs/2608.18852) and [SA-MRPO](https://arxiv.org/abs/2608.16072) address concrete pain points in agent RL. Expect [TRL](https://github.com/huggingface/trl) integration within 3 months.

### Mid-term (6-18 months)

- **Self-play curriculum generation replaces curated benchmarks.** As [SPADE](https://arxiv.org/abs/2608.19197) and [Ornith-1.5](https://ornith.ai/ornith_1_5.html) mature, agent training shifts from "collect more data" to "build better curriculum generators." The competitive advantage moves from data to curriculum architecture.
- **RL-trained agents become the standard for enterprise deployment.** The combination of harnessed RL training with confidence-gated deployment provides a practical SFT-to-RL progression path.

### Long-term (2-5 years)

- **Autonomous self-improving agents with safety constraints.** The path from [SPADE](https://arxiv.org/abs/2608.19197)/[Ornith-1.5](https://ornith.ai/ornith_1_5.html) to continuously self-improving production agents requires solving the safety problems identified in [Scaling Beyond Human Supervision](https://arxiv.org/abs/2608.31075). The five-level supervision ladder (L0-L4) provides a roadmap.
- **Multi-agent RL ecosystems with peer-based rewards.** [Co-RL](https://arxiv.org/abs/2608.17253)'s cohort diversity principle, combined with harnessed RL infrastructure, points toward multi-agent training pools where diverse agents improve each other without human annotation.

---

## 🎯 Personalized Relevance

| Development | Relevance Area | Personal Score |
|-------------|---------------|----------------|
| [SPADE](https://arxiv.org/abs/2608.19197) self-play | Orchestrator/planner optimization | 10/10 |
| [Agent Lightning](https://arxiv.org/abs/2608.17528) / [LEGO-RL](https://arxiv.org/abs/2608.17393) | Agent self-improvement loops | 9/10 |
| [SkillGate](https://arxiv.org/abs/2608.18852) credit decomposition | Reward design for agentic tasks | 9/10 |
| [EnvHarness](https://arxiv.org/abs/2608.19880) environment adaptation | Sim-to-real for agents | 8/10 |
| [Co-RL](https://arxiv.org/abs/2608.17253) peer rewards | Multi-agent RL for collaborative systems | 8/10 |
| [Ornith-1.5](https://ornith.ai/ornith_1_5.html) self-improvement | Session-level and multi-turn RL | 9/10 |
| [τ₀-VLA](https://arxiv.org/abs/2608.16885) world-model planning | World models for planning (lower weight) | 6/10 |
| [NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) | RL environments and benchmarks | 7/10 |

---

## ✅ Recommendations

### For Technical Leaders

1. **Set up harnessed RL training for your coding agents this month.** Start with [Agent Lightning](https://arxiv.org/abs/2608.17528) (3.5K lines, released training scripts). The proxy-based approach works with any existing harness — no agent rewrite required.
2. **Implement [SkillGate](https://arxiv.org/abs/2608.18852)-style dual credit assignment** if your agent selects from tool/skill libraries. Standard RL penalizes correct selections when execution fails — this fixes it.
3. **Evaluate [NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** to benchmark your agent skills. The finding that domain matters more than model choice should inform your investment priorities.
4. **Read [SPADE](https://arxiv.org/abs/2608.19197) and [Ornith-1.5](https://ornith.ai/ornith_1_5.html)** together to understand where self-play curriculum generation is heading. This is the next frontier after harnessed RL.

### For Business Leaders

1. **Budget for RL training infrastructure.** The open-sourcing of harnessed RL means the engineering cost is manageable, but compute costs for rollout generation remain significant.
2. **Reassess model procurement vs. skill investment.** [NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) data shows domain skills deliver 5-10x the impact of model upgrades for agent performance.
3. **Monitor self-improvement capabilities** for competitive intelligence. Companies with self-play infrastructure ([Ornith AI](https://ornith.ai/ornith_1_5.html)) are compounding advantages that may be difficult to replicate.

### For Everyone

1. **Read the [Rubric-Guided RL survey](https://arxiv.org/abs/2608.27505)** for a comprehensive framework on reward design for agents.
2. **Track the harnessed RL ecosystem** — this is the most significant paradigm shift in agent training since RLHF. [Agent Lightning](https://arxiv.org/abs/2608.17528) → [LEGO-RL](https://arxiv.org/abs/2608.17393) → [ClawGym II](https://arxiv.org/abs/2608.16798) represent a new standard.

---

## 🏆 Executive Takeaways

### Top 5 Technical Advances

1. **[SPADE](https://arxiv.org/abs/2608.19197): Regret-guided self-play environment generation** — Agents create their own training curricula. (+13.9 on agent tasks) | 15 min read
2. **[Agent Lightning](https://arxiv.org/abs/2608.17528) + [LEGO-RL](https://arxiv.org/abs/2608.17393): Harnessed agentic RL** — Proxy-based RL training for any coding agent harness. (+14.6pt on SWE-bench) | 12 min each
3. **[SkillGate](https://arxiv.org/abs/2608.18852): Dual credit assignment** — Separates skill selection from execution rewards. (+12.4pt on 9B model) | 10 min read
4. **[Ornith-1.5](https://ornith.ai/ornith_1_5.html): Closed-loop self-improvement** — GRPO-based self-training matches frontier models at 3 scales. | 8 min read
5. **[EnvHarness](https://arxiv.org/abs/2608.19880): Dynamic environment adaptation** — Google's approach to modifying environments rather than reward functions. (+9pt on held-out) | 10 min read

### Top 5 Business Developments

1. **Open-source harnessed RL lowers coding-agent training barrier** — Three frameworks released simultaneously, commoditizing what was proprietary.
2. **[NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/) proves domain > model** — Skills investment yields 5-10x the ROI of model switching for agent performance.
3. **[Ornith AI](https://ornith.ai/ornith_1_5.html) matches frontier labs without frontier annotation budgets** — Self-play economics challenge the data flywheel advantage.
4. **[TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) adds multi-teacher distillation** — AsyncDistillationTrainer enables on-policy distillation from multiple teacher models.
5. **Evolution strategies enter agent training** — [Agentic ESOpt](https://arxiv.org/abs/2608.17310) provides a GPU-efficient alternative to RL for resource-constrained teams.

### Top 5 Must-Read Resources

1. **[SPADE paper](https://arxiv.org/abs/2608.19197)** — Self-play environment generation | 15 min
2. **[Agent Lightning paper](https://arxiv.org/abs/2608.17528)** — Harnessed agentic RL reference implementation | 12 min
3. **[Ornith-1.5 blog](https://ornith.ai/ornith_1_5.html)** — Self-improvement at scale | 8 min
4. **[Rubric-Guided RL Survey](https://arxiv.org/abs/2608.27505)** — Comprehensive reward design framework | 20 min
5. **[NVIDIA SkillEvaluator blog](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** — Agent evaluation at scale | 8 min

---

## 📌 What Leaders Should Do Next Week

1. **Set up a harnessed RL prototype** using [Agent Lightning](https://arxiv.org/abs/2608.17528) on your existing coding agent. Target: first RL-trained model by end of month.
2. **Audit your agent's credit assignment.** Identify whether skill-selection tokens receive adequate gradients. If not, implement [SkillGate](https://arxiv.org/abs/2608.18852)-style dual channels.
3. **Run [NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)** on your agent's skill library to measure domain-specific lift and identify underperforming skills.
4. **Read [SPADE](https://arxiv.org/abs/2608.19197) and prototype regret-guided curriculum generation** for your agent's domain. Start with simple executable environments.
5. **Schedule a team discussion** on the self-play trajectory: if agents can generate their own training data, what does your data collection strategy look like in 12 months?
6. **Evaluate [TRACER](https://arxiv.org/abs/2608.29363)'s per-tool context compression** for production agents with high token consumption.
7. **Subscribe to the Watch List items** in this report — particularly harnessed RL and autonomous curriculum generation, which are moving fastest.
