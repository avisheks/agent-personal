---
title: "Cloud LLM Inference Services"
summary: "Managed LLM inference options across AWS (SageMaker LMI, Bedrock, Inferentia), GCP (Vertex AI, Cloud TPU), Azure (Azure ML, Azure OpenAI), and specialized providers (NVIDIA NIM, Together.ai, Fireworks.ai, Modal). Zero-ops options vs self-managed Kubernetes tradeoffs."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Cloud LLM Inference Services

## AWS

| Service | Ops Level | Multi-Node | Best For |
|---------|-----------|------------|----------|
| **SageMaker LMI** | Medium (managed containers) | Yes (multi-instance) | Teams wanting managed infra + model control |
| **Bedrock** | Zero | Abstracted | Pay-per-token, zero ops |
| **EKS + vLLM** | High (self-managed) | Yes (full control) | Maximum flexibility, cost optimization |
| **Inferentia2/Trainium** | Medium | Multi-chip within instance | ~40% lower cost/token vs GPU (AWS claim) |

^[multi-node-llm-inference-solutions.md]

## GCP

| Service | Ops Level | Multi-Node | Best For |
|---------|-----------|------------|----------|
| **Vertex AI + vLLM** | Medium | Yes (multi-host GPU/TPU) | GCP-native teams |
| **GKE + vLLM** | High | Yes (LeaderWorkerSet) | Full control on K8s |
| **Cloud TPU (JetStream)** | Medium | Multi-host TPU slices | Cost-effective at very high scale |

## Azure

| Service | Ops Level | Multi-Node | Best For |
|---------|-----------|------------|----------|
| **Azure ML (Foundry)** | Medium | Managed compute | Enterprise, 1900+ model catalog |
| **AKS + vLLM** | High | Yes | Full flexibility |
| **Azure OpenAI Service** | Zero | Abstracted | Enterprise compliance (SOC2, BAA, GDPR) |

## Specialized Providers

| Provider | Differentiator | Pricing | Scale-to-Zero |
|----------|---------------|---------|---------------|
| **NVIDIA NIM** | Pre-optimized TRT-LLM containers | License | No |
| **Together.ai** | Three deployment modes, fast new model support | Per-token | Yes |
| **Fireworks.ai** | FireAttention, 4x prefill claim | Per-token | Yes |
| **Modal** | Serverless GPU, ~10s cold start | Per-second | Yes |
| **HF Endpoints** | Deploy from Hub, SOC2 | Per-uptime | Yes |

## Decision: Managed vs Self-Hosted

| Factor | Managed (Bedrock/Vertex/Azure) | Self-Hosted (EKS/GKE/AKS + vLLM) |
|--------|-------------------------------|-----------------------------------|
| Ops burden | Zero | High (GPU scheduling, model loading, monitoring) |
| Cost at low volume | Optimal (pay-per-use) | Wasteful (fixed infra) |
| Cost at high volume | Expensive (per-token adds up) | Cheaper (amortized infra) |
| Fine-tuning | Limited (provider-dependent) | Full control |
| Data sovereignty | Third-party processing | On-premise possible |
| Latency control | Limited | Full (P99 tunable) |
| Model freshness | Provider decides when to update | You control versions |

Break-even: ~50-100M tokens/day for self-hosted to beat managed pricing (varies by provider and model). ^[multi-node-llm-inference-solutions.md]

## Related

- [[Multi-Node LLM Inference Frameworks]] — Open-source options
- [[VLLM Inference Engine]] — vLLM details
