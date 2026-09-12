# Search & Retrieval (Information Retrieval, Semantic Search, Hybrid Search Systems)

> **Last Updated:** 2026-05-31 | **Read time:** ~25 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Search has evolved from BM25 lexical matching [1] to hybrid sparse+dense pipelines with learned sparse models like SPLADE [3] and multi-stage reranking with cross-encoders [4].
> Key players: ColBERTv2 [15], SPLADE [3], FAISS [14], Sentence-BERT [8]. Main open problem: real-time index updates for billion-scale dense retrieval without quality degradation.
> Recent breakthrough: ColBERTv2 (2022) achieves cross-encoder quality at 100x lower latency via residual compression [15]. Trend: learned sparse retrieval replacing hand-tuned BM25.

## State of the Art

### Current Best Approaches

- **Hybrid BM25 + Dense retrieval with RRF** — Combines lexical precision with semantic recall via reciprocal rank fusion [12]; dominant production pattern
- **SPLADE learned sparse** — Transformer predicts term importance over full vocabulary, enabling semantic matching on inverted indexes [3]
- **ColBERTv2 late interaction** — Per-token embeddings with MaxSim scoring achieve near-cross-encoder quality with pre-computable document representations [15]
- **Multi-stage retrieval** — L0 candidate generation (BM25/ANN) → L1 cross-encoder rerank [4] → L2 business logic; standard at scale
- **Dense passage retrieval** — Bi-encoder models produce query/document embeddings for ANN search [2][8]

### Recent Breakthroughs (last 12 months)

- **ColBERTv2** (2022): Residual compression reduces storage 6-10x while maintaining late-interaction quality [15]
- **SPLADEv2** (2022): Distillation + improved regularization achieves dense retrieval quality on inverted index infrastructure [3]
- **Balanced Topic-Aware Sampling** (2021): TAS-B training produces bi-encoders competitive with cross-encoders on in-domain data [9]
- **Billion-scale FAISS on GPU** (2019, widely adopted 2023+): IVF-PQ with GPU acceleration enables sub-10ms search over 1B+ vectors [14]

### Open Problems

- **Real-time dense index updates**: Inserting new items into HNSW without quality degradation or full rebuild [5]
- **Cross-domain generalization**: Dense retrievers trained on one domain degrade 20-40% on out-of-domain queries [13]
- **Efficient cross-encoder serving**: Full cross-attention at scale remains latency-prohibitive for large candidate sets [4][7]
- **Multimodal retrieval fusion**: Combining text, image (CLIP [10]), and structured metadata in a unified ranking framework

## Executive Summary

Search and retrieval is the problem of finding the most relevant documents from a large corpus given a user query, operating under strict latency constraints. The key architectural decision is **lexical vs semantic vs hybrid retrieval** — and in production, the answer is always hybrid because failure modes are complementary: BM25 [1] handles exact matches that embeddings miss, dense retrieval [2] handles semantic matching that BM25 misses.

- **Choose BM25-only** when corpus is small (<100K), queries are keyword-based, and simplicity matters
- **Choose hybrid (BM25 + dense + RRF)** for production systems serving diverse query types at scale [12]
- **Choose SPLADE** when you want semantic matching without maintaining two separate index types [3]

**The killer framing:** "Every component in the retrieval pipeline earns its latency budget by fixing a specific failure mode — BM25 for exact match, dense for semantic, cross-encoder for fine-grained relevance [4], and each is measurable independently."

Cost headline: Full hybrid pipeline with cross-encoder reranking costs ~$0.001/query at scale; BM25-only costs ~$0.00001/query.

```
Multi-Stage Retrieval Pipeline
───────────────────────────────
Query → [Query Understanding: 5ms]
         ├── BM25 (inverted index): 10ms → top-1000
         └── Dense ANN (HNSW/IVF): 15ms → top-1000
              ↓
         [RRF Fusion]: 1ms → top-200
              ↓
         [Cross-Encoder Rerank]: 80ms → top-20
              ↓
         [Business Logic / Filters]: 2ms → final results
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Query types (keyword, NL, voice)? Corpus size? Latency SLA? Freshness? | Is this search for users, retrieval for a downstream model, or a matching system? |
| 2. Identify constraints | Vocabulary mismatch, scale (10M vs 1B items), p99 latency (<100ms?), domain jargon | Pure semantic misses exact terms; pure lexical misses intent. What's the failure cost? |
| 3. Propose baseline | BM25 on inverted index [1] + basic query processing | BM25 handles 60-70% of queries acceptably. Prove it's insufficient before adding complexity. |
| 4. Identify gaps | Paraphrase misses, acronym failures, zero-result queries, vocabulary mismatch | Systematic failure diagnosis: exact-match gap vs semantic gap vs coverage gap |
| 5. Introduce improvements | Hybrid retrieval [12], cross-encoder reranking [4], SPLADE [3], query rewriting | Each addition targets a measured failure mode with a specific latency budget |
| 6. Add evaluation + guardrails | NDCG@10, MRR, zero-result rate, interleaving experiments [11] | Offline metrics are necessary; online interleaving is authoritative for ranking changes |
| 7. Discuss scaling tradeoffs | HNSW memory [5] vs IVF-PQ compression [14], reranker latency, index freshness | Architecture must serve at <100ms p99 — every component justifies its latency contribution |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Index type | HNSW (graph) [5] | IVF-PQ (cluster) [14] | Corpus fits in memory, need <5ms latency | Memory-constrained, >100M vectors |
| Retrieval model | Bi-encoder [8] | SPLADE [3] | Need cross-lingual, existing vector DB infra | Have inverted index infra, want interpretability |
| Fusion | RRF [12] | Learned fusion | No labeled data, quick start | 10K+ labeled pairs, systems have different quality profiles |
| Reranking | Cross-encoder [4] | ColBERT [6] | Quality-critical, <200 candidates | Latency-critical, need >500 candidates reranked |
| Query expansion | Rule-based synonyms | LLM rewriting | Predictable domain, low latency | Open-ended queries, can afford 100ms+ |

## System Design Walkthrough

### Opening Frame

A production search system is a multi-stage pipeline where each stage trades compute for precision on a progressively smaller candidate set. The non-obvious insight: query understanding (classifying intent, fixing typos, expanding terms) often yields larger quality gains than improving the retrieval models themselves — yet it's consistently underinvested.

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Multi-Stage Search Pipeline                      │
├─────────────┬──────────────┬──────────────┬──────────────────────┤
│ Query Layer │ Retrieval    │ Ranking      │ Serving              │
├─────────────┼──────────────┼──────────────┼──────────────────────┤
│ Spell Fix   │ BM25 [1]     │ RRF [12]     │ Result Cache         │
│ Entity Det  │ Dense ANN [2]│ Cross-Enc [4]│ A/B / Interleave [11]│
│ Intent Clf  │ SPLADE [3]   │ Biz Logic    │ Feedback Logger      │
│ Rewrite     │ Filters      │ Diversity    │ Latency Monitor      │
└─────────────┴──────────────┴──────────────┴──────────────────────┘
```

