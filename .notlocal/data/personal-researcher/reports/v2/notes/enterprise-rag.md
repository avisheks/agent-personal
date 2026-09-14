# Enterprise RAG (Retrieval-Augmented Generation for Production Systems)

> **Last Updated:** 2026-05-31 | **Read time:** ~30 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Enterprise RAG has evolved from naive embed-and-retrieve pipelines to hybrid retrieval systems combining BM25 + dense vectors with cross-encoder reranking and post-generation faithfulness verification [1][10].
> Key players: HNSW-based vector stores [5], contextual chunking [14], Self-RAG [9], GraphRAG [13]. Main open problem: multi-hop reasoning over heterogeneous enterprise corpora without compounding hallucination.
> Recent breakthrough: Contextual Retrieval (Anthropic, 2024) — prepending document-level context to chunks reduced retrieval failures by 49% [14]. Trend: agentic RAG with iterative retrieval and tool-calling is replacing single-shot pipelines.

## State of the Art

### Current Best Approaches

- **Hybrid retrieval (BM25 + dense + RRF)** — Combines lexical precision for exact terms with semantic recall for paraphrases; fused via reciprocal rank fusion [6][11]
- **Cross-encoder reranking** — Jointly encodes query-document pairs for fine-grained relevance scoring after initial retrieval; typically yields 20-30% NDCG improvement [2]
- **Contextual chunking** — Prepends document-level summary to each chunk so it remains self-contained; Anthropic reported 49% fewer retrieval failures [14]
- **Self-RAG** — Model learns to decide when to retrieve, what to cite, and when to critique its own output; reduces over-retrieval and hallucination [9]
- **GraphRAG** — Constructs entity-relationship graphs from corpora to answer global/theme queries that vector search misses [13]

### Recent Breakthroughs (last 12 months)

- **Contextual Retrieval** (Oct 2024): Anthropic demonstrated that chunk-level context injection eliminates the "orphan chunk" problem at minimal indexing cost [14]
- **Self-RAG** (Oct 2024): Training models to emit retrieval/critique tokens enables adaptive retrieval — 20% fewer unnecessary retrievals [9]
- **GraphRAG** (Apr 2024): Microsoft showed graph-based summarization outperforms vector RAG on "what are the main themes" queries by 70%+ [13]
- **Matryoshka embeddings** (2024 adoption): Variable-dimension embeddings allow trading 2-8x storage for <3% recall loss [12]

### Open Problems

- **Multi-hop reasoning**: Queries requiring information synthesis across 3+ documents still produce compounding errors
- **Hallucination with correct context**: Models still confabulate even when the answer is in the retrieved passages [7]
- **Freshness at scale**: Real-time index updates with consistency guarantees across distributed vector stores
- **Evaluation without ground truth**: Automated faithfulness metrics correlate imperfectly with human judgments [8]

## Executive Summary

RAG externalizes knowledge from model weights to a retrieval system, solving static knowledge, hallucination, and attribution limitations of standalone LLMs [1]. The core architectural decision is whether to optimize retrieval quality (hybrid search, reranking, better chunks) or generation quality (prompting, verification, citation enforcement) — production systems need both.

- **Choose simple RAG** when: single document type, factual lookups, <1M documents
- **Choose full pipeline** (hybrid + rerank + verify) when: multi-tenant, regulated industry, diverse corpora
- **Choose agentic RAG** when: multi-hop questions, tool-calling needs, iterative refinement required

**The killer framing:** "RAG separates the reasoning capability (LLM) from the knowledge source (corpus) — letting you update knowledge without retraining, enforce accountability through citations, and control access at retrieval time."

Cost headline: A production RAG query costs $0.005-$0.04 depending on complexity; generation tokens dominate 70%+ of cost [10].

```
Decision Tree: RAG Architecture Selection
──────────────────────────────────────────
Query type?
├── Simple factual lookup
│   └── BM25 + small LLM, skip reranker → $0.005/query
├── Semantic/paraphrase queries
│   └── Hybrid (BM25 + dense) + reranker → $0.01/query
├── Multi-hop / synthesis
│   └── Agentic RAG: decompose → iterative retrieve → verify → $0.04/query
└── Global themes / summarization
    └── GraphRAG [13] → pre-computed community summaries
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Scope, accuracy bar, user types | Factual lookup vs synthesis? Citation required? Freshness tolerance (hours vs days)? Multi-tenant? |
| 2. Identify constraints | Latency, cost, compliance, scale | p50 latency budget (<2s?), per-query cost ceiling, data residency, corpus size (1M vs 100M docs)? |
| 3. Propose baseline | Embedding search + LLM generation | Single embedding model, top-5 chunks, one LLM call. Prove pattern works before adding complexity. |
| 4. Identify gaps | Where baseline fails | Systematic diagnosis: retrieval failures (exact terms missed), ranking failures (right doc ranked low), generation failures (hallucination despite correct context) [7]. |
| 5. Introduce improvements | Targeted fixes per failure mode | Hybrid retrieval for exact-term misses [6], cross-encoder reranking for ranking, contextual chunking for fragmentation [14], query routing for mixed complexity. |
| 6. Add evaluation + guardrails | Component + end-to-end + user metrics | RAGAS metrics [8], faithfulness verification, citation checking, access control testing. Slice by query type and doc type. |
| 7. Discuss scaling tradeoffs | Cost, latency, freshness, multi-tenancy | Token economics dominate — optimize prompt size first. Caching for repeated queries. Index-per-tenant vs shared-with-filters. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Retrieval method | Dense-only (ANN) | Hybrid (BM25 + dense + RRF) | Homogeneous semantic corpus, no acronyms | Enterprise docs with product codes, acronyms, IDs [6] |
| Vector index | HNSW [5] | IVF-PQ | Corpus fits in RAM (<50M docs) | 100M+ docs, memory-constrained |
| Chunking | Fixed-size (400 tokens) | Semantic/contextual [14] | Homogeneous doc types, fast iteration | Mixed formats, tables, cross-references |
| Reranking | Skip (retrieval-only) | Cross-encoder rerank | Latency <200ms total, simple factual queries | Complex queries where precision@5 matters |
| Generation model | Small/fast (Haiku-class) | Large/capable (Sonnet-class) | Simple factual, cost-sensitive | Multi-hop synthesis, high-stakes |

## System Design Walkthrough

### Opening Frame

A production RAG system is a DAG, not a fixed pipeline — query routing can skip steps, complexity detection can trigger multi-hop, and confidence thresholds can trigger fallbacks at any stage. The non-obvious insight: most RAG failures are retrieval failures misdiagnosed as generation failures — teams waste months prompt-engineering when the correct context never reached the model.

### Architecture

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│  User Query  │───▶│ Query Processing│───▶│ Embed Query  │
│              │    │ classify, route, │    │ (same model  │
│              │    │ rewrite          │    │  as indexing) │
└──────────────┘    └─────────────────┘    └──────┬───────┘
                                                   ▼
                                        ┌───────────────────┐
                                        │  Hybrid Retrieval  │
                                        │  BM25 + Dense ANN  │
                                        │  → RRF Fusion [11] │
                                        │  + ACL Filter      │
                                        └────────┬──────────┘
                                                 ▼
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Response    │◀───│  Faithfulness   │◀───│ Cross-Encoder│
│  + citations │    │  Verification   │    │ Reranker     │
│  + confidence│    │  (NLI check)    │    │ top-20→top-5 │
└──────────────┘    └─────────────────┘    └──────┬───────┘
                                                   ▼
                                        ┌───────────────────┐
                                        │  LLM Generation    │
                                        │  (stream, low-temp) │
                                        │  cite sources [1]  │
                                        └───────────────────┘
```

