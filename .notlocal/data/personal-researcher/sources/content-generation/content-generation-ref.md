---
title: "Content Generation Ref"
source: "data/researcher/reports/content-generation-ref.md"
ingestedAt: "2026-05-17T14:56:42Z"
truncated: true
originalChars: 105825
---
# GenAI Content Generation System Design — Interview Prep

> **Navigation**: [[#Design Flow Framework]] | [[#Full System Design Walkthrough (Principal/Director Level, ~4 min)]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Advanced Patterns Summary]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]


## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Output type, target metric, brand/policy constraints, one-shot vs continuous | Ad copy vs keywords vs product descriptions? Optimizing CTR, CVR, or adoption? |
| 2. Identify constraints | Brand safety, factual accuracy, advertiser trust, policy compliance, cost of bad output | Lower-funnel ads can't regress CVR or RoAS. Advertiser trust gates adoption. |
| 3. Propose baseline | Prompt-driven LLM with templates + few-shot examples | Prove the pattern generates plausible content before adding complexity |
| 4. Identify gaps | Generic output, hallucinated features, brand drift, no performance signal, adoption ceiling | The constraint isn't generation quality — it's adoption |
| 5. Introduce improvements | Critic/reranker, fine-tuning on approved examples, feedback loops, human-in-loop, intent-level abstraction | Each improvement targets a specific gap in baseline |
| 6. Add evaluation + guardrails | Human review pass rate, policy violations, A/B testing, prohibited claims filter, regression testing | Offline quality metrics are necessary but not sufficient — business metrics decide |
| 7. Discuss scaling tradeoffs | More candidates vs cost, fine-tuning vs flexibility, feedback loops vs attribution, i18n vs locale quality | Token cost grows linearly; advertiser trust doesn't |

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Full System Design Walkthrough (Principal/Director Level, ~4 min)

### Opening Frame (10s)

"Content generation for ads is fundamentally an adoption problem, not a generation problem. LLMs can produce thousands of keyword or copy variants — but the constraint that matters is whether advertisers trust the output enough to deploy it into their campaigns."

> [!experience] From my experience at Amazon Ads, we found that advertisers adopt only the top 30-50 of 200 recommended keywords. More generation doesn't help if adoption is capped. The system must optimize for advertiser trust and downstream performance, not just output volume.

### 1. Clarify Requirements

Before designing anything, I'd ask:

- **Output type**: What content are we generating? Keywords, ad copy (headlines/descriptions), product descriptions, audience targeting suggestions? Each has different quality bars and evaluation criteria.
- **Target metric**: What does "good" mean? CTR optimization favors clickbait; CVR optimization favors specificity; adoption rate measures whether advertisers actually use the output. These often conflict — an ad that maximizes clicks may not maximize conversions.
- **Funnel position**: Is this for upper-funnel (awareness, brand) or lower-funnel (conversion, Sponsored Products)? Lower-funnel has harder constraints — can't regress CVR or RoAS because advertisers measure performance directly.
- **Brand/policy constraints**: What can't the system say? Prohibited claims (medical, financial), competitor mentions, trademark restrictions, locale-specific regulations (EU vs US advertising law)?
- **One-shot vs continuous**: Is this a one-time generation (create keywords at campaign launch) or continuous (refresh copy based on performance signals)?
- **Scale**: How many advertisers, how many locales, how many content items per request? What's the latency requirement — batch generation or real-time?
- **Trust model**: Do advertisers review and approve generated content before it goes live, or is it auto-deployed? This changes the entire system design.

**Principal signal**: Frame requirements in terms of business risk, not technical features. "The accuracy bar depends on whether a bad keyword wastes ad spend or damages brand reputation. Those require different safety margins."

### 2. Identify Constraints

- **Brand safety**: Generated content represents the advertiser's brand. A hallucinated product feature or an off-brand tone damages the advertiser's trust in the platform. This is existential for an ads business — advertiser trust is the asset.
- **Factual accuracy**: Content must be grounded in real product attributes. An LLM that invents features the product doesn't have creates legal liability and erodes advertiser trust.
- **Policy compliance**: Advertising platforms have strict content policies — no prohibited claims, no competitor disparagement, no misleading language. Violations create regulatory risk and can get advertisers banned.
- **Advertiser trust**:

> [!experience] From my experience at Amazon Ads, the hardest constraint is earning advertiser trust in AI-generated content. Advertisers are cautious about letting AI touch their campaigns, especially in lower-funnel where bad targeting directly impacts RoAS.
- **Cost of bad output**: A bad search result is a minor annoyance. A bad ad keyword wastes real advertiser budget. A bad ad copy that violates policy can trigger regulatory action. The cost of errors is asymmetric — one bad output can destroy trust that took months to build.
- **Evaluation difficulty**: Unlike summarization or QA, there's no single "correct" answer for ad content. Quality is only measurable through downstream business metrics (CTR, CVR, adoption), which take days or weeks to observe.
- **Lower-funnel rigidity**: For Sponsored Products, the system must not regress CVR or RoAS. This means aggressive filtering and conservative rollout — you'd rather generate fewer, higher-quality suggestions than flood advertisers with mediocre options.

### 3. Propose Baseline (Template + LLM)

**Architecture:**

```
┌──────────────────┐    ┌────────────────┐    ┌─────────────────────┐    ┌────────────────┐    ┌──────────────┐
│ Product Catalog  │───▶│   Attribute    │───▶│ Prompt Construction │───▶│ LLM Generation │───▶│  Candidate   │
│ / ASIN Data      │    │  Extraction    │    │ (few-shot + policy) │    │ (N candidates) │    │  Pool        │
└──────────────────┘    └────────────────┘    └─────────────────────┘    └────────────────┘    └──────┬───────┘
                                                                                                      │
                    ┌─────────────────────────────────────────────────────────────────────────────────┘
                    ▼
┌──────────────┐    ┌────────────────┐    ┌───────────────┐    ┌──────────────────┐    ┌──────────────┐
│Policy Filter │───▶│ Quality Filter │───▶│ Top-K Ranking │───▶│Advertiser Review │───▶│    Deploy     │
└──────────────┘    └────────────────┘    └───────────────┘    └──────────────────┘    └──────┬───────┘
                                                                                              │
                    ┌─────────────────────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│Deployed Content  │───▶│ Performance Data   │───▶│ Feedback Signal │─ ─ ─▶ (back to Generation + Ranking)
│                  │    │ (CTR / CVR / RoAS) │    │                 │
└──────────────────┘    └────────────────────┘    └─────────────────┘
```

**Components:**
- **Input extraction**: Pull product title, category, attributes, existing keywords, price, and brand from catalog data. This grounds the LLM in facts rather than letting it hallucinate features.
- **Prompt template**: Few-shot examples showing (product attributes → high-performing keywords/copy) [1][2]. Include policy constraints in the system prompt. Use low temperature (0.2-0.4) for factual consistency, moderate temperature (0.5-0.7) for creative copy.
- **Candidate generation**: Generate N candidates (e.g., 50-200 keywords, 10-20 copy variants) per product.
- **Basic filtering**: Regex/rule-based filter for prohibited terms, policy violations, duplicate detection, length constraints.
- **Human-in-the-loop**: Advertiser reviews and selects which suggestions to deploy. This is not a weakness of the system — it's a feature.

> [!experience] From my experience at Amazon Ads, the key insight was: use LLMs only for GENERATION with human validation. This gives you speed without contaminating core auction/ranking models with unvetted content.

**Why start here**: This baseline can ship in weeks, immediately reduces the content creation bottleneck, and establishes a feedback loop (which suggestions do advertisers actually adopt?). Our keyword generation pipeline cut cycle time from 8 weeks to 2-3 days using this pattern.

### 4. Identify Gaps (Where Baseline Fails)

| Gap | Symptom | Root Cause |
|-----|---------|------------|
| **Generic output** | Keywords are obvious, non-differentiated | LLM produces the same suggestions for similar products. No personalization to advertiser's competitive position. |
| **Hallucinated features** | Copy mentions features the product doesn't have | LLM generates plausible but fabricated attributes. Not grounded in actual product data. |
| **Brand drift** | Tone/voice doesn't match advertiser's brand | Few-shot examples can't capture every brand's voice. One-size-fits-all prompting. |
| **No performance signal** | System doesn't learn which content performs well | Baseline has no feedback loop from CTR/CVR back to generation. Quality is static. |
| **Adoption ceiling** | Advertisers adopt only top 30-50 of 200 suggestions | This is the EARNED SECRET: the constraint isn't generation quality — it's adoption. More keywords don't help if advertisers only adopt the top 30. The system over-generates and under-personalizes. |
| **Locale mismatch** | Content doesn't resonate across locales | Direct translation loses cultural context, idiom, and search behavior. |
| **Policy violations at scale** | Rule-based filters miss subtle policy violations | Regex can't catch nuanced claims ("clinically proven" in a cosmetics ad) or context-dependent violations. |

**The adoption insight**:

> [!experience] From my experience at Amazon Ads, we discovered that advertisers adopted only the top 30-50 of 200 recommended keywords. This reframed the entire problem — we weren't solving a generation problem, we were solving a ranking and relevance problem. The system needed to generate fewer, better-ranked suggestions, not more. This led us to reframe keyword management as intent-level optimization rather than per-keyword optimization.

### 5. Introduce Improvements

#### 5a. Intent-Level Abstraction

Instead of generating individual keywords, generate at the intent level: what is the advertiser trying to capture?

**Example**: For a running shoe, instead of generating 200 individual keywords, generate 5-7 intent clusters:
- Performance running (marathon, tempo, race day)
- Comfort/lifestyle (everyday running, cushioned, walking)
- Brand-seekers (specific model names, competitor switches)
- Problem-solvers (plantar fasciitis, wide feet, overpronation)
- Deal-seekers (sale, discount, affordable running shoes)

Each intent cluster maps to a coherent keyword group. The advertiser reasons about intents, not individual words. This was the reframing we applied at Amazon Ads — intent-level optimization reduced cognitive load and increased adoption because advertisers could say "yes, I want to capture comfort-seekers" rather than evaluating 200 individual terms.

**Risk framing**: (P0) Business: wrong intent clusters mislead advertisers into wasted spend on irrelevant traffic | (P1) Technical: intent clustering quality degrades for niche products with ambiguous category boundaries | (P2) Org: product team must redesign advertiser UX around intent-level presentation rather than keyword lists

**Design choice**: Intent-level abstraction vs per-keyword generation
- **Pros**: Reduces cognitive load for advertisers (evaluate 5-7 clusters vs 200 keywords); maps to how advertisers think about their business; enables cluster-level adoption and performance measurement
- **Cons**: Requires robust intent clustering (bad clusters are worse than a flat list); adds a layer of abstraction that may confuse data-driven advertisers who want keyword-level control
- **Why chosen** (working backward from requirements): Adoption data showed advertisers only used top 30-50 of 200 keywords — the bottleneck was cognitive load, not generation quality. Intent-level framing directly addresses the adoption ceiling.
- **Alternative considered**: Per-keyword generation with better ranking. Rejected because even perfectly ranked keywords still require individual evaluation, which doesn't scale with advertiser attention.

#### 5b. Critic/Reranker Pipeline

```
LLM Generator → Candidate Pool → Critic Model (brand alignment, factuality, policy) → Reranker (predicted CTR/CVR) → Top-K → Advertiser
```

- **Critic model**: A second LLM pass (or specialized classifier) that evaluates each candidate for: factual grounding (does the claim match product attributes?) [11], brand alignment (does the tone match?), policy compliance (any violations?) [3]. This catches what the generator misses.
- **Performance reranker**: Predict CTR/CVR for each candidate using historical performance data. Rank candidates by expected business impact, not just generation quality.
- **Diversity filter**: Ensure the final set covers multiple intents, not just variations of the obvious keywords.

#### 5c. Fine-Tuning on Approved Examples

Use advertiser adoption signals as training data [1][15]: keywords/copy that advertisers approved and that subsequently performed well become positive examples.

**Caution**: Fine-tuning creates a feedback loop. If the model learns to generate only what was adopted before, it converges to safe, generic suggestions [1]. Maintain an exploration budget — always include a fraction of novel suggestions alongside fine-tuned safe picks.

**Risk framing**: (P0) Business: mode collapse from fine-tuning produces repetitive suggestions, leading to declining adoption and advertiser churn | (P1) Technical: training data curation overhead grows with each retraining cycle; stale data must be filtered without losing signal | (P2) Org: requires regular retraining pipeline ownership — unclear whether ML platform team or product ML team owns this

#### 5d. Feedback Loops from Performance Signals

```
Generated Content → Deployed → Performance Data (CTR, CVR, RoAS) → Feedback Signal → Improve Generator
```

**Challenge**: Attribution is hard. A keyword's performance depends on the ad creative, the landing page, the bid, the competition, and the auction dynamics — not just keyword quality. Isolating the content quality signal from confounders requires careful experimentation.

> [!experience] From my experience at Amazon Ads, we designed a double-randomized experimentation framework for measuring marketplace impact of generated content [12][13]. This controlled for both advertiser-side confounders (different bid strategies) and marketplace-side confounders (auction dynamics), allowing us to attribute performance changes specifically to the generated content.

**Risk framing**: (P0) Business: wrong attribution leads to optimizing the wrong signal, causing advertiser value destruction through misallocated spend | (P1) Technical: confounders (bid strategy, seasonality, auction dynamics) make causal inference genuinely hard — observational data gives wrong answers [14] | (P2) Org: requires experimentation infrastructure and data science support that may not exist or may be shared across teams

**Design choice**: Double-randomized experimentation vs standard A/B testing
- **Pros**: Isolates causal effect from marketplace spillover; produces trustworthy attribution signal; enables confident ship/no-ship decisions
- **Cons**: More complex to implement and analyze; requires marketplace-level randomization infrastructure; reduces statistical power (smaller effective sample per cell)
- **Why chosen** (working backward from requirements): Standard A/B tests in marketplace settings violate SUTVA — treatment changes auction dynamics for control advertisers too [13]. Wrong attribution signals lead to wrong optimization, which at scale destroys advertiser value.
- **Alternative considered**: Standard advertiser-level A/B testing with post-hoc marketplace adjustment. Rejected because post-hoc corrections rely on modeling assumptions that are hard to validate, and the stakes (advertiser trust, budget allocation) demand cleaner causal evidence.

#### 5e. Zero-Shot/Few-Shot for Internationalization

For expanding to new locales (we scaled to 19+ locales at Amazon Ads):

- **Zero-shot**: Use multilingual LLMs with locale-specific instructions [17][18]. Works surprisingly well for keyword generation because product attributes are often translatable.
- **Few-shot**: Curate 10-20 high-quality examples per locale from native speakers [2]. This captures cultural nuances (e.g., search behavior in Japan differs fundamentally from the US).
- **Never translate — regenerate**: Don't translate English keywords. Regenerate from product attributes in the target language. Translation preserves English search patterns; regeneration captures local search behavior.

#### 5f. Human-in-the-Loop Validation Design

The validation layer is not a band-aid — it's an architectural choice that enables speed without risk:

1. **Tier 1 — Automated**: Policy filters, factual grounding checks, brand-term validation (automated, milliseconds)
2. **Tier 2 — LLM-as-judge**: Second model evaluates quality, relevance, and compliance (automated, seconds)
3. **Tier 3 — Advertiser review**: Advertiser sees top-K suggestions, approves/rejects/edits (human, hours to days)
4. **Tier 4 — Performance validation**: A/B test approved content against existing campaigns (automated, days to weeks)

The key insight: each tier is a gate that catches different failure modes. Automated filters catch obvious violations. LLM critics catch subtle quality issues [9][10]. Advertiser review catches brand misalignment. Performance testing catches business impact regressions.

**Risk framing**: (P0) Business: removing human validation too early leads to policy violations at scale, destroying advertiser and platform trust | (P1) Technical: review queue becomes a bottleneck if suggestion volume outpaces advertiser attention | (P2) Org: unclear ownership between ML team and content/policy team over what gets auto-approved vs human-reviewed

**Design choice**: LLM generation + human validation vs full automation
- **Pros**: Captures the speed benefit of LLM generation (8 weeks to 2-3 days) while maintaining trust through human approval; prevents unvetted content from entering the auction system; builds advertiser trust incrementally
- **Cons**: Advertiser review introduces latency (hours to days); adoption depends on advertiser engagement with the review flow; scales with advertiser count but not with per-advertiser volume
- **Why chosen** (working backward from requirements): The cost of a bad ad (wasted budget, policy violation, brand damage) is asymmetric — one bad output destroys months of trust. Full automation is the goal state, but trust must be earned through demonstrated accuracy first.
- **Alternative considered**: Full automation with post-hoc monitoring only. Rejected because the cost of errors in advertising (real money, regulatory risk) is too high for a system that hasn't yet demonstrated reliability at scale.

#### Improved Architecture (Full Enhanced System)

```
┌──────────────┐    ┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│   Product    │───▶│ Intent-Level  │───▶│ LLM Generator  │───▶│  Candidate   │
│   Catalog    │    │ Abstraction   │    │ (fine-tuned)   │    │  Pool        │
└──────────────┘    └───────────────┘    └────────────────┘    └──────┬───────┘
                                                                      │
                    ┌─────────────────────────────────────────────────┘
                    ▼
┌──────────────┐    ┌───────────────┐    ┌────────────────┐
│   Critic /   │───▶│  Performance  │───▶│  Top-K         │
│   Reranker   │    │  Reranker     │    │  Candidates    │
└──────────────┘    └───────────────┘    └───────┬────────┘
                                                  │
                    ┌─────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  Multi-Tier Validation Pipeline                          │
│  ┌──────────┐   ┌───────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ Automated│──▶│LLM-Judge  │──▶│  Advertiser  │──▶│   A/B Test     │  │
│  │ Filters  │   │ Quality   │   │  Review      │   │   Validation   │  │
│  └──────────┘   └───────────┘   └──────────────┘   └───────┬────────┘  │
└──────────────────────────────────────────────────────────────┼──────────┘
                                                               │
┌──────────────┐    ┌───────────────┐    ┌────────────────┐    │
│  Locale      │    │  Performance  │◀───│    Deploy      │◀───┘
│  Router      │    │  Data         │    │                │
│  (i18n)      │    │ (CTR/CVR)    │    └────────────────┘
└──────┬───────┘    └───────┬───────┘
       │                    │
       ▼                    ▼
  Locale-specific    ┌────────────────┐
  Generation         │ Feedback Loop  │──▶ (back to Reranker + Generator)
  Pipelines          └────────────────┘
```

### 6. Evaluation + Guardrails

#### Offline Evaluation (Necessary but Not Sufficient)

| Metric | What It Measures | Target |
|--------|------------------|--------|
| Factual grounding rate [11] | % of claims traceable to product attributes | >98% |
| Policy violation rate | % of outputs flagging policy rules | <0.1% |
| Diversity score | Semantic diversity of generated candidates | >0.7 (pairwise dissimilarity) |
| Human review pass rate | % of outputs approved by human reviewers | >85% |
| Fluency/grammaticality [9] | Language quality score | >4.5/5 |
| Brand alignment score | LLM-as-judge brand consistency rating [10] | >4/5 |

#### Online Evaluation (Business Metrics That Actually Matter)

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| Adoption rate | % of suggestions advertisers deploy | The real constraint. If adoption is flat, generation quality doesn't matter. |
| Coverage | % of advertisers receiving suggestions | Reach of the system |
| CTR lift | Click-through rate of generated vs existing content | Direct performance signal |
| CVR lift | Conversion rate of generated vs existing content | Lower-funnel health check — can't regress this |
| RoAS impact | Return on ad spend change | Advertiser's bottom line |
| Time to first keyword | How quickly advertisers populate new campaigns | Operational efficiency gain |

#### Guardrails

- **Input guardrails**: Validate product data completeness before generation. Refuse to generate for products with insufficient attribute data rather than hallucinate.
- **Output guardrails**: Policy classifier (fine-tuned on historical violations), prohibited claims filter, trademark detector, competitor mention detector.
- **Brand safety layer**:

> [!experience] From my experience at Amazon Ads, we led security testing for GenAI models achieving zero vulnerabilities across 9 categories including brand safety and policy compliance [3]. This required systematic red-teaming: adversarial inputs, edge cases, and locale-specific policy variations.
- **Regression testing**: Before any model update, run the full generation pipeline against a golden set. Compare outputs to established baselines. Any regression in policy violation rate or factual grounding rate blocks deployment.
- **A/B testing for real decisions**: Offline metrics are proxies. The only way to know if generated content is "good" is to measure business impact through controlled experiments [12]. Our double-randomized framework measured marketplace-level impact — not just advertiser-level A/B tests, which can miss competition effects [13].

### 7. Scaling Tradeoffs

#### More Candidates vs Cost

Generating 200 candidates costs 4x more than generating 50 — but if advertisers only adopt 30-50 anyway, the marginal value of candidates 51-200 is near zero. **Optimization**: Generate fewer, higher-quality candidates using better prompting and intent-level abstraction. Invest compute in ranking, not generation.

#### Fine-Tuning vs Flexibility

Fine-tuning on approved content improves quality for common patterns but reduces ability to generate novel suggestions [15][16]. **Tradeoff**: Use fine-tuning for the "safe" candidate pool (high-probability adoptions) and zero-shot/few-shot for the "exploration" pool (novel suggestions). Maintain a 70/30 or 80/20 split.

#### Feedback Loops vs Attribution

Connecting generation quality to CTR/CVR is the holy grail but attribution is genuinely hard [14]. A keyword's performance is confounded by bid strategy, landing page quality, auction dynamics, and seasonality. **Approach**: Use randomized experiments rather than observational data [12][13]. Causal inference requires experimental design, not post-hoc correlation.

#### Centralized vs Per-Advertiser Models

One model for all advertisers is simpler but can't capture brand-specific voice. Per-advertiser fine-tuning is expensive and data-sparse for small advertisers. **Middle ground**: Cluster advertisers by category/brand-voice similarity, fine-tune per cluster, allow large advertisers to provide brand guidelines as prompt context.

#### i18n: Quality vs Locale Coverage

Expanding to 19+ locales creates a quality vs coverage tradeoff. **Approach from experience**: Zero-shot works for 80% of locales with structured product data [17][18]. Few-shot with 10-20 native examples closes the gap for most remaining cases. Full locale-specific fine-tuning reserved for top-revenue locales only.

**Risk framing**: (P0) Business: culturally inappropriate content in a new market causes brand damage and potential regulatory action | (P1) Technical: zero-shot quality varies unpredictably across locales — works well for Romance languages, poorly for CJK without examples | (P2) Org: no native speaker review capacity for long-tail locales means quality issues go undetected until advertiser complaints

**Design choice**: Zero-shot locale expansion vs per-locale fine-tuning
- **Pros**: Scales to 19+ locales without per-locale training data or model maintenance; fast time-to-market for new locales; few-shot examples (10-20) are cheap to curate
- **Cons**: Quality floor is lower for linguistically distant locales; cultural nuances in search behavior may be missed; no native review for long-tail locales
- **Why chosen** (working backward from requirements): Per-locale fine-tuning at 19+ locales is operationally unsustainable — each locale needs training data, evaluation, and ongoing maintenance. The tiered approach (fine-tune top 3-4, few-shot mid-tier, zero-shot long-tail) matches investment to revenue.
- **Alternative considered**: Per-locale fine-tuning for all locales. Rejected because the data and maintenance cost scales linearly with locale count while revenue follows a power law — most locales don't justify the investment.

#### Real-Time vs Batch

Real-time generation (at campaign creation) provides better UX but costs more and requires low-latency inference. Batch generation (nightly refresh) is cheaper but suggestions may be stale. **Hybrid**: Batch-generate for existing campaigns, real-time generate for new campaign creation flows where the advertiser is waiting.

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Interview Q&A Bank

### Q1: How would you design a content generation pipeline for ads at scale?

**Principal Answer**: The critical framing is that ad content generation is an adoption problem, not a generation problem. LLMs can produce hundreds of keyword or copy variants — the constraint is whether advertisers trust the output enough to deploy it.

> [!experience] From my experience at Amazon Ads, I designed a pipeline that reduced keyword generation from 8 weeks to 2-3 days [7]. The architecture:

1. **Input**: Product catalog data (attributes, category, existing keywords, brand guidelines)
2. **Generation**: LLM with few-shot examples, constrained by product attributes. Generate at the intent level — clusters of semantically related keywords — not individual terms.
3. **Filtering**: Multi-layer guardrails — automated policy checks, LLM-as-judge quality scoring, factual grounding verification
4. **Ranking**: Predict adoption likelihood and expected performance (CTR/CVR). Surface the top 30-50 candidates, not 200.
5. **Validation**: Human-in-the-loop — advertiser reviews and approves before deployment
6. **Feedback**: Downstream performance signals feed back into ranking and generation

**Production Architecture:**

```
┌───────────────┐    ┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│   Product     │───▶│   Intent      │───▶│  LLM Generator │───▶│  Candidate   │
│   Catalog     │    │  Clustering   │    │  (few-shot)    │    │  Pool        │
└───────────────┘    └───────────────┘    └────────────────┘    └──────┬───────┘
                                                                       │
                     ┌─────────────────────────────────────────────────┘
                     ▼
┌───────────────┐    ┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│  Policy +     │───▶│ LLM-as-Judge  │───▶│  Performance   │───▶│ Top-K to     │
│  Fact Filter  │    │ Quality Gate  │    │  Reranker      │    │ Advertiser   │
└───────────────┘    └───────────────┘    └────────────────┘    └──────┬───────┘
                                                                       │
                     ┌─────────────────────────────────────────────────┘
                     ▼
┌───────────────┐    ┌───────────────┐    ┌────────────────┐
│  Advertiser   │───▶│    Deploy     │───▶│  Performance   │─ ─ ─▶ (Feedback
│  Review       │    │               │    │  Monitoring    │        to Reranker
└───────────────┘    └───────────────┘    └────────────────┘        + Generator)
```

The key design choice: use LLMs only for generation with human validation. This gives you the speed of AI without contaminating core auction/ranking models with unvetted content. The speed gain is transformative — 8 weeks to days — but the quality bar is maintained through human review.

The business impact: this pattern scaled to serve 1M+ advertisers and enabled products like Keyword Groups (+2700 bps coverage, +1300 bps adoption) and Targeting Expansion ($100M+ revenue).

**Hard FUQ**: Your pipeline generates great keywords but adoption is flat. What do you do?

**Answer**: This is exactly the problem we faced. Advertisers adopted only the top 30-50 of 200 recommended keywords. The fix wasn't better generation — it was better presentation and abstraction.

Three interventions: (1) Reframe from per-keyword to intent-level — show "Performance Running" as a cluster, not 40 individual keywords. Advertisers reason about intents, not terms. (2) Reduce volume, increase relevance — surface fewer suggestions but each one is more targeted. 50 well-ranked suggestions outperform 200 sorted by alphabetical order. (3) Show expected impact — attach predicted performance data to each suggestion so the advertiser can make an informed decision rather than guessing.

The earned secret: more generation doesn't help if advertisers only adopt the top 30. The constraint is cognitive load and trust, not content quality.

**Hard FUQ**: How do you cold-start this system for a brand-new advertiser with no historical data?

**Answer**: Cold start is the hardest case. Three strategies: (1) Category-level transfer — use adoption and performance signals from similar advertisers in the same product category. A new shoe advertiser benefits from patterns observed across all shoe advertisers. (2) Product-attribute-driven generation — even without history, the product catalog provides rich grounding. Generate from attributes and rely heavily on the human review step. (3) Conservative initial volume — for cold-start advertisers, generate fewer suggestions with higher confidence. Build trust with 10 great keywords before surfacing 50.

---

### Q2: How do you handle brand safety and policy compliance in generated content?

**Principal Answer**: Brand safety in generated ad content is existential — a single policy violation can damage both the advertiser's brand and the platform's reputation. This requires defense in depth, not a single filter.

> [!experience] From my experience at Amazon Ads, we led security testing for GenAI models achieving zero vulnerabilities across 9 categories: brand safety, policy compliance, toxicity, competitor disparagement, medical/health claims, financial claims, age-inappropriate content, deceptive pricing, and trademark misuse [3][4].

**Architecture (layered defense)**:

1. **Input validation**: Verify product data is complete and consistent before generation. Refuse to generate for products with insufficient data — an ounce of prevention.
2. **Prompt-level constraints**: Explicit policy instructions in the system prompt. Negative examples showing what NOT to generate.
3. **Generation-time filtering**: During candidate generation, use constrained decoding or logit bias to suppress prohibited terms.
4. **Post-generation classifier**: Fine-tuned classifier trained on historical policy violations [4][16]. Catches subtle violations that rule-based filters miss (e.g., implied medical claims, misleading superlatives).
5. **LLM-as-judge**: Second model evaluates each candidate for policy compliance, brand alignment, and factual grounding [10]. This catches nuanced violations — "clinically tested" in a cosmetics context.
6. **Human review**: Final gate for high-risk categories (healthcare, financial, children's products).
7. **Continuous monitoring**: Monitor deployed content for policy drift. Performance changes can indicate policy-adjacent issues.

**Principal signal**: The safety architecture must be proportional to the cost of failure. A bad keyword suggestion wastes a few cents of ad spend. A policy violation in ad copy for a pharmaceutical product creates legal liability. The guardrail investment should match the risk profile.

**Hard FUQ**: An LLM generates ad copy that's technically policy-compliant but misleading in context (e.g., "award-winning" for a product that won a made-up award). How do you catch this?

**Answer**: This is the hardest class of violation — factually verifiable but practically misleading. Three approaches: (1) Factual grounding — every claim in the ad must trace to a verified product attribute. "Award-winning" requires a corresponding attribute entry for the specific award. If the attribute doesn't exist, the claim is blocked. (2) Claim classification — distinguish between objective claims (factual, verifiable) and subjective claims (opinion, puffery). Objective claims require evidence; subjective claims are allowed within bounds. (3) Adversarial testing — systematically red-team the generation pipeline with misleading-but-technically-compliant prompts. Build a test suite from these adversarial examples. This is how we achieved zero vulnerabilities — not by hoping the model behaves, but by systematically testing every failure mode.

---

### Q3: How do you know if generated content is "good"? (Offline metrics vs business metrics)

**Principal Answer**: "Good" has three layers, and most teams get stuck on layer one:

**Layer 1 — Linguistic quality** (necessary, not sufficient): Is the content grammatically correct, fluent, and on-brand? Measure with human review pass rate, fluency scoring, and LLM-as-judge. This is the easiest to measure and the least predictive of business impact.

**Layer 2 — Relevance and accuracy** (closer, still not enough): Is the content factually grounded in the product? Is it relevant to the advertiser's target audience? Measure with factual grounding rate, relevance scoring, and diversity metrics. This tells you the content is correct — not that it works.

**Layer 3 — Business impact** (the only metric that matters): Does the generated content improve downstream business metrics? Adoption rate (did the advertiser use it?), CTR (did users click?), CVR (did clicks convert?), RoAS (did the advertiser's return improve?). This is hard to measure but it's the only ground truth.

> [!experience] From my experience at Amazon Ads, the gap between layers 2 and 3 was where most surprises lived. Content that scored well on linguistic quality and factual accuracy sometimes had zero impact on CVR — because the content was correct but generic, failing to differentiate the product from competitors. Conversely, content that our human reviewers rated as merely "adequate" sometimes performed well because it matched real user search patterns.

**The resolution**: Use offline metrics (layers 1-2) as gates — they filter out bad content. Use online metrics (layer 3) as the optimization target — they tell you what's actually working. Never optimize for offline metrics alone; they're necessary conditions, not sufficient ones.

**Hard FUQ**: Your generated keywords have higher CTR than advertiser-written keywords, but lower CVR. Is that good or bad?

**Answer**: That's bad, and it's a common failure mode. Higher CTR with lower CVR means the generated content is attracting clicks that don't convert — essentially wasting advertiser budget. For lower-funnel ads (like Sponsored Products), CVR and RoAS are the primary constraints. I'd rather have slightly lower CTR with maintained or improved CVR.

This usually means the generated content is too broad or too aggressive — it promises more than the landing page delivers. The fix: (1) Ground generation more tightly in product-specific attributes rather than category-level appeals. (2) Include conversion signals in the ranking model, not just click signals. (3) A/B test with RoAS as the primary metric, not CTR.

---

### Q4: The adoption problem — generation quality vs user adoption

**Principal Answer**: This is the single most important insight in ad content generation, and most teams miss it: the constraint isn't generation quality — it's adoption. More keywords don't help if advertisers only adopt the top 30.

> [!experience] From my experience at Amazon Ads, we generated up to 200 keyword recommendations per advertiser. Adoption data showed that advertisers typically adopted only the top 30-50. The rest were ignored — not because they were bad keywords, but because advertisers have limited attention and trust.

**Why this happens**:
1. **Cognitive overload**: 200 suggestions is not a gift, it's a chore. Advertisers don't have time to evaluate each one.
2. **Trust deficit**: Advertisers are cautious about AI-generated suggestions, especially for performance-critical campaigns.
3. **Lack of context**: A bare keyword with no explanation of why it's relevant gives the advertiser no basis for decision-making.
4. **Risk aversion**: Adding a bad keyword costs real money. Advertisers default to conservatism.

**What we did**:
1. **Reframed from keywords to intents**: Instead of 200 individual keywords, present 5-7 intent clusters. "Keyword Groups" became a product that delivered +2700 bps coverage and +1300 bps adoption — because advertisers could reason about intent rather than individual terms.
2. **Reduced volume, increased signal**: Better to show 30 high-confidence suggestions than 200 sorted by the model's internal scoring.
3. **Added expected impact**: Showed predicted incremental impressions and clicks for each suggestion. Advertisers adopted more when they understood the expected business impact.
4. **Graduated trust**: Started with conservative suggestions for new advertisers, expanded as the system earned trust through demonstrated performance.

**Principal signal**: This is a product problem, not a model problem. You solve it by changing what you present and how, not by generating more or better content. The distinction between a Staff Engineer and a Director is recognizing that the bottleneck is human behavior, not model capability.

**Hard FUQ**: How do you measure whether the adoption problem is a quality problem or a UX problem?

**Answer**: Run a controlled experiment. Take the same set of keyword suggestions and present them in two different ways: (A) flat list of 200 keywords, (B) intent-clustered groups of 5-7 with expected impact annotations. If adoption is significantly higher for group B with identical keywords, the problem is UX/presentation, not quality. If adoption is similar, the problem is keyword quality or relevance.

In practice, it's usually both — but presentation improvements have a larger, faster effect. At Amazon Ads, the reframing to intent-level presentation was the single biggest driver of adoption improvement.

---

### Q5: Personalization vs generalization in content generation

**Principal Answer**: The tension is between a one-size-fits-all model that's easy to maintain and a per-advertiser model that's expensive and data-sparse. The right answer depends on advertiser size and available data.

**Personalization spectrum**:

| Approach | Personalization | Data Need | Maintenance |
|----------|----------------|-----------|-------------|
| Global model + category templates | Low | Minimal | Lowest |
| Category-clustered models | Medium | Category-level aggregates | Low-medium |
| Brand-voice conditioning (prompt) | Medium-high | Brand guidelines (text) | Medium |
| Per-advertiser fine-tuning | Highest | Large per-advertiser corpus | Highest |

**What works in practice**: For most advertisers (long tail), category-level conditioning is sufficient — a shoe advertiser gets shoe-specific prompting. For large advertisers with strong brands, inject brand guidelines, tone examples, and approved vocabulary into the prompt. Per-advertiser fine-tuning is only justified for the top 0.1% of advertisers by spend — and even then, the maintenance burden is significant.

> [!experience] From my experience at Amazon Ads, the Targeting Expansion system served 1M+ advertisers [7]. Per-advertiser fine-tuning at that scale is impossible. We used product-attribute-driven generation with category-level conditioning — personalized to the product, not the advertiser. This worked because the product's attributes carry most of the signal for ad relevance.

**Hard FUQ**: A large advertiser (top 50 by spend) says your generated keywords don't match their brand voice. What do you do?

**Answer**: Short-term: add their brand guidelines, approved vocabulary, and a few examples of their existing high-performing keywords to the prompt context. This is prompt-level personalization — fast to implement, no model changes. Medium-term: if prompt conditioning is insufficient, create a brand-voice fine-tuned adapter (LoRA) trained on their approved ad content. This is a per-advertiser investment justified by their spend level. Long-term: offer a self-service brand configuration tool where large advertisers define their voice, prohibited terms, and preferred style — then the system respects these automatically.

The key: don't build per-advertiser infrastructure for a problem that prompt engineering solves for 99% of cases.

---

### Q6: Fine-tuning vs prompting for style/brand consistency

**Principal Answer**: This is a false dichotomy in most real-world applications — the answer is layered: prompt first, fine-tune when prompting hits a ceiling.

**When prompting is sufficient (80% of cases)**:
- Category-level tone adjustment (formal for B2B, conversational for consumer)
- Basic brand constraints (prohibited terms, required disclosures)
- Few-shot style examples (3-5 examples of approved content per brand)
- Locale-specific language preferences (British vs American English, formality levels)

**When fine-tuning is justified (20% of cases)**:
- Large advertisers with strong, distinctive brand voices that few-shot can't capture
- Domain-specific jargon or tone that the base model consistently gets wrong
- When prompt length becomes a cost issue — distilling complex brand rules into model weights saves tokens per query

**When fine-tuning is dangerous**:
- Fine-tuning on a small dataset creates overfitting and mode collapse — the model generates the same patterns
- Fine-tuning for factual knowledge (product attributes) bakes in stale information
- Fine-tuning without careful deduplication creates repetitive outputs

> [!experience] From my experience, we used zero-shot and few-shot learning for i18n expansion to 19+ locales rather than fine-tuning per locale [17][18]. The rationale: multilingual LLMs already have strong language capability. Few-shot examples (10-20 per locale from native speakers) capture cultural nuance without the cost and maintenance burden of per-locale fine-tuning. Fine-tuning was reserved for the top 3-4 locales by revenue where the quality bar was highest.

**Hard FUQ**: You fine-tune on approved ad content but the model starts generating repetitive, "safe" suggestions. How do you fix this?

**Answer**: This is the exploration-exploitation tradeoff. Three interventions: (1) Temperature scheduling — fine-tuned model generates the "safe" pool at low temperature, base model generates the "explore" pool at higher temperature. Present both. (2) Diversity objective — add a diversity penalty during fine-tuning (or at decoding time) that penalizes outputs too similar to the training distribution. (3) Periodic reset — retrain periodically with a mix of recent high-performing content and a fraction of novel content, preventing the model from converging to a single mode.

The test: track the semantic diversity of generated candidates over time. If diversity is declining month-over-month, the fine-tuning is collapsing.

---

### Q7: Feedback loops — connecting generation quality to downstream metrics (CTR, CVR)

**Principal Answer**: Feedback loops from business metrics to generation quality are the highest-leverage long-term investment — and the hardest to get right because of attribution challenges.

**The attribution problem**: A keyword's CTR depends on the keyword itself, the ad creative, the landing page, the bid, the auction competition, the time of year, and the user's intent. Isolating the keyword quality signal from these confounders is genuinely difficult.

**Three levels of feedback loops**:

1. **Adoption signal** (easiest, fastest): Which suggestions did advertisers choose? This is available immediately and doesn't require downstream attribution. Use it to train a ranking model that predicts adoption likelihood.

2. **Performance signal** (harder, delayed): Among adopted suggestions, which ones performed well (high CTR, high CVR)? This requires weeks of performance data and careful confound control. Use it to retrain the ranking model and adjust generation prompts.

3. **Causal signal** (hardest, most valuable): What is the counterfactual impact — what would have happened without the generated content? This requires experimentation.

> [!experience] From my experience at Amazon Ads, we designed a double-randomized experimentation framework for measuring marketplace impact [12][13]. Standard A/B tests (randomize advertisers into treatment/control) miss marketplace effects — if treatment advertisers bid on new keywords, they change auction dynamics for everyone. Double randomization — randomize at both the advertiser level and the marketplace/auction level — isolates the true causal effect [14].

**Practical feedback architecture**:

```
┌───────────────────┐    ┌───────────────────┐    ┌──────────────────────┐
│ Generated Content │───▶│ Adoption Decision │───▶│  Performance Data    │
│                   │    │ (accept/reject)   │    │  (CTR / CVR / RoAS)  │
└───────────────────┘    └────────┬──────────┘    └──────────┬───────────┘
                                  │                          │
                                  ▼                          ▼
                         ┌────────────────┐         ┌────────────────────┐
                         │Adoption Ranker │◀────────│ Attribution Model  │
                         └───────┬────────┘         └────────┬───────────┘
                                 │                           │
                                 ▼                           ▼
                         ┌────────────────┐         ┌────────────────────┐
                         │Improved Ranking│         │ Improved Generation│
                         │                │         │ Prompts            │
                         └────────────────┘         └────────────────────┘
```

**Hard FUQ**: Your feedback loop creates a filter bubble — the system only generates keywords similar to what performed well before. How do you prevent this?

**Answer**: Three mechanisms: (1) Exploration budget — reserve 10-20% of suggestions for novel keywords that the performance model hasn't seen. Measure their adoption and performance separately. (2) Counterfactual evaluation — periodically evaluate unchosen suggestions through impression-based tests (show the ad with the unchosen keyword to a small traffic slice). (3) Novelty bonus — in the ranking model, add a bonus for suggestions that are semantically distant from the advertiser's existing keywords. This ensures the system keeps exploring new intent spaces rather than optimizing within a narrow band.

---

### Q8: Multi-lingual/multi-locale content generation

**Principal Answer**: Locale expansion is one of the highest-ROI applications of LLM-based content generation — and the biggest mistake is treating it as a translation problem.

> [!experience] From my experience at Amazon Ads, we used zero-shot and few-shot learning for i18n expansion to 19+ locales [17][18]. The key insight: never translate, always regenerate. Translating English keywords preserves English search patterns and idioms. Regenerating from product attributes in the target language captures how local users actually search.

**Architecture for multi-locale generation**:

1. **Input**: Locale-independent product attributes (category, price, specs) + locale-specific attributes (local brand name, local regulatory context)
2. **Generation**: Multilingual LLM with locale-specific system prompt. Few-shot examples from native speakers (10-20 per locale) capture cultural nuance, search patterns, and formality norms.
3. **Locale-specific guardrails**: Each locale has different advertising regulations. Germany has different prohibited claims than Japan. The policy classifier must be locale-aware.
4. **Evaluation**: Locale-specific human review for top locales by revenue. LLM-as-judge with locale-aware prompting for long-tail locales.

**Scaling strategy**:

| Locale tier | Volume | Approach | Quality bar |
|-------------|--------|----------|-------------|
| Tier 1 (top 3-4 by revenue) | Highest | Few-shot + locale-specific fine-tuning + native review | Highest |
| Tier 2 (next 5-8 locales) | Medium | Few-shot + LLM-as-judge evaluation | High |
| Tier 3 (long tail) | Lower | Zero-shot + automated quality checks | Acceptable |

**Hard FUQ**: Your system generates Japanese keywords that are grammatically correct but don't match how Japanese users actually search. How do you fix this?

**Answer**: This is the "fluent but unnatural" problem — the LLM generates proper Japanese but not search-pattern Japanese. Users search differently than they speak. Three fixes: (1) Mine actual search query logs for the product category in that locale. Use real search patterns as few-shot examples rather than editorial content. (2) Use search autocomplete data as a grounding signal — what does the search engine suggest when users start typing? (3) Partner with locale-specific teams for the top locales. Automated generation can't fully substitute for cultural understanding in high-revenue markets. The ROI of a native speaker reviewing the top 100 keywords for Japan far exceeds the cost.

---

### Q9: Human-in-the-loop validation design

**Principal Answer**: Human-in-the-loop is not a stopgap — it's a deliberate architectural choice that enables speed without risk. The question isn't "how do we remove the human?" but "how do we design the human review to be efficient, consistent, and trust-building?"

> [!experience] From my experience at Amazon Ads, the key insight was: use LLMs only for GENERATION with human validation. This let us cut cycle time from 8 weeks to 2-3 days while maintaining quality. The LLM handles the expensive creative work (generating candidate keywords and copy). The human handles the cheap but critical judgment work (approving or rejecting suggestions).

**Validation architecture**:

```
Tier 1: Automated (milliseconds)      → Policy filter, factual grounding, format validation
    ↓ (pass)
Tier 2: LLM-as-judge (seconds)        → Quality scoring, relevance assessment, brand alignment
    ↓ (pass)
Tier 3: Advertiser review (hours)     → Approve/reject/edit suggestions for their campaigns
    ↓ (deploy)
Tier 4: Performance validation (days)  → A/B test deployed content against baseline
```

**Design principles for efficient human review**:
1. **Pre-filter aggressively**: Don't show the advertiser content that fails automated checks. Every low-quality suggestion shown erodes trust.
2. **Batch by intent**: Present suggestions grouped by intent cluster, not as a flat list. Advertisers can approve/reject entire clusters.
3. **Show confidence**: Display the system's confidence level for each suggestion. Let the advertiser focus review time on uncertain cases.
4. **Learn from edits**: When advertisers edit suggestions (not just accept/reject), capture the edit as a training signal. Edits reveal exactly where the model falls short.
5. **Progressive trust**: As the system demonstrates accuracy over time, gradually increase the automation level. Start with human review for everything, evolve to human review only for edge cases.

**Hard FUQ**: At 1M+ advertisers, human review for every suggestion is impossible. How do you scale?

**Answer**: The human in the loop is the advertiser, not an internal reviewer. The system generates suggestions; each advertiser reviews their own. This scales naturally with the number of advertisers — each one reviews only their own suggestions.

For internal quality assurance, use statistical sampling — review a random sample of generated content per category/locale. Set quality thresholds: if the sample pass rate drops below 95%, pause generation for that segment and investigate. The system is supervised at the population level even though individual advertisers supervise their own campaigns.

---

### Q10: When NOT to use LLMs for content (when templates suffice)

**Principal Answer**: LLMs are expensive, slow, and non-deterministic. Using them when a template suffices is a costly architectural mistake. The decision framework:

**Use templates when**:
- The output structure is fixed and predictable (e.g., "Shop [Brand] [Product] — [Price] | Free Shipping")
- The input space is well-defined and finite (e.g., seasonal sale copy with predetermined offers)
- Determinism is required (regulatory disclosures, mandatory disclaimers)
- Volume is extremely high and latency budget is tight (millions of ads refreshed hourly)
- The content is boilerplate that doesn't benefit from creativity

**Use LLMs when**:
- The output requires creative variation (novel keyword discovery, long-tail intent coverage)
- The input space is open-ended (new product categories, emerging search patterns)
- Personalization at scale is needed (brand voice adaptation across thousands of advertisers)
- Cross-lingual generation is required (templates don't scale across 19+ locales)
- The task is conceptually hard to template (intent-level keyword generation, persuasive copy)

**The hybrid pattern**: Use templates for the structural shell and LLMs for the creative fill. Example: template defines the ad format (headline, description, call-to-action slots) and constraints (character limits, required elements). LLM generates the content that fills the slots. This gives you structural consistency with creative variation.

> [!experience] From my experience: Budget Recommendations at Amazon Ads used algorithmic/template approaches — the output is a number with supporting context, not creative content. Using an LLM to generate "You should increase your budget to $50" would be absurdly expensive for what a template does better. Keyword generation, on the other hand, benefits enormously from LLMs because the intent space is open-ended and creative.

**Hard FUQ**: Your team proposes using an LLM for every ad content task. How do you push back?

**Answer**: Cost and latency analysis kills this quickly. Calculate: (1) Cost per generation call times number of daily content items. If the answer is "$50K/month to generate content that templates produce for pennies," the LLM is unjustified. (2) Latency: templates return in milliseconds, LLM calls take seconds. For real-time ad serving, this matters. (3) Determinism: regulatory content must be exactly correct every time. LLMs can't guarantee this.

My rule: if you can write a template that produces 90%+ of the value, use the template. Save LLM budget for tasks where creativity, personalization, or cross-lingual generation creates genuine value.

---

### Q11: Measuring marketplace impact of generated content (experimentation)

**Principal Answer**: Measuring the true impact of generated ad content is harder than standard A/B testing because advertising is a marketplace — changes to one advertiser affect all advertisers through auction dynamics.

**Why standard A/B testing fails for ad content**:
- If treatment advertisers add AI-generated keywords, they now compete in new auctions
- This changes auction density, CPCs, and win rates for ALL advertisers — including control
- The treatment effect is contaminated by marketplace spillover (SUTVA violation) [13]
- You measure an attenuated effect because control advertisers are also affected [14]

> [!experience] From my experience at Amazon Ads, we designed a double-randomized experimentation framework to address this [12][13]:

**Double randomization**:
1. **First randomization (advertiser level)**: Randomly assign advertisers to treatment (receive AI-generated suggestions) and control (business as usual)
2. **Second randomization (marketplace level)**: Within the ad auction, create treatment and control auction buckets. Treatment auctions include the new content; control auctions don't.
3. **Cross-comparison**: Compare outcomes across the 2x2 matrix — treatment advertisers in treatment auctions vs control advertisers in control auctions. This isolates the causal effect from marketplace spillover.

**Metrics hierarchy for experiments**:
1. **Primary**: Advertiser revenue (incremental spend and revenue from new content)
2. **Secondary**: CVR and RoAS (must not regress — constraint, not objective)
3. **Tertiary**: Adoption rate, time to campaign activation
4. **Guardrail**: Customer (shopper) experience metrics — click satisfaction, return rates

**Principal signal**: A Director-level answer doesn't just describe A/B testing — it explains why naive experimentation gives wrong answers in marketplace settings and describes the experimental design that fixes it.

**Hard FUQ**: Your experiment shows positive adoption and positive CTR but neutral CVR. Ship or don't ship?

**Answer**: Neutral CVR with positive adoption is a cautious "ship with monitoring." The generated content is attracting new traffic (positive CTR) without degrading conversion quality (neutral CVR). This suggests incremental value. But: monitor CVR closely post-launch. The experiment may not have run long enough to capture long-term CVR effects. Also check advertiser-level heterogeneity — neutral CVR in aggregate can mask positive CVR for some advertisers and negative for others. If there's a segment with CVR regression, investigate before full rollout.

---

### Q12: Content generation for different stages of the funnel

**Principal Answer**: The funnel stage dictates almost everything about the content generation system — the output type, the quality bar, the evaluation metrics, and the guardrails.

**Upper funnel (awareness, brand)**:
- **Content type**: Brand storytelling, broad keywords, lifestyle imagery, video scripts
- **Quality bar**: Creative quality, brand consistency, emotional resonance
- **Evaluation**: Brand lift, recall, sentiment
- **LLM strengths**: Creativity, narrative variation, tone adaptation
- **LLM risks**: Brand drift, tone inconsistency across channels
- **Constraint level**: Moderate — some tolerance for creative experimentation

**Mid funnel (consideration)**:
- **Content type**: Product comparisons, feature highlights, category keywords
- **Quality bar**: Factual accuracy, competitive differentiation
- **Evaluation**: Engagement metrics, consideration set entry
- **LLM strengths**: Product attribute synthesis, competitive positioning
- **LLM risks**: Hallucinated features, competitor disparagement
- **Constraint level**: High — factual claims must be grounded

**Lower funnel (conversion, Sponsored Products)**:
- **Content type**: Specific keywords, product-focused copy, purchase-intent targeting
- **Quality bar**: Conversion performance, RoAS
- **Evaluation**: CVR, RoAS, adoption rate, incremental revenue
- **LLM strengths**: Long-tail keyword discovery, intent-level coverage
- **LLM risks**: Traffic that doesn't convert, wasted advertiser spend
- **Constraint level**: Highest — can't regress CVR or RoAS

> [!experience] From my experience at Amazon Ads, Sponsored Products is lower-funnel [7], which made the constraint profile extremely tight. We couldn't "get creative" with keyword suggestions — every suggestion had to be defensible in terms of conversion probability. This is why the human-in-the-loop validation layer was non-negotiable. Upper-funnel brand campaigns can tolerate more experimentation; lower-funnel conversion campaigns demand precision.

**Hard FUQ**: You're asked to build one content generation system that serves all funnel stages. Is that a good idea?

**Answer**: No. A single system with a single quality bar will either be too conservative for upper-funnel (killing creativity) or too permissive for lower-funnel (killing conversions). The right architecture: shared infrastructure (LLM serving, policy guardrails, evaluation framework) with funnel-specific pipelines (different prompts, different ranking models, different quality thresholds, different evaluation metrics).

Shared: product attribute extraction, policy compliance checking, experiment framework, observability.
Separate: generation strategy (creative vs precise), ranking model (engagement vs conversion), quality bar (moderate vs strict), human review level (sampling vs full).

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Distinguished Engineer Depth Probes

<details>
<summary><strong>DE Probe 1: Decoding Strategies — Controlling generation quality at the token level</strong></summary>

**Question**: Beyond temperature and top-p, what decoding strategies exist for controlling content generation quality? When would you use constrained/grammar-guided decoding?

**What they're testing**: Token-level control of generation — understanding the decoding design space beyond basic sampling.

**Answer**:
The decoding decision tree for ad content generation:

**Sampling strategies**:
- **Greedy** (temperature=0): Deterministic. Best for factual extraction. Worst for creative diversity. Use for: extracting product attributes, structured output.
- **Top-k**: Sample from the k highest-probability tokens. Problem: k is content-agnostic — a flat distribution needs large k, a peaked distribution is fine with small k.
- **Nucleus/Top-p**: Sample from the smallest set whose cumulative probability ≥ p. Adapts to distribution shape — wide when uncertain, narrow when confident. Standard default (p=0.9-0.95).
- **Typical sampling** (Meister et al., 2022): Sample tokens whose information content (negative log prob) is close to the expected information content. Produces more "human-like" text by avoiding both too-predictable and too-surprising tokens. Better than top-p for creative copy.
- **Contrastive decoding** (Li et al., 2022): Score = log P_large(token) - log P_small(token). Amplifies tokens the large model "knows" that the small model doesn't — surfaces sophisticated word choices while avoiding generic patterns. Useful for: differentiating ad copy that avoids cliches.

**Constrained generation** (critical for ad content):

Ad content has hard format requirements: character limits, required fields, prohibited patterns, JSON structure. Strategies:

1. **Grammar-guided decoding (GCD)**: Define a formal grammar (CFG/regex) that the output must satisfy. At each token, mask logits of tokens that would violate the grammar. Guarantees structural validity. Libraries: Outlines, Guidance, LMQL.
   ```
   # Example: keyword must be 2-5 words, no prohibited terms
   grammar = r"[a-z ]{5,40}"  # simplified
   # Decoder masks tokens that would exit the grammar state
   ```

2. **JSON-mode / structured output**: Constrain output to valid JSON matching a schema. OpenAI's JSON mode, Anthropic's tool use, or local grammar constraints. Essential for: generating structured keyword recommendations with metadata (intent cluster, confidence score, expected CTR).

3. **Logit processors**: Custom functions applied to logits before sampling. Examples:
   - Ban specific token sequences (competitor brand names, prohibited claims)
   - Boost tokens from an approved vocabulary
   - Enforce length constraints by increasing EOS probability as length approaches limit

**For ad content specifically**: Layer these — nucleus sampling for creative diversity + logit processor for prohibited terms + length constraint for format compliance. This gives you creative output that's guaranteed format-compliant and policy-safe at the decoding level, before any post-hoc filtering.

> [!experience] At Amazon Ads, we used constrained generation to guarantee that keyword suggestions were within character limits and didn't contain prohibited terms — catching violations at generation time rather than filtering post-hoc (which wastes compute generating content you'll discard).

**Follow-up**: What's the latency cost of grammar-guided decoding?

**Answer**: Per-token overhead is minimal (grammar state update + logit masking is O(vocabulary_size) which is negligible compared to the transformer forward pass). The real cost: grammar constraints can force the model into low-probability regions, requiring more tokens to express the same content (the model "works around" constraints). Typically 10-20% more tokens generated. For short-form content (ad copy, keywords), this is negligible. For long-form, it accumulates.

</details>

<details>
<summary><strong>DE Probe 2: RLHF/DPO — Training content generators from business signals</strong></summary>

**Question**: You have adoption data (which keywords advertisers chose) and performance data (CTR/CVR). How do you use these signals to train the generation model itself — not just a ranker?

**What they're testing**: Understanding of alignment techniques for closing the feedback loop into the model.

**Answer**:
Three approaches, ordered by complexity:

**1. Rejection Sampling + SFT (Simplest)**:
- Generate N candidates per product
- Filter to only those adopted AND high-performing (CTR > threshold)
- Fine-tune the base model on these (positive examples only)
- Pro: Simple. Con: Doesn't teach the model what NOT to generate.

**2. DPO (Direct Preference Optimization)**:
- Construct preference pairs: (chosen=adopted+high-CTR, rejected=not-adopted OR low-CTR)
- Train with DPO loss: `L = -log σ(β * (log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))`
- Where y_w is the preferred output, y_l is dispreferred, π_ref is the reference (base) model
- Pro: No reward model needed. Stable training. Con: Requires high-quality preference pairs — noisy pairs degrade quality.
- **Key decision**: What constitutes a valid preference pair? Adopted vs not-adopted is noisy (adoption depends on position, presentation, advertiser mood). Better: high-CTR vs low-CTR among adopted keywords — this isolates quality signal from presentation effects.

**3. RLHF with Reward Model**:
- Train a reward model: input=(product attributes + generated keyword), output=predicted performance score
- Train the generator to maximize reward via PPO
- Pro: Most flexible — reward can encode complex multi-objective preferences. Con: Reward hacking (model finds degenerate outputs that score high), training instability, infrastructure complexity.

**4. RLAIF (AI Feedback)**:
- Use a strong LLM to judge generated content quality (relevance, specificity, brand-safety)
- Use those judgments as the reward signal
- Pro: Scales without human annotation. Con: Inherits judge LLM biases; may not correlate with actual business performance.

**Practical recommendation for ad content**:
Start with Rejection Sampling + SFT (proven, simple). Graduate to DPO when you have 10K+ clean preference pairs. Reserve full RLHF for when you need multi-objective optimization (balance CTR, CVR, diversity, brand-safety simultaneously) and have the infra investment justified by scale.

> [!experience] At Amazon Ads, we used the simpler approach: adoption signals trained a ranking model (not the generator). The generator was improved through prompt engineering and few-shot updates. Full RLHF training of the generator was considered but the ROI wasn't clear — ranking improvements yielded 80% of the value at 20% of the complexity.

**Follow-up**: How do you prevent reward hacking — the model generating degenerate high-scoring outputs?

**Answer**: Three defenses: (1) KL penalty — DPO/PPO include a divergence penalty from the reference model, preventing the model from straying too far from natural generation. (2) Multi-objective reward — a single CTR reward gets hacked; a combined reward (CTR + CVR + diversity + fluency) is harder to exploit because degenerate outputs rarely score high on all dimensions. (3) Regular human evaluation — periodically score model outputs against the reference model's outputs. If model outputs become repetitive, formulaic, or "optimized" in unnatural ways, the reward signal is being gamed.

</details>

<details>
<summary><strong>DE Probe 3: Contextual Bandits for Explore/Exploit in Content Recommendations</strong></summary>

**Question**: How would you formalize the exploration-exploitation tradeoff in keyword recommendation using bandit algorithms?

**What they're testing**: Formal ML foundations — can you express the intuitive "show some novel suggestions" as a principled optimization problem?

**Answer**:
**Problem formulation**: At each time step t, for advertiser context x_t (product category, spend level, historical adoption):
- Action a_t ∈ {suggest keyword k1, k2, ..., kN}
- Reward r_t = adoption signal (0/1) or downstream performance (CTR)
- Goal: maximize cumulative reward while learning which keywords work for which contexts

**Bandit approaches**:

**1. Thompson Sampling (Bayesian)**:
- Maintain a posterior distribution over reward for each keyword-context pair
- Sample from each posterior; recommend keyword with highest sample
- Natural exploration: uncertain keywords get sampled above their mean sometimes
- Pro: Principled uncertainty quantification. Con: Computational cost of maintaining posteriors at scale.

```python
# Simplified Thompson Sampling for keyword recommendation
for keyword in candidates:
    # Beta distribution for adoption probability
    alpha = adopted_count[keyword] + 1
    beta = shown_count[keyword] - adopted_count[keyword] + 1
    sampled_reward[keyword] = np.random.beta(alpha, beta)
recommend top-K by sampled_reward
```

**2. LinUCB (Contextual)**:
- Model reward as linear function of context features: E[r|x,a] = x^T θ_a
- UCB score: x^T θ_a + α * sqrt(x^T A_a^{-1} x)
- Second term = uncertainty bonus — recommends keywords where we're uncertain about performance in this context
- Pro: Contextual — learns that "running shoes" keywords work for athletic product advertisers. Con: Linear assumption may be too restrictive.

**3. Neural Bandits (for complex contexts)**:
- Replace linear model with neural network for reward prediction
- Exploration via: dropout-based uncertainty, ensemble disagreement, or explicit exploration bonus
- Pro: Handles complex advertiser contexts. Con: Calibration of uncertainty is harder with neural networks.

**Practical architecture for ad content**:
```
Candidate Generation (LLM)
    → Scoring Model (predicted adoption + predicted performance)
    → Bandit Layer (adds exploration bonus based on uncertainty)
    → Final Ranking (top-K to advertiser)
```

The bandit layer doesn't replace the ranker — it adjusts scores based on how much we've learned about each keyword-context pair. Keywords we've shown many times and know perform well → exploit. Keywords we haven't tested in this context → explore.

**Budget allocation**: Reserve 10-20% of impression slots for exploration. Higher for new product categories (high uncertainty), lower for established categories (low uncertainty). Decay exploration as confidence grows.

> [!experience] At Amazon Ads, the targeting expansion system faced exactly this problem: we could recommend "safe" keywords with known performance, or "stretch" keywords with higher potential but unknown adoption. Our phased approach (head queries first, expand after ROI proven) was an informal bandit strategy — we could have formalized it with Thompson Sampling for more efficient exploration.

**Follow-up**: At 1M+ advertisers with 200 keywords each, how do you scale bandit updates?

**Answer**: You can't maintain per-keyword-per-advertiser posteriors at that scale (200M state entries). Solutions: (1) Cluster advertisers by context features, maintain bandits at the cluster level. (2) Hierarchical bandits — global prior shared across all advertisers, per-cluster adaptation, per-advertiser only for high-volume advertisers. (3) Batch Thompson Sampling — update posteriors in batch (daily) rather than per-impression. This loses some optimality but scales to billions of impressions.

</details>

<details>
<summary><strong>DE Probe 4: Attribution and Causal Inference — Double randomization mechanics</strong></summary>

**Question**: Walk me through the mechanics of double-randomized experimentation. Why does standard A/B testing fail for marketplace interventions?

**What they're testing**: Causal inference depth — understanding interference, SUTVA violations, and experimental design.

**Answer**:
**Why standard A/B fails for marketplace interventions**:

Standard A/B: Randomly assign advertisers to treatment (get AI-generated keywords) vs control (don't). Measure adoption + performance difference.

**The SUTVA violation** (Stable Unit Treatment Value Assumption): A/B testing assumes one user's treatment doesn't affect another user's outcome. In a marketplace, this is FALSE:
- Treatment advertisers bid on new AI-generated keywords → more competition in those auctions
- More competition → higher CPCs for ALL advertisers (including control)
- Control advertisers' performance degrades NOT because of their own treatment status, but because treatment changed the marketplace
- Result: treatment effect is UNDERSTATED (treatment looks less beneficial because control got worse)

**Double randomization design**:

Layer 1: Randomize **advertisers** into treatment/control (standard)
Layer 2: Randomize **marketplace contexts** (e.g., traffic slices, query segments, time periods) into isolated pools

```
                    Marketplace Pool A          Marketplace Pool B
Treatment Ads    [Treatment in isolated pool]  [Treatment in isolated pool]
Control Ads      [Control in isolated pool]    [Control in isolated pool]
```

By isolating marketplace contexts, treatment advertisers in Pool A don't affect control advertisers in Pool A — they compete in different auction sub-markets. The treatment effect is measured within-pool, and marketplace interference is bounded.

**Practical implementation at Amazon Ads scale**:
- Auction-level randomization: Assign query-impression slots to experimental pools
- Ensure pool balance: same traffic volume, query distribution, and advertiser mix per pool
- Duration: Run for 2-4 weeks to capture advertiser learning and seasonal effects
- Primary metric: Incremental RoAS (treatment - control, controlling for marketplace effects)
- Guardrail metrics: Auction health (CPM, fill rate), advertiser satisfaction (budget utilization), shopper experience (dwell time)

**Statistical considerations**:
- Cluster-robust standard errors (advertisers are clusters; impressions within-advertiser are correlated)
- Multiple testing correction (testing many metrics simultaneously)
- Power analysis accounting for marketplace-level variance (much higher than user-level)
- Interference detection: compare treatment effects across different pool sizes to test for residual interference

> [!experience] At Amazon Ads, we built the first double-randomized experimentation framework for this exact reason — standard A/B tests for advertiser recommendations consistently understated impact because marketplace interference diluted the signal. The framework became the org-wide standard for measuring marketplace-level impact.

**Follow-up**: What if your marketplace can't be cleanly partitioned into non-interfering pools?

**Answer**: In practice, perfect isolation is impossible (advertisers target overlapping queries). Three mitigations: (1) Increase pool granularity — smaller pools at the query-slot level rather than broad traffic splits. More pools → less interference per pool, but less power per pool. (2) Interference-aware estimation — model the spillover effects explicitly using exposure mapping: estimate what fraction of control's outcomes are affected by treatment's marketplace changes. Subtract estimated spillover. (3) Synthetic control methods — instead of randomized control, construct a synthetic control from pre-treatment time series. No marketplace interference because the control exists in the past, not the present. Trade randomization for temporal assumptions.

</details>

<details>
<summary><strong>DE Probe 5: Structured Generation for Ad Formats</strong></summary>

**Question**: Ad content has strict format requirements — character limits, required fields, prohibited patterns. How do you guarantee the model's output conforms to a schema without just filtering post-hoc?

**What they're testing**: Production-level generation control — guaranteed-valid outputs vs hope-and-filter.

**Answer**:
**The problem with filter-only**: If 30% of generated candidates fail format validation, you've wasted 30% of generation compute. At scale (1M+ advertisers × 50 candidates each), that's millions of wasted tokens. Worse: filtering biases toward shorter, simpler outputs that are more likely to be valid — reducing creative diversity.

**Guaranteed-valid generation approaches**:

**1. Schema-constrained decoding**:
Define the output schema as a finite state machine. At each token, compute the set of valid next tokens given the current state. Mask all other logits to -inf.

```python
# Schema: {"keyword": str(max=40), "intent": enum("brand","generic","competitor"), "confidence": float}
# At generation position for "intent" field:
valid_tokens = tokenizer.encode(["brand", "generic", "competitor"])
logits[~valid_tokens] = -inf
```

Libraries: Outlines (Python), Guidance (Microsoft), LMQL, Instructor.

**2. Two-pass generation**:
- Pass 1: Generate freely (high creativity, may violate format)
- Pass 2: Constrained rewrite — take the creative output and reformat to comply with schema
- Pro: Preserves creative diversity from Pass 1. Con: 2x generation cost.

**3. Template-filling with unconstrained generation**:
- Define template: `"[KEYWORD] | Intent: [INTENT] | Confidence: [SCORE]"`
- Generate each field independently with field-specific constraints
- Pro: Simplest. Con: Loses inter-field coherence (keyword should match its intent label).

**4. Tool-use / function-calling**:
- Frame generation as a tool call: model "calls" `create_keyword(text=..., intent=..., confidence=...)`
- Model architectures (GPT-4, Claude) are trained to produce valid tool-call JSON
- Pro: Native model capability, no external library needed. Con: Depends on model's tool-use training quality.

**For production ad content at Amazon Ads scale**:
- Keywords: Schema-constrained (short, simple structure, guaranteed valid)
- Ad copy: Two-pass (need creative diversity, then truncate/reformat to character limits)
- Structured recommendations (JSON with metadata): Function-calling / Instructor

**Character limit enforcement** (common interview follow-up):
- Naive: Generate, then truncate. Problem: truncated text may be incoherent.
- Better: Logit bias — as generated length approaches limit, progressively increase EOS token probability. Soft encouragement to wrap up naturally.
- Best: Grammar constraint with max-length rule. Guarantees the model stops before violating the limit.

**Follow-up**: The model consistently generates keywords at exactly the character limit (gaming the constraint). How do you fix this?

**Answer**: The model learned that longer = higher reward (longer keywords have more semantic content → higher predicted relevance). Two fixes: (1) Length normalization in the ranking model — don't reward length. Score per-character or per-word quality, not total quality. (2) Length diversity objective — penalize candidates whose lengths cluster around the limit. Reward a natural distribution of lengths. (3) Ablation: remove length from any features used in ranking/adoption prediction. If length is a confounder, the model exploits it.

</details>

<details>
<summary><strong>DE Probe 6: Embedding-Based Diversity Measurement</strong></summary>

**Question**: How do you quantify the diversity of generated content candidates? What metric, what threshold, and how do you trade off diversity against relevance?

**What they're testing**: Formal definition of diversity and its operationalization in a production ranking system.

**Answer**:
**Diversity metrics**:

**1. Intra-List Diversity (ILD)**:
```
ILD = (2 / K(K-1)) * Σ_i Σ_{j>i} dist(e_i, e_j)
```
Where e_i are embeddings of the K recommended items. ILD ∈ [0, 1] for cosine distance. Higher = more diverse.

**2. Maximal Marginal Relevance (MMR)**:
```
MMR_score(d) = λ * Relevance(q, d) - (1-λ) * max_{d' ∈ S} Similarity(d, d')
```
Iteratively select candidates that are relevant to the query AND dissimilar to already-selected candidates. λ controls the relevance-diversity tradeoff (typically λ=0.7 for relevance-heavy, 0.5 for balanced).

**3. Coverage**:
- Define semantic categories (intent clusters for keywords)
- Coverage = fraction of categories represented in top-K
- A perfectly diverse set of 5 keywords covers 5 different intent clusters

**4. Determinantal Point Process (DPP)**:
- Probabilistic model that naturally balances quality and diversity
- P(S) ∝ det(L_S) where L is a kernel matrix combining relevance and diversity
- Exact inference is O(K³) — feasible for small sets (5-20 candidates)
- Elegant but computationally expensive for large candidate pools

**Production implementation** (what I'd actually build):

```python
def diverse_top_k(candidates, query_embedding, k=5, lambda_=0.7):
    """MMR-based diverse selection"""
    selected = []
    remaining = list(candidates)
    
    for _ in range(k):
        scores = []
        for c in remaining:
            relevance = cosine_sim(query_embedding, c.embedding)
            max_sim = max(cosine_sim(c.embedding, s.embedding) for s in selected) if selected else 0
            mmr = lambda_ * relevance - (1 - lambda_) * max_sim
            scores.append((c, mmr))
        best = max(scores, key=lambda x: x[1])
        selected.append(best[0])
        remaining.remove(best[0])
    
    return selected
```

**Threshold setting**:
- Measure baseline ILD of human-curated keyword sets (the "natural" diversity level)
- Set ILD target to match or slightly exceed human baseline
- Monitor: if ILD drops below threshold → generation is collapsing (mode collapse in fine-tuning, or ranker over-optimizing for one intent cluster)
- Alert: ILD declining month-over-month = systematic diversity problem

> [!experience] At Amazon Ads, we observed that purely relevance-ranked keyword suggestions clustered around 2-3 obvious intents (e.g., for running shoes: "running shoes", "athletic footwear", "jogging shoes" — all the same intent). Intent-level reframing (+2700 bps coverage) was essentially an MMR-like intervention: we explicitly required the output to cover different intent clusters rather than ranking by relevance alone.

**Follow-up**: How do you handle the tension when the most diverse set is less likely to be adopted (advertisers prefer familiar, safe keywords)?

**Answer**: Present diverse candidates in separate "intent groups" rather than a single ranked list. The advertiser can adopt an entire intent group (high adoption per group) while the system ensures multiple groups are shown (diversity at the group level). This is the Keyword Groups product insight: diversity at the intent level, coherence within each group. Adoption is measured per-group, not per-keyword — this aligns the diversity objective with the adoption metric.

</details>

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use |
|---------|---------------|-------------|
| **Intent-Level Abstraction** | Adoption ceiling from cognitive overload | When per-item suggestions overwhelm advertisers; enables cluster-level reasoning |
| **Critic/Reranker Pipeline** | Generic or policy-violating output passing through | When baseline filter misses subtle quality issues; adds quality gate between generation and presentation |
| **Constitutional AI for Ads** [3] | Policy alignment without human labeling at scale | When you need scalable policy compliance checking that adapts to nuanced rules |
| **Double-Randomized Experimentation** [12][13] | Marketplace spillover in A/B tests | When generated content changes auction dynamics; standard A/B gives wrong answers |
| **Zero-Shot/Few-Shot i18n** | Expensive per-locale model maintenance | When expanding to many locales; regenerate from attributes rather than translate |
| **Feedback Loop with Exploration** | Model convergence to safe/generic output | When fine-tuning on adoption data creates a filter bubble |
| **Hybrid Template + LLM** | Over-using LLMs for structured content | When parts of the content are templatable and only creative elements need generation |
| **Progressive Trust Architecture** | Advertiser resistance to AI-generated content | When adoption is gated by trust; start conservative, expand automation as accuracy is demonstrated |

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Cost Model

### Per-Query Cost Breakdown (2026 pricing, approximate)

| Component | Cost/Query | Assumptions | Optimization Lever |
|-----------|-----------|-------------|-------------------|
| Product attribute extraction | ~$0 | Pre-computed in catalog pipeline | Batch during ingestion |
| LLM generation (50 candidates) | $0.008 | ~800 input tokens (attributes + few-shot) + 2000 output tokens (50 keywords), Haiku | Reduce candidate count; shorter prompts |
| LLM generation (10 ad copy variants) | $0.012 | ~1000 input + 3000 output tokens, Sonnet for quality | Route simple products to Haiku |
| Policy/quality filter (LLM-as-judge) | $0.004 | 50 candidates × 100 tokens each scored, Haiku | Batch scoring; only score top-K after initial filter |
| Reranker (predicted CTR/CVR) | $0.001 | Lightweight ML model, not LLM | Pre-computed features |
| **Total (keyword generation)** | **~$0.013** | 50 candidates, filter + rank | |
| **Total (ad copy generation)** | **~$0.020** | 10 variants, quality scoring | |

### Monthly Cost at Scale

| Scale | Advertisers Served/Day | Monthly Cost | Cost/Advertiser/Month | Notes |
|-------|----------------------|-------------|----------------------|-------|
| Pilot (10K advertisers) | 2,000 | ~$800 | $0.08 | Batch generation, nightly refresh |
| Growth (200K advertisers) | 50,000 | ~$20,000 | $0.10 | + real-time for new campaigns |
| Scale (1M+ advertisers) | 300,000 | ~$90,000 | $0.09 | Aggressive caching of stable products, model routing |

> [!experience] At Amazon Ads, the key insight was that cost-per-advertiser-served matters less than cost-per-adopted-suggestion. If you generate 200 keywords at $0.013 but only 30 get adopted, the effective cost per useful output is $0.087. Generating fewer, higher-quality candidates (50 instead of 200) at the same cost yields better ROI because the adoption rate per candidate is higher.

### Cost Optimization Priority Stack
1. **Reduce candidate count** (4x impact): Generate 50 well-ranked candidates, not 200. Adoption is capped at 30-50 anyway.
2. **Model routing** (2-3x): Simple product categories (basic apparel, generic goods) → Haiku. Complex categories (electronics, luxury, regulated) → Sonnet.
3. **Caching stable products** (1.5x): Products whose attributes haven't changed don't need regeneration. Cache until catalog update.
4. **Batch generation** (1.2x): Generate keywords nightly for existing campaigns. Real-time only for new campaign creation.
5. **Shared few-shot libraries** (1.1x): Category-level few-shot examples reused across advertisers, not generated per-request.

### Build vs Buy Analysis

| Component | Managed/API | Self-Hosted | Decision Criteria |
|-----------|-------------|-------------|-------------------|
| LLM Generation | Claude/GPT API (quality, zero infra) | vLLM + Llama (cost at scale, latency control) | API for <100K generations/day; self-hosted above + if custom fine-tuning needed |
| Policy classifier | Fine-tuned API model | Custom classifier on SageMaker | Self-hosted — policy rules are proprietary and need frequent updates |
| Reranker (CTR/CVR) | N/A — must be custom | Custom model on internal data | Always self-hosted — requires proprietary performance data |
| Quality scorer | LLM-as-judge via API | Custom fine-tuned scorer | API initially; migrate to custom as labeled data grows |
| A/B testing framework | Internal experimentation platform | Build on top of existing ads infra | Build — ads already has experimentation infra; extend it |

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Observability & Production Debugging

### Request-Level Traces (log per generation job)

| Field | Why | Used For |
|-------|-----|----------|
| `advertiser_id` + `product_ids` | Attribution, personalization analysis | Per-advertiser quality tracking |
| `input_attributes` (product data sent to LLM) | Verify grounding — was the input complete? | Hallucination root-cause |
| `generated_candidates[]` | Full output audit trail | Quality regression analysis |
| `policy_filter_results` (pass/fail per candidate) | Policy compliance tracking | Filter effectiveness |
| `quality_scores[]` (per candidate) | Track score distribution over time | Drift detection |
| `final_ranked_output[]` (what advertiser saw) | Adoption analysis | Ranking effectiveness |
| `adoption_signal` (which were selected) | Ground truth for ranking model | Feedback loop |
| `model_id` + `prompt_version` | Track which model/prompt produced what | A/B analysis, regression tracking |
| `generation_latency` | Performance monitoring | SLA compliance |
| `locale` + `category` | Slice analysis | Per-locale/category quality monitoring |

### Monitoring Dashboard (key panels)

| Panel | Metric | Alert Threshold | Escalation |
|-------|--------|----------------|------------|
| Policy violation rate | % candidates flagged by policy filter | >0.5% (was <0.1%) | → Immediate: freeze deployment, investigate prompt/model change |
| Adoption rate (7-day rolling) | % suggested keywords adopted by advertisers | <15% (was 22%) | → Product + ML review: is it quality or UX? |
| Factual grounding rate | % of claims traceable to product attributes | <95% (was 99%) | → ML on-call: check attribute extraction pipeline |
| Generation diversity (ILD) | Intra-list diversity of candidates | <0.5 (was 0.7) | → Model drift: check for mode collapse in fine-tuned model |
| CVR impact (treatment vs control) | Conversion rate for generated vs manual keywords | Negative delta >0.5% | → P0: generated content is hurting advertiser performance |
| Latency p95 (real-time path) | Generation time for new-campaign flow | >5s | → Infra: check LLM queue depth, batch size |

### Debugging Walkthrough

**Scenario**: Adoption rate dropped 30% week-over-week for electronics category advertisers.

**Step 1 — Scope the problem**: Check adoption by category. Electronics dropped from 25% → 17%. Other categories stable. This is category-specific, not systemic.

**Step 2 — Check generation quality**: Pull generated candidates for electronics advertisers this week vs last week. Run quality scorer on both. Finding: quality scores are similar (no degradation).

**Step 3 — Check what changed**: Diff the prompt template and model version. Finding: A new few-shot example was added to the electronics category prompt on Monday (the day adoption started dropping).

**Step 4 — Inspect the new example**: The new few-shot example is for a specific electronics sub-category (headphones) and it's biasing generation toward audio-related keywords even for non-audio products (laptops, cameras).

**Step 5 — Root cause**: Category-level few-shot contamination. A sub-category-specific example was added at the category level, biasing all electronics generation toward that sub-category's patterns.

**Step 6 — Fix**: (a) Immediate: roll back to previous prompt version. (b) Medium-term: sub-category-specific few-shot pools, not category-level. (c) Long-term: automated few-shot selection based on product similarity rather than manually curated category lists.

> [!experience] At Amazon Ads, prompt versioning and the ability to rapidly roll back was critical. A seemingly minor change (adding one example) caused measurable business impact. This is why we log `prompt_version` on every generation and can compare adoption/performance across prompt versions with statistical significance.

### Versioning & Rollback

| Component | How to Version | How to Rollback | A/B Test Strategy |
|-----------|---------------|-----------------|-------------------|
| Prompt template | Version ID in config; log per request | Config rollback (instant) | Route 10% of advertisers to new prompt, measure adoption + quality |
| Few-shot examples | Versioned library per category | Swap to previous library version | Shadow score: generate with both, compare quality scores |
| Fine-tuned model | Model version tag in model registry | Route traffic to previous model version | Gradual rollout: 5% → 25% → 100% with adoption gates |
| Policy classifier | Model version + rule version | Swap to previous version; may need re-score | Run both in parallel; alert if disagreement rate >2% |
| Ranking model (CTR/CVR predictor) | Model version in prediction service | Swap to previous version | Interleaving test: alternate old/new rankings for same advertiser |

[[#GenAI Content Generation System Design — Interview Prep|↑ Top]]

---

## Data Flywheel & Continuous Improvement

### Feedback Signals (ranked by value)

| Signal | Availability | Latency | What It Tells You | Action |
|--------|-------------|---------|-------------------|--------|
| Advertiser adoption (selected/rejected) | High volume | Immediate | Whether suggestions meet advertiser's bar | Train adoption ranker; analyze rejection patterns |
| Downstream CTR/CVR of adopted keywords | High volume | 1-4 weeks | Whether adopted content actually performs | Feed into performance reranker; flag low-performers |
| Advertiser edits before deploying | Medium volume | Immediate | WHERE the suggestion was close but not right | Gold signal for fine-tuning — the edit IS the correction |
| Advertiser explicit feedback ("not relevant") | Low volume | Immediate | Specific quality failure with context | High-priority debugging signal; add to regression set |
| Keyword pause/removal after deployment | Medium volume | Days-weeks | Content that performed poorly enough to remove | Negative signal for ranking model |
| Support tickets about suggestions | Very low volume | Days | Worst failures — confused/frustrated advertiser | P0 investigation; systemic issue |

### Active Learning: What to send for human evaluation

Budget: Evaluate 3% of generated candidate sets (at scale: ~10K sets/month). Select:

1. **New product categories** (no historical adoption data): Can't validate with signals alone
2. **Low adoption score + high quality score disagreement**: The quality model says it's good but advertisers don't adopt — why?
3. **First generation for new advertisers**: Cold-start quality validation
4. **Category-level regression detections**: When a category's adoption drops, evaluate a sample from that category
5. **Cross-locale samples**: Ensure quality in non-English locales where automated evaluation is weaker
6. **Random 10% of budget**: Unbiased quality measurement

### Improvement Prioritization Framework

| Failure Mode | Business Cost | Frequency | Fix Difficulty | Priority |
|---|---|---|---|---|
| Policy violation in deployed content | Very High (legal, brand damage, trust) | <0.1% | Medium (better classifier + human review) | **P0** |
| Low adoption (suggestions ignored) | High (no value delivered, wasted compute) | 70-80% of suggestions | Hard (product + ML + UX problem) | **P0** |
| Hallucinated product features | High (advertiser trust, potential legal) | 1-2% | Medium (better grounding, attribute verification) | **P1** |
| Generic/undifferentiated suggestions | Medium (low value, advertiser apathy) | 20-30% | Medium (better personalization, diversity) | **P1** |
| Locale quality issues | Medium (poor experience in non-US markets) | 5-15% in tail locales | Hard (need native speakers, cultural context) | **P2** |
| Slow generation (>5s for real-time path) | Low (UX friction) | 10% of requests | Low (routing, caching) | **P2** |

### System Versioning — Continuous Improvement Cadence

| Frequency | What Gets Updated | Validation Gate |
|-----------|-------------------|-----------------|
| Daily | Ranking model retrained on adoption signals | Adoption rate ≥ previous version on holdout |
| Weekly | Prompt refinements based on failure analysis | Quality score + adoption rate on shadow traffic |
| Monthly | Few-shot library refresh (new high-performing examples) | Human review pass rate ≥ 90% |
| Quarterly | Fine-tuned model retrain (if applicable) | Full regression suite + 2-week A/B test |
| As needed | Policy classifier update (new rules, new categories) | Zero violation rate