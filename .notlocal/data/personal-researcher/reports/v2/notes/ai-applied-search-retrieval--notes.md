# AI Applied to Search & Ads Retrieval: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-30 | **Read time:** ~18 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[search-retrieval]] — Infrastructure fundamentals: BM25, dense retrieval, SPLADE, ColBERT, hybrid pipelines
> - [[genai-search-ads]] — Business/industry angle: ad revenue models, campaign automation, agentic commerce
> - [[orc-evolution--notes]] — Full 13-phase evolution of LLM planning & orchestration

---

## Quick Catchup

> **Quick Catchup (July 2026):** AI in search+ads retrieval has evolved from LLM-based query rewriting (2023) through generative retrieval, LLM-as-ranker, and RAG pipelines to fully agentic search systems that plan multi-step retrieval strategies, reformulate queries, evaluate evidence, and synthesize answers autonomously.
> Key players: Google (AI Overviews, Gemini ranking), Perplexity (agentic search), OpenAI (SearchGPT/ChatGPT Search), Microsoft (Bing Copilot), Amazon (COSMO for product search). Main open problem: balancing retrieval accuracy with generation faithfulness — LLMs can hallucinate beyond what retrieved documents support.
> Recent breakthrough: Agentic search pipelines (2025-2026) autonomously decompose complex queries, run parallel retrievals, evaluate evidence quality, and synthesize — outperforming single-shot RAG by 30-50% on multi-hop benchmarks [1]. Trend: from "LLM rewrites query for traditional retrieval" to "LLM IS the retrieval orchestrator."

## State of the Art

### Current Best Approaches

- **Agentic search pipelines** — LLM plans retrieval strategy, reformulates queries, evaluates evidence, iterates until satisfied [1][2]
- **LLM-based query understanding** — Replace rule-based NER/intent/rewriting with instruction-tuned LLMs for zero-shot query expansion and reformulation [3][4]
- **LLM-as-ranker (listwise reranking)** — LLMs score or rerank candidate sets directly, outperforming cross-encoders on many benchmarks [5][6]
- **Generative retrieval** — Models generate document identifiers directly from queries, bypassing index lookup entirely [7]
- **RAG (Retrieval-Augmented Generation)** — Retrieve → Read → Generate pipeline; dominant pattern for grounded LLM responses [8]
- **Ads relevance via LLM** — LLM-based ad-query matching replaces keyword overlap; enables broad-match at high precision [9]

### Recent Breakthroughs (last 12 months)

- **2025-2026:** Agentic search (Perplexity, Google AI Overviews) deploys multi-step retrieval with self-evaluation, replacing single-shot RAG
- **2025:** COSMO (Amazon) applies LLM reasoning to product search — understanding shopping intent beyond keyword matching [10]
- **2025-2026:** Google AI Max uses Gemini to match ad intent without explicit keywords — 14% more conversions [9]
- **2024-2025:** Listwise LLM reranking (RankGPT, LRL) demonstrates that LLMs outperform fine-tuned cross-encoders on BEIR/TREC [5][6]

### Open Problems

- **Hallucination in grounded generation**: LLMs generate claims not supported by retrieved documents — the attribution/faithfulness problem
- **Latency at scale**: LLM-based ranking and query understanding add 100-500ms per query; infeasible for P99 < 200ms SLAs without distillation
- **Cost of LLM-in-the-loop**: Using frontier LLMs for every query is 100-1000x more expensive than traditional retrieval
- **Ads relevance vs. revenue optimization**: LLM-based ad matching improves relevance but may reduce ad diversity/competition
- **Evaluation**: Traditional IR metrics (nDCG, MRR) don't fully capture generative answer quality or agentic search effectiveness

## Executive Summary

AI applied to search+ads retrieval is the use of LLMs and agentic AI systems to improve every stage of the retrieval pipeline — from understanding what the user wants, through finding relevant documents, to ranking and synthesizing results into answers.

