---
title: "Group Relative Policy Optimization (GRPO)"
summary: "A DPO variant proposed by DeepSeek that avoids the critic model required in PPO by using a group mechanism for policy updates, reducing compute and memory overhead while maintaining strong performance."
sources:
  - genai-rl-applications/reinforcement-learning-from-human-feedback-rlhf-explained-intuitionlabs.md
  - sft-vs-dpo/sft-dpo.md
createdAt: 2026-05-24T12:56:01.897276+00:00
updatedAt: 2026-05-24T12:56:01.897276+00:00
---
I'll create a comprehensive wiki page about Supervised Fine-Tuning (SFT).

# Supervised Fine-Tuning (SFT)

## Overview

Supervised Fine-Tuning (SFT) is a machine learning technique used to adapt pre-trained language models to specific tasks or domains by training them on curated datasets of input-output pairs. SFT represents the first stage in most modern language model alignment pipelines and serves as the foundation for more advanced training methods like [[Direct Preference Optimization]] and [[Reinforcement Learning from Human Feedback]]. ^[sft-dpo.md]

## Core Concept

SFT operates on the principle of imitation learning, where the model learns to replicate high-quality demonstrations through maximum likelihood estimation. The training process involves feeding the model examples of desired behavior in the form of `(input, target_output)` pairs and optimizing the model to maximize the probability of producing the target outputs given the inputs. ^[sft-dpo.md]

## Training Process

### Data Requirements
SFT requires a dataset of demonstration pairs in the format `(x, y_good)`, where `x` represents the input prompt and `y_good` represents the desired output or demonstration. Unlike preference-based methods, SFT does not require comparative judgments between different outputs. ^[sft-dpo.md]

### Optimization Method
The training uses cross-entropy loss to maximize the likelihood of the target outputs. This approach is mathematically equivalent to maximum likelihood estimation, making it a straightforward supervised learning problem. The model learns to minimize the difference between its predicted token probabilities and the actual tokens in the demonstration data. ^[sft-dpo.md]

### Stability and Efficiency
SFT is characterized by high stability and sample efficiency compared to reinforcement learning approaches. The supervised learning framework provides consistent gradients and reliable convergence, making it an ideal starting point for model alignment. ^[sft-dpo.md]

## Applications

### Base Competence Development
SFT is particularly effective for establishing fundamental capabilities in language models, such as instruction following, formatting consistency, and domain-specific knowledge transfer. It serves as the foundation layer that enables models to understand and respond to user requests in a structured manner. ^[sft-dpo.md]

### Formatting and Structure
One of SFT's key strengths lies in teaching models consistent output formatting, response structure, and stylistic conventions. This makes it invaluable for applications requiring standardized outputs or specific communication patterns. ^[sft-dpo.md]

## Limitations

### Lack of Explicit Preference Modeling
Unlike [[Direct Preference Optimization]], SFT does not explicitly push down the probability of undesirable outputs. It only increases the likelihood of demonstrated behaviors without directly addressing what the model should avoid. ^[sft-dpo.md]

### Imitation Ceiling
SFT is fundamentally limited by the quality of its training demonstrations. The model can only learn to replicate the behaviors shown in the training data and cannot exceed the performance level of the demonstrators. ^[sft-dpo.md]

## Comparison with Other Methods

### Versus Direct Preference Optimization
While SFT focuses on imitating good examples, [[Direct Preference Optimization]] works with preference comparisons to explicitly model what outputs are better than others. DPO can push down the probability of inferior outputs, whereas SFT only reinforces positive examples. ^[sft-dpo.md]

### Versus Reinforcement Learning from Human Feedback
[[Reinforcement Learning from Human Feedback]] typically requires a reward model and uses policy gradient methods for optimization. SFT, in contrast, uses standard supervised learning techniques and does not require reward modeling, making it more computationally efficient and stable. ^[sft-dpo.md]

## Implementation

SFT is widely supported in modern machine learning frameworks, with implementations available in libraries like the Hugging Face Transformers and TRL (Transformer Reinforcement Learning) ecosystems. The technique can be easily integrated into existing training pipelines and scaled to large language models. ^[sft-dpo.md]

## Role in Multi-Stage Training

SFT typically serves as the first stage in sophisticated alignment pipelines. Many successful language models, including those behind ChatGPT and similar systems, use SFT as a foundation before applying more advanced techniques like [[Direct Preference Optimization]] or [[Reinforcement Learning from Human Feedback]] for further refinement. ^[sft-dpo.md]

## Related Pages in the Wiki

supervised-fine-tuning-sft
direct-preference-optimization-dpo
reinforcement-learning-from-human-feedback-rlhf
group-relative-policy-optimization-grpo
instruction-tuning
preference-learning
imitation-learning
maximum-likelihood-estimation
cross-entropy-loss
demonstration-learning
alignment-training-pipeline
hugging-face-transformers-library
model-fine-tuning
language-model-alignment
