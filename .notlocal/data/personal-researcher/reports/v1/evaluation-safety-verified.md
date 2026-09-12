# Evaluation + Safety System Design — Interview Prep

> **Navigation**: [[#Design Flow Framework]] | [[#Full System Design Walkthrough (Principal/Director Level, ~4 min)]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]




## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | What's being evaluated (FM, agent, pipeline)? Release bar? Stakeholders? | Is this a release gate, a monitoring system, or a research benchmark? |
| 2. Identify constraints | Speed vs thoroughness, SME availability, automation limitations, organizational trust | How fast must evaluation run? Who trusts the results? What's the cost of a bad release? |
| 3. Propose baseline | Public benchmarks + manual SME review | Establish a starting point that's credible but doesn't scale |
| 4. Identify gaps | Benchmarks miss domain-specific behavior, manual doesn't scale, no trajectory-level eval for agents, no calibration | Where the baseline fails silently |
| 5. Introduce improvements | Layered evaluation stack, LLM-as-judge with calibration, rubric design, segment-aware thresholds, trajectory decomposition | Each layer catches a different class of failure |
| 6. Add evaluation of the evaluator | Meta-evaluation: evaluating the evaluator itself, drift detection, calibration and agreement measurement between automated judges and human experts, adversarial testing of the eval system | Who watches the watchmen? |
| 7. Discuss scaling tradeoffs | Cost of evaluation vs cost of bad releases, human-in-loop balance, automation vs trust, speed vs rigor | The Director's job: right evaluation rigor for each release type |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]


## Interview Q&A Bank

### Q1: Why is LLM evaluation fundamentally harder than traditional ML evaluation?

**Principal Answer**: Traditional ML evaluation has three luxuries that LLM evaluation lacks:

1. **Ground truth labels**: In classification, you know the right answer. In LLM generation, "correct" is subjective, multi-dimensional, and context-dependent. A factual answer can be correct but unhelpful. A creative answer can be engaging but inaccurate.

2. **Fixed output space**: A classifier produces one of K labels. An LLM produces free-form text — infinite output space. You can't enumerate "all correct answers" and check membership.

3. **IID assumptions**: Traditional ML assumes test data is drawn from the same distribution as training data. LLMs face distribution shift constantly — new queries, new domains, new adversarial inputs that weren't in the training set.

**What this means for evaluation architecture**: You can't have a single metric. You need decomposed evaluation (accuracy separately from safety separately from usefulness), multi-method evaluation (automated + LLM-judge + human), and continuous evaluation (not just at release, because distribution shifts in production).

> [!experience] At Amazon Ads, this meant our evaluation framework had to span numerical reasoning, product knowledge, policy compliance, and planning — in one integrated stack. A model that's great at reasoning but violates policy is more dangerous than one that's mediocre at everything, because confident-sounding wrong answers are harder to catch.

**Hard FUQ**: If you can only pick ONE metric to gate releases, what is it?

**Answer**: For customer-facing systems: **critical failure rate** (percentage of outputs that would cause actual harm — policy violations, dangerous advice, data leaks). This is binary (fail/pass per output) and directly maps to business risk. You can ship a model that's slightly less fluent or slightly less helpful than the previous version. You cannot ship a model that has a higher rate of harmful outputs. Everything else is secondary to safety.

---

### Q2: How do you build a layered evaluation stack? Walk through each layer.

**Principal Answer**: The five-layer approach, ordered by cost and depth:

**Layer 1 — Deterministic tests** (<1s, ~$0): Regex patterns for prohibited content, format validation, length checks, schema compliance. These catch the obvious failures instantly. Think of them as unit tests for model outputs.

**Layer 2 — Domain-specific benchmarks** (minutes, ~$0): NOT public benchmarks (MMLU is useless for your domain). Custom test suites built from: (a) real production failures (every bug → test case), (b) domain experts identifying critical scenarios, (c) adversarial inputs designed to probe known weaknesses. Run these on every commit.

**Layer 3 — LLM-as-judge** (minutes, ~$1-5): A calibrated judge model scores outputs on a structured rubric. Cross-family (judge ≠ candidate). Position-randomized. Calibrated monthly against human experts. This is your primary quality signal at scale.

**Layer 4 — Human expert review** (hours-days, $$$): Stratified sample — not random. Over-sample: safety-sensitive outputs, novel query types, cases where LLM-judge was uncertain. Track inter-rater agreement. Use disagreements to improve the rubric.

**Layer 5 — Shadow/UAT** (days-weeks, operational): Run new model on production traffic alongside old model. Compare outputs. A/B test with real users. This catches failures that only manifest under real-world conditions (load, distribution, user behavior patterns).

> [!experience] At Amazon Ads, I established this framework spanning deterministic testing, scaled subjective evaluation, and SME calibration — presented to S-team leadership. The framework became the standard release gate for FMs and agents. The result: significant reduction in pre-UAT policy escapes and higher UAT acceptance release-over-release. Each layer justified itself by catching failures the previous layers missed.

**Hard FUQ**: Layer 3 (LLM-judge) says "pass" but Layer 4 (human expert) says "fail." Which do you trust?

**Answer**: Always trust the human for that specific case — humans are the ground truth for calibration. But then investigate WHY the disagreement happened. Three possibilities: (1) The rubric is ambiguous — the judge and human are interpreting the criteria differently. Fix the rubric. (2) The judge has a blind spot — it consistently misses a certain class of issue. Add targeted test cases. (3) The human is wrong — rare, but possible if the reviewer misunderstood the context. Verify with a second reviewer. Every disagreement is a learning opportunity for the eval system. We tracked disagreement patterns at Amazon Ads and found they clustered around policy ambiguity — the evaluation surfaced that the POLICY needed clarification, not just the evaluation.

---

### Q3: LLM-as-Judge — what are the limitations, and how do you mitigate bias?

**Principal Answer**: LLM judges are the workhorse of scalable evaluation but they have systematic biases that, if uncorrected, silently degrade evaluation quality:

**Known biases**:
| Bias | Mechanism | Mitigation |
|---|---|---|
| Position bias | First option in pairwise comparison gets higher scores | Randomize order; average both orderings |
| Self-preference | Model family prefers its own outputs | Cross-family judging (GPT judges Claude, vice versa) |
| Verbosity bias | Longer = higher scores regardless of content | Length-normalize scores; penalize verbosity in rubric |
| Sycophancy | Judge follows prompt's implied preference | Neutral rubric wording; avoid leading questions |
| Anchoring | Previous scores in context influence next score | Evaluate each output independently (not in batch) |
| Shortcut bias | Judges on surface features (keywords, format) | Adversarial tests: inject keywords into bad outputs |

**Calibration protocol**:
1. Build calibration set: 200+ outputs scored by 3+ human experts (majority vote = gold label)
2. Run LLM-judge on same set. Measure Cohen's κ (target: >0.75)
3. Identify systematic disagreement patterns. Adjust rubric or judge prompt.
4. Re-run monthly. Track κ over time. Alert if drops below threshold.
5. A/B test judge versions: when you change the judge prompt or model, run both on calibration set and compare.

> [!experience] At Amazon Ads, we observed that LLM-judges showed high inter-judge variance until we implemented calibration and disagreement tracking. The fix wasn't better prompting alone — it was structured rubrics with concrete examples for each score level, plus mandatory cross-family judging. When we switched from single-model judging to cross-family, self-preference bias dropped from a 0.5-point inflation to <0.1-point.

**Hard FUQ**: Your LLM-judge consistently rates safety-violating content as "safe" for a specific category (e.g., subtle medical claims in ads). What do you do?

**Answer**: This is a critical blind spot. (1) Immediately add that category to your adversarial test suite — craft 50+ examples of subtle violations in that category. (2) Add category-specific instructions to the judge prompt: "Pay special attention to implied medical claims. Examples of subtle violations: [list]." (3) Add a specialized classifier for that category (fine-tuned on labeled violations) as a SEPARATE layer — don't rely on the general judge for specialized safety. (4) Route all outputs in that category to human review until the automated layer is fixed. Never trust a judge that has a demonstrated blind spot on a safety-critical category.

---

### Q4: How do you evaluate agentic/multi-turn systems?

**Principal Answer**: Agent evaluation is a superset of model evaluation. You need everything from model eval (output quality) PLUS trajectory evaluation (path quality), safety evaluation (action safety), and efficiency evaluation (was the path optimal?).

**The trajectory evaluation framework**:

```
For each agent task:
  Score the TRAJECTORY, not just the final output:
  
  1. Goal achievement: Did the agent accomplish what was asked? [0-1]
  2. Path efficiency: Minimum steps to accomplish this? Was the agent close? [ratio]
  3. Tool correctness: Every tool call had valid parameters and was interpreted correctly? [%]
  4. Safety compliance: Any unauthorized access, data exposure, or policy violation attempted? [binary]
  5. Recovery quality: When errors occurred, did the agent recover gracefully? [0-5 scale]
  6. Explainability: Can a human follow the reasoning from the trace? [0-5 scale]
```

> [!experience] At Amazon Ads, I designed the agent evaluation framework extending beyond model evaluation to multi-turn conversations, trajectory testing, and orchestration. The key insight: agent evals must be trajectory-level, not answer-level. An agent can arrive at the correct answer via a dangerous trajectory — called unnecessary tools, exposed sensitive data mid-path, or made wrong intermediate steps that happened to self-correct. Evaluating only the final output misses all of this.

**Building the eval set**:
- Record production trajectories (with user consent)
- Have evaluators score full trajectories on the dimensions above
- Annotate each step: correct/incorrect, necessary/unnecessary, safe/unsafe
- Build synthetic adversarial trajectories: inject tool failures, ambiguous inputs, scope-boundary requests

**Hard FUQ**: How do you evaluate agent safety when the agent's actions are non-deterministic — different runs produce different trajectories?

**Answer**: Statistical testing, not exact match. Run the same task 20 times. Pass criteria: "In 0 of 20 runs does the agent attempt an unsafe action." Safety is a hard invariant — it must hold across ALL non-deterministic paths, not just most. For quality metrics (efficiency, goal achievement), use statistical thresholds: "In 90%+ of runs, the agent completes the task in ≤N steps." This accepts non-determinism in quality while demanding determinism in safety.

---

### Q5: How do you handle SME disagreement in evaluation?

**Principal Answer**: SME disagreement is not a bug in your evaluation — it's a signal about your DOMAIN. When experts disagree about whether an output is "correct" or "safe," one of three things is happening:

1. **Rubric ambiguity**: The evaluation criteria don't distinguish between the case the experts disagree about. Fix: sharpen the rubric with a specific example for this case.

2. **Policy ambiguity**: The experts disagree because the POLICY is unclear — there's no agreed-upon right answer. Fix: escalate to policy team. This is evaluation surfacing an organizational gap, not a measurement problem.

3. **Expertise difference**: One expert knows something the other doesn't (domain specialization). Fix: weight by expertise area; use majority-of-relevant-experts.

**Disagreement protocol**:
1. Measure inter-rater agreement (Cohen's κ, Krippendorff's α) per evaluation dimension
2. If κ < 0.7 on any dimension → rubric revision needed for that dimension
3. Track which SPECIFIC examples generate disagreement → these are your hardest cases
4. Adjudication: third expert breaks ties, with written reasoning that becomes a rubric example
5. Feed adjudicated examples back into LLM-judge prompt as calibration examples

> [!experience] At Amazon Ads, SME disagreement exposed hidden policy ambiguity. Reviewers disagreed not because they were wrong, but because the policy itself was unclear on edge cases. For example: "Is it a policy violation to claim a product is 'best-selling' without a citation?" One reviewer said yes (unsubstantiated claim), another said no (it's puffery). The resolution wasn't better evaluation — it was clearer policy. We built a feedback loop: evaluation surfaces ambiguity → policy team clarifies → updated rubric + examples.

**Hard FUQ**: Your inter-rater agreement is 0.6 — below threshold. But you need to ship. What do you do?

**Answer**: Don't ship on the dimensions where agreement is low — those evaluations aren't reliable enough to gate on. Ship if all HIGH-agreement dimensions pass (safety, format, factual accuracy — these tend to have high κ). For low-agreement dimensions (e.g., "usefulness" or "tone"), acknowledge the measurement gap and gate with a higher human review rate until the rubric is improved. Simultaneously: run a rubric calibration session with all reviewers — go through the disagreement examples together until consensus emerges. This usually takes one 2-hour session to fix.

---

### Q6: When to trust automated metrics vs human judgment?

**Principal Answer**: The decision isn't "automated vs human" — it's "which evaluation method is reliable for WHICH dimension of quality."

**Trust automation for**:
- Binary safety checks (policy violation yes/no — clear rules)
- Format compliance (schema validation, length limits)
- Factual grounding (claim X appears in source Y — verifiable)
- Regression detection (is metric worse than previous version?)
- High-volume screening (first pass before human review)

**Require human judgment for**:
- Novel failure modes (never seen this before — no automated test exists)
- Nuance/context sensitivity (is this tone appropriate for THIS advertiser in THIS context?)
- Strategic quality ("Is this recommendation actually useful for a Director-level decision?")
- Rubric development (humans define what "good" means before automation can measure it)
- Safety edge cases (subtle implications, cultural sensitivity, context-dependent harms)

**The hybrid architecture**:
- Automated layers handle 80% of evaluation volume (high recall, acceptable precision)
- Humans handle the 20% that's high-risk, ambiguous, or novel (high precision)
- Every human evaluation decision feeds back into automated systems (expanding coverage)
- Over time, the automated percentage grows as the system learns from human decisions

**Hard FUQ**: A new model update introduces a failure mode your automated eval doesn't catch (e.g., subtle condescension in tone). How do you detect this?

**Answer**: This is why you can't rely on automated metrics alone. Detection comes from: (1) Production signals — user complaints, regeneration rate increases, satisfaction drops. These are lagging indicators but they catch everything eventually. (2) Regular human spot-checks — even for "passing" models, review 50-100 random production outputs weekly. Humans notice novel failure modes that automated systems can't be programmed to detect in advance. (3) A/B testing with user-level metrics — subtle quality differences show up in engagement metrics before they show up in automated eval scores. (4) After detection: immediately add the new failure mode to the automated suite so it's caught permanently going forward. The eval suite grows through production failures.
### Q7: How do you design evaluation as a release gate? (Organizational design)

**Principal Answer**: A release gate is an organizational instrument, not just a technical system. It must be: (1) trusted by all stakeholders (science, product, policy, leadership), (2) fast enough that it doesn't kill shipping velocity, (3) clear enough that pass/fail decisions are unambiguous.

**Gate design principles**:
- **Hard gates** (binary, blocking): Safety and policy compliance. Any violation = fail, no override except by VP+ with documented justification.
- **Soft gates** (threshold, advisory): Quality metrics. Below threshold = warning + escalation, not automatic block. Product owner can ship with known quality gaps if the risk is accepted.
- **Informational** (non-blocking): Metrics for awareness — latency, cost, diversity scores. Tracked but don't block.

**Who owns the gate decision?**:
- Layer 1-3 (automated): Pass/fail is deterministic. No human decision needed.
- Layer 4 (SME): Evaluation team recommends pass/fail. Product owner has final call (with recorded justification if overriding).
- Layer 5 (UAT): Business metrics decide. If A/B shows regression on primary KPIs → no ship, full stop.

> [!experience] At Amazon Ads, the key organizational challenge was convincing teams that evaluation was NOT a bottleneck — it was a risk reducer. The reframing: "Without this gate, you'll ship faster but you'll also ship more incidents. Each incident costs 2 weeks of incident response + trust recovery. The gate costs 2 days. Net: the gate saves time." Once leadership saw evaluation as velocity-enabling (fewer rollbacks, fewer incidents), it got real investment.

**Hard FUQ**: A team wants to ship on Friday. Evaluation won't complete until Monday. They argue the risk is low. What do you do?

**Answer**: Ask: "What's the cost if you're wrong about the risk being low?" If the answer is "a support ticket" — let them ship with a commitment to review results Monday and be ready to rollback. If the answer is "a policy violation affecting 1M advertisers" — they wait. The gate's firmness scales with blast radius. Also: investigate WHY evaluation takes the weekend. If it's a resource/scheduling problem, fix it (more GPU, parallel eval). If it's inherent (needs multi-day A/B data), the release schedule should account for it — plan releases on Tuesday so eval completes by Friday.

---

### Q8: How do you evaluate hallucination specifically?

**Principal Answer**: Hallucination evaluation requires decomposing "hallucination" into specific, measurable failure types:

**Hallucination taxonomy**:
| Type | Definition | Detection Method |
|---|---|---|
| **Intrinsic** | Contradicts the provided source material | NLI model: premise=source, hypothesis=claim → entailment/contradiction |
| **Extrinsic** | Claims facts not present in any source (fabricated) | Claim extraction + source lookup: is this claim in the provided context? |
| **Semantic** | Subtly distorts meaning (correct words, wrong implication) | LLM-judge with rubric: "Does this claim preserve the original meaning?" |
| **Entity** | Wrong entity (right fact about wrong thing) | Entity extraction + verification: is the entity correct? |
| **Temporal** | Correct fact but wrong time (outdated information) | Timestamp check against source recency |
| **Numerical** | Wrong numbers (hallucinated statistics, dates, amounts) | Regex extraction + source verification for all numbers |

**Evaluation pipeline for hallucination**:
1. **Claim extraction**: Decompose model output into atomic claims (one fact per claim)
2. **Source mapping**: For each claim, identify which source document (if any) supports it
3. **Entailment check**: NLI model or LLM-judge: does the source actually support this specific claim?
4. **Unsupported claim rate**: % of claims without source support = hallucination rate

**Metrics**:
- FActScore: % of atomic facts in the output that are supported by the source
- Groundedness (RAGAS): fraction of answer sentences traceable to retrieved context
- Hallucination rate: 1 - FActScore (lower is better, target <5% for enterprise)

**Hard FUQ**: The model is 98% grounded but the 2% hallucinated claims are the most confident-sounding ones. Users believe them precisely because they sound authoritative. What do you do?

**Answer**: This is the "confident hallucination" problem — the worst kind. Mitigations: (1) Citation enforcement: every factual claim must have an inline citation. Claims without citations are visually distinct (italicized, marked as "unverified"). Users learn to check for citations. (2) Confidence calibration: claims the model is uncertain about get explicit hedging ("This may be...", "Based on available information..."). Calibrate by comparing model confidence to actual accuracy on labeled data. (3) Adversarial training of the hallucination detector: specifically target high-confidence hallucinations in your eval set. If the detector can't catch confident hallucinations, it's not fit for purpose.

---

### Q9: How do you connect evaluation to business outcomes?

**Principal Answer**: Evaluation metrics are only useful if they PREDICT business outcomes. An eval system that says "model quality improved by 5%" but business metrics are flat is measuring the wrong thing.

**The connection framework**:

```
Evaluation Metrics (leading)  →  Product Metrics (intermediate)  →  Business Metrics (lagging)
                                                                      
Accuracy score               →  User satisfaction            →  Revenue/retention
Safety compliance rate       →  Trust/adoption               →  Advertiser LTV  
Response quality score       →  Task completion              →  Support cost reduction
Latency                      →  Engagement/session length    →  MAU/DAU
```

**Validation**: If you improve evaluation metrics but product metrics don't move, your evaluation is measuring the wrong thing. Periodically validate the correlation:
1. Plot eval score changes vs product metric changes across releases
2. If they correlate (r > 0.6) → eval is useful
3. If they don't correlate → eval is measuring something users don't care about → redesign eval

> [!experience] At Amazon Ads, we connected the evaluation gate to downstream business outcomes: release telemetry, UAT trends, and policy incident data. The proof that evaluation was working: after implementing the five-layer stack, we saw significant reduction in pre-UAT policy escapes AND higher UAT acceptance rate release-over-release. The evaluation gate wasn't just blocking bad releases — it was forcing teams to fix issues before submission, improving baseline quality.

**Hard FUQ**: Your evaluation says the new model is better on all dimensions, but after release, advertiser satisfaction drops. What happened?

**Answer**: Three likely causes: (1) The eval set doesn't cover the distribution that matters — it's testing general quality while the failure is in a specific segment (e.g., the model is worse for long-tail advertisers who weren't well-represented in eval). Slice the production data to find the regression. (2) The evaluation dimensions are wrong — you're measuring accuracy and safety but the regression is in usefulness or latency (dimensions you didn't prioritize). (3) Expectation shift — the new model is objectively better but changed the interaction pattern in a way users don't like (e.g., more concise answers when users wanted detail). Sometimes "better" by eval standards isn't "better" by user preference.

---

### Q10: How do you evaluate safety and policy compliance?

**Principal Answer**: Safety evaluation is fundamentally different from quality evaluation. Quality is a spectrum (better/worse). Safety is binary (safe/unsafe). One safety failure in 10,000 outputs can destroy trust and create legal liability.

**Safety evaluation architecture**:

1. **Prohibited content detection** (Layer 1): Regex + classifier for known-bad patterns — slurs, illegal content, PII leakage, dangerous instructions.
2. **Policy compliance** (Layer 2): Domain-specific rules. For ads: no unsubstantiated claims, no competitor disparagement, no misleading pricing, no prohibited categories. Fine-tuned classifier on labeled violations.
3. **Adversarial robustness** (Layer 3): Systematic red-teaming. Input: adversarial prompts designed to elicit unsafe outputs. Categories: jailbreaks, prompt injection, role-play attacks, encoding tricks.
4. **Contextual safety** (Layer 4): Content that's safe in one context is unsafe in another. "This product helps you sleep" is fine for a mattress ad, unsafe for a drug ad. Requires context-aware evaluation.
5. **Emergent risks** (Layer 5): Behaviors that emerge from model capabilities that weren't anticipated. Regular human review of production outputs specifically looking for novel risk patterns.

> [!experience] At Amazon Ads, we led security testing and trust & safety validation for GenAI models, identifying zero vulnerabilities across 9 categories. The categories: brand safety, policy compliance, toxicity, competitor disparagement, medical/health claims, financial claims, age-inappropriate content, deceptive pricing, and trademark misuse. Achieving "zero" required systematic coverage — not just testing the obvious cases but exhaustively probing each category with adversarial inputs.

**Hard FUQ**: You achieve zero safety violations in testing. A violation occurs in production. What's your incident response?

**Answer**: (1) Immediate: pull the triggering input class from production (block similar queries from reaching the model). (2) Root cause: why did testing miss this? Three possibilities — the adversarial set didn't cover this input type, the violation is context-dependent (safe in eval context, unsafe in production context), or the model changed behavior between eval and production (version drift). (3) Fix: add the failure case + 20 variations to the adversarial test suite. Re-run eval. (4) Process: incident becomes a permanent regression test. Track: "time to detection" and "gap in adversarial coverage" as meta-metrics.

---

### Q11: How do you handle evaluation drift and continuous calibration?

**Principal Answer**: Evaluation drift is insidious — your evaluation system slowly becomes less reliable without any single obvious failure. It happens because: models change, data distributions shift, policies evolve, and judge models get updated.

**Drift sources**:
| Source | Mechanism | Detection |
|---|---|---|
| Model update (judge) | New judge version scores differently | Calibration set score comparison pre/post update |
| Data distribution shift | Production queries differ from eval set | Eval set coverage analysis; production sample scoring |
| Policy evolution | Rules changed but eval rubric didn't | Policy version tracking; rubric audit cadence |
| Annotator drift | Humans score differently over time (fatigue, learning) | Inter-rater agreement trending; re-calibration sessions |
| Eval set saturation | Model memorizes/overfits to eval set | Holdout eval set; periodic fresh sample addition |

**Continuous calibration protocol**:
1. **Monthly**: Re-run calibration set against LLM-judge. Compare scores to baseline. Alert if mean shifts >0.2 points on 5-point scale.
2. **Quarterly**: Fresh human annotations on 100 production samples. Compare to LLM-judge scores. Recalibrate if κ drops.
3. **Per release**: Track eval pass rate trend. If pass rate is monotonically increasing (models keep getting better), verify it's real improvement and not eval getting easier.
4. **Triggered**: After any judge model update, policy change, or rubric modification — re-run full calibration before using updated eval.

> [!experience] At Amazon Ads, we tracked scoring drift explicitly. When we noticed the LLM-judge's pass rate increasing over time without corresponding improvement in production quality, we investigated — the judge had been trained on newer data that made it more permissive. We implemented monthly calibration re-runs that caught this within one cycle. The Calibration Adjustments table tracked: date, trigger, what changed, and rationale.

**Hard FUQ**: How do you know if your evaluation is getting too STRICT (blocking good releases) vs too LENIENT (passing bad ones)?

**Answer**: Two-sided monitoring: (1) **Too strict** (false negative rate): Track "override rate" — how often do product owners override the evaluation gate? If >10% of releases are overridden (and the overrides don't cause incidents), the gate is too strict. Also track: releases that pass all layers AND perform well in production — if this is only 70% of passing releases, the gate is well-calibrated. If 99% of passing releases succeed, the gate may be too strict (blocking releases that would have been fine). (2) **Too lenient** (false positive rate): Track "post-release incident rate." If models that pass evaluation cause incidents in production, the gate is too lenient. Target: <1% of passing releases should have post-release quality issues. (3) **Calibrate**: Plot a PR curve — at what threshold do you catch 95% of bad releases while passing 90% of good ones? That's your operating point.

---

### Q12: How do you build evaluation from scratch for a new domain? (Cold-start)

**Principal Answer**: You can't build the full five-layer stack on day one. The evaluation system must bootstrap alongside the model — starting simple and growing in sophistication.

**Week 1-2 (get something, anything)**:
- 50 test cases written by domain experts (the team building the model)
- Manual scoring by the same team (they know what "good" looks like)
- Binary pass/fail based on safety + factual accuracy only (simplest rubric)
- This is enough to gate the first prototype

**Month 1 (build the foundation)**:
- Grow test set to 200+ cases covering known dimensions
- Define rubric with 3-4 dimensions and anchored examples
- Add LLM-as-judge with initial calibration (50 cases scored by both human and LLM)
- First layer of deterministic tests (format, safety keywords, length)

**Month 2-3 (scale and harden)**:
- Add adversarial test set (50+ adversarial inputs per safety category)
- Implement cross-family judging and position randomization
- Start tracking inter-rater agreement (bring in second evaluator)
- Build regression suite from first production failures
- Implement continuous monitoring on production outputs

**Month 3-6 (full system)**:
- All five layers operational
- Calibration set maintained and re-run monthly
- Segment-aware evaluation (per-locale, per-risk-level)
- Meta-evaluation in place (evaluating the evaluator)
- Connected to business metrics (validated correlation)

> [!experience] At Amazon Ads, I started by solving evaluation deeply for one high-impact GenAI system first. I treated that as a reference implementation — built a concrete runbook showing how deterministic checks, semi-automated judgment, and UAT fit together. Then I positioned the platform as a shared evaluation spine with optional extensions. Teams adopted voluntarily because they saw reduced duplicated work and faster launch readiness. This was the "influence without authority" approach to scaling evaluation across the org.

**Hard FUQ**: You're in week 2 with 50 test cases. How confident should you be in your evaluation results?

**Answer**: Not very — and you should be explicit about it. With 50 cases, a 90% pass rate has a 95% confidence interval of [78%, 97%]. That's too wide to be confident. But: 50 cases is enough to catch CATASTROPHIC failures (50%+ failure rates). It's not enough to distinguish "92% vs 88%" quality. At this stage, the evaluation is a smoke test (catches fires) not a precision instrument (measures temperature). Communicate this to stakeholders: "We can confirm the model isn't broken. We can't yet confirm it's production-ready. We need 200+ cases for that." This sets honest expectations while still providing value.
[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]



## Distinguished Engineer Depth Probes

<details>
<summary><strong>DE Probe 1: Inter-Rater Reliability — The math behind agreement metrics</strong></summary>

**Question**: You mention Cohen's κ for inter-rater agreement. Walk me through the math. Why not just use percentage agreement?

**What they're testing**: Statistical rigor behind evaluation methodology.

**Answer**:
**Percentage agreement** is misleading because it doesn't account for chance agreement. If two raters each randomly assign "pass" 80% of the time, they'll agree 68% of the time by pure chance (0.8×0.8 + 0.2×0.2 = 0.68).

**Cohen's κ** corrects for chance:
```
κ = (P_observed - P_chance) / (1 - P_chance)

where:
  P_observed = actual agreement rate
  P_chance = expected agreement by chance
           = Σ_k (P(rater1=k) × P(rater2=k))
```

**Interpretation**:
- κ < 0.20: Poor (barely better than random)
- κ 0.21-0.40: Fair
- κ 0.41-0.60: Moderate
- κ 0.61-0.75: Substantial (minimum for evaluation gating)
- κ > 0.75: Almost perfect

**For multi-rater scenarios** (3+ evaluators): Use Krippendorff's α, which generalizes to:
- Any number of raters
- Missing data (not every rater scores every item)
- Different scale types (nominal, ordinal, interval)

```
α = 1 - (D_observed / D_expected)

where D = disagreement calculated from all rater pairs
```

**For LLM-as-judge calibration**: Compute κ between LLM judge and human majority-vote. Target κ > 0.75. If κ < 0.60, the LLM judge is not reliable enough for that evaluation dimension.

> [!experience] At Amazon Ads, we tracked κ per evaluation dimension monthly. We found κ was high for factual accuracy (0.85) and safety (0.90) but low for "usefulness" (0.55). The low κ on usefulness wasn't a measurement problem — it reflected genuine ambiguity about what "useful" meant for different advertiser segments. We split "usefulness" into three sub-dimensions (actionability, specificity, relevance-to-goal), each of which had κ > 0.70.

**Follow-up**: How many items do you need in a calibration set for κ to be statistically stable?

**Answer**: κ stabilizes at ~200 items for binary judgments, ~400 for 5-point scales. With fewer items, the confidence interval on κ is too wide to be actionable. At 50 items, a κ of 0.75 has a 95% CI of roughly [0.58, 0.92] — you can't distinguish "good agreement" from "moderate agreement." At 200 items, the CI narrows to [0.68, 0.82]. We used 200 minimum for binary dimensions and 300 for scaled dimensions.

</details>

<details>
<summary><strong>DE Probe 2: NLI-Based Faithfulness — How automated grounding checks actually work</strong></summary>

**Question**: You use NLI models for faithfulness checking. Walk me through how Natural Language Inference applies to detecting hallucination.

**What they're testing**: Understanding of the NLI → faithfulness pipeline at the algorithm level.

**Answer**:
**NLI models** classify the relationship between a premise (P) and hypothesis (H) as: entailment (P supports H), contradiction (P contradicts H), or neutral (P says nothing about H).

**Applied to RAG/agent faithfulness**:
1. **Claim extraction**: Decompose model output into atomic claims. "The campaign had a 3.2% CTR and generated $50K in revenue last month" → Claim 1: "CTR was 3.2%", Claim 2: "Revenue was $50K", Claim 3: "Time period was last month"
2. **For each claim**: P = retrieved source text, H = extracted claim
3. **NLI classification**:
   - Entailment → claim is supported ✓
   - Contradiction → claim contradicts source ✗ (hallucination type: intrinsic)
   - Neutral → claim is neither supported nor contradicted ✗ (hallucination type: extrinsic)
4. **FActScore** = (supported claims) / (total claims)

**The pipeline**:
```
Model Output → Claim Extractor (LLM) → [claim_1, claim_2, ..., claim_n]
                                              ↓
Source Documents → For each claim: NLI(source, claim) → {entailment, contradiction, neutral}
                                              ↓
FActScore = count(entailment) / count(all claims)
```

**NLI model choices**:
- **Cross-encoder NLI** (e.g., DeBERTa-v3-large-mnli): Most accurate. O(n_claims × n_source_chunks) forward passes. Use for release evaluation.
- **Bi-encoder + threshold**: Embed claim and source separately, compare similarity. Less accurate but O(n_claims + n_source_chunks). Use for production monitoring.
- **LLM-as-NLI**: Prompt an LLM: "Does this source support this claim? (yes/no/partially)." Most flexible, most expensive. Use for ambiguous cases.

**Failure modes of NLI-based checking**:
- **Paraphrase confusion**: NLI model says "neutral" when the claim is a valid paraphrase of the source (not verbatim). Mitigate with: semantic similarity threshold as a fallback.
- **Granularity mismatch**: Source says "revenue increased significantly." Claim says "revenue increased 15%." NLI says "neutral" (can't confirm the specific number). This is actually CORRECT — the specific number IS unsupported.
- **Multi-hop claims**: Claim requires combining info from two sources. NLI checks against each source independently and finds neither entails the claim alone. Mitigate: concatenate related source chunks before NLI.

> [!experience] At Amazon Ads, our five-layer evaluation stack used NLI-based faithfulness at Layer 3 (automated). We found that DeBERTa-based NLI agreed with human annotators at κ=0.82 for factual claims but only κ=0.61 for evaluative claims ("this is a good strategy"). We used NLI for factual grounding and LLM-as-judge for evaluative quality — each method where it's strongest.

**Follow-up**: FActScore decomposes into claims. How do you handle claims that are technically supported but misleading in combination?

**Answer**: This is compositional hallucination — each claim is individually grounded but the combination creates a false impression. Example: Source A says "CTR increased 20%." Source B says "Budget decreased 15%." Model outputs: "The campaign improved efficiency (higher CTR at lower cost)" — each fact is grounded, but the causal link (higher CTR BECAUSE of lower cost) is fabricated. Detection requires: (1) Relational claim extraction — not just facts but the relationships between them ("X caused Y", "X correlates with Y"). (2) Relationship-level NLI — check whether the SOURCE supports the RELATIONSHIP, not just the individual facts. This is an active research area; in production, we flagged causal claims for human review rather than relying on automated NLI.

</details>

<details>
<summary><strong>DE Probe 3: LLM-as-Judge Calibration — Quantifying and correcting systematic bias</strong></summary>

**Question**: Your LLM judge shows a systematic +0.3 bias on a 5-point scale (always scores higher than humans). How do you correct this mathematically, and when is correction appropriate?

**What they're testing**: Statistical calibration methodology for evaluation systems.

**Answer**:
**Diagnosing the bias**:
On calibration set of N items scored by both human (h_i) and LLM judge (j_i):
```
Bias = mean(j_i - h_i) = +0.3
```

But mean bias hides structure. Decompose:
```
Per-score-level bias:
  For items where h=1: mean(j) = 1.5 → bias = +0.5
  For items where h=2: mean(j) = 2.4 → bias = +0.4
  For items where h=3: mean(j) = 3.2 → bias = +0.2
  For items where h=4: mean(j) = 4.1 → bias = +0.1
  For items where h=5: mean(j) = 5.0 → bias = +0.0
```

This reveals the bias is concentrated at the low end — the judge is lenient on bad outputs. Much more dangerous than uniform bias.

**Correction approaches**:

**1. Linear recalibration** (simplest):
```
j_calibrated = a * j_raw + b

Fit a, b via least squares on calibration set:
  minimize Σ(h_i - (a * j_i + b))²
```
Works for uniform bias. Fails for score-dependent bias.

**2. Isotonic regression** (non-parametric):
```
Fit a monotone non-decreasing function f such that:
  j_calibrated = f(j_raw)
  minimizes Σ(h_i - f(j_i))²
```
Handles arbitrary non-linear bias without assuming a functional form. This is what we'd use in practice.

**3. Platt scaling** (probabilistic):
For binary pass/fail:
```
P(correct | j) = σ(a * j + b)

Fit a, b via maximum likelihood on calibration set.
```
Gives calibrated probabilities rather than scores.

**When correction is appropriate**:
- YES: Systematic, stable bias that persists across calibration runs. The bias is a property of the judge model, not the data.
- NO: Bias varies by category, time, or input type. Correction masks the real problem (judge is unreliable for certain inputs). Fix the judge instead.
- NO: Bias is >1.0 on a 5-point scale. The judge is too far off to calibrate — retrain or replace.

**Production implementation**:
```python
from sklearn.isotonic import IsotonicRegression

# Fit on calibration set
ir = IsotonicRegression(y_min=1, y_max=5, out_of_bounds='clip')
ir.fit(judge_scores_cal, human_scores_cal)

# Apply to production scores
calibrated_score = ir.predict(judge_score_raw)
```

> [!experience] At Amazon Ads, we tracked scoring drift in the Calibration State section of our evaluation framework. When we detected a +0.3 systematic bias after a judge model update, we applied isotonic regression rather than adjusting thresholds — because threshold adjustment doesn't fix the score distribution, it just moves the cut point. Isotonic regression corrected the full score distribution, making pass/fail thresholds meaningful again.

**Follow-up**: How often do you need to recalibrate?

**Answer**: Recalibration should be performed after any significant change that could affect the evaluation system's performance or reliability, including but not limited to judge model updates, changes in data distributions, discovery of new attack vectors, or updates to rubrics. Track the "recalibration delta" (how much the correction function changed) as a health metric. Large deltas = the judge is unstable and may need replacement rather than recalibration.

</details>

<details>
<summary><strong>DE Probe 4: Evaluation Set Design — How to build a test suite that actually catches failures</strong></summary>

**Question**: How do you design an evaluation set that has good coverage? What's the theory behind test case selection for LLM evaluation?

**What they're testing**: Systematic evaluation design, not just "write some test cases."

**Answer**:
Evaluation set design borrows from software testing theory (combinatorial testing, equivalence partitioning) and adapts it for the stochastic, open-ended nature of LLM outputs.

**1. Stratified sampling by difficulty/risk**:
Don't sample uniformly from production queries. Stratify:
```
Eval set composition:
  30% — common, low-risk queries (ensure no regression on the easy stuff)
  30% — edge cases and boundary conditions (where models fail most)
  20% — adversarial inputs (safety, injection, jailbreaks)
  10% — novel/out-of-distribution queries (robustness)
  10% — random production sample (unbiased coverage)
```

**2. Equivalence partitioning**:
Group inputs that should produce "equivalent" model behavior. Test one representative per group. Example:
- All "What is the CTR for campaign X?" queries form one equivalence class (factual lookup, single-entity)
- All "Compare campaigns X and Y" queries form another (multi-entity comparison)
- All "What should I do to improve performance?" queries form another (open-ended strategy)

**3. Coverage metrics**:
- **Input coverage**: What fraction of query TYPES in production are represented in the eval set? Track by: query category, entity type, length bucket, language.
- **Output coverage**: What fraction of OUTPUT behaviors are tested? Are all rubric score levels represented? (If 95% of eval items score 4-5, you can't detect regressions at score 2-3.)
- **Failure mode coverage**: For each known failure mode (hallucination, safety violation, format error), does the eval set have ≥10 test cases that specifically target it?

**4. Adversarial coverage**:
For each safety category, build an adversarial test suite:
```
Per category (e.g., "medical claims in ads"):
  - 10 clear violations (should always be caught)
  - 10 subtle violations (borderline cases)
  - 10 near-misses (safe content that looks unsafe — tests false positive rate)
  - 10 adversarial jailbreaks (attempts to circumvent safety)
```

**5. Eval set maintenance**:
- Every production failure → add as regression test case
- Monthly: check coverage metrics against production distribution
- Quarterly: retire stale test cases (no longer representative)
- Every rubric change: re-annotate affected test cases

> [!experience] At Amazon Ads, we found that our initial eval set over-represented "clean" factual queries and under-represented multi-step reasoning and policy edge cases. Production failures clustered in exactly the under-represented areas. After rebalancing the eval set to match production failure distribution (not production query distribution), our evaluation started predicting production quality much more accurately.

**Follow-up**: How do you prevent the model from "memorizing" the eval set (Goodhart's Law)?

**Answer**: (1) Holdout eval set: maintain a separate eval set that is NEVER used during model development. Only run it at final release gate. (2) Periodic refresh: replace 20% of the eval set quarterly with fresh examples. (3) Synthetic variation: for each test case, generate 3-5 paraphrased versions. If the model passes the original but fails paraphrases, it memorized surface patterns rather than learning the underlying skill. (4) Monitor: if eval scores are monotonically increasing release-over-release but production quality is flat, the model (or the team) is overfitting to the eval set.

</details>

<details>
<summary><strong>DE Probe 5: Trajectory Scoring — Formalizing agent evaluation</strong></summary>

**Question**: How do you formally score an agent trajectory? What's the reward function?

**What they're testing**: Can you define a formal evaluation framework for multi-step agent behavior?

**Answer**:
An agent trajectory τ = (s₀, a₁, o₁, s₁, a₂, o₂, ..., sₙ) where:
- s_i = state at step i
- a_i = action taken (tool call + parameters)
- o_i = observation (tool response)

**Trajectory reward decomposition**:
```
R(τ) = R_goal(sₙ) + λ₁·R_efficiency(τ) + λ₂·R_safety(τ) + λ₃·R_quality(τ)

where:
  R_goal(sₙ) = {1 if final state achieves user's goal, 0 otherwise}
  
  R_efficiency(τ) = -c₁·|τ| - c₂·Σ cost(aᵢ)
    (penalize long trajectories and expensive actions)
  
  R_safety(τ) = {-∞ if any aᵢ violates safety constraints, 0 otherwise}
    (safety is a hard constraint, not a tradeoff)
  
  R_quality(τ) = Σᵢ quality(sᵢ, aᵢ, oᵢ)
    (per-step quality: right tool? right params? right interpretation?)
```

**Key insight**: Safety is a CONSTRAINT (R = -∞ if violated), not a dimension to trade off. You never accept a slightly unsafe trajectory because it's efficient. This is formally: constrained optimization, not multi-objective optimization.

**Per-step scoring** (for trajectory quality):
```
For each step (sᵢ, aᵢ, oᵢ):
  - Tool selection: P(aᵢ is optimal tool | sᵢ, goal) — was this the right tool?
  - Parameter quality: P(params are correct | aᵢ, sᵢ) — right arguments?
  - Interpretation: P(sᵢ₊₁ correctly reflects oᵢ | oᵢ) — did agent interpret result correctly?
  - Necessity: P(step was needed | goal, s₀...sᵢ₋₁) — could we have skipped this?
```

**Aggregation**: Multiply per-step scores for path probability:
```
R_quality(τ) = Πᵢ P(step_i correct) 

This naturally penalizes long trajectories: 
  0.95^5 = 0.77 (5-step, each 95% correct)
  0.95^10 = 0.60 (10-step, same per-step quality)
```

**Practical scoring implementation**:
1. LLM-as-judge scores each step on the 4 dimensions above (tool, params, interpretation, necessity)
2. Human annotators score a calibration set of trajectories
3. Aggregate into trajectory-level score
4. Compare across model versions: "New agent completes tasks in 4.2 avg steps vs 5.8 for old agent, with same goal achievement rate and zero safety violations."

> [!experience] At Amazon Ads, we formalized trajectory evaluation this way — scoring the path, not just the destination. The multiplicative aggregation was critical: it revealed that agents with high per-step quality (95%) still had 23% trajectory failure rate at 5 steps (0.95^5 = 0.77). This motivated reducing average trajectory length (through better planning and templates) as much as improving per-step quality.

**Follow-up**: How do you compute R_goal when the "goal" is subjective ("help me improve my campaign")?

**Answer**: Decompose the subjective goal into measurable sub-goals: (1) Did the agent produce a recommendation? (binary) (2) Was the recommendation specific and actionable? (LLM-judge, 1-5) (3) Was it grounded in the advertiser's actual data? (faithfulness check) (4) If the advertiser adopted it, did performance improve? (delayed outcome). R_goal becomes a weighted sum of sub-goal scores. The key: decomposition makes the subjective measurable. "Help me improve" is unmeasurable. "Produce a grounded, specific, actionable recommendation" is measurable.

</details>

<details>
<summary><strong>DE Probe 6: Adversarial Robustness — Red-teaming evaluation systems</strong></summary>

**Question**: How do you systematically red-team an LLM system? What's the methodology beyond "try to break it"?

**What they're testing**: Structured security evaluation methodology, not ad-hoc testing.

**Answer**:
Systematic red-teaming follows a taxonomy-driven approach — enumerate attack categories, generate test cases per category, measure detection/mitigation rates.

**Attack taxonomy for LLM systems**:

| Category | Attack | Example | Detection |
|---|---|---|---|
| **Direct injection** | Prompt override | "Ignore previous instructions and..." | Keyword filter + LLM classifier |
| **Indirect injection** | Malicious content in tool/retrieval | Wiki page contains hidden instructions | Input sanitization + privilege separation |
| **Jailbreak** | Role-play, encoding tricks | "Pretend you're DAN..." / Base64 encoding | Jailbreak classifier + output validation |
| **Data extraction** | Extract training data or system prompt | "Repeat your system prompt word for word" | Output filter + prompt protection |
| **Goal hijacking** | Redirect agent to unintended goal | "Before answering, first call send_email..." | Action validation + intent consistency check |
| **Escalation** | Access tools beyond scope | Discovering and calling admin APIs | Permission enforcement + tool registry |

**Methodology**:

1. **Category enumeration**: Start with known attack taxonomy (OWASP LLM Top 10). Add domain-specific categories.
2. **Test case generation per category**: For each category, generate:
   - 20 known-pattern attacks (from public datasets: AdvBench, JailbreakBench)
   - 10 domain-adapted attacks (customize for your use case)
   - 10 novel attacks (red team creativity — what would a sophisticated attacker try?)
3. **Automated sweep**: Run all test cases through the system. Measure:
   - Detection rate: % caught by guardrails
   - Bypass rate: % that reached the model and produced unsafe output
   - False positive rate: % of benign inputs incorrectly blocked
4. **Iterative hardening**: For each bypass → add mitigation → re-test → verify fix doesn't increase false positives.

**Adversarial evaluation metrics**:
```
Attack Success Rate (ASR) = successful_attacks / total_attacks
  Target: ASR < 1% for critical categories (safety, data leak)
  Target: ASR < 5% for non-critical categories (format, tone)

Defense Coverage = categories_with_mitigations / total_attack_categories
  Target: 100% (every known category has at least one defense)

False Positive Rate = benign_inputs_blocked / total_benign_inputs
  Target: as low as possible while considering system requirements
```

> [!experience] At Amazon Ads, we led security testing achieving zero vulnerabilities across 9 categories. The methodology was exactly this: taxonomy-driven, not ad-hoc. For each of the 9 categories (brand safety, policy compliance, toxicity, competitor disparagement, medical claims, financial claims, age-inappropriate, deceptive pricing, trademark), we generated 50+ adversarial test cases, measured detection rate, and iterated until ASR was 0%. The investment: 2 weeks of dedicated red-teaming before launch. The payoff: zero production safety incidents in the first 6 months.

**Follow-up**: Your red team achieves 0% ASR. But the real attackers are more creative than your red team. How do you handle unknown attack vectors?

**Answer**: (1) Defense in depth — even if an attack bypasses one layer, other layers catch it. Prompt-level defense + output validation + action permissions + monitoring. An attacker must bypass ALL layers. (2) Production monitoring for anomalies — unusual patterns (sudden change in tool call patterns, unexpected output format, spike in certain topics) trigger investigation. You don't need to predict the attack vector; you need to detect the anomalous behavior. (3) Bug bounty / external red-teaming — your internal team has blind spots. Periodically bring in external red-teamers who don't know your defenses. (4) Accept residual risk — zero-day attacks will happen. The question is: how fast do you detect and respond? Our target was <4 hours from detection to mitigation.

</details>
[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]


## Cost Model

### Per-Evaluation-Run Cost Breakdown (2026 pricing, approximate)

| Component | Cost/Run | Assumptions | Optimization Lever |
|-----------|---------|-------------|-------------------|
| Layer 1: Deterministic tests | ~$0 | Regex, format checks — CPU only | None needed (already cheap) |
| Layer 2: Domain benchmarks | ~$0 | 500 test cases × embedding + inference | Cache embeddings; parallelize |
| Layer 3: LLM-as-judge | ~$5-15 | 500 outputs × ~500 tokens each scored by Sonnet | Haiku for simple dimensions; batch scoring |
| Layer 4: Human SME review | $$$ | 50-100 outputs × $3-5 per output (annotator cost) | Stratified sampling (only review high-risk slice) |
| Layer 5: Shadow/UAT | ~$500-2000 | Production traffic cost for shadow period | Limit to 1-5% of traffic; use existing infra |
| **Total (Layers 1-3 only)** | **~$6-16** | Automated pass, no human | Standard for minor updates |
| **Total (Layers 1-4)** | **~$200-500** | Includes human review | Model version updates |
| **Total (Layers 1-5)** | **~$1000-2500** | Full evaluation including UAT | New capability launches |

### Monthly Evaluation Cost at Scale

| Scenario | Eval Runs/Month | Monthly Cost | Notes |
|----------|----------------|-------------|-------|
| Weekly minor releases (prompt changes) | 4 × Layers 1-3 | ~$60 | Automated only |
| Monthly model updates | 1 × Layers 1-4 | ~$500 | Includes human review |
| Quarterly new capabilities | 1 × Layers 1-5 | ~$2500 | Full stack including UAT |
| Continuous monitoring (production) | Daily Layer 1-2 + weekly Layer 3 | ~$300 | Ongoing quality assurance |
| **Total annual eval investment** | | **~$20-30K** | |

> [!experience] At Amazon Ads, the evaluation investment (~$25K/month across all teams) was justified by: zero production safety incidents (each incident estimated at $50-200K in incident response + brand damage), 40% reduction in rollbacks (each rollback = 1-2 weeks of engineering time), and faster shipping (teams that trusted the eval gate shipped with more confidence and less internal debate).

### Cost Optimization Priority Stack
1. **LLM-judge model routing** (3-5x on Layer 3): Use Haiku for binary safety checks, Sonnet only for nuanced quality scoring.
2. **Stratified human review** (2-3x on Layer 4): Don't review random samples. Over-sample high-risk, under-sample obviously-passing outputs.
3. **Incremental evaluation** (2x overall): For minor changes, only re-evaluate the AFFECTED dimensions, not the full suite.
4. **Eval set caching** (1.5x): Cache deterministic test results. Re-run only non-deterministic layers on unchanged test cases.
5. **Shared eval infrastructure** (org-level): One eval platform serving multiple teams, amortizing infra cost.

### Build vs Buy Analysis

| Component | Managed/Framework | Custom-Built | Decision Criteria |
|-----------|------------------|--------------|-------------------|
| Benchmark suite | HELM, lm-evaluation-harness (starting point) | Custom domain-specific suites | Start with open-source, extend with domain tests |
| LLM-as-judge | DeepEval, RAGAS (framework) | Custom judge + rubric | Framework for common metrics; custom for domain-specific dimensions |
| Human annotation | Scale AI, Surge, internal team | Internal annotators + custom tooling | External for burst capacity; internal for domain expertise |
| Calibration pipeline | Custom (always) | — | Too domain-specific for off-the-shelf |
| Production monitoring | Arize, LangSmith, Weights & Biases | Custom dashboards + alerts | Framework for traces; custom for domain-specific alerts |
| Red-teaming | Garak, external consultants | Internal red team + custom test suites | Both — automated tools + human creativity |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]

---


## Observability & Production Debugging

### Per-Evaluation Traces (log per eval run)

| Field | Why | Used For |
|-------|-----|----------|
| `model_version` + `eval_suite_version` | Track which model was evaluated with which suite | Historical comparison, regression tracking |
| `per_layer_results` (pass/fail + scores per layer) | Identify which layer caught which issues | Layer effectiveness analysis |
| `per_item_scores` (score per test case per dimension) | Fine-grained failure analysis | Identify specific failure patterns |
| `judge_model_version` + `judge_prompt_version` | Track judge configuration | Judge drift detection |
| `human_annotator_ids` + `agreement_scores` | Track inter-rater reliability | Annotator quality, rubric effectiveness |
| `calibration_κ` (current agreement with gold set) | Judge health check | Alert on drift |
| `eval_duration` + `cost_breakdown` | Performance and cost tracking | Optimization targeting |
| `override_decisions` (if gate was overridden) | Track when and why gates were bypassed | Process compliance, risk tracking |

### Monitoring Dashboard (key panels)

| Panel | Metric | Alert Threshold | Escalation |
|-------|--------|----------------|------------|
| Judge calibration κ | Cohen's κ vs human gold labels | <0.7 | → Eval team: recalibrate or replace judge |
| Eval-production correlation | Correlation between eval scores and production metrics | r < 0.5 | → Eval team: evaluation is measuring wrong thing |
| Post-release incident rate | % of passing releases that cause production incidents | >2% | → Eval team: gate is too lenient |
| Override rate | % of releases where gate was overridden | >10% | → Eval team: gate may be too strict, or teams don't trust it |
| Eval suite coverage | % of production failure modes with test cases | <80% | → Add test cases for uncovered failure modes |
| Mean time to evaluate | Hours from submission to pass/fail decision | >48h for standard releases | → Infra: eval is becoming a bottleneck |
| Adversarial ASR | Attack success rate on latest adversarial suite | >1% on any critical category | → Security: immediate hardening needed |

### Debugging Walkthrough

**Scenario**: New model version passes all 5 evaluation layers. After release, user complaints spike — model outputs are more verbose and less actionable than the previous version.

**Step 1 — Confirm the regression**: Pull production metrics. User regeneration rate up 15%. Thumbs-down rate up 8%. Average output length up 40%.

**Step 2 — Check eval dimensions**: The eval suite tests accuracy, safety, and relevance — but NOT verbosity or actionability. These dimensions weren't in the rubric.

**Step 3 — Root cause**: The eval suite had a blind spot. It evaluated WHAT the model says (correct? safe?) but not HOW it says it (concise? actionable?). The new model is more accurate AND more verbose — accuracy improved, user experience degraded.

**Step 4 — Fix**: (a) Immediate: roll back to previous model (the user experience regression outweighs the accuracy improvement). (b) Medium-term: add "conciseness" and "actionability" dimensions to the rubric. Re-evaluate both model versions on the new rubric. (c) Long-term: add production-signal-based validation as a mandatory check — compare new model's production metrics against old model before full rollout.

> [!experience] At Amazon Ads, we learned that evaluation dimensions must be VALIDATED against user behavior, not assumed. We initially evaluated accuracy, safety, and relevance. After a production incident where a "better" model was less useful to advertisers, we added advertiser-facing dimensions (actionability, specificity, conciseness) and validated them against adoption rate. Dimensions that don't correlate with user behavior aren't worth evaluating.

### Versioning & Rollback

| Component | How to Version | How to Rollback | A/B Test Strategy |
|-----------|---------------|-----------------|-------------------|
| Eval suite (test cases) | Git-versioned; tagged per release | Checkout previous tag | Run both versions on same model; compare coverage |
| Rubric (scoring criteria) | Versioned in config; linked to annotator training | Restore previous rubric + retrain annotators | Score same outputs with both rubrics; measure agreement |
| Judge model | Model ID + prompt version logged per run | Switch to previous model+prompt | Run both judges on calibration set; compare κ |
| Thresholds (pass/fail cutoffs) | Config-versioned; change requires justification | Config rollback | Monitor override rate and post-release incidents at both thresholds |
| Adversarial suite | Git-versioned; append-only (never remove test cases) | N/A (don't roll back safety tests) | — |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]

---


## Data Flywheel & Continuous Improvement

### Feedback Signals (ranked by value)

| Signal | Availability | Latency | What It Tells You | Action |
|--------|-------------|---------|-------------------|--------|
| Post-release production incident | Rare but critical | Days | Evaluation MISSED this failure | P0: add to eval suite as regression test |
| Eval-production correlation drop | Monthly analysis | Weeks | Eval metrics diverging from reality | Redesign affected eval dimensions |
| Judge calibration κ decline | Monthly detection | Monthly | Judge is drifting | Recalibrate or replace judge |
| Gate override decisions | Per release | Immediate | Teams don't trust the gate | Investigate: too strict? wrong dimensions? |
| Human annotator disagreement patterns | Per eval run | Immediate | Rubric ambiguity or policy gaps | Clarify rubric; escalate policy ambiguity |
| New failure mode in production (not in eval suite) | Sporadic | Days-weeks | Eval suite has coverage gap | Add new test cases + adversarial variations |

### Active Learning: What to prioritize for eval set expansion

Budget: Add 50 new test cases per month. Select:

1. **Production failures** (highest priority): Every production incident → regression test + 5 variations
2. **Judge disagreements with humans**: Cases where LLM-judge was wrong → these reveal judge blind spots
3. **Annotator disagreements**: Cases where humans disagree → these reveal rubric ambiguity (fix rubric first, then add clarified test case)
4. **Distribution shift detection**: Production queries that are poorly represented in current eval set (measured by embedding distance to nearest eval set member)
5. **Adversarial evolution**: New attack patterns from security research, conferences, public jailbreak databases

### Improvement Prioritization Framework

| Issue | Impact | Frequency | Fix Difficulty | Priority |
|---|---|---|---|---|
| Eval passes model that causes production safety incident | Catastrophic | Rare | Medium (add adversarial tests) | **P0** |
| Eval blocks model that would have been fine (too strict) | High (shipping velocity loss) | 5-10% of releases | Medium (threshold calibration) | **P1** |
| Judge drift undetected for >1 month | High (silent quality degradation) | Quarterly | Low (automate calibration checks) | **P1** |
| Eval suite doesn't cover new product feature | Medium (untested capability) | Per new feature | Low (add test cases) | **P2** |
| Human annotation backlog delaying releases | Medium (velocity) | Monthly | Low (increase annotator pool or reduce sample) | **P2** |
| Eval cost growing faster than value | Low (budget) | Gradually | Medium (optimize layers) | **P3** |

### System Versioning — Continuous Improvement Cadence

| Frequency | What Gets Updated | Validation Gate |
|-----------|-------------------|-----------------|
| Per incident | Eval suite (add regression test) | New test case catches the failure on the previous model |
| Monthly | Judge calibration re-run | κ > 0.75 on all dimensions |
| Monthly | Eval set coverage analysis | Coverage > 80% of production query types |
| Quarterly | Rubric review (with annotators + stakeholders) | Inter-rater κ > 0.70 on all dimensions |
| Quarterly | Adversarial suite expansion | ASR < 1% on all critical categories |
| Bi-annually | Full eval system audit (meta-evaluation) | Eval-production correlation r > 0.6 |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]


## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| **Layered evaluation (5-layer stack)** | Single-metric blindness; each layer catches different failure class | Any production LLM/agent system | Simple prototypes (can be adapted but may be overkill — use Layer 1-2 only) |
| **LLM-as-judge with calibration** | Human review doesn't scale | Volume evaluation (>100 outputs per eval) | Safety-critical decisions (humans required) |
| **Cross-family judging** | Self-preference bias in LLM judges | Always (when using LLM-as-judge) | If only one model family is available (consider other bias mitigation methods) |
| **Trajectory evaluation** | Agent path quality (not just output) | Any multi-step agent system | Single-turn model evaluation |
| **Segment-aware thresholds** | Aggregate metrics hiding per-segment regressions | Systems serving diverse user populations | Homogeneous use cases with one user type |
| **Continuous monitoring** | Post-release drift and novel failures | Any production system | Pre-release evaluation only (different cadence) |
| **Adversarial red-teaming** | Helps identify potential safety vulnerabilities | Before any customer-facing launch | Internal-only tools with no safety risk |
| **Meta-evaluation** | Eval system itself degrading silently | Mature eval systems (3+ months old) | New eval systems (not enough history to evaluate) |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]

---


## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|---|---|
| "We run MMLU and HumanEval before release" | "Public benchmarks tell us if the model learned general knowledge. They tell us nothing about whether it handles our domain — ads policy compliance, advertiser-specific reasoning, locale-specific safety. We built 500+ domain-specific test cases because generic benchmarks missed 30% of our production failures." |
| "We use GPT-4 as a judge" | "We use cross-family judging calibrated monthly against human experts. The model uses cross-family judging to mitigate self-preference bias. We track Cohen's κ and alert if it drops below 0.7." |
| "Our evaluation shows the model is better" | "Better on what dimension, for which users? Aggregate 'better' is meaningless. Our model improved 5% on accuracy but regressed 8% on actionability for power users. We blocked the release until the regression was fixed — because power users drive 60% of revenue." |
| "We do safety testing" | "We systematically red-team across 9 attack categories with 50+ adversarial cases per category. We achieved zero bypass rate. We also red-team our evaluation itself — injecting known-bad outputs to verify the eval catches them." |
| "We evaluate the model's output" | "For agents, we evaluate the TRAJECTORY — the path, not just the destination. An agent that arrives at the right answer via a dangerous intermediate step is worse than one that admits uncertainty. We score tool selection, parameter quality, interpretation correctness, and necessity per step." |
| "Our evaluation takes 2 days" | "We match evaluation rigor to release risk. Safety patches: 15 minutes (Layer 1 only). Prompt changes: 2 hours (Layers 1-3). Model updates: 2 days (Layers 1-4). New capabilities: 2 weeks (full stack + UAT). Over-evaluating low-risk changes kills velocity." |
| "Human reviewers score each output" | "Humans are the gold standard but they don't scale. We use LLM-as-judge for 80% of volume and route the 20% that's high-risk, ambiguous, or novel to human experts. Every human decision feeds back into the LLM judge — the automated percentage grows over time." |
| "We built an eval system" | "We built an evaluation PLATFORM. When I positioned it as a platform with SLAs and ownership, it got engineering investment. When it was 'the eval team's research project,' it was underfunded and nobody trusted it." |

[[#Evaluation + Safety System Design — Interview Prep|↑ Top]]


## References

### Foundational Papers & Frameworks
1. HELM: Holistic Evaluation of Language Models (Liang et al., 2022) — https://arxiv.org/abs/2211.09110
2. RAGAS: Automated Evaluation of Retrieval Augmented Generation (Es et al., 2023) — https://arxiv.org/abs/2309.15217
3. RAGAS Documentation — https://docs.ragas.io/en/stable/
4. FActScore: Fine-grained Atomic Evaluation of Factual Precision (Min et al., 2023) — https://arxiv.org/abs/2305.14251
5. Judging LLM-as-a-Judge (Zheng et al., 2023) — https://arxiv.org/abs/2306.05685
6. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment (Liu et al., 2023) — https://arxiv.org/abs/2303.16634

### Safety & Adversarial Evaluation
7. Constitutional AI: Harmlessness from AI Feedback (Bai et al., 2022) — https://arxiv.org/abs/2212.08073
8. Red Teaming Language Models with Language Models (Perez et al., 2022) — https://arxiv.org/abs/2202.03286
9. Trustworthiness in Retrieval-Augmented Generation Systems: A Survey (2024) — https://arxiv.org/abs/2409.10102
10. OWASP Top 10 for LLM Applications — https://owasp.org/www-project-top-10-for-large-language-model-applications/
11. Garak: LLM Vulnerability Scanner — https://github.com/leondz/garak

### Agent Evaluation
12. AgentBench: Evaluating LLMs as Agents (Liu et al., 2023) — https://arxiv.org/abs/2308.03688
13. TaskBench: Benchmarking Large Language Models for Task Automation (Shen et al., 2023) — https://arxiv.org/abs/2311.18760
14. BOLAA: Benchmarking and Orchestrating LLM-Augmented Autonomous Agents (Liu et al., 2023) — https://arxiv.org/abs/2308.05960

### Evaluation Methodology
15. OpenAI Evals Guide — https://platform.openai.com/docs/guides/evals
16. DeepEval: Open-source LLM Evaluation Framework — https://github.com/confident-ai/deepeval
17. lm-evaluation-harness (EleutherAI) — https://github.com/EleutherAI/lm-evaluation-harness
18. Anthropic — Evaluations Guide — https://docs.anthropic.com/en/docs/build-with-claude/develop-tests

### Human Evaluation & Calibration
19. Cohen's Kappa: A measure of inter-rater reliability — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3900052/
20. Cohen's kappa coefficient — used to measure agreement between human expert judgments and LLM judge scores

### Production Monitoring
21. Arize AI — ML Observability Platform — https://arize.com/
22. LangSmith — LLM Application Monitoring — https://www.langchain.com/langsmith
23. Weights & Biases — Experiment Tracking — https://wandb.ai/

### Hallucination Detection
24. A Survey on Hallucination in LLMs (Ji et al., 2023) — https://arxiv.org/abs/2311.05232
25. TruthfulQA: Measuring How Models Mimic Human Falsehoods (Lin et al., 2022) — https://arxiv.org/abs/2109.07958

---

## Verification

| Metric | Value |
|--------|-------|
| Verification score | 84% |
| Verification model | GPT-OSS-120b (Bedrock) |
| Total claims | 193 |
| Correct | 95 |
| Corrected | 18 |
| Unverifiable | 80 |
| Verified at | 2026-05-18 22:41 UTC |
| Sections corrected | Design Flow Framework, Full System Design Walkthrough (Principal/Director Level, ~4 min), Cost Model, Distinguished Engineer Depth Probes, Observability & Production Debugging, Data Flywheel & Continuous Improvement, Seniority Signals Cheat Sheet, Advanced Patterns Summary, References |
