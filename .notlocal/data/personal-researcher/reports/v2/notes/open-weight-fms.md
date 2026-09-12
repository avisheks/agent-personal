# Open-Weight Foundation Models for Fine-Tuning

> **Last Updated:** 2026-06-07 | **Read time:** ~18 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Model Catalog]] | [[#Decision Framework]] | [[#Fine-Tuning Methods]] | [[#Hardware Mapping]] | [[#License Guide]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** The open-weight landscape has consolidated around 7 frontier families: Llama 4 (Meta, 10M context), Qwen3 (Alibaba, 119 languages), GPT-OSS (OpenAI, single-GPU frontier), DeepSeek R1 (best reasoning), Mistral/Devstral (best open-source code), Gemma 3 (Google, 140+ languages), and Nemotron (NVIDIA, omnimodal) [1][2][3][4].
> Default recommendation: Qwen3-32B for most fine-tuning tasks (Apache 2.0, broad capability, standard tooling). Main open problem: no single model dominates all axes simultaneously.
> Recent breakthrough: GPT-OSS-120B (Aug 2025) proved MoE can deliver frontier reasoning on a single GPU via MXFP4 quantization [3]. Trend: MoE + aggressive quantization making 100B+ models accessible on consumer/single-GPU hardware.

## State of the Art

### Current Landscape (19+ Model Families)

**Tier 1 — Frontier (compete with proprietary models):**
- Meta Llama 4: MoE, multimodal, 10M context, Llama Community license [1]
- Alibaba Qwen3: Dense + MoE, 119 languages, Apache 2.0 [2]
- OpenAI GPT-OSS: MoE (MXFP4), single-GPU frontier reasoning, Apache 2.0 [3]
- DeepSeek V3/R1: MoE (MLA), 97.3% MATH-500, MIT license [4]
- Mistral AI: Dense + MoE, Devstral #1 SWE-bench, Apache 2.0 [5]
- Google Gemma 3: Dense, multimodal, 140+ languages, Gemma Terms [6]
- NVIDIA Nemotron: MoE omnimodal, 256K context, NVIDIA license [7]

**Tier 2 — Strong general-purpose:**
- Microsoft Phi-4: 14B dense, MIT, best math for size (80.4% MATH) [8]
- Qwen2.5-Coder: code-specialized, Apache 2.0, matches GPT-4o on code [2]
- StarCoder 2: 600+ programming languages, OpenRAIL-M [9]
- InternLM 2.5: 1M context, Apache 2.0 [10]

**Tier 3 — Specialized:**
- RWKV-7: RNN (non-transformer), O(n) linear complexity, Apache 2.0
- Jamba 1.5: SSM+Transformer hybrid, 2.5x faster inference, 256K context
- Falcon 3: STEM/code focused, Apache 2.0-based

### Recent Breakthroughs (last 12 months)

- **Llama 4** (Apr 2026): 10M token context via MoE Scout architecture; multimodal [1]
- **GPT-OSS** (Aug 2025): First OpenAI open-weight; MXFP4 fits 120B on single H100 [3]
- **DeepSeek-R1** (Jan 2025): Purely RL-trained reasoning; distilled versions enable 70B-class reasoning at 32B [4]
- **Devstral** (May 2025): #1 open-source SWE-bench (46.8%) at only 24B params [5]
- **Qwen3** (Apr 2025): Unified thinking/non-thinking in one model; 119 languages [2]

## Executive Summary

Open-weight models now match proprietary APIs on most tasks while offering full customization via fine-tuning. The decision is no longer "open vs closed" but "which open model for my specific use case."

**Default**: Qwen3-32B (Apache 2.0, 119 languages, thinking modes, standard LoRA tooling)

**Exceptions by task:**
- Complex reasoning → DeepSeek-R1 distilled 32B (MIT, frontier reasoning)
- Code → Devstral 24B (Apache 2.0, #1 SWE-bench)
- Agentic/tool use → GPT-OSS-120B (Apache 2.0, Harmony format)
- On-device → Phi-4-mini 3.8B (MIT, 128K context, 8GB)
- Maximum context → Llama 4 Scout (10M tokens)
- Maximum multilingual → Qwen3 (119 langs) or Gemma 3 (140+ langs)

```
The One-Line Decision:
                 Reasoning?  → DeepSeek-R1-32B
                 Code?       → Devstral 24B
                 Multilingual? → Qwen3-32B
                 Agentic?    → GPT-OSS-120B
                 Edge?       → Phi-4-mini 3.8B
                 Unsure?     → Qwen3-32B (safest default)
```

## Model Catalog

### Frontier Models (Tier 1)

| Family | Best Size for Fine-Tuning | Active Params | Context | License | Strength |
|--------|--------------------------|---------------|---------|---------|----------|
| Llama 4 Scout | 109B/17B active | 17B | 10M | Llama Community | Longest context, multimodal |
| Qwen3 | 32B (dense) | 32B | 128K | Apache 2.0 | Multilingual, thinking modes |
| GPT-OSS | 120B/5.1B active | 5.1B | 131K | Apache 2.0 | Reasoning, agentic, single-GPU |
| DeepSeek-R1 | Distilled 32B | 32B | 128K | MIT | Math (97.3%), reasoning |
| Devstral | 24B | 24B | 128K | Apache 2.0 | Code (#1 SWE-bench) |
| Gemma 3 | 27B | 27B | 128K | Gemma Terms | Vision, 140+ languages |
| Nemotron 3 Nano | 30B/3B active | 3B | 256K | NVIDIA License | Omnimodal (text/img/audio/video) |

### Strong General-Purpose (Tier 2)

| Family | Best Size | Context | License | Strength |
|--------|-----------|---------|---------|----------|
| Phi-4 | 14B | 16K | MIT | Math/reasoning for size |
| Phi-4-mini | 3.8B | 128K | MIT | Edge deployment, 128K in 8GB |
| Qwen2.5-Coder | 32B | 128K | Apache 2.0 | GPT-4o-level code |
| StarCoder 2 | 15B | 16K | OpenRAIL-M | 600+ languages |
| InternLM 2.5 | 7B | 1M | Apache 2.0 | Ultra-long context |

### Deprecated (Do Not Use)

| Old | Use Instead |
|-----|-------------|
| Llama 2 | Llama 3.1 / 4 |
| Qwen2 | Qwen3 |
| Code Llama | Devstral / Qwen2.5-Coder |
| Mistral 7B v0.1 | Mistral Small 24B |
| Phi-3 | Phi-4 |
| Gemma 1 | Gemma 3 |
| StarCoder 1 | StarCoder 2 |

## Decision Framework

### By Use Case

| Use Case | First Choice | Runner-Up | Budget |
|----------|-------------|-----------|--------|
| General chat | Qwen3-32B | Llama 4 Maverick | Qwen3-8B |
| Code generation | Devstral 24B | Qwen2.5-Coder-32B | Qwen2.5-Coder-7B |
| Math/reasoning | DeepSeek-R1 distilled 32B | Qwen3-32B (thinking) | Phi-4 14B |
| Multilingual | Qwen3-32B (119 langs) | Gemma 3 27B (140+) | Qwen3-8B |
| Agentic/tool use | GPT-OSS-120B | Devstral | Mistral Small 24B |
| Long context | Llama 4 Scout (10M) | InternLM 2.5 (1M) | Jamba 1.5 (256K) |
| On-device/edge | Phi-4-mini 3.8B | Qwen3-4B | Gemma 3 1B |
| Multimodal (vision) | Gemma 3 27B | Llama 4 | Nemotron 3 Nano |
| Synthetic data gen | Nemotron-4-340B | GPT-OSS-120B | Qwen3-235B |

### By Data Volume

| Data | Method | Model Guidance |
|------|--------|----------------|
| <100 examples | Few-shot or light LoRA (r=8) | Use largest model available — base capability dominates |
| 100–1K | LoRA (r=16-32) on instruct | Mid-size: Phi-4, Qwen3-8B, Mistral Small |
| 1K–10K | LoRA (r=64) on base model | Qwen3-32B, Llama 70B, Gemma 3 27B |
| 10K–100K | Full SFT on smaller model | Qwen3-14B, Llama 8B |
| 100K+ | Full SFT or continued pretraining | Qwen3-8B (CPT+SFT) |

**Principle**: More data → smaller model benefits from full SFT. Less data → larger model benefits from light adaptation.

## Fine-Tuning Methods

| Method | VRAM Need | When | Preserves Base? |
|--------|-----------|------|----------------|
| **Full SFT** | 2-8× model size (BF16) | Large dataset, max quality | Low (forgetting risk) |
| **LoRA** (r=16-64) | Base + small adapters | 1K-10K examples, maintain generality | High |
| **QLoRA** | 4-bit base + adapters | Consumer GPU, prototyping | High |
| **ESFT** (MoE) | Moderate | Selective expert tuning | Very high |
| **Continued Pretraining** | Very high | Domain adaptation, unlabeled corpus | Medium |

### Best-Supported Models by Method

| Method | Best Models |
|--------|-------------|
| Full SFT | Qwen3 (any), Llama 3.1/4, Phi-4, Gemma 3 |
| LoRA | All models; best ecosystem: Qwen3, Llama, Mistral |
| QLoRA | GPT-OSS-20B (16GB), Phi-4-mini (8GB), Qwen3-4B/8B |
| ESFT (expert-specific) | GPT-OSS-120B, Qwen3-235B-A22B |
| Continued Pretraining | Llama 3.1-8B, Qwen3-4B/8B, Falcon 3 (designed for this) |

## Hardware Mapping

| Hardware | Models That Fit | Method |
|----------|----------------|--------|
| **8GB** (RTX 4060) | Phi-4-mini, Qwen3-4B, GPT-OSS-20B | QLoRA only |
| **16-24GB** (RTX 4090) | Qwen3-8B, Phi-4, Gemma 3 12B, GPT-OSS-20B | QLoRA or LoRA |
| **80GB** (A100/H100) | Qwen3-32B, GPT-OSS-120B, Llama 70B | LoRA or SFT (≤32B) |
| **4-8× H100** | DeepSeek-R1-70B, Llama 4 Maverick, Qwen3-235B | Full SFT |
| **Multi-node** | DeepSeek V3 (671B), Nemotron-340B | Distributed SFT |

## License Guide

### Fully Permissive (Apache 2.0 / MIT) — Safest for Commercial

| Model | License | Any Restrictions? |
|-------|---------|-------------------|
| Qwen3 (all sizes) | Apache 2.0 | None |
| GPT-OSS (20B, 120B) | Apache 2.0 | None |
| Phi-4 / Phi-4-mini | MIT | None |
| Devstral | Apache 2.0 | None |
| Mixtral 8x22B | Apache 2.0 | None |
| DeepSeek V3/R1 | MIT | None |
| Falcon 3 | Apache 2.0-based | None |
| RWKV | Apache 2.0 | None |

### Permissive with Conditions

| Model | License | Key Condition |
|-------|---------|---------------|
| Llama 4 | Llama Community | 700M monthly active user cap |
| Gemma 3 | Gemma Terms | Must accept Google's terms |
| Nemotron | NVIDIA Open License | NVIDIA-specific terms |
| StarCoder 2 | OpenRAIL-M | Use restrictions (no harm) |

### Non-Commercial (AVOID for Business)

| Model | License | Why Restricted |
|-------|---------|----------------|
| Mistral Large | Research License | Explicitly non-commercial |
| Command R+ | CC-BY-NC | Non-commercial only |
| StableLM | Community License | Requires commercial agreement |

## References

- [1] Meta (2026) -- Llama 4 Release -- Llama Community License -- 10M context, multimodal MoE
- [2] Qwen Team (2025) -- Qwen3 Technical Report -- arXiv:2505.09388 -- 119 languages, Apache 2.0
- [3] OpenAI (2025) -- GPT-OSS Model Card -- arXiv:2508.10925 -- MXFP4, 128 experts, Apache 2.0
- [4] DeepSeek (2025) -- DeepSeek-R1 -- arXiv:2501.12948 -- 97.3% MATH-500, distilled variants, MIT
- [5] Mistral AI (2025) -- Devstral -- Apache 2.0 -- #1 SWE-bench open-source (46.8%)
- [6] Google DeepMind (2025) -- Gemma 3 -- 140+ languages, multimodal, Gemma Terms
- [7] NVIDIA (2026) -- Nemotron 3 Nano Omni -- 30B-A3B, omnimodal, 256K context
- [8] Microsoft (2025) -- Phi-4 -- MIT -- 80.4% MATH at 14B parameters
- [9] BigCode (2024) -- StarCoder 2 -- OpenRAIL-M -- 600+ programming languages
- [10] Shanghai AI Lab (2025) -- InternLM 2.5 -- 1M context, Apache 2.0

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-07 | Initial v2 generation | Comprehensive catalog of 19+ open-weight model families for fine-tuning. Decision framework by use case, hardware, data volume, license, and method. |
