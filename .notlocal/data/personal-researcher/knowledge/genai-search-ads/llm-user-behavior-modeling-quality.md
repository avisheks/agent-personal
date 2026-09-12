---
title: LLM Quality for User Behavior Modeling and Sequence Prediction
summary: "LLMs show 'moderate proficiency' on sequential rec tasks (5-20% below SASRec/BERT4Rec). Excel at: cold-start, conversational rec, demographic simulation, re-ranking. Fail at: sequential patterns, temporal dynamics, behavioral diversity, position/popularity bias. Root cause: models encode declared preferences (reviews) not revealed preferences (clicks)."
sources:
  - sources/genai-search-ads/llm-user-behavior-modeling-quality.md
createdAt: 2026-06-08
updatedAt: 2026-06-08
---

# LLM Quality for User Behavior Modeling and Sequence Prediction

## Verdict

LLMs are **moderately useful** for user behavior modeling — better than nothing in cold-start, worse than specialized models when behavioral data exists. The fundamental gap is structural: LLMs encode what people *say about* behavior (reviews, forums) but lack what people *actually do* (clicks, sessions, dwell times).

## Scorecard

| Capability | LLM Quality | vs Traditional Models |
|-----------|:-----------:|:--------------------:|
| Cold-start recommendation | Strong | Better (world knowledge compensates) |
| Conversational rec | Excellent | Dominates even without fine-tuning |
| Explainability | Strong | Comparable to SOTA |
| Demographic simulation | Strong | Captures "far beyond surface similarity" |
| Re-ranking (10-20 items) | Good | Competitive with baselines |
| Sequential prediction (next-item) | Moderate | 5-20% below SASRec/BERT4Rec |
| Temporal pattern recognition | Poor | Fails — "struggle to perceive order of interactions" |
| Full-catalog retrieval | Fails | Cannot compete without external retrieval |
| Behavioral diversity | Poor | Hyper-accuracy distortion (too average) |
| Individual-level prediction | Poor | Models aggregate, not individual patterns |

## Documented Successes

| Finding | Source | Year |
|---------|--------|------|
| Zero-shot GPT-3 outperforms some trained seq models (MovieLens 100K) | Wang & Lim | 2023 |
| Outperforms fine-tuned conversational rec models without fine-tuning | He et al. (CIKM) | 2023 |
| Simulated behavior "very close to real humans" (info cocoons) | RecAgent | 2023 |
| 50x cheaper than crowdworkers with high agreement | AlpacaFarm | 2023 |
| Captures fine-grained demographic correlations | Argyle et al. (Political Analysis) | 2023 |
| Replicates classic behavioral economics experiments | Horton (Homo Silicus) | 2023 |
| Recovers human-like developmental stages | Salewski et al. (NeurIPS Spotlight) | 2023 |

## Documented Failures

| Finding | Source | Year |
|---------|--------|------|
| "Only moderate proficiency" on sequential/direct rec accuracy | LLMRec (CIKM) | 2023 |
| "Struggle to perceive the order of historical interactions" | LLMRank (ECIR) | 2024 |
| "Strong primacy effect" — position bias in selections | Eicher & Irgolic | 2024 |
| Popularity bias independent of personalization | LLMRank | 2024 |
| "Hyper-accuracy distortion" — too perfect vs real humans | Aher et al. (Turing Experiments) | 2023 |
| Hallucinate non-existent items in recommendations | Di Palma et al. | 2023 |
| Preference ranking accuracy < 60% for RLHF models | Chen et al. | 2024 |
| Dark Triad scores higher than human average | Li et al. | 2023 |

## Why LLMs Succeed

1. **Pre-training data**: Reviews, forums, shopping guides, cultural knowledge → rich "world knowledge" about preferences
2. **Language understanding**: Can parse complex preference descriptions, item attributes, contextual signals
3. **Zero-shot transfer**: General knowledge applies to new domains without domain-specific training
4. **Conversational fit**: Recommendation IS a language task when framed conversationally

## Why LLMs Fail

1. **No behavioral data in training**: Click logs, session sequences, dwell times, private purchase history are NOT in pre-training corpora
2. **Declared vs revealed preferences**: LLMs model what people SAY they want (reviews) ≠ what they DO (clicks)
3. **RLHF misalignment**: Alignment training optimizes for helpfulness, not behavioral realism — models avoid dark patterns, impulsivity, irrationality
4. **Position/order blindness**: Transformer attention doesn't naturally encode sequential temporal importance of behavioral items
5. **Average person convergence**: Generation tends toward modal/mainstream behavior; no temperature setting produces realistic diversity distribution
6. **Catalog grounding**: Without knowledge of actual inventory/availability, LLMs hallucinate items

## When to Use LLMs vs Traditional Models

| Use Case | Best Approach | Why |
|----------|--------------|-----|
| New user (no history) | LLM | World knowledge > no data |
| Sequential prediction (long history) | SASRec/BERT4Rec | Trained on actual sequences |
| Conversational intent understanding | LLM | Natural language is the medium |
| Simulating aggregate demographics | LLM | Captures cultural patterns well |
| Individual behavior prediction | Traditional | Needs observed behavioral data |
| A/B test pre-screening | LLM (with calibration) | Cheap hypothesis filter; validate with real test |
| Precision ranking | Traditional + LLM re-rank | Two-stage: retrieve then re-rank |

## The Structural Gap (Cannot Be Closed Without Behavioral Fine-Tuning)

```
LLM Training Data:           Actual User Behavior:
─────────────────            ─────────────────────
Reviews & ratings            Click sequences
Forum discussions            Dwell times / scroll depth
Shopping guides              Cart abandonment patterns
News articles                Price sensitivity signals
Social media posts           Impulse vs planned behavior
                             Session context effects
                             Private browsing behavior
```

Fine-tuning on behavioral data closes this gap but defeats the zero-shot advantage and requires the very data that makes traditional models work.

## Related

- [[LLM-Based Behavior Simulators for Ads & Search]]
- [[Gen-AI Applied to Search and Advertising (2024-2026)]]
- [[Two-Tower Architecture]]
- [[Cross-Encoder Reranking]]
