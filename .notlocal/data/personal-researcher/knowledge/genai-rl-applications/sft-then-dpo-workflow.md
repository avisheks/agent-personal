---
title: "SFT-then-DPO Workflow"
summary: "A recommended two-stage fine-tuning approach where Supervised Fine-Tuning establishes a robust initial policy before applying Direct Preference Optimization for enhanced alignment and performance."
sources:
  - genai-rl-applications/fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md
  - sft-vs-dpo/fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md
createdAt: 2026-05-24T12:50:39.397818+00:00
updatedAt: 2026-05-24T12:50:39.397818+00:00
---
# SFT-then-DPO Workflow

The **SFT-then-DPO Workflow** is a recommended two-stage fine-tuning approach that combines [[Supervised Fine-Tuning (SFT)]] followed by [[Direct Preference Optimization (DPO)]] to achieve superior model alignment and performance compared to using either technique in isolation.

## Overview

The SFT-then-DPO workflow involves first performing [[Supervised Fine-Tuning (SFT)]] on a subset of preferred responses, then using the SFT fine-tuned model as the starting point to apply [[Direct Preference Optimization (DPO)]] using preference comparison data. This sequential approach leverages the strengths of both techniques to create more robust and well-aligned language models. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

## Methodology

### Stage 1: Supervised Fine-Tuning

The first stage employs traditional supervised learning using input-output pairs to adjust model parameters. The training process adjusts model weights to minimize the difference between predicted and target outputs across the provided examples, with the model replicating features found in the provided pairs. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

### Stage 2: Direct Preference Optimization

The second stage uses the SFT model as a foundation and applies [[Direct Preference Optimization (DPO)]] with pairwise comparisons (preferred and rejected example responses) to optimize the model to favor certain outputs over others. The model learns to replicate the preference patterns found in the provided comparison data. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

## Benefits

The SFT-then-DPO workflow provides several key advantages over using either technique independently:

### Enhanced Model Alignment

Performing [[Supervised Fine-Tuning (SFT)]] before [[Direct Preference Optimization (DPO)]] enhances model alignment and overall performance by establishing a robust initial policy, ensuring the model already prefers correct responses. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

### Training Stability

This approach reduces the magnitude of weight updates during DPO, stabilizing training and preventing overfitting by allowing DPO to efficiently refine subtle nuances. The combined workflow converges faster and yields higher-quality results. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

### Improved Performance

The sequential application allows DPO to focus on preference alignment rather than basic task learning, leading to more nuanced and contextually appropriate model outputs. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

## Implementation Considerations

When implementing the SFT-then-DPO workflow, practitioners should consider the quality and consistency of their preference datasets. The volume of data required for DPO depends on the use case, with thousands to tens of thousands of examples generally being better. For preference pairs, the ordering logic should be consistent (if A > B and B > C, then A > C). ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

## Use Cases

The SFT-then-DPO workflow is particularly effective for applications requiring both task competency and preference alignment, such as:

- Customer service assistants that need to maintain brand voice and tone
- Content generation systems requiring specific stylistic preferences
- Conversational AI systems that must balance helpfulness with safety considerations

The workflow excels in scenarios where response quality is subjective and cannot be measured objectively, or when nuanced criteria such as tone, style, appropriateness, or clarity matter. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]

## Alternative Approaches

While the SFT-then-DPO workflow is recommended by OpenAI, practitioners may choose to apply DPO directly without the initial SFT stage depending on their specific use case. However, the combined approach typically yields superior results due to the foundational benefits provided by the initial supervised fine-tuning stage. ^[fine-tuning-techniques-choosing-between-sft-dpo-and-rft-with-a-guide-to-dpo.md]
