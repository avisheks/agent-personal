# AI-Assisted Paper Research & Agentic Literature Workflows

> **Last Updated:** 2026-06-27 | **Read time:** ~12 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** AI-assisted research has moved from single-PDF chatbots to multi-tool pipelines that handle discovery → triage → extraction → synthesis autonomously.
> Key players: NotebookLM (multi-paper reasoning), Elicit (structured evidence extraction), Claude/ChatGPT (critique + deep Q&A). Main open problem: reliable autonomous citation-graph traversal without hallucinated references.
> Recent breakthrough: NotebookLM's cross-document reasoning (2025-2026) enables comparing 50+ papers in a single workspace [1]. Trend: agentic pipelines that compose these tools via APIs into fully automated literature review systems.

## State of the Art

### Current Best Approaches

- **NotebookLM** — Upload 50+ PDFs, get cross-document summaries, FAQs, audio overviews; low hallucination due to source grounding [1]
- **Elicit** — Natural-language search returning structured evidence tables (methodology, datasets, outcomes) from academic corpora [2]
- **Semantic Scholar** — Open API providing citation graphs, paper metadata, influential citations, author disambiguation, and recommendation feeds; backbone for programmatic discovery and verification [9]
- **Claude/ChatGPT as research critic** — Upload PDF + ask for methodological weaknesses, production failure modes, and falsification experiments [3]
- **Agentic pipelines (LangGraph/custom)** — Compose discovery → triage → extraction → vector storage → synthesis as a state machine with human-in-the-loop gates [4]

### Recent Breakthroughs (last 12 months)

- **NotebookLM cross-collection reasoning** (2025): Compare themes, contradictions, and methodology gaps across paper collections — not just single-doc Q&A [1]
- **Elicit evidence tables** (2025-2026): Automated extraction of sample sizes, datasets, and comparative results into structured formats [2]
- **Claude extended context** (2026): 1M-token context enables full-paper analysis without chunking artifacts [3]
- **Papers with Code integration** (2025-2026): Automated links between papers → implementations → benchmarks → leaderboards for ML research [5]
- **Semantic Scholar Recommendation API** (2025-2026): Personalized paper feeds based on reading history + citation velocity scoring to surface high-impact preprints early [9]

### Open Problems

- **Citation graph hallucination**: LLMs fabricate plausible but non-existent references when asked to "find related work" (Semantic Scholar API enables post-hoc verification but not prevention [9])
- **Cross-paper contradiction detection**: No tool reliably identifies when Paper A's results contradict Paper B's under similar conditions
- **Agentic pipeline evaluation**: No standard benchmark for measuring literature review quality (recall, precision, synthesis coherence)
- **Cost scaling**: Full agentic pipeline on 50 papers costs $5-15 per run — prohibitive for continuous monitoring

## Executive Summary

AI-assisted paper research replaces the traditional "read everything linearly" approach with a staged pipeline where AI handles volume and humans provide judgment. The core architectural decision: **human-in-the-loop triage (higher quality, slower) vs fully autonomous pipeline (faster, quality ceiling lower)**.

- **Choose human-in-the-loop** when: evaluating papers for strategic decisions, writing publications, novel domains
- **Choose fully autonomous** when: monitoring known fields, tracking benchmarks, maintaining a research knowledge base
- **Choose hybrid** when: weekly research digests where discovery is automated but synthesis requires critique

**The killer framing:** "The bottleneck in research is not finding papers — it's deciding which ones deserve 2 hours of your time. AI tools solve discovery; an agentic pipeline solves triage; but human judgment still owns the 'so what?'"

