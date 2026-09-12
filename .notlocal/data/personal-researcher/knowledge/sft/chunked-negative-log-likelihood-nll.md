---
title: "Chunked Negative Log-Likelihood (NLL)"
summary: "A memory optimization technique in TRL that reduces VRAM usage by 30-50% by dropping masked positions before the language model head during training."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:56:11.113607+00:00
updatedAt: 2026-06-15T11:56:11.113607+00:00
---
# Chunked Negative Log-Likelihood (NLL)

**Chunked Negative Log-Likelihood (NLL)** is a memory optimization technique used in [[Supervised Fine-Tuning (SFT)]] that reduces VRAM consumption by 30-50% during language model training. The technique works by dropping masked token positions before passing data through the language model head (lm_head), rather than computing the full sequence and then masking the loss. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Overview

Chunked NLL addresses a key memory bottleneck in standard fine-tuning approaches. In traditional [[Supervised Fine-Tuning (SFT)]], the model computes logits for all tokens in a sequence, including those that are masked out during loss calculation (such as prompt tokens in chat training). Chunked NLL eliminates this waste by removing masked positions before the computationally expensive lm_head operation. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Implementation

The technique is implemented in the TRL (Transformers Reinforcement Learning) library version 1.5.1 and later. It integrates with the standard [[Answer-Only Loss]] approach commonly used in chat model training, where loss is computed only on assistant response tokens while prompt tokens are masked with label=-100. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Memory Benefits

Chunked NLL provides substantial memory savings:

- **30-50% VRAM reduction** during training
- Particularly effective for long sequences where a large portion of tokens are masked
- Enables training of larger models or longer sequences on the same hardware ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Relationship to Other Techniques

Chunked NLL works alongside other memory optimization approaches in modern SFT pipelines:

- Compatible with [[Dataset Packing]] techniques like Best-Fit Decreasing
- Can be combined with [[Parameter-Efficient Fine-Tuning (PEFT)]] methods like [[Low-Rank Adaptation (LoRA)]]
- Integrates with mixed precision training using BF16 or FP16 ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Usage Context

This optimization is particularly valuable in scenarios where:

- Training chat models with long prompts and shorter responses
- Working with limited GPU memory resources
- Scaling to larger batch sizes for improved training stability
- Processing datasets with significant variation in prompt-to-response ratios ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]
