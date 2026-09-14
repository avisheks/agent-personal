# Reasoning LLMs

> **Last Updated:** 2026-05-31 | **Read time:** ~28 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Reasoning LLMs have evolved from prompting tricks (chain-of-thought [1]) to trained reasoning capabilities via RL (o1 [11], DeepSeek-R1 [13]).
> Key players: OpenAI o1/o3, Claude Extended Thinking [12], DeepSeek-R1 [13], Gemini 2.5 Pro. Main open problem: cost-efficient test-time compute allocation without quality regression.
> Recent breakthrough: DeepSeek-R1 (Jan 2025) demonstrated open-weight RL-trained reasoning matching o1-level performance using GRPO [4][13]. Trend: reasoning as an inference-time scaling axis complementing parameter scaling.

## State of the Art

### Current Best Approaches

- **RL-trained reasoning (o1/R1 style)** — Multi-stage pipeline (SFT cold-start then GRPO/PPO) trains models to generate long internal chains-of-thought before answering; achieves SOTA on math/code [11][13]
- **Extended thinking / budget forcing** — Allocate variable test-time compute per query; models learn when to think longer [5][12]
- **Process reward models (PRMs)** — Train verifiers that score each reasoning step, guiding search at inference [3][14]
- **Self-consistency decoding** — Sample multiple reasoning paths and majority-vote on final answers for reliability [6]
- **Distilled reasoning** — Transfer reasoning capability from large RL-trained models to smaller ones via SFT on reasoning traces [13]

### Recent Breakthroughs (last 12 months)

- **DeepSeek-R1** (Jan 2025): Open-weight 671B MoE model trained with GRPO achieves o1-level reasoning; released full technical report [13]
- **Scaling test-time compute** (Aug 2024): Snell et al. showed optimal compute allocation depends on problem difficulty — easy problems need breadth, hard problems need depth [5]
- **GRPO adoption** (Feb 2024): DeepSeekMath demonstrated critic-free RL training matching PPO quality at lower cost [4]
- **Claude Extended Thinking** (2024): Anthropic shipped streaming extended thinking with user-visible reasoning tokens [12]

### Open Problems

- **Compute-optimal test-time allocation**: How to decide how much reasoning budget to spend before seeing the answer [5]
- **Reasoning faithfulness**: Generated chains may not reflect actual model computation (post-hoc rationalization)
- **Benchmark saturation**: GSM8K at 95%+, MATH approaching 90% — remaining errors are annotation issues or genuine frontier problems [8][9]
- **Cost at scale**: 10-100x token generation per query makes reasoning models expensive for high-throughput applications

### Benchmark Standings

| Benchmark | SOTA Model | Score | Date |
|-----------|-----------|-------|------|
| MATH [9] | o3 (high compute) | 96.4% | Jan 2025 |
| GSM8K [8] | DeepSeek-R1 | 97.3% | Jan 2025 |
| ARC-AGI | o3 (high compute) | 87.5% | Dec 2024 |
| AIME 2024 | o3 | 96.7% | Jan 2025 |
| GPQA Diamond | Claude 3.5 (thinking) | 65.0% | 2024 |

## Executive Summary

Reasoning LLMs shift computation from training time to inference time — models learn to "think" through multi-step chains before answering, trading tokens for accuracy. The core architectural decision is **test-time compute allocation**: how much reasoning budget to spend per query, balancing cost against accuracy gain [5]. Choose distilled reasoning models for latency-sensitive applications, full RL-trained reasoning for accuracy-critical tasks, or adaptive routing between fast/reasoning models for cost-efficient production systems.

- **Choose RL-trained reasoning (o1/R1)** when accuracy on hard problems justifies 10-100x inference cost
- **Choose distilled reasoning** when you need 80% of reasoning quality at 2-5x base cost
- **Choose adaptive routing** when query mix includes both easy and hard problems (most production settings)

**The killer framing:** "Reasoning is not just better prompting — it is a fundamentally different compute paradigm where models allocate variable inference-time compute based on problem difficulty, and the training challenge is teaching *when* and *how much* to think, not just *what* to think."

Cost headline: Reasoning models generate 10-100x more tokens per query; at $15/M output tokens, a single hard math query can cost $0.10-1.00 vs $0.001 for a standard query.

```
Reasoning Approach Selection
─────────────────────────────────────────────
Query difficulty known?
├── YES, Easy → Route to fast model (no reasoning)
├── YES, Hard → Full reasoning model with high budget
└── NO (typical) → Adaptive system
    ├── Start with lightweight reasoning (self-consistency [6])
    ├── If confidence < threshold → Escalate to full reasoning [5]
    └── If still uncertain → PRM-guided tree search [3]
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Reasoning scope and latency budget | Math/code (verifiable) vs open-ended reasoning? Target latency: <2s (distilled) or <30s (full reasoning)? Accuracy target vs cost ceiling. |
| 2. Identify constraints | Compute budget and verification ability | Can you verify answers programmatically (math, code)? GPU memory for long-sequence generation? Budget for 10-100x token generation? |
| 3. Propose baseline | Chain-of-thought prompting + self-consistency | Prompt engineering with few-shot CoT [1]; sample k=5 paths with majority voting [6]. Establishes quality floor without training. |
| 4. Identify gaps | Where prompting fails on hard problems | Measure accuracy by difficulty tier; identify problem classes where CoT prompting plateaus (multi-step algebra, logical chains >5 hops). |
| 5. Introduce improvements | RL-trained reasoning or distillation | If verifiable domain: train with GRPO [4] + PRM [3]. If not: distill from frontier reasoning model. Add adaptive compute allocation [5]. |
| 6. Add evaluation + guardrails | Process verification and reasoning monitoring | PRM scoring per step [3]; detect reasoning loops/degeneracy; set max-token budgets; safety filters on reasoning traces. |
| 7. Discuss scaling tradeoffs | Cost management at production scale | Implement difficulty routing (fast/slow paths); KV-cache optimization for long reasoning; batch reasoning requests; cache common reasoning patterns. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Training approach | GRPO-based RL [4][13] | Distillation from frontier model | Verifiable rewards available; 3+ month timeline | Need deployment in weeks; frontier API accessible |
| Verification | Process Reward Model [3] | Outcome-only verification | Multi-step problems where intermediate errors compound | Simple problems; answer-level verification suffices |
| Inference strategy | Best-of-N with PRM reranking [3] | Single-pass extended thinking [12] | Latency tolerance >10s; accuracy paramount | Streaming UX required; moderate difficulty queries |
| Test-time compute | Fixed budget per query | Adaptive allocation [5] | Uniform difficulty distribution | Mixed difficulty; cost optimization critical |
| Model size | Full-size reasoning (70B+) | Distilled reasoning (7-14B) | Accuracy >95% required; offline batch OK | Real-time serving; cost < $0.01/query |

## System Design Walkthrough

### Opening Frame

Reasoning LLMs fundamentally reframe scaling — instead of only making models bigger (parameter scaling), we make them think longer (inference-time scaling). The non-obvious insight: these two axes are complementary but have different cost curves, and the optimal allocation between them shifts based on problem difficulty [5]. Production systems must implement adaptive compute allocation to avoid spending $1 on a query that a fast model handles for $0.001.

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                  REASONING LLM PRODUCTION SYSTEM                  │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │ Difficulty   │───→│ Reasoning Engine  │───→│ Verification  │  │
│  │ Router       │    │                  │    │ & Output      │  │
│  └──────────────┘    │ Fast path (CoT)  │    └───────────────┘  │
│        │             │ Medium (SC k=8)  │          │            │
│        │             │ Full (tree+PRM)  │          ▼            │
│        ▼             └──────────────────┘    ┌───────────────┐  │
│  ┌──────────────┐            │               │ Response      │  │
│  │ KV-Cache     │◄───────────┘               │ Cache         │  │
│  │ Manager      │                            └───────────────┘  │
│  └──────────────┘                                               │
├──────────────────────────────────────────────────────────────────┤
│  Training Pipeline: Base → Cold-Start SFT → GRPO [4] → Distill │
│  Verifier Pipeline: Step annotations → PRM training [3]         │
└──────────────────────────────────────────────────────────────────┘
```

