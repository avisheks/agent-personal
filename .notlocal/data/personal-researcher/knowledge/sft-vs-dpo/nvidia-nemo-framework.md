---
title: "nvidia-nemo-framework"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-18T18:34:55.816599+00:00
updatedAt: 2026-05-18T18:34:55.816599+00:00
---
# NVIDIA NeMo Framework

The **NVIDIA NeMo Framework** is a comprehensive toolkit for developing and deploying large language models, providing capabilities for [[Supervised Fine-Tuning (SFT)]], model training, and inference. The framework is designed to handle enterprise-scale AI model development with support for distributed training and various optimization techniques. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Architecture and Components

### Container-Based Deployment

NeMo Framework operates through containerized environments that provide consistent runtime environments for model training and inference. The framework uses Docker containers with pre-configured dependencies and optimized libraries for GPU acceleration, accessible through the `nvcr.io/nvidia/nemo:24.07` container image. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Model Parallelism Support

The framework supports both [[Tensor Model Parallelism]] and [[Pipeline Model Parallelism]] for training large models. For models like Nemotron 340B, the framework can be configured with tensor parallelism size of 8 and pipeline parallelism size of 12 or 16, enabling efficient distribution of model parameters across multiple GPUs. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Training Capabilities

### Supervised Fine-Tuning

NeMo Framework provides comprehensive support for [[Supervised Fine-Tuning (SFT)]] through the `megatron_gpt_finetuning.py` script. The framework supports various training configurations including precision settings (bf16), batch size management, and sequence length optimization. Training can be performed with packed sequences to improve efficiency, requiring adjustments to micro batch size and global batch size parameters. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Advanced Training Features

The framework includes support for [[FP8 Training]] precision, which can provide additional performance optimizations. It also supports [[Dataset Packing]] for improved training efficiency, where sequences are packed together to maximize GPU utilization. The framework provides configurable activation checkpointing with granularity options including selective checkpointing methods. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Multi-Node Training

NeMo Framework supports distributed training across multiple nodes, with integration for cluster management systems like Slurm. The framework can scale training workloads by replacing single-node execution commands with distributed execution patterns, supporting configurations with up to 12 nodes and 96 devices. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## NeMo Launcher

### Configuration Management

The NeMo Launcher provides a configuration-driven approach to managing training pipelines through YAML configuration files. The launcher organizes configurations into sections including `run`, `trainer`, `exp_manager`, and `model`, allowing for systematic management of training parameters. Configuration files are structured with defaults and stages sections to define pipeline execution order. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Pipeline Execution

The launcher supports multi-stage pipeline execution through the `main.py` script, where different training phases can be configured and executed sequentially. Users can specify dependencies between stages and configure resource allocation for each phase of the training process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Training Configuration

### Dataset Configuration

The framework supports multiple dataset formats including JSONL files for training, validation, and test data. It provides [[Concat Sampling Probabilities]] configuration for managing multiple training files, where probabilities must sum to 1.0. The framework supports various dataset parameters including sequence length limits, batch sizes, and worker configurations. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Optimization Settings

NeMo Framework includes sophisticated optimization capabilities with support for distributed_fused_adam optimizer and configurable learning rates. For full parameter fine-tuning, the framework recommends smaller learning rates such as 1e-6. The framework supports [[Answer-Only Loss]] configuration and various precision settings including bf16 and megatron_amp_O2. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Evaluation and Inference

### Model Evaluation

The framework provides evaluation capabilities through the `megatron_gpt_generate.py` script, which can assess model performance on test datasets. Evaluation supports configurable generation parameters including token limits, batch sizes, and output formatting options. The evaluation process can generate predictions and write results to specified output files in JSONL format. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Output Generation

NeMo Framework supports both greedy and sampling-based generation strategies for model inference. The framework can generate predictions with configurable token limits and supports writing predictions to file with customizable output paths. Evaluation results include sentence-level outputs that can be analyzed for model performance assessment. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Integration and Compatibility

### Model Format Support

The framework works with `.nemo` checkpoint format, providing a standardized approach to model serialization and loading. Models can be restored from checkpoints for continued training or inference deployment using the `restore_from_path` parameter. The framework supports checkpoint management with options for saving best models and creating checkpoints on training completion. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Resource Management

NeMo Framework includes sophisticated resource management capabilities, supporting configuration of memory limits, shared memory allocation, and GPU device assignment. The framework can manage complex distributed training scenarios with automatic resource optimization, including support for sequence parallelism and bias activation fusion optimizations. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]