- **Query Processing**: Classify intent, detect complexity (single vs multi-hop), rewrite ambiguous queries
- **Hybrid Retrieval**: Parallel BM25 (lexical) + dense ANN (semantic), fused via RRF [11], filtered by user ACLs
- **Cross-Encoder Reranker**: Jointly scores query-document pairs; narrows top-20 to top-5 for generation [2]
- **LLM Generation**: Low temperature, grounding instructions, citation enforcement, streaming for perceived latency
- **Faithfulness Verification**: NLI-based or LLM-based check that generated claims are grounded in retrieved text [9]

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Exact-term misses (product codes, IDs) | Add BM25 to hybrid pipeline [6] | Index size doubles; fusion adds 5-10ms |
| Chunk fragmentation (answer spans boundary) | Contextual chunking with doc-level prepend [14] | 20-30% more tokens per chunk; higher indexing cost |
| Lost-in-the-middle attention degradation | Place best chunks at context boundaries [7] | Requires relevance-aware ordering logic |
| Over-retrieval for simple queries | Self-RAG: model decides when to retrieve [9] | Requires training retrieval/critique tokens |
| Global/theme queries fail on vector search | GraphRAG for summarization queries [13] | Graph construction is expensive; stale quickly |

### Scaling Summary

- **10x docs (1M→10M)**: HNSW still works; shard by tenant or document type; add query caching
- **100x docs (10M→1B)**: Switch to IVF-PQ or tiered storage [5]; approximate search + reranker to recover recall
- **1000x queries**: Model routing (60% to small model), semantic caching (30% hit rate), async pre-computation of common answers

## Interview Q&A Bank

### Q1: What limitations of LLMs does RAG address?

> **Quick answer:** RAG externalizes knowledge from model weights to a retrieval system, solving static knowledge cutoffs, hallucination under uncertainty, lack of source attribution, and inability to condition on private/runtime-specific context [1].

RAG separates reasoning capability (LLM) from knowledge source (corpus). This solves six fundamental limitations: (1) static knowledge — models have training cutoffs; (2) imperfect memorization — compressed representations lose precision on long-tail facts; (3) hallucination — models generate plausible fiction rather than admitting ignorance; (4) no attribution — no traceability to sources; (5) expensive knowledge updates — fine-tuning is costly and brittle; (6) no access control — model weights cannot enforce per-user permissions [10].

The strategic frame: RAG lets you update knowledge without retraining, enforce accountability through citations, and maintain access control at retrieval time rather than at training time.

**Hard follow-up:** When would you choose fine-tuning over RAG?

> When the task requires internalizing a style, tone, or reasoning pattern — not factual knowledge. Fine-tuning changes HOW the model reasons; RAG changes WHAT it reasons about. For enterprise, the answer is usually both — fine-tune for domain reasoning patterns, RAG for factual grounding.

### Q2: Walk through a production RAG pipeline end-to-end.

> **Quick answer:** Query processing → embedding → hybrid retrieval (BM25 + dense via RRF) → reranking → prompt construction → generation → faithfulness verification → response with citations [1][10].

| Stage | Latency | Purpose |
|-------|---------|---------|
| Query processing | 5-10ms | Normalize, classify intent, rewrite if ambiguous |
| Embedding | 10-50ms | Compute query vector (same model as indexing) |
| Hybrid retrieval | 10-30ms | BM25 + dense ANN, fuse via RRF [11], ACL filter |
| Reranking | 50-200ms | Cross-encoder scores top-20, keeps top-5 [2] |
| Prompt construction | <5ms | Instructions + chunks + metadata |
| Generation | 500-3000ms | Low temperature, streaming, cite sources |
| Verification | 10-50ms | NLI faithfulness check on generated claims |

The pipeline is a DAG: query routing can skip reranking for simple queries, complexity detection triggers multi-hop decomposition, and confidence thresholds trigger fallbacks at any stage.

**Hard follow-up:** What about long-context models that can fit your entire corpus?

> Long context does not solve the problem — it shifts it [7]. You still need selection (which docs to stuff), you pay per-token cost at scale, models suffer "lost in the middle" attention degradation, and you lose the ability to evaluate retrieval as a separate component. Long context works for single-document QA, not open-ended enterprise QA over millions of documents.

### Q3: How do you design a chunking strategy?

> **Quick answer:** Start with section-aware chunking at ~400 tokens, measure retrieval recall, then adjust: smaller for factual lookup, larger for coherence, and add contextual prepending to make chunks self-contained [14].

