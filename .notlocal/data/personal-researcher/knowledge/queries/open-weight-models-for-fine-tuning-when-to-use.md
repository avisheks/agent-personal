---
title: "What are all the open-weight models that can be used for fine-tuning? When to use what?"
summary: "19+ model families across 3 tiers. Tier 1 frontier: Llama 4 (10M ctx, multimodal), Qwen3 (119 langs, Apache 2.0), GPT-OSS (single-GPU frontier), DeepSeek R1 (best reasoning), Mistral/Devstral (best code), Gemma 3 (140+ langs), Nemotron (omnimodal). Default recommendation: Qwen3-32B for most fine-tuning (Apache 2.0, broad capability, standard tooling). Decision based on: use case, hardware, data volume, license, fine-tuning method."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
## All Open-Weight Models for Fine-Tuning (Mid-2026)

### Tier 1: Frontier

| Model | Params (Active) | Architecture | License | Killer Feature |
|-------|----------------|-------------|---------|----------------|
| **Llama 4 Scout/Maverick** | 109B/17B, 400B/17B | MoE, multimodal | Llama Community | 10M / 1M context |
| **Qwen3** | 0.6B–235B (dense+MoE) | Dense + MoE | Apache 2.0 | 119 languages, thinking modes |
| **GPT-OSS-120B** | 117B/5.1B | MoE (MXFP4) | Apache 2.0 | Single-GPU frontier reasoning |
| **GPT-OSS-20B** | 21B/3.6B | MoE (MXFP4) | Apache 2.0 | Fits 16GB, reasoning |
| **DeepSeek V3/R1** | 671B/37B + distilled 1.5B–70B | MoE (MLA) | MIT | 97.3% MATH-500 |
| **Mistral Medium 3.5** | 128B | Dense | Modified MIT | 90% of Claude Sonnet 3.7 |
| **Devstral** | 24B | Dense | Apache 2.0 | #1 SWE-bench open-source |
| **Mixtral 8x22B** | 141B/~35B | MoE (8 experts) | Apache 2.0 | Proven MoE at scale |
| **Gemma 3** | 1B, 4B, 12B, 27B | Dense, multimodal | Gemma Terms | 140+ languages, vision |
| **Nemotron 3 Nano** | 30B/3B | MoE, omnimodal | NVIDIA License | Text/image/audio/video, 256K |

### Tier 2: Strong General-Purpose

| Model | Params | License | Killer Feature |
|-------|--------|---------|----------------|
| **Phi-4** | 14B | MIT | Best math/reasoning for size (80.4% MATH) |
| **Phi-4-mini** | 3.8B | MIT | 128K context in 3.8B, fits 8GB |
| **Qwen2.5-Coder** | 0.5B–32B | Apache 2.0 | Matches GPT-4o on code |
| **StarCoder 2** | 3B–15B | OpenRAIL-M | 600+ programming languages |
| **InternLM 2.5** | 7B–36B | Apache 2.0 | 1M context window |
| **Yi-1.5** | 6B–34B | Apache 2.0 | EN/ZH bilingual |

### Tier 3: Specialized

| Model | Unique Angle | License |
|-------|-------------|---------|
| **Falcon 3** (1B–10B) | STEM/code, 32K | Apache 2.0-based |
| **RWKV-7** (0.1B–3B) | O(n) linear RNN, unlimited context | Apache 2.0 |
| **Jamba 1.5** (52B–398B MoE) | SSM+Transformer hybrid, 2.5x faster, 256K | Permissive |
| **Snowflake Arctic** (480B/17B) | Enterprise MoE (largely superseded) | Apache 2.0 |

## When to Use What

### By Use Case

