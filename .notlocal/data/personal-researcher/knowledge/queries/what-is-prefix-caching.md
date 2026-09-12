---
title: "What is prefix caching?"
summary: "Prefix caching (= prompt caching) stores computed KV cache from shared prompt prefixes and reuses it across requests, avoiding redundant prefill computation. vLLM calls it 'prefix caching' (hash-based block lookup, zero-overhead, enabled by default in V1). SGLang calls it 'RadixAttention' (tree-based prefix sharing). Anthropic/OpenAI call it 'prompt caching' at the API level with tiered pricing (90%/50% discount). Same mechanism, different names."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
## Short Answer

**Prefix caching and prompt caching are the same thing** — different names used by different systems for the same mechanism: store the computed KV cache for a repeated prompt prefix, reuse it on subsequent requests.

| System | Name Used | Implementation |
|--------|-----------|---------------|
| **vLLM** | Prefix caching | Hash-based KV block lookup; zero-overhead; enabled by default in V1 |
| **SGLang** | RadixAttention | Tree-based prefix sharing; supports branching conversations |
| **Anthropic API** | Prompt caching | Explicit `cache_control` breakpoints; 90% discount on cached tokens |
| **OpenAI API** | Prompt caching | Automatic detection of repeated prefixes; 50% discount |

## Mechanism

```
Request 1: [System prompt: 2000 tokens] + [User query A: 100 tokens]
  → Compute all 2100 tokens; STORE KV cache for the 2000-token prefix

Request 2: [System prompt: 2000 tokens] + [User query B: 150 tokens]
  → Hash of prefix matches cached block → REUSE KV cache
  → Only compute the new 150 tokens
  → Savings: 93% of prefill eliminated
```

**How vLLM implements it:** Each KV cache block is identified by a hash of its token content. When a new request arrives, vLLM hashes its prefix tokens in block-sized chunks and checks for matches. Matched blocks are reused without recomputation. Unmatched blocks are computed fresh and added to the cache.

**How SGLang differs (RadixAttention):** Instead of flat hash lookup, SGLang maintains a radix tree (trie) of all cached prefixes. This enables efficient BRANCHING — if 10 requests share the first 1000 tokens but diverge after, the tree stores the shared prefix once and branches. More memory-efficient than vLLM's approach for workloads with partial prefix overlap.

## Principal+ Insight

Prefix caching is a **memory-compute trade-off**, not a free optimization:
- Cached KV blocks consume VRAM that could otherwise hold more concurrent requests
- If your bottleneck is KV cache capacity (limited concurrency), caching HURTS — it reserves memory for prefix blocks that may not be reused
- The real production challenge is **eviction policy** under shifting traffic patterns, not just enabling the feature

## When NOT to Use

- **Diverse prompts** (unique per request) → near-zero cache hit rate → lookup overhead is pure waste
- **Memory-constrained serving** → cached blocks compete with active request KV slots
- **Single-shot batch processing** → no repeated prefixes to cache

## Quantitative Impact

- Workload with 80% tokens in shared system prompt → 70-80% effective input cost reduction
- Anthropic: cached tokens at 90% discount ($0.30 vs $3.00 per 1M input tokens on Sonnet)
- OpenAI: cached tokens at 50% discount
- Self-hosted (vLLM): 10-30% higher throughput from freed prefill compute

## Related

- [[Prompt Caching]] — Full knowledge page
- See also: FAQ report [[LLM Inference Optimization FAQs]], FAQ 1
