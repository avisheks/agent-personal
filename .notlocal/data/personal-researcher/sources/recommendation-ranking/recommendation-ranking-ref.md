---
title: "Recommendation Ranking Ref"
source: "data/researcher/reports/recommendation-ranking-ref.md"
ingestedAt: "2026-05-17T14:56:52Z"
---
# Recommendation / Ranking with LLMs — Interview Prep

> **Navigation**: [[#Design Flow Framework]] | [[#Full System Design Walkthrough (Principal/Director Level, ~4 min)]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]


## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Ranking vs recommendation vs explanation? Personalization signals? Catalog size? Latency? Objectives? | Is the LLM the ranker, the feature generator, or the explainer? |
| 2. Identify constraints | Scale (millions of items), latency (<100ms for ranking), sparse feedback, cold-start, conflicting objectives | LLM-per-item is too expensive. Where does the LLM add value without blowing up cost? |
| 3. Propose baseline | Classic multi-stage: embedding retrieval → feature-based ranker. LLM only for explanation or offline feature generation | Prove value with proven architecture before adding LLM complexity |
| 4. Identify gaps | LLM-only doesn't scale, poorly calibrated on large sets, explanations may not reflect ranking logic, cold-start, adoption ceiling | The constraint is often adoption, not recall |
| 5. Introduce improvements | Multi-stage with LLM reranking on top-K, LLM as feature generator, semantic retrieval for sourcing, explanation post-ranking, business-rule constraints | Each LLM insertion point has different cost-value tradeoffs |
| 6. Add evaluation + guardrails | NDCG, recall, CTR, CVR, coverage, diversity, slice metrics, calibration, fairness, explanation consistency, online experimentation | Offline relevance often misses business behavior — A/B test is final arbiter |
| 7. Discuss scaling tradeoffs | LLM reranking quality vs latency/cost, retrieval breadth vs efficiency, explanation safety, multi-objective balancing | The evolution from traditional ML → deep learning → LLM-enhanced is about knowing where each layer adds value |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## Full System Design Walkthrough (Principal/Director Level, ~4 min)

### Opening Frame (10s)

"The question is not 'should we use LLMs for recommendations?' — it's 'WHERE in the pipeline does an LLM add value that justifies its cost?' From 12+ years building recommendation systems at Yahoo Labs and Amazon Ads — from FTRL click prediction to deep learning rankers to LLM-enhanced targeting — I've learned that the biggest constraint is never model quality. It's adoption. You can build the best ranker in the world, but if users only adopt the top 30 of 200 recommendations, your recall improvements are invisible. The system must optimize for human behavior, not just relevance scores."
### 1. Clarify Requirements

Before designing anything, I'd ask:

- **Task type**: Is this ranking (reorder a known candidate set), recommendation (surface items the user hasn't seen), or explanation (tell the user WHY these items are recommended)? Each has different LLM insertion points.
- **Personalization signals**: What do we know about the user? Behavioral history (clicks, purchases, dwell time)? Explicit preferences? Session context? Rich signals → classical collaborative filtering works well. Sparse signals → embeddings/LLMs help more.
- **Catalog size**: 1K items (LLM can score all), 100K (need retrieval + reranking), 100M (need multi-stage with aggressive pruning)? This determines where LLM computation is feasible.
- **Latency budget**: <50ms (real-time feed), <200ms (search results), <2s (exploration page)? LLM-per-item is ~50-100ms — only feasible on small candidate sets.
- **Objectives**: CTR optimization favors engagement. CVR optimization favors relevance. Revenue optimization favors high-value items. Diversity optimization fights filter bubbles. These conflict — which ones take priority?
- **Cold-start profile**: How many new items/users per day? Cold-start is where LLMs add the most value (content understanding without behavioral data).

**Principal signal**: Frame in terms of business objectives, not technical capabilities. "The ranking objective depends on whether we're optimizing for advertiser ROI, platform revenue, or user experience — these compete, and the Director's job is choosing the tradeoff."

### 2. Identify Constraints

- **Scale vs LLM cost**: A catalog of 10M items at $0.01/item/query = $100K per query. Obviously infeasible. LLMs can only touch a small candidate set (top 20-100 after retrieval).
- **Latency**: Real-time ranking at <100ms means the LLM can only rerank top-K after fast retrieval. Any LLM in the hot path must be small or cached.
- **Sparse feedback**: Most items have few interactions. Classical CF fails on the long tail. LLMs help by understanding item content (descriptions, attributes) without behavioral data.
- **Position bias**: Users click items at the top regardless of relevance. Training on click data without position correction = self-reinforcing bias. The ranker learns "position 1 is good" not "this item is good."
- **Multi-objective tension**: Relevance, diversity, fairness, freshness, and revenue all compete. A system optimizing purely for CTR becomes a filter bubble. A system optimizing for diversity sacrifices relevance.
- **Explanation fidelity**: If you generate explanations post-hoc, they may not reflect the actual ranking logic. "We recommended this because..." must be truthful, or you erode trust.

> [!experience] At Amazon Ads, the core constraint was lower-funnel performance — we couldn't regress CVR or RoAS because advertisers measure these directly. A recommendation that maximizes clicks but reduces conversions wastes advertiser budget. Every ranking improvement had to pass both online relevance metrics AND advertiser business metrics, measured with our double-randomized experimentation framework.

**Risk framing**: (P0) Business: wrong recommendations waste advertiser budget, erode platform trust | (P1) Technical: position bias in training data creates self-reinforcing loops | (P2) Org: ML team optimizes for model metrics while product team cares about business metrics — misalignment

### 3. Propose Baseline (Classic Multi-Stage)

**Architecture:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│  MULTI-STAGE RECOMMENDATION PIPELINE (Baseline)                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ Candidate     │───▶│ Scoring /    │───▶│ Business     │──▶ Top-K     │
│  │ Generation    │    │ Ranking      │    │ Rules        │   to User    │
│  │ [<10ms]       │    │ [10-50ms]    │    │ [<5ms]       │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│       │                    │                    │                         │
│  Collaborative       Feature-based         Diversity,                    │
│  filtering,          GBDT/DNN ranker       freshness,                    │
│  embedding ANN,      (CTR/CVR prediction)  dedup, policy                 │
│  popularity                                                              │
│                                                                           │
│  ┌──────────────────────────────────────────────────────┐               │
│  │  Offline: LLM for feature generation                  │               │
│  │  - Item embeddings from descriptions                  │               │
│  │  - Category/attribute extraction                      │               │
│  │  - Explanation templates (pre-computed)                │               │
│  └──────────────────────────────────────────────────────┘               │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Candidate generation** (<10ms): Collaborative filtering (user-item matrix), embedding ANN (two-tower retrieval), popularity-based, and rule-based sourcing. Retrieve 500-1000 candidates from a catalog of millions.
- **Scoring/ranking** (10-50ms): Feature-based ranker — GBDT (XGBoost/LightGBM) or DNN (deep & wide, DeepFM). Features: user history, item attributes, context (time, device, session), interaction features (CTR/CVR predictions).
- **Business rules** (<5ms): Diversity enforcement (max N items per category), freshness boost, policy filtering (suppress violating items), deduplication.
- **LLM role (offline only)**: Generate item embeddings from descriptions, extract structured attributes from unstructured item data, pre-compute explanation templates. NOT in the real-time path.

**Design choice**: LLM offline for features, NOT in real-time ranking path
- **Pros**: Zero latency impact on serving; LLM-generated features improve cold-start items; classical ranker stays fast and well-calibrated
- **Cons**: Can't use LLM for per-query reasoning; explanations are templates (not personalized); misses query-item semantic matching
- **Why chosen**: At 300M+ MAU with <100ms latency, any LLM in the hot path is infeasible for all candidates. LLM adds value in feature generation (offline, amortized) rather than per-query scoring.
- **Alternative considered**: LLM-only ranking — powerful but 1000x too slow and expensive for production scale.

> [!experience] At Amazon Ads, our baseline was exactly this multi-stage pipeline: sourcing via embedding retrieval + collaborative signals → ranking via deep learning models (cross-attention architectures achieving +900 bps relevance improvement) → business rules for diversity and policy. LLMs entered only for offline feature generation — keyword embedding, semantic attribute extraction. This architecture served 300M+ MAU with <100ms p99 latency.

### 4. Identify Gaps (Where Baseline Fails)

| Failure Mode | Symptom | Root Cause |
|---|---|---|
| **Cold-start items** | New items get no impressions | No behavioral data for CF; ranker features are all zero |
| **Long-tail irrelevance** | Niche items poorly ranked | Sparse feedback → noisy features → ranker under-serves long tail |
| **Semantic mismatch** | User searches "comfortable work shoes" → gets "formal leather shoes" | Feature-based ranker lacks query-item semantic understanding beyond keyword matching |
| **Stale recommendations** | Same items recommended repeatedly | Ranker optimizes for historical CTR → exploitation bias |
| **Filter bubble** | Users see decreasing diversity over time | Positive feedback loop: click → reinforce → more of the same |
| **Explanation disconnect** | "Recommended because you liked X" when the actual reason was position bias | Pre-computed explanations don't reflect real ranking logic |
| **Adoption ceiling** | Users only engage with top 5-10 of 30 recommendations | Cognitive load + trust deficit → similar to keyword adoption problem |
| **Multi-objective failure** | Optimizing CTR reduces conversion; optimizing diversity reduces engagement | Single-objective ranker can't balance competing goals |

> [!experience] At Amazon Ads, we discovered that advertisers adopted only the top 30-50 of 200 recommended keywords. The constraint wasn't retrieval quality — it was adoption. More recommendations didn't help if advertisers couldn't process them. This reframed the problem from "better ranking" to "better presentation and trust-building" — leading to the intent-level reframing that delivered +2700 bps coverage and +1300 bps adoption.

### 5. Introduce Improvements

#### 5a. LLM-Enhanced Retrieval (Semantic Sourcing)

Replace or augment traditional retrieval with LLM-based semantic understanding:

- **Two-tower with LLM embeddings**: Use LLM-generated embeddings (from item descriptions) as the item tower in a two-tower retrieval model. Improves semantic matching, especially for cold-start items.
- **Query understanding via LLM**: Expand/rewrite user query before retrieval. "Comfortable work shoes" → expanded intent: [comfort, office-appropriate, all-day wear, arch support].
- **Hybrid retrieval**: Combine collaborative signals (who bought what) + semantic signals (embedding similarity) + lexical signals (BM25 for exact matches).

> [!experience] At Amazon Ads, we invented a targeting expansion algorithm using semantic retrieval that improved recommendation coverage by +2200 bps while maintaining relevance thresholds. The key: use semantic retrieval to EXPAND the candidate pool beyond what collaborative filtering finds, then let the ranker filter for quality. Semantic retrieval was additive to CF, not a replacement.

**Risk framing**: (P0) Business: expanded retrieval without quality filtering → irrelevant recommendations → wasted advertiser budget | (P1) Technical: embedding quality varies across item categories; need per-category evaluation | (P2) Org: search/retrieval team must coordinate with ranking team on embedding alignment

#### 5b. LLM Reranking on Top-K

After initial retrieval + scoring produces top-50, apply LLM reranking on the final candidate set:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Candidate Gen│───▶│ ML Ranker    │───▶│ LLM Reranker │───▶│ Business     │──▶ User
│ (500-1000)   │    │ (→ top-50)   │    │ (→ top-10)   │    │ Rules        │
│ [<10ms]      │    │ [10-50ms]    │    │ [100-300ms]  │    │ [<5ms]       │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

**What LLM reranking adds**: The LLM can consider query-item semantic fit that feature-based rankers miss. It reads the item description, understands the query intent, and makes a judgment: "Given the user is searching for 'comfortable work shoes for standing all day', item A (running shoe) is less relevant than item B (supportive loafer) even though A has higher historical CTR."

**When it's worth the cost**: (a) High-value queries (user signals strong purchase intent). (b) Complex queries (multi-attribute, comparison, natural language). (c) Cold-start items (LLM can assess relevance from content when behavioral features are zero).

**Design choice**: LLM reranking on top-50, not top-500 or full catalog
- **Pros**: Captures semantic fit the ML ranker misses; manageable latency (50 items × 1 LLM call with list-wise scoring); highest ROI point for LLM insertion
- **Cons**: +100-300ms latency; LLM may not be calibrated for CTR/CVR prediction (good at relevance, bad at click prediction)
- **Why chosen**: The ML ranker is good at predicting clicks from behavioral features. The LLM is good at understanding semantic relevance. Combining them gets both — behavioral + semantic. Applying to top-50 (not more) keeps latency bounded.
- **Alternative considered**: LLM scoring all 500 retrieved candidates — 10x latency increase for diminishing returns (the ML ranker already filtered the worst candidates).

#### 5c. LLM as Feature Generator (Offline)

Use LLMs to generate rich features from unstructured item data:

- **Attribute extraction**: "This is a mid-century modern walnut dining table, seats 6" → structured attributes: {style: "mid-century modern", material: "walnut", type: "dining table", capacity: 6}
- **Category inference**: Assign fine-grained categories from descriptions when catalog metadata is incomplete.
- **Embedding generation**: Generate content embeddings from item titles + descriptions for semantic retrieval.
- **Query-item relevance features**: Offline batch job: for each (query_template, item) pair, LLM scores relevance 1-5. Use as a feature in the ranking model.

**Why offline**: These features are computed once per item (or per item update) and cached. Cost is amortized across all queries that touch the item. A $0.01 LLM call per item for 10M items = $100K one-time, not per-query.

#### 5d. Explanation Generation (Post-Ranking)

Generate personalized explanations AFTER ranking, not during:

```
Ranking pipeline produces: [item_A (score: 0.95), item_B (score: 0.87), ...]
                                            ↓
Explanation generator: "Recommended because it matches your interest in 
                        mid-century furniture and has 4.8★ reviews from 
                        buyers who also liked [item you purchased]."
```

**Critical constraint**: Explanations must be FAITHFUL to the actual ranking signals. If the item was ranked high because of collaborative filtering (similar users bought it), the explanation should reference that — not fabricate a relevance reason.

> [!experience] At Amazon Ads, we found that showing predicted impact alongside recommendations dramatically increased adoption. "Add this keyword cluster — predicted +12% reach within your RoAS guardrail" was far more effective than just listing keywords. The explanation was functional (actionable information), not decorative (post-hoc rationalization).

#### 5e. Zero-Shot/Few-Shot for Cold-Start and New Markets

For items with no behavioral data or new markets with no history:

- **Zero-shot item understanding**: LLM reads item description → generates embedding → item participates in semantic retrieval immediately.
- **Few-shot cross-market transfer**: Use behavioral patterns from data-rich markets to bootstrap recommendations in new markets.

> [!experience] At Amazon Ads, we scaled ML workflows to 19+ locales using zero-shot and few-shot learning, reducing time-to-market for new markets by 75%. The insight: zero-shot worked surprisingly well for marketplaces with similar languages (UK, DE, FR) because advertisers cross-sell across locales. For character-different marketplaces (JP, KSA), few-shot was required. Start with the simplest approach; complexity only where data proves it's needed.

#### 5f. Multi-Objective Optimization

Real recommendations must balance competing objectives:

| Objective | Metric | Tension With |
|---|---|---|
| Relevance | NDCG, CTR | Diversity (relevant = similar to past behavior) |
| Conversion | CVR, revenue | Engagement (high-CVR items may be boring/expected) |
| Diversity | ILD, category coverage | Relevance (diverse = less similar to known preferences) |
| Freshness | Avg item age in recommendations | Relevance (new items have uncertain quality) |
| Fairness | Exposure parity across item segments | Revenue (fair ≠ revenue-maximizing) |

**Approaches**:
- **Scalarization**: Weighted sum of objectives. Simple but choosing weights is hard and context-dependent.
- **Constrained optimization**: Optimize primary objective (CTR) subject to constraints (diversity ≥ threshold, fairness ≥ threshold). More principled.
- **Pareto-optimal reranking**: Generate multiple Pareto-optimal orderings, select based on context.
- **MMR (Maximal Marginal Relevance)**: At each position, select the item that maximizes λ × relevance - (1-λ) × max_similarity_to_already_selected. Naturally balances relevance and diversity.

### 6. Evaluation + Guardrails

#### Offline Evaluation

| Metric | What It Measures | Caveat |
|---|---|---|
| NDCG@K | Ranking quality (are good items ranked higher?) | Assumes relevance labels are correct — they may not be |
| Recall@K | Coverage (are relevant items in top-K?) | Doesn't distinguish between positions within K |
| CTR prediction AUC | Click prediction accuracy | Position-biased if not corrected |
| CVR prediction AUC | Conversion prediction accuracy | Sparse (most items have few conversions) |
| Coverage | Fraction of catalog that gets recommended | High coverage ≠ good recommendations |
| ILD (Intra-List Diversity) | Diversity of recommendations | High diversity ≠ user satisfaction |

#### Online Evaluation (the only metrics that matter)

| Metric | What It Measures | Why It's Authoritative |
|---|---|---|
| A/B tested CTR | Real user engagement | Accounts for position, context, everything |
| A/B tested CVR/revenue | Real business impact | The only metric advertisers/business care about |
| Long-term retention | Sustainable value (not just short-term clicks) | Catches filter bubble effects that CTR misses |
| User-level diversity | Are users seeing varied content over time? | Prevents engagement-maximizing echo chambers |

> [!experience] At Amazon Ads, we designed the first double-randomized experimentation framework for marketplace-level measurement. Standard A/B tests miss marketplace effects — if we recommend more keywords to treatment advertisers, they change auction dynamics for everyone. Double randomization isolates the causal effect by randomizing at both the advertiser and marketplace level. This became the org-wide experimentation standard.

#### Guardrails

- **Position bias correction**: Use IPW (Inverse Propensity Weighting) or position-aware models to deconfound click data from position effects.
- **Calibration**: Predicted CTR/CVR should match observed rates. Miscalibrated models over/under-bid in auctions.
- **Fairness auditing**: Check recommendation exposure across item categories, seller segments, and user demographics. Uneven exposure may indicate bias.
- **Explanation consistency**: LLM explanations must be grounded in actual ranking features. Audit by checking: "If we remove the factor cited in the explanation, does the item's rank actually change?"

### 7. Scaling Tradeoffs

#### Where LLM Adds Value vs Where It Doesn't

| Pipeline Stage | LLM Value | Cost | Verdict |
|---|---|---|---|
| Candidate generation (from millions) | Low (can't score millions) | Prohibitive | Don't use LLM here. Use embeddings + ANN. |
| Feature generation (offline) | High (content understanding) | Low (amortized) | **Best ROI for LLM** |
| Reranking (top-50) | Medium-High (semantic fit) | Medium (50 items per query) | Use selectively (high-value queries) |
| Explanation (post-ranking) | Medium (user trust) | Low-Medium | Use for high-engagement surfaces |
| Full ranking (all items) | Theoretically high | Prohibitive | Never. This is the wrong architecture. |

> [!experience] At Amazon Ads, the evolution over 12+ years was: FTRL online learning (Yahoo Labs, 100% query-ad coverage) → deep learning representation learning (cross-attention, +900 bps) → LLM-enhanced semantic retrieval (+2200 bps coverage) → LLM feature generation. Each era didn't replace the previous one — it added a layer. The FTRL-era features still run alongside LLM-generated features. The lesson: LLMs augment recommendation systems; they don't replace the classical pipeline.

#### Traditional ML vs LLM Ranking

| Factor | Traditional ML (GBDT/DNN) | LLM Reranking |
|---|---|---|
| Latency | 1-10ms per item | 50-300ms for list of 50 |
| Calibration | Well-calibrated (trained on clicks/conversions) | Poorly calibrated (semantic judgment, not probability) |
| Feature engineering | Manual, requires domain expertise | Automatic (reads descriptions, understands context) |
| Cold-start | Fails (no behavioral features) | Excels (content understanding) |
| Scale | Millions of items per second | Dozens of items per query |
| Explainability | Feature importance (SHAP) | Natural language (but may not be faithful) |

**The right answer**: Both. Traditional ML for scale + behavioral prediction. LLM for semantic understanding + cold-start + explanations. Multi-stage architecture where each does what it's best at.
[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

## Interview Q&A Bank

### Q1: Where does the LLM fit in a recommendation pipeline? Where does it NOT fit?

**Principal Answer**: The LLM fits where content understanding matters and behavioral data is insufficient. It does NOT fit where speed, calibration, and scale are primary requirements.

**LLM insertion points (ranked by ROI)**:
1. **Offline feature generation** (highest ROI): Extract structured attributes, generate embeddings, compute semantic features. Amortized cost, zero runtime latency impact.
2. **Reranking top-K** (high ROI, selective use): Semantic reranking of top-20-50 after the fast ranker. Add 100-300ms but capture semantic fit the ML ranker misses.
3. **Explanation generation** (medium ROI): Post-ranking explanations that tell users WHY. Builds trust, increases adoption.
4. **Query understanding** (medium ROI): Expand/rewrite queries before retrieval. Helps on ambiguous or natural-language queries.
5. **Cold-start item bootstrapping** (high ROI for new items): LLM reads item description → generates embedding → immediate participation in retrieval.

**Where LLM does NOT fit**:
- Scoring all candidates in a large catalog (100K+) — too slow, too expensive
- Calibrated CTR/CVR prediction — LLMs don't produce well-calibrated probabilities
- Real-time ranking in the hot path at <50ms — LLM inference is too slow
- Simple popularity-based recommendations — no content understanding needed

> [!experience] At Amazon Ads, we used LLMs for offline keyword generation (reducing cycle time from 8 weeks to <2 weeks) and semantic retrieval (expanding coverage by +2200 bps). The real-time ranking path stayed pure deep learning (cross-attention models, +900 bps) because it needed to serve 300M+ MAU at <100ms. LLMs augmented the pipeline where they added unique value; they didn't replace the fast path.

**Hard FUQ**: A PM wants to replace the entire ranking stack with an LLM ("just give it all the items and let it rank them"). How do you push back?

**Answer**: Math. A catalog of 100K items × $0.001/item per LLM call = $100 per query. At 10M queries/day = $1B/year. Even at 1000 items it's $10/query. The classical ranker handles 100K items in 10ms for ~$0.0001. Push back with: "LLMs are 100,000x more expensive per scoring operation. We should use them where they provide 100,000x more insight — which is semantic understanding on a small candidate set, not brute-force scoring of a large catalog."

---

### Q2: Multi-stage recommendation architecture — walk me through it.

**Principal Answer**: Multi-stage is the universal production architecture because no single model can efficiently handle both recall (find relevant items from millions) and precision (rank the best 10 from hundreds).

**Stage 1 — Candidate generation** (recall-focused, <10ms):
- Sources: collaborative filtering, embedding ANN (two-tower), trending/popular, rule-based (category match)
- Goal: 500-1000 candidates from a catalog of millions
- Quality bar: high recall (don't miss relevant items), acceptable noise (it's OK to include some irrelevant items)

**Stage 2 — Scoring/ranking** (precision-focused, 10-50ms):
- Model: GBDT or DNN (deep & wide, DeepFM, DCN) with hundreds of features
- Features: user behavioral (clicks, purchases, dwell), item features (attributes, popularity, freshness), context (time, device, session), cross features (user×item interaction history)
- Goal: Predict P(click), P(conversion), or a weighted combination → score each candidate
- Quality bar: well-calibrated probabilities, strong ranking correlation with real engagement

**Stage 3 — LLM reranking** (semantic, 100-300ms, OPTIONAL):
- Apply only on top-50 from Stage 2
- LLM considers: query-item semantic fit, item description quality, coherence of the recommendation set
- Goal: Capture semantic relevance that behavioral features miss

**Stage 4 — Business rules** (policy/guardrails, <5ms):
- Diversity enforcement, freshness boost, policy filtering, deduplication
- Goal: Ensure the final list serves business objectives beyond pure relevance

> [!experience] At Amazon Ads, our pipeline was: sourcing (embedding retrieval + collaborative signals) → semantic matching (cross-attention models, +900 bps) → personalized ranking (deep learning, +400 bps via representation learning) → business rules (diversity, policy). Each stage narrowed the funnel: millions → 1000 → 200 → final top-K. Total latency: <100ms at p99 for 300M+ MAU.

**Hard FUQ**: Your Stage 2 ranker has been optimized for years. Where's the diminishing returns, and when do you invest in Stage 3 (LLM reranking) instead?

**Answer**: Diminishing returns in Stage 2 show up when: (a) adding more features yields <0.1% AUC improvement, (b) A/B tests show ranking changes but no business metric movement, (c) failure analysis reveals the errors are semantic mismatches, not feature engineering gaps. At that point, the ranker has extracted all value from behavioral signals — the remaining errors are where behavioral data is absent (cold-start, novel queries, long-tail items). That's where LLM reranking adds value: semantic understanding that no amount of behavioral features can replicate.

---

### Q3: LLM-based semantic retrieval vs traditional collaborative filtering

**Principal Answer**: These are complementary, not competing. They solve different problems:

| Dimension | Collaborative Filtering | Semantic Retrieval (LLM-based) |
|---|---|---|
| Signal source | User behavior (clicks, purchases) | Content (descriptions, attributes) |
| Cold-start | Fails (no behavioral data) | Works (reads description) |
| Serendipity | Low (recommends what similar users liked) | Higher (can find semantically related but behaviorally disconnected items) |
| Popularity bias | High (reinforces popular items) | Lower (content quality independent of popularity) |
| Scale | Mature, fast (matrix factorization, ANN) | Newer, computationally heavier |
| Accuracy on established items | Very high (rich behavioral signal) | Lower (content doesn't capture taste) |

**The hybrid architecture**: Use CF for established items (rich behavioral data), semantic retrieval for cold-start and long-tail, and blend both for the middle.

> [!experience] At Amazon Ads, our targeting expansion algorithm used semantic retrieval to find query-keyword matches that collaborative signals missed — organic shopper queries that advertisers hadn't targeted yet. This expanded recommendation coverage by +2200 bps while maintaining relevance, because semantic retrieval found high-quality matches that simply didn't have behavioral history yet. CF alone would never surface them.

**Hard FUQ**: Semantic retrieval surfaces items that are semantically relevant but users don't click on. How do you address this?

**Answer**: This is the "relevant but not interesting" problem. Semantic similarity ≠ user preference. A user searching for "running shoes" might be semantically matched to "trail running shoes" but actually wants "road running shoes." Fix: (a) Fine-tune embeddings on click/purchase pairs, not just semantic similarity. This makes embeddings reflect user preference, not just content similarity. (b) Use semantic retrieval as a CANDIDATE SOURCE, not a ranker. The behavioral ranker (Stage 2) re-scores semantically retrieved candidates using behavioral signals. (c) Track "semantic retrieval → adoption" rate separately from "CF retrieval → adoption." If semantic candidates consistently under-adopt, the embeddings need domain-specific fine-tuning.

---

### Q4: Cold-start — how do LLMs help with new items/users?

**Principal Answer**: Cold-start is where LLMs add the most value relative to traditional ML, because they can reason about CONTENT when BEHAVIORAL data doesn't exist yet.

**Item cold-start** (new item, no clicks/purchases):
- LLM reads item description → generates content embedding → item immediately participates in semantic retrieval
- LLM extracts structured attributes → features for the ranking model (category, price point, quality signals)
- LLM generates "similar item" list from catalog descriptions → bootstrap CF signals from similar items

**User cold-start** (new user, no history):
- LLM processes initial signals (search query, browse category, device, time of day) → infer intent → retrieve relevant items without behavioral history
- Contextual bandits: recommend diverse items initially, learn user preferences from feedback, personalize quickly
- Cross-platform transfer: if user has signals from another surface (email, ads, social), use LLM to map across domains

> [!experience] At Amazon Ads, cold-start was critical for new marketplace expansion. When launching ads in a new locale, there's minimal advertiser behavioral data. We used zero-shot learning to bootstrap recommendations: US-trained models transferred to new locales using cross-marketplace advertiser behavior (advertisers who sell in both US and DE). Zero-shot worked for 80%+ of locales; few-shot closed the gap for the rest.

**Hard FUQ**: Your LLM generates an embedding for a new item that's semantically similar to a popular item, but they're actually in different quality tiers (the new item is much worse). How do you prevent recommending low-quality items based on semantic similarity alone?

**Answer**: Semantic similarity is necessary but not sufficient. Add quality signals: (a) Seller reputation (new seller → lower initial trust score). (b) Listing quality signals (photo count, description completeness, reviews if available). (c) Category-level priors (new items in high-return categories get lower initial scores). (d) Exploration with throttling: expose the new item to a small slice of users first. If engagement signals are positive, increase exposure. If negative, suppress. Don't give a new item the same exposure as a proven item just because their embeddings are close.

---

### Q5: The adoption problem — why generating better recommendations doesn't always help

**Principal Answer**: This is the EARNED SECRET of recommendation systems, and most teams miss it: the constraint is not model quality — it's adoption. You can improve NDCG by 10% and see zero business impact because users only look at the top few recommendations anyway.

> [!experience] At Amazon Ads, we generated up to 200 keyword recommendations per advertiser. Adoption data showed advertisers adopted only the top 30-50. The remaining 150 were ignored — not because they were bad, but because advertisers have limited attention and trust. Improving the quality of recommendations 51-200 was invisible to the business.

**Why this happens**:
1. **Cognitive overload**: 200 recommendations is a chore, not a gift. Users satisfice (pick "good enough" from the top) rather than optimize (evaluate all 200).
2. **Trust deficit**: Users don't trust AI recommendations enough to adopt deep into the list.
3. **Position effect**: Items at the top get disproportionate attention regardless of relevance.
4. **Lack of context**: A recommendation without explanation gives the user no basis for decision-making.

**What actually moves adoption**:
1. **Reduce volume, increase signal**: Show 30 high-confidence recommendations, not 200. Better to have 80% adoption of 30 than 15% of 200.
2. **Intent-level grouping**: Present recommendations as clusters (e.g., "Performance Running keywords" vs individual keywords). Users reason about intents, not individual items.
3. **Show expected impact**: "Adding this keyword cluster is predicted to increase reach by 12%" — quantified impact drives action.
4. **Progressive trust**: Start with conservative, obviously-good recommendations. Expand ambition as trust is established.

**Principal signal**: This is a PRODUCT problem, not a MODEL problem. The distinction between a Staff and a Director is recognizing that the bottleneck is human behavior, not model capability.

**Hard FUQ**: How do you measure whether improving the ranker is worth the investment, given the adoption ceiling?

**Answer**: Measure the marginal value curve: for each rank position K, what's the adoption probability and the business value of adoption? If adoption is 40% at K=1, 20% at K=5, 5% at K=10, and <1% at K>20, then ranking improvements that change positions 20+ are worthless. Focus on the top of the funnel: changes that move items between positions 1-10 have the highest business impact. A simple A/B test that measures business metric impact (not just ranking metric improvement) will reveal whether the ranker improvement actually reached the user.

---

### Q6: How do you measure recommendation system impact? (Experimentation)

**Principal Answer**: Measuring recommendation impact in a marketplace is fundamentally harder than measuring a UI change, because recommendations change the marketplace dynamics themselves.

**Why standard A/B testing fails for recommendations**:
- Treatment users who receive better recommendations bid on more keywords → changes auction dynamics for EVERYONE
- Control users' performance degrades not because of their own treatment, but because the marketplace changed
- Result: treatment effect is understated (SUTVA violation — Stable Unit Treatment Value Assumption)

**Double-randomized experimentation**:
- Layer 1: Randomize users/advertisers into treatment/control
- Layer 2: Randomize marketplace contexts (traffic slices, query segments) into isolated pools
- Treatment and control users compete in separate marketplace pools → interference is bounded

> [!experience] At Amazon Ads, we co-designed the first double-randomized experimentation framework to accurately measure marketplace-level impact. This resolved attribution bias that blocked prior launches and set a new org-wide experimentation standard. The framework was critical because standard A/B tests systematically understated the impact of recommendation improvements — leading leadership to under-invest in ML improvements that were actually very valuable.

**Offline vs online evaluation**:
| Method | What It Measures | Limitation |
|---|---|---|
| Offline (NDCG, Recall) | Ranking quality on held-out data | Doesn't account for position bias, marketplace effects, user behavior |
| Interleaving (A vs B in same list) | Pairwise preference | Can't measure absolute impact on business metrics |
| A/B test (standard) | Treatment vs control | SUTVA violation in marketplaces |
| Double-randomized | Causal marketplace impact | Requires large traffic, complex infrastructure |

**Hard FUQ**: You don't have enough traffic for double-randomized experimentation. What do you do?

**Answer**: Three alternatives: (1) Interleaving — show recommendations from both models in the same list, measure click preference. Requires 10x less traffic than A/B. (2) Synthetic control — compare against a predicted counterfactual built from pre-treatment time series (no need to split traffic at all). (3) Geo-based experiments — treat different geographic markets as independent experiments. Market A gets new model, Market B is control. Lower risk of marketplace interference because markets are naturally isolated.
### Q7: Balancing multiple objectives (relevance, diversity, fairness, business rules)

**Principal Answer**: Real recommendation systems serve multiple masters. The Director's job is deciding which objectives take priority WHEN — because they always conflict.

**The conflict matrix**:
- Relevance ↔ Diversity: Maximizing relevance means showing items most similar to past behavior. Maximizing diversity means varying the slate. These are mathematically opposed.
- Engagement ↔ Conversion: High-CTR items are often clickbait-y or controversial. High-CVR items are often expected and boring. Optimizing one degrades the other.
- Fairness ↔ Revenue: Fair exposure across sellers/items may not maximize revenue. Revenue-maximizing may systematically favor established sellers.
- Freshness ↔ Safety: New items are exciting but risky (no quality signal). Proven items are safe but stale.

**Approaches** (from simplest to most principled):
1. **Weighted scalarization**: score = w₁·relevance + w₂·diversity + w₃·freshness. Simple but choosing weights is ad hoc.
2. **Constrained optimization**: Maximize relevance subject to diversity ≥ threshold AND fairness ≥ threshold. More principled — thresholds are business decisions.
3. **MMR reranking**: At each position, select the item that maximizes λ·relevance - (1-λ)·max_similarity_to_selected. Natural diversity-relevance balance.
4. **Pareto reranking**: Generate multiple Pareto-optimal slates, select based on context. Most principled, most complex.

> [!experience] At Amazon Ads, the multi-objective challenge was: relevance (advertiser ROI), marketplace health (auction balance), and platform revenue. We used constrained optimization: maximize advertiser ROI subject to marketplace health guardrails (CVR and RoAS can't regress). Revenue was treated as a secondary objective — a healthy marketplace with satisfied advertisers generates more revenue long-term than short-term revenue maximization.

**Hard FUQ**: Your diversity constraint reduces CTR by 3%. Product pushes back. How do you make the case for keeping it?

**Answer**: Short-term CTR vs long-term engagement. Show the data: (a) Users exposed to diverse recommendations have 15% higher 30-day retention than users in filter bubbles. (b) Diverse recommendations surface long-tail items that have higher CVR (less competition, better match). (c) Without diversity, the system converges to recommending the same 100 popular items to everyone — and when those items become stale, the entire system degrades. The 3% CTR drop is an insurance premium against long-term engagement collapse.

---

### Q8: Cross-attention and deep learning architectures for relevance scoring

**Principal Answer**: The evolution of ranking architectures tells the story of how recommendation systems learned to model interactions — from manual features to automatic interaction learning.

**Architecture evolution**:

1. **Linear/FTRL** (Yahoo Labs era): Hand-crafted features + logistic regression with online learning. Fast, interpretable, but requires expert feature engineering. I used FTRL algorithms at Yahoo Labs achieving 100% query-ad pair coverage for click prediction.

2. **GBDT** (early Amazon era): XGBoost/LightGBM over hundreds of features. Better feature interactions (tree splits capture non-linearity) but still manual features.

3. **Deep & Wide / DeepFM**: Wide component memorizes feature interactions, deep component generalizes. Reduced feature engineering, better generalization.

4. **Two-tower (DSSM)**: Separate user and item encoders → dot product similarity. Enables pre-computation of item embeddings for fast ANN retrieval. Trade off interaction quality for serving speed.

5. **Cross-attention**: Query and item tokens attend to each other → rich interaction modeling. Captures fine-grained query-item relevance that dot-product misses. The trade-off: can't pre-compute (must run at query time).

> [!experience] At Amazon Ads, we developed deep learning similarity models using cross-attention architectures achieving +900 bps relevance improvement over the two-tower baseline. The key insight: two-tower models compute query and item embeddings independently, losing fine-grained interaction. Cross-attention captures "this specific word in the query matches this specific attribute in the item" — which matters enormously for ads where intent precision determines ROI.

**The latency trade-off**: Cross-attention requires O(|query| × |item|) computation per query-item pair. At ranking time with 200 candidates, that's 200 cross-attention forward passes. We managed this by: (a) distilling cross-attention into a smaller model for serving, (b) pre-computing item-side representations and only running the cross-attention head at query time, (c) applying cross-attention only to top-200 after a fast two-tower retrieval of top-1000.

**Hard FUQ**: When would you choose two-tower over cross-attention despite the quality difference?

**Answer**: When serving latency budget is <10ms per candidate (two-tower: 0.01ms/candidate vs cross-attention: 1-5ms/candidate). When the catalog is >100M items and you need retrieval (two-tower enables ANN, cross-attention doesn't). When the quality gap is small for your domain (if queries are simple keywords and items have few attributes, cross-attention's advantage shrinks). In practice: two-tower for retrieval (Stage 1), cross-attention for scoring (Stage 2 on reduced candidate set).

---

### Q9: Global expansion — zero-shot recommendation for new markets

**Principal Answer**: Expanding a recommendation system to a new market is a cold-start problem at the MARKET level — no behavioral data for any user-item pair in that locale.

**Approaches** (ordered by data requirement):

1. **Zero-shot transfer**: Apply the model trained on data-rich market (US) directly to new market. Works if: items overlap (same catalog), user behavior is similar (same product categories), and the model generalizes across locales.

2. **Few-shot adaptation**: Use a small labeled dataset from the new market (10-20 examples per task type) to adapt the model. Fine-tune the last layer or use in-context learning.

3. **Cross-market transfer learning**: Train on all markets jointly with market-specific embeddings. The shared layers capture universal patterns; market-specific layers capture locale differences.

4. **Full locale-specific model**: Train a separate model for each market. Requires sufficient data. Reserved for top markets by volume.

> [!experience] At Amazon Ads, we scaled to 19+ locales using zero-shot and few-shot learning, reducing time-to-market by 75%. Key findings: (a) Zero-shot worked surprisingly well for EU markets (UK, DE, FR) because advertisers cross-sell across locales — behavioral patterns transferred. (b) For character-different markets (JP, KSA Arabic), zero-shot failed on text features but cross-market behavioral signals still transferred. (c) Few-shot closed the gap: 10-20 high-quality examples per locale captured cultural nuance without full retraining.

**Hard FUQ**: Your zero-shot model recommends items that are relevant by US standards but culturally inappropriate in the new market. How do you catch this?

**Answer**: You can't catch cultural mismatch purely from ML metrics — NDCG looks fine because the items ARE relevant in a generic sense. Requires: (a) Native-speaker review of top-100 recommendations per locale before launch. (b) Locale-specific guardrails (e.g., dietary restrictions in Middle East markets, different beauty standards in Asian markets). (c) User feedback loop after launch — higher thumbs-down rate or lower adoption in specific categories signals cultural mismatch. (d) Conservative initial launch: smaller recommendation set, human-reviewed, expanding as confidence grows.

---

### Q10: Position bias correction in training data

**Principal Answer**: Position bias is the most pervasive confounder in recommendation systems. Users click items at the top REGARDLESS of relevance. If you train on click data without correction, your ranker learns "position 1 is good" not "this item is good" — and it becomes a self-reinforcing loop.

**The mechanism**:
```
Item at position 1 → clicked (because it's at position 1, not because it's best)
→ click is logged as positive signal
→ ranker learns to rank this item higher
→ item appears at position 1 more often
→ gets more clicks
→ feedback loop accelerates
```

**Correction methods**:

1. **IPW (Inverse Propensity Weighting)**:
   - Estimate P(click | position) — the probability of clicking based on position alone
   - Weight each training example by 1/P(click | position)
   - Items at position 1 have high P(click | position) → low weight (don't over-count)
   - Items at position 10 have low P(click | position) → high weight (these clicks are more informative)

2. **Position-aware model**:
   - Include position as a feature during training
   - At inference: set position=0 (or average position) to get position-debiased scores
   - The model learns: "This click was partly because of position 3, partly because of item relevance" and factors them separately

3. **Randomization experiments**:
   - Randomly shuffle a small percentage of results (1-5%)
   - Clicks on randomly-positioned items are unbiased (no position effect)
   - Use these as calibration data for the main model
   - Cost: slight degradation of user experience on the randomized traffic

> [!experience] At Amazon Ads, position bias was critical for keyword recommendation ranking. Without correction, the model learned to rank historically-popular keywords higher, making the long-tail invisible. We used position-aware modeling with randomization-based calibration — this revealed that many long-tail keywords had higher TRUE relevance than their click data suggested, once position effects were removed.

**Hard FUQ**: You correct for position bias, but now your model recommends items that are "truly relevant" but users still don't click on them (because they're at lower positions). The business sees lower CTR. How do you handle this?

**Answer**: This is the classic "debiasing hurts short-term metrics" problem. The fix isn't to remove the correction — it's to measure the RIGHT metric. (a) Measure CTR per-position (compare CTR at position 3 before/after debiasing). If items at each position get higher CTR, the ranker is better even if aggregate CTR drops (because you're surfacing less-popular items higher). (b) Run a long-term A/B test: debiased ranker vs biased ranker over 30 days. Debiased typically wins on long-term metrics (diversity, retention, long-tail conversion) even if it loses on short-term CTR. (c) Present the result to leadership as: "We traded 2% CTR for 15% more catalog coverage and 8% better long-tail conversion. This serves more advertisers and builds a healthier marketplace."

---

### Q11: When traditional ML outperforms LLMs for ranking

**Principal Answer**: LLMs are not universally better for ranking. Traditional ML outperforms LLMs in several important scenarios:

1. **Well-calibrated probability estimation**: LLMs produce relevance judgments, not calibrated P(click) or P(conversion). For auction-based systems where bid = value × P(conversion), you need calibrated probabilities. Traditional ML (logistic regression, calibrated GBDTs) excels here.

2. **Tabular/behavioral features**: When the signal is in structured features (user history, click patterns, time-of-day effects), traditional ML is better. LLMs are powerful for UNSTRUCTURED content understanding, not for learning f(user_clicks_last_7_days, device_type, hour).

3. **Real-time serving at extreme scale**: <10ms per candidate at 100K candidates. LLMs can't do this. GBDT or a shallow DNN can.

4. **Incremental learning**: FTRL and online learning algorithms update with every click in real-time. LLMs require batch retraining. For real-time auction systems where the world changes hourly, online learning wins.

5. **Interpretability requirements**: GBDT feature importance is well-understood. LLM ranking decisions are opaque. For regulated domains or systems where you must explain ranking decisions, traditional ML is safer.

> [!experience] At Yahoo Labs, I built distributed online learning models using FTRL algorithms achieving 100% query-ad pair coverage. These models updated in real-time with every click, adapting to changing user behavior within minutes. An LLM can't match this responsiveness — it would require continuous fine-tuning at enormous cost. FTRL is still the right choice for real-time bidding and auction systems.

**Hard FUQ**: If traditional ML is better for so many cases, what's the actual value-add of LLMs in recommendation?

**Answer**: LLMs add value precisely where traditional ML can't: (a) Understanding WHAT an item IS from unstructured descriptions (content understanding). (b) Understanding WHAT a user WANTS from natural language queries (intent understanding). (c) Bootstrapping recommendations for items/users with NO behavioral history (cold-start). (d) Generating human-readable explanations (trust-building). The key insight: LLMs and traditional ML are complementary layers, not competing approaches. The best systems use both — traditional ML for behavioral prediction at scale, LLMs for content understanding and cold-start.

---

### Q12: How do you handle the evolution from traditional ML → deep learning → LLM-enhanced recommendations?

**Principal Answer**: This evolution isn't a replacement chain — it's an accumulation of capabilities. Each era added a layer; none replaced the previous one.

**Era 1 — Feature Engineering + Linear Models** (2005-2015):
- Hand-crafted features (CTR history, category match, recency)
- Logistic regression with FTRL for online learning
- Strengths: Fast, interpretable, well-calibrated, online-learnable
- Still used for: real-time bidding, auction scoring, position-sensitive predictions

**Era 2 — Deep Learning** (2015-2022):
- Automatic feature interactions (Deep & Wide, DeepFM, DCN)
- Learned representations (two-tower, cross-attention)
- Strengths: Reduced feature engineering, captured non-linear patterns, cross-modal understanding
- Still used for: candidate scoring, representation learning, multi-task prediction

**Era 3 — LLM-Enhanced** (2022-present):
- Content understanding from descriptions (semantic retrieval)
- Reranking with natural language reasoning
- Explanation generation
- Cold-start bootstrapping
- Strengths: Semantic understanding, zero-shot generalization, natural language interfaces
- Used for: retrieval augmentation, reranking top-K, explanations, cold-start

> [!experience] At Amazon Ads, I've lived all three eras: FTRL at Yahoo Labs (Era 1) → cross-attention deep learning at Amazon (+900 bps, Era 2) → LLM-based semantic retrieval and keyword generation (Era 3). The FTRL features from Era 1 still run alongside LLM-generated features from Era 3. Each era's models serve different roles in the same pipeline. The lesson: don't rip and replace. Layer intelligently.

**Hard FUQ**: A new hire proposes rebuilding the entire recommendation stack with LLMs from scratch ("the old ML stack is technical debt"). How do you respond?

**Answer**: Ask them to prove it on one specific metric with one specific experiment before proposing a full rewrite. The "old ML stack" isn't debt — it's battle-tested, well-calibrated, serving 300M+ MAU at <100ms. It has 8+ years of optimization, edge-case handling, and failure mode coverage that a new LLM stack would need to relearn painfully. The right approach: identify WHERE the current stack underperforms (cold-start? semantic mismatch? long-tail?), insert LLM capability at THAT specific point, and A/B test the improvement. If the LLM adds value, expand its scope. If not, you haven't broken the production system trying. "Don't rewrite what works. Augment where it doesn't."
[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

## Distinguished Engineer Depth Probes

<details>
<summary><strong>DE Probe 1: Two-Tower Architecture — Training, serving, and the representation bottleneck</strong></summary>

**Question**: Walk me through the two-tower model architecture. Why is the dot-product interaction a bottleneck, and what alternatives exist?

**What they're testing**: Deep understanding of the core retrieval architecture and its mathematical limitations.

**Answer**:
**Two-tower architecture**:
```
Query Tower:          Item Tower:
  query features        item features
       ↓                     ↓
  Dense layers          Dense layers
       ↓                     ↓
  query_emb (d-dim)     item_emb (d-dim)
       
Score = dot(query_emb, item_emb) or cosine_sim
```

**Training**: Contrastive learning with in-batch negatives. For each (query, positive_item) pair, all other items in the batch serve as negatives.
```
L = -log(exp(sim(q, i+)/τ) / Σ_j exp(sim(q, i_j)/τ))
```

**The representation bottleneck**: All query information must compress into a d-dimensional vector. All item information must compress into a d-dimensional vector. The interaction between them is a single dot product — one scalar. This means:

1. **Token-level alignment is lost**: "red running shoes" matched against "red hiking boots" gets high similarity (most tokens match). A cross-encoder would see that "running" ≠ "hiking" in context. Dot product can't.

2. **Dimensionality limits expressiveness**: With d=128, the model has 128 numbers to encode everything about the query. Increasing d helps but increases memory (each item requires d×4 bytes).

3. **No query-dependent item representation**: The item embedding is fixed regardless of the query. But an item's relevance to "comfortable shoes" is different from its relevance to "stylish shoes" — the same item should emphasize different attributes for different queries.

**Alternatives to pure dot product**:

| Architecture | Interaction | Quality | Serving Cost |
|---|---|---|---|
| Two-tower (dot product) | query·item | Baseline | O(1) per candidate (with ANN) |
| Two-tower + MLP head | MLP(concat(query, item)) | +5-10% | O(K) with K candidates (can't use ANN) |
| ColBERT (late interaction) | Σ max(q_token · i_tokens) | +10-15% | Token-level ANN possible, 100x more storage |
| Cross-attention | Full attention across q and i tokens | +20-30% | O(K × |q| × |i|) — expensive |

**Production compromise**: Two-tower for retrieval (ANN over 100M items, <10ms), cross-attention for scoring top-200 (quality where it matters, bounded latency). This is what we ran at Amazon Ads.

> [!experience] At Amazon Ads, the +900 bps improvement from cross-attention over two-tower was specifically because ads require fine-grained intent matching — "buy running shoes" vs "review running shoes" are very different advertiser intents, and the two-tower dot product collapses them. Cross-attention captures that "buy" modifies the relevance of the item differently than "review."

**Follow-up**: How do you handle the negative sampling problem in two-tower training?

**Answer**: In-batch negatives are biased toward popular items (they appear in more batches). This makes the model under-value unpopular items. Corrections: (1) Log-Q correction: weight negatives inversely by frequency — rare items are "harder" negatives. (2) Hard negative mining: explicitly mine items that are similar but not relevant (same category, different intent). (3) Mixed negatives: batch negatives (easy, cheap) + mined hard negatives (expensive, high-value). The training signal from one hard negative ≈ 100 random negatives.

</details>

<details>
<summary><strong>DE Probe 2: Online Learning and FTRL — Real-time model updates</strong></summary>

**Question**: How does FTRL (Follow The Regularized Leader) work for real-time click prediction? Why is it preferred over SGD for online learning in ads?

**What they're testing**: Algorithm-level understanding of online learning — the mathematical foundation of real-time recommendation.

**Answer**:
**FTRL-Proximal** solves the online convex optimization problem with L1 regularization (sparsity):

```
At each round t:
  Receive feature vector x_t
  Predict: ŷ_t = σ(w_t · x_t)
  Observe label y_t
  Update:
    w_{t+1} = argmin_w [Σ_{s=1}^{t} g_s · w + (1/2)Σ_{s=1}^{t} σ_s ||w - w_s||² + λ₁||w||₁ + (λ₂/2)||w||²]
    
    where g_s = gradient at step s, σ_s = learning rate schedule
```

**Why FTRL over SGD**:
1. **Sparsity**: L1 regularization in FTRL produces truly sparse weights (many exactly 0). SGD with L1 produces near-zero weights that aren't exactly zero — bad for memory and serving speed at billions of features.
2. **Per-coordinate learning rates**: FTRL tracks per-feature statistics, giving features that update rarely a higher effective learning rate. Critical for ads where most features are sparse (each ad has unique features).
3. **Convergence with non-stationary data**: Ads data is non-stationary (user behavior changes hourly). FTRL's regret bounds hold under non-stationarity with appropriate learning rate scheduling.

**FTRL implementation (simplified)**:
```python
class FTRL:
    def __init__(self, alpha, beta, lambda1, lambda2):
        self.z = {}  # accumulated gradient - learning_rate * weight
        self.n = {}  # accumulated squared gradient
        
    def predict(self, features):
        w = {}
        for i in features:
            if abs(self.z.get(i, 0)) <= self.lambda1:
                w[i] = 0  # L1 sparsity: feature is zeroed out
            else:
                sign = -1 if self.z[i] < 0 else 1
                w[i] = -(self.z[i] - sign * self.lambda1) / (
                    (self.beta + sqrt(self.n.get(i, 0))) / self.alpha + self.lambda2)
        return sigmoid(sum(w[i] * features[i] for i in features))
    
    def update(self, features, prediction, label):
        gradient = prediction - label
        for i in features:
            g = gradient * features[i]
            sigma = (sqrt(self.n.get(i, 0) + g*g) - sqrt(self.n.get(i, 0))) / self.alpha
            self.z[i] = self.z.get(i, 0) + g - sigma * self.w.get(i, 0)
            self.n[i] = self.n.get(i, 0) + g*g
```

> [!experience] At Yahoo Labs, I built distributed click-prediction models using FTRL achieving 100% query-ad pair coverage. The key production insight: FTRL's per-coordinate learning rates were critical for handling the extreme sparsity of ads features — a specific advertiser×keyword feature might update once per day, while a global CTR feature updates millions of times. FTRL automatically adapts the learning rate for each, which SGD cannot do without manual tuning.

**Follow-up**: When would you replace FTRL with a neural network for online learning?

**Answer**: When feature interactions are the bottleneck, not feature sparsity. FTRL is linear — it can't model interactions without manual feature crosses. If the signal is in combinations of features (user_segment × item_category × time_of_day), a shallow neural net with online updates (via online SGD/Adam) captures interactions automatically. The tradeoff: neural nets are harder to train online stably, require more memory, and lose FTRL's sparsity advantages. In practice at Amazon Ads, we used both: FTRL for real-time CTR prediction (speed, sparsity) + periodic deep learning model refreshes (daily, for interaction quality).

</details>

<details>
<summary><strong>DE Probe 3: Calibration — Why predicted probabilities must match reality</strong></summary>

**Question**: What is model calibration in ranking systems, and why does it matter more for ads/recommendations than for general ML?

**What they're testing**: Understanding of calibration as a production requirement, not just a nice-to-have.

**Answer**:
**Calibration** means: if your model predicts P(click) = 0.05 for a set of items, then 5% of those items should actually be clicked. Formally: E[y | ŷ = p] = p for all p.

**Why it matters more for ads**:
In auctions, the bid is computed as: `bid = value × P(conversion)`. If P(conversion) is systematically over-estimated by 2x, the advertiser bids 2x too much → wastes budget → loses trust → churns. If under-estimated by 2x, the advertiser under-bids → loses impressions → gets less value → churns. Miscalibration DIRECTLY costs money.

**Measuring calibration**:
```
Expected Calibration Error (ECE):
  1. Bin predictions into B buckets by predicted probability
  2. For each bucket b:
     accuracy(b) = fraction of positives in bucket
     confidence(b) = mean predicted probability in bucket
  3. ECE = Σ_b (|bucket_b| / N) × |accuracy(b) - confidence(b)|
```

Good calibration: ECE < 0.02. Typical uncalibrated DNN: ECE = 0.05-0.10.

**Why models become uncalibrated**:
1. **Distribution shift**: Model trained on last month's data; this month's CTR distribution is different (seasonality, new products, market changes)
2. **Position bias**: Model trained on position-biased click data overpredicts CTR for items typically shown at high positions
3. **Negative sampling**: Training with random negatives (not true negatives) inflates predicted probabilities
4. **Model architecture**: Deep models are notoriously poorly calibrated — confident wrong predictions

**Calibration methods**:
- **Platt scaling**: Learn a logistic transform: P_calibrated = σ(a × logit + b). Fit a,b on a held-out calibration set.
- **Isotonic regression**: Non-parametric monotone mapping from raw scores to calibrated probabilities. More flexible than Platt.
- **Temperature scaling**: P_calibrated = σ(logit / T). Learn a single temperature T on held-out data. Simplest neural net calibration.

> [!experience] At Amazon Ads, calibration was a first-class metric — not an afterthought. We tracked ECE daily and re-calibrated weekly using isotonic regression on fresh data. When we introduced the deep learning cross-attention model (+900 bps relevance), it was initially poorly calibrated (ECE=0.08). Post-calibration brought it to ECE=0.015 without losing ranking quality. The ranking improvement was invisible to the business until calibration was fixed — because miscalibrated bids masked the relevance gains.

**Follow-up**: How do you maintain calibration for a model that serves globally across 19+ locales with different CTR distributions?

**Answer**: Per-locale calibration. Each locale has different base rates (Japan CTR ≈ 1.5%, US CTR ≈ 3%, Germany CTR ≈ 2.2%). A single global calibration function would over-predict for low-CTR locales and under-predict for high-CTR locales. Solution: fit per-locale isotonic regression on locale-specific holdout data. Monitor ECE per locale separately. Some locales with sparse data may need hierarchical calibration: locale-specific + regional fallback + global fallback.

</details>

<details>
<summary><strong>DE Probe 4: Position Bias — IPW and counterfactual learning</strong></summary>

**Question**: Walk me through Inverse Propensity Weighting for position bias correction. What are the assumptions, and when do they break?

**What they're testing**: Causal inference foundations applied to recommendation systems.

**Answer**:
**The problem**: Click data is confounded by position. P(click | item, position) ≠ P(click | item). We want to learn P(click | item) but only observe P(click | item, position).

**IPW formulation**:
Assume the click probability factorizes as:
```
P(click | item i, position k) = P(relevant | item i) × P(examine | position k)

where:
  P(relevant | item i) = true item relevance (what we want to learn)
  P(examine | position k) = probability user even looks at position k (position bias)
```

This is the **Position-Based Model (PBM)** assumption.

**IPW correction**: Weight each click by the inverse of the examination probability:
```
w_ik = 1 / P(examine | position k)

Weighted loss:
  L = Σ_i Σ_k w_ik × loss(ŷ_i, y_ik)
```

Items at position 1 (P(examine)≈1.0) get weight ≈1. Items at position 10 (P(examine)≈0.3) get weight ≈3.3. This up-weights clicks from low positions (these clicks are more informative — the user CHOSE to look that far down).

**Estimating P(examine | position k)**:
- **Randomization**: Show items in random positions for 1-5% of traffic. P(examine | k) = observed_click_rate(k) / true_relevance (approximated from randomized data).
- **EM algorithm**: Jointly estimate examination and relevance probabilities from observational data (no randomization needed but stronger assumptions).
- **Regression discontinuity**: If there's a natural "fold" (above/below the fold on the page), compare click rates just above and below.

**When IPW breaks**:
1. **Propensity estimation error**: If P(examine | k) is estimated incorrectly, the weights are wrong and the correction makes things worse. High-variance propensity weights (very small P(examine) → very large weight) amplify noise.
2. **PBM assumption violation**: If P(click) doesn't factorize into relevance × examination (e.g., users examine items BECAUSE they look relevant → examination depends on item), the assumption is violated.
3. **Presentation bias beyond position**: Item image, title, price, and rating badges all affect examination probability. Position is the biggest factor but not the only one.

**Practical mitigation for IPW instability**: Clip weights: w_ik = min(1/P(examine|k), max_weight). Typical max_weight = 10-20. Trades some bias for much lower variance.

> [!experience] At Amazon Ads, position bias correction was essential for keyword recommendation ranking. Without correction, popular keywords at position 1 accumulated disproportionate positive signals, making the long-tail invisible. We used a position-aware model with randomization-based propensity estimation on 2% of traffic. The correction revealed that many long-tail keywords had higher TRUE relevance than their click data suggested.

**Follow-up**: You clip the IPW weights at 20. How do you know this is the right clipping threshold?

**Answer**: Bias-variance tradeoff analysis. Plot the estimator's MSE as a function of the clipping threshold on a held-out randomized set (where true relevance is observable). Low threshold → high bias (under-correcting position effects). High threshold → high variance (noisy estimates). The optimal threshold minimizes MSE. In practice, we found diminishing returns beyond clip=15-20 for our data — the correction captured 95% of the position effect and the remaining 5% wasn't worth the variance.

</details>

<details>
<summary><strong>DE Probe 5: Negative Sampling Strategies — Beyond random negatives</strong></summary>

**Question**: In recommendation model training, how do you choose negative examples? Why does this matter?

**What they're testing**: Understanding of a subtle but high-impact training decision that directly affects model quality.

**Answer**:
In recommendation, you observe positive interactions (clicks, purchases) but don't observe true negatives (items the user saw and explicitly rejected). "No click" could mean: irrelevant, not seen, not interested right now but might be later, or interested but distracted.

**Negative sampling strategies**:

1. **Random negatives** (simplest): Sample random items from the catalog as negatives.
   - Pro: Easy, fast, provides "global" negative signal.
   - Con: Too easy — most random items are obviously irrelevant. Model learns trivial distinctions, not the hard ones that matter at ranking time.

2. **In-batch negatives**: For each (query, positive_item) pair in a batch, all other items in the batch serve as negatives.
   - Pro: Free (no extra computation), harder than random (items in the batch are at least somewhat relevant to someone).
   - Con: Biased toward popular items (they appear in more batches).

3. **Hard negatives**: Items that are SIMILAR to the positive but NOT relevant. E.g., "red running shoes" → negative: "red hiking boots" (similar embedding, different intent).
   - Pro: Forces the model to learn fine-grained distinctions.
   - Con: Too many hard negatives can prevent convergence (model can't distinguish anything). Mining is computationally expensive.
   - Strategy: 70% easy/random negatives + 30% hard negatives is a common ratio.

4. **Impression-based negatives**: Items the user SAW (was shown) but didn't click. True "negative" interactions.
   - Pro: Closest to real negatives — user made a choice.
   - Con: Still position-biased (user may not have examined items below the fold).

**The impact of negative sampling on model quality**:
```
Random negatives only:       AUC = 0.78
+ In-batch negatives:        AUC = 0.81 (+3%)
+ Hard negative mining:      AUC = 0.85 (+4%)
+ Impression-based negatives: AUC = 0.87 (+2%)
```

The gains from better negative sampling often exceed the gains from architecture improvements. This is one of the highest-leverage training decisions.

> [!experience] At Amazon Ads, we found that deep learning representation learning using gradient-boosted trees and factorization machines achieved +400 bps lift — and a significant fraction of that improvement came from better negative sampling. We mined hard negatives from items that were semantically similar but in different intent categories. This forced the model to learn intent-level discrimination, which is what matters for ads (same product, different buying intent = completely different ad relevance).

**Follow-up**: How do you handle the case where a hard negative is actually a relevant item the user just didn't interact with yet?

**Answer**: This is the "false negative" problem. If your hard negative is actually relevant, you're training the model to rank a good item lower — poisoning the training. Mitigations: (1) Only use items the user was SHOWN but didn't click as hard negatives (impression-based), not items they never saw. (2) Confidence thresholding: only mine hard negatives that are high-similarity but LOW predicted relevance by a separately-trained model. (3) Label smoothing: instead of binary labels (1=click, 0=no-click), use soft labels (0.1 for unclicked items at top positions, 0.0 for unclicked items at bottom positions) to account for uncertainty.

</details>

<details>
<summary><strong>DE Probe 6: Multi-Objective Optimization — Pareto and constrained approaches</strong></summary>

**Question**: How do you formally optimize multiple conflicting objectives (relevance, diversity, fairness) in a ranking system?

**What they're testing**: Can you formalize the multi-objective problem beyond "weighted sum"?

**Answer**:
**The problem**: We have K objectives f₁(x), f₂(x), ..., fₖ(x) over ranking x. Maximizing one typically degrades another.

**Approach 1: Scalarization**
```
maximize: w₁f₁(x) + w₂f₂(x) + ... + wₖfₖ(x)
```
Simple. But: (a) weights are arbitrary — who decides w₁=0.7, w₂=0.3? (b) Can't find solutions on non-convex parts of the Pareto frontier. (c) Sensitive to objective scaling (f₁ in [0,1] and f₂ in [0,1000] makes w meaningless without normalization).

**Approach 2: Constrained optimization**
```
maximize: f₁(x)                    [primary: relevance]
subject to: f₂(x) ≥ τ₂            [diversity threshold]
            f₃(x) ≥ τ₃            [fairness threshold]
            f₄(x) ≤ budget         [cost constraint]
```

More principled: stakeholders define THRESHOLDS for secondary objectives, then you maximize the primary objective subject to those constraints. Thresholds are business decisions, not model parameters.

Solve via: Lagrangian relaxation, or iterative reranking (greedily select items that satisfy constraints while maximizing primary objective).

**Approach 3: Pareto-optimal set**
Compute the set of solutions where no objective can be improved without degrading another.

```
x* is Pareto-optimal if ∄ x' such that:
  f_i(x') ≥ f_i(x*) for all i AND
  f_j(x') > f_j(x*) for at least one j
```

Generate multiple Pareto-optimal rankings → select based on context (e.g., new user gets diversity-heavy ranking, returning user gets relevance-heavy).

**Approach 4: Multi-task learning**
Train the ranking model to predict ALL objectives simultaneously (shared bottom layers, separate prediction heads per objective). At serving time, combine predictions using a context-dependent policy.

```
Shared layers → [P(click), P(convert), diversity_score, fairness_score]
                              ↓
                   Context-dependent combiner
                              ↓
                        Final ranking
```

> [!experience] At Amazon Ads, we used constrained optimization: maximize advertiser ROI subject to marketplace health guardrails (CVR can't regress, RoAS floor, auction balance). The thresholds were set by business/product leadership — they're business decisions, not ML decisions. This separation was critical organizationally: the ML team optimizes within constraints, the business team sets constraints. No one argues about weights.

**Follow-up**: The fairness constraint prevents your model from ranking the most revenue-maximizing items at the top. Revenue drops 5%. How do you make the case?

**Answer**: (1) Long-term argument: Unfair systems concentrate exposure on a few sellers → smaller sellers leave → less selection → users leave → revenue drops more than 5% in the long run. (2) Regulatory argument: Regulatory pressure on algorithmic fairness is increasing. Being proactive costs 5% revenue now; being reactive after enforcement costs 5% revenue + legal fees + brand damage. (3) Compromise: apply fairness constraints gradually — start with a weak constraint (95th percentile sellers get minimum 2% exposure), measure revenue impact, tighten if tolerable. This finds the Pareto-efficient point between fairness and revenue empirically.

</details>
[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

## Cost Model

### Per-Query Cost Breakdown (2026 pricing, approximate)

| Component | Cost/Query | Assumptions | Optimization Lever |
|-----------|-----------|-------------|-------------------|
| Candidate generation (ANN) | $0.00005 | HNSW over 10M items, managed vector DB | Self-hosted for higher scale |
| ML ranker (Stage 2) | $0.0001 | DNN inference on 500 candidates, GPU | Batching, model distillation |
| LLM reranking (Stage 3) | $0.005 | 50 candidates scored by Haiku, list-wise | Apply selectively; cache for common queries |
| Explanation generation | $0.002 | 1 Haiku call per recommendation set | Template-based for common patterns |
| Feature generation (offline, amortized) | $0.0001 | LLM per item, amortized over queries | Batch during ingestion; cache |
| **Total (without LLM reranking)** | **~$0.0003** | Classical pipeline only | |
| **Total (with LLM reranking)** | **~$0.007** | LLM on top-50 | |
| **Total (with reranking + explanation)** | **~$0.009** | Full LLM-enhanced pipeline | |

### Monthly Cost at Scale

| Scale | Queries/Day | Monthly Cost | Cost/Query | Notes |
|-------|------------|-------------|------------|-------|
| Classical only (300M MAU) | 50M | ~$450K | $0.0003 | No LLM in hot path (current Amazon Ads scale) |
| +LLM reranking (selective) | 50M (10M get LLM) | ~$520K (+$70K) | $0.0003-$0.007 | LLM only for high-value/complex queries |
| +LLM reranking (all) | 50M | ~$10.5M | $0.007 | Prohibitive — selective application required |

> [!experience] At Amazon Ads serving 300M+ MAU, the economics were clear: LLM reranking on ALL queries would cost 20x more than the classical pipeline. We applied it selectively — high-value queries (large advertisers, high bid ranges) and complex queries (multi-attribute, natural language). This captured 80% of the LLM value at 20% of the cost.

### Cost Optimization Priority Stack
1. **Selective LLM application** (5-10x): Route only high-value/complex queries through LLM reranking. 80% of queries get classical pipeline only.
2. **Offline LLM features** (amortize): Generate item embeddings/attributes once, serve forever. $100K one-time for 10M items vs $70K/month for real-time.
3. **Model distillation** (2-3x on ranker): Distill large ranking model to smaller student for serving. Same quality, 3x cheaper inference.
4. **Caching** (1.3-1.5x): Cache LLM reranking results for common query-candidate pairs. Cache explanations for popular items.
5. **Batch prediction** (1.2x): Pre-compute personalized recommendations in batch (nightly) for returning users. Real-time only for new sessions.

### Build vs Buy Analysis

| Component | Managed/API | Self-Hosted | Decision |
|-----------|-------------|-------------|----------|
| Vector DB (retrieval) | Pinecone, Weaviate | pgvector, FAISS | Self-host at >10M items for cost; managed for <10M |
| Ranking model | N/A (always custom) | Custom DNN/GBDT on GPU | Always custom — ranking is the core IP |
| LLM reranking | Claude/GPT API | vLLM + open-source | API for quality; self-host for volume (>1M queries/day) |
| Feature store | Feast, Tecton | Custom on Redis/DynamoDB | Managed for small teams; custom at scale |
| Experimentation | Internal platform | Build on existing infra | Always build — marketplace experimentation is too specialized |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## Observability & Production Debugging

### Per-Query Traces

| Field | Why | Used For |
|-------|-----|----------|
| `query_text` + `user_features` | Reproduce queries; analyze personalization | Debugging, A/B analysis |
| `candidate_set` (IDs + retrieval scores) | Inspect retrieval quality | Recall analysis |
| `ranker_scores` (per candidate) | Inspect ranking quality | Ranking analysis, calibration monitoring |
| `llm_reranker_scores` (if applied) | Compare LLM vs ML ranker | Value-add measurement |
| `final_ranking` + `business_rule_adjustments` | Track what changed post-ranking | Diversity/policy audit |
| `explanation_text` (if generated) | Audit explanation fidelity | Trust, compliance |
| `user_feedback` (click, purchase, dwell, skip) | Ground truth signal | Model training, evaluation |
| `position_shown` | Position bias tracking | IPW calibration |
| `latency_breakdown` (per stage) | Performance monitoring | Bottleneck identification |
| `model_versions` (per stage) | Track which models served | A/B attribution, regression tracking |

### Monitoring Dashboard

| Panel | Metric | Alert Threshold | Escalation |
|-------|--------|----------------|------------|
| Online CTR (A/B) | Treatment vs control CTR | Negative delta >0.5% for 24h | → ML on-call: ranking regression |
| Online CVR (A/B) | Treatment vs control CVR | Any negative delta for 48h | → P0: business metric regression |
| Calibration ECE | Expected Calibration Error | >0.03 (was 0.015) | → Recalibrate model |
| Retrieval recall (golden set) | Recall@100 on labeled queries | <85% (was 92%) | → Retrieval team: embedding or index issue |
| Catalog coverage | % of items recommended in last 7 days | <40% (was 55%) | → Diversity: filter bubble forming |
| LLM reranking lift | NDCG improvement from LLM stage | <2% (was 8%) | → LLM stage not adding value; investigate or remove |
| Latency p99 | End-to-end serving latency | >200ms (SLA: 100ms) | → Infra: check model serving, candidate set size |

### Debugging Walkthrough

**Scenario**: A/B test shows the new ranking model improves CTR by 3% but CVR drops by 1.5%. Net revenue is slightly negative.

**Step 1 — Segment analysis**: Slice CTR and CVR by item category, user segment, and query type. Finding: CTR improved uniformly (+3% everywhere). CVR dropped specifically for high-intent queries ("buy [product name]") by -4%, while low-intent queries ("compare [category]") improved CVR by +2%.

**Step 2 — Inspect ranking changes**: For high-intent queries, compare rankings old vs new. Finding: new model ranks "engaging" items higher (good images, catchy titles) that get clicks but don't convert. Old model ranked items with higher historical CVR higher.

**Step 3 — Root cause**: New model was trained with a CTR-focused objective. It learned to rank click-worthy items, not purchase-worthy items. For high-intent queries where the user is ready to buy, CTR-worthy ≠ CVR-worthy.

**Step 4 — Fix**: (a) Short-term: roll back for high-intent queries only (keep the improvement for low-intent). (b) Medium-term: retrain with a multi-objective loss: primary=CVR for high-intent queries, primary=CTR for low-intent queries, with query-intent classification routing. (c) Long-term: constrained optimization — maximize CTR subject to CVR ≥ previous_CVR per query segment.

> [!experience] At Amazon Ads, we encountered exactly this: improving keyword recommendation relevance (CTR) sometimes degraded conversion (CVR) for lower-funnel keywords. The resolution was the constraint-based approach: can't regress CVR or RoAS, period. This made CVR a hard guardrail, not a secondary objective.

### Versioning & Rollback

| Component | How to Version | How to Rollback | A/B Test Strategy |
|-----------|---------------|-----------------|-------------------|
| Retrieval embeddings | Index version + model ID | Alias swap to previous index | Shadow traffic: compare retrieval overlap |
| Ranking model | Model version in serving config | Route to previous model | Interleaving or A/B by user segment |
| LLM reranker | Prompt version + model ID | Config rollback | 5% traffic to new reranker; compare NDCG lift |
| Business rules | Rule version in config | Config rollback | Test rules on logged data before production |
| Feature pipeline | Pipeline version | Revert feature extraction; may need reindex | Compare feature distributions old vs new |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Availability | Latency | What It Tells You | Action |
|--------|-------------|---------|-------------------|--------|
| Click-through | High volume | Immediate | Engagement relevance (noisy due to position bias) | Train ranker with IPW correction |
| Purchase/conversion | Medium volume | Hours-days | True item value (strongest signal) | Primary ranking optimization target |
| Dwell time / scroll depth | High volume | Immediate | Implicit quality signal (long dwell = engaging) | Secondary ranking signal |
| Add to cart / save | Medium volume | Immediate | Purchase intent without completion | Intermediate signal between CTR and CVR |
| Returns / complaints | Low volume | Days-weeks | Negative quality signal (the recommendation led to a bad outcome) | Negative training signal; item quality adjustment |
| Explicit feedback (thumbs, ratings) | Low volume | Immediate | Direct quality assessment | Highest per-signal value; sparse |

### Improvement Prioritization

| Failure Mode | Business Cost | Frequency | Fix | Priority |
|---|---|---|---|---|
| Irrelevant top-3 recommendations | Very High (first impression drives engagement) | 5-10% | Better ranking for head queries | **P0** |
| Cold-start items invisible | High (new sellers/products get no exposure) | 15% of catalog | LLM-based content understanding + exploration | **P0** |
| Filter bubble (declining diversity) | High (long-term retention risk) | Gradual | MMR reranking, diversity constraints | **P1** |
| Miscalibrated CTR prediction | High (auction distortion) | Ongoing drift | Weekly recalibration pipeline | **P1** |
| Slow recommendation latency | Medium (UX degradation) | 5% of queries >200ms | Model distillation, caching | **P2** |
| Stale recommendations (same items) | Medium (user boredom) | 20-30% of sessions | Freshness boost, session-aware diversity | **P2** |

### Continuous Improvement Cadence

| Frequency | What Gets Updated | Validation Gate |
|-----------|-------------------|-----------------|
| Real-time | FTRL click model (online updates) | Calibration ECE < 0.02 |
| Daily | Feature pipeline (new behavioral data) | Feature distribution check |
| Weekly | Calibration re-fit (isotonic regression) | ECE improvement on holdout |
| Bi-weekly | LLM features refresh (new/updated items) | Embedding quality on golden set |
| Monthly | Full ranking model retrain | Offline NDCG + online A/B for 1 week |
| Quarterly | Architecture changes (new stages, new models) | Full regression suite + 2-week A/B |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| **Multi-stage pipeline** | Scale (can't score millions with one model) | Any production system with >10K items | Tiny catalogs (<1K) where you can score all |
| **LLM reranking on top-K** | Semantic fit that behavioral ranker misses | Cold-start, complex queries, high-value users | Latency-critical paths (<50ms budget) |
| **Two-tower retrieval** | Fast ANN-based candidate generation at scale | Large catalogs (>100K items) | When fine-grained interaction matters more than speed |
| **Cross-attention scoring** | Fine-grained query-item interaction | Precision ranking on reduced candidate set | Full catalog scoring (too slow) |
| **Position bias correction (IPW)** | Debiased training from position-confounded clicks | Any system trained on implicit feedback | Systems with explicit ratings (no position bias) |
| **MMR diversity reranking** | Filter bubble prevention | User-facing surfaces where variety matters | B2B/transactional where exact match is all that matters |
| **Zero-shot cross-market** | New market cold-start | Global expansion with data-sparse markets | Markets with very different user behavior patterns |
| **Double-randomized experimentation** | Marketplace interference in A/B tests | Marketplace-level interventions (ads, pricing) | Independent user experiments (no marketplace effects) |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|---|---|
| "We use a two-tower model for retrieval" | "Two-tower for retrieval, cross-attention for scoring. Two-tower compresses interaction into a dot product — sufficient for recall at scale but loses fine-grained intent matching. Cross-attention on top-200 captures the token-level alignment that matters for precision." |
| "We train on click data" | "We train on click data with IPW position correction and calibrate weekly with isotonic regression. Raw click data is position-biased — without correction, the model learns to rank items higher because they WERE at the top, not because they're better." |
| "We added an LLM to improve recommendations" | "We added LLM reranking selectively — only for high-value and complex queries where the behavioral ranker has insufficient signal. For 80% of queries, the classical pipeline outperforms at 1000x lower cost. The question isn't 'should we use LLMs' but 'where does the marginal value exceed the marginal cost?'" |
| "We optimize for CTR" | "We optimize for CVR subject to CTR and diversity constraints. CTR maximization is a trap — it favors clickbait and filter bubbles. We constraint-optimize: maximize the primary business metric (CVR/RoAS) subject to engagement and diversity floors." |
| "We improved NDCG by 5%" | "We improved NDCG by 5%, which translated to 2% CVR lift in the A/B test measured with double-randomized experimentation. Without marketplace-level measurement, we'd have seen only 1% — standard A/B understated the impact due to interference." |
| "We handle cold-start with content features" | "Cold-start is 15% of our catalog and disproportionately affects new sellers. We use LLM-generated content embeddings for immediate retrieval participation, plus contextual bandits for exploration. The 75% time-to-market reduction from zero-shot transfer made new market launches viable at 19+ locales." |
| "We recommend 200 items" | "We learned that users only engage with the top 10-30 recommendations regardless of list length. Improving positions 31-200 has zero business impact. We reframed from 'generate more recommendations' to 'present fewer, better ones with expected impact' — which delivered +2700 bps coverage and +1300 bps adoption." |
| "We A/B test our changes" | "Standard A/B is insufficient for marketplace interventions. When treatment users bid on new keywords, they change auction dynamics for control users — violating SUTVA. We designed double-randomized experimentation that isolates marketplace interference, which became the org-wide standard." |

[[#Recommendation / Ranking with LLMs — Interview Prep|↑ Top]]

---

## References

### Foundational Papers
1. Deep Learning Recommendation Model (DLRM) — Meta (Naumov et al., 2019) — https://arxiv.org/abs/1906.00091
2. Wide & Deep Learning for Recommender Systems — Google (Cheng et al., 2016) — https://arxiv.org/abs/1606.07792
3. DeepFM: A Factorization-Machine based Neural Network — (Guo et al., 2017) — https://arxiv.org/abs/1703.04247
4. Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations — Google (Yi et al., 2019) — https://research.google/pubs/pub48840/
5. Ad Click Prediction: a View from the Trenches — Google (McMahan et al., 2013) — https://research.google/pubs/pub41159/

### LLM-Enhanced Recommendations
6. A Survey on Large Language Models for Recommendation — (Wu et al., 2023) — https://arxiv.org/abs/2305.19860
7. Recommendation as Language Processing (RLP): A Unified Pretrain, Personalize, and Predict Paradigm — (Li et al., 2023) — https://arxiv.org/abs/2309.12740
8. LLM-Rec: Large Language Models for Recommendation — (Lyu et al., 2023) — https://arxiv.org/abs/2307.15780

### Retrieval & Embeddings
9. Dense Passage Retrieval for Open-Domain QA — (Karpukhin et al., 2020) — https://arxiv.org/abs/2004.04906
10. Sentence-BERT: Sentence Embeddings using Siamese BERT — (Reimers & Gurevych, 2019) — https://arxiv.org/abs/1908.10084
11. ColBERT: Efficient and Effective Passage Search — (Khattab & Zaharia, 2020) — https://arxiv.org/abs/2004.12832

### Evaluation & Experimentation
12. RAGAS Documentation — https://docs.ragas.io/en/stable/
13. Trustworthy Online Controlled Experiments — (Kohavi, Tang, Xu, 2020) — standard A/B testing reference
14. Interference in marketplace experiments — (Blake & Nosko, 2015; Taddy et al.) — marketplace A/B challenges

### Position Bias & Calibration
15. Unbiased Learning to Rank with Unbiased Propensity Estimation — (Ai et al., 2018) — https://arxiv.org/abs/1804.05938
16. Position Bias Estimation for Unbiased Learning to Rank in Personal Search — (Wang et al., 2018) — https://research.google/pubs/pub46485/
17. On Calibration of Modern Neural Networks — (Guo et al., 2017) — https://arxiv.org/abs/1706.04599

### Diversity & Fairness
18. Maximal Marginal Relevance (MMR) — (Carbonell & Goldstein, 1998) — foundational diversity method
19. Fairness of Exposure in Rankings — (Singh & Joachims, 2018) — https://arxiv.org/abs/1802.07281

### Online Learning
20. Follow-the-Regularized-Leader and Mirror Descent — (McMahan, 2017) — https://arxiv.org/abs/1711.01547
21. Practical Lessons from Predicting Clicks on Ads at Facebook — (He et al., 2014) — online learning in production

### Industry
22. Monolith: Real Time Recommendation System With Collisionless Embedding Table — ByteDance (Liu et al., 2022) — https://arxiv.org/abs/2209.07663
23. Embedding-based Retrieval in Facebook Search — Meta (Huang et al., 2020) — https://arxiv.org/abs/2006.11632
