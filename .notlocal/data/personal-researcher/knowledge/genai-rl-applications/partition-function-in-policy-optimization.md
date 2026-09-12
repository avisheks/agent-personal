---
title: "Partition Function in Policy Optimization"
summary: "A normalization function Z(x) that ensures probability distributions sum to 1 when reweighting reference policies by reward, which cancels out in pairwise comparisons enabling DPO's simplified optimization."
sources:
  - genai-rl-applications/simplifying-alignment-from-rlhf-to-direct-preference-optimization-dpo.md
createdAt: 2026-05-22T12:09:48.109969+00:00
updatedAt: 2026-05-22T12:09:48.109969+00:00
---
# Partition Function in Policy Optimization

The **partition function** is a mathematical construct used in policy optimization that serves as a normalization constant when reweighting probability distributions based on reward signals. In the context of language model alignment, the partition function enables the transformation from reinforcement learning-based approaches to direct optimization methods by providing a way to express optimal policies in closed form.

## Mathematical Definition

The partition function Z(x) is defined as:

Z(x) = ∑_y π_ref(y|x) exp[r(x,y)/β]

Where:
- π_ref(y|x) is the reference policy (typically from [[Supervised Fine-Tuning (SFT)]])
- r(x,y) is the reward function learned during [[Reinforcement Learning from Human Feedback (RLHF)]]
- β is a temperature parameter controlling the strength of the reward signal
- The sum is taken over all possible outputs y for a given input x ^[rlhf-to-dpo.md]

## Role in Policy Reweighting

The partition function enables the expression of an optimal policy π(y|x) in terms of the reference policy and reward function:

π(y|x) = (1/Z(x)) π_ref(y|x) exp[r(x,y)/β]

This formulation shows how the optimal policy can be viewed as a reweighted version of the reference policy, where:
- High-reward outputs receive exponentially higher probability mass
- The partition function Z(x) ensures the distribution remains normalized (probabilities sum to 1)
- The temperature parameter β controls how aggressively the policy shifts toward high-reward regions ^[rlhf-to-dpo.md]

## Cancellation Property in Pairwise Comparisons

A key insight in [[Direct Preference Optimization (DPO)]] is that the partition function cancels out when computing pairwise preference probabilities. For two outputs y₁ and y₂, the preference probability becomes:

p(y₁ > y₂|x) = σ(r(x,y₁) - r(x,y₂))

This cancellation occurs because both outputs share the same input x and therefore the same partition function Z(x). This mathematical property eliminates the need to explicitly compute Z(x), which would otherwise require summing over all possible outputs—a computationally intractable operation for large vocabulary language models. ^[rlhf-to-dpo.md]

## Computational Advantages

The partition function's cancellation property provides several computational benefits:

1. **Eliminates Intractable Summation**: Computing Z(x) exactly would require evaluating the reward function for every possible output sequence, which is computationally prohibitive for language models with large vocabularies.

2. **Enables Direct Optimization**: By working with ratios of probabilities rather than absolute probabilities, DPO can optimize policies directly without requiring reinforcement learning algorithms.

3. **Simplifies Implementation**: The mathematical simplification reduces the complexity of the optimization pipeline compared to traditional [[Reinforcement Learning from Human Feedback (RLHF)]] approaches. ^[rlhf-to-dpo.md]

## Connection to Statistical Mechanics

The partition function formulation draws from statistical mechanics, where similar constructs are used to describe probability distributions over system states. In the context of policy optimization:
- The reward function r(x,y) plays the role of negative energy
- The temperature parameter β controls the "sharpness" of the distribution
- Higher rewards correspond to lower energy states that are more probable ^[rlhf-to-dpo.md]

## Implications for Model Alignment

The partition function framework provides theoretical justification for why [[Direct Preference Optimization (DPO)]] can achieve similar alignment results to [[Reinforcement Learning from Human Feedback (RLHF)]] while avoiding the computational overhead of reinforcement learning. By expressing the optimal policy in terms of the partition function and then exploiting its cancellation properties, DPO maintains the theoretical grounding of RLHF while significantly simplifying the optimization process. ^[rlhf-to-dpo.md]
