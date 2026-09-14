---
title: "Train-on-Responses-Only"
summary: "A training configuration that applies loss only to assistant tokens in conversational data, preventing models from learning to generate user prompts and focusing learning on desired response patterns."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:57:15.968163+00:00
updatedAt: 2026-06-15T11:57:15.968163+00:00
---
# Train-on-Responses-Only

**Train-on-Responses-Only** is a supervised fine-tuning technique where the language model is trained to predict only the assistant's response tokens, while masking the loss computation on user prompt tokens. This approach prevents the model from learning to generate user prompts and focuses training exclusively on desired output behavior.

## Overview

In standard language model training, the model learns to predict the next token across the entire sequence. However, for chat and instruction-following applications, this can lead to undesired behavior where the model learns to generate user-like prompts rather than assistant responses. Train-on-Responses-Only addresses this by applying loss computation selectively to assistant tokens only. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Implementation

The technique is implemented by setting label values to -100 for all prompt tokens during training, which causes the cross-entropy loss function to ignore these positions. In the [[Hugging Face Transformers Library]], this is achieved through the `assistant_only_loss=True` parameter in training configurations. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

The approach requires careful handling of conversation formatting, where system prompts, user messages, and assistant responses must be properly delineated. Special tokens are typically used for role separation to ensure accurate masking of non-assistant content. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Applications

### Chat Models
Train-on-Responses-Only is considered standard practice for chat model development. It ensures that models learn appropriate conversational behavior without picking up user-side patterns that could lead to role confusion during inference. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

### Multi-turn Conversations
For multi-turn dialogue training, the technique becomes more complex as it must handle alternating user and assistant turns. Proper position encoding and attention masking are required to maintain conversation flow while preserving the response-only training objective. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Comparison with Full-Sequence Training

Full-sequence loss training, where the model learns to predict all tokens in the sequence, is typically reserved for continued pretraining scenarios where the goal is to learn general language patterns rather than specific interaction behaviors. For instruction-following and chat applications, Train-on-Responses-Only consistently produces better-aligned models. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Industry Adoption

Major language model developers have adopted Train-on-Responses-Only as a standard practice. The technique is implemented across various frameworks and has become the default approach for [[Supervised Fine-Tuning (SFT)]] in conversational AI applications. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Technical Considerations

The approach requires careful attention to tokenization and data formatting to ensure proper masking. Incorrect implementation can lead to training instability or suboptimal performance. Modern training frameworks provide built-in support for this technique, reducing implementation complexity for practitioners. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]
