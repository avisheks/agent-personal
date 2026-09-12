---
title: "GPT-OSS-120B not improving after SFT on 5K samples — reasons, next steps, distillation vs RL?"
summary: "Most likely cause: LoRA targeting MLP/expert layers (don't respond to PEFT in MoE) + 5K samples insufficient for 128-expert routing. Fix: attention-only LoRA, scale to 50K+, or switch to distillation→DPO pipeline. Use pass@k to decide distillation (low) vs RL (high)."
type: query
createdAt: 2026-06-07
topic: sft-vs-rl
---

# GPT-OSS-120B Not Improving After SFT on 5K Samples

## Why It's Not Working (Most Likely → Least Likely)

### 1. LoRA Targets Wrong Layers
HuggingFace Mixtral guidance: **"one should not target the MLP layers as they are sparse and don't interact well with PEFT."** GPT-OSS-120B has 128 MoE experts in the FFN/MLP layers. If LoRA targets these, gradients are diluted across experts that are only active ~3% of the time.

**Fix:** Target attention layers only (q_proj, k_proj, v_proj, o_proj).

### 2. Data Insufficient for MoE Routing
With top-4 of 128 experts, each expert receives gradient from ~3% of training tokens. At 5K samples, each expert sees ~150 effective gradient updates. MoE models need **more data AND more task diversity** than dense models to properly engage routing.

**Fix:** Scale to 50K+ samples with 5-10 related task types.

### 3. Single-Task Data Doesn't Engage Router
MoE routing concentrates: "the routing distribution for a specific task tends to be highly concentrated" in 5-15% of experts (ESFT paper). Single-task data leaves 85%+ of experts untouched.

**Fix:** Add diverse auxiliary tasks. Or use ESFT approach — identify and train only the relevant expert subset.

### 4. Learning Rate Too Low
MoE models benefit from higher learning rates than dense models. Try 2e-4 to 5e-4 instead of the typical 1e-4.

### 5. Capability Doesn't Exist (Wrong Method)
If the base model can't produce correct outputs even at pass@100 sampling, SFT alone won't create the capability. Need distillation from a stronger model.

## Diagnostic Protocol

| Step | Test | Outcome → Action |
|------|------|-----------------|
| 1 | pass@100 at T=0.8 on base model | High → use DPO. Low → distill from teacher |
| 2 | Overfit on 100 examples | Can't memorize → architecture/precision issue. Memorizes → data problem |
| 3 | Same data on Llama-3.1-8B | Dense improves, MoE doesn't → MoE-specific issue |
| 4 | Check routing entropy before/after | Decreased → expert collapse. Stable → not a routing issue |

## Distillation vs RL Decision

```
pass@100 high on your task?
├── YES → DPO/GRPO
│         Model already knows; just needs reliability
│         Generate preference pairs (correct vs incorrect outputs)
│         Apply DPO on Together AI (supported natively)
│
└── NO → Teacher (Claude/GPT-4) can do it?
    ├── YES → Distill
    │         Generate 50-100K demos with full chain-of-thought
    │         SFT with LoRA on attention layers, rank=64, LR=3e-4
    │         Then DPO on top
    │
    └── NO → Task too hard for 5.1B active params
              Consider using GPT-OSS-120B at "high" reasoning
              Or use a larger/denser model
```

## Recommended Pipeline

```bash
# Stage 1: Distill from teacher
# Use Claude/GPT-4 to generate 50K demonstrations with CoT reasoning
# Save as JSONL with prompt + full reasoning + answer

# Stage 2: SFT on Together AI
# Config: LoRA rank=64, attention-only, LR=3e-4, batch=2, grad_accum=8
# Data: 50K distilled demos, 1-2 epochs

# Stage 3: DPO refinement
# Generate outputs from Stage 2 model
# Score with verifier → create preference pairs
# Apply DPO via Together AI --from-checkpoint
```

## Key Numbers

| Parameter | Value | Source |
|-----------|-------|--------|
| Active params per token | 5.1B of 117B | Model card |
| Experts activated | 4 of 128 (top-4) | Model card |
| Gradient coverage per expert | ~3% of tokens | Calculated |
| Effective samples per expert at 5K | ~150 | Calculated |
| Minimum data for MoE fine-tuning | 50K+ (diverse) | HuggingFace MoE blog |
| ESFT expert relevance | 5-15% of experts per task | arXiv:2407.01906 |
| Together AI max LoRA rank | 64 | docs.together.ai |

## Sources

- [[MoE SFT Debugging — Why Fine-Tuning Fails and What To Do]]
- [[SFT vs RL Decision Framework]]
- ESFT (arXiv:2407.01906), HuggingFace MoE blog, DeepSeek-R1 (arXiv:2501.12948)
- Together AI docs (fine-tuning-models, DPO support for GPT-OSS-120B)
