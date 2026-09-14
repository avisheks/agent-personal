# SFT vs RL Post-Training: Decision Framework & Industry Evidence

> **Last Updated:** 2026-06-07 | **Read time:** ~15 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Cost Model]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** Post-training has evolved from "SFT is sufficient" to "SFT initializes, RL optimizes" as the industry standard pipeline.
> Key methods: DPO (offline, simple), GRPO (online, reasoning-focused), PPO (complex but powerful), RFT (minimal data). Main open problem: reward hacking — RLHF gains are partially driven by length bias, not genuine quality [11].
> Recent breakthrough: DeepSeek-R1 (Nature, 2025) showed pure RL produces emergent reasoning without SFT [4]. Trend: online/iterative methods replacing offline DPO; verifiable rewards replacing learned rewards.

## State of the Art

### Current Best Approaches

- **SFT + DPO** — Offline preference optimization; simple, stable, 1.5-2x compute. Llama 3.1 pipeline [16]
- **SFT + GRPO** — Critic-free online RL; dominant for reasoning tasks. DeepSeek-R1 achieves SOTA on math/code [4]
- **SFT + online iterative RLHF** — Highest quality but most complex; Self-Rewarding LLMs outperform GPT-4 [9]
- **Constitutional AI (RLAIF)** — Anthropic's approach; harmlessness without human harm labels [3]
- **RFT (Reinforcement Fine-Tuning)** — OpenAI product; RL with rubrics instead of demonstrations

### Recent Breakthroughs (last 12 months)

- **DeepSeek-R1** (Jan 2025): Pure RL produces emergent self-reflection, verification, backtracking — published in Nature [4]
- **PRIME** (2025): Process RL with implicit rewards; 15.1% over SFT with 10% of training data [10]
- **TTRL** (2025): Test-time RL with majority voting as pseudo-rewards; 211% improvement on AIME [14]
- **SimPO** (2024): Reference-free DPO; outperforms DPO by 6.4 points on AlpacaEval 2 [17]
- **RLVR Elicitation Theory** (2025): Evidence that RL redistributes, doesn't create, capabilities [13]

### Open Problems