Key tradeoffs: (1) **Size** — smaller chunks (100-200 tokens) give higher retrieval precision but fragment context; larger chunks (500-800) preserve discourse but dilute focus. (2) **Overlap** — 10-20% reduces boundary loss but increases index size. (3) **Boundary strategy** — naive fixed-size breaks mid-sentence; section-aware respects headings; semantic chunking splits on topic shifts. (4) **Hierarchical** — retrieve at sentence level for precision, expand to section level for generation context. (5) **Contextual** — prepend document-level context to each chunk so it is self-contained [14].

Special handling: tables get serialized with headers (never split a row); code chunks at function boundaries; lists stay together.

**Hard follow-up:** How do you handle a 500-page manual with tables, diagrams, and cross-references?

> Multi-modal pipeline: parse tables into structured format with headers, extract diagram captions, preserve cross-reference links as metadata. Chunk at section boundaries using the document's own structure. For cross-references, store the target as metadata so retrieval can follow links.

### Q4: How do you improve retrieval quality?

> **Quick answer:** Priority stack: (1) hybrid retrieval (BM25 + dense) for exact-term coverage [6], (2) cross-encoder reranking for precision [2], (3) contextual chunking [14], (4) query rewriting for ambiguous queries, (5) domain-fine-tuned embeddings.

| Improvement | ROI | Fixes |
|-------------|-----|-------|
| Hybrid retrieval [6][11] | Highest | Exact-term misses (acronyms, codes, IDs) |
| Cross-encoder reranking [2] | Very high | Right doc retrieved but ranked low |
| Contextual chunking [14] | High | Chunk loses meaning in isolation |
| Query rewriting / HyDE | Medium | Short/ambiguous queries |
| Fine-tuned embeddings | Medium-high | Domain-specific semantic gaps |

> [!experience] At Amazon Ads, ASINs and campaign IDs were the highest-precision queries — and the ones embeddings failed on most. BM25's IDF weighting made these near-perfect retrieval signals, validating hybrid retrieval as non-negotiable for enterprise.

**Hard follow-up:** You've tried all of this and recall is still at 85%. What next?

> Investigate the 15% failure patterns: (a) answer doesn't exist in corpus — expand sources or refuse gracefully; (b) answer is in structured data (tables, databases) — needs SQL retrieval path; (c) answer requires multi-hop across documents — single retrieval cannot find it. The fix is often "different retrieval path" or "honest refusal."

### Q5: How do you diagnose whether a bad answer came from retrieval or generation?

> **Quick answer:** Check if ground-truth doc is in top-20 (if no: retrieval failure), in top-5 (if no: ranking failure), or in context but answer still wrong (generation failure) [7].

Diagnostic protocol: Take the failing query. (1) Check if ground-truth document appears in top-20 retrieval results. If absent — retrieval problem (embedding quality, chunking, query mismatch). (2) If present but not in top-5 — ranking problem (bi-encoder not precise enough; fix with reranker). (3) If present and in top-5, feed only that single chunk to the model. If it still fails — generation problem (hallucination, misinterpretation). If it succeeds with one chunk but fails with five — context noise problem (irrelevant chunks diluting signal) [7].

At scale, automate this with: retrieval recall tracker on golden set, faithfulness scorer (high recall + low faithfulness = generation problem), and failure clustering by query/doc type.

**Hard follow-up:** How do you build this diagnostic at scale?

> Three automated signals: (1) Daily recall@K on 200 labeled queries — alerts on regression. (2) Faithfulness scorer on all responses — high retrieval recall + low faithfulness isolates generation problems. (3) Cluster failures by query type and document type to identify systemic issues rather than one-off bugs.

### Q6: How do you handle multi-hop questions?

> **Quick answer:** Detect complexity, decompose into atomic sub-questions, iteratively retrieve with each result informing the next, structure intermediates as JSON, synthesize with explicit evidence, and verify each claim's provenance [10].

Multi-hop breaks naive RAG: "Which Q3 projects exceeded budget AND missed delivery dates?" requires joining finance reports and timeline trackers. Architecture: (1) Detect — classify query complexity (multiple entities + comparison = multi-hop). (2) Decompose — LLM breaks into atomic sub-questions. (3) Iterative retrieval — each retrieval is informed by prior results. (4) Structure intermediates — convert to JSON to prevent hallucination compounding. (5) Synthesize — final prompt with only relevant structured evidence. (6) Verify — trace each claim to a specific source.

Trade-off: 3-5x latency and cost vs single retrieval. Only trigger for detected complex queries.

**Hard follow-up:** What if the decomposition is wrong?

> Mitigations: (1) Validate decomposition against original query — does answering all sub-questions actually answer the original? (2) Allow backtracking if sub-query retrieval fails. (3) For known patterns (comparison, aggregation, temporal), use template-based decomposition rather than freeform LLM decomposition.

### Q7: How do you prevent hallucination when correct context is retrieved?

> **Quick answer:** Layer defenses: grounding instructions, two-step generation (extract spans then synthesize), citation enforcement with post-hoc verification, low temperature, and fewer/more-relevant chunks to reduce noise [7][9].

Hallucination with correct context is the most insidious failure. Defense layers: (1) **Prompt architecture** — separate retrieved context from instructions; label sources with IDs. (2) **Two-step generation** — Step 1: extract relevant spans; Step 2: generate from extractions only. Makes hallucination detectable. (3) **Citation enforcement** — every claim must cite a source; verify cited text exists. (4) **Context optimization** — fewer, more relevant chunks beat many loosely related ones [7]. (5) **Refusal calibration** — system learns to say "I don't have enough information." (6) **Post-hoc verification** — NLI-based faithfulness check; if unsupported claims detected, regenerate or refuse [9].

**Hard follow-up:** How do you set the refusal confidence threshold without being too conservative?

> Calibrate empirically on a labeled eval set. Measure at what retrieval confidence answer quality drops below acceptable — set threshold there. Monitor refusal rate in production; if >10%, threshold is too aggressive or corpus has coverage gaps. Distinguish "low confidence in retrieval" (refuse) from "low confidence in a specific claim" (answer with caveat).

### Q8: How do you evaluate a RAG system comprehensively?

> **Quick answer:** Evaluate at three layers: component-level (retrieval recall, ranking NDCG), end-to-end (faithfulness, correctness, RAGAS metrics [8]), and user-level (regeneration rate, abandonment, thumbs down).