- **Query Layer**: Processes raw query in <10ms — spell correction, entity detection, intent classification, optional rewriting
- **Retrieval Layer**: Multiple retrievers run in parallel; each returns top-K candidates from the full corpus
- **Ranking Layer**: Fuses candidate sets via RRF [12], applies cross-encoder reranking [4] on top-200, then business rules
- **Serving Layer**: Caches popular queries, runs interleaving experiments [11], logs feedback for the data flywheel

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Vocabulary mismatch (paraphrases) | Add dense retrieval with domain-tuned embeddings [8] | +15ms latency, vector index infrastructure |
| Exact match failures (codes, IDs) | Ensure BM25 path with high-IDF term handling [1] | Requires maintaining inverted index alongside vector DB |
| Coarse ranking from dot-product | Cross-encoder reranking on top-200 [4] | +80ms latency, GPU serving cost |
| Domain abbreviation misses | SPLADE with learned expansion [3] or synonym dictionary | Model retraining or dictionary maintenance |
| Query ambiguity / short queries | Intent classification + conditional expansion | Risk of intent misclassification changing results |

### Scaling Summary

- **10x (10M→100M items)**: Shard index across machines; scatter-gather adds merge latency; quantize to INT8 for memory [14]
- **100x (1B items)**: Tiered index (hot in HNSW [5], cold in IVF-PQ [14]); cross-encoder budget shrinks to top-50; aggressive caching
- **1000x (10B queries/day)**: Pre-compute results for head queries; replicate index shards; model distillation for reranker

## Interview Q&A Bank

### Q1: Why does hybrid retrieval (BM25 + dense) dominate production systems?

> **Quick answer:** BM25 [1] and dense retrieval [2] have complementary failure modes — BM25 excels at exact matches and rare terms, dense excels at semantic matching — and combining them via RRF [12] covers both without requiring score normalization.

BM25 fails on vocabulary mismatch: "ML" never matches "machine learning" because there's zero token overlap. Dense retrieval fails on exact codes: ASIN "B0CXYZ123" gets split into meaningless BPE subwords with no learned semantics. The combination addresses both.

Fusion via RRF [12]: RRF_score(d) = sum over systems of 1/(k + rank(d)), where k=60 is standard. RRF is rank-based (no score normalization needed), favors consensus (items in both lists rank highest), and requires zero training data. At k=60, the score difference between rank 1 and 60 is only 0.008 — heavily rewarding items that appear in multiple systems.

| Failure Type | BM25 | Dense | Hybrid |
|---|---|---|---|
| Exact codes/IDs | Succeeds | Fails | Succeeds |
| Paraphrases | Fails | Succeeds | Succeeds |
| Rare domain terms | Succeeds (high IDF) | Often fails | Succeeds |
| Intent matching | Fails | Succeeds | Succeeds |

**Hard follow-up:** Your BM25 and dense systems have only 20% candidate overlap. Problem or strength?

> Diagnose by sampling items unique to each system and having humans judge relevance. If both unique sets are 70%+ relevant, low overlap is a strength (combined recall is high). If one set is <40% relevant, that retrieval path is miscalibrated for your domain and needs fixing.

---

### Q2: How does a cross-encoder differ from a bi-encoder, and where does ColBERT fit?

> **Quick answer:** Bi-encoders [8] encode query and document independently (fast, pre-computable), cross-encoders [4] encode them jointly (precise, expensive per-pair), and ColBERT [6] sits between — per-token embeddings with late MaxSim interaction.

Bi-encoder: query_emb = E(q), doc_emb = E(d), score = dot(query_emb, doc_emb). Pre-compute all doc embeddings, serve via ANN in <10ms over millions. Weakness: no token-level alignment between query and document [8].

Cross-encoder [4]: score = Model([q; SEP; d]). Full cross-attention captures "buy shoes" vs "review shoes" as different intents for the same product. But requires O(1) forward pass per candidate — 100 candidates takes ~80ms on GPU.

ColBERT [6][15]: computes per-token embeddings independently, then scores via MaxSim (for each query token, find max-similarity document token, sum). Document token embeddings are pre-computable. Trade-off: 100x more storage than bi-encoder but 100x faster than cross-encoder at query time.

**Hard follow-up:** When would you choose ColBERT over a cross-encoder?

> When latency budget is <50ms for reranking AND you need to rerank >200 candidates. ColBERTv2 [15] achieves within 2-3% of cross-encoder quality with residual compression reducing the storage overhead. At very large scale (hundreds of millions of items), cross-encoder on top-100 is often more cost-effective than ColBERT's storage cost.

---

### Q3: How does BM25 scoring work, and where does it break?

> **Quick answer:** BM25 [1] scores documents using saturating term frequency, inverse document frequency, and length normalization — derived from the probabilistic relevance framework. It fails on synonymy, multi-word concepts, and negation.

Formula: BM25(q,d) = sum over terms t in q of: IDF(t) * (tf(t,d) * (k1+1)) / (tf(t,d) + k1*(1-b+b*|d|/avgdl)) [1].

Components: (1) IDF = log((N-df+0.5)/(df+0.5)) — rare terms are more discriminative. (2) Saturating TF — mentioning "shoes" 100x isn't 100x better; k1=1.2 controls saturation. (3) Length normalization — b=0.75 corrects for longer documents naturally having higher TF.

