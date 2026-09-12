---
title: "multiplicative-scaling-laws-for-fine-tuning"
summary: ""
sources:
  - sft-vs-dpo/how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md
createdAt: 2026-05-21T01:48:34.794338+00:00
updatedAt: 2026-05-21T01:48:34.794338+00:00
---
# Multiplicative Scaling Laws for Fine-tuning

**Multiplicative Scaling Laws for Fine-tuning** are mathematical relationships that describe how the amount of post-training data required for [[Supervised Fine-Tuning (SFT)]] and [[Reinforcement Learning from Human Feedback (RLHF)]] decreases as model size increases. These laws challenge the conventional assumption that larger models always require proportionally more training data. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Overview

The multiplicative scaling laws were introduced in a breakthrough ICLR 2024 paper by researchers from Google DeepMind. The core finding demonstrates that "at equal quality, the amount of SFT data required drops as the model gets bigger." This represents a fundamental shift in understanding the relationship between model scale and data requirements during post-training phases. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Mathematical Formulation

### SFT Scaling Laws

The scaling law for [[Supervised Fine-Tuning (SFT)]] data requirements follows the formula:

**D ∝ X^(-r)**

Where:
- X = model size (parameters)
- D = SFT tokens required
- r = task/method exponent

The study identifies three scaling regimes with different exponent ranges:
- **Conservative**: r = 2.3
- **Typical**: r = 2.8  
- **Aggressive**: r = 3.5

^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

### RL Scaling Laws

For [[Reinforcement Learning from Human Feedback (RLHF)]] data, the scaling relationship uses a similar multiplicative approach, where larger models require progressively less reinforcement learning data to achieve equivalent performance levels. The formula for calculating RL data requirements is:

**P = P0 × (d-target / d0)**

Where P0 represents the baseline dataset size and d-target/d0 is the ratio calculated using baseline and target model sizes. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Practical Implications

### Data Requirements by Model Size

Using a baseline of a 100B parameter model trained on 20,000 SFT samples, the scaling laws predict dramatically reduced data needs for larger models. The aggressive scaling estimates suggest that a 1.7T parameter model would theoretically need just one good SFT sample for effective fine-tuning, though practical implementations still require multiple high-quality samples for model utility. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

### RL Data Scaling Patterns

For reinforcement learning data, using a baseline 100B model with 100,000 RL samples, the scaling laws show three distinct patterns:
- **Conservative estimates**: Larger models require more RL data
- **Typical estimates**: RL data requirements remain constant regardless of model size
- **Aggressive estimates**: RL data requirements shrink as models grow larger

^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

### Cost and Efficiency Benefits

The multiplicative scaling laws have significant implications for:

- **Reduced training costs** as model sizes increase
- **Faster iteration cycles** due to smaller dataset requirements  
- **Quality-focused data curation** rather than volume-based approaches
- **Competitive advantages** through efficiency optimization

^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Industry Impact and Future Trends

These scaling laws represent a paradigm shift from quantity-focused to quality-focused fine-tuning approaches. The research suggests that as LLMs scale, their hunger for massive post-training datasets diminishes, challenging the long-held belief that bigger models always demand more data. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

The trend toward aggressive scaling estimates is expected to accelerate as organizations seek to optimize costs. This shift emphasizes curating the right data rather than accumulating more data, fundamentally changing how the industry approaches model fine-tuning. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Limitations and Considerations

While the theoretical predictions suggest minimal data requirements for very large models, practical fine-tuning still requires sufficient high-quality data to ensure model utility and safety. The scaling laws provide guidance for data planning but must be balanced with real-world performance requirements and [[overfitting-detection-in-sft]] considerations. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

The research represents a rewriting of the LLM fine-tuning story, where the future focuses on making every sample count rather than feeding models endless amounts of data. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]