The core architectural question: **where in the retrieval stack do you insert the LLM?** Query understanding (cheapest), reranking (moderate), full generation (most expensive), or orchestration of the entire pipeline (agentic).

- **Choose LLM query rewriting** when you want quick wins on existing infrastructure (BM25/dense retrieval stays the same)
- **Choose LLM-as-ranker** when you have a good candidate set but poor ranking, and can afford inference latency
- **Choose RAG** when the task requires synthesized answers grounded in retrieved evidence
- **Choose agentic search** when queries are complex/multi-hop and require planning, iteration, and evidence evaluation
- **Choose LLM ads matching** when keyword-based ad relevance underperforms on broad/intent-based queries

**The killer insight:** "The LLM's role in search is evolving from 'helper' (rewrite my query) to 'orchestrator' (plan, retrieve, evaluate, iterate, synthesize). The end state is that the search engine IS an agent — retrieval becomes one tool among many."

```
LLM Integration Points in Search+Ads Retrieval
──────────────────────────────────────────────────────────────────────
Query side         Retrieval         Ranking           Response
──────────         ─────────         ───────           ────────
Query rewriting    Generative        LLM-as-ranker     RAG synthesis
Intent detection   retrieval         Listwise rerank   Answer generation
Entity extraction  (generate docIDs) Relevance scoring Summarization
Expansion/reformu- Dense embeddings  Ad matching       Citation
lation             (LLM-generated)                     attribution

         ┌─── Agentic layer (plans + orchestrates all of the above) ───┐
```

---

## Evolutionary Stages

### Stage 1 — LLM-Enhanced Query Understanding (2023)

**Goal:** Replace rule-based query preprocessing (NER, intent, rewriting) with LLMs for better coverage and zero-shot generalization.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| Query2Doc [3] | 2023 | LLM generates a pseudo-document from the query → appended to query for retrieval; simple and effective |
| HyDE [4] | 2023 | Hypothetical Document Embeddings — LLM generates a hypothetical answer, embed it, use as dense query |
| GRF (Generative Relevance Feedback) | 2023 | LLM generates expansion terms based on initial retrieval results |

**Key transition:** LLMs generate richer query representations than rule-based systems — zero-shot, no domain-specific training needed. A single prompt replaces spell correction + entity detection + intent classification + query expansion. But adds latency (one LLM call per query).

### Stage 2 — LLM-as-Ranker (2023-2024)

**Goal:** Use LLMs directly for relevance scoring, replacing or augmenting cross-encoder rerankers.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| RankGPT [5] | 2023 | Instruction-tuned LLM performs listwise reranking via permutation generation; zero-shot SOTA on BEIR |
| LRL (Listwise Reranker via LLM) [6] | 2024 | Efficient listwise reranking with sliding window; outperforms pointwise and pairwise approaches |
| PRP (Pairwise Ranking Prompting) | 2023 | LLM compares document pairs for ranking; strong but O(n²) |
| RankLLaMA | 2024 | Fine-tuned LLaMA for reranking; bridging zero-shot and trained approaches |

**Key transition:** LLMs outperform fine-tuned cross-encoders on many IR benchmarks without task-specific training. Listwise approaches (present N documents, ask for ranking) dominate over pointwise (score each independently). The cost: 100-1000x more expensive than a trained cross-encoder at inference.

### Stage 3 — Generative Retrieval (2022-2024)

**Goal:** Skip the index entirely — have the model generate document identifiers directly from the query.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| DSI (Differentiable Search Index) [7] | 2022 | Model memorizes corpus; generates docIDs token-by-token given a query |
| GENRE | 2022 | Autoregressive entity retrieval via constrained generation |
| SEAL | 2023 | Search engine with autoregressive LLMs; generates passage ngrams as identifiers |

**Key transition:** Collapses indexing + retrieval into a single model forward pass. Elegant but struggles at corpus scale (>1M documents) and with real-time updates. Currently more research frontier than production reality — but points toward a future where retrieval is fully neural.

