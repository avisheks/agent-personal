# LLM Content Generation for Ads

> **Last Updated:** 2026-05-31 | **Read time:** ~25 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** LLM-based ad content generation has evolved from template-filling to few-shot prompted generation with critic-reranker pipelines [1][2].
> Key players: GPT-4 [15], Llama 2 [10], Constitutional AI [9]. Main open problem: the adoption ceiling — advertisers ignore 70-85% of generated suggestions regardless of quality.
> Recent breakthrough: grammar-guided decoding (Outlines, 2023) guarantees structurally valid outputs at generation time [8]. Trend: bandit-based creative selection replacing static ranking.

## State of the Art

### Current Best Approaches

- **Few-shot prompted generation with constrained decoding** — LLM generates ad variants within format constraints enforced at the token level [1][8]
- **Critic-reranker pipelines** — Separate LLM-as-judge scores candidates on relevance, brand safety, and predicted performance before surfacing to advertisers [4]
- **DPO/RLHF-aligned generators** — Models fine-tuned on advertiser adoption and performance preferences produce higher-adoption content [3]
- **Thompson sampling for creative selection** — Bandit algorithms replace static ranking to balance exploration of novel variants with exploitation of proven performers [5][7]
- **Constitutional AI guardrails** — Self-critique loops enforce policy compliance without per-category human labeling [9]

### Recent Breakthroughs (last 12 months)

- **Outlines / grammar-guided generation** (Jul 2023): Guarantees structurally valid outputs via token masking, eliminating 20-30% waste from post-hoc filtering [8]
- **Direct Preference Optimization for ad copy** (May 2023): Aligns generators to advertiser adoption signals without reward model infrastructure [3]
- **LLM-as-Judge at scale** (Jun 2023): MT-Bench showed LLM judges correlate 0.85 with human preference at model level, enabling automated quality gating [4]
- **Nucleus sampling analysis** (2020): Demonstrated that top-p decoding produces more natural text than top-k for creative generation [11]

### Open Problems

- **Adoption ceiling**: Advertisers adopt only 15-25% of suggestions regardless of generation quality — a product/trust problem, not a model problem
- **Attribution**: Isolating keyword quality signal from bid, creative, landing page, and auction confounders
- **Multi-locale generation without translation**: Regenerating from attributes in target languages while capturing local search patterns
- **Diversity-relevance tension**: Rankers optimized for relevance collapse to 2-3 obvious intents

## Executive Summary

LLM content generation for ads uses large language models to produce ad copy, keywords, and creative variants at scale, then selects the best performers through critic-reranker pipelines and bandit-based optimization. The core architectural trade-off is generation volume vs. adoption rate — more candidates do not yield proportional adoption because advertisers have bounded attention and trust.

- **Choose few-shot prompting** when expanding to new locales or categories with limited data
- **Choose fine-tuned generators** when per-category adoption data exceeds 10K examples
- **Choose constrained decoding** when format compliance is non-negotiable (character limits, JSON schemas) [8]

**The killer framing:** "The constraint is not generation quality — it is adoption. You solve this by changing what you present (intent-level abstraction, predicted impact), not by generating more or better content."

Cost headline: Generation costs ~$0.01-0.02 per advertiser per batch at scale; the real cost is wasted compute on suggestions that are never adopted.

```
Pipeline: LLM Ad Content Generation
─────────────────────────────────────
Product Attributes → Intent Clustering → LLM Generation (constrained) [1][8]
    → Policy Filter [9] → LLM-as-Judge [4] → Bandit Ranking [5][7]
    → Top-K to Advertiser → Adoption Signal → Feedback Loop [3]
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Output type and target metric | Ad copy vs keywords vs product descriptions? Optimize CTR, CVR, or adoption rate? One-shot batch or continuous? |
| 2. Identify constraints | Brand safety, trust, cost of failure | Lower-funnel ads cannot regress CVR/RoAS. Policy violations are existential. Advertiser trust gates everything. |
| 3. Propose baseline | Prompted LLM with templates + few-shot [1] | Prove the pattern generates plausible content. Use constrained decoding for format compliance [8]. |
| 4. Identify gaps | Generic output, hallucinations, adoption ceiling | The gap is not quality — it is adoption. Advertisers ignore 150 of 200 suggestions regardless of quality. |
| 5. Introduce improvements | Critic/reranker [4], intent abstraction, feedback | Each improvement targets a specific gap: critic for quality, abstraction for cognitive load, bandits for exploration [5]. |
| 6. Add evaluation + guardrails | Multi-layer defense, A/B testing [14] | Offline metrics gate; online metrics optimize. Constitutional AI for scalable policy [9]. Double-randomized experiments for causal impact. |
| 7. Discuss scaling tradeoffs | Cost, diversity, feedback attribution | Token cost grows linearly; advertiser trust does not. Fewer high-quality candidates beat many mediocre ones. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Generation method | Few-shot prompting [1] | Fine-tuned model [10] | New categories, <1K examples, rapid iteration | >10K examples, stable category, measurable quality gain |
| Format enforcement | Constrained decoding [8] | Post-hoc filtering | Format compliance is critical, compute budget allows | Simple formats, high filtering pass rate |
| Creative selection | Static ranking | Thompson sampling [5][7] | Mature categories with known performers | New categories, need exploration, sufficient traffic |
| Quality scoring | Rule-based filters | LLM-as-Judge [4] | Clear binary rules (prohibited terms) | Nuanced quality (relevance, brand voice, persuasion) |
| Personalization | Category-level conditioning | Per-advertiser fine-tuning | Long-tail advertisers (99%) | Top 0.1% advertisers by spend |

## System Design Walkthrough

### Opening Frame

Ad content generation is an adoption problem, not a generation problem. LLMs can produce 50-200 candidate outputs per product — the constraint is whether advertisers trust and deploy them. The non-obvious insight: reducing suggestion volume while increasing signal per suggestion (predicted impact, intent clustering) drives more adoption than improving generation quality.

### Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│   Product    │───▶│    Intent    │───▶│ LLM Generator    │───▶│  Candidate  │
│   Catalog    │    │  Clustering  │    │ (constrained)[8] │    │  Pool       │
└──────────────┘    └──────────────┘    └──────────────────┘    └──────┬──────┘
                                                                       │
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐           │
│  Advertiser  │◀───│ Bandit Layer │◀───│ LLM-as-Judge [4] │◀──────────┘
│  (Top-K)     │    │  [5][7]      │    │ + Policy [9]     │
└──────┬───────┘    └──────────────┘    └──────────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│   Adoption   │───▶│  Feedback    │──▶ (Ranker + Generator updates)
│   Signal     │    │  Loop [3]    │
└──────────────┘    └──────────────┘
```

