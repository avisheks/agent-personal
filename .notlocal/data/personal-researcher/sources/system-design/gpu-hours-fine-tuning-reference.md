---
title: GPU Hours for Fine-Tuning LLMs — Comprehensive Reference
url: https://blog.eleuther.ai/transformer-math/
ingestedAt: 2026-06-07
type: benchmark
additional_sources:
  - https://huggingface.co/blog/llama3
  - https://huggingface.co/blog/llama31
  - https://huggingface.co/blog/mixtral
  - https://huggingface.co/blog/gemma2
  - https://huggingface.co/blog/personal-copilot
  - https://arxiv.org/abs/2305.14314
  - https://www.answer.ai/posts/2024-03-06-fsdp-qlora.html
  - https://www.together.ai/pricing
  - https://arxiv.org/abs/2305.16264
---

# GPU Hours for Fine-Tuning LLMs

## Core Formula (EleutherAI Transformer Math)

```
Training Time (seconds) = 6 * P * D / tau
```

Where:
- P = model parameters
- D = training tokens (dataset_examples * avg_tokens_per_example * epochs)
- tau = aggregate throughput = (Num_GPUs) * (Actual FLOP/s per GPU)

Practical FLOP/s per GPU:
- A100: ~120-180 TFLOP/s (150 typical with Flash Attention)
- H100: ~300-400 TFLOP/s (~2x A100)
- RTX 4090: ~165 TFLOP/s FP16 (~82 TFLOP/s effective for training)

For LoRA/QLoRA: forward pass still processes full model, so actual speedup is ~2-4x (not proportional to trainable params reduction).

## Memory Requirements by Method

| Method | Bits | 7-8B | 13-14B | 30-32B | 70-72B | 405B |
|--------|------|------|--------|--------|--------|------|
| Full SFT (FP32 optim) | 16+32 | 120 GB | 240 GB | 600 GB | 1,200 GB | ~7,200 GB |
| Full SFT (BF16) | 16 | 60 GB | 120 GB | 300 GB | 600 GB | ~3,250 GB |
| LoRA (16-bit) | 16 | 16 GB | 32 GB | 64 GB | 160 GB | ~950 GB |
| QLoRA (8-bit) | 8 | 10 GB | 20 GB | 40 GB | 80 GB | ~500 GB |
| QLoRA (4-bit) | 4 | 6 GB | 12 GB | 24 GB | 48 GB | ~250 GB |

Source: LLaMA-Factory, HuggingFace Llama 3.1 blog

## Verified Fine-Tuning Benchmarks

### Llama 3 Family

| Model | Method | Hardware | Dataset | Time | Cost |
|-------|--------|----------|---------|------|------|
| Llama 3 8B | QLoRA 4-bit | 1x A10G (24GB) | ~9.5K examples | ~4 hours | ~$4-5 |
| Llama 3.1 8B | QLoRA (Unsloth) | 1x A100 80GB | Alpaca-52K | ~1-2 hours | ~$3-5 |
| Llama 3.1 70B | LoRA | 8x A100 80GB | 10K-100K examples | 4-12 hours | $50-150 |
| Llama 3.1 405B | QLoRA 4-bit | 4-8x H100 80GB | — | Multi-day | $500-2000+ |

### Mistral / Mixtral

| Model | Method | Hardware | Dataset | Time |
|-------|--------|----------|---------|------|
| Mistral 7B | QLoRA 4-bit | 1x A100 40GB | 10K examples | 1-2 hours |
| Mixtral 8x7B | QLoRA 4-bit | 1x A100 80GB | UltraChat 200K | ~48 hours |
| Mixtral 8x22B | QLoRA 4-bit | 2-4x A100 80GB | — | 48-96 hours |

### StarCoder 15.5B (Cost Comparison)

| Method | Hardware | Time | Cost |
|--------|----------|------|------|
| Full SFT | 8x A100 80GB | 9 hours | $108 |
| QLoRA 4-bit | 1x A100 40GB | 12.5 hours | $13.75 |

