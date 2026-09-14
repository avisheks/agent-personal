---
title: "Speculative Decoding"
summary: "Latency optimization that uses a small/fast 'draft' model to propose N tokens, then the large target model verifies all N in a single forward pass (parallel verification). Reduces wall-clock latency 1.5-2x without quality loss because rejected tokens are resampled from the target distribution. Not useful when throughput (not latency) is the bottleneck, or when no suitable draft model exists."
sources:
  - vllm/multi-node-llm-inference-solutions.md
createdAt: "2026-06-07T00:00:00Z"
updatedAt: "2026-06-07T00:00:00Z"
---
# Speculative Decoding

**Speculative decoding** is a latency optimization technique where a small, fast "draft" model generates N candidate tokens speculatively, and the large "target" model verifies all N tokens in a single parallel forward pass. Accepted tokens are emitted immediately; rejected tokens are resampled from the target's distribution. The output is mathematically identical to the target model alone.

## Mechanism

```
Standard autoregressive (slow):
  Token 1 → full forward pass → Token 2 → full forward pass → ... → Token N
  Wall clock: N × latency_per_token

Speculative decoding (fast):
  Draft model: proposes tokens [t1, t2, t3, t4, t5] in ~5ms total
  Target model: verifies ALL 5 in ONE forward pass (~50ms)
  Result: accept t1, t2, t3 (correct), reject t4 → resample from target
  Wall clock: ~55ms for 4 tokens instead of 4 × 50ms = 200ms
  Speedup: ~3.6x in this example (typical: 1.5-2x due to varying acceptance rates)
```

## Key Properties

- **Lossless**: Output distribution is IDENTICAL to target model alone (provable via modified rejection sampling)
- **Acceptance rate**: Typically 60-80% for well-matched draft models; determines actual speedup
- **Draft model**: Usually 10-20x smaller than target (e.g., 1B draft for 70B target)
- **Trade-off**: Uses draft model memory + compute; only helps if draft is much faster than target

## Implementations

- **vLLM**: Built-in speculative decoding support
- **TensorRT-LLM**: Native speculative decoding with CUDA optimization
- **SGLang**: Supported
- **Medusa**: Multi-head speculative (no separate draft model; adds prediction heads to target)

## When NOT to Use

- **Throughput-bound** (not latency-bound): speculative decoding doesn't improve tokens/second/GPU — it reduces per-request latency at the cost of extra compute
- **No suitable draft model**: If the draft model's acceptance rate is <40%, overhead exceeds benefit
- **Batch size > 1**: At high batch sizes, GPU is already saturated; speculation adds compute without latency benefit
- **Memory-constrained**: Draft model consumes VRAM that could serve additional KV cache slots

## Related

- [[vLLM Single-GPU Requirements]] — speculative decoding as latency optimization
- [[Multi-Node LLM Inference Frameworks]]
