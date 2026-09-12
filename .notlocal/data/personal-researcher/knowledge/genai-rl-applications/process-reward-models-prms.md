---
title: "Process Reward Models (PRMs)"
summary: "Reward models trained to output scores at every step in a chain of thought reasoning process, providing supervision for intermediate reasoning steps rather than just final outcomes."
sources:
  - genai-rl-applications/2504.md
createdAt: 2026-05-24T12:47:18.498425+00:00
updatedAt: 2026-05-24T12:47:18.498425+00:00
---
# Process Reward Models (PRMs)

Process Reward Models (PRMs), originally called Process-supervised Reward Models, are specialized [[reward-modeling]] systems that output scores at every step in a [[chain-of-thought-reasoning]] process, rather than providing a single score for an entire response. These models represent a significant advancement in evaluating and training reasoning capabilities in language models. ^[2504.md]

## Overview

Process Reward Models differ fundamentally from standard reward models and [[outcome-reward-models]] in their granular approach to evaluation. While traditional reward models output a single score at the end-of-sequence (EOS) token and Outcome Reward Models (ORMs) predict correctness per token, PRMs specifically target the end of each reasoning step to provide step-by-step feedback on the reasoning process. ^[2504.md]

## Training and Architecture

### Training Data Requirements

PRMs require supervision at the end of each reasoning step, making their training data more complex than standard preference models. The training process involves:

- **Step-level annotations**: Each reasoning step receives a specific label, typically -1 for incorrect, 0 for neutral, and 1 for correct
- **Reasoning step separation**: Special tokens (like double newlines) mark the boundaries between reasoning steps
- **Per-step supervision**: Unlike ORMs that use outcome-level labels for every token, PRMs focus on step-specific feedback ^[2504.md]

### Implementation Structure

PRMs utilize a language modeling head that outputs predictions only at the end of reasoning steps, rather than continuously throughout the sequence. The implementation typically involves:

```
# Example from HuggingFace's TRL implementation
separator_ids = tokenizer.encode(step_separator, add_special_tokens=False)
completions_ids = [completion + separator_ids for completion in completions_ids]
labels = [[-100] * (len(completion) - 1) + [label] for completion, label in zip(completions_ids, labels)]
```

The model predicts three classes (-1, 0, 1) corresponding to incorrect, neutral, and correct reasoning steps respectively. ^[2504.md]

## Comparison with Related Models

### Model Types Comparison

| Model Class | Prediction Target | Training Method | Architecture |
|-------------|------------------|-----------------|--------------|
| **Process Reward Models** | Score for intermediate steps at end of reasoning steps | Stepwise annotations per reasoning step | Language modeling head with inference per reasoning step, predicts three classes |
| **Reward Models** | Quality probability at EOS token | Contrastive loss between pairwise comparisons | Regression/classification head on LM features |
| **Outcome Reward Models** | Correctness probability per-token | Labeled outcome pairs | Language modeling head per-token cross-entropy |
| **Value Functions** | Expected return given current state | Regression to each sequence point | Classification with per-token output |

^[2504.md]

## Applications and Use Cases

Process Reward Models are particularly valuable in domains requiring step-by-step reasoning verification, such as:

- **Mathematical problem solving**: Evaluating each step in mathematical proofs or calculations
- **Logical reasoning**: Assessing the validity of each inference in a logical chain
- **Multi-step problem decomposition**: Providing feedback on intermediate problem-solving steps

The granular feedback provided by PRMs enables more precise training of reasoning capabilities compared to outcome-only evaluation methods. ^[2504.md]

## Training Methodology

### Supervision Approaches

PRMs can be trained using different supervision methods:

- **Direct step annotation**: Human annotators label each reasoning step
- **Rollout-based supervision**: Collecting outcome data from intermediate states to supervise step-level predictions
- **Hybrid approaches**: Combining direct annotation with automated verification where possible

When rollouts from intermediate states are used to collect outcome data, the training blends multiple methodologies, but if the loss focuses on per-reasoning-step labels, it remains classified as PRM training. ^[2504.md]

## Relationship to RLHF Pipeline

Process Reward Models integrate into the broader [[reinforcement-learning-from-human-feedback]] framework as specialized evaluation tools. They can be used in:

- **[[rejection-sampling]]** workflows for filtering reasoning chains
- **[[policy-gradient-algorithms]]** training where step-level rewards guide optimization
- **[[direct-alignment-from-preferences-optimization-dapo]]** methods adapted for process-level feedback

The step-by-step evaluation capability of PRMs makes them particularly suitable for training models that need to maintain reasoning quality throughout extended problem-solving sequences. ^[2504.md]

## Current Limitations and Research Directions

While PRMs offer significant advantages for reasoning tasks, they face several challenges:

- **Annotation complexity**: Requiring step-level human supervision increases data collection costs and complexity
- **Limited tooling support**: PRMs have less support in open-source RLHF tools compared to standard reward models
- **Evaluation benchmarks**: Emerging evaluation frameworks like PRM Bench, VisualProcessBench, ViLBench, and VLRMBench are still developing standardized assessment methods

The field continues to evolve with new applications in [[reasoning-training]] and integration with modern [[four-stage-post-training-pipeline]] approaches. ^[2504.md]