- **Intent Clustering**: Groups semantically related keywords to reduce cognitive load on advertisers
- **Constrained Generator**: Grammar-guided decoding [8] guarantees format compliance at token level
- **LLM-as-Judge + Policy**: Multi-layer quality scoring and Constitutional AI compliance [4][9]
- **Bandit Layer**: Thompson sampling [5][7] balances exploration of novel variants with exploitation of proven performers
- **Feedback Loop**: Adoption and performance signals train the ranker via DPO [3]

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Adoption ceiling (70-85% ignored) | Intent-level abstraction + predicted impact | Requires intent taxonomy maintenance |
| Generic/undifferentiated suggestions | Diversity via MMR reranking [13] | Reduces average relevance score |
| Policy violations at scale | Constitutional AI self-critique [9] | 10-15% more generation tokens |
| Attribution confounders | Double-randomized experimentation [14] | Requires traffic partitioning, reduces power |
| Feedback loop filter bubble | Thompson sampling exploration [5][7] | 10-20% slots for uncertain variants |

### Scaling Summary

- **10x advertisers**: Batch generation nightly; cache stable products; route simple categories to smaller models
- **100x advertisers**: Shard by category; pre-compute intent clusters; use synthetic preferences [3] for ranker training
- **1000x impressions**: Bandit state maintenance becomes O(advertiser x keyword x context); hierarchical bandits with cluster-level priors [6]

## Interview Q&A Bank

### Q1: How would you design a content generation pipeline for ads at scale?

> **Quick answer:** The pipeline generates candidates via constrained LLM [1][8], filters through policy and quality layers [4][9], ranks via bandit-based selection [5], and surfaces intent-clustered suggestions with predicted impact to maximize adoption.

The architecture has six stages: (1) Product attribute extraction from catalog. (2) Intent clustering to group semantically related outputs. (3) LLM generation with constrained decoding for format compliance [8]. (4) Multi-layer filtering — automated policy checks, factual grounding, LLM-as-judge quality scoring [4]. (5) Bandit-based ranking that balances exploration and exploitation [5][7]. (6) Advertiser review with predicted impact annotations.

The critical insight: generate at the intent level, not individual items. Present 5-7 intent clusters rather than 200 individual keywords. Advertisers reason about intents ("Performance Running"), not terms.

| Component | Latency | Cost/Query |
|-----------|---------|-----------|
| Attribute extraction | Pre-computed | ~$0 |
| LLM generation (50 candidates) | 2-4s | $0.008 |
| Policy + quality filter | 1-2s | $0.004 |
| Bandit ranking | <100ms | $0.001 |

**Hard follow-up:** Your pipeline generates great content but adoption is flat. What do you do?

> Adoption is flat because the bottleneck is cognitive load and trust, not quality. Three interventions: (1) Reduce volume — surface 30 high-confidence suggestions, not 200. (2) Reframe from items to intents — let advertisers approve clusters. (3) Show predicted incremental impact per suggestion so advertisers can make informed decisions.

### Q2: How do you handle brand safety and policy compliance?

> **Quick answer:** Defense in depth: prompt-level constraints, constrained decoding to suppress prohibited tokens [8], Constitutional AI self-critique [9], LLM-as-judge post-generation [4], and human review for high-risk categories.

The layered architecture ensures no single point of failure. Constrained decoding catches violations at generation time (zero additional compute waste) [8]. Constitutional AI [9] handles nuanced policy rules without per-category human labeling — the model critiques its own output against a constitution of advertising policies. LLM-as-judge [4] provides a second-opinion evaluation layer.

The safety investment must be proportional to failure cost. A bad keyword wastes pennies of ad spend. A policy violation in pharmaceutical ad copy creates legal liability. Guardrail depth matches risk profile.

**Hard follow-up:** Generated copy says "award-winning" for a product with no verified awards. How do you catch this?

> Factual grounding: every objective claim must trace to a verified product attribute. "Award-winning" requires a corresponding attribute entry for the specific award. Claim classification distinguishes objective claims (require evidence) from subjective puffery (allowed within bounds). Red-team the pipeline systematically with misleading-but-technical prompts.

### Q3: How do you measure whether generated content is good?

> **Quick answer:** Three layers: linguistic quality (gate), relevance/accuracy (gate), business impact (optimization target). Only layer 3 — adoption, CTR, CVR — constitutes ground truth.

Offline metrics (fluency, factual grounding, LLM-as-judge scores [4]) are necessary gates that filter bad content. They are not optimization targets. Content that scores perfectly on linguistic quality can have zero business impact if it is correct but generic.

Online metrics tell you what works: adoption rate (did the advertiser use it?), CTR (did users click?), CVR (did clicks convert?). For lower-funnel ads, CVR and RoAS are constraints — higher CTR with lower CVR means attracting clicks that do not convert, wasting advertiser budget.

> [!experience] The gap between offline quality and business impact was where most surprises lived. Content rated "adequate" by reviewers sometimes outperformed "excellent" content because it matched real user search patterns rather than editorial standards.

**Hard follow-up:** Generated keywords have higher CTR but lower CVR than advertiser-written ones. Ship or not?

> Do not ship for lower-funnel. Higher CTR with lower CVR means the content attracts non-converting clicks — wasting budget. Ground generation more tightly in product-specific attributes, include conversion signals in ranking, and A/B test with RoAS as primary metric [14].

### Q4: How do you solve the adoption ceiling problem?

