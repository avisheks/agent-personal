---
title: "ST-MoE Freezing Paradox"
summary: "The counterintuitive finding that freezing MoE layers while updating other parameters works almost as well as full fine-tuning, while updating only MoE layers causes significant performance drops."
sources:
  - sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-15T11:21:32.078393+00:00
updatedAt: 2026-06-15T11:21:32.078393+00:00
---
# ST-MoE Freezing Paradox

The **ST-MoE Freezing Paradox** is a counterintuitive phenomenon observed in [[Mixture of Experts (MoE)]] architectures during [[Supervised Fine-Tuning (SFT)]], where freezing the MoE layers and updating all other parameters performs almost as well as updating all parameters, while updating only the MoE layers causes significant performance degradation. ^[moe-sft-failure-modes.md]

## Overview

The paradox challenges conventional wisdom about fine-tuning [[Mixture of Experts (MoE)]] models, revealing that the sparse expert layers may not be the primary drivers of task-specific adaptation despite being the most distinctive architectural component of MoE systems. ^[moe-sft-failure-modes.md]

## The Paradox Explained

### Core Observation

In traditional dense models, freezing the majority of parameters while fine-tuning only a subset typically leads to substantial performance drops. However, in MoE architectures, the opposite pattern emerges:

- **Freezing MoE layers + updating everything else**: Performance remains nearly equivalent to full parameter updates
- **Updating only MoE layers**: Results in significant performance degradation
- **Full parameter updates**: Achieves best performance but may disrupt expert specialization ^[moe-sft-failure-modes.md]

### Implications for Fine-Tuning Strategy

This paradox suggests that the attention layers and other non-expert components carry more responsibility for task adaptation than previously understood. The MoE layers appear to maintain their pre-trained routing and expert specialization patterns, while task-specific learning occurs primarily in the shared components. ^[moe-sft-failure-modes.md]

## Related Phenomena

### Routing Disruption

The paradox is closely related to routing disruption issues in MoE fine-tuning. Training all parameters can degrade the specialization of non-relevant experts, as the routing distribution for specific tasks is typically concentrated in only 5-15% of available experts. ^[moe-sft-failure-modes.md]

### Expert-Specific Fine-Tuning (ESFT)

The [[ESFT]] approach addresses the paradox by selectively training only task-relevant experts identified through routing analysis, preserving general capabilities while improving specialized performance. This method shows that fine-grained models with more experts (such as 128 experts) are more suitable for selective expert training than coarse-grained models. ^[moe-sft-failure-modes.md]

## Practical Implications

### Training Recommendations

Based on the ST-MoE Freezing Paradox, practitioners should:

- Target attention layers rather than MLP/expert layers during fine-tuning
- Consider freezing MoE layers when computational resources are limited
- Use expert-specific training methods when full parameter updates are necessary
- Avoid updating only MoE layers without corresponding updates to other components ^[moe-sft-failure-modes.md]

### Architecture Considerations

The paradox highlights the importance of understanding parameter roles in MoE architectures, where the routing mechanism and expert specialization may be more fragile than the shared attention and embedding layers. ^[moe-sft-failure-modes.md]

## See Also

- [[Mixture of Experts (MoE)]]
- [[Supervised Fine-Tuning (SFT)]]
- [[Parameter-Efficient Fine-Tuning (PEFT)]]
- [[Low-Rank Adaptation (LoRA)]]
