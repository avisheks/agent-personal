---
title: "chat-dataset-formats"
summary: ""
sources:
  - sft-vs-dpo/introduction-to-supervised-fine-tuning-dataset-formats-red-hat-developer.md
createdAt: 2026-05-20T03:37:48.774438+00:00
updatedAt: 2026-05-20T03:37:48.774438+00:00
---
# Chat Dataset Formats

Chat dataset formats are standardized structures used to organize conversational data for training large language models through [[Supervised Fine-Tuning (SFT)]]. These formats enable models to learn chat and assistant-style interactions by providing structured prompt-response pairs or simulated conversations that familiarize the model with conversational behavior patterns. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Overview

Large language models are conventionally trained in two phases: pre-training on unlabeled internet text and post-training using formatted conversational data. During the post-training phase, models learn to predict tokens that align with chatbot behavior through [[Supervised Fine-Tuning (SFT)]] using datasets of formatted prompt-response pairs or simulated conversations. ^[introduction-supervised-fine-tuning-dataset-formats.md]

Unfortunately, there isn't much consistency in input formats across the field. While some standards have emerged, particularly for chat conversation datasets, data keys often have different names and datasets frequently include extra fields that may or may not be relevant to the text generation task. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Template Processing

### Jinja Templating

Chat datasets are processed using [[Chat Template Formatting]] through the Jinja templating library, which defines a templating language for creating chat and prompt templates. These templates use special tokens to denote different sections of conversations, such as user prompts versus chatbot responses. ^[introduction-supervised-fine-tuning-dataset-formats.md]

A typical template structure includes role-based formatting:
- System messages with `<|system|>` tokens
- User messages with `<|user|>` tokens  
- Assistant responses with `<|assistant|>` tokens

### Token Sequence Generation

After templating, the formatted sequences are split into tokens and mapped to corresponding token indices. These indices select token embeddings (typically floating point vectors) for each token. The model loss during training measures next-token prediction error compared to ground truth, requiring flat tokenized sequences with corresponding labels where some tokens are masked out. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Dataset Format Categories

### Chat Formats

Chat formats organize entries as lists of dictionaries containing "content" and "role" values that form conversations. Two primary standards have emerged:

**OpenAI Format:**
- Uses "messages" as the top-level key
- Roles specified as "system", "user", or "assistant"
- Content stored in "content" field

**ShareGPT Format:**
- Uses "conversations" as the top-level key
- Roles specified as "system", "human", or "gpt"
- Content stored in "value" field

^[introduction-supervised-fine-tuning-dataset-formats.md]

### Instruct Formats

Instruct formats consist of prompt and response pairs, with variations in field naming and structure:

**Alpaca Format:**
- Separates "instruction" and "input" fields
- Uses "output" for responses
- Input field may be empty string

**Prompt-Response Format:**
- Simple "prompt" and "response" key structure
- Direct mapping between input and output

^[introduction-supervised-fine-tuning-dataset-formats.md]

### Text-Only Formats

Text-only datasets contain pre-processed conversations where prompt, response, and chat elements have already been formatted into template strings with established separators between different parts of speech. These use various special token patterns like `<INST>...</INST>` or `<human>...<bot>` to indicate different speakers. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## File Storage Formats

SFT datasets are commonly stored in JSON or JSONL (JSON Lines) files at the file level. Some datasets may also be compressed or stored in parquet files, which provide efficient column-based data storage format for large-scale training operations. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Template Consistency

When fine-tuning models that have already been instruct or chat tuned, existing templates are typically available through the model's tokenizer configuration. It is important to reuse these existing templates for further training to ensure the model sees only a single consistent template format throughout its training process. ^[introduction-supervised-fine-tuning-dataset-formats.md]