| Layer | Metrics | Tool |
|-------|---------|------|
| Retrieval | Recall@K, Context Precision, MRR | Golden set, daily automated |
| Ranking | NDCG improvement from reranker | A/B on shadow traffic |
| Generation | Faithfulness, Citation Accuracy, Hallucination Rate | RAGAS [8], NLI models |
| End-to-end | Answer Correctness, Completeness, Robustness | Labeled eval set |
| User-level | Regeneration rate, Thumbs down, Abandonment | Production analytics |

Slice all metrics by document type, query type, user segment, and query complexity. Aggregate metrics hide failure pockets [8].

**Hard follow-up:** How do you evaluate without a labeled golden set (cold-start)?

> Three approaches: (1) LLM-as-Judge — stronger model evaluates outputs (validate against human agreement rate). (2) Synthetic evaluation — generate QA pairs from corpus, test whether RAG can reproduce them. (3) Bootstrap from user feedback — collect thumbs up/down on first 1000 queries as growing eval set. Start with approach 1, validate with approach 3.

### Q9: How do you optimize latency and cost?

> **Quick answer:** Generation tokens dominate 70%+ of cost. Priority: (1) reduce prompt size (fewer/shorter chunks), (2) model routing by query complexity, (3) caching, (4) selective reranking [10].

| Bottleneck | % of Cost | Mitigation |
|------------|-----------|------------|
| Generation (input tokens) | 60-80% | Fewer chunks, shorter chunks, summarize low-priority context |
| Generation (output tokens) | 10-20% | Streaming, length limits, concise prompting |
| Reranking | 5-10% | Skip for simple queries; reduce candidates |
| Vector search | <2% | HNSW tuning [5], shard by tenant |
| Query embedding | <1% | Cache repeated queries |

Strategic optimizations: (1) Query routing — simple queries to small model + fewer chunks + no reranker; complex queries through full pipeline. (2) Semantic caching — same/similar questions get cached answers (20-40% hit rate in enterprise). (3) Progressive response — fast approximate answer from cache, refine if needed.

**Hard follow-up:** Your system has 3s p50 latency. Product wants sub-500ms. What do you cut?

> Stream (masks generation latency — time to first token matters). Pre-compute top-100 frequent queries. Route simple queries to smaller model with 3 chunks and no reranker. If still too slow, serve some queries from pre-built FAQ index without LLM generation.

### Q10: How do you design multi-tenant access control?

> **Quick answer:** Filter at retrieval time (never post-generation), test negative access in CI, and choose shared-index-with-metadata vs index-per-tenant based on compliance requirements.

Architecture options: (1) **Shared index + metadata filtering** — each chunk tagged with tenant/role permissions; filter at retrieval. Efficient but one filter bug = data leak. (2) **Index per tenant** — physical isolation; simpler security but higher infra cost. Use for HIPAA/FedRAMP. (3) **Hybrid** — shared index for common knowledge, per-tenant for sensitive data.

Non-negotiable principles: filter before generation (embedding processing is already a leak); test that user A CANNOT retrieve user B's docs; cascade deletion on access revocation; audit every retrieval.

**Hard follow-up:** A user asks a question answerable only by combining their permitted docs with restricted ones. What happens?

> Answer from ONLY permitted documents, even if incomplete. Indicate "I can only answer based on documents you have access to." Never surface the existence of restricted documents — not even a hint that more information exists, because that leaks the existence of restricted content.

### Q11: RAG vs Fine-tuning vs Long Context — when to use each?

> **Quick answer:** RAG for factual grounding + citations + freshness + access control; fine-tuning for style/reasoning patterns; long context for known single-document QA; RAG + fine-tuning for production enterprise systems [1][10].

| Approach | Best For | Weakness |
|----------|----------|----------|
| RAG [1] | Factual grounding, citations, freshness, access control | Retrieval latency, multi-hop complexity |
| Fine-tuning | Style/tone, reasoning patterns, domain behavior | No citations, stale, hallucination-prone for facts |
| Long context | Known document set, single-doc QA, code analysis | Cost per query, lost-in-the-middle [7], no scalability |
| RAG + Fine-tuning | Enterprise production — domain reasoning + factual grounding | Most complex to build and maintain |

Decision: Need citations? RAG. Need freshness? RAG. Need access control? RAG. Need to change model behavior/style? Fine-tune. Millions of documents, thousands of users? RAG.

**Hard follow-up:** Users say answers "don't sound like us" — do you fine-tune?

> First try prompt engineering with few-shot examples of desired tone. If insufficient, light fine-tuning on domain Q&A pairs for tone (not knowledge). The fine-tuned model generates in the right style; RAG provides factual grounding.

### Q12: How do you handle document freshness and real-time updates?

> **Quick answer:** Freshness strategy depends on acceptable staleness: batch nightly for bulk corpus + incremental hourly for recent changes + real-time CDC for critical sources.

| Staleness Tolerance | Architecture | Complexity |
|---------------------|--------------|------------|
| Days | Batch re-index (nightly ETL) | Low |
| Hours | Scheduled incremental indexing | Medium |
| Minutes | CDC → streaming index updates | High |
| Seconds | Real-time index + cache invalidation | Very high |

Enterprise pattern: batch nightly for bulk + incremental hourly for modified docs + real-time for policy docs. Attach "last updated" timestamps to chunks; refuse or caveat if critical doc hasn't been updated within expected window.

**Hard follow-up:** A document was updated 5 minutes ago but the index hasn't caught up. User asks about updated content.

> Depends on staleness tolerance. For hours-tolerance, system answers from stale content (acceptable tradeoff). For critical queries, add a "freshness check" — before answering about a doc, check source for latest version. Alternatively, route known-volatile queries through a direct-read path bypassing the index.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): Embedding Space Geometry — Cosine Similarity Limitations and Anisotropy</strong></summary>

Dense embeddings trained with contrastive objectives (e.g., InfoNCE: `L = -log(exp(sim(q,d+)/tau) / sum(exp(sim(q,d)/tau)))`) optimize for semantic neighborhood — pulling paraphrases together, pushing unrelated content apart [2]. This creates geometric properties that limit retrieval precision.

**Cosine similarity limitations:**

