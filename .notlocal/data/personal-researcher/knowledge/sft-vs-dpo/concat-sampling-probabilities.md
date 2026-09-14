---
title: "concat-sampling-probabilities"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-18T18:36:04.200107+00:00
updatedAt: 2026-05-18T18:36:04.200107+00:00
---
# Concat Sampling Probabilities

**Concat Sampling Probabilities** is a configuration parameter used in [[Supervised Fine-Tuning (SFT)]] to control the sampling distribution when training on multiple datasets. This parameter determines the percentage of fine-tuning data to use from each file when multiple training files are provided to the model. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Overview

When performing supervised fine-tuning with multiple training datasets, concat sampling probabilities specify how frequently each dataset should be sampled during training. The parameter accepts a list of probability values that correspond to each training file in the dataset configuration. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Configuration Requirements

The sum of all concat sampling probabilities must equal 1.0. This ensures that the probability distribution is valid and that all training data is properly weighted during the fine-tuning process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Usage Examples

### Single Dataset

For training with a single JSONL file, the concat sampling probability is set to 1.0:

```
TRAIN="[/path/to/databricks-dolly-15k/train.jsonl]"
CONCAT_SAMPLING_PROBS="[1.0]"
```

This configuration uses 100% of the data from the single training file. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Multiple Datasets

When training with multiple datasets, the probabilities can be distributed according to the desired sampling strategy:

```
TRAIN="[/path/to/dataset_1.jsonl,/path/to/dataset_2.jsonl]"
CONCAT_SAMPLING_PROBS="[0.3,0.7]"
```

In this example, 30% of the training samples come from dataset_1.jsonl and 70% come from dataset_2.jsonl. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Implementation in NVIDIA NeMo Framework

The concat sampling probabilities parameter is passed to the training configuration as `model.data.train_ds.concat_sampling_probabilities` when running the SFT command. This parameter works in conjunction with the `model.data.train_ds.file_names` parameter, which specifies the list of training files. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Example Configuration

In the [[NVIDIA NeMo Framework]], the parameter is set as part of the training command:

```bash
model.data.train_ds.file_names=${TRAIN_DS} \
model.data.train_ds.concat_sampling_probabilities=${CONCAT_SAMPLING_PROBS} \
```

For large models like Nemotron 340B, the configuration might include:

```
CONCAT_SAMPLING_PROBS="[1]"
TP_SIZE=8
PP_SIZE=12
```

This shows a single dataset configuration with full sampling probability and appropriate parallelism settings for the large model. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Practical Considerations

### Dataset Balancing

Concat sampling probabilities enable practitioners to balance the contribution of different datasets during fine-tuning. This is particularly useful when working with datasets of varying sizes or quality, allowing for strategic weighting of training data sources. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Multi-Domain Training

When fine-tuning on multiple domains or task types, concat sampling probabilities provide control over how much each domain contributes to the model's learning. This helps prevent any single dataset from dominating the training process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Integration with Training Pipeline

The concat sampling probabilities parameter is integrated into the complete SFT training pipeline alongside other critical parameters such as batch sizes, sequence lengths, and model parallelism configurations. It is typically set during the environment variable configuration phase before executing the training command. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Related Concepts

Concat sampling probabilities are particularly important when working with [[Dataset Packing]] and [[Task-Specific Dataset Preparation]], as they allow practitioners to balance the contribution of different datasets during the fine-tuning process. This parameter is essential for managing [[Cross-Domain Transfer in SFT]] scenarios where multiple domains or task types are represented in the training data. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]