```
Research Pipeline Decision Tree:

  Need to read papers?
       │
  ┌────┴────┐
  │ <10     │ ≥10 papers
  │ papers  │
  └────┬────┘     │
       │          ▼
  Claude/GPT   Need structured extraction?
  + PDF upload       │
                ┌────┴────┐
                │ No      │ Yes
                ▼         ▼
           NotebookLM   Elicit + Claude API
           (collection   + Vector DB
            reasoning)   (agentic pipeline)
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Volume, depth, cadence | How many papers/week? One-off survey or ongoing monitoring? Need structured data or prose summaries? |
| 2. Identify constraints | Budget, latency, quality bar | Can you tolerate 5% hallucination? Budget per paper ($0.02 triage vs $0.50 deep analysis)? Latency tolerance (real-time vs batch)? |
| 3. Propose baseline | Single-tool workflow | NotebookLM for <50 papers; Claude API + PDF upload for individual deep reads; Elicit for discovery |
| 4. Identify gaps | Coverage, structure, automation | Missing citation graph traversal? No structured extraction? No cross-paper synthesis? |
| 5. Introduce improvements | Multi-tool composition | Add Elicit for discovery → Claude for triage → NotebookLM for synthesis → pgvector for retrieval |
| 6. Add evaluation + guardrails | Hallucination detection, citation verification | Verify all extracted claims have page numbers; cross-check references against Semantic Scholar API; confidence scoring |
| 7. Discuss scaling tradeoffs | Automation vs quality, cost vs coverage | Full automation at 100+ papers/week; human gates at triage + final synthesis; model routing (Haiku for triage, Sonnet for critique) |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Discovery tool | Elicit | Papers with Code | Broad academic search across domains | ML/AI-specific with code/benchmarks needed |
| Citation traversal | Semantic Scholar API | Connected Papers | Programmatic graph traversal in automated pipelines, bulk metadata | Visual exploration, understanding field structure manually |
| Deep reading | NotebookLM | Claude API | Comparing multiple papers in collection | Single-paper critique with follow-up dialogue |
| Storage | Obsidian/Notion | PostgreSQL + pgvector | Personal notes, <100 papers | Programmatic queries, semantic search, >100 papers |
| Automation level | Human-in-the-loop | Fully agentic | Novel domain, high-stakes decisions | Monitoring known field, weekly digests |
| Extraction format | Prose summaries | Structured JSON | Sharing with non-technical stakeholders | Feeding into downstream systems/dashboards |

## System Design Walkthrough

### Opening Frame

The real engineering challenge isn't choosing between NotebookLM and Claude — it's designing the pipeline boundary between autonomous execution and human judgment gates. Every stage that runs without review compounds error; every stage that requires approval adds latency. The optimal design places gates at exactly two points: post-triage (confirm which papers deserve deep reads) and post-synthesis (confirm the narrative before it enters your knowledge base).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│            AI-Assisted Research Pipeline                          │
├────────────┬──────────────────┬──────────────────────────────────┤
│ Discovery  │  Analysis        │  Knowledge Layer                  │
│            │                  │                                   │
│ ┌────────┐ │  ┌────────────┐  │  ┌─────────────────────────────┐ │
│ │Elicit  │─┼─▶│Triage Agent│──┼─▶│Structured JSON Extraction   │ │
│ │PWC     │ │  │(Claude API)│  │  │(per-paper record)           │ │
│ │S2 API  │ │  └────────────┘  │  └─────────────────────────────┘ │
│ │ArXiv   │ │       │ ⛔       │           │                      │
│ └────────┘ │  Human gate      │           ▼                      │
│            │       │          │  ┌─────────────────────────────┐ │
│            │       ▼          │  │Embeddings + pgvector         │ │
│            │  ┌────────────┐  │  │(semantic search layer)       │ │
│            │  │Deep Reading│  │  └─────────────────────────────┘ │
│            │  │(NotebookLM/│  │           │                      │
│            │  │ Claude)    │  │           ▼                      │
│            │  └────────────┘  │  ┌─────────────────────────────┐ │
│            │       │          │  │Cross-Paper Synthesis Agent    │ │
│            │       ▼          │  │(weekly report generation)    │ │
│            │  ┌────────────┐  │  └─────────────────────────────┘ │
│            │  │Critique    │  │           │ ⛔                    │
│            │  │(Claude)    │  │      Human gate                  │
│            │  └────────────┘  │           │                      │
│            │                  │           ▼                      │
│            │                  │  ┌─────────────────────────────┐ │
│            │                  │  │Published Literature Review    │ │
│            │                  │  └─────────────────────────────┘ │
└────────────┴──────────────────┴──────────────────────────────────┘
```

- **Discovery Layer**: Queries Elicit/PWC/Semantic Scholar/ArXiv feeds for candidate papers; Semantic Scholar provides citation graphs, influential citation scoring, and recommendation feeds [9]
- **Triage Agent**: Scores each paper on novelty, depth, relevance, reproducibility (1-5 each); threshold ≥12 to proceed
- **Deep Reading**: NotebookLM for collections; Claude for individual critique with structured prompts
- **Knowledge Layer**: Structured JSON per paper → embeddings → pgvector for semantic retrieval
- **Synthesis Agent**: Clusters themes, identifies contradictions, proposes experiments from the knowledge base

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| LLMs hallucinate citations | Verify via Semantic Scholar/CrossRef API before storing | +200ms per reference, requires API keys |
| Triage scores are noisy | Calibrate against human decisions over 50+ papers, adjust thresholds | Requires initial labeling investment |
| NotebookLM not API-accessible | Use Claude 1M context as substitute for multi-paper reasoning | Higher cost ($0.50 vs $0 per collection) |
| No contradiction detection | Pairwise claim comparison with LLM-as-judge on overlapping topics | O(n²) scaling, expensive at >30 papers |
| Extraction schema drift | Version the JSON schema; validate every record against schema before storage | Reprocessing cost when schema evolves |

### Scaling Summary

- **10x (50 papers/week)**: Single pipeline instance, batch daily, one human review session/week
- **100x (500 papers/week)**: Parallel triage agents, model routing (Haiku for scoring, Sonnet for critique), dedicated vector DB
- **1000x (5000 papers/week)**: Distributed discovery across domains, hierarchical triage (fast reject → deep score), summarization layers to prevent context overflow, dedicated embedding inference

## Interview Q&A Bank

### Q1: What distinguishes an AI-assisted research pipeline from just asking ChatGPT to summarize papers?

> **Quick answer:** A pipeline provides structured extraction, persistent memory, cross-paper synthesis, and quality gates — ChatGPT gives one-shot summaries with no accumulation or verification [1][3].

A pipeline maintains state across sessions: every paper becomes a structured record (problem, method, dataset, results, limitations) stored in a searchable vector database. This enables queries like "show all papers using LLM-as-judge that report human correlation >0.8" — impossible with stateless chatbot interactions. Additionally, pipelines include verification gates (citation checking, confidence scoring) that prevent hallucinated claims from entering the knowledge base. The pipeline compounds value over time; a chatbot conversation is disposable.

**Hard follow-up:** When does the overhead of building a pipeline not justify itself over ad-hoc ChatGPT use?

