---
title: "dual-stage-mixed-fine-tuning-dmt"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:36:32.363701+00:00
updatedAt: 2026-05-18T18:36:32.363701+00:00
---
# Dual-Stage Mixed Fine-Tuning (DMT)

**Dual-Stage Mixed Fine-Tuning (DMT)** is an advanced training strategy for [[Supervised Fine-Tuning (SFT)]] that addresses the challenges of [[Catastrophic Forgetting in Fine-Tuning]] and cross-domain interference when training large language models on multiple abilities simultaneously. DMT enables models to acquire and retain diverse capabilities across specialized domains like mathematics and code generation while maintaining general instruction-following abilities. ^[supervised-fine-tuning-sft.md]

## Overview

DMT was developed to solve critical problems that arise when fine-tuning models on multiple skill domains. Traditional approaches to multi-ability training suffer from two main issues: multi-task mixing can impair general abilities due to cross-domain interference, while sequential SFT risks catastrophic forgetting where newly trained abilities overwrite previously learned ones, particularly when task domains overlap semantically. ^[supervised-fine-tuning-sft.md]

## Training Strategy

### Two-Stage Process

DMT employs a carefully structured two-stage approach:

**Stage 1: Specialized Skills Training**
- Fine-tune exclusively on specialized skills such as mathematical reasoning and code generation
- This stage consolidates high performance in technical domains without interference from general alignment data
- Focus on domains that benefit from substantial in-domain data scaling ^[supervised-fine-tuning-sft.md]

**Stage 2: Mixed Training with Rehearsal**
- Fine-tune on general ability data combined with a small proportion (k, typically 1/256) of specialized data from Stage 1
- The small fraction of specialized data acts as a rehearsal mechanism
- This prevents the overwriting of code and math capabilities during general alignment training ^[supervised-fine-tuning-sft.md]

### Key Parameters

The rehearsal fraction k is a critical hyperparameter in DMT. Setting k to a small, nonzero fraction (such as 1/256) provides optimal results. Setting k too high shifts the trade-off back towards interference and forgetting, while k=0 eliminates the rehearsal benefit entirely. ^[supervised-fine-tuning-sft.md]

## Performance Results

Quantitative evaluations demonstrate that DMT consistently outperforms both naive multi-task and sequential fine-tuning methods across multiple model sizes and evaluation benchmarks:

### 7B Parameter Models
- **Math (GSM8K)**: DMT achieves 41.92% vs 32.60% for mixed sequential training
- **Code (HumanEval)**: DMT achieves 17.68% vs 15.24% for mixed sequential training  
- **General (MT-Bench)**: DMT achieves 6.08 vs 6.02 for mixed sequential training ^[supervised-fine-tuning-sft.md]

### 13B Parameter Models
- **Math (GSM8K)**: DMT achieves 46.47% vs 40.48% for mixed sequential training
- **Code (HumanEval)**: DMT achieves 19.50% vs 18.30% for mixed sequential training
- **General (MT-Bench)**: DMT achieves 6.03 vs 5.93 for mixed sequential training ^[supervised-fine-tuning-sft.md]

## Technical Insights

### Representation Geometry

Analysis using t-SNE visualization reveals that mathematical reasoning queries maintain more distinct representation geometry post-DMT compared to code or general abilities, which remain more entangled. This explains the observed interference patterns between different skill domains. ^[supervised-fine-tuning-sft.md]

### Sequential Training Effects

In sequential SFT without rehearsal mechanisms, the last trained ability is preferentially retained while prior abilities are diminished. This demonstrates the importance of the rehearsal component in DMT's second stage. ^[supervised-fine-tuning-sft.md]

## Applications and Recommendations

DMT is particularly recommended for practical SFT of large language models that require balanced skill portfolios across multiple domains. The strategy is especially valuable when training models that need to excel in both specialized technical abilities (mathematics, code generation) and general instruction-following capabilities. ^[supervised-fine-tuning-sft.md]

### Best Practices

- Use DMT when training models on multiple distinct ability domains
- Set the rehearsal fraction k to approximately 1/256 for optimal balance
- Prioritize volume scaling for mathematical and code domains in Stage 1
- Focus on high-quality curation for general abilities in Stage 2 ^[supervised-fine-tuning-sft.md]

## Future Directions

Important open research areas for DMT include extending the framework to additional abilities such as creative writing and planning, developing dynamic adaptation methods for the k parameter, and exploring [[Parameter-Efficient Fine-Tuning (PEFT)]] extensions such as adapter-based implementations of the DMT strategy. ^[supervised-fine-tuning-sft.md]

## Related Concepts

DMT addresses fundamental challenges in [[Supervised Fine-Tuning (SFT)]] and provides a solution to [[Catastrophic Forgetting in Fine-Tuning]]. The strategy builds upon understanding of [[Cross-Domain Transfer in SFT]] and represents an advancement in multi-ability model training methodologies.
