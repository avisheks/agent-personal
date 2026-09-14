---
title: "microscaling-fp4-mxfp4"
summary: ""
sources:
  - numerical-representation/numerical-representation.md
createdAt: 2026-05-28T19:59:54.392901+00:00
updatedAt: 2026-05-28T19:59:54.392901+00:00
---
# Microscaling FP4 (MXFP4)

**Microscaling FP4 (MXFP4)** is an ultra-low precision numerical format that uses 4-bit floating point numbers with shared scaling factors and block-level scaling to enable stable training and inference of large language models. MXFP4 represents the cutting edge of numerical representation research, addressing the fundamental challenge that pure FP4 is too unstable for practical deep learning applications. ^[numerical-representation.md]

## Overview

MXFP4 introduces local scaling and adaptive normalization to reduce quantization error compared to naive 4-bit representations. The format uses shared scaling factors across small blocks of weights or activations, allowing for better preservation of numerical precision while maintaining the memory and computational benefits of 4-bit arithmetic. ^[numerical-representation.md]

The development of MXFP4 is part of the broader industry transition from higher precision formats: FP32 → FP16 mixed precision → [[BFloat16 (BF16)]] dominance → [[FP8 Training]] → experimental FP4/MXFP4 pipelines. This progression is fundamentally driven by the need for compute and memory efficiency at scale in modern GenAI and LLM systems. ^[numerical-representation.md]

## Technical Architecture

### Microscaling Approach

The core innovation of MXFP4 lies in its microscaling methodology, which addresses the instability issues inherent in pure FP4 formats. The system employs:

- **Shared scaling factors** across small tensor blocks
- **Block-level scaling** to maintain numerical stability  
- **Tiny 4-bit floats** with improved dynamic range management
- **Reduced quantization error** through adaptive normalization ^[numerical-representation.md]

### Training Techniques

Recent research has demonstrated near-lossless GPT training using MXFP4 through several key techniques:

- **[[Stochastic Rounding]]** to reduce bias accumulation
- **Hadamard transforms** for improved numerical properties
- **Variance stabilization** to maintain training stability ^[numerical-representation.md]

## Performance Benefits

MXFP4 offers significant advantages for large-scale model training and deployment:

- **Memory reduction**: Provides substantial memory savings compared to higher precision formats
- **Computational efficiency**: Enables faster processing through reduced bit-width operations
- **Scaling benefits**: Particularly valuable for trillion-parameter model training where memory and compute costs are critical ^[numerical-representation.md]

## Relationship to Other Formats

MXFP4 exists within the broader ecosystem of low-precision formats, including NVIDIA's NVFP4 for Blackwell GPUs. While NVFP4 uses hierarchical scaling and smaller microblocks, MXFP4 focuses on the microscaling approach with shared scaling factors. Both formats represent the research frontier in making FP4 training practically feasible, as FP4 training was previously considered impractical. ^[numerical-representation.md]

The format is also related to other ultra-low precision approaches like [[NormalFloat4 (NF4)]], which is used in [[QLoRA (Quantized LoRA)]] for 4-bit fine-tuning of large models. However, MXFP4 is designed for full training rather than just inference or parameter-efficient fine-tuning. ^[numerical-representation.md]

## Current Applications

MXFP4 is primarily used in experimental cutting-edge research contexts, as the format represents the newest generation of ultra-low precision training. The format is particularly relevant for researchers exploring the limits of numerical precision in large language model training, where traditional approaches using BF16 or FP8 may still be too memory-intensive for the largest models. ^[numerical-representation.md]

## Implementation Considerations

When implementing MXFP4 systems, several factors must be considered:

- **Hardware support**: Requires specialized hardware or software emulation for 4-bit floating point operations
- **Numerical stability**: Careful attention to outliers and gradient scaling is essential
- **Validation requirements**: Long-horizon stability testing is critical, as low precision can appear stable early but collapse late in training
- **Selective application**: Not all tensor operations may be suitable for MXFP4; sensitive components like embeddings and attention logits may require higher precision ^[numerical-representation.md]

## Future Directions

The development of MXFP4 aligns with the emerging trend toward **[[Adaptive Precision Training]]** and **heterogeneous precision** systems. Rather than using a single datatype globally, future systems are likely to dynamically select between different precision formats (FP4, FP8, BF16) based on tensor properties and sensitivity requirements. This represents a shift from viewing lower precision as merely compression to treating it as a core systems-design dimension for scaling intelligence. ^[numerical-representation.md]
