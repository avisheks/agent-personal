---
title: "Supervised Fine-Tuning (SFT) | meituan-longcat/LongCat-Image | DeepWiki"
source: "https://deepwiki.com/meituan-longcat/LongCat-Image/4.1-supervised-fine-tuning-(sft)"
ingestedAt: "2026-05-18T00:12:17Z"
---
# Supervised Fine-Tuning (SFT)

Relevant source files

## Purpose and Scope

This document describes the Supervised Fine-Tuning (SFT) training pipeline for LongCat-Image. SFT is a full-parameter fine-tuning approach that updates all model weights based on supervised image-text pairs, producing a task-adapted model from the LongCat-Image-Dev base checkpoint.

This page covers:

  * SFT data format requirements and preparation
  * Configuration parameters specific to SFT training
  * Execution workflow using the SFT training scripts
  * Technical implementation details of the SFT training loop



For parameter-efficient fine-tuning using low-rank adapters, see [LoRA Training](/meituan-longcat/LongCat-Image/4.2-lora-training). For preference-based optimization, see [Direct Preference Optimization (DPO)](/meituan-longcat/LongCat-Image/4.3-direct-preference-optimization-\(dpo\)). For general training system architecture and common patterns, see [Training System Overview](/meituan-longcat/LongCat-Image/4-training-system-overview). For comprehensive configuration reference, see [Configuration Reference](/meituan-longcat/LongCat-Image/5-configuration-reference).

Sources: [train_examples/README.md1-34](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L1-L34)

* * *

## SFT Training Architecture

The SFT pipeline follows a three-layer architecture common to all LongCat-Image training approaches: a shell script orchestrator, Python training logic, and YAML configuration.


**Diagram: SFT Pipeline Architecture**

The pipeline is launched via `train.sh`, which configures the distributed training environment and invokes `accelerate launch` with 8 processes and bfloat16 mixed precision. The Accelerate framework reads DeepSpeed configuration from `misc/accelerate_config.yaml` and executes `train_sft.py`, which loads all training parameters from `train_config.yaml`.

