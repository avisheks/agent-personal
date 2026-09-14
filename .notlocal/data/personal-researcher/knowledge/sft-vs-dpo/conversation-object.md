---
title: "conversation-object"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-oumi-oss.md
createdAt: 2026-05-20T03:42:43.372152+00:00
updatedAt: 2026-05-20T03:42:43.372152+00:00
---
# Conversation Object

The **Conversation Object** is a structured data representation used in supervised fine-tuning (SFT) to organize dialogue interactions between users and AI assistants. It serves as the standardized format for transforming raw dataset examples into a format suitable for training language models.

## Structure

A Conversation object consists of a sequence of messages, where each message contains a role and content. The primary roles are:

- **USER**: Represents input from the human user, typically questions or requests
- **ASSISTANT**: Represents responses from the AI model being trained

### Message Components

Each message within a Conversation object contains:
- **Role**: Identifies whether the message comes from a USER or ASSISTANT
- **Content**: The actual text content of the message

## Usage in SFT Datasets

In [[Supervised Fine-Tuning (SFT)]] workflows, the Conversation object is created through the `transform_conversation()` method implemented by dataset classes. This method takes raw dataset examples and converts them into the standardized conversation format required for training. ^[supervised-fine-tuning-oumi-oss.md]

### Transformation Process

When implementing a custom SFT dataset, developers must define how raw data examples are converted into Conversation objects. The transformation involves extracting user input and assistant responses from raw examples, creating Message objects for each role, and combining them into a Conversation object. ^[supervised-fine-tuning-oumi-oss.md]

The `transform_conversation()` method is a required implementation for all subclasses of [[BaseSftDataset]]. This method receives a dictionary representing one row of the raw dataset and must return a properly structured Conversation object containing the dialogue messages. ^[supervised-fine-tuning-oumi-oss.md]

### Example Structure

A typical implementation creates a Conversation with messages containing Role.USER and Role.ASSISTANT entries, where the content corresponds to the input and output fields from the raw dataset example. This standardized format ensures consistency across different datasets and enables the training pipeline to process dialogue data uniformly. ^[supervised-fine-tuning-oumi-oss.md]

## Implementation Example

The following structure demonstrates how raw dataset examples are transformed into Conversation objects:

```python
conversation = Conversation(
    messages=[
        Message(role=Role.USER, content=example['input']),
        Message(role=Role.ASSISTANT, content=example['output'])
    ]
)
```

This example shows the conversion of a raw dataset example containing 'input' and 'output' fields into a structured Conversation object with properly assigned roles. ^[supervised-fine-tuning-oumi-oss.md]

## Integration with Training Pipeline

The Conversation object integrates with the broader training infrastructure through [[Dataset-Task Synergy Patterns]] and [[Task-Specific Dataset Preparation]]. Once raw examples are transformed into Conversation objects, they can be processed by collators and fed into the model training loop as part of the [[SFT-then-DPO Workflow]]. ^[supervised-fine-tuning-oumi-oss.md]

## Dataset Registration

When creating custom SFT datasets, the Conversation object transformation is implemented within registered dataset classes. The registration pattern allows the training system to automatically discover and use different dataset formats while maintaining the consistent Conversation object interface. ^[supervised-fine-tuning-oumi-oss.md]
