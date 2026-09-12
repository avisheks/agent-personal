# Supervised Fine-Tuning: The Definitive Reference

> **Last Updated:** 2026-06-09 | **Read time:** ~18 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#Data Preparation]] | [[#Loss Functions]] | [[#Design Choices]] | [[#Application Quirks]] | [[#Industry Approaches]] | [[#Practitioner Recipe]] | [[#References]]

---



## References

- [1] LIMA — Zhou et al. (2023) — arXiv:2305.11206 — 1K examples suffice
- [2] Scaling Data-Constrained LMs — Muennighoff et al. (2023) — arXiv:2305.16264
- [3] InstructGPT — Ouyang et al. (2022) — arXiv:2203.02155
- [4] Constitutional AI — Bai et al. (2022) — arXiv:2212.08073
- [5] LoRA — Hu et al. (2021) — arXiv:2106.09685
- [6] NEFTune — Jain et al. (2023) — arXiv:2310.05914 — +8-35% AlpacaEval
- [7] Fewer Truncations — Krell et al. (ICML 2024) — arXiv:2404.10830 — Best-Fit Decreasing packing
- [8] DEITA — Liu et al. (ICLR 2024) — arXiv:2312.15685 — 6K samples match SOTA
- [9] FIM — Bavarian et al. (2022) — arXiv:2207.14255 — Fill-in-the-middle
- [10] PRM — Lightman et al. (2023) — arXiv:2305.20050 — Process supervision 78% MATH
- [11] Llama 3.1 — Meta (2024) — arXiv:2407.21783 — 15T tokens, 10M+ SFT
- [12] Qwen 2.5 — Alibaba (2024) — arXiv:2412.15115 — 18T tokens, 1M+ SFT
- [13] LongLoRA — Chen et al. (2023) — arXiv:2309.12307 — 100K context on single machine
- [14] LoRA Learns Less and Forgets Less — Biderman et al. (2024) — arXiv:2405.09673


## Quick Catchup

> **Quick Catchup (June 2026):** SFT has shifted from "more data is better" to "quality dominates quantity" — LIMA (1K examples), DEITA (6K), Yi (<10K) all achieve strong results. Key innovations: BFD packing (2x throughput, 58% less hallucination, ICML 2024), NEFTune (+8-35% AlpacaEval for free), chunked NLL (-30-50% VRAM, TRL v1.5.1). Main open problem: SFT ceiling — it cannot exceed demo quality, which is why every top lab follows SFT with RL.
> Recent breakthrough: DeepSeek-R1 showed minimal cold-start SFT + pure GRPO can match elaborate multi-stage pipelines. Trend: synthetic data from stronger models (Orca, Phi-3) replacing expensive human annotation.


## Data Preparation

### Quality vs Quantity

| Paper | Year | Dataset Size | Key Result |
|-------|------|:------------:|-----------|
| LIMA | 2023 | 1K | 43% preferred over GPT-4; "all knowledge is from pretraining" |
| DEITA | ICLR 2024 | 6K | 7.55 MT-Bench via complexity/quality/diversity scoring |
| Yi | 2024 | <10K | Each example verified by ML engineers |
| Scaling Data-Constrained | 2023 | — | 4 epochs of repetition is free; beyond = zero additional learning benefit |
| Llama 3.1 | 2024 | 10M+ | At massive scale with rejection sampling as quality filter |
| Qwen 2.5 | 2024 | 1M+ | Curated via quality scoring across 29 languages |

**The LIMA finding**: "Almost all knowledge in large language models is learned during pretraining, and only limited instruction tuning data is necessary to teach models to produce high quality output." SFT teaches FORMAT, not CAPABILITY.

### Packing (Mandatory)

Best-Fit Decreasing (BFD) packing from "Fewer Truncations, Improved Language Modeling" (ICML 2024):

| Metric | With BFD Packing | Without |
|--------|:----------------:|:-------:|
| Throughput | **2x** | 1x |
| Memory | **-20%** | baseline |
| Hallucination | **-58%** | baseline |
| Reading comprehension | **+4.7%** | baseline |
| Context following | **+16.8%** | baseline |

Requires `flash_attn_varlen_func` with `cu_seqlens` + `position_ids` to prevent cross-example attention.

### Train-on-Responses-Only

Standard for all chat/instruction SFT. In TRL: `assistant_only_loss=True`. Sets label=-100 on prompt tokens. Prevents model from "learning to generate" user prompts.

### Synthetic Data Generation

