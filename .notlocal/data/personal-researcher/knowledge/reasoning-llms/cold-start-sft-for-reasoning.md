---
title: "cold-start-sft-for-reasoning"
summary: ""
sources:
  - reasoning-llms/chatgpt-reasoning-llms.md
  - reasoning-llms/demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md
createdAt: 2026-05-29T04:50:20.735142+00:00
updatedAt: 2026-05-29T04:50:20.735142+00:00
---
# Cold-Start SFT for Reasoning

Cold-Start SFT for Reasoning refers to the initial supervised fine-tuning phase used to bootstrap reasoning capabilities in language models before applying reinforcement learning techniques. This approach serves as the foundation for training reasoning models that can later develop emergent reasoning abilities through reinforcement learning optimization.

## Overview

Cold-Start SFT represents the first stage in a multi-phase training pipeline for reasoning models. Rather than attempting to train reasoning capabilities from scratch using only reinforcement learning, this method begins with [[Supervised Fine-Tuning (SFT)]] on structured reasoning traces to establish basic reasoning patterns before transitioning to more advanced training techniques. ^[chatgpt-reasoning-llms.md]

The approach is particularly important because reasoning capability is not simply a matter of having "more data" but emerges from a combination of exploration, reward shaping, longer trajectories, verification loops, and policy optimization. Cold-Start SFT provides the initial structure that enables these more sophisticated training methods to be effective. ^[chatgpt-reasoning-llms.md]

## Training Pipeline Integration

Cold-Start SFT typically fits into a four-stage post-training pipeline for reasoning models:

1. **Pretrain base model** - Standard language model pretraining
2. **Cold-Start SFT on reasoning traces** - Initial supervised fine-tuning phase
3. **RL reasoning optimization** - Reinforcement learning with techniques like [[Group Relative Policy Optimization (GRPO)]] or PPO
4. **Distillation into smaller models** - Knowledge transfer to more efficient models

This structured approach allows models to first learn the format and structure of reasoning before developing the ability to generate novel reasoning paths through reinforcement learning. The cold-start phase teaches structure first, which is essential for the subsequent emergence of reasoning capabilities. ^[chatgpt-reasoning-llms.md]

## Implementation in DeepSeek-R1

The DeepSeek-R1 model provides a concrete example of Cold-Start SFT implementation. To prevent the early unstable cold start phase of RL training from the base model, researchers construct and collect a small amount of long chain-of-thought data to fine-tune the model as the initial RL actor. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

### Data Collection Methods

There are several approaches for collecting cold-start data for reasoning-oriented SFT:

#### Synthetic Generation
Prompting existing models (such as base language models) to produce long [[chain-of-thought-reasoning]] data, either through few-shot examples or by instructing the model to generate detailed answers with accompanying reflection and verification steps. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

#### Human Post-Processing
Using advanced reasoning models to generate large numbers of reasoning trajectories, then having humans post-process and select the highest quality outputs for training data. This approach combines automated generation with human quality control. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

#### Hybrid Approaches
Combining multiple data collection methods to create diverse training datasets that include thousands of cold-start examples covering various reasoning patterns and problem types. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

## Training Process

The Cold-Start SFT phase involves training the base model on carefully curated long chain-of-thought examples. This data serves as a seed for the subsequent RL training process, where the model begins its self-exploration by matching the style of the SFT training data. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

The training data introduces a human prior into the model's learning process, allowing researchers to explicitly select the style and pattern of reasoning from which the model learns. For example, the data can be structured to include summaries of each long chain-of-thought, teaching the model to summarize its entire reasoning process prior to providing its final answer. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

## Benefits and Necessity

Cold-Start SFT provides several key advantages in reasoning model training:

- **Eliminates instability** during the initial phases of RL training
- **Speeds up training** by providing a better starting point for exploration
- **Improves model quality** through structured reasoning patterns
- **Provides better priors** for the RL optimization process

While not completely necessary (as demonstrated by DeepSeek-R1-Zero's pure RL approach), Cold-Start SFT is practically useful when high-quality reasoning data is available. ^[demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md]

## Industry Adoption

Very few teams truly train reasoning from zero using only reinforcement learning. Most successful reasoning systems follow the pattern of starting with Cold-Start SFT before moving to reinforcement learning optimization. This staged approach has become the industry standard for developing reasoning capabilities in language models. ^[chatgpt-reasoning-llms.md]

The trend in the industry is toward distilled, reinforced, verifier-trained, and heavily scaffolded systems rather than training reasoning models completely from scratch. Cold-Start SFT serves as the critical foundation that enables these more advanced techniques to be effective. ^[chatgpt-reasoning-llms.md]

## Relationship to Chain-of-Thought Training

Cold-Start SFT often involves training on [[chain-of-thought-reasoning]] traces, where models learn to generate step-by-step reasoning processes. This supervised phase teaches the model the structure of reasoning before more advanced techniques like [[Group Relative Policy Optimization (GRPO)]] are applied to encourage the emergence of novel reasoning capabilities. ^[chatgpt-reasoning-llms.md]

## Practical Implementation

The most effective implementations of Cold-Start SFT focus on teaching reasoning structure first, before moving to more complex training phases. This approach has proven more successful than attempting to train reasoning capabilities entirely through reinforcement learning from the beginning. ^[chatgpt-reasoning-llms.md]

Modern reasoning model tutorials and implementations, including those based on DeepSeek-R1 methodology, typically incorporate Cold-Start SFT as a foundational component before applying reinforcement learning techniques for reasoning emergence. The approach is considered essential for establishing the basic patterns that enable more sophisticated reasoning to develop through subsequent training phases. ^[chatgpt-reasoning-llms.md]
