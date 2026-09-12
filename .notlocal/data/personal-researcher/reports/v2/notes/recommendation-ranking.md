# Recommendation & Ranking

> **Last Updated:** 2026-05-31 | **Read time:** ~30 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Production recommendation has settled on multi-stage pipelines (retrieval → scoring → reranking) where two-tower models handle retrieval [1][2] and cross-attention or DCN V2 architectures handle scoring [15].
> Key players: DLRM [11], DeepFM [9], DCN V2 [15], LLM-enhanced retrieval [14]. Main open problem: efficiently integrating LLM semantic understanding into latency-constrained pipelines without cost explosion.
> Recent breakthrough: LLM-as-feature-generator pipelines (2024-2025) achieve cold-start parity with behavioral models at 1/100th the latency cost of LLM-as-ranker [14]. Trend: hybrid architectures where LLMs augment offline signals while classical ML handles real-time scoring.

## State of the Art

### Current Best Approaches

- **Multi-stage retrieval + ranking** — Two-tower embedding retrieval (ANN) followed by deep scoring networks; deployed at YouTube [1], Meta [11], and all major platforms
- **DCN V2 / Deep & Cross architectures** — Explicit cross-feature interaction modeling replacing manual feature engineering; state-of-the-art on CTR prediction [15]
- **FTRL online learning** — Per-coordinate adaptive learning rates for real-time CTR/CVR prediction in ads; remains unmatched for latency-critical auction scoring [4]
- **LLM-enhanced retrieval** — Using language models for semantic query understanding, cold-start embedding generation, and offline feature extraction [14][12]
- **Multi-objective constrained ranking** — Pareto-aware optimization balancing relevance, diversity, fairness, and revenue with explicit business constraints [10]

### Recent Breakthroughs (last 12 months)

- **LLM-as-feature-generator pipelines** (2024-2025): Offline LLM processing generates semantic embeddings and structured attributes, enabling cold-start items to participate in retrieval immediately [14]
- **DCN V2** (2021, now widely adopted): Improved cross networks with mixture-of-experts and low-rank decomposition outperform DeepFM on large-scale CTR benchmarks [15]
- **Sampling-bias correction at scale** (Yi et al., maturing in production): Log-Q correction for in-batch negatives eliminates popularity bias in two-tower training [2]
- **Position-bias-aware training** (maturing): IPW and position-aware models now standard in production ranking pipelines [5][6]

### Open Problems

- **Real-time LLM integration**: LLM inference latency (100-500ms) incompatible with sub-50ms ranking SLAs; no efficient solution for full-catalog semantic scoring
- **Multi-objective Pareto optimization**: Finding the efficient frontier across relevance, diversity, fairness, and revenue without exhaustive search remains computationally expensive [10]
- **Distribution shift in online learning**: Non-stationary user behavior causes model drift faster than retraining cycles can compensate [4]
- **Unbiased evaluation from biased logs**: Position bias correction via IPW introduces high variance; optimal bias-variance tradeoff is domain-specific [5][6]

## Executive Summary

Recommendation and ranking systems retrieve candidates from large catalogs and score them for relevance, using a multi-stage pipeline that balances recall, precision, and latency. The core architectural decision is where each model type adds value: two-tower models for fast retrieval [1][3], deep interaction networks for precise scoring [9][15], FTRL for real-time calibration [4], and LLMs for semantic understanding where behavioral data is absent [14].

- **Choose two-tower retrieval** when catalog > 100K items and latency budget < 10ms per candidate
- **Choose cross-attention/DCN scoring** when precision matters on a reduced candidate set (top 200-500)
- **Choose LLM augmentation** for cold-start, semantic understanding, and offline feature generation
- **Choose FTRL online learning** for real-time auction scoring with billions of sparse features

**The killer framing:** "The evolution from FTRL to deep learning to LLM-enhanced is not replacement but accumulation — each layer serves where it adds unique value. The question is never 'which model' but 'which model at which stage for which latency budget.'"

Cost headline: Classical pipeline serves at $0.0003/query; adding LLM reranking on all queries costs 20x more — selective application on 20% of high-value queries captures 80% of the value [10].

```
Multi-Stage Pipeline Decision Tree
───────────────────────────────────
Catalog size?
├── <1K items → Score all with single model (no retrieval needed)
├── 1K-100K → Two-tower retrieval [1] + DNN scoring [9][15]
└── >100K → Two-tower ANN [1] + DNN scoring + optional LLM rerank [14]
    └── Cold-start items?
        ├── YES → LLM feature generation [14] + exploration
        └── NO → Behavioral features dominate
    └── Latency budget?
        ├── <50ms → Classical pipeline only [4]
        └── 100-300ms → Add LLM reranking on top-K [14]
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Ranking vs retrieval vs explanation; catalog size; latency SLA; objectives | Is the system optimizing CTR, CVR, revenue, or a multi-objective combination? What is the cold-start fraction? |
| 2. Identify constraints | Scale (millions of items), latency (<100ms p99), sparse feedback, conflicting objectives | LLM-per-item is too expensive at scale. Where does semantic understanding add value vs behavioral signals? |
| 3. Propose baseline | Multi-stage: two-tower retrieval [1] → feature-based ranker [9]. FTRL for real-time signals [4] | Prove value with proven architecture before adding complexity. Classical pipeline handles 80%+ of queries. |
| 4. Identify gaps | Cold-start items get no exposure; semantic mismatches missed by behavioral features; position bias in training data [5] | The constraint is often adoption or coverage, not model accuracy on head queries. |
| 5. Introduce improvements | LLM offline features [14], cross-attention scoring [15], IPW position correction [5][6], hard negative mining [13] | Each improvement has a specific cost-value tradeoff; never add uniformly. |
| 6. Add evaluation + guardrails | NDCG, calibration ECE, CTR, CVR, diversity, position-debiased metrics [5][6], online A/B | Offline metrics miss marketplace effects. Double-randomized experimentation for causal measurement. |
| 7. Discuss scaling tradeoffs | Online learning freshness vs batch quality [4]; retrieval breadth vs latency; multi-objective balancing [10] | The right answer depends on traffic volume, cold-start fraction, and business metric sensitivity. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Retrieval model | Two-tower (dot product) [1][3] | Cross-attention | Catalog >100K, need ANN indexing | Candidate set <500, precision critical |
| Online vs batch | FTRL online learning [4] | Daily batch retrain | Auction/bid systems, non-stationary data | Stable catalog, weekly feature changes |
| Negative sampling | In-batch negatives [2] | Hard negative mining [13] | Training speed priority, initial model | Quality priority, model plateau |
| Position correction | IPW weighting [5] | Position-aware feature [6] | Have randomization traffic for propensity | No randomization budget available |
| Multi-objective | Weighted scalarization | Constrained optimization [10] | Exploratory phase, few objectives | Production with business guardrails |
| LLM integration | Offline feature generation [14] | Real-time reranking | All queries, amortized cost | High-value queries only, budget allows |

## System Design Walkthrough

### Opening Frame

Production recommendation is a multi-stage funnel where each layer optimizes a different tradeoff: recall at scale (retrieval), precision at speed (scoring), semantic quality at cost (reranking). The non-obvious insight: the highest-leverage improvements often come not from better models but from better training data — hard negative mining [13], position bias correction [5], and calibration together yield more lift than architecture changes alone.

### Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                  Multi-Stage Recommendation Pipeline                    │
├────────────────┬───────────────┬────────────────┬─────────────────────┤
│  Retrieval     │  Scoring      │  Reranking     │  Business Rules     │
│  (Stage 1)     │  (Stage 2)    │  (Stage 3)     │  (Stage 4)          │
├────────────────┼───────────────┼────────────────┼─────────────────────┤
│ Two-tower [1]  │ DCN V2 [15]   │ LLM semantic   │ Diversity/policy    │
│ ANN index      │ DeepFM [9]    │  [14] (opt.)   │ Freshness/fairness  │
│ CF signals     │ FTRL [4]      │ Multi-obj [10] │ Dedup/filtering     │
│ ~1000 cands    │ ~200 scored   │ ~50 reranked   │ Final top-K         │
└────────────────┴───────────────┴────────────────┴─────────────────────┘
       <10ms           10-50ms        100-300ms          <5ms
```

