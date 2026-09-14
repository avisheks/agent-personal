---
title: "Open-Weight Model Families for Fine-Tuning (2026)"
summary: "Comprehensive catalog of open-weight foundation models: Tier 1 (Llama 4, Qwen3, GPT-OSS, DeepSeek, Mistral, Gemma, Nemotron), Tier 2 (Phi-4, Yi, StarCoder, InternLM), Tier 3 (Falcon, RWKV, Jamba). Decision axes: use case, hardware, license, data volume, fine-tuning method."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Open-Weight Model Families for Fine-Tuning (2026)

## Tier 1: Frontier Open-Weight Models

| Family | Sizes | Architecture | License | Best For |
|--------|-------|-------------|---------|----------|
| **Llama 4** (Meta) | Scout 109B/17B, Maverick 400B/17B | MoE, multimodal | Llama Community (700M MAU cap) | Long context (10M), multimodal |
| **Qwen3** (Alibaba) | 0.6B–235B dense+MoE | Dense + MoE | Apache 2.0 | Multilingual (119 langs), general, math |
| **GPT-OSS** (OpenAI) | 20B/3.6B, 120B/5.1B | MoE (MXFP4) | Apache 2.0 | Reasoning, agentic, code, single-GPU frontier |
| **DeepSeek V3/R1** | 671B/37B + distilled 1.5B-70B | MoE (MLA) | MIT | Math (97.3% MATH-500), reasoning |
| **Mistral** | Small 24B, Medium 128B, Mixtral 141B | Dense + MoE | Apache 2.0 / MIT | Code (Devstral #1 SWE-bench), general |
| **Gemma 3** (Google) | 1B, 4B, 12B, 27B | Dense, multimodal | Gemma Terms | Multilingual (140+ langs), vision |
| **Nemotron** (NVIDIA) | 30B-A3B, 70B, 340B | MoE + Dense | NVIDIA Open License | Synthetic data gen, omnimodal |

^[open-weight-models-catalog-2026.md]

## Tier 2: Strong General-Purpose

| Family | Sizes | License | Best For |
|--------|-------|---------|----------|
| **Phi-4** (Microsoft) | 3.8B, 14B | MIT | Math/reasoning for size, consumer GPU |
| **Qwen2.5-Coder** (Alibaba) | 0.5B–32B | Apache 2.0 | Code (matches GPT-4o) |
| **StarCoder 2** (BigCode) | 3B, 7B, 15B | OpenRAIL-M | 600+ programming languages |
| **InternLM 2.5** (Shanghai AI Lab) | 7B–36B | Apache 2.0 | 1M context, math, multimodal |
| **Yi-1.5** (01.AI) | 6B, 9B, 34B | Apache 2.0 | Bilingual EN/ZH (superseded by Qwen3) |

## Tier 3: Specialized

| Family | Architecture | License | Unique Angle |
|--------|-------------|---------|-------------|
| **Falcon 3** (TII) | Dense, 1B–10B | Apache 2.0-based | STEM/code focus, 32K context |
| **RWKV-7** | RNN (non-transformer) | Apache 2.0 | O(n) linear complexity, unlimited context |
| **Jamba 1.5** (AI21) | SSM+Transformer hybrid MoE | Permissive | 2.5x faster inference, 256K context |
| **Snowflake Arctic** | Dense-MoE hybrid, 480B/17B | Apache 2.0 | Enterprise (largely superseded) |

## Top Recommendation by Use Case

| Use Case | First Choice | Why |
|----------|-------------|-----|
| General fine-tuning | **Qwen3-32B** | Apache 2.0, 119 langs, thinking mode, broad strength |
| Code | **Devstral 24B** or **Qwen2.5-Coder-32B** | SWE-bench #1; GPT-4o-level coding |
| Math/Reasoning | **DeepSeek-R1 distilled 32B** | Frontier reasoning via distillation |
| Multilingual | **Qwen3** (119) or **Gemma 3** (140+) | Largest language coverage |
| On-device | **Phi-4-mini 3.8B** | MIT, 128K context, fits 8GB |
| Agentic | **GPT-OSS-120B** | Harmony format, tool use built-in |
| Maximum context | **Llama 4 Scout** (10M) | Unprecedented context window |

## Related

- [[Fine-Tuning Decision Framework]] — When to use LoRA vs full SFT vs QLoRA
- [[GPT-OSS-120B]] — OpenAI's open-weight reasoning model
- [[Qwen3 Language Model]] — Alibaba's flagship open model
