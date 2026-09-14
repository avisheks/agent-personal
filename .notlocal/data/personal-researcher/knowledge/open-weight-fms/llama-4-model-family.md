---
title: "Llama 4 Model Family"
summary: "Meta's latest generation featuring Scout (109B MoE) and Maverick (400B MoE) with multimodal capabilities and extended context lengths up to 10M tokens."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: 2026-06-15T12:01:54.821770+00:00
updatedAt: 2026-06-15T12:01:54.821770+00:00
---
# Llama 4 Model Family

The **Llama 4 Model Family** is Meta's latest generation of open-weight large language models, representing a significant advancement in multimodal capabilities and architectural efficiency. The family consists of two primary variants that utilize mixture-of-experts (MoE) architecture to achieve frontier performance while maintaining computational efficiency. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Model Variants

### Llama 4 Scout
Llama 4 Scout is the smaller variant in the family, featuring 109B total parameters with 17B active parameters through a [[Mixture of Experts (MoE)]] architecture using 16 experts. The model supports an exceptional 10 million token context window and includes multimodal capabilities for processing both text and visual inputs. ^[open-weight-foundation-models-catalog-mid-2026.md]

### Llama 4 Maverick
Llama 4 Maverick represents the flagship model with 400B total parameters and 17B active parameters, achieved through a more sophisticated MoE configuration utilizing 128 experts. Despite its larger parameter count, it maintains the same 17B active parameter efficiency as Scout while supporting a 1 million token context window and full multimodal functionality. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Technical Architecture

Both models in the Llama 4 family employ [[Mixture of Experts (MoE)]] architecture, which allows for large total parameter counts while keeping computational requirements manageable through selective expert activation. This approach enables the models to achieve frontier-level performance while maintaining practical deployment characteristics. ^[open-weight-foundation-models-catalog-mid-2026.md]

The models feature [[Long Context Scaling]] capabilities, with Scout supporting up to 10 million tokens and Maverick supporting 1 million tokens. This extended context capacity makes them particularly suitable for applications requiring processing of lengthy documents or maintaining extended conversational history. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Licensing and Availability

The Llama 4 models are released under the Llama Community License, which permits commercial use with a restriction of 700 million monthly active users (MAU). This licensing approach provides significant flexibility for most commercial applications while maintaining some usage limitations for the largest deployments. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Language Support

The Llama 4 family supports 12 languages, providing multilingual capabilities while maintaining a more focused language set compared to some competitors like [[Qwen3 Language Model]] which supports 119 languages. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Use Cases and Applications

### General Chat Applications
For general conversational AI applications, Llama 4 Maverick serves as a strong alternative to models like [[Qwen3 Language Model]] 32B variant, offering competitive performance with different architectural trade-offs. ^[open-weight-foundation-models-catalog-mid-2026.md]

### Long Context Processing
The exceptional context windows, particularly Scout's 10 million token capacity, make the Llama 4 family well-suited for applications requiring [[Long Context Scaling]], such as document analysis, extended research tasks, and comprehensive content generation. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Hardware Requirements

The MoE architecture of Llama 4 models requires substantial computational resources for optimal performance. Multi-node deployments are typically necessary for full fine-tuning, while inference can be optimized through frameworks supporting MoE architectures like [[vLLM Inference Engine]]. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Comparison with Other Models

Within the open-weight model ecosystem, Llama 4 competes directly with other frontier models such as [[Qwen3 Language Model]], [[GPT-OSS-120B]], and various other large-scale architectures. The choice between these models often depends on specific requirements for context length, language support, licensing terms, and computational constraints. ^[open-weight-foundation-models-catalog-mid-2026.md]
