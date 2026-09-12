# LLM Inference Optimization — FAQs

> **Last Updated:** 2026-06-07 | **Version:** 2.0

---

## FAQ 1: What is Prompt Caching (Prefix Caching)?

> **Terminology:** "Prompt caching" and "prefix caching" are the same thing. vLLM/SGLang call it prefix caching (implementation term). Anthropic/OpenAI call it prompt caching (API term). Same mechanism.

### Principal+ Answer

Prompt caching stores the computed KV cache from shared prompt prefixes and reuses it across requests, eliminating redundant prefill computation. When 100 requests share a 2,000-token system prompt, the model computes those 2,000 tokens ONCE and serves the cached KV pairs to all subsequent requests — reducing prefill cost by up to 95% for the shared portion [1][2].

**Quantitative impact:** For a workload where 80% of tokens are in a shared system prompt, caching reduces effective input cost by 70-80%. Anthropic prices cached tokens at 90% discount; OpenAI at 50% [1]. On self-hosted vLLM, caching translates to 10-30% higher throughput because freed prefill compute serves more concurrent decode slots.

**Mechanism:** vLLM V1 implements zero-overhead prefix caching via hash-based KV block lookup — if the hash of a prompt prefix matches a cached block, the KV pairs are reused without recomputation. SGLang uses RadixAttention, a tree-based structure enabling branching prefix sharing (e.g., different user queries branching from a shared few-shot prefix) [2].

**When it DOESN'T work:**
- Highly diverse prompts (unique per request) → near-zero cache hit rate → the cache lookup overhead is pure waste
- Memory-constrained serving → cached KV blocks consume VRAM that could instead serve more concurrent requests. If your bottleneck is KV cache capacity (limited concurrency), caching HURTS because it reserves memory for prefix blocks that may not be reused
- Batch processing (one-shot, no repeated prefixes) → nothing to cache

**The non-obvious production insight:** Cache eviction policy matters more than cache existence. An LRU eviction policy works for steady-state traffic but fails during traffic pattern shifts (morning: code queries with code system prompt; afternoon: chat queries with different system prompt). If the morning cache evicts the afternoon prefix, you get zero hits during the transition. Production systems need traffic-aware eviction or time-weighted retention.

### How This Differs by Seniority

| Level | What They'd Say | What's Missing |
|-------|----------------|----------------|
| **Junior/Mid** | "Prompt caching stores repeated prompts so you don't process them again. It makes things faster and cheaper." | No quantitative impact, no mechanism detail, no failure modes, no eviction policy considerations |
| **Senior** | "It caches KV pairs for shared prefixes. Saves compute proportional to prefix length. vLLM and API providers support it. Doesn't help with unique prompts." | Misses: memory trade-off (cache vs concurrency), eviction policy complexity, interaction with PagedAttention block allocation, SGLang's tree-based alternative |
| **Principal+** | "It's a memory-compute trade-off: cached KV blocks reduce prefill but consume VRAM that limits concurrency. The real production challenge is eviction policy under shifting traffic patterns, not just enabling the feature." | N/A (full picture) |

### Key Signals That Distinguish Principal+ Thinking

- Recognizes that caching is a **memory trade-off**, not a free optimization — cached blocks compete with active request KV cache for VRAM
- Considers **eviction policy** as the operationally hard problem (not just "turn it on")
- Knows when caching is **counterproductive** (memory-constrained, diverse prompts) — not just when it helps

---

## FAQ 2: What is Speculative Decoding?

### Principal+ Answer

Speculative decoding reduces per-request **latency** (not throughput) by having a small, fast "draft" model propose N tokens, then the large target model verifies all N in a single forward pass via parallel KV computation. Accepted tokens are emitted; rejected tokens are resampled from the target's exact distribution — making the output **mathematically identical** to standard autoregressive decoding [3][4].

**Quantitative impact:** Typical speedup is 1.5-2x on wall-clock latency. A 70B model generating at 50ms/token normally produces 1 token per forward pass. With speculative decoding (5 tokens drafted, ~70% acceptance rate), you produce ~3.5 tokens per target forward pass — effective latency of ~14ms/token. The draft model (e.g., 1B) generates 5 tokens in ~5ms, so total cycle is 55ms for 3.5 tokens vs 175ms normally [3].

**Why it's lossless:** Modified rejection sampling ensures the output distribution equals the target model's. If draft token probability ≥ target probability, accept. Otherwise, accept with probability (target/draft) and resample from a correction distribution. This is provably equivalent to sampling from the target alone [4].