> When reading <10 papers on a one-off topic you won't revisit. The pipeline's value comes from accumulation and retrieval — if there's no future query, there's no return on the extraction investment.

### Q2: How do you score papers for triage without reading them fully?

> **Quick answer:** Extract abstract + introduction + conclusion, score on 4 dimensions (novelty, technical depth, relevance, reproducibility) using a structured LLM prompt, threshold at total ≥12/20 [3].

| Dimension | Signal Source | Score Criteria |
|-----------|-------------|----------------|
| Novelty | Abstract claims, "we are the first to..." | 5 = genuinely new approach; 1 = incremental |
| Technical depth | Method section length, math density | 5 = novel algorithm/proof; 1 = prompt engineering only |
| Relevance | Keywords match to your research agenda | 5 = direct match; 1 = tangential |
| Reproducibility | Code availability, dataset access, detail level | 5 = code + data + config; 1 = no artifacts |

The key insight: triage doesn't need to be perfect. A 20% false-negative rate is acceptable — you'll catch important missed papers through citation graphs and social signals. A 10% false-positive rate just means occasionally reading a paper that doesn't pay off.

**Hard follow-up:** How do you calibrate the triage threshold over time?

> Track which papers you actually read deeply vs which you later wished you'd read. Adjust thresholds per-dimension based on recall errors. If you keep missing methodology papers, lower the "novelty" threshold and raise "technical depth" weight.

### Q3: What's the optimal structured extraction schema for research papers?

> **Quick answer:** A 12-field JSON record balancing completeness with extraction reliability: title, authors, problem, method, dataset, metrics, results, limitations, applicability, reproducibility_score, claims[], and relationships[] [4].

```json
{
  "title": "...",
  "authors": ["..."],
  "problem": "one-sentence problem statement",
  "method": "approach in 2-3 sentences",
  "dataset": "name, size, availability",
  "metrics": ["metric1", "metric2"],
  "results": "key numbers with context",
  "limitations": "author-stated + reviewer-inferred",
  "applicability": "how this applies to your domain",
  "reproducibility_score": 4,
  "claims": [{"text": "...", "evidence": "...", "confidence": 0.8}],
  "relationships": [{"paper": "...", "type": "extends|contradicts|uses"}]
}
```

The `claims[]` array is critical for cross-paper synthesis — it enables finding contradictions and convergent evidence across your corpus.

**Hard follow-up:** What fails in this schema at 500+ papers?

> The `relationships[]` field becomes O(n) to maintain per new paper. Solution: compute relationships lazily via embedding similarity at query time rather than eagerly at ingestion time.

### Q4: How does NotebookLM's cross-document reasoning differ from RAG over the same papers?

> **Quick answer:** NotebookLM reasons over the full text of uploaded documents in a single context window; RAG retrieves chunks and loses cross-document coherence [1].

NotebookLM can answer "what do papers A and B disagree on?" because both are fully in context. A RAG system retrieves relevant chunks from each paper independently — it may surface the right passages but cannot reliably detect that they contradict each other, because contradiction detection requires comparing full arguments, not isolated snippets. The tradeoff: NotebookLM is limited to ~50 documents and offers no API; RAG scales to thousands of papers with programmatic access but sacrifices synthesis quality.

**Hard follow-up:** How would you replicate NotebookLM's cross-document reasoning in a custom pipeline?

> Use Claude's 1M-token context: concatenate full texts of the top-K most relevant papers (by embedding similarity to the query), then prompt for cross-paper synthesis. Cost: ~$0.50 per synthesis query at 200K tokens input. This only works up to ~15-20 full papers per query.

### Q5: How should you use Claude vs ChatGPT vs Gemini for paper analysis?

> **Quick answer:** Claude excels at critique and finding methodological weaknesses; ChatGPT at structured extraction and summarization; Gemini at processing very long documents with its extended context [3].

| Task | Best Model | Why |
|------|-----------|-----|
| Methodological critique | Claude | Stronger at adversarial reasoning, identifying hidden assumptions |
| Structured extraction | ChatGPT (structured outputs) | JSON mode with guaranteed schema compliance |
| Very long papers (80+ pages) | Gemini 2.5 Pro | 1M+ native context, no chunking needed |
| Code analysis alongside paper | Claude | Better at connecting paper claims to implementation details |
| Quick summary for triage | Any (use cheapest) | Low-stakes task, Haiku/GPT-4o-mini sufficient |

**Hard follow-up:** When do model differences actually matter vs when is it just brand preference?

