---
title: "Suppose qwen3-32b is doing better than gpt-oss-120b on a specific task. How to decide between knowledge distillation from qwen3-32b, RL-DPO, RL-PPO/GRPO, or RL-PPO?"
summary: "Four options compared: (1) Distillation — cheapest, inject missing knowledge, bounded by teacher ceiling. (2) DPO — offline RL from preference pairs, stable but weaker optimization, no reward model needed. (3) GRPO — group-relative rewards without critic model, best for verifiable tasks (math/code), DeepSeek's approach. (4) PPO — online RL with reward model, strongest optimization but most expensive/unstable, can exceed all other methods. Key diagnostic: pass@64 test determines if RL is viable. Choose DPO for soft preferences, GRPO for verifiable rewards, PPO for maximum ceiling."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
## The Four Options

| Method | What It Does | Key Mechanism |
|--------|-------------|---------------|
| **Distillation** (SFT on Qwen3 outputs) | Imitates Qwen3's behavior via supervised learning | Minimize cross-entropy on teacher outputs |
| **DPO** (Direct Preference Optimization) | Offline RL using preference pairs (chosen vs rejected) | Implicit reward via log-ratio of policy/reference [arXiv:2305.18290] |
| **GRPO** (Group Relative Policy Optimization) | Online RL using group-based advantage without critic model | Group of samples → rank by reward → reinforce top-k [DeepSeek] |
| **PPO** (Proximal Policy Optimization) | Online RL with explicit reward model + value critic | Generate → score with reward model → policy gradient update [arXiv:2203.02155] |

## Head-to-Head Comparison

| Dimension | Distillation | DPO | GRPO | PPO |
|-----------|-------------|-----|------|-----|
| **Compute cost** | $ (single H100, hours) | $$ (preference data + training) | $$$ (on-policy generation + training) | $$$$ (reward model + value model + generation + training) |
| **Models needed** | 1 (student only) | 1 (policy + frozen reference) | 1 (policy only, no critic) | 3-4 (policy + reward + value + reference) |
| **Data requirement** | Teacher outputs (cheap to generate) | Preference pairs (chosen/rejected) | Prompts + reward function | Prompts + reward model |
| **Quality ceiling** | Bounded by Qwen3's quality | Bounded by preference data quality | Can exceed teacher (verifiable rewards) | Can exceed teacher (strongest optimization) |
| **Stability** | Very stable | Stable (offline, no generation loop) | Moderate (on-policy but no critic instability) | Least stable (reward hacking, mode collapse) |
| **Reward type needed** | None (imitation) | Pairwise preferences (soft) | Scalar reward per response (verifiable) | Scalar reward per response (any) |
| **On-policy generation** | No | No (offline) | Yes (generates samples each iteration) | Yes (generates samples each iteration) |
| **KL constraint** | Implicit (via replay data mixing) | Implicit (beta parameter in loss) | Explicit (KL penalty) | Explicit (KL penalty + clipping) |
| **Best for** | Missing knowledge, format/style | Subjective quality, safety, style alignment | Math, code, tasks with verifiable correctness | Maximum ceiling, complex multi-objective optimization |
| **Risk** | Style mimicry | Preference collapse, overfitting to pairs | Length hacking, reward gaming | Reward hacking, mode collapse, catastrophic forgetting |
| **Timeline** | Days | Days-Week | 1-2 Weeks | 2-4 Weeks |

## The Diagnostic: Pass@K Test (Still the First Step)

```
Run GPT-OSS-120B on the failing task at temperature 1.0, 64 samples:

  pass@64 = 0 (NEVER solves it):
    → Distillation (must inject the pattern; RL can't surface what doesn't exist)
    
  pass@64 > 0 but low (5-20% solve rate):
    → GRPO or PPO (amplify the latent capability via RL)
    → DPO also works if you can construct preference pairs
    
  pass@64 high (>50%) but greedy fails:
    → DPO (gentle preference nudge is sufficient)
    → GRPO is overkill for this case
```

This is the **elicitation theory** [arXiv:2504.13837]: RL redistributes probability mass but cannot create capabilities from nothing.

