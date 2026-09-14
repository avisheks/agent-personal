---
title: "group-relative-policy-optimization-grpo"
summary: ""
sources:
  - sft-vs-dpo/sft-dpo.md
createdAt: 2026-05-20T03:38:58.127201+00:00
updatedAt: 2026-05-20T03:38:58.127201+00:00
---
I'll create a comprehensive wiki page about Group Relative Policy Optimization (GRPO).

# Group Relative Policy Optimization (GRPO)

## Overview

Group Relative Policy Optimization (GRPO) is a policy optimization method for training language models that improves upon traditional approaches by using grouped sampling and relative rewards. GRPO was introduced as part of the DeepSeekMath project, which aimed to push the limits of mathematical reasoning in open language models. ^[sft-dpo.md]

## Core Concept

GRPO operates on the principle of "improving policy relative to groups of sampled outputs" rather than optimizing against individual responses or fixed reward models. This approach provides more efficient optimization compared to traditional methods like [[Proximal Policy Optimization]] (PPO) while maintaining the benefits of policy gradient methods. ^[sft-dpo.md]

## Key Characteristics

### Data Requirements
Unlike [[Supervised Fine-Tuning]] which requires demonstration pairs `(x, y_good)` or [[Direct Preference Optimization]] which needs pairwise comparisons `(x, y_preferred, y_rejected)`, GRPO works with grouped samples and relative reward signals. ^[sft-dpo.md]

### Optimization Method
GRPO uses relative rewards within groups of sampled outputs, making it distinct from:
- SFT's maximum likelihood approach
- DPO's preference-margin optimization  
- Traditional RLHF's expected reward maximization ^[sft-dpo.md]

### Reward Model Dependency
GRPO typically requires reward signals but processes them in a relative manner within sample groups, which can improve training stability and efficiency compared to absolute reward optimization. ^[sft-dpo.md]

## Applications

GRPO has shown particular effectiveness in reasoning-focused training scenarios. The method was specifically developed and demonstrated in the context of mathematical reasoning tasks, where the relative comparison of solution approaches within groups provides more nuanced optimization signals than binary preference judgments. ^[sft-dpo.md]

## Comparison with Other Methods

### Versus Supervised Fine-Tuning
While [[Supervised Fine-Tuning]] focuses on imitating target outputs through cross-entropy loss, GRPO explicitly incorporates preference signals and can push down the probability of inferior outputs within comparison groups. ^[sft-dpo.md]

### Versus Direct Preference Optimization  
Unlike [[Direct Preference Optimization]] which works with pairwise preferences, GRPO operates on groups of samples, potentially capturing more complex preference structures and providing richer optimization signals. ^[sft-dpo.md]

### Versus Traditional RLHF
GRPO offers improved sample efficiency compared to PPO-based [[Reinforcement Learning from Human Feedback]] while maintaining the ability to optimize for complex reward structures. ^[sft-dpo.md]

## Implementation

GRPO is supported in modern training frameworks, including the Hugging Face TRL (Transformer Reinforcement Learning) library, which provides trainer abstractions alongside other post-training methods. ^[sft-dpo.md]
