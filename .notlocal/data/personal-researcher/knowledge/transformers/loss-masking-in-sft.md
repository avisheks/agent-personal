---
title: "Loss Masking in SFT"
summary: "A technique in supervised fine-tuning where the model only learns to predict assistant responses, not user messages, by masking the loss computation for user tokens."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:45:06.893207+00:00
updatedAt: 2026-06-16T14:45:06.893207+00:00
---
# Loss Masking in SFT

Loss masking is a critical technique in [[Supervised Fine-Tuning (SFT)]] that controls which tokens the model learns to predict during training. Unlike pre-training where the model learns to predict every next token in a sequence, SFT requires selective learning to teach the model appropriate conversational behavior.

## Core Concept

During [[Supervised Fine-Tuning (SFT)]], training data consists of conversations between users and assistants with special tokens marking different speakers. Loss masking ensures the model only learns to generate assistant responses, not user messages, by selectively applying the loss function to specific tokens in the sequence. ^[Large Language Model (LLM) Training - Intro - final.pdf]

Without loss masking, the model would learn to predict user messages as well as assistant responses, leading to confusion about conversational roles and degraded performance as a helpful assistant. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Implementation

Loss masking works by creating a boolean mask that corresponds to each token in the training sequence. The mask determines whether the [[cross-entropy loss]] is computed for that position:

```
sequence = ["<|user|>", "What's", "2+2", "?", "<|end|>",           
           "<|assistant|>", "2+2", "equals", "4", "<|end|>"]

loss_mask = [False, False, False, False, False,  # User tokens - no loss
            False, True, True, True, True]        # Assistant tokens - compute loss
```

The training loop applies this mask during loss computation, ensuring gradients only flow through assistant token predictions. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Training Data Format

SFT training data uses special tokens to delineate different parts of conversations:

```
<|user|>How do I center a div in CSS?<|end|>
<|assistant|>You can center a div using flexbox:
```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}
```<|end|>
```

The loss mask ensures the model learns to predict only the assistant's response tokens, not the user's question or the special formatting tokens. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Technical Considerations

Loss masking maintains the same training mechanics as pre-training, including the [[AdamW]] optimizer, mixed precision training, and gradient accumulation. The key difference lies in the selective application of the loss function rather than changes to the underlying training infrastructure. ^[Large Language Model (LLM) Training - Intro - final.pdf]

Memory requirements remain identical to pre-training since the model architecture and parameter count are unchanged. The masking operation adds minimal computational overhead as it simply zeros out loss contributions from masked positions. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Relationship to Other Techniques

Loss masking is fundamental to SFT but distinct from techniques used in preference learning like [[Direct Preference Optimization (DPO)]]. While DPO learns from response comparisons, loss masking in SFT teaches basic conversational format through direct examples. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The technique enables the transition from a general language model trained on raw text to a conversational assistant that understands dialogue structure and appropriate response generation. ^[Large Language Model (LLM) Training - Intro - final.pdf]
