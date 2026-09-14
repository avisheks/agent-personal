---
title: "MXFP4 Quantization"
summary: "A 4-bit quantization format supported by TensorRT-LLM on Blackwell architecture GPUs for memory-efficient inference with minimal quality degradation."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:29:53.632580+00:00
updatedAt: 2026-06-15T11:29:53.632580+00:00
---
# MXFP4 Quantization

MXFP4 (Microscaling FP4) is a 4-bit floating-point quantization format designed for efficient neural network inference, particularly on modern GPU architectures. It represents a specialized approach to model compression that maintains numerical precision while significantly reducing memory requirements and computational overhead.

## Overview

MXFP4 quantization reduces model weights from standard 16-bit or 32-bit floating-point representations to 4-bit microscaling format. This technique is part of the broader category of [[mixed-precision-training]] approaches that optimize memory usage and inference speed while preserving model quality. The format is specifically optimized for hardware acceleration on advanced GPU architectures. ^[multi-node-llm-inference-solutions-at-scale.md]

## Technical Implementation

The microscaling approach in MXFP4 uses a shared scaling factor across groups of weights, allowing for more efficient representation than traditional uniform quantization. This shared scaling mechanism helps maintain the dynamic range necessary for neural network computations while achieving the 4-bit compression target. ^[multi-node-llm-inference-solutions-at-scale.md]

## Hardware Support

MXFP4 quantization is supported on NVIDIA's Blackwell architecture GPUs, representing a hardware-software co-design approach to efficient inference. The format is integrated into [[tensorrt-llm]] (NVIDIA's optimized inference engine), where it works alongside other quantization formats including [[fp8-training]], INT4, and INT8 variants. ^[multi-node-llm-inference-solutions-at-scale.md]

## Performance Characteristics

When deployed on compatible hardware, MXFP4 can provide substantial memory savings compared to higher-precision formats. For large language models, this translates to reduced GPU memory requirements, enabling deployment of larger models on the same hardware or improved throughput through increased batch sizes. The format is particularly relevant for [[mixture-of-experts-moe]] architectures where memory efficiency is critical for scaling. ^[multi-node-llm-inference-solutions-at-scale.md]

## Integration with Inference Frameworks

MXFP4 support is available through [[tensorrt-llm]], which provides optimized kernels for Blackwell GPUs. This integration allows models to leverage the quantization format as part of broader multi-node inference deployments, working in conjunction with parallelism strategies like tensor parallel and expert parallel configurations. ^[multi-node-llm-inference-solutions-at-scale.md]

## Comparison with Other Quantization Methods

MXFP4 sits alongside other 4-bit quantization approaches like [[normalfloat4-nf4]] and traditional INT4 methods. Unlike integer-based quantization, the floating-point nature of MXFP4 can better preserve the distribution characteristics of neural network weights, potentially leading to better model quality retention during compression. ^[multi-node-llm-inference-solutions-at-scale.md]

## Applications

The primary application of MXFP4 quantization is in large-scale language model inference, where memory bandwidth often becomes the bottleneck rather than computational throughput. This makes it particularly valuable for deployment scenarios involving models like [[gpt-oss-120b]] or [[qwen3-language-model]] variants where memory efficiency directly impacts serving capacity and cost. ^[multi-node-llm-inference-solutions-at-scale.md]