- **Retrieval**: Two-tower models [1][3] encode queries and items independently; dot-product enables ANN search over millions of items in <10ms
- **Scoring**: Deep interaction models [9][15] with hundreds of features score the reduced candidate set; FTRL [4] provides real-time calibration
- **Reranking (optional)**: LLM-based semantic reranking [14] on top-50; multi-objective optimization [10] balances competing goals
- **Business rules**: Diversity enforcement, freshness boost, policy filtering applied deterministically

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Two-tower loses fine-grained interaction | Cross-attention on top-200; late interaction (ColBERT-style) | +1-5ms/candidate; can't use ANN |
| Position bias in click training data | IPW correction [5][6] with randomization-based propensity | Requires 1-5% randomized traffic (slight UX cost) |
| Popular items dominate retrieval | Log-Q sampling bias correction [2]; hard negative mining [13] | Compute cost for mining; risk of false negatives |
| Cold-start items invisible | LLM feature generation [14]; contextual bandits for exploration | LLM offline cost; exploration reduces short-term CTR |
| Single-objective misses business goals | Constrained multi-objective optimization [10] | Secondary objectives cap primary metric ceiling |
| Model calibration drift | Weekly isotonic regression recalibration; per-locale calibration | Engineering overhead; locale-specific monitoring |

### Scaling Summary

- **10x candidates**: Retrieval stays efficient (ANN scales sub-linearly); scoring needs model distillation or GPU batching
- **100x catalog**: Embedding index sharding; periodic full re-index; FTRL memory becomes a concern (billions of features) [4]
- **1000x traffic**: Horizontal scaling of serving; pre-computed batch recommendations for returning users; LLM reranking becomes selective-only (cost prohibitive at full scale)

## Interview Q&A Bank

### Q1: How does a two-tower model work for recommendation retrieval?

> **Quick answer:** Two separate neural networks encode queries and items into the same embedding space; relevance is approximated by dot product, enabling sub-linear ANN retrieval over millions of items [1][3].

The query tower processes user context (history, demographics, session) into a d-dimensional vector. The item tower processes item features (title, category, attributes) into the same space. Training uses contrastive loss on (query, positive_item) pairs with in-batch negatives [2]. At serving time, item embeddings are pre-computed and indexed for ANN lookup (HNSW, ScaNN), giving O(log N) retrieval from catalogs of millions.

The fundamental limitation is the representation bottleneck: all query-item interaction reduces to a single scalar (dot product). This means "red running shoes" vs "red hiking boots" may score similarly because most embedding dimensions align. Cross-attention captures this distinction but cannot be pre-indexed [1].

| Architecture | Interaction | Quality vs Baseline | Serving Cost |
|---|---|---|---|
| Two-tower (dot) [1][3] | query . item | Baseline | O(log N) with ANN |
| Two-tower + MLP head | MLP(q, i) | +5-10% | O(K) — no ANN |
| Cross-attention | Full token attention | +20-30% | O(K x seq_len^2) |

**Hard follow-up:** How do you handle the fact that in-batch negatives are biased toward popular items?

> Yi et al. [2] showed that in-batch negatives over-represent popular items because they appear in more batches. The fix is log-Q correction: weight each negative by 1/log(freq + 1), giving rare items higher negative weight. This forces the model to distinguish between truly irrelevant items and simply unpopular ones.

### Q2: What is FTRL and why is it still used in modern recommendation systems?

> **Quick answer:** FTRL (Follow The Regularized Leader) is an online learning algorithm with per-coordinate learning rates and L1 sparsity that enables real-time model updates on billions of sparse features — critical for auction systems where the world changes hourly [4].

FTRL maintains per-feature accumulators (z and n) that track gradient history. The key advantages over SGD: (1) L1 regularization produces truly sparse weights (exactly zero), critical when models have billions of features. (2) Per-coordinate learning rates automatically adapt — a rare advertiser-keyword feature gets a higher effective learning rate than a global CTR feature. (3) Regret bounds hold under non-stationarity [4].

In modern systems, FTRL handles the real-time calibration layer while deep models provide representation learning. The combination works because FTRL excels at sparse tabular features (user_id x item_id x hour) while DNNs excel at dense learned representations.

**Hard follow-up:** When would you replace FTRL with a neural network for online learning?

> When feature interactions are the bottleneck rather than feature sparsity. FTRL is linear — it cannot model interactions without manual crosses. A shallow network with online Adam captures interactions automatically, but loses FTRL's sparsity and per-coordinate adaptivity. In practice, both run in parallel: FTRL for calibration, DNN for representation [4].

### Q3: How does DeepFM combine factorization machines with deep learning?

> **Quick answer:** DeepFM jointly trains a factorization machine (capturing second-order feature interactions) and a deep network (capturing higher-order interactions) with shared embeddings, eliminating manual feature engineering [9].

