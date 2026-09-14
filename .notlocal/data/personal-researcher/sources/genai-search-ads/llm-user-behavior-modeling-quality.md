---
title: How Good Are LLMs at User Behavior Modeling and Sequence Prediction?
url: https://arxiv.org/abs/2305.19860
ingestedAt: 2026-06-08
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2306.15498
  - https://arxiv.org/abs/2305.08845
  - https://arxiv.org/abs/2308.10149
  - https://arxiv.org/abs/2310.10108
  - https://arxiv.org/abs/2304.03153
  - https://arxiv.org/abs/2301.13838
  - https://arxiv.org/abs/2305.02412
  - https://arxiv.org/abs/2305.10263
---

# LLMs for User Behavior Modeling — Quality Assessment

## Overall Verdict

LLMs show "only moderate proficiency" on accuracy-based sequential recommendation tasks (LLMRec, CIKM 2023). They consistently underperform specialized models (SASRec, BERT4Rec, GRU4Rec) by 5-20% NDCG on fine-grained behavioral prediction. They excel at: cold-start, conversational recommendation, explainability, demographic simulation, and re-ranking small candidate sets.

## Successes

### Cold-Start / Zero-Shot
- GPT-3 with 3-step prompting outperforms some trained sequential models on MovieLens 100K (Wang & Lim, 2023)
- RecMind (NAACL 2024): Zero-shot approaches P5 performance with Self-Inspiring planning
- ChatGPT excels in cold-start and re-ranking (Di Palma et al., 2023)

### Conversational Recommendation
- LLMs outperform fine-tuned conversational rec models even WITHOUT fine-tuning (He et al., CIKM 2023)

### Demographic Simulation ("Silicon Samples")
- Argyle et al. (Political Analysis, 2023): GPT-3 conditioned on demographics produces responses capturing "complex interplay between ideas, attitudes, and socio-cultural context" — "far beyond surface similarity"
- Homo Silicus (Horton et al., 2023): Replicates classic behavioral economics experiments qualitatively

### Behavioral Fidelity
- RecAgent (2023): Simulated behaviors "very close to real humans" for information cocoons/conformity
- AlpacaFarm (2023): 50x cheaper than crowdworkers, high agreement with humans on preference judgments
- In-Context Impersonation (NeurIPS 2023 Spotlight): LLMs recover human-like developmental stages

## Failures

### Position & Popularity Bias
- LLMRank (ECIR 2024): "Strong primacy effect" — first items disproportionately selected
- Eicher & Irgolic (2024): "LLMs experience cognitive load compensated for with bias"; guard rails "increase bias"
- LLMs "can be biased by popularity" independent of personalization fit

### Sequential Order Perception
- LLMRank: LLMs "struggle to perceive the order of historical interactions" — critical for temporal behavioral patterns

### Hyper-Accuracy Distortion
- Aher et al. (2023, "Turing Experiments"): Models produce TOO-PERFECT responses not matching noise/irrationality of real humans

### The "Average Person" Problem
- RLHF makes models helpful, not realistic — poor at simulating impulsive, irrational, or malicious behavior
- LLMs on personality inventories score higher than human average on Dark Triad (Li et al., 2023)
- No temperature setting produces realistic behavioral variance distribution

### Hallucination
- Di Palma et al. (2023): LLMs recommend non-existent items, requiring post-processing pipelines

### Preference Ranking Accuracy
- Chen et al. (2024): "Most state-of-the-art preference-tuned models achieve ranking accuracy < 60%"

## Root Cause Analysis

### Why LLMs Succeed
- Pre-training includes: product reviews, shopping guides, forum discussions, cultural knowledge, social science literature
- This gives "world knowledge" about preferences, demographics, item popularity

### Why LLMs Fail
- Pre-training DOES NOT include: click logs, session sequences, impression data, dwell times, scroll patterns, private purchase history
- Fundamental gap: LLMs model DECLARED preferences (what people say) not REVEALED preferences (what people do)
- RLHF optimizes for helpfulness, not behavioral realism
- No training signal for temporal dynamics, price sensitivity, or impulsive behavior

### The Structural Gap
"World knowledge vs behavioral knowledge" — LLMs know ABOUT behavior from text descriptions but have never observed actual behavioral sequences. This is unlikely to close without direct behavioral fine-tuning, which defeats the zero-shot advantage.
