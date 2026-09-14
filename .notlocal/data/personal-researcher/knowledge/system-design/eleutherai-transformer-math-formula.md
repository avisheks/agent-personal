---
title: "EleutherAI Transformer Math Formula"
summary: "A mathematical formula for calculating training time as 6 * P * D / tau, where P is model parameters, D is training tokens, and tau is aggregate throughput."
sources:
  - system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-15T11:54:03.138867+00:00
updatedAt: 2026-06-15T11:54:03.138867+00:00
---
# EleutherAI Transformer Math Formula

The **EleutherAI Transformer Math Formula** is a computational framework for estimating training time and resource requirements for [[transformer-architecture]] models. The formula provides a standardized approach to calculate GPU hours, memory requirements, and costs for various fine-tuning methods including full [[supervised-fine-tuning-sft]], [[low-rank-adaptation-lora]], and [[qlora-quantized-lora]]. ^[gpu-hours-for-fine-tuning-llms.md]

## Core Mathematical Framework

The fundamental equation for training time estimation is:

```
Training Time (seconds) = 6 * P * D / tau
```

Where:
- **P** = total model parameters
- **D** = training tokens (dataset_examples × avg_tokens_per_example × epochs)  
- **tau** = aggregate throughput = (Num_GPUs) × (Actual FLOP/s per GPU)

The constant "6" represents the theoretical FLOP count per parameter per token in [[autoregressive-language-model]] training, accounting for both forward and backward passes. ^[gpu-hours-for-fine-tuning-llms.md]

## Hardware Performance Benchmarks

### GPU Throughput Values

Practical FLOP/s performance varies significantly by hardware generation:

- **A100**: ~120-180 TFLOP/s (150 TFLOP/s typical with Flash Attention)
- **H100**: ~300-400 TFLOP/s (approximately 2x A100 performance)
- **RTX 4090**: ~165 TFLOP/s FP16 (~82 TFLOP/s effective for training workloads)

These values incorporate real-world efficiency factors including memory bandwidth limitations and attention mechanism optimizations. ^[gpu-hours-for-fine-tuning-llms.md]

## Memory Requirements by Training Method

Memory consumption scales differently across fine-tuning approaches:

### Full SFT Requirements
- **FP32 optimization**: 120 GB for 7-8B models, scaling to ~7,200 GB for 405B models
- **BF16 precision**: 60 GB for 7-8B models, scaling to ~3,250 GB for 405B models

### Parameter-Efficient Methods
- **[[low-rank-adaptation-lora]] (16-bit)**: 16 GB for 7-8B models, ~950 GB for 405B models
- **[[qlora-quantized-lora]] (8-bit)**: 10 GB for 7-8B models, ~500 GB for 405B models  
- **[[qlora-quantized-lora]] (4-bit)**: 6 GB for 7-8B models, ~250 GB for 405B models

The memory reduction in LoRA methods comes from storing only low-rank adaptation matrices rather than full model gradients, though the forward pass still processes the complete model. ^[gpu-hours-for-fine-tuning-llms.md]

## Empirical Training Benchmarks

### Llama Model Family Performance

Verified benchmarks demonstrate scaling patterns across model sizes:

- **Llama 3 8B + QLoRA 4-bit**: ~4 hours on 1x A10G (24GB) for 9.5K examples
- **Llama 3.1 8B + QLoRA**: 1-2 hours on 1x A100 80GB for Alpaca-52K dataset
- **Llama 3.1 70B + LoRA**: 4-12 hours on 8x A100 80GB for 10K-100K examples
- **Llama 3.1 405B + QLoRA 4-bit**: Multi-day training on 4-8x H100 80GB

### Mixture-of-Experts Performance

[[mixture-of-experts-moe]] architectures show different scaling characteristics:

- **Mixtral 8x7B + QLoRA 4-bit**: ~48 hours on 1x A100 80GB for UltraChat 200K
- **Mixtral 8x22B + QLoRA 4-bit**: 48-96 hours on 2-4x A100 80GB

The sparse activation patterns in MoE models create non-linear scaling relationships compared to dense architectures. ^[gpu-hours-for-fine-tuning-llms.md]

## Cost Analysis Framework

### Cloud Training Economics

Training costs vary significantly by method and model size. For a standard 10K example dataset (123M tokens total):

**Full SFT Costs:**
- 7-8B models: $15-40 on cloud infrastructure
- 32B models: $120-250  
- 70-72B models: $400-1,000
- 405B models: $10,000-40,000

**QLoRA 4-bit Costs:**
- 7-8B models: $1-4
- 32B models: $10-25
- 70-72B models: $20-60
- 405B models: $200-600

### Managed Service Pricing

Commercial fine-tuning services offer standardized pricing per million training tokens:
- Models up to 16B: $0.48 (LoRA) to $0.54 (Full SFT)
- Models 17-69B: $1.50 (LoRA) to $1.65 (Full SFT)  
- Models 70-100B: $2.90 (LoRA) to $3.20 (Full SFT)

These services abstract infrastructure management while providing predictable cost structures. ^[gpu-hours-for-fine-tuning-llms.md]

## Scaling Laws and Optimization Principles

### Computational Scaling Relationships

The formula reveals several key scaling behaviors:

1. **Linear parameter scaling**: 2x model parameters ≈ 2x training time
2. **Linear data scaling**: 2x training tokens ≈ 2x training time  
3. **Near-linear sequence length scaling**: 2x sequence length ≈ 2x time + 2x memory (with Flash Attention)
4. **Inverse GPU scaling**: 2x GPUs ≈ 0.5x training time (data parallel)

### Method-Specific Efficiency Gains

- **LoRA vs Full SFT**: 2-4x faster training, 3-10x memory reduction
- **QLoRA vs LoRA**: ~50% memory reduction, ~10-20% slower due to quantization overhead
- **H100 vs A100**: 1.7-2.5x performance improvement

### Diminishing Returns Threshold

Empirical evidence shows diminishing returns beyond 4 epochs of data repetition, with negligible improvement in model performance despite linear increases in computational cost. ^[gpu-hours-for-fine-tuning-llms.md]

## Applications and Limitations

The EleutherAI formula provides reliable estimates for standard [[supervised-fine-tuning-sft]] scenarios but has limitations for specialized training regimes. It assumes standard [[autoregressive-language-model]] architectures and may require adjustments for novel architectures or training objectives like [[reinforcement-learning-from-human-feedback-rlhf]]. ^[gpu-hours-for-fine-tuning-llms.md]

The framework serves as a foundational tool for resource planning in [[ai-coding-agents]], [[constitutional-ai-training-pipeline]], and other applications requiring precise computational budgeting for model development.
