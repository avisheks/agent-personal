---
title: "cross-domain-interference-in-sft"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:37:10.565915+00:00
updatedAt: 2026-05-18T18:37:10.565915+00:00
---
# Cross-Domain Interference in SFT

Cross-domain interference in [[Supervised Fine-Tuning (SFT)]] refers to the phenomenon where training data from one domain negatively impacts model performance in another domain during multi-task fine-tuning. This interference occurs when models attempt to learn multiple abilities simultaneously, leading to degraded performance compared to single-domain training.

## Mechanism and Causes

Cross-domain interference emerges when different types of SFT data are mixed during training. The interference is particularly pronounced when models are trained on heterogeneous domains such as mathematical reasoning, code generation, and general instruction following simultaneously. As data quantities grow, interference becomes more problematic: additional data from unrelated domains can behave as noise, degrading the in-domain generalization of each ability type. ^[supervised-fine-tuning-sft.md]

The underlying cause relates to conflicting optimization signals across domains. Different abilities demonstrate distinct scaling laws and data requirements, creating tension when trained together. Mathematical reasoning and code generation abilities improve monotonically with in-domain data, while general human-aligned abilities saturate quickly with minimal data. ^[supervised-fine-tuning-sft.md]

## Impact on Model Performance

Multi-task mixing during SFT can significantly impair general ability performance due to cross-domain interference. When code, math, and general response data are trained simultaneously, models often experience degraded performance compared to domain-specific training approaches. ^[supervised-fine-tuning-sft.md]

Experimental evidence shows that naive multi-task approaches consistently underperform compared to strategic training methods. For example, in LLaMA-7B experiments, multi-task training achieved 47.53 on GSM8K math tasks compared to 49.10 for math-only training, demonstrating clear interference effects. ^[supervised-fine-tuning-sft.md]

## Data Quantity vs Composition Effects

The absolute amount of data for each domain dominates the effect of composition ratio in determining interference patterns. Provided each skill receives sufficient examples, the fraction of each type in the mix becomes secondary. Sharp deterioration occurs only when particular domains become severely underrepresented in the training mixture. ^[supervised-fine-tuning-sft.md]

In low-resource settings, mixing different ability data can lead to synergistic transfer and improved multi-task performance. However, as data quantities grow, interference emerges where additional data from unrelated domains behaves as noise, degrading in-domain generalization. ^[supervised-fine-tuning-sft.md]

## Relationship to Catastrophic Forgetting

Cross-domain interference is closely related to [[Catastrophic Forgetting in Fine-Tuning]], but represents a distinct phenomenon. While catastrophic forgetting involves the complete overwriting of previously learned abilities, cross-domain interference occurs during simultaneous multi-domain training and manifests as reduced performance across all domains rather than complete loss of specific abilities. ^[supervised-fine-tuning-sft.md]

## Representation Geometry Analysis

T-SNE visualization reveals that mathematical reasoning queries maintain more distinct representation geometry compared to code or general abilities, which remain more entangled. This geometric analysis explains the observed interference patterns, with math abilities showing greater resistance to interference due to their more distinct representational structure. ^[supervised-fine-tuning-sft.md]

## Mitigation Strategies

### Dual-Stage Mixed Fine-Tuning

The primary solution to cross-domain interference is [[Dual-Stage Mixed Fine-Tuning (DMT)]], which addresses interference through strategic training sequencing:

- **Stage 1**: Fine-tune exclusively on specialized skills (math and code) to consolidate high performance in those areas
- **Stage 2**: Fine-tune on general ability data plus a small proportion of specialized data as rehearsal to prevent overwriting

This approach preserves high performance across all abilities while avoiding the interference patterns of naive multi-task training. ^[supervised-fine-tuning-sft.md]

### Data Composition Management

Careful management of data composition helps minimize interference effects. The strategy involves:

- Ensuring sufficient absolute quantities of data for each domain
- Avoiding severe underrepresentation of any particular domain
- Prioritizing volume for code and math abilities while focusing on curation for general alignment tasks

^[supervised-fine-tuning-sft.md]

## Experimental Evidence

Extensive experiments demonstrate the reality and impact of cross-domain interference across different model sizes and training configurations:

| Training Strategy | GSM8K (Math) | HumanEval (Code) | MT-Bench (General) |
|------------------|--------------|------------------|-------------------|
| Math only | 49.10 | 6.71 | 2.53 |
| Multi-task | 47.53 | 14.63 | 5.76 |
| DMT (1/256) | 41.92 | 17.68 | 6.08 |

The results show that while multi-task training maintains reasonable performance across domains, it suffers from interference compared to specialized training. DMT successfully balances performance across all abilities. ^[supervised-fine-tuning-sft.md]

## Model Size Dependencies

Cross-domain interference patterns vary with model size. Larger models consistently outperform smaller models across all abilities when provided equal amounts of data, reflecting increased capacity to exploit SFT signals. However, interference effects persist across all model sizes, making strategic training approaches essential regardless of model scale. ^[supervised-fine-tuning-sft.md]

## Implications for Model Development

Cross-domain interference has significant implications for developing multi-ability language models:

- Arbitrary mixing or random sequencing of SFT domains risks losing key abilities, especially in data-rich settings
- Strategic approaches like DMT are essential for practical SFT of models aiming for balanced skill portfolios
- Different abilities require different data investment strategies based on their unique scaling laws

^[supervised-fine-tuning-sft.md]

Understanding and mitigating cross-domain interference is crucial for scaling multi-domain fine-tuning approaches and developing versatile language models that maintain high performance across diverse capabilities without destructive interference patterns.
