---
title: "Fill-in-Middle (FIM) Training"
summary: "A code-specific training technique that randomly masks middle portions of code sequences at 50% rate, enabling models to complete code given prefix and suffix context without harming autoregressive performance."
sources:
  - sft/sft-deep-dive-comprehensive.md
createdAt: 2026-06-15T11:56:22.218296+00:00
updatedAt: 2026-06-15T11:56:22.218296+00:00
---
# Fill-in-Middle (FIM) Training

**Fill-in-Middle (FIM) Training** is a specialized training technique used in code generation models where the model learns to predict missing code segments given surrounding context. Unlike traditional autoregressive training that predicts tokens sequentially from left to right, FIM training enables models to generate code in the middle of existing code blocks, making them more effective for code completion and editing tasks.

## Overview

FIM training addresses a fundamental limitation of standard autoregressive language models in code generation scenarios. While traditional models excel at generating code from the beginning of a file or function, they struggle with inserting code in the middle of existing contexts. FIM training solves this by teaching models to understand and generate code given both prefix (before) and suffix (after) context. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Training Methodology

### Data Preparation

FIM training requires restructuring code datasets into prefix-middle-suffix triplets. During training, code segments are randomly split into three parts: a prefix (beginning context), a middle section (target to predict), and a suffix (ending context). The model learns to predict the middle section given the prefix and suffix as input. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

### Training Rate and Performance Impact

Research shows that FIM training can be applied at a 50% rate during [[Supervised Fine-Tuning (SFT)]] without harming autoregressive performance. This means that half of the training examples use the FIM format while the other half maintain traditional left-to-right generation. This balanced approach ensures the model retains its ability to generate code sequentially while gaining fill-in-middle capabilities. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

### Special Modes

FIM training often incorporates specialized modes such as PSM (Prefix-Suffix-Middle) and SPM (Suffix-Prefix-Middle) to vary the order in which context is presented to the model. These variations help the model become more robust to different input formats and improve its ability to understand code structure regardless of how the context is arranged. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

## Applications in Code Generation

FIM training is particularly valuable for:

- **Code completion**: Filling in missing function bodies, variable assignments, or logic blocks
- **Code editing**: Inserting new functionality into existing codebases
- **Refactoring assistance**: Helping developers modify code while preserving surrounding context
- **Interactive development environments**: Enabling more natural code assistance in IDEs

## Integration with Modern Training Pipelines

FIM training is commonly integrated into the [[Supervised Fine-Tuning (SFT)]] phase of model development, particularly for code-focused models. It represents one of several application-specific quirks that have emerged in specialized fine-tuning approaches, alongside techniques for mathematical reasoning, chat interfaces, and tool use. ^[supervised-fine-tuning-for-llms-comprehensive-deep-dive.md]

The technique has become standard practice in training code generation models, as it significantly improves the practical utility of these models in real-world development scenarios without compromising their fundamental autoregressive capabilities.
