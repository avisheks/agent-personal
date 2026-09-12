# Fine-Tuning with Noisy Labels

> **Last Updated:** 2026-05-31 | **Read time:** ~25 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Learning with noisy labels has evolved from simple loss reweighting [12] to hybrid semi-supervised approaches like DivideMix [3] that treat noisy samples as unlabeled data.
> Key players: Confident Learning/cleanlab [1], Co-teaching [2], DivideMix [3], symmetric losses [8]. Main open problem: handling instance-dependent noise where corruption probability varies per sample [6].
> Recent breakthrough: Wei et al. (2022) demonstrated that real-world human annotation noise is far more structured than synthetic noise benchmarks suggest [9]. Trend: data-centric AI treats label quality as the primary lever for model improvement.

## State of the Art

### Current Best Approaches

- **DivideMix** — Models noisy labels via BMM, splits data into clean/noisy sets, applies MixMatch semi-supervised learning on both; SOTA on CIFAR with 90% noise [3]
- **Confident Learning (cleanlab)** — Estimates the joint distribution of noisy and true labels using out-of-fold predictions; identifies and removes/corrects mislabeled samples [1]
- **Co-teaching+** — Two networks train simultaneously, each feeding the other small-loss samples while disagreement filtering prevents convergence to same errors [2]
- **Forward/Backward Loss Correction** — Estimates the noise transition matrix T and uses it to correct the loss function during training [7]
- **Symmetric Cross Entropy** — Combines standard CE with reverse CE to achieve noise-tolerance guarantees under both symmetric and asymmetric noise [4]

### Recent Breakthroughs (last 12 months)

- **Real-world noise characterization** (2022): Wei et al. showed that human annotation noise on CIFAR-10N is instance-dependent and far less uniform than synthetic benchmarks assume [9]
- **AUM ranking** (2020): Area Under the Margin provides a training-free metric to rank samples by mislabel likelihood without retraining [10]
- **Flooding regularization** (2020): Ishida et al. showed that preventing training loss from reaching zero improves generalization under noise by keeping models in a "flat minima" region [14]
- **Anchor-point estimation** (2019): Xia et al. proved that anchor points (samples belonging to a single class with probability 1) suffice to estimate noise rates without clean validation data [15]

### Open Problems

- **Instance-dependent noise**: Most methods assume class-conditional noise; real-world noise depends on individual sample difficulty [6][9]
- **Scaling to foundation models**: Noise-robust methods developed on CIFAR/ImageNet may not transfer to billion-parameter LLM fine-tuning
- **Open-set noise**: Samples from out-of-distribution classes mixed into training data violate closed-set assumptions
- **Combining noisy labels with noisy features**: Joint corruption of inputs and labels remains theoretically underexplored

## Executive Summary

Fine-tuning with noisy labels addresses the reality that 5-40% of real-world training annotations contain errors [1][6], and neural networks memorize these errors after initially learning clean patterns [5]. The core architectural decision is **filtering** (remove suspected noisy samples) vs **correction** (estimate true labels or modify the loss function to tolerate noise).

- **Choose filtering** (Co-teaching [2], cleanlab [1]) when data is abundant and noise is random
- **Choose loss correction** (forward T-correction [7], symmetric losses [8]) when data is scarce or noise transition matrix is estimable
- **Choose hybrid** (DivideMix [3]) when noise rates exceed 40% and you need maximum accuracy

**The killer framing:** "DNNs memorize clean patterns first and noisy labels later [5] — every robust training method exploits this temporal signal, either by early stopping, small-loss selection, or curriculum ordering."

Cost headline: Confident Learning [1] adds <5% preprocessing cost but typically recovers 5-15% of lost accuracy by removing 10-30% of the noisiest samples.

```
Decision Tree: Handling Label Noise
────────────────────────────────────
Know the noise transition matrix T?
├── YES → Loss correction: L_corrected = T^(-1) * L [7]
│   └── T estimated via anchor points? [15]
│       ├── YES → Forward correction (unbiased)
│       └── NO → Estimate T via confident learning [1]
└── NO → Use sample selection
    ├── Noise rate < 20% → Confident Learning + filter [1]
    ├── Noise rate 20-50% → Co-teaching / DivideMix [2][3]
    └── Noise rate > 50% → DivideMix + semi-supervised [3]
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Noise characterization | Symmetric vs asymmetric noise? Estimated noise rate? Is clean validation data available? Target accuracy vs baseline on clean data. |
| 2. Identify constraints | Data budget and compute | Dataset size (filtering is wasteful if small); GPU budget (Co-teaching needs 2x models); availability of anchor points for T estimation [15]. |
| 3. Propose baseline | Standard CE with early stopping | Train with cross-entropy, monitor val loss, stop before memorization [5]. This exploits the learning-then-memorizing dynamic as a free baseline. |
| 4. Identify gaps | Memorization detection | Plot per-sample loss trajectories; identify when clean/noisy loss curves diverge [5][10]. Measure AUM to rank suspicious samples [10]. |
| 5. Introduce improvements | Noise-aware training | Add confident learning for filtering [1], or switch to symmetric loss [4], or deploy Co-teaching [2] based on noise rate assessment. |
| 6. Add evaluation + guardrails | Clean holdout + noise auditing | Evaluate on verified-clean test set; monitor noise detection precision/recall; track label flip statistics across training runs. |
| 7. Discuss scaling tradeoffs | Cost of robustness at scale | Confident learning needs N*K cross-val passes [1]; Co-teaching doubles model count [2]; DivideMix requires warmup epochs [3]. Trade compute for accuracy. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Noise handling approach | Filter noisy samples [1] | Correct the loss function [7] | Data is abundant (>100K), noise is random | Data is scarce, noise matrix T is estimable |
| Loss function | Symmetric CE [4] | Standard CE + reweighting [11] | Need drop-in replacement, moderate noise | Have importance weights or clean validation set |
| Training strategy | Co-teaching (two networks) [2] | Single network + mixup/DivideMix [3] | Noise rate < 40%, need simplicity | Noise rate > 40%, willing to accept complexity |
| Sample scoring | Cross-val predicted probs [1] | AUM ranking [10] | Need per-class noise estimates | Need fast, training-free ranking |
| Curriculum design | Self-paced (easy-to-hard) [13] | Anti-curriculum (hard-to-easy) | Standard noise, sufficient data | Need to identify boundary cases early |

## System Design Walkthrough

### Opening Frame

Label noise is not a data-cleaning chore — it is the primary bottleneck in production ML where annotation error rates compound across retraining cycles. The non-obvious insight: DNNs learn clean patterns in early epochs and memorize noise later [5], giving us a temporal signal that every robust method exploits — from small-loss selection to curriculum learning to AUM scoring.

### Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                 Noise-Robust Fine-Tuning Pipeline              │
├─────────────┬─────────────────┬───────────────┬───────────────┤
│ Detection   │  Correction     │  Training     │  Validation   │
├─────────────┼─────────────────┼───────────────┼───────────────┤
│ Cross-val   │ T-matrix [7]    │ Co-teaching[2]│ Clean holdout │
│ probs [1]   │ Relabeling      │ DivideMix [3] │ AUM rank [10] │
│ AUM [10]    │ Anchor pts [15] │ Sym. loss [4] │ Noise audit   │
│ Loss curves │ Importance wt   │ Curriculum[13]│ Flip tracking │
└─────────────┴─────────────────┴───────────────┴───────────────┘
       │               │                │               │
       ▼               ▼                ▼               ▼
  [Rank samples]  [Fix labels or    [Train with    [Confirm quality
   by noise       adjust loss]       robustness]    on clean data]
   likelihood]
```

