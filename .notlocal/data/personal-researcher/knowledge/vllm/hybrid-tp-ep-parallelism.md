---
title: "Hybrid TP+EP Parallelism"
summary: "A parallelism strategy that combines Tensor Parallel and Expert Parallel modes, where moe_tp_size * moe_ep_size equals tp_size, optimizing MoE model serving across multiple GPUs."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:29:41.314841+00:00
updatedAt: 2026-06-15T11:29:41.314841+00:00
---
# Hybrid TP+EP Parallelism

**Hybrid TP+EP Parallelism** is a distributed inference strategy that combines [[Tensor Parallelism]] (TP) and [[Expert Parallelism]] (EP) to optimize the serving of [[Mixture of Experts (MoE)]] models across multiple GPUs. This approach allows for efficient scaling of large MoE models by splitting both the dense layers via tensor parallelism and the expert layers via expert parallelism within the same deployment. ^[multi-node-llm-inference-solutions-at-scale.md]

## Architecture Overview

In hybrid TP+EP configurations, the model is partitioned using two complementary strategies. Dense transformer layers (attention and feed-forward networks) are split across GPUs using tensor parallelism, where weight matrices within layers are distributed and require AllReduce communication after each layer. Simultaneously, the MoE expert layers are distributed using expert parallelism, where entire experts are placed on different GPUs and tokens are routed via all-to-all communication patterns. ^[multi-node-llm-inference-solutions-at-scale.md]

The mathematical relationship in hybrid deployments follows the constraint: `moe_tp_size * moe_ep_size == tp_size`, ensuring that the total parallelism degree remains consistent across both dense and expert components of the model. ^[multi-node-llm-inference-solutions-at-scale.md]

## Implementation Support

[[TensorRT-LLM]] provides first-class support for hybrid TP+EP parallelism through configurable `moe_tp_size` and `moe_ep_size` parameters. This allows practitioners to fine-tune the balance between tensor and expert parallelism based on their specific model architecture and hardware configuration. ^[multi-node-llm-inference-solutions-at-scale.md]

[[vLLM]] supports a variant called Wide-EP combined with data parallelism, which has demonstrated performance of 2.2k tokens/second/H200 on Coreweave InfiniBand infrastructure. The framework also includes Expert Parallel Load Balancing (EPLB) and DeepEP all-to-all kernels for optimized MoE serving. ^[multi-node-llm-inference-solutions-at-scale.md]

[[SGLang]] offers all four parallelism modes including both TP and EP, making it suitable for hybrid configurations, particularly with its day-one support for models like DeepSeek V3/R1. ^[multi-node-llm-inference-solutions-at-scale.md]

## Communication Requirements

Hybrid TP+EP parallelism requires high-bandwidth interconnects due to the dual communication patterns. Tensor parallelism demands AllReduce operations every layer, which benefits significantly from NVLink connections (>400 Gb/s) within nodes. Expert parallelism requires all-to-all token dispatch communication, which also benefits from high-bandwidth networking but can tolerate slightly higher latency than TP operations. ^[multi-node-llm-inference-solutions-at-scale.md]

## Use Cases and Decision Criteria

Hybrid TP+EP parallelism is specifically recommended for MoE models where both dense layer performance and expert routing efficiency are critical. This approach is particularly valuable when deploying large MoE models that exceed the memory capacity of tensor parallelism alone, or when the expert count is high enough to benefit from dedicated expert parallelism. ^[multi-node-llm-inference-solutions-at-scale.md]

The decision to use hybrid TP+EP over pure tensor parallelism or pure expert parallelism depends on the specific MoE architecture, available hardware topology, and performance requirements. Models with many experts and substantial dense components typically benefit most from this hybrid approach. ^[multi-node-llm-inference-solutions-at-scale.md]
