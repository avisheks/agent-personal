---
title: "NeMo-RL Framework"
summary: "NVIDIA's RL post-training framework focusing on critic-free methods like GRPO with Megatron 6D parallelism, optimized for NVIDIA hardware and large-scale training."
sources:
  - sft-vs-dpo/rl-training-frameworks-verl-nemo-comparison.md
createdAt: 2026-06-15T11:39:15.242984+00:00
updatedAt: 2026-06-15T11:39:15.242984+00:00
---
# NeMo-RL Framework

**NeMo-RL** (formerly NeMo-Aligner) is NVIDIA's reinforcement learning framework for post-training large language models, designed to scale efficiently on NVIDIA hardware architectures. The framework focuses on critic-free RL methods and integrates deeply with NVIDIA's Megatron Core for distributed training at scale. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Overview

NeMo-RL is part of NVIDIA's broader NeMo ecosystem and represents a production-grade solution for reinforcement learning from human feedback (RLHF) and related post-training techniques. The framework emphasizes scalability on NVIDIA hardware, particularly H100 and GB200 systems, while maintaining compatibility with the Megatron parallelism strategies. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Supported Algorithms

The framework implements several modern RL algorithms optimized for language model training:

- **[[Group Relative Policy Optimization (GRPO)]]** - Primary algorithm for policy optimization
- **GSPO** - Group-based policy optimization variant
- **[[Direct Alignment from Preferences Optimization (DAPO)]]** - Direct preference alignment
- **GDPO** - Generalized direct preference optimization
- **[[Supervised Fine-Tuning (SFT)]]** with LoRA support
- **[[Direct Preference Optimization (DPO)]]** with LoRA support
- **On-Policy Distillation** - Knowledge transfer techniques
- **Reward Modeling** - Training reward functions for RLHF

Notably, NeMo-RL has dropped support for PPO and REINFORCE methods, focusing instead on critic-free approaches that are more stable and efficient at scale. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Architecture and Parallelism

### Core Technologies

NeMo-RL builds on two primary architectural foundations:

- **DTensor** - Supports FSDP2, tensor parallelism (TP), sequence parallelism (SP), and pipeline parallelism (PP)
- **[[Mixture of Experts (MoE)]] Core** - Implements 6D parallelism including TP, PP, SP, context parallelism (CP), expert parallelism (EP), and FSDP

### Inference Integration

The framework integrates with multiple inference backends:
- **[[vLLM Inference Engine]]** - External inference engine
- **Megatron-native inference** - Direct inference without weight conversion, providing significant performance advantages

The Megatron-native approach eliminates the overhead of converting weights between training and inference formats, resulting in faster rollout generation during RL training. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Performance and Scale

### Hardware Support

NeMo-RL is optimized exclusively for NVIDIA hardware:
- **H100 GPUs** - Primary target platform
- **GB200-NVL72** - Next-generation architecture with 256 GPUs per node
- **FP8 end-to-end training** - Leveraging latest precision formats

### Benchmarked Performance

The framework has demonstrated strong performance on large-scale models:
- **DeepSeek V3 671B** - Achieved 12.1-30.2 tokens/second/GPU
- **[[Qwen3 Language Model]] 235B** - Reached 37.4-163 tokens/second/GPU
- **Megatron backend** - Showed 36-56% performance improvement over DTensor at 70B parameter scale

Testing has been conducted on systems with up to 512 H100 GPUs, demonstrating the framework's ability to scale to enterprise-level deployments. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Key Features

### Advanced Optimization

- **Async GRPO** - Asynchronous implementation of Group Relative Policy Optimization
- **Speculative decoding** - Accelerated inference during rollout generation
- **FP8 training pipeline** - End-to-end support for 8-bit floating point precision

### Production Integration

NeMo-RL has been used to train NVIDIA's flagship language models, including the Nemotron-3 series (Nano, Super, and Ultra variants), demonstrating its production readiness and reliability. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Comparison with Alternatives

### vs veRL

While veRL offers broader algorithm support including PPO and supports multiple hardware vendors, NeMo-RL provides deeper integration with NVIDIA's ecosystem and Megatron architecture. NeMo-RL's Megatron-native inference provides performance advantages that veRL's multi-backend approach cannot match on NVIDIA hardware. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

### vs HuggingFace TRL

[[Hugging Face Transformers Library]] TRL offers easier setup and broader algorithm support for research, but NeMo-RL is specifically designed for production-scale deployments on NVIDIA infrastructure. TRL is better suited for single-node experiments, while NeMo-RL targets multi-node enterprise deployments. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]

## Use Cases and Recommendations

NeMo-RL is most appropriate for:

- **Large-scale deployments** (32+ GPUs) on NVIDIA hardware
- **Production environments** requiring maximum performance and stability
- **Organizations** already using Megatron for pre-training
- **Models** at 70B+ parameters where the framework's optimizations provide significant benefits

For smaller deployments or research environments, alternative frameworks like TRL or LLaMA-Factory may be more suitable due to their easier setup and broader compatibility. ^[rl-post-training-frameworks-verl-vs-nemo-rl-vs-alternatives.md]
