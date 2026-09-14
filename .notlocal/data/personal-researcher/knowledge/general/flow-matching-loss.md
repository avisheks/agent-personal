---
title: "flow-matching-loss"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:53:07.040679+00:00
updatedAt: 2026-05-28T19:53:07.040679+00:00
---
# Flow Matching Loss

Flow Matching Loss is a training objective used in diffusion models that trains the model to predict the vector field that transforms noise to clean data representations. In the context of image generation models, this loss function enables the model to learn the flow dynamics between random noise and target images in latent space. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Training Objective

Flow Matching Loss is formulated as a mean squared error between the model's predicted velocity and the target velocity:

```
Loss = MSE(predicted_velocity, target_velocity)
```

Where:
- `predicted_velocity` is the transformer's output given noisy latents and text conditioning
- `target_velocity` is the ground truth flow direction computed from clean and noisy latents

The model learns to predict the vector field that defines the optimal path from noise to data, enabling generation through iterative denoising steps. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Implementation in Training Pipelines

Flow Matching Loss serves as the core training objective in [[supervised-fine-tuning-sft]] for diffusion models. During training, the loss is computed by:

1. Encoding clean images into latent representations using a VAE
2. Adding noise to the latents according to a noise schedule
3. Having the model predict the velocity field given the noisy latents and text conditioning
4. Computing the MSE between predicted and target velocities

The scheduler's dynamic shifting parameter can adjust the noise schedule based on image resolution, improving training stability across different aspect ratios. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Implementation Details

The effectiveness of Flow Matching Loss depends on several factors:

- **Noise Schedule**: The choice of noise scheduler (such as FlowMatchEulerDiscreteScheduler) affects the quality of the target velocity computations
- **Mixed Precision**: Training typically uses bfloat16 precision for the forward and backward passes to balance numerical stability with memory efficiency
- **Gradient Clipping**: A maximum gradient norm (typically 1.0) is applied to prevent training instability

The loss is optimized using AdamW with specific hyperparameters tuned for large-scale diffusion training, including learning rates around 1e-5 and weight decay of 1e-2. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Relationship to Other Loss Functions

Flow Matching Loss differs from other training objectives used in generative models:

- **Supervised Loss**: Flow Matching Loss is used in supervised training with image-text pairs, while preference-based methods like [[direct-preference-optimization-dpo]] use ranking losses on preference pairs
- **Reconstruction Loss**: Unlike VAE reconstruction losses that operate in pixel space, Flow Matching Loss operates in the latent space and focuses on learning the generation dynamics
- **Adversarial Loss**: Flow Matching Loss does not require a discriminator network, making training more stable than GAN-based approaches

^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Dynamic Noise Schedule Integration

The Flow Matching Loss implementation supports dynamic noise schedule shifting through the `use_dynamic_shifting` parameter. This feature adjusts the noise schedule based on image resolution and aspect ratio, which is particularly important when training with [[multi-resolution-bucketing]]. The dynamic shifting helps maintain consistent training dynamics across different image dimensions and aspect ratios within the same batch. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Optimization Considerations

Flow Matching Loss training benefits from several optimization strategies:

- **Gradient Accumulation**: When memory constraints limit batch size, gradient accumulation maintains effective batch sizes for stable training
- **Learning Rate Scheduling**: Constant learning rates after warmup have proven effective for supervised fine-tuning of pretrained diffusion models
- **Checkpoint Management**: Regular checkpoint saving enables recovery from training interruptions and model evaluation at different stages

The loss computation is integrated with distributed training frameworks like Accelerate and DeepSpeed for efficient multi-GPU training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Model Architecture Integration

Flow Matching Loss is specifically designed to work with transformer-based diffusion models. In the LongCat-Image architecture, the loss function operates on the outputs of the LongCatImageTransformer2DModel, which processes both visual latents and text conditioning. The loss computation takes into account the model's 6B parameters during full parameter fine-tuning, distinguishing it from parameter-efficient approaches that only update adapter weights. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Distributed Training Considerations

Flow Matching Loss computation is optimized for distributed training environments. The loss calculation is performed across multiple GPUs using frameworks like Accelerate with DeepSpeed, enabling efficient training of large-scale diffusion models. The implementation includes gradient synchronization and accumulation strategies to maintain training stability across distributed processes. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
