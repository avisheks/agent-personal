# ML System Design: GPU Planning & Fine-Tuning Infrastructure

> **Last Updated:** 2026-06-07 | **Read time:** ~12 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Cost Model]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** Fine-tuning infrastructure has shifted from "Full SFT on clusters" to "QLoRA on single GPUs" as the default for most workloads.
> Key enablers: QLoRA [1], Flash Attention [2], Unsloth 2x optimizations, FSDP+QLoRA for multi-GPU [3]. Main open problem: optimal rank selection for LoRA is still empirical — no reliable a priori formula.
> Recent breakthrough: Answer.ai's FSDP+QLoRA (Mar 2024) enabled 70B fine-tuning on 2x RTX 3090 at $0.60/hr. Trend: fine-tuning is becoming a commodity operation, not an infrastructure challenge.

## State of the Art

### Current Best Approaches

- **QLoRA 4-bit** — Fine-tune any model up to 70B on a single A100-80GB; dominant for most production workloads due to 8-50x cost reduction vs Full SFT [1]
- **FSDP + QLoRA** — Distributed QLoRA across consumer GPUs; enables 70B on 2x RTX 3090 [3]
- **Managed fine-tuning APIs** — Together AI, Fireworks, Google Vertex offer per-token pricing ($0.48-6.00/1M tokens); zero infrastructure needed
- **Unsloth** — 2x speed, 70% less memory through kernel-level optimizations; dominant for single-GPU fine-tuning
- **Full SFT with DeepSpeed ZeRO-3** — Still required when LoRA rank is insufficient for complex domain adaptation (>5% quality gap)

### Recent Breakthroughs (last 12 months)

- **FSDP+QLoRA** (Mar 2024): 70B on 2x consumer GPUs; democratized large model fine-tuning [3]
- **Unsloth 2x** (2024-2025): Kernel-level optimizations halving training time without quality loss
- **Together AI serverless fine-tuning** (2025): Pay-per-token fine-tuning; no GPU provisioning needed
- **H100 availability normalization** (2025): H100 spot pricing dropped to $3/hr, making Full SFT of 70B economically viable

### Open Problems

- **Rank selection**: No reliable formula for choosing LoRA rank; empirical sweep still required
- **MoE fine-tuning**: Expert routing disruption during fine-tuning is poorly understood; ESFT [4] is promising but not mainstream
- **Long-context fine-tuning**: Memory requirements scale linearly with sequence length; 128K fine-tuning remains expensive
- **Catastrophic forgetting**: Even LoRA can degrade base capabilities on sufficiently different domains

## Executive Summary

GPU planning for fine-tuning is a 3-variable optimization: **model size** (determines memory floor), **method** (Full SFT vs LoRA vs QLoRA — determines compute multiplier), and **dataset scale** (determines wall-clock time). The core trade-off: Full SFT gives maximum quality but costs 8-50x more than QLoRA; QLoRA closes 95% of the gap for 95% of workloads.

- **Choose QLoRA** when: budget-constrained, <5% quality gap acceptable, single-GPU deployment preferred
- **Choose LoRA** when: need more capacity than QLoRA (rank >64), multi-GPU available, quality-sensitive domain
- **Choose Full SFT** when: QLoRA/LoRA leave >5% quality gap, have 8+ GPUs, domain is radically different from pre-training

**The killer framing:** "Fine-tuning cost scales linearly with model size and dataset tokens. The method choice (Full/LoRA/QLoRA) provides a 10-50x cost lever without proportional quality loss."

Cost headline: Fine-tuning Llama 3.1 70B on 10K examples costs $20-60 (QLoRA, self-managed) or ~$180 (managed API).