### Why Pass@64 = 0 Means "Distill, Don't RL"

**What it means architecturally:** When you sample 64 times at temperature 1.0, you explore a wide range of the model's output distribution. If ZERO samples succeed, the knowledge/pattern needed to solve the task **does not exist anywhere** in the model's activated parameters. The gap is not "the model knows but expresses poorly" — it genuinely does not know.

**Why RL fails when pass@K = 0:**
```
RL works by reinforcing behaviors the model already exhibits occasionally:

  pass@64 = 5%  → RL amplifies that 5% to dominant behavior (works!)
  pass@64 = 0%  → Nothing to amplify → gradient signal is zero → no learning

GRPO specifically: if all K samples in a group score 0 on the reward,
  advantage for every sample is 0, policy doesn't update.
PPO: reward model gives 0 for everything, value function learns
  "expect nothing," no useful gradient.
```

**Why distillation works when pass@K = 0:**

Distillation **injects the missing pattern** by showing examples of correct behavior the model has never produced itself:
```
Before distillation: P(correct answer) = 0 across all 117B params
After distillation:  P(correct answer) > 0 (pattern now exists in relevant experts)
After optional RL:   P(correct answer) >> 0 (amplified from the injected seed)
```

**The GPT-OSS-120B MoE angle:** Pass@64 = 0 likely means one of:
1. **No expert was trained on this domain** — none of 128 experts contain the relevant weights
2. **Router never selects the right expert** — knowledge may exist in expert #87 but is unreachable for this input type
3. **5.1B active params insufficient** — task requires broader knowledge than top-4 experts can provide

Distillation via LoRA/ESFT addresses all three: writes the pattern into existing experts, adjusts routing via implicit SFT signal, or strengthens the domain-relevant experts.

**Edge case — pass@64 = 0 but pass@1000 > 0?** If you can afford sampling 1000+ and find occasional successes, technically RL could work — the capability exists but is astronomically rare. In practice, distillation is still pragmatic because RL with a 0.1% base rate requires enormous compute to amplify. **Rule of thumb: if pass@64 = 0, distill first to get pass@64 > 0, THEN RL to make it reliable.**

### Why 64 Samples? (Not 128, 256, or 16)

The choice of K=64 is not a magic number — it's a **practical trade-off** between statistical confidence, compute cost, and alignment with RL training dynamics:

**Statistical reasoning:**
```
If the true success probability is p, the probability of seeing
ZERO successes in K samples is: P(0 successes) = (1-p)^K

At K=64:
  p=1%  → P(miss all 64) = 0.99^64 = 52.5%   (might miss a 1% capability)
  p=2%  → P(miss all 64) = 0.98^64 = 27.2%   (likely catches 2%+ capability)  
  p=5%  → P(miss all 64) = 0.95^64 = 3.7%    (almost certainly catches 5%+)
  p=10% → P(miss all 64) = 0.90^64 = 0.1%    (definitely catches 10%+)

At K=16:
  p=5%  → P(miss all 16) = 0.95^16 = 44%     (MISSES half the time!)

At K=128:
  p=1%  → P(miss all 128) = 0.99^128 = 27.5% (catches more, but 2x compute)
  p=2%  → P(miss all 128) = 0.98^128 = 7.4%  (marginally better than K=64)
```

