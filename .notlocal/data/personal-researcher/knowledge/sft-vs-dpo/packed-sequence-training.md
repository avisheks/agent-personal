---
title: "packed-sequence-training"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md
createdAt: 2026-05-18T18:35:37.384467+00:00
updatedAt: 2026-05-18T18:35:37.384467+00:00
---
# Packed Sequence Training

**Packed Sequence Training** is a training optimization technique used in [[Supervised Fine-Tuning (SFT)]] that enables more efficient processing of variable-length sequences by combining multiple shorter sequences into single training examples up to a maximum sequence length. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Overview

In standard training approaches, each training example typically corresponds to a single sequence, which can lead to inefficient GPU utilization when sequences are shorter than the maximum sequence length. Packed sequence training addresses this by concatenating multiple sequences together to better utilize the available sequence length capacity. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Implementation in NeMo Framework

### Data Format Requirements

To enable packed sequence training in the [[NVIDIA NeMo Framework]], the training data must be prepared in a specific packed format. Unlike standard training which uses `.jsonl` files, packed sequence training requires data to be stored as `.npy` files that contain the pre-packed sequences. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Configuration Parameters

Packed sequence training is enabled through specific configuration adjustments in the NeMo Framework. The key parameter `+model.data.train_ds.packed_sequence=True` must be added to activate the packed sequence functionality. The training data file path should point to the packed `.npy` file rather than a standard `.jsonl` file. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Batch Size Adjustments

When using packed sequences, both micro batch size and global batch size need to be significantly reduced compared to standard training. This adjustment is necessary because packing increases the effective amount of data processed per batch. For example, when training with a sequence length of 4096, the global batch size might be reduced from 128 to 8, while the micro batch size is set to 1. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

### Configuration Example

The following configuration demonstrates how to enable packed sequence training in NeMo:

```
model.data.train_ds.file_names=/path/to/dolly/packed_4096_seed0.npy
+model.data.train_ds.packed_sequence=True
model.micro_batch_size=1
model.global_batch_size=8
```

This configuration specifies the packed data file, enables packed sequence mode, and sets appropriate batch sizes for the packed training approach. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Benefits

Packed sequence training provides improved training efficiency by maximizing the utilization of the available sequence length capacity. This optimization is particularly beneficial when working with datasets containing many sequences that are significantly shorter than the maximum sequence length, as it reduces the amount of padding required and increases the effective throughput of the training process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]

## Integration with Other Techniques

Packed sequence training can be combined with other training optimizations available in the NeMo Framework. It is compatible with advanced precision techniques such as [[FP8 Training]] and can be used alongside [[Parameter-Efficient Fine-Tuning (PEFT)]] methods for further efficiency gains during the fine-tuning process. ^[supervised-fine-tuning-sft-nvidia-nemo-framework-user-guide.md]