Where it breaks: (a) Independence assumption — "New York" = "New" + "York", may match HVAC products for "Air." (b) No synonymy — "ML" and "machine learning" have zero BM25 similarity. (c) No semantics — polysemous words like "bank" are indistinguishable. (d) Short queries — 1-2 word queries are dominated by IDF, a corpus-global property.

**Hard follow-up:** How does SPLADE improve on BM25 while keeping inverted index infrastructure?

> SPLADE [3] predicts importance weights over the full vocabulary at each token position, then max-pools. "Running shoes" activates "jogging: 0.4, sneakers: 0.2, footwear: 0.5" — terms not in the document get non-zero weights. This stores in a standard inverted index but captures semantic expansion that BM25 cannot. Quality reaches ~95% of dense retrieval with lexical serving speed.

---

### Q4: How do you fuse results from multiple retrieval systems?

> **Quick answer:** RRF (Reciprocal Rank Fusion) [12] is the default — it's rank-based (no score normalization), robust without training data, and favors items that appear in multiple systems.

RRF formula: RRF_score(d) = sum_r 1/(k + rank_r(d)) [12]. At k=60, the function heavily rewards consensus across systems. Key property: BM25 scores range 0-20, cosine similarity ranges -1 to 1, but RRF only uses ranks — sidestepping the normalization problem entirely.

Alternatives: (1) **Score interpolation**: score = alpha*BM25_norm + (1-alpha)*dense_norm. Requires careful normalization and a tuning parameter. (2) **Learned fusion**: train a model on (BM25_rank, dense_rank, features) → relevance. Better by 2-5% recall when you have >10K labeled pairs.

When RRF fails: if one system is strictly better for 90% of queries, RRF gives equal weight to the weaker system, diluting quality. Fix: weighted RRF or query-type routing.

**Hard follow-up:** How do you handle an item that appears in BM25 top-10 but is completely missing from dense results?

> In RRF, missing items get no contribution from the absent system — effectively penalized. This is usually desirable (consensus is valuable). If your systems have structurally different coverage (e.g., one handles English, another handles code), use max-score instead of sum, or route queries to the appropriate system rather than fusing.

---

### Q5: How do you choose and fine-tune an embedding model for domain search?

> **Quick answer:** Evaluate on YOUR production queries (not MTEB), choose based on domain performance + latency constraints, and fine-tune with contrastive learning on click/purchase pairs using hard negative mining [8][9].

Selection: (1) Domain evaluation — MTEB #1 may rank #5 on your queries. (2) Dimension trade-off — 384-dim serves 3x faster than 1024-dim with <5% quality loss. (3) Multilingual capability — choose multilingual from day one if serving multiple locales [8].

Fine-tuning uses InfoNCE loss: L = -log(exp(sim(q, d+)/tau) / sum_negatives(exp(sim(q, d-)/tau))). Use click pairs as positives, shown-but-not-clicked as negatives. Hard negative mining (items semantically similar but not relevant) provides the strongest gradient signal [9]. TAS-B (topic-aware sampling) ensures balanced training across query types [9].

Critical: fine-tune on PRODUCTION queries (messy, abbreviated, with typos), not curated evaluation queries. The model must learn your users' actual language.

**Hard follow-up:** Fine-tuning on click data is position-biased. How do you correct for this?

> Apply inverse propensity weighting: weight each (query, clicked_item) pair by 1/P(examine|position). Items clicked at low positions get higher weight. Alternatively, use conversion data (less position-biased) or include unbiased pairs from randomized traffic experiments.

---

### Q6: What is NDCG and how does it differ from MRR for retrieval evaluation?

> **Quick answer:** NDCG (Normalized Discounted Cumulative Gain) handles graded relevance across all positions; MRR (Mean Reciprocal Rank) only measures the rank of the first relevant result. NDCG is standard for ranked lists; MRR for navigational queries.

NDCG@K = DCG@K / IDCG@K, where DCG@K = sum_{i=1}^{K} (2^{rel_i} - 1) / log2(i+1). It discounts relevance by log-position and normalizes by the ideal ranking. A perfect ranking scores 1.0.

MRR = mean over queries of 1/rank(first_relevant_result). Only cares about the top relevant result — ignores the quality of positions 2-K.

| Metric | Best for | Handles graded relevance | Position-sensitive |
|---|---|---|---|
| NDCG@K | General ranking evaluation | Yes (0-4 scale) | Yes (log discount) |
| MRR | Navigational queries (one right answer) | No (binary) | Yes (1/rank) |
| Recall@K | Candidate generation quality | No (binary) | No |

**Hard follow-up:** Your offline NDCG improved 8% but online CTR didn't change. What happened?

> The improvement was likely on long-tail queries representing a small fraction of production volume. Slice by query frequency: if head queries (80% of traffic) show no improvement, the aggregate uplift is invisible online. Additionally, the label set may not represent production — maintain a production query sample refreshed monthly alongside curated eval sets.

---

### Q7: How do you handle domain-specific vocabulary that embedding models miss?

> **Quick answer:** Maintain BM25 as a safety net for codes/IDs, build a domain synonym dictionary for abbreviations, and fine-tune embeddings on domain pairs. Never rely on embeddings alone for exact-match queries.

Problem taxonomy: (1) Codes/IDs — meaningless strings that BPE splits randomly. (2) Acronyms — "CPC", "RoAS" may have wrong or no learned semantics. (3) Jargon — domain-specific meanings differing from general English. (4) Compound terms — multi-word concepts that should be atomic.

Solutions stack: (a) BM25 handles all exact-match queries natively [1]. (b) Synonym dictionary expands abbreviations at query time before both retrieval systems see the query. (c) Domain vocabulary in tokenizer — "RoAS" should be one token. (d) Embedding fine-tuning on domain query-document pairs [8][9].

> [!experience] At Amazon Ads, ASINs were the highest-precision query type — embeddings completely failed because BPE splits "B0CXYZ123" into meaningless subwords. BM25 handles it trivially. This single failure mode justified maintaining lexical retrieval for the system's entire lifetime.

**Hard follow-up:** Can you train embeddings that handle exact codes correctly?