**Why K=64 is the sweet spot:**
- **Catches ≥5% capabilities with 96% confidence** — if the model can solve it 5%+ of the time, K=64 will almost certainly find at least one success
- **Compute-feasible**: 64 forward passes on GPT-OSS-120B at ~1s each = ~1 minute per prompt. Testing 100 prompts = ~2 hours. K=256 would take ~8 hours.
- **Aligned with literature**: DeepSeek, Qwen, and academic RL papers standardized on pass@64 and pass@96 as evaluation metrics [arXiv:2501.12948][arXiv:2505.09388]. The RL training signal becomes practically useful at ~5% base rate — below that, GRPO groups have too few positive examples per batch.
- **Diminishing returns**: Going from K=64 → K=128 catches p=1-2% capabilities that are nearly impossible to amplify via RL anyway (you'd need thousands of GRPO iterations). If it's that rare, distillation is still more practical.
- **RL batch alignment**: GRPO typically uses group sizes of 16-64 samples per prompt during training. If the base model can't produce a correct answer in a group of 64, it won't produce one during training either — meaning the training signal will be empty for this prompt.

**When to use different K values:**

| K | When to Use | Rationale |
|---|-------------|-----------|
| 16 | Quick sanity check; obviously-present capabilities | Fast (~15s/prompt), catches >15% capabilities |
| **64** | **Standard diagnostic (recommended)** | Catches >5% with 96% confidence; 2hrs for 100 prompts; matches RL group size |
| 128-256 | High-stakes decision; expensive RL already budgeted | Catches 1-2% rare capabilities; 2x compute |
| 1000+ | Research exploration only | If capability is this rare, distill first anyway |

**The practical implication:** If you're deciding between $500 distillation and $20K GRPO, spending 2 hours on pass@64 testing is a trivial cost that prevents making the wrong $20K bet.

## When to Use Each Method

### Distillation (SFT on Qwen3 Outputs)

**Choose when:**
- GPT-OSS lacks the KNOWLEDGE entirely (pass@64 = 0)
- Qwen3 has training data GPT-OSS never saw (multilingual, domain-specific)
- You need the improvement in DAYS, not weeks
- Budget is <$1K
- You DON'T need to exceed Qwen3's quality

**Mechanism:**
```
Qwen3-32B generates outputs → GPT-OSS trained to imitate via cross-entropy loss
Loss = -sum(log P_student(token | context)) over Qwen3's outputs
```

**GPT-OSS specifics:** LoRA on targeted MoE experts (ESFT), mix 30-50% Qwen3 data + 50-70% replay.

**Cost:** ~$500-1K | **Timeline:** Days | **Ceiling:** Bounded by Qwen3

---

### DPO (Direct Preference Optimization)

**Choose when:**
- Task quality is SUBJECTIVE (no verifiable right answer)
- You have preference pairs (chosen/rejected) OR can generate them from Qwen3 vs GPT-OSS outputs
- Stability is more important than maximum performance
- You want RL-like gains WITHOUT on-policy generation infrastructure
- Safety/alignment tuning (harmlessness, helpfulness ranking)

**Mechanism:**
```
Loss_DPO = -log σ(β * (log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))

Where:
  y_w = preferred (Qwen3's better output)
  y_l = rejected (GPT-OSS's worse output)
  π_ref = frozen GPT-OSS base (reference policy)
  β = KL constraint strength (typically 0.1-0.5)
```

**Constructing preference pairs for this case:**
1. Run both Qwen3-32B and GPT-OSS-120B on same prompts
2. Use LLM-as-judge to determine which response is better
3. Train GPT-OSS with DPO: chosen=Qwen3 output, rejected=GPT-OSS output

**Advantages over PPO:** No reward model needed, no value function, no on-policy generation loop (offline on fixed dataset). Much simpler infrastructure.

**Limitations:**
- Offline — doesn't adapt to the model's evolving distribution during training
- Bounded by the quality of preference pairs (if Qwen3 is only slightly better, signal is weak)
- Can suffer **preference collapse** — model reduces likelihood of BOTH chosen and rejected [DPOP paper]
- Beta sensitivity — too high β → undertrained; too low β → forgets base capabilities

**Cost:** ~$2K-5K | **Timeline:** Days-1 Week | **Ceiling:** Bounded by preference pair quality (≈ Qwen3)

---

### GRPO (Group Relative Policy Optimization)

**Choose when:**
- Task has VERIFIABLE REWARDS (math proofs, code that passes tests, factual accuracy)
- You want to EXCEED Qwen3's quality (not just match it)
- You don't want to train a separate reward model (PPO's main complexity)
- Budget is moderate ($5K-20K)
- DeepSeek-R1 style reasoning improvement is the goal

**Mechanism:**
```
For each prompt x:
  1. Generate K responses: {y_1, ..., y_K} from current policy π
  2. Score each: r_i = reward(y_i)  (e.g., code passes tests? math proof verifies?)
  3. Compute group advantage: A_i = (r_i - mean(r)) / std(r)
  4. Update policy: maximize sum(A_i * log π(y_i|x)) - β * KL(π || π_ref)

No value model (critic) needed — advantage estimated from the group statistics.
```

