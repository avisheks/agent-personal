---
title: "Llama-Factory Training Framework"
summary: "A framework for supervised fine-tuning of language models that provides configuration-based training with support for LoRA and other parameter-efficient methods."
sources:
  - fine-tuning-noisy-labels/robustft-readme-md-at-main-luo-junyu-robustft-github.md
createdAt: 2026-05-20T03:03:21.842926+00:00
updatedAt: 2026-05-20T03:03:21.842926+00:00
---
# Llama-Factory Training Framework

Llama-Factory is a training framework commonly used for [[Supervised Fine-Tuning (SFT)]] of large language models. The framework provides infrastructure for training models with custom datasets and configurations, supporting various training approaches including LoRA (Low-Rank Adaptation) fine-tuning. ^[RobustFT/README.md]

## Integration with Training Workflows

Llama-Factory integrates into multi-stage training pipelines that involve data preparation, model training, and evaluation phases. The framework requires specific dataset formatting and configuration setup to execute training runs effectively. ^[RobustFT/README.md]

### Dataset Configuration

The framework uses a dataset registry system where training datasets must be registered in the `dataset_info.json` file. This file maps dataset names to their corresponding file paths and formats, enabling the framework to locate and load training data during the fine-tuning process. ^[RobustFT/README.md]

### Training Configuration

Training parameters are specified through YAML configuration files, such as `llama3_lora_sft.yaml`, which define model specifications, dataset selections, storage paths, and hyperparameters. The framework maintains default training parameters while allowing customization for specific use cases. ^[RobustFT/README.md]

## LoRA Training Support

Llama-Factory supports [[Parameter-Efficient Fine-Tuning (PEFT)]] through LoRA adapters. The training process generates LoRA modules that can be loaded alongside base models during inference, enabling efficient model adaptation without modifying the original model weights. ^[RobustFT/README.md]

## Inference Integration

The framework integrates with [[vLLM Inference Engine]] for serving fine-tuned models. LoRA-trained models can be deployed using vLLM's LoRA module loading capabilities, allowing multiple fine-tuned variants to be served from a single base model instance. The inference setup supports enabling LoRA modules and specifying module paths for deployment. ^[RobustFT/README.md]

## Command Line Interface

Llama-Factory provides a command-line interface through the `llamafactory-cli` tool, which executes training runs based on provided configuration files. The CLI supports GPU specification through environment variables and accepts YAML configuration files as input parameters. ^[RobustFT/README.md]
