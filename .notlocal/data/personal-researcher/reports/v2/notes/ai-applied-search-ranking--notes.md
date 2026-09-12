# AI Applied to Search & Ads Ranking: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-30 | **Read time:** ~18 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[recommendation-ranking]] — Traditional ML ranking infrastructure: two-tower, DCN V2, FTRL, multi-objective (standard format)
> - [[ai-applied-search-retrieval--notes]] — LLM in retrieval pipeline (upstream of ranking)
> - [[genai-search-ads]] — Business/industry view of AI in search+ads
> - [[policy-dist--notes]] — Policy distillation techniques for compiling LLM rankers into cheap models

---

## Quick Catchup

> **Quick Catchup (July 2026):** LLMs in search+ads ranking have evolved from LLM-generated features for CTR models (2023) through zero-shot LLM reranking (RankGPT, 2023), distilled LLM rankers (RankLLaMA, 2024), to unified ranking foundation models and RL-optimized multi-objective ranking agents (2025-2026).
> Key players: Google (Gemini for ranking, AI Max), Microsoft (Bing LLM ranking), Amazon (COSMO, LLM for product ranking), Meta (LLM features for ads), Baidu (ERNIE for sponsored search). Main open problem: latency — LLM inference at 100-500ms is incompatible with sub-50ms ranking SLAs; distillation is the bridge but loses quality.
> Recent breakthrough: Listwise LLM reranking (RankGPT/LRL) demonstrates zero-shot ranking quality exceeding fine-tuned cross-encoders on BEIR/TREC benchmarks [1][2]. Trend: LLMs define what "relevance" means (offline, as judges/teachers) while distilled models do the real-time scoring.

## State of the Art

### Current Best Approaches

- **LLM-as-reranker (listwise)** — Present N candidates to LLM, ask for optimal permutation; zero-shot SOTA on IR benchmarks [1][2]
- **LLM-as-feature-generator** — Offline LLM produces semantic features (item descriptions, intent tags, query-ad match scores) consumed by real-time CTR models [3]
- **Distilled LLM rankers** — Fine-tune open-source LLMs (Llama, Mistral) on ranking data → production-grade reranker at cross-encoder latency [4]
- **LLM-as-judge for ranking labels** — Replace human relevance annotations with LLM judgments for training data; scale labeling 100x [5]
- **RL-optimized ranking policies** — Treat ranking as a sequential decision problem; optimize for long-term user/business value via offline RL [6]
- **Unified ranking foundation models** — Single pretrained model handles multiple ranking tasks (web, ads, products) via task-specific prompting [7]

### Recent Breakthroughs (last 12 months)

- **2024-2025:** RankGPT/LRL demonstrate zero-shot listwise reranking matching or exceeding supervised cross-encoders [1][2]
- **2024:** RankLLaMA — fine-tuned Llama for ranking; 10x cheaper than GPT-4 reranking at 90%+ quality [4]
- **2025:** Google AI Max — Gemini-powered intent matching for ads without explicit keywords; +14% conversions [8]
- **2025-2026:** LLM-as-judge replaces human raters at scale for ranking evaluation and label generation [5]
- **2025:** Offline RL for ranking (counterfactual LTR) — learn ranking policies from click logs correcting for position bias [6]

### Open Problems

- **Latency gap**: LLM reranking is 100-1000x slower than production cross-encoders; only viable for top-K reranking or offline scoring
- **Distillation quality loss**: Compressing LLM ranking into fast models loses 5-15% quality; closing this gap is active research
- **Position bias in LLM ranking**: LLMs exhibit their own position bias (preferring items at list start/end); debiasing LLM judgments is non-trivial
- **Multi-objective LLM ranking**: LLMs optimize for a single notion of "relevance"; encoding multiple business objectives (revenue, diversity, freshness, fairness) into LLM ranking is unsolved
- **Ads auction integration**: LLM-based ad relevance must compose with bid/auction dynamics; relevance improvements may reduce competition/revenue

## Executive Summary

AI applied to search+ads ranking is the use of LLMs to improve how results are scored and ordered — from generating better features for existing rankers, through directly scoring relevance, to acting as the ranking system itself.

The core architectural question: **where does the LLM sit in the ranking pipeline, and at what latency/cost?**

