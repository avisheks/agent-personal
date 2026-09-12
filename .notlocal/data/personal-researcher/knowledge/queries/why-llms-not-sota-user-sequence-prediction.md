---
title: "Why are LLMs not SOTA at user sequence behavior prediction?"
summary: "Six reasons: (1) Over-capacity — SASRec 0.83M beats LlamaRec 7B by 25%; (2) Order-blind — shuffled sequences change LLM reps only 1-7%; (3) Vocab mismatch — millions of items vs 100K tokens; (4) Information gap — text holds ~14% of useful signal vs CF; (5) No collaborative signal in text; (6) Generation ≠ ranking. Fundamental: text describes what items ARE, behavior reveals what items DO for users. No text scaling recovers absent behavioral data."
type: query
createdAt: 2026-06-08
topic: genai-search-ads
---

# Why Are LLMs NOT SOTA at User Sequence Behavior Prediction?

## One-Line Answer

Because user behavior prediction depends on collaborative co-occurrence patterns and temporal transition dynamics that exist only in interaction logs, not in any text LLMs were trained on — and the task needs shallow transition learning (2 layers), not deep semantic processing (12+ layers).

## Six Technical Reasons

### 1. Architectural Over-Capacity = Noise

| Model | Params | Beauty NDCG@5 |
|-------|:------:|:-------------:|
| SASRec | 0.83M | 0.0510 |
| FMLP-Rec | 0.92M | 0.0507 |
| LlamaRec | 7,000M | 0.0405 |

**SASRec (0.83M) beats LlamaRec (7B) by 25.7%.** "The Elephant in the Room" (RecSys 2024) shows RECFORMER's layers 0-7 do work a simple embedding lookup already handles. Behavior needs 2 layers of transition learning, not 12+ layers of semantic processing.

### 2. Order Blindness

"Lost in Sequence" (KDD 2025): **Shuffling sequences changes LLM reps by only 1-7%** (cosine sim 0.93-0.98). SASRec changes by 25-35%. LLMs encode token-level position, not interaction-level temporal order. The sequential signal is buried in formatting.

### 3. Vocabulary Mismatch

Language: ~100K tokens with compositional semantics. Recommendation: millions of items with NO inherent behavioral relationships. LLMs hallucinate non-existent items because item IDs have no semantic grounding in text space.

### 4. Information-Theoretic Gap (~14% of Signal)

RLMRec: Pure semantic embeddings achieve R@20 = 0.0199 vs CF = 0.1343. **Text captures ~14% of the behavioral signal.** OPT-175B frozen still trails IDCF by 3.2x. Scaling doesn't close the gap because the information was never in text.

### 5. No Collaborative Filtering Signal in Text

CoLLM: Text-only LLM AUC = 0.7375 vs DIN (attention CF) = 0.8163. Two items with identical descriptions can have completely different collaborative patterns. "LLMs underperform simple traditional CF models under warm scenarios" (KDD 2024).

### 6. Generation ≠ Ranking

Recommendation is scoring/ranking, not generation. Lite-LLM4Rec: replacing generation with direct projection gives **+46.8% performance + 97% efficiency gain**. Beam search is "ultimately unnecessary for sequential recommendations."

## The Fundamental Theorem

> **Text describes what items ARE. Behavior reveals what items DO for users. These are distinct information sources with provably different mutual information with the prediction target.**

Latent factors that drive purchases — price sensitivity, quality perception, occasion-specific needs, social signaling — are encoded in behavioral co-occurrence patterns but absent from text descriptions. No amount of text scaling recovers information that was never in text.

## What Would Make LLMs SOTA?

All known paths require behavioral data (defeating the zero-shot advantage):
- Behavior pre-training of embeddings (+21%, RecSys 2024)
- CF embedding injection into LLM (+7.3% AUC, CoLLM)
- Distilling CF-SRec representations into LLMs (SOTA on Movies, KDD 2025)
- Using LLM for item initialization only, discarding at inference

## Optimal Architecture

```
Use LLM for:                Use SASRec/BERT4Rec for:
─────────────               ─────────────────────────
Cold-start items            Warm sequential prediction
Semantic understanding      Temporal transition modeling
Explainability              Collaborative filtering
Cross-domain transfer       Real-time scoring (<50ms)
Item initialization         Implicit feedback handling
```

## Key Papers

| Paper | Venue | Key Number |
|-------|-------|-----------|
| "Are LLM-based Rec the Best?" | 2024 | SASRec 0.83M > LlamaRec 7B by 25.7% |
| "Lost in Sequence" | KDD 2025 | Shuffled = 1-7% change (should be 25%+) |
| "The Elephant in the Room" | RecSys 2024 | Layers 0-7 wasted; behavior-tuned +21% |
| "Upper Limits of TCF" | 2023 | 175B still 3.2x below IDCF |
| CoLLM | TKDE 2025 | Text LLM 0.7375 vs CF 0.8163 AUC |
| RLMRec | 2023 | Semantic = ~14% of CF signal |
| Lite-LLM4Rec | 2024 | Removing generation = +46.8% perf |

## Sources

- [[Why LLMs Are NOT SOTA at User Sequence Prediction]] (knowledge page)
- [[LLM Quality for User Behavior Modeling and Sequence Prediction]]
- [[LLM-Based Behavior Simulators for Ads & Search]]