| Method | Source | Key Result |
|--------|--------|-----------|
| Evol-Instruct (WizardLM) | ICLR 2024 | "Superior to human-created"; 90% of ChatGPT on 17/29 skills |
| Orca | 2023 | GPT-4 explanation traces → 13B surpasses Vicuna by 100% on BBH |
| Phi-3 | 2024 | "Textbooks" + web filtering → 3.8B gets 69% MMLU |
| Self-Rewarding LMs | ICML 2024 | Model self-judges → 3 iterations beats Claude 2, GPT-4 |

### Data Repetition Rule

**Up to 4 epochs of repeated data is effectively free** (negligible loss change). Beyond 4 epochs, the value provides zero additional learning benefit. Validated across 400 runs, 900B tokens, models up to 9B params. Implication: don't collect more data until you've repeated existing data 4x.


## Loss Functions

### The Hierarchy (Most to Least Important)

1. **NEFTune** (arXiv:2310.05914): Add noise to embedding vectors during training. LLaMA-2-7B: 29.8% → **64.7%** on AlpacaEval. Zero cost, zero complexity. **Enable by default.**

2. **Answer-only loss**: Mask prompt tokens (label=-100). Standard for instruction tuning. Focuses all gradient signal on response quality.

3. **Chunked NLL** (TRL v1.5.1): Drops masked positions BEFORE lm_head matmul and reduces VRAM usage. **30-50% less VRAM**. Set `loss_type="chunked_nll"`.

4. **Standard cross-entropy**: `-sum log p(y_t | y_<t)` — the universal default. Everything else builds on this.

5. **ORPO** (arXiv:2403.07691): Combines SFT + preference optimization in single step. "A minor penalty for disfavored style is sufficient."

6. **Label smoothing**: Rarely needed. Short training and early stopping can provide some regularization, but they may not be entirely equivalent to label smoothing in all cases.

---


## Design Choices

### The Numbers That Work

| Parameter | 7B | 13B | 70B | 400B+ | Source |
|-----------|:--:|:---:|:---:|:-----:|--------|
| LR (full FT) | 2e-5 | 1-2e-5 | 5e-6 to 1e-5 | 1-5e-6 | TRL default, Llama recipes |
| LR (LoRA) | 1-3e-4 | 1e-4 | 1e-4 | 5e-5 | TRL docs |
| Epochs | 2-3 | 2-3 | 1-2 | 1 | LIMA, Scaling paper |
| Batch (effective) | 32-128 | 64-128 | 128-256 | 256+ | Stability considerations |
| Scheduler | Cosine | Cosine | Cosine | Cosine | StarCoder, most recipes |
| Warmup | 30 steps | 50-100 | 100-200 | 200+ | StarCoder: 30 steps |
| Precision | BF16 | BF16 | BF16 | BF16 | TRL default |
| Weight decay | 0-0.01 | 0-0.01 | 0 | 0 | StarCoder: 0.01 |
| Dropout | OFF | OFF | OFF | OFF | LoRA is better regularizer |

### Why These Choices

**Dropout off**: SFT runs are 1-3 epochs. LoRA "mitigates forgetting more than common regularization techniques such as weight decay and dropout" (arXiv:2405.09673).

**1-3 epochs max**: Beyond 3 epochs on instruction data, models memorize patterns. The Scaling paper proves >4x repetition is worthless.

**BF16 always**: Larger dynamic range than FP16. No loss scaling needed. Standard on A100/H100.

### LoRA vs Full Fine-Tuning

| Dimension | LoRA | Full FT |
|-----------|------|---------|
| Memory | 3-10x less | Full model + optimizer |
| Trainable params | 0.1-2% | 100% |
| Quality ceiling | 95-99% of full FT | Maximum |
| Forgetting | Less (preserves base) | More |
| Cost | QLoRA 7.8x cheaper | Baseline |
| When to use | Default; sufficient for most | >5% quality gap with LoRA |

Full FT "learns perturbations with rank 10-100x greater than typical LoRA" (arXiv:2405.09673). But LoRA closes 95% of the gap at 3-10x lower cost.


## Application Quirks

### Code Generation

**FIM (fill-in-the-middle)** at 50% rate: moves middle span to end of sequence during training. Two modes: PSM (Prefix-Suffix-Middle), SPM (Suffix-Prefix-Middle). "Does NOT harm autoregressive performance across a wide range of scales." **Recommendation: train all future models with FIM by default.**

StarCoder recipe: lr=5e-5, seq=2048, cosine, bf16. Full FT: 9hrs/$108 (8xA100). QLoRA: 12.5hrs/$14 (1xA100).

