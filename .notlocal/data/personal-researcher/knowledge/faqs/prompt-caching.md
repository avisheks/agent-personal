---
title: "Prompt Caching"
summary: "Technique that reuses computed KV cache from repeated prompt prefixes across requests, avoiding redundant prefill computation. Saves 10-30% tokens/cost for system-prompt-heavy workloads. vLLM implements as zero-overhead prefix caching; Anthropic/OpenAI offer API-level caching with tiered pricing. Not useful when prompts are highly diverse (low cache hit rate)."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Prompt Caching

**Prompt caching** (also called prefix caching) stores and reuses the computed KV cache from shared prompt prefixes across multiple requests, eliminating redundant prefill computation for repeated system prompts, few-shot examples, or document contexts.

## Mechanism

When multiple requests share the same prefix (e.g., a system prompt), the model must compute attention KV pairs for those tokens on every request. Prompt caching computes them ONCE, stores the KV cache, and reuses it for subsequent requests with the same prefix.

```
Without caching:  [System prompt: 2000 tokens] + [User query: 100 tokens] → compute ALL 2100
With caching:     [System prompt: 2000 tokens CACHED] + [User query: 100 tokens] → compute only 100
Savings:          95% of prefill computation eliminated for this request
```

## Implementations

- **vLLM**: Zero-overhead prefix caching (enabled by default in V1); hash-based cache lookup
- **Anthropic API**: Explicit cache_control breakpoints; cached input at 90% discount
- **OpenAI API**: Automatic caching for repeated prefixes; 50% discount on cached tokens
- **SGLang**: RadixAttention — tree-based prefix sharing for branching conversations

## When NOT to Use

- Prompts are highly diverse (unique per request) → near-zero cache hit rate
- KV cache memory is the bottleneck → caching consumes VRAM that could serve more concurrent requests
- Single-shot batch processing → no repeated prefixes to cache

## Related

- [[vLLM Single-GPU Requirements]] — prefix caching as throughput optimization
- [[Multi-Node LLM Inference Frameworks]]