```
Method vs Cost (70B model, 10K examples, 4K seq, 3 epochs):
                     GPU-hours    Wall Clock        Cost
─────────────────────────────────────────────────────────
Full SFT             320-640      20-40 hrs         $400-1,000
LoRA (r=64)          24-120       6-15 hrs          $40-180
QLoRA 4-bit          24-60        12-30 hrs         $20-60
Managed API          N/A          ~2-4 hrs          ~$180
─────────────────────────────────────────────────────────
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Quality bar, domain distance from pre-training, latency of fine-tuning | Is this domain adaptation (LoRA sufficient) or capability injection (may need Full SFT)? |
| 2. Identify constraints | GPU budget, timeline, team expertise | Can you provision 8x A100? Do you have DeepSpeed/FSDP expertise? Or is managed API the only option? |
| 3. Propose baseline | QLoRA 4-bit on smallest viable hardware | Start with QLoRA r=16 on 1x A100; measure quality gap vs base model on held-out eval |
| 4. Identify gaps | Quality delta, training instability, forgetting | If gap >5% on domain eval, escalate: increase rank, switch to LoRA, or try Full SFT on subset |
| 5. Introduce improvements | Rank scaling, data quality, longer training | Increase rank to 64-128, filter training data, extend to 5 epochs before jumping to Full SFT |
| 6. Add evaluation | Held-out eval, base capability regression | Track BOTH domain performance AND base capability (detect catastrophic forgetting) |
| 7. Scaling tradeoffs | Cost vs quality vs time | At 100K+ examples: consider FSDP multi-node; at 1M+: consider data filtering over more epochs |

## System Design Walkthrough

### Architecture: Fine-Tuning Infrastructure

```
┌─────────────────────────────────────────────────────────┐
│              Fine-Tuning Pipeline                         │
├──────────────┬───────────────────┬──────────────────────┤
│ Data Layer   │  Compute Layer    │  Evaluation Layer     │
│ ┌──────────┐ │  ┌─────────────┐  │  ┌────────────────┐ │
│ │Dataset   │ │  │Method Router │  │  │Domain Eval     │ │
│ │Prep +    │─┼─▶│(Full/LoRA/  │──┼─▶│(held-out set)  │ │
│ │Filtering │ │  │QLoRA)       │  │  ├────────────────┤ │
│ └──────────┘ │  └─────────────┘  │  │Base Capability │ │
│              │         │         │  │Regression      │ │
├──────────────┴─────────┼─────────┴──┴────────────────┘─┤
│                        ▼                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │  GPU Cluster / Managed API                         │  │
│  │  Memory: model + optimizer + activations + KV      │  │
│  │  Scaling: FSDP (data parallel) or ZeRO-3          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Memory Budget Formula

```
Full SFT memory ≈ 18 * P bytes (FP16 weights + FP32 optimizer + gradients)
LoRA memory    ≈ 2 * P bytes (frozen weights) + 18 * P_trainable bytes
QLoRA memory   ≈ 0.5 * P bytes (4-bit weights) + 18 * P_trainable bytes
```

Where P = total params, P_trainable = LoRA params (typically 0.1-2% of P).

## Interview Q&A Bank

### Q1: How do you estimate GPU hours for a fine-tuning job?

> **Quick answer:** Training Time = 6 * P * D / tau, where P = parameters, D = total tokens, tau = GPUs * FLOP/s. For 70B QLoRA on 10K examples: ~24-60 GPU-hours on A100.

The formula comes from the compute cost of forward + backward passes (6 FLOPs per parameter per token). Practical throughput (tau) depends on hardware, precision, and memory management. A100 achieves ~150 TFLOP/s with Flash Attention; H100 achieves ~350 TFLOP/s.

For LoRA/QLoRA, the forward pass still processes all parameters (reading frozen weights), so the speedup is 2-4x (not proportional to the 100-1000x reduction in trainable params). The savings come primarily from memory (smaller optimizer state) enabling larger batch sizes.

**Hard follow-up:** Why isn't LoRA 100x faster if it trains 100x fewer parameters?

> Because the forward pass reads ALL weights regardless of which are trainable. The backward pass computes gradients only for trainable params (fast), but the forward pass dominates runtime. The real LoRA advantage is memory: smaller optimizer state → larger batches → better GPU utilization → 2-4x throughput gain.

### Q2: When should you use Full SFT vs LoRA vs QLoRA?

> **Quick answer:** Default to QLoRA. Escalate to LoRA if quality gap >3% on domain eval. Escalate to Full SFT only if LoRA at r=128 still leaves >5% gap — this is rare outside radically new domains.

Decision tree:
1. Start with QLoRA 4-bit, r=16 → evaluate
2. If gap >3%: increase to r=64, add FFN layers → evaluate
3. If still >3%: switch to LoRA (16-bit), r=64-128 → evaluate
4. If still >5%: Full SFT (this implies domain is very far from pre-training distribution)

In practice, 90%+ of production fine-tuning uses QLoRA or LoRA. Full SFT is reserved for: (a) pre-training continuation, (b) safety alignment, (c) radically new modalities.

**Hard follow-up:** What's the theoretical limit of LoRA quality vs Full SFT?

> LoRA paper [5] showed r=8 on GPT-3 175B matched full fine-tuning quality. The intrinsic dimensionality of the adaptation is much lower than the model dimension. However, this depends on domain distance — for domains well-represented in pre-training, r=4-16 suffices; for novel domains, r=128+ may be needed, approaching Full SFT compute anyway.

### Q3: How does sequence length affect fine-tuning cost?

