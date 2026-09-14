---
title: "Vision-Language Model Fine-Tuning with Noisy Labels"
summary: "The challenge of adapting pre-trained vision-language models like CLIP to downstream tasks when training data contains mislabeled samples, requiring specialized techniques beyond conventional small-loss criteria."
sources:
  - fine-tuning-noisy-labels/0568.md
createdAt: 2026-05-20T02:59:12.830488+00:00
updatedAt: 2026-05-20T02:59:12.830488+00:00
---
# Vision-Language Model Fine-Tuning with Noisy Labels

Vision-Language Model Fine-Tuning with Noisy Labels refers to the challenge of adapting pre-trained [[vision-fine-tuning|vision-language models]] to downstream tasks when the training data contains incorrect or mislabeled samples. This problem is particularly relevant for models like CLIP that rely on image-text alignment for classification tasks. ^[0568.md]

## Problem Definition

The core challenge involves adapting a pre-trained vision-language model using training data {(xi, yi)}N where xi represents the i-th training sample, yi denotes the observed label (which may be incorrect), and N represents the total number of training images. The goal is to maintain model performance despite the presence of noisy labels that can cause the model to memorize incorrect patterns. ^[0568.md]

## Key Challenges

### Self-Confirmation Bias

Traditional approaches that rely on self-generated predictions to clean samples or assign pseudo labels suffer from self-confirmation bias, where prediction errors propagate and amplify during training. This occurs when the same model used for noise detection is also used for label correction. ^[0568.md]

### Limitations of Small-Loss Criteria

Conventional small-loss criteria, which assume that deep neural networks learn clean samples before noisy ones, fail to reliably distinguish clean samples from noisy ones in vision-language models, especially in ambiguous cases. The simple image-language matching in these models can lead to overfitting on noisy samples. ^[0568.md]

## Screening, Rectifying, and Re-Screening Framework

A unified approach to address noisy labels consists of three main steps: screening observed labels to identify potential mislabels, rectifying these labels for effective optimization, and re-screening to mitigate self-confirmation bias. ^[0568.md]

### Dual-Level Semantic Matching

This mechanism combines macro-level and micro-level textual prompts to better differentiate clean samples from noisy ones. Macro-level prompts use simple class name templates like "a photo of a {class}", while micro-level prompts incorporate detailed features such as shapes, textures, and colors. The combination reduces overlap between clean and noisy samples in the loss space. ^[0568.md]

### Tri-Segment Sample Classification

Rather than the traditional binary classification of samples into clean and noisy categories, a tri-segment approach categorizes samples into clean, ambiguous, and noisy classes. This accounts for the overlap between clean and noisy data distributions and enables more precise handling of uncertain samples. ^[0568.md]

### Label Rectification Strategies

Different strategies are applied based on sample classification:
- Clean samples retain their original labels
- Ambiguous samples receive a weighted combination of observed and pseudo labels
- Noisy samples are assigned pseudo labels generated from model predictions ^[0568.md]

### Cross-Validation with Auxiliary Models

To mitigate self-confirmation bias, an auxiliary vision-language model (such as BLIP) is used for cross-validation of rectified labels. This provides an independent assessment of label quality and enhances the robustness of the label correction process. ^[0568.md]

## Training Objectives

The framework employs a composite loss function that includes:
- Cross-entropy loss for standard classification
- Consistency constraints between macro-level and micro-level predictions
- Entropy penalty terms to encourage confident predictions ^[0568.md]

High-quality samples identified through re-screening are used directly for [[prompt-template-encoding|prompt learning]], while lower-quality samples undergo data augmentation techniques like mixup to minimize the influence of remaining label errors. ^[0568.md]

## Applications and Performance

This approach has been evaluated across multiple datasets including Flowers102, EuroSAT, StanfordCars, OxfordPets, DTD, Caltech101, UCF101, Food101, ImageNet, and SUN397. The method demonstrates superior performance compared to existing approaches, particularly under high noise conditions where traditional methods struggle significantly. ^[0568.md]

The framework shows particular effectiveness in extreme scenarios, such as datasets with 100% label noise, where it maintains reasonable performance while other methods fail completely. This robustness makes it valuable for real-world applications where [[Noisy SME Label Supervision|label quality]] cannot be guaranteed. ^[0568.md]
