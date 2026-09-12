---
title: "Semantic Anchors"
summary: "Pure, immutable reference points generated from diverse text descriptions that serve as external ground truth independent of potentially corrupt training labels."
sources:
  - fine-tuning-noisy-labels/cvpr-poster-tango-text-anchored-guided-optimization-for-robust-fine-tuning-vision-language-models-under-label-noise.md
createdAt: 2026-05-20T03:00:38.783577+00:00
updatedAt: 2026-05-20T03:00:38.783577+00:00
---
# Semantic Anchors

**Semantic Anchors** are pure, immutable reference points generated from diverse text descriptions that serve as an external source of ground truth for training vision-language models. They provide a way to establish reliable semantic references that are independent of potentially corrupted training data labels. ^[cvpr-poster-tango.md]

## Overview

Semantic anchors represent a novel approach to handling label noise in vision-language model training by leveraging the text modality to create clean reference points. Unlike traditional methods that rely on self-referential loops using a model's own predictions, semantic anchors establish ground truth that is fully independent of the training data's potentially corrupt labels. ^[cvpr-poster-tango.md]

## Key Characteristics

Semantic anchors possess several important properties:

- **Purity**: They are generated from clean text descriptions rather than noisy training labels
- **Immutability**: Once established, they remain fixed throughout the training process
- **Diversity**: They are created from varied text descriptions to capture different semantic aspects
- **Independence**: They provide ground truth that is separate from potentially corrupted training data ^[cvpr-poster-tango.md]

## Applications in Vision-Language Models

### Text-Anchored Classification

Semantic anchors enable the replacement of conventional linear classifiers with parameter-free Text-Anchored Classifiers. In this approach, predictions are made through a direct, weighted consensus of the clean anchors rather than through learned parameters that might be influenced by noisy labels. ^[cvpr-poster-tango.md]

### Label Validation and Correction

The anchors serve as an external ground truth for validating training samples' given labels. This validation process provides a more robust signal for sample selection and [[Label Noise Filtering|label correction]] compared to methods that rely solely on the model's own predictions. ^[cvpr-poster-tango.md]

## Implementation Framework

Semantic anchors are implemented within the TANGO (Text-Anchored Guided Optimization) framework, which reframes two key aspects of learning with noisy labels:

1. **Classification Mechanism**: Replacing traditional linear classifiers with anchor-based consensus systems
2. **Refinement Process**: Using anchor-guided mechanisms to validate and correct labels during training ^[cvpr-poster-tango.md]

## Advantages Over Traditional Approaches

The semantic anchor approach offers several benefits over conventional noise-handling methods:

- **External Ground Truth**: Provides validation independent of potentially corrupted training data
- **Cross-Modal Leverage**: Utilizes text modality information beyond simple noise detection
- **Robust Reference Points**: Maintains clean semantic references throughout the training process ^[cvpr-poster-tango.md]

## Related Concepts

Semantic anchors are particularly relevant in the context of [[Supervised Fine-Tuning (SFT)]] of vision-language models, where [[Label Noise Filtering]] and robust training methods are essential for achieving good performance on specialized tasks.