- **Detection**: Confident learning [1] produces out-of-fold predicted probabilities to estimate which samples are mislabeled; AUM [10] ranks samples by margin stability during training
- **Correction**: Noise transition matrix T estimated via anchor points [15] enables unbiased forward loss correction [7]; alternatively, relabel high-confidence errors
- **Training**: Co-teaching [2] uses dual networks selecting small-loss samples for each other; DivideMix [3] applies semi-supervised learning to the noisy partition
- **Validation**: Clean holdout set (even 1K verified samples) provides ground truth for noise detection calibration

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Standard CE memorizes noise [5] | Symmetric CE [4] or MAE loss [8] | Reduced convergence speed on clean samples |
| Binary clean/noisy classification | DivideMix's BMM-based soft partition [3] | +complexity, warmup epochs required |
| Unknown noise transition matrix | Anchor point estimation [15] | Assumes anchor points exist; fails for overlapping classes |
| Single-model confirmation bias | Co-teaching with two divergent networks [2] | 2x memory and compute cost |
| Static sample weights | Curriculum learning with difficulty scoring [13] | Requires difficulty metric design; ordering sensitivity |

### Scaling Summary

- **10x data (100K→1M)**: Confident learning cross-validation becomes expensive — switch to AUM-based ranking [10] which scores samples during a single training run
- **100x data (1M→100M)**: Co-teaching requires distributed dual-model training; transition matrix estimation needs sampling-based approximation; DivideMix warmup scales linearly
- **1000x data (100M→10B)**: All per-sample methods become intractable — move to importance reweighting [11] with streaming estimation, or train on curated subsets identified by fast heuristics

## Interview Q&A Bank

### Q1: Why do DNNs memorize noisy labels, and how does this inform robust training?

> **Quick answer:** DNNs fit clean patterns first (low-complexity features) then memorize noise later (high-complexity patterns) [5]. This temporal separation enables small-loss selection, early stopping, and curriculum-based methods.

Arpit et al. (2017) showed that DNNs learn generalizable patterns before memorizing random labels [5]. The mechanism: clean samples share common features that produce low-loss quickly via gradient alignment, while noisy samples require the network to memorize individual examples, which happens later when the model has sufficient capacity. This "memorization gap" is observable as a divergence between clean-sample loss (continues decreasing) and noisy-sample loss (plateaus then decreases slowly).

This insight drives nearly every robust method: Co-teaching [2] selects small-loss samples in early epochs when they are predominantly clean; DivideMix [3] uses a warmup period to separate distributions; AUM [10] measures how consistently a sample stays above the decision margin. Early stopping is the simplest exploitation — halt training before memorization begins.

| Epoch range | What model learns | Implication |
|-------------|-------------------|-------------|
| 1-20 | Common patterns (clean) | Small-loss = likely clean [2] |
| 20-100 | Decision boundaries | AUM separates clean/noisy [10] |
| 100+ | Individual memorization | Noisy labels fully fit [5] |

**Hard follow-up:** How would you detect the transition point from learning to memorization?

> Track per-sample loss trajectories and fit a two-component mixture model to the loss distribution at each epoch. The transition occurs when the lower component (clean) stabilizes while the upper component (noisy) begins decreasing. Alternatively, monitor AUM: when AUM variance across samples peaks, the model is at the learning-memorization boundary [10].

### Q2: What is the noise transition matrix and how is it used for loss correction?

> **Quick answer:** The noise transition matrix T[i][j] = P(noisy=j | clean=i) describes the probability of each class being flipped to another. Multiplying the inverse of T with the loss function yields an unbiased estimator of the clean-data risk [7][12].

Natarajan et al. (2013) proved that if you know T, you can construct an unbiased loss: L_corrected(f(x), y_noisy) = T^{-1} L(f(x), y_noisy) [12]. Patrini et al. (2017) extended this to DNNs with two practical approaches: forward correction (multiply softmax outputs by T before computing loss) and backward correction (multiply the loss gradient by T^{-1}) [7].

The challenge is estimating T. Anchor points — samples that belong to class i with probability 1 — allow direct estimation: T[i][j] = P(y_noisy=j | x is an anchor for class i) [15]. Xia et al. (2019) showed that even approximate anchor points suffice for consistent T estimation [15].

```
Forward correction: L_forward = CE(T * softmax(f(x)), y_noisy)
Backward correction: L_backward = T^(-1) * CE(softmax(f(x)), y_noisy)
```

**Hard follow-up:** When does T-matrix correction fail?

> When noise is instance-dependent (T varies per sample rather than being class-conditional), the matrix framework breaks down [6]. Also fails when T is poorly conditioned (near-singular), amplifying estimation errors through the inverse. In practice, condition number > 10 indicates unreliable correction.

### Q3: How does Co-teaching handle extremely noisy labels?

> **Quick answer:** Two networks are trained simultaneously; each selects its smallest-loss samples and feeds them to the other for training, preventing both networks from converging to the same memorized errors [2].

Han et al. (2018) introduced Co-teaching based on the insight that two networks initialized differently will disagree on which samples to memorize [2]. Each network selects R(t) = 1 - min(t/T_k * noise_rate, noise_rate) fraction of its smallest-loss samples per mini-batch and sends them to its peer. The key innovation: the "disagreement" between networks prevents co-memorization that would occur if a single network selected its own training samples.

The sample selection rate R(t) starts at 100% and decays to (1 - noise_rate) over T_k epochs, gradually filtering more aggressively as both networks improve their ability to distinguish clean from noisy samples. At 45% symmetric noise on CIFAR-10, Co-teaching maintains >85% test accuracy where standard training drops to ~70% [2].

**Hard follow-up:** Why not just train one network and select its own small-loss samples?

