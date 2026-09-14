---
title: "GPT-OSS Model Family"
summary: "OpenAI's open-source models including 120B and 20B variants using MoE architecture with MXFP4 quantization and Apache 2.0 licensing."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: 2026-06-15T12:02:16.017653+00:00
updatedAt: 2026-06-15T12:02:16.017653+00:00
---
# GPT-OSS Model Family

The **GPT-OSS Model Family** is an open-source collection of large language models released by OpenAI in August 2025 under the Apache 2.0 license. The family consists of two primary models: [[GPT-OSS-120B]] and [[GPT-OSS-20B]], both utilizing a [[Mixture-of-Experts-MoE]] architecture designed for efficient inference and fine-tuning. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

## Architecture

Both models in the GPT-OSS family employ a sparse MoE design that activates only a subset of parameters during inference, enabling deployment on consumer hardware while maintaining competitive performance. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### GPT-OSS-120B

The flagship [[GPT-OSS-120B]] model contains 117 billion total parameters with 5.1 billion active parameters during inference. It uses 128 experts with top-4 routing, meaning only 4 experts are activated for each token. The model supports MXFP4 quantization and can run on a single H100 GPU. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### GPT-OSS-20B

The smaller [[GPT-OSS-20B]] model contains 21 billion total parameters with 3.6 billion active parameters. This model is designed to fit within 16GB of VRAM, making it accessible for deployment on consumer-grade hardware. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

## Key Features

### Harmony Format

Both models utilize a proprietary "Harmony format" that enables structured interaction patterns and improved consistency in responses. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### Adjustable Reasoning Levels

The GPT-OSS models feature adjustable reasoning levels, allowing users to control the depth of reasoning applied to different tasks. This capability enables optimization for both speed and accuracy depending on the use case. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### Agentic Capabilities

The models are specifically designed for agentic applications, including tool use, web interaction, and code generation. This makes them particularly suitable for autonomous agent deployments and interactive coding environments. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

## Performance Characteristics

### Hallucination Rate

GPT-OSS-120B exhibits a 78% hallucination rate, which significantly limits its effectiveness for question-answering tasks requiring high factual accuracy. This high hallucination rate makes the model less suitable for applications where factual precision is critical. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### Quantization Support

The models support MXFP4 quantization through the [[vLLM-Inference-Engine]], though the performance impact compared to BF16 precision varies by use case. Both quantization formats are supported by vLLM for deployment flexibility. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

## Fine-Tuning Considerations

### Hardware Requirements

For fine-tuning GPT-OSS models, different approaches are recommended based on available hardware:
- 8GB VRAM: QLoRA only for GPT-OSS-20B
- 16-24GB VRAM: LoRA or QLoRA for GPT-OSS-20B
- 80GB (A100/H100): LoRA or full SFT for GPT-OSS-120B ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

### Training Challenges

When GPT-OSS-120B shows limited improvement after supervised fine-tuning on small datasets (e.g., 5K samples), several factors may be responsible including the sparse MoE architecture's training dynamics, data quality issues, or the need for alternative approaches such as knowledge distillation from higher-performing models like [[Qwen3-Language-Model]] variants. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

## Positioning in the Ecosystem

The GPT-OSS family represents OpenAI's entry into the open-source model space, competing with other frontier open-weight models such as the [[Qwen3-Language-Model]] family and Meta's Llama series. The models are positioned as particularly strong for agentic applications and tool use, though their high hallucination rates limit their applicability for factual question-answering tasks. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]

The Apache 2.0 licensing makes these models fully permissive for commercial use, distinguishing them from models with usage restrictions or non-commercial licenses. ^[Open-Weight Foundation Models Catalog for Fine-Tuning (Mid-2026).md]