Cosine similarity measures angular distance: `cos(a,b) = a . b / (||a|| ||b||)`. It ignores magnitude and assumes uniform isotropy — that vectors uniformly occupy the hypersphere. In practice, embedding spaces are highly anisotropic: vectors cluster in a narrow cone, making most pairwise cosine similarities fall in [0.5, 1.0] rather than [-1, 1]. This compression means the *effective dynamic range* for distinguishing relevant from irrelevant is tiny (often <0.15 cosine units).

**Anisotropy problem:**

For a d-dimensional embedding space, if the mean vector mu != 0, all vectors have positive cosine with mu, creating a baseline similarity floor. Formally: `E[cos(x, y)] = ||mu||^2 / (||mu||^2 + sigma^2)` where sigma^2 is the per-dimension variance. When training data is domain-specific, mu drifts and this floor rises toward 1.0, making cosine near-useless for discrimination.

Mitigation: subtract the mean vector (centering), apply whitening transform W = Sigma^{-1/2} to equalize variance across dimensions. Post-hoc whitening recovers 3-5% recall on narrow-domain corpora.

**Matryoshka Representation Learning (MRL)** [12]:

MRL trains embeddings so that any prefix of dimension d' < d forms a valid (lower-quality) embedding: `L_MRL = sum_{d' in D} L_contrastive(x[:d'])` where D = {32, 64, 128, 256, 512, 768}. This enables adaptive retrieval: use 64-dim for coarse candidate generation (16x storage savings), then full 768-dim for re-scoring top-100. Empirically, 256-dim Matryoshka embeddings retain 97% of 768-dim recall@10 at 3x compression [12].

**Production implication**: For enterprise RAG with 100M+ chunks, use Matryoshka embeddings at 256-dim for the HNSW index (saves ~67% memory) and full-dimension for the reranking stage.

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): HNSW Index Internals — Layer Construction, Search, and Memory-Accuracy Trade-offs</strong></summary>

HNSW (Hierarchical Navigable Small World) [5] builds a multi-layer skip-list-like graph for approximate nearest neighbor search. Understanding its internals is critical for tuning production vector stores.

**Layer construction:**

Each vector is inserted into layer 0 (densest) and probabilistically promoted to higher layers. Promotion probability: `p(l) = exp(-l * mL)` where `mL = 1/ln(M)`. This creates a geometric distribution — layer l has approximately N/M^l nodes. At each layer, the inserted node connects to its M nearest already-inserted neighbors found via greedy search with beam width `ef_construction`.

**Graph connectivity:**

- `M` (connections per node): Typically 16-64. Layer 0 uses M0 = 2*M for higher connectivity.
- `ef_construction`: Search width during insertion (100-400). Higher = better graph quality, slower build.
- Total edges: approximately `N * M * avg_layers = N * M * (1 + 1/ln(M))`.

**Search algorithm:**

```
function SEARCH(query, K):
  entry_point = top_layer_entry
  for layer = top_layer down to 1:
    entry_point = greedy_search(query, entry_point, ef=1)  // navigate
  candidates = beam_search(query, entry_point, ef=ef_search)  // layer 0
  return top_K(candidates)
```

Search complexity: O(log(N) * M) for navigation layers + O(ef_search * M) for layer 0. Total: O(log(N) * M + ef_search * M). The ef_search parameter is the primary recall-latency knob at query time.

**Memory-accuracy trade-off at scale:**

For N=100M vectors, d=768 dimensions:
- HNSW full precision: N * (d * 4 + M * 2 * 4 * avg_layers) = 100M * (3072 + 512) ~ 358 GB
- HNSW with scalar quantization (INT8): 100M * (768 + 512) ~ 128 GB, recall@10 ~ 99%
- IVF-PQ (64 bytes/vector): 100M * 64 ~ 6.4 GB, recall@10 ~ 85-90%

The production decision: if corpus fits in RAM with HNSW, use it. If not, use IVF-PQ with cross-encoder reranking on top-50 to recover recall to ~93% [5].

**Key tuning insight**: ef_search has diminishing returns — doubling from 100 to 200 typically gains 1-2% recall but doubles latency. Profile on your data to find the knee of the curve.

</details>

<details><summary><strong>DE Probe 3 (DATA): Chunking Strategies — Semantic vs Fixed-Size, Overlap, and Metadata Preservation</strong></summary>

Chunking determines the atomic unit of retrieval — bad chunks poison everything downstream. The core tension: smaller chunks improve retrieval precision but lose context; larger chunks preserve discourse but dilute signal and waste the context window.

**Fixed-size chunking:**

Split text at N-token boundaries (typically 300-500). Advantages: deterministic, fast, uniform index. Failures: breaks mid-sentence, severs table rows, separates a claim from its evidence. Overlap (10-20%) partially mitigates boundary loss: chunk_i covers tokens [i*stride, i*stride + size] where stride = size * (1 - overlap). At 20% overlap with 400-token chunks, index size grows by 25%.

**Semantic chunking:**

Split on topic boundaries detected by embedding similarity drop between consecutive sentences. Algorithm:

```
for each sentence pair (s_i, s_{i+1}):
  sim = cosine(embed(s_i), embed(s_{i+1}))
  if sim < threshold:  // topic boundary
    create_split()
```

Produces variable-size chunks (100-1000 tokens). Higher quality but expensive: requires embedding every sentence during indexing. Threshold calibration is corpus-specific — too low = few splits (giant chunks), too high = many splits (fragments).

**Contextual chunking** [14]:

Anthropic's approach prepends a document-level context sentence to each chunk: "This chunk is from [Document Title], Section [X], discussing [topic summary]." Each chunk becomes self-contained — no longer depends on surrounding chunks for interpretation. Reported 49% fewer retrieval failures. Cost: ~50-100 extra tokens per chunk (increases index size by 15-25%).

**Metadata preservation strategy:**

Every chunk must carry: (1) document_id + version, (2) section hierarchy (heading path), (3) position (page/section number), (4) creation/modification timestamp, (5) access control tags, (6) content type (prose, table, code, list). This metadata enables: filtering at retrieval, freshness checks, access control, and debugging.

**Hierarchical chunking for decoupled granularity:**

Store chunks at multiple levels — sentence (50 tokens), paragraph (200 tokens), section (800 tokens). Retrieve at sentence level for precision, expand to parent section for generation context. This decouples retrieval granularity from synthesis granularity without compromise.

**Decision framework**: Start section-aware at ~400 tokens. If recall on factual queries is low, go smaller. If answers lack coherence, go larger or add hierarchical expansion. Always add contextual prepending [14] — it is nearly free relative to its impact.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): RAG Evaluation Frameworks — Faithfulness, Relevance, and RAGAS Metrics</strong></summary>

