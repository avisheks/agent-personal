# Knowledge Base Index

## General
- [Adoption Ceiling Problem](adoption-ceiling-problem.md) — The phenomenon where users only engage with the top few recommendations regardless of list quality, making improvements to lower-ranked items invisible to business metrics.
- [Cross-Attention Ranking](cross-attention-ranking.md) — A ranking approach where query and item tokens attend to each other to capture fine-grained interactions that dot-product similarity cannot model.
- [Double-Randomized Experimentation](double-randomized-experimentation.md) — An experimental design that randomizes both users and marketplace contexts to isolate causal effects in two-sided marketplaces where standard A/B testing fails due to interference.
- [FTRL Online Learning](ftrl-online-learning.md) — Follow-the-Regularized-Leader algorithm that enables real-time model updates with sparsity-inducing L1 regularization, particularly effective for high-dimensional sparse features in ads.
- [Model Calibration](model-calibration.md) — The requirement that predicted probabilities match observed frequencies, critical for auction-based systems where miscalibrated predictions directly impact bidding and revenue.
- [Multi-Stage Recommendation Pipeline](multi-stage-recommendation-pipeline.md) — A production architecture that separates candidate generation (recall-focused) from scoring/ranking (precision-focused) to efficiently handle both scale and quality in recommendation systems.
- [Position Bias Correction](position-bias-correction.md) — Methods like Inverse Propensity Weighting (IPW) that correct for the confounding effect of item position on user clicks in recommendation training data.
- [Two-Tower Architecture](two-tower-architecture.md) — A neural network architecture with separate encoders for queries and items that enables fast retrieval through pre-computed embeddings but limits interaction modeling to dot products.
