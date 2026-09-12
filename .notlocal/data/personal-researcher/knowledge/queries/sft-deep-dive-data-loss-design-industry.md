---
title: "Deep dive on SFT for LLMs: data prep, loss functions, design choices, application quirks, industry differences?"
summary: "Quality>>quantity (LIMA: 1K examples, DEITA: 6K matches SOTA). Packing gives 2x throughput + 58% less hallucination. NEFTune is biggest free win (+35% AlpacaEval). 1-3 epochs max (4x repetition is free). Code: FIM 50%. Math: process supervision 78% MATH. Industry: OpenAI (SFT→RLHF), Anthropic (self-critique), Meta (10M demos), DeepSeek (minimal SFT→GRPO), Qwen (18T pretrain + 1M SFT + 29 langs)."
type: query
createdAt: 2026-06-09
topic: sft
---

# SFT Deep Dive: Data, Loss Functions, Design Choices, Applications, Industry

## Quick Answer

SFT is the foundation of all LLM post-training. The key insights: **quality dominates quantity** (1K-10K curated examples can match massive datasets), **packing is mandatory** (2x throughput, 58% less hallucination), **NEFTune is free performance** (+8-35%), **1-3 epochs is optimal** (4x data repetition is free per scaling laws), and **every top lab follows SFT with RL** because SFT is bounded by demonstration quality.

## Data Preparation — What Matters Most

### Quality >> Quantity (Proven)

| Evidence | Data Size | Result |
|----------|:---------:|--------|
| LIMA (2023) | 1K | 43% preferred over GPT-4 |
| DEITA (ICLR 2024) | 6K | 7.55 MT-Bench (matches SOTA) |
| Yi (2024) | <10K | Each example verified by ML engineers |
| Qwen 2.5 | 1M+ | But curated via quality scoring |
| Llama 3.1 | 10M+ | Massive scale with rejection sampling |

### Packing (Don't Skip This)

Best-Fit Decreasing packing (ICML 2024): **2x throughput, 20% memory reduction, 58% hallucination reduction**. Use `flash_attn_varlen_func` with `cu_seqlens`. Standard in TRL.

### Format

- Conversational (ChatML/Llama format) with `role`/`content` messages
- Train on responses only (`assistant_only_loss=True`)
- Multi-turn: loss only on assistant turns

## Loss Functions — Beyond Default CE

| Loss | Free Performance | Cost |
|------|:----------------:|------|
| NEFTune (embedding noise) | **+8-35% AlpacaEval** | Zero (just add noise) |
| Chunked NLL | -30-50% VRAM | Zero (TRL built-in) |
| ORPO | SFT + alignment in 1 step | Needs preference pairs |
| Standard CE | Baseline | — |

**NEFTune is the single biggest free improvement**: LLaMA-2-7B jumps from 29.8% to 64.7% on AlpacaEval.

## Design Choices — The Numbers

| Choice | Value | Why |
|--------|-------|-----|
| Learning rate | 2e-5 (full FT), 1e-4 (LoRA) | TRL default; works across model sizes |
| Epochs | 1-3 | Beyond 3 = memorization; 4x repetition is free |
| Batch size | 32-128 effective | Stable gradients without overfitting |
| Scheduler | Cosine with warmup | Smooth decay; most published recipes use this |
| Precision | BF16 | Larger dynamic range; no loss scaling needed |
| Weight decay | 0 to 0.01 | Short training = early stopping suffices |
| Dropout | OFF | LoRA is a better regularizer; SFT is too short for dropout to help |
| LoRA rank | 16-64 typical | Higher → approaches full FT quality at cost of efficiency |

## Application Quirks

| Domain | Key Quirk | Evidence |
|--------|-----------|----------|
| Code | FIM at 50% rate (fill-in-middle) | Does NOT harm autoregressive quality |
| Math | Process supervision (step labels) | 78% MATH vs ~60% with outcome-only |
| Chat | assistant_only_loss + system prompts | Standard practice for all dialogue SFT |
| Tool use | Train on parallel calls + implicit params | ToolLLM: 16K real APIs |
| Long context | LongLoRA: 7B → 100K context | Embedding + norm layers must be trainable |
| Vision | Image encoder/resolution matters most | Connector design is negligible (MM1) |
| Multilingual | 29+ languages (Qwen) | Cross-lingual transfer from high-resource |

## Industry Differences

| Lab | SFT Data Scale | Pipeline After SFT | What's Unique |
|-----|:--------------:|-------------------|---------------|
| OpenAI | Undisclosed | RM → PPO (InstructGPT) | Pioneered SFT→RLHF; proprietary |
| Anthropic | Self-generated | Self-critique → RLAIF | No human harm labels; constitutional principles |
| Meta | 10M+ annotations | Reject Sample → PPO → DPO | Largest published; open weights |
| DeepSeek | Minimal cold-start | GRPO (pure RL) | Proves minimal SFT + strong RL works |
| Qwen | 1M+ curated | Multi-stage RL | 18T pretrain, 29 languages, domain variants |
| Google | Undisclosed | Knowledge distillation (Gemma) | Distillation replaces SFT for small models |
| Mistral | Undisclosed | DPO | Architectural efficiency > data volume |

## The SFT Ceiling (Why RL Follows)

SFT is bounded by demonstration quality. It teaches FORMAT and STYLE, not new capabilities (those come from pretraining). Every top lab follows SFT with RL because:
- RL can exceed the demo ceiling
- RL optimizes holistic properties (safety, helpfulness) that are hard to demonstrate
- The "less is more" finding is specifically about SFT — capability is pre-trained

## Sources

- [[Supervised Fine-Tuning Deep Dive]] (knowledge page)
- LIMA (arXiv:2305.11206), DEITA (arXiv:2312.15685), Scaling (arXiv:2305.16264)
- NEFTune (arXiv:2310.05914), Fewer Truncations (arXiv:2404.10830)
- InstructGPT (arXiv:2203.02155), Llama 3.1 (arXiv:2407.21783), Qwen 2.5 (arXiv:2412.15115)
- TRL documentation (huggingface.co/docs/trl/sft_trainer)
