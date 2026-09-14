---
title: "dynamic-noise-schedule-shifting"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:53:43.821480+00:00
updatedAt: 2026-05-28T19:53:43.821480+00:00
---
# Dynamic Noise Schedule Shifting

Dynamic Noise Schedule Shifting is a training technique used in diffusion models to adjust the noise schedule based on image resolution, improving training stability across different aspect ratios. This approach is implemented as an optional feature in the LongCat-Image training pipeline.

## Overview

Dynamic Noise Schedule Shifting modifies the standard noise scheduling process during diffusion model training by adapting the noise levels according to the resolution of input images. The technique addresses challenges that arise when training on images with varying resolutions and aspect ratios, which is common in multi-resolution training scenarios. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The shifting mechanism is controlled by the `use_dynamic_shifting` parameter in training configurations and works in conjunction with the FlowMatchEulerDiscreteScheduler to provide resolution-aware noise scheduling. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Implementation

In the LongCat-Image training system, Dynamic Noise Schedule Shifting is implemented within the FlowMatchEulerDiscreteScheduler component. When enabled through the `use_dynamic_shifting: true` configuration parameter, the scheduler automatically adjusts noise levels based on the dimensions of input images during training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The technique operates during the [[flow-matching-loss]] training objective, where the model learns to predict the vector field that transforms noise to clean latent representations. By adapting the noise schedule to image resolution, the shifting mechanism helps maintain consistent training dynamics across images of different sizes processed through the [[multi-resolution-bucketing]] system. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Integration with Training Pipeline

Dynamic Noise Schedule Shifting is integrated into the [[supervised-fine-tuning-sft]] pipeline as part of the model loading and preparation phase. The LongCat-Image-Dev checkpoint includes the FlowMatchEulerDiscreteScheduler with dynamic shifting capabilities, which can be enabled or disabled through configuration. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The shifting mechanism works alongside other training components including the LongCatImageTransformer2DModel, AutoencoderKL for latent space encoding, and AutoModel for text processing. This integration ensures that noise schedule adjustments are coordinated with the overall training process. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Configuration Parameters

The dynamic shifting feature is controlled through the model settings section of the training configuration:

- **`use_dynamic_shifting`**: Boolean parameter (default: `true`) that enables or disables the dynamic noise schedule shifting mechanism
- The parameter works in conjunction with other model settings such as `resolution`, `aspect_ratio_type`, and the FlowMatchEulerDiscreteScheduler configuration ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Benefits and Applications

Dynamic Noise Schedule Shifting provides improved training stability when working with multi-resolution datasets. This is particularly valuable in scenarios where training data includes images with diverse aspect ratios, as processed by bucketing strategies like `mar_1024` that group images by aspect ratio (1:1, 3:4, 16:9). ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The technique helps maintain consistent training dynamics across different image resolutions, potentially leading to better model performance and more stable convergence during the training process. This is especially important for large-scale diffusion models that need to handle varied input dimensions effectively. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Architecture

The dynamic shifting mechanism is part of the three-layer architecture used in LongCat-Image training:

1. **Shell Script Layer**: The training is launched via shell scripts that configure the distributed environment
2. **Python Training Logic**: The `train_sft.py` script implements the training loop with dynamic shifting integration
3. **YAML Configuration**: Training parameters including `use_dynamic_shifting` are specified in configuration files ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The FlowMatchEulerDiscreteScheduler with dynamic shifting capabilities is loaded as part of the complete LongCat-Image-Dev checkpoint, which also includes the 6B parameter diffusion transformer, VAE encoder, and text processing components. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Relationship to Flow Matching Loss

Dynamic Noise Schedule Shifting operates within the context of the [[flow-matching-loss]] training objective. The scheduler's dynamic adjustments ensure that the flow matching process remains stable across different image resolutions, maintaining the quality of the vector field predictions that transform noise to clean latent representations. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The technique specifically addresses the challenge of maintaining consistent loss computation when training on images with varying dimensions, which is crucial for the effectiveness of the flow matching training paradigm used in modern diffusion models. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
