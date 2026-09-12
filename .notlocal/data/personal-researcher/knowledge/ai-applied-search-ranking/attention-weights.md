---
title: "attention-weights"
summary: ""
sources:
  - ai-applied-search-ranking/what-is-grouped-query-attention-ibm.md
createdAt: 2026-07-30T17:07:28.426953+00:00
updatedAt: 2026-07-30T17:07:28.426953+00:00
---
# Attention Weights

**Attention weights** are normalized probability distributions that determine how much focus a token should pay to other tokens in a sequence during the attention mechanism in transformer models. They represent the relative importance of each token when computing contextual representations.

## Computation Process

Attention weights are derived through a multi-step process within the attention layer. First, alignment scores are calculated between tokens using their query (Q) and key (K) vectors. For each token x in a sequence, alignment scores are computed by taking the dot product of that token's query vector Qx with the key vector K of each other token - essentially multiplying them together. When there is a meaningful relationship between two tokens reflected in similarities between their respective vectors, this multiplication yields a large value. Conversely, if the two vectors aren't aligned, the multiplication produces a small or negative value. Most transformer models use [[Scaled Dot Product Attention]], where the QK product is scaled by multiplying by 1/√dk to improve training stability. ^[what-is-grouped-query-attention-ibm.md]

The alignment scores are then processed through a softmax function to produce the final attention weights. The softmax function normalizes all inputs to values between 0 and 1 such that they all sum to 1. The outputs of this softmax function are the attention weights, with each weight representing the share (out of 1) of token x's attention to be paid to each of the other tokens. If a token's attention weight is close to 0, it will be effectively ignored. An attention weight of 1 would mean that a token receives x's entire attention while all others are ignored. ^[what-is-grouped-query-attention-ibm.md]

## Application in Context Updates

Once computed, attention weights are used to update token representations with contextual information. The value vector for each token is multiplied by its corresponding attention weight. These attention-weighted contributions from each previous token are then averaged together and added to the original vector embedding for token x. Through this process, token x's embedding is updated to reflect the context provided by other tokens in the sequence that are relevant to it. ^[what-is-grouped-query-attention-ibm.md]

The updated vector embedding is subsequently sent to another linear layer with its own weight matrix WZ, where the context-updated vector is normalized back to a consistent number of dimensions before being passed to the next attention layer. Each progressive attention layer captures greater contextual nuance through this iterative refinement process. ^[what-is-grouped-query-attention-ibm.md]

## Related Concepts

Attention weights are fundamental to several advanced attention mechanisms, including [[Grouped Query Attention (GQA)]] and other variants that optimize computational efficiency while maintaining model performance. They also play a crucial role in [[Chain-of-Thought Reasoning]] by allowing models to focus on relevant previous steps in multi-step reasoning processes.
