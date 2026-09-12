---
title: "tensor-model-parallelism"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-18T18:35:12.090675+00:00
updatedAt: 2026-05-18T18:35:12.090675+00:00
---
# Tensor Model Parallelism

Tensor Model Parallelism is a distributed training technique that splits model parameters across multiple devices to enable training and inference of large neural networks that exceed the memory capacity of a single GPU.

## Overview

Tensor Model Parallelism divides the model's tensors (weights and activations) across multiple devices, allowing each device to hold only a portion of the model parameters. This approach enables the training and deployment of models that would otherwise be too large to fit in the memory of a single accelerator. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Configuration Parameters

The key configuration parameter for Tensor Model Parallelism is `tensor_model_parallel_size`, which specifies the number of devices across which the model tensors are distributed. This parameter must be set appropriately based on the model size and available hardware resources. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Model-Specific Settings

Different model sizes require different tensor parallelism configurations:

- **Large models (340B parameters)**: Require `tensor_model_parallel_size=8` when combined with [[Pipeline Model Parallelism]]
- **Smaller models**: May use `tensor_model_parallel_size=1` for single-device deployment ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Integration with Pipeline Parallelism

Tensor Model Parallelism is often used in conjunction with [[Pipeline Model Parallelism]] to handle extremely large models. The combination allows for both horizontal (tensor) and vertical (pipeline) distribution of the model:

- `tensor_model_parallel_size`: Controls horizontal distribution across devices
- `pipeline_model_parallel_size`: Controls vertical distribution across pipeline stages ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

For example, a 340B parameter model might use `tensor_model_parallel_size=8` and `pipeline_model_parallel_size=12` or `pipeline_model_parallel_size=16` depending on the specific deployment configuration. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Implementation in Training Frameworks

Tensor Model Parallelism is implemented as a configuration parameter in distributed training frameworks such as the [[NVIDIA NeMo Framework]]. It can be enabled alongside other optimization techniques such as:

- Sequence parallelism (`sequence_parallel=True`)
- Mixed precision training
- Activation checkpointing ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

The parallelism strategy is typically configured at the model level and remains consistent across training, validation, and inference phases of the machine learning pipeline. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Usage in Supervised Fine-Tuning

When performing [[Supervised Fine-Tuning (SFT)]], tensor model parallelism settings must be configured based on the base model architecture. The configuration involves setting both tensor and pipeline parallelism values before initiating the fine-tuning process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

For evaluation phases, tensor model parallelism settings may be adjusted independently. Smaller models during inference might use `tensor_model_parallel_size=1` even if they were trained with higher parallelism values, depending on the available hardware resources. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Configuration Examples

### Training Configuration

For large-scale model training, tensor parallelism is configured alongside other distributed training parameters. The configuration includes setting the tensor model parallel size as an environment variable and passing it to the training script:

```
TP_SIZE=8
PP_SIZE=12
```

These values are then used in the model configuration:

```
model.tensor_model_parallel_size=${TP_SIZE}
model.pipeline_model_parallel_size=${PP_SIZE}
model.sequence_parallel=True
```

This configuration enables distributed training across multiple devices while maintaining model coherence. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Evaluation Configuration

During model evaluation, tensor parallelism can be adjusted for different hardware constraints. For single-device inference, the configuration can be simplified:

```
model.tensor_model_parallel_size=1
model.pipeline_model_parallel_size=1
```

This configuration allows for single-device inference when sufficient memory is available, providing flexibility in deployment scenarios. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## NeMo Launcher Integration

When using the [[NVIDIA NeMo Framework]] Launcher, tensor model parallelism is configured through YAML configuration files. The model section specifies the parallelism parameters:

```yaml
model:
  restore_from_path: /path/to/nemotron-340b.nemo
  tensor_model_parallel_size: 8
  pipeline_model_parallel_size: 16
```

The launcher automatically handles the distribution of the model across the specified number of devices based on these configuration parameters. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]