- **Difficulty Router**: Classifies query complexity to allocate compute budget; simple queries skip reasoning entirely
- **Reasoning Engine**: Implements multiple reasoning strategies (single-pass CoT, self-consistency [6], PRM-guided tree search [3])
- **KV-Cache Manager**: Critical for long reasoning sequences; manages memory pressure from 10-100x longer generations
- **Verification Layer**: PRM [3] scores intermediate steps; outcome verifiers check final answers
- **Training Pipeline**: Multi-stage GRPO [4] training with process reward models for step-level supervision

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Uniform compute spend on all queries | Adaptive difficulty routing [5] | Router accuracy vs wasted compute on misclassified queries |
| KV-cache OOM on long reasoning | Paged attention + speculative eviction | Latency spikes during cache management vs memory savings |
| Reasoning loops/degeneracy | Token budget caps + loop detection | May cut off genuinely complex reasoning vs preventing runaway cost |
| Single reasoning path fragility | Self-consistency voting [6] | k-fold cost increase vs reliability gain |
| Unfaithful reasoning traces | Process reward training [3] | Annotation cost for step-level labels vs reasoning quality |

### Scaling Summary

- **10x scale**: KV-cache becomes primary bottleneck; implement paged attention and prefix sharing for common reasoning patterns; batch requests by difficulty tier
- **100x scale**: Must implement aggressive routing — 80%+ of queries should skip reasoning entirely; distill multiple specialist reasoning models per domain
- **1000x scale**: Reasoning-as-a-service architecture; precompute reasoning for common query clusters; hierarchical caching with semantic deduplication

## Interview Q&A Bank

### Q1: What is chain-of-thought prompting and why does it improve reasoning?

> **Quick answer:** Chain-of-thought prompting [1] elicits step-by-step reasoning by providing exemplars with intermediate steps, improving accuracy on multi-step problems by decomposing them into manageable sub-problems.

Wei et al. [1] demonstrated that simply adding "Let's think step by step" or providing few-shot examples with explicit reasoning steps dramatically improves performance on arithmetic, commonsense, and symbolic reasoning tasks. The mechanism: standard prompting asks the model to jump directly from question to answer, which fails when the answer requires composing multiple reasoning steps. CoT prompting instead decomposes the problem, letting the model solve each step within its capacity.

Key results: CoT improved GSM8K accuracy from 18% to 57% on PaLM 540B [1]. Kojima et al. [10] showed even zero-shot CoT ("Let's think step by step") provides substantial gains without exemplars. The effectiveness scales with model size — below ~100B parameters, CoT often hurts because smaller models generate incoherent intermediate steps.

| Approach | GSM8K (PaLM 540B) | Requires exemplars |
|----------|--------------------|--------------------|
| Standard prompting | 18% | No |
| Zero-shot CoT [10] | 43% | No |
| Few-shot CoT [1] | 57% | Yes (5-8 exemplars) |
| Self-consistency [6] | 74% | Yes + k samples |

**Hard follow-up:** Why does CoT fail on smaller models?

> Smaller models lack the capacity to generate coherent multi-step reasoning. They produce plausible-looking but logically inconsistent steps, and errors compound across the chain. The threshold appears around 60-100B parameters — below this, CoT introduces noise rather than structure.

### Q2: How does self-consistency improve chain-of-thought reasoning?

> **Quick answer:** Self-consistency [6] samples multiple reasoning paths (k=5-40) from the same prompt and takes a majority vote on the final answer, exploiting the insight that correct reasoning paths converge while incorrect paths are diverse.

Wang et al. [6] showed that a single CoT sample is fragile — the model might take a wrong turn at any step. But correct answers tend to be reachable via multiple valid reasoning paths, while incorrect answers are typically reached by unique error patterns. By sampling k diverse paths (using temperature T=0.7-1.0) and voting on final answers, self-consistency provides robust accuracy improvements.

The compute cost scales linearly with k, but accuracy gains follow diminishing returns — going from k=1 to k=5 gives the largest improvement, while k>40 rarely helps. On GSM8K, self-consistency pushed PaLM 540B from 57% (single CoT) to 74% [6]. The method is orthogonal to the base model — it works with any CoT approach as the underlying sampler.

**Hard follow-up:** When does self-consistency fail, and what replaces it?

> Self-consistency fails when the model cannot generate correct paths at all (the problem exceeds its capability) or when incorrect paths converge on the same wrong answer (systematic bias). In these cases, PRM-guided tree search [3] is needed — it actively evaluates and prunes reasoning steps rather than passively voting on outcomes.

### Q3: What are process reward models and how do they differ from outcome reward models?

> **Quick answer:** Process reward models (PRMs) [3] assign reward scores to each intermediate reasoning step, enabling step-level verification and search guidance, whereas outcome reward models (ORMs) only score the final answer.

Lightman et al. [3] demonstrated that PRMs trained on human step-level annotations outperform ORMs for guiding best-of-N selection on math problems. The key advantage: PRMs can identify exactly where reasoning goes wrong, enabling targeted correction. ORMs only know the final answer is wrong — they cannot localize the error.

Training PRMs requires step-level annotations — humans label each step as correct, incorrect, or neutral. This is expensive (Lightman et al. annotated 75K solutions with ~800K step labels [3]), but the resulting verifier is far more powerful for search. At inference, PRMs score each reasoning step as it is generated, enabling beam search over reasoning trees where low-scoring branches are pruned early.

Uesato et al. [14] showed that even imperfect PRMs (trained on noisy step labels) substantially outperform ORMs on problems requiring 5+ reasoning steps. The advantage grows with problem difficulty because ORMs must evaluate entire solution paths holistically, while PRMs factorize evaluation into tractable per-step decisions.

