---
title: "Why do we need the value function? Was GRPO the first to remove it? What breaks without it?"
summary: "The value function serves as a variance-reducing baseline for policy gradients. GRPO was NOT the first attempt to remove it — REINFORCE (1992) never had one, and various baseline methods preceded GRPO. PPO and A2C break without it due to high-variance gradient estimates."
type: query
createdAt: 2026-07-28
---

# Why Do We Need the Value Function? Was GRPO the First to Remove It?

## The Role of the Value Function

In policy gradient methods, the value function V(s) serves three purposes:

1. **Variance reduction (primary).** The raw policy gradient (REINFORCE) uses total return R as the reward signal. This has extremely high variance — one lucky trajectory can dominate the gradient. Subtracting a baseline b(s) that doesn't depend on the action reduces variance without introducing bias:

   `∇J = E[∇log π(a|s) · (R - b(s))]`

   The optimal baseline is approximately V(s) — the expected return from state s. This gives you the **advantage** A(s,a) = Q(s,a) - V(s), which tells you "how much better was this action than average?"

2. **Credit assignment.** In multi-step episodes, the value function helps attribute outcomes to specific actions via Temporal Difference (TD) learning and Generalized Advantage Estimation (GAE): `A_t = δ_t + γλδ_{t+1} + ...` where `δ_t = r_t + γV(s_{t+1}) - V(s_t)`.

3. **Bootstrapping.** Actor-critic methods use V(s) to estimate future returns without waiting for episode completion, enabling online learning and handling infinite-horizon tasks.

## What Breaks Without It

| Algorithm | Needs Value Function | What Breaks Without It |
|-----------|---------------------|----------------------|
| **REINFORCE** | No (but benefits from baseline) | Works but has prohibitively high variance — impractical for LLMs with 32K+ token sequences |
| **PPO (actor-critic)** | Yes (critic computes advantages) | Cannot compute GAE advantages; falls back to REINFORCE-like high variance; training destabilizes |
| **A2C/A3C** | Yes (core to architecture) | Completely non-functional — the "critic" IS the value function |
| **SAC (Soft Actor-Critic)** | Yes (Q-function + V-function) | Cannot compute soft Bellman backup; no entropy-regularized value target |
| **TD3** | Yes (twin Q-functions) | No target for policy improvement; no Bellman update possible |

For LLMs specifically, the problem is acute: sequences are long (thousands of tokens), rewards are sparse (only at end of generation), and the action space is enormous (vocab size ~100K). Without a value function, gradient variance makes training infeasibly slow.

## Was GRPO the First to Remove It?

**No.** The history of value-function-free policy optimization:

| Method | Year | How It Avoids V(s) | Limitation |
|--------|------|-------------------|-----------|
| **REINFORCE** | 1992 | Never had one — uses raw returns | Extremely high variance |
| **REINFORCE + simple baseline** | 1992+ | Uses running average of returns as baseline | Better but not state-dependent |
| **Self-play baselines** | 2017+ | Uses opponent's score or population average | Domain-specific (games only) |
| **Reward-weighted regression** | 2007 | Weights samples by reward, no explicit baseline | Requires many samples |
| **RLOO (REINFORCE Leave-One-Out)** | 2024 | Uses leave-one-out mean of K samples as baseline | Requires multiple samples per prompt |
| **GRPO** | 2025 | Uses group mean/std of G samples as baseline | Requires G completions per prompt |

GRPO's innovation is not "removing the value function" in general — REINFORCE never had one. GRPO's innovation is **making it practical for LLMs** by replacing the learned critic with an empirical group statistic that:
- Requires no additional neural network (saves ~50% memory)
- Has no approximation error (the group statistics are exact for the sampled group)
- Provides both mean AND variance normalization (the `/std` term stabilizes across prompts of varying difficulty)

## The Key Insight

The value function is one specific solution to the variance reduction problem. The deeper need is: **policy gradients need a baseline to be practical.** GRPO doesn't solve variance reduction differently in principle — it uses the same idea (subtract expected reward) but estimates it empirically from a group of samples rather than learning it via a neural network. The tradeoff: GRPO needs G forward passes per prompt (compute cost) instead of one critic forward pass (memory + approximation cost).

## Related

- [[Group Relative Policy Optimization (GRPO)]]
- [[Proximal Policy Optimization (PPO)]]
