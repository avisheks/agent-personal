---
title: "UnslothVisionDataCollator"
summary: "A specialized data collator class designed for vision-language model training that handles multimodal data preprocessing and batching."
sources:
  - lora/lora-fine-tuning-hyperparameters-guide-unsloth-documentation.md
createdAt: 2026-05-28T19:19:37.635268+00:00
updatedAt: 2026-05-28T19:19:37.635268+00:00
---
# UnslothVisionDataCollator

**UnslothVisionDataCollator** is a specialized data collation class designed for vision-language model fine-tuning within the Unsloth framework. It provides functionality for handling multimodal training data while offering response-only training capabilities similar to those available for large language models.

## Overview

The UnslothVisionDataCollator serves as the vision equivalent of Unsloth's text-based data collators, enabling efficient processing of vision-language training datasets. It incorporates features specifically designed for multimodal learning scenarios where both visual and textual components need to be properly aligned and processed during training. ^[lora-hyperparameters-guide.md]

## Key Features

### Response-Only Training Support

The collator includes built-in support for response-only training, which allows models to focus learning on assistant responses rather than the entire conversation. This is achieved through the `train_on_responses_only` parameter, which when enabled, masks the instruction portions of the training data. ^[lora-hyperparameters-guide.md]

### Template-Based Instruction Parsing

The class supports template-based parsing through `instruction_part` and `response_part` parameters, which define the specific tokens or strings that demarcate user instructions and assistant responses within the training data. This functionality is equivalent to the `train_on_responses_only` function used with traditional [[Supervised Fine-Tuning (SFT)]] for language models. ^[lora-hyperparameters-guide.md]

## Configuration Parameters

The UnslothVisionDataCollator accepts several key parameters:

- **train_on_responses_only**: Boolean flag that enables response-only training mode, equivalent to the train_on_responses_only functionality for LLMs
- **instruction_part**: String defining the token or template that marks the beginning of user instructions
- **response_part**: String defining the token or template that marks the beginning of assistant responses  
- **force_match**: Boolean parameter that ensures strict matching including newlines and whitespace characters ^[lora-hyperparameters-guide.md]

## Usage Context

The UnslothVisionDataCollator is typically used in conjunction with [[Parameter-Efficient Fine-Tuning (PEFT)]] techniques like [[Low-Rank Adaptation (LoRA)]] for vision-language models. It integrates with the broader Unsloth ecosystem to provide efficient fine-tuning capabilities for multimodal applications while maintaining compatibility with standard [[Chat Template Formatting]] approaches. ^[lora-hyperparameters-guide.md]
