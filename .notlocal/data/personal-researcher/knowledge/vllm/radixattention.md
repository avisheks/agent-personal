---
title: "RadixAttention"
summary: "SGLang's unique prefix caching mechanism that uses tree-based structures for efficient reuse of computed attention states across requests with shared prefixes."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: 2026-06-15T11:29:10.917171+00:00
updatedAt: 2026-06-15T11:29:10.917171+00:00
---
# RadixAttention

**RadixAttention** is a prefix caching optimization technique developed by the LMSYS team for the [[SGLang]] inference framework. It represents a key differentiator that enables SGLang to achieve superior performance in scenarios with shared prompt prefixes by maintaining a radix tree data structure to efficiently cache and reuse key-value (KV) cache entries across multiple requests. ^[multi-node-llm-inference-solutions.md]

## Overview

RadixAttention addresses the common inefficiency in [[long-context-scaling]] scenarios where multiple inference requests share common prompt prefixes. Traditional attention mechanisms recompute the KV cache for each request independently, even when significant portions of the input are identical across requests. RadixAttention solves this by organizing cached attention states in a tree structure that allows automatic sharing of computation for common prefixes. ^[multi-node-llm-inference-solutions.md]

## Technical Implementation

The system maintains a radix tree (compressed trie) where each node represents a sequence of tokens and stores the corresponding KV cache states. When a new request arrives, RadixAttention traverses the tree to find the longest matching prefix, reuses the cached computation up to that point, and only computes attention for the novel suffix tokens. ^[multi-node-llm-inference-solutions.md]

This approach is particularly effective for applications like [[chain-of-thought-reasoning]] where multiple reasoning paths may share common initial steps, or in multi-turn conversations where context accumulates incrementally. ^[multi-node-llm-inference-solutions.md]

## Performance Benefits

RadixAttention provides significant throughput improvements in prefix-heavy workloads compared to traditional caching approaches. The technique is especially valuable when combined with SGLang's other optimizations for [[long-context-memory-handling]] scenarios. ^[multi-node-llm-inference-solutions.md]

## Integration with SGLang

RadixAttention is implemented as a core component of the [[SGLang]] framework, working alongside other parallelism modes including tensor parallel (TP), pipeline parallel (PP), expert parallel (EP), and data parallel (DP). The system supports deployment across multiple hardware platforms including NVIDIA GPUs, AMD MI355/MI300 series, Intel processors, TPUs via SGLang-Jax, and Ascend NPUs. ^[multi-node-llm-inference-solutions.md]

## Comparison with Other Caching Approaches

While other inference engines like [[vLLM-inference-engine]] implement PagedAttention for memory efficiency and basic prefix caching, RadixAttention's tree-based approach provides more sophisticated sharing capabilities for complex prefix patterns. This makes it particularly suitable for applications requiring extensive [[context-window-evolution]] and shared reasoning contexts. ^[multi-node-llm-inference-solutions.md]
