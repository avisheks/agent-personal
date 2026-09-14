---
title: "Cross-Modal Noise Detection"
summary: "The use of information from multiple modalities (vision and text) to identify and handle label noise in training datasets."
sources:
  - fine-tuning-noisy-labels/cvpr-poster-tango-text-anchored-guided-optimization-for-robust-fine-tuning-vision-language-models-under-label-noise.md
createdAt: 2026-05-20T03:01:14.370540+00:00
updatedAt: 2026-05-20T03:01:14.370540+00:00
---
# Cross-Modal Noise Detection

Cross-modal noise detection refers to techniques that leverage information from multiple modalities (such as text and vision) to identify and handle noisy or incorrect labels in training datasets. This approach represents an advancement over traditional single-modal methods by utilizing the complementary nature of different data modalities to improve noise identification accuracy.

## Overview

Traditional approaches to learning with noisy labels typically rely on a self-referential loop, using a model's own predictions to correct errors. However, recent Vision-Language Model (VLM)-specific methods have begun to leverage cross-modal information to aid in noise detection, moving beyond the limitations of single-modal approaches. ^[cvpr-poster-tango.md]

The core principle behind cross-modal noise detection is that different modalities can provide independent sources of validation for label correctness. When labels in one modality are corrupted, information from another modality can serve as a more reliable reference point for identifying and correcting these errors.

## Applications in Vision-Language Models

In the context of [[Supervised Fine-Tuning (SFT)]] for Vision-Language Models, cross-modal noise detection has become particularly important due to the prevalence of label noise in real-world datasets. Fine-tuning large-scale Vision-Language Models is crucial for specialized tasks, but their performance is often undermined by the label noise prevalent in real-world datasets. ^[cvpr-poster-tango.md]

Recent approaches explore using the text modality not just to identify noise, but to establish a source of ground truth that is fully independent of the training data's potentially corrupt labels. This represents a significant departure from traditional methods that remain dependent on the potentially corrupted training data itself. ^[cvpr-poster-tango.md]

## Technical Approaches

### Text-Anchored Methods

One approach to cross-modal noise detection involves establishing "semantic anchors" - pure, immutable reference points generated from diverse text descriptions. These anchors serve as an external ground truth source that is independent of the training data's labels, providing a more robust foundation for noise detection and correction. ^[cvpr-poster-tango.md]

### Cross-Modal Validation

Cross-modal noise detection systems typically implement validation mechanisms that check each sample's given label against information from alternative modalities. This cross-modal validation provides a more robust signal for sample selection and [[Label Noise Filtering]], as it does not rely solely on the model's own predictions or the potentially corrupted training labels. ^[cvpr-poster-tango.md]

## Related Concepts

Cross-modal noise detection is closely related to several other techniques in machine learning:

- [[Multi-Annotator Label Aggregation]] - combining labels from multiple sources
- [[LLM-Based Label Correction]] - using language models to correct noisy labels  
- [[Noise-Aware Fine-Tuning]] - training methods that account for label noise
- [[Noisy SME Label Supervision]] - handling noise in subject matter expert annotations

## Performance Benefits

Extensive experiments demonstrate that cross-modal noise detection approaches can achieve competitive and often state-of-the-art performance compared to traditional single-modal methods. The key advantage lies in the independence of the validation signal from the potentially corrupted training data, leading to more reliable noise identification and correction. ^[cvpr-poster-tango.md]