**Why GRPO over PPO:**
- No critic model = 50% less VRAM, simpler training loop
- Group normalization provides stable baselines without value function estimation
- DeepSeek proved this works for frontier reasoning (R1 used GRPO-style training)
- Naturally handles sparse rewards (only a few of K samples may be correct)

**Why GRPO over DPO:**
- On-policy — generates fresh samples each iteration (adapts to improving model)
- Works with scalar rewards (not just pairwise preferences)
- Can exceed teacher ceiling (reward-maximizing, not imitation-bounded)
- Better for tasks where correctness is binary (pass/fail)

**GPT-OSS specifics:** Generate K=16-64 samples per prompt from GPT-OSS-120B at varying reasoning levels. Score with verifiable reward (code execution, proof checker). KL-constrain heavily (β=0.04-0.1) to preserve existing reasoning.

**Cost:** ~$5K-20K | **Timeline:** 1-2 Weeks | **Ceiling:** Can exceed Qwen3

---

### PPO (Proximal Policy Optimization)

**Choose when:**
- Maximum possible quality improvement is the goal (cost is secondary)
- Task requires a LEARNED reward model (subjective quality with no verifiable answer)
- You need multi-objective optimization (helpful AND harmless AND concise)
- You have infrastructure for 3-4 model training loop
- InstructGPT/ChatGPT-style alignment is the target

**Mechanism:**
```
Full pipeline (4 models simultaneously):
  1. Policy model π (GPT-OSS-120B being improved)
  2. Reference model π_ref (frozen GPT-OSS-120B for KL constraint)
  3. Reward model R (trained on human/AI preference data)
  4. Value model V (critic — estimates expected future reward)

Each iteration:
  a. π generates responses to prompts
  b. R scores each response
  c. V estimates baseline value
  d. Advantage = R(y) - V(x) 
  e. Update π: maximize clipped advantage - β * KL(π || π_ref)
  f. Update V: minimize (V(x) - R(y))²
```

