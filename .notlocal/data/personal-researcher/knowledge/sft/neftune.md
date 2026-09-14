---
title: "NEFTune"
summary: "A technique that adds noise to embeddings during supervised fine-tuning, providing massive free improvements of 8-35% on benchmarks like AlpacaEval without architectural changes."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:55:58.071036+00:00
updatedAt: 2026-06-15T11:55:58.071036+00:00
---
# NEFTune

**NEFTune** (Noisy Embeddings Improve Instruction Finetuning) is a simple yet highly effective technique for improving the performance of [[supervised-fine-tuning-sft|supervised fine-tuning]] in large language models. The method involves adding uniform noise to token embeddings during training, which has been shown to produce substantial improvements in instruction-following capabilities with minimal implementation overhead. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Overview

NEFTune was introduced in 2023 as a straightforward modification to the standard fine-tuning process. The technique adds uniform noise to the embedding vectors of input tokens during training, which acts as a form of regularization that improves the model's ability to follow instructions and engage in conversations. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Performance Impact

The effectiveness of NEFTune has been demonstrated across multiple benchmarks and model scales. On AlpacaEval, models trained with NEFTune showed dramatic improvements, with performance increasing from 29.8% to 64.7% in some cases. This represents one of the most significant "free" improvements available in fine-tuning, requiring no additional data, computational resources, or architectural changes. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Implementation

NEFTune is implemented by modifying the embedding layer during training to add uniform noise to the token embeddings. The technique is simple enough that it can be easily integrated into existing fine-tuning pipelines without significant code changes. The noise is applied only during training and not during inference. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Industry Adoption

NEFTune has become a standard recommendation in fine-tuning workflows due to its consistent positive impact and ease of implementation. The technique is particularly valuable because it provides substantial improvements without requiring additional hyperparameter tuning or increased computational costs, making it an attractive option for practitioners working with limited resources. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Relationship to Other Techniques

NEFTune can be combined with other fine-tuning approaches such as [[low-rank-adaptation-lora|LoRA]], [[parameter-efficient-fine-tuning-peft|parameter-efficient fine-tuning]], and various [[supervised-fine-tuning-sft|supervised fine-tuning]] strategies. The technique is complementary to most other optimization methods and does not interfere with standard training procedures. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]
