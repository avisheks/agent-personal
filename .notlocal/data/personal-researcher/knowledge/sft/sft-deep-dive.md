---
title: "Supervised Fine-Tuning Deep Dive"
summary: "Definitive SFT reference: data prep (quality>>quantity, LIMA 1K examples, packing 2x throughput), loss functions (CE, NEFTune +35%, chunked NLL -50% VRAM), design choices (lr 2e-5, 1-3 epochs, BF16, cosine), application quirks (code FIM 50%, math process supervision 78%, long context LongLoRA 100K), and industry differences (OpenAI→RLHF, Anthropic→RLAIF, Meta→10M demos, DeepSeek→minimal SFT+GRPO)."
sources:
  - sources/sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-09
updatedAt: 2026-06-09
---

# Supervised Fine-Tuning Deep Dive

## The Practitioner's Recipe (7B model, start here)

```
1. Curate 10K-50K high-quality examples (quality >> quantity)
2. Conversational format with proper chat template
3. Train on responses only (assistant_only_loss=True)
4. Pack sequences with BFD + Flash Attention 2
5. lr=2e-5 (full FT) or 1e-4 (LoRA), cosine scheduler, 30-step warmup
6. 2-3 epochs max, effective batch size 32-128
7. BF16, gradient checkpointing enabled
8. Enable NEFTune (+8-35% improvement, zero cost)
9. Monitor validation loss; stop if it increases
```

## Data Preparation

### Quality vs Quantity (The Evidence)

| Finding | Paper | Implication |
|---------|-------|-------------|
| 1K examples → 43% preferred over GPT-4 | LIMA (2023) | Quality dominates at small scale |
| 6K samples match SOTA (7.55 MT-Bench) | DEITA (ICLR 2024) | Scoring complexity/quality/diversity works |
| <10K examples, each verified by engineers | Yi (2024) | Human curation > volume |
| 4 epochs of repetition is free | Scaling Data-Constrained (2023) | Don't collect more data until you've repeated 4x |
| 10M+ annotations across post-training | Llama 3.1 | At massive scale, volume matters too |

### Packing (2x Throughput, 58% Less Hallucination)

Best-Fit Decreasing packing (ICML 2024): concatenate examples into fixed-length sequences via bin-packing. Requires `flash_attn_varlen_func` with `cu_seqlens` to prevent cross-example attention.

Results: 2x throughput, 20% memory reduction, +4.7% reading comprehension, +16.8% context following, **58% hallucination reduction** vs standard concatenation that breaks documents.

### Train-on-Responses-Only

Standard for all chat/instruction SFT. Set labels=-100 on prompt tokens. Focuses gradient on generating good responses, not imitating user prompts. Only use full-sequence loss for continued pretraining.

## Loss Functions

| Loss | Effect | When to Use |
|------|--------|-------------|
| Standard CE | Default next-token prediction | Always (baseline) |
| Answer-only (masked) | Loss on responses only | Chat/instruction SFT |
| NEFTune (noise in embeddings) | +8-35% AlpacaEval | Always enable (free improvement) |
| Chunked NLL | 30-50% less VRAM | Large vocab models (Qwen 151K tokens) |
| ORPO | SFT + preference in one step | When you have preference pairs during SFT |
| Label smoothing | Prevents overconfidence | Rarely needed (short training is enough) |

**NEFTune is the biggest free win**: LLaMA-2-7B on Alpaca goes from 29.8% to **64.7%** on AlpacaEval just by adding noise to embedding vectors during training.

## Design Choices

| Parameter | 7B | 13B | 70B | 400B+ |
|-----------|:--:|:---:|:---:|:-----:|
| LR (full FT) | 2e-5 | 1-2e-5 | 5e-6 to 1e-5 | 1-5e-6 |
| LR (LoRA) | 1-3e-4 | 1e-4 | 1e-4 | 5e-5 |
| Epochs | 2-3 | 2-3 | 1-2 | 1 |
| Batch size (eff) | 32-128 | 64-128 | 128-256 | 256+ |
| Scheduler | Cosine | Cosine | Cosine | Cosine |
| Precision | BF16 | BF16 | BF16 | BF16 |
| Weight decay | 0-0.01 | 0-0.01 | 0 | 0 |
| Dropout | Off | Off | Off | Off |

