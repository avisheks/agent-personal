---
title: "llm-d Kubernetes-Native Inference"
summary: "An open-source Kubernetes-native distributed inference framework built on vLLM with KV-cache-aware routing and disaggregated serving as first-class features."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:29:23.770637+00:00
updatedAt: 2026-06-15T11:29:23.770637+00:00
---
# llm-d Kubernetes-Native Inference

**llm-d** is an open-source Kubernetes-native distributed inference framework designed for large language model serving at scale. Built on top of [[vLLM Inference Engine]], llm-d provides first-class support for disaggregated prefill/decode architectures and is emerging as a standard solution for Kubernetes-based vLLM deployments. ^[multi-node-llm-inference-solutions-at-scale.md]

## Architecture

llm-d implements a Kubernetes-native approach to distributed LLM inference, leveraging the orchestration capabilities of Kubernetes for managing multi-node deployments. The framework is built on vLLM as its underlying inference engine, inheriting vLLM's performance optimizations while adding Kubernetes-specific features for production deployment. ^[multi-node-llm-inference-solutions-at-scale.md]

### Disaggregated Serving

A key architectural feature of llm-d is its first-class support for disaggregated prefill/decode serving. This approach separates the prefill phase (processing input tokens) from the decode phase (generating output tokens), allowing for optimized resource allocation and improved throughput. The disaggregated architecture can achieve up to 2.5x throughput improvements compared to traditional unified serving approaches. ^[multi-node-llm-inference-solutions-at-scale.md]

### KV-Cache-Aware Routing

llm-d implements KV-cache-aware routing mechanisms that optimize request distribution based on the state of key-value caches across different nodes. This intelligent routing helps minimize cache misses and improves overall system efficiency in multi-node deployments. ^[multi-node-llm-inference-solutions-at-scale.md]

### Wide-EP Integration

The framework supports vLLM's Wide-EP (Wide Expert Parallel) capabilities, which enable efficient scaling for [[Mixture of Experts (MoE)]] models. Wide-EP provides "well-lit paths" for expert routing, optimizing communication patterns in distributed MoE inference. ^[multi-node-llm-inference-solutions-at-scale.md]

## Deployment Scenarios

llm-d is particularly well-suited for hyperscale deployments with 100+ nodes, where Kubernetes orchestration becomes mandatory for managing the complexity of distributed inference. The framework addresses the operational challenges of running large-scale LLM inference in production environments. ^[multi-node-llm-inference-solutions-at-scale.md]

For multi-node deployments in the 10-100 node range, llm-d combined with vLLM Wide-EP provides disaggregated serving capabilities with autoscaling features, making it a recommended solution for organizations requiring high-throughput LLM inference. ^[multi-node-llm-inference-solutions-at-scale.md]

## Relationship to Other Frameworks

llm-d is positioned alongside other Kubernetes-based inference solutions such as Ray Serve + vLLM and NVIDIA Dynamo, all of which use vLLM as their underlying inference engine. However, llm-d distinguishes itself through its native Kubernetes integration and specialized support for disaggregated architectures. ^[multi-node-llm-inference-solutions-at-scale.md]

The framework represents part of the broader ecosystem of multi-node LLM inference solutions, which includes open-source frameworks like [[vLLM Inference Engine]], TensorRT-LLM, and SGLang, as well as cloud-managed services from major providers. ^[multi-node-llm-inference-solutions-at-scale.md]

## Current Status

As of version 0.7, llm-d is actively developed and gaining adoption as a standard for Kubernetes-native distributed inference. The framework benefits from the ongoing improvements in vLLM, including the V1 architecture that provides 1.7x throughput improvements over previous versions. ^[multi-node-llm-inference-solutions-at-scale.md]
