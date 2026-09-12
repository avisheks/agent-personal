---
title: "SFT vs RL? pros and cons? when to do what? what are some successes and failures from industry use cases?"
summary: "SFT is simple/cheap/stable but bounded by demo quality. RL unlocks holistic optimization (safety, reasoning) and can exceed SFT ceiling. InstructGPT, DeepSeek-R1, Constitutional AI are successes; reward hacking via length bias, mode collapse, overoptimization are documented failures. Industry standard is SFT+RL pipeline."
type: query
createdAt: 2026-06-07
topic: sft-vs-rl
---

# SFT vs RL: Pros, Cons, Decision Framework, Industry Cases

## Quick Answer

**SFT** is simple, stable, and cheap — but bounded by demonstration quality. **RL** (RLHF, DPO, GRPO) can exceed that ceiling by optimizing holistic properties, but adds complexity, instability, and reward hacking risk. The industry standard is **SFT then RL** — SFT provides a strong initialization, RL refines on top.

## Pros and Cons

| Dimension | SFT | RL (RLHF/DPO/GRPO) |
|-----------|-----|---------------------|
| Complexity | Simple (1 model, standard training) | Complex (2-4 models, generation loops) |
| Compute | 1x baseline | 1.5-6x depending on method |
| Stability | Very stable | Risk of reward hacking, mode collapse |
| Quality ceiling | Bounded by demonstrations | Can exceed demonstrations |
| Data needs | 10K-100K expert demos ($$$) | 10K-50K preference pairs or verifiable rewards |
| Best for | Format transfer, instruction following | Safety, reasoning, holistic quality |
| Failure mode | Smart copier (imitates, doesn't reason) | Reward hacking (length bias, Goodhart's law) |

## When to Use What

| Scenario | Approach | Cost |
|----------|----------|------|
| Format/style adaptation | SFT only | $ |
| Instruction following | SFT + DPO | $$ |
| Safety alignment | SFT + RLHF/RLAIF | $$$ |
| Math/code reasoning | SFT + GRPO/PRM | $$$ |
| Domain expertise | SFT + RFT (rubrics) | $$ |
| SOTA quality | SFT + online iterative RLHF | $$$$ |
| Budget-constrained | SFT + offline DPO | $$ |

## Key Industry Successes

1. **InstructGPT** (2022): 1.3B RLHF model preferred over 175B GPT-3
2. **DeepSeek-R1** (2025): Pure RL produces emergent reasoning; published in Nature
3. **Constitutional AI** (Anthropic): Harmless without human harm labels
4. **Self-Rewarding LLMs** (2024): 3 iterations outperforms Claude 2, Gemini Pro, GPT-4
5. **PRIME** (2025): Process RL gives 15.1% improvement over SFT with 10% of training data

## Key Industry Failures

1. **Length bias**: RLHF gains "largely driven by increasing response length" not quality
2. **Reward overoptimization**: Gold reward follows inverted-U; gibberish can score high
3. **Mode collapse**: DPO can reduce likelihood of preferred examples (DPOP paper)
4. **SFT insufficient for self-correction**: Distribution mismatch at inference time
5. **Alignment tax**: Aggressive safety training degrades capabilities

## The Elicitation Theory

RL does not teach new capabilities — it elicits and amplifies latent ones from the base model. If base model cannot solve at pass@k=infinity, RL won't either. RL redistributes probability mass, chains micro-skills, and makes rare correct behaviors reliable.

## Sources

- [[SFT vs RL Decision Framework]]
- [[Industry Successes and Failures: SFT vs RL]]
- InstructGPT (arXiv:2203.02155), DPO (arXiv:2305.18290), DeepSeek-R1 (arXiv:2501.12948)
- Reward overoptimization (arXiv:2210.10760), Length bias (arXiv:2310.03716)
- RLVR elicitation theory (arXiv:2504.13837)
