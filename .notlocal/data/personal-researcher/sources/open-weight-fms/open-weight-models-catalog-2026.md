---
title: "Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026)"
url: "multiple (HuggingFace model cards, official announcements, arxiv papers, benchmark leaderboards)"
ingestedAt: "2026-06-07T00:00:00Z"
type: "article"
---

# Open-Weight Foundation Models Catalog (Mid-2026)

## Tier 1: Frontier

### Meta Llama 4 / 3.3 / 3.1
- Llama 4 Scout: 109B total / 17B active (MoE, 16 experts), 10M context, multimodal
- Llama 4 Maverick: 400B total / 17B active (MoE, 128 experts), 1M context, multimodal
- Llama 3.3: 70B dense, 128K context
- Llama 3.1: 8B/70B/405B dense, 128K context
- License: Llama Community (commercial OK, 700M MAU cap)
- Languages: 12

### Qwen3 / Qwen2.5 (Alibaba)
- Dense: 0.6B, 1.7B, 4B, 8B, 14B, 32B
- MoE: 30B-A3B, 235B-A22B
- 128K context (YaRN), 119 languages, Apache 2.0
- Dual thinking/non-thinking modes
- Qwen2.5-Coder: 0.5B-32B, code-specialized, Apache 2.0

### GPT-OSS (OpenAI)
- 120B: 117B total / 5.1B active (MoE, 128 experts, top-4), MXFP4, single H100
- 20B: 21B total / 3.6B active, fits 16GB
- Apache 2.0, released Aug 2025
- Harmony format, adjustable reasoning levels, agentic (tool use/web/code)

### DeepSeek V3 / R1
- V3: 671B total / 37B active (MoE, MLA), 128K, MIT
- R1: Same architecture, frontier reasoning (97.3% MATH-500)
- R1 Distilled: 1.5B-70B dense (Qwen2.5/Llama3 base), practical for fine-tuning
- Strong math (90.2% MATH-500), code (82.6% HumanEval-Mul)

### Mistral AI
- Mistral Medium 3.5: 128B dense, 128K, modified MIT (commercial OK)
- Mistral Small 3.1 / Devstral: 24B, Apache 2.0, SWE-bench #1 open-source (46.8%)
- Mixtral 8x22B: 141B MoE, 64K, Apache 2.0
- Mistral Large: 123B dense, research only (NON-COMMERCIAL)

### Google Gemma 3 / 2
- Gemma 3: 1B, 4B, 12B, 27B (multimodal), 128K, 140+ languages
- Gemma 2: 2B, 9B, 27B (text only), 8K
- Gemma Terms of Use (commercial OK)

### NVIDIA Nemotron
- Nemotron 3 Nano Omni: 30B-A3B MoE, 256K, omnimodal (text/image/audio/video)
- Nemotron-4-340B: 340B dense, synthetic data generation
- Llama-3.1-Nemotron-70B: 71B dense, 128K
- NVIDIA Open Model License (commercial OK)

## Tier 2: Strong General-Purpose

### Microsoft Phi-4
- Phi-4: 14B dense, 16K, MIT, exceptional math (80.4% MATH)
- Phi-4-mini: 3.8B, 128K, MIT, fits consumer GPU
- English-primary

### Cohere Command R+
- 104B dense, 128K, CC-BY-NC (NON-COMMERCIAL)
- Excellent RAG with citation support, 23 languages

### 01.AI Yi / Yi-1.5
- 6B, 9B, 34B dense, 200K context variant, Apache 2.0
- Bilingual EN/ZH (largely superseded by Qwen3)

### StarCoder 2 (BigCode)
- 3B, 7B, 15B, 16K context, OpenRAIL-M (permissive)
- 600+ programming languages, 4T+ tokens

### InternLM 2.5 (Shanghai AI Lab)
- 7B primary, 1M context, Apache 2.0
- Strong math, tool use, multimodal variants (InternVL)

## Tier 3: Specialized / Smaller

### TII Falcon 3
- 1B, 3B, 7B, 10B dense, 32K, Apache 2.0-based license

### RWKV-7 "Goose"
- 0.1B-3B, RNN-based (NOT transformer), unlimited context, Apache 2.0
- Linear O(n) complexity

### Jamba 1.5 (AI21 Labs)
- 52B/398B MoE (SSM+Transformer hybrid), 256K, permissive
- 2.5x faster inference than comparable transformers

### Snowflake Arctic
- 480B total / 17B active (dense-MoE hybrid), Apache 2.0
- Enterprise-focused, largely superseded

## Decision Framework

### By Use Case
| Use Case | Top Pick | Runner-up | Budget |
|----------|----------|-----------|--------|
| General chat | Qwen3-32B | Llama 4 Maverick | Qwen3-8B |
| Code generation | Devstral (24B) | Qwen2.5-Coder-32B | Qwen2.5-Coder-7B |
| Math/reasoning | DeepSeek-R1 distilled 32B | Qwen3-32B (thinking) | Phi-4 (14B) |
| Multilingual | Qwen3 (119 langs) | Gemma 3 (140+ langs) | Llama 4 (12 langs) |
| Long context | Llama 4 Scout (10M) | Jamba 1.5 (256K) | InternLM 2.5 (1M) |
| Agentic/tool use | GPT-OSS-120B | Devstral | Mistral Small 3.1 |
| On-device/edge | Phi-4-mini (3.8B) | Qwen3-4B | Gemma 3 1B |

### By Hardware
| Hardware | Fits (inference) | Fine-tuning method |
|----------|-----------------|-------------------|
| 8GB VRAM | GPT-OSS-20B (QLoRA), Qwen3-4B | QLoRA only |
| 16-24GB | GPT-OSS-20B (LoRA), Qwen3-8B, Phi-4 | QLoRA or LoRA |
| 80GB (A100/H100) | GPT-OSS-120B, Qwen3-32B, 70B models | LoRA or full SFT (smaller) |
| 4-8× H100 | DeepSeek-R1-70B (full SFT), Llama 4 | Full SFT |
| Multi-node | DeepSeek V3/R1 (671B), Nemotron-340B | Distributed full SFT |

### By License
| Fully Permissive (Apache 2.0/MIT) | Permissive with Conditions | Non-Commercial |
|-----------------------------------|---------------------------|----------------|
| Qwen3, GPT-OSS, Mixtral, Phi-4, Falcon 3, RWKV | Llama 4 (700M MAU), Gemma 3 (Google terms), Nemotron | Mistral Large, Command R+ |

### By Data Volume
| Data | Approach | Best Models |
|------|----------|-------------|
| <100 examples | Few-shot or light LoRA (r=8) | Qwen3-32B, GPT-OSS-120B |
| 100-1K | LoRA (r=16-32) | Phi-4, Qwen3-8B, Mistral Small |
| 1K-10K | LoRA (r=64+) or QLoRA on base | Qwen3-32B, Llama 70B |
| 10K-100K | Full SFT on smaller model | Qwen3-14B, Llama 8B |
| 100K+ | Full SFT or continued pretraining | Qwen3-8B (CPT+SFT) |
