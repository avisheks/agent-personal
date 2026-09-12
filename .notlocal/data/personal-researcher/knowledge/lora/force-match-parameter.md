---
title: "Force Match Parameter"
summary: "A configuration option that enforces strict matching of patterns including newlines and whitespace characters in chat template parsing."
sources:
  - lora/lora-fine-tuning-hyperparameters-guide-unsloth-documentation.md
createdAt: 2026-05-28T19:20:05.925876+00:00
updatedAt: 2026-05-28T19:20:05.925876+00:00
---
# Force Match Parameter

The **Force Match Parameter** is a configuration option in the Unsloth Vision Data Collator that controls how strictly the system matches text patterns during training data processing. When enabled, this parameter ensures that newlines and other whitespace characters are matched exactly during the pattern matching process. ^[lora-hyperparameters-guide.md]

## Overview

The force match parameter is implemented as a boolean flag (`force_match = True`) within the `UnslothVisionDataCollator` class. Its primary function is to enhance the precision of text pattern matching by including newline characters and other whitespace in the matching algorithm. ^[lora-hyperparameters-guide.md]

## Configuration

The parameter is configured alongside other training options in the data collator:

- **Default Value**: `True`
- **Type**: Boolean
- **Purpose**: Match newlines and whitespace characters exactly during pattern matching ^[lora-hyperparameters-guide.md]

## Relationship to Response-Only Training

The force match parameter works in conjunction with the [[train-on-responses-only]] functionality. It is used when defining instruction and response parts for training, ensuring that the boundaries between different sections of the training data are matched precisely, including any newline characters that separate them. ^[lora-hyperparameters-guide.md]

When used with [[instruction_part]] and [[response_part]] parameters, the force match setting helps maintain the exact formatting structure of conversational training data, which is particularly important for maintaining the integrity of chat-based training formats. ^[lora-hyperparameters-guide.md]

## Technical Implementation

The force match parameter is integrated into the `UnslothVisionDataCollator` class as part of the data preprocessing pipeline. It affects how the system processes training examples by ensuring that whitespace characters, particularly newlines, are treated as significant elements in the pattern matching process rather than being ignored or normalized. ^[lora-hyperparameters-guide.md]
