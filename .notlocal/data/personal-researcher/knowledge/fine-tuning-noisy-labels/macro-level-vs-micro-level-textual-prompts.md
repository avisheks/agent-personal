---
title: "Macro-Level vs Micro-Level Textual Prompts"
summary: "Two complementary prompt types where macro-level uses simple class names for inter-class separability while micro-level incorporates detailed attributes like shapes and textures for more reliable image-text matching."
sources:
  - fine-tuning-noisy-labels/0568.md
createdAt: 2026-05-20T02:58:57.265262+00:00
updatedAt: 2026-05-20T02:58:57.265262+00:00
---
# Macro-Level vs Micro-Level Textual Prompts

**Macro-Level vs Micro-Level Textual Prompts** refers to a dual-level semantic matching approach used in vision-language models to improve label screening and classification accuracy, particularly in noisy label scenarios. This technique combines two distinct types of textual prompts that operate at different levels of semantic granularity to enhance model robustness and performance.

## Overview

The dual-level approach addresses limitations found when using single-type prompts for image-text matching tasks. Macro-level prompts ensure inter-class separability but are prone to overfitting noisy samples due to the simplicity of image-language matching. Micro-level prompts provide more reliable matching and reduce overfitting to noisy samples, but may cause underfitting on clean samples. The combination of both types creates a more effective screening mechanism that reduces overlap between clean and noisy samples in the loss space. ^[0568.md]

## Macro-Level Textual Prompts

Macro-level textual prompts follow the original CLIP design, using class name templates to generate broad categorical descriptions. For a given class j, the macro-level textual prompt is defined as:

```
Tmac_j = 'a photo of a {classj}.'
```

These prompts are processed through the text encoder along with learnable prompts to produce embedding vectors that represent each class at a high level of abstraction. The resulting class embeddings are used to compute probabilities representing the likelihood of a sample belonging to each class. ^[0568.md]

## Micro-Level Textual Prompts

Micro-level textual prompts incorporate class-specific features to enhance alignment between image and text embeddings. These prompts introduce detailed attributes such as shapes, textures, colors, and other unique characteristics of each class. For class j, the micro-level textual prompt is expressed as:

```
Tmic_j = 'a photo of a {class j}, which is/has {features of class j}.'
```

The text encoder processes these detailed prompts to produce micro-level embeddings that capture fine-grained semantic information. This approach provides more reliable matching compared to macro-level prompts alone, particularly in scenarios with label noise. ^[0568.md]

## Dual-Level Semantic Matching Mechanism

The dual-level approach combines both macro-level and micro-level prompts in a unified framework for improved label screening. The mechanism uses a sample-wise loss function composed of three key terms:

### Cross-Entropy Loss
Evaluates the discrepancy between predicted class probabilities from both prompt types and the observed label:

```
ℓce(xi, yi) = -∑[yi,j log(pmac_i,j) + yi,j log(pmic_i,j)]
```

### Consistency Constraint
Imposes agreement between predictions from macro-level and micro-level prompts using Jensen-Shannon divergence:

```
ℓcon(xi) = ∑[pmac_i,j log(pmac_i,j/pmic_i,j) + pmic_i,j log(pmic_i,j/pmac_i,j)]
```

### Entropy Penalty
Encourages confident predictions by penalizing overly smooth outputs:

```
ℓent(xi) = -∑[pmac_i,j log(pmac_i,j) + pmic_i,j log(pmic_i,j)]
```

The overall loss function combines these terms: `ℓ(xi, yi) = ℓce(xi, yi) + λℓcon(xi) + βℓent(xi)`, where λ and β are hyperparameters. ^[0568.md]

## Applications in Label Screening

The dual-level approach effectively reduces overlap between clean and noisy samples in the loss distribution, enabling more accurate tri-segment sample screening. This method categorizes samples into clean, ambiguous, and noisy classes, which is particularly valuable for [[Noisy SME Label Supervision]] and [[Label Noise Filtering]] applications.

Experimental results demonstrate that dual-level textual prompts significantly outperform single-level approaches in separating clean from noisy samples. The method shows particular effectiveness in high-noise scenarios, where traditional small-loss criteria struggle to maintain accuracy. ^[0568.md]

## Integration with Vision-Language Models

The dual-level approach integrates seamlessly with existing vision-language architectures, particularly CLIP-based models. The method requires minimal additional computational overhead while providing substantial improvements in robustness. The approach can be combined with other techniques such as [[Cross-Encoder Reranking]] and [[LLM-Based Label Correction]] for enhanced performance in noisy label scenarios. ^[0568.md]

## Performance Benefits

Extensive experiments across multiple datasets demonstrate that the dual-level semantic matching approach achieves superior performance compared to single-prompt methods. The technique shows particular strength in handling various noise types, including symmetric flip noise and pair flip noise, with improvements ranging from 8-10% in high-noise scenarios compared to baseline approaches. ^[0568.md]
