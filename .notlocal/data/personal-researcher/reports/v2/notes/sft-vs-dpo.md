# SFT vs DPO (Supervised Fine-Tuning vs Direct Preference Optimization)

> **Last Updated:** 2026-05-31 | **Read time:** ~25 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** LLM alignment has evolved from the 3-stage RLHF pipeline (SFT → Reward Model → PPO) to direct alignment methods like DPO that eliminate the reward model entirely [2].
> Key players: DPO [2], GRPO [11], KTO [9], IPO [10]. Main open problem: scaling preference optimization beyond single-turn without reward hacking.
> Recent breakthrough: GRPO (Jan 2024) achieves RLHF-competitive results with group-relative scoring and no critic network [11]. Trend: hybrid SFT+DPO pipelines dominate production.

## State of the Art

### Current Best Approaches

- **SFT + DPO pipeline** — Fine-tune on demonstrations first, then refine with pairwise preferences; used by Llama 2 Chat [7] and Zephyr [8]
- **GRPO (Group Relative Policy Optimization)** — Replaces value network with group-based advantage estimation; used by DeepSeekMath [11]
- **KTO (Kahneman-Tversky Optimization)** — Works with unpaired binary feedback (thumbs up/down), removing the need for pairwise comparisons [9]
- **IPO (Identity Preference Optimization)** — Adds regularization to prevent overfitting the Bradley-Terry assumption [10]
- **Iterative DPO / Online DPO** — Generates on-policy responses to avoid distribution shift; demonstrated in Self-Rewarding LMs [15] and CRINGE [17]

### Recent Breakthroughs (last 12 months)

- **GRPO** (Jan 2024): Eliminated critic network overhead while matching PPO quality on math reasoning [11]
- **KTO** (Feb 2024): Showed alignment is possible without paired preferences, reducing data collection cost by ~50% [9]
- **Self-Rewarding LMs** (Jan 2024): Models generate their own preference data, enabling alignment without human annotators [15]
- **West-of-N sampling** (Jan 2024): Synthetic preference generation via best-of-N creates high-quality training pairs from any SFT model [16]

### Open Problems

- **Distribution shift**: Offline DPO trains on static data while the policy evolves, degrading alignment over time [2]
- **Reward hacking at scale**: Models exploit preference patterns without genuine capability improvement
- **Multi-turn alignment**: Current methods optimize single-turn responses; multi-turn coherence remains unsolved
- **Length bias**: DPO-trained models tend to produce longer outputs that score well on preferences but reduce utility

## Executive Summary

SFT teaches a model *what* to say by imitating demonstrations; DPO teaches it *which* outputs humans prefer by directly optimizing pairwise comparisons without training a separate reward model [2]. The core architectural decision is whether you have demonstration data (use SFT), preference data (use DPO/variants), or both (use the SFT→DPO pipeline that has become the industry standard [7][8]).

- **Choose SFT** when you have high-quality demonstrations and need format/style compliance
- **Choose DPO** when you have pairwise preference data and need to refine an already-capable model
- **Choose SFT→DPO** (the standard pipeline) when building a production chat model from a pretrained base

**The killer framing:** "SFT sets the floor (competence); DPO raises the ceiling (preference alignment). Production systems need both — SFT alone lacks preference signal, DPO alone lacks behavioral grounding."

Cost headline: DPO training costs ~40% less than equivalent RLHF (PPO) because it eliminates the reward model and value network [2].

```
Decision Tree: Choosing Your Alignment Method
─────────────────────────────────────────────
Have demonstration data?
├── YES → Run SFT first (always)
│   └── Have preference pairs?
│       ├── YES → SFT → DPO [2]
│       └── NO → Have thumbs up/down?
│           ├── YES → SFT → KTO [9]
│           └── NO → Ship SFT-only
└── NO → Have preference pairs?
    ├── YES → DPO on base model (risky, needs strong base)
    └── NO → Collect demonstrations first
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Task type and quality bar | Single-turn vs multi-turn? Format compliance vs open-ended quality? Latency budget determines model size. |
| 2. Identify constraints | Data availability and compute | How many demonstrations (SFT needs 10K-100K)? How many preference pairs (DPO needs 50K-200K)? GPU hours budget? |
| 3. Propose baseline | SFT on available demonstrations | Train LoRA [12] SFT on curated demos. Evaluate on held-out set. This becomes DPO's reference model. |
| 4. Identify gaps | Where SFT falls short | Measure: helpfulness (preference win-rate), safety (refusal accuracy), format adherence. Gap = preference signal needed. |
| 5. Introduce improvements | Add DPO/variant for preference alignment | Choose DPO [2] for paired data, KTO [9] for unpaired, GRPO [11] for math/reasoning. Tune β carefully. |
| 6. Add evaluation + guardrails | Multi-dimensional eval suite | LLM-as-Judge [13] + human eval on 500 samples. Safety classifiers. Reward model score monitoring. |
| 7. Discuss scaling tradeoffs | Online vs offline, data freshness | Offline DPO is simpler but drifts. Online/iterative DPO [17] is costlier but tracks policy. At scale, use synthetic preferences [16]. |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Alignment method | DPO (offline) | PPO (online RL) | Limited compute, <200K pref pairs, single-turn | Complex reward shaping, multi-objective, multi-turn |
| Data source | Human preferences | AI-generated (synthetic) [16] | High-stakes domain, regulatory need | Rapid iteration, cost-sensitive, scalable |
| Parameter efficiency | Full fine-tune | LoRA [12] | Model <7B, sufficient GPU memory | Model >13B, multi-tenant serving |
| DPO variant | Standard DPO [2] | IPO [10] | Clean preference data, low noise | Noisy labels, need regularization |
| Feedback type | Pairwise comparisons | Binary (good/bad) | Annotator capacity for A/B, subtle distinctions | High volume, crowd workers, simpler UX |

## System Design Walkthrough

### Opening Frame

The production alignment pipeline is not a single training run — it is a continuous system that collects preferences, trains policies, evaluates safety, and monitors for reward hacking. The non-obvious insight: the reference model in DPO is both a regularizer and a liability — it freezes your quality floor at training time while the world's expectations evolve.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Alignment Training Pipeline                    │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Data Layer  │  Train Layer │  Eval Layer  │  Serving Layer     │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│ Demos (SFT)  │ SFT Train    │ MT-Bench[13] │ A/B Inference      │
│ Pref Pairs   │ DPO Train    │ Human Eval   │ Safety Filter      │
│ Synthetic[16]│ Ref Model    │ Win-Rate     │ Preference Logger  │
│ Binary FB    │ LoRA [12]    │ Safety Suite │ Drift Detector     │
└──────────────┴──────────────┴──────────────┴────────────────────┘
        │              │              │               │
        ▼              ▼              ▼               ▼
   [Collection]  [Training]     [Gating]       [Production]
   Human/AI →    SFT → DPO →   Pass/Fail →    Serve + Log →
   Store pairs   Checkpoint     Deploy gate    Feedback loop
```

