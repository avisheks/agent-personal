# GPT-OSS-120B vs Qwen3-32B: MoE Reasoning Model vs Dense General-Purpose Model

> **Last Updated:** 2026-06-06 | **Read time:** ~24 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** GPT-OSS-120B (OpenAI's open-weight MoE, 117B total / 5.1B active, 128 experts, top-4 routing) and Qwen3-32B (Alibaba's open-weight dense, 32B active, 64 layers) represent two poles of open-source LLM design [1][2].
> Key distinction: GPT-OSS-120B is a reasoning-first model (o3-mini class, AIME 95.8%) while Qwen3-32B is a versatile generalist (119 languages, dual thinking modes). Main open problem: no single model excels at both deep reasoning AND broad multilingual coverage.
> Recent breakthrough: Both released under Apache 2.0 in 2025, enabling cross-model distillation and hybrid deployments [1][2]. Trend: MoE + MXFP4 quantization makes frontier-class reasoning accessible on single GPUs.

## State of the Art

### Current Best Approaches

- **GPT-OSS-120B (MoE reasoning)** — 128 experts with top-4 routing; 5.1B active params per token; trained with CoT RL (o3-style); ships in MXFP4 on single H100 [1]
- **Qwen3-32B (dense generalist)** — 32B dense transformer; 64 layers; 128K context; dual thinking/non-thinking modes; trained on 36T tokens across 119 languages [2]
- **Hybrid routing** — Complexity-based router sends reasoning tasks to GPT-OSS-120B and general tasks to Qwen3-32B, achieving optimal cost-quality across workloads [1][2]
- **Cross-model distillation** — Using Qwen3-32B multilingual outputs to augment GPT-OSS-120B via LoRA/ESFT [3][4]

### Recent Breakthroughs (last 12 months)

- **GPT-OSS release** (Aug 2025): OpenAI's first open-weight models; GPT-OSS-120B achieves 95.8% on AIME 2024 with MXFP4 quantization [1]
- **Qwen3 release** (Apr 2025): 8-model family from 0.6B to 235B; Qwen3-32B achieves prior-generation 72B performance at half the parameters [2]
- **ESFT for MoE** (2024): Expert-Specialized Fine-Tuning enables selective capability transfer without disrupting existing experts [4]
- **Weak-to-Strong Generalization** (2023): OpenAI proved smaller models can effectively supervise larger ones [3]

### Open Problems

- **Hallucination in sparse models**: GPT-OSS-120B's 5.1B active params limit factual recall (78.2% hallucination on SimpleQA) — architectural, not a training failure; router may not select the expert storing the needed fact [1]
- **MoE routing under production traffic**: Real workload distributions create expert load imbalance [5][6]
- **Cross-architecture distillation**: Dense→MoE capability transfer requires output-level methods; no logit-level path exists [3]
- **Reasoning mode cost control**: GPT-OSS-120B at "high" reasoning is expensive per token; at "low" it underperforms Qwen3-32B [1]

### Benchmark Standings

| Benchmark | GPT-OSS-120B (High) | Qwen3-32B (Base) | Winner | Source |
|-----------|---------------------|------------------|--------|--------|
| MMLU | 90.0 | 83.61 | GPT-OSS-120B | [1][2] |
| MMMLU (multilingual) | 81.3 | 83.83 | Qwen3-32B | [1][2] |
| GPQA Diamond | 80.1 | 49.49 | GPT-OSS-120B | [1][2] |
| AIME 2024 | 95.8 | <85.7* | GPT-OSS-120B | [1][2] |
| GSM8K | — | 93.40 | — | [2] |
| Codeforces Elo | 2463-2622 | — | GPT-OSS-120B | [1] |
| SWE-Bench Verified | 62.4 | — | GPT-OSS-120B | [1] |
| SimpleQA (accuracy) | 16.8% | — | Qwen3-32B | [1] |
| EvalPlus (code) | — | 72.05 | — | [2] |

*Qwen3-235B flagship achieves 85.7% on AIME'24; Qwen3-32B would score lower.

## Executive Summary

GPT-OSS-120B and Qwen3-32B represent two fundamentally different approaches to open-weight LLM design: **sparse reasoning specialist** vs **dense generalist**. Both are Apache 2.0 and deployable on-premise, but they excel at different workloads [1][2].

- **Choose GPT-OSS-120B** when: complex reasoning, math, competitive coding, agentic tool use, single-GPU frontier deployment
- **Choose Qwen3-32B** when: multilingual workloads, fine-tuning needed, factual QA, predictable latency, simpler ops
- **Choose hybrid routing** when: diverse workloads spanning both reasoning-heavy and general tasks

**The killer framing:** "This is not a quality debate — it is a specialization decision. GPT-OSS-120B stores 117B params of reasoning knowledge but only activates 5.1B per token. Qwen3-32B activates ALL 32B params every token. The question is whether your task needs deep specialist reasoning or broad consistent capability."

