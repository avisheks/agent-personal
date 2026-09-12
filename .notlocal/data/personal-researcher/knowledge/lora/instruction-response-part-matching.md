---
title: "Instruction-Response Part Matching"
summary: "A mechanism that identifies and separates instruction and response portions in chat templates using specific string patterns for targeted training."
sources:
  - lora/lora-fine-tuning-hyperparameters-guide-unsloth-documentation.md
createdAt: 2026-05-28T19:19:59.288016+00:00
updatedAt: 2026-05-28T19:19:59.288016+00:00
---
# Instruction-Response Part Matching

**Instruction-Response Part Matching** is a training technique used in supervised fine-tuning that allows models to selectively learn from specific portions of conversational data by distinguishing between instruction and response segments within training examples.

## Overview

Instruction-Response Part Matching enables fine-tuning frameworks to apply loss computation only to designated response portions of training conversations, while masking the instruction portions from gradient updates. This approach is particularly useful when training conversational AI models where the goal is to improve response generation rather than instruction understanding. ^[lora-hyperparameters-guide.md]

## Implementation

The technique is implemented through specialized data collators that identify and separate instruction and response segments within training data. In the Unsloth framework, this functionality is provided through the `UnslothVisionDataCollator` class, which includes parameters for configuring instruction-response matching. ^[lora-hyperparameters-guide.md]

### Key Parameters

The implementation uses several key parameters to control the matching behavior:

- **instruction_part**: Defines the delimiter or pattern that marks the beginning of instruction segments
- **response_part**: Specifies the delimiter or pattern that identifies response segments  
- **force_match**: Controls whether the matching algorithm should strictly match formatting elements like newlines
- **train_on_responses_only**: A boolean flag that enables or disables the selective training behavior ^[lora-hyperparameters-guide.md]

## Chat Template Integration

Instruction-Response Part Matching integrates with [[Chat Template Formatting]] systems to work with structured conversational formats. For example, in Llama-style chat templates, the instruction part might be marked with `<|start_header_id|>user<|end_header_id|>\n\n` while the response part uses `<|start_header_id|>assistant<|end_header_id|>\n\n` as delimiters. ^[lora-hyperparameters-guide.md]

## Applications in Fine-Tuning

This technique is commonly used in [[Supervised Fine-Tuning (SFT)]] workflows where the objective is to improve model responses while preserving the model's ability to understand instructions. By applying loss only to response tokens, the training process focuses computational resources on the portions of the conversation that directly contribute to response quality improvement. ^[lora-hyperparameters-guide.md]

The approach is particularly valuable when combined with [[Parameter-Efficient Fine-Tuning (PEFT)]] methods like [[Low-Rank Adaptation (LoRA)]], as it allows for more targeted adaptation of model parameters to specific conversational roles and response patterns. ^[lora-hyperparameters-guide.md]
