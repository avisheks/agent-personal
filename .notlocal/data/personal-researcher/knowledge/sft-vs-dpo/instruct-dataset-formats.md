---
title: "instruct-dataset-formats"
summary: ""
sources:
  - sft-vs-dpo/introduction-to-supervised-fine-tuning-dataset-formats-red-hat-developer.md
createdAt: 2026-05-20T03:38:02.980743+00:00
updatedAt: 2026-05-20T03:38:02.980743+00:00
---
# Instruct Dataset Formats

Instruct dataset formats are standardized structures used to organize training data for [[Supervised Fine-Tuning (SFT)]] of large language models. These formats define how prompt-response pairs and conversational data are structured to train models for chat and assistant-style interactions during the post-training phase. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Overview

During [[Supervised Fine-Tuning (SFT)]], models learn to predict subsequent tokens that align with chatbot behavior by training on datasets of formatted prompt-response pairs or simulated conversations. The challenge lies in the lack of consistency across input formats, though some standards have emerged, particularly for chat conversation datasets. Data keys often have different names or datasets include extra fields which may or may not be relevant to the text generation task. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Template Processing

### Jinja Templating

Instruct datasets use [[Chat Template Formatting]] through the [[Jinja Templating for LLMs]] library to convert structured data into flat tokenized sequences. Templates define how to format different message roles using special tokens to denote user prompts versus chatbot responses. ^[introduction-supervised-fine-tuning-dataset-formats.md]

A typical template structure includes:
- Role-specific formatting for system, user, and assistant messages
- Special tokens to separate different components
- End-of-sequence tokens to mark message boundaries ^[introduction-supervised-fine-tuning-dataset-formats.md]

When fine-tuning a model that has already been instruct/chat tuned, it is important to reuse the existing template for further training so that the model sees only a single consistent template format. ^[introduction-supervised-fine-tuning-dataset-formats.md]

### Token Processing

After templating, the formatted sequence undergoes tokenization where tokens are mapped to corresponding indices. These indices select token embeddings (floating point vectors) for each token, creating the final input format for model training. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Dataset Format Categories

### Chat Formats

Chat formats structure entries as lists of dictionaries containing "content" and "role" values that form conversations. Two common variants include:

**OpenAI Format**: Uses "messages" as the top-level key with "role" and "content" fields for each message entry. ^[introduction-supervised-fine-tuning-dataset-formats.md]

**ShareGPT Format**: Uses "conversations" as the top-level key with "from" and "value" fields, where roles are labeled as "system," "human," or "gpt." ^[introduction-supervised-fine-tuning-dataset-formats.md]

### Instruct Formats

Instruct formats organize data as prompt-response pairs, often with additional structure:

**Alpaca Format**: Separates prompts into "instruction" and "input" components, paired with an "output" response. The input field may be empty for simple instruction-following tasks. ^[introduction-supervised-fine-tuning-dataset-formats.md]

**Prompt-Response Format**: Uses direct "prompt" and "response" key pairs for straightforward question-answer structures. ^[introduction-supervised-fine-tuning-dataset-formats.md]

### Text-Only Formats

Text-only formats contain pre-processed data where prompt/response/chat formatting has already been applied. These datasets consist of single formatted strings with established separators between different speech components, using various special token schemes to indicate different speakers or sections. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## File Storage

Instruct datasets are commonly stored in JSON or JSONL (JSON Lines) file formats. Some datasets may be compressed or stored in Parquet files, which provide efficient column-based data storage for large-scale training operations. ^[introduction-supervised-fine-tuning-dataset-formats.md]

## Standardization Efforts

The AI community has begun establishing standards, particularly for chat-style datasets, to improve compatibility across different model-dataset combinations. Consistent [[Prompt Template Encoding]] ensures models receive uniform formatting during fine-tuning, which is crucial for maintaining training stability and performance. Organizations like Red Hat use [[Jinja Templating for LLMs]] and standardized dataset formats in their training libraries to ensure models are always fine-tuned with consistent prompting templates. ^[introduction-supervised-fine-tuning-dataset-formats.md]