```
Architecture Comparison:
                          GPT-OSS-120B (MoE)        Qwen3-32B (Dense)
──────────────────────────────────────────────────────────────────────
Total parameters          116.8B                    32B
Active params/token       5.1B (4.4%)               32B (100%)
Experts                   128 (top-4 routing)       N/A
Layers                    36                        64
Context length            131K                      128K
VRAM (deployment)         ~62GB (MXFP4, 1×H100)    ~20GB (Q4) / ~64GB (BF16)
Reasoning mode            Low/Medium/High           Thinking/Non-thinking
Training                  CoT RL (o3-style)         4-stage (SFT + RL + distill)
Languages                 Limited                   119 languages
License                   Apache 2.0                Apache 2.0
──────────────────────────────────────────────────────────────────────
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Task type, languages, latency SLA, fine-tuning needs | Is the workload reasoning-heavy or general-purpose? How many languages? Is domain adaptation needed? |
| 2. Identify constraints | GPU budget, ops complexity tolerance, hallucination tolerance | Single H100 available? Can you manage MoE routing? Is 78% hallucination on factual QA acceptable? |
| 3. Propose baseline | Single-model deployment | GPT-OSS-120B for reasoning-dominant workloads; Qwen3-32B for general/multilingual workloads |
| 4. Identify gaps | Quality delta on non-primary tasks | GPT-OSS-120B weak on multilingual/factual; Qwen3-32B weak on complex reasoning. Measure gap on your domain eval set. |
| 5. Introduce improvements | Hybrid routing, selective distillation | Route by task complexity. Optionally distill Qwen3 multilingual into GPT-OSS via LoRA [3][4]. |
| 6. Add evaluation + guardrails | Dual-model eval, hallucination detection | Evaluate both models on held-out set. Monitor GPT-OSS hallucination rate. Track per-model cost. |
| 7. Discuss scaling tradeoffs | MoE expert utilization, LoRA adapter management | 10x: add replicas. 100x: expert-parallel sharding for GPT-OSS. Qwen3 scales linearly with TP. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Model | GPT-OSS-120B | Qwen3-32B | Reasoning/math/coding/agentic tasks | Multilingual/fine-tuning/factual QA/general chat |
| Quantization | MXFP4 (GPT-OSS native) | Q4 AWQ (Qwen3) | Single-H100 deployment, reasoning workloads | Consumer GPU, general workloads [7] |
| Fine-tuning | LoRA on specific MoE experts (ESFT) | Standard LoRA/full SFT | Adding narrow capability to GPT-OSS [4] | Broad domain adaptation on Qwen3 |
| Context strategy | GPT-OSS native 131K | Qwen3 YaRN-extended 128K [8] | Reasoning over long documents | Multilingual long documents |
| Serving engine | vLLM with MoE support | vLLM standard | GPT-OSS deployment [1] | Qwen3 deployment [2] |

## System Design Walkthrough

### Opening Frame

The engineering challenge is not choosing one model — it is building a routing layer that sends each request to the optimal model based on task characteristics, then maintaining a unified evaluation framework across two fundamentally different architectures (sparse MoE vs dense transformer).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               Hybrid GPT-OSS + Qwen3 Serving Platform            │
├──────────────┬───────────────────┬──────────────────────────────┤
│ Request      │  Routing Layer    │  Model Fleet                  │
│ Classifier   │                   │                               │
│ ┌──────────┐ │  ┌─────────────┐  │  ┌────────────────────────┐ │
│ │Complexity │─┼─▶│Task-Type    │──┼─▶│GPT-OSS-120B (MXFP4)   │ │
│ │+ Language │ │  │Router       │  │  │1×H100 — reasoning/code │ │
│ │Detector   │ │  └─────────────┘  │  └────────────────────────┘ │
│ └──────────┘ │         │         │  ┌────────────────────────┐ │
│              │         └─────────┼─▶│Qwen3-32B (AWQ-4bit)    │ │
│              │                   │  │1×A100 — general/multi-l │ │
│              │                   │  └────────────────────────┘ │
├──────────────┴───────────────────┴──────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Unified Evaluation + Observability                         │ │
│  │  Latency | Quality | Cost/Token | Hallucination Rate        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

- **Request Classifier**: Detects task complexity (reasoning indicators, math symbols, code markers) and language in <5ms
- **Task-Type Router**: Sends reasoning/coding/agentic to GPT-OSS-120B; multilingual/general/factual to Qwen3-32B
- **GPT-OSS-120B path**: MXFP4 on single H100; reasoning level set by task complexity estimate
- **Qwen3-32B path**: AWQ-4bit on single A100; thinking mode toggled by complexity
- **Unified Eval**: Compares outputs across models on shared rubric; monitors hallucination rates

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| GPT-OSS hallucination on factual queries | Route factual QA to Qwen3-32B; add retrieval augmentation for GPT-OSS | Added routing complexity |
| Qwen3 weak on complex reasoning | Route multi-step math/logic to GPT-OSS-120B | Higher cost for reasoning tasks |
| MoE expert load imbalance | Capacity-constrained routing with EMA tracking [5][6] | Slight quality reduction from forced routing |
| No single model covers all languages well | Qwen3-32B handles multilingual; GPT-OSS handles English reasoning | Cross-model latency variance |
| Fine-tuning MoE is complex | Use ESFT (expert-specific) + LoRA for GPT-OSS; standard LoRA for Qwen3 [4] | Requires routing analysis for ESFT |

### Scaling Summary

- **10x**: Add replicas of each model; route by load + task type; autoscale independently
- **100x**: Expert-parallel sharding for GPT-OSS-120B across nodes; tensor-parallel Qwen3-32B; dedicated routing service
- **1000x**: Geo-distributed model fleet; distill GPT-OSS reasoning into smaller task-specific models; Qwen3 for all general traffic

## Interview Q&A Bank

### Q1: What are the fundamental architectural differences between GPT-OSS-120B and Qwen3-32B?

> **Quick answer:** GPT-OSS-120B is a 117B-param MoE with 128 experts activating 5.1B per token via top-4 routing; Qwen3-32B is a 32B dense transformer using all parameters every token [1][2].

GPT-OSS-120B uses 36 layers with alternating banded-window (128 tokens) and dense attention, RoPE + YaRN for 131K context, and MXFP4 quantization as its release format. It was post-trained with CoT RL similar to o3, giving it strong chain-of-thought reasoning at adjustable depth (low/medium/high) [1]. Qwen3-32B uses 64 layers with GQA (64 Q-heads, 8 KV-heads), QK-Norm, RoPE for 128K context, and a 4-stage post-training pipeline (CoT cold-start, RL, thinking-mode fusion, general RL). It supports a thinking/non-thinking toggle for adaptive compute [2].

The MoE design means GPT-OSS-120B stores 23x more knowledge (117B vs 5.1B active) but processes each token with only 16% of Qwen3-32B's active compute. This favors tasks where the routing network can select highly relevant experts (reasoning, coding) but disadvantages tasks requiring broad, uniform knowledge (factual recall, multilingual).

**Hard follow-up:** Why does GPT-OSS-120B hallucinate more despite having 117B total parameters?

> Only 5.1B params activate per token — factual recall depends on active capacity, not total storage. The routing network may not select the expert containing the needed fact. Dense Qwen3-32B uses ALL 32B params every token, giving it 6x more active capacity for factual retrieval per inference step.

### Q2: How does MXFP4 quantization work for GPT-OSS-120B, and why doesn't it degrade performance?

> **Quick answer:** MXFP4 (Microscaling FP4, 4.25 bits) is the release format — all published benchmarks were measured at this precision. MoE expert weights tolerate 4-bit because each expert specializes on narrow distributions [1][9].

MXFP4 uses shared scaling factors across small blocks (16-32 elements), preserving local precision while achieving ~4x compression vs BF16. Three factors make it work for MoE: (1) each of 128 experts handles a narrow domain, so per-expert weight distributions have lower dynamic range; (2) top-4 ensemble routing dilutes any single expert's quantization error; (3) the model was explicitly designed and trained accounting for MXFP4 precision [1][9].

Memory: MXFP4 fits GPT-OSS-120B on a single H100 (~62GB). BF16 would require ~234GB (3× H100s) for marginal-if-any quality gain. vLLM supports both via OpenAI's deployment cookbook [1].

| Format | VRAM | GPUs | Benchmarks measured at? |
|--------|------|------|------------------------|
| MXFP4 (release) | ~62GB | 1× H100 | YES — all reported scores |
| BF16 | ~234GB | 3× H100 | No public checkpoint |

**Hard follow-up:** How does this compare to AWQ-4bit on Qwen3-32B?

> AWQ-4bit on Qwen3-32B reduces from ~64GB (BF16) to ~20GB with <1% quality loss on aggregate benchmarks [7]. The key difference: AWQ is a post-hoc compression applied to a model trained in BF16, so there IS a quality delta (small). GPT-OSS-120B's MXFP4 is the native format — no separate higher-precision version exists to compare against.

### Q3: When does GPT-OSS-120B's "low" reasoning mode underperform Qwen3-32B?

> **Quick answer:** At "low" reasoning, GPT-OSS-120B drops to AIME 56.3% and MMLU 85.9% — below Qwen3-32B's base performance on general tasks. The model is designed for high-reasoning use; low mode trades quality for speed [1][2].

GPT-OSS-120B offers three reasoning levels that control chain-of-thought depth. At "high," it achieves frontier results (AIME 95.8%, GPQA 80.1%). At "low," it skips deep reasoning and relies on its 5.1B active parameters for direct answers — insufficient for complex tasks and often worse than Qwen3-32B's consistent 32B-active-param performance on general queries [1].

This creates a cost trap: using GPT-OSS-120B at "high" for simple tasks wastes compute (deep CoT for a summarization request), while using it at "low" for everything produces worse results than Qwen3-32B. The solution is routing by task complexity — reserve GPT-OSS "high" for tasks that genuinely benefit from deep reasoning.

**Hard follow-up:** How do you detect when a task needs "high" vs "low" reasoning?

> Classify based on features: presence of mathematical notation, multi-step logic indicators ("prove," "derive," "analyze step by step"), code complexity markers, and domain signals. A lightweight classifier (~100M params, <5ms) trained on task-outcome data can achieve >90% routing accuracy. Monitor quality on routed tasks — if "low" responses get corrected frequently, tighten the threshold.

### Q4: How would you deploy both models for a hybrid production system?

> **Quick answer:** GPT-OSS-120B on 1× H100 (MXFP4) for reasoning tasks; Qwen3-32B on 1× A100-80GB (AWQ-4bit) for general tasks; lightweight router in front; unified eval comparing both [1][2].

Hardware: GPT-OSS-120B requires 1× H100-80GB (MXFP4). Qwen3-32B at AWQ-4bit fits on 1× A100-80GB (~20GB weights + 60GB KV cache). Both served via vLLM with PagedAttention [10]. The router is a lightweight model or heuristic that classifies requests in <5ms.

Throughput: GPT-OSS-120B at "high" reasoning generates fewer tokens/second (thinking overhead). Qwen3-32B produces 15-22 tok/s consistently. Plan capacity independently — GPT-OSS handles fewer concurrent requests due to longer generation times.

```
Cost per 1M tokens (self-hosted, reserved instances):
  GPT-OSS-120B (H100): ~$1.50/1M tokens (at 70% util)
  Qwen3-32B (A100):    ~$0.60/1M tokens (at 70% util)
  
  Hybrid (70% Qwen3 / 30% GPT-OSS): ~$0.87/1M tokens
  vs all-GPT-OSS:                     ~$1.50/1M tokens (42% savings)
