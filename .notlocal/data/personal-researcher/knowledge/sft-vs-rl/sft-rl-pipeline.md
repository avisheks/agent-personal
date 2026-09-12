---
title: "SFT-RL Pipeline"
summary: "The industry-standard approach where Supervised Fine-Tuning provides strong initialization followed by Reinforcement Learning optimization, used by major AI companies like OpenAI, Meta, Anthropic, and DeepSeek."
sources:
  - sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-15T11:23:38.454183+00:00
updatedAt: 2026-06-15T11:23:38.454183+00:00
---
# SFT-RL Pipeline

The **SFT-RL Pipeline** is the industry-standard approach for post-training large language models, combining [[Supervised Fine-Tuning (SFT)]] as an initialization phase followed by [[Reinforcement Learning from Human Feedback (RLHF)]] or other RL methods for optimization. This two-stage approach has been adopted by major AI companies including OpenAI, Meta, Anthropic, and DeepSeek to achieve state-of-the-art performance in language model alignment and capability enhancement. ^[sft-vs-rl-for-post-training-llms.md]

## Pipeline Architecture

The SFT-RL pipeline consists of two sequential phases that address different aspects of model training:

### Stage 1: Supervised Fine-Tuning
[[Supervised Fine-Tuning (SFT)]] serves as the foundation phase, using next-token prediction on high-quality demonstrations. This stage provides format learning, style transfer, and establishes a strong baseline for the model's behavior patterns. SFT requires 10K-100K demonstration examples and operates at 1x baseline compute cost. ^[sft-vs-rl-for-post-training-llms.md]

### Stage 2: Reinforcement Learning
The RL phase optimizes beyond demonstration quality using various methods including [[Reinforcement Learning from Human Feedback (RLHF)]], [[Direct Preference Optimization (DPO)]], or [[Group Relative Policy Optimization (GRPO)]]. This stage enables holistic property optimization and can improve both accuracy and diversity simultaneously, something SFT alone cannot achieve. ^[sft-vs-rl-for-post-training-llms.md]

## Why Both Stages Are Necessary

SFT alone is bounded by demonstration quality and cannot exceed the training data ceiling. It suffers from exposure bias and trades off between maj@1 and pass@96 performance. RL methods, while capable of optimization beyond demonstrations, require a strong initialization to be effective and stable. ^[sft-vs-rl-for-post-training-llms.md]

The combination unlocks capabilities that neither approach can achieve independently:
- Simultaneous accuracy and diversity improvement
- Self-correction abilities beyond training data distribution
- Long [[Chain-of-Thought Reasoning]] with backtracking
- Optimization of evaluator-defined properties like safety and helpfulness ^[sft-vs-rl-for-post-training-llms.md]

## Industry Implementations

### OpenAI InstructGPT
The landmark InstructGPT implementation demonstrated that a 1.3B parameter model trained with the SFT-RL pipeline was preferred over the much larger 175B parameter GPT-3 base model, establishing the effectiveness of this approach. ^[sft-vs-rl-for-post-training-llms.md]

### Anthropic Constitutional AI
Anthropic's [[Constitutional AI]] framework uses the SFT-RL pipeline with [[Constitutional AI (CAI)]] principles, achieving harmlessness without requiring human harm labels in the training data. ^[sft-vs-rl-for-post-training-llms.md]

### DeepSeek-R1
[[DeepSeek-R1 Model]] represents a pure RL approach following SFT initialization, producing emergent reasoning behaviors and achieving state-of-the-art performance on mathematical and coding tasks. The model demonstrates how RL can organize latent capabilities into novel reasoning strategies. ^[sft-vs-rl-for-post-training-llms.md]

### Meta Llama 3.1
Meta's implementation uses an iterative pipeline: SFT → Rejection Sampling → [[Direct Preference Optimization (DPO)]], showing how multiple RL techniques can be combined within the overall framework. ^[sft-vs-rl-for-post-training-llms.md]

## Compute and Resource Requirements

The pipeline has different computational demands for each stage:

| Stage | Relative Compute | Models in Memory | Data Requirements |
|-------|-----------------|------------------|-------------------|
| SFT | 1x (baseline) | 1 | 10K-100K demonstrations |
| RLHF/PPO | 4-6x | 4 (policy, reference, reward, value) | ~50K preference pairs |
| DPO | 1.5-2x | 2 (policy + reference) | 10K-100K preference pairs |
| GRPO | 2-3x | 1 + sampling overhead | Unlimited (self-generated) |

^[sft-vs-rl-for-post-training-llms.md]

## Limitations and Challenges

### Training Instability
RL methods in the pipeline can suffer from reward hacking, overoptimization, and mode collapse without proper regularization techniques like KL divergence penalties. ^[sft-vs-rl-for-post-training-llms.md]

### Length Bias
Some RLHF improvements have been found to be "largely driven by increasing response length" rather than genuine quality improvements, requiring careful reward model design. ^[sft-vs-rl-for-post-training-llms.md]

### Elicitation vs Generation
Research suggests that RL methods primarily redistribute probability mass rather than generating fundamentally new capabilities, serving as amplifiers and organizers of existing model knowledge rather than teachers of new skills. ^[sft-vs-rl-for-post-training-llms.md]

## Alternative Approaches

While the SFT-RL pipeline remains the industry standard, alternative methods include:
- SFT-only approaches for well-defined tasks with abundant demonstrations
- Pure RL methods like DeepSeek-R1-Zero for specific reasoning tasks
- [[Constitutional AI]] for reducing human annotation requirements
- Self-rewarding systems that iterate on their own feedback ^[sft-vs-rl-for-post-training-llms.md]

The choice between approaches depends on task requirements, available data, computational budget, and desired model capabilities.
