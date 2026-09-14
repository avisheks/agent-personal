---
title: "Elicitation Theory in Post-Training"
summary: "The theoretical framework suggesting that post-training techniques like RL primarily redistribute probability mass and organize existing capabilities rather than creating fundamentally new abilities in language models."
sources:
  - sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-15T11:22:10.227150+00:00
updatedAt: 2026-06-15T11:22:10.227150+00:00
---
# Elicitation Theory in Post-Training

**Elicitation Theory in Post-Training** refers to the theoretical framework that post-training methods like [[Reinforcement Learning from Human Feedback (RLHF)]] and [[Direct Preference Optimization (DPO)]] primarily elicit and reorganize existing capabilities within pre-trained language models rather than creating fundamentally new abilities. This theory challenges the assumption that post-training methods teach models novel skills, instead proposing they redistribute probability mass to surface latent knowledge already present in the base model. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Core Theoretical Framework

The elicitation interpretation suggests that "RLVR does not generate fundamentally new reasoning abilities beyond what already exists in the base model." Research demonstrates that base models at high pass@k can solve the same problems that post-trained models solve at pass@1, indicating that the underlying capabilities were already present but not easily accessible through standard sampling. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

This framework positions [[Reinforcement Learning from Human Feedback (RLHF)]] and related methods as amplifiers and organizers rather than teachers. The methods serve to reorganize existing latent capabilities into more coherent and accessible reasoning strategies, rather than expanding the fundamental capability space of the model. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Evidence Supporting Elicitation Theory

### Capability Redistribution

Base models demonstrate that capabilities exist in latent form before post-training. When evaluated with high sampling budgets (pass@k), pre-trained models can solve problems that appear beyond their reach when using standard sampling methods. This suggests that post-training methods primarily change how probability mass is distributed across possible outputs rather than creating new knowledge. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

### Emergent Organization

[[DeepSeek R1 Reasoning Model]] provides evidence that [[Reinforcement Learning from Human Feedback (RLHF)]] can organize latent capabilities into novel reasoning strategies. The model demonstrates emergent reasoning behaviors that appear from pure RL training, suggesting that while fundamental capabilities may be pre-existing, their organization and accessibility can be dramatically improved through post-training. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Implications for Post-Training Methods

### Supervised Fine-Tuning Limitations

[[Supervised Fine-Tuning (SFT)]] faces inherent limitations under elicitation theory, as it is bounded by demonstration quality and cannot exceed the training data ceiling. The method suffers from exposure bias and requires expensive expert demonstrations, making it insufficient for accessing the full range of latent capabilities in base models. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

### Reinforcement Learning Advantages

[[Reinforcement Learning from Human Feedback (RLHF)]] methods can optimize beyond demonstration quality and enable holistic property optimization. These approaches can simultaneously improve both accuracy (maj@1) and diversity (pass@96), unlocking capabilities that SFT alone cannot access. The methods excel at exploration beyond the training data distribution and optimization of evaluator-defined properties. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Practical Applications

### Self-Correction Capabilities

Elicitation theory explains why RL methods like SCoRe show 15.6% improvement on mathematical reasoning tasks compared to SFT. The theory suggests that self-correction abilities exist latently in base models but require RL training to become accessible and reliable. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

### [[Chain-of-Thought Reasoning]]

Long [[Chain-of-Thought Reasoning]] with backtracking capabilities emerge through RL training, supporting the elicitation framework. These reasoning patterns appear to be latent in base models but require specific training approaches to surface and organize effectively. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Limitations and Counterevidence

While elicitation theory provides a compelling framework, some evidence suggests post-training may create genuinely new capabilities. [[DeepSeek R1 Reasoning Model]] demonstrates reasoning strategies that may represent novel organizational patterns rather than simple redistribution of existing knowledge. The theory continues to evolve as researchers investigate the boundaries between capability elicitation and genuine capability creation. ^[sft-vs-rl-for-post-training-llms-comprehensive-comparison.md]

## Related Concepts

- [[Reinforcement Learning from Human Feedback (RLHF)]]
- [[Direct Preference Optimization (DPO)]]
- [[Supervised Fine-Tuning (SFT)]]
- [[Chain-of-Thought Reasoning]]
- [[DeepSeek R1 Reasoning Model]]
