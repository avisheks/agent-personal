---
title: "basesftdataset"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-oumi-oss.md
createdAt: 2026-05-20T03:42:33.040257+00:00
updatedAt: 2026-05-20T03:42:33.040257+00:00
---
# BaseSftDataset

**BaseSftDataset** is the base class for all Supervised Fine-Tuning (SFT) datasets in Oumi OSS. It provides a standardized interface for implementing dataset-specific transformation logic that converts raw data into conversation format suitable for training language models. ^[supervised-fine-tuning-oumi-oss.md]

## Overview

BaseSftDataset serves as the foundation for creating SFT datasets by requiring subclasses to implement the `transform_conversation()` method. This method defines how raw dataset examples are converted into structured [[Supervised Fine-Tuning (SFT)]] conversation objects that can be used for model training. ^[supervised-fine-tuning-oumi-oss.md]

## Core Functionality

### Transform Conversation Method

The primary requirement for BaseSftDataset subclasses is implementing the `transform_conversation()` method. This method takes a raw example from the dataset and transforms it into a Conversation object containing structured messages with roles and content. The method receives a dictionary representing one row of the raw dataset and must return a Conversation object with appropriate Message objects containing Role and content information. ^[supervised-fine-tuning-oumi-oss.md]

### Integration with Training Pipeline

BaseSftDataset integrates with the Oumi OSS training configuration through the `TrainingConfig` system. Datasets can be specified in training configurations using parameters such as `dataset_name`, `split`, and `stream` for handling large datasets. The system supports collator specifications such as `text_with_padding` for batching during training. ^[supervised-fine-tuning-oumi-oss.md]

## Implementation Pattern

### Creating Custom Datasets

To create a new SFT dataset, developers must:

1. Subclass BaseSftDataset
2. Implement the `transform_conversation()` method
3. Register the dataset using the `@register_dataset` decorator ^[supervised-fine-tuning-oumi-oss.md]

The implementation requires defining dataset-specific transformation logic in the `transform_conversation()` method, which converts raw dataset examples into structured conversation format with user and assistant messages. ^[supervised-fine-tuning-oumi-oss.md]

### Registration System

Custom datasets are registered to the dataset registry using decorators and must be added to the appropriate Python modules to be discoverable by the system. This registration enables the datasets to be referenced by name in configuration files and Python code. ^[supervised-fine-tuning-oumi-oss.md]

## Usage Patterns

### Configuration-Based Usage

BaseSftDataset subclasses can be used through configuration files by specifying the registered dataset name in the training configuration. The system supports various parameters including dataset splits, streaming mode for large datasets, and collator specifications. ^[supervised-fine-tuning-oumi-oss.md]

### Programmatic Usage

Datasets can also be instantiated programmatically using the `build_dataset()` function, which takes parameters such as dataset name, tokenizer, and dataset split to create dataset instances for use in training loops. The datasets can then be used with PyTorch DataLoader for batch processing during training. ^[supervised-fine-tuning-oumi-oss.md]

### Compatible Dataset Reuse

The system supports using unregistered datasets that share the same format as registered datasets through dataset name overrides using the `dataset_name_override` parameter in `dataset_kwargs`. This allows developers to leverage existing dataset classes for new data sources without explicit registration, though this feature is noted as experimental. ^[supervised-fine-tuning-oumi-oss.md]

## Example Implementation

A typical BaseSftDataset implementation follows this pattern:

```python
@register_dataset("custom_sft_dataset")
class CustomSftDataset(BaseSftDataset):
    def transform_conversation(self, example: Dict[str, Any]) -> Conversation:
        conversation = Conversation(
            messages=[
                Message(role=Role.USER, content=example['input']),
                Message(role=Role.ASSISTANT, content=example['output'])
            ]
        )
        return conversation
```

The `transform_conversation()` method receives a dictionary representing one row of the raw dataset and returns a Conversation object with structured Message objects containing Role and content information. ^[supervised-fine-tuning-oumi-oss.md]

## Related Concepts

BaseSftDataset works closely with [[Chat Template Formatting]] for structuring conversations, [[Dataset Packing]] for efficient batching, and [[Task-Specific Dataset Preparation]] for domain-specific adaptations. It also integrates with [[Parameter-Efficient Fine-Tuning (PEFT)]] methods and supports [[Hugging Face Transformers Library]] tokenizers for text processing.
