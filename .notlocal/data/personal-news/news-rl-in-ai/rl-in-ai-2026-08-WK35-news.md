# RL for LLM Training Weekly Briefing (Week 35)
**Week 35 | August 23–29, 2026**
⏱️ 18 min read

---

## 📋 Executive Briefing

Infrastructure consolidation dominated WK35. [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) and [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) shipped on the same day (August 26), creating the tightest RL training stack yet: TRL now delegates entirely to vLLM's native server (1,218 to ~130 lines, 1.44--1.59x speedup), while vLLM added first-class RL lifecycle gRPC endpoints and sparse NCCL weight-transfer primitives. The new [AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0) in TRL supports multi-teacher on-policy distillation (MOPD), arriving just as an explosion of OPD research validated the paradigm.

On-policy distillation (OPD) went from "promising alternative" to "dominant research theme" in a single week. Six independent papers attacked different OPD failure modes: [RA-OPD](https://arxiv.org/abs/2608.27960) filters teacher-reward misalignment, [OPDVR](https://arxiv.org/abs/2608.24696) fuses OPD with verifiable rewards via ReLU gating, [Open-MOPD](https://arxiv.org/abs/2608.19098) recovers 83.4% of multi-teacher headroom (up from 35.6%), and a [critical review](https://arxiv.org/abs/2608.25936) systematized collapse modes. Combined with WK34's [SimpleOPD](https://arxiv.org/abs/2608.14277) breakthrough, OPD is now the most active subfield in RL post-training research.

[TailSFT](https://arxiv.org/abs/2608.25756) from Malladi et al. demonstrated that filtered SFT -- concentrating learning on under-modeled tail regions -- yields up to 4% absolute pass@1 gains in subsequent GRPO runs. This establishes that pre-RL SFT quality compounds downstream, a finding that should reshape how teams sequence their post-training pipelines.

Credit assignment continued its rapid advance with [VICT](https://arxiv.org/abs/2608.28128) (EMNLP 2026), which traces credit through verifier internals rather than learning separate critics, and [FARCA](https://arxiv.org/abs/2608.24350), which uses counterfactual evidence attribution for factual grounding. RLVR diversity concerns deepened with ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) showing 67% solution coverage loss concentrated at trajectory entry points.

---

## ⚡ What Changed Since Last Week

- **[TRL v1.11.0 released](https://github.com/huggingface/trl/releases/tag/v1.11.0)** -- vLLM native server (1.44--1.59x speedup), AsyncDistillationTrainer with MOPD, DistillationTrainer tool calling; dropped vLLM 0.18
- **[vLLM v0.28.0 released](https://github.com/vllm-project/vllm/releases/tag/v0.28.0)** -- RL lifecycle gRPC endpoints, sparse NCCL weight updates, 584 commits from 270 contributors
- **[On-policy distillation explosion](https://arxiv.org/abs/2608.27960)** -- six OPD papers in one week: RA-OPD, OPDVR, Open-MOPD, critical review, Beyond Imitation, SecOPD
- **[TailSFT: SFT quality compounds in RL](https://arxiv.org/abs/2608.25756)** -- filtered SFT on tail regions yields +4% pass@1 in subsequent GRPO; stage-aware pipeline design
- **[VICT: Verifier-instrumented credit tracing](https://arxiv.org/abs/2608.28128)** -- EMNLP 2026; credit from verifier internals without learned critics
- **[RLVR narrows at the entrance](https://arxiv.org/abs/2608.29188)** -- 67% coverage loss concentrated at trajectory entry; parameter interpolation recovers 37%
- **[ES achieves broader coverage than GRPO](https://arxiv.org/abs/2608.27351)** -- evolution strategies avoid entropy collapse while matching RL performance
- **[Distributed RL systematized](https://arxiv.org/abs/2608.27046)** -- Besta et al. taxonomy of PPO/GRPO parallelism strategies
- **[Batch size scaling rules for LLM RL](https://arxiv.org/abs/2608.29296)** -- square-root LR scaling with Adam; up to 29% time-to-target improvement
- **[Prime Agent: self-improving RLM harness](https://arxiv.org/abs/2608.23552)** -- Prime Intellect; 95.5% on ARC-AGI-3 RHAE with persistent harness
- **[ERPO: Environmental regularization](https://arxiv.org/abs/2608.23311)** -- EMNLP 2026; Query-KL replaces Policy-KL to preserve exploration

---

## 🔬 Top Technical Developments

### 1. TRL v1.11.0 + vLLM v0.28.0: Infrastructure Consolidation

| Metric | Score |
|--------|-------|
| Strategic Importance | 10/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 10/10 |
| Business Impact | 10/10 |
| Personal Relevance | 10/10 |
| Confidence | High |

🚀 Production-ready

**Sources:** [TRL v1.11.0 release](https://github.com/huggingface/trl/releases/tag/v1.11.0) | [vLLM v0.28.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) | **Reading time:** 10 min (combined)

[TRL](https://github.com/huggingface/trl) v1.11.0 replaces its custom vLLM server with vLLM's native server, shrinking `vllm_serve.py` from 1,218 to ~130 lines. Weight sync now uses vLLM's NCCL engine (single packed broadcast), delivering **1.44--1.59x speedup** on GRPO benchmarks (H100, Qwen2.5). The new [AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0) enables multi-teacher on-policy distillation (MOPD) with `teacher_id` column routing. [DistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0) now supports tool calling. On the same day, [vLLM](https://github.com/vllm-project/vllm) v0.28.0 shipped RL lifecycle gRPC endpoints (pause/resume, sleep/wake, weight-transfer RPCs) and sparse checkpoint-coordinate NCCL weight updates, making vLLM a true RL-aware inference engine.

> 💡 **Key Insight:** This is the most significant RL training infrastructure event since [TRL](https://github.com/huggingface/trl) introduced AsyncGRPO. The simultaneous release creates a native, high-performance stack where TRL owns training and vLLM owns generation with first-class RL lifecycle control. The AsyncDistillationTrainer's MOPD support arrives precisely when OPD research is peaking -- perfect timing.

---

### 2. On-Policy Distillation Explosion: Six Papers in One Week

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 9/10 |
| Business Impact | 9/10 |
| Personal Relevance | 10/10 |
| Confidence | High |

🧪 Early prototype

**Sources:** [RA-OPD](https://arxiv.org/abs/2608.27960) | [OPDVR](https://arxiv.org/abs/2608.24696) | [Open-MOPD](https://arxiv.org/abs/2608.19098) | [Critical Review](https://arxiv.org/abs/2608.25936) | [Beyond Imitation](https://arxiv.org/abs/2608.19408) | [Consolidating RLVR via MOPD](https://arxiv.org/abs/2608.27409) | **Reading time:** 25 min (combined)

Six independent papers attacked OPD failure modes in a single week. [RA-OPD](https://arxiv.org/abs/2608.27960) (Gan et al.) filters trajectories where teacher distillation returns conflict with outcome rewards, significantly outperforming standard OPD across Qwen3 and DeepSeek-R1 families. [OPDVR](https://arxiv.org/abs/2608.24696) (Lin et al.) fuses OPD with verifiable rewards via ReLU gating -- correct trajectories get non-negative rewards, incorrect get non-positive, no extra hyperparameters. [Open-MOPD](https://arxiv.org/abs/2608.19098) (Gao et al., ByteDance/Tsinghua) discovers standard multi-teacher OPD captures only 35.6% of available headroom, then fixes it via token-share balancing to reach 83.4%. [Consolidating RLVR](https://arxiv.org/abs/2608.27409) (Wu et al.) compares Merge, Mix-RL, and MOPD fusion paradigms with practical guidance. A [critical review](https://arxiv.org/abs/2608.25936) systematized OPSD collapse as governed by three levers: token weighting, privileged information, and signal dynamics.

> 🚀 **Opportunity:** OPD has crossed from "interesting alternative" to "the most researched post-training technique." With TRL's AsyncDistillationTrainer shipping the same week, the research-to-production pipeline is unusually fast. Teams not evaluating OPD are falling behind.

---

### 3. TailSFT: Filtered Fine-Tuning Compounds in RL

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 9/10 |
| Business Impact | 8/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🚀 Production-ready

**Source:** [TailSFT: Filtered Fine-Tuning Improves Post-Training Performance](https://arxiv.org/abs/2608.25756) -- Malladi, Jelassi, Foster, Ash, Krishnamurthy | **Reading time:** 10 min

Filters out already-learned sequences during SFT to focus on under-modeled tail regions. On OLMo-3 7B, [TailSFT](https://arxiv.org/abs/2608.25756) improves pass@16 by up to 17% absolute. Critically, higher-coverage TailSFT checkpoints yield **up to 4% absolute pass@1 gains** in subsequent GRPO runs, establishing that SFT quality compounds downstream. Provides a diagnostic tool for determining when TailSFT is most beneficial.

> 💡 **Key Insight:** This is the strongest evidence yet for "stage-aware" pipeline design. The quality of your SFT checkpoint directly determines your RL ceiling. Teams should evaluate their SFT data for redundancy before investing in RL compute.

---

### 4. VICT: Verifier-Instrumented Credit Tracing (EMNLP 2026)

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 9/10 |
| Practical Adoption | 7/10 |
| Business Impact | 8/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🧪 Early prototype

**Source:** [VICT: Verifier-Instrumented Credit Tracing for Long-Horizon LLM Agent RL](https://arxiv.org/abs/2608.28128) -- Li, Zhang, Zhang, Huang, Ma (EMNLP 2026) | **Reading time:** 12 min

Extracts executable atoms and dependency edges from terminal verifiers, redistributing group-relative advantage only along traced credit paths. Requires no learned critic, process labels, or additional rollouts -- modifies only the advantage computation. Strong results on ALFWorld and WebShop, matching recent fine-grained credit methods. Transforms credit assignment from a rollout-inference problem into a verifier-tracing problem, advancing WK31's [CoRT](https://arxiv.org/abs/2607.25659) and WK34's [Le Critique](https://arxiv.org/abs/2608.16739) themes.

> 💡 **Key Insight:** VICT is the most practical credit assignment advance this quarter. By reusing information already in verifiers rather than training separate critics, it eliminates the main cost barrier to fine-grained credit. EMNLP acceptance validates the approach.

---

### 5. RLVR Solution Space Narrowing: "Locked at the Entrance"

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 7/10 |
| Business Impact | 8/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🔬 Research-only

**Source:** [Locked at the Entrance, Open Inside: Where RLVR Narrows the Solution Space](https://arxiv.org/abs/2608.29188) -- Zhou, Li | **Reading time:** 10 min

Demonstrates that RLVR reduces solution coverage by up to 67%, with per-token likelihood shifts 11x--16x larger before the first arithmetic operation than during downstream reasoning. Models can execute alternative solutions when given correct starting prompts but fail to initiate them independently. Parameter interpolation between early/late checkpoints recovers 37% coverage without sacrificing pass@1. Staged SFT-DPO-RLVR pipelines preserve greater diversity than direct RLVR.

> ⚠️ **Risk:** This deepens WK34's [support reshaping](https://arxiv.org/abs/2608.00220) finding. RLVR doesn't just narrow the support -- it narrows it at the entrance, making the damage invisible during execution. Combined evidence: RLVR improves greedy accuracy but systematically destroys diversity and future trainability. Teams must monitor coverage metrics alongside accuracy.

---

### 6. Evolution Strategies: Broader Coverage than GRPO

| Metric | Score |
|--------|-------|
| Strategic Importance | 8/10 |
| Technical Innovation | 8/10 |
| Practical Adoption | 7/10 |
| Business Impact | 7/10 |
| Personal Relevance | 8/10 |
| Confidence | High |

🧪 Early prototype

**Source:** [Understanding Evolution Strategies for LLM Reasoning: Broader Reasoning Coverage than GRPO](https://arxiv.org/abs/2608.27351) -- Ba, Zheng, Xie et al. | **Reading time:** 10 min

Demonstrates that Evolution Strategies (ES) outperform GRPO by achieving broader reasoning coverage through population diversity. ES avoids the entropy collapse seen in GRPO and produces targeted parameter updates rather than widespread model changes. The authors develop a hybrid ES+GRPO training strategy combining both methods' strengths. This matures WK34's nascent [ES vs RL debate](https://arxiv.org/abs/2608.17310), providing the first systematic comparison.

> 💡 **Key Insight:** ES addresses RLVR's diversity problem at the algorithmic level rather than through post-hoc fixes. Combined with ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188), there's a growing case for ES-GRPO hybrids: use ES to maintain coverage breadth, GRPO to sharpen accuracy.

---

### 7. Performance Foundations of Distributed Reasoning LMs

| Metric | Score |
|--------|-------|
| Strategic Importance | 9/10 |
| Technical Innovation | 7/10 |
| Practical Adoption | 9/10 |
| Business Impact | 9/10 |
| Personal Relevance | 9/10 |
| Confidence | High |

🚀 Production-ready

**Source:** [Performance Foundations of Parallel & Distributed Reasoning Language Models](https://arxiv.org/abs/2608.27046) -- Besta, Schmidt, Nonino et al. (ETH Zurich) | **Reading time:** 15 min

Systematizes the RL-for-LLM paradigm with compute-centric analysis of PPO and GRPO. Develops a taxonomy of parallelism strategies: disaggregated placement, stage fusion, hybrid parallelism, and asynchronous execution. Provides practical guidelines for building scalable training infrastructure. This is the first comprehensive reference for distributed RL training architecture decisions.

> 🚀 **Opportunity:** This paper fills a critical gap. Until now, distributed RL training knowledge was scattered across framework docs and tribal knowledge. Having a systematic reference will accelerate adoption by teams that couldn't justify the exploration cost.

---

## 🏢 Frontier Lab Scorecards

| Lab | Releases | Research | Strategic Direction |
|-----|----------|----------|---------------------|
| **Anthropic** | — | [Enabling independent research on Claude usage](https://www.anthropic.com/research) (Aug 26) | Continued alignment science investment; quiet week on RL-specific publications after WK34's triple release |
| **Google DeepMind** | — | [Visual General Intelligence white paper](https://deepmind.google/research/publications/270149/) (Aug 26) | VGI focus; no RL-specific output this week |
| **Microsoft** | — | No new RL publications in window | Quiet after WK34's [Agent Lightning](https://arxiv.org/abs/2608.17528) and Build26 demo |
| **NVIDIA** | [TensorRT Model Connect](https://developer.nvidia.com/blog/) (Aug 28); [NVLink Fusion](https://developer.nvidia.com/blog/) (Aug 26); [CUDA Python 1.0](https://developer.nvidia.com/blog/) (Aug 25); [Vera Rubin announcement](https://developer.nvidia.com/blog/) (Aug 24) | — | Infrastructure focus: Vera Rubin next-gen GPU, NVLink Fusion for NVHBM, CUDA Python stability. No RL-specific updates |
| **OpenAI** | Blog inaccessible (403) | No confirmed RL publications | Silent week |
| **Meta** | — | No new RL/GRPO publications | Quiet period continues |
| **HuggingFace** | [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) (Aug 26) | [GRPO with TRL tutorial](https://huggingface.co/blog/grpo-with-trl-ifstruct) (Sep 3, preview) | Landmark release: vLLM native server, AsyncDistillationTrainer, MOPD |
| **Prime Intellect** | [Prime Agent](https://arxiv.org/abs/2608.23552) (Aug 24) | Self-improving RLM harness; 95.5% ARC-AGI-3 RHAE | Emerging player in agentic RL infrastructure |

**Power Ranking Shift:** HuggingFace's [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) simultaneous release cements the TRL+vLLM stack as the default open-source RL training infrastructure. No competitor shipped comparable functionality this week. Prime Intellect emerges as a noteworthy new entrant with [Prime Agent](https://arxiv.org/abs/2608.23552).

---

## 🌐 Open-Source Ecosystem Tracking

| Project | Activity | Trajectory |
|---------|----------|-----------|
| **[TRL](https://github.com/huggingface/trl)** | **v1.11.0 released Aug 26.** 25 PRs merged (Aug 23--29): vLLM native server ([#6765](https://github.com/huggingface/trl/pull/6765)), AsyncDistillationTrainer, DistillationTrainer tool calling, missing entropy gradient fix ([#6625](https://github.com/huggingface/trl/pull/6625)), vLLM weight sync fix ([#6913](https://github.com/huggingface/trl/pull/6913)), dropped vLLM 0.18 ([#6844](https://github.com/huggingface/trl/pull/6844)), QLoRA GRPO/RLOO VLM tests ([#6909](https://github.com/huggingface/trl/pull/6909), [#6910](https://github.com/huggingface/trl/pull/6910)). ~19.2K stars | 📈 Accelerating |
| **[vLLM](https://github.com/vllm-project/vllm)** | **v0.28.0 released Aug 26.** 584 commits, 270 contributors. RL lifecycle gRPC ([#51316](https://github.com/vllm-project/vllm/pull/51316)), sparse NCCL weight updates ([#53751](https://github.com/vllm-project/vllm/pull/53751)), DeepSeek V4 sparse MLA, Kimi-K3 performance push. ~91K stars | 📈 Accelerating |
| **[verl](https://github.com/volcengine/verl)** | 10 PRs merged: DeepSeek V4 QAT bf16 fake quant ([#7577](https://github.com/volcengine/verl/pull/7577)), vLLM prefix-cache hit counts ([#7565](https://github.com/volcengine/verl/pull/7565)), context parallelism padding fix, strict dynamic micro-batch limits. ~23.3K stars | ➡️ Stable |
| **[OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)** | Quiet week after v0.11.0 (Aug 13). Approaching 10K stars. Description now highlights "Agentic RL" prominently | ➡️ Stable |
| **[SkyRL](https://github.com/NovaSky-AI/SkyRL)** | 2 PRs: GatedDeltaNet LoRA targeting ([#2093](https://github.com/NovaSky-AI/SkyRL/pull/2093)), sharded RDT weight sync ([#2090](https://github.com/NovaSky-AI/SkyRL/pull/2090)). ~2.2K stars | ➡️ Stable |
| **[OraRL](https://github.com/HVision-NKU/OraRL)** | New -- annotations as rollouts for video MLLM RL ([paper](https://arxiv.org/abs/2608.20492)). 152 stars | 📈 New entry |
| **[NeMo-Aligner](https://github.com/NVIDIA/NeMo-Aligner)** | No activity. Last release v0.7.0 (March 2025, 17+ months ago). 852 stars | 📉 Decelerating |

**Notable:** TRL's accidental v1.12.0 release (bit-identical to v1.11.0 on PyPI) burned the version number; next real release will be v1.13.0. The [TRL](https://github.com/huggingface/trl)+[vLLM](https://github.com/vllm-project/vllm) co-release demonstrates deep integration between the two projects.

---

## 💰 Business & Market Intelligence

- **[TRL v1.11.0 + vLLM v0.28.0: RL infrastructure consolidation](https://github.com/huggingface/trl/releases/tag/v1.11.0):** The simultaneous release creates a vertically integrated open-source RL training stack. TRL's 1.44--1.59x speedup on GRPO benchmarks directly reduces training costs. vLLM's RL lifecycle gRPC endpoints eliminate the need for custom inference servers. This tightens [HuggingFace](https://huggingface.co/)'s position as the default RL training platform.
- **[NVIDIA Vera Rubin and infrastructure announcements](https://developer.nvidia.com/blog/):** NVIDIA announced Vera Rubin GPUs, NVLink Fusion with NVHBM, and CUDA Python 1.0 stability milestone at GTC 2026. While not RL-specific, next-generation GPU infrastructure directly impacts RL training economics. The Vera Rubin + NVLink Fusion combination targets the memory bandwidth bottleneck that limits GRPO rollout throughput.
- **[Prime Intellect enters agentic RL](https://arxiv.org/abs/2608.23552):** Prime Agent's 95.5% on ARC-AGI-3 RHAE with a persistent harness architecture positions Prime Intellect as a serious agentic RL infrastructure provider. Their open-source Creative Commons release follows WK34's harness-native RL convergence theme.
- **[verl ecosystem expansion](https://github.com/volcengine/verl):** ByteDance/Volcengine's verl (23.3K stars) continues growing its enterprise presence with DeepSeek V4 QAT support and prefix-cache observability for RL rollouts. The gap between TRL (HuggingFace ecosystem) and verl (Chinese AI ecosystem) is a strategic divide worth monitoring.
- **[NeMo-Aligner stagnation](https://github.com/NVIDIA/NeMo-Aligner):** NVIDIA's RL training framework has not shipped a release in 17 months while competitors grow rapidly. This suggests NVIDIA is pivoting its RL strategy to hardware/inference (vLLM integration) rather than maintaining its own training framework.
- **[SWE-bench continues consolidating](https://www.swebench.com/):** Multiple WK35 papers reference SWE-bench as the primary agentic RL evaluation. Combined with WK34's harness-native convergence, SWE-bench is becoming the standard benchmark for RL-trained coding agents.

---

## 📄 Research Papers

### Tier 1 -- Must-Read

1. **[TailSFT: Filtered Fine-Tuning Improves Post-Training Performance](https://arxiv.org/abs/2608.25756)** -- Malladi, Jelassi, Foster, Ash, Krishnamurthy
   Filtered SFT on under-modeled tail regions improves pass@16 by 17% and subsequent GRPO pass@1 by 4% on OLMo-3 7B. Establishes stage-aware pipeline design.
   Strategic: 9 | Technical: 7 | Practical: 9 | Business: 8 | 🚀 Production-ready

2. **[VICT: Verifier-Instrumented Credit Tracing](https://arxiv.org/abs/2608.28128)** -- Li, Zhang, Zhang, Huang, Ma (EMNLP 2026)
   Extracts credit paths from verifier internals; no critics, process labels, or extra rollouts needed. Strong ALFWorld/WebShop results.
   Strategic: 9 | Technical: 9 | Practical: 7 | Business: 8 | 🧪 Early prototype

3. **[RA-OPD: Reward-Aligned On-Policy Distillation](https://arxiv.org/abs/2608.27960)** -- Gan, Li, Wang et al.
   Filters teacher-reward misalignment by comparing trajectory distillation returns against outcome rewards. Outperforms standard OPD across Qwen3 and DeepSeek-R1 families on math and code.
   Strategic: 8 | Technical: 7 | Practical: 8 | Business: 8 | 🧪 Early prototype

4. **[When Do Larger Batches Help Scale LLM RL?](https://arxiv.org/abs/2608.29296)** -- Li, Wang, Huang et al.
   Square-root LR scaling with Adam produces batch-size-invariant learning curves. Larger batches help only when throughput gains exceed sampling penalties. Up to 29% time-to-target improvement with GRPO/PPO.
   Strategic: 8 | Technical: 7 | Practical: 9 | Business: 8 | 🚀 Production-ready

5. **[OPDVR: On-Policy Distillation with Verifiable Reward](https://arxiv.org/abs/2608.24696)** -- Lin, Zhao, Jiang et al.
   ReLU gating fuses OPD with verifiable rewards. No extra hyperparameters. Consistent improvements across six reasoning benchmarks. GRPO-compatible.
   Strategic: 8 | Technical: 7 | Practical: 8 | Business: 8 | 🧪 Early prototype

6. **[Locked at the Entrance: Where RLVR Narrows the Solution Space](https://arxiv.org/abs/2608.29188)** -- Zhou, Li
   67% solution coverage loss from RLVR, concentrated at trajectory entry (11x--16x larger shifts). Parameter interpolation recovers 37%. Staged SFT-DPO-RLVR preserves more diversity.
   Strategic: 9 | Technical: 7 | Practical: 7 | Business: 7 | 🔬 Research-only

7. **[Performance Foundations of Parallel & Distributed Reasoning LMs](https://arxiv.org/abs/2608.27046)** -- Besta, Schmidt, Nonino et al. (ETH Zurich)
   Systematizes PPO/GRPO parallelism: disaggregated placement, stage fusion, hybrid parallelism, async execution. First comprehensive reference for distributed RL training.
   Strategic: 9 | Technical: 7 | Practical: 9 | Business: 9 | 🚀 Production-ready

### Tier 2 -- Noteworthy

8. **[Open-MOPD: Diagnosing Capability Imbalance in Multi-Teacher OPD](https://arxiv.org/abs/2608.19098)** -- Gao, Chi, Yan et al. (ByteDance/Tsinghua)
   Standard MOPD captures only 35.6% headroom; token-share balancing and dynamic budget raise it to 83.4%. Open-sourced training recipes.
   Strategic: 8 | Technical: 8 | Practical: 8 | Business: 8 | 🧪 Early prototype

9. **[Understanding ES for LLM Reasoning: Broader Coverage than GRPO](https://arxiv.org/abs/2608.27351)** -- Ba, Zheng, Xie et al.
   ES achieves broader reasoning coverage via population diversity, avoiding entropy collapse. Hybrid ES+GRPO strategy proposed.
   Strategic: 8 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

10. **[JudgePanel: Compact Judge via Adaptive Multi-Reward RL](https://arxiv.org/abs/2608.29168)** -- Qian, Zhang, Song et al.
    AdaReward dynamically rebalances reward weights as objectives saturate. 14B model outperforms larger specialized judges.
    Strategic: 8 | Technical: 8 | Practical: 8 | Business: 8 | 🧪 Early prototype

11. **[DA3PO: Difficulty-Aware Advantage Amplification](https://arxiv.org/abs/2608.27982)** -- Gan, Li, Wang et al.
    Amplifies advantages of difficult correct responses that DAPO's Dynamic Sampling underutilizes. Minimal code change over GRPO. Drop-in improvement.
    Strategic: 7 | Technical: 7 | Practical: 9 | Business: 7 | 🚀 Production-ready

12. **[ERPO: Environmental Regularization for LLM Policy Optimization](https://arxiv.org/abs/2608.23311)** -- Zhou, Meng, He et al. (Alibaba, EMNLP 2026)
    Query-KL replaces Policy-KL, moving regularization from response-side to input-side. Preserves exploration while stabilizing training. Improved accuracy across six math benchmarks.
    Strategic: 8 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

13. **[Demystifying RL Post-Training of Language Models](https://arxiv.org/abs/2608.24949)** -- Clay, Gollapudi, Harilal et al.
    Pedagogical primer using output-distribution entropy as analytical lens. Shows spurious reward impact depends on prompt distribution. Clarifies exploration dynamics.
    Strategic: 9 | Technical: 6 | Practical: 8 | Business: 7 | 🧪 Early prototype

### Tier 3 -- Domain Applications and Extensions

14. **[ERR+: Entropy Resolution for Efficient LLM Reasoning](https://arxiv.org/abs/2608.28771)** -- Jiang, Wang, Wu et al.
    Uses entropy drops in thinking tokens as reward signal. Two-phase RLVR framework improving both accuracy and conciseness.
    Strategic: 8 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

15. **[Consolidating RLVR Across Domains](https://arxiv.org/abs/2608.27409)** -- Wu, Yang, Cai et al.
    Compares Merge, Mix-RL, and MOPD for multi-domain RLVR. Performance gaps average 1.4 points, up to 8.6 on specific tasks. Practical fusion guidance.
    Strategic: 8 | Technical: 6 | Practical: 9 | Business: 8 | 🚀 Production-ready

16. **[RubricRM: Generative Reward Modeling via Dynamic Rubrics](https://arxiv.org/abs/2608.26956)** -- Kan, Wang, Luo et al.
    Pairwise generative RM producing input-specific rubrics. Two-stage SFT + GRPO training. Competitive with proprietary judges.
    Strategic: 8 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

17. **[Boosting LLM Exploration via Weak-Model Guidance in RLVR](https://arxiv.org/abs/2608.27420)** -- Shen, Zhang, Li et al.
    Forces target models to generate from weaker-model prefixes. Substantially expands reasoning coverage at scale. Simple technique for addressing entropy collapse.
    Strategic: 8 | Technical: 7 | Practical: 8 | Business: 7 | 🧪 Early prototype

18. **[BPCO: Best Practice Critic Optimization](https://arxiv.org/abs/2608.23566)** -- Qi, Zhou, Lee
    Stable critic training via DPPO with reward-range-bounded values and length-adaptive advantages. Matches GRPO with single response per prompt.
    Strategic: 7 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

19. **[Prime Agent: A Self-Improving RLM Harness](https://arxiv.org/abs/2608.23552)** -- Karten, Zhang et al. (Prime Intellect)
    Persistent harness with continual memory, recursive subagent coordination, and agents view. 95.5% ARC-AGI-3 RHAE. Open-source.
    Strategic: 8 | Technical: 7 | Practical: 8 | Business: 8 | 🧪 Early prototype

20. **[Disentangling Optimization Scale from Preference Scale in DPO](https://arxiv.org/abs/2608.27032)** -- Kruzhilov
    DPO's beta entangles preference-noise with optimization dynamics. Centered-softplus reformulation makes them independently tunable.
    Strategic: 7 | Technical: 8 | Practical: 7 | Business: 6 | 🔬 Research-only

21. **[FARCA: Fact-Aligned Credit Assignment](https://arxiv.org/abs/2608.24350)** -- Xie, Zheng, Shen et al.
    Counterfactual evidence attribution for factual grounding. Reliability-weighted token-level signals.
    Strategic: 8 | Technical: 8 | Practical: 6 | Business: 7 | 🔬 Research-only

22. **[Privacy Without Regret: DP Inference-Time Alignment](https://arxiv.org/abs/2608.26324)** -- Jain, Bhattad, Chowdhury
    Calibrated noise in Best-of-N provides epsilon-DP while implementing KL-regularized alignment. Noise as alignment feature, not just privacy cost.
    Strategic: 8 | Technical: 8 | Practical: 6 | Business: 7 | 🔬 Research-only

23. **[RCCA: Rubric-to-Code Credit Assignment](https://arxiv.org/abs/2608.27906)** -- Jin, Chen, Chen et al.
    Hierarchical rewards (format, source, runtime, functional) with token-level attribution. 41.25 on MiniAppBench, 76.19 on ArtifactsBench.
    Strategic: 7 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

24. **[SRPO: Self-Reflective Policy Optimization](https://arxiv.org/abs/2608.23493)** -- Liu, Shi, Yang et al.
    LLMs analyze completed trajectories to synthesize "reflection patches" as dense token-level training signals. No external critics needed.
    Strategic: 7 | Technical: 8 | Practical: 7 | Business: 7 | 🧪 Early prototype

25. **[Is Next-Chunk Reasoning RL Better than SFT?](https://arxiv.org/abs/2608.23256)** -- Tang, Fang, Sun et al.
    Mixed SFT achieves higher post-RLVR ceiling than next-chunk reasoning RL at 60x less compute. Challenges RL-first assumptions for non-CoT data.
    Strategic: 7 | Technical: 6 | Practical: 8 | Business: 7 | 🧪 Early prototype

26. **[TTPO: Test-Time Policy Optimization](https://arxiv.org/abs/2608.27448)** -- Wang, Lu, Wang et al.
    On-policy self-distillation + RL at test time without ground-truth labels. Token-level selection refines both components. Matches label-supervised methods.
    Strategic: 7 | Technical: 8 | Practical: 6 | Business: 6 | 🧪 Early prototype

27. **[One Symptom, Three Levers: Critical Review of OPSD](https://arxiv.org/abs/2608.25936)** -- Robert, Qader
    Systematizes OPSD collapse via token weighting, privileged information, and signal dynamics. Shared vocabulary for failure modes. Important reference.
    Strategic: 7 | Technical: 5 | Practical: 7 | Business: 6 | 🔬 Research-only

28. **[SecOPD: Mitigating Prompt Injections by On-Policy Distillation](https://arxiv.org/abs/2608.21500)**
    OPD as defense against adaptive prompt injections. Safety application of distillation.
    Strategic: 7 | Technical: 6 | Practical: 7 | Business: 7 | 🧪 Early prototype

---

## 🧬 Research Blogs

1. **[HuggingFace: GRPO with TRL for Structured Outputs in 100 Steps](https://huggingface.co/blog/grpo-with-trl-ifstruct)** -- Leonie Monigatti | Sep 3 (preview, tied to TRL v1.11.0)
   Fine-tuned a 350M [Liquid AI](https://www.liquid.ai/) model using GRPO with [TRL](https://github.com/huggingface/trl): JSON compliance 18.0% to 31.9%, overall 22.6% to 29.7% on IFStruct benchmark. Only 100 steps, LoRA targeting ~6M parameters on free-tier GPU. Three-component weighted reward (format validity, field count, schema). Demonstrates GRPO is practical even for tiny models on constrained hardware.
   Strategic: 7 | Technical: 5 | Practical: 9 | 🚀 Production-ready

2. **[Anthropic: Enabling Independent Research on How People Use Claude](https://www.anthropic.com/research)** -- Anthropic | Aug 26
   [Anthropic](https://www.anthropic.com/) enables external researchers to study Claude usage patterns independently. While not directly RL-focused, this supports alignment research by providing outside scrutiny of post-training behavior in production -- relevant to the reward hacking and alignment monitoring themes from WK34's [misaligned reward seeker](https://alignment.anthropic.com/2026/reward-seeker).
   Strategic: 7 | Technical: 4 | Practical: 6 | 🔬 Research-only

3. **[Demystifying RL Post-Training](https://arxiv.org/abs/2608.24949)** -- Clay, Gollapudi, Harilal et al. | Aug 24
   Pedagogical primer deconstructing RL post-training mechanics. Uses output-distribution entropy to examine how base model priors, reward granularity, prompt diversity, and scale shape outcomes. Shows spurious reward impact depends on prompt distribution. Essential reading for teams starting with RL post-training.
   Strategic: 9 | Technical: 6 | Practical: 8 | 🧪 Early prototype

4. **[One Symptom, Three Levers: Critical Review of OPSD](https://arxiv.org/abs/2608.25936)** -- Robert, Qader | Aug 26
   Deep systematization of on-policy self-distillation failure modes. Token weighting, privileged information, and signal dynamics as governing levers. Creates shared vocabulary for the OPD community. Critical reference as OPD becomes the dominant paradigm.
   Strategic: 7 | Technical: 5 | Practical: 7 | 🔬 Research-only

5. **[Locked at the Entrance: Where RLVR Narrows](https://arxiv.org/abs/2608.29188)** -- Zhou, Li | Aug 29
   Detailed analysis showing per-token shifts are 11--16x larger at trajectory entry than during execution. Entrance-prefix guidance restores completion rates from 0.018 to 0.212 under PPO. Strongest mechanistic explanation yet for RLVR's diversity cost.
   Strategic: 9 | Technical: 7 | Practical: 7 | 🔬 Research-only

6. **[Consolidating RLVR: Merge vs. Mix RL vs. MOPD](https://arxiv.org/abs/2608.27409)** -- Wu et al. | Aug 27
   Practical comparison of three multi-domain RLVR fusion approaches. Clear decision framework: Merge for existing experts, Mix RL for unified training, MOPD when preserving domain-specific gains matters. Performance gaps of 1.4 (avg) to 8.6 (max) between approaches.
   Strategic: 8 | Technical: 6 | Practical: 9 | 🚀 Production-ready

7. **[Open-MOPD: From 35.6% to 83.4% Headroom Recovery](https://arxiv.org/abs/2608.19098)** -- Gao et al. (ByteDance/Tsinghua) | Aug 19
   Why standard multi-teacher OPD fails: sequence-length disparities, non-uniform learning rates, and reward staleness. Token-share balancing as the fix. Complete open-source training recipes.
   Strategic: 8 | Technical: 8 | Practical: 8 | 🧪 Early prototype

8. **[TailSFT: Stage-Aware Pipeline Design](https://arxiv.org/abs/2608.25756)** -- Malladi et al. | Aug 26
   The practical case for evaluating SFT checkpoints by their downstream RL performance rather than standalone metrics. Coverage and pass@K as predictors of post-RL success. Includes a diagnostic tool for determining when TailSFT helps most.
   Strategic: 9 | Technical: 7 | Practical: 9 | 🚀 Production-ready

9. **[Disentangling Beta in DPO](https://arxiv.org/abs/2608.27032)** -- Kruzhilov | Aug 27
   Analysis of how DPO's coefficient beta entangles preference-noise scale with optimization dynamics. Centered-softplus reformulation as the fix. Important for anyone tuning DPO hyperparameters -- beta has been doing two jobs simultaneously.
   Strategic: 7 | Technical: 8 | Practical: 7 | 🔬 Research-only

10. **[ERPO: Query-KL for Stable Exploration](https://arxiv.org/abs/2608.23311)** -- Zhou et al. (Alibaba, EMNLP 2026) | Aug 24
    Moves KL regularization from response-side (Policy-KL) to input-side (Query-KL), preserving exploration while controlling drift. EMNLP acceptance validates the approach. Directly relevant to the RLVR diversity problem identified by [support reshaping](https://arxiv.org/abs/2608.00220) and ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188).
    Strategic: 8 | Technical: 8 | Practical: 7 | 🧪 Early prototype

11. **[Survey on Rubric-Guided RL for Language Models](https://arxiv.org/abs/2608.27505)** -- Shan, Shao | Aug 27
    Surveys rubric-guided RL as an answer to RLHF limitations. Bayesian framework with constitutions as priors, rubrics as conditional instantiations. Covers granularity tradeoffs and semantic drift in reward specification.
    Strategic: 7 | Technical: 5 | Practical: 7 | 🔬 Research-only

---

## 🛠️ Engineering Blogs

| # | Post | Source | Signal | Key Insight |
|---|------|--------|--------|-------------|
| 1 | [TRL v1.11.0: Use vLLM's own server (#6765)](https://github.com/huggingface/trl/pull/6765) | HuggingFace TRL | 🚀 | 1,218 to ~130 lines; 1.44--1.59x GRPO speedup via NCCL weight sync |
| 2 | [AsyncDistillationTrainer with MOPD support](https://github.com/huggingface/trl/releases/tag/v1.11.0) | HuggingFace TRL | 🚀 | Multi-teacher on-policy distillation via teacher_id routing |
| 3 | [Fix missing entropy gradient in ChunkedLogProb (#6625)](https://github.com/huggingface/trl/pull/6625) | HuggingFace TRL | 🚀 | Critical correctness fix for chunked loss computation |
| 4 | [Fix vLLM weight sync fails instead of hanging (#6913)](https://github.com/huggingface/trl/pull/6913) | HuggingFace TRL | 🚀 | Reliability improvement for RL training loops |
| 5 | [Drop vLLM 0.18 support (#6844)](https://github.com/huggingface/trl/pull/6844) | HuggingFace TRL | 🧪 | Requires vLLM 0.19+; cleans up compatibility debt |
| 6 | [DistillationTrainer tool calling support (#6723)](https://github.com/huggingface/trl/releases/tag/v1.11.0) | HuggingFace TRL | 🚀 | Distillation for tool-using models |
| 7 | [QLoRA tests for GRPO and RLOO VLM suites (#6909, #6910)](https://github.com/huggingface/trl/pull/6909) | HuggingFace TRL | 🧪 | Quantized RL training validation |
| 8 | [Remove one host sync from SFT chunked_nll loss (#6842)](https://github.com/huggingface/trl/pull/6842) | HuggingFace TRL | 🧪 | SFT performance optimization |
| 9 | [Suggest migrating GKD to DistillationTrainer (#6847)](https://github.com/huggingface/trl/pull/6847) | HuggingFace TRL | 🧪 | GKD deprecation path |
| 10 | [vLLM v0.28.0: RL lifecycle gRPC endpoints](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) | vLLM | 🚀 | pause/resume, sleep/wake, weight-transfer RPCs for RL |
| 11 | [vLLM v0.28.0: Sparse NCCL weight updates (#53751)](https://github.com/vllm-project/vllm/pull/53751) | vLLM | 🚀 | Checkpoint-coordinate sparse updates; O(nnz) wire payloads |
| 12 | [verl: DeepSeek V4 QAT bf16 fake quant (#7577)](https://github.com/volcengine/verl/pull/7577) | verl | 🧪 | Quantization-aware training for latest models |
| 13 | [verl: vLLM prefix-cache hit counts (#7565)](https://github.com/volcengine/verl/pull/7565) | verl | 🧪 | Better observability for RL rollouts |
| 14 | [NVIDIA: CUDA Python 1.0 stable APIs](https://developer.nvidia.com/blog/) | NVIDIA | 🧪 | Foundation for custom RL training kernels |
| 15 | [NVIDIA: NVLink Fusion with NVHBM](https://developer.nvidia.com/blog/) | NVIDIA | 🧪 | Next-gen interconnect for RL training clusters |

---

## 📦 GitHub Projects

| Project | Stars | This Week | Category |
|---------|-------|-----------|----------|
| **[huggingface/trl](https://github.com/huggingface/trl)** | ~19.2K | v1.11.0 released, 25 PRs merged | RL Training |
| **[vllm-project/vllm](https://github.com/vllm-project/vllm)** | ~91K | v0.28.0 released, 256 PRs merged | RL Inference |
| **[volcengine/verl](https://github.com/volcengine/verl)** | ~23.3K | 10 PRs, DeepSeek V4 QAT | RL Training |
| **[OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)** | ~10K | Quiet; approaching 10K stars | RL Training |
| **[HVision-NKU/OraRL](https://github.com/HVision-NKU/OraRL)** | 152 | New -- annotations as rollouts for video MLLM RL | RL for Video |
| **[Ch921-cell/Remember-R1](https://github.com/Ch921-cell/Remember-R1)** | 347 | ACM MM 2026 Oral -- RL for visual forgetting | RL for VLMs |
| **[hexo-ai/sia](https://github.com/hexo-ai/sia)** | 2,142 | Self-improving AI framework | Self-Improvement |
| **[alexzhang13/rlm](https://github.com/alexzhang13/rlm)** | 5,585 | Inference library for recursive LMs | RL Inference |
| **[wangclnlp/RRC](https://github.com/wangclnlp/RRC)** | 3 | Ranking-Based Reward Construction | Reward Modeling |
| **[stonewst/SR-TTRL](https://github.com/stonewst/SR-TTRL)** | 1 | ICML 2026 -- self-reflective test-time RL | Test-Time RL |

---

## 🎙️ Videos & Podcasts

No significant RL-for-LLMs-focused podcast episodes or talks identified for August 23--29, 2026. The broader AI podcast landscape ([Latent Space](https://www.latent.space/), [Gradient Dissent](https://wandb.ai/site/podcast)) did not feature dedicated RL training content this week. The [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) release and [OPD explosion](#research) are likely to generate long-form discussion in WK36. [Prime Intellect's](https://arxiv.org/abs/2608.23552) ARC-AGI-3 result may attract interview coverage.

---

## 💬 Community Insights

### OPD Maturation Generates Framework Debates

The simultaneous appearance of six OPD papers ([RA-OPD](https://arxiv.org/abs/2608.27960), [OPDVR](https://arxiv.org/abs/2608.24696), [Open-MOPD](https://arxiv.org/abs/2608.19098), [critical review](https://arxiv.org/abs/2608.25936), [Beyond Imitation](https://arxiv.org/abs/2608.19408), [SecOPD](https://arxiv.org/abs/2608.21500)) is sparking debates about when OPD beats GRPO and when it doesn't. The community consensus is forming around a spectrum: use OPD when you have a strong teacher and limited compute, GRPO when you need to push past teacher quality, and RLVR when you have verifiable tasks. [TRL](https://github.com/huggingface/trl)'s AsyncDistillationTrainer shipping in the same week accelerates practitioner adoption.

### RLVR Diversity Alarm Grows

[Locked at the Entrance](https://arxiv.org/abs/2608.29188) and [Weak-Model Guidance](https://arxiv.org/abs/2608.27420) deepen WK34's [support reshaping](https://arxiv.org/abs/2608.00220) concerns. The community is increasingly alarmed that RLVR systematically destroys solution diversity while appearing to improve accuracy. Practitioners are asking: "If RLVR narrows at the entrance, are we optimizing ourselves into a corner?" The [ES vs GRPO](https://arxiv.org/abs/2608.27351) paper's finding that ES avoids entropy collapse is generating particular interest as a potential mitigation.

### TRL v1.11.0 Draws Infrastructure Attention

The [vLLM native server integration](https://github.com/huggingface/trl/pull/6765) and 1.44--1.59x speedup are drawing significant practitioner attention. The accidental v1.12.0 release (bit-identical to v1.11.0) generated brief confusion but was quickly explained. The deeper signal: [TRL](https://github.com/huggingface/trl) and [vLLM](https://github.com/vllm-project/vllm) are converging into a single integrated stack, which practitioners view positively for reducing integration complexity.

### Stage-Aware Pipeline Design Gains Traction

[TailSFT](https://arxiv.org/abs/2608.25756)'s finding that SFT quality compounds in RL is generating "aha moments" in the community. The implication -- that teams should evaluate SFT checkpoints by their downstream RL performance, not standalone metrics -- challenges common practice. Combined with [Is Next-Chunk Reasoning RL Better than SFT?](https://arxiv.org/abs/2608.23256) showing mixed SFT achieves higher post-RLVR ceilings at 60x less compute, the stage-ordering question is becoming central to pipeline design.

---

## 📈 Emerging Themes

1. **On-policy distillation is the dominant research front.** Six OPD papers in one week ([RA-OPD](https://arxiv.org/abs/2608.27960), [OPDVR](https://arxiv.org/abs/2608.24696), [Open-MOPD](https://arxiv.org/abs/2608.19098), [critical review](https://arxiv.org/abs/2608.25936), [Beyond Imitation](https://arxiv.org/abs/2608.19408), [SecOPD](https://arxiv.org/abs/2608.21500)), plus [TRL](https://github.com/huggingface/trl)'s AsyncDistillationTrainer release, make OPD the single most active subfield in RL post-training. The maturation from WK31's "promising alternative" to WK35's "dominant paradigm" took just four weeks.

2. **Infrastructure consolidation accelerates.** [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) create the tightest open-source RL training stack. [verl](https://github.com/volcengine/verl) continues growing in the Chinese ecosystem. [NeMo-Aligner](https://github.com/NVIDIA/NeMo-Aligner) stagnation signals NVIDIA pivoting to hardware. The distributed RL reference ([Besta et al.](https://arxiv.org/abs/2608.27046)) provides the missing architectural playbook.

3. **RLVR diversity concerns deepen.** ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) (67% coverage loss), [Weak-Model Guidance](https://arxiv.org/abs/2608.27420), and WK34's [support reshaping](https://arxiv.org/abs/2608.00220) form a consistent narrative: RLVR improves greedy accuracy but systematically destroys diversity at trajectory entry points. [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351) and staged SFT-DPO-RLVR pipelines are emerging as mitigations.

4. **Credit assignment proliferates across granularities.** [VICT](https://arxiv.org/abs/2608.28128) (verifier tracing, EMNLP), [FARCA](https://arxiv.org/abs/2608.24350) (counterfactual evidence), [RCCA](https://arxiv.org/abs/2608.27906) (rubric-to-code), [ERR+](https://arxiv.org/abs/2608.28771) (entropy resolution), and [SRPO](https://arxiv.org/abs/2608.23493) (self-reflective) all tackle credit at different levels -- token, segment, step, and trajectory. This extends WK31's [CoRT](https://arxiv.org/abs/2607.25659) and WK34's [Le Critique](https://arxiv.org/abs/2608.16739) into a broad research front.

5. **Stage-aware pipeline design is emerging.** [TailSFT](https://arxiv.org/abs/2608.25756) (SFT quality compounds in RL), [Is Next-Chunk RL Better than SFT?](https://arxiv.org/abs/2608.23256) (mixed SFT at 60x less compute), and ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) (staged SFT-DPO-RLVR preserves diversity) all show that the ordering and quality of pipeline stages matters as much as the RL algorithm itself.

6. **Generative reward modeling advances.** [RubricRM](https://arxiv.org/abs/2608.26956) (dynamic rubrics via GRPO), [JudgePanel](https://arxiv.org/abs/2608.29168) (adaptive multi-reward), and [DA3PO](https://arxiv.org/abs/2608.27982) (difficulty-aware advantages) push reward modeling beyond scalar scores toward structured, dynamic evaluation criteria.

7. **ES vs GRPO debate matures with empirical evidence.** [Ba et al.](https://arxiv.org/abs/2608.27351) provide the first systematic ES-GRPO comparison, showing ES achieves broader coverage through population diversity while avoiding entropy collapse. Combined with WK34's [Agentic ESOpt](https://arxiv.org/abs/2608.17310), ES is establishing itself as a serious alternative for diversity-sensitive post-training.

---

## 📊 Trend Tracking Over Time

| Theme | First Noted | Consecutive Weeks | Momentum |
|-------|-------------|-------------------|----------|
| GRPO as default LLM RL optimizer | WK30 | 6 (gap WK32-33) | ➡️ Stable -- still dominant but [ES comparison](https://arxiv.org/abs/2608.27351) challenges |
| GRPO limitations being characterized | WK30 | 6 | 📈 Accelerating -- [RLVR narrowing](https://arxiv.org/abs/2608.29188), [ES coverage](https://arxiv.org/abs/2608.27351) |
| Self-play for non-verifiable rewards | WK30 | 6 | ➡️ Stable -- no major new results this week |
| Async RL infrastructure | WK30 | 6 | 📈 Accelerating -- [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) shipped |
| Process vs. outcome rewards tension | WK30 | 6 | ➡️ Stable -- [VICT](https://arxiv.org/abs/2608.28128) advances verifier-based credit |
| On-policy distillation as RL alternative | WK31 | 5 | 📈 Accelerating -- 6 papers + [TRL AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0); now dominant research front |
| Agentic RL as distinct subfield | WK31 | 5 | ➡️ Stable -- [Prime Agent](https://arxiv.org/abs/2608.23552) continues WK34 harness-native theme |
| Self-play as universal RL paradigm | WK31 | 5 | ➡️ Stable -- no follow-up to WK34's [SPADE](https://arxiv.org/abs/2608.19197) |
| Token-level credit for GRPO | WK31 | 5 | 📈 Accelerating -- [VICT](https://arxiv.org/abs/2608.28128), [FARCA](https://arxiv.org/abs/2608.24350), [RCCA](https://arxiv.org/abs/2608.27906), [ERR+](https://arxiv.org/abs/2608.28771), [SRPO](https://arxiv.org/abs/2608.23493) |
| Meta-learned reward shaping | WK31 | 5 | ➡️ Stable -- no follow-up |
| Harness-native RL training | WK34 | 2 | ➡️ Stable -- [Prime Agent](https://arxiv.org/abs/2608.23552) continues pattern but no new breakthrough |
| Multi-reward optimization | WK34 | 2 | 📈 Accelerating -- [JudgePanel AdaReward](https://arxiv.org/abs/2608.29168), [DA3PO](https://arxiv.org/abs/2608.27982) |
| RLVR trainability/diversity concerns | WK34 | 2 | 📈 Accelerating -- ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188), [Weak-Model Guidance](https://arxiv.org/abs/2608.27420) |
| Reward hacking as systemic risk | WK34 | 2 | ➡️ Stable -- [Privacy Without Regret](https://arxiv.org/abs/2608.26324) links to DP |
| RL post-training privacy risks | WK34 | 2 | ➡️ Stable -- no direct follow-up |
| OPD as dominant research paradigm | WK35 | 1 | 📈 New theme -- 6 papers in one week |
| Stage-aware pipeline design | WK35 | 1 | 📈 New theme -- [TailSFT](https://arxiv.org/abs/2608.25756), [Is Next-Chunk RL > SFT?](https://arxiv.org/abs/2608.23256) |
| ES vs GRPO with empirical comparison | WK35 | 1 | 📈 New theme -- [Ba et al.](https://arxiv.org/abs/2608.27351) systematic study |

---

## 🏗️ Implications for LLM Builders

1. **Upgrade to [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) immediately.** The vLLM native server delivers 1.44--1.59x GRPO speedup with no algorithmic changes. vLLM's RL lifecycle gRPC endpoints eliminate the need for custom inference servers. This is free performance.

2. **Evaluate on-policy distillation now.** Six papers validated OPD from different angles, and [TRL](https://github.com/huggingface/trl)'s AsyncDistillationTrainer provides production infrastructure. Start with [OPDVR](https://arxiv.org/abs/2608.24696) (simplest, no extra hyperparameters) or [RA-OPD](https://arxiv.org/abs/2608.27960) (strongest results on Qwen3/DeepSeek-R1). For multi-teacher setups, implement [Open-MOPD](https://arxiv.org/abs/2608.19098)'s token-share balancing.

3. **Apply [TailSFT](https://arxiv.org/abs/2608.25756) before RL training.** Filter out already-learned SFT sequences to focus on under-modeled tails. The 4% absolute pass@1 gain in subsequent GRPO compounds for free. Use their diagnostic tool to determine impact before committing compute.

4. **Monitor solution diversity alongside accuracy.** ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) shows RLVR destroys 67% of solution coverage at trajectory entry points, invisible to standard metrics. Add pass@K, solution coverage, and diversity metrics to your evaluation dashboard. Consider staged SFT-DPO-RLVR pipelines to preserve diversity.

5. **Adopt [DA3PO](https://arxiv.org/abs/2608.27982) for drop-in GRPO improvement.** Difficulty-aware advantage amplification requires minimal code changes and consistently outperforms standard GRPO by utilizing hard-to-sample correct responses that DAPO underutilizes.

---

## 🔍 Implications for Post-Training Strategy

1. **Rethink pipeline ordering with stage-aware design.** [TailSFT](https://arxiv.org/abs/2608.25756) shows SFT checkpoint quality compounds in RL, and [Is Next-Chunk RL Better than SFT?](https://arxiv.org/abs/2608.23256) shows mixed SFT achieves higher post-RLVR ceilings at 60x less compute. Invest more in SFT data quality and checkpoint selection before committing to RL compute.

2. **Choose your post-training method by task characteristics.** The emerging decision framework: [OPD](https://arxiv.org/abs/2608.27960) when you have a strong teacher and limited compute; [GRPO](https://github.com/huggingface/trl) when you need to push past teacher quality; [RLVR](https://arxiv.org/abs/2608.24696) when you have verifiable tasks; [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351) when diversity preservation matters. Use [Consolidating RLVR](https://arxiv.org/abs/2608.27409) to choose fusion paradigm.

3. **Build RLVR diversity monitoring into your pipeline.** The evidence is now overwhelming: RLVR narrows solution space at trajectory entry ([Locked at the Entrance](https://arxiv.org/abs/2608.29188)), compresses rewardable support ([WK34 support reshaping](https://arxiv.org/abs/2608.00220)), and degrades best@N ([WK34 RLVR trainability](https://arxiv.org/abs/2608.00220)). Implement [Weak-Model Guidance](https://arxiv.org/abs/2608.27420) as a simple mitigation, or [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351) for stronger diversity preservation.

4. **Invest in credit assignment infrastructure.** [VICT](https://arxiv.org/abs/2608.28128) (verifier tracing) and [FARCA](https://arxiv.org/abs/2608.24350) (counterfactual evidence) show credit assignment is advancing rapidly. VICT's approach of reusing verifier internals rather than training critics is particularly practical. Evaluate whether your verifiers expose enough structure for VICT-style tracing.

5. **Use [batch size scaling rules](https://arxiv.org/abs/2608.29296) to optimize training costs.** Square-root LR scaling with Adam produces batch-size-invariant curves. Larger batches reduce time-to-target only when throughput gains exceed sampling penalties -- use this decision rule before scaling up hardware.

---

## 👀 Watch List

| Technology | First Noted | Status | This Week's Movement |
|-----------|-------------|--------|---------------------|
| GRPO impossibility tradeoff | WK30 | 🔬 Research-only | No new fixes; [DA3PO](https://arxiv.org/abs/2608.27982) addresses hard-prompt dimension |
| Self-play for open-ended RL | WK30 | 🧪 Early adoption | No major new results post-WK34's [SPADE](https://arxiv.org/abs/2608.19197) |
| Entropy-scaled trust regions (ESTR) | WK30 | ❄️ Cooling | No replication (4 weeks stale) |
| Dense reward collapse (dark room) | WK30 | ❄️ Cooling | No fix proposed (4 weeks stale) |
| Adaptive rollout allocation (VIGOR) | WK30 | ❄️ Cooling | No replication (4 weeks stale) |
| GRPO on continuous control | WK30 | ❄️ Cooling | No progress (4 weeks stale) |
| On-policy distillation as GRPO alternative | WK31 | 🚀 Breakout | 📈 6 papers + [TRL AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0); graduating to mainstream |
| Token-level credit for GRPO | WK31 | 🧪 Early adoption | 📈 [VICT](https://arxiv.org/abs/2608.28128) (EMNLP), [FARCA](https://arxiv.org/abs/2608.24350), [RCCA](https://arxiv.org/abs/2608.27906) |
| Meta-learned reward shaping | WK31 | 🧪 Early prototype | No follow-up (3 weeks stale) |
| NVIDIA RL framework (Molt) | WK31 | 🚀 Production-ready | No updates; [NeMo-Aligner](https://github.com/NVIDIA/NeMo-Aligner) stagnating |
| Harness-native RL training | WK34 | 🧪 Early adoption | [Prime Agent](https://arxiv.org/abs/2608.23552) continues; no second wave yet |
| RLVR support collapse | WK34 | 🔬 Research-only → 🧪 Early adoption | 📈 ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) deepens; mitigations proposed |
| RL reward hacking generalization | WK34 | 🧪 Early adoption | [Privacy Without Regret](https://arxiv.org/abs/2608.26324) links DP to reward hacking |
| Multi-reward saturation management | WK34 | 🧪 Early prototype | 📈 [JudgePanel AdaReward](https://arxiv.org/abs/2608.29168) adds adaptive rebalancing |
| ES-GRPO hybrids | WK35 | 🧪 Early prototype | New -- [Ba et al.](https://arxiv.org/abs/2608.27351) first systematic comparison |
| Stage-aware pipeline design | WK35 | 🧪 Early prototype | New -- [TailSFT](https://arxiv.org/abs/2608.25756) + [Is RL > SFT?](https://arxiv.org/abs/2608.23256) |
| Generative reward modeling | WK35 | 🧪 Early prototype | New -- [RubricRM](https://arxiv.org/abs/2608.26956) via dynamic rubrics |

**Graduation:** On-policy distillation graduates from Watch List to mainstream coverage. With 6 papers in one week, [TRL](https://github.com/huggingface/trl) infrastructure support, and production-ready results, OPD is no longer "promising" -- it is an established post-training technique.

---

## 🔮 Contrarian View

### What the community may be overestimating

**On-policy distillation as a universal replacement for RL.** Six papers and a [TRL](https://github.com/huggingface/trl) trainer create compelling momentum, but OPD has a ceiling: it cannot exceed teacher quality. [Is Next-Chunk RL Better than SFT?](https://arxiv.org/abs/2608.23256) shows mixed SFT outperforms RL under non-CoT data -- but this finding may not generalize to domains where reasoning chains are essential. [Open-MOPD](https://arxiv.org/abs/2608.19098)'s 83.4% headroom recovery means 16.6% remains unreachable via distillation. Teams adopting OPD as an RL replacement rather than complement risk leaving significant capability on the table.

### What the community may be underestimating

**The compounding effect of pipeline stage quality.** [TailSFT](https://arxiv.org/abs/2608.25756)'s 4% pass@1 gain from better SFT initializations compounds with every downstream stage. ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) shows RLVR diversity loss concentrates at trajectory entry -- the very tokens most influenced by SFT priors. [ERPO](https://arxiv.org/abs/2608.23311) shows Query-KL (input-side regularization) outperforms Policy-KL (response-side). All three findings point to the same insight: **the most impactful optimization is often upstream of RL**, in data curation, SFT checkpoint selection, and input distribution design. The community continues to focus disproportionately on RL algorithm improvements while neglecting the pre-RL stages that determine the RL ceiling.

---

## 🧭 Strategic Analysis

**Short-term (0--6 months):**
- [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0) will become the default open-source RL training stack. Expect rapid adoption of AsyncDistillationTrainer for OPD workflows.
- [TailSFT](https://arxiv.org/abs/2608.25756)-style pre-RL checkpoint optimization will become standard practice for teams with iterative post-training pipelines.
- RLVR diversity monitoring (pass@K, coverage metrics) will be added to major training frameworks following ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188) and [WK34's support reshaping](https://arxiv.org/abs/2608.00220).
- [DA3PO](https://arxiv.org/abs/2608.27982) and [ERPO](https://arxiv.org/abs/2608.23311) will be adopted as drop-in improvements to existing GRPO/RLVR pipelines.

**Mid-term (6--18 months):**
- On-policy distillation will be integrated into standard post-training recipes alongside SFT and RL, creating SFT-OPD-RL three-stage pipelines. [Open-MOPD](https://arxiv.org/abs/2608.19098)'s multi-teacher architecture will enable specialist-to-generalist distillation at scale.
- [VICT](https://arxiv.org/abs/2608.28128)-style verifier-instrumented credit assignment will replace outcome-only training for tasks with structured verifiers.
- [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351) will emerge as the preferred approach for diversity-sensitive post-training (safety, alignment, creative tasks).
- [Distributed RL training](https://arxiv.org/abs/2608.27046) will be commoditized through framework support, lowering the barrier for smaller teams.

**Long-term (2--5 years):**
- Stage-aware pipeline design will be automated -- ML systems will optimize the entire SFT-OPD-RL pipeline jointly rather than tuning each stage independently.
- RLVR diversity preservation will be solved at the algorithmic level through ES-RL hybrid architectures, input-side regularization ([ERPO](https://arxiv.org/abs/2608.23311)), and learned curriculum design.
- Credit assignment will be fine-grained enough to enable single-step policy updates, eliminating the need for multi-rollout group sampling.

---

## 🎯 Personalized Relevance

| Area | Score | This Week's Highlight |
|------|-------|----------------------|
| GRPO and preference optimization advances | 10/10 | [DA3PO](https://arxiv.org/abs/2608.27982) (drop-in improvement), [ERPO](https://arxiv.org/abs/2608.23311) (EMNLP), [DPO beta disentangling](https://arxiv.org/abs/2608.27032) |
| Reward modeling and verification | 9/10 | [RubricRM](https://arxiv.org/abs/2608.26956) (generative RM), [JudgePanel](https://arxiv.org/abs/2608.29168) (adaptive multi-reward) |
| Process reward models and verifiers | 9/10 | [VICT](https://arxiv.org/abs/2608.28128) (EMNLP, verifier-instrumented credit), [FARCA](https://arxiv.org/abs/2608.24350) (factual credit) |
| RL for reasoning (math, code, planning) | 9/10 | [TailSFT](https://arxiv.org/abs/2608.25756) (SFT compounds in RL), [ERR+](https://arxiv.org/abs/2608.28771) (entropy rewards) |
| Training infrastructure and efficiency | 10/10 | [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0), [batch scaling](https://arxiv.org/abs/2608.29296), [distributed RL reference](https://arxiv.org/abs/2608.27046) |
| On-policy distillation | 10/10 | [RA-OPD](https://arxiv.org/abs/2608.27960), [OPDVR](https://arxiv.org/abs/2608.24696), [Open-MOPD](https://arxiv.org/abs/2608.19098), [critical review](https://arxiv.org/abs/2608.25936), [TRL AsyncDistillationTrainer](https://github.com/huggingface/trl/releases/tag/v1.11.0) |
| Multi-agent RL | 6/10 | No major multi-agent results; [JudgePanel](https://arxiv.org/abs/2608.29168) uses panel deliberation |

---

## ✅ Recommendations

### For LLM training teams
1. **Upgrade to [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM 0.28](https://github.com/vllm-project/vllm/releases/tag/v0.28.0)** -- 1.44--1.59x GRPO speedup via native vLLM server and NCCL weight sync
2. **Apply [TailSFT](https://arxiv.org/abs/2608.25756) filtering** before RL to focus SFT on under-modeled data; 4% absolute pass@1 gain compounds in subsequent GRPO
3. **Pilot [RA-OPD](https://arxiv.org/abs/2608.27960) or [OPDVR](https://arxiv.org/abs/2608.24696)** for one distillation workload using [TRL](https://github.com/huggingface/trl)'s new AsyncDistillationTrainer
4. **Add diversity monitoring** (pass@K, coverage) to RLVR pipelines per ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188)
5. **Implement [DA3PO](https://arxiv.org/abs/2608.27982)** as a drop-in GRPO improvement -- minimal code change, consistent gains on hard prompts

### For post-training strategists
1. **Adopt stage-aware pipeline design** per [TailSFT](https://arxiv.org/abs/2608.25756) -- evaluate SFT checkpoints by downstream RL performance, not standalone metrics
2. **Use [batch size scaling rules](https://arxiv.org/abs/2608.29296)** (square-root LR with Adam) before scaling up hardware; wrong batch sizes waste compute
3. **Read [Besta et al.](https://arxiv.org/abs/2608.27046)** as the reference for distributed RL training architecture decisions
4. **Consider [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351)** for diversity-sensitive tasks where RLVR narrows the solution space
5. **Evaluate multi-domain RLVR fusion** per [Consolidating RLVR](https://arxiv.org/abs/2608.27409) -- choose Merge, Mix-RL, or MOPD based on your domain overlap

### For everyone
1. Read [TailSFT](https://arxiv.org/abs/2608.25756) -- the most practically impactful paper of the week (SFT quality compounds in RL)
2. Track the OPD explosion -- six papers in one week signals a paradigm shift in post-training
3. Monitor the [TRL](https://github.com/huggingface/trl)+[vLLM](https://github.com/vllm-project/vllm) stack convergence -- this is becoming the default

---

## 🏆 Executive Takeaways

### Top 5 Technical Advances
1. **[TRL v1.11.0 + vLLM v0.28.0 infrastructure consolidation](https://github.com/huggingface/trl/releases/tag/v1.11.0)** -- native vLLM server, RL lifecycle gRPC, 1.44--1.59x GRPO speedup (10 min)
2. **[On-policy distillation explosion](https://arxiv.org/abs/2608.27960)** -- six papers validating OPD from different angles; dominant research paradigm (25 min combined)
3. **[TailSFT: SFT quality compounds in RL](https://arxiv.org/abs/2608.25756)** -- filtered SFT on tails yields +4% pass@1 in GRPO; stage-aware pipeline design (10 min)
4. **[VICT: Verifier-instrumented credit tracing](https://arxiv.org/abs/2608.28128)** -- EMNLP 2026; credit from verifier internals without critics or process labels (12 min)
5. **[RLVR narrows at the entrance](https://arxiv.org/abs/2608.29188)** -- 67% coverage loss concentrated at trajectory entry; parameter interpolation recovers 37% (10 min)

### Top 5 Business Developments
1. **[TRL + vLLM same-day release](https://github.com/huggingface/trl/releases/tag/v1.11.0)** -- RL training stack consolidation; AsyncDistillationTrainer with MOPD (10 min)
2. **[NVIDIA Vera Rubin GPU announcement](https://developer.nvidia.com/blog/)** -- next-gen hardware for RL training economics (5 min)
3. **[Prime Intellect enters agentic RL](https://arxiv.org/abs/2608.23552)** -- 95.5% ARC-AGI-3 RHAE with open-source persistent harness (10 min)
4. **[verl ecosystem expansion](https://github.com/volcengine/verl)** -- DeepSeek V4 QAT; Chinese AI ecosystem growing (5 min)
5. **[NeMo-Aligner stagnation](https://github.com/NVIDIA/NeMo-Aligner)** -- 17+ months without release; NVIDIA pivoting to hardware (2 min)

### Top 5 Must-Read Resources
1. [TailSFT: Filtered Fine-Tuning Improves Post-Training Performance](https://arxiv.org/abs/2608.25756) (10 min)
2. [VICT: Verifier-Instrumented Credit Tracing](https://arxiv.org/abs/2608.28128) (12 min)
3. [Locked at the Entrance: Where RLVR Narrows the Solution Space](https://arxiv.org/abs/2608.29188) (10 min)
4. [Performance Foundations of Distributed Reasoning LMs](https://arxiv.org/abs/2608.27046) (15 min)
5. [Demystifying RL Post-Training of Language Models](https://arxiv.org/abs/2608.24949) (12 min)

---

## 📌 What Leaders Should Do Next Week

1. **Upgrade to [TRL v1.11.0](https://github.com/huggingface/trl/releases/tag/v1.11.0) + [vLLM v0.28.0](https://github.com/vllm-project/vllm/releases/tag/v0.28.0)** in a staging environment -- the 1.44--1.59x GRPO speedup is free performance
2. **Run [TailSFT](https://arxiv.org/abs/2608.25756) diagnostic** on your SFT data to quantify redundancy and potential downstream RL gains
3. **Add pass@K and solution diversity metrics** to RLVR training dashboards per ["Locked at the Entrance"](https://arxiv.org/abs/2608.29188)
4. **Pilot on-policy distillation** using [TRL](https://github.com/huggingface/trl)'s new AsyncDistillationTrainer with [OPDVR](https://arxiv.org/abs/2608.24696) on one reasoning workload
5. **Implement [DA3PO](https://arxiv.org/abs/2608.27982) difficulty-aware advantages** on your existing GRPO pipeline -- minimal code change, consistent improvement
6. **Read [Besta et al.](https://arxiv.org/abs/2608.27046)** if planning to scale RL training -- the first systematic reference for distributed RL architecture
7. **Evaluate whether [ES-GRPO hybrids](https://arxiv.org/abs/2608.27351)** could address diversity concerns in your RLVR pipelines
8. **Update WK34 action items:** Test [SimpleOPD](https://arxiv.org/abs/2608.14277) with [TRL](https://github.com/huggingface/trl) v1.11.0 AsyncDistillationTrainer; verify [SA-MRPO](https://arxiv.org/abs/2608.16072) implementation; check [RLVR support reshaping](https://arxiv.org/abs/2608.00220) mitigation status

---

*Sources: 28+ arXiv papers, 25 TRL PRs, 256 vLLM PRs, 10 verl PRs, NVIDIA Developer Blog, Anthropic Research, HuggingFace Blog, Google Scholar, Semantic Scholar*
*Prior report: WK34 (August 16--22, 2026)*
*Next report: WK36 (August 30 -- September 5, 2026)*

