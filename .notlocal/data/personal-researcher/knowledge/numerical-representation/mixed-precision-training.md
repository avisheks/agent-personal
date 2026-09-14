---
title: "mixed-precision-training"
summary: ""
sources:
  - numerical-representation/numerical-representation.md
createdAt: 2026-05-28T19:58:25.047516+00:00
updatedAt: 2026-05-28T19:58:25.047516+00:00
---
# Mixed Precision Training

Mixed Precision Training is a technique that uses multiple numerical data types within a single neural network training process to optimize memory usage, computational efficiency, and training stability. Rather than using a single precision format throughout the entire training pipeline, mixed precision strategically assigns different numerical representations to different components of the training process. ^[numerical-representation.md]

## Overview

Modern large language model training has evolved from using FP32 everywhere to sophisticated mixed precision approaches that can include FP16, BF16, FP8, and even experimental FP4 formats. This transition is fundamentally driven by the need for compute and memory efficiency at scale, particularly for trillion-token LLM training where the datatype determines GPU memory footprint, training throughput, interconnect bandwidth, stability, scaling efficiency, energy cost, and convergence quality. ^[numerical-representation.md]

## Core Precision Formats

### FP32 (Full Precision)
FP32 uses 32 bits with 8 exponent bits and 23 mantissa bits, providing very high dynamic range and precision. In mixed precision training, FP32 is typically reserved for optimizer master weights, critical reductions, debugging, and numerically sensitive kernels. Pure FP32 training for frontier LLMs is largely obsolete due to cost, being extremely expensive with 2× memory usage compared to FP16/BF16 and slow tensor-core utilization. ^[numerical-representation.md]

### FP16 Mixed Precision
FP16 was the first major mixed-precision breakthrough, using 16 bits with 5 exponent bits and 10 mantissa bits. The key innovation was using FP16 for forward/backward passes while maintaining FP32 master weights for optimizer updates. This approach enabled approximately 2× memory reduction, Tensor Core acceleration, larger batch sizes, and faster training, making GPT-scale training economically feasible. ^[numerical-representation.md]

However, FP16 suffers from a narrow exponent range that easily causes gradient underflow and activation overflow, leading to NaNs, unstable training, and divergence. This requires loss scaling techniques where gradients are multiplied by a scaling factor before the backward pass and then unscaled later to avoid underflow. ^[numerical-representation.md]

### BF16 (Current Industry Standard)
[[BFloat16 (BF16)]] uses 16 bits with 8 exponent bits and 7 mantissa bits, keeping FP32's exponent range while reducing mantissa precision. This format has become the current industry default for LLM training because it solves FP16's instability problems. BF16 provides the same exponent range as FP32 for much better stability, eliminates the need for loss scaling, offers better gradient stability critical for transformers, and allows easy migration from FP32 with minimal tuning. ^[numerical-representation.md]

BF16 is now the default training precision for major models including Meta Llama, Google Gemini, and most open-source transformer stacks, with strong community consensus favoring BF16 over FP16 for stability. ^[numerical-representation.md]

### FP8 Training
[[FP8 Training]] represents the new frontier in mixed precision training, offering 2× lower memory usage, higher throughput, lower communication cost, and better scaling efficiency compared to BF16. Two common variants exist: E4M3 (4 exponent, 3 mantissa bits) and E5M2 (5 exponent, 2 mantissa bits). ^[numerical-representation.md]

FP8 training requires sophisticated techniques including per-channel scaling, tensor-wise scaling, delayed scaling, selective FP16/BF16 fallback, and [[Stochastic Rounding]] to handle quantization noise, outliers, unstable gradients, attention sensitivity, and optimizer instability. DeepSeek-V3 pioneered production-scale FP8 mixed precision training for a 671B [[Mixture of Experts (MoE)]] model, demonstrating feasibility at extreme scale. ^[numerical-representation.md]

## Typical Mixed Precision Pipeline

A standard BF16 mixed precision training setup uses different precisions for different components:

- **Activations**: BF16
- **Weights**: BF16  
- **Gradients**: BF16
- **Optimizer states**: FP32
- **Master weights**: FP32
- **Reductions**: FP32

This approach works because neural networks are surprisingly tolerant to noise, and most tensors do not require FP32 precision but only need stable dynamic range. ^[numerical-representation.md]

## Quantization for Fine-Tuning

### QLoRA Approach
[[Parameter-Efficient Fine-Tuning (PEFT)]] techniques like [[QLoRA (Quantized LoRA)]] represent a major breakthrough in mixed precision training. QLoRA freezes a 4-bit quantized base model while training small LoRA adapters in higher precision, enabling fine-tuning of 65B parameter models on consumer GPUs. The precision stack uses [[NormalFloat4 (NF4)]] for base weights, BF16 for LoRA adapters, and FP32 for the optimizer. ^[numerical-representation.md]

## Ultra-Low Precision Training

### FP4 and Microscaling Formats
Experimental work with FP4, [[Microscaling FP4 (MXFP4)]], and NVFP4 formats aims to achieve 3.5× memory reduction versus FP16 with less than 1% degradation for some LLM tasks. These approaches use shared scaling factors, block-level scaling, hierarchical scaling, and variance stabilization techniques. NVIDIA's NVFP4 for Blackwell GPUs introduces 4-bit floating point with hierarchical scaling and smaller microblocks for improved accuracy retention. ^[numerical-representation.md]

Recent research demonstrates near-lossless GPT training using MXFP4 with [[Stochastic Rounding]], Hadamard transforms, and variance stabilization, making FP4 training practically feasible where it was previously considered impractical. ^[numerical-representation.md]

## Emerging Directions

### Adaptive Precision Training
Research is moving toward [[Adaptive Precision Training]] where different tensors use different formats based on their sensitivity. Instead of applying one datatype globally, easy tensors might use FP4/FP8 while sensitive tensors use BF16. This approach recognizes that embeddings, attention logits, normalization layers, and router logits in [[Mixture of Experts (MoE)]] models often need higher precision than other components. ^[numerical-representation.md]

## Training Stage Recommendations

Different training phases benefit from different precision strategies:

**Pretraining**: Small models (<7B) use BF16, mid-scale models (7B-70B) use BF16 or FP8, and frontier models (>100B) use FP8 mixed precision.

**Fine-tuning**: Full fine-tuning uses BF16, [[Parameter-Efficient Fine-Tuning (PEFT)]] uses BF16, consumer GPU QLoRA uses NF4 + BF16, and RLHF strongly prefers BF16 due to numerical instability.

**Inference**: Highest quality uses BF16, high throughput uses FP8, low memory uses INT4/NF4, and edge/mobile deployment uses INT4/INT2. ^[numerical-representation.md]

## Best Practices

Mixed precision training requires careful attention to several key practices:

- **Use BF16 as default** unless hardware lacks support or explicitly optimizing for FP8
- **Keep optimizer states in FP32** for Adam moments, stability, and convergence
- **Apply selective precision** - do not quantize all components equally
- **Monitor outliers** which can destroy low-precision stability through clipping, scaling, and normalization
- **Use stochastic rounding** for FP8, FP4, and MXFP4 to reduce bias accumulation
- **Validate long-horizon stability** since low precision can appear stable early but collapse late in training

^[numerical-representation.md]

## Industry Trend

The clear industry progression follows the path FP32→BF16→FP8→FP4, but the future likely involves heterogeneous precision rather than a single datatype. Different tensors, layers, and training phases will use different numerical formats dynamically selected during training, making mixed precision training a core systems-design dimension for scaling intelligence. ^[numerical-representation.md]
