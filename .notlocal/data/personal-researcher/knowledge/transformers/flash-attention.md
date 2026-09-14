---
title: "Flash Attention"
summary: "An engineering breakthrough that computes attention in chunks that fit in fast SRAM memory, achieving 2-4x speedup by minimizing slow memory transfers despite doing more computation."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:43:29.281333+00:00
updatedAt: 2026-06-16T14:43:29.281333+00:00
---
# Flash Attention

Flash Attention is an engineering breakthrough that enables efficient computation of attention mechanisms in transformer models by optimizing memory access patterns rather than reducing computational complexity. It addresses the quadratic memory scaling problem that makes long context windows prohibitively expensive in large language models. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## The Quadratic Scaling Problem

In standard [[transformer-architecture]] implementations, the attention mechanism creates a fundamental bottleneck. When computing attention scores, the model must create and store a matrix of size `[seq_len × seq_len]`, where each position computes how much it should attend to every other position. This creates both computational and memory challenges that scale quadratically with sequence length. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The memory requirements become prohibitive quickly:

- **1K tokens**: 1K × 1K matrix = 2MB memory
- **8K tokens**: 8K × 8K matrix = 128MB memory  
- **32K tokens**: 32K × 32K matrix = 2GB memory
- **128K tokens**: 128K × 128K matrix = 32GB memory

^[Large Language Model (LLM) Training - Intro - final.pdf]

## Memory Bandwidth Bottleneck

The core insight behind Flash Attention is that modern GPUs are not compute-bound but memory-bound for attention operations. While GPUs can perform 300+ TFLOPS of computation, they can only move around 2TB/s of memory. The standard attention implementation spends most of its time moving large attention matrices between slow main GPU memory (HBM) and compute units, rather than actually performing calculations. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Flash Attention Solution

Flash Attention solves this by never materializing the full attention matrix in memory. Instead of the standard approach:

```
scores = Q @ K.T             # Creates [seq_len × seq_len] in memory
attention = softmax(scores)  # Read huge matrix, write it back
output = attention @ V       # Read huge matrix again
```

Flash Attention computes attention in chunks that fit entirely in SRAM (the fast on-chip memory). SRAM has only about 20MB of capacity but operates 10× faster than main GPU memory. The algorithm processes the attention computation in tiles, keeping intermediate results in fast memory and accumulating the final output without ever storing the complete attention matrix. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Performance Characteristics

Flash Attention achieves 2-4× speedup over standard attention implementations despite actually performing MORE total computation. This counterintuitive result demonstrates how hardware-aware algorithms can outperform theoretically optimal approaches by minimizing expensive memory transfers. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The algorithm recomputes certain values during the backward pass rather than storing them, trading additional computation for reduced memory usage. This trade-off proves beneficial because the extra computation happens in fast SRAM while avoiding slow memory transfers.

## Impact on Long Context Models

Flash Attention is essential for making [[long-context-scaling]] viable in modern language models. Without it, the memory requirements for attention matrices would exceed available GPU memory at the context lengths that current models support (32K-128K tokens). The technique enables the development of models with extended context windows that would otherwise be impossible to train or run efficiently. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Related Concepts

Flash Attention works in conjunction with other memory optimization techniques in transformer models, including [[mixture-of-experts-moe]] architectures and various forms of [[context-window-compaction]]. It is particularly important for [[vllm-inference-engine]] implementations that need to serve long-context requests efficiently in production environments.