**Why PPO over GRPO:**
- Learned reward model handles SUBJECTIVE quality (where verifiable rewards don't exist)
- Value function provides lower-variance advantage estimates (more stable with non-binary rewards)
- Multi-objective rewards (combine helpfulness + safety + format in one reward model)
- Can capture nuanced preferences that simple binary rewards miss

**Why PPO over DPO:**
- On-policy (adapts to model's evolving distribution)
- Explicit reward model can be reused and improved independently
- Stronger optimization — iterative online RL outperforms single-pass offline RL
- Handles continuous reward spectrums (not just binary preference)

**Limitations (why NOT PPO):**
- 4 models in memory simultaneously (~4x VRAM vs distillation)
- Reward hacking: model finds output patterns that score high on reward model but are garbage to humans
- Mode collapse: diversity collapses toward one reward-hacking pattern
- Most unstable of all methods — requires extensive hyperparameter tuning (clipping ε, KL β, learning rates for all models)
- Overkill for tasks with verifiable rewards (GRPO is simpler and equally effective)

**GPT-OSS specifics:** For a 120B MoE model, PPO is extremely expensive — need reward model (could use Qwen3-32B-as-judge), value model (smaller GPT-OSS or separate), plus on-policy generation from 120B model. Realistic only with multi-node infrastructure.

**Cost:** ~$20K-100K+ | **Timeline:** 2-4 Weeks | **Ceiling:** Highest possible

---

## Decision Matrix (All 4 Options)

| Question | → Distillation | → DPO | → GRPO | → PPO |
|----------|---------------|-------|--------|-------|
| pass@64 = 0? (model never solves it) | **YES** | — | — | — |
| Task is subjective? (style, safety, preference) | — | **YES** | — | **YES** (if budget allows) |
| Task has verifiable rewards? (math, code) | — | — | **YES** | Also works |
| Need to exceed Qwen3? | — | — | **YES** | **YES** |
| Budget < $1K? | **YES** | — | — | — |
| Budget $2-5K? | ✓ | **YES** | — | — |
| Budget $5-20K? | — | ✓ | **YES** | — |
| Budget $20K+? | — | — | ✓ | **YES** |
| Have preference pairs available? | — | **YES** | — | — |
| Have reward model infrastructure? | — | — | — | **YES** |
| Need multi-objective optimization? | — | — | — | **YES** |
| Stability priority? | **YES** | ✓ | ✓ | — |

## The Optimal Pipeline (Industry Standard)

```
Phase 1: Distillation ($500-1K, days)
  └─ SFT on Qwen3 outputs + replay data
  └─ GPT-OSS now MATCHES Qwen3 on the task
  └─ Provides warm initialization for RL

Phase 2a (if verifiable rewards exist): GRPO ($5-20K, 1-2 weeks)
  └─ On-policy generation + verifiable reward scoring
  └─ GPT-OSS now EXCEEDS Qwen3
  
Phase 2b (if subjective quality): DPO ($2-5K, days) or PPO ($20K+, weeks)
  └─ DPO if budget-constrained and teacher-ceiling is acceptable
  └─ PPO if maximum quality is the goal and infrastructure exists

Skip Phase 1 ONLY if pass@64 is already high (>20%) — the model already
has the capability and just needs RL to make it reliable.
```

## Cost-Quality Frontier

```
Quality
  ↑
  |                                    PPO ●
  |                               GRPO ●
  |                         DPO ●
  |              Distillation ●
  |    Base GPT-OSS ●
  |
  └──────────────────────────────────────→ Cost
       $0    $1K    $5K    $10K   $50K   $100K

  Distillation: cheapest, bounded by teacher
  DPO:          moderate cost, stable, bounded by preference quality  
  GRPO:         good cost-quality ratio for verifiable tasks
  PPO:          most expensive, highest ceiling, least stable
```

## Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|-----------------|
| "Use PPO for math" | Math has verifiable rewards → GRPO is equally effective and 5x cheaper | GRPO with code/proof verification |
| "Use DPO to exceed Qwen3" | DPO is bounded by preference pair quality (≈ Qwen3 outputs) | GRPO or PPO to exceed teacher |
| "Use distillation for reasoning depth" | Mimicry doesn't teach reasoning strategy | GRPO/PPO incentivizes deeper chains |
| "Use GRPO for style/safety alignment" | No binary reward for "safe" or "well-styled" | DPO or PPO with preference-trained reward model |
| "Skip distillation, go straight to PPO" | Cold-start PPO is unstable and slow to converge | Distill first → PPO from warm start |
| "DPO is always better than PPO because simpler" | DPO is offline → doesn't adapt to improving policy → weaker optimization | PPO at high budget; DPO when budget-constrained |
| "GRPO doesn't need KL constraint" | Without KL, GRPO collapses to reward hacking just like PPO | Always KL-constrain (β=0.04-0.1) |

## Summary Decision Tree

```
Is GPT-OSS's failure due to MISSING KNOWLEDGE (pass@64 = 0)?
  YES → Distillation from Qwen3
  NO ↓

Does the task have VERIFIABLE REWARDS (math, code, factual)?
  YES → GRPO (best cost-quality for verifiable tasks)
       (or PPO if multi-objective: correct + concise + safe)
  NO ↓

Is the task about SUBJECTIVE QUALITY (style, safety, preference)?
  YES → DPO (if budget < $10K) or PPO (if budget > $20K)
  NO ↓

Does GPT-OSS occasionally get it right (pass@64 > 0)?
  YES → GRPO with LLM-as-judge reward
  NO → Distillation first, then GRPO/DPO on top

Do you need to EXCEED Qwen3's quality?
  YES → Distillation → GRPO (or PPO for maximum ceiling)
  NO → Distillation alone or DPO
```

## Related

- [[SFT vs RL Pros Cons and Industry Cases]]
- [[Reverse Distillation: Qwen3-32B → GPT-OSS-120B Feasibility]]
- [[Strong-to-Weak Distillation]]
- [[Reasoning Model Distillation]]
- [[Direct Preference Optimization (DPO)]]
- [[Group Relative Policy Optimization (GRPO)]]
