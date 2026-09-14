---
title: "Multi-Node LLM Inference Solutions at Scale"
url: "multiple (vLLM blog, NVIDIA TRT-LLM docs, SGLang homepage, DeepSpeed-MII, AWS/GCP/Azure docs, Databricks benchmarks)"
ingestedAt: "2026-06-07T00:00:00Z"
type: "article"
---

# Multi-Node LLM Inference Solutions at Scale

## Open-Source Frameworks

### vLLM Multi-Node (Ray-Based)
- Dominant open-source inference engine (UC Berkeley)
- V1 architecture (Jan 2025): 1.7x throughput over V0
- Multi-node via Ray; multiprocessing for single-node
- Parallelism: TP (within node), PP (across nodes), Elastic EP (May 2026), DP
- Wide-EP: 2.2k tok/s/H200 on Coreweave InfiniBand (Dec 2025 blog)
- Disaggregated prefill/decode: 2.5x throughput (Apr 2026 blog)
- Features: PagedAttention, zero-overhead prefix caching, speculative decoding, DBO, vLLM Router
- Quantization: FP8, INT4 (AWQ, GPTQ), INT8; Marlin kernels
- MoE: Elastic EP with EPLB (Expert Parallel Load Balancing), DeepEP all-to-all kernels

### TensorRT-LLM (NVIDIA)
- NVIDIA's optimized engine using TRT compilation + custom CUDA kernels
- Multi-node via MPI/NCCL; supports GB200 NVL72
- Parallelism: TP, PP, EP, hybrid TP+EP (moe_tp_size * moe_ep_size == tp_size)
- Benchmarks: Llama 8B FP8 GH200 ~27.3k tok/s; 405B FP8 H200 TP=8 ~4.7k tok/s (128/128 seq)
- Features: CUDA graphs, in-flight batching, KV paging, speculative decoding
- Quantization: FP8, INT4, INT8, MXFP4 (Blackwell), FP4 (Blackwell)
- MoE: First-class EP support, configurable moe_ep_size
- Powers NVIDIA NIM containers

### SGLang
- High-performance framework (LMSYS, UC Berkeley/Stanford)
- All four parallelism modes: TP, PP, EP, DP
- RadixAttention for prefix caching (unique differentiator)
- Day-one DeepSeek V3/R1 support
- 2.7x decoding throughput on GB200 NVL72 (self-reported)
- Hardware: NVIDIA, AMD (MI355/MI300), Intel, TPUs (via SGLang-Jax), Ascend NPUs
- Version requirement: 0.4.6.post1+ for Qwen3

### DeepSpeed-MII
- Microsoft's inference library, built on DeepSpeed
- Parallelism: TP + model replication (no native EP or PP)
- Dynamic SplitFuse optimization
- Claimed 2.5x over vLLM (Jan 2024 -- predates vLLM V1, likely outdated)
- v0.3.3 (Mar 2025), 2.1k stars, slower dev pace
- Supports Mixtral 8x7B but no specialized EP mode

### Ray Serve + vLLM
- Ray's serving framework wrapping vLLM
- Adds: autoscaling, fault tolerance, multi-model, Kubernetes (KubeRay)
- Standard recommendation for production vLLM at scale
- Powers: llm-d, NVIDIA Dynamo, Anyscale

### llm-d (Kubernetes-Native)
- Open-source K8s-native distributed inference (v0.7)
- Built on vLLM, disaggregated prefill/decode first-class
- KV-cache-aware routing, Wide-EP "well-lit paths"
- Emerging standard for K8s-based vLLM at scale

### Petals (Decentralized)
- BitTorrent-style distributed inference
- Llama 70B: ~6 tok/s, Falcon 180B: ~4 tok/s
- Research/hobby only, not production

### llama.cpp (Distributed)
- Experimental RPC backend for multi-node
- Not for production serving

## Cloud-Managed Services

### AWS
- SageMaker LMI: vLLM/TRT-LLM backends, multi-instance endpoints, auto-scaling
- Bedrock: Fully managed, pay-per-token, zero ops
- EKS + vLLM/TRT-LLM: Full control Kubernetes
- Inferentia2/Trainium: Custom silicon, ~40% lower cost/token (AWS claim)

### GCP
- Vertex AI + vLLM: Managed serving on GPUs or TPUs
- GKE + vLLM: Kubernetes with LeaderWorkerSet for multi-node
- Cloud TPU (JetStream): Google's optimized TPU serving
- DeepSeek V3 multi-host deployments supported

### Azure
- Azure ML (Foundry Models): 1,900+ model catalog, managed compute
- AKS + vLLM/TRT-LLM: Self-managed Kubernetes
- Azure OpenAI Service: Hosted open models (DeepSeek, Llama, Mistral)
- Provisioned throughput: reserved capacity, fungible across models

### Inference Providers
- NVIDIA NIM: Pre-optimized TRT-LLM containers, enterprise license
- Together.ai: Custom engine, "Serverless 2.0", three deployment modes
- Fireworks.ai: FireAttention, claimed 4x faster prefill vs vLLM
- Anyscale: Managed Ray Serve platform
- Modal: Serverless GPU, ~10s cold start, scale-to-zero
- Replicate: Container-based, simple API
- HF Inference Endpoints: TGI-based, SOC2, scale-to-zero

## Parallelism Comparison

| Type | Splits | Communication | Best Interconnect | When |
|------|--------|---------------|-------------------|------|
| Tensor Parallel | Weight matrices within layers | AllReduce every layer | NVLink (>400 Gb/s) | Within single node |
| Pipeline Parallel | Layers across stages | Point-to-point | Ethernet OK | Across nodes, slower interconnect |
| Expert Parallel | Entire experts across GPUs | All-to-all token dispatch | High-bandwidth | MoE models with many experts |

Hybrid: TRT-LLM supports TP+EP combined; vLLM supports Wide-EP + DP.

## Decision Matrix

| Scenario | Recommended | Rationale |
|----------|-------------|-----------|
| Single GPU | vLLM or llama.cpp | Simplest |
| Single node 2-8 GPUs | vLLM TP | NVLink, well-tested |
| Multi-node <10 | vLLM (TP+PP) or TRT-LLM | vLLM simpler; TRT-LLM lower latency |
| Multi-node 10-100 | vLLM Wide-EP + Ray Serve/llm-d | Disaggregated serving, autoscaling |
| Hyperscale 100+ | llm-d + vLLM Wide-EP + disaggregated | K8s orchestration mandatory |
| MoE specifically | vLLM EP or SGLang EP or TRT-LLM EP | All three have native EP |
| Lowest latency | TensorRT-LLM | Compiled CUDA kernels |
| Highest throughput | vLLM Wide-EP + disaggregated | 2.2k tok/s/H200 demonstrated |
| Zero ops | Bedrock/Vertex/Azure OpenAI/Modal | Fully managed |

## Key Numbers

- vLLM V1: 1.7x over V0 (first-party, Jan 2025)
- vLLM Wide-EP: 2.2k tok/s/H200 (first-party, Coreweave IB, Dec 2025)
- vLLM disaggregated: 2.5x throughput (first-party, Apr 2026)
- TRT-LLM Llama 8B FP8 GH200: ~27.3k tok/s (first-party, 128/128)
- SGLang GB200 NVL72: 2.7x decoding (marketing claim, unverified)
- TP 4x→8x latency: only 0.7x reduction at batch=1 (Databricks, third-party)
- Continuous batching: 10-20x vs dynamic batching (general principle)
- Memory bandwidth is the inference bottleneck, not FLOPS