The FM component models pairwise interactions: y_FM = w_0 + sum(w_i * x_i) + sum_pairs(<v_i, v_j> * x_i * x_j). The deep component feeds the same embeddings through multiple dense layers. Both share the embedding layer, enabling end-to-end training without feature engineering [9].

Compared to Wide & Deep (which requires manual cross features for the wide component), DeepFM automates interaction discovery. Compared to DCN V2 [15], DeepFM is simpler but less expressive on high-order interactions.

| Model | Feature Interactions | Manual Engineering | Expressiveness |
|---|---|---|---|
| Logistic + FTRL [4] | None (linear) | Full manual | Low |
| FM [7] | 2nd order | None | Medium |
| DeepFM [9] | 2nd + higher | None | High |
| DCN V2 [15] | Explicit cross layers | None | Very high |

**Hard follow-up:** Why do factorization machines work well with sparse features?

> FMs factorize the interaction weight matrix into low-rank embeddings: W_ij = <v_i, v_j> [7]. This means even feature pairs that never co-occur in training get a learned interaction weight via their embeddings. For sparse recommendation data where most user-item pairs are unobserved, this generalization is critical.

### Q4: How do you design a multi-stage recommendation pipeline for a 100M-item catalog?

> **Quick answer:** Stage 1 retrieves ~1000 candidates via ANN in <10ms [1]; Stage 2 scores with a deep model (DCN V2/DeepFM) in 10-50ms [9][15]; Stage 3 optionally applies LLM reranking on top-50 for semantic quality [14]; Stage 4 enforces business rules.

The key insight: each stage trades off recall for precision at increasing computational cost. Stage 1 (two-tower + ANN [1]) must be fast because it searches the full catalog. Stage 2 (deep scoring [9][15]) can be expensive per-candidate because it only sees 1000 items. Stage 3 (LLM [14]) can be very expensive because it only sees 50.

Design decisions at each stage: retrieval needs multiple sources (embedding similarity, collaborative filtering, trending, rules) to maximize recall. Scoring needs rich features (behavioral + contextual + item attributes) for precision. Reranking needs semantic understanding for cases where behavioral data is insufficient.

**Hard follow-up:** Your Stage 2 ranker has been optimized for years — when do you invest in Stage 3 LLM reranking instead?

> When failure analysis reveals errors are semantic mismatches (not feature engineering gaps), when cold-start items are a significant fraction, and when the top-50 from Stage 2 contains items that are behaviorally similar but semantically different. The signal: adding features yields <0.1% AUC improvement but qualitative review shows clear semantic errors.

### Q5: How do you correct position bias in recommendation training data?

> **Quick answer:** Position bias means users click items at the top regardless of quality; IPW (Inverse Propensity Weighting) corrects by up-weighting clicks from lower positions where examination probability is lower [5][6].

The Position-Based Model assumes: P(click | item, position) = P(relevant | item) x P(examine | position) [5]. IPW weights each training example by 1/P(examine | position). Items clicked at position 1 (P(examine) near 1.0) get weight ~1; items clicked at position 10 (P(examine) ~0.3) get weight ~3.3 — these clicks are more informative because the user chose to look that far down.

Propensity estimation approaches: (1) Randomization — shuffle 1-5% of results, measure position-dependent click rates [6]. (2) EM algorithm — jointly estimate examination and relevance from observational data. (3) Position-aware model — include position as a feature during training, set position=0 at inference [6].

The key challenge: high IPW weights (for low-position clicks) amplify noise. Clipping weights at 10-20 trades some bias for much lower variance [5].

**Hard follow-up:** You correct for position bias, but CTR drops because you're surfacing less-popular items higher. How do you handle this?

> Measure CTR per-position (not aggregate). If items at each position get higher CTR after debiasing, the ranker is better even if aggregate CTR drops. Run a 30-day A/B: debiased typically wins on retention, diversity, and long-tail conversion even if short-term aggregate CTR dips.

### Q6: How does negative sampling strategy affect two-tower model quality?

> **Quick answer:** The choice of negatives determines what distinctions the model learns — random negatives teach trivial discrimination, while hard negatives force fine-grained intent matching that matters at ranking time [2][13].

Negative sampling strategies in order of difficulty:

1. **Random negatives**: Sample from catalog uniformly. Easy to discriminate; model learns gross category differences but not fine-grained relevance [2].
2. **In-batch negatives**: Other items in the batch serve as negatives. Free, harder than random, but biased toward popular items [2].
3. **Hard negatives**: Items similar to the positive but not relevant (e.g., same category, different intent) [13]. Force fine-grained discrimination. The training signal from one hard negative approximates 100 random negatives.
4. **Impression-based**: Items shown but not clicked. True negatives but position-biased.

Production recipe: 70% in-batch negatives (with log-Q correction [2]) + 30% mined hard negatives [13]. Yang et al. [13] showed that mixed negative sampling outperforms either strategy alone.

**Hard follow-up:** How do you prevent a hard negative from actually being a relevant item the user simply did not interact with?

> Only mine hard negatives from items the user was shown but did not click (impression-based). Apply confidence thresholding: only use items with high embedding similarity but low predicted relevance by a separately-trained model. Label smoothing (0.1 for unclicked items at top positions vs 0.0 at bottom) accounts for uncertainty.

### Q7: How do you balance multiple conflicting objectives in a ranking system?

> **Quick answer:** Use constrained optimization — maximize the primary objective (e.g., relevance) subject to business-defined thresholds on secondary objectives (diversity, fairness, freshness) — rather than arbitrary weighted sums [10].

The Zhao et al. [10] approach at YouTube: predict multiple objectives (click, watch-time, satisfaction, freshness) with shared-bottom multi-task learning, then combine using a context-dependent policy.

Approaches ordered by sophistication:
1. **Scalarization**: score = w1*f1 + w2*f2. Simple but weights are arbitrary and can't find non-convex Pareto solutions.
2. **Constrained optimization**: maximize f1 subject to f2 >= threshold. More principled — thresholds are explicit business decisions [10].
3. **MMR reranking**: At each position, select item maximizing lambda*relevance - (1-lambda)*max_similarity_to_selected. Natural diversity-relevance balance.
4. **Pareto set generation**: Compute Pareto-optimal slates; select based on user context.

> [!experience] At Amazon Ads, we used constrained optimization: maximize advertiser ROI subject to marketplace health guardrails (CVR and RoAS floors). The separation was organizationally critical: ML optimizes within constraints, business sets constraints.

