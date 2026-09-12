---
title: "Expert-Specific Fine-Tuning (ESFT)"
summary: "A fine-tuning approach for MoE models that selectively trains only task-relevant experts identified through routing analysis, preserving general ability while improving specialized performance."
sources:
  - sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-15T11:20:06.363960+00:00
updatedAt: 2026-06-15T11:20:06.363960+00:00
---
# Expert-Specific Fine-Tuning (ESFT)

**Expert-Specific Fine-Tuning (ESFT)** is a specialized training approach for [[Mixture of Experts (MoE)]] models that selectively updates only the most task-relevant experts rather than training all parameters. This method addresses the unique challenges that arise when fine-tuning sparse MoE architectures, where traditional [[Supervised Fine-Tuning (SFT)]] approaches often fail or degrade performance.

## Core Concept

ESFT operates on the principle that for any given task, only a small subset of experts in a MoE model are actively engaged. The method identifies these task-relevant experts through routing analysis and restricts parameter updates to this subset, preserving the specialization of non-relevant experts while improving performance on the target task. ^[moe-sft-failure-modes.md]

The approach is particularly effective for fine-grained MoE models with many experts (such as 128 experts) compared to coarse-grained models with fewer experts (such as 8 experts). This is because fine-grained models naturally develop more specialized expert functions that can be precisely targeted. ^[moe-sft-failure-modes.md]

## Technical Implementation

### Expert Selection Methods

ESFT employs routing analysis to identify which experts should be updated during training. The primary method is the **ESFT-Token approach**, which selects experts based on their cumulative routing scores with a threshold of top_p=0.1-0.2. This means only experts that collectively handle 10-20% of the most frequent routing decisions are updated during fine-tuning. ^[moe-sft-failure-modes.md]

Random expert selection serves as a baseline but consistently underperforms informed selection by 2.8-20.4 points across various tasks, demonstrating the importance of routing-guided expert identification. ^[moe-sft-failure-modes.md]

### Parameter Targeting Strategy

Unlike dense models where [[Low-Rank Adaptation (LoRA)]] can be applied broadly, MoE models require careful consideration of which parameter types to update. Research indicates that MLP layers in MoE architectures are sparse and don't interact well with [[Parameter-Efficient Fine-Tuning (PEFT)]] methods. Instead, ESFT focuses on attention layers while leaving MLP/expert layers largely unchanged. ^[moe-sft-failure-modes.md]

## Advantages Over Traditional SFT

### Routing Preservation

Traditional SFT on MoE models suffers from **routing disruption**, where training all parameters degrades the specialization of experts not relevant to the target task. ESFT maintains the routing distribution by only updating experts that are naturally engaged by the task data. ^[moe-sft-failure-modes.md]

### Gradient Efficiency

In large MoE models like [[GPT-OSS-120B]] with 128 experts using top-4 routing, each expert receives gradients from only approximately 3% of tokens. With small datasets (5K samples), each expert may see only ~150 effective samples, leading to **gradient dilution**. ESFT concentrates gradient updates on the most relevant experts, improving training efficiency. ^[moe-sft-failure-modes.md]

### Overfitting Mitigation

Sparse MoE models are more prone to overfitting than dense models. By limiting parameter updates to task-relevant experts, ESFT reduces the risk of overfitting while maintaining the model's general capabilities across other domains. ^[moe-sft-failure-modes.md]

## Relationship to Other Training Approaches

### Integration with Reinforcement Learning

ESFT can serve as an effective initialization step before [[Reinforcement Learning from Human Feedback (RLHF)]] or [[Direct Preference Optimization (DPO)]]. The proven pipeline follows a distill-then-RL approach, where ESFT provides the initial capability development that RL methods can then refine for consistency and reliability. ^[moe-sft-failure-modes.md]

### Comparison with Knowledge Distillation

When deciding between ESFT and [[Reasoning Model Distillation]], the choice depends on the base model's existing capabilities. If pass@k scores are low (indicating the capability doesn't exist in the model weights), distillation from a stronger teacher model is preferred. If pass@k scores are high (indicating latent capability), ESFT can effectively surface and improve these existing abilities. ^[moe-sft-failure-modes.md]

## Practical Considerations

### Data Requirements

ESFT requires larger and more diverse datasets compared to dense model fine-tuning. While traditional SFT might work with 5K samples, MoE models typically need 50K+ samples with sufficient task diversity to properly engage the routing mechanisms and provide adequate training signal to selected experts. ^[moe-sft-failure-modes.md]

### Hyperparameter Adjustments

MoE models often require higher learning rates (2e-4 to 5e-4) compared to dense models due to the sparse activation patterns. Additionally, precision considerations become important, as lower precision formats like MXFP4 may limit gradient fidelity for the targeted parameter updates. ^[moe-sft-failure-modes.md]

## Applications and Limitations

ESFT is particularly well-suited for scenarios where task-specific performance improvements are needed without sacrificing the model's general capabilities. However, it requires careful routing analysis and may not be suitable for tasks that require broad activation across many experts or fundamental changes to the model's knowledge base.

The method represents a significant advancement in making MoE architectures more amenable to task-specific fine-tuning, addressing longstanding challenges in training these powerful but complex model architectures.