> Partially — add code-aware tokenization and train with code-based pairs. But new unseen codes require continuous fine-tuning. Pragmatically, BM25 for exact match + embeddings for semantic is cheaper and more robust than forcing embeddings to solve both problems.

---

### Q8: How do you scale retrieval to serve 300M+ MAU at <100ms?

> **Quick answer:** Pre-compute all item embeddings, shard indexes across machines with scatter-gather, use tiered storage (hot in HNSW [5], cold in IVF-PQ [14]), and cache repeated queries for 15-30% hit rate.

| Component | Strategy | Latency Budget |
|---|---|---|
| Query processing | CPU-only, lightweight | <5ms |
| BM25 retrieval | Sharded inverted index | <10ms |
| Dense ANN | HNSW in-memory [5] | <15ms |
| Cross-encoder rerank [4] | GPU, top-100 only | <80ms |
| Feature lookup | Pre-computed, cached | <1ms |

Key decisions: (1) Never compute item embeddings at query time — only the query embedding. (2) Scatter-gather across index shards, merge top-K locally. (3) Quantize vectors: INT8 gives 4x compression with <1% recall loss [14]. (4) Tiered serving: top 10% items (by traffic) in fast HNSW, rest in IVF-PQ on SSD.

**Hard follow-up:** HNSW for 100M items at 768-dim FP32 requires ~300GB. How do you handle this?

> Scalar quantization (INT8) reduces to 75GB with <1% recall loss. Product quantization compresses to 6-12GB with 5-10% recall loss (recoverable with reranker). Alternatively, shard across machines or use tiered storage — hot tier HNSW (top 10M), cold tier IVF-PQ [14] (remaining 90M).

---

### Q9: When should you use online interleaving experiments vs standard A/B testing?

> **Quick answer:** Interleaving [11] measures retrieval quality directly by mixing results from two systems in the same list, requiring 10x less traffic than A/B testing to reach statistical significance. Use it for ranking/retrieval changes; use A/B for UI or feature changes.

Interleaving [11]: present results from system A and system B alternately in a single result list. Users click based on relevance without position confounds (both systems get equal exposure). The system whose results receive more clicks wins. Chapelle et al. demonstrated this requires only 10% of A/B test traffic for equivalent statistical power [11].

When to use interleaving: retrieval algorithm changes, fusion parameter tuning, reranker model swaps — any change that only affects result ordering. When NOT to use: UI layout changes, new features (no baseline to interleave against), or changes that affect result presentation.

**Hard follow-up:** Your CTR improved 5% after a retrieval change, but you can't isolate whether it's better retrieval or just more attractive items surfaced. How?

> Interleaving eliminates this confound because both systems get equal position exposure. If you only have A/B data, control for item attractiveness by computing CTR conditioned on the item being shown (not its position). Items that appear in both conditions provide a natural control.

---

### Q10: How do you build a retrieval system from scratch — in what order?

> **Quick answer:** Phase 1: BM25 + eval foundation → Phase 2: dense retrieval + hybrid fusion → Phase 3: reranking + query understanding → Phase 4: fine-tuning and online optimization.

| Phase | Timeline | What | Why |
|---|---|---|---|
| 1 | Week 1-2 | BM25 [1] + basic query processing + labeled eval set | Working search handling 60-70% of queries; eval baseline before adding complexity |
| 2 | Month 2 | Dense retrieval [2][8] + RRF fusion [12] | Measure semantic improvement; only keep if hybrid improves recall by >5% on semantic queries |
| 3 | Month 3 | Cross-encoder reranker [4] + intent classification | Precision improvement on top-K; conditional processing by query type |
| 4 | Month 4+ | Embedding fine-tuning [9], SPLADE [3], A/B testing [11] | Domain adaptation based on production signals |

The evaluation foundation (Phase 1) is non-negotiable — without 200+ labeled query-document pairs, you cannot measure whether subsequent additions actually help.

**Hard follow-up:** At Phase 2, hybrid retrieval only improves recall by 3% over BM25 alone. Worth the complexity?

> Slice by query type. If semantic queries improved 20% while exact-match stayed flat, the 3% aggregate hides real value on a growing segment. Calculate: 3% more relevant results at $0.10/result on 1M queries/day = ~$1M/year. Compare against vector DB + embedding pipeline infrastructure cost to decide.

---

### Q11: How do you use implicit feedback (clicks, purchases) to improve retrieval?

> **Quick answer:** Clicks (noisy, position-biased) train ranking with IPW correction; purchases (strong signal, delayed) provide the strongest positive pairs for embedding fine-tuning; query refinements signal retrieval failure on the original query.

| Signal | Noise Level | Use Case | Key Correction |
|---|---|---|---|
| Click | High (position bias) | Ranking features, embedding fine-tuning | IPW by position |
| Purchase/conversion | Low | Strongest positive training pair | Weight 5-10x vs clicks |
| Skip (shown, not clicked) | Medium | Weak negative signal | Only use with high impression count |
| Query refinement | Low | Negative signal for original results | Map to coverage gaps |
| Dwell time | Medium | Weight clicks (long dwell > short) | Normalize by content length |

Feedback loop: retrieval → user sees results → user acts → signal fed back to improve retrieval. The flywheel compounds: better retrieval → more relevant clicks → better training data → better retrieval.

**Hard follow-up:** You've improved retrieval with click feedback for 6 months. How do you detect filter bubble formation?

> Monitor catalog coverage (% of items retrieved in any query per month) and novelty rate (% of results user hasn't seen before). If either declines, enforce diversity constraints and compare quality on a fresh eval set (new queries, new items) vs production eval set. Degradation on fresh data while production metrics improve indicates overfitting to historical patterns.

---

### Q12: What is HyDE and when does it help vs hurt retrieval?

> **Quick answer:** HyDE (Hypothetical Document Embeddings) uses an LLM to generate an ideal answer to the query, then embeds that answer for retrieval — bridging the query-document representation gap for vague queries but hurting exact-match and navigational queries.

How it works: query "How to sleep better?" → LLM generates a hypothetical ideal document → embed the generated document → search for real documents similar to the hypothetical. The generated document is in "document space" rather than "query space," improving embedding alignment with actual documents [13].

When it helps: vague/short queries, questions that don't share vocabulary with answers, exploratory queries. When it hurts: navigational queries ("B0CXYZ123"), exact-match queries, and keyword queries where the user knows exactly what they want — the LLM generation adds noise and 100-200ms latency.

**Hard follow-up:** HyDE adds 200ms latency per query. How do you make it production-viable?

> Route selectively: classify queries as navigational/exact vs exploratory. Only apply HyDE to exploratory queries with low initial retrieval confidence (BM25 returns <10 results above threshold). Cache LLM outputs for repeated queries. Alternatively, distill the HyDE pattern into query expansion rules offline.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): SPLADE Term Weighting — Expansion, Compression, and Regularization</strong></summary>

