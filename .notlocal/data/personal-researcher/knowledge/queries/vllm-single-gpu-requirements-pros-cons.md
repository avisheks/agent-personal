---
title: "What is the vLLM requirement for single-GPU deployment? What are the pros and cons?"
summary: "vLLM requires: Python 3.9+, a CUDA-compatible GPU with sufficient VRAM to hold model weights + KV cache + runtime overhead (~4GB). For single-GPU: GPT-OSS-120B needs 1× H100-80GB (MXFP4, ~62GB); Qwen3-32B needs 1× A100-80GB or RTX 4090-24GB (AWQ-4bit, ~20GB). Pros: PagedAttention (2-4x throughput), continuous batching, OpenAI-compatible API, broad model support. Cons: high VRAM requirement (no CPU offload by default), limited single-GPU concurrency for large models, MoE routing overhead, slower than custom kernels for specific architectures."
type: "query"
createdAt: "2026-06-06T00:00:00Z"
---
## Single-GPU vLLM Requirements

### Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| GPU | CUDA-capable (compute 7.0+) | H100-80GB or A100-80GB | Ampere or newer preferred for BF16/FP8 |
| VRAM | Enough for model + KV + runtime | 80GB for large models | Model-dependent (see table below) |
| System RAM | 2× model size (for loading) | 128GB+ | Initial weight loading requires CPU RAM |
| Storage | NVMe SSD | NVMe SSD (fast load) | Model weights 20-60GB+ |
| Python | 3.9+ | 3.10-3.12 | With CUDA toolkit |

### VRAM Budget for Single-GPU Deployment

```
VRAM = Model Weights + KV Cache Pool + vLLM Runtime Overhead

Where:
  Model Weights = params × bytes_per_param (quantization-dependent)
  KV Cache Pool = remaining VRAM after weights + overhead
  Runtime Overhead = ~4GB (CUDA context, buffers, scheduler)
```

### Model-Specific Requirements (Single GPU)

| Model | Format | Weight VRAM | Runtime | KV Available | Max Concurrent (4K ctx) | GPU Needed |
|-------|--------|-------------|---------|--------------|------------------------|-----------|
| GPT-OSS-120B | MXFP4 | ~54GB | ~4GB | ~12GB | ~6 requests | 1× H100-80GB |
| GPT-OSS-120B | BF16 | ~234GB | ~4GB | — | NOT FEASIBLE | 3× H100 (TP=3) |
| Qwen3-32B | AWQ-4bit | ~20GB | ~4GB | ~56GB | ~56 requests | 1× A100-80GB |
| Qwen3-32B | BF16 | ~64GB | ~4GB | ~12GB | ~12 requests | 1× H100-80GB |
| Qwen3-32B | AWQ-4bit | ~20GB | ~4GB | ~0GB (tight) | ~1-2 requests | 1× RTX 4090-24GB |

^[[VRAM-Based Model Selection]], [[GPT-OSS-120B MXFP4 vs BF16]]

### Software Requirements

```bash
# Basic installation
pip install vllm

# Launch single-GPU server
vllm serve Qwen/Qwen3-32B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --max-model-len 128000 \
  --gpu-memory-utilization 0.90 \
  --port 8000

# GPT-OSS-120B
vllm serve openai/gpt-oss-120b \
  --quantization mxfp4 \
  --tensor-parallel-size 1 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.92 \
  --port 8000
```

## Pros of vLLM for Single-GPU Deployment

