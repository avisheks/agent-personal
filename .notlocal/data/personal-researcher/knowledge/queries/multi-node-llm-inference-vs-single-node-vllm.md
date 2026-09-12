---
title: "What are some multi-node LLM inferencing solutions available at scale (vs. single-node vLLM)? What open-source solutions are available? What is available on the cloud? When to use what?"
summary: "Open-source: vLLM multi-node (dominant, Wide-EP, disaggregated prefill/decode), TensorRT-LLM (lowest latency, NVIDIA-optimized), SGLang (heterogeneous hardware, RadixAttention), DeepSpeed-MII (Microsoft ecosystem). Cloud: AWS SageMaker/Bedrock, GCP Vertex AI, Azure ML/OpenAI, plus providers (NIM, Together, Fireworks, Modal). Decision: single node TP for 2-8 GPUs; vLLM+Ray/llm-d for 10-100 nodes; TRT-LLM for lowest latency; managed cloud for zero ops."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
## Open-Source Multi-Node Solutions

| Framework | Parallelism | MoE Support | Key Differentiator | When to Use |
|-----------|-------------|-------------|-------------------|-------------|
| **vLLM** (multi-node) | TP, PP, EP, DP | Elastic EP, Wide-EP, EPLB | PagedAttention, disaggregated prefill/decode, broadest model support | Default choice — most production deployments |
| **TensorRT-LLM** | TP, PP, EP, hybrid TP+EP | First-class | Compiled CUDA kernels, CUDA graphs, NVIDIA-optimized | Lowest single-request latency on NVIDIA GPUs |
| **SGLang** | TP, PP, EP, DP | Native | RadixAttention, AMD/TPU/Ascend support | Heterogeneous hardware, structured output, DeepSeek models |
| **DeepSpeed-MII** | TP + replication | Mixtral only (no EP) | Dynamic SplitFuse | Microsoft ecosystem, simple replication scaling |
| **Ray Serve + vLLM** | Via vLLM | Via vLLM | Autoscaling, fault tolerance, multi-model | Production orchestration, K8s integration |
| **llm-d** | Via vLLM | Via vLLM | K8s-native, KV-aware routing, disaggregated | Kubernetes-scale deployments (emerging standard) |
| **Petals** | Decentralized (layer-split) | No | BitTorrent-style peer network | Research/hobby only (~6 tok/s for 70B) |

^[[Multi-Node LLM Inference Frameworks]]

## Cloud-Managed Services

### AWS
| Service | Ops Level | Use Case |
|---------|-----------|----------|
| **SageMaker LMI** | Medium | Managed vLLM/TRT-LLM containers with auto-scaling |
| **Bedrock** | Zero | Pay-per-token API, no infrastructure |
| **EKS + vLLM** | High | Full control, cost optimization |
| **Inferentia2/Trainium** | Medium | ~40% lower cost/token vs GPU |

### GCP
| Service | Ops Level | Use Case |
|---------|-----------|----------|
| **Vertex AI + vLLM** | Medium | Managed GPU/TPU serving |
| **GKE + vLLM** | High | K8s with LeaderWorkerSet for multi-node |
| **Cloud TPU (JetStream)** | Medium | Highest throughput at large scale |

### Azure
| Service | Ops Level | Use Case |
|---------|-----------|----------|
| **Azure ML (Foundry)** | Medium | 1,900+ model catalog, managed compute |
| **AKS + vLLM** | High | Full flexibility on K8s |
| **Azure OpenAI Service** | Zero | Enterprise compliance (SOC2, BAA) |

### Inference Providers
| Provider | Differentiator | Scale-to-Zero |
|----------|---------------|---------------|
| **NVIDIA NIM** | Pre-optimized TRT-LLM containers | No |
| **Together.ai** | Three deploy modes, fast model onboarding | Yes |
| **Fireworks.ai** | FireAttention, 4x prefill claim | Yes |
| **Modal** | Serverless GPU, ~10s cold start | Yes |
| **HF Endpoints** | One-click from Hub, SOC2 | Yes |