### Stage 4 — RAG: Retrieval-Augmented Generation (2023-2025)

**Goal:** Ground LLM generation in retrieved evidence to reduce hallucination.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| RAG (Lewis et al.) [8] | 2020 | Original retrieve-then-generate; retriever provides context for generator |
| Self-RAG | 2023 | Model decides when to retrieve, what to retrieve, and self-evaluates relevance |
| CRAG (Corrective RAG) | 2024 | Evaluates retrieval quality; triggers web search if initial retrieval is insufficient |
| Adaptive RAG | 2024 | Routes queries: no retrieval (simple) vs. single-retrieval vs. multi-step (complex) |

**Key transition:** RAG becomes the dominant pattern for production LLM applications (enterprise search, customer support, coding assistants). The evolution: basic RAG → self-evaluating RAG → adaptive/corrective RAG that knows when retrieval failed and takes corrective action. This is the bridge to agentic search.

### Stage 5 — LLM for Ads Retrieval & Matching (2024-2026)

**Goal:** Replace keyword-based ad-query matching with LLM-powered semantic relevance scoring.

| System | Year | Core Contribution |
|--------|------|-------------------|
| Google AI Max [9] | 2025 | Gemini matches ad intent without explicit keywords; 14% more conversions |
| Amazon COSMO [10] | 2025 | LLM reasoning for product search — understands shopping intent beyond keywords |
| Microsoft Ads broad match | 2024+ | LLM-based query-ad semantic matching enables broad match at high precision |
| Meta Advantage+ targeting | 2024+ | AI-driven audience expansion beyond explicit targeting parameters |

**Key transition:** Ads retrieval shifts from "match keywords" to "match intent." LLMs understand that a query for "comfortable work shoes" is relevant to an ad for "ergonomic office footwear" without explicit keyword overlap. This expands the addressable ad inventory but raises concerns about relevance degradation and advertiser trust.

### Stage 6 — Agentic Search Pipelines (2025-2026)

**Goal:** LLM autonomously plans and executes multi-step retrieval strategies — decomposing queries, running parallel searches, evaluating evidence, and iterating until the answer is complete.

| System | Year | Core Contribution |
|--------|------|-------------------|
| Perplexity [1] | 2024-2026 | Agentic search: decompose → retrieve → evaluate → synthesize with citations |
| Google AI Overviews | 2025 | Multi-source retrieval + LLM synthesis integrated into search results (1B+ users) |
| OpenAI SearchGPT / ChatGPT Search [2] | 2025 | Conversational search with agentic retrieval and source attribution |
| Microsoft Bing Copilot | 2024-2025 | Multi-turn search with planning, retrieval, and synthesis |
| Deep Research agents | 2026 | Multi-hour research sessions with autonomous retrieval, reading, and synthesis |

**Key transition:** The LLM becomes the search orchestrator, not just a component. The pipeline: Plan (decompose complex query) → Retrieve (multiple sources, parallel) → Evaluate (is evidence sufficient?) → Reformulate (if not) → Synthesize (generate grounded answer with citations). This outperforms single-shot RAG by 30-50% on complex multi-hop queries but costs 10-100x more per query.

#### Agentic Search Pipeline

```
Complex query
 ↓
Plan: decompose into sub-questions
 ↓
For each sub-question:
 ├── Formulate search query
 ├── Retrieve from multiple sources (web, docs, APIs)
 ├── Evaluate evidence quality
 ├── If insufficient → reformulate + re-retrieve
 └── Extract relevant facts
 ↓
Synthesize: combine facts into coherent answer
 ↓
Cite: attribute each claim to source
 ↓
Self-check: verify answer against retrieved evidence
 ↓
Return grounded answer with citations
```

### Stage 7 — Ads as Agentic Commerce (2026 — Emerging)

**Goal:** AI agents don't just find ads — they complete purchases, negotiate, and optimize campaigns autonomously.