Sources: [train_examples/sft/train.sh1-13](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train.sh#L1-L13) [train_examples/sft/train_config.yaml1-46](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L1-L46)

* * *

## Data Format Specification

SFT training requires a JSONL (JSON Lines) or TXT file where each line represents one training sample. Each sample must contain four required fields.

### Required Fields

Field| Type| Description| Example  
---|---|---|---  
`img_path`| string| Absolute or relative path to training image| `./data_example/images/0.png`  
`prompt`| string| Text description or caption for the image| `A lovely little girl.`  
`width`| integer| Width of the image in pixels| `1024`  
`height`| integer| Height of the image in pixels| `1024`  
  
### Example Data Format


The `width` and `height` fields are used by the multi-resolution bucketing system (see [Multi-Resolution Bucketing](/meituan-longcat/LongCat-Image/6.3-multi-resolution-bucketing)) to efficiently batch images with similar aspect ratios. Images will be transformed according to the specified `aspect_ratio_type` (e.g., `mar_1024`) during training.

Sources: [train_examples/README.md6-16](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L6-L16)

* * *

## Data Loading and Processing Pipeline


**Diagram: SFT Data Processing Flow**

The data pipeline begins by parsing the JSONL file specified in `data_txt_root`. Each sample's dimensions are used by `MultiResolutionDistributedSampler` to assign it to an aspect ratio bucket (e.g., 1:1, 3:4, 16:9) according to the `mar_1024` bucketing strategy. Images undergo aspect-ratio-aware resizing and center cropping to match their bucket dimensions. Text prompts are tokenized with a maximum length of 512 tokens and wrapped in a template structure. With probability `null_text_ratio` (0.1), prompts are replaced with empty strings to enable classifier-free guidance during training. Finally, samples are batched with size 4 using 8 DataLoader workers.

Sources: [train_examples/sft/train_config.yaml1-13](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L1-L13) [train_examples/README.md8-16](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L8-L16)

* * *

## Configuration Parameters

The SFT training configuration is defined in `train_config.yaml` and organized into four categories.

### 1\. Data Settings

Parameter| Type| Default| Description  
---|---|---|---  
`data_txt_root`| string| Required| Path to JSONL/TXT file containing training data  
`resolution`| integer| `1024`| Target resolution for image processing  
`aspect_ratio_type`| string| `mar_1024`| Bucketing strategy: `mar_256`, `mar_512`, or `mar_1024`  
`null_text_ratio`| float| `0.1`| Probability of replacing prompt with empty string (CFG)  
`dataloader_num_workers`| integer| `8`| Number of parallel data loading workers  
`train_batch_size`| integer| `4`| Batch size per GPU device  
`repeats`| integer| `1`| Number of times to repeat the dataset per epoch  
  
### 2\. Model Settings

Parameter| Type| Default| Description  
---|---|---|---  
`pretrained_model_name_or_path`| string| Required| Path to LongCat-Image-Dev checkpoint directory  
`diffusion_pretrain_weight`| string| `null`| Optional: specific diffusion weight path to override  
`text_tokenizer_max_length`| integer| `512`| Maximum sequence length for text tokenization  
`use_dynamic_shifting`| boolean| `true`| Enable dynamic noise schedule shifting  
`resume_from_checkpoint`| string| `latest`| Checkpoint to resume from: `latest` or path  
  
### 3\. Training Settings

Parameter| Type| Default| Description  
---|---|---|---  
`use_ema`| boolean| `false`| Enable Exponential Moving Average of weights  
`ema_rate`| float| `0.999`| EMA decay rate (if enabled)  
`mixed_precision`| string| `bf16`| Mixed precision mode: `bf16`, `fp16`, or `no`  
`max_train_steps`| integer| `100000`| Total number of training steps  
`gradient_accumulation_steps`| integer| `1`| Steps to accumulate gradients before update  
`gradient_checkpointing`| boolean| `true`| Enable gradient checkpointing to reduce memory  
`gradient_clip`| float| `1.0`| Maximum gradient norm for clipping  
`learning_rate`| float| `1e-5`| Initial learning rate  
`adam_weight_decay`| float| `1e-2`| Weight decay coefficient for AdamW  
`adam_epsilon`| float| `1e-8`| Epsilon for numerical stability  
`adam_beta1`| float| `0.9`| Adam beta1 parameter  
`adam_beta2`| float| `0.999`| Adam beta2 parameter  
`lr_scheduler`| string| `constant`| Learning rate schedule type  
`lr_warmup_steps`| integer| `1000`| Number of warmup steps  
`lr_num_cycles`| integer| `1`| Number of learning rate cycles (for cosine)  
`lr_power`| float| `1.0`| Power for polynomial decay  
  
### 4\. Logging Settings

Parameter| Type| Default| Description  
---|---|---|---  
`log_interval`| integer| `20`| Steps between logging metrics  
`save_model_steps`| integer| `1000`| Steps between checkpoint saves  
`work_dir`| string| `output/sft_model`| Directory for checkpoints and logs  
`seed`| integer| `43`| Random seed for reproducibility  
  
### Prompt Template Configuration

SFT supports optional prompt templating for structured text encoding:

Parameter| Type| Description  
---|---|---  
`prompt_template_encode_prefix`| string| Text prepended before prompt  
`prompt_template_encode_suffix`| string| Text appended after prompt  
`prompt_template_encode_start_idx`| integer| Token index where prompt content starts  
`prompt_template_encode_end_idx`| integer| Token index where prompt content ends  
  
The default template wraps prompts in a system-user-assistant dialogue format:
    
    
    <|im_start|>system
    As an image captioning expert, generate a descriptive text prompt based on an image content, suitable for input to a text-to-image model.<|im_end|>
    <|im_start|>user
    {prompt}<|im_end|>
    <|im_start|>assistant
    

Sources: [train_examples/sft/train_config.yaml1-46](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L1-L46)

* * *

## Execution Workflow

### Step 1: Prepare Training Data

Create a JSONL or TXT file with the required fields:


### Step 2: Configure Training Parameters

Edit `train_examples/sft/train_config.yaml`:


Adjust other parameters as needed for your hardware and dataset.

### Step 3: Launch Training


The training script performs the following sequence:


**Diagram: SFT Training Execution Sequence**

The shell script first configures environment variables to prevent tokenizer parallelism issues and extend NCCL timeouts for stable distributed training. It then invokes `accelerate launch` with 8 processes (one per GPU) and bfloat16 precision, which reads DeepSpeed configuration and executes `train_sft.py`. The training script loads the model, initializes the optimizer, and enters the main training loop where it performs forward/backward passes, accumulates gradients, updates parameters, and periodically saves checkpoints.

Sources: [train_examples/sft/train.sh1-13](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train.sh#L1-L13) [train_examples/README.md19-34](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L19-L34)

### Step 4: Monitor Training

Training logs and checkpoints are saved to the `work_dir`:
    
    
    output/sft_model/
    ├── checkpoint-1000/
    │   ├── diffusion_pytorch_model.safetensors
    │   ├── optimizer.bin
    │   ├── random_states_*.pkl
    │   └── scheduler.bin
    ├── checkpoint-2000/
    ├── ...
    └── logs/
    

The `resume_from_checkpoint` parameter enables resuming from interruptions:

  * `latest`: Automatically loads the most recent checkpoint
  * `/path/to/checkpoint-N`: Resumes from a specific checkpoint directory



Sources: [train_examples/sft/train_config.yaml20-22](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L20-L22) [train_examples/README.md32-33](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L32-L33)

* * *

## Technical Implementation Details

### Model Loading and Preparation

The SFT training script loads the complete LongCat-Image-Dev checkpoint, which includes:

  * **LongCatImageTransformer2DModel** : 6B parameter diffusion transformer
  * **AutoencoderKL** : VAE for latent space encoding
  * **AutoModel** : Text encoder for processing prompts
  * **FlowMatchEulerDiscreteScheduler** : Noise scheduler with optional dynamic shifting



All model parameters are trainable during SFT, distinguishing it from parameter-efficient approaches like LoRA.

### Training Objective

SFT minimizes the flow matching loss, training the model to predict the vector field that transforms noise to clean latent representations:
    
    
    Loss = MSE(predicted_velocity, target_velocity)
    

Where:

  * `predicted_velocity` is the transformer's output given noisy latents and text conditioning
  * `target_velocity` is the ground truth flow direction computed from clean and noisy latents



The scheduler's `use_dynamic_shifting` parameter adjusts the noise schedule based on image resolution, improving training stability across different aspect ratios.

### Distributed Training Strategy

SFT leverages Accelerate with DeepSpeed for efficient distributed training:

Component| Configuration  
---|---  
**Processes**|  8 (one per GPU)  
**Mixed Precision**|  bfloat16 for forward/backward passes  
**Gradient Checkpointing**|  Enabled to reduce memory usage  
**Gradient Accumulation**|  1 step (immediate updates)  
**Gradient Clipping**|  Max norm of 1.0  
**Communication Backend**|  NCCL with 12000s timeout  
  
The environment variable `TOKENIZERS_PARALLELISM=False` prevents multiprocessing conflicts in the tokenizer, while `NCCL_DEBUG=INFO` enables verbose logging for debugging distributed operations.

### Optimizer Configuration

SFT uses AdamW with the following hyperparameters optimized for large-scale diffusion training:

  * **Learning Rate** : 1e-5 (constant after warmup)
  * **Warmup Steps** : 1000 (linear warmup)
  * **Weight Decay** : 1e-2 (applied to all parameters except biases and normalization layers)
  * **Beta1/Beta2** : 0.9/0.999 (standard Adam momentum parameters)
  * **Epsilon** : 1e-8 (numerical stability)



The learning rate schedule is constant after warmup, which has proven effective for supervised fine-tuning of pretrained diffusion models.

Sources: [train_examples/sft/train_config.yaml24-46](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L24-L46) [train_examples/sft/train.sh1-13](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train.sh#L1-L13)

* * *

## Relationship to Other Training Methods

SFT is one of four training approaches in the LongCat-Image training ecosystem:


**Diagram: SFT in Training Ecosystem**

**SFT vs. LoRA** : SFT updates all 6B parameters, while LoRA only trains small adapter matrices (rank 32), making LoRA more memory-efficient but potentially less expressive. See [LoRA Training](/meituan-longcat/LongCat-Image/4.2-lora-training) for details.

**SFT vs. DPO** : SFT uses supervised image-text pairs, while DPO uses preference pairs (win/lose images) to align the model with human preferences. DPO also maintains a frozen reference model. See [Direct Preference Optimization (DPO)](/meituan-longcat/LongCat-Image/4.3-direct-preference-optimization-\(dpo\)).

**SFT vs. Edit Training** : SFT trains on generation pairs (text → image), while edit training uses triplets (reference image + edit instruction → edited image) for image editing capabilities. See [Image Editing Training](/meituan-longcat/LongCat-Image/4.4-image-editing-training).

Sources: [train_examples/README.md1-34](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/README.md?plain=1#L1-L34)

* * *

## Common Issues and Solutions

### Out of Memory Errors

If training fails with CUDA out of memory:

  * Reduce `train_batch_size` (e.g., from 4 to 2)
  * Increase `gradient_accumulation_steps` to maintain effective batch size
  * Ensure `gradient_checkpointing: true` is set
  * Consider reducing `resolution` (e.g., from 1024 to 768)



### Slow Training Speed

If training is slower than expected:

  * Increase `dataloader_num_workers` (but watch CPU/RAM usage)
  * Verify `mixed_precision: bf16` is enabled
  * Check that all 8 GPUs are utilized (`nvidia-smi`)
  * Ensure dataset files are on fast storage (SSD, not network drive)



### NCCL Timeout Errors

If distributed training hangs or times out:

  * Verify `NCCL_TIMEOUT=12000` is set (12000 seconds = 3.3 hours)
  * Check network connectivity between nodes
  * Enable verbose logging with `NCCL_DEBUG=INFO`
  * Reduce checkpoint save frequency if timeouts occur during saves



### Resume from Checkpoint Not Working

If `resume_from_checkpoint: latest` fails:

  * Verify checkpoint directories exist in `work_dir`
  * Check that checkpoint directory contains all required files
  * Try specifying the full checkpoint path instead of `latest`
  * Ensure sufficient disk space for checkpoint saves



Sources: [train_examples/sft/train.sh1-13](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train.sh#L1-L13) [train_examples/sft/train_config.yaml1-46](https://github.com/meituan-longcat/LongCat-Image/blob/93ccfe90/train_examples/sft/train_config.yaml#L1-L46)