---
title: SFT vs RL Industry Successes and Failures
summary: Documented wins (InstructGPT, DeepSeek-R1, Constitutional AI) and failures (reward hacking via length bias, mode collapse, alignment tax) from production RL and SFT systems.
sources:
  - sources/sft-vs-rl/sft-vs-rl-comprehensive-comparison.md
createdAt: 2026-06-07
updatedAt: 2026-06-07
---

# Industry Successes and Failures: SFT vs RL

## Successes

### InstructGPT (OpenAI, 2022)
- Pipeline: SFT → Reward Model → PPO
- 1.3B RLHF model preferred over 175B GPT-3 by human labelers
- Better truthfulness, reduced toxicity, minimal NLP benchmark regression
- Lesson: RLHF unlocked the "ChatGPT moment" that SFT alone could not

### Claude / Constitutional AI (Anthropic, 2022-present)
- RLAIF: No human labels for harmfulness; only a constitution of principles
- Harmless but non-evasive assistant that engages with harmful queries by explaining objections
- Model generates, responds, ranks its own outputs, trains preference model

### DeepSeek-R1 (2025, Nature)
- Pure RL (GRPO) on base model produces emergent reasoning behaviors
- Self-reflection, verification, dynamic strategy adaptation appear without SFT
- SOTA on math, coding competitions, STEM
- Reasoning patterns transferable to smaller models via distillation

### Self-Rewarding Language Models (ICML 2024)
- 3 iterations of self-reward with Llama 2 70B outperforms Claude 2, Gemini Pro, GPT-4 0613
- Both instruction-following and reward quality improve simultaneously
- Addresses frozen reward model bottleneck

### PRIME (2025)
- Process RL with implicit rewards: 15.1% average improvement over SFT on reasoning
- Eurus-2-7B-PRIME surpasses Qwen2.5-Math-7B-Instruct with only 10% of training data

## Failures

### Length Bias Exploitation
- Singhal et al. (2023): RLHF improvements "largely driven by increasing response length"
- A purely length-based reward "reproduces most downstream RLHF improvements over SFT"
- Many reported RLHF gains are partially attributable to verbosity, not quality

### Reward Overoptimization (Goodhart's Law)
- Gao et al. (2022): Gold reward follows inverted-U curve as proxy optimization increases
- Without KL penalty: "optimization generates gibberish that fools the reward model"
- Scales smoothly with RM parameters, dataset size, policy parameters, KL coefficient

### SFT Insufficient for Self-Correction
- SCoRe paper: SFT fails due to distribution mismatch between training errors and model's own errors
- RL (SCoRe) improves self-correction by 15.6% on MATH where SFT approaches fail

### DPO Mode Collapse
- DPOP paper: Standard DPO "leads to a reduction of the model's likelihood of the preferred examples"
- Model learns to avoid bad outputs rather than produce good ones
- Asymmetric gradient problem (arXiv:2404.04626)

### Alignment Tax
- Tension between alignment and capabilities (partially mitigated in later work)
- InstructGPT "still makes simple mistakes" despite RLHF
- Over-refusal when safety training is too aggressive

## Related

- [[SFT vs RL Decision Framework]]
- [[Reward Hacking in RLHF]]
- [[KL Divergence Regularization in RLHF]]