> Self-training creates confirmation bias — the network preferentially selects samples it already fits well, including memorized noisy samples. Co-teaching breaks this because each network's errors are partially independent due to different initialization and different selected subsets, creating a form of peer review [2].

### Q4: How does DivideMix combine noise handling with semi-supervised learning?

> **Quick answer:** DivideMix fits a two-component beta mixture model to per-sample losses, divides data into a labeled set (likely clean) and an unlabeled set (likely noisy), then applies MixMatch semi-supervised learning to use both partitions [3].

Li et al. (2020) observed that discarding noisy samples wastes information — those samples still contain valid input features even if labels are wrong [3]. DivideMix uses a GMM/BMM on per-sample loss to compute posterior probability of each sample being clean (w_i). Samples with w_i > threshold form the labeled set; others become "unlabeled." Then MixMatch generates pseudo-labels for the unlabeled set using predictions from a co-trained network, applies sharpening and mixup augmentation, and trains on both sets jointly.

This achieves 96.1% on CIFAR-10 with 90% symmetric noise — only 2% below clean-data performance [3]. The co-training aspect (two networks cross-validating each other's clean/noisy partition) prevents error accumulation.

**Hard follow-up:** What is the failure mode of DivideMix under asymmetric noise?

> Under asymmetric (class-dependent) noise, the BMM may fail to separate clean and noisy distributions when confusion occurs between semantically similar classes (e.g., cat/dog). The loss distributions overlap more, making clean/noisy separation unreliable. DivideMix partially addresses this via co-refinement, but performance degrades more under asymmetric than symmetric noise at the same rate [3].

### Q5: How would you design a noise-robust fine-tuning system for a production LLM?

> **Quick answer:** Use confident learning [1] on cross-validated predictions to identify mislabeled samples, apply symmetric loss [4] during training, and implement a human-in-the-loop correction pipeline for high-value flagged samples.

The production pipeline has three stages. First, embed all training samples and run K-fold cross-validation to generate out-of-fold predicted probabilities. Confident learning [1] uses these to estimate the joint distribution P(y_noisy, y_true) and flag samples where the predicted class disagrees with the given label. Second, route flagged samples through a correction pipeline: high-confidence corrections get auto-relabeled, uncertain cases go to human review, and irreparable samples get removed. Third, train with robust loss (symmetric CE [4] or flooding [14]) on the cleaned dataset with sample weights inversely proportional to estimated noise likelihood.

> [!experience]
> The most impactful intervention is not algorithmic sophistication but clean validation data. Even 500 verified-clean samples enable reliable noise detection calibration and provide an unbiased evaluation signal.

**Hard follow-up:** How do you handle the case where your noise detection model was itself trained on noisy data?

> Bootstrap confidence: train K noise detectors on K different subsets, flag samples that all K detectors agree are noisy (high precision), and use the disagreement set for human review. The intersection of independent noisy detectors converges to true noise faster than any single detector.

### Q6: What are robust loss functions and when should you use them?

> **Quick answer:** Robust losses (MAE [8], symmetric CE [4], flooding [14]) satisfy noise-tolerance conditions that prevent memorization of corrupted labels, at the cost of slower convergence on clean data.

Ghosh et al. (2017) proved that a loss function is noise-tolerant under symmetric noise if the sum of losses over all classes is constant: sum_k L(f(x), k) = C [8]. MAE (mean absolute error) satisfies this condition; standard CE does not. However, MAE converges very slowly because its gradients are constant regardless of prediction confidence.

Zhang & Sabuncu (2018) proposed Generalized Cross Entropy (GCE), which interpolates between CE (fast convergence) and MAE (noise robustness) via a parameter q: L_GCE = (1 - f(x)_y^q) / q [4]. At q=0, it reduces to CE; at q=1, to MAE. The symmetric cross-entropy (SCE = CE + RCE) combines standard CE with a "reverse" cross-entropy term that provides the noise tolerance guarantee [4].

Flooding [14] takes a different approach: it prevents the training loss from going below a threshold b, keeping the model in a broad minimum that resists memorization: L_flood = |L - b| + b.

| Loss | Noise tolerance | Convergence | Best for |
|------|----------------|-------------|----------|
| CE | None | Fast | Clean data only |
| MAE [8] | Symmetric noise | Very slow | Theoretical baseline |
| GCE (q=0.7) [4] | Partial | Moderate | Practical default |
| SCE [4] | Symmetric noise | Moderate | Drop-in CE replacement |
| Flooding [14] | Implicit | Fast (with threshold) | Any loss + regularization |

**Hard follow-up:** Why does MAE underperform CE even on noisy data in practice, despite theoretical guarantees?

> MAE's constant gradient magnitude means it cannot upweight confident correct predictions or downweight uncertain ones — it treats a 99% confident correct prediction the same as a 51% confident one. This severely slows learning of clean patterns. GCE [4] fixes this by allowing tunable gradient scaling via q.

### Q7: How does confident learning estimate which samples are mislabeled?

> **Quick answer:** Confident learning [1] uses out-of-fold predicted probabilities to estimate the joint distribution P(y_given, y_true) via class-conditional thresholds, then identifies samples where the model's prediction confidently disagrees with the given label.

The cleanlab methodology [1] proceeds in three steps. (1) Generate out-of-fold predicted probabilities via K-fold cross-validation — each sample gets a probability vector from a model that never saw it during training. (2) For each class j, compute a threshold t_j as the average predicted probability of class j among all samples labeled j. (3) A sample (x_i, y_i=j) is flagged as mislabeled if its predicted probability for some other class k exceeds t_k, indicating the model confidently believes it belongs to class k instead.

This constructs a confident joint matrix C[j][k] counting samples labeled j but predicted as k. Normalizing C gives an estimate of the joint P(y_noisy=j, y_true=k), from which the noise transition matrix T can be derived. Northcutt et al. demonstrated this finds label errors in ImageNet, MNIST, and 10 other benchmarks with high precision [1].

**Hard follow-up:** What happens when all classes have similar predicted probabilities (low model confidence)?

> When the model is poorly calibrated or undertrained, thresholds t_j collapse toward 1/K (uniform), and confident learning loses discriminative power. The fix: use temperature scaling or Platt calibration on the out-of-fold probabilities before applying thresholds, or train longer before computing OOF predictions.

### Q8: How do you measure the impact of label noise on model performance?

> **Quick answer:** Plot learning curves comparing models trained on clean vs noisy data at various noise rates; measure the memorization gap using per-sample loss trajectories [5]; and compute AUM to quantify noise impact per sample [10].

The standard diagnostic involves: (1) Train on data with known injected noise at rates 0%, 10%, 20%, 40% and plot test accuracy vs noise rate — the slope reveals model sensitivity. (2) Track training accuracy vs test accuracy gap — a widening gap indicates memorization of noise rather than learning of patterns [5]. (3) Compute AUM (Area Under the Margin) for each sample across training: AUM_i = (1/E) sum_e [logit_correct(e) - max_other_logit(e)]. Samples with low or negative AUM are likely mislabeled [10].

Memorization detection: Arpit et al. [5] showed that shuffling labels and measuring how quickly the model achieves high training accuracy reveals capacity for memorization. A model that memorizes 100% of random labels has excessive capacity that will also memorize real noise.

**Hard follow-up:** How do you distinguish between hard examples and mislabeled examples?

> Hard examples have low AUM but positive (the model eventually learns them); mislabeled examples have negative AUM (the model's correct-class logit is consistently below the top incorrect logit) [10]. Additionally, hard examples typically cluster in embedding space near class boundaries, while mislabeled examples cluster with the wrong class.

### Q9: What is curriculum learning and how does it help with noisy labels?

> **Quick answer:** Curriculum learning [13] orders training samples from easy to hard, which naturally prioritizes clean samples (easy to fit) before noisy ones (hard/impossible to fit), providing implicit noise robustness.

Bengio et al. (2009) showed that presenting training samples in a meaningful order — starting with easy examples and gradually introducing harder ones — can improve both convergence speed and final generalization [13]. Under label noise, this becomes particularly powerful: "easy" samples are predominantly clean (consistent patterns), while "hard" samples include both genuinely difficult examples and mislabeled ones.

The difficulty scoring function is critical. Options include: loss-based (per-sample training loss after a few warmup epochs), confidence-based (model's predicted probability for the given label), and AUM-based [10] (margin stability over training). Self-paced learning automates the curriculum by allowing the model to choose which samples to learn from at each epoch based on a loss threshold that gradually increases.

> [!experience]
> Curriculum learning's main failure mode under noise is that "hardness" conflates two distinct causes: genuine complexity and label corruption. Separating these requires a secondary signal like ensemble disagreement or cross-validation confidence.

**Hard follow-up:** Can curriculum learning hurt performance under asymmetric noise?

> Yes — if easy-to-hard ordering is based solely on loss, and the asymmetric noise creates "easy but wrong" samples (e.g., class A consistently mislabeled as similar class B), these get learned early and bias the model before genuine samples are seen. The fix: use disagreement-based difficulty (two models) rather than single-model loss [2].

### Q10: How do you build a data flywheel that handles noisy user feedback?

> **Quick answer:** Convert implicit signals (clicks, dwell time, skip) into probabilistic labels, aggregate across users to reduce per-label noise, and use confident learning [1] to identify reliable signal before training.

User feedback is inherently noisy: a click does not guarantee relevance, and absence of a click does not guarantee irrelevance. The flywheel design: (1) Collect raw signals with uncertainty estimates (click = 0.7 positive, ignore = 0.3 negative). (2) Aggregate across multiple users seeing the same item to compute posterior label estimates via beta-binomial models. (3) Apply confident learning on aggregated labels to identify high-confidence training signal. (4) Train model on confident subset, deploy, collect more feedback.

The key insight: noise decreases with aggregation (O(1/sqrt(N)) for N independent users), so popular items get clean labels quickly while tail items remain noisy. This creates a natural curriculum where the model first learns from high-traffic (clean) signal and gradually incorporates tail (noisy) signal as it accumulates.

**Hard follow-up:** How do you prevent the flywheel from reinforcing model biases?

> Exposure bias: the model only gets feedback on items it surfaces, creating a filter bubble. Mitigation: inject exploration traffic (5-10% random/diverse items), log propensity scores for inverse-propensity-weighted training, and explicitly track coverage metrics across the item catalog.

### Q11: How does importance reweighting handle noisy labels theoretically?

> **Quick answer:** Importance reweighting assigns each sample a weight w(x) = P(clean|x,y) / P(noisy|x,y) such that the weighted noisy-data risk equals the clean-data risk in expectation [11][12].

Liu & Tao (2016) showed that under class-conditional noise with known T, the optimal importance weights are w = T^{-1} applied to the label distribution [11]. Natarajan et al. (2013) proved that with these weights, empirical risk minimization on noisy data converges to the same minimizer as on clean data [12]. The practical challenge is estimating the weights without clean data.

Modern implementations use the noise transition matrix: for sample (x, y_noisy=j), the weight is w_j = sum_i T^{-1}[j][i] * P(y_true=i|x). When T is unknown, it can be estimated from the data using anchor points [15] or confident learning [1].

**Hard follow-up:** Why does importance reweighting fail with high noise rates?

> At high noise rates, T^{-1} has large entries, producing extreme weights that increase variance dramatically. A sample with true label A but noisy label B might receive weight >10, making training unstable. Practical fix: clip weights to [0.1, 10] range, accepting small bias for large variance reduction.

### Q12: What are anchor points and how do they enable noise-rate estimation?

> **Quick answer:** Anchor points are samples for which P(y_true=i|x)=1 — they belong to class i with certainty. Given anchor points, the noise transition matrix T[i][j] = P(y_noisy=j|anchor_i) can be directly estimated from observed noisy labels [15].

Xia et al. (2019) proved that anchor points are both necessary and sufficient for identifiability of the noise transition matrix without clean validation data [15]. An anchor point for class i is a sample x where the true posterior P(y=i|x) = 1. In practice, samples with very high model confidence after initial training serve as approximate anchors.

The estimation procedure: (1) Train a model on noisy data for a few epochs. (2) For each class i, identify the sample x* with highest predicted probability for class i — this is the approximate anchor. (3) Estimate T[i][j] as the average noisy-label distribution among samples most similar to anchor_i in embedding space. This gives a complete T matrix without any clean labels.

**Hard follow-up:** What if no perfect anchor points exist (e.g., all classes overlap)?

> Xia et al. [15] showed that T-estimation degrades gracefully with imperfect anchors — the estimation error is bounded by the anchor "purity" (1 - max_posterior). For highly overlapping classes, use multiple approximate anchors per class and average their T estimates, or switch to confident-learning-based T estimation [1] which does not require strict anchor assumptions.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): Noise Transition Matrices — Estimating P(noisy|clean) via Anchor Points</strong></summary>

The noise transition matrix T is a K x K stochastic matrix where T[i][j] = P(y_noisy=j | y_true=i). The fundamental identifiability question: can T be recovered from noisy data alone?

**Identifiability theorem** [12][15]: T is identifiable if and only if for each class i, there exists at least one anchor point x where P(y_true=i|x) = 1. Under this condition:

```
T[i][j] = P(y_noisy=j | x is anchor_i)
         = E[1{y_noisy=j} | x = anchor_i]
```

**Practical estimation via anchor approximation** [15]:

```python
def estimate_transition_matrix(model_probs, noisy_labels, K):
    """Estimate T using approximate anchor points [15]."""
    T = np.zeros((K, K))
    for i in range(K):
        # Find approximate anchor: sample with highest P(y=i|x)
        class_probs = model_probs[:, i]
        anchor_idx = np.argmax(class_probs)
        # Anchor purity check
        if class_probs[anchor_idx] < 0.95:
            warnings.warn(f"Weak anchor for class {i}: {class_probs[anchor_idx]:.3f}")
        # Estimate row i of T from noisy labels near anchor
        similar = np.argsort(-class_probs)[:100]  # top-100 most confident
        for j in range(K):
            T[i][j] = np.mean(noisy_labels[similar] == j)
    # Ensure rows sum to 1
    T = T / T.sum(axis=1, keepdims=True)
    return T
```

**Forward loss correction** [7]: Given estimated T, the corrected loss becomes L_corrected(f(x), y) = CE(T^T * softmax(f(x)), y). This is unbiased: E_noisy[L_corrected] = E_clean[L_original] when T is exact.

**Error propagation**: If T_hat has estimation error epsilon (element-wise), the bias of the corrected risk is bounded by: |R_corrected - R_clean| <= ||T^{-1}|| * epsilon * max_loss. The condition number kappa(T) = ||T|| * ||T^{-1}|| governs sensitivity — when kappa > 10, small T errors produce large risk bias.

**Connection to confident learning** [1]: The confident joint C[i][j] estimated by cleanlab relates to T via: C[i][j] proportional to T[i][j] * P(y_true=i). Thus T can be recovered: T[i][j] = C[i][j] / sum_j C[i][j]. This alternative to anchor-point estimation is more robust when anchors are impure.

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): Curriculum Learning Pipeline — Sample Ordering and Progressive Training</strong></summary>

Curriculum learning [13] structures training as a sequence of increasingly difficult tasks. Under label noise, this becomes a noise-aware scheduling system where difficulty correlates with noise probability.

**Formal framework**: Define a scoring function s(x_i, y_i, theta_t) that measures sample difficulty at training step t. The curriculum C(t) = {i : s(x_i, y_i, theta_t) < lambda(t)} where lambda(t) is a monotonically increasing threshold (pacing function).

**Pipeline architecture for noise-robust curriculum**:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│ Warmup      │───>│ Score        │───>│ Sort & Bucket   │───>│ Progressive  │
│ (5 epochs,  │    │ Computation  │    │ [Easy|Med|Hard] │    │ Training     │
│  all data)  │    │ per sample   │    │                 │    │ (expand set) │
└─────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     Loss-based     AUM-based [10]  Confidence-based
     s = L(x,y)    s = -AUM(x)     s = -P(y|x)
```

**Self-paced learning variant** — jointly optimizes model parameters theta and sample weights v:

```
min_{theta, v} sum_i v_i * L(x_i, y_i; theta) - lambda * sum_i v_i
subject to: v_i in [0, 1]
```

The closed-form solution for v given theta: v_i = 1 if L(x_i) < lambda, else 0. The pacing parameter lambda increases each epoch, gradually admitting harder (potentially noisier) samples.

**Production considerations**:
- **Score staleness**: Difficulty scores computed at epoch 5 become stale by epoch 50. Solution: recompute scores every N epochs with exponential moving average.
- **Distributed training**: In multi-GPU settings, different workers see different subsets. Curriculum must be globally coordinated via a shared score database.
- **Interaction with noise rate**: At noise rate p, the optimal pacing starts at (1-p) fraction of data (approximately all clean samples) and expands to 100% over T_curriculum epochs.
- **Failure mode**: If the warmup phase overfits to noise (too many warmup epochs), difficulty scores become unreliable. Limit warmup to 2-5% of total training epochs.

**Empirical result** [13]: Curriculum learning on noisy data achieves the performance of training on ~30% more data, because early emphasis on clean patterns creates a stronger feature extractor that is more resistant to subsequent noise exposure.

</details>

<details><summary><strong>DE Probe 3 (DATA): Confident Learning — Identifying Mislabeled Examples via Cleanlab</strong></summary>

Confident learning [1] provides a principled framework for characterizing label noise without requiring clean validation data. The core insight: use out-of-fold model predictions as a surrogate for the unobserved true labels.

**The confident joint estimation** [1]:

For K classes, the confident joint C_tilde is a K x K matrix where C_tilde[i][j] = |{x : y_given=i, y_pred=j with confidence > t_j}|. The threshold t_j is class-specific: t_j = (1/|D_j|) * sum_{x: y=j} P_hat(y=j|x) — the average self-confidence for class j.

**Why class-specific thresholds matter**: A model might be 90% confident on dogs but only 60% confident on wolves. Using a global threshold would under-detect noise in low-confidence classes and over-detect in high-confidence ones.

**Complete cleanlab pipeline**:

```python
from cleanlab import Datalab

# Step 1: Generate out-of-fold predicted probabilities
from sklearn.model_selection import cross_val_predict
pred_probs = cross_val_predict(model, X, y, cv=5, method='predict_proba')

# Step 2: Find label issues
lab = Datalab(data={'labels': y}, label_name='labels')
lab.find_issues(pred_probs=pred_probs)

# Step 3: Retrieve ranked label errors
issues = lab.get_issues()
label_errors = issues[issues['is_label_issue']].sort_values('label_quality_score')

# Step 4: Decision — filter vs correct
high_confidence_errors = label_errors[label_errors['label_quality_score'] < 0.1]
# Auto-correct: use model's predicted class
corrections = pred_probs[high_confidence_errors.index].argmax(axis=1)
```

**Theoretical guarantees** [1]: Under class-conditional noise with transition matrix T, confident learning exactly identifies the noise rates: P_hat(y_noisy=i, y_true=j) converges to P(y_noisy=i, y_true=j) as n -> infinity, assuming the model is calibrated.

**Failure modes and mitigations**:
1. **Poorly calibrated models**: Temperature scaling or isotonic regression on a small clean set restores calibration before applying confident learning.
2. **Class imbalance**: Minority classes have unreliable threshold estimates. Mitigation: use at least 50 samples per class for stable t_j estimation.
3. **Model-data circularity**: The model trained on noisy data inherits biases. Mitigation: use early-stopped models (before memorization) for OOF prediction [5].
4. **High-dimensional inputs**: In high-d embedding spaces, classifier probabilities become overconfident. Mitigation: reduce dimensionality before computing OOF predictions.

**Impact at scale** [1]: Northcutt et al. applied confident learning to 10 popular ML benchmarks and found 3.3% average label error rate — including 6% errors in ImageNet validation set. Correcting these errors improved model accuracy by up to 10% without any architectural change.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Measuring Label Noise Impact — Learning Curves and Memorization Detection</strong></summary>

Rigorous evaluation of noise impact requires separating three confounded effects: (1) reduced effective dataset size (fewer clean samples), (2) actively harmful gradients from wrong labels, and (3) capacity consumption by memorized noise.

**Diagnostic methodology**:

**Experiment 1 — Noise sensitivity curve**: Train identical models on data with injected noise at rates {0, 0.1, 0.2, 0.3, 0.5}. Plot test accuracy vs noise rate. The slope d(accuracy)/d(noise_rate) quantifies model vulnerability. Compare against the theoretical lower bound for CE loss under symmetric noise: accuracy_noisy >= accuracy_clean * (1 - noise_rate) [12].

**Experiment 2 — Memorization index** [5]: For each sample, compute:

```
memorization_index(x_i) = accuracy_with(x_i) - accuracy_without(x_i)
```

High memorization index for a specific sample means the model's ability to classify that sample depends entirely on having seen it during training — the hallmark of memorized noise.

**Experiment 3 — AUM diagnostic** [10]:

```python
def compute_aum(logits_history, labels, num_epochs):
    """
    logits_history: [num_epochs, num_samples, num_classes]
    Returns per-sample AUM score.
    """
    aum_scores = np.zeros(len(labels))
    for epoch in range(num_epochs):
        for i, (logit, label) in enumerate(zip(logits_history[epoch], labels)):
            correct_logit = logit[label]
            other_logits = np.delete(logit, label)
            margin = correct_logit - other_logits.max()
            aum_scores[i] += margin / num_epochs
    return aum_scores
    # Interpretation: AUM < 0 => likely mislabeled
    # AUM ~ 0 => ambiguous/hard
    # AUM >> 0 => confidently correct
```

**Separation quality metric**: After computing AUM, measure the AUROC of distinguishing injected noisy labels from clean labels. AUROC > 0.95 indicates that the metric reliably separates noise from signal [10]. Pleiss et al. showed AUM achieves >0.98 AUROC on CIFAR-10 with symmetric noise [10].

**Learning curve analysis for noise detection timing**: Plot training loss for the bottom 10% AUM samples (suspected noisy) vs top 10% (confident clean). The epoch at which these curves diverge marks the optimal point to compute difficulty scores — too early gives unreliable estimates, too late means the model has already memorized noise.

**Production evaluation protocol**: Maintain a curated clean test set (human-verified, even if small — 1K samples suffices). Report: (1) Clean-test accuracy at each noise handling stage, (2) Noise detection precision@K, (3) Effective dataset retention rate after filtering.

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Data Flywheel with Noisy Feedback — Converting User Signals to Training Labels</strong></summary>

Production systems must convert noisy implicit feedback (clicks, dwell time, purchases, skips) into training labels while maintaining signal quality across the flywheel's iterations.

**Signal aggregation architecture**:

```
User Action → Raw Signal → Aggregation → Confident Subset → Model Training
  click(+0.6)     per-item      beta-binomial     cleanlab [1]      weighted loss
  skip(-0.3)      per-user      posterior mean     threshold t       deploy
  dwell(+0.4)     temporal      credible interval  → training set    → more feedback
```

**Noise model for implicit feedback**: Each user action a_u on item i provides a noisy observation of relevance r_i. Model: P(a_u = positive | r_i) = r_i * (1-epsilon_fn) + (1-r_i) * epsilon_fp, where epsilon_fn is false-negative rate (relevant item not clicked) and epsilon_fp is false-positive rate (irrelevant item clicked accidentally).

**Aggregation via beta-binomial model**:

```python
def aggregate_feedback(item_signals):
    """Aggregate noisy user signals into posterior label estimate."""
    # Prior: Beta(alpha_0, beta_0) — uninformative
    alpha, beta = 1.0, 1.0
    for signal in item_signals:
        if signal > 0:  # positive signal
            alpha += signal
        else:           # negative signal
            beta += abs(signal)
    # Posterior mean as label probability
    p_relevant = alpha / (alpha + beta)
    # Confidence: width of 95% credible interval
    confidence = 1.0 - (beta_dist.ppf(0.975, alpha, beta) -
                        beta_dist.ppf(0.025, alpha, beta))
    return p_relevant, confidence
```

**Flywheel noise accumulation problem**: Each iteration introduces model bias into feedback collection (exposure bias). Over K iterations without intervention, the noise compounds: effective_noise(K) ~ noise_base + K * feedback_bias. Mitigation requires:
1. **Exploration injection**: 5-10% random traffic ensures unbiased feedback on unexposed items.
2. **Propensity scoring**: Weight each feedback signal by 1/P(exposure|model), debiasing position and selection effects.
3. **Periodic clean-data injection**: Every N iterations, collect human-annotated ground truth on a random sample to recalibrate the flywheel.

**Production monitoring**: Track the "label confidence distribution" over flywheel iterations. A healthy flywheel shows increasing average confidence (more data → better labels). A degrading flywheel shows decreasing confidence or bimodal distribution collapse (model only surfaces items it is already confident about).

**Threshold for training inclusion**: Only include items where credible interval width < 0.3 AND total feedback count > 10 interactions. This naturally creates a curriculum where popular items (high signal) enter training first and tail items (low signal) accumulate evidence over time.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Robust Loss Functions — Symmetric Losses, MAE vs CE, and Flooding</strong></summary>

The choice of loss function fundamentally determines a model's vulnerability to label noise. The theoretical framework for noise-tolerant losses is based on the symmetry condition [8].

**Noise-tolerance theorem** [8]: A loss function L is tolerant to symmetric noise with rate eta if: sum_{k=1}^{K} L(f(x), k) = C (constant). Under this condition, the minimizer of the noisy risk equals the minimizer of the clean risk, regardless of noise rate.

**Analysis of standard losses**:

| Loss | Formula | sum_k L(f,k) | Noise-tolerant? |
|------|---------|--------------|-----------------|
| CE | -log(p_y) | -sum_k log(p_k) = H(p) + log(K) | NO (varies with p) |
| MAE [8] | 1 - p_y | K - 1 | YES (constant) |
| GCE [4] | (1-p_y^q)/q | (K - sum_k p_k^q)/q | Approximately (q→1) |
| SCE [4] | CE + alpha*RCE | Varies | YES (by construction) |
| Flooding [14] | \|L-b\| + b | N/A (meta-loss) | Implicit |

**Why MAE is noise-tolerant but impractical** [8]: MAE gradient = -(1/K) * (e_y - p), which has constant norm regardless of p_y. This means the model receives the same gradient magnitude whether it predicts the correct class with 0.99 probability or 0.01 probability. Clean samples that are already well-classified get unnecessarily large gradients, slowing convergence by 5-10x compared to CE.

**Generalized Cross Entropy (GCE)** [4] bridges the gap:

```
L_GCE(f(x), y) = (1 - f(x)_y^q) / q

Gradient: dL/d(f_y) = -f_y^{q-1}
```

At q=0: recovers CE (fast convergence, not robust). At q=1: recovers MAE (robust, slow). Setting q=0.7 gives a practical compromise — noise-tolerant for noise rates up to ~40% while maintaining reasonable convergence [4].

**Flooding** [14] — a meta-approach applicable to ANY loss:

```python
def flooding_loss(loss, b=0.04):
    """Prevent loss from going below threshold b [14]."""
    return torch.abs(loss - b) + b
    # When loss > b: gradient unchanged (normal training)
    # When loss < b: gradient REVERSED (pushes loss back up)
```

The insight: when loss reaches b, the model enters a "random walk" regime around flat minima rather than continuing to a sharp minimum that memorizes noise. Ishida et al. [14] showed flooding improves generalization by 1-3% under noise without requiring noise rate estimation — it works by preventing the model from "going too far" rather than by detecting noise.

**Practical recommendation hierarchy**:
1. **Default**: SCE (CE + 0.1 * RCE) [4] — drop-in replacement, handles up to 30% symmetric noise
2. **High noise (>30%)**: GCE with q=0.7 [4] — better theoretical guarantees
3. **Unknown noise**: Flooding with b = 0.8 * (converged clean loss) [14] — requires no noise rate estimation
4. **Asymmetric noise**: Forward T-correction [7] — requires T estimation but handles any noise structure

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Sample Usage | Cost/Sample |
|-----------|-----------|------------------|-------------|
| Embedding generation | $0.0001/sample | 1 forward pass | $0.0001 |
| K-fold cross-validation [1] | 5x training cost | 5 folds | $0.0005 |
| AUM computation [10] | ~1x training cost | 1 full training run | $0.0001 |
| Confident learning detection | $0.00001/sample | N log N ranking | $0.00001 |
| LLM-based label correction | $0.01/sample | 500 tokens avg | $0.01 |
| Human review (flagged samples) | $0.50/sample | Expert annotation | $0.50 |
| **Total (automated pipeline)** | | | **~$0.011** |
| **Total (with human review on 5%)** | | | **~$0.036** |

### Monthly Cost at Scale

| Scale | Samples | Automated Cost | Human Review (5%) | Total Monthly |
|-------|---------|----------------|-------------------|---------------|
| Small | 10K | $110 | $250 | $360 |
| Medium | 100K | $1,100 | $2,500 | $3,600 |
| Large | 1M | $11,000 | $25,000 | $36,000 |
| Enterprise | 10M | $110,000 | $250,000 | $360,000 |

### Cost Optimization Priority Stack

1. **AUM over cross-validation** (80% savings on detection): AUM [10] computes noise scores during a single training run vs 5x cost for K-fold confident learning [1]
2. **Threshold-based routing** (60% savings on correction): Only send low-confidence flagged samples to expensive LLM correction; auto-correct high-confidence ones
3. **Embedding caching** (50% savings on repeated runs): Cache embeddings across retraining cycles — they change slowly
4. **Batch LLM correction** (30% savings): Group similar errors for batch API calls with shared context
5. **Active learning for human review** (40% savings): Only route maximally uncertain samples to expensive human annotators

### Build vs Buy

| Capability | Build Cost | Buy Option | Recommendation |
|------------|------------|------------|----------------|
| Noise detection | $200K (4 eng-months) | cleanlab Pro: $30K/yr | **Buy** — mature, well-tested [1] |
| Loss correction | $50K (1 eng-month) | Open source (PyTorch) | **Build** — trivial to implement [4][7] |
| Curriculum learning | $100K (2 eng-months) | No good vendor | **Build** — domain-specific ordering [13] |
| Human review platform | $500K (6 eng-months) | Label Studio: $10K/yr | **Buy** — commodity capability |
| End-to-end pipeline | $800K (8 eng-months) | No integrated vendor | **Build** — competitive differentiator |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Noise detection rate (% flagged) | >40% of new batch flagged | Data pipeline team — possible upstream corruption |
| Clean holdout accuracy | >3% drop from baseline | ML team — model degradation |
| AUM distribution shift | KL divergence > 0.1 from baseline | Retrigger noise detection |
| Label correction confidence | Mean confidence < 0.7 | Pause auto-correction, route to human |
| Training loss on clean subset | Increasing after epoch 20 | Possible overfitting to noise [5] |
| Cross-val OOF calibration error | ECE > 0.1 | Recalibrate before confident learning |
| Human review disagreement rate | Cohen's kappa < 0.6 | Revise annotation guidelines |

### Debugging Walkthrough

```
Model accuracy dropped on clean test set
    │
    ├── Check: Was training data recently updated?
    │   ├── YES → Compare noise detection rate before/after
    │   │         Was new data noisier? → Re-run confident learning [1]
    │   └── NO → Check training dynamics
    │
    ├── Check: Training loss still decreasing but val loss increasing?
    │   ├── YES → Memorization detected [5]
    │   │         → Reduce epochs OR apply flooding [14]
    │   └── NO → Check: loss flat but accuracy dropped?
    │            → Label distribution shift → audit class balance
    │
    └── Check: Noise detection precision on known-injected noise
        ├── Degraded → Model OOF predictions miscalibrated → recalibrate
        └── Stable → Problem is in correction, not detection
                    → Audit LLM corrections for systematic bias
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| Noise detection model + thresholds | Pin to previous checkpoint; recompute scores | Single retraining run |
| Transition matrix T estimate | Store per-dataset T versions; revert correction | All samples corrected in that window |
| Training data (clean/noisy splits) | Snapshot full dataset + partition labels | Complete model retrain needed |
| Loss function parameters (q, b, alpha) | Config-driven; instant rollback | Next training run only |
| Human correction decisions | Immutable audit log; can undo specific corrections | Individual samples |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Model disagreement with human labels | Critical — direct noise signal | Compare model predictions vs given labels on new data |
| AUM score distribution shift | High — early noise warning | Track AUM histogram across retraining cycles [10] |
| Human annotator agreement rate | High — label quality proxy | Periodic double-annotation of 5% samples |
| Downstream task performance | Critical — business impact | A/B testing model versions on clean holdout |
| User feedback on model outputs | Medium — indirect quality signal | Implicit signals aggregated via beta-binomial model |
| Confident learning joint matrix evolution | Medium — noise pattern tracking | Compare C[i][j] across dataset versions [1] |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|----------------|---------------|
| Per-batch | Noise detection thresholds t_j [1] | Flagging rate within [15%, 35%] |
| Weekly | Human review sample selection | Maximize disagreement coverage |
| Bi-weekly | Transition matrix T re-estimation [15] | Condition number kappa(T) < 10 |
| Monthly | Loss function hyperparameters (q, b) | Val accuracy improvement > 0.5% |
| Quarterly | Full pipeline re-evaluation | Clean-test accuracy gain justifies cost |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| **Co-teaching** [2] | Single-model confirmation bias | Noise rate 20-50%, two GPUs available | Low noise (<10%), memory constrained |
| **DivideMix** [3] | Discarding useful noisy samples | High noise (>40%), want maximum accuracy | Simple tasks, small datasets |
| **Forward T-correction** [7] | Unknown noise structure | T is estimable, noise is class-conditional | Instance-dependent noise, T ill-conditioned |
| **Symmetric CE** [4] | CE vulnerability to noise | Drop-in replacement needed, symmetric noise | Asymmetric noise, need fastest convergence |
| **AUM ranking** [10] | Expensive cross-validation | Large datasets, need fast scoring | Very early training (unstable margins) |
| **Confident learning** [1] | Identifying specific mislabeled samples | Need to correct/remove individual errors | Model is poorly calibrated, tiny dataset |
| **Flooding** [14] | Memorization without knowing noise rate | Any setting, no noise rate needed | Already using robust loss, loss won't converge |
| **Curriculum learning** [13] | Training instability under noise | Clear difficulty ordering exists | All samples similarly difficult |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|-----------------|------------------------------|
| "We filtered out the noisy labels" | "We estimated the noise transition matrix via anchor points [15], applied forward correction [7] for an unbiased risk estimator, and retained 95% of training data" |
| "The model overfits to noise" | "DNNs memorize clean patterns before noisy ones [5] — we exploit this temporal signal via AUM scoring [10] to identify the 12% of samples responsible for 80% of memorization error" |
| "We used robust loss" | "Symmetric CE [4] provides noise tolerance guarantees but sacrifices convergence speed — we use GCE with q=0.7 up to 40% noise and switch to flooding [14] when noise rate is unknown" |
| "We need better annotations" | "Confident learning [1] identified 8% label errors in our training set; correcting just those errors improved accuracy by 6% — cheaper than re-annotating the full dataset" |
| "Co-teaching uses two networks" | "Co-teaching [2] breaks confirmation bias by peer-selecting small-loss samples; the R(t) schedule decay matches our estimated noise rate to ensure asymptotic clean-set convergence" |
| "We built a data cleaning pipeline" | "We treat user feedback as noisy observations, aggregate via beta-binomial models, apply confident learning [1] on the posterior means, and only admit samples with credible interval width < 0.3 into training" |

## References

### Foundational Papers

- [1] Northcutt, C., Jiang, L., & Chuang, I. (2021) — Confident Learning: Estimating Uncertainty in Dataset Labels — JAIR. Introduced the confident joint for characterizing label noise and finding mislabeled samples across 10 benchmarks.
- [2] Han, B., Yao, Q., Yu, X., et al. (2018) — Co-teaching: Robust Training of DNNs with Extremely Noisy Labels — NeurIPS 2018. Dual-network peer selection of small-loss samples prevents co-memorization.
- [3] Li, J., Socher, R., & Hoi, S.C.H. (2020) — DivideMix: Learning with Noisy Labels as Semi-Supervised Learning — ICLR 2020. Treats noisy samples as unlabeled data and applies MixMatch for SOTA results at 90% noise.
- [4] Zhang, Z. & Sabuncu, M. (2018) — Generalized Cross Entropy Loss for Training DNNs with Noisy Labels — NeurIPS 2018. GCE and symmetric CE interpolate between noise-robustness and convergence speed.
- [5] Arpit, D., Jastrzebski, S., et al. (2017) — A Closer Look at Memorization in Deep Networks — ICML 2017. Established that DNNs learn patterns before memorizing noise, the temporal foundation for all selection methods.
- [6] Song, H., Kim, M., Park, D., et al. (2022) — Learning from Noisy Labels with Deep Neural Networks: A Survey — IEEE TNNLS. Comprehensive survey covering noise models, robust training, and evaluation protocols.
- [7] Patrini, G., Rozza, A., et al. (2017) — Making Deep Neural Networks Robust to Label Noise: a Loss Correction Approach — CVPR 2017. Forward and backward loss correction using estimated noise transition matrix T.
- [8] Ghosh, A., Kumar, H., & Sastry, P.S. (2017) — Robust Loss Functions under Label Noise for Deep Neural Networks — AAAI 2017. Proved noise-tolerance condition (constant sum over classes) and showed MAE satisfies it.
- [9] Wei, J., Zhu, Z., et al. (2022) — Learning with Noisy Labels Revisited: A Study Using Real-World Human Annotations — ICLR 2022. CIFAR-10N/100N benchmarks reveal real-world noise is instance-dependent, not class-conditional.
- [10] Pleiss, G., Zhang, T., Elenberg, E., & Weinberger, K. (2020) — Identifying Mislabeled Data using the Area Under the Margin Ranking — NeurIPS 2020. AUM provides training-free per-sample noise ranking with >0.98 AUROC.
- [11] Liu, T. & Tao, D. (2016) — Classification with Noisy Labels by Importance Reweighting — IEEE TPAMI. Importance weighting framework for unbiased risk estimation under class-conditional noise.
- [12] Natarajan, N., Dhillon, I., Ravikumar, P., & Tewari, A. (2013) — Learning with Noisy Labels — NeurIPS 2013. Foundational theory proving unbiased risk correction is possible given known noise rates.
- [13] Bengio, Y., Louradour, J., Collobert, R., & Weston, J. (2009) — Curriculum Learning — ICML 2009. Established that training order (easy-to-hard) improves convergence and generalization.
- [14] Ishida, T., Yamane, I., Sakai, T., et al. (2020) — Do We Need Zero Training Loss After Achieving Zero Training Error? (Flooding) — ICML 2020. Preventing loss from reaching zero keeps models in flat minima, improving noise robustness.
- [15] Xia, X., Liu, T., et al. (2019) — Anchor Points Are All You Need for Noise-Rate Estimation — NeurIPS 2019. Proved anchor points are necessary and sufficient for identifying the noise transition matrix.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Restructured from v1 with 6 diverse DE probes, inline citations, and streamlined format |