| System | Year | Core Contribution |
|--------|------|-------------------|
| Google Direct Offers | 2026 | Native checkout within AI search via Universal Commerce Protocol |
| OpenAI Operator + Stripe | 2025-2026 | AI agent completes purchases within chat |
| Microsoft Copilot Checkout | 2025-2026 | Agent-mediated purchasing within search/assistant |

**Key transition:** Search retrieval evolves from "find and rank results" to "find, evaluate, negotiate, and execute." The agent doesn't just retrieve ads — it acts on them. This transforms the retrieval problem into an end-to-end decision-making problem where the "ranking metric" is purchase completion, not click-through.

---

## Key Themes & Connections

### Theme 1: The LLM Moves Up the Stack

```
Stage 1: LLM helps QUERY (rewriting, expansion)
 → Stage 2: LLM helps RANKING (reranking retrieved results)
  → Stage 3: LLM IS retrieval (generative retrieval)
   → Stage 4: LLM GENERATES answer from retrieval (RAG)
    → Stage 5: LLM matches INTENT for ads
     → Stage 6: LLM ORCHESTRATES entire search pipeline (agentic)
      → Stage 7: LLM EXECUTES actions (agentic commerce)
```

Each stage gives the LLM more control. The end state: the traditional search engine becomes one tool the agent can call.

### Theme 2: The Latency-Quality-Cost Trilemma

| Approach | Latency | Quality | Cost per Query |
|----------|---------|---------|----------------|
| BM25 + cross-encoder | ~50ms | Good | ~$0.001 |
| LLM query rewriting + BM25 | ~200ms | Better | ~$0.01 |
| LLM-as-ranker (listwise) | ~500ms | Best (single-shot) | ~$0.05 |
| RAG (single retrieval) | ~1s | Good + grounded | ~$0.05 |
| Agentic search (multi-step) | ~5-30s | Best (complex queries) | ~$0.50-$5.00 |

Production systems use **tiered routing**: simple queries → fast path (BM25 + reranker); complex queries → slow path (agentic). The routing decision itself can be LLM-powered.

### Theme 3: Distillation Makes LLM-Search Practical

The pattern that makes all stages production-viable:

1. **Prototype** with frontier LLM (GPT-4, Claude) — proves the approach works
2. **Distill** into a smaller model (fine-tuned 7B or custom ranker) — brings latency/cost to production levels
3. **Deploy** the distilled model at scale

Examples:
- LLM reranking → distill into fine-tuned cross-encoder (RankLLaMA)
- LLM query expansion → distill into small query rewriter
- Agentic search → compile workflow into model weights (subterranean agents)

### Theme 4: Ads Retrieval Is Converging with Organic Search

| Dimension | Traditional Ads | Traditional Organic | Converging Toward |
|-----------|----------------|--------------------|--------------------|
| Matching | Keyword bid | BM25 + semantic | LLM intent matching (both) |
| Ranking signal | CTR × bid | Relevance + engagement | Multi-objective with LLM scoring |
| Result format | Text snippet + link | Blue links → featured snippets | AI-generated answer with embedded ads/products |
| Success metric | Click/conversion | Session satisfaction | Task completion (agentic) |

The distinction between "ad retrieval" and "organic retrieval" is blurring. Both use the same LLM infrastructure, same intent understanding, same ranking approaches. The difference is the objective function (revenue vs. relevance) and the auction mechanism.

### Theme 5: Search+Ads as Offline-to-Online Policy Learning

Search ranking and ad selection are naturally policy learning problems (see [[policy-dist--notes]]):

| Component | As Policy Learning |
|-----------|-------------------|
| Query understanding | State representation |
| Ranking/ad selection | Action (which items to show, in what order) |
| Click/conversion | Reward signal |
| Session history | State transitions |
| Counterfactual evaluation | "Would a different ranking have been better?" |

This connects to offline policy learning (learn from click logs), RLVR (verify with conversion outcomes), and online policy distillation (distill strong ranker into cheap model).

---

