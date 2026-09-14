---
title: "classifier-free-guidance-training"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:54:01.987952+00:00
updatedAt: 2026-05-28T19:54:01.987952+00:00
---
# Classifier-Free Guidance Training

Classifier-Free Guidance Training is a technique used in diffusion model training that enables models to perform conditional generation without requiring a separate classifier network. During training, the model learns to generate both conditional and unconditional outputs by randomly replacing text prompts with empty strings, allowing it to support classifier-free guidance during inference.

## Overview

In traditional classifier guidance, a separate neural network classifier is trained to distinguish between different classes or conditions, and its gradients are used to guide the diffusion process toward desired outputs. Classifier-free guidance eliminates the need for this separate classifier by training a single model to handle both conditional and unconditional generation scenarios. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The technique works by randomly setting text prompts to empty strings during training with a specified probability, typically around 10%. This teaches the model to generate images both with and without text conditioning, enabling it to interpolate between conditional and unconditional predictions during inference. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Training Implementation

### Null Text Ratio Configuration

The core parameter controlling classifier-free guidance training is the `null_text_ratio`, which determines the probability that a text prompt will be replaced with an empty string during training. In [[Supervised Fine-Tuning (SFT)]] implementations, this is typically set to 0.1 (10% probability). ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Data Processing Pipeline

During training, the data processing pipeline applies the null text ratio transformation after tokenization but before feeding samples to the model. For each training sample, a random number is generated, and if it falls below the `null_text_ratio` threshold, the text prompt is replaced with an empty string while preserving the image data. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The empty string replacement occurs at the prompt level rather than the token level, ensuring that when guidance is disabled, the model receives a completely unconditional signal rather than partial conditioning. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Benefits

### Single Model Architecture

Classifier-free guidance training allows a single diffusion model to serve dual purposes: generating images conditioned on text prompts and generating unconditional images. This eliminates the computational overhead and training complexity of maintaining separate classifier networks. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Inference-Time Control

Models trained with classifier-free guidance can adjust the strength of conditioning during inference by interpolating between conditional and unconditional predictions. This provides fine-grained control over how closely generated images follow the input prompts without requiring model retraining. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Improved Training Stability

By learning both conditional and unconditional generation within the same training loop, the model develops more robust internal representations that are less prone to overfitting to specific prompt patterns or distributions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Integration with Training Systems

### Multi-Resolution Compatibility

Classifier-free guidance training integrates seamlessly with [[multi-resolution-bucketing]] systems. The null text ratio is applied consistently across all aspect ratio buckets, ensuring that unconditional generation capabilities are learned for all supported image dimensions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Template-Based Prompts

When using structured prompt templates (such as dialogue formats with system messages), the entire templated prompt is replaced with an empty string when the null text ratio triggers, rather than just the user content portion. This ensures clean unconditional training signals. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Distributed Training

The null text ratio transformation is applied consistently across all distributed training processes, with each process independently determining whether to nullify prompts based on its local random state. This maintains training consistency while preserving the stochastic nature of the guidance training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Configuration Parameters

The primary configuration parameter for classifier-free guidance training is:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `null_text_ratio` | float | `0.1` | Probability of replacing prompt with empty string |

This parameter is typically configured in the data settings section of training configurations and affects the data loading pipeline rather than the model architecture itself. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Relationship to Other Techniques

Classifier-free guidance training is commonly used alongside other training methodologies including [[Supervised Fine-Tuning (SFT)]], [[direct-preference-optimization-dpo]], and [[parameter-efficient-fine-tuning-peft]] approaches. The technique is model-agnostic and can be applied to any conditional diffusion training setup that uses text-image pairs. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The training approach complements other conditioning techniques and does not interfere with architectural choices such as attention mechanisms, normalization schemes, or optimization strategies. It works particularly well with [[flow-matching-loss]] objectives and [[dynamic-noise-schedule-shifting]] techniques used in modern diffusion model training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