- **Choose LLM-as-feature-generator** when you want to enhance existing CTR models without changing the serving stack (safest, lowest latency impact)
- **Choose LLM-as-reranker** when you have a small candidate set (top-20) and can tolerate 200-500ms latency for final ranking
- **Choose distilled LLM ranker** when you want LLM quality at cross-encoder latency (production workhorse)
- **Choose LLM-as-judge** when you need massive-scale relevance labels for training and evaluation
- **Choose RL ranking policy** when optimizing for long-term metrics (session satisfaction, LTV) beyond single-query relevance

**The killer insight:** "The LLM's primary value in ranking isn't real-time scoring — it's defining what 'good' means. LLMs serve as offline teachers/judges that set the standard; distilled models serve that standard in real-time. The LLM is the curriculum designer; the production ranker is the student."

```
LLM Role in Ranking Pipeline
──────────────────────────────────────────────────────────────────────
OFFLINE (no latency constraint)          ONLINE (sub-50ms SLA)
─────────────────────────────            ────────────────────────
LLM generates features                  CTR model scores with LLM features
LLM generates training labels           Distilled ranker scores candidates
LLM evaluates ranking quality           Fast cross-encoder reranks top-K
LLM designs reward functions            RL policy optimizes ranking

           Teacher (LLM)  ──distill──→  Student (production model)
```

---

## Evolutionary Stages

### Stage 1 — LLM-Generated Features for Classical Rankers (2023-2024)

**Goal:** Use LLMs offline to produce richer features (semantic embeddings, structured attributes, intent tags) consumed by real-time CTR/ranking models.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| LLM-enhanced retrieval pipelines [3] | 2023-2024 | LLM generates item descriptions, category tags, query-intent labels offline → fed as features to DCN/DeepFM |
| KAR (Knowledge-Augmented Recommendation) | 2024 | LLM augments user/item representations with world knowledge for cold-start |
| CTRL (Collaborative-Task Ranking with LLMs) | 2024 | LLM generates collaborative signals as features for ranking models |

**Key transition:** LLMs enter ranking without changing the serving architecture. The production model (DCN V2, DLRM) stays the same; it just gets better input features. This solves cold-start (new items get LLM-generated descriptions immediately) and improves semantic matching (LLM understands synonyms, intent, context). Zero latency impact because LLM runs offline in batch.

### Stage 2 — Zero-Shot LLM Reranking (2023-2024)

**Goal:** Use LLMs directly as rerankers — present a candidate list and ask the model to score or permute.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| RankGPT [1] | 2023 | Listwise reranking: present N documents, ask LLM for optimal permutation; zero-shot SOTA on BEIR |
| LRL (Listwise Reranker via LLM) [2] | 2024 | Sliding window listwise reranking for efficiency; handles long candidate lists |
| PRP (Pairwise Ranking Prompting) | 2023 | Compare document pairs via LLM; high quality but O(n²) comparisons |
| Pointwise LLM scoring | 2023 | Score each document independently (simplest but weakest approach) |

**Key transition:** LLMs outperform fine-tuned cross-encoders on many IR benchmarks WITHOUT task-specific training. The insight: internet-scale pretraining already encodes a strong notion of "relevance." Listwise > pairwise > pointwise for quality. But: cost is 100-1000x a trained cross-encoder, making it impractical for full candidate sets. Only viable for top-K reranking.

#### Ranking Paradigms Comparison

| Paradigm | How It Works | Quality | Cost | Production Viable |
|----------|-------------|---------|------|-------------------|
| Pointwise | Score each doc independently | Low | N calls | Moderate (cheap per call) |
| Pairwise | Compare all pairs | High | O(N²) calls | No (too expensive) |
| Listwise | Present full list, get permutation | Highest | 1 call (but long context) | Top-K only |

### Stage 3 — Distilled LLM Rankers (2024)

**Goal:** Fine-tune smaller models on LLM-generated ranking data to achieve LLM quality at cross-encoder latency.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| RankLLaMA [4] | 2024 | Fine-tune Llama for pointwise/listwise ranking; 10x cheaper than GPT-4 at 90%+ quality |
| RankZephyr | 2024 | Distill GPT-4 listwise ranking into 7B model; competitive with teacher on BEIR |
| RankVicuna | 2024 | Fine-tuned Vicuna for ranking; explores instruction-tuning for relevance scoring |
| MonoT5 / RankT5 | 2023-2024 | T5-based pointwise rankers; smaller and faster than decoder-only LLMs |

