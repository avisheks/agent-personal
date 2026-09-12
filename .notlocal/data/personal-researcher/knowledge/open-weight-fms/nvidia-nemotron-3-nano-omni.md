---
title: "NVIDIA Nemotron 3 Nano Omni"
summary: "A 30B-A3B MoE model with 256K context supporting omnimodal processing across text, image, audio, and video modalities."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: 2026-06-15T12:03:05.847671+00:00
updatedAt: 2026-06-15T12:03:05.847671+00:00
---
# NVIDIA Nemotron 3 Nano Omni

**NVIDIA Nemotron 3 Nano Omni** is a multimodal [[mixture-of-experts-moe]] language model developed by NVIDIA as part of their Nemotron model family. The model features a 30B total parameter count with 3B active parameters and supports omnimodal capabilities across text, image, audio, and video inputs. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Architecture

Nemotron 3 Nano Omni utilizes a [[mixture-of-experts-moe]] architecture with 30 billion total parameters but only 3 billion active parameters during inference. This design allows the model to maintain high capability while reducing computational requirements compared to dense models of similar total parameter count. ^[open-weight-foundation-models-catalog-mid-2026.md]

The model supports a [[long-context-scaling]] window of 256K tokens, enabling processing of extended documents and conversations. Its omnimodal design allows it to handle multiple input modalities including text, images, audio, and video within a single unified architecture. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Capabilities

### Multimodal Processing

The model's key distinguishing feature is its omnimodal capability, supporting text, image, audio, and video inputs simultaneously. This makes it suitable for applications requiring cross-modal understanding and generation tasks. ^[open-weight-foundation-models-catalog-mid-2026.md]

### Context Length

With its 256K token context window, Nemotron 3 Nano Omni can process lengthy documents and maintain coherent conversations across extended interactions. This positions it among models with [[long-context-scaling]] capabilities. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Licensing and Availability

The model is released under the NVIDIA Open Model License, which permits commercial use. This licensing approach makes it accessible for both research and commercial applications while maintaining NVIDIA's terms of use. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Model Family Context

Nemotron 3 Nano Omni is part of NVIDIA's broader Nemotron model family, which includes other variants such as Nemotron-4-340B (a 340B dense model focused on synthetic data generation) and Llama-3.1-Nemotron-70B (a 71B dense model with 128K context). The Nano Omni variant represents NVIDIA's approach to creating efficient multimodal models through [[mixture-of-experts-moe]] architecture. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Positioning in the Ecosystem

Within the landscape of open-weight foundation models, Nemotron 3 Nano Omni occupies a unique position as one of the few omnimodal models available for fine-tuning. While other models like [[qwen3-language-model]] and [[gpt-oss-120b]] focus primarily on text or limited multimodal capabilities, Nemotron 3 Nano Omni's comprehensive multimodal support distinguishes it for applications requiring diverse input types. ^[open-weight-foundation-models-catalog-mid-2026.md]
