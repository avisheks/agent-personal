---
title: MoE SFT Failure Modes — Why GPT-OSS-120B Might Not Improve After SFT
url: https://arxiv.org/abs/2407.01906
ingestedAt: 2026-06-07
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2305.14705
  - https://arxiv.org/abs/2305.14314
  - https://arxiv.org/abs/2501.12948
  - https://arxiv.org/abs/2402.03300
  - https://arxiv.org/abs/2503.01307
  - https://arxiv.org/abs/2402.12354
  - https://huggingface.co/blog/moe
  - https://huggingface.co/blog/mixtral
  - https://docs.together.ai/docs/fine-tuning-models
---

# MoE SFT Failure Modes and Remediation

## Why SFT on GPT-OSS-120B (MoE, 128 experts, top-4, 5.1B active) might not improve

### MoE-Specific Failure Modes

1. **Routing disruption**: ESFT paper (arXiv:2407.01906) shows routing distribution for a specific task is highly concentrated in ~5-15% of experts. Training ALL parameters degrades specialization of non-relevant experts.

2. **Gradient dilution**: With top-4 of 128 experts, each expert receives gradient from ~3% of tokens. At 5K samples, each expert sees ~150 effective samples — insufficient.

3. **MLP layers don't respond to LoRA**: HuggingFace Mixtral guidance: "one should not target the MLP layers as they are sparse and don't interact well with PEFT."

4. **ST-MoE freezing paradox**: Freezing MoE layers and updating everything else works "almost as well as updating all parameters." Updating only MoE layers causes "huge performance drop."

5. **MoE overfits faster**: "Sparse models are more prone to overfitting than dense models" (HuggingFace MoE blog).

### General Failures Amplified by MoE

- 5K samples too small — MoE models need MORE data and MORE task diversity than dense
- Single-task data doesn't engage routing properly
- Learning rate possibly too low (MoE needs higher LR)
- MXFP4 precision may limit gradient fidelity for LoRA

### ESFT Key Finding

Only train task-relevant experts (identified via routing analysis):
- ESFT-Token method: train experts with top_p=0.1-0.2 of cumulative routing score
- Preserves general ability while improving specialized ability
- Fine-grained models (128 experts) MORE suitable for ESFT than coarse (8 experts)
- Random expert selection degrades 2.8-20.4 points vs informed selection

## Distillation vs RL Decision

### Use distillation when:
- pass@k is low (capability doesn't exist in weights)
- Strong teacher available
- Need to instill new knowledge/patterns

### Use RL when:
- pass@k is high (model knows but is inconsistent)
- Verifiable reward signal exists
- Want to improve reliability without new knowledge

### Proven pipeline: Distill → RL
- DeepSeek-R1: SFT cold start → GRPO
- GPT-OSS-120B model card: "trained using large-scale distillation and reinforcement learning"
- STaR paper: RL requires pre-existing reasoning behaviors; prime with SFT first

## Practical Next Steps (Decision Tree)

1. Test pass@100 on base model → determines if capability is latent
2. If low pass@k: distill from teacher (50-100K demos with CoT)
3. If high pass@k: apply DPO (generate preference pairs from correct vs incorrect)
4. In both cases: target attention layers only, not MLP/expert layers
5. Scale data to 50K+ with task diversity
6. Use higher learning rate (2e-4 to 5e-4)