**Key transition:** The "teacher-student" pattern makes LLM ranking practical: (1) use GPT-4/Claude as teacher to generate ranking labels or permutations, (2) fine-tune a 7B model on this data, (3) deploy the 7B model at cross-encoder latency. Quality loss is 5-15% but cost drops 100x. This is the bridge from research to production.

### Stage 4 — LLM-as-Judge for Ranking Labels & Evaluation (2024-2025)

**Goal:** Replace human relevance annotators with LLM judges — scaling label generation 100x while maintaining quality.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| LLM-as-judge for IR [5] | 2024 | Use GPT-4 to generate relevance labels (0-3 scale); correlates 0.85+ with human judgments |
| ARES (Automated Retrieval Evaluation) | 2024 | LLM evaluates RAG system quality (context relevance, answer faithfulness, answer relevance) |
| Prometheus | 2024 | Open-source evaluator LLM trained specifically for scoring/judging tasks |
| Arena-style evaluation | 2024-2025 | Pairwise LLM comparison of ranking quality; scalable preference collection |

**Key transition:** Human relevance labeling doesn't scale (expensive, slow, inconsistent). LLM judges generate training labels AND evaluation metrics at 100x scale. This unlocks: (1) training data for distilled rankers, (2) continuous evaluation of production ranking, (3) rapid iteration on ranking quality. Caveat: LLM judges have their own biases (verbosity, position, format) that must be calibrated.

### Stage 5 — LLM for Ads Ranking & Relevance (2024-2026)

**Goal:** Replace keyword-based ad relevance scoring with LLM-powered semantic intent matching.

| System | Year | Core Contribution |
|--------|------|-------------------|
| Google AI Max [8] | 2025 | Gemini matches ad intent without keywords; +14% conversions via semantic broad match |
| Amazon COSMO | 2025 | LLM reasons about shopping intent for product ranking |
| Baidu ERNIE for sponsored search | 2024 | LLM-based query-ad relevance scoring in sponsored search auction |
| Meta LLM features for ads | 2024-2025 | LLM generates ad creative understanding features for CTR prediction |

**Key transition:** Ads ranking shifts from "does the ad keyword match the query?" to "does the ad satisfy the user's intent?" LLMs understand that "best headphones for running" matches an ad for "sweatproof wireless earbuds" without keyword overlap. This expands addressable inventory (+20-40% more ads eligible per query) while improving relevance. The challenge: maintaining auction fairness and advertiser trust when matching is semantic rather than explicit.

### Stage 6 — RL-Optimized Ranking Policies (2024-2026)

**Goal:** Treat ranking as a sequential decision problem — optimize for long-term user and business value, not just per-query relevance.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| Unified Off-Policy LTR [6] | 2023 | Formulates LTR as MDP; connects counterfactual ranking with offline RL |
| RL for session-level ranking | 2024-2025 | Optimize for session satisfaction (clicks + reformulations + conversions) not single-query CTR |
| Multi-objective RL ranking | 2025 | Balance relevance, diversity, freshness, fairness, revenue via constrained RL |
| LLM-designed reward for ranking | 2025+ | LLM generates reward functions that capture nuanced ranking quality (Eureka-style for search) |

**Key transition:** Ranking becomes a POLICY problem rather than a prediction problem. Instead of "predict CTR for each item," the system asks "what ranking sequence maximizes long-term value?" This connects to offline policy learning — learning ranking policies from click logs while correcting for position bias and exploration deficiency. LLMs assist by designing the reward functions that define "good ranking."

### Stage 7 — Unified Ranking Foundation Models (2025-2026 — Emerging)

**Goal:** One pretrained model handles multiple ranking tasks (web search, product search, ads, recommendations) via task-specific prompting or adapters.

