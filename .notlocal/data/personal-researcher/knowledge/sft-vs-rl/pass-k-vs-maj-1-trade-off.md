---
title: "Pass@k vs Maj@1 Trade-off"
summary: "The fundamental tension in language model training between optimizing for single-attempt accuracy (maj@1) versus multi-attempt success rate (pass@k), where different training methods affect these metrics differently."
sources:
  - sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-15T11:23:53.341044+00:00
updatedAt: 2026-06-15T11:23:53.341044+00:00
---
# Pass@k vs Maj@1 Trade-off

The **Pass@k vs Maj@1 Trade-off** refers to a fundamental tension in language model optimization between maximizing the probability of generating at least one correct solution when sampling multiple times (Pass@k) versus maximizing the probability of generating a correct solution on the first attempt (Maj@1). This trade-off has significant implications for model training strategies and deployment considerations.

## Definition and Metrics

**Pass@k** measures the probability that at least one correct solution appears when sampling k responses from a model. It reflects the model's ability to explore the solution space and find correct answers through multiple attempts. **Maj@1** (majority at 1) measures the probability that the model generates a correct response on its first attempt, representing the model's precision and reliability for single-shot inference. ^[sft-vs-rl-for-post-training-llms.md]

## The Core Trade-off

Traditional [[Supervised Fine-Tuning (SFT)]] approaches face a fundamental limitation: they can improve Pass@k or Maj@1, but typically not both simultaneously. SFT suffers from exposure bias and is bounded by demonstration quality, creating a ceiling effect where models cannot exceed the performance of their training data. This creates a trade-off where optimizing for one metric often comes at the expense of the other. ^[sft-vs-rl-for-post-training-llms.md]

## How Reinforcement Learning Breaks the Trade-off

[[Reinforcement Learning from Human Feedback (RLHF)]] and related methods uniquely enable simultaneous improvement in both Pass@k and Maj@1 metrics. Singh et al. (2024) demonstrated that RL approaches can optimize beyond demonstration quality and achieve holistic property optimization that improves both accuracy and diversity simultaneously. This represents a key advantage of RL over traditional SFT approaches. ^[sft-vs-rl-for-post-training-llms.md]

## Training Method Implications

### SFT Limitations
[[Supervised Fine-Tuning (SFT)]] is bounded by the quality of demonstrations and cannot exceed the training data ceiling. The method trades off between Maj@1 and Pass@k performance, requiring practitioners to choose which metric to prioritize during training. ^[sft-vs-rl-for-post-training-llms.md]

### RL Advantages
Methods like [[Group Relative Policy Optimization (GRPO)]] and [[Reinforcement Learning from Human Feedback (RLHF)]] enable exploration beyond the training data distribution. DeepSeek-R1 achieved state-of-the-art performance on math, coding, and STEM tasks by using pure RL training, demonstrating emergent reasoning behaviors that improved both metrics. ^[sft-vs-rl-for-post-training-llms.md]

### DPO Considerations
[[Direct Preference Optimization (DPO)]] faces limitations as an offline method that is bounded by collected data. While more stable than full RLHF, it has been "widely reported significantly inferior to online iterative RLHF" for breaking the Pass@k vs Maj@1 trade-off. ^[sft-vs-rl-for-post-training-llms.md]

## Elicitation Theory Perspective

According to elicitation theory, base models at high Pass@k can solve problems that RL models solve at Pass@1, suggesting that RL redistributes probability mass rather than expanding fundamental capability space. However, DeepSeek-R1-Zero demonstrates that RL can organize latent capabilities into novel reasoning strategies, serving as an amplifier and organizer rather than a teacher. ^[sft-vs-rl-for-post-training-llms.md]

## Industry Applications

The trade-off has practical implications for deployment strategies. Models optimized for high Maj@1 are suitable for single-shot applications where reliability is paramount, while models optimized for high Pass@k are better for scenarios where multiple attempts are feasible and finding any correct solution is valuable. [[Chain-of-Thought Reasoning]] and [[Multi-Step Reasoning]] tasks particularly benefit from approaches that can improve both metrics simultaneously. ^[sft-vs-rl-for-post-training-llms.md]

## Computational Considerations

Breaking the Pass@k vs Maj@1 trade-off typically requires more computational resources. While SFT requires 1x baseline compute, RL methods like RLHF require 4-6x compute due to their multi-model setup. However, this investment enables the simultaneous optimization that SFT cannot achieve. ^[sft-vs-rl-for-post-training-llms.md]
