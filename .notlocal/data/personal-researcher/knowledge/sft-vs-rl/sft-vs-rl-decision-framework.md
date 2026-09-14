---
title: "SFT vs RL Decision Framework"
summary: "A systematic approach to choosing between Supervised Fine-Tuning (SFT), Reinforcement Learning (RL), or combined approaches for post-training language models based on task requirements, data availability, and computational constraints."
sources:
  - sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-15T11:21:54.403429+00:00
updatedAt: 2026-06-15T11:21:54.403429+00:00
---
# SFT vs RL Decision Framework

## Decision Matrix

| Scenario | Approach | Rationale |
|----------|----------|-----------|
| Format/style adaptation | SFT only | Demonstrations sufficient; low cost |
| General instruction following | SFT + DPO | DPO adds preference alignment cheaply |
| Safety alignment | SFT + RLHF/RLAIF | RL essential for nuanced safety boundaries |
| Math/code reasoning | SFT + GRPO/PRM | Verifiable rewards enable strong RL signal |
| Domain expertise (medical, legal) | SFT + RFT | RL with rubrics exceeds SFT ceiling |
| Resource-constrained | SFT + offline DPO | Best quality/compute tradeoff |
| State-of-the-art quality | SFT + online iterative RLHF | Highest quality but most expensive |
| Small model improvement | Distill from RL-trained large model | Transfers RL gains via SFT |

## When SFT Alone Suffices

[[Supervised Fine-Tuning (SFT)]] alone is appropriate when the task is well-defined with abundant high-quality demonstrations, format/style transfer is the primary goal, budget is constrained (both compute and annotation), or the domain has clear correct answers that can be demonstrated. ^[sft-vs-rl-comprehensive-comparison.md]

## When RL Is Necessary

Reinforcement learning becomes necessary when optimizing holistic properties (helpfulness, safety) that are easier to evaluate than demonstrate, when there's a need to exceed the quality of available demonstrations, when the task requires exploration (math, code, reasoning), for safety alignment across adversarial distributions, or when improving both accuracy and diversity simultaneously. ^[sft-vs-rl-comprehensive-comparison.md]

## Method Comparison

### SFT Characteristics

SFT offers a simple training objective (next-token prediction), stable dynamics, low compute (1x baseline), predictable outcomes, and fast iteration. However, it is bounded by demonstration quality, cannot exceed training data ceiling, suffers exposure bias, requires expensive expert demonstrations, and trades off maj@1 vs pass@96. ^[sft-vs-rl-comprehensive-comparison.md]

### RLHF (PPO) Characteristics

[[Reinforcement Learning from Human Feedback (RLHF)]] optimizes beyond demonstration quality, uniquely improves both maj@1 and pass@96 simultaneously, and enables holistic property optimization. InstructGPT 1.3B was preferred over 175B GPT-3. However, it requires a complex 4-model setup, has training instability, suffers from reward hacking and overoptimization, uses 4-6x compute vs SFT, and needs ~50K human preference labels. ^[sft-vs-rl-comprehensive-comparison.md]

### DPO Characteristics

[[Direct Preference Optimization (DPO)]] requires no reward model or RL loop, uses a simple classification loss, is stable and lightweight, and only requires policy + reference model. However, it is offline/static (limited by collected data), can reduce absolute likelihood of preferred responses, and is "widely reported significantly inferior to online iterative RLHF." ^[sft-vs-rl-comprehensive-comparison.md]

### GRPO Characteristics

[[Group Relative Policy Optimization (GRPO)]] is critic-free (no value model, ~50% less memory than PPO), with DeepSeek-R1 achieving SOTA on math/coding/STEM, and emergent reasoning behaviors appearing from pure RL. However, it is theoretically a biased estimator (REINFORCE++), requires verifiable rewards, and needs substantial compute for multi-sample generation. ^[sft-vs-rl-comprehensive-comparison.md]

## The Elicitation Theory

RL does not generate fundamentally new reasoning abilities beyond what exists in the base model. Base models at high pass@k can solve everything RL models solve at pass@1. RL redistributes probability mass and organizes latent micro-skills into coherent strategies. ^[sft-vs-rl-comprehensive-comparison.md]

The implication is that if the base model cannot solve a problem at all (even with many attempts), RL will not help. In such cases, it's better to invest in better pretraining or distillation from a stronger model instead. However, DeepSeek-R1-Zero shows RL can organize latent capabilities into novel reasoning strategies, serving as amplifier and organizer rather than teacher. ^[sft-vs-rl-comprehensive-comparison.md]

## Industry Evidence

### Successes

Industry successes include InstructGPT (2022) where 1.3B RLHF was preferred over 175B GPT-3, Claude's Constitutional AI achieving harmlessness without human harm labels, DeepSeek-R1 (2025) where pure RL produced emergent reasoning published in Nature, Llama 3.1's iterative SFT → Rejection Sampling → DPO pipeline, and Self-Rewarding LLMs where 3 iterations of self-reward outperformed Claude 2, Gemini Pro, and GPT-4 0613. ^[sft-vs-rl-comprehensive-comparison.md]

### Failures

Industry failures include length bias exploitation where RLHF improvements were "largely driven by increasing response length," reward overoptimization where gold reward follows inverted-U as proxy optimization increases, SFT being insufficient for self-correction due to distribution mismatch between training errors and model's own errors, mode collapse where training without KL penalty produces gibberish that fools reward model, and DPO reducing likelihood of preferred examples. ^[sft-vs-rl-comprehensive-comparison.md]

## Compute and Data Requirements

### Compute Comparison

SFT requires 1x baseline compute with 1 model in memory. DPO requires 1.5-2x compute with 2 models (policy + reference). GRPO requires 2-3x compute with 1 model plus sampling overhead. PPO/RLHF requires 4-6x compute with 4 models (policy, reference, reward, value). Online iterative DPO requires 3-4x compute with 2 models plus generation cycles. ^[sft-vs-rl-comprehensive-comparison.md]

### Data Requirements

SFT requires 10K-100K demonstrations. RLHF requires ~50K preference pairs for reward model training. DPO requires 10K-100K preference pairs. GRPO requires unlimited prompts with verifiable rewards (self-generated). RFT requires hundreds to thousands of prompts with rubrics. ^[sft-vs-rl-comprehensive-comparison.md]

## What RL Unlocks That SFT Cannot

RL enables simultaneous accuracy and diversity improvement, self-correction ability (SCoRe RL improves by 15.6% on MATH vs SFT), long [[Chain-of-Thought Reasoning]] with backtracking, exploration beyond training data distribution, and optimization of evaluator-defined properties. ^[sft-vs-rl-comprehensive-comparison.md]