**When it DOESN'T work:**
- **Throughput-bound workloads** (high batch size): The GPU is already saturated computing batched forward passes. Adding speculative tokens increases compute without reducing per-token latency because the batch is the bottleneck, not single-request generation speed
- **No suitable draft model**: Acceptance rate depends on draft-target alignment. A poorly matched draft (<40% acceptance) adds latency instead of reducing it. Finding/training a good draft model is non-trivial engineering
- **Memory-constrained**: The draft model consumes VRAM (1-3GB for a 1B draft) that could otherwise hold more KV cache slots, reducing concurrency
- **Streaming with tight TTFT requirements**: The initial draft adds a small delay to time-to-first-token (draft generation time before any verification)

**The non-obvious production insight:** Speculative decoding helps **latency at low batch sizes** but can actually HURT total system throughput. If you're serving 100 concurrent users, the GPU is already busy — adding speculation competes for the same compute cycles. The technique is most valuable for latency-sensitive single-user scenarios (coding assistants, real-time chat) where the GPU has idle capacity between tokens. In high-utilization serving (>70% GPU), standard continuous batching often outperforms speculative approaches on aggregate metrics.

### How This Differs by Seniority

| Level | What They'd Say | What's Missing |
|-------|----------------|----------------|
| **Junior/Mid** | "A small model generates tokens and a big model checks them. It's faster because the big model can verify multiple tokens at once." | No understanding of WHY it's lossless (rejection sampling), no quantitative speedup, no awareness that it trades throughput for latency |
| **Senior** | "Draft model proposes tokens, target verifies in parallel. Lossless via rejection sampling. 1.5-2x speedup. Requires a well-aligned draft model with high acceptance rate." | Misses: throughput vs latency distinction (it ONLY helps latency), batch-size dependency (useless at high batch), memory cost competing with KV cache, production insight about utilization |
| **Principal+** | "It's a latency optimization that trades GPU compute and memory for faster single-request generation. Valuable at low utilization; counterproductive at high batch sizes where the GPU is already saturated. The real engineering challenge is draft model selection and knowing when to disable it based on current load." | N/A (full picture) |

### Key Signals That Distinguish Principal+ Thinking

- Distinguishes **latency vs throughput** precisely — speculative decoding helps one, can hurt the other
- Understands the **utilization dependency** — valuable at low load, counterproductive at high load
- Recognizes the **adaptive control problem** — production systems should dynamically enable/disable speculation based on current batch size and GPU utilization

---

## FAQ 3: What is Disaggregated Serving?

### Principal+ Answer

Disaggregated serving separates LLM inference into two **physically distinct GPU pools**: prefill nodes (process the input prompt) and decode nodes (generate output tokens one at a time). This eliminates the fundamental resource mismatch in standard serving where both phases share the same GPU despite having opposite computational profiles [5][6].

**The core problem it solves:**
```
Standard (aggregated) serving — one GPU does both:
  Prefill: COMPUTE-bound (parallel matrix multiplies over all input tokens)
    → GPU compute fully utilized, memory bandwidth idle
  Decode:  MEMORY-BANDWIDTH-bound (sequential, one token at a time)
    → Memory bandwidth saturated, GPU compute 10-30% utilized
    
Result: During decode (majority of time), 70-90% of GPU FLOPS are wasted.
During prefill, memory bandwidth is wasted. Neither phase uses the full GPU.
```

**Disaggregated architecture:**
```
┌─────────────────┐         KV cache         ┌──────────────────┐
│  Prefill Pool   │ ──── transfer (NVLink/ ──→│   Decode Pool    │
│  (compute-opt)  │      InfiniBand)          │  (bandwidth-opt) │
│                 │                           │                  │
│ High FLOPS util │                           │ High BW util     │
│ Short residence │                           │ Long residence   │
│ Batch many      │                           │ Serve many       │
│ prompts at once │                           │ concurrent users │
└─────────────────┘                           └──────────────────┘
```

**Quantitative impact:** vLLM reports **2.5x throughput improvement** on a single 8-GPU node with disaggregated prefill/decode (Apr 2026 blog) [5]. Fireworks.ai claims 4x on prefill-heavy workloads via their "FireAttention" disaggregated architecture.

**Why it works — the math:**
```
Standard: GPU utilization during decode ≈ 15-30% (bandwidth-bound)
  → Effective throughput = 30% × peak FLOPS

Disaggregated: Prefill GPUs at 80%+ compute util; Decode GPUs at 80%+ BW util
  → Both pools operating near hardware limits
  → System throughput ≈ 2-3x (both pools efficient simultaneously)
```

