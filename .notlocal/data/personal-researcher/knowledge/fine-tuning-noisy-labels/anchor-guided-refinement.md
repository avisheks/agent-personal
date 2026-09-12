---
title: "Anchor-Guided Refinement"
summary: "A mechanism that validates each sample's given label against external semantic anchors to provide robust signals for sample selection and label correction."
sources:
  - fine-tuning-noisy-labels/cvpr-poster-tango-text-anchored-guided-optimization-for-robust-fine-tuning-vision-language-models-under-label-noise.md
createdAt: 2026-05-20T03:00:53.967665+00:00
updatedAt: 2026-05-20T03:00:53.967665+00:00
---
# Anchor-Guided Refinement

**Anchor-Guided Refinement** is a mechanism used in machine learning to validate and correct noisy labels by comparing them against external ground truth references called "semantic anchors." This approach provides a more robust signal for sample selection and label correction compared to traditional self-referential methods. ^[cvpr-poster-tango.md]

## Overview

Traditional approaches to learning with noisy labels typically rely on a self-referential loop, using a model's own predictions to correct errors. In contrast, Anchor-Guided Refinement establishes a source of ground truth that is fully independent of the training data's potentially corrupt labels. ^[cvpr-poster-tango.md]

The mechanism operates by validating each sample's given label against semantic anchors—pure, immutable reference points generated from diverse text descriptions. This external validation provides a more reliable foundation for identifying and correcting label noise than methods that depend solely on the model's internal representations. ^[cvpr-poster-tango.md]

## Implementation in TANGO Framework

Anchor-Guided Refinement is a core component of the **T**ext-**AN**chored **G**uided **O**ptimization (TANGO) framework, which is designed for robust fine-tuning of Vision-Language Models under label noise conditions. The mechanism works in conjunction with semantic anchors to reframe key aspects of learning with noisy labels. ^[cvpr-poster-tango.md]

In the TANGO framework, Anchor-Guided Refinement operates alongside a parameter-free Text-Anchored Classifier that makes predictions through direct, weighted consensus of clean anchors. This dual approach leverages the text modality not just to identify noise, but to establish an independent source of ground truth. ^[cvpr-poster-tango.md]

## Applications

The mechanism is particularly valuable for [[Supervised Fine-Tuning (SFT)]] scenarios where [[Label Noise Filtering]] is critical. It addresses challenges in fine-tuning large-scale Vision-Language Models where performance is often undermined by label noise prevalent in real-world datasets. ^[cvpr-poster-tango.md]

Anchor-Guided Refinement has demonstrated competitive and often state-of-the-art performance in experimental evaluations, making it a promising approach for robust model training under noisy conditions. ^[cvpr-poster-tango.md]

## Related Concepts

The mechanism relates to broader concepts in machine learning including [[Noisy SME Label Supervision]], [[Multi-Annotator Label Aggregation]], and [[LLM-Based Label Correction]]. It represents an evolution in approaches to handling label noise by incorporating external validation rather than relying solely on internal model consistency. ^[cvpr-poster-tango.md]
