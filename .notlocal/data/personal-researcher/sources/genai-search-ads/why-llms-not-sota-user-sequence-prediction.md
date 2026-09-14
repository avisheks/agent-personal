---
title: "Why LLMs Are NOT SOTA at User Sequence Behavior Prediction — Deep Technical Analysis"
url: https://arxiv.org/abs/2404.08796
ingestedAt: 2026-06-08
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2408.14238
  - https://arxiv.org/abs/2502.13909
  - https://arxiv.org/abs/2312.02443
  - https://arxiv.org/abs/2305.11700
  - https://arxiv.org/abs/2310.19488
  - https://arxiv.org/abs/2404.11343
  - https://arxiv.org/abs/2303.13835
  - https://arxiv.org/abs/2310.15950
  - https://arxiv.org/abs/2402.09543
---

# Why LLMs Are NOT SOTA at User Behavior Sequence Prediction

## The Definitive Evidence

SASRec (0.83M params) beats LlamaRec (7B params) by 25.7% on NDCG@5 (Amazon Beauty). The 8,500x parameter gap actively HURTS — "Are LLM-based Recommenders Already the Best?" (arXiv:2408.14238).

## Six Technical Reasons

### 1. Architectural Mismatch

"The Elephant in the Room" (RecSys 2024): RECFORMER (Longformer, 12 layers) loses to SASRec (2 layers, 0.83M params). Layers 0-7 do intra-item token aggregation (unnecessary — an embedding lookup suffices). Only layers 8-11 do sequential preference modeling, and they converge to what SASRec does with 2 layers.

Language needs deep syntactic/semantic processing. Behavior sequences only need shallow transition pattern learning. Extra capacity = noise.

### 2. Positional/Order Blindness

"Lost in Sequence" (KDD 2025): When interaction sequences are SHUFFLED, LLM4Rec user representations change by only 1-7% (cosine sim 0.93-0.98). SASRec changes by 25-35% (sim 0.65-0.75).

LLMs treat interaction histories as UNORDERED BAGS. Positional encoding operates at token level, not interaction level. The sequential signal is buried in formatting text.

### 3. Token Vocabulary Problem

Language: ~100K tokens with rich learned semantics. Recommendations: millions of items with NO inherent semantic relationships in behavioral space. E4SRec: LLMs "often generate out-of-range results" — hallucinated items outside the catalog.

### 4. Text ≠ Behavior (Information-Theoretic Gap)

RLMRec (arXiv:2310.15950): Pure semantic embeddings achieve R@20 = 0.0199 vs CF baseline GCCF = 0.1343 on Amazon-Book — text contains only ~14% of useful signal that behavioral representations capture.

"Upper Limits of Text-Based CF" (arXiv:2305.11700): OPT-175B frozen achieves only HR@10=2.09 vs IDCF=6.79 on DSSM (3.2x deficit).

Text describes WHAT items ARE. Behavior reveals what items DO for users. These are distinct information sources.

### 5. Collaborative Filtering Signal Absent from Text

CoLLM (IEEE TKDE 2025): Text-only LLM AUC 0.7375 vs attention CF (DIN) 0.8163 on Amazon-Book. Two items with identical text descriptions can have completely different collaborative patterns.

A-LLMRec (KDD 2024): "LLMs underperform simple traditional CF models under warm scenarios due to lack of collaborative knowledge."

### 6. Generation ≠ Ranking

Lite-LLM4Rec: "beam search decoding is ultimately unnecessary for sequential recommendations." Recommendation is a scoring/ranking task, not a generation task. Converting to generation adds:
- Token-by-token overhead (sequential where parallel suffices)
- Output validity issues (hallucinated items)
- 97% efficiency loss

A "straight item projection head" — reverting to traditional scoring — achieves 46.8% better performance.

## The Fundamental Asymmetry

```
What LLMs Know:           What Prediction Needs:
───────────────           ──────────────────────
Item descriptions         Who bought what together
Review sentiments         Temporal transition probabilities  
Cultural context          Implicit negative feedback (non-clicks)
Shopping guides           Price sensitivity patterns
Product attributes        Session-level context effects
                          Power-law interaction distributions
```

No amount of text scaling can recover information that was never in text.

## What Would Make LLMs SOTA?

1. **Behavior pre-training**: +21% when PLM embeddings are tuned on interactions (Elephant paper)
2. **Hybrid injection**: CoLLM injects CF embeddings into LLM token space (+7.3% AUC)
3. **Distillation**: LLM-SRec distills CF-SRec into LLMs → achieves SOTA (KDD 2025)
4. **But**: all these require behavioral data, defeating the zero-shot advantage
