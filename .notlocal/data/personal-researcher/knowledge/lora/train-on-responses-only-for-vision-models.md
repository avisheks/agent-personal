---
title: "Train on Responses Only for Vision Models"
summary: "A training configuration that applies response-only training to vision-language models, equivalent to the text-only train_on_responses_only functionality but adapted for multimodal data."
sources:
  - lora/lora-fine-tuning-hyperparameters-guide-unsloth-documentation.md
createdAt: 2026-05-28T19:19:50.374300+00:00
updatedAt: 2026-05-28T19:19:50.374300+00:00
---
# Train on Responses Only for Vision Models

**Train on Responses Only for Vision Models** is a training technique that extends the concept of response-only training from language models to vision-language models. This approach allows models to learn only from the assistant's responses while ignoring the instruction portions during training, similar to how it works for text-only language models.

## Implementation

The technique is implemented through the `UnslothVisionDataCollator` class, which provides equivalent functionality to the `train_on_responses_only` function used for [[Low-Rank Adaptation (LoRA)]] fine-tuning of language models. The data collator includes specific parameters that mirror the behavior of the text-based implementation:

- `train_on_responses_only`: A boolean flag that enables response-only training for vision models
- `instruction_part`: Specifies the template marker that identifies instruction sections
- `response_part`: Defines the template marker that identifies response sections  
- `force_match`: Ensures exact matching including newlines and formatting ^[lora-hyperparameters-guide.md]

## Configuration Example

The implementation follows the same pattern as text-based models, using chat template markers to distinguish between instruction and response portions. For example, using Llama-style chat templates:

```python
instruction_part = "<|start_header_id|>user<|end_header_id|>\n\n"
response_part = "<|start_header_id|>assistant<|end_header_id|>\n\n"
```

This configuration allows the vision model to focus learning exclusively on the assistant's responses while masking out the user instructions during training. ^[lora-hyperparameters-guide.md]

## Relationship to Text Models

This approach directly parallels the `train_on_responses_only` function used in [[Supervised Fine-Tuning (SFT)]] for text-only models. The vision implementation maintains the same core principle of selective training on response tokens while providing the necessary adaptations for handling multimodal data that includes both visual and textual components. ^[lora-hyperparameters-guide.md]
