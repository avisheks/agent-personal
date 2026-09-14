---
title: "Quality over Quantity in SFT Data"
summary: "The principle that small, high-quality datasets (like LIMA's 1K examples or DEITA's 6K samples) can match or exceed the performance of much larger datasets when examples are carefully curated for complexity, quality, and diversity."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:57:04.747882+00:00
updatedAt: 2026-06-15T11:57:04.747882+00:00
---
# Quality over Quantity in SFT Data

Quality over quantity in [[Supervised Fine-Tuning (SFT)]] represents a paradigm shift from traditional machine learning approaches that emphasized large datasets. This principle demonstrates that carefully curated, high-quality training examples can achieve superior performance compared to massive datasets of lower quality. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Core Evidence

The LIMA study (2023) provided foundational evidence for this paradigm by achieving 43% preference over GPT-4 on some benchmarks using only 1,000 carefully selected examples. This demonstrated that strategic data curation could compete with models trained on orders of magnitude more data. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

DEITA (ICLR 2024) further validated this approach by matching state-of-the-art performance (7.55 MT-Bench score) using only 6,000 samples selected through complexity, quality, and diversity scoring mechanisms. The Yi model family achieved strong results with fewer than 10,000 examples, each verified by ML engineers. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Quality Control Mechanisms

### Complexity and Diversity Scoring
Modern SFT approaches employ automated scoring systems to evaluate training examples across multiple dimensions. The DEITA framework demonstrates how complexity, quality, and diversity metrics can identify the most valuable training samples from larger candidate pools. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

### Human Verification
Industry leaders like the Yi model team implement human verification processes where ML engineers review each training example. This manual curation ensures that every sample meets specific quality standards before inclusion in the training dataset. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

### Synthetic Data Generation
High-quality synthetic data generation techniques like Evol-Instruct from WizardLM (ICLR 2024) use iterative complexity escalation to create sophisticated training examples. The Orca model achieved ChatGPT-level performance on BBH by using GPT-4 explanation traces, demonstrating how synthetic data can maintain quality while scaling. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Scaling Laws and Repetition

Research on data-constrained scaling reveals that quality datasets can be repeated up to 4 epochs without performance degradation, after which benefits decay to zero. This finding supports the quality-over-quantity approach by showing that well-curated datasets maintain their effectiveness through multiple training passes. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Industry Implementation

Large-scale implementations demonstrate varying approaches to quality curation. [[Qwen3 Language Model]] uses over 1 million curated SFT samples across 29+ languages, while maintaining strict quality standards. Meta's Llama 3.1 employs over 10 million human annotations across all post-training phases, representing a hybrid approach that combines scale with quality control. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Practical Benefits

The quality-over-quantity paradigm offers several practical advantages:

- **Reduced computational costs**: Smaller, high-quality datasets require less training time and resources
- **Improved performance**: Carefully curated examples lead to better model capabilities on target tasks
- **Faster iteration**: Smaller datasets enable quicker experimentation and refinement cycles
- **Better generalization**: High-quality examples help models learn more robust patterns

^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Related Concepts

This paradigm connects closely with [[Parameter-Efficient Fine-Tuning (PEFT)]] techniques like [[Low-Rank Adaptation (LoRA)]], which similarly achieve strong results with minimal parameter updates. The approach also relates to [[Constitutional AI]] frameworks that emphasize principled data curation and [[Reinforcement Learning from Human Feedback (RLHF)]] systems that prioritize high-quality human feedback over volume.