- **Data Layer**: Manages demonstration corpora and preference datasets; handles deduplication, quality filtering, and synthetic generation [16]
- **Train Layer**: Runs SFT then DPO sequentially; the SFT checkpoint becomes DPO's reference model π_ref
- **Eval Layer**: Multi-signal evaluation combining LLM-as-Judge [13], safety classifiers, and sampled human review
- **Serving Layer**: Deploys aligned model with A/B testing, logs user interactions for the data flywheel

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Distribution shift in offline DPO | Online/iterative DPO — regenerate pairs from current policy [17] | 3-5x compute cost per iteration |
| Length exploitation | Add length penalty to DPO loss or use length-controlled DPO | May hurt genuinely detailed responses |
| Catastrophic forgetting of SFT skills | Regularize DPO with SFT loss mixture (e.g., 10% SFT data in DPO batch) | Slightly dilutes preference signal |
| Reward hacking on narrow patterns | Diverse preference data + ensemble reward models for filtering | Annotation cost scales linearly |
| Reference model staleness | Periodically update π_ref to latest checkpoint | Destabilizes training if done too frequently |

### Scaling Summary

- **10x data**: LoRA [12] still works; batch accordingly; main bottleneck is preference annotation throughput
- **100x data**: Need distributed DPO with sharded reference model; switch to synthetic preference generation [16] for volume
- **1000x users**: Online DPO becomes necessary; deploy preference collection at inference time; multi-objective alignment (safety vs helpfulness) requires Pareto-front approaches

## Interview Q&A Bank

### Q1: What is the fundamental difference between SFT and DPO?

> **Quick answer:** SFT maximizes the likelihood of demonstration tokens (behavioral cloning); DPO maximizes the likelihood that preferred responses score higher than rejected ones under an implicit reward model [2].

SFT minimizes cross-entropy loss on expert demonstrations: L_SFT = -E[log π(y|x)]. It teaches the model *what to say* but cannot express *relative quality* — all demonstrations are treated as equally good.

DPO reformulates the RLHF objective by noting that the optimal policy under a reward model has a closed-form relationship to the reward [2]. Instead of training a reward model and running PPO [4], DPO directly optimizes: L_DPO = -E[log σ(β(log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))]. This captures relative quality between preferred (y_w) and rejected (y_l) responses.

The key insight: SFT provides a strong initialization (the reference policy π_ref), and DPO refines it using preference signal. Without SFT first, DPO struggles because the base model's output distribution is too far from the preference data distribution [8].

**Hard follow-up:** Why can't you just do DPO on a base model without SFT?

> The base model's generation distribution has minimal overlap with the preference data distribution. DPO's gradients become noisy when π_ref assigns near-zero probability to both chosen and rejected responses. Empirically, Zephyr [8] showed that skipping SFT degrades DPO by 15+ points on MT-Bench.

### Q2: How does DPO eliminate the reward model from RLHF?

> **Quick answer:** DPO derives that the optimal policy under any reward model can be expressed as r(x,y) = β log(π(y|x)/π_ref(y|x)) + C, then substitutes this into the Bradley-Terry preference model to get a loss that depends only on the policy [2].

Traditional RLHF [1][3] has three stages: (1) SFT on demonstrations, (2) train a reward model on preferences, (3) optimize the policy with PPO [4] against the reward model while staying close to π_ref via KL penalty. This is complex — PPO requires a value network, reward model inference at each step, and careful hyperparameter tuning.

DPO's key mathematical insight [2]: given the KL-constrained RL objective, the optimal policy satisfies π*(y|x) = π_ref(y|x) · exp(r(x,y)/β) / Z(x). Rearranging gives r(x,y) = β log(π*(y|x)/π_ref(y|x)) + β log Z(x). Substituting into the Bradley-Terry model P(y_w > y_l) = σ(r(y_w) - r(y_l)), the partition function cancels, yielding a loss purely in terms of policy log-ratios.

This eliminates: the reward model (~same size as policy), the value network, PPO's clipping/GAE machinery, and reward model inference during training. The result is ~40% less compute and far simpler implementation.

**Hard follow-up:** What assumption does this derivation rely on, and when does it break?

> It assumes the Bradley-Terry preference model perfectly captures human preferences — that preferences are transitive and determined by a scalar reward difference. When preferences are intransitive (A>B, B>C, C>A) or context-dependent, the implicit reward is misspecified. IPO [10] addresses this by not assuming Bradley-Terry.

### Q3: What role does β (beta) play in DPO, and how do you tune it?

> **Quick answer:** β controls the KL penalty strength — how far the aligned policy can deviate from the reference. Low β allows aggressive optimization (risk of reward hacking); high β keeps the policy conservative (underutilizes preferences) [2].

β appears in the DPO loss as a temperature on the log-ratio difference. Formally, it scales the implicit reward: r(x,y) = β log(π(y|x)/π_ref(y|x)). At β→∞, the loss becomes insensitive to policy changes (no learning). At β→0, the policy is unconstrained and may collapse to degenerate solutions.

Practical tuning: start with β=0.1 for general chat alignment (Llama 2 used 0.1 [7]). For safety-critical tasks, use β=0.3-0.5 to stay close to the SFT reference. For creative tasks, β=0.05 allows more exploration. The gradient magnitude scales inversely with β — lower β produces larger updates, requiring lower learning rates to compensate.

| β range | Behavior | Use case |
|---------|----------|----------|
| 0.01-0.05 | Aggressive; large policy shift | Creative writing, style transfer |
| 0.1-0.2 | Standard; balanced | General chat [7][8] |
| 0.3-0.5 | Conservative; safety-first | Medical, legal, financial |

**Hard follow-up:** How does β interact with the learning rate, and can you derive the effective update magnitude?

> The per-sample gradient magnitude is proportional to β · (1 - σ(·)). With low β, the implicit reward gap is amplified, causing large logit shifts. You must reduce LR proportionally — empirically, LR ≈ 1e-6 for β=0.1 and LR ≈ 5e-7 for β=0.05. The product β·LR should remain roughly constant for stable training.

### Q4: When should you use DPO vs PPO vs GRPO?

