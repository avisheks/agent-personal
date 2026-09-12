---
title: "position-bias-correction"
summary: ""
sources:
  - recommendation-ranking/recommendation-ranking-ref.md
createdAt: 2026-05-18T18:37:44.373884+00:00
updatedAt: 2026-05-18T18:37:44.373884+00:00
---
# Position Bias Correction

Position bias correction is a critical technique in recommendation and ranking systems that addresses the systematic bias introduced when users interact with items based on their display position rather than their true relevance. This bias occurs because users are more likely to click on items shown at higher positions (e.g., top of a list or search results) regardless of the item's actual quality or relevance to their needs.

## The Position Bias Problem

Position bias manifests when the probability of user interaction depends on both the item's relevance and its display position. Users exhibit a strong tendency to examine and click items at the top of lists, creating a confounding effect where P(click | item, position) ≠ P(click | item). This leads to a feedback loop where items that appear at higher positions receive more clicks, which in turn causes ranking algorithms to learn that these items should be ranked higher, perpetuating the bias. ^[recommendation-ranking-ref.md]

The most common model for understanding this bias is the Position-Based Model (PBM), which assumes that click probability factorizes as: P(click | item i, position k) = P(relevant | item i) × P(examine | position k), where P(relevant | item i) represents the true item relevance and P(examine | position k) represents the probability that a user examines an item at position k. ^[recommendation-ranking-ref.md]

## Correction Methods

### Inverse Propensity Weighting (IPW)

The most widely used approach for position bias correction is Inverse Propensity Weighting. This method weights each training example by the inverse of the examination probability: w_ik = 1 / P(examine | position k). Items at position 1 (where P(examine) ≈ 1.0) receive weight ≈ 1, while items at position 10 (where P(examine) ≈ 0.3) receive weight ≈ 3.3. This up-weighting of clicks from lower positions makes them more informative, as users who click items far down the list have made a more deliberate choice. ^[recommendation-ranking-ref.md]

### Position-Aware Modeling

An alternative approach includes position as an explicit feature during model training. At inference time, the position is set to a neutral value (such as 0 or the average position) to obtain position-debiased scores. This allows the model to learn the separate contributions of position and item relevance to click probability. ^[recommendation-ranking-ref.md]

### Randomization Experiments

Some systems use randomization experiments where a small percentage of results (typically 1-5%) are randomly shuffled. Clicks on randomly-positioned items provide unbiased signals that can be used for calibration, though this approach comes with the cost of slightly degraded user experience on the randomized traffic. ^[recommendation-ranking-ref.md]

## Estimation of Examination Probabilities

Accurate position bias correction requires reliable estimates of P(examine | position k). Several methods exist for obtaining these estimates:

- **Randomization-based estimation**: Using data from randomized experiments to directly observe examination probabilities
- **EM algorithms**: Jointly estimating examination and relevance probabilities from observational data without requiring randomization
- **Regression discontinuity**: Exploiting natural breaks in page layout (such as above/below the fold) to compare click rates

The quality of propensity estimation is critical, as incorrect estimates can make the correction worse than no correction at all. ^[recommendation-ranking-ref.md]

## Limitations and Challenges

Position bias correction faces several practical challenges. The IPW approach can suffer from high variance when examination probabilities are very small, leading to extremely large weights that amplify noise. To address this, practitioners often clip weights at a maximum threshold (typically 10-20) to trade some bias for much lower variance. ^[recommendation-ranking-ref.md]

The Position-Based Model assumption may be violated when examination probability depends on item characteristics beyond position. For example, users may examine items because they appear relevant based on thumbnails, titles, or other visual cues, creating dependencies that the simple factorization cannot capture. ^[recommendation-ranking-ref.md]

Additionally, presentation bias extends beyond position to include factors like item images, titles, prices, and rating badges that all affect examination probability. While position is typically the largest factor, these other elements can also introduce systematic biases. ^[recommendation-ranking-ref.md]

## Production Considerations

In production recommendation systems, position bias correction has proven essential for maintaining fair exposure across items in the catalog. Without correction, popular items that historically appeared at high positions accumulate disproportionate positive signals, making long-tail items effectively invisible to users. This creates a self-reinforcing cycle that reduces catalog diversity and can harm marketplace health. ^[recommendation-ranking-ref.md]

The correction is particularly important for systems that optimize for long-term metrics like user retention and marketplace diversity, even if it may temporarily reduce short-term engagement metrics like click-through rate. The trade-off typically involves accepting a small decrease in immediate CTR in exchange for better long-term catalog coverage and user experience diversity. ^[recommendation-ranking-ref.md]

## Related Concepts

Position bias correction is closely related to other debiasing techniques in machine learning, including [[Model Calibration]] methods that ensure predicted probabilities match observed rates, and [[Multi-Objective Optimization]] approaches that balance relevance with diversity and fairness objectives. It also connects to [[FTRL Online Learning]] systems that must continuously adapt to changing user behavior while maintaining unbiased training signals.
