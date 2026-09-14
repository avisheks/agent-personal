---
title: "scaled-dot-product-attention"
summary: ""
sources:
  - ai-applied-search-ranking/what-is-grouped-query-attention-ibm.md
createdAt: 2026-07-30T17:07:17.418707+00:00
updatedAt: 2026-07-30T17:07:17.418707+00:00
---
# Scaled Dot Product Attention

**Scaled Dot Product Attention** is a fundamental mechanism used in transformer architectures to calculate relationships between tokens in a sequence. It is a variant of the basic dot product attention that includes a scaling factor to improve training stability.

## Overview

Scaled dot product attention operates within the attention layer of transformer models, where query (Q), key (K), and value (V) vectors are used to calculate alignment scores between each token at each position in a sequence. These alignment scores are then normalized into attention weights using a softmax function. ^[what-is-grouped-query-attention-ibm.md]

## Mechanism

### Alignment Score Calculation

For each token x in a sequence, alignment scores are calculated by computing the dot product of that token's query vector Qx with the key vector K of each of the other tokens. This involves multiplying the vectors together - if a meaningful relationship between two tokens is reflected in similarities between their respective vectors, multiplying them together will yield a large value. If the two vectors aren't aligned, multiplying them together will yield a small or negative value. ^[what-is-grouped-query-attention-ibm.md]

The key innovation of scaled dot product attention is that these query-key alignment scores (QK) are scaled by multiplying by 1/√dk, where dk is the dimension of the key vectors. This scaling factor improves training stability. ^[what-is-grouped-query-attention-ibm.md]

### Attention Weight Generation

The scaled alignment scores are then input to a softmax function, which normalizes all inputs to values between 0 and 1 such that they all add up to 1. The outputs of the softmax function are the attention weights, each representing the share (out of 1) of token x's attention to be paid to each of the other tokens. If a token's attention weight is close to 0, it will be ignored. An attention weight of 1 would mean that a token receives x's entire attention and all others will be ignored. ^[what-is-grouped-query-attention-ibm.md]

### Context Integration

Finally, the value vector for each token is multiplied by its attention weight. These attention-weighted contributions from each previous token are averaged together and added to the original vector embedding for token x. With this process, token x's embedding is updated to reflect the context provided by the other tokens in the sequence that are relevant to it. ^[what-is-grouped-query-attention-ibm.md]

## Processing Flow

The updated vector embedding is sent to another linear layer with its own weight matrix WZ, where the context-updated vector is normalized back to a consistent number of dimensions and then sent to the next attention layer. Each progressive attention layer captures greater contextual nuance. ^[what-is-grouped-query-attention-ibm.md]

## Related Concepts

Scaled dot product attention is closely related to [[Grouped Query Attention (GQA)]], which is an optimization technique that reduces computational costs while maintaining performance quality in transformer models.
