---
title: "Perplexity as SFT Predictor"
summary: "The finding that training data with lower perplexity relative to the base model consistently leads to greater improvements in downstream performance, outperforming semantic similarity and other factors as a predictor of SFT success."
sources:
  - sft-vs-dpo/2506.md
  - general/massive-supervised-fine-tuning-experiments-reveal-how-data-layer-and-training-factors-shape-llm-alignment-quality.md
  - sft-vs-dpo/massive-supervised-fine-tuning-experiments-reveal-how-data-layer-and-training-factors-shape-llm-alignment-quality.md
createdAt: 2026-05-18T01:10:07.181697+00:00
updatedAt: 2026-05-18T01:10:07.181697+00:00
---
# Perplexity as SFT Predictor

**Perplexity as SFT Predictor** refers to the empirical finding that training data with lower perplexity for a base model consistently leads to greater improvements in downstream performance during [[Supervised Fine-Tuning (SFT)]]. This relationship has emerged as a more reliable predictor of SFT effectiveness than traditional metrics such as content similarity between training and evaluation data or tokenizer compatibility. ^[2506.14681v2.md]

## Overview

In large-scale experiments involving over 1,000 SFT models across twelve base models and diverse training datasets, researchers discovered that perplexity serves as a robust predictor of SFT success. The finding challenges conventional assumptions that datasets closely resembling target tasks yield the best results, instead suggesting that data requiring minimal additional learning or unlearning from the base model produces more consistent improvements. ^[2506.14681v2.md]

## Key Findings

### Perplexity Outperforms Traditional Metrics

Comprehensive evaluation across multiple model families revealed that perplexity consistently predicts SFT effectiveness, often surpassing superficial similarity between training data and benchmark tasks. This relationship holds across different model architectures and training configurations, making it a more universal predictor than previously considered factors such as topic similarity and average sequence length. ^[2506.14681v2.md]

### Cross-Domain Transfer Effects

The perplexity-based prediction framework helps explain observed cross-domain transfer phenomena, such as code generation data improving mathematical reasoning performance. Rather than relying on topic alignment, the effectiveness appears to correlate with how well the base model can process the training data, as measured by perplexity scores. ^[2506.14681v2.md]

## Practical Implications

### Data Selection Strategy

The perplexity predictor suggests a fundamental shift in SFT data selection strategies. Instead of prioritizing datasets that topically match evaluation tasks, practitioners should focus on training data that the base model can process with lower perplexity. This approach may lead to more robust performance improvements across diverse downstream tasks. ^[2506.14681v2.md]

### Compatibility Assessment

Perplexity serves as a practical proxy for compatibility between models and training data rather than a causal factor. The metric captures multiple latent properties of both the data and model, making it useful for assessing whether a particular dataset will be effective for fine-tuning a specific base model. ^[2506.14681v2.md]

## Relationship to Model Architecture

The perplexity predictor appears to work consistently across different model families, suggesting it captures fundamental aspects of how language models process and adapt to new data during fine-tuning. The relationship holds for both full-parameter tuning and [[Parameter-Efficient Fine-Tuning (PEFT)]] approaches, indicating broad applicability across training methods. ^[2506.14681v2.md]

## Limitations and Future Research

While perplexity proves insightful as a predictor, it can fluctuate based on tokenizer design and base training distributions. This variability indicates a need for more nuanced measures that account for these technical factors. Identifying the causal drivers behind the perplexity-performance association remains an important direction for future research. ^[2506.14681v2.md]

The finding that perplexity outperforms content similarity challenges existing assumptions about optimal training data selection and suggests that compatibility between model and data, rather than topical alignment, may be the key factor in successful supervised fine-tuning. ^[2506.14681v2.md]
