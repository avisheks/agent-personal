---
title: "Model Calibration"
summary: "The requirement that predicted probabilities match observed frequencies, critical for auction-based systems where miscalibrated predictions directly impact bidding and revenue."
sources:
  - recommendation-ranking-ref.md
createdAt: 2026-05-17T15:16:26.302947+00:00
updatedAt: 2026-05-17T15:16:26.302947+00:00
---
# Model Calibration

**Model Calibration** refers to the alignment between a machine learning model's predicted probabilities and the actual observed frequencies of outcomes. A well-calibrated model produces predictions where, for example, when the model predicts a 70% probability of an event occurring, that event actually occurs approximately 70% of the time across all instances with similar predictions.

## Definition and Importance

Model calibration ensures that predicted probabilities reflect true likelihoods rather than just relative rankings. Formally, a model is perfectly calibrated when the expected outcome equals the predicted probability: E[y | ŷ = p] = p for all probability values p. ^[recommendation-ranking-ref.md]

Calibration becomes critically important in systems where predicted probabilities directly influence business decisions. In auction-based advertising systems, bids are computed as: `bid = value × P(conversion)`. If P(conversion) is systematically overestimated by 2x, advertisers bid twice as much as they should, waste budget, lose trust, and eventually churn. Conversely, underestimated probabilities lead to underbidding, lost impressions, and reduced value for advertisers. ^[recommendation-ranking-ref.md]

## Measuring Calibration

### Expected Calibration Error (ECE)

The most common metric for measuring calibration is Expected Calibration Error (ECE):

1. Bin predictions into B buckets by predicted probability
2. For each bucket b:
   - accuracy(b) = fraction of positives in bucket
   - confidence(b) = mean predicted probability in bucket
3. ECE = Σ_b (|bucket_b| / N) × |accuracy(b) - confidence(b)|

Good calibration typically requires ECE < 0.02, while typical uncalibrated deep neural networks often exhibit ECE = 0.05-0.10. ^[recommendation-ranking-ref.md]

## Why Models Become Miscalibrated

Several factors contribute to poor model calibration:

**Distribution Shift**: Models trained on historical data may become miscalibrated when the underlying data distribution changes due to seasonality, new products, or market shifts. ^[recommendation-ranking-ref.md]

**Position Bias**: In recommendation systems, models trained on position-biased click data tend to overpredict click-through rates for items typically shown at high positions. ^[recommendation-ranking-ref.md]

**Negative Sampling**: Training with random negatives rather than true negatives can inflate predicted probabilities, as the model learns to distinguish between obviously relevant and obviously irrelevant items rather than making fine-grained distinctions. ^[recommendation-ranking-ref.md]

**Model Architecture**: Deep neural networks are notoriously poorly calibrated out of the box, often producing overconfident predictions even when they are incorrect. ^[recommendation-ranking-ref.md]

## Calibration Methods

### Platt Scaling

Platt scaling learns a logistic transformation: P_calibrated = σ(a × logit + b), where parameters a and b are fit on a held-out calibration set. This method is simple and effective for binary classification problems. ^[recommendation-ranking-ref.md]

### Isotonic Regression

Isotonic regression provides a non-parametric monotone mapping from raw scores to calibrated probabilities. This approach is more flexible than Platt scaling and can capture non-linear relationships between predicted and actual probabilities. ^[recommendation-ranking-ref.md]

### Temperature Scaling

For neural networks, temperature scaling applies a single parameter T to soften the predictions: P_calibrated = σ(logit / T). The temperature T is learned on held-out data. This is the simplest neural network calibration method and often performs surprisingly well. ^[recommendation-ranking-ref.md]

## Production Considerations

### Maintaining Calibration Over Time

Calibration requires ongoing maintenance in production systems. Models can drift out of calibration as data distributions change, requiring regular recalibration using fresh data. Weekly recalibration using isotonic regression on recent data is a common practice. ^[recommendation-ranking-ref.md]

### Multi-Market Calibration

For systems serving multiple geographic markets or user segments, per-segment calibration may be necessary. Each locale or segment may have different base rates (e.g., Japan CTR ≈ 1.5%, US CTR ≈ 3%, Germany CTR ≈ 2.2%), requiring locale-specific calibration functions to avoid systematic over- or under-prediction. ^[recommendation-ranking-ref.md]

### Calibration vs. Ranking Quality

Calibration corrections typically preserve ranking quality while improving probability estimates. The ranking order of items generally remains unchanged, but the confidence scores become more reliable for downstream decision-making. ^[recommendation-ranking-ref.md]

## Applications in Recommendation Systems

In recommendation and ranking systems, calibration serves multiple purposes beyond auction bidding. Well-calibrated models enable better [[Multi-Objective Optimization]] by providing reliable probability estimates for different objectives. They also support more effective [[Position Bias]] correction techniques that rely on accurate probability estimates. ^[recommendation-ranking-ref.md]

Calibration becomes particularly important when combining predictions from multiple models or when using model outputs to make automated decisions about content promotion, budget allocation, or risk assessment. ^[recommendation-ranking-ref.md]
