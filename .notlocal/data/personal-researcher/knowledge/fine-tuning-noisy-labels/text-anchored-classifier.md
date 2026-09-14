---
title: "Text-Anchored Classifier"
summary: "A parameter-free classification approach that makes predictions through direct weighted consensus of clean semantic anchors rather than traditional linear classifiers."
sources:
  - fine-tuning-noisy-labels/cvpr-poster-tango-text-anchored-guided-optimization-for-robust-fine-tuning-vision-language-models-under-label-noise.md
createdAt: 2026-05-20T03:00:46.323789+00:00
updatedAt: 2026-05-20T03:00:46.323789+00:00
---
# Text-Anchored Classifier

A **Text-Anchored Classifier** is a parameter-free classification mechanism that replaces conventional linear classifiers in vision-language models by making predictions through a direct, weighted consensus of clean semantic anchors. This approach is designed to improve robustness when fine-tuning vision-language models under label noise conditions. ^[cvpr-poster-tango.md]

## Overview

The Text-Anchored Classifier operates by establishing predictions as a weighted consensus of pure, immutable reference points called "semantic anchors." These anchors are generated from diverse text descriptions and serve as a source of ground truth that is fully independent of potentially corrupt training data labels. ^[cvpr-poster-tango.md]

## Key Components

### Semantic Anchors

The classifier relies on semantic anchors—a set of pure, immutable reference points generated from diverse text descriptions. These anchors provide an external ground truth source that remains unaffected by label noise in the training dataset. ^[cvpr-poster-tango.md]

### Parameter-Free Design

Unlike conventional linear classifiers that require learned parameters, the Text-Anchored Classifier operates without trainable parameters. This design choice helps maintain the integrity of the classification process by avoiding potential corruption from noisy training signals. ^[cvpr-poster-tango.md]

## Integration with TANGO Framework

The Text-Anchored Classifier is a central component of the TANGO (Text-Anchored Guided Optimization) framework, which addresses [[Noisy SME Label Supervision]] challenges in [[Supervised Fine-Tuning (SFT)]] of vision-language models. The classifier works in conjunction with an Anchor-Guided Refinement mechanism that validates sample labels against the external ground truth provided by the semantic anchors. ^[cvpr-poster-tango.md]

## Applications

This classifier is particularly valuable for specialized tasks requiring fine-tuning of large-scale vision-language models where [[Label Noise Filtering]] is critical. The approach has demonstrated competitive and often state-of-the-art performance in handling label noise during the fine-tuning process. ^[cvpr-poster-tango.md]

## Related Concepts

The Text-Anchored Classifier represents an alternative to traditional [[LLM-Based Label Correction]] approaches that typically rely on self-referential loops using a model's own predictions. Instead, it leverages cross-modal information from text descriptions to establish an independent source of truth for classification decisions. ^[cvpr-poster-tango.md]