Evaluating RAG requires metrics at every component — retrieval quality alone does not predict answer quality, and end-to-end metrics alone cannot diagnose failures [8].

**RAGAS framework** [8] defines four core metrics:

1. **Faithfulness** — What fraction of claims in the answer are supported by the retrieved context? Computed by: (a) decompose answer into atomic claims, (b) for each claim, check if context entails it via NLI. Score = supported_claims / total_claims. Target: >0.95 for production.

2. **Answer Relevance** — Does the answer address the question? Computed by generating N synthetic questions from the answer, then measuring cosine similarity between synthetic questions and the original. Low score indicates off-topic answers.

3. **Context Precision** — Are the retrieved contexts ranked by relevance? Computed as weighted precision where higher-ranked relevant contexts contribute more. Measures ranking quality independent of generation.

4. **Context Recall** — Does the retrieved context contain all information needed to answer? Computed by decomposing the ground-truth answer into claims and checking context coverage.

**Metric correlations and failure modes:**

| Failure | Faithfulness | Context Recall | Diagnosis |
|---------|-------------|----------------|-----------|
| Hallucination | LOW | HIGH | Generation problem — correct context, wrong answer |
| Missing info | HIGH | LOW | Retrieval problem — wrong context retrieved |
| Both bad | LOW | LOW | Retrieval AND generation failing |
| System working | HIGH | HIGH | Monitor for regression |

**LLM-as-Judge vs NLI models:**

LLM judges (GPT-4, Claude) achieve ~0.85 correlation with human faithfulness judgments at the system level but only ~0.65 at instance level [8]. NLI models (DeBERTa-based) are faster (10ms vs 2s) and cheaper but handle only atomic entailment — they miss multi-sentence reasoning chains.

**Production evaluation protocol**: Run RAGAS metrics [8] daily on 200 golden-set queries. Alert when faithfulness drops below 92% or context recall below 85%. Slice by document type and query complexity — aggregate metrics hide failure pockets in specific query categories.

**Limitation of automated metrics**: RAGAS assumes claim decomposition is correct — but claim extraction itself has ~90% accuracy. This means ~10% of faithfulness measurements are noise. Calibrate against monthly human evaluation on 100 samples.

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Hallucination Detection and Attribution — Grounding Verification at Inference Time</strong></summary>

Post-generation hallucination detection is the last line of defense — it catches failures that prompting alone cannot prevent [7][9]. The challenge: verification must be fast enough to not block response delivery and accurate enough to not refuse correct answers.

**Inference-time grounding verification pipeline:**

```
Step 1: Decompose response into atomic claims
  "Revenue grew 15% in Q3, driven by APAC expansion"
  → ["Revenue grew 15% in Q3", "Growth was driven by APAC expansion"]

Step 2: For each claim, find best-matching span in retrieved context
  → Use token-level similarity or NLI to locate supporting evidence

Step 3: Score entailment (support, contradict, neutral)
  → NLI model: P(entailment | context, claim) > threshold?

Step 4: Action based on verification result
  → All supported: serve response
  → Partially supported: serve with caveats on unsupported claims
  → Contradicted: regenerate with stricter constraints or refuse
```

**Self-RAG approach** [9]: Instead of a separate verification step, Self-RAG trains special tokens into the model: [Retrieve] (should I retrieve?), [IsREL] (is retrieved passage relevant?), [IsSUP] (does passage support my response?), [IsUSE] (is response useful?). The model generates these tokens inline, enabling real-time self-assessment without external verifiers. This reduces unnecessary retrieval by ~20% and hallucination by 10-15%.

**Attribution granularity:**

Sentence-level attribution ("This sentence is supported by Chunk #3") vs claim-level attribution ("The revenue figure is from Chunk #2; the APAC claim is from Chunk #5"). Claim-level is more precise but 3-5x more expensive (requires NLI per claim, not per sentence).

**Production considerations:**

- Latency budget: NLI models add 10-50ms for 5 claims; LLM-based verification adds 200-500ms
- False refusal rate: if verification threshold is too strict, >5% of correct answers get blocked
- Calibration: start with NLI-based scoring, set threshold at 0.7 (permissive), measure false refusals on golden set, tighten gradually
- When models confabulate despite correct context [7]: often caused by context noise (irrelevant chunks diluting signal). Reducing from 5 to 3 highly-relevant chunks can reduce hallucination more than any verification layer.

**Key insight**: Hallucination detection is necessary but not sufficient — the highest-leverage investment is preventing hallucination through better retrieval, chunking, and context curation rather than catching it post-hoc.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Hybrid Retrieval — BM25 + Dense, Reciprocal Rank Fusion, and Query Routing</strong></summary>

Hybrid retrieval combines the complementary strengths of sparse (lexical) and dense (semantic) retrieval [6][11]. BM25 excels at exact term matching with IDF weighting (rare terms get HIGH weight); dense embeddings excel at semantic matching (paraphrases, synonyms). Neither alone is sufficient for enterprise corpora.

**BM25 scoring** [6]:

```
BM25(q, d) = sum_{t in q} IDF(t) * (tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d|/avgdl))
```

Where IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5)). Key property: rare terms (low df) get high IDF — the exact inverse of embedding failure modes on uncommon terms. Parameters: k1=1.2 (term frequency saturation), b=0.75 (length normalization).

**Reciprocal Rank Fusion (RRF)** [11]:

```
RRF_score(d) = sum_{r in rankers} 1 / (k + rank_r(d))
```

Where k=60 (standard constant that dampens the influence of high-ranked documents). RRF is parameter-free beyond k, requires no score normalization (unlike CombSUM which requires calibrated scores), and empirically outperforms learned fusion on diverse query types [11].

**Why RRF over learned fusion:**

Learned fusion (e.g., linear combination with tuned weights) requires: (1) labeled data per query type, (2) score calibration across retrieval systems, (3) retraining when either retriever changes. RRF is robust to score distribution differences — it only uses rank ordinals, making it invariant to retriever updates.