**Hard follow-up:** Your diversity constraint reduces CTR by 3%. How do you justify keeping it?

> Show long-term data: users exposed to diverse recommendations have higher 30-day retention. Without diversity, the system converges to recommending the same items to everyone — and when those items become stale, the entire system degrades. The 3% CTR drop is insurance against long-term engagement collapse.

### Q8: When does traditional ML outperform LLMs for ranking?

> **Quick answer:** Traditional ML wins when you need calibrated probabilities for auctions [4], real-time serving at <10ms [4][11], tabular/behavioral features, or incremental online learning — LLMs add value only where content understanding or cold-start is the bottleneck [14].

| Scenario | Winner | Why |
|---|---|---|
| Calibrated P(click) for bid = value x P(click) | FTRL/DNN [4] | LLMs don't produce calibrated probabilities |
| 100K candidates in <10ms | Shallow DNN [11] | LLMs are 1000x slower per item |
| Tabular behavioral features | GBDT/DNN [9][15] | LLMs are for unstructured content, not f(clicks, device, hour) |
| Real-time adaptation (hourly changes) | FTRL [4] | LLMs require batch retraining |
| Cold-start item understanding | LLM [14] | No behavioral data; content is all you have |
| Semantic query-item matching | LLM [14] | Fine-grained language understanding |

The insight: LLMs and traditional ML are complementary layers. Traditional ML handles behavioral prediction at scale; LLMs handle content understanding and cold-start [14].

**Hard follow-up:** If traditional ML is better for so many cases, what's the actual value-add of LLMs?

> LLMs add value precisely where behavioral data is absent: understanding what an item IS from descriptions, understanding what a user WANTS from natural language queries, bootstrapping cold-start recommendations, and generating explanations that build trust. The best systems use both — each at the stage where it adds unique value.

### Q9: How do you handle cold-start for new items with no behavioral data?

> **Quick answer:** LLMs read item descriptions to generate content embeddings for immediate retrieval participation [14], extract structured attributes for the ranking model, and bootstrap collaborative signals from semantically similar items.

Cold-start approaches by data requirement:
1. **LLM content embedding** [14]: Process item description → embedding → immediate participation in ANN retrieval. Zero behavioral data needed.
2. **Attribute extraction**: LLM extracts category, price tier, quality signals → features for ranking model.
3. **Similar-item transfer**: Find semantically similar items with behavioral history → transfer their interaction signals as priors.
4. **Contextual bandits**: Explore by showing cold-start items to a small traffic slice; learn from feedback; expand or suppress exposure.

The key tradeoff: pure semantic similarity can surface items that are content-relevant but quality-mismatched. A new item semantically similar to a bestseller may be much lower quality. Mitigation: combine semantic embedding with quality priors (seller reputation, listing completeness) and throttled exploration.

**Hard follow-up:** Your LLM-generated embedding places a new low-quality item near a popular high-quality item. How do you prevent recommending it widely?

> Never give cold-start items full exposure based on embedding similarity alone. Use quality priors (seller score, listing completeness) as initial gates. Explore with throttling: expose to 1% of eligible traffic. If engagement metrics (CTR, dwell time) exceed a threshold within 48 hours, increase exposure. If not, suppress.

### Q10: How do you design unbiased evaluation when all your data comes from a biased production system?

> **Quick answer:** Use IPW to reweight logged interactions by inverse examination probability [5], randomization experiments on small traffic slices to estimate propensities [6], and counterfactual evaluation methods that estimate new ranker performance from old ranker logs.

The challenge: you want to evaluate a new ranking model, but your logged data was collected under the old model. Items the old model ranked highly got more exposure and more clicks — this doesn't mean they're better, just that they were shown more.

Counterfactual evaluation via IPS (Inverse Propensity Scoring): for each logged (query, item, click) triple, weight by the ratio of the new model's probability of showing that item to the old model's probability. Items that would be shown more by the new model but were rarely shown by the old model get up-weighted [5].

In practice, combine: (1) small randomization traffic (1-5%) for unbiased propensity estimation [6], (2) IPW-corrected offline evaluation for rapid iteration, (3) full A/B test for final deployment decisions. The layering minimizes the need for expensive online experiments during model development.

**Hard follow-up:** Your propensity estimates have high variance for items rarely shown by the old model. How do you handle this?

> Clip propensity weights at max_weight=15-20 (trades some bias for lower variance). Use doubly-robust estimation: combine an imputation model (predicts what the click would have been) with IPW. Bias from imputation errors is corrected by IPW; variance from extreme weights is bounded by the imputation model [5].

### Q11: How does DCN V2 improve over DeepFM for feature interaction modeling?

> **Quick answer:** DCN V2 replaces the fixed factorization of DeepFM with learnable cross layers that model arbitrary-order feature interactions explicitly, combined with a mixture-of-experts structure for expressiveness [15].

DCN V2's cross layer at layer l: x_{l+1} = x_0 * (W_l * x_l + b_l) + x_l, where * denotes element-wise multiplication [15]. Each layer explicitly models one additional order of feature interaction. Stacking L cross layers captures up to (L+1)-order interactions with O(d) parameters per layer (vs O(d^2) for a dense layer).

Key improvements over the original DCN: (1) Low-rank decomposition of W_l reduces parameters while maintaining expressiveness. (2) Mixture-of-experts within cross layers allows different interaction patterns for different input subspaces. (3) Stacked + parallel architectures combine explicit crossing with implicit DNN interactions [15].

DCN V2 outperforms DeepFM on large-scale CTR benchmarks because it models higher-order interactions explicitly rather than relying on the deep component to discover them implicitly [15].

**Hard follow-up:** When would you still prefer DeepFM over DCN V2?

> When the feature space is moderate (<1000 features), training data is limited, and second-order interactions suffice. DeepFM [9] is simpler to implement, faster to train, and less prone to overfitting on small datasets. DCN V2 shines with large feature spaces and abundant data where higher-order interactions provide significant lift [15].

### Q12: How do you integrate LLMs into recommendation without blowing up latency and cost?

> **Quick answer:** Use LLMs offline for feature generation (amortized cost, zero runtime latency) and selectively in real-time for high-value queries only — the key insight is that 80% of queries get no benefit from LLM semantic understanding because behavioral signals suffice [14].