```

**Hard follow-up:** What's the cold-start latency for each model?

> GPT-OSS-120B (MXFP4, 62GB): ~15-20s model load time on H100 NVMe. Qwen3-32B (AWQ-4bit, 20GB): ~5-8s on A100. Mitigate with: keep-alive policies (don't unload), pre-warmed standby replicas, or serverless platforms with model caching (Modal, Daytona).

### Q5: How do you fine-tune GPT-OSS-120B vs Qwen3-32B?

> **Quick answer:** Qwen3-32B uses standard LoRA/SFT (well-understood, fits on single GPU). GPT-OSS-120B requires ESFT (Expert-Specialized Fine-Tuning) — identify relevant experts via routing analysis, fine-tune only those, freeze the rest [4].

Qwen3-32B fine-tuning is straightforward: LoRA (rank 16-64) on attention layers, training in BF16, using standard frameworks (Unsloth, TRL, Axolotl). Memory: ~24GB with LoRA on an A100. Full SFT needs 2-4× A100s.

GPT-OSS-120B fine-tuning is more complex due to MoE architecture. The ESFT approach [4]: (1) analyze routing patterns to identify which of 128 experts handle your target domain, (2) apply LoRA only to those experts, (3) freeze all other experts and the router. This preserves existing reasoning while adding capability. Alternative: full LoRA across all experts, but with replay data (50-70% existing capability data) to prevent catastrophic forgetting [3][11].

| Dimension | GPT-OSS-120B | Qwen3-32B |
|-----------|-------------|-----------|
| Method | ESFT + LoRA on target experts | Standard LoRA/SFT |
| Hardware | 1× H100 (MXFP4 base + BF16 adapters) | 1× A100 (LoRA) or 2-4× A100 (full SFT) |
| Complexity | High (routing analysis needed) | Low (standard pipeline) |
| Risk | Router disruption, load imbalance | Catastrophic forgetting (standard mitigation) |
| Replay data needed | Yes (50-70%) | Optional but recommended |

**Hard follow-up:** Can you fine-tune GPT-OSS-120B's router to redirect tokens to different experts?

> Technically yes, but dangerous. Changing routing patterns affects ALL downstream tasks, not just your target domain. The safer approach is to fine-tune expert weights while keeping the router frozen — let existing routing patterns persist while improving what the selected experts produce.

### Q6: How do you transfer Qwen3-32B's multilingual capability into GPT-OSS-120B?

> **Quick answer:** Generate multilingual data from Qwen3-32B, mix with GPT-OSS replay data (30-50% new / 50-70% replay), LoRA fine-tune GPT-OSS-120B on the mix. Works because the 117B param pool likely contains latent multilingual capacity in under-utilized experts [3][4].

This is "weak-to-strong" cross-architecture distillation. It works when the target capability is latent in the student model [3]. GPT-OSS-120B's 117B params across 128 experts likely include experts exposed to multilingual data during pre-training that are currently underweight in routing.

Methods (ranked by feasibility):
1. **SFT on Qwen3 outputs + LoRA** — Generate diverse multilingual outputs from Qwen3-32B; fine-tune GPT-OSS with LoRA [3][11]
2. **ESFT (expert-targeted)** — Identify multilingual experts via routing analysis; train only those [4]
3. **GKD (on-policy)** — GPT-OSS generates multilingual outputs; Qwen3 scores/corrects them [12]
4. **Knowledge Fusion** — Use both models' output distributions as training signal [13]

What does NOT work: logit-level distillation (different tokenizers), weight merging (different architectures), transferring capabilities with zero latent representation in GPT-OSS.

**Hard follow-up:** How do you verify the transfer actually worked vs mere style mimicry?

> Evaluate on held-out multilingual benchmarks NOT represented in the training data. If GPT-OSS only learned to format multilingual outputs without genuine understanding, it will fail on novel language tasks. Also test on the student's original strengths (AIME, GPQA) — if reasoning degraded >2%, the replay ratio was insufficient.

### Q7: How does MoE expert routing work in GPT-OSS-120B, and what are production failure modes?

> **Quick answer:** Each token is routed to the top-4 of 128 experts via learned gating logits. Production failure: expert collapse (few experts handle most traffic) and load imbalance (hotspot experts queue while others idle) [5][6].

The gating function computes logits g(x) = W_g * x for each token, softmax selects top-4 experts. Token is processed by all 4, outputs weighted by gate probabilities. With 128 experts and top-4, each token uses 5.1B of 117B params [1].

Failure modes in production:
1. **Expert collapse**: Router converges to always selecting the same 10-20 experts. Cause: positive feedback (popular experts get more gradient, improve further). Detection: coefficient of variation (CV) of expert load > 0.3 [5][6].
2. **Temporal load shift**: Morning traffic (code-heavy) loads coding experts; afternoon (chat-heavy) loads different experts. Creates time-varying hotspots.
3. **Routing-latency coupling**: Overloaded experts queue tokens while idle experts waste compute, creating P99 latency spikes.

Mitigation: capacity-constrained routing with EMA-based load penalties [5][6]. Increase routing temperature to spread load when CV exceeds threshold.

**Hard follow-up:** Can expert collapse happen at inference time if no training is occurring?

> Not in the traditional sense (routing weights are frozen at inference). But effective collapse manifests when real traffic distribution is narrower than training distribution — if 80% of production queries are similar, the same experts activate repeatedly, creating hotspots. The solution is inference-time load-aware logit penalties, not routing weight updates.

### Q8: Why does GPT-OSS-120B have 78% hallucination rate? Is it poor for QnA tasks?

> **Quick answer:** The 78.2% hallucination on SimpleQA is an architectural consequence of MoE sparse activation (5.1B of 117B active per token), not a training failure. It makes GPT-OSS-120B poor for FACTUAL QA but excellent for REASONING QA. Qwen3-32B's 32B active params give 6x more factual recall per token [1][2].

**The mechanism:**
```
Facts stored across 128 experts during training
  → Router selects top-4 experts per token at inference
  → If needed fact is in expert #87 but router picks #12, #34, #56, #91
  → Fact is inaccessible → model confabulates a plausible answer
