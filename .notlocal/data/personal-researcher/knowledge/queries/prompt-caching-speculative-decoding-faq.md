---
title: "What is prompt caching? What is speculative decoding?"
summary: "Prompt caching: reuses computed KV cache from repeated prefixes across requests, saving 10-30% cost (vLLM zero-overhead, Anthropic 90% discount). Not useful with diverse prompts. Speculative decoding: draft model proposes N tokens, target verifies in one pass, reducing latency 1.5-2x with zero quality loss. Not useful when throughput (not latency) is the bottleneck or batch sizes are large."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
See FAQ report: [[LLM Inference Optimization FAQs]]
- [[Prompt Caching]]
- [[Speculative Decoding]]
