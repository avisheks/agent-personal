---
title: "Best-Fit Decreasing (BFD) Packing"
summary: "A bin-packing algorithm used in TRL for sequence packing that achieves 2x throughput, 20% memory reduction, and 58% hallucination reduction by efficiently combining multiple training examples into single batches."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:55:48.743534+00:00
updatedAt: 2026-06-15T11:55:48.743534+00:00
---
# Best-Fit Decreasing (BFD) Packing

**Best-Fit Decreasing (BFD) Packing** is a bin-packing algorithm used in supervised fine-tuning of large language models to efficiently group training sequences of varying lengths into batches. The algorithm addresses the challenge of memory waste and computational inefficiency that occurs when sequences of different lengths are naively batched together.

## Overview

BFD packing is the default bin-packing strategy implemented in the [[Hugging Face Transformers Library]]'s TRL (Transformer Reinforcement Learning) framework. The algorithm works by first sorting sequences in decreasing order of length, then placing each sequence into the first bin (batch) where it fits, creating new bins as needed when no existing bin has sufficient remaining capacity. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Performance Benefits

BFD packing delivers significant improvements in training efficiency for [[Supervised Fine-Tuning (SFT)]]:

- **2x throughput improvement** compared to standard batching approaches
- **20% memory reduction** during training
- **58% hallucination reduction** in model outputs ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

These improvements stem from more efficient GPU utilization and reduced padding requirements when sequences of similar lengths are grouped together.

## Technical Implementation

The algorithm requires specialized attention mechanisms to prevent cross-contamination between different sequences within the same batch. Specifically, it uses `flash_attn_varlen_func` with `cu_seqlens` parameters to ensure that attention computations respect sequence boundaries and prevent models from attending across different training examples packed into the same batch. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Applications in Language Model Training

BFD packing is particularly valuable in [[Supervised Fine-Tuning (SFT)]] scenarios where training datasets contain sequences with highly variable lengths. This is common in instruction-following datasets, conversational AI training, and multi-turn dialogue systems where responses can range from brief acknowledgments to detailed explanations. The algorithm helps maximize hardware utilization while maintaining training quality. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Related Concepts

BFD packing is part of broader efficiency techniques in language model training, including [[Parameter-Efficient Fine-Tuning (PEFT)]], [[Mixed-Precision Training]], and [[Dataset Packing]] strategies. It complements other optimization approaches like gradient checkpointing and model parallelism in reducing the computational costs of fine-tuning large language models. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]
