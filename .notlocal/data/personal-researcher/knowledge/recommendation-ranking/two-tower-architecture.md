---
title: "two-tower-architecture"
summary: ""
sources:
  - recommendation-ranking/recommendation-ranking-ref.md
createdAt: 2026-05-18T18:38:03.664123+00:00
updatedAt: 2026-05-18T18:38:03.664123+00:00
---
# Two-Tower Architecture

Two-tower architecture is a neural network design pattern commonly used in recommendation systems and information retrieval for efficiently computing similarity between queries and items at scale. The architecture consists of two separate neural networks (towers) that independently encode queries and items into dense vector representations, with similarity computed via dot product or cosine similarity.

## Architecture Overview

The two-tower model separates the encoding of queries and items into independent neural networks:

```
Query Tower:          Item Tower:
  query features        item features
       ↓                     ↓
  Dense layers          Dense layers
       ↓                     ↓
  query_emb (d-dim)     item_emb (d-dim)
       
Score = dot(query_emb, item_emb) or cosine_sim
```

Each tower processes its respective input features through multiple dense layers to produce fixed-dimensional embeddings. The final similarity score is computed as the dot product between the query and item embeddings. This design enables pre-computation of item embeddings for fast retrieval using approximate nearest neighbor (ANN) search. ^[recommendation-ranking-ref.md]

## Training Methodology

Two-tower models are typically trained using contrastive learning with in-batch negatives. For each (query, positive_item) pair in a training batch, all other items in the batch serve as negative examples. The training objective uses a softmax loss function:

```
L = -log(exp(sim(q, i+)/τ) / Σ_j exp(sim(q, i_j)/τ))
```

where `sim(q, i+)` is the similarity between query and positive item, `τ` is a temperature parameter, and the sum is over all items in the batch. ^[recommendation-ranking-ref.md]

## Advantages and Limitations

### Advantages

The primary advantage of two-tower architecture is its serving efficiency. Item embeddings can be pre-computed offline and stored in a vector database, enabling sub-millisecond retrieval using ANN search across millions of items. This makes it suitable for large-scale production systems requiring low latency. ^[recommendation-ranking-ref.md]

### The Representation Bottleneck

The fundamental limitation of two-tower models is the representation bottleneck. All query information must compress into a d-dimensional vector, and all item information must similarly compress into a d-dimensional vector. The interaction between them reduces to a single scalar dot product, which loses fine-grained interactions. ^[recommendation-ranking-ref.md]

This bottleneck manifests in several ways:

- **Token-level alignment loss**: A query like "red running shoes" matched against "red hiking boots" receives high similarity because most tokens match, despite the semantic difference between "running" and "hiking"
- **Fixed item representations**: Item embeddings remain constant regardless of query context, preventing query-dependent emphasis of different item attributes
- **Limited interaction modeling**: Complex relationships between query and item features cannot be captured through simple dot product similarity ^[recommendation-ranking-ref.md]

## Production Applications

Two-tower architecture serves as the foundation for candidate generation in [[Multi-Stage Recommendation Pipeline]]s. In production systems, it typically handles the first stage of retrieval, narrowing millions of items to hundreds of candidates in under 10 milliseconds. More sophisticated models like [[Cross-Attention]] architectures are then applied to the reduced candidate set for precision ranking. ^[recommendation-ranking-ref.md]

At scale, two-tower models enable approximate nearest neighbor search over catalogs of 100+ million items. The architecture's ability to pre-compute item embeddings makes it the standard choice for retrieval systems where serving latency is critical. ^[recommendation-ranking-ref.md]

## Alternatives and Evolution

Several architectural alternatives address the limitations of pure two-tower models:

- **Two-tower + MLP head**: Adds a multi-layer perceptron over concatenated embeddings, improving interaction modeling at the cost of losing pre-computation benefits
- **ColBERT**: Implements late interaction between query and item tokens while maintaining some retrieval efficiency
- **Cross-attention models**: Provide full attention across query and item tokens for maximum interaction quality but require computation at query time ^[recommendation-ranking-ref.md]

The evolution from two-tower to more sophisticated architectures reflects the fundamental tradeoff between serving efficiency and interaction modeling quality. Modern production systems often use two-tower for retrieval and cross-attention for ranking, combining the benefits of both approaches. ^[recommendation-ranking-ref.md]

## Training Challenges

### Negative Sampling Bias

In-batch negatives used during training are biased toward popular items, as they appear in more batches. This makes the model under-value unpopular items. Corrections include log-Q weighting (inversely weighting negatives by frequency) and hard negative mining to explicitly find items that are similar but not relevant. ^[recommendation-ranking-ref.md]

### Position Bias Effects

When training on click data, two-tower models can learn position effects rather than true relevance. Items clicked at position 1 may be clicked due to position rather than quality, creating a self-reinforcing loop where popular items accumulate more positive signals. [[Position Bias Correction]] through inverse propensity weighting or position-aware modeling is essential for learning true item relevance. ^[recommendation-ranking-ref.md]
