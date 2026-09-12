---
title: "Wide-EP (Wide Expert Parallel)"
summary: "A parallelism strategy in vLLM that achieves 2.2k tokens/second/H200 on Coreweave InfiniBand by distributing experts across multiple nodes with optimized all-to-all communication."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:28:50.767174+00:00
updatedAt: 2026-06-15T11:28:50.767174+00:00
---
# Wide-EP (Wide Expert Parallel)

Wide-EP (Wide Expert Parallel) is an advanced parallelization strategy for distributed inference of [[Mixture of Experts (MoE)]] models that extends traditional Expert Parallel (EP) approaches to achieve higher throughput and better resource utilization across multiple nodes. ^[multi-node-llm-inference-solutions-at-scale.md]

## Overview

Wide-EP represents an evolution of standard Expert Parallel techniques, designed specifically for large-scale [[Mixture of Experts (MoE)]] model deployment. Unlike traditional EP that distributes experts across GPUs within a single node, Wide-EP extends this distribution across multiple nodes while maintaining efficient communication patterns. ^[multi-node-llm-inference-solutions-at-scale.md]

The approach is particularly effective when combined with disaggregated serving architectures, where prefill and decode operations are separated to optimize resource allocation and throughput. ^[multi-node-llm-inference-solutions-at-scale.md]

## Implementation in vLLM

The [[vLLM Inference Engine]] has implemented Wide-EP as part of its V1 architecture, achieving significant performance improvements over traditional parallelization approaches. In December 2025, vLLM demonstrated Wide-EP achieving 2.2k tokens/second per H200 GPU on Coreweave's InfiniBand infrastructure. ^[multi-node-llm-inference-solutions-at-scale.md]

vLLM's Wide-EP implementation includes:

- **Elastic EP (EPLB)**: Expert Parallel Load Balancing that dynamically adjusts expert distribution
- **DeepEP kernels**: Optimized all-to-all communication kernels for expert routing
- **Integration with disaggregated serving**: 2.5x throughput improvement when combined with separated prefill/decode operations ^[multi-node-llm-inference-solutions-at-scale.md]

## Technical Architecture

Wide-EP operates by distributing entire experts across multiple GPUs and nodes, requiring high-bandwidth all-to-all communication for token dispatch between experts. This differs from Tensor Parallel, which splits weight matrices within layers and requires AllReduce operations every layer, and Pipeline Parallel, which distributes layers across stages with point-to-point communication. ^[multi-node-llm-inference-solutions-at-scale.md]

The approach is most effective with high-bandwidth interconnects, though it can tolerate lower bandwidth connections better than Tensor Parallel due to its communication pattern. ^[multi-node-llm-inference-solutions-at-scale.md]

## Performance Characteristics

Wide-EP has demonstrated superior scaling characteristics for [[Mixture of Experts (MoE)]] models compared to traditional parallelization approaches. The 2.2k tokens/second per H200 GPU benchmark represents a significant improvement over standard EP implementations. ^[multi-node-llm-inference-solutions-at-scale.md]

When combined with disaggregated prefill/decode architectures, Wide-EP can achieve up to 2.5x throughput improvements, making it particularly suitable for high-throughput serving scenarios. ^[multi-node-llm-inference-solutions-at-scale.md]

## Use Cases and Applications

Wide-EP is recommended for:

- **Multi-node deployments with 10-100 GPUs**: Particularly when combined with Ray Serve or llm-d orchestration
- **Hyperscale deployments (100+ GPUs)**: Essential for Kubernetes-based orchestration with llm-d
- **MoE model serving**: Specifically designed for models with many experts that benefit from expert-level parallelization ^[multi-node-llm-inference-solutions-at-scale.md]

## Integration with Orchestration Systems

Wide-EP works effectively with modern orchestration frameworks:

- **Ray Serve + vLLM**: Adds autoscaling, fault tolerance, and multi-model capabilities
- **llm-d (Kubernetes-Native)**: Provides KV-cache-aware routing and "well-lit paths" for Wide-EP
- **Disaggregated serving**: Separates prefill and decode operations for optimal resource utilization ^[multi-node-llm-inference-solutions-at-scale.md]

## Comparison with Other Parallelization Strategies

| Strategy | Communication Pattern | Best Interconnect | Optimal Use Case |
|----------|----------------------|-------------------|------------------|
| Tensor Parallel | AllReduce every layer | NVLink (>400 Gb/s) | Within single node |
| Pipeline Parallel | Point-to-point | Ethernet acceptable | Across nodes, slower interconnect |
| Wide-EP | All-to-all token dispatch | High-bandwidth preferred | MoE models, multi-node scaling |

^[multi-node-llm-inference-solutions-at-scale.md]

## Related Technologies

Wide-EP is often deployed alongside other optimization techniques including [[Speculative Decoding]], [[Prompt Caching]], and various quantization methods to maximize inference efficiency in distributed MoE model serving scenarios. ^[multi-node-llm-inference-solutions-at-scale.md]