**Query routing architecture:**

Not all queries benefit from both retrievers. Production router:

| Query Signal | Route | Rationale |
|-------------|-------|-----------|
| Contains product code, ID, or exact phrase | BM25-heavy (weight 0.7/0.3) | Lexical match dominates |
| Semantic/paraphrase ("how do I...") | Dense-heavy (weight 0.3/0.7) | Embedding captures intent |
| Ambiguous / mixed | Equal RRF (0.5/0.5) | Let fusion decide |
| Multi-hop detected | Iterative with both | Each sub-query may need different balance |

Implementation: lightweight classifier (logistic regression on query features: length, entity count, question-word presence) routes queries with <1ms overhead. Alternatively, run both always and let RRF handle it — the cost of running BM25 is negligible (<5ms), so routing mainly saves dense-retrieval latency for queries where BM25 alone suffices.

**Enterprise validation**: On corpora with product codes, legal citations, and domain acronyms, hybrid retrieval with RRF improves recall@10 by 15-25% over dense-only, with the largest gains on exact-term queries [6][14].

</details>

## Cost Model

### Per-Query Cost Breakdown

| Component | Cost/Query | Assumptions | Optimization Lever |
|-----------|-----------|-------------|-------------------|
| Query embedding | $0.00002 | text-embedding-3-small, 768-dim | Cache repeated queries |
| Vector search (managed) | $0.00005 | Pinecone serverless, 10M vectors [15] | Self-hosted pgvector at lower scale |
| BM25 search | $0.00001 | Elasticsearch/OpenSearch | Co-located with vector store |
| Reranking (cross-encoder) | $0.0003 | 20 candidates, bge-reranker-large | Skip for simple queries |
| Generation (input tokens) | $0.005 | 5 chunks x 400 tokens = 2000 tokens, Claude Haiku | Fewer chunks, shorter chunks |
| Generation (output tokens) | $0.003 | ~500 output tokens, Claude Haiku | Length limits, concise prompting |
| **Total (simple query)** | **~$0.008** | Haiku, 5 chunks, no reranker | |
| **Total (complex query)** | **~$0.04** | Sonnet, reranker, multi-hop (2 LLM calls) | |

### Monthly Cost at Scale

| Scale | Queries/Day | Monthly Cost | Cost/Answer | Key Optimization |
|-------|------------|-------------|-------------|-----------------|
| Pilot (1K users) | 5,000 | ~$1,200 | $0.008 | Full pipeline, no optimization |
| Growth (50K users) | 100,000 | ~$15,000 | $0.005 | Caching (30%), routing to small model |
| Scale (1M+ users) | 2,000,000 | ~$120,000 | $0.002 | Caching (40%), routing (60% Haiku), reduced chunks |

### Cost Optimization Priority Stack

| Priority | Optimization | Savings |
|----------|-------------|---------|
| 1 | Reduce prompt size (fewer/shorter chunks) | 3-5x on generation cost |
| 2 | Model routing (simple → small model, complex → large) | 2-3x overall |
| 3 | Semantic caching (25-40% hit rate in enterprise) | 1.3-1.5x |
| 4 | Selective reranking (skip for high-confidence simple queries) | 1.2x |
| 5 | Matryoshka embeddings for index compression [12] | 60-70% storage savings |

### Build vs Buy

| Component | Managed | Self-Hosted | Recommendation |
|-----------|---------|-------------|----------------|
| Vector DB | Pinecone ($70/mo per 1M vectors) [15] | pgvector (compute only) | Managed if <10M vectors; self-host if 100M+ or data residency |
| Embedding | OpenAI/Cohere API ($0.02/1M tokens) | Sentence-transformers on GPU | API if <1M queries/day; self-host if need fine-tuning |
| LLM Generation | Claude/GPT API (pay per token) | vLLM + open-source on GPU | API for quality-critical; self-host for high-volume cost savings |
| Reranker | Cohere Rerank ($1/1K searches) | bge-reranker on GPU | API for simplicity; self-host if latency-sensitive |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Retrieval recall (golden set, daily) | <90% (baseline 95%) | ML on-call: embedding drift or index corruption |
| Faithfulness rate | <92% (baseline 96%) | ML on-call: prompt degradation or model regression |
| Hallucination rate (unsupported claims) | >5% | Immediate: block deployment |
| Latency p50 / p95 | p50 >2s or p95 >8s | Infra on-call: check generation queue |
| Cache hit rate | <15% (baseline 30%) | Investigate: invalidation bug or distribution shift |
| Zero-result rate | >3% | Content gap: corpus coverage issue |
| Access control violations | Any non-zero | Security: immediate investigation |

### Debugging Walkthrough

```
Symptom: User reports wrong answer
├── Check 1: Freshness — Is the source document up-to-date in index?
│   └── Stale → Re-index; check CDC pipeline
├── Check 2: Retrieval — Is correct doc in top-20?
│   └── Missing → Embedding/chunking problem; check query-doc alignment
├── Check 3: Ranking — Is correct doc in top-5 passed to LLM?
│   └── Ranked low → Reranker issue; check reranker model version
├── Check 4: Context noise — Do irrelevant chunks dilute signal?
│   └── Yes → Reduce K, improve chunk relevance filtering [7]
└── Check 5: Generation — Feed only correct chunk; does model answer correctly?
    └── Still wrong → Generation failure; stricter prompting, lower temperature
```

### Versioning & Rollback

