---
title: "Search Retrieval Ref"
source: "data/researcher/reports/search-retrieval-ref.md"
ingestedAt: "2026-05-17T14:56:54Z"
---
# Search / Query Understanding / Semantic Retrieval — Interview Prep

> **Navigation**: [[#Design Flow Framework]] | [[#Full System Design Walkthrough (Principal/Director Level, ~4 min)|Full System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]


## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Query types (keyword, NL, voice, mixed)? Corpus type (products, docs, entities)? Relevance definition? Exact vs semantic? | Is this a search engine, a retrieval layer for downstream ranking, or a semantic matching system? |
| 2. Identify constraints | Ambiguity, vocabulary mismatch, scale, latency, domain jargon, acronyms/typos | Pure semantic misses exact terms; pure lexical misses intent. What's the failure cost? |
| 3. Propose baseline | BM25 / lexical retrieval + simple reranker | Surprisingly strong baseline. Prove it isn't enough before adding complexity. |
| 4. Identify gaps | Lexical fails on paraphrases, dense fails on exact entities, query ambiguity, lost intent in short queries | Systematic failure diagnosis: vocabulary mismatch vs intent mismatch vs coverage gap |
| 5. Introduce improvements | Hybrid sparse+dense, query rewriting/expansion, metadata filters, entity preservation, cross-encoder reranking, learned representations | Each fix targets a specific retrieval failure mode |
| 6. Add evaluation + guardrails | Recall, MRR, NDCG, zero-result rate, click-based relevance, human review for edge cases, slice analysis | Offline metrics are necessary; online A/B is authoritative |
| 7. Discuss scaling tradeoffs | Hybrid adds complexity, rewriting can distort intent, reranking adds latency, freshness vs index stability | The architecture must serve 300M+ MAU at <100ms — every component earns its place |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## Full System Design Walkthrough (Principal/Director Level, ~4 min)

### Opening Frame (10s)

"Search and retrieval is the foundation that every other AI system stands on — RAG, recommendations, agents, content matching. Get retrieval wrong and everything downstream fails. From 12+ years building retrieval systems at Yahoo Labs and Amazon Ads — from FTRL click prediction at 100% query-ad coverage to cross-attention relevance models at +900 bps to zero-shot retrieval across 19 locales — the consistent lesson is: hybrid retrieval is non-negotiable for production. Pure semantic misses exact terms. Pure lexical misses intent. The question is how to combine them, not whether to."
### 1. Clarify Requirements

Before designing anything, I'd ask:

- **Query types**: Keywords ("nike air max 90"), natural language ("comfortable shoes for standing all day"), voice (transcription errors, conversational), mixed intent ("nike shoes under $100 near me")? Each requires different processing.
- **Corpus type**: Products (structured attributes + descriptions), documents (long-form unstructured), entities (knowledge graph nodes), logs/code (domain-specific syntax)? Corpus structure determines chunking and indexing strategy.
- **Relevance definition**: Exact match (user searches product SKU → must return that exact product), semantic match (user describes a need → return relevant items), or both? Ads search requires both: "B0CXYZ123" must exact-match the ASIN, "comfortable work shoes" must semantic-match.
- **Latency budget**: <20ms (autocomplete), <50ms (search results), <200ms (secondary retrieval for RAG/recommendations)? This determines whether cross-encoders, query expansion, or LLM processing are feasible.
- **Scale**: 10K documents (brute-force works), 10M items (need ANN indexing), 1B+ (need sharding and sophisticated index management)?
- **Freshness**: How quickly must new/updated items be searchable? Real-time (<1 min), near-real-time (<1 hour), batch (daily)?

**Principal signal**: Frame retrieval as a BUSINESS problem, not a ranking problem. "The cost of a missed retrieval in ads is lost revenue — an advertiser's product exists but the system can't find it. The cost of an irrelevant retrieval is wasted impression budget."

### 2. Identify Constraints

- **Vocabulary mismatch**: Users say "sneakers," catalog says "athletic footwear." Users type "ML," your docs use "machine learning." This is THE fundamental search problem — bridging the vocabulary gap.
- **Query ambiguity**: "Apple" = company? fruit? "Java" = programming language? island? coffee? Short queries are especially ambiguous.
- **Domain-specific terminology**: Ads domain: ASINs, campaign IDs, bid types, match types. Every domain has jargon, acronyms, and codes that generic models don't understand.
- **Typos and noise**: Users misspell ("runing shoes"), use abbreviations ("ML sys design"), or include irrelevant tokens ("um, I need shoes for running"). The system must be robust.
- **Scale vs quality**: At 10M+ items, you can't run a cross-encoder on every candidate. You need fast approximate retrieval followed by precise scoring.
- **Cold-start items**: New items with no behavioral data must still be discoverable from day one.

> [!experience] At Amazon Ads, the vocabulary mismatch problem was extreme. Advertisers think in product terms ("running shoes"), shoppers search in intent terms ("shoes for marathon training"), and the system needs to bridge both. Product codes (ASINs like "B0CXYZ123") are high-precision queries that embeddings completely fail on — BM25 catches them trivially. This is why hybrid retrieval was non-negotiable for us.

**Risk framing**: (P0) Business: missed retrieval = lost revenue (advertiser product exists, system can't find it) | (P1) Technical: vocabulary mismatch is an open problem even with LLMs | (P2) Org: search team owns retrieval, ranking team owns scoring — misalignment on what "recall" means

### 3. Propose Baseline (BM25 + Reranker)

**Architecture:**

```
┌──────────────────────────────────────────────────────────────────────┐
│  SEARCH PIPELINE (Baseline)                                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │ Query        │───▶│ BM25 Index   │───▶│ Lightweight  │──▶ Top-K  │
│  │ Processing   │    │ (Inverted    │    │ Reranker     │   Results │
│  │ [<5ms]       │    │  Index)      │    │ [10-50ms]    │           │
│  │              │    │ [5-20ms]     │    │              │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│       │                                                               │
│  Tokenization,                                                        │
│  lowercasing,                                                         │
│  stop words,                                                          │
│  spell correction                                                     │
│                                                                       │
│  ┌──────────────────────────────────────────────────┐               │
│  │  Offline: Index Construction                      │               │
│  │  Documents → Tokenize → Build inverted index      │               │
│  │  (term → document_ids + term frequencies)         │               │
│  └──────────────────────────────────────────────────┘               │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Query processing**: Tokenization, lowercasing, stop word removal, basic spell correction. Prepare the query for lexical matching.
- **BM25 retrieval**: Term-frequency-based scoring with document length normalization. Fast (inverted index lookup), precise for exact matches, no training needed.
- **Lightweight reranker**: Simple feature-based model (GBDT or shallow DNN) on top-100. Features: BM25 score, query-document overlap, item popularity, freshness. Improves precision without heavy computation.

**BM25 scoring**:
```
BM25(q, d) = Σ_{t ∈ q} IDF(t) × (tf(t,d) × (k₁+1)) / (tf(t,d) + k₁ × (1 - b + b × |d|/avgdl))

where: IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))
       k₁ ≈ 1.2, b ≈ 0.75 (standard tuning)
```

**Why start here**: BM25 is surprisingly strong. It's fast, requires no training, handles exact matches perfectly, and is well-understood. Many teams skip BM25 and go straight to dense retrieval — then spend months debugging why product codes and acronyms don't work. Start with BM25, measure where it fails, then add dense retrieval for those specific failure modes.

**Design choice**: BM25 baseline over dense-only baseline
- **Pros**: Fast (<10ms), no training needed, perfect for exact matches (product codes, names), interpretable (you can see WHY a document was retrieved)
- **Cons**: Misses paraphrases and semantic similarity, no concept of "meaning" — purely lexical matching
- **Why chosen**: In enterprise/ads search, 40-60% of queries contain exact terms (product names, codes, category names) that BM25 handles perfectly. Build the semantic layer on top, not instead of.
- **Alternative considered**: Dense-only (embedding similarity) — works for semantic queries but silently fails on exact matches. Harder to debug.

> [!experience] At Yahoo Labs, I built distributed online learning models (FTRL) for click prediction achieving 100% query-ad pair coverage. The retrieval layer underneath was BM25-based. Even with sophisticated ranking on top, the quality of the initial retrieval set determined the ceiling of the entire system. A great ranker can't fix a retrieval miss.

### 4. Identify Gaps (Where Baseline Fails)

| Failure Mode | Symptom | Root Cause |
|---|---|---|
| **Semantic mismatch** | "Comfortable standing shoes" → no results (catalog has "ergonomic footwear") | BM25 can't bridge vocabulary gap — different words, same meaning |
| **Short/ambiguous queries** | "Apple" → mixes products, company info, recipes | No intent disambiguation; BM25 treats all tokens equally |
| **Paraphrase blindness** | "ML pipeline" and "machine learning workflow" return different results | No semantic understanding — these are the same concept |
| **Entity-only queries** | "B0CXYZ123" → works perfectly (BM25 strength) | Not a gap — this is where BM25 excels. Keep it. |
| **Long-tail queries** | Rare/niche queries with few matching documents | Sparse term overlap between niche query and relevant documents |
| **Cross-lingual queries** | Query in English, relevant document in German | BM25 is language-specific; no cross-lingual capability |
| **Intent evolution** | User refines query across session but search treats each query independently | No session context; each query is independent |

> [!experience] At Amazon Ads, we pushed back when senior leadership wanted full embedding-based retrieval upfront. The data showed: tail-query coverage was sparse with embeddings (rare product codes missed), objectives were under-specified (what does "semantic similarity" mean for an ad keyword?), and we risked building a powerful system advertisers didn't trust. We proposed a phased approach: BM25 for head queries (high signal), add semantic retrieval for torso/tail only after ROI was proven. This was the right call — head queries got immediate value while we invested in getting semantic retrieval right.

### 5. Introduce Improvements

#### 5a. Hybrid Retrieval (Sparse + Dense)

The core improvement: combine lexical (BM25) and semantic (embedding) retrieval.

**Improved Architecture:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HYBRID SEARCH PIPELINE                                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────┐                                                        │
│  │ Query        │                                                        │
│  │ Processing   │                                                        │
│  └──────┬───────┘                                                        │
│         │                                                                 │
│    ┌────┴────┐                                                           │
│    ▼         ▼                                                           │
│  ┌──────┐  ┌──────────┐                                                 │
│  │ BM25 │  │ Dense    │                                                 │
│  │[5ms] │  │ ANN      │                                                 │
│  │      │  │[10-20ms] │                                                 │
│  └──┬───┘  └───┬──────┘                                                 │
│     │          │                                                          │
│     └────┬─────┘                                                          │
│          ▼                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ Fusion (RRF) │───▶│ Cross-Encoder│───▶│ Business     │──▶ Results   │
│  │ [<1ms]       │    │ Reranker     │    │ Rules        │               │
│  │              │    │ [50-200ms]   │    │ [<5ms]       │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

**Fusion strategy — Reciprocal Rank Fusion (RRF)**:
```
RRF_score(d) = Σ_r 1 / (k + rank_r(d))

where r = each retrieval system (BM25, dense), k = 60 (standard constant)
```

RRF is robust, requires no tuning, and outperforms learned fusion in most settings.

> [!experience] At Amazon Ads, hybrid retrieval was non-negotiable. Our targeting expansion algorithm combined BM25 (for exact product/keyword matches) with semantic retrieval (for intent-level expansion). The hybrid approach expanded recommendation coverage by +2200 bps while maintaining relevance — neither BM25 alone nor dense retrieval alone achieved this.

**Risk framing**: (P0) Business: missed retrieval = lost revenue (advertiser's relevant product not shown) | (P1) Technical: dual index maintenance, fusion weight tuning, embedding model updates require reindexing | (P2) Org: search infra team must support both index types

#### 5b. Cross-Encoder Reranking

After hybrid retrieval returns top-100, apply a cross-encoder reranker for precision:

- **Bi-encoder** (retrieval): Encodes query and document independently → dot product. Fast but misses fine-grained interaction.
- **Cross-encoder** (reranking): Encodes [query; SEP; document] jointly → full cross-attention. Captures token-level alignment ("comfortable" in query aligns with "cushioned" in document). 20-30% NDCG improvement over bi-encoder.

> [!experience] At Amazon Ads, we developed deep learning similarity models using cross-attention architectures achieving +900 bps relevance improvement over baseline semantic retrieval. The key: two-tower (bi-encoder) models compute query and item independently, losing fine-grained interaction. Cross-attention captures that "buy running shoes" and "review running shoes" are very different intents for the same product — which matters enormously for ad relevance where intent precision determines advertiser ROI.

**Design choice**: Cross-encoder reranking on top-100, not full cross-attention retrieval
- **Pros**: Captures fine-grained semantic fit; bounded latency (100 forward passes); highest single-component quality improvement
- **Cons**: +50-200ms latency; can't precompute (must run at query time); O(K) per query
- **Why chosen**: Cross-encoder quality improvement (+900 bps in our case) justifies latency cost on a reduced candidate set. Applying to all candidates is computationally infeasible.
- **Alternative considered**: ColBERT (late interaction) — compromise between two-tower and cross-encoder. Pre-computes token embeddings, scores via MaxSim. 100x storage increase but faster than cross-encoder. Use when latency budget is tighter.

#### 5c. Query Understanding

Process the query BEFORE retrieval to improve recall:

- **Query rewriting**: Expand ambiguous queries. "Comfortable shoes" → "comfortable shoes ergonomic footwear cushioned standing all day." Use LLM or trained seq2seq model.
- **Query classification**: Classify intent (navigational, transactional, informational) to route to different retrieval strategies. Navigational → exact match priority. Transactional → semantic + behavioral. Informational → broad semantic.
- **Entity recognition**: Detect product names, brands, codes in the query. Preserve them for exact matching even if the query also has semantic components. "Nike Air Max size 10" → entity: "Nike Air Max", attribute: "size 10", intent: purchase.
- **Spell correction**: "runing shoes" → "running shoes." Critical for mobile queries (40%+ have typos on mobile).
- **HyDE (Hypothetical Document Embeddings)**: For vague queries, generate a hypothetical ideal answer using an LLM, embed that, and use it for retrieval. Bridges the gap between query language and document language.

**Risk framing**: (P0) Business: query rewriting that distorts intent → irrelevant results → user frustration | (P1) Technical: LLM-based rewriting adds 200-500ms latency | (P2) Org: query understanding team must coordinate with retrieval team on rewrite quality

#### 5d. Learned Sparse Representations (SPLADE)

An alternative to dense embeddings: learn SPARSE representations that maintain the efficiency of inverted index lookup while capturing semantic meaning:

```
SPLADE: For each token in the document, predict which vocabulary terms it should activate (and with what weight).

"Comfortable walking shoes" → activates: comfortable(0.8), ergonomic(0.4), footwear(0.6), walking(0.9), cushioned(0.3)

This is stored in an inverted index (like BM25) but the activated terms include SEMANTICALLY RELATED terms, not just literal tokens.
```

**Advantages over dense retrieval**: Uses standard inverted index infrastructure (Elasticsearch, Lucene). No vector database needed. Exact match capability preserved. Faster than ANN for most corpus sizes.

#### 5e. Zero-Shot Cross-Lingual Retrieval

For multi-locale search without per-locale training data:

- **Multilingual embedding models**: Models like mE5, multilingual-e5-large encode queries and documents in any language into the same embedding space. A query in Japanese and a document in English map to nearby points if semantically related.
- **Cross-lingual BM25 with translation**: Translate the query to the document language before BM25 retrieval. Simple but effective for high-resource language pairs.
- **Language-agnostic SPLADE**: Train SPLADE on multilingual data — each document activates vocabulary terms across languages.

> [!experience] At Amazon Ads, we scaled retrieval to 19+ locales using zero-shot transfer. Key finding: zero-shot worked surprisingly well for EU markets because advertisers cross-sell across locales — the same product has descriptions in multiple languages, and advertiser behavior patterns transferred. For JP and KSA Arabic, few-shot adaptation with 10-20 locale-specific examples was required because search behavior diverges significantly from English patterns.

#### 5f. Session-Aware and Personalized Retrieval

For users who search iteratively (query → refine → refine):

- **Session context**: Incorporate previous queries in the session into retrieval. If the user searched "running shoes" then "arch support," the second query means "running shoes with arch support."
- **User preference features**: Encode user purchase history, category preferences, and price sensitivity as additional retrieval features.
- **Diversification across session**: If the user has already seen 10 Nike shoes, diversify subsequent results toward other brands even if the query mentions Nike.

### 6. Evaluation + Guardrails

#### Retrieval-Specific Metrics

| Metric | What It Measures | Why It Matters |
|---|---|---|
| Recall@K | % of relevant items in top-K | Retrieval MUST find relevant items — downstream ranking can't fix misses |
| MRR (Mean Reciprocal Rank) | Average 1/rank of first relevant result | Critical for navigational queries (user wants THE one result) |
| NDCG@K | Ranking quality (graded relevance) | Captures both recall and ranking within retrieved set |
| Zero-result rate | % of queries returning no results | Users who get nothing are lost users |
| Click-through rate (online) | Engagement with retrieved results | Proxy for result relevance in production |
| Query refinement rate | % of users who immediately refine query | High refinement = first results weren't satisfactory |

#### Evaluation by Query Type (slice analysis)

| Query Type | Primary Metric | Why Different |
|---|---|---|
| Navigational ("Nike Air Max 90") | MRR (want exact item at position 1) | Precision matters more than recall |
| Transactional ("buy running shoes") | NDCG@10 (good set of purchase options) | Diversity + relevance matter equally |
| Informational ("best shoes for flat feet") | Recall@20 (comprehensive coverage) | Breadth matters more than precision |
| Entity ("B0CXYZ123") | MRR = 1 or nothing | Binary — exact match or failure |

> [!experience] At Amazon Ads, we evaluated retrieval quality using both offline metrics (recall@K on labeled query-document pairs) and online signals (CTR, adoption rate). The critical finding: offline metrics can look great while online performance suffers — because offline evaluation uses clean queries while production queries have typos, abbreviations, and ambiguity. We maintained a "production query sample" eval set alongside the clean eval set to catch this gap.

#### Guardrails

- **Zero-result fallback**: If no results above threshold, broaden the query (relax filters, expand semantically) rather than return empty. Users who get zero results almost never return.
- **Relevance floor**: Don't return results below a minimum relevance score. Bad results are worse than fewer results.
- **Diversity enforcement**: For informational queries, ensure results span multiple categories/perspectives.
- **Freshness signals**: Show "last updated" timestamps. Flag stale results when freshness matters.

### 7. Scaling Tradeoffs

#### Hybrid Retrieval: Complexity vs Quality

| Approach | Quality | Latency | Infra Complexity |
|---|---|---|---|
| BM25 only | Good for exact, fails on semantic | <10ms | Low (inverted index only) |
| Dense only | Good for semantic, fails on exact | 10-30ms | Medium (vector DB + embedding model) |
| Hybrid (BM25 + Dense + RRF) | Best — covers both | 15-40ms | High (both index types + fusion) |
| Hybrid + cross-encoder reranker | Best precision | 70-250ms | Highest (full stack) |

**Decision**: The quality improvement from hybrid is almost always worth the complexity. The cross-encoder reranker is worth it when latency budget allows (>100ms) and the domain requires fine-grained relevance (ads, e-commerce, legal).

#### Embedding Model Selection

| Factor | Consideration |
|---|---|
| Quality | Evaluate on YOUR data, not MTEB leaderboard. Domain-specific performance varies wildly. |
| Dimensionality | 384-dim is sufficient for most cases. 768-dim adds 2x memory for ~2% recall improvement. |
| Fine-tuning | Domain fine-tuning on query-document pairs from your data: 5-15% recall improvement. Worth it if you have labeled pairs. |
| Multilingual | If serving multiple locales: use multilingual model from the start. Switching later requires full reindex. |

> [!experience] At Amazon Ads, we found that embedding model selection should be validated on production query distributions, not benchmarks. Generic embedding models performed well on "clean" evaluation queries but poorly on production queries with typos, abbreviations, and mixed-language patterns (advertisers mixing English with locale-specific terms). Domain fine-tuning on real production query-item pairs closed a 12% recall gap.

#### Reranking: Quality vs Latency

- 20 candidates × cross-encoder = ~50ms (fast enough for most search)
- 100 candidates × cross-encoder = ~200ms (borderline for real-time search)
- 500 candidates × cross-encoder = ~1000ms (too slow for interactive search; OK for batch)

**Optimization**: (a) Reduce candidate set to top-50 before reranking. (b) Use a smaller cross-encoder (MiniLM vs DeBERTa). (c) Apply selectively — only rerank when initial retrieval scores are ambiguous (high score variance = confident retrieval → skip reranker).

#### Freshness: Index Update Strategy

| Tolerance | Strategy | Complexity |
|---|---|---|
| Daily | Nightly full reindex | Low |
| Hourly | Incremental updates to existing index | Medium |
| Minutes | Streaming updates (CDC → index) | High |
| Seconds | Real-time indexing + cache invalidation | Very high |

> [!experience] At Amazon Ads, freshness was critical for keyword recommendations — stale recommendations waste advertiser budget. We used incremental hourly updates for the main index plus real-time updates for critical fields (bid status, budget status, campaign state). The full reindex ran nightly as a consistency check. This hybrid approach balanced freshness with operational simplicity.
[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

## Interview Q&A Bank

### Q1: Hybrid retrieval — why and how to fuse sparse + dense?

**Principal Answer**: Hybrid retrieval exists because neither sparse nor dense retrieval is sufficient alone, and the failure modes are complementary.

**Sparse (BM25)** excels at: exact matches (product codes, names, IDs), high-frequency terms with strong IDF signal, interpretability (you can see which terms matched and why).

**Dense (embedding ANN)** excels at: semantic matching (paraphrases, related concepts), cross-lingual similarity, understanding query INTENT beyond literal words.

**Failure complementarity**: When BM25 fails (vocabulary mismatch), dense succeeds. When dense fails (exact terms, rare codes), BM25 succeeds. Combining them covers both.

**Fusion methods**:
1. **RRF (Reciprocal Rank Fusion)**: score(d) = 1/(k + rank_BM25(d)) + 1/(k + rank_dense(d)). No training needed. Robust. Standard choice.
2. **Learned fusion**: Train a lightweight model to predict relevance from (BM25_score, dense_score, other features). Better when you have labeled data. Requires training.
3. **Score interpolation**: score = α × BM25_norm(d) + (1-α) × dense_norm(d). Requires normalizing scores to same scale. α is a tunable parameter.

> [!experience] At Amazon Ads, hybrid retrieval was the foundation of our targeting expansion system. BM25 caught product codes, brand names, and advertiser-specific acronyms that embeddings missed entirely. Semantic retrieval caught intent-level matches (organic shopper queries mapped to advertiser keywords) that BM25 couldn't bridge. The combination expanded coverage by +2200 bps — neither system alone came close.

**Hard FUQ**: Your BM25 and dense retrieval return very different candidate sets (only 20% overlap). Is this a problem or a strength?

**Answer**: It depends on WHY. Low overlap + both sets are relevant = strength (each system finds different relevant items, combined recall is high). Low overlap + one set is mostly irrelevant = problem (that system is poorly calibrated for your domain). Diagnose: sample 50 items unique to BM25 and 50 unique to dense. Have humans judge relevance. If both sets are 70%+ relevant, the low overlap is a feature. If one set is <40% relevant, that retrieval path needs fixing (better embeddings, better BM25 tuning, better query processing).

---

### Q2: Cross-attention vs bi-encoder — when and why?

**Principal Answer**: This is the fundamental precision-vs-speed tradeoff in retrieval, and the answer is always "use both in different pipeline stages."

**Bi-encoder (two-tower)**: Encodes query and document independently → dot product similarity. Item embeddings pre-computed → ANN retrieval over millions in <10ms. But: the query and document never "see" each other until the dot product — fine-grained token alignment is impossible.

**Cross-encoder**: Encodes [query; SEP; document] jointly → full transformer cross-attention between query and document tokens. Captures: "comfortable" in query aligns with "cushioned" in document, "running" disambiguates "shoes" differently than "dress." But: requires a forward pass per (query, document) pair → can't pre-compute, can't use ANN.

> [!experience] At Amazon Ads, we achieved +900 bps relevance improvement by moving from two-tower to cross-attention scoring on the reduced candidate set. The improvement was specifically because ad intent is fine-grained: "buy Nike running shoes" and "compare Nike running shoes" are very different for the advertiser, and the two-tower dot product collapses them. Cross-attention distinguishes them because the model can attend to "buy" vs "compare" in the context of each product description.

**Production architecture**: Bi-encoder for recall (retrieve 1000 candidates from millions, <10ms). Cross-encoder for precision (rerank top-100 to top-10, 50-200ms). Each model does what it's best at.

**Hard FUQ**: ColBERT (late interaction) sits between bi-encoder and cross-encoder. When would you choose it over either?

**Answer**: ColBERT computes per-token embeddings for both query and document independently (like bi-encoder) then scores via MaxSim: for each query token, find the max-similarity document token, sum across query tokens. It captures token-level alignment (like cross-encoder) but allows pre-computing document token embeddings (like bi-encoder). Trade-offs: 100x more storage than bi-encoder (token-level vs pooled embeddings), but 100x faster than cross-encoder at query time. Choose ColBERT when: latency budget is tight (<50ms for reranking), you need token-level quality, and storage is cheap. We evaluated ColBERT at Amazon Ads — quality was within 2-3% of full cross-attention but the 100x storage increase at our scale (hundreds of millions of items) made it impractical. Cross-attention on a smaller candidate set was more cost-effective.

---

### Q3: Query understanding — classification, rewriting, expansion

**Principal Answer**: Query understanding is the most underinvested component of search systems. Most teams build sophisticated retrieval and ranking but feed them raw, ambiguous queries. Processing the query before retrieval often yields larger improvements than improving retrieval itself.

**Query understanding pipeline**:
```
Raw Query → Spell Correct → Entity Detect → Intent Classify → Rewrite/Expand → Retrieval
```

1. **Spell correction** (<5ms): "runing shoes" → "running shoes." Critical for mobile (40%+ typo rate). Use edit-distance with domain vocabulary boosting.
2. **Entity detection** (<10ms): Identify product names, brand names, codes. "Nike Air Max 90 size 10" → {brand: Nike, product: Air Max 90, attribute: size 10}. Entities get exact-match treatment in retrieval.
3. **Intent classification** (<5ms): Navigational (wants one specific item), transactional (wants to buy from a category), informational (wants to learn). Routes to different retrieval strategies.
4. **Query rewriting** (10-200ms depending on method): Expand with synonyms, related terms, or LLM-generated paraphrases. "Comfortable standing shoes" → "comfortable standing shoes OR ergonomic footwear OR cushioned work shoes."
5. **Query decomposition** (for complex queries): "Red Nike running shoes under $100 near me" → separate: attribute filter (color=red), brand filter (Nike), category (running shoes), price filter (<$100), location filter.

> [!experience] At Amazon Ads, entity detection was critical: when an advertiser searches for their own ASIN ("B0CXYZ123"), the system MUST return that exact product — no semantic expansion, no fuzzy matching. We preserved entity integrity through the entire pipeline: detected entities bypass semantic expansion and get exact-match priority. This saved us from the embarrassing failure of returning a competitor's product when an advertiser searches for their own.

**Hard FUQ**: Query rewriting adds terms that change the user's intent ("comfortable shoes" gets expanded to "orthopedic shoes" which the user didn't want). How do you prevent this?

**Answer**: Three safeguards: (1) Expansion terms are ADDED as OR conditions, not replacements. The original query terms always have highest weight. (2) Relevance feedback: if expanded terms consistently lead to low-CTR results, downweight or remove them from the expansion model. (3) Conservative expansion: only expand when BM25 recall is below threshold (i.e., the original query doesn't have enough results). If the original query already returns 100+ results, don't expand — you don't need to. Expansion is a RECALL fix, not a precision improvement.

---

### Q4: Handling domain-specific vocabulary (ads terminology, product codes)

**Principal Answer**: Domain-specific vocabulary is the Achilles' heel of generic embedding models and the main reason BM25 remains essential in production search.

**Problem categories**:
1. **Codes/IDs**: ASINs, campaign IDs, SKUs — meaningless strings that BPE tokenizers split into random subwords with no learned semantics.
2. **Acronyms**: CPC, RoAS, CTR, ACOS — domain-standard abbreviations that generic models may not know or may assign wrong meanings.
3. **Jargon**: "Sponsored Products," "match type," "negative keyword" — terms with domain-specific meanings different from general English.
4. **Compound terms**: "auto-targeting," "bid optimization," "budget recommendation" — multi-word concepts that should be treated as units.

**Solutions**:
1. **BM25 as safety net**: All codes, IDs, and exact-match terms route through BM25. This is free — BM25 handles them natively. Never rely on embeddings for exact-match queries.
2. **Domain vocabulary enrichment**: Add domain terms to the tokenizer vocabulary (or use a domain-adapted tokenizer). "RoAS" should be one token, not "R" + "o" + "AS."
3. **Synonym expansion**: Maintain a domain-specific synonym dictionary: {CPC: "cost per click", RoAS: "return on ad spend", SP: "Sponsored Products"}. Expand at query time.
4. **Embedding fine-tuning**: Fine-tune embeddings on domain query-document pairs so the embedding space captures domain-specific similarity (not just general English similarity).

> [!experience] At Amazon Ads, product codes (ASINs) were the highest-precision query type — an advertiser searching their own ASIN expects exact match. Embeddings completely failed on ASINs because BPE splits "B0CXYZ123" into meaningless subword pieces. BM25 handles it trivially (exact string match with high IDF). This single failure mode justified maintaining BM25 alongside dense retrieval for the entire system lifetime.

**Hard FUQ**: You fine-tune embeddings on domain data. But now general queries ("what is machine learning") perform worse because the model over-specialized. How do you balance?

**Answer**: (1) Two embedding models: general-purpose for broad queries, domain-fine-tuned for domain queries. Route by query classification. (2) Mixed fine-tuning: train on 70% domain data + 30% general data to prevent catastrophic forgetting. (3) Adapter-based fine-tuning (LoRA): add domain-specific adapters while keeping the base model frozen. Switch adapters based on query domain classification. In practice at Amazon Ads, we used the adapter approach — domain-specific retrieval quality without losing general-purpose capability.

---

### Q5: Cold-start retrieval for new items/markets (zero-shot)

**Principal Answer**: Cold-start is where semantic retrieval proves its value most clearly — because there's no behavioral data to fall back on.

**Item cold-start** (new product, no clicks/searches):
- **Content embedding**: LLM or embedding model reads the product title + description → generates embedding → product immediately participates in semantic retrieval.
- **Attribute-based retrieval**: Even without embeddings, structured attributes (category, brand, price range) enable rule-based retrieval into relevant candidate pools.
- **Transfer from similar items**: Find the most similar existing items (by embedding distance) and bootstrap: the new item inherits the behavioral features of its nearest neighbors.

**Market cold-start** (new locale, no behavioral data):

> [!experience] At Amazon Ads, we scaled retrieval to 19+ locales using zero-shot and few-shot learning, reducing time-to-market for new markets by 75%. The zero-shot approach: train retrieval models on US data (data-rich), apply directly to new locale. Surprisingly, this worked for EU markets (UK, DE, FR) because advertisers cross-sell across locales — the behavioral patterns transferred. For JP and KSA Arabic where search behavior diverges significantly from English patterns, we needed few-shot adaptation: 10-20 query-document pairs from native speakers to calibrate the model for locale-specific search patterns.

**Phased cold-start strategy**:
1. **Day 0**: Content-based retrieval only (embeddings from descriptions). Quality is mediocre but items are discoverable.
2. **Week 1-4**: Collect initial behavioral signals (impressions, clicks). Start building collaborative features.
3. **Month 1-3**: Enough behavioral data for the ranking model. Transition from content-only to hybrid (content + behavioral).
4. **Month 3+**: Full pipeline equivalent to established markets.

**Hard FUQ**: Your zero-shot model works in Germany but fails in Japan. What's different, and how do you diagnose?

**Answer**: Three likely causes: (1) Linguistic: BPE tokenization of Japanese produces 3-5x more tokens per concept than English/German, degrading embedding quality. Solution: use a multilingual model trained with Japanese data (mE5, multilingual-SBERT). (2) Search behavior: Japanese users search differently — more specific, longer queries, different intent patterns. The US-trained query understanding model misclassifies Japanese intents. Solution: few-shot adaptation of the intent classifier. (3) Cultural: product relevance differs — what "comfortable shoes" means in Japan differs from Germany (different foot shapes, different style preferences, different brands). Solution: locale-specific relevance labels for evaluation and fine-tuning. Diagnose by: slicing retrieval recall by query type (navigational, transactional, informational) × locale. The worst-performing slice tells you where the transfer failed.

---

### Q6: Real-time vs batch retrieval systems

**Principal Answer**: The choice between real-time and batch retrieval depends on query predictability and freshness requirements.

| Dimension | Real-Time Retrieval | Batch Retrieval |
|---|---|---|
| **When** | User types a query → results in <100ms | Pre-compute results for predicted queries nightly |
| **Freshness** | Always current (index is live) | Stale by design (results reflect last batch) |
| **Personalization** | Full (user context available at query time) | Limited (must predict user needs ahead of time) |
| **Cost** | High (compute per query) | Low (amortized over many users) |
| **Coverage** | All queries (including novel ones) | Only predicted/common queries |

**Hybrid architecture** (most production systems):
- **Real-time** for interactive search (user types query, expects immediate results)
- **Batch** for recommendation surfaces (homepage, "you might also like" — can pre-compute)
- **Near-real-time** for trending/breaking items (new product launch must be discoverable within minutes)

> [!experience] At Amazon Ads, we used a hybrid: real-time retrieval for advertiser-initiated search (campaign management, keyword discovery) and batch pre-computation for recommendation surfaces (suggested keywords, opportunity alerts). The batch path served 80% of keyword recommendations because the query space was predictable (product category × advertiser profile = finite combinations). Real-time was reserved for the 20% that was genuinely novel.

**Hard FUQ**: Your batch-computed recommendations become stale for advertisers whose campaigns change rapidly (multiple daily updates). How do you handle this?

**Answer**: Tiered freshness: (1) Batch base: nightly refresh for the full advertiser population. (2) Incremental updates: for advertisers whose campaign state changed since last batch (detected via CDC), re-compute their recommendations in near-real-time (within 1 hour). (3) Real-time fallback: if an advertiser's context has changed SO much that pre-computed results are invalid (new campaign, budget change >50%), fall back to real-time retrieval for that session. Track the "staleness hit rate" — what percentage of served recommendations are from stale batch vs fresh computation. Target: <5% of served results are meaningfully stale.
### Q7: Embedding model selection and fine-tuning for domain search

**Principal Answer**: Embedding model selection is one of the highest-commitment decisions in search — changing the model later requires full reindexing (hours to days of compute, potential quality regression during transition).

**Selection criteria** (in priority order):
1. **Domain performance**: Evaluate on YOUR queries, not MTEB leaderboard. A model that's #1 on MTEB may rank #5 on your domain.
2. **Latency/size**: Smaller models (384-dim) serve 3x faster than larger models (1024-dim) with typically <5% quality loss. Memory scales linearly with dimensions.
3. **Multilingual capability**: If serving multiple locales, choose multilingual from day one. Switching later = full reindex × N locales.
4. **Fine-tunability**: Can you fine-tune on your domain data? Domain fine-tuning typically yields 5-15% recall improvement.

**Fine-tuning strategy**:
- **Data**: Query-document pairs from click logs (positive = clicked, negative = shown but not clicked). Minimum 10K pairs for meaningful improvement.
- **Method**: Contrastive learning with hard negative mining. Fine-tune only the last 2-4 layers (LoRA or adapter-based) to preserve general capability.
- **Validation**: Compare fine-tuned vs base model on held-out labeled query set. Monitor for catastrophic forgetting on general queries.

> [!experience] At Amazon Ads, we found that generic embedding models performed well on "clean" evaluation queries but poorly on production queries with typos, abbreviations, and mixed-language patterns. Domain fine-tuning on real production query-item pairs closed a 12% recall gap. The key: fine-tune on PRODUCTION queries (messy, abbreviated, with typos), not on curated evaluation queries (clean, well-formed). The model needs to learn your users' actual language, not idealized queries.

**Hard FUQ**: You fine-tune on click data, but clicks are position-biased. Won't the embeddings learn position bias too?

**Answer**: Yes — if you fine-tune on raw click data, items shown at position 1 will cluster closer to all queries (because they were clicked more, regardless of relevance). Mitigations: (1) IPW on training pairs: weight each (query, clicked_item) pair by 1/P(examine|position). Items clicked at low positions get higher weight. (2) Use conversion data instead of clicks: conversions are less position-biased (users who convert actively chose the item). (3) Include unbiased negatives: combine biased click pairs with a smaller set of unbiased pairs from randomized traffic.

---

### Q8: Measuring retrieval quality in production (beyond offline metrics)

**Principal Answer**: Offline retrieval metrics (recall, NDCG on labeled sets) are necessary but insufficient. They measure quality on CURATED queries with KNOWN relevance — which doesn't represent the full production distribution.

**Production-specific metrics**:

| Metric | What It Measures | Why Offline Misses It |
|---|---|---|
| Zero-result rate | % of queries with no results above threshold | Offline eval never tests queries that have no good match |
| Query refinement rate | % of users who immediately refine/rephrase | Indicates first results were unsatisfactory |
| Click-through at position K | CTR distribution across positions | Reveals position bias and result quality decay |
| Time to first click | How quickly users find what they want | Efficiency metric; lower = better results |
| Search abandonment | % of searches with no clicks at all | Strongest signal that retrieval failed |
| Downstream conversion | Purchase/adoption rate from search | The only metric that ultimately matters |

**The offline-online gap**: We've seen cases where offline recall improved 8% but production CTR didn't change — because the improvement was on long-tail queries that represent 5% of production volume. And cases where offline metrics were flat but production improved — because query processing improvements helped messy real queries that weren't in the clean eval set.

**Closing the gap**: Maintain TWO eval sets: (1) Clean labeled set for controlled regression testing. (2) Production sample set — random sample of real production queries, labeled by crowd workers, refreshed monthly. The production sample catches failures that the clean set misses.

> [!experience] At Amazon Ads, we maintained both evaluation tracks. The clean eval set had high agreement between annotators (κ=0.85) but missed production patterns like mixed-language queries, truncated mobile queries, and voice-transcribed queries. The production sample set was noisier (κ=0.72) but predicted online metric movements much better. We used the clean set for regression testing (fast, deterministic) and the production sample for quality assessment (realistic, noisy).

**Hard FUQ**: Your production CTR improved 5% after a retrieval change, but you can't tell if it's better retrieval or just showing different items that happen to be more clickable. How do you isolate the retrieval contribution?

**Answer**: Interleaving experiment: show results from both old and new retrieval systems in the same result list (alternating positions). Users click on whichever results they prefer — no position effect because both systems get equal exposure. The preference ratio directly measures retrieval quality improvement. Interleaving requires 10x less traffic than A/B testing to achieve statistical significance, making it ideal for isolating retrieval changes.

---

### Q9: Scaling retrieval to 300M+ users — architecture decisions

**Principal Answer**: Scaling search/retrieval to hundreds of millions of users requires making explicit choices about what's computed per-query vs pre-computed, what's exact vs approximate, and what's real-time vs cached.

**Architecture for 300M+ MAU**:

| Component | Strategy | Latency Budget |
|---|---|---|
| Query processing | Per-query, lightweight (<5ms) | Spell correction, entity detection, intent classification |
| BM25 retrieval | Per-query, sharded inverted index | <10ms with proper sharding (shard by hash) |
| Dense retrieval | Per-query, HNSW ANN over pre-computed embeddings | <20ms with in-memory index |
| Reranking | Per-query, but only on top-K (K=50-100) | <100ms (cross-encoder) or <10ms (lightweight model) |
| User features | Pre-computed (batch, hourly), cached per user | <1ms (cache lookup) |
| Item features | Pre-computed (batch), cached per item | <1ms (cache lookup) |

**Scaling decisions**:

1. **Index sharding**: Shard by document hash for uniform load. Scatter-gather: query hits all shards, each returns local top-K, merge globally. Tradeoff: more shards = lower latency per shard but higher merge cost.

2. **Embedding pre-computation**: ALL item embeddings pre-computed and indexed. NEVER compute item embeddings at query time. Only the query embedding is computed per-request.

3. **Tiered serving**: Hot items (top 10% by traffic) in fast cache. Warm items in in-memory index. Cold items (long tail) in disk-based index with higher latency.

4. **Query caching**: Cache (query_hash → results) for repeated queries. At 300M MAU, many queries are repeated within minutes. Cache hit rate: 15-30% for head queries.

> [!experience] At Amazon Ads, serving 300M+ MAU at <100ms required every component to justify its latency. We pre-computed item embeddings during ingestion, maintained HNSW in-memory for hot locales, and used tiered caching for repeated advertiser queries. The cross-attention reranker (+900 bps) was worth its 50-100ms latency because it only ran on top-200 candidates — not the full corpus.

**Hard FUQ**: Your index has 100M items. HNSW requires all vectors in memory. That's ~300GB for 768-dim FP32. How do you handle this?

**Answer**: Three options, ordered by preference: (1) Scalar quantization (INT8): 4x compression → 75GB. <1% recall loss. This is the default choice. (2) Product quantization: 24-48x compression → 6-12GB. 5-10% recall loss, recoverable with a reranker. (3) Sharding across machines: split index across N machines, each holds a portion. Scatter-gather at query time. (4) Tiered storage: top 10M items (by traffic) in HNSW in-memory. Remaining 90M in IVF-PQ on SSD. Route queries to appropriate tier. Most queries only need the hot tier.

---

### Q10: Personalized retrieval/ranking — when and how?

**Principal Answer**: Personalization in retrieval means: different users searching the same query should get different results based on their history, preferences, and context.

**Personalization layers**:

1. **Query-level** (no personalization): Same results for every user. Simple, cacheable, fair. Use for: navigational queries, entity lookups, new users with no history.

2. **Segment-level**: Different results per user segment (new vs returning, high-value vs low-value, category preference). Moderate personalization, still cacheable per segment.

3. **User-level**: Each user gets individually tailored results. Full personalization, not cacheable. Use for: returning users with rich history.

**How to personalize retrieval** (not just ranking):
- **User embedding**: Encode user history (past clicks, purchases, searches) into a user embedding. Add to query embedding: personalized_query = f(query_emb, user_emb). Items close to this combined embedding are both relevant to the query AND aligned with the user.
- **Filter boosting**: Boost items from categories/brands the user has engaged with before. Soft boost (add score), not hard filter (don't hide unseen categories).
- **Contextual features**: Time of day, device, location, session history. "Running shoes" on Saturday morning vs Tuesday at 11pm likely has different intent.

**The personalization-diversity tension**: Extreme personalization creates filter bubbles. If you always boost what the user clicked before, they never see anything new. Balance with: (a) diversity constraints (max 3 items per category), (b) serendipity slots (5% of results from outside the user's history), (c) periodic exploration (every Nth session, broaden results).

**Hard FUQ**: Two users search "shoes" — one always buys Nike, the other always buys Adidas. Should the retrieval layer personalize, or should it return the same results and let ranking personalize?

**Answer**: Retrieval should return a SUPERSET that covers both — retrieve Nike shoes AND Adidas shoes AND other brands. Then ranking personalizes: the Nike user sees Nike ranked higher, the Adidas user sees Adidas ranked higher. Personalizing retrieval risks MISSING relevant items that the user hasn't tried yet (maybe the Nike user would love a New Balance shoe, but personalized retrieval excluded it). Retrieval should maximize recall; ranking should maximize precision+personalization. Separation of concerns.

---

### Q11: When dense retrieval fails and lexical wins (and vice versa)

**Principal Answer**: Understanding where each retrieval method fails is more important than knowing where it works — it determines your hybrid strategy.

**Dense retrieval fails when**:
| Scenario | Why Dense Fails | Why Lexical Succeeds |
|---|---|---|
| Exact codes (ASINs, SKUs) | BPE splits codes into meaningless subwords | Exact string match is trivial for inverted index |
| Rare domain terms ("ACOS", "SQR") | Insufficient training data for rare terms | IDF gives high weight to rare terms (highly discriminative) |
| Negation ("shoes NOT red") | Embeddings don't encode negation well | Boolean queries are native to inverted index |
| Number matching ("size 10", "under $100") | Embeddings treat numbers as text tokens | Can be handled with structured filters |
| Very short queries (1 word) | Insufficient context for meaningful embedding | BM25 handles single-token lookup fine |

**Lexical retrieval fails when**:
| Scenario | Why Lexical Fails | Why Dense Succeeds |
|---|---|---|
| Paraphrases ("ML" vs "machine learning") | No lexical overlap | Same meaning → similar embeddings |
| Conceptual queries ("help me sleep better") | No product mentions exact words | Semantic match to sleep aids, mattresses, etc. |
| Cross-lingual | Different languages = zero token overlap | Multilingual embeddings map to same space |
| Intent matching ("best gift for dad") | No product contains "gift for dad" | Embeddings capture gift-giving intent |

> [!experience] At Amazon Ads, the clearest failure case was ASINs. An advertiser searching "B0CXYZ123" — their own product code — got zero results from dense retrieval (the embedding of a random alphanumeric string is meaningless). BM25 returned the exact product instantly. This single failure mode meant we could never go dense-only. Conversely, when advertisers searched "increase reach for my running shoe campaigns," BM25 returned nothing useful (no document contained that exact phrase). Dense retrieval found keyword expansion recommendations that matched the intent.

**Hard FUQ**: Can you train embeddings that handle exact codes correctly?

**Answer**: Partially. (1) Add code-aware tokenization: treat ASINs/codes as single tokens (not BPE-split). This requires a custom tokenizer. (2) Train with code-based pairs: (ASIN_query → ASIN_product) as positive pairs. The model learns that these character sequences map to specific items. (3) But: this makes the embedding model domain-specific and won't transfer to new products with unseen codes. You'd need continuous fine-tuning as new products are added. Pragmatically: it's cheaper and more robust to keep BM25 for exact-match queries and use embeddings where they actually add value (semantic matching). Don't force embeddings to solve a problem that BM25 solves perfectly.

---

### Q12: Building a retrieval system from scratch — what order?

**Principal Answer**: The build order matters because each component's value depends on what's already in place, and missteps create technical debt that's expensive to unwind.

**Phase 1 (Week 1-2): BM25 + basic query processing**
- Inverted index (Elasticsearch/OpenSearch) over your corpus
- Tokenization, lowercasing, stop words, basic spell correction
- This gives you a working search system that handles 60-70% of queries acceptably

**Phase 2 (Week 3-4): Evaluation foundation**
- Build labeled eval set (200+ query-document pairs, human-annotated)
- Establish baseline metrics (recall@K, MRR, zero-result rate)
- You need this BEFORE adding complexity — otherwise you can't measure improvement

**Phase 3 (Month 2): Dense retrieval**
- Choose embedding model (evaluate 3-4 on your eval set, not MTEB)
- Build vector index (HNSW via pgvector, FAISS, or managed vector DB)
- Implement hybrid fusion (RRF) with BM25
- Measure: does hybrid improve recall over BM25 alone? By how much? On which query types?

**Phase 4 (Month 3): Reranking + query understanding**
- Add cross-encoder reranker on top-100
- Add query classification (navigational vs semantic) and entity detection
- These build on Phase 3's improved candidate set

**Phase 5 (Month 4+): Optimization**
- Fine-tune embeddings on domain data
- Add query expansion/rewriting
- A/B test online with real users
- Iterate based on production signals

> [!experience] At Amazon Ads, we followed exactly this order — phased build with measurement at each stage. Senior leadership pushed to jump to full embedding-based retrieval (Phase 3) immediately. I pushed back with data showing that BM25 alone handled 60% of queries well, and we needed an evaluation foundation before we could measure whether dense retrieval actually helped. The phased approach delivered value at every stage while avoiding the "big rewrite" risk.

**Hard FUQ**: You're at Phase 3 and hybrid retrieval only improves recall by 3% over BM25 alone. Is it worth the complexity?

**Answer**: 3% aggregate may be misleading. Slice by query type: (a) If semantic queries (paraphrases, intent-based) improved 20% while exact-match queries stayed flat, the 3% aggregate hides a meaningful improvement on a growing query type. Worth keeping. (b) If improvement is uniform 3% across all types, the value is marginal relative to complexity. Consider: is 3% recall worth maintaining a vector database + embedding pipeline + fusion logic? It depends on the business value of those additional relevant results. At $0.10 per relevant result, 3% more recall on 1M queries/day = $3K/day = ~$1M/year. Compared to the infra cost of the vector DB + embeddings pipeline, this may or may not be worth it.
[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

## Distinguished Engineer Depth Probes

<details>
<summary><strong>DE Probe 1: BM25 Internals — Why does TF-IDF work, and where does it break mathematically?</strong></summary>

**Question**: Walk me through the BM25 scoring formula. Why the specific functional form? Where does it fail?

**What they're testing**: Understanding the probabilistic foundation of lexical retrieval, not just "it's a keyword search."

**Answer**:
BM25 is derived from the probabilistic relevance framework (Robertson-Sparck Jones):

```
BM25(q, d) = Σ_{t ∈ q} IDF(t) × (tf(t,d) × (k₁ + 1)) / (tf(t,d) + k₁ × (1 - b + b × |d|/avgdl))
```

**Component decomposition**:

1. **IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))**: Rare terms are more discriminative. A term appearing in 5 of 10M documents is highly informative. A term appearing in 5M of 10M is noise. IDF captures this — it's the log-odds ratio of the term being relevant vs appearing by chance.

2. **Saturating TF**: `tf × (k₁+1) / (tf + k₁ × ...)`: Raw term frequency has diminishing returns. A document mentioning "shoes" 100 times isn't 100x more relevant than one mentioning it once. The k₁ parameter controls saturation speed (typical: k₁=1.2). At k₁=0: all non-zero TF is equal. At k₁→∞: raw TF with no saturation.

3. **Length normalization**: `(1 - b + b × |d|/avgdl)`: Long documents naturally have higher TF. Without correction, BM25 biases toward long documents. b=0.75: moderate correction. b=0: no length normalization. b=1: full normalization.

**Where BM25 fails mathematically**:
1. **Independence assumption**: BM25 scores terms independently. "New York" = "New" + "York." It can't capture that "New York" is a single concept, not two separate words. Workaround: add bigram/trigram tokens to the index.
2. **No synonymy**: "ML" and "machine learning" share zero terms → zero BM25 similarity. IDF can't help because it only weighs terms that appear, not terms that SHOULD appear.
3. **No semantics**: "Bank" (financial) and "bank" (river) are the same token. BM25 can't disambiguate polysemy.
4. **Short query problem**: For 1-2 word queries, TF saturation barely matters and the score is dominated by IDF — which is a global property of the corpus, not query-specific. Short queries get generic results.

> [!experience] At Amazon Ads, BM25's independence assumption was a practical problem for multi-word product names. "Nike Air Max 90" should match the exact product, but BM25 treats it as four independent terms and might rank a document with high frequency of "Air" (HVAC products) above the actual shoe. We used phrase matching (exact n-gram boost) on top of BM25 to handle this.

**Follow-up**: How does SPLADE improve on BM25 while keeping the inverted index structure?

**Answer**: SPLADE (Sparse Lexical and Expansion) learns to EXPAND each document with semantically related terms before indexing. "Running shoes" → expanded to include "jogging," "athletic footwear," "sneakers" with learned weights. This lives in a standard inverted index but captures semantic similarity that BM25 misses. Formally: for each token position, SPLADE predicts an importance weight over the FULL vocabulary (not just the token at that position). The result: a sparse vector where many vocabulary terms have non-zero weight, stored in an inverted index. Retrieval is standard inverted index lookup, but the index now contains semantic expansions. Quality: ~95% of dense retrieval quality with inverted index serving speed.

</details>

<details>
<summary><strong>DE Probe 2: HNSW vs IVF — ANN algorithm tradeoffs at scale</strong></summary>

**Question**: Compare HNSW and IVF-based ANN algorithms. When would you choose each?

**What they're testing**: Algorithm-level understanding of approximate nearest neighbor search — the foundation of dense retrieval.

**Answer**:

**HNSW (Hierarchical Navigable Small World)**:
- Data structure: Multi-layer navigable graph. Each node (vector) connects to M nearest neighbors. Higher layers are exponentially sparser.
- Search: Start at top layer, greedily navigate to nearest node, drop to next layer, expand beam search at layer 0.
- Build: O(N × log N × ef_construction). Each insertion traverses the graph to find neighbors.
- Query: O(log N × ef_search × M). Logarithmic in dataset size.
- Memory: Full vectors in memory + graph edges. ~(d×4 + M×2×4×layers) bytes per vector. For 768-dim, M=16: ~3.2KB per vector.

**IVF (Inverted File Index)**:
- Data structure: Partition vectors into K clusters (via k-means). Each cluster has an inverted list of member vectors.
- Search: Find nearest C cluster centroids to query → search within those C lists (brute force or with product quantization).
- Build: O(N × K × iterations) for k-means + list construction.
- Query: O(C × avg_list_size). Depends on C (search breadth) and list sizes.
- Memory: Can be combined with Product Quantization (PQ) for massive compression. PQ reduces 768×4=3072 bytes to 64-128 bytes per vector.

**Head-to-head comparison**:

| Factor | HNSW | IVF-PQ |
|---|---|---|
| Recall@10 (100M vectors) | 95-98% | 85-92% (recoverable with reranker) |
| Query latency | 1-5ms | 2-10ms |
| Memory per vector | ~3.2KB (full) | ~128 bytes (PQ) — 25x compression |
| Memory for 100M vectors | ~320GB | ~12.8GB |
| Build time | Hours (sequential) | Hours (parallelizable) |
| Update cost | O(log N) per insert | Re-cluster periodically |
| Best for | High-recall, in-memory affordable | Large corpus, memory-constrained |

**Decision framework**:
- Corpus fits in memory with HNSW (<50M items on a 256GB machine) → use HNSW
- Corpus doesn't fit → IVF-PQ + cross-encoder reranker to recover recall
- Need online updates (frequent inserts/deletes) → HNSW (graph update is efficient)
- Batch-only updates → IVF (re-cluster on schedule)

> [!experience] At Amazon Ads with hundreds of millions of items, HNSW in pure form was memory-prohibitive for the full catalog. We used HNSW for high-traffic item segments (top 10% by impressions) and IVF-PQ for the long tail. The cross-encoder reranker recovered the recall gap on IVF-PQ retrievals. This tiered approach gave us 95%+ effective recall at 1/10th the memory cost of full HNSW.

**Follow-up**: You add 1M new items per day. How do you handle index updates?

**Answer**: HNSW supports incremental inserts (O(log N) per item, no rebuild needed). IVF requires periodic re-clustering (centroids drift as data distribution changes). Practical approach: (1) HNSW: insert new items as they arrive. Rebuild nightly for optimal graph quality. (2) IVF: add new items to nearest existing cluster (approximate, fast). Re-cluster weekly. During re-clustering, serve from the old index (blue-green).

</details>

<details>
<summary><strong>DE Probe 3: Learned Sparse Representations (SPLADE) — Bridging lexical and semantic</strong></summary>

**Question**: How does SPLADE work? Why is it sometimes called "the best of both worlds"?

**What they're testing**: Understanding of the newest retrieval paradigm that combines lexical and semantic advantages.

**Answer**:
SPLADE (SParse Lexical AnD Expansion model) produces a SPARSE representation over the full vocabulary for each document and query. Unlike dense embeddings (one fixed-dim vector), SPLADE produces a vector of size |V| (vocabulary size, ~30K) where most entries are zero.

**Mechanism**:
```
For each token position i in document d:
  h_i = BERT(d)[i]                    # contextualized token embedding
  w_i = log(1 + ReLU(W × h_i))       # transform to vocabulary-size logits
  
SPLADE(d) = max_pool over all positions: s_j = max_i(w_i[j])
  for each vocabulary term j
```

**What this does**: For each vocabulary term j, the model predicts the maximum importance of that term across all positions in the document. "Running shoes" might activate:
```
running: 0.9, shoes: 0.8, jogging: 0.4, athletic: 0.3, sneakers: 0.2, footwear: 0.5, ...
(30K - 6 other terms: 0.0)
```

The EXPANSION is the key: terms like "jogging" and "sneakers" that DON'T appear in the document get non-zero weights because the model learned they're semantically related.

**Why "best of both worlds"**:
1. **Lexical precision**: Original document terms get high weights → exact match queries work (like BM25)
2. **Semantic expansion**: Related terms get non-zero weights → paraphrase queries work (like dense)
3. **Inverted index serving**: The sparse representation stores in a standard inverted index → same infrastructure as BM25, same serving speed
4. **Interpretability**: You can see WHICH expanded terms were activated and WHY a document matched

**Comparison**:

| | BM25 | Dense (bi-encoder) | SPLADE |
|---|---|---|---|
| Representation | Bag of exact terms | d-dim dense vector | |V|-dim sparse vector |
| Infrastructure | Inverted index | Vector DB + ANN | Inverted index |
| Semantic matching | No | Yes | Yes |
| Exact match | Yes (strong) | Weak (BPE issues) | Yes (original terms retained) |
| Interpretability | High (term overlap) | Low (black box) | Medium (expanded terms visible) |
| Storage | Low | Medium (d × 4 bytes/vec) | Low-Medium (sparse → compressed inverted lists) |

**When to use SPLADE over hybrid BM25+dense**:
- You don't want to maintain two separate index types (simplicity)
- Your infra is optimized for inverted indexes (Elasticsearch/Lucene stack)
- You need interpretability (can explain which expanded terms caused the match)

**When SPLADE falls short**:
- Cross-lingual retrieval (SPLADE works per-language; multilingual dense embeddings work across languages)
- Very short queries (1-2 words) where expansion may over-generalize

> [!experience] We evaluated SPLADE at Amazon Ads as a potential replacement for our hybrid BM25+dense setup. Quality was competitive (within 2% of hybrid on our eval set), but the advantage was operational: one index type instead of two, simpler infrastructure, no fusion tuning. The drawback: SPLADE models are harder to fine-tune than embedding models, and retraining requires reindexing (same as dense). We ultimately kept hybrid because our infrastructure was already built, but for a new system I'd strongly consider SPLADE as the starting point.

**Follow-up**: How do you control SPLADE's sparsity? If it activates too many vocabulary terms, the index becomes dense and slow.

**Answer**: L1 regularization on the SPLADE output: `L_total = L_ranking + λ × Σ_j |s_j|`. Higher λ → sparser representations (fewer activated terms) → faster retrieval but potentially lower recall. Typical non-zero terms per document: 100-300 out of 30K vocabulary. This is sparse enough for efficient inverted index serving. Monitor the average number of activated terms during training — if it grows beyond 500, increase λ.

</details>

<details>
<summary><strong>DE Probe 4: Contrastive Learning for Embeddings — The training objective that makes retrieval work</strong></summary>

**Question**: Walk me through the contrastive learning objective used to train retrieval embeddings. Why InfoNCE, and what are the failure modes?

**What they're testing**: Understanding the training objective at the mathematical level — not just "we fine-tune embeddings."

**Answer**:
**InfoNCE loss** (the standard for retrieval embedding training):

```
L = -log(exp(sim(q, d+) / τ) / (exp(sim(q, d+) / τ) + Σ_{d- ∈ D_neg} exp(sim(q, d-) / τ)))
```

Where:
- q = query embedding, d+ = positive (relevant) document embedding
- D_neg = set of negative documents
- sim = cosine similarity (or dot product)
- τ = temperature (controls sharpness of the distribution)

**Interpretation**: Maximize the probability that the positive document is closer to the query than all negatives. This is a softmax cross-entropy over the similarity scores.

**Temperature τ controls the learning dynamic**:
- High τ (>1.0): Softmax is flat → model treats all negatives similarly → learns coarse distinctions (relevant vs completely unrelated)
- Low τ (<0.1): Softmax is peaked → model focuses on the hardest negatives → learns fine-grained distinctions but training is unstable
- Typical: τ = 0.05-0.1 for retrieval embeddings

**Failure modes**:

1. **Dimensional collapse**: All embeddings converge to a low-dimensional subspace. The model uses only 10 of 768 dimensions. Detection: compute the singular values of the embedding matrix — if they decay rapidly, the effective dimensionality is low. Fix: add a uniformity regularization term or use whitening.

2. **Popularity bias**: Frequently occurring items appear in more negative sets, getting pushed away from more queries. Popular items end up in a "far-from-everything" region. Fix: frequency-weighted negative sampling (log-Q correction).

3. **Hard negative collapse**: If negatives are too hard (very similar to positive), the model can't converge — gradient signals conflict. Fix: curriculum learning — start with easy negatives, gradually introduce harder ones.

4. **Batch size sensitivity**: InfoNCE performance improves with larger batch sizes (more negatives → better gradient estimate). Small batches (<64) produce noisy gradients and poor convergence. Large batches (4096+) require distributed training.

> [!experience] At Amazon Ads, when we fine-tuned embeddings for targeting expansion, we encountered popularity bias: high-traffic products were pushed to a "dead zone" in embedding space because they appeared as negatives so frequently. We applied log-Q correction — weighting negatives inversely by their frequency — which restored those products to meaningful embedding positions and improved retrieval recall for popular products by 8%.

**Follow-up**: How do you evaluate whether embeddings have collapsed or are well-distributed?

**Answer**: Three metrics: (1) **Alignment**: Average cosine similarity between positive pairs. Should be high (>0.8). Low alignment = model can't distinguish similar items. (2) **Uniformity**: How uniformly embeddings are distributed on the hypersphere. Measured as: `L_uniform = log(E[exp(-2 × ||x - y||²)])` averaged over random pairs. Lower = more uniform = better. (3) **Effective dimensionality**: Ratio of the sum of singular values to the max singular value of the embedding matrix. Higher = more dimensions are used. If effective dimensionality is <50% of the embedding dimension, the model is wasting capacity. Plot these during training — if alignment improves but uniformity degrades, the model is collapsing.

</details>

<details>
<summary><strong>DE Probe 5: Reciprocal Rank Fusion — Why it works and when it doesn't</strong></summary>

**Question**: RRF is the standard fusion method for hybrid retrieval. Walk me through why it works, what the k parameter does, and when it fails.

**What they're testing**: Deeper understanding than "we use RRF" — the mathematical properties and failure modes.

**Answer**:
**RRF formula**:
```
RRF_score(d) = Σ_r 1 / (k + rank_r(d))

where r iterates over retrieval systems, rank_r(d) = rank of document d in system r
```

**Why it works (mathematical intuition)**:
- 1/(k + rank) is a hyperbolic decay function. Items ranked 1st get score 1/(k+1), items ranked 100th get 1/(k+100). The decay is steep at the top and flat at the bottom.
- k controls the "trust in high ranks": Large k (k=60, standard) → all ranks within top-100 get similar scores → neither system dominates. Small k (k=1) → top-ranked items dominate → the system with the "better" top-1 wins.
- **Key property**: RRF is RANK-based, not score-based. This means you don't need to normalize BM25 scores and embedding scores to the same scale. This is huge practically — BM25 scores range from 0-20, cosine similarity from -1 to 1, and normalizing them without distortion is hard.

**Why k=60 is standard**: At k=60, the score difference between rank 1 and rank 60 is: 1/61 - 1/120 ≈ 0.008. The difference between rank 1 and rank 2 is: 1/61 - 1/62 ≈ 0.0003. This means RRF with k=60 heavily favors items that appear in BOTH lists (rank-based consensus) over items that are ranked very high in only one list. It's a consensus function.

**When RRF fails**:
1. **One system is consistently better**: If dense retrieval is strictly better than BM25 for 90% of queries, RRF gives equal vote to BM25, diluting the better system. Fix: weighted RRF — multiply each system's contribution by a learned weight.
2. **Score distribution mismatch in meaning**: If BM25 returns 1000 items but only top-10 are relevant, while dense returns 100 items that are all somewhat relevant, RRF treats ranks equally even though they carry different information. The BM25 item at rank 50 is irrelevant; the dense item at rank 50 is moderately relevant.
3. **Missing items**: If a document appears in one system but not the other, it gets a penalty (no contribution from the missing system). For hybrid retrieval, this is actually desirable — consensus is important. But for specialized retrievers (one for English content, one for code), missing from one system shouldn't penalize.

**Alternatives to RRF**:
- **Learned fusion**: Train a model: relevance = f(BM25_score, dense_score, query_features). Better when you have labeled data. Requires training and is sensitive to score distribution shifts.
- **Cascade**: Dense first → BM25 as filter (keep only items that also appear in BM25 top-K). Useful when you trust dense for recall but want BM25 for precision.

> [!experience] At Amazon Ads, we used RRF for fusing BM25 and semantic retrieval in the targeting expansion system. The k=60 default worked well for our case because both systems contributed genuine value on different query types. We tested weighted RRF (2:1 in favor of semantic for intent-based queries) and saw a modest improvement (+1.5% recall), but the added complexity of query-type-dependent weights wasn't worth it at that stage.

**Follow-up**: How do you decide between RRF and learned fusion?

**Answer**: Start with RRF (zero training required, robust, works out of the box). If you have 10K+ labeled query-document pairs AND the two systems have very different quality profiles (one is much better for certain query types), switch to learned fusion — train a gradient-boosted model on (BM25_rank, dense_rank, query_type_features) → relevance. The improvement over RRF is typically 2-5% recall. Below 10K labeled pairs, learned fusion overfits and RRF is safer.

</details>

<details>
<summary><strong>DE Probe 6: Relevance Feedback Loops — Implicit signals for retrieval improvement</strong></summary>

**Question**: How do you use implicit user feedback (clicks, dwell time, purchases) to improve retrieval? What are the pitfalls?

**What they're testing**: Understanding of the feedback loop between production signals and retrieval quality — the data flywheel for search.

**Answer**:
**The feedback loop**:
```
Retrieval → User sees results → User clicks/skips/purchases → Signal fed back to improve retrieval
```

**Types of implicit feedback**:

| Signal | What It Means | Noise Level | How to Use |
|---|---|---|---|
| Click | User was interested enough to click | High (position bias, attractive thumbnail) | Training data for ranking, with position correction |
| Skip (saw but didn't click) | Probably not relevant for this query | Medium (might be relevant but user was lazy) | Negative training signal (weak) |
| Dwell time | Long dwell = found value; short dwell = disappointment | Medium (depends on content length) | Weight clicks by dwell: long_dwell click > short_dwell click |
| Purchase | Strong positive signal — user converted | Low noise | Strongest positive training signal |
| Add to cart | Purchase intent but not completed | Low-medium | Strong positive, slightly weaker than purchase |
| Query refinement | First results didn't satisfy | Low noise | The ORIGINAL query-result pair was bad (negative signal) |

**Using feedback to improve retrieval**:

1. **Embedding fine-tuning**: Use (query, clicked_item) as positive pairs, (query, skipped_item) as negatives. Fine-tune embeddings weekly on accumulated feedback. The embeddings learn YOUR users' notion of relevance, not generic semantic similarity.

2. **Click-through features for ranking**: Add user_clicked_similar_items, category_click_rate, brand_preference as features in the reranker. These personalize ranking based on aggregate behavioral patterns.

3. **Query expansion from clicks**: If users searching "comfortable shoes" consistently click items with "ergonomic" in the description, add "ergonomic" as an expansion term for "comfortable shoes." Learn query→expansion mappings from click patterns.

**Pitfalls**:

1. **Position bias (biggest)**: Users click top results regardless of relevance. Training on raw clicks teaches "position 1 is good," not "this item is relevant." Fix: IPW correction or position-aware models.

2. **Popularity bias**: Popular items accumulate more clicks → get ranked higher → get more clicks. Long-tail items starve for feedback. Fix: exploration (show some random/under-exposed items), frequency-based negative sampling.

3. **Feedback delay**: Purchases happen hours/days after the search. The feedback loop is slow for conversion signals. Click signals are fast but noisy. Optimal: use click signals for fast iteration, validate with conversion signals weekly.

4. **Confounding**: A click doesn't mean the RETRIEVAL was good — it might mean the item image was attractive (presentation effect). If you optimize retrieval for clicks, you might optimize for attractive thumbnails, not relevant content.

> [!experience] At Amazon Ads, we used advertiser adoption as the primary feedback signal for keyword recommendations (analogous to clicks for search). The key insight: adoption signals are available immediately and don't require downstream attribution. We trained a ranking model on adoption patterns that predicted which recommendations advertisers would act on — this was the daily flywheel that compounded improvement over months. The ranking model improvement yielded more value than generator improvements because it directly targeted the adoption bottleneck.

**Follow-up**: You've been improving retrieval with feedback for 6 months. How do you know you haven't created a filter bubble where the system only retrieves what users have already clicked?

**Answer**: Monitor two metrics: (1) **Catalog coverage over time**: What percentage of the catalog gets retrieved in any query each month? If declining → filter bubble forming. (2) **Novelty rate**: What percentage of retrieved items are items the user has never seen before? If declining → personalization is over-specializing. Set minimum thresholds for both and enforce with diversity constraints. Also: periodically compare retrieval quality on a FRESH eval set (new queries, new items not in training) vs the production eval set. If fresh-set quality degrades while production-set quality improves, the model is overfitting to historical patterns.

</details>
[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

## Cost Model

### Per-Query Cost Breakdown (2026 pricing, approximate)

| Component | Cost/Query | Assumptions | Optimization Lever |
|-----------|-----------|-------------|-------------------|
| Query processing (spell, entity, classify) | ~$0 | CPU-only, <5ms | None needed |
| BM25 retrieval | $0.00001 | Elasticsearch/OpenSearch, sharded | Self-hosted infra cost only |
| Dense ANN retrieval | $0.00005 | HNSW over 10M items, managed vector DB | Self-hosted pgvector for cost |
| RRF fusion | ~$0 | CPU merge, <1ms | None needed |
| Cross-encoder reranking (top-100) | $0.001 | bge-reranker-large, self-hosted GPU | Reduce to top-50; smaller model |
| LLM query expansion (optional) | $0.003 | Haiku call for rewriting | Only on low-recall queries |
| **Total (BM25 only)** | **~$0.00001** | Baseline | |
| **Total (hybrid, no reranker)** | **~$0.00006** | BM25 + dense + RRF | |
| **Total (hybrid + reranker)** | **~$0.001** | Full pipeline | |
| **Total (hybrid + reranker + LLM expansion)** | **~$0.004** | Maximum pipeline | |

### Monthly Cost at Scale

| Scale | Queries/Day | Monthly Cost | Cost/Query | Notes |
|-------|------------|-------------|------------|-------|
| BM25 only (300M MAU) | 50M | ~$15K (infra) | $0.00001 | Elasticsearch cluster |
| + Dense retrieval | 50M | ~$30K (+$15K vector DB) | $0.00006 | Additional vector index infra |
| + Cross-encoder reranker | 50M | ~$80K (+$50K GPU) | $0.001 | GPU serving for reranker |
| + Selective LLM expansion (10%) | 5M | ~$95K (+$15K LLM) | $0.001 avg | LLM only on low-recall queries |

> [!experience] At Amazon Ads serving 300M+ MAU, the retrieval infrastructure cost was dominated by compute (GPU for cross-attention models, serving infrastructure) rather than LLM API calls — because the LLM was used offline for feature generation, not per-query. The cross-attention reranker at +900 bps justified its GPU cost ($50K/mo) against the revenue it unlocked ($100M+ annualized from targeting expansion). Cost-per-query is meaningless without revenue-per-query context.

### Cost Optimization Priority Stack
1. **Tiered index** (3-5x memory savings): Hot items in HNSW, cold items in IVF-PQ. Most queries only hit the hot tier.
2. **Selective reranking** (2x on reranker cost): Skip cross-encoder when BM25 and dense agree on top-5 (high-confidence retrieval).
3. **Query result caching** (1.3-1.5x): Cache (query_hash → results) for repeated queries. 15-30% hit rate for head queries.
4. **Model distillation** (2x on reranker): Distill cross-encoder into a bi-encoder with MLP head. 80% of quality at 10x faster inference.
5. **LLM expansion only on failure** (selective): Only invoke LLM query expansion when initial retrieval returns <10 results above threshold.

### Build vs Buy Analysis

| Component | Managed | Self-Hosted | Decision |
|-----------|---------|-------------|----------|
| Inverted index (BM25) | Elastic Cloud ($2K+/mo) | Self-hosted Elasticsearch ($500/mo compute) | Self-host at scale for cost; managed for small teams |
| Vector DB | Pinecone ($70/mo per 1M vecs) | pgvector or FAISS (compute only) | Managed if <10M vectors; self-host above |
| Embedding model | API (OpenAI, Cohere) | Self-hosted sentence-transformers | Self-host always for search (latency-critical, high volume) |
| Cross-encoder reranker | Cohere Rerank API | Self-hosted bge-reranker on GPU | Self-host (latency control, cost at volume) |
| Query understanding | Custom (always) | — | Too domain-specific for off-the-shelf |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## Observability & Production Debugging

### Per-Query Traces

| Field | Why | Used For |
|-------|-----|----------|
| `raw_query` + `processed_query` | Track query processing changes | Debug rewriting issues |
| `spell_corrections` | Did we change the query? | Spell correction accuracy |
| `entity_detections` | What entities were found? | Entity recognition quality |
| `intent_classification` | Navigational/transactional/informational | Routing correctness |
| `bm25_results` (doc_ids + scores, top-20) | BM25 retrieval quality | Per-system recall analysis |
| `dense_results` (doc_ids + scores, top-20) | Dense retrieval quality | Per-system recall analysis |
| `fused_results` (doc_ids + RRF scores) | Fusion quality | Compare fused vs individual systems |
| `reranker_results` (doc_ids + reranker scores) | Reranking quality | Reranker value-add measurement |
| `final_results` | What the user saw | Ground truth for online metrics |
| `user_action` (click, skip, purchase, refine) | User feedback | Training data, quality monitoring |
| `latency_breakdown` (per component) | Performance | Bottleneck identification |

### Monitoring Dashboard

| Panel | Metric | Alert Threshold | Escalation |
|-------|--------|----------------|------------|
| Zero-result rate | % queries with no results | >3% (was 1.5%) | → Retrieval team: coverage gap or index issue |
| Search abandonment rate | % searches with no clicks | >25% (was 18%) | → Quality team: results aren't satisfying users |
| BM25-only recall@10 (golden set) | Recall on labeled queries | <75% (was 82%) | → Index issue: check tokenization, index freshness |
| Dense recall@10 (golden set) | Recall on labeled queries | <80% (was 88%) | → Embedding issue: model drift, index corruption |
| Hybrid lift over best-single | How much hybrid adds vs best individual system | <3% (was 8%) | → Investigate: is one system degraded? Is fusion broken? |
| Reranker NDCG lift | NDCG improvement from reranker | <5% (was 12%) | → Reranker not adding value; check model, candidate set |
| Query latency p99 | End-to-end search latency | >100ms (SLA: 50ms) | → Infra: check index health, reranker queue |
| Embedding index freshness | Time since last item was indexed | >2h (target: <1h) | → Pipeline: indexing delay |

### Debugging Walkthrough

**Scenario**: Users searching "wireless earbuds ANC" (Active Noise Cancellation) get results for regular wireless earbuds without ANC. The ANC products exist in the catalog but aren't being retrieved.

**Step 1 — Check BM25**: Query "wireless earbuds ANC" against BM25 index. Finding: BM25 returns ANC products correctly (the term "ANC" appears in their titles). BM25 recall is fine.

**Step 2 — Check dense retrieval**: Embed the query and search the vector index. Finding: Dense retrieval returns generic wireless earbuds but NOT ANC-specific ones. The embedding of "ANC" doesn't map to the embedding of "Active Noise Cancellation" or "noise cancelling."

**Step 3 — Check fusion**: RRF combines both lists. BM25 has the ANC products; dense doesn't. In the fused ranking, ANC products get a score from BM25 but zero from dense (they're not in the dense results at all). Generic earbuds get scores from BOTH systems and rank higher in the fused list.

**Step 4 — Root cause**: The abbreviation "ANC" is an out-of-vocabulary term for the embedding model. BPE splits it into subword tokens without learned semantics. Dense retrieval can't match it to "Active Noise Cancellation" in product descriptions.

**Step 5 — Fix**: (a) Short-term: add "ANC" → "Active Noise Cancellation" to the synonym expansion dictionary in query processing. Expand before BOTH retrieval systems see the query. (b) Medium-term: fine-tune embeddings with domain query-product pairs that include abbreviations. (c) Long-term: consider SPLADE, which learns to expand "ANC" → "noise cancelling" automatically during indexing.

> [!experience] This exact class of bug — domain abbreviations missed by embeddings — was endemic at Amazon Ads. Campaign types ("SP" for Sponsored Products), bid types ("CPC"), and product codes all suffered from the same root cause. We maintained a domain synonym dictionary with 500+ entries that expanded in query processing before any retrieval system saw the query.

### Versioning & Rollback

| Component | How to Version | How to Rollback | A/B Test Strategy |
|-----------|---------------|-----------------|-------------------|
| BM25 index | Index version tag, rebuilt nightly | Alias swap to previous index | Shadow query: compare results from both indexes |
| Dense index (embeddings) | Embedding model version + index build ID | Alias swap | Shadow retrieval: compare recall@10 on golden set |
| Embedding model | Model ID in serving config | Load previous model + reindex (hours) | Evaluate on golden set before reindex; interleaving test after |
| Cross-encoder reranker | Model version in config | Route to previous model | 5% traffic to new reranker; compare NDCG lift |
| Query processing rules | Config version (synonym dict, entity rules) | Config rollback (instant) | A/B test: 50% of traffic sees new rules |
| RRF parameters (k, weights) | Config version | Config rollback | Interleaving test: old vs new fusion parameters |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Availability | Latency | What It Tells You | Action |
|--------|-------------|---------|-------------------|--------|
| Click on result | High volume | Immediate | Engagement relevance (noisy: position bias) | Train ranking with IPW; update embedding fine-tuning data |
| Zero-result query | Medium volume | Immediate | Coverage gap — query has no good match | Add to gap tracking; inform content/catalog team |
| Query refinement | Medium volume | Immediate | First results unsatisfactory | Negative signal for original query-result pair |
| Purchase from search | Lower volume | Hours-days | True relevance (strongest signal) | Strongest training positive; weight 5-10x vs clicks |
| Dwell time | High volume | Immediate | Content quality after click | Weight long-dwell clicks higher in training |
| Query-to-entity mapping corrections | Low volume (manual) | Days | Entity detection errors | Update entity model training data |

### Improvement Prioritization

| Failure Mode | Business Cost | Frequency | Fix | Priority |
|---|---|---|---|---|
| Zero results on valid query | Very High (user lost) | 1-3% | Expand retrieval (synonym dict, better embeddings) | **P0** |
| Exact-match query fails (product code) | Very High (user frustrated) | 1-2% | Ensure BM25 path handles all codes | **P0** |
| Semantic mismatch (right intent, wrong items) | High (user disappointed) | 10-15% | Improve embeddings, query understanding | **P1** |
| Slow queries (>100ms p99) | Medium (UX degradation) | 5% of queries | Index optimization, caching, reranker routing | **P1** |
| Irrelevant results ranked high | Medium (trust erosion) | 5-10% | Better reranking, diversity, freshness | **P2** |
| Stale results (index not current) | Medium (wrong information) | 2-5% | Improve indexing pipeline freshness | **P2** |

### Continuous Improvement Cadence

| Frequency | What Gets Updated | Validation Gate |
|-----------|-------------------|-----------------|
| Real-time | Synonym dictionary (add new abbreviations/terms) | Spot-check: does the new synonym improve relevant query results? |
| Daily | Query processing rules (spell correction, entity patterns) | Zero-result rate ≤ previous day |
| Weekly | BM25 index rebuild (fresh content, updated documents) | Recall@10 on golden set ≥ previous |
| Bi-weekly | Embedding fine-tuning (on accumulated click/purchase data) | Recall@10 improvement on golden set |
| Monthly | Cross-encoder reranker retrain | NDCG@10 improvement + online A/B for 1 week |
| Quarterly | Embedding model replacement (new base model) | Full reindex + regression suite + 2-week A/B |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| **Hybrid retrieval (BM25 + Dense + RRF)** | Vocabulary mismatch AND exact-match needs | Almost always in production | Tiny corpora (<1K) where brute-force works |
| **Cross-encoder reranking** | Fine-grained relevance precision | Latency budget >50ms; quality-critical surfaces | Ultra-low latency (<20ms total budget) |
| **SPLADE (learned sparse)** | Semantic matching with inverted index efficiency | When you want to replace hybrid with one system | Cross-lingual retrieval; extremely short queries |
| **ColBERT (late interaction)** | Token-level matching faster than cross-encoder | Moderate latency budget; need interpretability | Memory-constrained (100x more storage than bi-encoder) |
| **HyDE (hypothetical document)** | Vague/short queries with poor direct embedding | Queries that are questions, not keywords | Navigational/exact-match queries (worsens them) |
| **Query classification + routing** | Different query types need different retrieval strategies | Systems serving diverse query patterns | Homogeneous query patterns (single intent type) |
| **Zero-shot cross-lingual** | New locale with no training data | Market expansion with multilingual embedding models | Locales with fundamentally different search behavior |
| **Session-aware retrieval** | Iterative search where context builds across queries | Interactive search with query refinement | One-shot retrieval (no session context) |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|---|---|
| "We use vector search for retrieval" | "We use hybrid retrieval because pure vector search misses exact terms — ASINs, product codes, domain acronyms. At Amazon Ads, this single failure mode meant we could never go dense-only. BM25 catches what embeddings miss; embeddings catch what BM25 misses." |
| "We use the top embedding model from MTEB" | "We evaluate on OUR production queries, not MTEB. The #1 MTEB model was #4 on our domain because production queries have typos, abbreviations, and mixed-language patterns. Domain fine-tuning on real query-item pairs closed a 12% recall gap." |
| "We added a cross-encoder reranker" | "Cross-attention reranking gave us +900 bps relevance improvement because it captures token-level intent alignment that dot-product similarity misses. 'Buy running shoes' and 'review running shoes' are completely different intents for the same product — the cross-encoder distinguishes them." |
| "We built dense retrieval for all queries" | "We phased the rollout: BM25 first for head queries where it handles 60% well. Dense retrieval added for semantic queries after we had an evaluation foundation to measure improvement. Senior leadership wanted embeddings-first — I pushed back with data showing the phased approach was lower risk." |
| "We optimize for recall@10" | "Recall@10 is our offline metric but CTR and conversion are what matter. We've seen 8% offline recall improvement translate to zero online impact because the improvement was on long-tail queries representing 5% of production volume. We always validate with A/B tests." |
| "We handle new markets by translating queries" | "Never translate — always regenerate. Translated queries preserve English search patterns. We regenerated from product attributes in the target language, which captures how local users actually search. This plus zero-shot transfer reduced time-to-market by 75% across 19+ locales." |
| "We use HNSW for our vector index" | "HNSW for the hot tier (top 10% of items by traffic), IVF-PQ for the long tail. Full HNSW at hundreds of millions of items was memory-prohibitive. The tiered approach gave 95%+ effective recall at 1/10th the memory cost." |
| "We measure recall on our eval set" | "We maintain TWO eval sets: a clean labeled set for regression testing and a production query sample refreshed monthly. The clean set has high annotator agreement (κ=0.85) but misses real-world query patterns. The production sample is noisier but predicts online metric movements much better." |

[[#Search / Query Understanding / Semantic Retrieval — Interview Prep|↑ Top]]

---

## References

### Foundational Retrieval
1. Okapi BM25 (Robertson et al., 1994) — The probabilistic retrieval model underlying BM25
2. Dense Passage Retrieval (Karpukhin et al., 2020) — https://arxiv.org/abs/2004.04906
3. Sentence-BERT (Reimers & Gurevych, 2019) — https://arxiv.org/abs/1908.10084
4. ColBERT: Efficient and Effective Passage Search (Khattab & Zaharia, 2020) — https://arxiv.org/abs/2004.12832

### Learned Sparse Retrieval
5. SPLADE: Sparse Lexical and Expansion Model (Formal et al., 2021) — https://arxiv.org/abs/2107.05720
6. SPLADEv2 (Formal et al., 2022) — https://arxiv.org/abs/2109.10086

### Hybrid Retrieval & Fusion
7. Reciprocal Rank Fusion (Cormack et al., 2009) — RRF: standard fusion for hybrid retrieval
8. Hybrid Retrieval in Practice — Pinecone (2024) — https://www.pinecone.io/learn/hybrid-search-intro/

### Cross-Encoder & Reranking
9. Cross-Encoders for Reranking — Sentence-Transformers documentation — https://www.sbert.net/examples/applications/cross-encoder/README.html
10. MS MARCO passage reranking baselines — standard benchmarks for cross-encoder quality

### Approximate Nearest Neighbor
11. HNSW: Efficient and Robust Approximate Nearest Neighbor (Malkov & Yashunin, 2018) — https://arxiv.org/abs/1603.09320
12. Product Quantization for Nearest Neighbor Search (Jegou et al., 2010) — https://ieeexplore.ieee.org/document/5432202
13. FAISS: A Library for Efficient Similarity Search — Meta (2017) — https://github.com/facebookresearch/faiss

### Query Understanding
14. HyDE: Precise Zero-Shot Dense Retrieval without Relevance Labels (Gao et al., 2022) — https://arxiv.org/abs/2212.10496
15. Query Understanding at Scale — Google Research

### Evaluation
16. RAGAS Documentation — https://docs.ragas.io/en/stable/
17. BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models (Thakur et al., 2021) — https://arxiv.org/abs/2104.08663
18. MTEB: Massive Text Embedding Benchmark (Muennighoff et al., 2022) — https://arxiv.org/abs/2210.07316

### Position Bias & Learning to Rank
19. Unbiased Learning to Rank with Unbiased Propensity Estimation (Ai et al., 2018) — https://arxiv.org/abs/1804.05938
20. Position Bias Estimation for Unbiased Learning to Rank (Wang et al., 2018) — https://research.google/pubs/pub46485/

### Production Systems
21. Embedding-based Retrieval in Facebook Search — Meta (Huang et al., 2020) — https://arxiv.org/abs/2006.11632
22. Monolith: Real Time Recommendation System — ByteDance (Liu et al., 2022) — https://arxiv.org/abs/2209.07663
23. Contextual Retrieval — Anthropic (2024) — https://www.anthropic.com/research/contextual-retrieval