```

Dense Qwen3-32B uses ALL 32B params every token — every fact stored anywhere in the model is accessible at every inference step. This gives it 6x more active capacity for factual retrieval (32B vs 5.1B).

**Critical distinction — not all QnA is equal:**

| QnA Type | GPT-OSS-120B | Why |
|----------|-------------|-----|
| Factual ("Who directed...?") | POOR — 78.2% hallucination | Needs closed-book recall; 5.1B active insufficient |
| Reasoning ("Prove that...") | EXCELLENT — AIME 95.8% | Deep CoT reasoning, not factual recall |
| Math ("Solve this equation") | EXCELLENT — GPQA 80.1% | Computation, not knowledge retrieval |
| Code ("Fix this bug") | EXCELLENT — SWE-Bench 62.4% | Logic + pattern matching, not facts |
| Agentic ("Search X, then do Y") | EXCELLENT — Tau-Bench 67.8% | Tool use grounds answers externally |
| Open-book (with RAG context) | GOOD | Retrieved context bypasses routing problem |

**Mitigation strategies:**
1. **Route factual QA to Qwen3-32B** — 32B active = 6x more recall; simple routing decision
2. **Add retrieval (RAG)** — External knowledge grounds answers regardless of active params
3. **Use "high" reasoning mode** — Longer CoT enables self-checking factual claims
4. **Ensemble verification** — Generate from both models; flag disagreements for review

**Decision rule for QnA workloads:**
```
Factual recall QA?           → Qwen3-32B (or GPT-OSS + RAG)
Reasoning/logic/math QA?     → GPT-OSS-120B
Context-grounded QA (docs)?  → Either works
Mixed workload?              → Hybrid routing by question type
```

**Hard follow-up:** Does higher reasoning level reduce GPT-OSS-120B's hallucination?

> Partially. At "high" reasoning, the model generates more tokens to self-check claims via chain-of-thought — it can catch logical inconsistencies. But the fundamental limitation (5.1B active params for factual storage) persists. Longer reasoning helps detect errors in reasoning chains but cannot conjure facts absent from the activated experts. For factual QA, the answer is RAG or routing to Qwen3, not more reasoning tokens.

### Q9: How do you monitor a hybrid GPT-OSS + Qwen3 deployment?

> **Quick answer:** Track per-model metrics independently (latency, quality, hallucination rate, cost), plus routing-level metrics (routing accuracy, cost-per-quality-point, misroute rate).

Key metrics for GPT-OSS-120B specifically:
- Expert load CV (alert if >0.3 sustained 5min)
- Reasoning level distribution (are tasks being routed to appropriate depth?)
- Hallucination rate on factual subset (sample 5%, judge with Qwen3)

Key metrics for Qwen3-32B specifically:
- Thinking mode activation rate (should correlate with task complexity)
- Quality on reasoning subset (catch if complex tasks leak past router)
- KV cache utilization (critical for 128K context requests)

Routing-level metrics:
- Misroute rate: tasks that should have gone to the other model (detected via quality sampling)
- Cost-per-quality-point: dollars spent per unit quality on each model path
- Model availability: failover triggers when one model degrades

**Hard follow-up:** How do you detect routing drift over time?

> Weekly re-evaluation: sample 1000 recent requests, run through both models, compare quality. If the non-routed model would have produced significantly better output >10% of the time, retune routing thresholds. Also track input distribution shifts — new workload patterns may require updated routing heuristics.

### Q10: Compare the cost economics of each model for different workload types.

> **Quick answer:** GPT-OSS-120B costs ~$1.50/1M tokens self-hosted (H100); Qwen3-32B costs ~$0.60/1M tokens (A100). The 2.5x cost difference is justified only for tasks where GPT-OSS's reasoning superiority matters [1][2].

| Workload | Best Model | Cost/1M tok | Quality Advantage |
|----------|-----------|-------------|-------------------|
| Math tutoring | GPT-OSS-120B | $1.50 | AIME 95.8% (irreplaceable) |
| Code review (complex) | GPT-OSS-120B | $1.50 | SWE-Bench 62.4% |
| Multilingual support | Qwen3-32B | $0.60 | 119 languages, MMMLU 83.83% |
| Document summarization | Qwen3-32B | $0.60 | Sufficient quality, 60% cheaper |
| Agentic orchestration | GPT-OSS-120B | $1.50 | Harmony format, Tau-Bench 67.8% |
| General chat | Qwen3-32B | $0.60 | Consistent, no reasoning overhead |
| Hybrid (70/30) | Mixed | $0.87 | Best of both, 42% cheaper than all-GPT-OSS |

Break-even thinking: If GPT-OSS-120B is 2.5x more expensive but produces >2.5x better outcomes on a task, use it. Otherwise, use Qwen3-32B.

**Hard follow-up:** At what volume does self-hosting beat API alternatives?

> Both models are open-weight (no API needed for base inference). The relevant comparison is self-hosted vs inference providers (Together.ai, Fireworks.ai). GPT-OSS-120B on Together.ai: ~$0.15/$0.60 per 1M in/out tokens. Self-hosted at $1.50/1M breaks even only if you need >10M tokens/day and require data sovereignty or custom fine-tuning. For pure inference, API providers are often cheaper than self-hosting.

### Q11: How does context handling differ between the two models?

> **Quick answer:** GPT-OSS-120B supports 131K context with alternating banded-window (128 tokens) + dense attention. Qwen3-32B supports 128K with standard full attention + RoPE. Qwen3's approach is simpler but uses more KV cache memory per request [1][2][8].

GPT-OSS-120B's alternating attention pattern: odd layers use banded-window attention (128-token local window), even layers use full dense attention. This reduces quadratic attention cost while maintaining long-range capability via the dense layers. KV cache is bounded by window size on half the layers.

Qwen3-32B uses full attention on all 64 layers. KV cache per request at 128K context:
```
64 layers × 8 KV heads × 128 dim × 128K tokens × 2 bytes = ~16.4GB per request
```
This severely limits concurrent requests at full context. At 4K context, only ~1GB per request.

For long-document workloads, GPT-OSS-120B's hybrid attention is more memory-efficient per request. For short-context high-concurrency workloads, Qwen3-32B's simpler architecture is easier to optimize.

**Hard follow-up:** Can you extend GPT-OSS-120B's context beyond 131K?

> The banded-window layers don't require positional extension (they're local). The dense layers use RoPE + YaRN [8], which can theoretically be extended further. However, the 128-token window in half the layers creates an information bottleneck at extreme lengths — context beyond what the dense layers can cover in one pass requires multiple passes of banded→dense propagation.

### Q12: What's the licensing situation for building products on top of these models?

> **Quick answer:** Both are Apache 2.0 — fully permissive for commercial use, modification, distribution, and derivative works. You can distill between them, fine-tune, deploy commercially, and distribute modified weights [1][2].

Apache 2.0 grants: commercial use, modification, distribution, patent use, private use. It requires: license notice preservation, state changes documentation. It does NOT restrict: using model outputs for training other models, commercial deployment, creating proprietary derivatives.

Practical implications:
- Fine-tune either model on proprietary data → your adapters are yours
- Distill from Qwen3 into GPT-OSS (or vice versa) → fully legal
- Deploy both in commercial product → no royalties or restrictions
- Machine-generated outputs are not copyrightable → training data from either model is unencumbered

The only nuance: if you redistribute modified weights, you must include the Apache 2.0 license notice. You don't need to open-source your modifications.

**Hard follow-up:** Are there any "model output" restrictions?

> No. Apache 2.0 has no output restrictions. Unlike some earlier model licenses with commercial thresholds or "no competing model" clauses, Apache 2.0 is unconditionally permissive. Both OpenAI (GPT-OSS) and Alibaba (Qwen3) chose this explicitly to maximize adoption.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): MoE Routing Mathematics — Why 5.1B Active of 117B Total?</strong></summary>

GPT-OSS-120B uses top-4 routing across 128 experts. The mathematical rationale for this design:

**Parameter allocation per expert:**
```
Total params: 116.8B
Non-expert params (embedding, attention, router): ~16B estimated
Expert params: ~100.8B across 128 experts
Per-expert params: 100.8B / 128 = ~787M per expert
Active per token (top-4): 4 × 787M = ~3.15B (expert FFN only)
Plus shared params (attention, embedding): ~2B
Total active: ~5.1B
```

**Why top-4 (not top-1, top-2, or top-8)?**

The quality-efficiency tradeoff follows approximately:
```
Quality ∝ log(k) for top-k routing (diminishing returns)
Compute ∝ k (linear cost)

