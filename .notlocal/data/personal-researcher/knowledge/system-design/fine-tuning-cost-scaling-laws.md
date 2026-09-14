---
title: "Fine-Tuning Cost Scaling Laws"
summary: "Empirical relationships showing linear scaling with model size and dataset tokens, inverse scaling with GPU count, and efficiency multipliers for different methods."
sources:
  - system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-15T11:54:38.947391+00:00
updatedAt: 2026-06-15T11:54:38.947391+00:00
---
# Fine-Tuning Cost Scaling Laws

Fine-tuning cost scaling laws describe the mathematical relationships between model parameters, dataset size, hardware configuration, and computational requirements for adapting pre-trained language models. These laws enable practitioners to estimate GPU hours, memory requirements, and costs before beginning fine-tuning projects. ^[gpu-hours-for-fine-tuning-llms.md]

## Core Mathematical Framework

The fundamental formula for training time estimation follows the EleutherAI Transformer Math framework:

```
Training Time (seconds) = 6 * P * D / tau
```

Where P represents model parameters, D represents training tokens (dataset examples × average tokens per example × epochs), and tau represents aggregate throughput (number of GPUs × actual FLOP/s per GPU). ^[gpu-hours-for-fine-tuning-llms.md]

Practical FLOP/s performance varies significantly by hardware: A100 GPUs typically achieve 120-180 TFLOP/s with Flash Attention (150 TFLOP/s typical), H100 GPUs reach 300-400 TFLOP/s (approximately 2x A100 performance), and RTX 4090 GPUs deliver ~165 TFLOP/s FP16 with ~82 TFLOP/s effective training performance. ^[gpu-hours-for-fine-tuning-llms.md]

## Memory Scaling Patterns

Memory requirements scale predictably across different fine-tuning methods and model sizes. Full [[Supervised Fine-Tuning (SFT)]] with FP32 optimizers requires approximately 120 GB for 7-8B parameter models, scaling to 1,200 GB for 70-72B models and ~7,200 GB for 405B models. [[Parameter-Efficient Fine-Tuning (PEFT)]] methods dramatically reduce these requirements: [[Low-Rank Adaptation (LoRA)]] with 16-bit precision needs only 16 GB for 7-8B models, while [[QLoRA (Quantized LoRA)]] with 4-bit quantization requires just 6 GB for the same model size. ^[gpu-hours-for-fine-tuning-llms.md]

## Hardware Scaling Laws

Several key scaling relationships govern fine-tuning performance. Training time scales linearly with model parameters (2x parameters ≈ 2x time) and linearly with dataset tokens (2x data ≈ 2x time). Sequence length scaling is near-linear with Flash Attention (2x sequence length ≈ 2x time + 2x memory). GPU count scaling follows inverse linear relationships in data parallel configurations (2x GPUs ≈ 0.5x time). ^[gpu-hours-for-fine-tuning-llms.md]

Hardware generation improvements provide substantial speedups: H100 GPUs deliver 1.7-2.5x faster performance compared to A100 GPUs. Method efficiency varies significantly: LoRA provides 2-4x speed improvements and 3-10x memory reduction compared to full fine-tuning, while QLoRA achieves ~50% memory reduction compared to LoRA with ~10-20% slower performance due to quantization overhead. ^[gpu-hours-for-fine-tuning-llms.md]

## Empirical Benchmarks

Verified benchmarks demonstrate these scaling laws in practice. Llama 3 8B fine-tuning with QLoRA 4-bit on a single A10G (24GB) requires approximately 4 hours for ~9.5K examples at $4-5 cost. Llama 3.1 70B with LoRA on 8x A100 80GB takes 4-12 hours for 10K-100K examples at $50-150 cost. Mixtral 8x7B with QLoRA 4-bit on a single A100 80GB requires ~48 hours for UltraChat 200K dataset. ^[gpu-hours-for-fine-tuning-llms.md]

Cost comparisons reveal dramatic efficiency differences between methods. StarCoder 15.5B full SFT on 8x A100 80GB takes 9 hours at $108 cost, while QLoRA 4-bit on a single A100 40GB requires 12.5 hours at $13.75 cost, demonstrating the cost-time trade-offs inherent in different approaches. ^[gpu-hours-for-fine-tuning-llms.md]

## Cost Estimation Framework

For full SFT with 10K examples, 4096 tokens, and 3 epochs (~123M tokens), costs scale from $15-40 for 7-8B models to $400-1,000 for 70-72B models and $10,000-40,000 for 405B models. LoRA fine-tuning reduces these costs dramatically: 7-8B models cost $2-8, while 70-72B models cost $40-180. QLoRA 4-bit provides the most economical option: 7-8B models cost $1-4, and even 70-72B models cost only $20-60. ^[gpu-hours-for-fine-tuning-llms.md]

## Diminishing Returns Patterns

The scaling laws reveal important efficiency boundaries. Beyond 4 epochs of data repetition, improvements become negligible, establishing practical limits for dataset reuse. LoRA rank selection follows similar patterns, with ranks beyond 64-128 providing minimal benefits for most tasks while significantly increasing computational costs. ^[gpu-hours-for-fine-tuning-llms.md]

## Managed Service Economics

Managed fine-tuning services follow predictable pricing patterns based on model size. Together AI charges $0.48 per 1M training tokens for LoRA on models up to 16B parameters, $1.50 for 17-69B models, $2.90 for 70-100B models, and $5.00 for [[GPT-OSS-120B]]. These prices reflect the underlying computational scaling laws while incorporating service margins and infrastructure costs. ^[gpu-hours-for-fine-tuning-llms.md]
