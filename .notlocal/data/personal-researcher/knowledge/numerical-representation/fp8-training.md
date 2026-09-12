---
title: "fp8-training"
summary: ""
sources:
  - numerical-representation/numerical-representation.md
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-28T19:59:04.676941+00:00
updatedAt: 2026-05-28T19:59:04.676941+00:00
---
# FP8 Training

FP8 Training is a precision optimization technique that enables training neural networks using 8-bit floating-point arithmetic instead of the traditional 16-bit or 32-bit formats. This approach reduces memory usage and can accelerate training while maintaining model quality.

## Overview

FP8 (8-bit floating-point) training represents a significant advancement in neural network training efficiency. By using lower precision arithmetic, FP8 training can substantially reduce memory requirements and computational overhead during the training process. This technique is particularly valuable for training large language models where memory constraints are often a limiting factor. ^[numerical-representation.md]

The industry has evolved through a progression of numerical representations: FP32 everywhere → FP16 mixed precision → [[BFloat16 (BF16)]] dominance → FP8 training → experimental FP4/MXFP4/NVFP4 pipelines. This transition is fundamentally driven by compute and memory efficiency at scale. ^[numerical-representation.md]

## FP8 Formats

FP8 training typically uses two common variants that balance dynamic range and precision differently:

- **E4M3**: 4-bit exponent, 3-bit mantissa
- **E5M2**: 5-bit exponent, 2-bit mantissa

These formats provide different trade-offs between numerical range and precision, allowing practitioners to select the most appropriate variant for their specific training requirements. ^[numerical-representation.md]

## Benefits and Advantages

FP8 training offers several key advantages over higher precision formats:

- **Memory Efficiency**: Provides 2× lower memory usage compared to BF16, enabling larger models or batch sizes on the same hardware
- **Higher Throughput**: Reduced computational overhead leads to faster training speeds
- **Lower Communication Cost**: Reduced bandwidth requirements for distributed training
- **Better Scaling Efficiency**: More efficient utilization of resources at large scale
- **Energy Efficiency**: Lower power consumption due to reduced computational requirements

For trillion-token LLM training, the datatype choice determines GPU memory footprint, training throughput, interconnect bandwidth, stability, scaling efficiency, energy cost, and convergence quality. ^[numerical-representation.md]

## Implementation Challenges

FP8 training is significantly less forgiving than higher precision formats and presents several technical challenges:

- **Quantization Noise**: Increased numerical noise due to reduced precision
- **Outlier Sensitivity**: Extreme values can destabilize training
- **Gradient Instability**: Gradients may become unstable or vanish
- **Attention Sensitivity**: Attention mechanisms are particularly sensitive to precision reduction
- **Optimizer Instability**: Optimization algorithms may require careful tuning

Modern FP8 systems address these challenges through techniques including per-channel scaling, tensor-wise scaling, delayed scaling, selective FP16/BF16 fallback, and [[Stochastic Rounding]]. ^[numerical-representation.md]

## Implementation in NeMo Framework

The [[NVIDIA NeMo Framework]] supports FP8 training as part of its [[Supervised Fine-Tuning (SFT)]] capabilities. To enable FP8 training in NeMo, specific configuration adjustments are required during the fine-tuning process. The framework allows users to activate FP8 training by modifying the training configuration parameters, though the exact configuration details require adjusting the configs appropriately. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Mixed Precision Strategy

FP8 training typically employs a mixed precision approach rather than using FP8 for all components. A typical FP8 mixed precision pipeline might use:

- **Activations**: FP8
- **Weights**: FP8  
- **Gradients**: FP8
- **Optimizer States**: FP32
- **Master Weights**: FP32
- **Critical Reductions**: FP32

This selective approach maintains training stability while maximizing the memory and computational benefits of lower precision arithmetic. ^[numerical-representation.md]

## Integration with Dataset Packing

FP8 training can be used in conjunction with [[Dataset Packing]] techniques for enhanced training efficiency. When using packed sequences with FP8 training, practitioners need to adjust both the micro batch size and global batch size due to the packing optimization. This combination allows for maximum utilization of available memory and computational resources during the training process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Real-World Applications

FP8 training has been successfully deployed in production-scale systems. DeepSeek pioneered production-scale FP8 mixed precision training for a 671B MoE model, validating FP8 training feasibility at extreme scale. Their innovations included FP8 mixed precision, hardware/software co-design, communication overlap, and stable large-scale MoE optimization. ^[numerical-representation.md]

## Best Practices

When implementing FP8 training, several best practices should be followed:

- **Selective Precision**: Not all components should use FP8 equally. Sensitive components like embeddings, attention logits, normalization layers, and router logits often need higher precision
- **Outlier Management**: Use clipping, scaling, normalization, or SmoothQuant-style transformations to handle outliers that can destroy low-precision stability
- **Stochastic Rounding**: Important for reducing bias accumulation in FP8 training
- **Long-Horizon Validation**: Test long training runs, loss spike behavior, and downstream evaluation drift, as low precision can appear stable early but collapse late in training

^[numerical-representation.md]

## Integration with Other Techniques

FP8 training is often used in conjunction with other optimization techniques such as [[Parameter-Efficient Fine-Tuning (PEFT)]] and various parallelization strategies including [[Tensor Model Parallelism]] and [[Pipeline Model Parallelism]]. The NeMo Framework supports FP8 training alongside features like packed sequence training, where both techniques can be used together to maximize training efficiency. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Current Recommendations

For different training scenarios, the current industry recommendations are:

- **Small models (<7B)**: [[BFloat16 (BF16)]] remains preferred
- **Mid-scale models (7B-70B)**: BF16 or FP8 depending on requirements
- **Frontier models (>100B)**: FP8 mixed precision is increasingly standard
- **Fine-tuning**: BF16 is generally recommended, especially for RLHF which is numerically unstable

The technique represents an important tool in the optimization toolkit for training large-scale neural networks efficiently, marking a significant step toward more efficient training of increasingly large models. ^[numerical-representation.md]