**When it DOESN'T work:**
- **Single-user latency-sensitive**: Adding KV cache transfer between pools adds 5-20ms to time-to-first-token. For single-user interactive chat, this latency penalty may negate throughput gains.
- **Small scale (<4 GPUs)**: Not enough GPUs to meaningfully separate pools. Need at minimum 2 prefill + 2 decode to see benefit.
- **Short prompts + long outputs**: If prefill is trivial (10 tokens) and decode is long (2000 tokens), the prefill pool is idle 99% of the time. Works best when both phases have substantial work.
- **Network-constrained**: KV cache transfer between pools requires high-bandwidth interconnect (NVLink within node, InfiniBand across nodes). On Ethernet, transfer latency dominates.

**The non-obvious production insight:** The hardest engineering problem is **KV cache routing** — when a prefill completes, which decode node should receive the KV cache? Naive round-robin creates imbalanced decode loads. KV-aware routing (as implemented in llm-d and NVIDIA Dynamo) tracks each decode node's cache occupancy and routes to the node with most available slots. This routing decision happens in <1ms but determines system-level throughput.

### How This Differs by Seniority

| Level | What They'd Say | What's Missing |
|-------|----------------|----------------|
| **Junior/Mid** | "It separates the prompt processing from token generation onto different GPUs to make things faster." | No understanding of WHY (compute vs bandwidth mismatch), no quantitative impact, no awareness of KV cache transfer cost or routing complexity |
| **Senior** | "Prefill is compute-bound, decode is memory-bandwidth-bound. Separating them lets each pool be optimized for its bottleneck. vLLM gets 2.5x throughput. Requires high-bandwidth interconnect for KV transfer." | Misses: KV-aware routing as the hard problem, when it's counterproductive (low scale, short prompts, latency-sensitive), interaction with prefix caching (cached prefixes eliminate prefill entirely, reducing disaggregation benefit) |
| **Principal+** | "It's a systems-level resource scheduling optimization. The real challenge is KV cache routing — deciding which decode node receives each completed prefill — not the separation itself. And it interacts non-obviously with prefix caching: if 80% of prefills hit cache, the prefill pool is underutilized and you've over-provisioned." | N/A (full picture) |

### Key Signals That Distinguish Principal+ Thinking

- Identifies **KV cache routing** (not the split itself) as the operationally hard problem
- Recognizes the **interaction with prefix caching** — high cache hit rates reduce prefill load, potentially making the prefill pool over-provisioned
- Understands **when it's counterproductive** — single-user latency, small scale, short prompts — not just when it helps

---

## FAQ 4: What is OpenAI-Compatible API?

### Principal+ Answer

The "OpenAI-compatible API" is a **de-facto industry standard** HTTP API specification that mirrors OpenAI's REST endpoints (`/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`). It is NOT an official standard body specification — it's "whatever OpenAI ships" that the ecosystem reverse-engineers and replicates. Serving frameworks and providers implement it so that applications built for OpenAI can switch to any backend by changing a single line: `base_url` [7].

**What it standardizes:**
```python
# Application code — works with ANY OpenAI-compatible backend:
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",  # ← Only this line changes
    api_key="not-needed-for-local",       # vLLM, SGLang, Ollama, etc.
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-32B",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7,
    max_tokens=1000,
)
```

**Who implements it:**

| Layer | Implementers | Coverage |
|-------|-------------|----------|
| **Self-hosted engines** | vLLM, SGLang, Ollama, llama.cpp server, TGI | Full chat/completions; partial embeddings/tools |
| **Inference providers** | Together.ai, Fireworks.ai, Groq, Anyscale, DeepInfra | Full parity (most features) |
| **Cloud managed** | Azure OpenAI, AWS Bedrock (via adapter) | Full or near-full |
| **Local tools** | LM Studio, Jan, GPT4All | Chat completions; basic |

**Key endpoints in the spec:**
```
POST /v1/chat/completions    — Chat format (messages array)
POST /v1/completions         — Raw completion (prompt string)
POST /v1/embeddings          — Text embeddings
GET  /v1/models              — List available models
POST /v1/chat/completions    — With tools/function_calling
     (streaming via SSE)     — Server-Sent Events for token streaming
```

**What varies across implementations (the compatibility gaps):**
- **Function calling / tools** — Format varies; some engines support OpenAI's exact schema, others approximate
- **Response format** (JSON mode, structured output) — Partial support in most engines
- **Logprobs** — Not all engines expose token log-probabilities
- **Vision/multimodal** — Image inputs via base64/URL; inconsistent support
- **Streaming behavior** — SSE format matches but chunking granularity differs
- **Reasoning/thinking tokens** — No standard; GPT-OSS uses "Harmony" format, Qwen3 uses `<think>` tags, DeepSeek-R1 uses `<reasoning>` — NOT part of the "OpenAI-compatible" spec