LLM integration points ranked by ROI:
1. **Offline feature generation** (highest ROI): LLM processes item catalog → structured attributes + embeddings. Amortized once per item, served forever. Zero runtime cost [14].
2. **Query understanding** (medium ROI): LLM rewrites/expands ambiguous queries before retrieval. Adds 50-100ms but only for complex queries.
3. **Reranking top-K** (high ROI, selective): Semantic reranking of top-50. Adds 100-300ms. Apply only to high-value/complex queries [14].
4. **Explanation generation** (medium ROI): Post-ranking explanations for trust-building. Can be cached for common items.

The cost math: LLM scoring all 100K candidates at $0.001/item = $100/query. Classical ranker: $0.0001/query. Use LLMs where they provide 100,000x more insight — semantic understanding on small candidate sets, not brute-force scoring [14].

> [!experience] At Amazon Ads, LLM-based semantic retrieval expanded coverage by +2200 bps for cold-start queries while the real-time ranking path stayed pure deep learning at <100ms for 300M+ MAU.

**Hard follow-up:** A PM wants to replace the entire ranking stack with an LLM. How do you push back?

> Cost math: 50M queries/day x $0.007/query (LLM on all) = $10.5M/month vs $450K/month for classical. Show the 20x cost increase yields <5% quality improvement on queries with behavioral data. Frame: "Use LLMs where behavioral data fails (cold-start, semantic mismatch); use classical ML where it excels (calibrated scoring at scale)."

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): Two-Tower Architecture — Dot-Product Approximation, Hard Negative Mining, and Contrastive Loss</strong></summary>

**The two-tower model** [1][3] approximates relevance through inner product of independently computed embeddings:

```
score(q, i) = <f_query(q), f_item(i)> = q_emb^T * i_emb
```

where f_query and f_item are deep networks producing d-dimensional embeddings.

**Contrastive loss formulation** (InfoNCE / in-batch softmax):

```
L = -log( exp(sim(q, i+) / tau) / (exp(sim(q, i+) / tau) + sum_j exp(sim(q, i_j-) / tau)) )
```

where tau is a temperature parameter, i+ is the positive item, and {i_j-} are negatives [1]. In-batch negatives: for batch size B, each positive item serves as negative for all other queries in the batch — yielding B-1 negatives per pair for free [2].

**The sampling bias problem**: In-batch negatives are sampled proportional to item popularity (popular items appear in more batches). This creates a systematic bias: the model under-penalizes popular items as negatives and over-penalizes rare items. Yi et al. [2] prove that the unbiased estimator requires correction:

```
L_corrected = -log( exp(s(q,i+)) / (exp(s(q,i+)) + sum_j exp(s(q,i_j-) - log(p_j))) )
```

where p_j is the sampling probability of item j (proportional to its frequency). This log-Q correction ensures rare items are treated as "harder" negatives.

**Hard negative mining** [13]: Random negatives are too easy — most random items are obviously irrelevant. Hard negatives are items with high embedding similarity but different intent (e.g., "running shoes" positive → "hiking boots" hard negative). Yang et al. [13] show mixed sampling (70% in-batch with log-Q + 30% mined hard negatives) outperforms either strategy alone by 4-6% in Recall@K.

**Dot-product limitations**: The interaction reduces to a single scalar. Given d=128, the model compresses all query information into 128 numbers. Token-level alignment is lost — "buy red shoes" and "review red shoes" produce similar embeddings despite radically different intents. The production compromise: two-tower for retrieval (ANN over 100M+ items), cross-attention for scoring on the reduced set [1][3].

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): FTRL Online Learning — Per-Coordinate Learning Rates and Feature Hashing at Scale</strong></summary>

**FTRL-Proximal** [4] solves online convex optimization with L1 regularization for true sparsity:

```
At each round t:
  w_{t+1} = argmin_w [ sum_{s=1}^t g_s . w + (1/2) sum_{s=1}^t sigma_s ||w - w_s||^2
                        + lambda_1 ||w||_1 + (lambda_2/2) ||w||_2^2 ]
```

**Per-coordinate learning rates**: FTRL maintains per-feature accumulators n_i (sum of squared gradients for feature i). The effective learning rate for feature i is alpha / (beta + sqrt(n_i)) [4]. A feature that updates once per day (rare advertiser-keyword cross) gets a much higher learning rate than one updating millions of times (global CTR). This is critical in ads where feature sparsity spans 6+ orders of magnitude.

**Sparsity via L1**: At prediction time, FTRL checks if |z_i| <= lambda_1 — if so, w_i = 0 exactly. This yields truly sparse models (90%+ zeros at serving time), critical for memory efficiency with billions of features [4].

```python
def ftrl_predict(features, z, n, alpha, beta, lambda1, lambda2):
    w = {}
    for i in features:
        if abs(z.get(i, 0)) <= lambda1:
            w[i] = 0.0  # TRUE sparsity: feature contributes nothing
        else:
            sign_z = -1.0 if z[i] < 0 else 1.0
            w[i] = -(z[i] - sign_z * lambda1) / (
                (beta + sqrt(n.get(i, 0))) / alpha + lambda2)
    return sigmoid(sum(w[i] * features[i] for i in w if w[i] != 0))
```

**Feature hashing at scale**: With billions of possible feature crosses (user_id x item_id x hour x device), explicit enumeration is impossible. McMahan et al. [4] use hashing: hash(feature_name) → bucket_id in a fixed-size array. Collisions are acceptable because: (1) L1 regularization zeros out low-signal colliding features, (2) the collision rate at 2^24 buckets is <0.1% for typical feature distributions.

**Production reality**: At Yahoo/Google scale, FTRL serves click prediction with: model size ~10GB (after sparsity), update latency <1ms per event, and 100% query-ad pair coverage [4]. No neural architecture matches this combination of speed, sparsity, and online adaptivity for auction-critical CTR prediction.

</details>

<details><summary><strong>DE Probe 3 (DATA): Negative Sampling Strategies — In-Batch vs Global, Popularity Debiasing, Hard Negatives</strong></summary>

In recommendation training, true negatives (items a user saw and rejected) are rare. Most "negatives" are items the user never encountered. The negative sampling strategy determines what the model learns to discriminate [2][13].

**In-batch negatives** [2]: For batch size B with pairs {(q_i, item_i+)}, each item_j (j != i) serves as negative for query q_i. Advantages: (1) Free — no extra data loading. (2) Diverse — batch contains items from different categories. (3) Moderately hard — items relevant to someone are harder than random catalog items.

**Popularity bias in in-batch negatives**: Item j appears as a negative with probability proportional to its frequency in the training data. Popular items are over-represented as negatives, teaching the model "popular items are irrelevant" — the opposite of reality. Yi et al. [2] derive the correction:

```
Corrected logit for negative j: s(q, j) - log(p_j)
where p_j = count(j) / sum(counts)
```

This is equivalent to importance-weighted estimation that debiases toward a uniform item distribution.

**Hard negative mining** [13]: Mine items that are embedding-similar to the positive but from a different intent/category. Yang et al. [13] propose mixed negative sampling:

```
Negatives for (q, i+):
  - 70% in-batch (with log-Q correction) [2]
  - 20% hard negatives (top-K nearest by current embeddings, filtered by label)
  - 10% random (from global catalog, for calibration)
```

**The false negative problem**: A "hard negative" might actually be relevant — the user simply hasn't interacted with it yet. If you train the model to push away a relevant item, you poison the representation. Mitigations: (1) Only mine hard negatives from items the user was explicitly shown (impression-based). (2) Confidence filtering: exclude hard negatives whose relevance probability exceeds 0.3 according to a separately-trained model. (3) Label smoothing: assign soft labels (0.05-0.1) to hard negatives instead of 0, acknowledging uncertainty [13].

**Empirical impact** (approximate lifts):
```
Random negatives only:         Recall@100 = 0.45
+ In-batch (no correction):   Recall@100 = 0.52 (+7 points)
+ Log-Q correction [2]:       Recall@100 = 0.55 (+3 points)
+ Hard negative mining [13]:  Recall@100 = 0.61 (+6 points)
```

The gains from better negative sampling frequently exceed gains from architecture changes.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Position Bias and IPW — Unbiased Evaluation from Biased Logs</strong></summary>

**The problem**: Logged click data is confounded by position. We observe P(click | item, position) but want to learn P(relevant | item). Without correction, models learn "position 1 is good" rather than "this item is good" [5][6].

**Position-Based Model (PBM)** assumption [5]:

```
P(click | item i, position k) = P(relevant | item i) * P(examine | position k)
```

This factorization assumes examination depends only on position, and relevance depends only on the item. It's the foundational assumption behind IPW correction.

**IPW correction for training** [5]:

```
Weighted loss: L = sum_samples w_k * loss(y_hat, y)
where w_k = 1 / P(examine | position k)
```

Clicks from position 1 (P(examine) ~ 0.95) get weight ~1.05. Clicks from position 8 (P(examine) ~ 0.25) get weight ~4.0. The intuition: a click at position 8 is much more informative about true relevance because the user made an effort to examine that far.

**Propensity estimation methods** [6]:

1. **Randomization (gold standard)**: Shuffle 1-5% of traffic randomly. P(examine | k) = click_rate(k) / avg_relevance. Requires sacrificing some user experience.
2. **Regression discontinuity**: Exploit natural position discontinuities (above/below fold). Compare click rates at positions 5 vs 6 if the fold is between them.
3. **EM algorithm** (Wang et al. [6]): Jointly estimate examination and relevance from observational data. Assumes clicks follow PBM; iterates between estimating P(examine) and P(relevant).

**IPW variance problem**: For items at position 20 (P(examine) ~ 0.05), the weight is 20x. These extreme weights amplify noise. Joachims et al. [5] recommend clipped IPW:

```
w_k = min(1 / P(examine | k), max_weight)
```

Typical max_weight = 10-20. The bias-variance tradeoff: low threshold → under-corrects (biased but stable); high threshold → fully corrects (unbiased but noisy). Plot MSE as a function of clip threshold on held-out randomized data to find the optimum [5].

**When PBM breaks**: (1) Examination depends on the item (attractive thumbnails get examined regardless of position). (2) Context effects (previous items affect attention to subsequent ones). (3) Heterogeneous users (some scroll deeply, some don't). Extensions: cascading models, user-specific propensities, and doubly-robust estimators that combine IPW with an imputation model for variance reduction [6].

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Multi-Objective Ranking — Pareto Optimization, Scalarization, Constraint Satisfaction</strong></summary>

Real ranking systems serve multiple conflicting objectives simultaneously: relevance, engagement (CTR), conversion (CVR), diversity, fairness, freshness, and revenue [10].

**The conflict matrix**: Maximizing relevance concentrates recommendations on similar items (reducing diversity). Maximizing engagement favors clickbait (reducing conversion). Maximizing revenue favors established sellers (reducing fairness). No single ranking optimizes all simultaneously.

**Approach 1: Weighted scalarization** [10]:

```
score(item) = w_click * P(click) + w_convert * P(convert) + w_fresh * freshness_score
```

Zhao et al. [10] at YouTube use this with learned weights conditioned on user context. Limitation: can't find Pareto-optimal solutions on non-convex regions; weights require careful tuning and normalization.

**Approach 2: Constrained optimization**:

```
maximize: E[P(satisfy) | ranking]
subject to: diversity(slate) >= 0.4
            fairness(exposure) >= min_threshold
            P(convert) >= historical_floor
```

Solve via Lagrangian relaxation or greedy re-ranking (at each position, select the item maximizing the primary objective that satisfies all constraints). Thresholds are business decisions, not model parameters — this organizational separation is critical [10].

**Approach 3: Multi-task learning with shared bottom** [10]:

```
Shared embedding layers → [task-specific towers]
  → P(click), P(convert), P(long_dwell), P(share)
      ↓
  Context-dependent combination policy
      ↓
  Final ranking score
```

Each task head uses the same learned representations but produces different predictions. The combination policy (e.g., multiplicative: score = P(click)^a * P(convert)^b) can vary by user segment [10].

**Pareto-optimal slate generation**: Generate K diverse rankings (each emphasizing a different objective). For each user context, select the ranking closest to the preferred tradeoff point. This requires efficient Pareto frontier computation — evolutionary algorithms (NSGA-II) or linear scalarization with varied weights can approximate the frontier.

**Production pattern**: Predict all objectives with shared-bottom multi-task network [10][11], combine with a tuneable policy (initially scalarized, evolved to constrained), enforce hard business guardrails (fairness floors, safety gates) as post-ranking filters. Monitor each objective independently — a "Pareto regression" (where one objective improves but another degrades without justification) triggers review.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): LLM-Enhanced Retrieval — Semantic Understanding for Query-Item Matching</strong></summary>

Traditional retrieval relies on behavioral signals (collaborative filtering) or shallow text matching (BM25, keyword overlap). LLM-enhanced retrieval uses deep language understanding to match queries with items based on semantic meaning — critical for cold-start, long-tail, and natural language queries [14][12].

**Integration architectures for LLM in retrieval** [14]:

1. **LLM as feature generator (offline)**: Process item catalog offline → generate dense embeddings and structured attributes. Index for ANN retrieval. Zero runtime LLM cost.
2. **LLM as query expander (online, lightweight)**: Rewrite ambiguous queries ("something for cold weather running") into structured queries before standard retrieval. Adds 50-100ms.
3. **LLM as scoring backbone (offline distillation)**: Use LLM to generate relevance labels for query-item pairs, then distill into a fast two-tower model. Gets LLM quality at two-tower speed.
4. **LLM as reranker (online, selective)**: Score top-K items using LLM with full item descriptions in context. Most expensive; apply to <20% of traffic.

**DSSM to LLM evolution** [3][14]:

```
DSSM (2013) [3]:     word hashing → MLP → embedding → cosine sim
Two-tower (2016) [1]: feature embedding → DNN → embedding → dot product
LLM-enhanced (2023+) [14]: 
  - Offline: LLM(item_text) → dense embedding → index
  - Online: two-tower retrieval + LLM reranking on top-K
```

Huang et al. [3] introduced deep semantic matching via DSSM; modern LLM-enhanced retrieval extends this by using transformer-based understanding for items with rich textual descriptions.

**The recommendation-as-language paradigm** [12]: Zhu et al. propose treating user-item interactions as language sequences: "[USER] watched [ITEM_A], bought [ITEM_B], searched [QUERY] → recommend [?]". The LLM's language understanding enables reasoning about user intent. Limitation: slow inference and inability to generalize to new items not in training vocabulary [12].

**Production reality** [14]: Pure LLM-as-retriever doesn't scale (can't index LLM outputs for ANN without two-tower decomposition). The practical architecture: LLM generates item embeddings offline (one-time cost), these are indexed alongside behaviorally-trained embeddings, and retrieval blends both sources. For cold-start items, LLM embeddings are the only retrieval path. For items with rich behavioral data, behavioral embeddings dominate. Lin et al. [14] survey shows this hybrid approach captures 80-90% of LLM quality at 1/100th the runtime cost.

</details>

## Cost Model

### Per-Query Cost Breakdown

| Component | Cost/Query | Assumptions | Optimization Lever |
|-----------|-----------|-------------|-------------------|
| Candidate generation (ANN) | $0.00005 | HNSW over 10M items | Self-host at scale; batch pre-compute |
| ML ranker (Stage 2) | $0.0001 | DNN on 500 candidates, GPU | Batching, distillation |
| LLM reranking (Stage 3) | $0.005 | 50 candidates, Haiku list-wise | Selective application; caching |
| Feature generation (offline) | $0.0001 | Amortized over queries | Batch during ingestion |
| **Total (classical only)** | **~$0.0003** | | |
| **Total (with LLM rerank)** | **~$0.007** | | |

### Monthly Cost at Scale

| Scale | Queries/Day | Monthly Cost | Notes |
|-------|------------|-------------|-------|
| Classical (300M MAU) | 50M | ~$450K | No LLM in hot path |
| +LLM selective (20% queries) | 50M (10M get LLM) | ~$520K | High-value queries only |
| +LLM all queries | 50M | ~$10.5M | Cost-prohibitive; never do this |

### Cost Optimization Priority Stack

| Priority | Optimization | Estimated Savings |
|----------|-------------|-------------------|
| 1 | Selective LLM routing (20% of traffic) | 5-10x vs full LLM coverage |
| 2 | Offline LLM features (amortize once per item) | 100x vs real-time per query |
| 3 | Model distillation for ranker | 2-3x inference cost |
| 4 | Result caching (common query-item pairs) | 1.3-1.5x |
| 5 | Batch pre-computation for returning users | 1.2x |

### Build vs Buy

| Component | Build | Buy Option | Recommendation |
|-----------|-------|------------|----------------|
| Vector DB | FAISS/pgvector | Pinecone, Weaviate | Self-host at >10M items |
| Ranking model | Custom DNN [9][15] | N/A | Always build — core IP |
| LLM reranking | vLLM + open-source | Claude/GPT API | API for quality; self-host at >1M queries/day |
| Feature store | Redis/DynamoDB | Feast, Tecton | Build if deeply integrated; buy otherwise |
| Experimentation | Build internal | N/A | Always build — marketplace experiments too specialized |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Online CTR (A/B) | Negative delta >0.5% for 24h | ML on-call: ranking regression |
| Online CVR | Any regression for 48h | P0: business metric regression |
| Calibration ECE | >0.03 (baseline 0.015) | Recalibrate immediately |
| Retrieval Recall@100 (golden set) | <85% (baseline 92%) | Retrieval team: embedding/index issue |
| Catalog coverage (7-day) | <40% (baseline 55%) | Diversity: filter bubble forming |
| LLM reranking lift (NDCG) | <2% (baseline 8%) | Remove LLM stage or investigate |
| Latency p99 | >200ms (SLA: 100ms) | Infra: model serving or candidate set size |

### Debugging Walkthrough

```
Symptom: CTR improves +3% but CVR drops -1.5%
├── Segment analysis: slice by item category, user segment, query intent
│   └── Finding: high-intent queries ("buy X") lost CVR; low-intent improved
├── Inspect ranking changes on high-intent queries
│   └── Finding: model ranks "engaging" (clickbait-y) items higher
├── Root cause: model trained with CTR objective only
└── Fix:
    ├── Short-term: roll back for high-intent queries only
    ├── Medium-term: multi-objective loss (CVR for high-intent, CTR for low)
    └── Long-term: constrained optimization [10] — CTR can't regress CVR
```

### Versioning & Rollback