**Why dropout is off**: SFT runs are short (1-3 epochs). LoRA itself is a better regularizer than dropout (arXiv:2405.09673). Early stopping on val loss is sufficient.

**Why 1-3 epochs**: Beyond 3 epochs on instruction data, models memorize specific patterns rather than learning generalizable instruction-following. The Scaling paper proves >4 epochs of repeated data provides zero additional value.

## Application Quirks

### Code Generation
- **FIM** (fill-in-middle) at 50% rate: moves middle span to end during training. Does NOT harm autoregressive quality. "Future models should be trained with FIM by default."
- StarCoder recipe: lr=5e-5, seq=2048, 2000 steps, cosine, bf16. Full FT: 9hrs/$108 on 8xA100. QLoRA: 12.5hrs/$14 on 1xA100.

### Math/Reasoning
- **Process supervision** (step-by-step) dramatically outperforms outcome-only: 78% MATH (PRM800K).
- SFT data must have verified step-by-step solutions, not just correct final answers.
- DeepSeekMath: 120B math tokens from Common Crawl → continues pre-training before SFT.

### Long Context
- **LongLoRA** extends 7B from 4K to 100K context on single 8xA100.
- Key: embedding and normalization layers MUST be trainable for context extension.
- Shifted Sparse Attention during training, dense at inference.

### Vision-Language
- Image encoder + resolution matters most; connector design is negligible (MM1, Apple).
- LLaVA-1.5: CLIP-ViT-L-336px + MLP projection, 1.2M data, trains in 1 day on 8xA100.

### Tool Use / Function Calling
- ToolLLM: 16,464 real APIs from RapidAPI, ChatGPT generates solution paths.
- Must train on: simple calls, multiple selection, parallel calls, implicit parameter conversion.

## Industry Approaches

| Lab | SFT Philosophy | What's Unique |
|-----|---------------|---------------|
| **OpenAI** | Human demos → SFT → RM → PPO | Pioneered the pipeline; heavily proprietary |
| **Anthropic** | Self-critique/revision → SFT on revised outputs | No human harm labels; constitutional principles only |
| **Meta** | Massive annotation (10M+) → SFT → Rejection Sampling → DPO | Open weights; multi-stage; largest published SFT corpus |
| **DeepSeek** | Minimal cold-start SFT → GRPO | Proves RL can work with very little SFT; extremely cost-efficient |
| **Qwen** | 18T pretrain + 1M+ curated SFT + multilingual (29+ langs) | Broadest language coverage; domain variants (Code, Math) |
| **Google** | Knowledge distillation for small models (Gemma 2) | Novel: distillation replaces SFT for 2B/9B models |
| **Mistral** | Architectural efficiency (SWA, GQA) + minimal disclosure | Strong results from smaller models; MT-Bench 8.6 |

## Key Insight: SFT Ceiling

SFT is bounded by demonstration quality — it cannot produce outputs better than its training data (on average). This is why every top lab follows SFT with some form of RL (PPO, DPO, GRPO) to exceed the SFT ceiling. The "less is more" finding (LIMA) applies to the SFT phase specifically: what you teach in SFT is format/style, not capability — capability comes from pretraining.

## Related

- [[Supervised Fine-Tuning (SFT)]] (in sft-vs-dpo)
- [[Low-Rank Adaptation (LoRA)]]
- [[SFT vs RL Decision Framework]]
- [[GPU Hours for Fine-Tuning LLMs]]
- [[MoE SFT Debugging — Why Fine-Tuning Fails and What To Do]]
