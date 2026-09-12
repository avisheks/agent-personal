---
title: "veRL Framework"
summary: "ByteDance's open-source RL post-training framework with 21.8k stars supporting online RL algorithms like PPO and GRPO across multi-hardware environments with hybrid-controller architecture."
sources:
  - sft-vs-dpo/rl-training-frameworks-verl-nemo-comparison.md
createdAt: 2026-06-15T11:38:55.642963+00:00
updatedAt: 2026-06-15T11:38:55.642963+00:00
---
# veRL Framework

The **veRL Framework** is an open-source reinforcement learning post-training system developed by ByteDance/Volcengine for large language models. It is designed to scale online RL algorithms across hundreds of GPUs while supporting multiple hardware backends and inference engines. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Overview

veRL is hosted on GitHub under the repository volcengine/verl with 21,848 stars and an Apache 2.0 license. The latest version is v0.8.0 released in June 2026. The framework is backed by academic research published as HybridFlow in EuroSys 2025. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Supported Algorithms

veRL implements a comprehensive set of online RL algorithms including:

- [[reinforcement-learning-from-human-feedback-rlhf|PPO]]
- [[group-relative-policy-optimization-grpo|GRPO]]
- GSPO
- [[direct-alignment-from-preferences-optimization-dapo|DAPO]]
- DrGRPO
- REINFORCE++
- RLOO
- PRIME
- ReMax
- SPPO
- On-Policy Distillation

Notably, veRL does not provide native support for offline algorithms like [[direct-preference-optimization-dpo|DPO]], KTO, or SimPO, focusing primarily on online RL methods. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Architecture

The framework employs a Hybrid-controller architecture that combines Ray orchestration with NCCL collectives for distributed training. It supports multiple backend systems including FSDP, FSDP2, [[mixture-of-experts-moe|Megatron-LM]], and TorchTitan. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

For inference during rollout generation, veRL integrates with [[vllm-inference-engine|vLLM]], [[sglang-inference-framework|SGLang]], and TensorRT-LLM. The 3D-HybridEngine provides zero-redundancy resharding and flexible device mapping capabilities. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Hardware Support

veRL supports multiple hardware platforms including:
- NVIDIA GPUs
- AMD MI300X/MI325X/MI355X
- Ascend NPUs

This multi-hardware approach distinguishes it from frameworks like [[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives|NeMo-RL]] that focus exclusively on NVIDIA hardware. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Performance and Scale

The framework has demonstrated training capabilities on large models including 671B [[deepseek-r1-model|DeepSeek]], [[qwen3-language-model|Qwen3-235B]], using up to 64 H800 GPUs. Performance benchmarks show 1.53x to 20.57x improvements over baseline systems, as validated through peer review in the EuroSys 2025 publication. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Key Features

- **VeOmni**: Multimodal RL capabilities
- **Fully async trainer**: Asynchronous training pipeline
- **3D-HybridEngine**: Advanced memory and compute optimization
- **Multi-backend flexibility**: Support for various distributed training backends

^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Production Usage

veRL is used internally at ByteDance and has been adopted by over 150 community projects. The [[direct-alignment-from-preferences-optimization-dapo|DAPO]] algorithm implemented in veRL achieved a score of 50 on the AIME 2024 benchmark. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

## Comparison with Alternatives

When compared to other RL post-training frameworks, veRL is positioned for large-scale deployments. For smaller setups (1-8 GPUs), frameworks like [[hugging-face-trl-library|TRL]] or LLaMA-Factory may be more appropriate. For medium scale (8-32 GPUs), both veRL and OpenRLHF are viable options. At enterprise scale (32+ GPUs), veRL competes directly with [[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives|NeMo-RL]]. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]

The framework's strength lies in its support for online RL algorithms and multi-hardware compatibility, while its limitation is the lack of native offline preference optimization methods like [[direct-preference-optimization-dpo|DPO]]. ^[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives.md]