| Component | How to Version | Rollback Strategy |
|-----------|---------------|-------------------|
| Retrieval embeddings | Index version + model ID | Alias swap to previous index (minutes) |
| Ranking model | Model version in config | Route to previous model (seconds) |
| LLM reranker | Prompt version + model ID | Config rollback (seconds) |
| FTRL online model [4] | Periodic snapshots | Revert to last snapshot; replay events |
| Feature pipeline | Pipeline version hash | Revert extraction; may need re-index |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Latency | Value | Action |
|--------|---------|-------|--------|
| Click-through | Immediate | Engagement (noisy — position-biased) | Train with IPW correction [5] |
| Purchase/conversion | Hours-days | True item value (strongest signal) | Primary ranking target |
| Dwell time | Immediate | Implicit quality signal | Secondary ranking feature |
| Returns/complaints | Days-weeks | Negative quality signal | Item quality adjustment |
| Explicit ratings | Immediate | Direct quality (sparse) | Highest per-signal value |
| Adoption rate (B2B) | Days | Recommendation utility | Product-level optimization |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Real-time | FTRL click model [4] | Calibration ECE < 0.02 |
| Daily | Feature pipeline refresh | Feature distribution check |
| Weekly | Calibration re-fit (isotonic regression) | ECE improvement on holdout |
| Monthly | Full ranking model retrain [9][15] | Offline NDCG + 1-week online A/B |
| Quarterly | Architecture changes, new stages | Full regression suite + 2-week A/B |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Multi-stage pipeline [1][11] | Can't score millions with one model | Catalog >10K items | Tiny catalogs where brute-force scoring works |
| Two-tower retrieval [1][3] | Fast ANN candidate generation at scale | Catalog >100K items | When fine-grained interaction needed |
| Cross-attention scoring [15] | Fine-grained query-item interaction | Precision ranking on top-200-500 | Full catalog scoring (too slow) |
| IPW position correction [5][6] | Debiased training from position-biased logs | Any system trained on click data | Systems with only explicit feedback |
| Hard negative mining [13] | Model learns fine-grained distinctions | After in-batch negatives plateau | Early training (destabilizes learning) |
| FTRL online learning [4] | Real-time adaptation at extreme sparsity | Auction/bidding with billions of features | When deep interactions matter more than sparsity |
| LLM offline features [14] | Cold-start item bootstrapping | New items without behavioral history | Items with rich behavioral data |
| Multi-objective constrained [10] | Conflicting business objectives | Production with diversity/fairness requirements | Single-objective exploratory systems |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|----------------|----------------------|
| "We use a two-tower model for retrieval" | "Two-tower for retrieval, cross-attention for scoring. Dot product is sufficient for recall at scale but loses fine-grained intent matching [1]. Cross-attention on top-200 captures token-level alignment." |
| "We train on click data" | "We train with IPW position correction [5] and recalibrate weekly. Raw clicks are position-biased — without correction the model learns position, not relevance." |
| "We added an LLM to improve recommendations" | "LLM reranking selectively on high-value queries and cold-start [14]. For 80% of queries, classical ML outperforms at 1000x lower cost. The question is where marginal value exceeds marginal cost." |
| "We optimize for CTR" | "We maximize CVR subject to CTR and diversity constraints [10]. CTR alone favors clickbait. Constrained optimization with explicit business guardrails prevents short-term metric gaming." |
| "We use random negatives" | "70% in-batch with log-Q correction [2] + 30% hard negatives [13]. Random negatives teach trivial distinctions — hard negatives force the model to learn what matters at ranking time." |
| "We improved NDCG by 5%" | "5% NDCG translated to 2% CVR lift in double-randomized A/B — standard A/B understated impact due to marketplace interference (SUTVA violation)." |
| "We A/B test our changes" | "Standard A/B fails for marketplace interventions — treatment changes auction dynamics for control [10]. We use double-randomized experimentation or interleaving for trustworthy measurement." |

## References

### Foundational Papers

- [1] Covington et al. (2016) — *Deep Neural Networks for YouTube Recommendations* — RecSys 2016 — Established the two-tower retrieval + DNN scoring multi-stage architecture used by all major platforms.
- [3] Huang et al. (2013) — *Learning Deep Structured Semantic Models for Web Search* — CIKM 2013 — Introduced DSSM; deep semantic matching via separate query/document towers with cosine similarity.
- [4] McMahan et al. (2013) — *Ad Click Prediction: a View from the Trenches* — KDD 2013 — Defined FTRL-Proximal with per-coordinate learning rates; still the foundation of real-time ad CTR prediction.
- [7] Rendle (2010) — *Factorization Machines* — ICDM 2010 — Introduced FM for sparse feature interaction modeling; foundation for all FM-based recommendation models.
- [8] He et al. (2017) — *Neural Collaborative Filtering* — WWW 2017 — Replaced matrix factorization dot product with neural architecture; proved non-linear user-item interactions improve recommendation.
- [9] Guo et al. (2017) — *DeepFM: A Factorization-Machine based Neural Network for CTR Prediction* — IJCAI 2017 — Combined FM and DNN with shared embeddings; eliminated manual feature engineering for CTR prediction.
- [11] Naumov et al. (2019) — *Deep Learning Recommendation Model for Personalization and Recommendation Systems* — arXiv:1906.00091 — Meta's DLRM; defined the embedding table + interaction + MLP architecture now standard in industry.

### Retrieval & Training

- [2] Yi et al. (2019) — *Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations* — RecSys 2019 — Proved in-batch negative bias and derived log-Q correction for unbiased two-tower training.
- [13] Yang et al. (2020) — *Mixed Negative Sampling for Learning Two-tower Neural Networks in Recommendations* — WWW 2020 — Demonstrated mixed negative strategies (in-batch + hard) outperform single-strategy approaches.
- [15] Wang et al. (2021) — *DCN V2: Improved Deep & Cross Network and Practical Lessons for Web-scale Learning to Rank* — WWW 2021 — Advanced cross-network architecture with mixture-of-experts; state-of-the-art on large-scale CTR benchmarks.

### Position Bias & Evaluation

- [5] Joachims et al. (2017) — *Unbiased Learning-to-Rank with Biased Feedback* — SIGIR 2017 — Formalized IPW for position bias correction; proved propensity-weighted training yields unbiased ranking.
- [6] Wang et al. (2018) — *Position Bias Estimation for Unbiased Learning to Rank in Personal Search* — WSDM 2018 — Developed EM-based propensity estimation without randomization; practical for large-scale search systems.

### Multi-Objective & Production

- [10] Zhao et al. (2019) — *Recommending What Video to Watch Next: A Multitask Ranking System* — RecSys 2019 — YouTube's multi-objective ranking with shared-bottom architecture; production multi-task learning at scale.

### LLM-Enhanced Recommendation

- [12] Zhu et al. (2022) — *Recommendation as Language Processing (RLMRec)* — arXiv:2206.02631 — Proposed framing user-item interactions as language sequences; demonstrated LLM reasoning for recommendation.
- [14] Lin et al. (2023) — *How Can Recommender Systems Benefit from Large Language Models: A Survey* — arXiv:2306.05817 — Comprehensive survey of LLM integration points (feature generation, scoring, explanation) in recommendation pipelines.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; restructured to v2 template with 6 diverse DE probes (math/systems/data/evaluation/production/architecture), 15 inline citations, cost model, and observability |