| Component | Versioning Strategy | Rollback Method |
|-----------|-------------------|----------------|
| Embedding model | Separate index per version; alias routing | Swap alias to previous index |
| Chunking strategy | Reindex into new collection | Alias swap |
| Prompt template | Version in config store; logged per request | Config rollback (seconds) |
| Generation model | Model ID logged per request | Route to previous model |
| Reranker | Model version in traces | Disable reranker (retrieval-only fallback) |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| User thumbs down + correction | Highest — specific failure with ground truth | UI button (3-5% response rate) |
| Regeneration requests | Implicit rejection (don't know why) | Log regeneration events |
| Citation click-through | Trust/verification signal | Link tracking |
| Session abandonment | System failed to help | Session analytics |
| Helpdesk ticket after RAG query | Worst failures — user escalated | Ticket system integration |
| Document update frequency | Which docs go stale fastest | Source metadata |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Daily | Retrieval recall monitoring on golden set | Automated; alert on regression |
| Weekly | Add failing queries to eval set; retune chunking | >10 new failure patterns clustered |
| Monthly | Embedding model evaluation; prompt optimization | A/B test shows >5% improvement |
| Quarterly | Full re-index with new chunking/embedding strategy | Offline eval shows >10% recall gain |

> [!experience] The most common production failure is stale subsections within an "updated" document — a doc current at the doc level can have stale subsections. This motivates section-level freshness tracking, not just doc-level.

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Self-RAG [9] | Over-retrieval, unnecessary latency | When many queries don't need retrieval | All queries need retrieval |
| GraphRAG [13] | Global/theme questions over large corpora | "Summarize all X" or "What are the main themes?" | Factual point queries |
| Agentic RAG | Multi-step reasoning with tool-calling | Multi-hop, iterative refinement needed | Simple factual lookups |
| Contextual Retrieval [14] | Chunk-boundary information loss | Mixed doc types, chunks lose meaning in isolation | Already self-contained chunks |
| Matryoshka Embeddings [12] | Storage cost at scale | 100M+ vectors needing compression | Small corpora where storage is cheap |
| Query Routing | One-size-doesn't-fit-all pipeline | Mixed query types (factual vs synthesis) | Homogeneous query distribution |
| Hybrid BM25+Dense [6][11] | Exact-term misses from dense-only | Enterprise docs with codes, acronyms, IDs | Pure semantic corpus with no exact terms |
| RETRO-style retrieval [4] | Conditioning generation on retrieved tokens at training | Building retrieval-native models | Using off-the-shelf LLMs |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|----------------|----------------------|
| "We use vector search and BM25" | "Hybrid retrieval is necessary for enterprise — the question is fusion strategy (RRF vs learned) and when to route to one vs both [11]" |
| "We chunk at 512 tokens" | "Chunking is the most underrated component — we measure retrieval recall to find optimal size and use hierarchical chunking to decouple retrieval granularity from synthesis granularity [14]" |
| "We add a reranker" | "Reranking is the single highest-leverage improvement, but not always worth the latency — I apply it selectively based on query routing" |
| "We test with RAGAS" | "We evaluate at three layers: component (retrieval recall, NDCG), end-to-end (faithfulness, correctness), and user-level (regeneration rate). Aggregate metrics hide failure pockets [8]" |
| "We prevent hallucination with prompting" | "Hallucination is often a retrieval signal, not a generation problem — before adding prompt constraints, check whether correct context reaches the model [7]" |
| "We scale with more GPUs" | "Token economics dominate. The highest-leverage cost optimization is reducing prompt size — fewer chunks, shorter chunks, smarter routing. Hardware doesn't fix architecture problems" |

## References

### Foundational Papers

- [1] Lewis et al. (2020) — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — arXiv:2005.11401 — Introduced the RAG architecture combining parametric and non-parametric memory for knowledge-intensive tasks.
- [2] Karpukhin et al. (2020) — *Dense Passage Retrieval for Open-Domain Question Answering* — arXiv:2004.04906 — Established dense retrieval with bi-encoders as competitive with BM25; introduced DPR training methodology.
- [3] Izacard & Grave (2021) — *Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering* — arXiv:2007.01282 — Fusion-in-Decoder: demonstrated multi-passage generation outperforms single-passage by fusing evidence.
- [4] Borgeaud et al. (2022) — *Improving Language Models by Retrieving from Trillions of Tokens (RETRO)* — arXiv:2112.04426 — Showed retrieval-augmented training at trillion-token scale with chunked cross-attention.
- [5] Malkov & Yashunin (2018) — *Efficient and Robust Approximate Nearest Neighbor using Hierarchical Navigable Small World Graphs* — arXiv:1603.09320 — The HNSW algorithm powering most production vector search systems.
- [6] Robertson & Zaragoza (2009) — *The Probabilistic Relevance Framework: BM25 and Beyond* — Foundations and Trends in IR — Definitive reference for BM25 scoring and the probabilistic relevance framework.

### Architecture & Production

- [7] Shi et al. (2023) — *Large Language Models Can Be Easily Distracted by Irrelevant Context* — arXiv:2302.00093 — Demonstrated that irrelevant retrieved passages degrade LLM accuracy by 20-30%; motivates context curation.
- [9] Asai et al. (2024) — *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* — arXiv:2310.11511 — Model learns when to retrieve and self-evaluates output quality via reflection tokens.
- [11] Cormack et al. (2009) — *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods* — SIGIR 2009 — Introduced RRF as a simple, parameter-free rank fusion method for combining multiple retrieval systems.
- [12] Kusupati et al. (2022) — *Matryoshka Representation Learning* — arXiv:2205.13147 — Training embeddings where any dimension prefix is a valid lower-dimensional embedding; enables adaptive-precision retrieval.

### Evaluation & Frameworks

- [8] Es et al. (2024) — *RAGAS: Automated Evaluation of Retrieval Augmented Generation* — arXiv:2309.15217 — Defined faithfulness, answer relevance, context precision, and context recall metrics for RAG evaluation.
- [10] Gao et al. (2024) — *Retrieval-Augmented Generation for Large Language Models: A Survey* — arXiv:2312.10997 — Comprehensive survey covering RAG paradigms, enhancement methods, and evaluation approaches.

### Industry & Systems

- [13] Microsoft (2024) — *GraphRAG: Graph-based Retrieval Augmented Generation for Complex Queries* — github.com/microsoft/graphrag — Graph-based RAG using community detection for global/theme queries over large corpora.
- [14] Anthropic (2024) — *Contextual Retrieval* — anthropic.com/news/contextual-retrieval — Prepending document context to chunks reduced retrieval failures by 49%; combined with BM25 reduced failures by 67%.
- [15] Pinecone — *Vector Database Documentation* — docs.pinecone.io — Reference implementation for managed vector search with metadata filtering and hybrid search.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; added diverse DE probes (math/systems/data/eval/production/architecture), enforced length and citation constraints, removed appendix and sub-Q&A banks |