SPLADE [3] produces sparse representations over the full vocabulary |V| (~30K tokens) for each document and query. The mechanism:

```
For token position i in document d:
  h_i = BERT(d)[i]                     # contextualized embedding
  w_i = log(1 + ReLU(W_proj * h_i))    # project to |V|-dim, apply log-saturation
  
SPLADE(d)_j = max_i(w_i[j])            # max-pool over positions for each vocab term j
```

The `log(1 + ReLU(x))` activation ensures: (1) non-negativity (required for inverted index), (2) saturation (diminishing returns like BM25's TF saturation [1]), (3) sparsity (ReLU zeros out most terms).

**Sparsity control via L1 regularization:**

```
L_total = L_ranking + lambda_q * ||SPLADE(q)||_1 + lambda_d * ||SPLADE(d)||_1
```

lambda_d controls document sparsity (index size): higher lambda_d → fewer activated terms per document → smaller posting lists → faster retrieval. lambda_q controls query sparsity (search cost): fewer query terms → fewer posting lists accessed. Typical: 100-300 non-zero terms per document out of 30K vocabulary [3].

**Term weighting analysis:** Unlike BM25 where weights are corpus statistics [1], SPLADE learns contextual importance. "Running shoes" assigns high weight to "running" and "shoes" (original terms) AND non-zero weight to "jogging" (0.4), "athletic" (0.3), "sneakers" (0.2). This expansion bridges vocabulary mismatch while maintaining inverted index serving.

**Compression trade-off:** At lambda_d = 0.01, average ~200 non-zero terms, NDCG@10 on MSMARCO: 0.380. At lambda_d = 0.1, average ~50 non-zero terms, NDCG@10: 0.365. The 4% quality drop buys 4x smaller index and proportionally faster retrieval [3].

**Why SPLADE beats BM25 + dense hybrid on efficiency:** Single index, single retrieval pass, single infrastructure. The hybrid requires maintaining two separate systems, two queries per request, and a fusion step. SPLADE achieves ~95% of hybrid quality with half the infrastructure complexity [3].

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): ANN Index Serving — Sharding, Replication, Real-Time Updates</strong></summary>

Serving approximate nearest neighbor search at scale requires solving three simultaneous problems: latency (p99 < 20ms), throughput (>100K QPS), and freshness (new items searchable within minutes) [5][14].

**HNSW vs IVF architecture comparison:**

| Factor | HNSW [5] | IVF-PQ [14] |
|---|---|---|
| Memory/vector (768-dim) | ~3.2KB (full + graph) | ~128 bytes (PQ compressed) |
| 100M vectors memory | ~320GB | ~12.8GB (25x less) |
| Query latency | 1-5ms | 2-10ms |
| Recall@10 | 95-98% | 85-92% |
| Insert cost | O(log N), online | Batch re-cluster periodically |
| Update suitability | Excellent (incremental) | Poor (requires re-partitioning) |

**Sharding strategies:**

1. **Hash-based sharding**: Distribute vectors by ID hash. Scatter-gather: query hits ALL shards, each returns local top-K, coordinator merges. Pro: uniform load. Con: every query hits every shard (fan-out = N_shards).

2. **Cluster-based sharding**: Partition by embedding clusters. Route query to relevant shards only (fan-out = 2-3 shards). Pro: lower fan-out. Con: uneven load, routing errors miss results.

**Real-time updates in HNSW [5]:** HNSW supports O(log N) incremental inserts — new items immediately participate in search. However, graph quality degrades over time (suboptimal neighbor connections). Production pattern: insert new items in real-time for freshness, rebuild the full graph nightly for quality. During rebuild, serve from the old graph (blue-green deployment).

**Replication for throughput:** At 100K QPS with 5ms/query, a single HNSW shard handles ~200 QPS (single-threaded search). For 100K QPS: replicate each shard 500x? No — batch queries and parallelize within shards. With 8 cores per replica and batched search, each replica handles ~1.5K QPS. Need ~70 replicas across all shards [14].

**GPU-accelerated IVF [14]:** FAISS on GPU achieves 5-10x throughput over CPU for IVF-PQ search. At billion-scale, GPU-IVF with 4 A100s handles the same QPS as 200 CPU machines — often more cost-effective at extreme scale.

</details>

<details><summary><strong>DE Probe 3 (DATA): Query Understanding — Intent Classification, Rewriting, Spell Correction</strong></summary>

Query understanding transforms raw user input into structured, actionable retrieval requests. The pipeline runs in <10ms total and typically yields larger quality gains than improving retrieval models.

**Query understanding pipeline:**
```
Raw Query → Spell Correct (3ms) → Entity Detect (3ms) → Intent Classify (2ms) → Rewrite/Expand (conditional, 5-200ms)
```

**Spell correction architecture:** Edit-distance with domain vocabulary boosting. At mobile scale, 30-40% of queries contain typos. System: (1) Build vocabulary from corpus + query logs. (2) For each query term, check if it exists in vocabulary. (3) If not, find candidates within edit distance 2. (4) Rank by: language model probability * domain frequency * edit distance penalty. Critical: never correct entities (brand names, product codes) — maintain an entity whitelist that bypasses correction.

**Intent classification taxonomy:**
- **Navigational** (wants one specific item): route to exact-match, skip expansion
- **Transactional** (wants to buy from a category): full hybrid retrieval + personalization
- **Informational** (wants to learn): semantic retrieval emphasized over lexical

