---
title: "pipeline-model-parallelism"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-18T18:35:25.276355+00:00
updatedAt: 2026-05-18T18:35:25.276355+00:00
---
# Pipeline Model Parallelism

Pipeline Model Parallelism is a distributed training technique that divides a neural network model across multiple devices by splitting it into sequential stages, where different layers or groups of layers are placed on different devices and data flows through them in a pipeline fashion.

## Overview

Pipeline Model Parallelism enables training of large neural networks that cannot fit on a single device by partitioning the model vertically across multiple devices. Each device handles a subset of the model's layers, and training data flows through the pipeline from one stage to the next. This approach is particularly useful for very large language models that exceed the memory capacity of individual GPUs. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Configuration in Training Systems

In distributed training frameworks, Pipeline Model Parallelism is configured alongside other parallelization strategies. The pipeline parallelism size parameter (`pipeline_model_parallel_size`) determines how many devices the model is split across. For example, when training large models like Nemotron 340B, a typical configuration might use `PP_SIZE=12` or `pipeline_model_parallel_size=16`, indicating the model is divided into 12 or 16 sequential stages respectively. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

Pipeline Model Parallelism is commonly used in combination with [[Tensor Model Parallelism]], where `tensor_model_parallel_size` and `pipeline_model_parallel_size` work together to distribute both computation and model parameters across available devices. This hybrid approach allows for efficient scaling to very large model sizes. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Implementation in Training Workflows

During [[Supervised Fine-Tuning (SFT)]] of large language models, Pipeline Model Parallelism parameters are set based on the model size and available hardware. The configuration typically includes setting both the pipeline parallel size and other related parameters such as micro batch size and global batch size to optimize memory usage and training throughput. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

Training frameworks like [[NVIDIA NeMo Framework]] support Pipeline Model Parallelism through configuration parameters that can be adjusted for different model sizes and hardware configurations. The pipeline parallel size must be carefully chosen to balance memory usage, communication overhead, and training efficiency across the distributed system. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Configuration Examples

For large-scale models, specific pipeline parallelism configurations are recommended based on model size:

- **Nemotron 340B**: Uses `PP_SIZE=12` in basic configurations or `pipeline_model_parallel_size=16` in launcher configurations
- **Multi-node setups**: Pipeline parallelism is often combined with tensor parallelism, such as `tensor_model_parallel_size=8` and `pipeline_model_parallel_size=16` for distributed training across multiple nodes ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

The pipeline parallel size is typically set during the training command execution and can be adjusted through configuration files or command-line parameters depending on the available hardware resources and model requirements. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Multi-Node Training Considerations

When running Pipeline Model Parallelism across multiple nodes, the configuration must account for the distributed nature of the training setup. The total number of devices is calculated as `num_nodes × devices`, and the pipeline parallelism size must divide evenly into this total to ensure proper model distribution across the available hardware. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

For evaluation and inference after training, the pipeline parallelism configuration may be adjusted differently than during training. Evaluation tasks often use smaller pipeline parallel sizes (such as `pipeline_model_parallel_size=1`) to optimize for inference speed rather than memory distribution. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]