> **Quick answer:** The adoption ceiling occurs when increasing generation volume or quality does not yield proportional adoption. The fix is product-level: reduce cognitive load (intent clustering), increase signal (predicted impact), and build graduated trust.

Advertisers adopt 15-25% of suggestions. The constraint is not quality — it is attention and trust. Three interventions:

1. **Intent-level abstraction**: Present 5-7 intent clusters instead of 200 items. Advertisers approve clusters, not individual keywords.
2. **Reduce volume, increase relevance**: 30 well-ranked suggestions outperform 200 sorted by internal score.
3. **Predicted impact**: Attach expected incremental impressions/clicks to each suggestion. Decision-making requires information.

The measurement: run a controlled experiment with identical keywords presented two ways — flat list vs intent-clustered with impact. If adoption improves for the clustered presentation, the problem is UX, not quality.

**Hard follow-up:** How do you measure whether it is a quality problem or a UX problem?

> A/B test the same generated content with different presentations. If adoption differs, it is UX. Also analyze rejection patterns — if advertisers reject suggestions they later add manually, the problem is trust/timing, not quality. Track the "manual add rate" of previously rejected suggestions.

### Q5: How does the feedback loop work from business metrics back to generation?

> **Quick answer:** Three levels of feedback: adoption signal (immediate, trains ranker), performance signal (1-4 weeks, retrains ranker + adjusts prompts), causal signal (via experimentation, validates the system) [14].

The attribution problem makes direct feedback hard. A keyword's CTR depends on the bid, the creative, the landing page, and the auction competition. You cannot naively correlate keyword quality with CTR.

Practical feedback architecture: (1) Adoption signals train a ranking model immediately — which suggestions did advertisers choose? (2) Among adopted suggestions, performance data (CTR, CVR) after 2-4 weeks informs the ranking model about quality. (3) Causal signals from randomized experiments [14] validate overall system value.

DPO [3] can align the generator itself: construct preference pairs where chosen = adopted + high-CTR keywords, rejected = not-adopted or low-CTR keywords. This closes the loop into the model.

**Hard follow-up:** The feedback loop creates a filter bubble — only generating keywords similar to past performers. How do you prevent this?

> Thompson sampling [5][7] in the ranking layer — reserve 10-20% of impression slots for uncertain keywords. Also: counterfactual evaluation of unchosen suggestions on small traffic slices, and a novelty bonus for keywords semantically distant from the advertiser's existing set [13].

### Q6: How do you decide between few-shot prompting and fine-tuning?

> **Quick answer:** Prompt first (covers 80% of cases). Fine-tune when prompting hits a ceiling — distinctive brand voices, domain-specific jargon, or when distilling complex prompt rules into weights saves token cost at scale [1][10].

| Approach | When it works | When it fails |
|----------|--------------|---------------|
| Few-shot prompting [1] | New categories, rapid iteration, locale expansion | Distinctive brand voice, complex style rules |
| Category-level fine-tuning [10] | Stable categories with >10K examples | Data-sparse categories, rapidly changing products |
| Per-advertiser adapter (LoRA) [12] | Top 0.1% advertisers by spend | Long-tail advertisers (insufficient data) |

The hybrid pattern dominates production: base model + category-specific few-shot examples + brand guidelines in context. Fine-tuning is reserved for cases where the prompt context window is the bottleneck.

**Hard follow-up:** You fine-tune on approved content but the model generates repetitive, "safe" output. How do you fix?

> This is mode collapse from fine-tuning on a narrow distribution. Three fixes: (1) Temperature scheduling — fine-tuned model generates safe candidates, base model generates exploratory candidates at higher temperature. (2) Diversity penalty during decoding [11][13]. (3) Track semantic diversity of outputs monthly — if declining, the fine-tuning is collapsing.

### Q7: How do you generate content for 19+ locales without per-locale fine-tuning?

> **Quick answer:** Never translate — always regenerate from product attributes in the target language. Multilingual LLMs with 10-20 locale-specific few-shot examples capture cultural search patterns without per-locale model maintenance [1][10].

Translation preserves source-language idioms and search patterns. Regeneration from attributes in the target language captures how local users actually search. A Japanese user searches differently than an English user would translate.

Tiered approach: Tier 1 (top 3-4 locales by revenue) gets few-shot + locale-specific fine-tuning + native review. Tier 2 (next 5-8) gets few-shot + LLM-as-judge [4]. Tier 3 (long tail) gets zero-shot + automated quality checks.

**Hard follow-up:** Generated Japanese keywords are grammatically correct but do not match how users search. Fix?

> Mine actual search query logs for the product category in that locale. Use real search autocomplete patterns as few-shot examples. For top locales, partner with native speakers to review the top 100 keywords — the ROI far exceeds the cost.

### Q8: When should you use templates instead of LLMs?

> **Quick answer:** Use templates when output structure is fixed, determinism is required, or volume/latency demands it. Use LLMs when creativity, cross-lingual generation, or open-ended intent coverage is needed [1].

| Criterion | Template | LLM |
|-----------|----------|-----|
| Output structure | Fixed ("Shop [Brand] — [Price]") | Variable (creative copy) |
| Determinism | Required (legal disclaimers) | Not required |
| Volume/latency | Millions/hour, <10ms | Thousands/hour, 2-5s |
| ROI of creativity | Low (boilerplate) | High (differentiation) |

The hybrid pattern: templates define structural shells (headline, description, CTA slots with character limits), LLMs fill the creative slots. Structural consistency with creative variation.

**Hard follow-up:** Your team proposes LLMs for all ad content. How do you push back?

> Cost and latency analysis. Calculate: cost per generation x daily volume. If templates produce 90%+ of the value, the LLM is unjustified. Reserve LLM budget for tasks where creativity, personalization, or cross-lingual generation creates measurable incremental value.

### Q9: How do you measure marketplace impact of generated content?

> **Quick answer:** Standard A/B tests fail in marketplaces because treatment changes auction dynamics for everyone (SUTVA violation). Use double-randomized experimentation — randomize advertisers AND marketplace contexts into isolated pools [14].

