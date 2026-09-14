---
title: "multi-ability-sft-strategy"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:37:48.986154+00:00
updatedAt: 2026-05-18T18:37:48.986154+00:00
---
# Multi-Ability SFT Strategy

Multi-Ability SFT Strategy refers to training approaches designed to optimize large language models across multiple distinct capabilities simultaneously through [[Supervised Fine-Tuning (SFT)]]. These strategies address the fundamental challenge of learning diverse skills—such as mathematical reasoning, code generation, and general instruction following—without experiencing [[Catastrophic Forgetting in Fine-Tuning]] or cross-domain interference. ^[supervised-fine-tuning-sft.md]

## Core Challenges

### Ability-Dependent Scaling Patterns

Different capabilities exhibit distinct scaling behaviors during SFT. Mathematical reasoning and code generation abilities improve monotonically and robustly as the amount of in-domain SFT data increases, with scaling curves that are often log-linear and unbounded within practical data volumes. In contrast, general human-aligned abilities such as instruction following show rapid improvement with as little as 1,000 samples but quickly saturate, with additional data yielding negligible gains beyond this point. ^[supervised-fine-tuning-sft.md]

### Cross-Domain Interference

Multi-task mixing—training on code, math, and general responses simultaneously—can impair general ability performance due to cross-domain interference. Sequential SFT, where models are trained on one ability after another, risks catastrophic forgetting, where newly trained abilities overwrite previously learned ones, particularly when task domains overlap semantically. ^[supervised-fine-tuning-sft.md]

## Data Composition Principles

### Quantity vs. Composition Trade-offs

The amount of data for a given domain dominates the effect of composition ratio. Provided each skill receives a sufficient number of examples, the fraction of each type in the mix is secondary, with sharp deterioration occurring only when particular domains become underrepresented. Data composition experiments reveal that mixing SFT data types is especially beneficial in low-resource settings, where different ability data leads to synergistic transfer and improved multi-task performance. ^[supervised-fine-tuning-sft.md]

### Model Size Dependencies

Scaling experiments across model sizes reveal that larger models consistently outperform smaller models across all abilities when provided equal amounts of data, reflecting increased capacity to exploit SFT signals. This advantage becomes more pronounced as data volumes grow. However, in extremely low-data regimes, smaller models sometimes outperform due to large-model overfitting, though this advantage vanishes rapidly with additional data. ^[supervised-fine-tuning-sft.md]

## Dual-Stage Mixed Fine-Tuning (DMT)

The [[Dual-Stage Mixed Fine-Tuning (DMT)]] strategy represents an advanced approach to multi-ability SFT that effectively mitigates both catastrophic forgetting and cross-domain interference. ^[supervised-fine-tuning-sft.md]

### Two-Stage Process

**Stage 1** involves fine-tuning exclusively on specialized skills such as math and code, consolidating high performance in those areas. **Stage 2** fine-tunes on general ability data plus a small proportion (k, e.g., 1/256) of specialized data, which acts as a rehearsal mechanism to prevent the overwriting of code and math capabilities by general alignment training. ^[supervised-fine-tuning-sft.md]

### Performance Results

Quantitative results demonstrate that DMT preserves high performance across all abilities, outperforming both naive multi-task and sequential methods. For example, with a 7B parameter model, DMT (1/256) achieves 41.92 on GSM8K math tasks, 17.68 on HumanEval code tasks, and 6.08 on MT-Bench general tasks, compared to mixed sequential training which achieves 32.60, 15.24, and 6.02 respectively. ^[supervised-fine-tuning-sft.md]

## Implementation Considerations

### Rehearsal Parameter Tuning

Performance boosts on all abilities are observed when the rehearsal parameter k in DMT is set to a small, nonzero fraction. Setting k too high shifts the trade-off back towards interference and forgetting, while k=0 leads to catastrophic forgetting of specialized abilities. ^[supervised-fine-tuning-sft.md]

### Representation Geometry

Extensive analysis reveals that the representation geometry for math queries remains more distinct post-DMT than code or general abilities, which remain more entangled, explaining the observed interference patterns. This geometric separation supports the effectiveness of the DMT approach in maintaining distinct capability domains. ^[supervised-fine-tuning-sft.md]

## Strategic Recommendations

### Domain-Specific Data Investment

For general abilities that saturate with only a few thousand examples, further scaling up data quantity is inefficient, and targeted, high-quality curation is advised. For mathematical reasoning and code generation, continuous scaling of in-domain examples brings continual improvements, suggesting different data investment strategies for different capability types. ^[supervised-fine-tuning-sft.md]

### Training Order Management

Data mixing should be managed with respect to absolute quantities per skill, as arbitrary mixing or random sequencing of SFT domains risks losing key abilities, especially in data-rich settings. In sequential SFT, the last trained ability is preferentially retained, with prior abilities diminished in the absence of mixing. ^[supervised-fine-tuning-sft.md]

## Future Directions

Important open areas include extending the DMT framework to acquisition of additional abilities such as creative writing and planning, dynamic adaptation of the rehearsal parameter, and [[Parameter-Efficient Fine-Tuning (PEFT)]] extensions such as adapter-based SFT approaches. ^[supervised-fine-tuning-sft.md]
