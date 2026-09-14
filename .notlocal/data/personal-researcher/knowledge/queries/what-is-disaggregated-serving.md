---
title: "What is disaggregated serving?"
summary: "Disaggregated serving separates LLM inference into two distinct GPU pools: prefill nodes (compute-bound, process input prompt in parallel) and decode nodes (memory-bandwidth-bound, generate tokens autoregressively). This eliminates the fundamental resource mismatch where prefill wastes memory bandwidth and decode wastes FLOPS. vLLM reports 2.5x throughput improvement. Key trade-off: adds KV cache transfer latency between pools + operational complexity."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
See FAQ report: [[LLM Inference Optimization FAQs]], FAQ 3
- [[Multi-Node LLM Inference Frameworks]]
- [[Prompt Caching]]
