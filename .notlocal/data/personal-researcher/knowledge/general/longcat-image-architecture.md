---
title: "longcat-image-architecture"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:54:28.612435+00:00
updatedAt: 2026-05-28T19:54:28.612435+00:00
---
# LongCat-Image Architecture

LongCat-Image is a 6-billion parameter text-to-image diffusion model developed by Meituan that uses a transformer-based architecture for high-resolution image generation. The model employs flow matching as its core generative mechanism and supports multiple training paradigms including [[Supervised Fine-Tuning (SFT)]], [[parameter-efficient-fine-tuning-peft]], and [[direct-preference-optimization-dpo]]. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Architecture Overview

The LongCat-Image architecture consists of four primary components that work together to generate images from text descriptions. The **LongCatImageTransformer2DModel** serves as the core 6-billion parameter diffusion transformer that predicts velocity fields in the flow matching framework. The **AutoencoderKL** provides VAE-based latent space encoding and decoding for efficient processing. The **AutoModel** handles text encoding and prompt processing with support for up to 512 tokens. Finally, the **FlowMatchEulerDiscreteScheduler** manages the noise scheduling process with optional [[dynamic-noise-schedule-shifting]] capabilities. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Flow Matching Framework

LongCat-Image uses flow matching as its generative objective rather than traditional diffusion denoising. The model learns to predict vector fields that transform noise distributions into clean latent representations through the loss function: `Loss = MSE(predicted_velocity, target_velocity)`. The scheduler's dynamic shifting feature adjusts the noise schedule based on image resolution, improving training stability across different aspect ratios and resolutions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Multi-Resolution Support

The architecture incorporates sophisticated [[multi-resolution-bucketing]] through the `aspect_ratio_type` parameter, supporting three bucketing strategies: `mar_256`, `mar_512`, and `mar_1024`. The `MultiResolutionDistributedSampler` assigns training samples to aspect ratio buckets (such as 1:1, 3:4, 16:9) based on their dimensions, enabling efficient batching of images with similar aspect ratios. Images undergo aspect-ratio-aware resizing and center cropping to match their assigned bucket dimensions during processing. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Training System Architecture

LongCat-Image supports four distinct training approaches within a unified three-layer architecture. The system uses shell script orchestrators that configure distributed training environments and invoke `accelerate launch` with multiple processes and mixed precision. Python training scripts handle the core training logic and model updates. YAML configuration files define all training parameters and hyperparameters for reproducible experiments. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Training Methods

The architecture supports multiple training paradigms for different use cases. [[Supervised Fine-Tuning (SFT)]] updates all 6 billion parameters using supervised image-text pairs, providing maximum model expressiveness. [[parameter-efficient-fine-tuning-peft]] uses low-rank adapter matrices (rank 32) for reduced memory requirements. [[direct-preference-optimization-dpo]] employs preference pairs (win/lose images) to align the model with human preferences while maintaining a frozen reference model. Image editing training uses triplets (reference image + edit instruction → edited image) to enable image modification capabilities. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Distributed Training Infrastructure

The architecture leverages Accelerate with DeepSpeed for efficient distributed training across 8 GPUs. The system uses one process per GPU with bfloat16 mixed precision for forward and backward passes. [[gradient-descent-optimization]] is enabled with gradient checkpointing to reduce memory usage, while gradient accumulation allows for flexible effective batch sizes. The NCCL communication backend handles distributed operations with extended timeouts (12000 seconds) for stability during long training runs. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Memory Optimization

LongCat-Image implements several memory optimization strategies to handle the 6-billion parameter model efficiently. Gradient checkpointing trades computation for memory by recomputing activations during backward passes. Mixed precision training uses bfloat16 for most operations while maintaining fp32 precision for critical computations. The `TOKENIZERS_PARALLELISM=False` environment variable prevents multiprocessing conflicts in the tokenizer that could cause memory issues. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Text Processing Pipeline

The text processing component supports flexible [[prompt-template-encoding]] for structured text encoding. The default template wraps prompts in a system-user-assistant dialogue format that positions the model as an image captioning expert. Text prompts are tokenized with a maximum length of 512 tokens and can include configurable prefix and suffix templates. During training, prompts are replaced with empty strings with probability `null_text_ratio` (default 0.1) to enable [[classifier-free-guidance-training]]. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Configuration System

The architecture uses a comprehensive YAML-based configuration system organized into four categories. Data settings control input processing, resolution handling, and aspect ratio bucketing strategies. Model settings specify checkpoint paths, tokenizer limits, and dynamic noise schedule shifting options. Training settings define optimization parameters, learning rates, and gradient handling. Logging settings manage checkpoint frequency, output directories, and reproducibility seeds. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Hyperparameter Optimization

LongCat-Image uses AdamW optimization with hyperparameters specifically tuned for large-scale diffusion training. The learning rate of 1e-5 remains constant after a 1000-step linear warmup period. Weight decay of 1e-2 is applied to all parameters except biases and normalization layers. The optimizer uses standard Adam momentum parameters (beta1=0.9, beta2=0.999) with epsilon=1e-8 for numerical stability. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Checkpoint and Resume System

The architecture includes robust checkpoint management for long-running training jobs. Checkpoints are saved every 1000 steps by default and include the complete model state, optimizer state, random number generator states, and scheduler configuration. The `resume_from_checkpoint` parameter supports both automatic resumption from the latest checkpoint and manual specification of checkpoint paths. This enables recovery from interruptions and continuation of training across multiple sessions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Data Format and Processing

LongCat-Image requires training data in [[jsonl-training-data-format]] with four mandatory fields per sample: `img_path` (image file path), `prompt` (text description), `width` (image width in pixels), and `height` (image height in pixels). The data loading pipeline uses these dimensions for multi-resolution bucketing, where samples are assigned to aspect ratio buckets for efficient batching. Images are processed through aspect-ratio-aware resizing and center cropping to match their bucket dimensions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Performance and Scalability

The architecture is designed for large-scale training with several performance optimizations. The distributed training setup supports 8 GPUs with NCCL communication and extended timeouts for stability. Memory usage is optimized through gradient checkpointing and mixed precision training. The multi-resolution bucketing system improves training efficiency by batching images with similar aspect ratios together. Checkpoint saving occurs every 1000 steps to balance training continuity with storage requirements. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
