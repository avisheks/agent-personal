---
title: "post-training-data-requirements"
summary: ""
sources:
  - sft-vs-dpo/how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md
createdAt: 2026-05-20T03:40:04.491426+00:00
updatedAt: 2026-05-20T03:40:04.491426+00:00
---
# Post-Training Data Requirements

Post-training data requirements refer to the amount of data needed to fine-tune large language models (LLMs) after their initial pretraining phase. Unlike pretraining, which requires massive amounts of raw internet data, post-training focuses on smaller, higher-quality datasets to make models useful for real-world applications. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Background

Models pretrained on freely available internet data often suffer from high entropy, where the data is either biased or so neutral that the model cannot distinguish between right and wrong responses. Post-training techniques like [[Supervised Fine-Tuning (SFT)]] and [[Reinforcement Learning from Human Feedback (RLHF)]] address these issues by training models on curated, high-quality datasets. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Multiplicative Scaling Laws

Research from Google DeepMind introduced multiplicative scaling laws that fundamentally changed understanding of post-training data requirements. These laws demonstrate that "at equal quality, the amount of SFT data required drops as the model gets bigger." ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

### SFT Data Scaling

The scaling relationship for [[Supervised Fine-Tuning (SFT)]] data follows the formula where X represents model size in parameters, D represents SFT tokens, and r is a task/method exponent. The study shows exponent ranges of r∈[2.3, 2.8, 3.5] for conservative, typical, and aggressive estimates respectively. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

Using a baseline of a 100B parameter model trained on 20,000 SFT samples, the scaling laws predict dramatically reduced data requirements for larger models. For a 1.7T parameter model, aggressive estimates suggest requiring just one high-quality SFT sample, though practical applications still need multiple samples for effective fine-tuning. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

### Reinforcement Learning Data Scaling

Similar scaling principles apply to reinforcement learning data requirements. The formula uses a baseline dataset size P0 and calculates ratios based on model size differences between baseline and target models. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

Conservative estimates suggest larger models require more RL data, typical estimates indicate constant requirements regardless of model size, while aggressive estimates predict shrinking RL data needs as models grow larger. Industry trends favor the aggressive approach due to cost optimization pressures. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Quality Over Quantity Paradigm

The research reveals that as LLMs scale, their requirements for massive post-training datasets diminish significantly. This challenges the traditional belief that bigger models always demand more data and shifts focus from quantity to quality in dataset curation. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

For organizations, this translates to reduced costs, faster iteration cycles, and competitive advantages built on efficiency rather than data volume. The future of LLM fine-tuning emphasizes making every training sample count rather than accumulating endless amounts of data. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

## Implications for Model Development

The multiplicative scaling laws suggest that larger models become increasingly sample-efficient during post-training. This efficiency gain occurs because larger models develop better internal representations during pretraining, requiring fewer examples to learn specific behaviors or align with human preferences. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]

This trend has significant implications for the development cycle of large language models, as it reduces the bottleneck of collecting massive amounts of high-quality post-training data. Instead, the focus shifts to careful curation and selection of the most informative training examples. ^[how-much-posttraining-data-do-you-really-need-to-finetune-a-model.md]