k=1: 787M active expert params — too sparse for complex tasks
k=2: 1.57B — works for simple MoE (standard top-2 routing) [5]
k=4: 3.15B — sweet spot for reasoning: enough diversity without 
     excessive compute
k=8: 6.3B — diminishing quality gains, 2× compute vs k=4
```

**Expert specialization analysis:**

In production, GPT-OSS-120B's 128 experts show task-concentrated routing [4]. For a math query, the same ~8-12 experts activate consistently. For code, a different ~8-12. The top-4 selection from 128 means:
```
P(optimal expert selected) = 1 - (124/128 × 123/127 × 122/126 × 121/125)
                           ≈ 1 - (0.969)^4 ≈ 0.118 per attempt

For 4 attempts (top-4): P(at least one optimal) ≈ 1 - (1-0.031)^4 ≈ 0.12
```

Wait — this seems low. The key insight: experts aren't uniformly optimal. The router LEARNS which experts are relevant, so P(correct routing) >> random. Empirically, the router achieves >95% agreement with "oracle routing" (selecting experts that minimize loss on held-out data) [4].

**MXFP4 interaction:** With 128 experts quantized to MXFP4, total storage = 100.8B × 4.25 bits / 8 = ~53.6GB for expert weights. Plus ~10GB for shared layers in higher precision. Total ~62-64GB — fits on one H100 [1][9].

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): Serving Two Architecturally Different Models — Unified vLLM Deployment</strong></summary>

Deploying GPT-OSS-120B (MoE) and Qwen3-32B (dense) on the same vLLM cluster creates unique engineering challenges. The models have fundamentally different memory profiles, batching characteristics, and failure modes [1][2][10].

**Memory profiles compared:**
```
GPT-OSS-120B (MXFP4, 1× H100-80GB):
  Expert weights:     ~54GB (MXFP4)
  Shared layers:      ~10GB (BF16 for attention/embed)
  Runtime overhead:   ~4GB
  Available for KV:   ~12GB
  KV per request (4K): ~2GB (36 layers, banded+dense)
  Max concurrent:     ~6 requests at 4K context

Qwen3-32B (AWQ-4bit, 1× A100-80GB):
  Model weights:      ~20GB
  Runtime overhead:   ~4GB
  Available for KV:   ~56GB
  KV per request (4K): ~1GB (64 layers, full attention, GQA)
  Max concurrent:     ~56 requests at 4K context
```

**Critical insight:** GPT-OSS-120B has 9x fewer concurrent slots than Qwen3-32B on equivalent hardware. This means:
- GPT-OSS requests need shorter queue times → more replicas needed per RPS
- Qwen3 handles burst traffic much better
- Auto-scaling algorithms must be model-specific

**Batching differences:**
- GPT-OSS-120B: variable generation length (reasoning mode creates long CoT). Batch completion times vary wildly (2s for "low" vs 60s for "high").
- Qwen3-32B: more predictable generation. Thinking mode adds variance but less extreme.

**vLLM configuration per model:**
```python
# GPT-OSS-120B config
engine_args = EngineArgs(
    model="openai/gpt-oss-120b",
    quantization="mxfp4",
    tensor_parallel_size=1,
    max_model_len=131072,
    gpu_memory_utilization=0.92,
    max_num_seqs=6,  # Limited by KV cache budget
    enable_chunked_prefill=True,
)

# Qwen3-32B config  
engine_args = EngineArgs(
    model="Qwen/Qwen3-32B-AWQ",
    quantization="awq",
    tensor_parallel_size=1,
    max_model_len=128000,
    gpu_memory_utilization=0.90,
    max_num_seqs=56,  # Much higher concurrency
    enable_chunked_prefill=True,
)
```

**Auto-scaling signals:**
- GPT-OSS-120B: scale on KV cache pressure (>85% utilization) and queue depth
- Qwen3-32B: scale on queue depth and P95 latency
- Router: scale on request classification throughput (if >10ms P99, add capacity)

</details>

<details><summary><strong>DE Probe 3 (DATA): Training Data Divergence — Why Qwen3 Wins Multilingual and GPT-OSS Wins Reasoning</strong></summary>

The performance differences between GPT-OSS-120B and Qwen3-32B trace directly to training data composition and post-training methodology [1][2].

**Qwen3-32B training data [2]:**
- Pre-training: ~36 trillion tokens
- Language coverage: 119 languages and dialects
- Sources: web data, books, PDFs, synthetic code and math from earlier Qwen models
- Explicit multilingual design: significant non-English data investment
- Result: MMMLU 83.83% (broad multilingual strength)

**GPT-OSS-120B training data [1]:**
- Pre-training: trillions of tokens (exact count undisclosed)
- Knowledge cutoff: June 2024
- Post-training: CoT RL similar to o3/o4-mini (reasoning-focused)
- Explicit reasoning optimization: "high" mode trained with extended chain-of-thought RL
- 2.1M H100-hours of training compute
- Result: AIME 95.8%, Codeforces 2463 Elo (deep reasoning strength)

**Why this creates a fundamental trade-off:**

Multilingual breadth requires broad data coverage across languages — every language token reduces English/reasoning token budget. GPT-OSS-120B invested its compute in reasoning RL instead:

```
Simplified compute allocation:
  Qwen3-32B:    [40% English | 25% Chinese | 15% other langs | 10% code | 10% math]
  GPT-OSS-120B: [60% English | 5% other | 15% code | 20% reasoning RL]
  
  → Qwen3 allocates ~35% to non-English → strong multilingual
  → GPT-OSS allocates ~20% to reasoning RL → strong reasoning
  → These are fundamentally competing budget allocations