## Estimated GPU Hours by Model Size

### Full SFT (10K examples, 4096 tokens, 3 epochs = ~123M tokens)

| Model | GPUs Needed | A100 Hours | H100 Hours | Cost (Cloud) |
|-------|-------------|------------|------------|--------------|
| 7-8B | 4x A100 80GB | 12-24 GPU-hrs | 8-12 GPU-hrs | $15-40 |
| 13-14B | 8x A100 80GB | 40-80 GPU-hrs | 24-40 GPU-hrs | $50-100 |
| 32B | 8x A100 80GB | 96-160 GPU-hrs | 48-80 GPU-hrs | $120-250 |
| 70-72B | 16-32x A100 80GB | 320-640 GPU-hrs | 160-320 GPU-hrs | $400-1,000 |
| 405B | 128+ A100/H100 | 10,000-25,000 GPU-hrs | 5,000-12,000 GPU-hrs | $10,000-40,000 |

### LoRA (r=16-64, all linear layers)

| Model | Min Hardware | A100 GPU-hrs | Cost |
|-------|-------------|--------------|------|
| 7-8B | 1x A100 80GB | 1-3 | $2-8 |
| 13-14B | 1-2x A100 80GB | 2-10 | $5-15 |
| 32B | 2-4x A100 80GB | 8-40 | $15-60 |
| 70-72B | 4-8x A100 80GB | 24-120 | $40-180 |
| 405B | 16-32x H100 | 480-1,920 | $700-3,000 |

### QLoRA 4-bit

| Model | Min Hardware | Time (wall clock) | Cost |
|-------|-------------|-------------------|------|
| 7-8B | 1x RTX 4090 (24GB) | 2-6 hours | $1-4 |
| 13-14B | 1x A100 40GB | 3-8 hours | $3-12 |
| 32B | 1x A100 80GB | 6-15 hours | $10-25 |
| 70-72B | 2x A100 80GB | 12-30 hours | $20-60 |
| 405B | 4-8x H100 80GB | 48-120 hours | $200-600 |

## Managed Fine-Tuning Services (per 1M Training Tokens)

| Provider | Model Size | LoRA | Full SFT |
|----------|-----------|------|----------|
| Together AI | Up to 16B | $0.48 | $0.54 |
| Together AI | 17-69B | $1.50 | $1.65 |
| Together AI | 70-100B | $2.90 | $3.20 |
| Together AI | GPT-OSS-120B | $5.00 | N/A |
| Together AI | Qwen3-235B | $6.00 | N/A |

## Cloud GPU Pricing (per GPU-hour)

| GPU | RunPod | GCP On-Demand | GCP Spot | Lambda Labs |
|-----|--------|---------------|----------|-------------|
| RTX 4090 (24GB) | $0.69 | N/A | N/A | ~$0.50 |
| A100 40GB | N/A | $2.93 | $0.88 | $1.10 |
| A100 80GB | $1.39-1.49 | $3.67 | $1.10 | ~$1.50 |
| H100 80GB | $2.89-3.29 | $10.20 | $3.06 | N/A |

## Scaling Laws

1. **Linear with model size**: 2x params ≈ 2x time
2. **Linear with dataset tokens**: 2x data ≈ 2x time
3. **Near-linear with seq length** (Flash Attention): 2x seq ≈ 2x time + 2x memory
4. **Inverse linear with GPU count** (data parallel): 2x GPUs ≈ 0.5x time
5. **H100 vs A100**: H100 is ~1.7-2.5x faster
6. **LoRA vs Full**: 2-4x faster, 3-10x less memory
7. **QLoRA vs LoRA**: ~50% less memory, ~10-20% slower (quant/dequant overhead)
8. **Diminishing returns**: Beyond 4 epochs of data repetition, negligible improvement
