---
title: "Sft Dpo"
source: "data/researcher/sft-dpo.md"
ingestedAt: "2026-05-17T23:21:54Z"
---
# Primer Resources for SFT, DPO, and GRPO

## Best Single Practical Primer

The best single primer is the Hugging Face TRL Quickstart / documentation:

- https://huggingface.co/docs/trl/quickstart

Why it’s good:
- Covers SFT, DPO, PPO, and GRPO in one ecosystem
- Includes runnable examples
- Explains trainer abstractions (`SFTTrainer`, `DPOTrainer`, etc.)
- Modern and actively maintained

---

## Foundational Papers

### 1. InstructGPT (SFT + RLHF Pipeline)

**Paper:**  
Training Language Models to Follow Instructions with Human Feedback  
(Ouyang et al., 2022)

Link:
- https://arxiv.org/abs/2203.02155

Why read it:
- Explains the canonical pipeline:
  1. Supervised Fine-Tuning (SFT)
  2. Reward modeling
  3. RLHF (PPO)

This is the foundation for understanding modern alignment training.

---

### 2. DPO Paper

**Paper:**  
Direct Preference Optimization: Your Language Model is Secretly a Reward Model  
(Rafailov et al., 2023)

Link:
- https://arxiv.org/abs/2305.18290

Why read it:
- Introduces DPO as a simpler alternative to PPO-based RLHF
- Shows how preference optimization can be done directly from chosen/rejected pairs
- Very important for understanding current post-training methods

---

### 3. GRPO Paper / Resource

**Paper:**  
DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

Link:
- https://arxiv.org/abs/2402.03300

Why read it:
- Introduces GRPO (Group Relative Policy Optimization)
- Important for reasoning-focused training
- Shows how grouped sampling and relative rewards improve optimization efficiency

---

## Recommended Learning Order

1. Read the InstructGPT paper (focus on SFT + RLHF sections)
2. Train a small SFT model using LoRA
3. Read the DPO paper
4. Implement DPO using TRL
5. Read the DeepSeekMath GRPO section
6. Compare:
   - SFT = imitation learning
   - DPO = preference optimization
   - GRPO = relative/group-based policy optimization

---

## Good Supplemental Resources

### Hugging Face Blog + Docs
- https://huggingface.co/blog
- https://huggingface.co/docs/trl

### Stanford CS324 / CS25 LLM Lectures
- https://stanford-cs324.github.io/winter2022/
- https://web.stanford.edu/class/cs25/

### Anthropic Alignment Posts
- https://www.anthropic.com/research

---

## Mental Model

A useful simplification:

- SFT:
  "Copy high-quality demonstrations"

- DPO:
  "Prefer better answers over worse ones"

- GRPO:
  "Improve policy relative to groups of sampled outputs"


========

# SFT vs DPO vs RLHF — Detailed Notes

## Quick Summary Table

| Aspect | SFT (Supervised Fine-Tuning) | DPO (Direct Preference Optimization) | RLHF (PPO-style) |
|---|---|---|---|
| Data format | `(x, y_good)` demonstrations | `(x, y_preferred, y_rejected)` pairwise comparisons | `(x, y)` + `reward(y|x)` |
| Core idea | Imitate target outputs via cross-entropy | Increase probability of preferred response vs rejected one | Optimize policy to maximize expected reward |
| Needs reward model? | No | No | Usually yes |
| Optimization method | Maximum likelihood / cross-entropy | Preference-margin / logistic loss | Policy gradient (PPO) |
| Pushes down bad outputs? | Not explicitly | Yes | Indirectly |
| Typical stability | Very stable | Stable | Less stable |
| Sample efficiency | High | High | Lower |
| When to use | Base competence / formatting | Preference alignment | True reward optimization |

---

# Conceptual Difference

## SFT

SFT trains the model to imitate demonstrations.

You tell the model:

> “Given this input, produce this output.”

### Example

Prompt:
```text
Recommend next best action for this Walmart Ads campaign.