A lightweight classifier (logistic regression on n-gram features) achieves >90% accuracy in <2ms. This enables routing: navigational queries skip expensive expansion/reranking entirely.

**Query rewriting strategies:**
1. **Synonym expansion**: "comfortable shoes" → "comfortable shoes OR ergonomic footwear" — additive, safe
2. **LLM-based rewriting**: Generate N paraphrases, embed each, retrieve union of results — powerful but 100-200ms
3. **Pseudo-relevance feedback**: Retrieve initial results, extract discriminative terms, expand query — classic but can drift

**Guardrails:** Expansion terms are OR conditions (never replace original). If original query returns >50 results above threshold, don't expand (you have sufficient recall). Only expand on low-recall queries. Track expansion-to-CTR: if expanded terms consistently lead to unclicked results, remove them from the expansion model.

> [!experience] At Amazon Ads, entity detection was critical: "B0CXYZ123" must return that exact product with no semantic expansion. Entities bypass the entire expansion pipeline and get exact-match priority — preventing the embarrassing failure of returning a competitor's product.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Offline vs Online Metrics — NDCG, MRR, and Interleaving Experiments</strong></summary>

The evaluation problem in retrieval: offline metrics measure quality on curated queries with known relevance; online metrics measure real user satisfaction on the production distribution. They frequently disagree.

**Offline metrics formulas:**

```
NDCG@K = DCG@K / IDCG@K
DCG@K = sum_{i=1}^{K} (2^{rel_i} - 1) / log2(i+1)

MRR = (1/|Q|) * sum_{q in Q} 1/rank(first_relevant_for_q)

Recall@K = |relevant docs in top-K| / |total relevant docs|
```

NDCG handles graded relevance (0-4 scale), discounts by log-position, and normalizes to [0,1]. MRR only measures the first relevant result — appropriate for navigational queries with one right answer.

**The offline-online gap:** Common scenario: offline NDCG improves 8% but production CTR unchanged — because improvement is on long-tail queries representing 5% of volume. Conversely, offline metrics flat but production improves — because query processing improvements help messy real queries absent from the clean eval set.

**Interleaving experiments [11]:** The gold standard for online retrieval evaluation. Method: (1) For each query, get results from system A and system B. (2) Interleave into a single list (team-draft or balanced interleaving). (3) User clicks indicate preference. (4) System whose results receive more clicks wins.

Statistical power advantage [11]: Interleaving achieves significance with ~10% of A/B test traffic because each query is its own control (both systems get equal exposure). Chapelle et al. validated on large-scale search that interleaving preferences agree with long-term A/B outcomes 90%+ of the time [11].

**Metric selection guide:**

| Use Case | Primary Metric | Secondary | Online Validation |
|---|---|---|---|
| Candidate generation (L0) | Recall@1000 | — | Coverage metrics |
| Reranking (L1) | NDCG@10 | MRR@10 | Interleaving [11] |
| End-to-end quality | NDCG@10 | Zero-result rate | A/B on CTR + conversion |
| Navigational queries | MRR | — | Time-to-click |

**Two eval set strategy:** (1) Clean labeled set — high annotator agreement (kappa=0.85), deterministic regression testing. (2) Production sample — random real queries, refreshed monthly, noisier (kappa=0.72) but predicts online metric movements much better.

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Cross-Encoder Reranking Latency — When to Apply, Distillation, Caching</strong></summary>

Cross-encoder reranking [4] processes each (query, document) pair through full transformer cross-attention, achieving the highest relevance quality but at significant latency cost. The production question is always: how to get cross-encoder quality without cross-encoder latency.

**Latency analysis:** A cross-encoder (e.g., 12-layer BERT [4]) on GPU processes ~500 pairs/second. Reranking 100 candidates = 200ms; reranking 1000 = 2 seconds. For a 50ms latency budget, you can rerank at most 25 candidates — often insufficient for quality.

**When to apply cross-encoder reranking:**
1. **Always apply** when: quality is revenue-critical AND candidate set is small (<200)
2. **Conditionally apply** when: only needed for ambiguous queries (route by confidence score from L0)
3. **Skip** when: latency budget <20ms, OR L0 retrieval systems strongly agree on ranking (high confidence)

**Selective reranking strategy:** Compute agreement score between BM25 and dense top-10. If agreement > 80% (8+ shared items in same order), skip cross-encoder — both systems are confident. If agreement < 40%, cross-encoder is critical for disambiguation. This reduces reranker invocations by 30-50%.

**Distillation to reduce latency [7]:**

```
Teacher: cross-encoder (12-layer, 110M params, 200ms/100 candidates)
Student: bi-encoder with MLP head (6-layer encoder + 2-layer MLP, 15ms/100 candidates)

L_distill = KL(teacher_scores, student_scores) over (query, candidate_set) pairs
```

The student learns the teacher's ranking preferences but scores via dot-product + MLP — pre-computable document representations, 10-15x faster inference. Quality retention: typically 80-90% of teacher's NDCG improvement [7][9].

**Result caching for rerankers:** Cache (query_hash, candidate_set_hash) → reranked_order. At scale, 15-30% of queries are repeated within minutes (head queries). Cache invalidation: TTL-based (5-15 minutes) or trigger on index updates. The cross-encoder result is deterministic given fixed inputs — safe to cache aggressively.

> [!experience] At Amazon Ads, cross-encoder reranking delivered +900 bps relevance improvement because it captures token-level intent alignment ("buy shoes" vs "compare shoes") that dot-product similarity collapses. The 50-100ms budget was justified because it only ran on top-200 candidates.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Multi-Stage Retrieval — L0 Generation → L1 Rerank → L2 Business Logic</strong></summary>

Multi-stage retrieval is the universal production pattern because no single model can optimize for both recall (finding all relevant items from billions) and precision (ordering top-10 perfectly) within a latency budget.

**Stage breakdown:**

```
L0: Candidate Generation (10ms budget)
  Input: full corpus (10M-1B items)
  Output: top-1000 candidates
  Methods: BM25 [1], bi-encoder ANN [2][8], SPLADE [3]
  Optimize for: RECALL@1000 (if relevant item isn't here, it's lost forever)

L1: Reranking (80ms budget)
  Input: top-1000 from L0
  Output: top-50 ranked by relevance
  Methods: cross-encoder [4], ColBERT [6][15], learned ranker with features
  Optimize for: NDCG@10

L2: Business Logic (5ms budget)
  Input: top-50 from L1
  Output: final displayed results
  Methods: diversity constraints, freshness boost, policy filters, personalization
  Optimize for: user satisfaction + business objectives
```

