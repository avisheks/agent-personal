---
title: "TANGO Framework"
summary: "A Text-Anchored Guided Optimization framework for robust fine-tuning of Vision-Language Models under label noise using semantic anchors as external ground truth."
sources:
  - fine-tuning-noisy-labels/cvpr-poster-tango-text-anchored-guided-optimization-for-robust-fine-tuning-vision-language-models-under-label-noise.md
createdAt: 2026-05-20T03:00:26.055431+00:00
updatedAt: 2026-05-20T03:00:26.055431+00:00
---
# TANGO Framework

TANGO (Text-Anchored Guided Optimization) is a framework designed for robust fine-tuning of [[Vision-Language Models]] under label noise conditions. The framework addresses the challenge of training large-scale Vision-Language Models (VLMs) on real-world datasets that contain noisy or incorrect labels, which can significantly undermine model performance on specialized tasks. ^[cvpr-poster-tango.md]

## Overview

Traditional approaches to learning with noisy labels typically rely on a self-referential loop, using a model's own predictions to correct errors. While recent VLM-specific methods have begun to leverage cross-modal information to aid in noise detection, TANGO explores an alternative direction by using the text modality not just to identify noise, but to establish a source of ground truth that is fully independent of the training data's potentially corrupt labels. ^[cvpr-poster-tango.md]

## Core Components

### Semantic Anchors

The TANGO framework is centered on "semantic anchors"—a set of pure, immutable reference points generated from diverse text descriptions. These anchors serve as clean, external ground truth references that are independent of the potentially noisy training labels. ^[cvpr-poster-tango.md]

### Text-Anchored Classifier

TANGO replaces the conventional linear classifier with a parameter-free Text-Anchored Classifier. This component makes predictions through a direct, weighted consensus of the clean anchors, eliminating the need for traditional classification parameters that might be corrupted by noisy training data. ^[cvpr-poster-tango.md]

### Anchor-Guided Refinement

The framework introduces an Anchor-Guided Refinement mechanism that validates each sample's given label against the external ground truth provided by the semantic anchors. This mechanism provides a more robust signal for sample selection and label correction compared to self-referential approaches. ^[cvpr-poster-tango.md]

## Applications

TANGO is specifically designed for fine-tuning large-scale Vision-Language Models on specialized tasks where label noise is prevalent in real-world datasets. The framework addresses the critical challenge of maintaining model performance when training data contains incorrect or corrupted labels. ^[cvpr-poster-tango.md]

## Performance

Extensive experiments demonstrate that TANGO achieves competitive and often state-of-the-art performance in robust fine-tuning scenarios. The framework's approach of using text-based semantic anchors as external ground truth provides superior robustness compared to traditional self-referential noise handling methods. ^[cvpr-poster-tango.md]