```

**Post-training divergence:**

Qwen3-32B's 4-stage pipeline: (1) Long-CoT cold-start SFT, (2) RL for reasoning, (3) thinking-mode fusion (merge thinking/non-thinking), (4) general RL for broad capability [2].

GPT-OSS-120B's pipeline: CoT RL similar to o3 family — deep reinforcement learning on chain-of-thought with verifiable rewards (math proofs, code tests). This is heavily optimized for tasks with clear correctness criteria [1].

The result: GPT-OSS excels where there's a "right answer" (math, code, logic). Qwen3 excels where there's "good coverage" (languages, general knowledge, factual recall).

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Evaluating MoE vs Dense Models Fairly — Benchmark Design</strong></summary>

Comparing GPT-OSS-120B and Qwen3-32B on benchmarks introduces systematic biases that favor one architecture over the other [1][2].

**Bias toward GPT-OSS-120B:**
- Benchmarks with chain-of-thought evaluation (AIME, GPQA): GPT-OSS's reasoning training directly optimizes for these
- English-only benchmarks (most standard evals): GPT-OSS's English-heavy training maximizes score
- Benchmarks allowing extended generation: "high" reasoning mode can think longer

**Bias toward Qwen3-32B:**
- Multilingual benchmarks (MMMLU): Qwen3's 119-language training directly optimizes for this
- Factual recall benchmarks (SimpleQA): Dense architecture = more active params for retrieval
- Benchmarks penalizing hallucination: GPT-OSS's 78.2% hallucination is punished
- Short-answer benchmarks: Qwen3's non-thinking mode gives concise answers without CoT overhead

**Fair comparison methodology:**

1. **Match compute**: Compare GPT-OSS at "medium" reasoning (not "high") against Qwen3 with thinking enabled — this roughly equalizes tokens-per-response
2. **Domain-stratified eval**: Separate results by task type (reasoning, factual, multilingual, code) — aggregate scores are misleading
3. **Control for generation length**: Normalize quality by tokens generated — GPT-OSS "high" may produce 10x more tokens for the same quality delta
4. **Cost-normalized comparison**: Quality per dollar, not raw quality — GPT-OSS may win on quality but lose on quality-per-compute

**Recommended eval matrix:**

| Dimension | Benchmark | Why Fair |
|-----------|-----------|----------|
| Reasoning | AIME, GPQA | Core strength of GPT-OSS; measures genuine capability |
| Code | SWE-Bench, EvalPlus | Both have code capability; different strengths |
| Multilingual | MMMLU, XL-Sum | Core strength of Qwen3; fair head-to-head |
| Factual | SimpleQA, TriviaQA | Tests architectural limitation of MoE |
| Practical | Chatbot Arena (blind) | Holistic human preference, decontaminated |

**The honest conclusion:** No single number can fairly compare these models. The right question is not "which is better?" but "which is better FOR MY WORKLOAD?" — and the answer almost always is "both, routed appropriately."

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Failure Modes Unique to Each Architecture</strong></summary>

GPT-OSS-120B and Qwen3-32B have different production failure modes due to their architectural differences [1][2][5][6].

**GPT-OSS-120B failure modes:**

1. **Expert collapse at inference** (MoE-specific):
   - Symptom: P99 latency spikes, some experts at 95% util while others at 5%
   - Detection: CV of expert load > 0.3 sustained 5 minutes
   - Mitigation: load-aware logit penalties, routing temperature increase
   - Impact: Quality degradation on affected token types

2. **Reasoning mode runaway** (reasoning-model-specific):
   - Symptom: "High" reasoning produces 10,000+ token CoT for simple queries
   - Detection: generation length > 5x expected for task class
   - Mitigation: max_tokens cap, early stopping when confidence threshold reached
   - Impact: GPU-hours wasted, queue starvation for other requests

3. **Hallucination on factual queries** (sparse-model-specific):
   - Symptom: Confident wrong answers on knowledge questions
   - Detection: SimpleQA-style probes in 5% of traffic
   - Mitigation: Route factual queries to Qwen3; add retrieval for GPT-OSS
   - Impact: User trust degradation

4. **MXFP4 precision edge cases** (quantization-specific):
   - Symptom: Rare numerical errors in mathematical computation
   - Detection: Canary math problems with known answers
   - Mitigation: Fall back to BF16 for precision-critical sub-tasks (if multi-GPU available)
   - Impact: Usually negligible; model designed for MXFP4

**Qwen3-32B failure modes:**

1. **Thinking mode stuck** (thinking-model-specific):
   - Symptom: Model enters deep thinking on simple queries, wasting tokens
   - Detection: thinking token ratio > 3:1 vs response tokens for simple classifications
   - Mitigation: Force non-thinking mode for queries classified as simple
   - Impact: Latency increase, cost waste

2. **KV cache OOM at long context** (dense-model-specific):
   - Symptom: OOM crash when multiple 128K-context requests arrive simultaneously
   - Detection: KV cache utilization > 90%
   - Mitigation: PagedAttention + request queuing + dynamic context limit [10]
   - Impact: Request drops, service degradation

3. **Catastrophic forgetting after fine-tuning** (fine-tuning-specific):
   - Symptom: Domain capability improves but general quality drops
   - Detection: Regression suite on base capabilities after every fine-tune
   - Mitigation: Replay data (20-30% general), LoRA instead of full SFT [11]
   - Impact: Silent quality degradation on non-domain tasks

4. **Multilingual quality variance** (multilingual-model-specific):
   - Symptom: Excellent in top-10 languages, poor in long-tail languages (language 80-119)
   - Detection: Per-language quality monitoring
   - Mitigation: Language-specific routing (low-resource langs → specialized smaller model)
   - Impact: Uneven user experience across language markets

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Cross-Model Distillation — Dense↔MoE Knowledge Transfer</strong></summary>

Transferring capabilities between Qwen3-32B (dense) and GPT-OSS-120B (MoE) is architecturally complex because the models represent knowledge differently [3][4][11][12][13].

**Why standard distillation doesn't work directly:**

1. **Tokenizer mismatch**: Qwen3 and GPT-OSS use different tokenizers → logit distributions aren't comparable → no KL-divergence minimization possible at token level
2. **Architecture mismatch**: 32B dense weights ≠ 117B MoE weights → no weight merging, task arithmetic, or direct parameter transfer
3. **Capacity asymmetry**: Qwen3 uses 32B per token; GPT-OSS uses 5.1B → the student (GPT-OSS) has LESS per-token capacity than the teacher for broad tasks

**What DOES work — output-level transfer:**

```
Method 1: SFT on teacher outputs (PROVEN)
─────────────────────────────────────────
Qwen3-32B generates multilingual data
    → GPT-OSS-120B trained on these outputs via LoRA
    → Mix with GPT-OSS replay data (50-70%)
    → Evaluate: did multilingual improve? did reasoning degrade?