| Pro | What It Means | Impact |
|-----|---------------|--------|
| **PagedAttention** | KV cache allocated in non-contiguous blocks on demand | 2-4x throughput vs naive serving; near-zero memory waste [arXiv:2309.06180] |
| **Continuous batching** | New requests join batch mid-generation | No idle GPU cycles waiting for long generations to finish |
| **OpenAI-compatible API** | Drop-in replacement for OpenAI API | Zero application code changes when switching from API to self-hosted |
| **Broad model support** | Supports most HuggingFace models, MoE, LoRA adapters | One serving framework for GPT-OSS, Qwen3, and others |
| **Quantization support** | AWQ, GPTQ, MXFP4, FP8 built-in | Run 120B+ models on single GPU via quantization |
| **LoRA hot-swap** | Serve multiple LoRA adapters on same base model | Multi-tenant without multiple copies of base weights |
| **Speculative decoding** | Draft model accelerates generation 1.5-2x | Latency reduction without quality loss |
| **Prefix caching** | Shared system prompts cached across requests | 10-20% token savings on repeated prefixes |
| **Chunked prefill** | Long prompts processed in chunks during batch idle | Doesn't block generation for other requests |

## Cons of vLLM for Single-GPU Deployment

| Con | What It Means | Impact |
|-----|---------------|--------|
| **High VRAM requirement** | No CPU offload by default; model must fit entirely in GPU | Limits model size to what VRAM allows |
| **Limited concurrency (large models)** | GPT-OSS-120B: only ~6 concurrent requests on H100 | Low throughput for heavy models; need multiple replicas |
| **Cold start latency** | Model loading takes 15-20s for large models | Not suitable for scale-to-zero without warm standby |
| **MoE routing overhead** | Expert dispatch adds 5-15ms per batch for MoE models | Minor latency penalty vs dense models |
| **Memory fragmentation** | Long-running sessions can fragment KV cache | Periodic restart may be needed under high load |
| **Not optimized for all architectures** | Custom attention patterns (e.g., GPT-OSS banded+dense) may not be fully optimized | Newer/exotic architectures may underperform vs custom kernels |
| **Single-GPU throughput ceiling** | Cannot exceed what one GPU computes | For >100 req/s at large model size, need multi-GPU or replicas |
| **No native CPU fallback** | If VRAM insufficient, fails rather than falling back to CPU | Unlike llama.cpp/Ollama which support partial CPU offload |
| **Complexity vs simpler options** | More configuration knobs than Ollama/llama.cpp | Overkill for personal single-user deployment |

## When to Use vLLM Single-GPU vs Alternatives

| Scenario | Best Option | Why |
|----------|-------------|-----|
| Production serving, >10 req/s | **vLLM** | PagedAttention + continuous batching maximize throughput |
| Personal/dev, 1-2 users | **Ollama** or **llama.cpp** | Simpler setup, CPU offload, less config |
| Latency-critical, single model | **vLLM** or **SGLang** | Speculative decoding, optimized kernels |
| Multi-model serving | **vLLM** | Native multi-model + LoRA hot-swap |
| Consumer GPU (8-24GB) | **Ollama** / **llama.cpp** | CPU+GPU hybrid offloading fills the gap |
| H100/A100 production | **vLLM** | Full utilization of high-end hardware |
| MoE model (GPT-OSS-120B) | **vLLM** | Best MoE support; explicit MXFP4 path |

## Key Trade-off: Throughput vs Simplicity

```
           Throughput
              ↑
              |     vLLM (PagedAttention, continuous batch)
              |       ↗
              |     SGLang (comparable, slightly different features)
              |   ↗
              |  TGI (production-ready, slightly lower peak)
              | ↗
              | Ollama (simple, CPU offload, lower throughput)
              |
              └──────────────────────────────────→ Simplicity
```

vLLM maximizes throughput but requires more setup, VRAM planning, and operational knowledge. For single-GPU deployments where you need maximum requests/second from expensive hardware, vLLM is the right choice. For casual use where simplicity matters more than throughput, Ollama or llama.cpp are better.

## Related

- [[VLLM Inference Engine]] — General vLLM capabilities
- [[VRAM-Based Model Selection]] — Choosing models by GPU memory
- [[SGLang Inference Framework]] — Alternative serving framework
- [[GPT-OSS-120B MXFP4 vs BF16]] — Specific deployment for GPT-OSS
