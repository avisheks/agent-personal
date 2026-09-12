---
title: "Post-Training"
summary: "A comprehensive set of techniques applied after pretraining to make language models more useful, including instruction tuning, preference finetuning, and reinforcement finetuning."
sources:
  - genai-rl-applications/2504.md
createdAt: 2026-05-24T12:45:47.844777+00:00
updatedAt: 2026-05-24T12:45:47.844777+00:00
---
# Post-Training

Post-training is a comprehensive set of techniques applied after pretraining to make language models more useful for downstream tasks. It encompasses all training that occurs after the large-scale autoregressive pretraining phase on primarily web data and has become crucial to the transition of language models from academic experiments to general-purpose technology. ^[2504.md]

## Overview

Post-training can be summarized as using three main optimization methods:

1. **Instruction/[[Supervised Fine-Tuning (SFT)]] (IFT/SFT)** - Teaching formatting and foundational instruction following abilities, largely focused on learning features in language
2. **Preference Finetuning (PreFT)** - Aligning to human preferences and achieving performance improvements, largely focused on style of language and subtle human preferences that are hard to quantify  
3. **[[Reinforcement Fine-Tuning (RFT)]]** - The newest type of post-training that boosts performance on verifiable domains ^[2504.md]

## The Elicitation Interpretation

A key intuition for understanding post-training's effectiveness is the **elicitation interpretation**, which suggests that post-training extracts and amplifies valuable behaviors already present in the base model rather than teaching entirely new capabilities. This theory, also known as the Superficial Alignment Hypothesis, proposes that a model's knowledge and capabilities are learned almost entirely during pretraining, while post-training teaches the model which subdistribution of formats to use when interacting with users. ^[2504.md]

However, modern evidence suggests this interpretation is incomplete. Post-training has demonstrated the ability to substantially improve model performance beyond mere formatting, particularly in areas like mathematical reasoning and [[Chain-of-Thought Reasoning]], indicating that the impact is far from "superficial." ^[2504.md]

## Evolution of Post-Training Recipes

### Early RLHF Era (InstructGPT)

The canonical early post-training recipe followed a three-step process:

1. **Instruction tuning** on ~10K examples to teach question-answer format
2. **Training a [[Reward Modeling|reward model]]** on ~100K pairwise prompts to capture human preferences  
3. **[[Reinforcement Learning from Human Feedback]]** training on ~100K prompts using the reward model ^[2504.md]

### Modern Multi-Stage Approaches (Tülu 3)

Contemporary post-training involves many more model versions and training stages. The [[Tülu 3 Language Model]] recipe exemplifies this evolution:

1. **Instruction tuning** on ~1M examples using primarily synthetic data
2. **On-policy preference data training** on ~1M preference pairs to boost conversational ability
3. **Reinforcement Learning with Verifiable Rewards** on ~10K prompts for specific skill improvement ^[2504.md]

### Reasoning Model Era (DeepSeek R1)

The emergence of reasoning models has led to further evolution in post-training recipes:

1. **"Cold-start"** training with 100K+ on-policy reasoning samples
2. **Large-scale reinforcement learning** training until convergence
3. **[[Rejection Sampling]]** on reasoning problems and general queries
4. **Mixed reinforcement learning** combining verifiable rewards with general preference tuning ^[2504.md]

## Key Components

Post-training relies on several core techniques:

- **[[Supervised Fine-Tuning (SFT)]]** - The foundation for teaching instruction-following behavior
- **[[Reward Modeling]]** - Training models to capture human preference signals
- **[[Direct Preference Optimization (DPO)]]** - Algorithms that optimize preferences without intermediate reward models
- **[[Constitutional AI]]** - Methods for using AI feedback in the training process
- **[[Regularization]]** - Techniques to prevent over-optimization during training ^[2504.md]

## Relationship to RLHF

While [[Reinforcement Learning from Human Feedback]] was historically central to post-training and colloquially encompassed all post-training techniques after ChatGPT's release, RLHF is now understood as one component within the broader post-training framework. RLHF specifically focuses on preference finetuning, which has more complexity than instruction tuning and is more established than reinforcement finetuning. ^[2504.md]

## Impact and Significance

Post-training has proven crucial for creating effective general-purpose models. Unlike instruction finetuning alone, techniques like RLHF generalize far better across domains, helping bridge the gap between raw language model capabilities and user-facing applications. The style and format of information presentation, which post-training heavily influences, plays a crucial role in how information is learned and communicated. ^[2504.md]

Modern post-training represents a convergence of multiple fields including philosophy, psychology, economics, optimal control, reinforcement learning, and deep learning systems. This interdisciplinary foundation enables the integration of complex human values and objectives into AI systems used in real-world applications. ^[2504.md]
