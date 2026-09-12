---
title: GPU Hours for Fine-Tuning LLMs
summary: Comprehensive reference for estimated GPU hours, memory requirements, and costs for fine-tuning base models (7B-405B) across Full SFT, LoRA, and QLoRA methods on A100/H100/consumer GPUs.
sources:
  - sources/system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-07
updatedAt: 2026-06-07
---

# GPU Hours for Fine-Tuning LLMs

## Core Estimation Formula

From EleutherAI's Transformer Math:

```
Training Time (seconds) = 6 * P * D / tau
```

- P = model parameters
- D = total training tokens (examples * tokens_per_example * epochs)
- tau = Num_GPUs * FLOP/s per GPU

Practical throughput: A100 ~150 TFLOP/s, H100 ~350 TFLOP/s, RTX 4090 ~82 TFLOP/s effective.

## Quick Reference Table (10K examples, 4K seq, 3 epochs)

| Model Size | Full SFT (GPU-hrs) | LoRA (GPU-hrs) | QLoRA 4-bit (wall clock) | QLoRA Cost |
|-----------|--------------------:|---------------:|-------------------------:|-----------:|
| 7-8B | 12-24 | 1-3 | 2-6 hrs (1x 4090) | $1-4 |
| 13-14B | 40-80 | 2-10 | 3-8 hrs (1x A100) | $3-12 |
| 32B | 96-160 | 8-40 | 6-15 hrs (1x A100-80) | $10-25 |
| 70-72B | 320-640 | 24-120 | 12-30 hrs (2x A100-80) | $20-60 |
| 405B | 10,000-25,000 | 480-1,920 | 48-120 hrs (4-8x H100) | $200-600 |

## Memory Requirements

| Method | 7-8B | 32B | 70-72B | 405B |
|--------|------|-----|--------|------|
| Full SFT (BF16) | 60 GB | 300 GB | 600 GB | 3,250 GB |
| LoRA (16-bit) | 16 GB | 64 GB | 160 GB | 950 GB |
| QLoRA (4-bit) | 6 GB | 24 GB | 48 GB | 250 GB |

## Scaling Laws

- 2x model params → 2x time
- 2x dataset → 2x time
- 2x seq length → ~2x time (Flash Attention) or ~4x (standard attention)
- 2x GPUs → ~0.5x time (data parallel, good interconnect)
- H100 → 1.7-2.5x faster than A100
- LoRA → 2-4x faster than Full SFT, 3-10x less memory
- QLoRA → ~50% less memory than LoRA, 10-20% slower
- Beyond 4 epochs → diminishing returns

## Key Verified Benchmarks

- Llama 3 8B QLoRA on 1x A10G: ~4 hrs, ~$4 (HuggingFace blog)
- Mixtral 8x7B QLoRA on 1x A100-80: ~48 hrs (HuggingFace blog)
- StarCoder 15.5B Full SFT: 9 hrs/$108 vs QLoRA: 12.5 hrs/$13.75

## Managed Services

Together AI pricing per 1M training tokens: $0.48 (≤16B LoRA), $1.50 (17-69B), $2.90 (70-100B), $5.00 (GPT-OSS-120B), $6.00 (Qwen3-235B).

## Related

- [[Low-Rank Adaptation (LoRA)]]
- [[QLoRA (Quantized LoRA)]]
- [[Supervised Fine-Tuning (SFT)]]
- [[Mixed-Precision Training]]
