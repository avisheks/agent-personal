---
title: "Gradient Checkpointing"
summary: "A memory optimization technique used in conjunction with LoRA and QLoRA that trades computation for memory by recomputing intermediate activations during backpropagation instead of storing them."
sources:
  - lora/fine-tuning-using-lora-and-qlora-geeksforgeeks.md
createdAt: 2026-05-28T19:17:35.687916+00:00
updatedAt: 2026-05-28T19:17:35.687916+00:00
---
# Gradient Checkpointing

**Gradient Checkpointing** is a memory optimization technique used during neural network training that trades computation time for reduced memory usage by selectively storing and recomputing intermediate activations during the backward pass.

## Overview

Gradient checkpointing addresses the memory bottleneck that occurs during backpropagation in deep neural networks. During forward propagation, neural networks must store all intermediate activations to compute gradients during the backward pass. For very large models, these stored activations can consume enormous amounts of memory, often exceeding available GPU VRAM. ^[fine-tuning-using-lora-and-qlora.md]

The technique works by strategically discarding some intermediate activations during the forward pass and recomputing them as needed during backpropagation. This creates a time-memory trade-off where training takes longer but requires significantly less memory. ^[fine-tuning-using-lora-and-qlora.md]

## Implementation in Fine-Tuning

Gradient checkpointing is particularly valuable when combined with parameter-efficient fine-tuning methods like [[Low-Rank Adaptation (LoRA)]] and [[QLoRA (Quantized LoRA)]]. In [[QLoRA (Quantized LoRA)]] implementations, gradient checkpointing is commonly enabled alongside quantization configurations to further reduce memory requirements during training. ^[fine-tuning-using-lora-and-qlora.md]

Libraries such as BitsAndBytes for quantization and PEFT for [[Low-Rank Adaptation (LoRA)]] often incorporate gradient checkpointing as a standard optimization when fine-tuning large language models on resource-constrained hardware. ^[fine-tuning-using-lora-and-qlora.md]

## Benefits and Trade-offs

The primary benefit of gradient checkpointing is enabling the training of larger models or larger batch sizes on hardware with limited memory capacity. This is especially important for [[Parameter-Efficient Fine-Tuning (PEFT)]] approaches where the goal is to make large model training accessible on consumer-grade GPUs. ^[fine-tuning-using-lora-and-qlora.md]

The main trade-off is increased training time, as the network must perform additional forward computations during the backward pass to reconstruct the discarded activations. However, this computational overhead is often acceptable given the substantial memory savings achieved. ^[fine-tuning-using-lora-and-qlora.md]

## Related Techniques

Gradient checkpointing is frequently used in combination with other memory optimization strategies, including model quantization techniques like those used in [[QLoRA (Quantized LoRA)]], and parameter-efficient methods such as [[Low-Rank Adaptation (LoRA)]]. These complementary approaches can dramatically reduce the hardware requirements for fine-tuning large language models. ^[fine-tuning-using-lora-and-qlora.md]