**Why this decomposition is optimal:** Each stage applies progressively more expensive computation to a progressively smaller candidate set. The total compute is: O(N * cheap) + O(1000 * medium) + O(50 * expensive) — far less than applying expensive ranking to all N items.

**Critical property — recall is ceiling:** L1 can only reorder items from L0's output. If L0 misses a relevant document, no amount of reranking recovers it. This is why L0 optimizes for recall (cast a wide net) while L1 optimizes for precision (order correctly). Monitoring L0 recall@1000 is the single most important retrieval metric.

**Multi-retriever L0 with fusion:** Run BM25 and dense ANN in parallel (both <15ms), fuse via RRF [12] to form the candidate set. This is strictly better than either alone because failure modes are complementary. The fusion step adds <1ms (simple rank merge).

**L2 business logic examples:** (1) Diversity — max 3 results per brand/category. (2) Freshness — boost items added in last 24h. (3) Policy — suppress out-of-stock, age-restricted, or geo-blocked items. (4) Personalization — boost items aligned with user history. These rules override L1 ranking when business requirements trump pure relevance.

**Latency budget allocation:** Total SLA of 100ms forces hard choices. If query understanding takes 10ms and L0 takes 15ms, L1 gets at most 70ms. With cross-encoder at 200ms/100-candidates, you can only rerank top-35 in budget. Solution: distilled reranker [7] at 15ms/100-candidates, enabling top-200 reranking within budget.

</details>

## Cost Model

### Per-Query Cost Breakdown

| Component | Cost/Query | Assumptions | Optimization |
|-----------|-----------|-------------|--------------|
| Query processing (spell, entity, classify) | ~$0 | CPU-only, <5ms | None needed |
| BM25 retrieval | $0.00001 | Self-hosted Elasticsearch, sharded | Infra cost only |
| Dense ANN retrieval [5][14] | $0.00005 | HNSW over 10M items | Quantization, tiered index |
| RRF fusion [12] | ~$0 | CPU merge, <1ms | None needed |
| Cross-encoder reranking (top-100) [4] | $0.001 | Self-hosted GPU, bge-reranker | Reduce to top-50; distill model |
| LLM query expansion (selective) | $0.003 | Haiku-class call, only on low-recall | Apply only when <10 results |

### Monthly Cost at Scale

| Scale | Queries/Day | Monthly Cost | Cost/Query |
|-------|------------|-------------|------------|
| BM25 only | 50M | ~$15K (infra) | $0.00001 |
| + Dense retrieval | 50M | ~$30K | $0.00006 |
| + Cross-encoder reranker | 50M | ~$80K | $0.001 |
| + Selective LLM expansion (10%) | 50M | ~$95K | $0.001 avg |

### Cost Optimization Priority Stack

| Priority | Optimization | Estimated Savings |
|----------|-------------|-------------------|
| 1 | Tiered index: HNSW hot, IVF-PQ cold [14] | 60-80% memory |
| 2 | Selective reranking (skip on high-confidence) | 30-50% GPU cost |
| 3 | Query result caching (15-30% hit rate) | 15-30% compute |
| 4 | Model distillation (cross-encoder → bi-encoder+MLP) [7] | 80-90% reranker cost |
| 5 | INT8 quantization for HNSW vectors | 75% memory |

### Build vs Buy

| Capability | Build | Buy Option | Recommendation |
|-----------|-------|------------|----------------|
| Inverted index (BM25) | Self-hosted ES ($500/mo) | Elastic Cloud ($2K+/mo) | Self-host at scale |
| Vector DB | FAISS/pgvector (compute only) | Pinecone ($70/mo per 1M vecs) | Managed if <10M; self-host above |
| Embedding model | Self-hosted sentence-transformers [8] | OpenAI/Cohere embedding API | Self-host (latency-critical, high volume) |
| Cross-encoder reranker [4] | Self-hosted on GPU | Cohere Rerank API | Self-host for latency control |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Zero-result rate | >3% (baseline 1.5%) | Retrieval team: coverage gap or index failure |
| Search abandonment | >25% (baseline 18%) | Quality team: results unsatisfying |
| BM25 recall@10 (golden set) | <75% (baseline 82%) | Index team: tokenization or freshness issue |
| Dense recall@10 (golden set) | <80% (baseline 88%) | ML team: model drift or index corruption |
| Hybrid lift over best-single | <3% (baseline 8%) | Investigate: one system degraded? fusion broken? |
| Reranker NDCG lift | <5% (baseline 12%) | Reranker not adding value — check model, candidates |
| Query latency p99 | >100ms (SLA: 50ms) | Infra: index health, reranker queue, cache miss |
| Embedding index freshness | >2 hours (target: <1h) | Pipeline: indexing delay or failure |

### Debugging Walkthrough

