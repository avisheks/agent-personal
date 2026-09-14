---
title: "dataset-streaming-mode"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-oumi-oss.md
createdAt: 2026-05-18T18:34:18.080337+00:00
updatedAt: 2026-05-18T18:34:18.080337+00:00
---
# Dataset Streaming Mode

Dataset Streaming Mode is a configuration option in machine learning frameworks that enables processing of large datasets without loading the entire dataset into memory at once. This approach is particularly useful when working with datasets that are too large to fit in available system memory.

## Overview

In the context of [[Supervised Fine-Tuning (SFT)]], streaming mode can be enabled through configuration parameters to handle large-scale training datasets efficiently. The streaming approach allows models to process data incrementally, making it possible to work with datasets that would otherwise exceed memory constraints. ^[supervised-fine-tuning-oumi-oss.md]

## Configuration

Dataset streaming mode is controlled through the `stream` parameter in training configurations. When set to `true`, the system processes the dataset in a streaming fashion rather than loading it entirely into memory. The parameter is typically specified alongside other dataset configuration options such as dataset name and data split selection. ^[supervised-fine-tuning-oumi-oss.md]

### Example Configuration

The streaming mode can be configured in the training configuration as follows:

```yaml
training:
  data:
    train:
      datasets:
        - dataset_name: your_sft_dataset_name
          split: train
          stream: true
      collator_name: text_with_padding
```

In this configuration, the `stream: true` setting enables streaming mode for the specified dataset, allowing the training process to handle large datasets without memory overflow issues. ^[supervised-fine-tuning-oumi-oss.md]

## Benefits

The primary advantage of dataset streaming mode is memory efficiency. By processing data incrementally rather than loading entire datasets into memory, streaming mode enables training on datasets that would otherwise be impossible to use due to memory limitations. This is particularly valuable when working with large-scale language model training datasets or when operating in resource-constrained environments. ^[supervised-fine-tuning-oumi-oss.md]

## Implementation Context

Dataset streaming mode is available as part of the dataset configuration parameters in machine learning frameworks. It works in conjunction with other dataset parameters including dataset name specification, data split selection, and collator configuration for batching operations. The streaming approach is particularly useful when combined with [[BaseSftDataset]] implementations for supervised fine-tuning workflows. ^[supervised-fine-tuning-oumi-oss.md]

## Usage in Training Pipelines

When implementing dataset streaming mode, the configuration is typically specified within the training data parameters. The streaming mode setting is applied at the dataset level, allowing different datasets within the same training configuration to use different streaming settings based on their size and memory requirements. This flexibility enables optimized resource utilization across diverse training scenarios. ^[supervised-fine-tuning-oumi-oss.md]