| Concept | Year | Core Contribution |
|---------|------|-------------------|
| Universal ranking model [7] | 2025+ | Single model pretrained on diverse ranking data; task-specific via prompt/adapter |
| Cross-domain transfer | 2025+ | Ranking knowledge from web search transfers to product search and ads |
| Multimodal ranking | 2025-2026 | LLM ranks across modalities (text, image, video) within a single model |

**Key transition:** Instead of training separate rankers for web, products, and ads, a single foundation model learns "what it means to rank well" across domains. This mirrors the LLM pattern: pretrain broadly, adapt cheaply. The promise: ranking improvements in one domain automatically benefit others. Early research stage — not yet production-proven at scale.

---

## Key Themes & Connections

### Theme 1: The Teacher-Student Pattern Dominates

The pattern that makes LLM ranking production-viable:

```
OFFLINE (teacher)                        ONLINE (student)
──────────────────                       ─────────────────
GPT-4 / Claude as ranker                 Distilled 7B ranker (RankLLaMA)
 ↓ generate labels/permutations           ↓ score candidates in <50ms
 ↓ train student on teacher data          ↓ serve at production scale
 ↓ evaluate via LLM-as-judge              ↓ continuously retrained
```

Every successful LLM-ranking deployment follows this: LLM defines quality (teacher), smaller model delivers it (student). Direct LLM ranking is only for low-QPS offline pipelines or final top-5 reranking.

### Theme 2: The Latency-Quality Pareto Frontier

| Model | Latency (P95) | NDCG@10 (BEIR avg) | Cost / 1K queries | Production Role |
|-------|---------------|--------------------|--------------------|-----------------|
| BM25 | ~5ms | 0.40 | $0.001 | Candidate retrieval |
| Cross-encoder (fine-tuned) | ~30ms | 0.52 | $0.01 | L2 reranker |
| RankLLaMA (7B) | ~100ms | 0.55 | $0.05 | Premium reranker |
| GPT-4 listwise | ~2000ms | 0.58 | $2.00 | Offline labeling / top-5 |

The gap between cross-encoder and LLM is 5-10% quality for 100x cost. Distillation closes this gap to 2-3% — the remaining question is whether that last few percent justifies the production complexity.

### Theme 3: From Pointwise Prediction to Sequential Policy

```
Traditional: Predict P(click | query, item)  →  Sort by score  →  Done
    │
    │ Limitation: ignores position effects, session context, long-term value
    ▼
RL-based: State(query, session) → Action(ranking) → Reward(clicks+conversions+satisfaction)
    │
    │ Advantage: optimizes for the outcome, not the prediction
    ▼
LLM-enhanced RL: LLM designs the reward function that defines "good ranking"
```

This connects directly to offline policy learning (learn from click logs), RLVR (verify with conversion outcomes), and the policy distillation report (distill strong ranking policy into cheap model).

### Theme 4: Position Bias — The Universal Confounder

Every ranking system (traditional AND LLM-based) faces position bias:

| System | Position Bias Problem | Mitigation |
|--------|----------------------|-----------|
| Traditional ranker | Users click top positions regardless of relevance | IPW, position-aware training |
| LLM-as-ranker | LLM favors items at start/end of presented list | Shuffle + re-rank, calibration |
| LLM-as-judge | LLM rates first-presented item higher | Randomize order, multi-judge |
| Offline RL from logs | Click data is position-biased → policy learns position, not quality | Counterfactual correction |

The lesson: switching from classical to LLM ranking does NOT eliminate position bias — it introduces a different form. Every evaluation and training pipeline must account for it.

### Theme 5: Ads Ranking — Where Revenue Meets Relevance

| Objective | What Traditional Ads Ranking Does | What LLM-Enhanced Does |
|-----------|----------------------------------|----------------------|
| Relevance | Keyword match + CTR prediction | Semantic intent matching (AI Max) |
| Revenue | bid × pCTR × quality score | bid × LLM-relevance × pCTR |
| Diversity | Hard rules (one ad per advertiser) | LLM-aware diversity (different intents) |
| Fairness | Budget pacing, frequency caps | LLM monitors for discrimination |
| User experience | Separate from ranking | Integrated (LLM considers ad+organic holistically) |

The tension: LLM-based relevance improvements may reduce the number of eligible ads per auction (more precise matching = fewer candidates), which can reduce revenue through decreased competition. The business challenge is optimizing relevance AND revenue jointly.