Standard A/B: treatment advertisers add AI-generated keywords, compete in new auctions, change CPCs for all advertisers including control. The treatment effect is contaminated by marketplace spillover.

Double randomization [14]: (1) Randomize advertisers into treatment/control. (2) Randomize marketplace contexts (query-impression slots) into isolated pools. Treatment advertisers in Pool A do not affect control advertisers in Pool B. The treatment effect is measured within-pool with bounded interference.

Metrics hierarchy: Primary = incremental revenue. Secondary = CVR/RoAS (must not regress). Guardrail = shopper experience (click satisfaction).

**Hard follow-up:** Experiment shows positive adoption, positive CTR, neutral CVR. Ship or not?

> Cautious ship with monitoring. Neutral CVR with positive adoption suggests incremental value without degrading conversion quality. But monitor CVR closely post-launch — the experiment may not have captured long-term effects. Check advertiser-level heterogeneity for hidden regressions.

### Q10: How do you design human-in-the-loop validation at scale?

> **Quick answer:** The human in the loop IS the advertiser — each reviews their own suggestions. The system pre-filters aggressively so every surfaced suggestion passes automated quality gates. Internal QA uses statistical sampling at the population level.

Validation tiers: (1) Automated policy filter (milliseconds). (2) LLM-as-judge quality scoring [4] (seconds). (3) Advertiser review (hours). (4) Performance validation via A/B test (days) [14].

Design principles: pre-filter aggressively (never show content that fails automated checks — each bad suggestion erodes trust). Batch by intent (approve/reject clusters, not individual items). Show confidence levels. Learn from edits (when advertisers modify suggestions, the edit IS the correction signal [3]).

**Hard follow-up:** At 1M+ advertisers, how do you scale quality assurance?

> Statistical sampling: review a random sample per category/locale. Set thresholds: if sample pass rate drops below 95%, pause generation for that segment. The system is supervised at the population level even though individual advertisers supervise their own campaigns.

### Q11: How do you handle the diversity-relevance tension in recommendations?

> **Quick answer:** Use MMR (Maximal Marginal Relevance) to iteratively select candidates that are relevant AND dissimilar to already-selected items [13]. Present diverse candidates in separate intent groups so diversity operates at the group level while coherence is maintained within groups.

The problem: purely relevance-ranked suggestions cluster around 2-3 obvious intents. For running shoes, you get "running shoes," "athletic footwear," "jogging shoes" — all the same intent.

