---
title: "MLP-LoRA Incompatibility in MoE"
summary: "The finding that LoRA applied to MLP layers in MoE models performs poorly because sparse MLP layers don't interact well with parameter-efficient fine-tuning methods."
sources:
  - sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-15T11:21:05.856775+00:00
updatedAt: 2026-06-15T11:21:05.856775+00:00
---
# MLP-LoRA Incompatibility in MoE

**MLP-LoRA Incompatibility in MoE** refers to the fundamental technical limitation where [[Low-Rank Adaptation (LoRA)]] cannot be effectively applied to the MLP (Multi-Layer Perceptron) layers of [[Mixture-of-Experts-MoE]] architectures. This incompatibility creates significant challenges for [[Parameter-Efficient Fine-Tuning (PEFT)]] of MoE models and contributes to [[Supervised Fine-Tuning (SFT)]] failure modes in sparse architectures.

## Technical Foundation

The incompatibility stems from the sparse activation patterns inherent in MoE architectures. In models like [[GPT-OSS-120B]], which uses 128 experts with top-4 routing, only a small subset of experts are active for any given token. When LoRA adapters are applied to MLP layers, they attempt to modify parameters that may not be consistently activated during training, leading to ineffective adaptation. ^[moe-sft-failure-modes.md]

The HuggingFace Mixtral guidance explicitly states: "one should not target the MLP layers as they are sparse and don't interact well with PEFT." This recommendation reflects the fundamental mismatch between LoRA's dense adaptation approach and the sparse nature of expert layers. ^[moe-sft-failure-modes.md]

## Routing Disruption Effects

When LoRA is applied to MLP layers in MoE models, it can disrupt the carefully learned routing patterns. The ESFT paper demonstrates that routing distribution for specific tasks is highly concentrated in approximately 5-15% of experts. Training all parameters, including non-relevant experts through LoRA adapters, can degrade the specialization of experts that should remain unchanged for the target task. ^[moe-sft-failure-modes.md]

This routing disruption is particularly problematic because MoE models rely on expert specialization for their effectiveness. When LoRA adapters interfere with this specialization, the model's overall performance can degrade rather than improve.

## Gradient Dilution Problem

The sparse activation pattern in MoE architectures creates a gradient dilution effect when combined with LoRA. With top-4 routing out of 128 experts, each expert receives gradients from only approximately 3% of tokens. In scenarios with limited training data (such as 5K samples), each expert may see only around 150 effective samples, which is insufficient for meaningful LoRA adaptation. ^[moe-sft-failure-modes.md]

This gradient dilution is compounded by LoRA's low-rank constraint, which further limits the model's ability to learn from the sparse gradient signals reaching each expert.

## Alternative Approaches

### Attention-Only LoRA

The recommended approach for MoE fine-tuning is to apply LoRA exclusively to attention layers while leaving MLP/expert layers frozen. This strategy preserves expert specialization while allowing the model to adapt its attention patterns to new tasks. ^[moe-sft-failure-modes.md]

### Expert-Specific Fine-Tuning (ESFT)

The ESFT method addresses MLP-LoRA incompatibility by selectively training only task-relevant experts identified through routing analysis. This approach uses the ESFT-Token method to train experts with top_p=0.1-0.2 of cumulative routing score, preserving general ability while improving specialized performance. ^[moe-sft-failure-modes.md]

### Full Parameter Training Considerations

Research shows that freezing MoE layers and updating everything else works "almost as well as updating all parameters," while updating only MoE layers causes "huge performance drop." This finding suggests that the attention layers carry more adaptation capacity than the expert layers in MoE architectures. ^[moe-sft-failure-modes.md]

## Implications for Model Training

The MLP-LoRA incompatibility has several important implications for training MoE models:

- **Data Requirements**: MoE models require significantly more training data and task diversity compared to dense models to overcome the gradient dilution effect. ^[moe-sft-failure-modes.md]

- **Overfitting Susceptibility**: Sparse models are more prone to overfitting than dense models, making the choice of adaptation strategy even more critical. ^[moe-sft-failure-modes.md]

- **Learning Rate Sensitivity**: MoE models may require higher learning rates (2e-4 to 5e-4) to compensate for the reduced gradient flow to individual experts. ^[moe-sft-failure-modes.md]

## Related Concepts

This incompatibility is closely related to other MoE training challenges including [[Catastrophic Forgetting in Fine-Tuning]], expert routing optimization, and the broader challenges of [[Parameter-Efficient Fine-Tuning (PEFT)]] in sparse architectures. Understanding this limitation is crucial for developing effective training strategies for large-scale MoE models like [[GPT-OSS-120B]].