^[[Cloud LLM Inference Services]]

## Decision Framework: When to Use What

### By Scale

| Scale | Best Option | Why |
|-------|-------------|-----|
| **1 GPU, 1 user** | vLLM (or Ollama for simplicity) | Simplest, sufficient |
| **1 node, 2-8 GPUs** | vLLM with `--tensor-parallel-size N` | NVLink fast, well-tested, single command |
| **Multi-node, <10 nodes** | vLLM (TP within + PP across) OR TRT-LLM | vLLM simpler ops; TRT-LLM for lowest latency |
| **Multi-node, 10-100** | vLLM Wide-EP + Ray Serve or llm-d | Need disaggregated serving, autoscaling, intelligent routing |
| **Hyperscale, 100+ nodes** | llm-d + vLLM Wide-EP + disaggregated | K8s orchestration mandatory; EPLB for MoE |
| **Zero ops desired** | Bedrock / Vertex AI / Azure OpenAI / Modal | Fully managed, pay per use |

### By Priority

| Priority | Best Option | Why |
|----------|-------------|-----|
| **Lowest latency** | TensorRT-LLM | Compiled kernels, hardware-specific optimization |
| **Highest throughput** | vLLM Wide-EP + disaggregated prefill/decode | 2.2k tok/s/H200 demonstrated |
| **MoE models (GPT-OSS-120B)** | vLLM EP, SGLang EP, or TRT-LLM EP | All have native expert parallel |
| **Simplest ops** | Managed cloud (Bedrock/Vertex/Modal) | Zero infrastructure |
| **Heterogeneous hardware** | SGLang | AMD, TPU, Ascend, Intel support |
| **Cost optimization** | Self-hosted vLLM on reserved instances | Break-even at ~50-100M tok/day |
| **Auto-scaling** | Ray Serve + vLLM or llm-d | Scale up/down including scale-to-zero |

### By MoE Model (GPT-OSS-120B, DeepSeek V3)

| Approach | Framework | Config |
|----------|-----------|--------|
| Single H100 | vLLM (MXFP4, TP=1) | Fits on 1 GPU, ~6 concurrent requests |
| 2-8 H100s (1 node) | vLLM (TP=N or EP) | Higher concurrency + throughput |
| Multi-node EP | vLLM Wide-EP or SGLang EP | Experts distributed across GPUs/nodes; maximizes KV cache per GPU |
| Enterprise/managed | NVIDIA NIM or SageMaker LMI | Pre-optimized containers |

## Parallelism: TP vs PP vs EP

| | Tensor Parallel | Pipeline Parallel | Expert Parallel |
|---|---|---|---|
| **Splits** | Weight matrices within layers | Layers across stages | Entire experts across GPUs |
| **Communication** | AllReduce every layer | Point-to-point between stages | All-to-all token dispatch |
| **Latency** | Lowest (parallel compute) | Higher (pipeline bubbles) | Moderate |
| **Best interconnect** | NVLink (>400 Gb/s) | Ethernet OK | InfiniBand for all-to-all |
| **Scaling limit** | ~8-16 GPUs | Dozens of stages | Scales with expert count |
| **When** | Within NVLink domain | Across nodes, slow interconnect | MoE models |

## Key Insight

**Memory bandwidth, not FLOPS, is the inference bottleneck.** At multi-node scale, interconnect bandwidth becomes the limiting factor. Use:
- NVLink for TP (within node)
- InfiniBand for EP (across nodes for MoE)
- Ethernet only for PP or replica-based scaling

The biggest throughput gains at scale come from **disaggregated prefill/decode** (2.5x on vLLM) — separating compute-intensive prefill from memory-bound decode onto different GPU pools.

## Related

- [[Multi-Node LLM Inference Frameworks]]
- [[Cloud LLM Inference Services]]
- [[vLLM Single-GPU Requirements and Pros/Cons]]
- [[VLLM Inference Engine]]
