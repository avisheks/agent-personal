---
title: "KV Caching"
summary: "A memory-for-compute trade-off that stores Key and Value matrices from previous tokens to avoid recomputation during text generation, critical for making inference fast enough to be usable."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:43:46.061488+00:00
updatedAt: 2026-06-16T14:43:46.061488+00:00
---
# KV Caching

KV Caching is a memory optimization technique used during inference in transformer-based language models to avoid redundant computation when generating text sequentially. The technique exploits the fact that Key (K) and Value (V) matrices in the attention mechanism only depend on their input tokens and remain constant once computed, allowing them to be cached and reused across generation steps. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## How KV Caching Works

During text generation, language models produce tokens one at a time in an autoregressive manner. Without caching, each new token would require recomputing the Key and Value matrices for all previous tokens in the sequence. KV caching stores these matrices after their initial computation, enabling significant computational savings. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The K and V matrices have a useful property: they only depend on their input tokens, not on what comes after. This means once computed for a token position, they can be cached and reused for all subsequent generation steps. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Types of KV Caching

### Generation Cache
When generating sequences like "The cat sat on the mat" one token at a time, the model needs all previous K,V vectors for attention computation. Without caching, this would require recomputing K,V for "The", then "The cat", then "The cat sat"—resulting in quadratic computational overhead. With generation caching, each token's K,V is computed once and reused. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Prompt Cache
System prompts that are repeated across requests (such as "You are a helpful assistant...") can have their K,V cached and shared between requests. The first request computes and stores the cache, while later requests simply load from the existing cache. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Memory Requirements

KV caching comes with substantial memory costs that scale with context length and model architecture:

```
# Memory cost per token across all layers:
32 layers × 2 vectors (K,V) × 4096 dims × 2 bytes = 524KB per token

32K context = 17GB KV cache
128K context = 67GB KV cache (approaching model size!)
```

The memory requirements can approach or exceed the size of the model itself for long contexts. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Memory Optimization Techniques

Production systems employ several compression techniques to manage KV cache memory:

- **[[Grouped-Query Attention]] (GQA)**: Multiple attention heads share K,V matrices, providing up to 8× memory reduction
- **Quantization**: Using INT8 or INT4 precision instead of FP16, achieving 2-4× memory reduction  
- **Sliding Window**: Only caching recent tokens with a fixed cache size limit

^[Large Language Model (LLM) Training - Intro - final.pdf]

## Context Length Limitations

The "128K context" advertised by many models isn't just about computational capability—it's fundamentally limited by the memory required to store 67GB of KV cache. Most practical context limits are actually memory limits rather than computational ones. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Performance Impact

KV caching represents a classic compute-memory tradeoff. While it dramatically reduces the computational overhead of sequential generation from quadratic to linear complexity, it requires substantial memory allocation. The technique is essential for making text generation fast enough to be practically usable in production systems. ^[Large Language Model (LLM) Training - Intro - final.pdf]

When KV cache compression techniques are applied, they can impact model performance. If a model "performs bad" at inference, it could be due to aggressive compression of the KV cache rather than fundamental model limitations. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Related Concepts

KV caching is closely related to other inference optimization techniques like [[Prompt Caching]] and [[Speculative Decoding]], and is implemented in inference frameworks such as the [[vLLM Inference Engine]]. The technique is particularly important for [[long-context-scaling]] applications where memory efficiency becomes critical.
