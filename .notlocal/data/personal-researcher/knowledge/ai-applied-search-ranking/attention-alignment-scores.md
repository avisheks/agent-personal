---
title: "attention-alignment-scores"
summary: ""
sources:
  - ai-applied-search-ranking/what-is-grouped-query-attention-ibm.md
createdAt: 2026-07-30T17:07:10.028929+00:00
updatedAt: 2026-07-30T17:07:10.028929+00:00
---
# Attention Alignment Scores

**Attention Alignment Scores** are numerical values calculated in the attention mechanism of transformer models to determine the relevance between different tokens in a sequence. These scores form the foundation for computing attention weights, which determine how much focus each token should receive when processing a particular position in the sequence.

## Calculation Process

In the attention layer, alignment scores are computed using the query (Q), key (K), and value (V) vectors. For each token x in a sequence, alignment scores are calculated by computing the dot product of that token's query vector Qx with the key vector K of each of the other tokens - in other words, by multiplying them together. If a meaningful relationship between 2 tokens is reflected in similarities between their respective vectors, multiplying them together will yield a large value. If the 2 vectors aren't aligned, multiplying them together will yield a small or negative value. ^[grouped-query-attention.md]

Most transformer models use a variant called [[Scaled Dot Product Attention]], in which QK is scaled—that is, multiplied—by 1/√dk to improve training stability. ^[grouped-query-attention.md]

## Conversion to Attention Weights

These query-key alignment scores are then input into a softmax function. Softmax normalizes all inputs to a value between 0 and 1 such that they all add up to 1. The outputs of the softmax function are the [[Attention Weights]], each representing the share (out of 1) of token x's attention to be paid to each of the other tokens. If a token's attention weight is close to 0, it will be ignored. An attention weight of 1 would mean that a token receives x's entire attention and all others will be ignored. ^[grouped-query-attention.md]

## Integration with Value Vectors

Finally, the value vector for each token is multiplied by its attention weight. These attention-weighted contributions from each previous token are averaged together and added to the original vector embedding for token x. With this, token x's embedding is now updated to reflect the context provided by the other tokens in the sequence that are relevant to it. This produces a [[Context-Updated Vector Embedding]]. ^[grouped-query-attention.md]

## Role in Model Architecture

The updated vector embedding is then sent to another linear layer, with its own weight matrix WZ, where the context-updated vector is normalized back to a consistent number of dimensions and then sent to the next attention layer. Each [[Progressive Attention Layers]] captures greater contextual nuance. ^[grouped-query-attention.md]

Attention alignment scores are fundamental to how [[Transformer Architecture]] models process sequential information and enable [[Chain-of-Thought Reasoning]] by allowing tokens to selectively attend to relevant context from earlier positions in the sequence.
