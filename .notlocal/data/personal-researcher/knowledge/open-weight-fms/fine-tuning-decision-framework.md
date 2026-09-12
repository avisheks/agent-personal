---
title: "Fine-Tuning Decision Framework"
summary: "Decision guide for choosing which open-weight model to fine-tune based on 5 axes: use case, hardware constraints, data volume, license requirements, and fine-tuning method. Includes hardware-to-model mapping and data volume recommendations."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Fine-Tuning Decision Framework

## By Hardware

| Available Hardware | Models That Fit | Fine-Tuning Method |
|-------------------|----------------|-------------------|
| **8GB VRAM** (RTX 3060/4060) | GPT-OSS-20B (QLoRA), Qwen3-4B, Phi-4-mini 3.8B | QLoRA only |
| **16-24GB** (RTX 4090) | GPT-OSS-20B (LoRA), Qwen3-8B (QLoRA), Phi-4 14B (QLoRA), Gemma 3 12B | QLoRA or LoRA (small models) |
| **80GB** (A100/H100) | GPT-OSS-120B (LoRA), Qwen3-32B (LoRA/SFT), Llama 70B (QLoRA) | LoRA or full SFT (≤32B) |
| **4-8× H100** | DeepSeek-R1-70B (full SFT), Llama 4 Maverick, Qwen3-235B | Full SFT |
| **Multi-node** | DeepSeek V3/R1 (671B), Nemotron-340B | Distributed full SFT |

^[open-weight-models-catalog-2026.md]

## By Data Volume

| Data Available | Approach | Model Size Guidance |
|---------------|----------|---------------------|
| **<100 examples** | Few-shot prompting or very light LoRA (r=8) | Use largest model you can serve (Qwen3-32B, GPT-OSS-120B) — base capability matters most |
| **100–1K examples** | LoRA (r=16-32) on instruct model | Mid-size: Phi-4 14B, Qwen3-8B, Mistral Small 24B |
| **1K–10K examples** | LoRA (r=64+) or QLoRA on base model | Qwen3-32B, Llama 70B, Gemma 3 27B |
| **10K–100K examples** | Full SFT on smaller model OR LoRA on larger | Qwen3-14B (full SFT), Llama 70B (LoRA) |
| **100K+ examples** | Full SFT, possibly continued pretraining | Qwen3-8B/14B (full SFT), Llama 8B (CPT+SFT) |

Key principle: **more data → smaller model benefits from full SFT; less data → larger model benefits from light adaptation**.

## By Fine-Tuning Method

| Method | VRAM Need | When | Preserves Base? | Best Models |
|--------|-----------|------|----------------|-------------|
| **Full SFT** | High (2-8× model BF16 size) | Large dataset, maximum quality, single-task | Low (forgetting risk) | Qwen3, Llama, Phi-4 |
| **LoRA** (r=16-64) | Low (base + adapters) | 1K-10K examples, maintain generality | High | All models |
| **QLoRA** | Very low (4-bit base + adapters) | Consumer GPU, rapid prototyping | High | GPT-OSS-20B, Phi-4-mini, Qwen3-4B/8B |
| **Continued Pretraining** | Very high | Domain adaptation with unlabeled corpus | Medium | Llama 8B, Qwen3-4B/8B, Falcon 3 |
| **ESFT** (MoE-specific) | Moderate | Selective capability addition to MoE | Very high | GPT-OSS-120B, Qwen3-235B-A22B |

## By License

| Need | Fully Permissive | Permissive with Conditions | Avoid for Commercial |
|------|-----------------|---------------------------|---------------------|
| **Frontier** | Qwen3, GPT-OSS, Mixtral 8x22B | Llama 4 (700M MAU cap), Gemma 3 | Mistral Large, Command R+ |
| **Mid-size** | Phi-4 (MIT), Qwen2.5-Coder, Devstral | Nemotron (NVIDIA license) | — |
| **Small** | RWKV (Apache 2.0), Falcon 3 | — | StableLM |

## Quick Decision Tree

```
What's your USE CASE?
├─ Code → Devstral 24B or Qwen2.5-Coder-32B
├─ Math/Reasoning → DeepSeek-R1 distilled 32B
├─ Multilingual → Qwen3-32B
├─ Agentic → GPT-OSS-120B
├─ General → Qwen3-32B (safest default)
└─ Edge/on-device → Phi-4-mini 3.8B

What's your HARDWARE?
├─ 8GB → QLoRA on Phi-4-mini or Qwen3-4B
├─ 24GB → LoRA on Qwen3-8B or Phi-4
├─ 80GB → LoRA on Qwen3-32B or GPT-OSS-120B
└─ Multi-GPU → Full SFT on 14B-70B

Must be COMMERCIAL + FULLY PERMISSIVE?
├─ Yes → Qwen3, GPT-OSS, Phi-4, Devstral
└─ No → Also consider Llama 4, Gemma 3
```

## Related

- [[Open-Weight Model Families for Fine-Tuning (2026)]]
- [[Reverse Distillation: Qwen3-32B → GPT-OSS-120B Feasibility]]
- [[Strong-to-Weak Distillation]]
