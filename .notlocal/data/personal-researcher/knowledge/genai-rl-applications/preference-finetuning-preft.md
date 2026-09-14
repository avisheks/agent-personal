---
title: "Preference Finetuning (PreFT)"
summary: "A category of training methods that align models to human preferences and improve style of language generation, including both RLHF and direct alignment algorithms like DPO."
sources:
  - genai-rl-applications/2504.md
createdAt: 2026-05-24T12:46:06.980745+00:00
updatedAt: 2026-05-24T12:46:06.980745+00:00
---
# Preference Finetuning (PreFT)

**Preference Finetuning (PreFT)** is a category of machine learning techniques used to align language models to human preferences and values. PreFT encompasses multiple optimization methods that tune models based on comparative human feedback rather than direct supervision, with the goal of improving model behavior and output quality according to human judgment. ^[2504.md]

## Overview

Preference finetuning represents one of three main components of modern post-training for language models, alongside [[Supervised Fine-Tuning (SFT)]] and Reinforcement Finetuning (RFT). While instruction tuning teaches models the question-answer format and basic skills, PreFT focuses on aligning models to human preferences and improving the style and quality of language generation. ^[2504.md]

The core motivation behind PreFT is that directly capturing complex human values in a single reward function is effectively impossible. Instead, these techniques leverage the principle that it is far easier for humans (and AI systems) to differentiate between good and bad responses than to generate good responses from scratch. ^[2504.md]

## Key Techniques

### Reinforcement Learning from Human Feedback (RLHF)

[[Reinforcement Learning from Human Feedback (RLHF)]] is the foundational technique within PreFT. RLHF follows a three-stage process:

1. **Instruction tuning** on supervised examples to teach basic formatting
2. **[[Reward Modeling]]** using human preference data to create optimization targets  
3. **[[Policy Gradient Algorithms]]** to optimize the model against the reward model

This approach modifies the standard reinforcement learning setup by using learned reward models instead of environmental rewards, eliminating state transitions, and providing response-level rather than token-level feedback. ^[2504.md]

### Direct Alignment Algorithms

[[Direct Alignment from Preferences Optimization (DAPO)]] methods, such as [[Direct Preference Optimization (DPO)]], optimize models directly from pairwise preference data without requiring an intermediate reward model. These algorithms have become popular alternatives to traditional RLHF due to their computational efficiency and implementation simplicity. ^[2504.md]

### Rejection Sampling

Rejection sampling represents the most basic PreFT technique, where multiple candidate completions are generated and filtered using a reward model to select only high-quality responses for further training. ^[2504.md]

## Training Process

### Problem Formulation

PreFT adapts the standard reinforcement learning optimization objective:

```
J(π) = E_τ∼π[r_θ(s_t,a_t)] - βD_KL(π_RL(·|s_t)∥π_ref(·|s_t))
```

Where the reward function `r_θ` is a learned model of human preferences, and the KL divergence term provides regularization to prevent the model from deviating too far from its starting point. ^[2504.md]

### Data Requirements

PreFT relies heavily on preference data collected through human annotation or AI feedback. This data typically consists of pairwise comparisons where annotators indicate which of two model responses they prefer for a given prompt. The collection process involves specialized interfaces and careful attention to bias mitigation. ^[2504.md]

## Applications and Impact

### Style and Behavior Alignment

PreFT techniques excel at teaching models subtle stylistic and behavioral preferences that are difficult to capture through direct supervision. This includes improving response helpfulness, reducing harmful outputs, and matching specific organizational or product requirements. ^[2504.md]

### Generalization Benefits

Compared to instruction finetuning alone, PreFT methods demonstrate superior generalization across domains. The contrastive nature of preference learning, which shows models both positive and negative examples, contributes to this improved robustness. ^[2504.md]

## Modern Developments

### Multi-Stage Training

Contemporary PreFT implementations involve complex, multi-stage processes with numerous training iterations. Modern recipes demonstrate how PreFT integrates with other post-training techniques across multiple rounds of optimization. ^[2504.md]

### Reasoning Applications

Recent developments have extended PreFT to reasoning-heavy domains through techniques like [[Process Reward Models]] and verifiable reward training, as demonstrated in models like DeepSeek R1. ^[2504.md]

### Synthetic Data Integration

The field has increasingly moved toward using AI-generated preference data and [[Constitutional AI]] methods to reduce reliance on human annotation while maintaining training effectiveness. ^[2504.md]

## Challenges and Limitations

### Over-optimization

PreFT methods are susceptible to over-optimization, where models learn to exploit reward model weaknesses rather than genuinely improving. This necessitates careful regularization and monitoring throughout training. ^[2504.md]

### Implementation Complexity

Effective PreFT requires substantially more computational resources, data collection infrastructure, and technical expertise compared to basic instruction tuning, making it more expensive and time-consuming to implement properly. ^[2504.md]

### Bias and Representation

Preference data inherently contains human biases and may not represent diverse perspectives adequately, requiring careful consideration of data collection practices and evaluation methods. ^[2504.md]