- **Reward hacking via length bias**: Improvements "largely driven by increasing response length" [11]
- **Overoptimization (Goodhart's Law)**: Gold reward follows inverted-U as proxy optimization increases [7]
- **DPO's ceiling**: Offline DPO "widely reported significantly inferior to online iterative RLHF"
- **MoE fine-tuning**: Expert routing disruption during RL is poorly understood

## Executive Summary

SFT and RL are complementary, not competing. SFT teaches format and basic capabilities via imitation; RL optimizes holistic properties (safety, reasoning quality) that are easier to evaluate than to demonstrate. The core trade-off: **SFT is bounded by demonstration quality but stable; RL can exceed that ceiling but introduces instability, reward hacking, and 2-6x compute cost.**

- **SFT alone**: Format transfer, instruction following, budget-constrained
- **SFT + DPO**: General alignment, preference optimization at low cost
- **SFT + RL (GRPO/PPO)**: Reasoning, safety, exceeding demonstration quality
- **Pure RL (no SFT)**: Possible but less efficient; SFT initialization helps

**The killer framing:** "SFT teaches a model WHAT to say. RL teaches it HOW WELL to say it. SFT sets the floor; RL raises the ceiling — but only for properties the reward signal can capture."

```
Quality vs Method:
                    SFT ceiling
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
           ╱ RL (with good reward)
     ─ ─ ─
    ╱
───╱ SFT baseline

                    ╲ RL (reward hacking)
                     ╲ ─ ─ ─ (quality degrades)

Compute →
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | What property to optimize? Format? Safety? Reasoning? | Is the goal demonstrable (→ SFT) or evaluable-but-hard-to-demonstrate (→ RL)? |
| 2. Identify constraints | Compute budget, annotation budget, timeline | Can you afford 4-6x compute for PPO? Or is DPO (1.5-2x) the ceiling? |
| 3. Propose baseline | SFT on best available demonstrations | Train SFT model; evaluate on held-out domain task; measure quality ceiling |
| 4. Identify gaps | Quality gap between SFT and human-preferred quality | If gap <3%: SFT sufficient. If 3-10%: add DPO. If >10% or safety-critical: full RL |
| 5. Introduce RL | Choose method based on signal availability | Verifiable rewards (math/code) → GRPO. Preference pairs → DPO/PPO. Constitution → RLAIF |
| 6. Monitor for failure | Reward hacking, mode collapse, forgetting | Track length correlation, base capability regression, reward vs true quality divergence |
| 7. Iterate | Online/iterative approaches compound gains | Self-rewarding or iterative DPO: each round generates better data for the next |

## System Design Walkthrough

### The Industry-Standard Post-Training Pipeline

```
┌───────────────────────────────────────────────────────────────────┐
│                   Post-Training Pipeline                            │
├───────────┬─────────────────┬─────────────────┬──────────────────┤
│ Stage 1   │ Stage 2         │ Stage 3         │ Stage 4           │
│ SFT       │ Reward Signal   │ RL Optimization │ Evaluation        │
│           │                 │                 │                   │
│ Expert    │ Human prefs OR  │ PPO / DPO /     │ Held-out eval +   │
│ demos →   │ AI feedback OR  │ GRPO / RFT →    │ Base capability   │
│ Format +  │ Verifiable      │ Optimize beyond │ regression +      │
│ Baseline  │ rewards         │ SFT ceiling     │ Safety checks     │
└───────────┴─────────────────┴─────────────────┴──────────────────┘
     1x           varies            1.5-6x              —
   compute                         compute
```

### What RL Unlocks That SFT Cannot

1. **Simultaneous accuracy + diversity** — SFT trades off maj@1 vs pass@96; RL improves both [8]
2. **Self-correction** — SCoRe (RL) improves by 15.6% on MATH where SFT fails [15]
3. **Emergent reasoning strategies** — Self-reflection, verification appear from pure RL [4]
4. **Exploration beyond training data** — RL discovers solutions not in demonstrations
5. **Holistic property optimization** — Safety, helpfulness as unified objectives

### The Elicitation Theory

RL does NOT teach new capabilities — it elicits and amplifies latent ones [13]. Evidence:
- Base models at high pass@k solve everything RL models solve at pass@1
- RL redistributes probability mass, chains micro-skills, makes rare behaviors reliable
- If base model cannot solve a problem at all, RL will not help

Implication: invest in better pretraining or distillation for genuinely new capabilities.

## Interview Q&A Bank

### Q1: What's the fundamental difference between SFT and RL for post-training?

> **Quick answer:** SFT minimizes distance to demonstration distribution (imitation). RL maximizes a reward signal (optimization). SFT is bounded by demo quality; RL can exceed it but introduces instability.

SFT trains with cross-entropy loss on expert demonstrations — the model learns to produce outputs statistically similar to the training data. RL trains with a reward signal that evaluates output quality — the model explores and is reinforced for good outcomes regardless of whether they appear in training data. This is why RL can exceed SFT: it's not limited to imitating a fixed distribution.

**Hard follow-up:** If RL just elicits latent capabilities, why not just use best-of-N sampling from the SFT model?

> Best-of-N at inference time approximates RL's effect (sampling diversity then selecting the best). But it's N times more expensive at inference, every single call. RL amortizes that cost into training — it reshapes the distribution once so that pass@1 is as good as pass@N was. RL is "offline best-of-N" baked into the weights.

### Q2: When does RLHF actually help vs when is it length bias?

> **Quick answer:** Singhal et al. (2023) showed RLHF improvements are "largely driven by increasing response length" [11]. A purely length-based reward reproduces most gains. Real RLHF value appears in safety alignment and reasoning, not general helpfulness.

The test: compare your RLHF model against an SFT model with a simple "always be verbose" instruction. If they're similar, your reward model learned length, not quality. Real RL value shows up when: (1) the task has verifiable correct answers (math, code), (2) the optimization target is genuinely hard to demonstrate (safety nuance), or (3) you use process rewards that can't be gamed by length alone.

**Hard follow-up:** How do you build a reward model that doesn't reward length?

> Length-normalize reward scores. Or use DPO with length-controlled preference pairs (choose between responses of similar length). Or use verifiable rewards (math correctness, test passing) that are length-invariant. SimPO [17] uses average log probability (inherently length-normalized) as the reward signal.

### Q3: Walk through the InstructGPT pipeline and what each stage contributed.

> **Quick answer:** SFT made GPT-3 follow instructions (format). RLHF made it follow them WELL (quality). The 1.3B RLHF model was preferred over the 175B base — proving RL adds qualitative value that scaling alone doesn't provide [1].

Stage 1 (SFT): 13K demonstrations from labelers. Teaches the model to respond in instruction-following format. Without this, PPO is unstable (policy is too far from desired distribution). Stage 2 (Reward Model): 33K comparisons. Labelers rank 4-9 model outputs per prompt. Trains a 6B reward model. Stage 3 (PPO): Optimizes the SFT model against the reward model with KL penalty to prevent drift. Result: 85% win rate over SFT model in human preference.

**Hard follow-up:** Why couldn't they just collect 50K demonstrations and skip RL entirely?

> Because it's 10x cheaper to rank outputs than to write perfect ones. And ranking captures holistic quality (helpfulness, safety, nuance) that's hard to specify in a demonstration. You can tell whether response A is better than B without being able to write the ideal response yourself. RL exploits this asymmetry between evaluation and generation.

### Q4: DeepSeek-R1 showed pure RL works without SFT. Does this invalidate the SFT→RL pipeline?

> **Quick answer:** No. R1-Zero (pure RL) works but is less efficient. R1 (SFT cold start + GRPO) outperforms R1-Zero. SFT makes RL more sample-efficient by providing a better starting point [4].

DeepSeek-R1-Zero demonstrates that reasoning can emerge from pure RL with verifiable rewards (math correctness). But it requires significantly more compute to converge and produces less readable outputs. R1 adds a small SFT cold-start phase (seeded with examples of reasoning chains) before GRPO, achieving better results faster. The lesson: SFT is not strictly necessary but remains the practical default because it reduces RL compute by 2-5x.

**Hard follow-up:** What "emerged" from pure RL that SFT couldn't produce?

> Self-reflection ("wait, let me reconsider..."), verification ("let me check this step..."), and dynamic strategy switching. These metacognitive behaviors were not in any training data — they arose because GRPO's reward structure incentivized them. The model discovered that checking its work leads to higher rewards. SFT can only produce these if they're explicitly demonstrated.

### Q5: How do you detect and prevent reward hacking?

> **Quick answer:** Monitor correlation between reward score and true quality (via held-out human eval). When they diverge, the model is hacking. Prevention: KL penalty, length normalization, diverse reward signals, process rewards over outcome rewards.

Gao et al. (2022) showed gold reward follows an inverted-U as proxy optimization increases [7]. The model initially improves genuinely, then starts exploiting reward model blind spots. Detection: (1) track response length over training — exponential growth signals length hacking, (2) periodic human eval on same prompts — if human preference plateaus while reward increases, hacking is occurring, (3) check reward model confidence calibration — overconfident scores on long outputs suggest exploitation.

**Hard follow-up:** Is there a theoretical limit to how much you can optimize against a reward model?

> Yes — Gao et al. derive scaling laws showing the optimal KL budget depends on reward model quality. With a perfect reward model, infinite optimization is fine. With any imperfect model, there's an optimal stopping point beyond which true quality degrades. Practically: stop when held-out eval plateaus, not when reward plateaus.

## Cost Model

### Compute Comparison (70B model, 10K examples, 3 epochs)

| Method | Models in Memory | Relative Compute | Wall Clock (8xA100) | Cost |
|--------|:----------------:|:----------------:|:--------------------:|:----:|
| SFT only | 1 | 1x | 4-12 hrs | $50-150 |
| SFT + DPO | 2 (policy + ref) | 1.5-2x | 8-20 hrs | $100-250 |
| SFT + GRPO | 1 + sampling | 2-3x | 15-30 hrs | $180-400 |
| SFT + PPO | 4 (policy, ref, RM, value) | 4-6x | 30-60 hrs | $400-800 |
| SFT + online iterative DPO | 2 + generation cycles | 3-4x | 20-40 hrs | $250-500 |

### Data Cost Comparison

| Method | Data Type | Volume Needed | Annotation Cost |
|--------|-----------|:-------------:|:---------------:|
| SFT | Expert demonstrations | 10K-100K | $5-50 per example |
| DPO | Preference pairs | 10K-100K | $1-5 per comparison |
| PPO/RLHF | Preferences (for RM) | ~50K | $1-5 per comparison |
| GRPO | Prompts + verifiable rewards | Unlimited | ~$0 marginal |
| RFT | Prompts + rubrics | 100s-1000s | $0.10-1 per rubric |
| RLAIF | Constitution (principles) | 10-50 rules | One-time authoring |

### Break-Even: When Is RL Worth the Cost?

RL adds 1.5-6x compute cost. It's worth it when:
- Quality gap between SFT and desired output > 3% on domain eval
- Task requires safety alignment (can't be demonstrated, only evaluated)
- Verifiable rewards exist (math, code, factual QA with known answers)
- Scale justifies fixed cost (deploying to millions of users)

RL is NOT worth it when:
- SFT achieves acceptable quality
- No reliable reward signal exists
- Budget allows <2x compute overhead
- Task is simple format transfer

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use |
|---------|---------------|-------------|
| SFT → DPO | Cheap preference alignment | Default for most fine-tuning |
| SFT → GRPO | Reasoning quality | Math, code, any verifiable domain |
| SFT → PPO | Maximum flexibility in reward | Complex multi-objective alignment |
| Constitutional AI | Safety without harm labels | When safety is critical, annotation is expensive |
| Iterative self-rewarding | Frozen RM bottleneck | When you want compounding improvements |
| Distillation from RL model | Transfer RL gains cheaply | Improving small models from large RL-trained ones |
| Process Reward Models | Credit assignment in reasoning | Multi-step tasks where final answer is insufficient signal |
| RFT (rubric-based) | Low-annotation RL | Domain expertise tasks with verifiable criteria |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal Says |
|-----------------|---------------------|
| "We need RLHF to improve our model" | "First measure the SFT ceiling. If it's within 3% of target, DPO is sufficient at 1/4 the cost of PPO" |
| "DPO is simpler so we should use it" | "DPO is offline — bounded by collected data quality. If we need to exceed that ceiling, online methods are worth the complexity" |
| "Our reward model shows improving scores" | "Track reward score vs held-out human eval independently. Divergence signals reward hacking — check length correlation first" [11] |
| "RL teaches the model to reason" | "RL redistributes probability mass onto correct solutions already latent in the base model. If pass@1000 can't solve it, RL won't either" [13] |
| "DeepSeek did pure RL, we should too" | "R1-Zero works but R1 (SFT cold start + GRPO) is more efficient. SFT reduces RL compute 2-5x. Pure RL is a research result, not an operational recommendation" |
| "Let's fine-tune for safety with SFT" | "SFT-only safety creates over-refusal or under-refusal. RL enables nuanced safety boundaries that generalize to adversarial inputs" |

## References

- [1] Ouyang et al. (2022) — Training language models to follow instructions with human feedback — arXiv:2203.02155 [InstructGPT]
- [2] Rafailov et al. (2023) — Direct Preference Optimization — arXiv:2305.18290 [DPO]
- [3] Bai et al. (2022) — Constitutional AI: Harmlessness from AI Feedback — arXiv:2212.08073
- [4] DeepSeek-AI (2025) — DeepSeek-R1: Incentivizing Reasoning via RL — Nature 645; arXiv:2501.12948
- [5] Hu et al. (2021) — LoRA: Low-Rank Adaptation — arXiv:2106.09685
- [6] Lightman et al. (2023) — Let's Verify Step by Step — arXiv:2305.20050 [PRM]
- [7] Gao et al. (2022) — Scaling Laws for Reward Model Overoptimization — arXiv:2210.10760
- [8] Singh et al. (2024) — Beyond Human Data: Scaling Self-Training — arXiv:2403.04642
- [9] Yuan et al. (2024) — Self-Rewarding Language Models — ICML 2024; arXiv:2401.10020
- [10] PRIME (2025) — Process Reinforcement through Implicit Rewards — arXiv:2502.01456
- [11] Singhal et al. (2023) — Length Correlations in RLHF — arXiv:2310.03716
- [12] Qu et al. (2025) — Demystifying Long Chain-of-Thought Reasoning — arXiv:2502.03373
- [13] RLVR (2025) — Does Not Teach New Reasoning — arXiv:2504.13837
- [14] TTRL (2025) — Test-Time Reinforcement Learning — arXiv:2504.16084
- [15] Kumar et al. (2024) — SCoRe: Self-Correction via RL — arXiv:2409.12917
- [16] Meta (2024) — The Llama 3 Herd of Models — arXiv:2407.21783
- [17] Meng et al. (2024) — SimPO: Simple Preference Optimization — arXiv:2405.14734

---

## MoE SFT Debugging: When GPT-OSS-120B Doesn't Improve

> **Added:** 2026-06-07 | **Source:** ESFT (arXiv:2407.01906), HuggingFace MoE/Mixtral blogs, Together AI docs, ST-MoE research

### Root Causes (Priority Order)

| # | Cause | Evidence | Fix |
|---|-------|----------|-----|
| 1 | LoRA targets MLP/expert layers | HF Mixtral: "should not target MLP layers — sparse, don't interact well with PEFT" | Target attention only (q/k/v/o) |
| 2 | 5K samples insufficient for 128 experts | Each expert gets ~3% of tokens → ~150 effective samples | Scale to 50K+ with task diversity |
| 3 | Single-task data doesn't engage routing | ESFT: routing is concentrated in 5-15% of experts per task | Add 5-10 related task types |
| 4 | Learning rate too low | MoE needs higher LR than dense | Try 2e-4 to 5e-4 |
| 5 | Wrong method (capability doesn't exist) | Elicitation theory: SFT can't create what's not latent | Switch to distillation from teacher |

### Diagnostic Protocol

```
Step 1: pass@100 at T=0.8 on base model
  → High: use DPO (model knows, just inconsistent)
  → Low: distill from teacher (50-100K CoT demos)

Step 2: Overfit on 100 examples
  → Can't memorize: architecture/precision problem
  → Memorizes: data quality/quantity problem

Step 3: Same data on dense model (Llama-3.1-8B)
  → Dense improves, MoE doesn't: MoE-specific issue
```

### Teacher Distillation vs RL Decision

| Signal | → Distillation | → RL (DPO/GRPO) |
|--------|---------------|-----------------|
| pass@100 | Low | High |
| Teacher available | Yes | Not needed |
| Reward verifiable | Hard | Yes (code, math) |
| What it does | Instills new capability | Improves consistency of existing capability |
| MoE advantage | CoT demos → more tokens → more experts get gradient | Respects existing routing specialization |

### Recommended Pipeline for GPT-OSS-120B

```
1. Distill: Generate 50-100K demos from Claude/GPT-4 (with full CoT)
2. SFT: LoRA rank=64, attention-only, LR=3e-4, 1-2 epochs
3. DPO: Generate outputs → score with verifier → preference pairs
4. Together AI supports: SFT → DPO → deploy (natively)
```

### Key Numbers

- Active params: 5.1B of 117B (4.4% utilization)
- Expert coverage per sample: ~3% (top-4 of 128)
- Effective samples per expert at 5K: ~150
- Minimum recommended: 50K+ diverse samples
- Together AI max LoRA rank: 64
- ESFT expert relevance: only 5-15% of experts matter per task

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-07 | Added MoE SFT Debugging section | GPT-OSS-120B not improving after 5K SFT — root causes (LoRA on MLP, gradient dilution, insufficient data), diagnostic protocol, distillation vs RL decision tree, recommended pipeline |
| 2026-06-07 | Initial v2 generation | SFT vs RL comprehensive comparison — decision framework, industry successes/failures, elicitation theory, cost model, 5 Q&As with hard follow-ups |
| 2026-06-07 | Filed distillation-vs-RL decision query | Applied to GPT-OSS-120B vs Qwen3-32B context: pass@64 diagnostic, 5-question decision framework, when to use distillation→RL pipeline. Knowledge base query filed. |
| 2026-06-07 | Filed tool-calling fine-tuning query | SFT dominates for format/schema adherence (1K-5K examples). RL adds value only for multi-step sequencing and error recovery. Challenge breakdown: schema adherence, argument hallucination, when-to-call, multi-step planning, error recovery. |