**Hard follow-up:** How do you train a PRM without expensive human step annotations?

> Use Monte Carlo estimation: for each step in a solution, generate N random completions from that point. The step's correctness score is the fraction of completions that reach the correct final answer. This automates step-level labeling using only outcome verification, though it requires significant compute (~100 completions per step).

### Q4: Explain GRPO and why DeepSeek chose it over PPO for reasoning training.

> **Quick answer:** GRPO [4] eliminates PPO's critic network by using group-relative advantage estimation — sampling G completions per prompt and normalizing rewards within each group — reducing memory by ~33% and eliminating critic hyperparameter sensitivity.

For each prompt x, GRPO samples G completions {y_1,...,y_G}, scores them with a reward function R, and computes advantages as:

```
A(x, y_i) = (R(x, y_i) - mean(R(x, y_1..G))) / std(R(x, y_1..G))
```

The policy gradient uses these normalized advantages directly, without a learned value function. DeepSeekMath [4] used G=64 samples per prompt with binary math correctness as reward. DeepSeek-R1 [13] extended this to general reasoning with rule-based rewards (format compliance, correctness).

Why GRPO suits reasoning: (1) Math/code rewards are verifiable, so no learned reward model is needed. (2) The group baseline adapts automatically to problem difficulty — hard problems with low group accuracy still produce useful gradients. (3) Eliminating the critic removes a major source of training instability. DeepSeek reported GRPO converged faster and more reliably than PPO across all reasoning benchmarks [4][13].

**Hard follow-up:** What happens when G is too small or too large?

> G too small (G<4): advantage estimates have high variance, destabilizing training. G too large (G>128): compute cost per update is excessive and marginal variance reduction is minimal (variance scales as 1/G). The sweet spot is G=16-64, balancing compute cost against gradient quality. For sparse-reward tasks, larger G is needed to ensure at least some positive-reward samples per group.

### Q5: How does test-time compute scaling work, and what is the optimal allocation strategy?

> **Quick answer:** Test-time compute scaling [5] allocates more inference-time computation (more tokens, samples, or search steps) to harder problems, achieving better accuracy-per-FLOP than simply using a larger model on all queries.

Snell et al. [5] showed that test-time compute and model size are complementary scaling axes. A smaller model with more test-time compute can match a larger model on hard problems — but the optimal allocation depends on problem difficulty. For easy problems, additional test-time compute is wasted (the model gets it right on the first try). For hard problems, more compute helps up to a ceiling set by the model's fundamental capability.

The practical implication: production systems need difficulty-adaptive routing. Snell et al. found that for a fixed compute budget, the optimal strategy allocates disproportionately to hard problems rather than spreading compute uniformly. This motivates the router-based architecture where a lightweight classifier estimates difficulty and sets the reasoning budget accordingly.

Two mechanisms for spending test-time compute: (1) **Breadth** — sample more independent paths (self-consistency [6], best-of-N + PRM [3]). (2) **Depth** — extend reasoning chains, allowing more sequential steps. Breadth helps when the correct path is reachable but unlikely; depth helps when problems require genuinely longer inference chains.

**Hard follow-up:** How do you build a difficulty classifier for routing without ground-truth difficulty labels?

> Use proxy signals: (1) Self-consistency agreement — sample k=3 quick paths; high disagreement signals difficulty. (2) Perplexity of the initial reasoning steps. (3) Problem length/structural complexity features. Train the router on historical data where difficulty is measured by whether the fast model succeeded.

### Q6: What is the training pipeline for a reasoning model like DeepSeek-R1?

> **Quick answer:** DeepSeek-R1 [13] uses a four-stage pipeline: base pretraining, cold-start SFT on reasoning traces, GRPO-based RL with rule-based rewards, and distillation into smaller models.

The R1 pipeline [13]: (1) **Cold-start SFT**: Fine-tune the base model on thousands of curated reasoning traces to establish the format (thinking tags, step-by-step structure). Without this, RL exploration produces incoherent outputs. (2) **GRPO RL training**: The main reasoning capability emerges here. The model generates multiple solutions per problem, receives binary correctness rewards plus format rewards, and updates via group-relative policy optimization [4]. (3) **Rejection sampling SFT**: After RL, sample many solutions from the trained model, filter for correct+high-quality traces, and do another SFT pass to stabilize. (4) **Distillation**: Transfer reasoning capability to smaller models (1.5B-70B) via SFT on R1's reasoning traces.

A critical finding [13]: pure RL from the base model (skipping cold-start SFT) eventually works but takes 3-4x longer and produces less stable training. The cold-start SFT phase teaches reasoning structure; RL teaches reasoning capability. STaR [7] established this principle earlier — bootstrap reasoning by training on correct self-generated rationales.

**Hard follow-up:** Why does DeepSeek-R1 use rule-based rewards instead of a learned reward model?

> Learned reward models can be gamed (reward hacking), especially during extended RL training. Rule-based rewards (math correctness checker, code test execution, format validation) are unhackable — they measure ground truth directly. This is only possible for verifiable domains; for open-ended reasoning, learned rewards remain necessary.

### Q7: How do you serve a reasoning model in production with acceptable latency?

> **Quick answer:** Streaming the chain-of-thought to users, implementing KV-cache optimization for long sequences, setting token budgets, and routing easy queries to fast models are the primary production strategies.

Reasoning models generate 10-100x more tokens than standard models. A 2000-token reasoning chain at 50 tokens/second takes 40 seconds — unacceptable for interactive applications without streaming. Production mitigations:

**Streaming**: Show reasoning tokens as they are generated (Claude Extended Thinking [12] approach). Users see the model "working" rather than waiting for a blank response. Hide or summarize the reasoning chain based on UX requirements.

**KV-cache management**: Long reasoning sequences create massive KV-cache pressure. For a 70B model with 128 layers and 2048-token reasoning chain, KV-cache alone requires ~40GB per concurrent request. Solutions: paged attention (vLLM), prefix caching for shared prompt prefixes, and aggressive eviction of completed reasoning tokens.

**Budget caps**: Set maximum reasoning tokens (e.g., 4096) to bound worst-case latency and cost. Monitor for truncation-induced accuracy drops.

**Difficulty routing**: Route 70-80% of queries to a fast non-reasoning model; only escalate to the reasoning model for genuinely difficult queries.

**Hard follow-up:** How do you handle the "thinking too long" failure mode where the model generates thousands of reasoning tokens without converging?

> Implement early stopping heuristics: (1) detect repetition loops (n-gram overlap >60% over sliding window), (2) monitor PRM scores — if step scores stop improving for N steps, force conclusion, (3) set hard token limits with graceful degradation (output best partial answer).

### Q8: How do you evaluate reasoning model quality beyond final-answer accuracy?

> **Quick answer:** Evaluate reasoning process quality (step correctness, logical coherence, efficiency) alongside outcome accuracy, using PRMs [3], human annotation of traces, and behavioral metrics like reasoning length distribution.

