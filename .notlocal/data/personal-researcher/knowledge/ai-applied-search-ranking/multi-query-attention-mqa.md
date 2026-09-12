---
title: "multi-query-attention-mqa"
summary: ""
sources:
  - ai-applied-search-ranking/grouped-query-attention-gqa-geeksforgeeks.md
  - ai-applied-search-ranking/what-is-grouped-query-attention-gqa-ai-tldr.md
createdAt: 2026-07-30T17:10:38.467850+00:00
updatedAt: 2026-07-30T17:10:38.467850+00:00
---
# Multi-Query Attention (MQA)

**Multi-Query Attention (MQA)** is an optimization technique for transformer models that reduces memory usage and improves inference speed by sharing key and value representations across all attention heads while maintaining separate query representations for each head. MQA represents one extreme of the attention mechanism spectrum, with [[Grouped Query Attention (GQA)]] serving as a middle ground between MQA and traditional multi-head attention. ^[grouped-query-attention-gqa-geeksforgeeks.md] ^[what-is-grouped-query-attention-gqa-ai-tldr.md]

## Architecture

In standard multi-head attention (MHA), each attention head maintains its own separate query, key, and value representations. MQA modifies this by having all query heads share a single set of keys and values, while each head retains its own unique queries. This architectural change significantly reduces the number of parameters and memory requirements during inference. ^[grouped-query-attention-gqa-geeksforgeeks.md]

The attention computation in MQA follows the same mathematical framework as standard attention:

```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

However, instead of having H separate key and value heads for H query heads, MQA uses only one shared key-value pair across all heads. ^[grouped-query-attention-gqa-geeksforgeeks.md]

## Performance Characteristics

MQA offers substantial computational benefits compared to multi-head attention. It achieves inference speeds that are 1.5-2× faster than MHA while using the lowest memory footprint among attention variants. However, this efficiency comes at the cost of reduced accuracy, typically showing a 5-15% decrease in performance compared to MHA across various tasks. ^[grouped-query-attention-gqa-geeksforgeeks.md]

The memory complexity reduction is significant, as MQA eliminates the need to store separate key-value pairs for each attention head in the KV cache. This makes it particularly beneficial for long-context processing and scenarios with memory constraints. ^[what-is-grouped-query-attention-gqa-ai-tldr.md]

## Relationship to Other Attention Mechanisms

MQA sits at one end of the attention mechanism spectrum. At the other end is multi-head attention (MHA), where each query head has its own dedicated key and value heads. [[Grouped Query Attention (GQA)]] provides a compromise between these approaches by organizing query heads into groups, with each group sharing a single key-value pair. ^[what-is-grouped-query-attention-gqa-ai-tldr.md]

| Method | K/V Heads (for 32 query heads) | KV-cache size | Quality | Typical use |
|--------|--------------------------------|---------------|---------|-------------|
| Multi-head (MHA) | 32 (one per query) | Largest | Best | Older/smaller models |
| Grouped-query (GQA) | 4 or 8 (shared in groups) | Small | Near-MHA | Most modern open models |
| Multi-query (MQA) | 1 (shared by all) | Smallest | Slight drop | Latency-critical applications |

^[what-is-grouped-query-attention-gqa-ai-tldr.md]

## Applications and Use Cases

MQA is particularly well-suited for latency-critical applications where inference speed is prioritized over maximum accuracy. The technique is most beneficial in scenarios involving long sequences, high batch sizes, or memory-constrained environments, as the KV cache grows with sequence length and concurrent users. ^[what-is-grouped-query-attention-gqa-ai-tldr.md]

The approach is less commonly used in modern large language models compared to [[Grouped Query Attention (GQA)]], as GQA provides a better balance between efficiency and quality retention. However, MQA remains relevant for specific deployment scenarios where maximum memory efficiency is required. ^[grouped-query-attention-gqa-geeksforgeeks.md]

## Limitations

The primary limitation of MQA is the quality degradation that results from forcing all attention heads to share the same key-value representations. This constraint can reduce the model's ability to capture diverse attention patterns and relationships in the input data. Additionally, the shared key-value approach can lead to less stable training compared to multi-head attention. ^[grouped-query-attention-gqa-geeksforgeeks.md] ^[what-is-grouped-query-attention-gqa-ai-tldr.md]

Despite these limitations, MQA's extreme efficiency makes it valuable for specific deployment scenarios where the trade-off between speed and accuracy is acceptable.