---

## Reading Schedule

| Week | Papers/Systems | Central Question |
|------|---------------|-----------------|
| **1** | LLM-as-feature-generator [3], KAR, CTRL | How do LLMs enhance classical ranking without changing the serving stack? |
| **2** | RankGPT [1], LRL [2], PRP, pointwise scoring | Can LLMs directly rank documents? How do listwise/pairwise/pointwise compare? |
| **3** | RankLLaMA [4], RankZephyr, MonoT5 | How do you distill LLM ranking quality into production-speed models? |
| **4** | LLM-as-judge [5], ARES, Prometheus | How do LLM judges replace human annotators for training data and evaluation? |
| **5** | Google AI Max [8], COSMO, ERNIE for ads | How do LLMs transform ad relevance from keyword match to intent match? |
| **6** | Unified Off-Policy LTR [6], RL for ranking, session optimization | How does treating ranking as RL improve long-term outcomes? |
| **7** | Universal ranking models [7], cross-domain transfer, multimodal ranking | Can one ranking model serve web, products, and ads? |
| **8** | Position bias in LLM ranking, auction dynamics + LLM relevance, fairness | What are the failure modes and biases unique to LLM-based ranking? |

---

## References

### LLM-as-Ranker

- [1] Sun et al. (2023) — *Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents (RankGPT)* — https://arxiv.org/abs/2304.09542 — Listwise reranking via LLM permutation generation; zero-shot SOTA
- [2] Ma et al. (2024) — *Listwise Reranker via LLM (LRL)* — Efficient sliding-window listwise reranking outperforming pointwise/pairwise

### LLM Features & Distillation

- [3] LLM-enhanced ranking pipelines (2023-2024) — Offline LLM generates semantic features consumed by real-time CTR models; solves cold-start
- [4] Ma et al. (2024) — *Fine-Tuning LLaMA for Multi-Stage Text Ranking (RankLLaMA)* — https://arxiv.org/abs/2310.08319 — Distilled LLM ranker at cross-encoder latency

### LLM-as-Judge

- [5] Thomas et al. (2024) — *Large Language Models Can Accurately Predict Search Quality* — Microsoft — LLM judges correlate 0.85+ with human relevance assessments

### RL for Ranking

- [6] Zhang et al. (2023) — *Unified Off-Policy Learning to Rank: A Reinforcement Learning Perspective* — NeurIPS — Connects counterfactual LTR with offline RL

### Foundation Models for Ranking

- [7] Unified ranking foundation models (2025+) — Single pretrained model handles web, product, and ad ranking via task-specific adaptation

### Ads Ranking

- [8] Google (2025) — *AI Max for Search Campaigns* — Gemini-powered intent matching without explicit keywords; +14% conversions

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| Start with LLM-as-feature-generator (Stage 1) — it improves your existing ranker with zero serving-stack changes and zero latency impact | Industry pattern (Meta, Amazon, Google ads) |
| RankLLaMA at 7B parameters gives ~90% of GPT-4 ranking quality at 100x lower cost — this is the production-viable sweet spot today | RankLLaMA benchmarks (2024) |
| LLM-as-judge is the single highest-ROI application — it replaces $50K+/month in human labeling with $500/month in API calls at comparable quality | Microsoft, Google ranking evaluation teams |
| Position bias in LLM rankers is REAL and DIFFERENT from user position bias — always randomize candidate order when using LLMs for evaluation/labeling | Sun et al. follow-up analysis; community best practices |
| For ads: LLM relevance improvements increase long-tail ad matching (+20-40% eligible ads) but can decrease auction competition — monitor revenue impact alongside relevance metrics | Google AI Max results; industry observations |
| The endgame is NOT "LLM replaces the ranker" — it's "LLM defines what good ranking looks like, and efficient models serve that definition at scale" | Architecture convergence (2025-2026) |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-30 | Initial v2 generation (study-notes format) | Created from query on LLM + agentic AI in search+ads ranking; covers LLM features → zero-shot reranking → distillation → LLM-as-judge → ads intent matching → RL ranking → foundation models |
| 2026-07-30 | Filed | [UNVERIFIED] — run /verify-report --topic ai-applied-search-ranking when runtime available |
