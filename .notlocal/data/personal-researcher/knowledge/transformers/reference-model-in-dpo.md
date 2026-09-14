---
title: "Reference Model in DPO"
summary: "A frozen copy of the SFT checkpoint used in Direct Preference Optimization to prevent model collapse by ensuring preference learning doesn't deviate too far from reasonable language modeling."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:45:21.434228+00:00
updatedAt: 2026-06-16T14:45:21.434228+00:00
---
# Reference Model in DPO

A **reference model** in Direct Preference Optimization (DPO) is a frozen copy of the Supervised Fine-Tuning (SFT) checkpoint that serves as a baseline to prevent model collapse during preference learning. The reference model acts as an anchor point, ensuring that the model being trained doesn't deviate too drastically from reasonable language modeling behavior while learning human preferences.

## Purpose and Function

The reference model solves a critical problem in preference optimization known as the **collapse problem**. Without a reference point, a model trained to maximize the likelihood of chosen responses could find degenerate solutions by making certain phrases extremely likely across all contexts, regardless of appropriateness. ^[Large Language Model (LLM) Training - Intro - final.pdf]

For example, if the training data shows "Once upon a time, in a land far away..." was chosen for a creative writing prompt, the model might learn to use this phrase for all prompts—technical manuals, quantum physics explanations, horror stories—because it technically satisfies the objective of making chosen responses more likely. This destroys the model's ability to generate appropriate, diverse responses. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## How It Works

The reference model prevents collapse by serving as a comparison baseline in the DPO loss function. Instead of optimizing "make chosen responses likely," DPO optimizes "make chosen responses more likely than the reference model would, but don't deviate too much." ^[Large Language Model (LLM) Training - Intro - final.pdf]

The DPO loss function computes log probability ratios between the current model and the reference model:

- **Chosen log ratio**: `chosen_logprobs - ref_chosen_logprobs`
- **Rejected log ratio**: `rejected_logprobs - ref_rejected_logprobs`

Positive ratios indicate the current model likes a response more than the reference did; negative ratios indicate less preference. The loss function then optimizes for the chosen response to have a higher ratio than the rejected response, relative to what the reference model thought. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Technical Implementation

The reference model is created by making a frozen copy of the SFT checkpoint before beginning preference training. During DPO training, both models process the same inputs, but only the training model's weights are updated. The reference model's parameters remain fixed throughout the entire preference optimization process. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Memory Requirements

Using a reference model doubles the memory footprint for model weights during training. For a 32B parameter model, the memory breakdown becomes:

- Training model: 64GB
- Reference model: 64GB (frozen, no gradients)
- Gradients: 64GB
- AdamW optimizer state: 256GB
- Total: ~448GB plus activations ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Beta Parameter Control

The **beta parameter** in DPO controls the trade-off between preference learning strength and adherence to the reference model. A small beta (0.1) keeps the model very close to the SFT baseline, while a large beta (0.5) allows stronger preference learning but risks degrading response quality. This parameter effectively controls how much deviation from the reference model is acceptable. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Relationship to Other Techniques

The reference model concept is specific to [[Direct Preference Optimization (DPO)]] and distinguishes it from other preference learning approaches. In [[Reinforcement Learning from Human Feedback (RLHF)]] with [[PPO Training Policy]], a separate reward model is trained instead of using a reference model for comparison. The reference model approach in DPO eliminates the need for explicit reward model training while achieving similar preference alignment objectives. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Limitations and Considerations

While the reference model successfully prevents collapse, it assumes that the SFT checkpoint represents reasonable baseline behavior. If the SFT model itself has significant issues, the reference model will anchor those problems into the preference-optimized model. Additionally, the reference model approach works best when preferences can be captured through pairwise comparisons, but may be insufficient for complex multi-objective optimization scenarios. ^[Large Language Model (LLM) Training - Intro - final.pdf]
