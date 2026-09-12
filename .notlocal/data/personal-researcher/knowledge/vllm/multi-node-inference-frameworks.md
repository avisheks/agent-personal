---
title: "Multi-Node LLM Inference Frameworks"
summary: "Comparison of open-source multi-node inference solutions: vLLM (dominant, Ray-based, Wide-EP), TensorRT-LLM (NVIDIA-optimized, lowest latency), SGLang (RadixAttention, AMD/TPU support), DeepSpeed-MII (Microsoft ecosystem). vLLM is default choice; TRT-LLM for latency-critical; SGLang for heterogeneous hardware."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Multi-Node LLM Inference Frameworks

## Framework Comparison

| Framework | Owner | Parallelism | MoE EP | Unique Feature | Best For |
|-----------|-------|-------------|--------|----------------|----------|
| **vLLM** | UC Berkeley | TP, PP, EP, DP | Elastic EP (May 2026) | PagedAttention, Wide-EP, disaggregated prefill/decode | Default choice, broadest model support |
| **TensorRT-LLM** | NVIDIA | TP, PP, EP, hybrid TP+EP | First-class | Compiled CUDA kernels, CUDA graphs | Lowest latency on NVIDIA hardware |
| **SGLang** | LMSYS | TP, PP, EP, DP | Native | RadixAttention, AMD/TPU/Ascend support | Structured output, heterogeneous hardware |
| **DeepSpeed-MII** | Microsoft | TP + replication | Mixtral only | Dynamic SplitFuse | Microsoft/DeepSpeed ecosystem |
| **Ray Serve + vLLM** | Anyscale | Via vLLM | Via vLLM | Autoscaling, fault tolerance, multi-model | Production orchestration at scale |
| **llm-d** | Open-source | Via vLLM | Via vLLM | K8s-native, KV-aware routing | Kubernetes deployments |

^[multi-node-llm-inference-solutions.md]

## Parallelism Strategies

| Strategy | What It Splits | Communication | When to Use |
|----------|---------------|---------------|-------------|
| Tensor Parallel (TP) | Weight matrices within layers | AllReduce every layer | Within NVLink domain (single node) |
| Pipeline Parallel (PP) | Layers across stages | Point-to-point | Across nodes with slower interconnect |
| Expert Parallel (EP) | Entire experts across GPUs | All-to-all dispatch | MoE models (128+ experts) |
| Data Parallel (DP) | Replicas of full model | None (independent) | Throughput scaling via replicas |

Guideline: TP within nodes, PP or EP across nodes. NVLink for TP; Ethernet acceptable for PP; InfiniBand for EP all-to-all. ^[multi-node-llm-inference-solutions.md]

## Key Performance Numbers

| Claim | Source | Verification |
|-------|--------|-------------|
| vLLM V1: 1.7x over V0 | vLLM blog, Jan 2025 | First-party benchmark |
| vLLM Wide-EP: 2.2k tok/s/H200 | vLLM blog, Dec 2025 | First-party, Coreweave IB |
| vLLM disaggregated: 2.5x throughput | vLLM blog, Apr 2026 | First-party claim |
| TRT-LLM Llama 8B FP8: 27.3k tok/s | NVIDIA perf page | First-party, 128/128 seq only |
| SGLang 2.7x on GB200 NVL72 | SGLang homepage | Marketing, unverified |
| TP 4x→8x: only 0.7x latency at batch=1 | Databricks | Third-party verified |

## Related

- [[Cloud LLM Inference Services]] — AWS, GCP, Azure managed options
- [[VLLM Inference Engine]] — Single-node vLLM details
- [[vLLM Single-GPU Requirements]] — Requirements and pros/cons
