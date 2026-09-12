---
title: "Why LLMs Are NOT SOTA at User Sequence Prediction"
summary: "Six technical reasons: (1) architectural over-capacity (SASRec 0.83M beats LlamaRec 7B by 25%), (2) positional/order blindness (shuffled sequences change LLM reps only 1-7%), (3) vocabulary mismatch (millions of items vs 100K tokens), (4) information-theoretic gap (text holds ~14% of useful signal vs CF), (5) no collaborative filtering signal in text, (6) generation ≠ ranking. Fundamental: text describes what items ARE; behavior reveals what items DO for users."
sources:
  - sources/genai-search-ads/why-llms-not-sota-user-sequence-prediction.md
createdAt: 2026-06-08
updatedAt: 2026-06-08
---

# Why LLMs Are NOT SOTA at User Sequence Prediction

## The Headline Number

**SASRec (0.83M params) beats LlamaRec (7B params) by 25.7% on NDCG@5.** The 8,500x parameter advantage is counterproductive.

## Six Technical Reasons

### 1. Architectural Over-Capacity (Extra Layers = Noise)

RECFORMER (Longformer, 12 layers) loses to SASRec (2 layers) on multiple datasets. "The Elephant in the Room" (RecSys 2024) shows layers 0-7 perform intra-item token aggregation — a function a simple embedding lookup already handles. Only layers 8-11 model sequential preferences, converging to exactly what SASRec does in 2 layers.

**Behavior sequences need shallow transition learning, not deep semantic processing.** Language complexity ≠ behavioral complexity.

### 2. Positional/Order Blindness

"Lost in Sequence" (KDD 2025): Shuffling interaction sequences changes LLM4Rec representations by only **1-7%** (cosine sim 0.93-0.98). SASRec changes by **25-35%** (sim 0.65-0.75).

**LLMs treat behavior histories as unordered bags.** RoPE/absolute positions encode token position, not interaction position. Sequential signal drowns in formatting text.

### 3. Token Vocabulary Mismatch

Language: ~100K tokens with learned compositional semantics. Recommendation: millions of items with NO pre-trained behavioral relationships. LLMs "often generate out-of-range results" — hallucinated items outside the catalog (E4SRec).

### 4. Information-Theoretic Gap (Text ≈ 14% of Signal)

RLMRec (arXiv:2310.15950): Pure semantic embeddings achieve R@20 = 0.0199 vs CF baseline = 0.1343 on Amazon-Book. Text contains approximately **14% of the useful signal** that behavioral representations capture.

OPT-175B frozen achieves HR@10 = 2.09 vs IDCF = 6.79 — a **3.2x deficit** even at 175B scale.

### 5. No Collaborative Filtering Signal in Text

CoLLM (TKDE 2025): Text-only LLM AUC = 0.7375 vs attention CF (DIN) = 0.8163. Two items with identical text can have completely different collaborative patterns. "LLMs underperform simple traditional CF models under warm scenarios" (A-LLMRec, KDD 2024).

### 6. Generation ≠ Ranking

Recommendation is a scoring/ranking task, not a generation task. Lite-LLM4Rec: eliminating generation (using direct projection head) gives **46.8% better performance + 97% efficiency gain**. Beam search is "ultimately unnecessary for sequential recommendations."

## The Fundamental Asymmetry

| What Text Encodes | What Prediction Needs |
|-------------------|-----------------------|
| What items ARE (descriptions, attributes) | What items DO for users (behavioral signal) |
| Declared preferences (reviews, forums) | Revealed preferences (clicks, purchases) |
| Cultural/semantic similarity | Collaborative/behavioral similarity |
| Stable grammar/semantics | Non-stationary drift, context-dependent patterns |
| Dense signal (every token informative) | Extremely sparse (1 click per 1000 impressions) |

**No amount of scaling a text-trained model recovers information that was never in text.**

## What Would Close the Gap

| Approach | Evidence | Trade-off |
|----------|----------|-----------|
| Behavior pre-training of embeddings | +21% when PLM tuned on interactions (RecSys 2024) | Loses zero-shot advantage |
| CF embedding injection into LLM | +7.3% AUC (CoLLM, TKDE 2025) | Requires behavioral data |
| Distill CF-SRec into LLM | SOTA on Movies (LLM-SRec, KDD 2025) | Still needs CF model first |
| Use LLM for initialization only | Best of both (Elephant paper) | LLM discarded at inference |

All paths to LLM SOTA for sequence prediction require behavioral data — defeating the zero-shot advantage that motivated using LLMs in the first place.

## Practical Architecture Recommendation

```
Optimal: LLM (cold-start + semantic) → SASRec/BERT4Rec (warm sequential)
                                            ↑
                                    CF embeddings from
                                    interaction data
                                            ↑
                                    Negative sampling +
                                    contrastive learning
```

Use LLMs for what they're good at (understanding items, cold-start, explaining). Use lightweight specialized models for what they're good at (temporal sequences, collaborative patterns, real-time scoring at <50ms).

## Related

- [[LLM Quality for User Behavior Modeling and Sequence Prediction]]
- [[LLM-Based Behavior Simulators for Ads & Search]]
- [[Two-Tower Architecture]]
- [[Cross-Encoder Reranking]]
- [[Multi-Stage Recommendation Pipeline]]