Final-answer accuracy misses critical failure modes: a model might get the right answer via wrong reasoning (lucky cancellation of errors), or generate correct reasoning but make an arithmetic slip at the final step. Process evaluation catches these.

| Eval Dimension | Metric | Method |
|---------------|--------|--------|
| Step correctness | PRM score per step [3] | Automated PRM evaluation |
| Logical coherence | Human rating (1-5) on trace quality | Expert annotation, N=200 |
| Reasoning efficiency | Tokens per correct solution | Automated compute tracking |
| Error localization | Position of first error in trace | PRM step-level scoring |
| Diversity | Distinct reasoning strategies per problem | Clustering on solution paths |
| Faithfulness | Correlation between trace and model internals | Probing / intervention studies |

Benchmark concerns: GSM8K [8] is nearly saturated (>95%) and likely contaminated in training sets. MATH [9] is harder but approaching 90% for frontier models. The field needs harder benchmarks (GPQA, ARC-AGI, FrontierMath) to differentiate reasoning capabilities.

**Hard follow-up:** How do you detect if your model has memorized benchmark solutions rather than genuinely reasoning?

> (1) Test on novel problems with identical structure but different numbers/names. (2) Introduce controlled perturbations to benchmark problems and check if accuracy drops disproportionately. (3) Evaluate on held-out benchmarks never seen during training. (4) Analyze reasoning traces for signs of pattern matching vs genuine step derivation.

### Q9: When should you NOT use a reasoning model?

> **Quick answer:** Skip reasoning for factual retrieval, simple classification, creative generation, and any task where a standard model achieves >95% accuracy — reasoning adds 10-100x cost with minimal quality gain for easy tasks.

The cost-quality curve for reasoning is highly non-linear. On easy tasks, reasoning adds tokens (cost) without improving accuracy. On moderate tasks, a small reasoning budget helps. On hard tasks, extensive reasoning is essential. The production mistake is applying reasoning uniformly.

Tasks where reasoning hurts ROI: (1) Information retrieval / factual QA — the model knows or doesn't know; thinking longer won't help. (2) Simple classification (sentiment, topic) — single forward pass suffices. (3) Creative writing — CoT can make outputs mechanical. (4) High-throughput batch tasks where latency matters more than marginal accuracy.

The routing decision should use expected value: `EV(reasoning) = P(reasoning_correct) * value - cost`. If `P(fast_correct) > 0.95`, reasoning's marginal value rarely justifies 10-100x cost. Build a lightweight difficulty estimator and route accordingly [5].

**Hard follow-up:** How do you quantify the cost-accuracy tradeoff to set your routing threshold?

> Run the reasoning model on a sample of production traffic. Plot accuracy gain vs cost for each difficulty tier. Set the routing threshold where marginal accuracy gain per dollar drops below your business value threshold (e.g., if each correct answer is worth $0.50, route to reasoning only when the expected accuracy gain exceeds cost/0.50).

### Q10: How does DeepSeek-R1's training differ from OpenAI's o1?

> **Quick answer:** Both use RL to train reasoning, but R1 [13] uses GRPO with rule-based rewards on an open-weight model, while o1 [11] likely uses PPO/variant with learned reward models. R1's approach is more reproducible; o1's is more general.

Key architectural differences (based on published information):

| Aspect | DeepSeek-R1 [13] | OpenAI o1 [11] |
|--------|-------------------|----------------|
| RL algorithm | GRPO [4] | Likely PPO variant |
| Reward signal | Rule-based (correctness + format) | Learned reward model |
| Base model | DeepSeek-V3 (671B MoE) | GPT-4 family |
| Open weights | Yes | No |
| Cold-start SFT | Explicit stage | Undisclosed |
| Distillation | Published recipe (1.5B-70B) | Not published |

R1 demonstrated that RL-trained reasoning can emerge from relatively simple rewards (binary correctness) without sophisticated reward modeling [13]. This was surprising — the field expected learned reward models were essential. The implication: for verifiable domains, GRPO + rule-based rewards is the practical choice.

**Hard follow-up:** Could you reproduce o1-level reasoning on open-source infrastructure today?

> Partially. R1 shows the core approach works. Gaps: (1) o1 likely has better training data curation. (2) Multi-domain reasoning (beyond math/code) requires learned rewards which are harder to engineer. (3) Safety training for reasoning traces adds complexity not in R1's report. With current open tooling (DeepSpeed, vLLM, R1 recipe), you can reproduce math/code reasoning but general reasoning remains harder.

### Q11: What is STaR and how does it bootstrap reasoning capability?

> **Quick answer:** STaR (Self-Taught Reasoner) [7] iteratively improves reasoning by training on the model's own correct reasoning traces — generating rationales, filtering for correct answers, and fine-tuning on the successful traces.

Zelikman et al. [7] proposed a self-improvement loop: (1) Prompt the model to generate rationales for training problems. (2) Keep only rationales that lead to correct answers. (3) Fine-tune the model on these correct rationales. (4) Repeat. Each iteration, the model can solve more problems correctly, generating more training data for the next round.

The key insight is "rationalization": for problems the model gets wrong, provide the correct answer and ask it to generate a rationale *given* the answer. This produces training signal even from initially-failed problems, preventing the dataset from shrinking across iterations.

STaR bridges prompting and RL — it improves reasoning without explicit reward models or policy gradients, using only SFT on self-generated data. It is a precursor to more sophisticated approaches like R1's pipeline, establishing that reasoning can be bootstrapped from a model's own generations filtered by correctness.

**Hard follow-up:** What prevents STaR from converging to a local optimum where the model only solves easy problems?

> Rationalization is the key mechanism — by providing answers for hard problems and training on those rationales, STaR injects signal from problems the model cannot yet solve independently. Without rationalization, the method degenerates to self-consistency amplification on easy problems only.

### Q12: How do you implement adaptive test-time compute allocation in production?

> **Quick answer:** Use a lightweight difficulty classifier to route queries to appropriate reasoning tiers (no reasoning / light CoT / full tree search), with feedback loops that calibrate routing thresholds based on observed accuracy and cost.

Production implementation requires three components:

**Difficulty classifier**: A small model (or even the first few tokens of reasoning) predicts problem difficulty. Train on historical data: (query, fast_model_correct, reasoning_model_correct). Features: query length, presence of multi-step indicators, domain signals. Target: marginal accuracy gain from reasoning.

**Reasoning tiers**: (1) No reasoning — direct generation for trivial queries. (2) Light reasoning — single CoT pass with 256-512 token budget. (3) Medium — self-consistency with k=8 [6]. (4) Heavy — PRM-guided tree search with 4096+ token budget [3][5].

**Calibration loop**: Monitor per-tier accuracy weekly. If the "no reasoning" tier shows accuracy drops, the difficulty threshold is too aggressive — lower it. If the "heavy" tier rarely outperforms "medium," raise the escalation threshold to save cost.