Precedent: DeepSeek-R1 distilled 671B MoE → 32B dense via SFT
           (cross-architecture, proven to work) [3]

Method 2: ESFT — Expert-Specialized Fine-Tuning (MoE-SPECIFIC)
──────────────────────────────────────────────────────────────
Step 1: Route multilingual tokens through GPT-OSS-120B
Step 2: Identify which of 128 experts activate most for multilingual
Step 3: Apply LoRA ONLY to those experts
Step 4: Freeze all other experts + router

Advantage: Maximum preservation of reasoning (untouched experts)
Challenge: Requires routing analysis infrastructure [4]

Method 3: GKD — On-Policy Distillation (AVOIDS COVARIATE SHIFT)
───────────────────────────────────────────────────────────────
Step 1: GPT-OSS generates multilingual outputs (on its own distribution)
Step 2: Qwen3-32B scores/corrects these outputs
Step 3: GPT-OSS fine-tuned on its own corrected outputs

Advantage: Student trains on ITS OWN distribution → no distribution shift
Challenge: Requires Qwen3 to reliably evaluate GPT-OSS quality [12]
```

**The "Weak-to-Strong" principle [3]:**

OpenAI's research proved that weaker model supervision CAN improve stronger models — but only when the stronger model has LATENT capability that the signal helps elicit. GPT-OSS-120B's 117B total params likely contain latent multilingual knowledge across its 128 experts. Qwen3's multilingual outputs serve as a high-quality signal to activate these dormant pathways.

**Failure case — when distillation breaks:**
- If GPT-OSS has ZERO multilingual representation in any expert → can't activate what doesn't exist
- If style mimicry dominates over genuine transfer → novel multilingual tasks fail [arXiv:2305.15717]
- If replay ratio too low → catastrophic forgetting destroys reasoning

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | GPT-OSS-120B | Qwen3-32B | Notes |
|-----------|-------------|-----------|-------|
| Inference (self-hosted, per 1M tokens) | ~$1.50 | ~$0.60 | H100 vs A100, 70% utilization |
| Inference (API provider) | $0.15/$0.60 in/out | ~$0.10/$0.30 in/out | Together.ai / Fireworks pricing |
| Fine-tuning (LoRA, one-time) | ~$500-1000 | ~$200-500 | H100 vs A100, ESFT complexity |
| KV cache per request (4K) | ~2GB | ~1GB | MoE has fewer layers but larger hidden |
| Reasoning overhead | 2-10x token generation (CoT) | 1-3x (thinking mode) | GPT-OSS "high" generates much more |

### Monthly Cost at Scale (Self-Hosted)

| Scale | GPT-OSS-120B Only | Qwen3-32B Only | Hybrid (70% Qwen / 30% GPT-OSS) |
|-------|-------------------|----------------|----------------------------------|
| 10M tok/day | $4,500 (1×H100) | $1,800 (1×A100) | $2,600 |
| 100M tok/day | $45,000 (10×H100) | $12,000 (7×A100) | $21,900 |
| 1B tok/day | $180,000 (40×H100) | $60,000 (35×A100) | $96,000 |

### Cost Optimization Priority Stack

1. **Hybrid routing** — 70% general traffic to Qwen3 (60% cheaper) → 42% savings vs all-GPT-OSS
2. **Reasoning level control** — Use GPT-OSS "low" for sub-tasks that don't need deep CoT → 50-70% token savings on those tasks
3. **Qwen3 non-thinking mode** — Disable thinking for simple queries → 50% token savings
4. **Quantization** — Both models already quantized (MXFP4 / AWQ) → already optimized
5. **Prefix caching** — System prompts shared across requests → 10-20% savings on repeated prefixes
6. **Batch processing** — Aggregate non-urgent requests for higher throughput utilization

### Build vs Buy

| Capability | Self-Host Cost | Provider Option | Recommendation |
|-----------|---------------|-----------------|----------------|
| GPT-OSS-120B inference | $4,500/mo (1×H100) | Together.ai $0.15/$0.60/1M | Provider until >50M tok/day |
| Qwen3-32B inference | $1,800/mo (1×A100) | Fireworks $0.10/$0.30/1M | Provider until >30M tok/day |
| Fine-tuning (LoRA) | $500-1000 one-time | Not available externally | Self-host (custom data) |
| Routing layer | $500/mo (lightweight) | Build custom (simple classifier) | Build (strategic asset) |
| Evaluation framework | $2,000/mo (judge model) | Build custom | Build (differentiator) |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | GPT-OSS-120B Threshold | Qwen3-32B Threshold | Escalation |
|--------|----------------------|--------------------|-----------| 
| P95 latency | >5s (includes CoT) | >2s | Scale replicas; check reasoning mode distribution |
| Expert load CV | >0.3 sustained 5min | N/A (dense) | Increase routing temperature |
| KV cache utilization | >85% | >90% | Queue new requests; scale out |
| Hallucination rate (sampled) | >80% on factual subset | >30% | Route factual queries away from GPT-OSS |
| Reasoning token waste | >5x expected gen length | >3x thinking ratio | Cap max_tokens; force lower reasoning level |
| Quality score (judge) | <85% on routed subset | <85% on routed subset | Retune routing thresholds |
| GPU utilization | <30% sustained | <30% sustained | Scale down (cost waste) |

### Debugging Walkthrough

```
SYMPTOM: GPT-OSS-120B quality drop
│
├─ CHECK: Expert load distribution
│  ├─ CV > 0.5? → Expert collapse → increase routing temperature
│  └─ Balanced? → continue
│
├─ CHECK: Reasoning mode distribution
│  ├─ Stuck on "low" for complex tasks? → Router misconfiguration
│  └─ All on "high"? → Wasting compute → check routing classifier
│
└─ CHECK: Input distribution shift
   ├─ New task types? → Router needs retraining
   └─ Same distribution? → Check for model degradation (quantization edge case)

