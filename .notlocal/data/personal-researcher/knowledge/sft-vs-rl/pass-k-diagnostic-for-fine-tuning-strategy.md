---
title: "Pass@k Diagnostic for Fine-Tuning Strategy"
summary: "A decision framework that uses pass@k metrics on base models to determine whether to use distillation (low pass@k) or reinforcement learning (high pass@k) for improvement."
sources:
  - sft-vs-rl/moe-sft-failure-modes-gpt-oss.md
createdAt: 2026-06-15T11:21:20.646209+00:00
updatedAt: 2026-06-15T11:21:20.646209+00:00
---
# Pass@k Diagnostic for Fine-Tuning Strategy

Pass@k is a diagnostic metric that measures whether a model has latent capabilities by evaluating how often it produces correct solutions when given multiple attempts. This metric serves as a critical decision point for choosing between different fine-tuning approaches, particularly for mixture-of-experts (MoE) models like [[GPT-OSS-120B]].

## Core Concept

Pass@k evaluates a model by generating k different responses to the same problem and measuring how many contain correct solutions. A high pass@k score indicates the model possesses the underlying capability but applies it inconsistently, while a low pass@k score suggests the capability is absent from the model's weights entirely. ^[moe-sft-failure-modes.md]

The diagnostic works by distinguishing between two fundamental problems: capability gaps (knowledge doesn't exist) versus consistency gaps (knowledge exists but is unreliably accessed). This distinction directly informs the choice between knowledge transfer methods like distillation and reliability improvement methods like reinforcement learning. ^[moe-sft-failure-modes.md]

## Decision Framework

### Low Pass@k Scenarios

When pass@k scores remain low even with many attempts (k=100), this indicates the model lacks the fundamental capability in its weights. The recommended approach is knowledge distillation from a stronger teacher model. This involves generating 50-100K demonstrations with [[chain-of-thought-reasoning]] from a more capable model and using [[supervised-fine-tuning-sft]] to transfer the knowledge. ^[moe-sft-failure-modes.md]

### High Pass@k Scenarios

High pass@k scores indicate the model possesses latent capabilities but applies them inconsistently. In these cases, reinforcement learning approaches like direct preference optimization (DPO) are more effective. The strategy involves generating preference pairs from correct versus incorrect model outputs and training the model to prefer the correct responses. ^[moe-sft-failure-modes.md]

## MoE-Specific Considerations

For [[mixture-of-experts-moe]] models, pass@k diagnostics become more complex due to routing dynamics. MoE models like [[GPT-OSS-120B]] with 128 experts and top-4 routing create additional failure modes that can mask true capabilities. ^[moe-sft-failure-modes.md]

### Routing Disruption Effects

MoE models concentrate routing for specific tasks in only 5-15% of experts. When fine-tuning updates all parameters, it can degrade the specialization of non-relevant experts, leading to apparent capability loss even when the underlying knowledge exists. This makes pass@k interpretation more nuanced for MoE architectures. ^[moe-sft-failure-modes.md]

### Gradient Dilution Impact

With top-4 routing across 128 experts, each expert receives gradients from only ~3% of tokens. At small dataset sizes like 5K samples, each expert sees approximately 150 effective samples, which is insufficient for learning. This can result in low pass@k scores that reflect training inadequacy rather than capability absence. ^[moe-sft-failure-modes.md]

## Proven Pipeline Integration

The most successful approach combines both strategies sequentially. Models like DeepSeek-R1 demonstrate the effectiveness of starting with SFT for cold-start capability building, followed by group relative policy optimization (GRPO) for consistency improvement. This aligns with the pass@k diagnostic: first address capability gaps through distillation, then improve reliability through reinforcement learning. ^[moe-sft-failure-modes.md]

The [[GPT-OSS-120B]] model card explicitly mentions training "using large-scale distillation and reinforcement learning," confirming this sequential approach. Research on self-taught reasoner (STaR) methods shows that reinforcement learning requires pre-existing reasoning behaviors, making the distill-then-RL pipeline particularly effective. ^[moe-sft-failure-modes.md]

## Implementation Guidelines

When applying pass@k diagnostics, several practical considerations emerge. Testing should use pass@100 on the base model to establish baseline capabilities. For MoE models, attention should focus on targeting attention layers only rather than MLP or expert layers, as sparse layers don't interact well with parameter-efficient fine-tuning methods. ^[moe-sft-failure-modes.md]

Data scaling becomes critical, with successful implementations requiring 50K+ samples with task diversity rather than small, single-task datasets. Learning rates may need adjustment upward (2e-4 to 5e-4) for MoE models compared to dense architectures. ^[moe-sft-failure-modes.md]