| Use Case | First Choice | Why | Budget Alternative |
|----------|-------------|-----|-------------------|
| **General fine-tuning** | Qwen3-32B | Apache 2.0, 119 langs, thinking mode, broad | Qwen3-8B |
| **Code generation** | Devstral 24B | #1 SWE-bench open-source (46.8%) | Qwen2.5-Coder-7B |
| **Math/reasoning** | DeepSeek-R1 distilled 32B | Frontier reasoning via distillation | Phi-4 (14B) |
| **Multilingual** | Qwen3-32B (119 langs) | Broadest Apache 2.0 multilingual | Gemma 3 27B (140+ langs) |
| **Agentic/tool use** | GPT-OSS-120B | Harmony format, built for tools | Mistral Small 3.1 |
| **Long context** | Llama 4 Scout (10M) | Unprecedented length | InternLM 2.5 (1M) |
| **On-device/edge** | Phi-4-mini (3.8B) | MIT, 128K, fits 8GB | Qwen3-4B |
| **Multimodal (vision)** | Gemma 3 27B | Image understanding + 140+ langs | Llama 4 (multimodal) |

### By Hardware

| Hardware | Best Models | Method |
|----------|-------------|--------|
| **8GB VRAM** | Phi-4-mini, Qwen3-4B, GPT-OSS-20B | QLoRA only |
| **24GB VRAM** | Qwen3-8B, Phi-4 14B, Gemma 3 12B | QLoRA or LoRA |
| **80GB (A100/H100)** | Qwen3-32B, GPT-OSS-120B, Llama 70B | LoRA or full SFT (≤32B) |
| **4-8× H100** | DeepSeek-R1-70B, Llama 4 Maverick | Full SFT |
| **Multi-node** | DeepSeek V3 (671B), Nemotron-340B | Distributed SFT |

### By Data Volume

| Data | Approach | Reasoning |
|------|----------|-----------|
| **<100 examples** | Largest model + few-shot or light LoRA (r=8) | Base capability dominates |
| **100–1K** | LoRA (r=16-32) on instruct model | Enough for style/format adaptation |
| **1K–10K** | LoRA (r=64) on base model | Genuine capability tuning |
| **10K–100K** | Full SFT on smaller model | Small model fully adapts |
| **100K+** | Full SFT or continued pretraining | Domain-specific foundation |

### By License (Commercial Fine-Tuning)

| Fully Permissive (Apache 2.0/MIT) | Permissive with Conditions | NON-COMMERCIAL |
|-----------------------------------|---------------------------|----------------|
| **Qwen3**, **GPT-OSS**, **Phi-4**, **Devstral**, Mixtral, Falcon 3, RWKV, StarCoder 2 | Llama 4 (700M MAU cap), Gemma 3 (Google terms), Nemotron (NVIDIA license) | Mistral Large, Command R+, StableLM |

## Default Recommendation

**If you're unsure, start with Qwen3-32B (Apache 2.0).** It's the safest default:
- Fully permissive license
- 119 languages
- Thinking/non-thinking dual mode
- 128K context
- Standard LoRA/SFT tooling works cleanly
- Strong across all benchmarks
- Active community (Alibaba maintains regularly)

**Exception**: If your task is primarily reasoning/math → DeepSeek-R1 distilled 32B. If code → Devstral 24B. If agentic → GPT-OSS-120B. If edge → Phi-4-mini.

## Deprecated / Superseded (Do NOT Use)

| Old Model | Use Instead | Why |
|-----------|-------------|-----|
| Llama 2 | Llama 3.1 / 4 | Obsolete |
| Qwen2 | Qwen3 | Strictly better |
| Mistral 7B v0.1 | Mistral Small 24B | Much stronger |
| Code Llama | Devstral / Qwen2.5-Coder | Outperformed |
| StarCoder 1 | StarCoder 2 | Obsolete |
| Gemma 1 | Gemma 3 | Two generations behind |
| Phi-3 | Phi-4 | Superseded |

## Related

- [[Open-Weight Model Families for Fine-Tuning (2026)]]
- [[Fine-Tuning Decision Framework]]
- [[Qwen3 Language Model]]
- [[GPT-OSS-120B]]