## Reading Schedule

| Week | Papers/Systems | Central Question |
|------|---------------|-----------------|
| **1** | Query2Doc [3], HyDE [4], GRF | How do LLMs improve query representation for retrieval? |
| **2** | RankGPT [5], LRL [6], PRP, RankLLaMA | Can LLMs directly rank documents better than trained rankers? |
| **3** | DSI [7], GENRE, SEAL | Can we eliminate the index entirely with generative retrieval? |
| **4** | RAG [8], Self-RAG, CRAG, Adaptive RAG | How do we ground LLM generation in retrieved evidence? |
| **5** | Google AI Max [9], COSMO [10], Microsoft broad match | How do LLMs transform ad-query matching from keywords to intent? |
| **6** | Perplexity [1], ChatGPT Search [2], Bing Copilot, Deep Research | What does fully agentic search look like? |
| **7** | Google Direct Offers, OpenAI Operator, Copilot Checkout | How does search evolve from retrieval to action execution? |
| **8** | Distillation for search (RankLLaMA), tiered routing, cost optimization | How do we make LLM-powered search affordable at scale? |

---

## References

### Agentic Search

- [1] Perplexity AI (2024-2026) — Agentic search pipeline: decompose → retrieve → evaluate → synthesize with citations
- [2] OpenAI (2025) — *SearchGPT / ChatGPT Search* — Conversational search with agentic retrieval and source attribution

### LLM Query Understanding

- [3] Wang et al. (2023) — *Query2Doc: Query Expansion with Large Language Models* — https://arxiv.org/abs/2303.07678 — LLM generates pseudo-document appended to query for retrieval
- [4] Gao et al. (2023) — *Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)* — https://arxiv.org/abs/2212.10496 — Hypothetical document embeddings for zero-shot dense retrieval

### LLM-as-Ranker

- [5] Sun et al. (2023) — *Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents (RankGPT)* — https://arxiv.org/abs/2304.09542 — Listwise reranking via permutation generation
- [6] Ma et al. (2024) — *Listwise Reranker via LLM* — Efficient sliding-window listwise reranking outperforming pointwise/pairwise

### Generative Retrieval

- [7] Tay et al. (2022) — *Transformer Memory as a Differentiable Search Index (DSI)* — NeurIPS — Model memorizes corpus and generates docIDs from queries

### RAG

- [8] Lewis et al. (2020) — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — NeurIPS — https://arxiv.org/abs/2005.11401 — Original RAG paper

### Ads Retrieval

- [9] Google (2025) — *AI Max for Search Campaigns* — Gemini-powered intent matching without explicit keywords; +14% conversions
- [10] Amazon (2025) — *COSMO: A Large-Scale E-commerce Common Sense Knowledge Generation and Serving System* — LLM reasoning for product search intent

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| LLM query rewriting is the highest-ROI first step — it improves existing BM25/dense pipelines without changing infrastructure | Industry pattern (Google, Bing, Amazon) |
| Distill LLM rankers into fine-tuned cross-encoders before production — 100x cheaper at ~90% quality retention | RankLLaMA, ColBERT distillation literature |
| Agentic search is only worth the cost for complex/multi-hop queries (~10-20% of traffic); route the rest to traditional fast path | Perplexity architecture discussions |
| For ads, LLM-based broad match increases ad inventory coverage by 20-40% but requires careful relevance guardrails to maintain advertiser trust | Google AI Max results, Microsoft broad match |
| The "attribution problem" (citing which document supports which claim) is unsolved at production quality — current best is retrieve-then-generate with forced inline citations | RAG production deployments (2024-2026) |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-30 | Initial v2 generation (study-notes format) | Created from query on LLM + agentic AI applications in search+ads retrieval; covers query understanding → LLM ranking → generative retrieval → RAG → ads matching → agentic search → agentic commerce |
| 2026-07-30 | Filed | [UNVERIFIED] — run /verify-report --topic ai-applied-search-retrieval when runtime available |