```
Symptom: Users searching "wireless earbuds ANC" get non-ANC results
├── Step 1: Check BM25 → returns ANC products correctly (term "ANC" in titles)
├── Step 2: Check dense → returns generic earbuds, NOT ANC-specific
│   Root cause: "ANC" is OOV for embedding model, no learned semantics
├── Step 3: Check fusion → ANC products get BM25 score only, generic get BOTH → generic ranks higher
└── Fix:
    ├── Short-term: Add "ANC" → "Active Noise Cancellation" to synonym dictionary
    ├── Medium-term: Fine-tune embeddings with domain abbreviation pairs
    └── Long-term: SPLADE [3] learns expansion automatically
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| BM25 index | Alias swap to previous build | Instant, zero downtime |
| Dense index + embedding model | Alias swap; reindex for model change (hours) | Minutes (alias) or hours (reindex) |
| Cross-encoder reranker [4] | Route to previous model version | Seconds (config change) |
| Query processing config | Config rollback (instant) | Seconds |
| RRF parameters [12] | Config rollback | Seconds |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Click on result | Engagement relevance (noisy: position bias) | Click logger with position tracking |
| Zero-result query | Coverage gap — no good match exists | Query-level monitoring |
| Query refinement | First results unsatisfactory | Session analysis |
| Purchase from search | Strongest relevance signal | Attribution pipeline |
| Dwell time (long vs short) | Content quality proxy post-click | Page instrumentation |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Real-time | Synonym dictionary (new abbreviations) | Spot-check: does new synonym improve results? |
| Daily | Query processing rules, spell correction | Zero-result rate <= previous day |
| Weekly | BM25 index rebuild (fresh content) | Recall@10 on golden set >= previous |
| Bi-weekly | Embedding fine-tuning on click/purchase pairs [9] | Recall@10 improvement on golden set |
| Monthly | Cross-encoder retrain [4] | NDCG improvement + 1-week online A/B |
| Quarterly | Embedding model replacement | Full reindex + regression suite + 2-week interleaving [11] |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Hybrid BM25 + Dense + RRF [12] | Complementary failure modes | Production systems with diverse queries | Tiny corpora (<1K items) |
| SPLADE learned sparse [3] | Semantic matching on inverted index | Want single index, interpretability | Cross-lingual retrieval |
| Cross-encoder reranking [4] | Fine-grained relevance precision | Quality-critical, <200 candidates | Ultra-low latency (<20ms total) |
| ColBERTv2 late interaction [15] | Token-level matching at speed | Moderate latency, >200 candidates | Memory-constrained environments |
| HyDE (hypothetical document) | Vague queries with poor embeddings | Exploratory/question queries | Navigational/exact-match queries |
| Query classification + routing | Different strategies per intent | Diverse query patterns | Homogeneous query types |
| Tiered index (HNSW + IVF-PQ) [5][14] | Memory constraints at scale | >50M items, memory-limited | Small corpus fitting single machine |
| Interleaving experiments [11] | Measure ranking quality directly | Retrieval/ranking changes | UI or feature changes |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|----------------|----------------------|
| "We use vector search for retrieval" | "We use hybrid — pure dense misses exact codes/IDs [1]. BM25 catches what embeddings miss; complementary failure modes justify both systems." |
| "We use the top MTEB model" | "We evaluate on production queries — MTEB #1 was #4 on our domain. Fine-tuning on real messy queries closed a 12% recall gap [8][9]." |
| "We added a cross-encoder reranker" | "Cross-encoder [4] earned its 80ms budget because it captures intent-level distinctions (buy vs compare) that dot-product collapses." |
| "We optimize for recall@10" | "Recall@10 is offline; CTR and conversion are what matter. 8% offline improvement translated to zero online lift because it was on long-tail queries [11]." |
| "We use HNSW for our vector index" | "HNSW [5] for hot tier (top 10% by traffic), IVF-PQ [14] for long tail — 95%+ effective recall at 1/10th memory." |
| "We A/B test retrieval changes" | "Interleaving [11] needs 10x less traffic and directly measures retrieval quality without position confounds." |
| "We measure quality on our eval set" | "Two eval sets: clean labeled for regression, production sample refreshed monthly for realistic quality assessment." |

## References

### Foundational Papers

- [1] Robertson & Zaragoza (2009) — *The Probabilistic Relevance Framework: BM25 and Beyond* — Foundations and Trends in IR — Definitive reference for BM25 derivation from the probabilistic relevance framework.
- [2] Karpukhin et al. (2020) — *Dense Passage Retrieval for Open-Domain Question Answering* — arXiv:2004.04906 — Established dense bi-encoder retrieval as competitive with BM25 for open-domain QA.
- [3] Formal et al. (2021) — *SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking* — arXiv:2107.05720 — Learned sparse representations achieving semantic matching on inverted index infrastructure.
- [4] Nogueira & Cho (2019) — *Passage Re-ranking with BERT* — arXiv:1901.04085 — First demonstration of cross-encoder reranking with transformers; established the bi-encoder → cross-encoder pipeline.
- [5] Malkov & Yashunin (2018) — *Efficient and Robust Approximate Nearest Neighbor using Hierarchical Navigable Small World Graphs* — arXiv:1603.09320 — HNSW algorithm; the standard for in-memory ANN search.
- [6] Khattab & Zaharia (2020) — *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction* — arXiv:2004.12832 — Late interaction model bridging bi-encoder efficiency and cross-encoder quality.

### Frameworks & Implementation

- [8] Reimers & Gurevych (2019) — *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks* — arXiv:1908.10084 — Made BERT practical for similarity search via siamese fine-tuning.
- [14] Johnson et al. (2019) — *Billion-scale similarity search with GPUs* — arXiv:1702.08734 — FAISS library; IVF-PQ and GPU-accelerated ANN at billion scale.
- [15] Santhanam et al. (2022) — *ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction* — arXiv:2112.01488 — Residual compression reduces ColBERT storage 6-10x with minimal quality loss.

### Evaluation & Experimentation

- [11] Chapelle et al. (2012) — *Large-scale Validation and Analysis of Interleaved Search Evaluation* — TOIS — Proved interleaving requires 10x less traffic than A/B testing for ranking experiments.
- [12] Cormack et al. (2009) — *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods* — SIGIR 2009 — Introduced RRF; standard fusion for hybrid retrieval.

### Surveys & Training

- [7] Lin et al. (2021) — *Pretrained Transformers for Text Ranking: BERT and Beyond* — arXiv:2010.06467 — Comprehensive survey of transformer-based ranking methods and distillation.
- [9] Hofstatter et al. (2021) — *Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling* — arXiv:2104.06967 — TAS-B training produces competitive bi-encoders via balanced sampling.
- [10] Radford et al. (2021) — *Learning Transferable Visual Models From Natural Language Supervision (CLIP)* — arXiv:2103.00020 — Multimodal contrastive learning; foundation for image-text retrieval.
- [13] Guo et al. (2020) — *Semantic Models for the First-stage Retrieval: A Comprehensive Review* — arXiv:2103.04831 — Survey of semantic retrieval models including dense, sparse, and hybrid approaches.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; enforced length constraints, added Quick Catchup/State of Art, diverse DE probes across 6 categories, 15+ inline citations |