```
Monthly cost optimization (1M queries):
  80% no-reasoning ($0.001/q) = $800
  15% light ($0.01/q)        = $1,500
  4% medium ($0.05/q)        = $2,000
  1% heavy ($0.50/q)         = $5,000
  Total: $9,300 vs $500,000 if all queries used heavy reasoning
```

**Hard follow-up:** How do you handle queries where the difficulty classifier is wrong — a query classified as "easy" that the fast model gets wrong?

> Implement a verification layer on fast-model outputs: run a lightweight confidence check (output probability, self-consistency with k=2). If confidence is below threshold, automatically escalate to the next reasoning tier. This "verify-then-escalate" pattern catches misclassified hard queries with minimal additional cost.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): Test-Time Compute Scaling — Optimal Allocation Between Search Breadth and Depth</strong></summary>

Snell et al. [5] formalize the test-time compute scaling problem: given a fixed inference-time FLOP budget C, how should it be allocated between parallel samples (breadth N) and sequential reasoning length (depth L)?

**Formal framework**: Let accuracy A(N, L) be the probability of producing a correct answer given N independent samples each of length L tokens. The compute cost is proportional to N * L. The optimization problem:

```
max A(N, L)  subject to  N * L <= C
```

For self-consistency [6] with majority voting:
```
A(N, L) = P(majority correct) = sum_{k=ceil(N/2)}^{N} C(N,k) * p(L)^k * (1-p(L))^(N-k)
```

where p(L) is single-sample accuracy at depth L. The key insight: p(L) is concave in L (diminishing returns from longer reasoning), while majority-vote accuracy is convex in N (sharp phase transition around p > 0.5).

**Optimal allocation depends on p(L)**:
- If p(L) > 0.5 (model can solve it): allocate to breadth (more samples, majority vote). Accuracy improves exponentially with N when p > 0.5.
- If p(L) < 0.5 (model struggles): allocate to depth (longer reasoning chains). Need to push p(L) above 0.5 before breadth helps.
- If p(L) << 0.5 regardless of L (beyond capability): no allocation helps — escalate to a larger model.

**Empirical findings** [5]: On MATH [9] problems, easy problems (difficulty 1-2) have p(L) > 0.8 even at minimal depth — breadth (N=16, L=256) dominates. Hard problems (difficulty 5) have p(L) < 0.3 at L=256 but p(L) = 0.6 at L=2048 — depth first, then breadth. This motivates adaptive allocation.

**PRM-guided search** [3] changes the picture fundamentally. Instead of independent samples, PRM enables tree search where branches are pruned based on step-level scores. This achieves accuracy between breadth-only and depth-only at lower total compute by avoiding wasting tokens on unpromising paths. The effective sample efficiency of PRM-guided search is 3-5x higher than naive self-consistency.

**Production implication**: The optimal strategy is a two-phase protocol — (1) estimate p(L) with a quick probe (k=3 samples at moderate depth), (2) allocate remaining budget to breadth if p > 0.5, depth if p < 0.5, and give up (use cached answer or escalate) if p << 0.2.

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): Serving Reasoning Models — Streaming Long CoT, KV-Cache Pressure, and Latency Management</strong></summary>

Reasoning models generate 10-100x more tokens than standard models, creating unique serving infrastructure challenges not present in traditional LLM deployment.

**KV-cache pressure analysis**: For a transformer with H heads, D head dimension, and L layers, KV-cache per token = 2 * H * D * L * sizeof(dtype). For a 70B model (80 layers, 64 heads, 128 dim, fp16):

```
KV per token = 2 * 64 * 128 * 80 * 2 bytes = 2.62 MB/token
2048-token reasoning chain = 5.4 GB KV-cache per request
At 100 concurrent reasoning requests = 540 GB KV-cache alone
```

This exceeds available GPU memory on even 8xH100 nodes (640GB total, minus model weights of ~140GB). Solutions:

**Paged Attention (vLLM)**: Allocates KV-cache in non-contiguous pages, enabling dynamic memory sharing between requests. Critical for reasoning models where generation length is highly variable (some queries reason for 200 tokens, others for 8000).

**Prefix caching**: Reasoning requests sharing the same system prompt and few-shot examples can share KV-cache for the common prefix. For a 500-token prefix shared across 100 requests, this saves 500 * 2.62MB * 99 = ~130GB.

**Speculative eviction**: For reasoning tokens that have been "consumed" (the model has moved past them), evict KV-cache entries and recompute on-demand if attention revisits them. In practice, reasoning models exhibit strong locality — recent reasoning steps attend mostly to the last 256-512 tokens, making eviction of earlier reasoning tokens low-cost.

**Streaming architecture for long CoT** [12]:
```
Client ←─ SSE stream ─── Gateway ←── Inference Engine
                                      │
                         Token buffer (batches of 4-8 tokens)
                         Reasoning visibility control:
                           - Full: stream all thinking tokens
                           - Summary: stream every 10th token + final
                           - Hidden: buffer internally, stream only answer
```

**Latency management**: Time-to-first-token (TTFT) is standard; the critical metric for reasoning models is time-to-first-answer-token (TTFAT) — how long until the useful response begins. For a 2000-token reasoning chain at 50 tok/s, TTFAT = 40s. Mitigations: (1) parallel prefill for reasoning prefix, (2) speculative decoding for reasoning tokens (draft model predicts reasoning steps), (3) early exit when PRM confidence exceeds threshold.

</details>

<details><summary><strong>DE Probe 3 (DATA): Training Reasoning — Process Reward Models, Step-Level Supervision, and Synthetic Rationale Generation</strong></summary>

The data challenge in reasoning training: outcome labels (correct/incorrect) are cheap but provide sparse signal; step-level labels are rich but expensive. The field has developed multiple approaches to bridge this gap.

**Process reward model training** [3][14]: Lightman et al. [3] annotated 75K math solutions with per-step correctness labels (~800K step labels total). The PRM architecture adds a scalar head after each step token, trained with binary cross-entropy on step correctness. Training requires careful definition of "step boundaries" — typically sentence-ending punctuation or explicit markers like "\n\n".

Uesato et al. [14] compared process-based and outcome-based feedback, finding:
```
PRM advantage = f(reasoning_length)
  - 1-3 steps: ORM matches PRM (errors don't compound)
  - 4-7 steps: PRM +8-12% accuracy (error localization helps)
  - 8+ steps: PRM +15-25% accuracy (ORM cannot identify where errors begin)
```

**Monte Carlo PRM estimation** (avoiding human annotation): For each step s_i in solution S:
1. Generate N completions from step s_i onward (random policy)
2. Step score = fraction of completions reaching correct final answer
3. Train PRM to predict this score per step

This converts outcome verification (cheap) into step-level signal (expensive) at the cost of O(steps * N) generations per training example. Typical settings: N=32-100 completions per step.

