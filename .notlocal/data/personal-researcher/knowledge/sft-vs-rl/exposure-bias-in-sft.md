---
title: "Exposure Bias in SFT"
summary: "The phenomenon where supervised fine-tuning creates a distribution mismatch between training conditions (teacher forcing) and inference conditions (autoregressive generation), leading to error accumulation."
sources:
  - sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-15T11:22:24.490542+00:00
updatedAt: 2026-06-15T11:22:24.490542+00:00
---
# Exposure Bias in SFT

**Exposure bias** is a fundamental limitation in [[Supervised Fine-Tuning (SFT)]] where models are trained on expert demonstrations but must generate text autoregressively at inference time, creating a distribution mismatch between training and deployment conditions.

## The Problem

During SFT training, models learn to predict the next token given the ground truth context from expert demonstrations. However, at inference time, models must generate text using their own previously generated tokens as context. This creates a compounding error problem where small mistakes early in generation can lead to increasingly poor outputs as the model drifts from the training distribution. ^[sft-vs-rl-for-post-training-llms.md]

The exposure bias manifests as a gap between training accuracy (where models see perfect context) and generation quality (where models see their own imperfect outputs). This distribution mismatch means that SFT models cannot learn to recover from their own errors during generation. ^[sft-vs-rl-for-post-training-llms.md]

## Why SFT Cannot Solve This

SFT is fundamentally bounded by the quality of demonstrations in the training data. Models learn to mimic expert behavior but cannot exceed the ceiling of their training examples. When models encounter situations not covered in demonstrations or make errors during generation, they lack the ability to self-correct because they were never trained on recovery strategies. ^[sft-vs-rl-for-post-training-llms.md]

This limitation is particularly problematic for tasks requiring [[Multi-Step Reasoning]] or [[Chain-of-Thought Reasoning]], where early errors can cascade through the reasoning process. SFT models may perform well on individual reasoning steps when given perfect context, but struggle with full problem-solving when they must build on their own intermediate outputs. ^[sft-vs-rl-for-post-training-llms.md]

## How RL Addresses Exposure Bias

[[Reinforcement Learning from Human Feedback (RLHF)]] and related methods like [[Group Relative Policy Optimization (GRPO)]] can mitigate exposure bias by training models on their own generated outputs. During RL training, models sample from their current policy and receive rewards based on the quality of complete generations, not just next-token predictions. ^[sft-vs-rl-for-post-training-llms.md]

This approach allows models to learn recovery strategies and self-correction behaviors. For example, the SCoRe method using RL improves performance by 15.6% on MATH problems compared to SFT by enabling models to backtrack and correct their reasoning when they detect errors. ^[sft-vs-rl-for-post-training-llms.md]

## Industry Evidence

The exposure bias problem explains several observed patterns in industry deployments. [[InstructGPT]] demonstrated that a 1.3B parameter model trained with RLHF was preferred over a 175B parameter GPT-3 model trained only with SFT, suggesting that addressing exposure bias can be more valuable than simply scaling model size. ^[sft-vs-rl-for-post-training-llms.md]

Recent work on [[DeepSeek-R1 Model]] shows that pure RL training can produce emergent reasoning behaviors and self-correction abilities that are not present in SFT-only models, even when the base model has the underlying capabilities. This supports the theory that exposure bias prevents SFT models from organizing their latent abilities into effective generation strategies. ^[sft-vs-rl-for-post-training-llms.md]

## Mitigation Strategies

Beyond RL methods, several techniques can partially address exposure bias:

- **Iterative training**: Alternating between SFT on model outputs and expert demonstrations
- **[[Rejection Sampling]]**: Generating multiple candidates and training on the best ones
- **Curriculum learning**: Gradually exposing models to their own outputs during training
- **[[Constitutional AI]]**: Using AI feedback to train models on self-correction

However, these approaches typically provide only partial solutions compared to full RL training that directly optimizes for generation quality under the model's own distribution. ^[sft-vs-rl-for-post-training-llms.md]
