---
title: "Disaggregated Prefill/Decode Serving"
summary: "An architecture that separates compute-bound prefill operations from bandwidth-bound decode operations onto distinct GPU pools, achieving 2.5x throughput improvements."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:29:00.620967+00:00
updatedAt: 2026-06-15T11:29:00.620967+00:00
---
# Disaggregated Prefill/Decode Serving

**Disaggregated Prefill/Decode Serving** is an architectural pattern for large language model inference that separates the prefill phase (processing input prompts) from the decode phase (generating output tokens) across different compute resources. This approach optimizes resource utilization by matching the distinct computational characteristics of each phase to specialized hardware configurations.

## Architecture Overview

In traditional LLM serving, both prefill and decode operations run on the same GPU cluster. Disaggregated serving splits these workloads across separate, specialized clusters optimized for their respective computational patterns. The prefill cluster processes input prompts and generates initial key-value (KV) cache states, which are then transferred to the decode cluster for autoregressive token generation. ^[multi-node-llm-inference-solutions-at-scale.md]

## Performance Benefits

Disaggregated serving delivers significant throughput improvements over monolithic architectures. [[vLLM Inference Engine]] demonstrated 2.5x throughput gains with disaggregated prefill/decode in April 2026. This performance boost stems from optimizing each phase independently - prefill clusters can maximize parallel processing of input sequences, while decode clusters focus on low-latency sequential generation. ^[multi-node-llm-inference-solutions-at-scale.md]

## Implementation in Production Systems

The **llm-d** framework provides Kubernetes-native distributed inference with first-class support for disaggregated prefill/decode serving. This system includes KV-cache-aware routing to efficiently transfer intermediate states between clusters. [[vLLM Inference Engine]] has integrated disaggregated serving as a core feature, making it accessible for production deployments at scale. ^[multi-node-llm-inference-solutions-at-scale.md]

## Computational Characteristics

Prefill and decode phases have fundamentally different resource requirements. Prefill operations are compute-intensive and highly parallelizable, benefiting from high-throughput configurations with many cores. Decode operations are memory bandwidth-bound and latency-sensitive, requiring fast memory access and low communication overhead. This mismatch makes disaggregated serving particularly effective for optimizing overall system efficiency. ^[multi-node-llm-inference-solutions-at-scale.md]

## Relationship to Other Serving Patterns

Disaggregated serving complements other inference optimizations like [[Mixture of Experts (MoE)]] architectures and multi-node parallelism strategies. It works alongside techniques such as [[Speculative Decoding]] and [[Prompt Caching]] to further improve inference efficiency. The pattern is especially valuable in hyperscale deployments where resource specialization can yield substantial cost and performance benefits. ^[multi-node-llm-inference-solutions-at-scale.md]