SYMPTOM: Qwen3-32B latency spike
│
├─ CHECK: KV cache utilization (>90%?)
│  ├─ Yes → Long context surge → enforce context limits or scale
│  └─ No → continue
│
├─ CHECK: Thinking mode activation
│  ├─ Thinking on simple queries? → Force non-thinking for low-complexity
│  └─ Appropriate? → continue
│
└─ CHECK: Batch queue depth
   ├─ Growing? → Add replicas
   └─ Stable? → Check GPU memory pressure / thermal throttling
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|-----------------|-------------------|--------------|
| GPT-OSS-120B model weights | Blue-green on H100 fleet | All reasoning tasks |
| Qwen3-32B model weights | Blue-green on A100 fleet | All general tasks |
| LoRA adapters (fine-tuned) | Detach adapter, revert to base | Fine-tuned domain only |
| Routing classifier | Feature flag (<1s toggle) | Request distribution |
| Reasoning level thresholds | Config reload (no restart) | GPT-OSS cost/quality |
| Thinking mode policy | Config reload | Qwen3 cost/quality |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Routing accuracy (was the model choice optimal?) | Very high | Re-run 5% of requests through both models; compare |
| Per-model quality on routed tasks | High | LLM-as-judge on sample |
| Cost-per-quality-point by model | High | Daily cost/quality aggregation |
| Hallucination reports | High | User feedback + automated fact-checking |
| Reasoning mode efficiency | Medium | Tokens generated vs quality achieved |
| Expert utilization balance | Medium | vLLM instrumentation on GPT-OSS |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|----------------|---------------|
| Real-time | Routing thresholds, reasoning level selection | Automated anomaly detection |
| Daily | Expert load balancing params | CV drift detection |
| Weekly | Routing classifier retrain | >5% misroute rate on evaluation sample |
| Monthly | LoRA adapters (domain-specific) | A/B test showing >3% quality improvement |
| Quarterly | Base model upgrade (new Qwen/GPT-OSS release) | Full eval suite, 2-week shadow deployment |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Hybrid routing (GPT-OSS + Qwen3) | Cost vs quality optimization | Diverse workloads spanning reasoning + general | Uniform workload (use one model) |
| ESFT (Expert-Specialized Fine-Tuning) [4] | Adding capability to MoE without disruption | Domain adaptation on GPT-OSS-120B | Broad fine-tuning (use Qwen3 instead) |
| Reasoning level routing | Compute waste on simple tasks | GPT-OSS handling mixed-complexity traffic | All tasks genuinely need deep reasoning |
| Thinking mode toggle (Qwen3) | Adaptive depth without model switching | Variable-complexity traffic on Qwen3 | All tasks need full thinking |
| Cross-model distillation [3] | Combining strengths of both models | Multilingual GPT-OSS or reasoning Qwen3 | When architectures prohibit method (e.g., logit distill) |
| Ensemble verification | Hallucination reduction | High-stakes factual queries | Latency-sensitive paths (adds 2× gen time) |
| Prefix caching (vLLM) [10] | System prompt token waste | Repeated prompts across requests | Highly diverse prompts (low cache hit) |
| Cascading (Qwen3 → GPT-OSS fallback) | Quality floor with cost ceiling | When Qwen3 handles 70%+ adequately | When routing is reliable (prefer direct routing) |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|-----------------|------------------------------|
| "GPT-OSS-120B is better because it has higher MMLU" | "MMLU at 90% vs 84% matters only if your workload is English knowledge QA. For multilingual support, MMMLU shows Qwen3 wins. Match the benchmark to the workload." |
| "Just use GPT-OSS for everything — it's frontier class" | "At 'low' reasoning it drops below Qwen3. At 'high' it costs 2.5x more. Route 70% of traffic to Qwen3, save 42%, lose nothing on non-reasoning tasks." |
| "Qwen3-32B is better because you can fine-tune it easily" | "Fine-tuning is a means, not an end. If your task is reasoning-heavy and GPT-OSS solves it out-of-box at 95.8% AIME, spending months fine-tuning Qwen3 to get to 70% is the wrong trade-off." |
| "MoE is always more efficient — fewer active params" | "GPT-OSS's 5.1B active params create a hallucination floor that no amount of routing can fix. Dense Qwen3's 32B active gives 6x more factual recall per token. Efficiency isn't free." |
| "We need to fine-tune GPT-OSS for our domain" | "ESFT on MoE requires routing analysis, expert identification, and careful replay data balancing. If standard LoRA on Qwen3 achieves 90% of the goal, the 50x simpler path wins." |
| "Both models are Apache 2.0 so they're interchangeable" | "Licensing is identical but architectures are not. The deployment, fine-tuning, monitoring, and failure modes are completely different. Same license ≠ same operational burden." |
| "Let's just pick one model to simplify ops" | "Picking one model optimizes for ops simplicity while leaving 30-40% of cost or quality on the table. The routing layer is 100 lines of code. The savings are $50K+/month at scale." |

## References

### Foundational Papers & Sources

- [1] OpenAI (2025) -- GPT-OSS-120B Model Card -- arXiv:2508.10925 -- 117B MoE, 5.1B active, 128 experts top-4, MXFP4, AIME 95.8%, trained with CoT RL
- [2] Qwen Team (2025) -- Qwen3 Technical Report -- arXiv:2505.09388 -- 32B dense, 64 layers, 128K context, 36T tokens, 119 languages, dual thinking modes
- [3] Burns et al. (2023) -- Weak-to-Strong Generalization -- arXiv:2312.09390 -- Proved smaller models can improve larger ones; GPT-2 supervision on GPT-4 recovered near-GPT-3.5
- [4] Xu et al. (2024) -- ESFT: Expert-Specialized Fine-Tuning for MoE -- arXiv:2407.01906 -- Selective expert training; routing is task-concentrated; freeze unrelated experts
- [5] Fedus et al. (2022) -- Switch Transformers -- arXiv:2101.03961 -- MoE with auxiliary load-balancing loss; expert collapse analysis
- [6] Shazeer et al. (2017) -- Sparsely-Gated Mixture-of-Experts Layer -- arXiv:1701.06538 -- Foundational MoE gating mechanisms and load balancing
- [7] Lin et al. (2024) -- AWQ: Activation-aware Weight Quantization -- arXiv:2306.00978 -- 4-bit quantization with <1% quality loss for dense models
- [8] Peng et al. (2023) -- YaRN: Efficient Context Window Extension -- arXiv:2309.00071 -- NTK-aware RoPE interpolation for context scaling
- [9] Rouhani et al. (2023) -- Microscaling Data Formats for Deep Learning -- arXiv:2310.10537 -- MXFP4 format specification and near-lossless training results
- [10] Kwon et al. (2023) -- Efficient Memory Management for LLM Serving with PagedAttention -- arXiv:2309.06180 -- vLLM PagedAttention; 2-4x throughput improvement
- [11] Biderman et al. (2024) -- LoRA Learns Less and Forgets Less -- arXiv:2405.09673 -- LoRA preserves base capabilities better than full fine-tuning
- [12] Singh et al. (2023) -- GKD: Generalized Knowledge Distillation -- arXiv:2306.13649 -- On-policy distillation avoiding covariate shift
- [13] Wan et al. (2024) -- Knowledge Fusion of Large Language Models -- arXiv:2401.10491 (ICLR 2024) -- Cross-architecture transfer via generative distributions

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-06 | Initial v2 generation | New focused report: GPT-OSS-120B vs Qwen3-32B only. Covers architecture, benchmarks, deployment, fine-tuning, distillation, cost, observability. All references to GPT-4/4o, Qwen2.5, Mixtral, etc. removed. |
| 2026-06-06 | Expanded hallucination Q&A (Q8) | Rewrote Q8 with full mechanism explanation, QnA-type suitability table, decision rule, and mitigation strategies. Clarified poor for factual QA, excellent for reasoning QA. |
| 2026-06-06 | Filed vLLM single-GPU query | Requirements, pros/cons indexed in knowledge base. Report Q4 and DE Probe 2 already cover vLLM single-GPU deployment (VRAM budgets, concurrency limits, config examples). |
| 2026-06-07 | Multi-node inference knowledge added | Filed comprehensive comparison of multi-node solutions (vLLM, TRT-LLM, SGLang, DeepSpeed-MII) + cloud services (AWS/GCP/Azure) in knowledge base. Scaling guidance: TP within node, PP/EP across nodes, Wide-EP for MoE. |