### Math/Reasoning

**Process supervision dramatically outperforms outcome-only:**
- PRM800K: 800K step-level human labels → **78% MATH**
- Each reasoning step gets a correctness label
- SFT data for math MUST have verified step-by-step solutions, not just final answers
- DeepSeekMath: 120B math tokens from Common Crawl → continues pretraining before SFT

### Long Context

**LongLoRA** (arXiv:2309.12307): Extends 7B from 4K to **100K** context on single 8xA100.
- Shifted Sparse Attention during training, dense at inference
- **Embedding and normalization layers MUST be trainable** for context extension
- "Only two lines of code in training"

### Tool Use / Function Calling

- ToolLLM: 16,464 real APIs from RapidAPI Hub, ChatGPT generates solution paths
- Must train on: simple calls, multiple selection, parallel calls, implicit parameter conversion
- Formats: OpenAI JSON Schema, Gorilla OpenFunctions, REST API

### Vision-Language

- "Image encoder + resolution matters most; connector design is negligible" — MM1 (Apple)
- LLaVA-1.5: CLIP-ViT-L-336px + MLP, 1.2M data, 1 day on 8xA100
- Set `max_length=None` to avoid truncating image tokens (TRL)


## Industry Approaches

### Pipeline Comparison

| Lab | SFT Phase | What Follows | Total Pipeline |
|-----|-----------|-------------|---------------|
| **OpenAI** | Human demonstrations → SFT | RM → PPO | SFT → RM → PPO |
| **Anthropic** | Self-critique/revision → SFT on revised | AI preference model → RL | Constitutional AI (RLAIF) |
| **Meta** | 10M+ human annotations → SFT | Rejection Sampling → PPO → DPO | Multi-stage, open-weight |
| **DeepSeek** | Minimal cold-start SFT | GRPO (pure RL) | Minimal SFT → GRPO |
| **Qwen** | 18T pretrain + 1M+ curated SFT + multilingual (29+ langs) | Multi-stage RL | 18T pretrain + 1M+ curated SFT + multilingual (29+ langs) + multistage RL |
| **Google** | Knowledge distillation (Gemma 2B/9B) | — | Distillation replaces SFT for small models |
| **Mistral** | Undisclosed (minimal) | DPO | Architectural efficiency focus |

### What Each Lab Uniquely Contributes

- **OpenAI**: Proved SFT→RLHF works (1.3B InstructGPT > 175B GPT-3)
- **Anthropic**: Proved no human harm labels needed (constitutional principles suffice)
- **Meta**: Proved massive open annotation + multi-stage can match proprietary
- **DeepSeek**: Proved minimal SFT + strong RL = cost-efficient SOTA
- **Qwen**: Proved broadest multilingual coverage (29 langs) + domain variants scale
- **Google**: Proved distillation can replace SFT for small models entirely


## Practitioner Recipe (Start Here)

```
7B Model, 10K-50K curated examples:

1. Format: Conversational (ChatML/Llama), responses only
2. Packing: BFD with Flash Attention 2
3. Loss: Standard CE + NEFTune
4. LR: 2e-5 (full FT) or 1e-4 (LoRA r=32-64)
5. Scheduler: Cosine, 30-step warmup
6. Epochs: 2-3 (or until val loss increases)
7. Batch: 32-128 effective (via gradient accumulation)
8. Precision: BF16, gradient checkpointing ON
9. Code-specific: Add FIM at 50% rate
10. Math-specific: Use step-level verified solutions

Expected: Train in 2-6 hours on 1x A100-80GB (QLoRA)
          or 4-12 hours on 8x A100 (full FT)
```

---


## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-09 | Initial v2 generation | [UNVERIFIED] Comprehensive SFT reference: data prep (quality>>quantity, packing, synthetic), loss functions (NEFTune technique, chunked NLL, ORPO), design choices (lr/epochs/precision by model size), application quirks (code FIM, math PRM, long context, vision), industry pipeline comparison (more than 7 labs). Run /verify-report --topic sft when available. |

---

## Verification

| Metric | Value |
|--------|-------|
| Verification score | 79% |
| Verification model | GPT-OSS-120b (Bedrock) |
| Total claims | 133 |
| Correct | 77 |
| Corrected | 20 |
| Unverifiable | 36 |
| Verified at | 2026-06-09 17:50 UTC |
| Sections corrected | Loss Functions, Quick Catchup, Data Preparation, Design Choices, Application Quirks, References, Practitioner Recipe (Start Here), Industry Approaches, Changelog |