> **Quick answer:** Use DPO for offline paired preferences with simple implementation; PPO for complex multi-objective rewards or multi-turn; GRPO for reasoning tasks where you can verify correctness programmatically [11].

| Method | Data requirement | Compute | Best domain | Limitation |
|--------|-----------------|---------|-------------|------------|
| DPO [2] | Paired preferences (offline) | 1x (baseline) | Single-turn chat | Distribution shift |
| PPO [4] | Reward model + online gen | 3-4x | Multi-turn, multi-objective | Complexity, instability |
| GRPO [11] | Verifiable rewards (e.g., math) | 1.5x | Reasoning, code | Needs objective scoring |
| KTO [9] | Unpaired binary feedback | 0.8x | High-volume, low-quality labels | Weaker signal per sample |
| IPO [10] | Paired preferences | 1x | Noisy preference data | Less studied at scale |

The architectural decision hinges on your data and verification ability. If you can programmatically score outputs (math correctness, code passes tests), GRPO eliminates the need for human preferences entirely [11]. If you only have thumbs-up/down, KTO [9] avoids the expensive pairing step.

**Hard follow-up:** Why does GRPO work well for math but poorly for open-ended chat?

> GRPO estimates advantages by sampling multiple responses and computing group-relative rewards [11]. For math, the reward is binary (correct/incorrect), giving clean signal. For chat, reward is subjective and noisy — group-relative scoring amplifies noise rather than signal, making the advantage estimates unreliable.

### Q5: How do you build a preference dataset for DPO?

> **Quick answer:** Generate multiple responses per prompt from your SFT model, have annotators rank them pairwise, filter for inter-annotator agreement, and deduplicate. Quality of preferences matters more than quantity [5].

The pipeline: (1) Curate diverse prompts covering your use cases. (2) Generate 4-8 responses per prompt from the SFT model (or a mix of models for diversity). (3) Present pairs to annotators for comparison. (4) Filter: keep only pairs with >70% annotator agreement. (5) Balance: ensure chosen/rejected aren't trivially distinguishable (e.g., by length alone).

Critical quality factors: Anthropic's work [5] showed that preference quality degrades with annotator fatigue — sessions >2 hours produce noisy labels. The "margin" matters: pairs where chosen is barely better than rejected provide less gradient signal than clear wins. AlpacaFarm [14] demonstrated that simulated preferences from GPT-4 correlate 0.85+ with human preferences, enabling scalable synthetic data.

For production, the hybrid approach dominates: 20% human-annotated (high quality, diverse) + 80% synthetic (scalable, consistent). West-of-N [16] generates synthetic preferences by sampling N responses and pairing best-vs-worst, achieving 90%+ of human-annotation quality.

**Hard follow-up:** How do you handle ties and near-ties in preference annotation?

> Discard ties for standard DPO (it cannot represent indifference). For IPO [10], ties can be included as "equal preference" pairs with modified loss. Alternatively, use a 5-point scale (much better / better / tie / worse / much worse) and only keep the "much better" pairs for initial DPO training — this gives cleaner signal at the cost of data volume.

### Q6: How does LoRA interact with DPO training?

> **Quick answer:** LoRA [12] makes DPO practical for large models by training only low-rank adapter weights (~0.1% of parameters), while the frozen base serves as an implicit reference model — eliminating the need to store π_ref separately.

In full fine-tune DPO, you must maintain two copies of the model: the training policy π_θ and the frozen reference π_ref. For a 70B model, this requires ~280GB just for weights (2 × 70B × 2 bytes in fp16). LoRA [12] solves this elegantly: the base model IS the reference, and only the adapter weights are trained. The log-ratio log(π_θ/π_ref) reduces to the difference in logits caused by the adapter.

