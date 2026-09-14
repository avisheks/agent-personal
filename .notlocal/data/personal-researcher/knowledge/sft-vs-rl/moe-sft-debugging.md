---
title: MoE SFT Debugging — Why Fine-Tuning Fails and What To Do
summary: MoE models (GPT-OSS-120B) fail under standard SFT because LoRA targets MLP/expert layers that don't respond to PEFT, gradient is diluted across 128 experts, and 5K samples is insufficient for sparse routing. Fix by targeting attention-only, scaling to 50K+, or switching to distillation/RL.
sources:
  - sources/sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-07
updatedAt: 2026-06-07
---

# MoE SFT Debugging — Why Fine-Tuning Fails and What To Do

## Root Causes (Priority Order)

1. **LoRA targeting MLP/expert layers** — HuggingFace: "one should not target the MLP layers as they are sparse and don't interact well with PEFT." Switch to attention layers only (q/k/v/o projections).

2. **Insufficient data for MoE** — With top-4 of 128 experts, each expert gets gradient from ~3% of tokens. At 5K samples, ~150 effective samples per expert. Need 50K+ with task diversity.

3. **No task diversity** — MoE routing engages different expert subsets per task. Single-task data activates the same ~10 experts repeatedly, leaving the rest untrained. Use 5-10 related tasks.

4. **MXFP4 precision floor** — 4-bit expert weights may limit gradient fidelity, though model was trained at this precision.

5. **Wrong method entirely** — If model already has latent capability (check pass@k), SFT is wrong. Use DPO/GRPO.

## Diagnostic Steps

### Step 1: pass@k Test

Generate 100 samples per problem at T=0.8 from base model. If pass@100 is high → model knows the answer, just needs reliability → use RL. If pass@100 is low → capability doesn't exist → use distillation.

### Step 2: Overfit Test

Train on 100 examples for many epochs. Can't memorize → architecture/precision problem. Memorizes but doesn't generalize → data problem.

### Step 3: Dense Comparison

Fine-tune Llama-3.1-8B (similar active compute) on same data. If it improves → MoE-specific issue.

## Decision Tree

```
pass@100 high? → DPO/GRPO (improve reliability)
pass@100 low? → Teacher (Claude/GPT-4) can do it?
    YES → Distill 50-100K demos → then DPO
    NO  → Task too hard for this model
```

## MoE-Specific Fixes

| Fix | What It Does | Evidence |
|-----|-------------|----------|
| Target attention only | Avoids sparse MLP layers that resist PEFT | HuggingFace Mixtral blog |
| ESFT (expert-specific) | Train only task-relevant experts (top_p=0.1-0.2) | arXiv:2407.01906 |
| Higher learning rate | MoE benefits from 2-5e-4 vs typical 1-2e-4 | HuggingFace MoE blog |
| More diverse data | Engages routing across expert subsets | arXiv:2305.14705 |
| Freeze router | Router doesn't need to change; prevents instability | ST-MoE research |

## Distillation vs RL Framework

| Axis | → Distillation | → RL (DPO/GRPO) |
|------|---------------|-----------------|
| Latent capability | Low (pass@k low) | High (pass@k high) |
| Teacher available | Yes (Claude/GPT-4) | Not needed |
| Reward signal | Hard to verify | Verifiable (code, math) |
| Data needed | 50-100K teacher demos | Preference pairs or verifier |
| MoE advantage | CoT generates more tokens → more experts get gradient | Optimizes output quality → respects existing routing |

## Recommended Pipeline for GPT-OSS-120B

```
1. Distill from teacher (50-100K samples with full CoT)
2. SFT with LoRA targeting attention layers only, rank=64, LR=3e-4
3. Follow with DPO using preference pairs (correct vs incorrect outputs)
4. Together AI supports this: SFT → DPO → deploy
```

## Related

- [[SFT vs RL Decision Framework]]
- [[Industry Successes and Failures: SFT vs RL]]
- [[Low-Rank Adaptation (LoRA)]]
- [[Attention Layer Targeting in LoRA]]
- [[GPT-OSS-120B]]
