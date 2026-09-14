---
title: "GPU Memory Requirements by Fine-Tuning Method"
summary: "Systematic breakdown of VRAM requirements for different fine-tuning approaches ranging from 6GB (QLoRA 4-bit) to 7,200GB (Full SFT FP32) for various model sizes."
sources:
  - system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-15T11:54:18.155376+00:00
updatedAt: 2026-06-15T11:54:18.155376+00:00
---
# GPU Memory Requirements by Fine-Tuning Method

GPU memory requirements for fine-tuning large language models vary dramatically based on the chosen method, model size, and precision settings. Understanding these requirements is crucial for selecting appropriate hardware and optimizing costs for [[Supervised Fine-Tuning (SFT)]] workflows.

## Memory Requirements by Method

The memory footprint of fine-tuning depends primarily on whether gradients and optimizer states are stored for all parameters or only a subset. Full fine-tuning requires storing model weights, gradients, and optimizer states (typically Adam with momentum), while parameter-efficient methods like [[Low-Rank Adaptation (LoRA)]] and [[QLoRA (Quantized LoRA)]] dramatically reduce memory needs by training only a small fraction of parameters. ^[gpu-hours-for-fine-tuning-llms.md]

### Memory Scaling by Model Size

| Method | Bits | 7-8B | 13-14B | 30-32B | 70-72B | 405B |
|--------|------|------|--------|--------|--------|------|
| Full SFT (FP32 optim) | 16+32 | 120 GB | 240 GB | 600 GB | 1,200 GB | ~7,200 GB |
| Full SFT (BF16) | 16 | 60 GB | 120 GB | 300 GB | 600 GB | ~3,250 GB |
| LoRA (16-bit) | 16 | 16 GB | 32 GB | 64 GB | 160 GB | ~950 GB |
| QLoRA (8-bit) | 8 | 10 GB | 20 GB | 40 GB | 80 GB | ~500 GB |
| QLoRA (4-bit) | 4 | 6 GB | 12 GB | 24 GB | 48 GB | ~250 GB |

^[gpu-hours-for-fine-tuning-llms.md]

## Full Fine-Tuning Memory Requirements

Full [[Supervised Fine-Tuning (SFT)]] requires storing the complete model in GPU memory along with gradients and optimizer states. When using FP32 optimizer states (standard for Adam), memory requirements include 16-bit model weights plus 32-bit optimizer states, effectively requiring 48 bits per parameter. Using BF16 precision throughout reduces this to approximately 32 bits per parameter. ^[gpu-hours-for-fine-tuning-llms.md]

For models exceeding single-GPU memory capacity, techniques like [[Gradient Checkpointing]] and model parallelism become necessary. The largest models like 405B parameter variants require distributed training across dozens of high-memory GPUs. ^[gpu-hours-for-fine-tuning-llms.md]

## Parameter-Efficient Fine-Tuning Memory Savings

[[Parameter-Efficient Fine-Tuning (PEFT)]] methods achieve substantial memory reductions by training only a subset of parameters. [[Low-Rank Adaptation (LoRA)]] typically reduces memory requirements by 3-10x compared to full fine-tuning, while [[QLoRA (Quantized LoRA)]] can achieve 10-20x reductions by combining low-rank adaptation with quantization. ^[gpu-hours-for-fine-tuning-llms.md]

The memory savings from LoRA come from storing gradients and optimizer states only for the low-rank adapter matrices, which represent a small fraction of total parameters. However, the base model must still be loaded in full precision for forward passes, limiting the maximum memory reduction achievable. ^[gpu-hours-for-fine-tuning-llms.md]

## Quantization Impact on Memory

[[4-bit Weight Quantization]] through QLoRA enables fine-tuning of large models on consumer hardware. 4-bit quantization reduces base model memory by approximately 4x compared to 16-bit precision, while 8-bit quantization provides a 2x reduction. The quantization overhead during training is typically 10-20% slower due to quantization and dequantization operations. ^[gpu-hours-for-fine-tuning-llms.md]

## Hardware Selection Guidelines

Memory requirements directly determine minimum hardware specifications for different fine-tuning approaches. Consumer GPUs like RTX 4090 (24GB) can handle QLoRA fine-tuning of models up to 13-14B parameters, while professional GPUs like A100 (80GB) enable LoRA fine-tuning of 70B+ models or full fine-tuning of smaller models. ^[gpu-hours-for-fine-tuning-llms.md]

For the largest models like [[GPT-OSS-120B]] or 405B parameter variants, multi-GPU setups become mandatory even with aggressive quantization. The choice between methods often comes down to balancing memory constraints, training speed, and final model quality requirements. ^[gpu-hours-for-fine-tuning-llms.md]