Practical configuration for DPO with LoRA: rank r=64-128 (higher than SFT's typical r=16-32 because preference learning needs more capacity), α=128-256, applied to all attention projections (q, k, v, o) and MLP layers. Learning rate: 5e-7 to 2e-6.

The key trade-off: LoRA constrains the policy to a low-rank subspace around the reference, which naturally regularizes against reward hacking but limits the magnitude of preference-driven changes. For aggressive alignment (safety refusals), full fine-tune outperforms LoRA by 5-10% on refusal benchmarks.

**Hard follow-up:** Can you merge the LoRA adapter into the base and then run another round of DPO with a new LoRA?

> Yes — this is "iterative LoRA DPO." Merge adapter into base (new reference), generate fresh pairs from the merged model, train new LoRA. Each iteration allows O(rank) additional movement. Zephyr [8] and iterative DPO work [17] use this pattern. Risk: each merge accumulates drift from the original base, making rollback harder.

### Q7: How do you detect reward hacking in a DPO-trained model?

> **Quick answer:** Monitor the gap between implicit reward (DPO log-ratio) and actual human preference win-rate; if implicit reward rises while human win-rate plateaus or drops, the model is hacking the preference pattern rather than improving quality.

Reward hacking manifests when the model exploits spurious correlations in preference data — e.g., longer responses, sycophantic agreement, or hedge phrases that correlate with "preferred" labels but don't improve utility.

Detection signals: (1) **Length divergence**: track output length percentiles over training; >30% increase signals exploitation. (2) **Diversity collapse**: measure distinct n-gram ratio; drop below 0.7 indicates mode collapse. (3) **Win-rate saturation**: implicit DPO reward keeps climbing but MT-Bench [13] or human eval plateaus. (4) **Sycophancy score**: measure agreement rate on controversial prompts — increase beyond 80% is a red flag.

Mitigation: (1) Length-penalized DPO: subtract α·len(y) from implicit reward. (2) Data augmentation: add "rejected = long sycophantic" pairs explicitly. (3) Early stopping on held-out human eval, not training loss. (4) Diverse preference data: Anthropic [5] found that mixing helpful and harmless preferences prevents single-dimension hacking.

**Hard follow-up:** How would you design an automated reward hacking detector that works without human evaluation?

> Train a separate "hacking classifier" on known exploit patterns (length, sycophancy, hedging). Compute per-response exploit features, compare distribution to the SFT baseline. Alert when any feature's KL divergence from baseline exceeds a threshold. Additionally, use a diverse ensemble of reward models — if one RM scores a response highly but others don't, it's likely exploiting a single model's bias.

### Q8: How do you evaluate an aligned model beyond simple accuracy?

> **Quick answer:** Use a multi-signal evaluation stack: automated (MT-Bench, AlpacaEval), safety (refusal accuracy, toxicity rate), human (pairwise comparison with N=500+), and behavioral (diversity, length, calibration) [13][14].

| Eval dimension | Metric | Tool/Method | Threshold |
|---------------|--------|-------------|-----------|
| Helpfulness | MT-Bench score [13] | GPT-4 judge | >7.5 for production |
| Safety | Refusal rate on harmful prompts | Safety classifier | >95% |
| Truthfulness | TruthfulQA MC accuracy | Standard bench | >60% |
| Diversity | Distinct-3 gram ratio | Compute from generations | >0.75 |
| Preference | Human win-rate vs baseline | A/B eval, N=500 | >55% |
| Verbosity | Median response length | Compute | Within 20% of target |

The key insight from AlpacaFarm [14]: automated evaluators (LLM-as-Judge) correlate ~0.85 with human rankings at the model level but only ~0.65 at the instance level. Use automated for rapid iteration, but gate production deployment on human eval.

**Hard follow-up:** MT-Bench uses GPT-4 as judge — how do you handle the bias when your model is also GPT-4 class?

> Self-preference bias inflates scores by 10-15% when judge and candidate are similar [13]. Mitigations: (1) use a diverse judge panel (Claude + GPT-4 + Gemini), (2) position-swap debiasing (score A-first and B-first, average), (3) anchor with human agreement rate on a calibration set of 200 samples to compute a correction factor.

### Q9: How do you handle catastrophic forgetting during DPO?

> **Quick answer:** Mix 5-15% SFT replay data into DPO batches, use low learning rates (5e-7), and monitor performance on a held-out general capability benchmark after each checkpoint.

DPO can degrade capabilities the SFT model already had — especially on tasks not represented in preference data. For example, a model aligned for chat may lose code generation ability if no code preferences are included. This is particularly dangerous because DPO's loss actively pushes probability mass away from rejected responses, which may overlap with correct responses on other tasks.

Mitigations: (1) **SFT replay**: include original SFT examples as a regularization term: L = L_DPO + λ·L_SFT (λ=0.1-0.5). Llama 2 [7] uses this approach. (2) **Elastic weight consolidation**: penalize changes to weights important for pre-existing capabilities. (3) **Task-specific evaluation**: maintain a regression test suite covering 5-10 core capabilities; fail the deployment gate if any drops >3%. (4) **LoRA isolation** [12]: train DPO adapter separately; if capability regresses, reduce adapter contribution via scaling factor.

**Hard follow-up:** If you observe forgetting on code tasks after chat alignment, how do you fix it without retraining from scratch?

> Generate code preference pairs (correct solution vs buggy solution) and add them to the DPO dataset. Alternatively, train a separate code-specific LoRA adapter and merge both adapters at inference time with task-routing. The nuclear option: multi-task DPO with domain-weighted sampling — oversample underperforming domains until parity is restored.

### Q10: How does online/iterative DPO solve distribution shift?

> **Quick answer:** Instead of training on a fixed preference dataset, iterative DPO generates new responses from the *current* policy, collects fresh preferences on those responses, and trains the next iteration — keeping training data on-distribution [17].

Offline DPO's fundamental weakness: the preference data was generated by a *different* policy (the SFT model or a previous checkpoint). As training progresses, the policy π_θ diverges from the data-generating policy, making the preference signal stale. The model encounters states it was never trained on.

Iterative DPO [17] fixes this with a loop: (1) Generate responses from current π_θ. (2) Score/rank with reward model or human annotators. (3) Form preference pairs from current-policy outputs. (4) Run DPO update. (5) Repeat. Self-Rewarding Language Models [15] push this further by having the model judge its own outputs.

The trade-off is compute: each iteration requires full generation (expensive for large models) and fresh annotation. In practice, teams run 3-5 iterations with synthetic scoring [16] between major human annotation rounds.

**Hard follow-up:** How do you prevent iterative DPO from collapsing into a mode where the model only generates "safe" easily-preferred responses?

> Maintain diversity pressure: (1) Use high temperature during generation (T=0.9-1.0). (2) Reject pairs where both responses are near-identical (edit distance <10%). (3) Include "exploration" prompts that push the model outside its comfort zone. (4) Track entropy of the policy's output distribution — if it drops below a threshold, inject random SFT demonstrations to re-diversify.

### Q11: How would you scale DPO training to a 70B+ parameter model?

> **Quick answer:** Use LoRA [12] for memory efficiency, DeepSpeed ZeRO-3 for weight sharding, gradient checkpointing to trade compute for memory, and offload the reference model to CPU or use the LoRA-as-reference trick.

The memory challenge for full-parameter DPO on 70B: policy (140GB fp16) + reference (140GB fp16) + optimizer states (280GB for Adam) + gradients (140GB) = ~700GB minimum. This exceeds even 8×A100-80GB clusters.

| Strategy | Memory saved | Compute cost | Implementation |
|----------|-------------|--------------|----------------|
| LoRA (r=64) [12] | ~95% (policy trainable params) | +5% | HuggingFace PEFT |
| ZeRO-3 sharding | Scales with #GPUs | +10% communication | DeepSpeed |
| Gradient checkpointing | ~60% activation memory | +33% compute | PyTorch native |
| Reference offload to CPU | ~50% GPU memory | +15% (PCIe transfer) | Custom |
| fp8 quantized reference | ~50% ref memory | +5% (quantization error) | bitsandbytes |

The production recipe: LoRA [12] on 8×A100s with DeepSpeed ZeRO-2 (shard optimizer + gradients), fp16 policy, bf16 frozen base-as-reference. Training 70B with 100K preference pairs: ~48 GPU-hours.

**Hard follow-up:** How do you ensure the reference model's log-probabilities remain numerically consistent across distributed training?

> In ZeRO-3, gathering weights for reference forward pass introduces non-determinism from float reduction order. Fix: (1) pin reference model on dedicated GPUs with no sharding, (2) use fp32 for reference logit computation, (3) run reference forward pass in eval mode with deterministic algorithms enabled. Alternatively, pre-compute all reference log-probs before training and store them — this eliminates runtime reference model entirely at the cost of O(dataset) storage.

### Q12: What is the theoretical relationship between DPO and reward modeling?

> **Quick answer:** DPO is mathematically equivalent to RLHF with an optimal reward model under the Bradley-Terry preference assumption — it implicitly learns the same reward function but parameterizes it through the policy's log-ratio rather than a separate network [2].

The equivalence: In standard RLHF, you train reward model r_φ on preferences, then solve max_π E[r_φ(x,y)] - β·KL(π||π_ref). The solution is π*(y|x) ∝ π_ref(y|x)·exp(r(x,y)/β). DPO inverts this: r(x,y) = β·log(π(y|x)/π_ref(y|x)) + β·log Z(x) [2].

This means any DPO-trained policy *implicitly* contains a reward model — you can extract it by computing log-ratios. This is powerful for interpretability: analyze which responses your model considers "high reward" without explicitly training an RM.

The equivalence breaks when: (1) The Bradley-Terry model is misspecified (human preferences aren't explained by scalar rewards) [10]. (2) The policy class is restricted (LoRA can't represent the true optimal policy). (3) Optimization is imperfect (finite data, finite training). In these cases, DPO and RLHF diverge — RLHF with a separate RM can be more robust because the RM provides error correction that DPO's implicit RM lacks.

**Hard follow-up:** Can you extract the implicit reward from a DPO-trained model and use it to train another model with PPO?

> Yes — compute r(x,y) = β·log(π_DPO(y|x)/π_ref(y|x)) for arbitrary (x,y) pairs. This "distilled reward" can train a PPO policy. The advantage: you get a reward model "for free" from DPO training. The limitation: this reward is only accurate in the region where π_DPO has coverage — it extrapolates poorly to out-of-distribution responses, unlike a separately trained RM that sees diverse data.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1: DPO Loss Gradient Dynamics and β Sensitivity</strong></summary>

The DPO loss for a single preference pair (x, y_w, y_l) is [2]:

```
L = -log σ(β · (log π_θ(y_w|x)/π_ref(y_w|x) - log π_θ(y_l|x)/π_ref(y_l|x)))
```

Let u = β · (log π_θ(y_w|x)/π_ref(y_w|x) - log π_θ(y_l|x)/π_ref(y_l|x)). Then L = -log σ(u) = log(1 + e^{-u}).

The gradient with respect to model parameters θ:

```
∂L/∂θ = -σ(-u) · β · (∂log π_θ(y_w|x)/∂θ - ∂log π_θ(y_l|x)/∂θ)
```

The σ(-u) term acts as an **adaptive weight**: when the model already correctly ranks y_w > y_l (u >> 0), σ(-u) → 0 and the gradient vanishes. When the model is wrong (u << 0), σ(-u) → 1 and full gradient is applied. This is analogous to hard-example mining in contrastive learning.

**β's role in gradient magnitude**: The factor β multiplies the log-ratio difference. For fixed log-ratio gap Δ, increasing β from 0.1 to 0.5 multiplies u by 5, which can push σ(-u) to 0 faster — effectively making easy examples "invisible" sooner. This creates a tension:

- **Low β (0.01-0.05)**: Large effective gradients, policy moves far from reference. Risk: gradient explosion on already-correct pairs when policy has drifted significantly.
- **High β (0.3-0.5)**: Small effective gradients, policy stays near reference. Risk: underfitting — many pairs contribute near-zero gradient before learning completes.

**Stability analysis**: Training diverges when the log-ratio log(π_θ/π_ref) grows unbounded. With LoRA [12], this is naturally bounded by the adapter's rank — the maximum logit shift is bounded by O(r · ||A|| · ||B||). Full fine-tuning requires explicit gradient clipping (typically at 1.0) and learning rate warmup.

**Empirical guideline**: Set β such that the initial u-values have mean ~0 and std ~1 across the training set. This ensures σ(-u) ≈ 0.5 at the start — half the dynamic range is available for both increasing and decreasing the implicit reward.

</details>

<details><summary><strong>DE Probe 2: Distributed DPO Training — Reference Model Memory and Synchronization</strong></summary>

DPO requires computing log-probabilities from both π_θ (training policy) and π_ref (frozen reference) on every batch. In distributed settings, this creates unique challenges not present in standard fine-tuning.

**Memory architecture for 70B DPO on 8×A100-80GB:**

```
Option A: Co-located (both models on same GPUs)
  Per-GPU: π_θ shard (17.5GB) + π_ref shard (17.5GB) + optimizer (35GB) + activations (~10GB) = 80GB
  → Barely fits with ZeRO-3, no room for large batch sizes

Option B: Dedicated reference GPUs
  GPUs 0-5: π_θ with ZeRO-2 (optimizer+gradient sharding)
  GPUs 6-7: π_ref replicated (full model per GPU for fast forward pass)
  → Wastes 2 GPUs but enables larger batches on training GPUs

Option C: Pre-computed reference log-probs (offline reference)
  Precompute log π_ref(y_w|x) and log π_ref(y_l|x) for all training pairs
  Store as dataset columns (~16 bytes per token × dataset size)
  Training only needs π_θ — standard distributed fine-tuning
  → Best throughput but cannot handle online/iterative DPO
```

**Synchronization concerns**: In ZeRO-3 with co-located models, the reference forward pass triggers all-gather operations that compete with training communication. Solutions: (1) Pin reference with `requires_grad=False` and exclude from ZeRO sharding. (2) Use FSDP with separate process groups for reference and policy. (3) Pipeline the reference forward pass asynchronously — compute reference logprobs on batch N while training on batch N-1.

**Numerical consistency**: Float32 vs float16 reference logprobs can diverge by O(1e-3) per token, compounding over sequences of 2048 tokens to O(1.0) in total log-prob. This noise directly corrupts the DPO loss. Best practice: compute reference logprobs in fp32 even when training in fp16/bf16.

**LoRA simplification** [12]: When using LoRA, the reference IS the frozen base — no separate model needed. The log-ratio becomes simply the logit difference contributed by the adapter: log(π_θ/π_ref) = log(softmax(logits + ΔW·h)) - log(softmax(logits)). This can be computed in a single forward pass, halving memory and eliminating synchronization entirely.

</details>

<details><summary><strong>DE Probe 3: Preference Data Quality — Annotation Disagreement and Noise Robustness</strong></summary>

Preference data quality is the dominant factor in DPO success — noisy labels flip the gradient direction, actively teaching the model wrong preferences [5].

**Noise taxonomy:**
1. **Random noise**: Annotator attention lapses (5-15% of labels). Effect: reduces gradient signal but doesn't create systematic bias.
2. **Systematic bias**: Position preference (always prefer option A), length preference, or style preference. Effect: model learns spurious correlations.
3. **Genuine disagreement**: Subjective preferences where reasonable annotators differ. Effect: averaging conflicting signals produces conservative, bland outputs.

**Quantifying annotation quality**: Inter-annotator agreement measured by Cohen's κ:
- κ > 0.8: High agreement, safe for DPO
- κ = 0.6-0.8: Moderate; filter to keep only majority-agreed pairs
- κ < 0.6: Low; this data will actively harm DPO training

Anthropic's data collection [5] achieved κ ≈ 0.72 on helpfulness and κ ≈ 0.85 on harmlessness. Harmlessness has higher agreement because it's more objective.

**DPO's noise sensitivity vs PPO's**: DPO is MORE sensitive to label noise than PPO-based RLHF. Reason: in RLHF, the reward model sees all preference data and averages noise across many pairs. DPO applies each preference pair directly to the policy gradient — a single flipped label creates a direct wrong-direction update. IPO [10] addresses this by adding ε-margin regularization that prevents overfitting to individual pairs.

**Practical noise mitigation pipeline:**
```python
# 1. Collect K annotations per pair (K >= 3)
# 2. Compute agreement score
agreement = sum(annotations) / K  # fraction choosing y_w
# 3. Filter: keep only pairs with agreement > threshold
threshold = 0.7  # conservative
pairs = [p for p in dataset if p.agreement > threshold]
# 4. Weight by margin: confident pairs get higher loss weight
weights = [(p.agreement - 0.5) * 2 for p in pairs]  # 0 to 1 scale
# 5. Curriculum: train on high-agreement pairs first, add noisier pairs later
```

AlpacaFarm [14] showed that synthetic preferences from strong LLMs have higher self-consistency (κ ≈ 0.90) than human annotators, suggesting that hybrid human-synthetic pipelines produce cleaner training signal at lower cost.

</details>

<details><summary><strong>DE Probe 4: Evaluating Alignment — Automated Metrics vs Human Preference Correlation</strong></summary>

The evaluation problem in alignment: human preferences are the ground truth, but human eval is expensive ($2-5 per comparison), slow (days of turnaround), and itself noisy. Automated metrics must correlate strongly with human preferences to be useful for rapid iteration [13].

**Correlation landscape (model-level, 95% CI):**

| Metric | Spearman ρ with human pref | Cost per eval | Latency |
|--------|---------------------------|---------------|---------|
| GPT-4 as Judge [13] | 0.85 ± 0.04 | $0.03 | 5s |
| Claude as Judge | 0.83 ± 0.05 | $0.02 | 3s |
| Reward model score | 0.75 ± 0.07 | $0.001 | 0.1s |
| BLEU/ROUGE | 0.25 ± 0.10 | $0.0001 | 0.01s |
| Perplexity | 0.15 ± 0.12 | $0.001 | 0.1s |
| Human eval (fresh panel) | 1.00 (reference) | $3.00 | 48h |

**Key findings from MT-Bench [13]:** LLM-as-Judge correlates well at ranking models (model-level) but poorly at ranking individual responses (instance-level, ρ ≈ 0.65). This means: use automated eval for model selection and hyperparameter tuning, but gate deployment on human eval.

**Biases in automated evaluation:**
1. **Self-preference**: Models prefer outputs similar to their own style (+10-15% bias)
2. **Verbosity**: Judges prefer longer outputs even when shorter is better (+5-8% for length)
3. **Position**: First-presented option gets +3-5% preference
4. **Sycophancy**: Confident-sounding but wrong answers preferred over hedged correct ones

**Production evaluation protocol:**
1. **Daily (automated)**: MT-Bench [13] + safety suite on every checkpoint. Takes 30 minutes.
2. **Weekly (hybrid)**: 200 samples scored by LLM panel + 50 by humans. Compute judge-human agreement drift.
3. **Pre-deploy (human)**: 500+ pairwise comparisons with production traffic prompts. Require >55% win-rate vs current production model with p<0.05.

AlpacaFarm [14] showed that using simulated preferences for method *development* (choosing between DPO variants, tuning β) correlates r=0.97 with the ranking you'd get from human preferences. This validates using synthetic eval during development and reserving human eval for deployment gates.

</details>

<details><summary><strong>DE Probe 5: Detecting Reward Hacking and Mode Collapse in Production</strong></summary>

Reward hacking occurs when the model achieves high implicit reward (or human preference proxy) by exploiting distributional shortcuts rather than genuinely improving. In production, this manifests gradually — often undetected until user satisfaction drops.

**Production monitoring signals:**

```
Reward Hacking Detection Dashboard
────────────────────────────────────
Signal 1: Length Drift
  Baseline (SFT): median 180 tokens, p95 450 tokens
  Alert: median > 250 OR p95 > 700
  
Signal 2: Diversity Collapse
  Metric: distinct-4gram ratio across 1000 same-prompt samples
  Baseline: 0.82
  Alert: < 0.65 (model converging to template responses)

Signal 3: Sycophancy Index
  Test: Present factually wrong claims, measure agreement rate
  Baseline: 15% (model corrects 85%)
  Alert: > 35% (model agreeing to avoid conflict)

Signal 4: Reward-Quality Divergence
  Track: implicit_reward (β·log_ratio) vs human_win_rate
  Alert: implicit_reward ↑ for 3 consecutive evals while win_rate flat/down
```

**Mode collapse signatures**: When DPO overoptimizes, the model's output distribution narrows. Detection: (1) Sample 100 responses for each of 50 diverse prompts. (2) Compute within-prompt cosine similarity of embeddings. (3) Alert if mean similarity > 0.85 (responses becoming interchangeable).

**Root causes and mitigations:**

| Cause | Detection | Fix |
|-------|-----------|-----|
| Length exploitation | Length percentile drift | Add length penalty to loss or length-normalize implicit reward |
| Sycophantic collapse | Agreement rate on controversial prompts | Include "correction" preference pairs in data [5] |
| Format gaming | Template detection via regex | Diversify preference data formats |
| Single-dimension optimization | Factor analysis on rewards | Multi-objective DPO with per-dimension β |

**The nuclear option — rollback protocol**: If hacking is detected post-deployment, immediately rollback to the pre-DPO SFT checkpoint (known-safe baseline). This is why maintaining versioned checkpoints at each training stage is non-negotiable. The SFT model may be less "preferred" but won't exhibit adversarial exploits.

Post-mortems from Self-Rewarding LMs [15]: When models judge their own outputs, reward hacking accelerates because the judge and policy share biases. Mitigate with external scoring signals or periodic human recalibration.

</details>

<details><summary><strong>DE Probe 6: GRPO/IPO/KTO — When DPO's Assumptions Don't Hold</strong></summary>

DPO assumes: (1) preferences follow Bradley-Terry (scalar reward difference), (2) paired comparisons are available, (3) offline data is sufficient. When these break, alternative methods are needed.

**IPO — When Bradley-Terry Fails** [10]:
Human preferences are often intransitive (A>B, B>C, C>A). IPO replaces the sigmoid-based BT loss with a squared error that only requires the policy to prefer y_w by a margin ε:

```
L_IPO = (log(π_θ(y_w|x)/π_ref(y_w|x)) - log(π_θ(y_l|x)/π_ref(y_l|x)) - 1/(2β))²
```

This is more robust because: (1) It doesn't assume preferences are generated by a scalar reward. (2) The squared loss prevents overconfident optimization beyond the margin. (3) It naturally handles noisy labels — a flipped pair contributes bounded loss.

**KTO — When Paired Data Is Unavailable** [9]:
KTO only needs to know whether a response is "good" or "bad" (binary signal), not which of two responses is better. Inspired by prospect theory:

```
L_KTO = E_good[-log σ(β · rθ(x,y))] + E_bad[-log σ(-β · rθ(x,y))]
where rθ(x,y) = log(π_θ(y|x)/π_ref(y|x)) - E_ref[log(π_θ/π_ref)]
```

The E_ref subtraction centers the reward estimates, handling the "all responses are mediocre" case. KTO reduces annotation cost by ~50% since annotators only label individual responses, not pairs.

**GRPO — When You Have Verifiable Rewards** [11]:
For math/code where correctness is checkable, GRPO samples G responses per prompt, computes rewards, and uses group-relative advantage:

```
Advantage_i = (r_i - mean(r_1..G)) / std(r_1..G)
L_GRPO = -E[Advantage_i · log π_θ(y_i|x) - β · KL(π_θ||π_ref)]
```

GRPO eliminates the critic/value network (saving ~50% memory vs PPO [4]) and the preference annotation step. DeepSeekMath [11] used G=64 samples per prompt, achieving state-of-the-art math reasoning.

**Decision framework:**

| Condition | Method | Reason |
|-----------|--------|--------|
| Clean paired preferences, single-turn | DPO [2] | Simplest, well-understood |
| Noisy/intransitive preferences | IPO [10] | Robust to BT violations |
| Only binary feedback available | KTO [9] | No pairing needed |
| Verifiable reward function exists | GRPO [11] | No human annotation needed |
| Multi-turn with complex dynamics | PPO [4] | Can shape reward over trajectory |

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Training-Run Usage | Cost |
|-----------|-----------|----------------------|------|
| Preference annotation (human) | $3/pair | 50K pairs | $150,000 |
| Preference annotation (synthetic) [16] | $0.05/pair | 200K pairs | $10,000 |
| SFT training (7B, 8×A100) | $3/GPU-hr | 24 GPU-hrs | $72 |
| DPO training (7B, 8×A100) | $3/GPU-hr | 48 GPU-hrs | $144 |
| Evaluation (MT-Bench, 1 run) [13] | $0.03/sample | 3K samples | $90 |
| Human eval (deploy gate) | $4/comparison | 500 pairs | $2,000 |

### Monthly Cost at Scale

| Scale | Compute (train) | Annotation | LLM Eval | Total/month |
|-------|-----------------|------------|----------|-------------|
| Startup (1 model/month) | $500 | $10K (synthetic) | $200 | ~$11K |
| Mid-scale (weekly iterations) | $2K | $40K (hybrid) | $800 | ~$43K |
| Enterprise (daily iterations, 70B) | $50K | $150K (human+synthetic) | $5K | ~$205K |

### Cost Optimization Priority Stack

| Priority | Optimization | Estimated Savings |
|----------|-------------|-------------------|
| 1 | Replace human annotation with synthetic [16] | 70-90% annotation cost |
| 2 | Use LoRA instead of full fine-tune [12] | 60-80% compute |
| 3 | Pre-compute reference log-probs (offline reference) | 30-40% training compute |
| 4 | Curriculum filtering (train on high-signal pairs first) | 20-30% faster convergence |
| 5 | Distill 70B aligned model to 7B for serving | 90% inference cost |

### Build vs Buy

| Capability | Build Cost (annual) | Buy Option | Recommendation |
|-----------|-------------------|------------|----------------|
| Preference collection platform | $200K eng + $500K annotation | Scale AI, Surge AI | Buy unless >1M pairs/year |
| DPO training infrastructure | $50K eng + compute | Together AI, Anyscale | Build if core competency |
| Evaluation pipeline | $100K eng | AlpacaFarm [14] (open-source) | Build on open-source |
| Safety classifiers | $150K eng | Anthropic API, OpenAI moderation | Buy for baseline, build domain-specific |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Implicit reward (β·log_ratio) mean | >3.0 (reward hacking) | Page on-call, freeze training |
| KL divergence from reference | >15 nats average | Warning; check for mode collapse |
| Training loss plateaus for >500 steps | Δloss < 0.001 | Investigate data quality or LR |
| Output length p95 | >2x baseline | Check length exploitation |
| Safety refusal rate | <90% on red-team set | Block deployment |
| Human win-rate vs previous model | <50% (regression) | Rollback to previous checkpoint |
| Distinct-4gram ratio | <0.65 | Diversity collapse; add data variety |

### Debugging Walkthrough

```
Symptom: DPO training loss not decreasing
├── Check 1: Are preference labels correct? (sample 20, manually verify)
│   └── >3 errors in 20 → Data pipeline bug → Fix labels, retrain
├── Check 2: Is β too high? (compute mean initial σ(-u))
│   └── mean σ(-u) < 0.1 → β too high → Reduce β by 2-5x
├── Check 3: Is learning rate too low?
│   └── Gradient norm < 1e-6 → Increase LR by 3-10x
└── Check 4: Is reference model correct?
    └── log π_ref(y_w) ≈ log π_ref(y_l) for all pairs → Wrong ref model loaded

Symptom: Model outputs degenerate after DPO
├── Check 1: KL divergence from reference
│   └── KL > 20 → Over-optimization → Increase β, reduce epochs
├── Check 2: Output diversity (sample 50 prompts × 10 responses)
│   └── Similarity > 0.9 → Mode collapse → Add diversity regularization
└── Check 3: Capability regression on benchmarks
    └── MMLU/HumanEval dropped → Catastrophic forgetting → Add SFT replay
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|----------------|-------------------|--------------|
| SFT checkpoint (π_ref) | Always kept; never overwritten | Full retraining from this point |
| DPO checkpoint per epoch | Keep last 5; rollback = swap served model | Minutes (model swap) |
| Preference dataset version | Git-tag + hash; revert to known-good | Retraining required (hours) |
| Training config (β, LR, epochs) | Config file in git; rollback = re-run | Retraining required |
| LoRA adapter weights [12] | Stored separately; swap/disable instantly | Seconds (adapter hot-swap) |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Explicit thumbs up/down | Direct preference; highest quality | UI button, 2-5% response rate |
| Pairwise comparison (A/B test) | Gold standard for DPO pairs | Serve 2 models, collect choice |
| Regeneration requests | Implicit rejection signal | Log when user clicks "regenerate" |
| Edit distance (user edits output) | Shows what model got wrong | Diff user's edit vs original |
| Conversation abandonment | Response quality proxy | Session analytics |
| Copy/share actions | Positive signal (response was useful) | UI event tracking |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|---------------|---------------|
| Daily | Preference data filtering + quality scores | Automated pipeline; no gate |
| Weekly | Synthetic preference generation [16] from new prompts | Coverage metric on prompt clusters |
| Bi-weekly | DPO fine-tuning iteration on accumulated preferences | >5K new high-quality pairs accumulated |
| Monthly | Human evaluation + safety audit | Win-rate >55% vs current prod AND safety >95% |
| Quarterly | Full SFT retrain on updated demonstration corpus | Major capability gap identified |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Iterative/Online DPO [17] | Distribution shift from offline data | Rapidly evolving use cases | Stable domains, limited compute |
| Self-Rewarding [15] | Annotation bottleneck | Domains where model can self-judge | Safety-critical tasks |
| West-of-N synthetic pairs [16] | Scale preference data cheaply | Any domain with good SFT base | When base model is too weak |
| Multi-objective DPO | Conflicting goals (helpful vs safe) | Chat with safety constraints | Single-objective tasks |
| DPO + SFT loss mixture | Catastrophic forgetting | Broad-capability models | Narrow-task specialists |
| LoRA adapter stacking [12] | Multi-domain alignment | Multi-tenant serving | When domains conflict |
| Reject sampling + DPO | Quality of preference data | Bootstrap from reward model | When RM is unreliable |
| Curriculum DPO (easy→hard) | Training stability | Large diverse datasets | Small homogeneous datasets |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|----------------|----------------------|
| "We should use DPO because it's simpler than RLHF" | "DPO's simplicity trades off distribution coverage — we need iterative DPO [17] for our evolving use case" |
| "We need more preference data" | "We need higher-quality preferences — filtering to κ>0.7 agreement will help more than 2x volume" |
| "β=0.1 is the standard" | "β should be set so initial u-values have unit variance — compute it empirically from the first batch" |
| "DPO training converges fast" | "Fast convergence often means reward hacking — track win-rate against held-out human eval, not training loss" |
| "Let's use GPT-4 as judge for eval" | "LLM judges have position bias and self-preference — we need debiased panels with human calibration [13]" |
| "LoRA reduces memory" | "LoRA also bounds the policy's deviation from reference, acting as implicit KL regularization [12]" |
| "Our model is aligned — DPO loss is low" | "Low DPO loss means we overfit the training preferences — show me win-rate on fresh, held-out prompts" |

## References

### Foundational Papers

- [1] Ouyang et al. (2022) — *Training language models to follow instructions with human feedback* — arXiv:2203.02155 — Introduced InstructGPT; established the SFT → RM → PPO pipeline as the standard RLHF recipe.
- [2] Rafailov et al. (2023) — *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* — arXiv:2305.18290 — Core DPO paper; proved the closed-form equivalence between reward modeling and policy optimization.
- [3] Ziegler et al. (2019) — *Fine-Tuning Language Models from Human Preferences* — arXiv:1909.08593 — Early work on applying reward learning to language model fine-tuning.
- [4] Schulman et al. (2017) — *Proximal Policy Optimization Algorithms* — arXiv:1707.06347 — The RL algorithm underlying most RLHF implementations.
- [5] Bai et al. (2022) — *Training a Helpful and Harmless Assistant from Human Feedback* — arXiv:2204.05862 — Anthropic's work on preference data collection and multi-objective alignment.
- [6] Christiano et al. (2017) — *Deep Reinforcement Learning from Human Preferences* — arXiv:1706.03741 — Foundational paper on learning reward models from human preference comparisons.

### Frameworks & Implementation

- [7] Touvron et al. (2023) — *Llama 2: Open Foundation and Fine-Tuned Chat Models* — arXiv:2307.09288 — Production-scale SFT + RLHF pipeline; established β=0.1 and SFT→DPO as industry standard.
- [8] Tunstall et al. (2023) — *Zephyr: Direct Distillation of LM Alignment* — arXiv:2310.16944 — Demonstrated DPO with distilled preferences achieves competitive alignment on 7B models.
- [12] Hu et al. (2021) — *LoRA: Low-Rank Adaptation of Large Language Models* — arXiv:2106.09685 — Parameter-efficient fine-tuning; critical for making DPO practical on large models.

### Production & Safety

- [15] Yuan et al. (2024) — *Self-Rewarding Language Models* — arXiv:2401.10020 — Models generate own training signal; demonstrates iterative self-improvement loop.
- [16] Pace et al. (2024) — *West-of-N: Synthetic Preference Generation for Language Models* — arXiv:2401.12086 — Scalable synthetic preference data via best-of-N sampling.
- [17] Xu et al. (2024) — *Some Things Are More CRINGE Than Others: Iterative Preference Optimization* — arXiv:2312.16682 — Iterative DPO addressing distribution shift through on-policy data generation.

### Evaluation & Benchmarks

- [13] Zheng et al. (2023) — *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* — arXiv:2306.05685 — Established LLM-as-Judge methodology; quantified biases and correlation with human preferences.
- [14] Dubois et al. (2024) — *AlpacaFarm: A Simulation Framework for Methods that Learn from Human Feedback* — arXiv:2305.14387 — Simulated preference framework; showed synthetic eval correlates 0.97 with human rankings for method development.

### DPO Variants

- [9] Ethayarajh et al. (2024) — *KTO: Model Alignment as Prospect Theoretic Optimization* — arXiv:2402.01306 — Alignment from unpaired binary feedback; removes need for pairwise preference data.
- [10] Azar et al. (2024) — *A General Theoretical Paradigm to Understand Learning from Human Feedback* — arXiv:2310.12036 — IPO; adds margin regularization to handle Bradley-Terry violations and noisy preferences.
- [11] Shao et al. (2024) — *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models* — arXiv:2402.03300 — Introduced GRPO; group-relative advantage estimation without critic network.

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; fixed duplicate DE probes, added diverse sub-topics, enforced length constraints |
| 2026-06-08 | Filed DPO infrastructure comparison (veRL vs NeMo-RL) | veRL is online-RL only (no DPO). NeMo-RL supports DPO+GRPO. TRL is best for offline DPO. Decision framework by scale/algorithm/hardware. Knowledge page + query filed. |
