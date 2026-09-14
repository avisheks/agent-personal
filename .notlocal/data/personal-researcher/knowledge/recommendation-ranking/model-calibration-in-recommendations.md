---
title: "model-calibration-in-recommendations"
summary: ""
sources:
  - recommendation-ranking/recommendation-ranking-ref.md
createdAt: 2026-05-18T18:34:25.059302+00:00
updatedAt: 2026-05-18T18:34:25.059302+00:00
---
# Model Calibration in Recommendations

**Model Calibration in Recommendations** refers to ensuring that predicted probabilities from recommendation models accurately reflect the true likelihood of user actions. In a well-calibrated model, when the system predicts a 30% probability of a user clicking an item, approximately 30% of items with that prediction should actually be clicked across all instances.

## Definition and Importance

Model calibration ensures that predicted probabilities reflect true likelihoods rather than just relative rankings. This distinction is critical in systems where probability estimates drive downstream decisions, particularly in auction-based environments and recommendation systems where monetary bids are calculated based on predicted conversion probabilities. ^[recommendation-ranking-ref.md]

In recommendation systems, calibration matters more than in general machine learning applications because miscalibrated predictions directly impact business outcomes. When auction bids are computed as `bid = value × P(conversion)`, systematic over-estimation by 2x causes advertisers to bid twice as much as optimal, wasting budget and eroding trust. Conversely, under-estimation by 2x leads to under-bidding, reduced impressions, and lost value. ^[recommendation-ranking-ref.md]

## Measuring Calibration

### Expected Calibration Error (ECE)

The standard metric for measuring calibration is Expected Calibration Error:

1. Bin predictions into B buckets by predicted probability
2. For each bucket b:
   - accuracy(b) = fraction of positives in bucket
   - confidence(b) = mean predicted probability in bucket
3. ECE = Σ_b (|bucket_b| / N) × |accuracy(b) - confidence(b)|

Well-calibrated models typically achieve ECE < 0.02, while uncalibrated deep neural networks often exhibit ECE = 0.05-0.10. ^[recommendation-ranking-ref.md]

## Sources of Miscalibration

### Distribution Shift
Models trained on historical data may become miscalibrated when the underlying data distribution changes due to seasonality, new products, or market dynamics. A model trained on last month's click-through rates may systematically over or under-predict when user behavior patterns shift. ^[recommendation-ranking-ref.md]

### Position Bias
Training data from recommendation systems often contains [[Position Bias Correction]], where items at higher positions receive more clicks regardless of their true relevance. Models trained on this biased data tend to overpredict click probabilities for items typically shown at high positions. ^[recommendation-ranking-ref.md]

### Negative Sampling
Training with random negative examples rather than true negatives can inflate predicted probabilities, as the model learns to distinguish between obviously relevant and obviously irrelevant items rather than making fine-grained relevance judgments. ^[recommendation-ranking-ref.md]

### Model Architecture
Deep neural networks are notoriously poorly calibrated out-of-the-box, often producing overconfident predictions. This tendency toward miscalibration increases with model complexity and depth. ^[recommendation-ranking-ref.md]

## Calibration Methods

### Platt Scaling
Platt scaling learns a logistic transformation: P_calibrated = σ(a × logit + b), where parameters a and b are fitted on a held-out calibration set. This method assumes the calibration function follows a sigmoid shape. ^[recommendation-ranking-ref.md]

### Isotonic Regression
Isotonic regression provides a non-parametric monotone mapping from raw model scores to calibrated probabilities. This approach is more flexible than Platt scaling as it doesn't assume a specific functional form for the calibration curve. ^[recommendation-ranking-ref.md]

### Temperature Scaling
For neural networks, temperature scaling applies a single parameter T to soften the output: P_calibrated = σ(logit / T). The temperature T is learned on held-out validation data. This is the simplest neural network calibration method. ^[recommendation-ranking-ref.md]

## Production Considerations

### Maintenance Schedule
Calibration requires ongoing maintenance as data distributions shift over time. Production systems typically re-calibrate weekly using isotonic regression on fresh data to maintain ECE below acceptable thresholds. ^[recommendation-ranking-ref.md]

### Multi-Market Calibration
Global recommendation systems serving multiple markets face the challenge that different regions have different base rates for user actions. A single global calibration function would systematically over-predict for low-engagement markets and under-predict for high-engagement markets. The solution involves fitting per-locale calibration functions on locale-specific holdout data. ^[recommendation-ranking-ref.md]

### Business Impact
Poor calibration can mask improvements in model quality. When a new ranking model achieves better relevance metrics but remains poorly calibrated, the business impact may be invisible until calibration is corrected. Calibration serves as a bridge between model improvements and measurable business outcomes. ^[recommendation-ranking-ref.md]

## Related Concepts

Model calibration intersects with several other recommendation system concepts:

- [[Position Bias Correction]] addresses one major source of training data bias that leads to miscalibration
- [[Double-Randomized Experimentation]] provides unbiased evaluation of calibrated models in marketplace settings
- [[Two-Tower Architecture]] and other model architectures may require different calibration approaches
- [[Multi-Stage Recommendation Pipeline]] systems need calibration at each stage where probability estimates are used