> **Quick answer:** With Flash Attention, cost scales linearly with sequence length (2x seq = ~2x time + ~2x memory). Without Flash Attention, it's quadratic (2x seq = ~4x time).

Memory scaling is always linear (KV cache and activations grow with sequence length). The compute scaling depends on attention implementation. Flash Attention achieves near-linear by avoiding materializing the full attention matrix.

At 128K sequence length on a 70B model, KV cache alone is ~10GB per sequence, limiting batch size to 1-2 on an A100-80GB even with QLoRA. This is why long-context fine-tuning remains expensive.

**Hard follow-up:** Is it better to fine-tune at short context and rely on inference-time extension (YaRN)?

> For most tasks, yes. Fine-tune at 4-8K, serve at 128K with YaRN. The exception: if the task requires reasoning over information at specific long-range positions (e.g., document comparison), you need to fine-tune at the target length for the model to learn those attention patterns.

## Cost Model

### Per-Run Cost (10K examples, 4K seq, 3 epochs)

| Model | QLoRA Cost | LoRA Cost | Full SFT Cost | Managed API Cost |
|-------|:----------:|:---------:|:-------------:|:----------------:|
| 7-8B | $1-4 | $2-8 | $15-40 | ~$6 |
| 13-14B | $3-12 | $5-15 | $50-100 | ~$18 |
| 32B | $10-25 | $15-60 | $120-250 | ~$60 |
| 70-72B | $20-60 | $40-180 | $400-1,000 | ~$180 |
| 405B | $200-600 | $700-3,000 | $10,000-40,000 | ~$1,000 |

### Cloud GPU Pricing (per GPU-hour, as of June 2026)

| GPU | RunPod | GCP Spot | Lambda Labs |
|-----|--------|----------|-------------|
| RTX 4090 | $0.69 | N/A | $0.50 |
| A100 80GB | $1.39-1.49 | $1.10 | $1.50 |
| H100 80GB | $2.89-3.29 | $3.06 | N/A |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use |
|---------|---------------|-------------|
| QLoRA 4-bit | Memory reduction (fits 70B on 1 GPU) | Default for all fine-tuning |
| FSDP + QLoRA | Multi-GPU QLoRA on consumer hardware | When single GPU is too slow for 70B+ |
| Rank scheduling | Underfitting at low rank | Start r=8, increase to 64 during training |
| Replay mixing | Catastrophic forgetting | Mix 20-30% base-task data with domain data |
| ESFT (expert-specific) | MoE fine-tuning without routing disruption | Adapting MoE models to new domains [4] |
| Managed APIs | Zero infrastructure overhead | Iteration speed > cost optimization |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal Says |
|-----------------|---------------------|
| "We need 8x H100 to fine-tune 70B" | "QLoRA fits 70B on 1x A100. Start there — escalate hardware only when quality demands it" |
| "Full fine-tuning gives best quality" | "Full SFT gives 1-3% over LoRA in most domains, at 10-50x the cost. Measure the gap first" |
| "We need more data to improve quality" | "Beyond 4 epochs of repetition, adding data provides diminishing returns. Filter for quality first" |
| "Let's use the managed API, it's simpler" | "At 50+ fine-tuning runs/month, self-managed QLoRA saves 60-80%. The break-even is ~5 runs/month on 70B" |

## References

- [1] Dettmers et al. (2023) — QLoRA: Efficient Finetuning of Quantized LLMs — arXiv:2305.14314
- [2] Dao et al. (2022) — FlashAttention: Fast and Memory-Efficient Exact Attention — arXiv:2205.14135
- [3] Answer.ai (2024) — FSDP + QLoRA: Training 70B on 2 Consumer GPUs — answer.ai/posts/2024-03-06-fsdp-qlora
- [4] Xu et al. (2024) — ESFT: Expert-Specialized Fine-Tuning for MoE — arXiv:2407.01906
- [5] Hu et al. (2021) — LoRA: Low-Rank Adaptation of Large Language Models — arXiv:2106.09685
- [6] EleutherAI — Transformer Math 101 — blog.eleuther.ai/transformer-math/
- [7] Muennighoff et al. (2023) — Scaling Data-Constrained Language Models — arXiv:2305.16264
- [8] HuggingFace (2024) — Fine-tuning Llama 3 with QLoRA — huggingface.co/blog/llama3
- [9] HuggingFace (2024) — Personal Copilot: Full vs QLoRA Cost — huggingface.co/blog/personal-copilot

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-07 | Initial v2 generation | GPU hours reference for fine-tuning; covers formula, memory requirements, verified benchmarks, cost model, scaling laws |
