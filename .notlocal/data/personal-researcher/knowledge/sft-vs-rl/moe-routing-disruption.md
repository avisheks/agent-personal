---
title: "MoE Routing Disruption"
summary: "The phenomenon where fine-tuning all parameters in MoE models degrades the specialization of non-relevant experts by disrupting the learned routing distribution."
sources:
  - sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-15T11:20:19.576940+00:00
updatedAt: 2026-06-15T11:20:19.576940+00:00
---
# MoE Routing Disruption

**MoE Routing Disruption** refers to the degradation of expert specialization in [[Mixture of Experts (MoE)]] models during [[Supervised Fine-Tuning (SFT)]], where training on task-specific data disrupts the learned routing patterns that direct tokens to appropriate experts. This phenomenon is a primary cause of fine-tuning failures in sparse [[Mixture of Experts (MoE)]] architectures like [[GPT-OSS-120B]]. ^[moe-sft-failure-modes.md]

## Core Mechanism

In MoE models, the routing mechanism learns to send different types of tokens to specialized experts during pre-training. However, when fine-tuning on narrow task-specific datasets, the routing distribution becomes highly concentrated in only 5-15% of available experts. Training all parameters simultaneously causes gradient updates to degrade the specialization of non-relevant experts, leading to overall performance decline rather than improvement. ^[moe-sft-failure-modes.md]

## Technical Manifestations

### Gradient Dilution
With architectures like [[GPT-OSS-120B]]'s top-4 routing across 128 experts, each expert receives gradients from approximately 3% of tokens. At typical fine-tuning scales of 5,000 samples, individual experts see only ~150 effective training examples, which is insufficient for meaningful adaptation while preserving existing capabilities. ^[moe-sft-failure-modes.md]

### Expert Interference
The ESFT paper demonstrates that random expert selection during fine-tuning can degrade performance by 2.8-20.4 points compared to informed selection of task-relevant experts. This occurs because updates to irrelevant experts interfere with their pre-trained specializations without providing compensating benefits for the target task. ^[moe-sft-failure-modes.md]

### MLP Layer Incompatibility
MoE architectures exhibit poor compatibility with parameter-efficient methods like LoRA when applied to MLP layers. The sparse nature of expert activations means these layers "don't interact well with PEFT," requiring different adaptation strategies than dense models. ^[moe-sft-failure-modes.md]

## ESFT Solution Framework

Expert-Specialized Fine-Tuning (ESFT) addresses routing disruption by training only task-relevant experts identified through routing analysis:

- **ESFT-Token method**: Trains experts with top_p=0.1-0.2 of cumulative routing score
- **Preservation principle**: Maintains general capabilities while improving specialized performance
- **Architecture sensitivity**: Fine-grained models (128 experts) show greater suitability for ESFT than coarse-grained models (8 experts)

^[moe-sft-failure-modes.md]

## Comparison with Dense Models

MoE routing disruption represents a fundamental difference from dense model fine-tuning challenges like [[Catastrophic Forgetting in Fine-Tuning]]. While dense models suffer from uniform parameter interference, MoE models face selective expert degradation that can be addressed through targeted training strategies. The ST-MoE research shows that freezing MoE layers while updating other parameters works "almost as well as updating all parameters," highlighting the sensitivity of routing mechanisms. ^[moe-sft-failure-modes.md]

## Practical Implications

### Data Requirements
MoE models require significantly more training data and task diversity than dense models to avoid routing disruption. The concentrated routing patterns mean that insufficient data leads to expert under-utilization and performance degradation. ^[moe-sft-failure-modes.md]

### Precision Considerations
Lower precision formats like MXFP4 may exacerbate routing disruption by limiting gradient fidelity during the fine-tuning process, particularly when combined with parameter-efficient methods. ^[moe-sft-failure-modes.md]

## Related Concepts

MoE routing disruption connects to broader challenges in [[Long-Context Scaling]] and [[Chain-of-Thought Reasoning]], where maintaining expert specialization becomes crucial for complex reasoning tasks. Understanding this phenomenon is essential for effective deployment of large MoE models like [[GPT-OSS-120B]] and [[Qwen3 Language Model]] family architectures.
