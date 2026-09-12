---
title: "Reinforcement Finetuning (RFT)"
summary: "The newest type of post-training that uses reinforcement learning to boost performance on verifiable domains, particularly for reasoning tasks with clear correctness criteria."
sources:
  - genai-rl-applications/2504.md
createdAt: 2026-05-24T12:46:23.022558+00:00
updatedAt: 2026-05-24T12:46:23.022558+00:00
---
# Reinforcement Finetuning (RFT)

**Reinforcement Finetuning (RFT)** is the newest type of post-training optimization method for language models that focuses on boosting performance on verifiable domains through reinforcement learning techniques. RFT represents an evolution beyond traditional preference finetuning, targeting specific capabilities that can be objectively measured and verified. ^[2504.md]

## Overview

RFT is one of three main optimization methods used in modern post-training, alongside [[Supervised Fine-Tuning (SFT)]] and preference finetuning. While instruction tuning teaches formatting and basic instruction-following abilities, and preference finetuning aligns models to human preferences and style, RFT specifically targets performance improvements on tasks where success can be objectively verified. ^[2504.md]

The technique builds extensively on the infrastructure and ideas developed for [[Reinforcement Learning from Human Feedback (RLHF)]], but evolves much faster due to its focus on domains with clear success metrics rather than subjective human preferences. ^[2504.md]

## Key Characteristics

### Verifiable Domains
RFT is particularly effective in domains where the correctness of outputs can be automatically verified, such as:
- Mathematical reasoning problems
- Code generation and execution
- Logic puzzles and formal reasoning tasks

This focus on verifiable domains allows for more reliable reward signals compared to subjective preference data. ^[2504.md]

### Relationship to Reasoning Models
RFT has become closely associated with the development of reasoning models, such as OpenAI's o1 and similar systems. These models demonstrate how reinforcement learning can be applied to improve step-by-step reasoning capabilities, often involving [[Chain-of-Thought Reasoning]] processes. ^[2504.md]

The success of reasoning models has shown that RFT can enable substantial performance improvements on challenging benchmarks when applied to domains with clear verification criteria. ^[2504.md]

## Training Process

### Multi-Stage Approach
Modern RFT implementations typically involve multiple training stages, as demonstrated in models like DeepSeek R1:

1. **Cold-start training** with filtered reasoning samples
2. **Large-scale reinforcement learning** on reasoning problems  
3. **[[Rejection Sampling]]** on mixed reasoning and general queries
4. **Mixed reinforcement learning** combining verifiable rewards with general preference tuning

This multi-stage approach allows models to develop strong reasoning capabilities while maintaining general-purpose functionality. ^[2504.md]

### Integration with Other Methods
RFT is often combined with other post-training techniques:
- Initial [[Supervised Fine-Tuning (SFT)]] to establish basic capabilities
- [[Reward Modeling]] for domains where verification is possible
- Traditional preference finetuning for general interaction quality

## Technical Implementation

### Reward Signals
Unlike traditional RLHF which relies on human preference data, RFT can utilize:
- **[[Outcome Reward Models]]** that predict correctness of final answers
- **[[Process Reward Models]]** that evaluate intermediate reasoning steps
- Direct verification against ground truth in mathematical or logical domains

### Optimization Challenges
RFT faces similar optimization challenges to other RL-based approaches:
- Need for careful [[Regularization]] to prevent over-optimization
- Balancing performance on target domains with general capabilities
- Managing the computational cost of iterative RL training

## Current Applications

### Reasoning Models
The most prominent application of RFT has been in developing reasoning models that can:
- Solve complex mathematical problems
- Perform multi-step logical reasoning
- Generate and verify their own reasoning chains

### Domain-Specific Enhancement
RFT has shown particular promise for enhancing model performance in:
- Mathematical problem solving (AIME, competition mathematics)
- Code generation and debugging
- Scientific reasoning tasks

## Future Directions

RFT represents a rapidly evolving area of research, with ongoing development in:
- Scaling to larger and more diverse reasoning domains
- Integration with inference-time scaling techniques
- Development of better verification methods for complex reasoning tasks

The field continues to build on the foundational work in [[Reinforcement Learning from Human Feedback (RLHF)]] while pushing toward more objective and verifiable optimization targets. ^[2504.md]

## See Also

- [[Supervised Fine-Tuning (SFT)]]
- [[Reinforcement Learning from Human Feedback (RLHF)]]
- [[Chain-of-Thought Reasoning]]
- [[Outcome Reward Models]]
- [[Process Reward Models]]
- [[Rejection Sampling]]
