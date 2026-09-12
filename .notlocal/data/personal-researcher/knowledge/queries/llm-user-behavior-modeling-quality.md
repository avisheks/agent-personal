---
title: "How good are LLMs at user behavior modeling and sequence prediction? Successes and failures?"
summary: "Moderate — 5-20% below SASRec/BERT4Rec on sequential tasks. Excel at cold-start, conversational rec, demographic simulation. Fail at temporal patterns, behavioral diversity, position bias. Root cause: LLMs encode declared preferences (reviews) not revealed preferences (clicks). Structural gap won't close without behavioral fine-tuning."
type: query
createdAt: 2026-06-08
topic: genai-search-ads
---

# How Good Are LLMs at User Behavior Modeling?

## One-Line Answer

**Moderate** — useful for cold-start and demographic simulation, but 5-20% below specialized sequential models (SASRec/BERT4Rec) on fine-grained behavior prediction.

## Where LLMs Excel

| Strength | Evidence | Why |
|----------|----------|-----|
| Cold-start (no user history) | GPT-3 beats trained seq models on MovieLens 100K zero-shot | World knowledge compensates for missing data |
| Conversational recommendation | Outperforms fine-tuned CRS models WITHOUT fine-tuning (CIKM 2023) | Language IS the medium |
| Demographic simulation | "Far beyond surface similarity" (Argyle, Political Analysis 2023) | Cultural patterns in pre-training data |
| Behavioral economics replication | Qualitatively matches classic experiments (Homo Silicus, 2023) | Social science knowledge encoded |
| Re-ranking (10-20 items) | Competitive with baselines, especially books domain | Good at comparative judgment |
| Cheap behavior hypothesis generation | 50x cheaper than crowdworkers (AlpacaFarm) | Speed + cost for screening |

## Where LLMs Fail

| Failure | Evidence | Why |
|---------|----------|-----|
| Sequential prediction | "Only moderate proficiency" (LLMRec, CIKM 2023) | No click-sequence data in pre-training |
| Temporal order perception | "Struggle to perceive order of interactions" (LLMRank, ECIR 2024) | Attention doesn't encode temporal importance |
| Position bias | "Strong primacy effect" — first items over-selected (Eicher & Irgolic, 2024) | Cognitive load → heuristic fallback |
| Popularity bias | Well-known items get unfair preference (LLMRank) | Frequency in training data = salience |
| Behavioral diversity | "Hyper-accuracy distortion" — too perfect (Aher, 2023) | RLHF optimizes helpfulness, not realism |
| Individual-level prediction | Converges to "average person" | No individual behavioral signal |
| Impulsive/irrational behavior | Cannot simulate | RLHF makes models rational + helpful |
| Catalog grounding | Hallucinate non-existent items (Di Palma, 2023) | No inventory/availability knowledge |

## Root Cause: Declared vs Revealed Preferences

LLMs are trained on what people *write about* their preferences (reviews, forums, guides) — **declared preferences**. But actual user behavior is driven by **revealed preferences** (what they click, dwell on, buy, abandon) which are private and not in any pre-training corpus.

This is a **structural gap**: the data that would make LLMs good behavior predictors (click logs, session sequences, dwell times) is exactly the proprietary behavioral data that makes traditional models work. Fine-tuning on it defeats the zero-shot advantage.

## Practical Recommendation

| Task | Use LLM? | Alternative |
|------|:--------:|------------|
| New user, no history | Yes | — |
| Testing ad creative appeal (qualitative) | Yes | — |
| Simulating demographic segments | Yes | — |
| Predicting next click in session | No | SASRec, BERT4Rec |
| Predicting conversion probability | No | Trained classifier on log data |
| A/B test pre-screening | Yes (with calibration) | Then validate with real test |
| Full personalized recommendation | No | Two-tower + behavioral model |

## Key Numbers

- LLM sequential rec accuracy: **5-20% below** SASRec/BERT4Rec (NDCG/HitRate)
- AlpacaFarm: **50x cheaper** than crowdworkers, high human agreement
- Preference ranking accuracy (RLHF models): **< 60%** (Chen et al., 2024)
- Position bias: **"strong primacy effect"** (Eicher & Irgolic, 28 pages of measurements)
- RecAgent behavioral fidelity: **"very close to real humans"** (qualitative, not quantified)

## Sources

- [[LLM Quality for User Behavior Modeling and Sequence Prediction]]
- [[LLM-Based Behavior Simulators for Ads & Search]]
- LLMRec (CIKM 2023), LLMRank (ECIR 2024), RecAgent (2023)
- Argyle et al. (Political Analysis 2023), Horton (Homo Silicus, 2023)
- AlpacaFarm (2023), Agent4Rec (SIGIR 2024)
