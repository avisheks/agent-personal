---
title: "catastrophic-forgetting"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:37:30.288696+00:00
updatedAt: 2026-05-18T18:37:30.288696+00:00
---
# Catastrophic Forgetting

**Catastrophic Forgetting** is a critical challenge in machine learning where neural networks lose previously learned knowledge when trained on new tasks or data. In the context of large language models (LLMs), this phenomenon becomes particularly problematic during fine-tuning processes, where models may overwrite existing capabilities while acquiring new ones.

## Overview

Catastrophic forgetting occurs when a model's parameters are updated to optimize for new training objectives, causing the network to "forget" previously learned patterns and behaviors. This is especially concerning in [[Supervised Fine-Tuning (SFT)]] scenarios where models need to maintain multiple capabilities simultaneously while learning new skills. ^[supervised-fine-tuning-sft.md]

## Manifestation in Fine-Tuning

### Sequential Training Problems

When models undergo sequential training on different abilities, catastrophic forgetting presents significant challenges. In sequential SFT approaches, where models are trained on one ability after another, there is substantial risk that newly trained abilities will overwrite previously learned ones, particularly when task domains overlap semantically. ^[supervised-fine-tuning-sft.md]

Research has shown that in sequential SFT, the last trained ability is preferentially retained, with prior abilities becoming diminished in the absence of proper mixing strategies. ^[supervised-fine-tuning-sft.md]

### Multi-Task Interference

Catastrophic forgetting also manifests through cross-domain interference in multi-task learning scenarios. When training on multiple abilities simultaneously (such as code generation, mathematical reasoning, and general instruction following), models can experience performance degradation in some domains due to conflicting optimization signals. Multi-task mixing can impair general abilities due to cross-domain interference between different skill domains. ^[supervised-fine-tuning-sft.md]

## Mitigation Strategies

### Dual-Stage Mixed Fine-Tuning

One of the most effective approaches to combat catastrophic forgetting is the [[Dual-Stage Mixed Fine-Tuning (DMT)]] strategy, which operates in two distinct phases:

1. **Stage 1**: Fine-tune exclusively on specialized skills (such as math and code), consolidating high performance in those specific areas
2. **Stage 2**: Fine-tune on general ability data while including a small proportion of specialized data as a rehearsal mechanism

This rehearsal mechanism prevents the overwriting of previously learned capabilities by maintaining exposure to earlier training domains. The rehearsal parameter (k) is typically set to a small fraction, such as 1/256, to balance retention with new learning. ^[supervised-fine-tuning-sft.md]

### Data Mixing Approaches

Strategic data composition can help mitigate catastrophic forgetting through careful management of training data proportions. Research demonstrates that when the rehearsal parameter (k) in DMT is set to a small, nonzero fraction, performance improvements are observed across all abilities. However, setting this parameter too high shifts the trade-off back towards interference and forgetting. ^[supervised-fine-tuning-sft.md]

The absolute data quantity for each domain is the primary determinant of ability enhancement, rather than the fractional mix ratios. This means that ensuring sufficient examples for each skill domain is more important than achieving perfect proportional balance. ^[supervised-fine-tuning-sft.md]

## Empirical Evidence

Experimental results comparing different training strategies show clear evidence of catastrophic forgetting and the effectiveness of mitigation approaches. Sequential training methods show significant drops in previously learned abilities, while multi-task mixing can impair general abilities due to cross-domain interference. ^[supervised-fine-tuning-sft.md]

DMT strategies successfully preserve high performance across multiple abilities simultaneously. For example, in LLaMA-7B experiments, DMT (1/256) achieved 41.92 on GSM8K math tasks, 17.68 on HumanEval code tasks, and 6.08 on MT-Bench general tasks, outperforming both naive multi-task and sequential methods across all domains. ^[supervised-fine-tuning-sft.md]

### Performance Comparison

| Training Strategy | GSM8K (Math) | HumanEval (Code) | MT-Bench (General) |
|---|---|---|---|
| Sequential | 31.39 | 15.85 | 5.72 |
| Mixed Sequential | 32.60 | 15.24 | 6.02 |
| **DMT (1/256)** | **41.92** | **17.68** | **6.08** |

These results demonstrate that DMT effectively prevents catastrophic forgetting while maintaining strong performance across all evaluated abilities. ^[supervised-fine-tuning-sft.md]

## Representation Geometry Analysis

Extensive t-SNE visualization and ablation studies reveal insights into the underlying mechanisms of catastrophic forgetting. The representation geometry for math queries remains more distinct post-DMT than code or general abilities, which remain more entangled, explaining the observed interference patterns between different skill domains. ^[supervised-fine-tuning-sft.md]

## Implications for Model Development

Catastrophic forgetting has significant implications for practical LLM development:

- **Training Strategy Design**: Careful composition of SFT data and training order is essential for large-scale, multi-ability LLMs
- **Data Management**: Strategic data allocation is crucial, with absolute quantities per skill being more important than proportional mixing
- **Capability Retention**: Advanced SFT strategies are necessary for multi-ability alignment without destructive interference

The phenomenon underscores that arbitrary mixing or random sequencing of SFT domains risks losing key abilities, especially in data-rich settings. ^[supervised-fine-tuning-sft.md]

## Future Directions

Important open research areas include:

- Extending mitigation frameworks like DMT to additional abilities beyond math and code (such as creative writing and planning)
- Developing dynamic adaptation methods for rehearsal parameters
- Exploring [[Parameter-Efficient Fine-Tuning (PEFT)]] approaches that may be more resistant to catastrophic forgetting
- Investigating parameter-efficient extensions such as adapter-based SFT methods

These directions aim to create more robust training paradigms that can acquire new capabilities without sacrificing existing knowledge. ^[supervised-fine-tuning-sft.md]