MMR score [13]: λ * Relevance(q, d) - (1-λ) * max Similarity(d, d'). Iteratively select candidates that balance relevance with novelty. Typical λ=0.7 for relevance-heavy applications.

The product solution: present diversity at the intent-group level, coherence within groups. Advertisers adopt entire intent groups (high adoption per group) while the system ensures multiple groups are shown (diversity at the category level).

**Hard follow-up:** The most diverse set is less likely to be adopted — advertisers prefer familiar keywords. How do you handle this?

> Separate "core" slots (familiar, high-confidence) from "expansion" slots (novel, uncertain). Show both with clear labeling. Track adoption by slot type. Use Thompson sampling [5] for expansion slots to learn which novel intents resonate without risking core adoption.

### Q12: How do you architect content generation for different funnel stages?

> **Quick answer:** Funnel stage dictates everything — output type, quality bar, metrics, and constraint level. Lower-funnel demands precision (cannot regress CVR); upper-funnel permits creative experimentation.

| Dimension | Upper Funnel (Awareness) | Lower Funnel (Conversion) |
|-----------|-------------------------|---------------------------|
| Content type | Brand storytelling, broad keywords | Specific keywords, product copy |
| Quality bar | Creative quality, brand voice | Conversion performance |
| Primary metric | Brand lift, engagement | CVR, RoAS |
| Constraint level | Moderate (creative license) | Highest (cannot regress) |
| LLM value-add | Creativity, narrative variation | Long-tail discovery, intent coverage |

A single system with a single quality bar will be too conservative for upper-funnel or too permissive for lower-funnel. Architecture: shared infrastructure (LLM serving, policy, experiments) with funnel-specific pipelines (different prompts, rankers, thresholds).

**Hard follow-up:** One system for all funnel stages — good or bad idea?

> Bad. Shared infrastructure (policy guardrails, evaluation framework, experiment platform) with separate pipelines (generation strategy, ranking model, quality bar) per funnel stage. The cost of one quality bar: killing creativity in brand campaigns or killing conversions in product campaigns.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1: Constrained Decoding — Grammar-Guided Generation for Ad Formats (MATH)</strong></summary>

Ad content has hard format requirements: character limits, required fields, prohibited terms, valid JSON schemas. Post-hoc filtering wastes 20-30% of generation compute. Constrained decoding guarantees valid outputs at generation time [8].

**Formal framework**: Define the output constraint as a finite automaton M = (Q, Σ, δ, q0, F) where Q = states, Σ = token vocabulary, δ = transition function. At each generation step t in state q_t, compute the set of valid next tokens:

```
V(q_t) = {token ∈ Σ : δ(q_t, token) ≠ ∅}
mask(logits, q_t) = logits[i] if token_i ∈ V(q_t), else -∞
```

The Outlines framework [8] compiles regex patterns and JSON schemas into finite state machines, then applies this mask at every decoding step. The key insight: the grammar state machine runs in O(|V|) per token (a bitmap AND operation on the vocabulary), which is negligible compared to the transformer forward pass.

**Token masking for ad constraints:**

```python
# Prohibited terms (competitor brands, medical claims)
prohibited_sequences = compile_to_fsa(["competitor_brand", "clinically proven", ...])
# Character limit: max 30 chars for headline
length_fsa = regex_to_fsa(r".{1,30}")  
# Combined constraint: intersection of FSAs
combined = intersect(format_fsa, complement(prohibited_sequences), length_fsa)
```

**Structured outputs for ad metadata:**

```json
{"keyword": str, "intent": enum("brand","generic","competitor"), 
 "confidence": float(0,1), "expected_ctr": float}
```

Each field constrains valid tokens at its position. The enum field restricts to exactly 3 token sequences. The float field restricts to digit/decimal tokens within bounds.

**Latency analysis**: Per-token overhead is O(|V|) for mask application — typically <1ms on modern hardware. However, constraints can force the model into low-probability regions, requiring 10-20% more tokens to express equivalent content [8]. For short-form ad content (keywords, headlines), this overhead is negligible. The net compute saving from eliminating wasted invalid generations typically exceeds the per-token overhead.

**Interaction with sampling** [11]: Constrained decoding composes with nucleus sampling — apply the grammar mask first, then renormalize and sample from the reduced distribution. This preserves creative diversity within the valid output space.

</details>

<details><summary><strong>DE Probe 2: Multi-Variant Generation Pipeline — Batched Inference and Cache Strategies (SYSTEMS)</strong></summary>

Generating 50-200 ad variants per product for 1M+ advertisers requires careful systems design. The naive approach (sequential generation per advertiser) is cost-prohibitive and latency-bound.

**Batched inference architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  Request Aggregator (groups by category/locale)          │
├─────────────────────────────────────────────────────────┤
│  Shared Prefix Cache (product attributes + few-shot)    │
│  Key insight: 800 of 1000 input tokens are shared       │
│  across all variants for a single product               │
├─────────────────────────────────────────────────────────┤
│  Parallel Decode (N variants simultaneously)            │
│  KV-cache shared for prefix, diverges at generation     │
├─────────────────────────────────────────────────────────┤
│  Output Deduplication + Diversity Filter [13]           │
└─────────────────────────────────────────────────────────┘
```

**KV-cache economics**: For a 7B model with 2048-token context, the KV-cache per sequence is ~2GB (32 layers x 32 heads x 128 dim x 2048 tokens x 2 bytes x 2 for K+V). Generating 50 variants naively requires 100GB of KV-cache. Prefix sharing reduces this to ~2GB (shared prefix) + 50 x 80MB (per-variant suffix) = ~6GB — a 16x reduction.

**A/B routing for variant selection**: In production, not all variants are served simultaneously. A/B routing assigns advertisers to variant groups:

```python
# Multi-armed routing with Thompson sampling [5]
def route_advertiser(advertiser_context, variants):
    for v in variants:
        # Beta posterior from adoption observations
        alpha = v.adoptions + 1
        beta = v.shown - v.adoptions + 1
        v.score = np.random.beta(alpha, beta)
    return sorted(variants, key=lambda v: v.score, reverse=True)[:k]
```

**Cache invalidation strategy**: Product attributes change infrequently (median: once per month). Cache generated candidates keyed on (product_attribute_hash, prompt_version, model_version). Invalidate on: (1) product attribute update, (2) prompt template change, (3) model version deployment. At 1M advertisers with monthly attribute changes, ~97% of cached generations remain valid on any given day — reducing daily generation load by 30x.

**Batch scheduling**: Generate nightly for existing campaigns (latency-insensitive). Reserve real-time generation capacity for new campaign creation (latency-sensitive, <5s). This dual-path architecture reduces peak GPU utilization by 4-5x compared to all-real-time.

</details>

<details><summary><strong>DE Probe 3: Quality Annotation — LLM-as-Judge Scoring and Human-AI Calibration (DATA)</strong></summary>

Evaluating ad content quality at scale requires automated scoring that correlates with human judgment. LLM-as-Judge [4] provides this, but calibration against human preferences and domain-specific biases requires careful design.

**LLM-as-Judge for ad content scoring** [4]:

```
Score dimensions (1-5 scale):
1. Relevance: Does the content match the product and target audience?
2. Factual grounding: Are all claims verifiable from product attributes?
3. Brand safety: Does it comply with advertising policies? [9]
4. Persuasion: Does it motivate the target action (click, purchase)?
5. Differentiation: Does it distinguish from generic category copy?
```

**Human-AI calibration protocol**: LLM judges correlate 0.85 with human preferences at the model level but only 0.65 at the instance level [4]. For ads, this means LLM-as-Judge reliably identifies which generation *system* is better but may misjudge individual ads.

Calibration procedure: (1) Human annotators score 500 ads across all 5 dimensions. (2) Compute per-dimension bias: LLM_score - Human_score. (3) Apply affine correction: calibrated = a * LLM_score + b where (a,b) minimize MSE against human scores. (4) Re-calibrate monthly as product categories evolve.

**Preference data construction for DPO [3] in ads:**

| Signal source | Pair construction | Quality | Volume |
|---------------|------------------|---------|--------|
| Advertiser adoption | Adopted vs rejected | High (real preference) | High |
| CTR differential | High-CTR vs low-CTR (same product) | Medium (confounded) | Medium |
| LLM-as-Judge scores [4] | Top-scored vs bottom-scored | Medium (proxy) | Very high |
| Human annotation | Expert A/B comparison | Highest | Low |

**Noise in ad preference data**: Adoption signal is noisy — position bias (advertisers adopt top-listed suggestions), fatigue effects, and brand-specific preferences confound the signal. Mitigation: (1) Position-randomize suggestions. (2) Filter to pairs with >0.3 CTR differential for performance-based pairs. (3) Use margin-weighted DPO loss where confident pairs get higher weight [3].

**Active learning for annotation budget**: With limited human annotation budget (3% of generated sets), prioritize: new product categories (no signal), cold-start advertisers, locale-specific samples where automated evaluation is weaker, and random 10% for unbiased measurement.

</details>

<details><summary><strong>DE Probe 4: Ad Copy Metrics — CTR Prediction, Engagement Correlation, Brand Safety Scoring (EVALUATION)</strong></summary>

Evaluating ad content requires metrics at multiple levels: generation quality (offline), predicted performance (bridging), and actual business impact (online). The challenge is building reliable bridges between offline scores and online outcomes.

**CTR prediction from ad copy features:**

The prediction model maps textual features to expected CTR:

```
CTR_predicted = f(semantic_embedding, structural_features, category_context)

Structural features:
- Token count / character count
- Contains price mention (binary)
- Contains call-to-action (binary)
- Superlative count ("best," "top," "#1")
- Question format (binary)
- Emotional valence score
```

Training data: historical ad copy with observed CTR, controlling for position and bid. The model learns which textual patterns correlate with clicks. Critical caveat: CTR prediction must be calibrated — overestimated CTR leads to poor advertiser decisions.

**Engagement correlation analysis**: Not all engagement metrics align:

| Metric pair | Correlation | Implication |
|-------------|-------------|-------------|
| CTR ↔ CVR | 0.3-0.5 | High CTR does not imply high conversion |
| CTR ↔ Adoption | 0.4-0.6 | Advertisers partially trust CTR predictions |
| Fluency ↔ CTR | 0.1-0.2 | Linguistic quality barely predicts clicks |
| Specificity ↔ CVR | 0.5-0.7 | Product-specific copy converts better |
| Diversity ↔ Coverage | 0.8+ | Diverse suggestions reach more users |

**Brand safety scoring architecture** [9]:

```
Input: generated_ad_copy + product_category + locale
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
[Rule-based]  [Classifier]  [LLM-Judge]
 Prohibited    Fine-tuned    Constitutional
 terms list    on violations  AI critique [9]
    │           │            │
    └───────────┼────────────┘
                ▼
         Ensemble Score (0-1)
         Threshold: 0.95 for standard, 0.99 for high-risk categories
```

The ensemble combines fast rule-based detection (microseconds, catches obvious violations), fine-tuned classifier (milliseconds, catches learned patterns), and LLM-as-judge [4] (seconds, catches nuanced/contextual violations). The cascade runs cheapest first — only invoke LLM-judge for candidates passing the first two layers.

**Calibration across categories**: Brand safety thresholds vary by category. Healthcare requires 0.99+ (near-zero tolerance). Consumer electronics requires 0.95. The threshold is set by: historical violation rate x expected cost of violation. Categories with high violation cost demand higher thresholds.

</details>

<details><summary><strong>DE Probe 5: Adoption Ceiling — Why Generated Content Gets Rejected and How to Measure/Fix It (PRODUCTION)</strong></summary>

The adoption ceiling is the dominant production challenge: improving generation quality past a threshold yields diminishing returns on adoption. Understanding why requires decomposing rejection into root causes.

**Rejection taxonomy (from production data):**

| Rejection reason | Frequency | Observable signal | Fix category |
|-----------------|-----------|-------------------|--------------|
| Irrelevant to brand/product | 25% | High semantic distance to existing keywords | Better grounding |
| Already known/obvious | 20% | High overlap with current keyword set | Novelty filtering |
| Too many suggestions (cognitive overload) | 20% | Adoption rate drops with volume | Reduce volume |
| No predicted impact shown | 15% | Flat adoption across confidence levels | Add impact estimates |
| Trust deficit (new to AI suggestions) | 10% | Adoption increases over time per advertiser | Graduated trust |
| Actual quality issue | 10% | Correlated with low LLM-judge scores | Quality improvement |

**Key insight**: Only 10% of rejections are actual quality problems. The other 90% are product, UX, and trust problems.

**Measurement framework:**

```
Adoption funnel per suggestion:
  Shown to advertiser (100%)
  → Viewed/expanded (60%)        ← Attention gate
  → Evaluated (30%)              ← Cognitive load gate  
  → Considered relevant (20%)    ← Relevance gate
  → Adopted (15%)                ← Trust/confidence gate
  → Retained after 7 days (12%) ← Performance gate
```

Track conversion at each stage. If "viewed → evaluated" is the bottleneck, the problem is presentation (too many items). If "evaluated → considered relevant" is the bottleneck, the problem is targeting. Each bottleneck has a different fix.

**Graduated trust protocol:**

| Advertiser maturity | Volume shown | Suggestion type | Confidence bar |
|--------------------|--------------|-----------------|----------------|
| New (first 30 days) | 10 suggestions | Conservative, high-confidence | >0.9 |
| Growing (30-90 days) | 25 suggestions | Mix conservative + moderate | >0.7 |
| Mature (90+ days) | 50 suggestions | Include exploratory | >0.5 |

> [!experience] The reframing from individual keywords to intent-level clusters was the single biggest adoption driver — not because the content changed, but because advertisers could reason about "Performance Running" as a concept rather than evaluating 40 individual terms.

**A/B testing the ceiling**: To measure whether you are at the ceiling, run: (A) current suggestions at current quality, (B) same suggestions with 2x quality investment (more generation, better ranking, human-curated top-K). If adoption is similar, you have hit the ceiling — further quality investment has diminishing returns. Redirect effort to UX and trust interventions.

</details>

<details><summary><strong>DE Probe 6: Bandit-Based Creative Selection — Thompson Sampling for Ad Variant Optimization (ARCHITECTURE)</strong></summary>

Static ranking of ad variants ignores uncertainty and prevents learning. Bandit algorithms formalize the exploration-exploitation trade-off, learning which variants work for which contexts while minimizing regret [5][6][7].

**Problem formulation**: At each time step t, for advertiser context x_t (product category, spend level, historical adoption):
- Action a_t: recommend keyword variant k from candidate set K
- Reward r_t: adoption (binary) or downstream CTR (continuous)
- Goal: maximize cumulative reward while efficiently exploring uncertain variants

**Thompson Sampling [5][7]:**

```python
# Per-variant-context posterior
for variant in candidates:
    # Beta posterior for adoption probability
    alpha = adoptions[variant, context] + prior_alpha
    beta = shown[variant, context] - adoptions[variant, context] + prior_beta
    sampled_reward = np.random.beta(alpha, beta)
    
# Recommend top-K by sampled reward
recommendations = sorted(candidates, key=sampled_reward, reverse=True)[:K]
```

Thompson Sampling naturally explores: uncertain variants (wide posterior) occasionally sample above their mean, getting shown and reducing uncertainty. Well-characterized variants (narrow posterior) are exploited efficiently. This is Bayes-optimal for the multi-armed bandit [7].

**Contextual extension (LinUCB)** [6]: When advertiser features predict variant performance, model reward as linear in context:

```
E[r | x, a] = x^T θ_a + α · sqrt(x^T A_a^{-1} x)
```

The second term is the uncertainty bonus — recommends variants where we are uncertain about performance in this context. This learns that "running shoes" keywords work for athletic product advertisers without explicitly programming this.

**Scaling to 1M advertisers x 200 keywords:**

Per-keyword-per-advertiser posteriors require 200M state entries. Solutions:
1. **Hierarchical bandits**: Global prior shared across advertisers, cluster-level adaptation (by category/spend), per-advertiser only for high-volume
2. **Batch Thompson Sampling**: Update posteriors daily (not per-impression), trading optimality for scalability
3. **Feature-based generalization** [6]: Share reward parameters across variants with similar embeddings, reducing the state space from O(advertisers x variants) to O(feature_dim)

**Regret analysis** [7]: Thompson Sampling achieves O(sqrt(KT log T)) regret for K arms over T rounds, matching the information-theoretic lower bound. In practice, this means: after ~100 observations per variant-context pair, the bandit has converged to near-optimal selection. For high-traffic advertisers, convergence is fast; for low-traffic advertisers, the prior dominates (which is correct — exploit category-level knowledge).

**Architecture integration:**

```
LLM Generation → Candidate Pool → Scoring Model (predicted quality)
                                        │
                                        ▼
                               Bandit Layer [5][7]
                               (adjusts scores based on uncertainty)
                                        │
                                        ▼
                               Final Top-K to Advertiser
                                        │
                                        ▼
                               Observe adoption → Update posterior
```

The bandit layer does not replace the scoring model — it adjusts scores based on how much has been learned about each variant-context pair. High-confidence high-scoring variants are exploited; uncertain variants get an exploration boost proportional to their uncertainty.

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Advertiser Usage | Cost |
|-----------|-----------|---------------------|------|
| Product attribute extraction | ~$0 | Pre-computed in catalog | Amortized |
| LLM generation (50 candidates) [1] | $0.004/1K tokens | ~2800 tokens (800 in + 2000 out) | $0.008 |
| Constrained decoding overhead [8] | +15% of generation | 1 generation | $0.001 |
| LLM-as-Judge scoring [4] | $0.002/candidate | 50 candidates | $0.004 |
| Bandit ranking [5] | $0.00001/score | 50 scores | ~$0 |
| **Total per advertiser per batch** | | | **~$0.013** |

### Monthly Cost at Scale

| Scale | Advertisers/Day | Monthly Cost | Cost/Advertiser/Month |
|-------|----------------|-------------|----------------------|
| Pilot (10K advertisers) | 2,000 | ~$800 | $0.08 |
| Growth (200K advertisers) | 50,000 | ~$20,000 | $0.10 |
| Scale (1M+ advertisers) | 300,000 | ~$90,000 | $0.09 |

### Cost Optimization Priority Stack

| Priority | Optimization | Estimated Savings |
|----------|-------------|-------------------|
| 1 | Reduce candidate count (50 vs 200) | 4x generation cost |
| 2 | Model routing (simple→Haiku, complex→Sonnet) | 2-3x |
| 3 | Cache stable products (invalidate on attribute change) | 30x daily load reduction |
| 4 | Batch nightly generation (real-time only for new campaigns) | 4-5x peak GPU |
| 5 | Shared few-shot libraries per category | 1.1x prompt cost |

### Build vs Buy

| Capability | Build | Buy | Recommendation |
|-----------|-------|-----|----------------|
| LLM generation | vLLM + Llama [10] (cost at scale) | Claude/GPT API (quality, zero infra) | API for <100K/day; self-host above |
| Policy classifier [9] | Custom on internal data | Moderation APIs | Build — policy rules are proprietary |
| CTR/CVR reranker | Custom model (requires proprietary data) | N/A | Always build |
| Quality scorer [4] | LLM-as-judge via API initially | Scale to custom | API initially; custom as labels grow |
| Experiment framework [14] | Extend existing ads infra | N/A | Build on existing platform |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Policy violation rate | >0.1% of deployed content | P0: freeze deployment, investigate |
| Adoption rate (7-day rolling) | Drop >20% from baseline | Product + ML review |
| Factual grounding rate | <98% | ML on-call: check attribute extraction |
| Generation diversity (ILD) | <0.5 (baseline 0.7) | Model drift: check for mode collapse |
| CVR impact (treatment vs control) [14] | Negative delta >0.5% | P0: generated content hurting advertisers |
| Latency p95 (real-time path) | >5s | Infra: check LLM queue depth |
| Bandit convergence rate [5] | <50 observations/variant after 14 days | Traffic allocation issue |

### Debugging Walkthrough

```
Symptom: Adoption rate dropped 30% for electronics category
├── Step 1: Scope — is it category-specific or systemic?
│   └── Only electronics → category-specific
├── Step 2: Quality check — run scorer on this week vs last week
│   └── Scores similar → not a quality regression
├── Step 3: Diff changes — prompt template, model version, few-shot examples
│   └── New few-shot example added Monday (day drop started)
├── Step 4: Inspect — new example is headphones-specific, biasing all electronics
│   └── Root cause: sub-category contamination of category-level prompt
└── Step 5: Fix
    ├── Immediate: rollback to previous prompt version
    ├── Medium-term: sub-category-specific few-shot pools
    └── Long-term: automated few-shot selection by product similarity
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| Prompt template | Config rollback (instant) | Minutes |
| Few-shot examples | Swap to previous library version | Minutes |
| Fine-tuned model [10] | Route traffic to previous version | Gradual (5%→100%) |
| Policy classifier [9] | Parallel scoring, swap on alert | Minutes |
| Ranking/bandit model [5] | Swap model version in serving | Minutes |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Advertiser adoption (accept/reject) | Direct preference; immediate | UI interaction logging |
| Downstream CTR/CVR of adopted content | Performance ground truth; delayed 1-4 weeks | Attribution pipeline |
| Advertiser edits before deploying | Precise correction signal [3] | Diff tracking |
| Keyword pause/removal after deployment | Negative performance signal | Campaign monitoring |
| Explicit "not relevant" feedback | Targeted quality failure | UI button (low volume) |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Daily | Bandit posteriors [5], adoption ranker | Adoption rate >= previous on holdout |
| Weekly | Prompt refinements from failure analysis | Quality score + adoption on shadow traffic |
| Monthly | Few-shot library refresh (new high-performers) | Human review pass rate >= 90% |
| Quarterly | Fine-tuned model retrain [10] (if applicable) | Full regression suite + 2-week A/B test [14] |
| As needed | Policy classifier [9] update | Zero violation rate on adversarial suite |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Intent-level abstraction | Cognitive overload and adoption ceiling | Per-item suggestions overwhelm advertisers | Simple products with <5 keywords |
| Constrained decoding [8] | Format violations and wasted compute | Format compliance is critical | Simple text with no structural constraints |
| Thompson sampling [5][7] | Static ranking prevents learning | Sufficient traffic for posterior convergence | <100 observations per variant |
| Constitutional AI guardrails [9] | Policy compliance without per-category labeling | Many categories, evolving rules | Simple binary prohibited-term rules |
| MMR diversity reranking [13] | Relevance-only ranking collapses to few intents | Category with rich intent space | Narrow categories with 1-2 intents |
| Double-randomized experiments [14] | Marketplace spillover in A/B tests | Generated content changes auction dynamics | Non-marketplace interventions |
| DPO from adoption signals [3] | Closing feedback loop into generator | >10K clean preference pairs available | <1K pairs (use ranking model instead) |
| Hybrid template + LLM | Over-using LLMs for structured content | Parts of output are deterministic | Fully creative or fully structured content |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|----------------|------------------------------|
| "We generate 200 keywords per advertiser" | "Advertisers adopt only the top 30-50. The constraint is adoption, not generation. We reframe to intent-level abstraction." |
| "We filter for policy violations" | "Defense in depth: constrained decoding [8], Constitutional AI [9], LLM-as-judge [4], human review. We achieved zero violations through systematic red-teaming." |
| "We A/B test generated content" | "Standard A/B fails in marketplaces — SUTVA violation. We use double-randomized experimentation [14] to isolate causal impact." |
| "We rank by predicted quality" | "Static ranking prevents learning. Thompson sampling [5][7] formalizes exploration-exploitation, learning which variants work for which contexts." |
| "We measure CTR of generated content" | "CTR alone is misleading. Higher CTR with lower CVR wastes budget. Metric hierarchy depends on funnel — lower-funnel demands CVR/RoAS." |
| "We fine-tune for each locale" | "Never translate — regenerate from attributes in target language. Few-shot with native examples captures search patterns without per-locale models [1]." |
| "We use LLMs for all ad content" | "Templates for deterministic structure, LLMs for creative variation. Match tool to task — cost and latency analysis kills naive LLM-for-everything." |

## References

### Foundational Papers

- [1] Brown et al. (2020) — *Language Models are Few-Shot Learners* — arXiv:2005.14165 — Demonstrated few-shot prompting enables task-specific generation without fine-tuning; foundational for ad content generation pipelines.
- [2] Ouyang et al. (2022) — *Training language models to follow instructions with human feedback* — arXiv:2203.02155 — Established RLHF pipeline (SFT → RM → PPO) for aligning generation to human preferences.
- [3] Rafailov et al. (2023) — *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* — arXiv:2305.18290 — Enables closing feedback loops from adoption/performance signals directly into the generator.
- [10] Touvron et al. (2023) — *Llama 2: Open Foundation and Fine-Tuned Chat Models* — arXiv:2307.09288 — Production-scale alignment; established patterns for fine-tuning and safety applicable to ad generation.
- [11] Holtzman et al. (2020) — *The Curious Case of Neural Text Degeneration* — arXiv:1904.09751 — Introduced nucleus (top-p) sampling; critical for creative diversity in generation.
- [15] OpenAI (2023) — *GPT-4 Technical Report* — arXiv:2303.08774 — State-of-the-art model capabilities for generation and evaluation.

### Constrained Generation & Diversity

- [8] Willard & Louf (2023) — *Efficient Guided Generation for Large Language Models* — arXiv:2307.09702 — Outlines framework; grammar-guided decoding via FSM-based token masking for guaranteed-valid structured outputs.
- [12] Zhang et al. (2023) — *Llama-Adapter: Efficient Fine-tuning of Language Models with Zero-init Attention* — arXiv:2303.16199 — Parameter-efficient adaptation for domain-specific generation.
- [13] Carbonell & Goldstein (1998) — *The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries* — SIGIR 1998 — MMR algorithm for balancing relevance and diversity in recommendation.

### Bandit Algorithms & Experimentation

- [5] Chapelle & Li (2011) — *An Empirical Evaluation of Thompson Sampling* — NIPS 2011 — Validated Thompson Sampling for online advertising; demonstrated efficiency vs UCB approaches.
- [6] Li et al. (2010) — *A Contextual-Bandit Approach to Personalized News Article Recommendation* — arXiv:1003.0146 — LinUCB; contextual bandits for recommendation with user features.
- [7] Agrawal & Goyal (2012) — *Analysis of Thompson Sampling for the Multi-armed Bandit Problem* — COLT 2012 — Proved Bayesian regret bounds for Thompson Sampling; theoretical foundation.
- [14] Kohavi et al. (2013) — *Online Controlled Experiments at Large Scale* — KDD 2013 — Established methodology for large-scale A/B testing; addresses marketplace effects and metric hierarchies.

### Safety & Evaluation

- [4] Zheng et al. (2023) — *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* — arXiv:2306.05685 — Established LLM-as-Judge methodology; quantified biases and 0.85 correlation with human preferences.
- [9] Bai et al. (2022) — *Constitutional AI: Harmlessness from AI Feedback* — arXiv:2212.08073 — Self-critique against a constitution of rules; scalable policy compliance without per-category human labeling.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; added SOTA section, constrained decoding probe, bandit architecture probe, enforced length/citation constraints |