**Synthetic rationale generation** for cold-start SFT [7][13]:
- **Distillation from frontier models**: Prompt GPT-4/R1 with problems, extract reasoning traces. Filter for correctness. Cost: ~$0.05/trace.
- **STaR bootstrapping** [7]: Generate rationales from current model, keep correct ones, fine-tune, repeat. Free but limited by model's current capability.
- **Rejection sampling from RL-trained model** [13]: After GRPO training, sample many solutions, keep correct ones with high PRM scores. Produces high-quality training data for subsequent SFT passes or distillation.

**Quality filtering for reasoning traces**: Not all correct solutions are good training data. Filter criteria: (1) Correctness (necessary). (2) Reasoning coherence (PRM score > 0.8 at all steps). (3) Minimal length (prefer concise correct reasoning). (4) Diversity (deduplicate near-identical reasoning strategies). (5) No shortcutting (solutions must show genuine reasoning, not pattern matching).

Havrilla et al. [15] showed that the choice between process and outcome supervision interacts with the RL algorithm — PPO benefits more from process rewards while simpler algorithms like expert iteration work well with outcome rewards alone.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Reasoning Benchmarks — GSM8K, MATH, ARC Saturation and Contamination Concerns</strong></summary>

The reasoning evaluation landscape faces a crisis of benchmark saturation and contamination as frontier models approach ceiling performance.

**Benchmark progression and saturation**:

| Benchmark | Release | Initial SOTA | Current SOTA | Saturated? |
|-----------|---------|-------------|--------------|------------|
| GSM8K [8] | 2021 | 35% (GPT-3 + verifier) | 97.3% (R1) | Yes |
| MATH [9] | 2021 | 6.9% (GPT-3) | 96.4% (o3) | Nearly |
| ARC-Challenge | 2018 | 25% | 95%+ | Yes |
| GPQA Diamond | 2023 | 34% (GPT-4) | ~65% | No |
| ARC-AGI | 2024 | 0% (GPT-4) | 87.5% (o3 high) | No |

**Contamination concerns**: GSM8K's 8,500 test problems have been widely reproduced in web crawls and likely appear in pretraining data for many models. Evidence: (1) Models solve GSM8K problems with unusual speed (fewer reasoning tokens than comparably-difficult novel problems). (2) Performance drops significantly on rephrased versions of GSM8K problems with identical mathematical structure but different surface forms. (3) Simple perturbations (changing names, numbers) cause disproportionate accuracy drops on suspected-contaminated models.

Cobbe et al. [8] originally paired GSM8K with a verifier to detect incorrect solutions. Today the benchmark primarily measures whether models have seen similar problems during training rather than genuine mathematical reasoning.

**MATH benchmark** [9] remains partially useful because: (1) problems span difficulty levels 1-5 with hard problems still challenging, (2) the answer format (boxed LaTeX) makes contamination easier to detect via exact-match memorization, (3) level-5 problems still separate models meaningfully (50-70% accuracy range).

**Evaluation best practices for reasoning in 2025**:
1. **Use held-out variants**: Generate novel problems with the same mathematical structure but different surface form
2. **Track performance by difficulty tier**: Aggregate scores hide that models saturate easy problems while hard ones still differentiate
3. **Include process evaluation**: Use PRMs [3] to score reasoning quality, not just final-answer accuracy
4. **Test for robustness**: Perturbed versions, adversarial rephrasing, irrelevant information injection
5. **Use dynamic benchmarks**: Problems generated after model training cutoff (FrontierMath, recent competition problems)

Hendrycks et al. [9] designed MATH specifically to be resistant to saturation (problems from mathematical competitions requiring genuine multi-step reasoning), yet even this benchmark is approaching ceiling for frontier reasoning models, demonstrating the rapid pace of capability improvement.

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): When NOT to Reason — Cost/Latency Trade-offs and Routing Between Fast and Reasoning Models</strong></summary>

The most expensive mistake in production reasoning systems is applying reasoning uniformly. The expected value framework:

```
EV(reasoning) = [P(reason_correct) - P(fast_correct)] * Value(correct) - Cost(reasoning)
Route to reasoning iff EV(reasoning) > 0
```

**Cost structure** (typical pricing, 2025):
- Fast model (e.g., Claude Haiku, GPT-4o-mini): ~$0.25/M input, $1.00/M output
- Reasoning model (e.g., o1, Claude with thinking): ~$15/M input, $60/M output + 10-100x more output tokens
- Per-query cost ratio: reasoning is 100-1000x more expensive

**Difficulty-stratified analysis** (empirical, on a math QA workload):

| Difficulty | Fast model accuracy | Reasoning accuracy | Gain | Reasoning cost | Recommend |
|-----------|--------------------|--------------------|------|----------------|-----------|
| Trivial (60% of queries) | 98% | 99% | +1% | $0.05 | Fast |
| Moderate (25%) | 75% | 92% | +17% | $0.15 | Reasoning if value > $0.88 |
| Hard (12%) | 30% | 78% | +48% | $0.50 | Reasoning |
| Extreme (3%) | 5% | 45% | +40% | $1.00 | Reasoning + human review |

**Router architecture**: A production routing system needs:
1. **Feature extraction**: Query embeddings, structural complexity (number of sub-questions, domain), historical accuracy at similar queries
2. **Difficulty prediction**: Regression model predicting P(fast_correct) and P(reason_correct)
3. **Value-aware routing**: Different queries have different business value; route based on expected value, not just difficulty
4. **Feedback loop**: Log routing decisions and outcomes; retrain router weekly

**Latency trade-off**: Beyond cost, reasoning adds 5-40s of latency. For real-time applications (autocomplete, ad ranking, recommendations), this is unacceptable regardless of accuracy benefit. The routing decision must consider latency SLAs:

```python
def should_reason(query, latency_sla_ms, value_per_correct):
    difficulty = estimate_difficulty(query)
    fast_p = predict_accuracy(query, model='fast')
    reason_p = predict_accuracy(query, model='reasoning')
    reason_cost = estimate_cost(query, model='reasoning')
    reason_latency = estimate_latency(query, model='reasoning')
    
    if reason_latency > latency_sla_ms:
        return False  # Hard latency constraint
    expected_gain = (reason_p - fast_p) * value_per_correct
    return expected_gain > reason_cost
```

**Anti-pattern**: Reasoning on retrieval-augmented queries where the answer is in the context. Models with extended thinking will "reason" about information that's directly stated, wasting tokens. Add a "direct extraction" path for RAG queries with high-confidence context matches.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): GRPO and Group-Relative Optimization — Variance Reduction Without Critic Networks</strong></summary>

GRPO [4] represents a fundamental simplification of policy optimization for reasoning. The mathematical foundation explains why eliminating the critic network improves both efficiency and stability.

