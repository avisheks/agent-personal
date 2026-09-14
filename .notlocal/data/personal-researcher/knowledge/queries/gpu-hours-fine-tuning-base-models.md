---
title: "Estimated GPU hours (with breakdown) for fine-tuning different base models?"
summary: "Full SFT ranges from 12 GPU-hrs (8B) to 25,000 GPU-hrs (405B); QLoRA 4-bit brings this to 2-6 hrs on a single consumer GPU for 8B models, $20-60 for 70B. Scaling is linear with model size and dataset tokens."
type: query
createdAt: 2026-06-07
topic: system-design
---

# Estimated GPU Hours for Fine-Tuning Different Base Models

## Quick Answer

For a standard fine-tuning run (10K examples, 4096 tokens/example, 3 epochs):

| Model | Full SFT (A100 GPU-hrs) | LoRA (A100 GPU-hrs) | QLoRA 4-bit (wall clock, min HW) | QLoRA Cost |
|-------|:-----------------------:|:-------------------:|:--------------------------------:|:----------:|
| 7-8B | 12-24 | 1-3 | 2-6 hrs (1x RTX 4090) | $1-4 |
| 13-14B | 40-80 | 2-10 | 3-8 hrs (1x A100 40GB) | $3-12 |
| 32B | 96-160 | 8-40 | 6-15 hrs (1x A100 80GB) | $10-25 |
| 70-72B | 320-640 | 24-120 | 12-30 hrs (2x A100 80GB) | $20-60 |
| 141B (MoE) | 1,280-2,560 | 120-480 | 24-60 hrs (4x A100 80GB) | $50-120 |
| 405B | 10,000-25,000 | 480-1,920 | 48-120 hrs (4-8x H100) | $200-600 |

## Formula

```
Training Time (seconds) = 6 * P * D / tau
```

Where P = parameters, D = total training tokens, tau = GPUs * FLOP/s per GPU.

## Key Factors

1. **Method choice dominates cost**: QLoRA is 8-50x cheaper than Full SFT
2. **Dataset size scales linearly**: 100K examples = 10x the time of 10K
3. **Sequence length scales linearly** with Flash Attention (quadratic without)
4. **H100 is 1.7-2.5x faster** than A100 per GPU-hour
5. **Diminishing returns beyond 4 epochs** of data repetition

## Managed Alternative

Together AI offers per-token pricing: $0.48-6.00 per 1M training tokens depending on model size. A typical 70B LoRA run (10K examples) costs ~$180 via managed service vs ~$40-180 self-managed.

## Sources

- [[GPU Hours for Fine-Tuning LLMs]]
- EleutherAI Transformer Math (blog.eleuther.ai/transformer-math/)
- HuggingFace model blogs (Llama 3, Mixtral, Gemma 2)
- LLaMA-Factory memory requirements
- Together AI, RunPod, GCP pricing (as of June 2026)