**When it DOESN'T work (compatibility breaks):**
- **Model-specific features**: GPT-OSS-120B's Harmony response format, Qwen3's thinking mode toggle, Claude's `cache_control` — all require model-specific code despite the "compatible" API
- **Behavioral differences**: Same prompt + same parameters → different output quality/style per backend (the API is format-compatible, not behavior-compatible)
- **Rate limiting / error codes**: Each provider has different rate limit semantics, retry behavior, and error response formats
- **Token counting**: Tokenizers differ between models; `max_tokens` means different actual text lengths

**The non-obvious production insight:** "OpenAI-compatible" creates a false sense of portability. The API format is portable; the **application behavior** is not. A production app tuned to GPT-4's response style (conciseness, formatting, tool-calling reliability) will degrade when pointed at a local Qwen3-32B even though the API calls succeed. The compatibility is at the **transport layer**, not the **semantic layer**. Real portability requires model-specific prompt tuning, output parsing, and quality evaluation — the API compatibility just eliminates the HTTP/SDK rewrite.

### How This Differs by Seniority

| Level | What They'd Say | What's Missing |
|-------|----------------|----------------|
| **Junior/Mid** | "It means you can use the OpenAI Python library to talk to other models. Just change the URL." | No awareness of compatibility gaps (tools, vision, reasoning tokens), no understanding that behavior differs even when format matches, no production portability caveats |
| **Senior** | "It's a de-facto standard for LLM serving APIs. vLLM, Together, etc. implement it. Lets you swap backends without rewriting clients. But some features like function calling have inconsistent support across engines." | Misses: transport vs semantic portability distinction, model-specific features that break the abstraction (Harmony, thinking tokens), rate-limit/error divergence, token-counting differences |
| **Principal+** | "It's transport-layer portability, not semantic portability. The API calls succeed but application behavior changes because models respond differently to the same prompts. Real backend portability requires prompt adaptation, output parsing, and quality eval — the 'compatible API' just saves you an HTTP rewrite, which is the easy part." | N/A (full picture) |

### Key Signals That Distinguish Principal+ Thinking

- Distinguishes **transport compatibility** (API format matches) from **semantic compatibility** (model behavior matches) — they're independent
- Identifies the **false sense of portability** — teams assume "compatible API = drop-in replacement" and are surprised when quality degrades
- Knows the **specific gaps** that break real applications (reasoning tokens, tool calling format, tokenizer differences) rather than just saying "mostly compatible"

---

## References

- [1] Anthropic / OpenAI API documentation — Prompt caching pricing: Anthropic 90% discount, OpenAI 50% discount on cached input tokens
- [2] vLLM V1 blog (Jan 2025) — Zero-overhead prefix caching enabled by default; SGLang RadixAttention as tree-based alternative
- [3] Leviathan et al. (2023) — "Fast Inference from Transformers via Speculative Decoding" — arXiv:2211.17192 — Original speculative decoding paper; proves lossless via modified rejection sampling
- [4] Chen et al. (2023) — "Accelerating Large Language Model Decoding with Speculative Sampling" — arXiv:2302.01318 — Independent concurrent work on same technique; establishes 2-3x speedup range
- [5] vLLM blog (Apr 2026) — Disaggregated Prefill/Decode — 2.5x throughput improvement on single 8-GPU node; first-party benchmark
- [6] Zhong et al. (2024) — "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving" — arXiv:2401.09670 — Academic foundation for disaggregated serving; shows 2-4x goodput improvement
- [7] OpenAI API Reference (2024-present) — platform.openai.com/docs/api-reference — De-facto specification that vLLM, SGLang, Together.ai, and 50+ others replicate

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-07 | Initial generation | FAQ entries for prompt caching and speculative decoding with principal+ framing and seniority contrast |
| 2026-06-07 | Added prefix caching terminology note | Clarified that "prefix caching" (vLLM/SGLang) = "prompt caching" (Anthropic/OpenAI API) — same mechanism, different names |
| 2026-06-07 | Added FAQ 3: Disaggregated Serving | Prefill/decode separation, 2.5x throughput, KV routing as hard problem, interaction with prefix caching |
| 2026-06-07 | Added FAQ 4: OpenAI-Compatible API | De-facto standard, transport vs semantic portability, compatibility gaps, who implements it |
