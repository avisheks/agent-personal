---
title: SFT vs RL for Post-Training LLMs — Comprehensive Comparison
url: https://arxiv.org/abs/2203.02155
ingestedAt: 2026-06-07
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2305.18290
  - https://arxiv.org/abs/2212.08073
  - https://arxiv.org/abs/2501.12948
  - https://arxiv.org/abs/2305.20050
  - https://arxiv.org/abs/2210.10760
  - https://arxiv.org/abs/2403.04642
  - https://arxiv.org/abs/2504.13837
  - https://arxiv.org/abs/2401.10020
  - https://arxiv.org/abs/2502.01456
  - https://arxiv.org/abs/2310.03716
  - https://arxiv.org/abs/2502.03373
  - https://arxiv.org/abs/2504.16084
  - https://arxiv.org/abs/2409.12917
  - https://arxiv.org/abs/2405.14734
---

# SFT vs RL for Post-Training LLMs

## Pros and Cons

### SFT

Pros: Simple training objective (next-token prediction), stable dynamics, low compute (1x baseline), predictable outcomes, fast iteration.

Cons: Bounded by demonstration quality, cannot exceed training data ceiling, suffers exposure bias, requires expensive expert demonstrations, trades off maj@1 vs pass@96.

### RLHF (PPO)

Pros: Optimizes beyond demonstration quality, uniquely improves both maj@1 and pass@96 simultaneously (Singh et al., 2024), enables holistic property optimization. InstructGPT 1.3B preferred over 175B GPT-3.

Cons: Complex 4-model setup, training instability, reward hacking, overoptimization (Gao et al., 2022), 4-6x compute vs SFT, ~50K human preference labels needed.

### DPO

Pros: No reward model or RL loop, simple classification loss, stable and lightweight, only requires policy + reference model.

Cons: Offline/static (limited by collected data), can reduce absolute likelihood of preferred responses (DPOP paper), "widely reported significantly inferior to online iterative RLHF."

### GRPO (DeepSeek)

Pros: Critic-free (no value model, ~50% less memory than PPO), DeepSeek-R1 achieves SOTA on math/coding/STEM, emergent reasoning behaviors appear from pure RL.

Cons: Theoretically biased estimator (REINFORCE++), requires verifiable rewards, substantial compute for multi-sample generation.

### Constitutional AI / RLAIF

Pros: No human harm labels needed, scales with fewer annotations, produces harmless but non-evasive assistants.

Cons: Quality bounded by AI evaluator, may amplify evaluator biases.

## When to Use What

SFT alone: well-defined tasks, abundant demonstrations, format/style transfer, budget-constrained.

RL necessary: holistic property optimization (safety, helpfulness), exceeding demonstration quality, reasoning/exploration tasks, improving both accuracy and diversity.

SFT + RL pipeline (industry standard): SFT provides strong initialization → RL optimizes on top. Used by OpenAI, Meta, Anthropic, DeepSeek.

## What RL Unlocks That SFT Cannot

1. Simultaneous accuracy + diversity improvement (Singh et al., 2024)
2. Self-correction ability: SCoRe (RL) improves by 15.6% on MATH vs SFT
3. Long chain-of-thought reasoning with backtracking
4. Exploration beyond training data distribution
5. Optimization of evaluator-defined properties

## Industry Successes

- InstructGPT (2022): 1.3B RLHF preferred over 175B GPT-3
- Claude: Constitutional AI achieves harmlessness without human harm labels
- DeepSeek-R1 (2025): Pure RL produces emergent reasoning, published in Nature
- Llama 3.1: Iterative SFT → Rejection Sampling → DPO pipeline
- Self-Rewarding LLMs: 3 iterations of self-reward outperforms Claude 2, Gemini Pro, GPT-4 0613

## Industry Failures

- Length bias exploitation: RLHF improvements "largely driven by increasing response length" (Singhal et al., 2023)
- Reward overoptimization: Gold reward follows inverted-U as proxy optimization increases (Gao et al., 2022)
- SFT insufficient for self-correction: distribution mismatch between training errors and model's own errors
- Mode collapse: Without KL penalty, training produces gibberish that fools reward model
- DPO can reduce likelihood of preferred examples (DPOP paper)

## Elicitation Theory

"RLVR does not generate fundamentally new reasoning abilities beyond what already exists in the base model" (arXiv:2504.13837). Base models at high pass@k solve everything RL models solve at pass@1. RL redistributes probability mass rather than expanding capability space.

However: DeepSeek-R1-Zero shows RL can organize latent capabilities into novel reasoning strategies. TTRL surpasses maj@n ceiling. RL serves as amplifier and organizer, not teacher.

## Compute Comparison

| Method | Relative Compute | Models in Memory |
|--------|-----------------|-----------------|
| SFT | 1x (baseline) | 1 |
| DPO | 1.5-2x | 2 (policy + reference) |
| GRPO | 2-3x | 1 + sampling overhead |
| PPO/RLHF | 4-6x | 4 (policy, reference, reward, value) |
| Online iterative DPO | 3-4x | 2 + generation cycles |

## Data Requirements

| Method | Data Type | Typical Volume |
|--------|-----------|---------------|
| SFT | Demonstrations | 10K-100K |
| RLHF | Preference pairs | ~50K for RM |
| DPO | Preference pairs | 10K-100K |
| GRPO | Prompts + verifiable rewards | Unlimited (self-generated) |
| RFT | Prompts + rubrics | Hundreds to thousands |