**GRPO objective** (from DeepSeekMath [4]):
```
L_GRPO = -E_x [1/G * sum_i (min(r_i * A_i, clip(r_i, 1-e, 1+e) * A_i)) - beta * KL(pi_theta || pi_ref)]

where:
  r_i = pi_theta(y_i|x) / pi_old(y_i|x)  (importance ratio)
  A_i = (R(x,y_i) - mu_G) / sigma_G       (group-normalized advantage)
  mu_G = (1/G) * sum_j R(x,y_j)           (group mean reward)
  sigma_G = std({R(x,y_j)}_j)             (group std reward)
```

**Variance reduction analysis**: In standard policy gradient with baseline b:
```
Var[grad] = E[(R - b)^2 * ||grad log pi||^2]
Optimal baseline: b* = E[R * ||grad log pi||^2] / E[||grad log pi||^2]
```

PPO approximates b* with a critic V(s), which introduces:
- **Approximation error**: V_theta is never perfect; error = E[(V_theta(s) - V*(s))^2]
- **Training lag**: Critic updates lag behind policy, creating stale baselines
- **Hyperparameter coupling**: Critic LR, value loss coefficient, GAE lambda all interact

GRPO's group mean mu_G is an unbiased estimator of E[R|x] with variance sigma^2_R / G. Unlike the critic, it:
- Has no approximation error (it's a sample mean, not a function approximation)
- Is always current (computed from the current policy's generations)
- Requires no additional hyperparameters (only G, which is robust in range 16-64)

**Why group normalization (dividing by sigma_G) matters**: Without normalization, prompts with high-variance rewards dominate the gradient. A math problem with solutions scoring {0, 0, 0, 0, 1, 0, 0, 0} (one correct out of G=8) would have mean=0.125, and the correct solution's advantage = 0.875. But a creative writing prompt with scores {3.2, 3.5, 3.1, 3.8, ...} would have larger absolute advantages despite being less informative. Dividing by sigma_G equalizes contribution across prompts, regardless of reward scale.

**Comparison of memory footprint** (67B model, G=64):
```
PPO:  Policy (134GB) + Critic (134GB) + Optim_policy (268GB) + Optim_critic (268GB) = 804GB
GRPO: Policy (134GB) + Optim_policy (268GB) + G fwd passes (reusable buffer) = 402GB + buffer
Memory savings: ~50% (enables larger models on same hardware)
```

**When GRPO fails**: (1) Unverifiable rewards — when rewards come from a noisy learned RM, group normalization amplifies noise. (2) Extremely sparse rewards — if G=64 and only 1% of solutions are correct, most groups have zero positive examples, producing degenerate gradients. (3) Multi-objective settings — group normalization treats all reward dimensions equally, preventing Pareto-optimal solutions. In these cases, PPO's critic can learn a more nuanced value function that accounts for reward structure.

DeepSeek-R1 [13] scaled GRPO to 671B parameters with G=64, demonstrating that the approach works at frontier scale. The key implementation detail: generate all G completions in a single batched forward pass (parallelized across GPUs), then compute advantages and update the policy. This achieves near-linear scaling efficiency.

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Query Usage | Cost/Query |
|-----------|-----------|----------------|------------|
| Reasoning tokens (generation) | $60/M tokens | 2000 tokens avg | $0.12 |
| Input tokens (prompt + context) | $15/M tokens | 500 tokens | $0.0075 |
| PRM verification (per step) | $0.001/step | 15 steps | $0.015 |
| KV-cache memory (GPU-hrs) | $3/GPU-hr | 0.001 GPU-hr | $0.003 |
| Difficulty routing (classifier) | $0.25/M tokens | 500 tokens | $0.000125 |

### Monthly Cost at Scale

| Scale | Reasoning Compute | Fast Model Compute | Router | Total/month |
|-------|------------------|--------------------|--------|-------------|
| 10K queries/day | $18K (30% reasoning) | $300 | $50 | ~$18K |
| 100K queries/day | $108K (20% reasoning) | $3K | $500 | ~$112K |
| 1M queries/day | $540K (10% reasoning) | $30K | $5K | ~$575K |

### Cost Optimization Priority Stack

| Priority | Optimization | Estimated Savings |
|----------|-------------|-------------------|
| 1 | Difficulty-based routing (skip reasoning for easy queries) [5] | 60-80% total cost |
| 2 | Distilled reasoning model (7B instead of 70B) for medium queries | 70-90% per-query |
| 3 | Response caching for repeated/similar reasoning queries | 20-40% at scale |
| 4 | Token budget caps (truncate reasoning at diminishing returns) | 15-30% per-query |
| 5 | KV-cache sharing (prefix caching, paged attention) | 20-30% memory/compute |
| 6 | Batch reasoning requests (offline) vs real-time | 40-60% throughput gain |

### Build vs Buy

| Capability | Build Cost (annual) | Buy Option | Recommendation |
|-----------|-------------------|------------|----------------|
| Reasoning model training (GRPO) | $2M+ (compute + eng) | OpenAI o1 / Claude thinking API | Buy unless reasoning is core IP |
| PRM training [3] | $500K (annotations + compute) | No turnkey option | Build if quality is critical |
| Difficulty router | $100K eng | Simple heuristics first | Build incrementally from heuristics |
| Serving infrastructure (long CoT) | $300K eng | Fireworks, Together AI | Buy for speed; build at scale |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Reasoning tokens/query (p95) | >5000 tokens (runaway reasoning) | Auto-truncate + alert on-call |
| Time-to-first-answer-token | >30s (p95) | Page on-call; check for reasoning loops |
| KV-cache utilization | >85% GPU memory | Scale serving nodes; enable eviction |
| Reasoning loop detection | >60% n-gram overlap in 256-token window | Force early conclusion |
| PRM step score (mean) | <0.5 (reasoning quality degradation) | Investigate model regression |
| Router accuracy (predicted vs actual difficulty) | <70% agreement | Retrain router; review feature drift |
| Cost per correct answer | >2x baseline | Review routing thresholds |

### Debugging Walkthrough

```
Symptom: Accuracy dropped on hard math problems
├── Check 1: Is the reasoning model generating shorter traces?
│   └── Mean reasoning tokens dropped >30% → Model regression → Rollback checkpoint
├── Check 2: Is the router sending hard queries to fast model?
│   └── Router difficulty threshold shifted → Recalibrate on fresh data
├── Check 3: Are PRM scores still predictive?
│   └── PRM-accuracy correlation dropped → PRM drift → Retrain PRM
└── Check 4: Is the problem distribution shifting?
    └── New problem types not seen in training → Collect data, retrain

Symptom: Inference costs spiked 3x
├── Check 1: Reasoning token distribution shifted?
│   └── p95 length doubled → Check for reasoning loops → Add loop detection
├── Check 2: Router sending more queries to reasoning tier?
│   └── Traffic distribution changed → Recalibrate difficulty thresholds
└── Check 3: KV-cache thrashing causing recomputation?
    └── Cache eviction rate >50% → Increase memory allocation or reduce concurrency
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| Reasoning model checkpoint | Swap served model (blue/green) | 5 min (traffic drain + swap) |
| PRM checkpoint [3] | Hot-swap verifier; disable tree search if broken | Minutes (affects accuracy, not availability) |
| Routing thresholds | Config change, instant rollback | Seconds; affects cost/accuracy tradeoff |
| Token budget caps | Config change | Seconds; may truncate complex reasoning |
| Training data (GRPO trajectories) | Git-tagged datasets; full retrain required | Days (requires retraining) |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Final answer correctness (verifiable domains) | Gold standard reward signal | Automated checkers (math, code tests) |
| User edits to reasoning output | Shows reasoning gaps | Diff analysis on edited responses |
| Reasoning chain abandonment (user interrupts) | Reasoning too slow or wrong | Session analytics (interrupt events) |
| PRM step scores on production traffic | Reasoning quality distribution | Automated PRM inference on samples |
| Router accuracy (did reasoning help?) | Routing calibration signal | Compare fast vs reasoning on same query |
| Difficulty estimation vs actual outcome | Router training data | Log predictions and outcomes |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Daily | Routing threshold calibration from fresh outcomes | Automated; cost stays within 10% of target |
| Weekly | PRM evaluation on production reasoning samples | PRM-accuracy correlation >0.7 |
| Bi-weekly | Synthetic reasoning data generation (STaR-style [7]) | New data improves held-out accuracy >1% |
| Monthly | GRPO fine-tuning on accumulated correct trajectories | Win-rate >55% vs current model on hard problems |
| Quarterly | Full reasoning model retraining with updated curriculum | Major capability gap on new problem classes |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Self-consistency voting [6] | Single-path fragility | Any CoT task with verifiable answers | When p(correct) < 0.3 (voting won't help) |
| PRM-guided tree search [3] | Wasted compute on wrong paths | Hard multi-step problems; latency budget >10s | Simple problems; real-time requirements |
| Adaptive compute allocation [5] | Uniform overspend on easy queries | Mixed-difficulty production traffic | Uniform-difficulty batch processing |
| STaR self-improvement [7] | Limited reasoning training data | Bootstrap reasoning without human annotation | When model is too weak to generate any correct traces |
| Distilled reasoning [13] | Full model too expensive to serve | High-throughput applications | When accuracy on hardest problems is critical |
| Speculative decoding for CoT | Slow reasoning token generation | Long reasoning chains with predictable patterns | Highly diverse/unpredictable reasoning |
| Reasoning caching | Repeated similar queries | FAQ-style workloads, shared problem structures | Novel/unique queries |
| Budget forcing (early exit) | Runaway reasoning cost | Latency-constrained serving | When reasoning must complete for correctness |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|----------------|----------------------|
| "We should add chain-of-thought to improve accuracy" | "CoT only helps above ~100B params [1]; for our 7B model, we need distilled reasoning traces, not prompting" |
| "Let's use the reasoning model for all queries" | "80% of queries don't benefit from reasoning — the router saves us $400K/month by sending easy queries to the fast model [5]" |
| "More samples in self-consistency is always better" | "Returns diminish sharply past k=16; the compute is better spent on PRM-guided search which eliminates wrong paths early [3][6]" |
| "We need human annotations for step-level training" | "Monte Carlo PRM estimation gives us step labels from outcome verification alone — 100x cheaper than human annotation [3][14]" |
| "Our model scores 97% on GSM8K" | "GSM8K is saturated and likely contaminated; show me GPQA or held-out competition problems with perturbation robustness [8][9]" |
| "GRPO is just PPO without the critic" | "GRPO's group normalization automatically adapts to per-prompt difficulty and eliminates the critic's moving-target problem [4][13]" |
| "Reasoning models are too expensive for production" | "With adaptive routing, only 10-20% of queries hit the reasoning model; blended cost is 3-5x base, not 100x" |

## References

### Foundational Papers

- [1] Wei et al. (2022) — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* — arXiv:2201.11903 — Established that few-shot prompting with intermediate steps dramatically improves reasoning in large models.
- [2] Yao et al. (2023) — *Tree of Thoughts: Deliberate Problem Solving with Large Language Models* — arXiv:2305.10601 — Generalized CoT to tree-structured exploration with backtracking and search algorithms.
- [6] Wang et al. (2023) — *Self-Consistency Improves Chain of Thought Reasoning in Language Models* — arXiv:2203.11171 — Showed majority voting over multiple CoT paths provides robust accuracy gains.
- [7] Zelikman et al. (2022) — *STaR: Bootstrapping Reasoning With Reasoning* — arXiv:2203.14465 — Introduced iterative self-improvement via training on self-generated correct rationales.
- [10] Kojima et al. (2022) — *Large Language Models are Zero-Shot Reasoners* — arXiv:2205.11916 — Demonstrated zero-shot CoT ("Let's think step by step") provides reasoning gains without exemplars.

### Training & Optimization

- [3] Lightman et al. (2023) — *Let's Verify Step by Step* — arXiv:2305.20050 — Demonstrated process reward models outperform outcome reward models for multi-step math reasoning.
- [4] Shao et al. (2024) — *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models* — arXiv:2402.03300 — Introduced GRPO; group-relative advantage estimation without critic network.
- [13] DeepSeek (2025) — *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning* — arXiv:2501.12948 — Full technical report on RL-trained reasoning matching o1-level performance.
- [14] Uesato et al. (2022) — *Solving math word problems with process- and outcome-based feedback* — arXiv:2211.14275 — Compared process vs outcome supervision; showed process feedback superior for multi-step reasoning.
- [15] Havrilla et al. (2024) — *Teaching Large Language Models to Reason with Reinforcement Learning* — arXiv:2403.04642 — Systematic comparison of RL algorithms for reasoning training; analyzed interaction between reward type and algorithm choice.

### Production & Systems

- [5] Snell et al. (2024) — *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters Alone* — arXiv:2408.03314 — Formalized test-time compute allocation; showed adaptive budget outperforms uniform allocation.
- [11] OpenAI (2024) — *Learning to Reason with LLMs* — OpenAI blog — Introduced o1 reasoning model; demonstrated RL-trained reasoning achieving breakthrough performance on math/science.
- [12] Anthropic (2024) — *Claude's Extended Thinking* — Anthropic documentation — Production implementation of streaming reasoning with user-visible thinking tokens.

### Evaluation & Benchmarks

- [8] Cobbe et al. (2021) — *Training Verifiers to Solve Math Word Problems* — arXiv:2110.14168 — Introduced GSM8K benchmark and verifier-based approach to math reasoning.
- [9] Hendrycks et al. (2021) — *Measuring Mathematical Problem Solving with the MATH Dataset* — arXiv:2103.03874 — Competition-level math benchmark spanning difficulty levels 1-5; designed to resist quick saturation.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; fixed duplicate DE probes (v1 had 5 identical GRPO probes), added 6 diverse sub-topics per constraint, enforced length limits, added citations |