> For triage and summarization, model differences are negligible — use the cheapest. For critique (finding what's wrong with a paper) and synthesis (connecting ideas across papers), Claude consistently outperforms on adversarial reasoning tasks. The gap matters most when the paper has subtle methodological flaws that a surface-level read would miss.

### Q6: How do you convert a manual research workflow into an agentic SOP?

> **Quick answer:** Decompose each stage into inputs/actions/decision-criteria/outputs/escalation-rules, then implement as a state machine where edges are decision thresholds and nodes emit structured artifacts [4].

The conversion principle: every implicit human judgment becomes an explicit scoring function with a threshold. "Is this paper interesting?" becomes "score ≥ 12/20 on 4 dimensions." Every manual step becomes a node that produces a typed artifact. The SOP becomes executable when:

1. Every input is machine-readable (PDF → text, search query → API call)
2. Every decision has a numeric threshold (not "use judgment")
3. Every output is structured (JSON, not prose)
4. Every escalation point is defined (when to involve human)

```
SOP Node Template:
  Input:     typed artifact from previous node
  Action:    LLM call with structured output schema
  Decision:  IF score < threshold → reject ELSE → continue
  Output:    structured artifact for next node
  Escalate:  IF confidence < 0.6 → human review
```

**Hard follow-up:** What percentage of a research workflow can realistically be automated?

> ~80% of volume (discovery, triage, extraction, storage) but only ~20% of value (the insights come from synthesis and critique, which still benefit from human judgment). The automation handles the "reading 30 papers to find 5 worth your time" problem.

### Q7: How do you detect and prevent citation hallucination in an agentic pipeline?

> **Quick answer:** Never trust LLM-generated references — verify every citation against Semantic Scholar API before storage; flag any reference that returns no match [9].

Semantic Scholar's `/paper/search` endpoint is the backbone of citation verification in agentic pipelines. It covers 200M+ papers and returns structured metadata including DOI, venue, year, and citation count — all useful for validation beyond simple existence checks [9].

```python
import requests

def verify_citation(ref: dict) -> dict:
    # Semantic Scholar paper search API
    resp = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": ref["title"], "limit": 1,
                "fields": "title,doi,year,citationCount,authors"}
    )
    results = resp.json().get("data", [])
    if results and similarity(results[0]["title"], ref["title"]) > 0.9:
        ref["verified"] = True
        ref["doi"] = results[0].get("doi")
        ref["s2_id"] = results[0]["paperId"]
        ref["citation_count"] = results[0]["citationCount"]
    else:
        ref["verified"] = False
        ref["confidence"] = 0.0
    return ref
```

The failure mode is subtle: an LLM will generate a perfectly formatted reference with a real author name, plausible title, and correct venue — but the paper doesn't exist. This is undetectable without API verification. In an automated pipeline, unverified references propagate downstream and corrupt synthesis outputs. Semantic Scholar's free tier (100 requests per 5 minutes) is sufficient for verifying a batch of 20 papers' worth of references in a single pipeline run.

**Hard follow-up:** What about papers that exist but the LLM misattributes their findings?

> Extract the specific claim + page/section reference, then verify by retrieving the actual paper text and checking if the attributed claim appears. This requires access to the full text, making it expensive (~$0.10 per claim verification with an LLM comparison).

### Q8: How do you build semantic search over a research knowledge base?

> **Quick answer:** Embed each paper's structured record (not raw text) with text-embedding-3-large, store in pgvector, and query with hybrid search (embedding similarity + keyword BM25) [4].

The key design choice: embed the *structured extraction* (problem + method + results), not the full paper text. Full-text embeddings dilute signal with boilerplate (related work, acknowledgments). Structured embeddings are denser and more query-relevant.

```sql
-- Schema
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    title TEXT,
    extraction JSONB,
    embedding vector(3072),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Hybrid search: semantic + keyword
SELECT *, (embedding <=> query_embedding) * 0.7 +
          ts_rank(to_tsvector(extraction), query) * 0.3 AS score
FROM papers
ORDER BY score
LIMIT 10;
```

**Hard follow-up:** When does embedding-based search fail for research papers?

> When the query is about methodology specifics ("papers using contrastive loss with negative sampling >100") — embeddings capture semantic similarity but miss precise technical constraints. Solution: extract methodology keywords into a structured field and combine embedding search with exact-match filters.

### Q9: What's the cost model for running a weekly agentic literature review?

> **Quick answer:** ~$5-15/week for 20 papers discovered → 5 deep-read → 1 synthesis report, using model routing to minimize spend on low-value stages [3][4].

| Stage | Model | Papers | Cost/Paper | Weekly Cost |
|-------|-------|--------|-----------|-------------|
| Discovery | Elicit (free tier) | 20 | $0 | $0 |
| Triage | Haiku | 20 | $0.01 | $0.20 |
| Deep extraction | Sonnet | 5 | $0.50 | $2.50 |
| Critique | Sonnet | 5 | $0.30 | $1.50 |
| Embedding | text-embedding-3-large | 5 | $0.01 | $0.05 |
| Synthesis | Sonnet (200K context) | 1 | $3.00 | $3.00 |
| **Total** | | | | **~$7.25** |

**Hard follow-up:** How do you reduce cost without reducing coverage?

> Model routing: use Haiku for triage (90% of volume), Sonnet only for papers that pass threshold. Cache embeddings (compute once, query forever). Batch synthesis weekly instead of per-paper. Skip critique for papers with reproducibility_score ≥ 4 (well-documented papers need less skepticism).

### Q10: How would you evaluate the quality of an automated literature review?

> **Quick answer:** Compare against a human-written review on the same corpus: measure claim recall (did it find key findings?), precision (are stated facts correct?), and synthesis coherence (does the narrative make sense?) [2].

| Metric | What It Measures | How to Compute |
|--------|-----------------|----------------|
| Claim recall | Coverage of key findings | Human annotates ground-truth claims; measure % found |
| Claim precision | Accuracy of stated facts | Verify each claim against source paper |
| Citation accuracy | References are real and correctly attributed | API verification + spot-check attribution |
| Synthesis coherence | Narrative connects papers logically | LLM-as-judge with rubric (1-5) |
| Contradiction detection | Identifies when papers disagree | Inject known contradictions, measure detection rate |

**Hard follow-up:** What's the failure mode that's hardest to detect?

> Plausible but wrong synthesis — when the review connects two papers' findings in a way that sounds correct but misrepresents the causal relationship. Example: "Paper A shows X improves Y; Paper B shows Y improves Z; therefore X improves Z" — this transitivity doesn't necessarily hold, but reads convincingly.

### Q11: How do you handle the "cold start" problem when building a research knowledge base from scratch?

> **Quick answer:** Seed with 10-20 foundational papers from a trusted survey, extract structure, then use citation graphs to expand outward — don't start from keyword search [2][5].

The cold-start strategy:
1. Find 1-2 recent survey papers in your domain (these cite 50-100 relevant papers)
2. Extract the survey's reference list as your seed corpus
3. Use Semantic Scholar's `/paper/{id}/references` and `/paper/{id}/citations` endpoints to pull metadata for all referenced papers, ranked by `influentialCitationCount` [9]
4. Deep-read the top 10 most-cited papers from that list
5. Use Connected Papers for visual cluster exploration, Semantic Scholar API for programmatic graph traversal
6. Expand outward from clusters, not from keyword search

This ensures your knowledge base starts with high-quality, community-validated papers rather than whatever keyword search returns (which may include preprints, workshops, and low-impact work).

**Hard follow-up:** When should you deliberately include low-quality or negative-result papers?

> When building a critique layer: papers with known flaws serve as calibration examples for your triage agent. Include 5-10 papers you've manually rated as "not worth reading" so the triage model can learn what rejection looks like.

### Q12: What does a production-grade research agent architecture look like?

> **Quick answer:** A LangGraph state machine with 7 nodes (discover → triage → extract → critique → store → synthesize → publish), human gates after triage and synthesis, and a feedback loop from published reports back to discovery keywords [4].

```
┌─────────┐    ┌────────┐    ┌─────────┐    ┌──────────┐
│Discover │───▶│Triage  │─⛔─▶│Extract  │───▶│Critique  │
└─────────┘    └────────┘    └─────────┘    └──────────┘
                                                  │
┌─────────┐    ┌────────────┐    ┌──────────┐    │
│Publish  │◀─⛔─│Synthesize  │◀───│Store     │◀───┘
└─────────┘    └────────────┘    └──────────┘
     │                                    ▲
     └────── feedback (new keywords) ─────┘
```

The feedback loop is critical: published reports reveal gaps ("we have no papers on X") which generate new discovery keywords. This makes the system self-improving in coverage without requiring self-improving models.

**Hard follow-up:** What's the minimal viable version of this that delivers value in one week?

> Claude API + a single Python script: download PDF → extract with structured prompt → append JSON to a file → weekly manual review. No vector DB, no embeddings, no state machine. Add infrastructure only when the JSON file exceeds what you can grep through manually (~100 papers).

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1: Embedding Strategy — Full-Text vs Structured vs Hierarchical</strong></summary>

The choice of what to embed determines retrieval quality more than the embedding model itself.

**Full-text embedding** (naive): embed the entire paper text as one vector.
- Problem: dilutes signal with boilerplate (acknowledgments, formatting, related work rehash)
- Typical retrieval precision@10: ~0.45

**Structured embedding** (recommended): embed the extraction JSON (problem + method + key results).
- Advantage: dense signal, no noise from peripheral content
- Typical retrieval precision@10: ~0.72
- Implementation: `embed(f"{paper.problem} {paper.method} {paper.results}")`

**Hierarchical embedding** (advanced): multiple vectors per paper at different granularities.
```
Level 0: Paper-level (title + abstract) — for broad discovery
Level 1: Section-level (each major section) — for methodology search
Level 2: Claim-level (each extracted claim) — for fact verification
```

Storage cost comparison at 1000 papers:
- Full-text (1 vector): 3072 dims × 4 bytes × 1000 = 12 MB
- Hierarchical (avg 15 vectors): 3072 × 4 × 15000 = 180 MB

The hierarchical approach enables queries at different specificity levels: "papers about RLHF" (Level 0) vs "papers that use PPO with KL penalty" (Level 1) vs "papers claiming RLHF outperforms DPO on safety benchmarks" (Level 2).

Retrieval latency with HNSW index: <10ms for all approaches at 1000 papers. The bottleneck shifts to the LLM reranking step (~200ms) at Level 2 where you have 15K vectors to search.

</details>

<details><summary><strong>DE Probe 2: Triage Calibration — Bayesian Scoring with Human Feedback</strong></summary>

Naive triage (fixed thresholds) drifts as your research interests evolve. A calibrated system updates scoring weights from your reading decisions.

**Model**: Each dimension (novelty, depth, relevance, reproducibility) has a weight `w_i` initialized to 0.25. The triage score is:

```
score = Σ(w_i × s_i)  where s_i ∈ [1,5], Σw_i = 1
```

**Calibration loop**:
```python
# After human reads (or skips) a triaged paper:
def update_weights(paper, human_decision):
    # human_decision: "worth_reading" | "not_worth_reading"
    predicted_score = sum(w[i] * paper.scores[i] for i in dims)
    
    if human_decision == "worth_reading" and predicted_score < threshold:
        # False negative — increase weight of highest-scoring dimension
        best_dim = argmax(paper.scores)
        w[best_dim] += learning_rate
        
    if human_decision == "not_worth_reading" and predicted_score >= threshold:
        # False positive — decrease weight of highest-scoring dimension
        best_dim = argmax(paper.scores)
        w[best_dim] -= learning_rate
    
    normalize(w)  # ensure sum = 1
```

After 50 calibration examples, weights typically converge. A researcher focused on production ML might end up with: relevance=0.35, reproducibility=0.30, depth=0.20, novelty=0.15 — deprioritizing novelty in favor of practical applicability.

The threshold itself should also adapt: if false-negative rate >10% (missing important papers), lower threshold by 1 point. If false-positive rate >30% (wasting time on unimportant papers), raise by 1 point.

</details>

<details><summary><strong>DE Probe 3: Cross-Paper Contradiction Detection</strong></summary>

Detecting contradictions is the hardest unsolved problem in automated literature review. Two papers may report different results under similar conditions without explicitly disagreeing.

**Approach**: Extract claims as structured triples, then compare across papers.

```python
# Claim extraction
claim = {
    "subject": "RLHF",
    "predicate": "outperforms",
    "object": "DPO",
    "condition": "safety benchmarks",
    "magnitude": "+12%",
    "dataset": "SafetyBench",
    "paper_id": "paper_A"
}

# Contradiction detection via pairwise comparison
def find_contradictions(claims: list[dict]) -> list[tuple]:
    contradictions = []
    for a, b in combinations(claims, 2):
        if (a["subject"] == b["subject"] and
            a["object"] == b["object"] and
            a["predicate"] != b["predicate"]):
            # Potential contradiction — verify conditions match
            condition_sim = embed_similarity(a["condition"], b["condition"])
            if condition_sim > 0.8:
                contradictions.append((a, b, condition_sim))
    return contradictions
```

**Failure modes**:
1. Implicit contradictions: Paper A shows method works; Paper B shows it fails — but they use different datasets without noting this explains the discrepancy
2. Scope contradictions: "X works for classification" vs "X fails for generation" — not actually contradicting
3. Magnitude contradictions: Both agree X > Y, but by 2% vs 20% — practically different conclusions

The LLM-as-judge step is essential: after structural comparison identifies candidates, an LLM evaluates whether the contradiction is real, apparent (different conditions), or a scope difference. This adds ~$0.05 per candidate pair but reduces false-positive contradictions by ~70%.

</details>

<details><summary><strong>DE Probe 4: Pipeline Orchestration — State Machine vs DAG vs Event-Driven</strong></summary>

Three architectural patterns for research agent pipelines, each with different failure and recovery semantics.

**State Machine (LangGraph)**: Nodes = stages, edges = decisions. Linear with conditional branching.
```
Strengths: Easy to reason about, built-in retry, checkpointing
Weakness: Cannot parallelize independent papers; sequential by design
Best for: Single-paper deep analysis with decision points
```

**DAG (Airflow/Prefect)**: Tasks with dependency edges. Parallel where dependencies allow.
```
Strengths: Parallel paper processing, dependency management, scheduling
Weakness: No dynamic branching mid-execution; topology fixed at compile time
Best for: Batch processing 20+ papers weekly with fixed pipeline
```

**Event-Driven (Temporal/custom)**: Activities triggered by events with durable state.
```
Strengths: Dynamic workflows, long-running (weeks), failure recovery
Weakness: Complexity, harder to debug, eventual consistency
Best for: Continuous monitoring with variable pipeline depth per paper
```

**Recommended hybrid for research**:
```
DAG (outer loop): weekly batch of 20 papers, parallel triage
  └─ State Machine (inner loop): per-paper analysis with decisions
       └─ Event-Driven (trigger): new paper alert → inject into next batch
```

Recovery semantics matter: if Claude API fails mid-extraction, the state machine retries that node. If a paper is retracted after storage, an event triggers deletion propagation. If the weekly batch fails, the DAG retries from the last successful node (not from scratch).

</details>

<details><summary><strong>DE Probe 5: Quality Evaluation — LLM-as-Judge for Literature Reviews</strong></summary>

Evaluating automated literature review quality requires multi-dimensional judgment that a single metric cannot capture.

**Evaluation rubric** (5 dimensions, each 1-5):

| Dimension | 1 (Fail) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| Coverage | Misses >50% of key papers | Covers major papers, misses niche | Complete coverage including edge cases |
| Accuracy | >3 factual errors | 0-1 minor errors | Zero errors, all claims verified |
| Synthesis | List of summaries, no connection | Groups by theme | Identifies trends, contradictions, gaps |
| Actionability | No clear takeaways | General recommendations | Specific next experiments/decisions |
| Citation quality | Hallucinated refs | All refs real, some misattributed | Perfect attribution with page numbers |

**Multi-judge protocol**:
```python
judges = [
    {"model": "claude-sonnet", "role": "methodology_expert"},
    {"model": "claude-sonnet", "role": "domain_expert"},
    {"model": "claude-sonnet", "role": "skeptic"},
]

scores = []
for judge in judges:
    score = judge.evaluate(review, rubric, role=judge["role"])
    scores.append(score)

final = median(scores)  # median is more robust than mean to outlier judges
pass_threshold = 3.5 / 5.0 on all dimensions
```

The "skeptic" judge is critical — it's specifically prompted to find hallucinated claims, unsupported connections, and missing caveats. Without it, reviews tend to score artificially high because LLM judges default to charitable interpretation.

Calibration: run the evaluation on 10 human-written reviews first to establish the score distribution. Automated reviews should score within 1 standard deviation of human reviews to ship.

</details>

<details><summary><strong>DE Probe 6: Knowledge Base Maintenance — Decay, Deduplication, and Versioning</strong></summary>

A research knowledge base degrades without active maintenance. Papers become outdated, claims get superseded, and duplicate entries accumulate.

**Decay model**: Each paper record has a `relevance_half_life` based on field velocity.
```python
# ML/AI: half-life = 18 months (fast-moving)
# Systems: half-life = 36 months
# Theory: half-life = 60 months

current_relevance = initial_relevance * (0.5 ** (age_months / half_life))

# Papers below relevance threshold get archived (not deleted)
if current_relevance < 0.3:
    archive(paper)  # move to cold storage, exclude from active search
```

**Deduplication**: Papers often appear in multiple venues (arXiv preprint → conference → journal). Detect via:
1. Title similarity > 0.95 (exact match with minor formatting differences)
2. Author overlap > 80% AND abstract similarity > 0.85
3. When detected: keep the most recent/authoritative version, link others as `superseded_by`

**Versioning**: Papers themselves get updated (v1→v2 on arXiv), and your extraction may need updating:
```
paper_v1.json (extracted 2026-01)
paper_v2.json (extracted 2026-06, after paper revision)
    diff: results section changed, new ablation added
    action: update knowledge base claims, flag downstream syntheses for re-evaluation
```

The cascade problem: when a foundational paper's claims change, every synthesis that references it may be invalid. Track dependency graphs: `synthesis_report.depends_on = [paper_A, paper_B, ...]` and trigger re-evaluation when any dependency updates.

Storage strategy: hot (active search, <6 months old), warm (searchable but lower ranking, 6-24 months), cold (archived, only accessible via direct lookup, >24 months or relevance < 0.3).

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Paper Usage | Cost |
|-----------|-----------|----------------|------|
| Discovery (Elicit free tier) | $0 | 1 query | $0.00 |
| Citation graph (Semantic Scholar API) | $0 (free, 100 req/5min) | 2-3 calls (refs + citations) | $0.00 |
| Triage (Haiku) | $0.25/$1.25 per 1M in/out | ~3K tokens | $0.01 |
| Deep extraction (Sonnet) | $3/$15 per 1M in/out | ~30K in + 2K out | $0.12 |
| Critique (Sonnet) | $3/$15 per 1M in/out | ~30K in + 1K out | $0.11 |
| Embedding (text-embedding-3-large) | $0.13/1M tokens | ~2K tokens | $0.0003 |
| Storage (pgvector on RDS) | $0.10/GB/month | ~5KB per paper | negligible |
| Weekly synthesis (Sonnet, 200K context) | $3/$15 per 1M in/out | ~200K in + 5K out | $0.68 |

### Monthly Cost at Scale

| Scale | Papers/Week | LLM Cost | Infra | Total/Month |
|-------|-------------|----------|-------|-------------|
| Personal (researcher) | 20 | $30 | $5 (local pgvector) | $35 |
| Team (5 researchers) | 100 | $150 | $25 (RDS small) | $175 |
| Organization (lab) | 500 | $750 | $100 (RDS + compute) | $850 |

### Cost Optimization Priority Stack

| Optimization | Estimated Savings |
|-------------|-------------------|
| Model routing: Haiku for triage (80% of volume) | 40-50% |
| Skip critique for high-reproducibility papers | 15-20% |
| Cache embeddings (compute once per paper) | 5-10% |
| Batch synthesis weekly instead of per-paper | 10-15% |
| Use Elicit free tier for discovery instead of LLM | 5% |

### Build vs Buy

| Capability | Build Cost | Buy Option | Recommendation |
|-----------|-----------|------------|----------------|
| Paper discovery | Free (Elicit/PWC/Semantic Scholar APIs) | Elicit Pro ($50/mo) | Free tier sufficient for <100 papers/week; S2 API is free + open |
| Citation graph traversal | Semantic Scholar API (free) | Connected Papers ($5/mo pro) | S2 API for automation (free, programmatic); Connected Papers for visual exploration |
| Multi-paper reasoning | Custom pipeline (~$30/mo LLM) | NotebookLM (free) | NotebookLM for exploration; custom for automation |
| Knowledge base | pgvector + Python (~2 days setup) | Notion AI ($10/mo) | Build if you need programmatic access; buy if manual OK |
| Full pipeline orchestration | LangGraph + 1 week dev | No turnkey option | Build — no product covers the full pipeline today |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Triage false-negative rate | >15% (measured via user overrides) | Recalibrate weights; lower threshold |
| Extraction schema compliance | <95% records valid | Check PDF parsing; update extraction prompt |
| Citation verification rate | <90% verified | LLM generating hallucinated refs; add verification step |
| Synthesis coherence (LLM judge) | <3.5/5.0 | Review input quality; check for contradictory sources |
| Weekly pipeline completion | Fails 2+ consecutive weeks | Investigate API failures; check rate limits |
| Cost per paper | >2x baseline ($0.50) | Check for prompt bloat; verify model routing working |

### Debugging Walkthrough

```
Symptom: Synthesis report contains a claim not in any source paper
    │
    ├─ Check citation verification → Was the claim cited?
    │   └─ NO → Hallucination in synthesis step → Add claim-source verification
    │   └─ YES → Citation exists but is misattributed ↓
    ├─ Check extraction accuracy → Was the source paper extracted correctly?
    │   └─ NO → PDF parsing or extraction prompt failure → Fix extraction
    │   └─ YES ↓
    └─ Check synthesis prompt → Is the synthesis prompt encouraging extrapolation?
        └─ YES → Constrain prompt: "only state what is explicitly in the sources"
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| Extraction schema | Keep last 3 versions; re-extract on schema change | All new extractions |
| Triage weights | Git-tracked; revert to last calibrated state | Future triage decisions only |
| Synthesis prompts | Versioned in config; regenerate last report | Most recent synthesis |
| Knowledge base state | Daily pg_dump snapshots; point-in-time recovery | Full corpus |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| User overrides triage (reads a rejected paper) | Highest — direct calibration signal | Track papers accessed that scored below threshold |
| User marks synthesis claim as wrong | High — extraction/synthesis bug | Explicit flag in review interface |
| Paper cited in user's own work | Medium — validates deep-read decision | Track which extracted papers appear in user's outputs |
| Time spent on paper (proxy for value) | Low — noisy signal | Track document open duration if available |
| Downstream experiment proposed from synthesis | Medium — validates synthesis quality | Track experiment-to-source-paper links |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Per-session | Triage weight calibration | ≥5 override signals accumulated |
| Weekly | Discovery keywords from synthesis gaps | Synthesis identifies "no papers on X" |
| Monthly | Extraction schema evolution | >10% of papers have fields that don't fit schema |
| Quarterly | Pipeline architecture (new tools, models) | New model release OR cost >2x baseline |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Model routing (Haiku→Sonnet) | Cost reduction without quality loss | Multi-stage pipelines with varying complexity | Single-stage where all tasks need high quality |
| Citation graph expansion (S2 API) | Cold-start discovery via influential citations | Building knowledge base from scratch; use S2's `influentialCitationCount` to prioritize | Already have comprehensive corpus |
| Hierarchical embeddings | Query specificity mismatch | Queries range from broad to very specific | All queries are same specificity level |
| Contradiction detection | Missing cross-paper insights | Overlapping papers with potentially conflicting results | Papers from unrelated subfields |
| Feedback calibration loop | Triage drift over time | Ongoing usage with human overrides available | One-off survey with no future iterations |
| Lazy relationship computation | O(n²) relationship scaling | Knowledge base >100 papers | Small corpus where eager computation is cheap |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|-----------------|------------------------------|
| "Let's use RAG over all our papers" | "RAG retrieves chunks; synthesis requires full-document reasoning. Use RAG for fact lookup, but cross-paper synthesis needs papers fully in context — that's a different architecture" |
| "We should automate the entire literature review" | "Automate volume (discovery, triage, extraction) — but humans own synthesis and 'so what.' The 80/20 is: AI reads 30 papers so you can deeply engage with 5" |
| "NotebookLM is enough for our research workflow" | "NotebookLM excels at exploration but has no API, no structured output, no persistence. It's a tool, not a system. The system needs extraction, storage, and retrieval around it" |
| "Just use ChatGPT to summarize papers" | "Summaries are the least valuable output. The value is in structured extraction (queryable later), contradiction detection (insights you'd miss), and calibrated triage (saving time on the right papers)" |
| "We need a vector database for 50 papers" | "At 50 papers, a JSON file with grep is faster to build, easier to debug, and sufficient. Vector DB adds value at 200+ papers when keyword search stops working" |
| "The pipeline should handle any research domain" | "Domain-specific calibration is the whole point. A pipeline tuned for ML papers (fast decay, code emphasis) fails for clinical trials (slow decay, methodology emphasis). Generality is the enemy of precision here" |

## References

### Foundational Tools

- [1] Google NotebookLM — notebooklm.google — Multi-document reasoning with source grounding, cross-paper comparison, audio overviews
- [2] Elicit — elicit.com — Natural-language academic search with structured evidence table extraction
- [3] Anthropic Claude — claude.ai — Long-context (1M token) analysis, structured output, adversarial critique capabilities
- [4] LangGraph — langchain-ai.github.io/langgraph — State machine orchestration for multi-step agentic workflows
- [5] Papers with Code — paperswithcode.com — Paper-implementation-benchmark linkage for ML research
- [9] Semantic Scholar — semanticscholar.org (API: api.semanticscholar.org) — Open academic graph with 200M+ papers; provides citation graphs, influential citation scoring, author disambiguation, paper recommendations, and free API (100 req/5min unauthenticated, 1 req/sec with API key). Key endpoints: `/paper/search`, `/paper/{id}/references`, `/paper/{id}/citations`, `/recommendations/v1/papers`. Powers both discovery (recommendation feeds) and verification (citation existence checks) in agentic pipelines

### Supporting Tools

- [6] Connected Papers — connectedpapers.com — Citation graph visualization and cluster discovery (built on Semantic Scholar data)
- [7] Consensus — consensus.app — Evidence-based question answering directly from research papers
- [8] SciSpace — scispace.com — AI-powered equation explanation, figure interpretation, methodology parsing

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-27 | Added Semantic Scholar as primary tool | Elevated from supporting tool to foundational: discovery, citation graph traversal, verification, cold-start expansion. Updated architecture, cost model, Q&A, decision matrix, and references. |
| 2026-06-27 | Initial v2 generation | Compiled from seed: AI-assisted paper research tools + agentic workflow SOP pattern |
