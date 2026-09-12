# GPT vs Qwen: Open-Source vs Proprietary LLMs

> **Last Updated:** 2026-05-31 | **Read time:** ~28 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** The GPT vs Qwen landscape has evolved from monolithic dense transformers to sparse Mixture-of-Experts architectures that activate only a fraction of total parameters per token [5][3].
> Key players: GPT-4/GPT-4o (proprietary API), Qwen2.5-72B/Qwen2.5-MoE (open-weight), Mixtral 8x7B [3], DeepSeek-V2 [13]. Main open problem: MoE expert collapse under production load imbalance [4].
> Recent breakthrough: DeepSeek-V2 (May 2024) demonstrated economical MoE with multi-head latent attention at 236B total / 21B active params [13]. Trend: open-weight models closing the gap on proprietary APIs, making self-hosting viable at scale.

## State of the Art

### Current Best Approaches

- **Proprietary API (GPT-4o)** — Dense transformer with undisclosed architecture; strongest general capability but no weight access; used via rate-limited API [1]
- **Open-weight MoE (Qwen2.5-72B-MoE)** — Sparse gating with top-k expert selection; full weight access enables quantization, fine-tuning, and self-hosting [2]
- **Efficient MoE (Mixtral 8x7B)** — 8 experts, 2 active per token, delivering 12B active params at 46B total; strong quality/cost ratio [3]
- **Multi-head Latent Attention MoE (DeepSeek-V2)** — Compresses KV cache via latent vectors; 236B total with 21B active; lowest cost-per-token among frontier models [13]
- **Quantized self-hosted deployment (vLLM + AWQ)** — PagedAttention [6] with 4-bit quantization [15] enables serving 70B models on a single A100-80GB

### Recent Breakthroughs (last 12 months)

- **DeepSeek-V2** (May 2024): 236B MoE with economical training and inference; introduced MLA to reduce KV cache 93% [13]
- **Qwen2.5 series** (Sep 2024): Open-weight family matching GPT-4-turbo on MMLU at 72B scale; strong multilingual and code [2]
- **Mixtral 8x22B** (Apr 2024): Scaled sparse MoE to 141B total params; outperformed Llama 2 70B at lower inference cost [3]
- **AWQ adoption** (2024): Activation-aware weight quantization became standard for production serving; <1% quality loss at 4-bit [15]

### Open Problems

- **Expert collapse in production**: Router concentrates traffic on few experts under real workload distributions [4][5]
- **Long-context MoE serving**: Combining 128K+ context with sparse routing creates memory scheduling challenges [9][10]
- **Benchmark contamination**: Open models may overfit to public eval sets; Chatbot Arena provides decontaminated signal but is noisy [11]
- **TCO crossover uncertainty**: Self-hosted break-even depends on utilization, which fluctuates unpredictably in production

### Benchmark Standings

| Benchmark | GPT-4o | Qwen2.5-72B | Mixtral 8x22B | Source |
|-----------|--------|-------------|---------------|--------|
| MMLU | 88.7 | 86.1 | 77.8 | [1][2][3] |
| HumanEval | 90.2 | 86.4 | 75.6 | [1][2] |
| Chatbot Arena ELO | 1287 | 1241 | 1148 | [11] |
| GSM8K | 95.3 | 93.8 | 88.2 | [1][2] |

## Executive Summary

GPT vs Qwen represents the fundamental deployment decision between proprietary API access (GPT-4/4o) and open-weight self-hosting (Qwen2.5 family) for production LLM workloads. The core trade-off: proprietary APIs offer zero infrastructure burden and frontier capability but impose vendor lock-in, rate limits, and per-token costs that scale linearly; open-weight models offer full control, customization, and TCO advantages at scale but demand GPU infrastructure, MoE routing expertise, and quantization engineering [1][2].

- **Choose GPT-4 API** when: rapid prototyping, low-volume (<1M tokens/day), need frontier reasoning, cannot staff ML infrastructure
- **Choose Qwen self-hosted** when: >50M tokens/day, data sovereignty required, need fine-tuning, cost optimization critical
- **Choose hybrid** when: variable workloads benefit from routing simple queries to self-hosted and complex queries to API

**The killer framing:** "This is not a model quality debate -- it is an infrastructure economics decision. At low volume, APIs win on TCO. Above the crossover point (~100M tokens/day), self-hosted open-weight models with quantization save 60-80% while matching 95% of API quality."

Cost headline: GPT-4o API at $5/$15 per 1M input/output tokens vs self-hosted Qwen2.5-72B-AWQ at ~$0.80 equivalent per 1M tokens on reserved A100s at 70%+ utilization.

```
TCO Decision Framework:
                          API (GPT-4o)      Self-Hosted (Qwen2.5-72B)
────────────────────────────────────────────────────────────────────
Volume < 10M tok/day      $50/day           $280/day (infra fixed)
Volume = 100M tok/day     $500/day          $280/day (break-even)
Volume = 1B tok/day       $5,000/day        $420/day (clear winner)
────────────────────────────────────────────────────────────────────
Setup cost                $0                ~$200K (eng + infra)
Customization             None              Full fine-tune + quant
Data privacy              Third-party       On-premise
Latency control           Limited           Full (P99 tunable)
```

## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Volume, latency SLA, data sensitivity, multilingual needs | API vs self-hosted threshold; determine if MoE routing complexity is justified for workload diversity |
| 2. Identify constraints | GPU budget, team ML-infra skill, regulatory (data residency) | Can you staff vLLM ops? Is 4-bit quantization acceptable for your quality bar? Rate limit tolerance? |
| 3. Propose baseline | Single model deployment with simplest serving path | GPT-4o API for <50M tokens/day; Qwen2.5-72B on vLLM with AWQ-4bit [6][15] for higher volume |
| 4. Identify gaps | Quality delta on domain tasks, latency variance, cost scaling | Measure: API quality vs quantized self-hosted on domain eval set; identify tasks where gap exceeds 5% |
| 5. Introduce improvements | Hybrid routing, MoE load balancing, long-context optimization | Route complex reasoning to API, bulk/simple to self-hosted; add RoPE scaling [9] for long context |
| 6. Add evaluation + guardrails | Decontaminated eval, Chatbot Arena correlation, cost monitoring | LLM-as-judge on 1K samples/week; cost-per-quality-point tracking; drift detection [11] |
| 7. Discuss scaling tradeoffs | Expert utilization, KV cache pressure, multi-region replication | 10x: quantization + batching. 100x: distributed MoE with expert-parallel sharding [4][13] |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Deployment model | API (GPT-4o) | Self-hosted (Qwen) | Volume <50M tok/day, no ML-infra team | Volume >100M tok/day, data sovereignty, need fine-tuning |
| Architecture | Dense model | MoE (sparse) | Predictable latency, simple ops | Diverse workloads, cost efficiency at scale [3][5] |
| Quantization | FP16 (full precision) | AWQ 4-bit [15] | Maximum quality, sufficient VRAM | Memory-constrained, <1% quality loss acceptable |
| Context extension | Native window only | RoPE/YaRN scaling [9][10] | Tasks fit in 8K tokens | Document analysis requiring 32K-128K context |
| Serving engine | Naive HF inference | vLLM PagedAttention [6] | Dev/research, low throughput | Production, >100 req/s, memory efficiency critical |

## System Design Walkthrough

### Opening Frame

The real engineering challenge is not picking GPT vs Qwen -- it is building infrastructure that can dynamically route between models based on cost, quality, and latency constraints while maintaining a unified evaluation framework across fundamentally different serving architectures (API vs self-hosted MoE).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Hybrid LLM Serving Platform                   │
├─────────────┬───────────────────┬───────────────────────────────┤
│ Request     │  Routing Layer    │  Model Fleet                   │
│ Classifier  │                   │                                │
│ ┌─────────┐ │  ┌─────────────┐  │  ┌──────────┐ ┌────────────┐ │
│ │Complexity│─┼─▶│Cost-Quality │──┼─▶│GPT-4o API│ │Qwen-72B    │ │
│ │Estimator │ │  │Router       │  │  │(complex) │ │vLLM+AWQ    │ │
│ └─────────┘ │  └─────────────┘  │  └──────────┘ │(bulk/simple)│ │
│             │         │         │               └────────────┘ │
├─────────────┴─────────┼─────────┴───────────────────────────────┤
│                       ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Unified Evaluation + Observability                      │    │
│  │  Latency | Quality Score | Cost/Token | Expert Utilization│    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

- **Request Classifier**: Estimates query complexity (token count, reasoning depth, language) in <5ms
- **Cost-Quality Router**: Routes to cheapest model meeting the quality SLA for this request class
- **GPT-4o API path**: Reserved for complex reasoning, multi-hop, frontier capability needs
- **Qwen-72B vLLM path**: Handles bulk traffic with PagedAttention [6] and AWQ quantization [15]
- **Unified Eval**: Compares outputs across backends on shared rubric; detects routing drift

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| API rate limits during traffic spikes | Request queue with priority + self-hosted overflow | Added latency for queued requests |
| MoE expert imbalance under real traffic | Auxiliary load-balancing loss + capacity constraints [4] | Slight quality reduction from forced routing |
| KV cache explosion at long context | YaRN position interpolation [10] + sliding window | Loses precise recall beyond window boundary |
| Quantization quality loss on rare tasks | Selective full-precision for flagged domains | 2x memory for precision-critical subset |
| Benchmark contamination in eval | Chatbot Arena ELO [11] + held-out private test sets | Slower feedback loop, smaller eval sets |

### Scaling Summary

- **10x (1B tokens/day)**: Add vLLM replicas with autoscaling on queue depth; quantization covers memory; API overflow still viable
- **100x (10B tokens/day)**: Expert-parallel MoE sharding across multi-node [13]; dedicated GPU clusters per region; API becomes emergency-only fallback
- **1000x (100B tokens/day)**: Custom inference kernels; speculative decoding; model distillation from 72B to task-specific 7B models; geo-distributed serving with local caches

## Interview Q&A Bank

### Q1: What are the fundamental architectural differences between GPT-4 and Qwen2.5 models?

> **Quick answer:** GPT-4 is a proprietary dense (or undisclosed-sparse) transformer accessed only via API [1]; Qwen2.5 is an open-weight family offering both dense and MoE variants with full weight access for quantization and fine-tuning [2].

GPT-4 provides no architectural transparency -- its parameter count, layer structure, and potential MoE design are undisclosed [1]. Qwen2.5-72B publishes full architecture details: 72B dense parameters, GQA attention, SwiGLU activation, 128K context via YaRN-extended RoPE [2][9][10]. The practical difference for engineers: GPT-4 is a black-box API with guaranteed SLAs but no customization, while Qwen offers full model surgery -- quantization to 4-bit [15], LoRA fine-tuning, custom KV cache strategies, and deployment on your own infrastructure via vLLM [6].

The MoE variant (Qwen2.5-MoE) uses top-2 routing across multiple experts, activating ~14B parameters per token from a larger total pool [2]. This provides GPT-4-class quality on many benchmarks at a fraction of the inference cost, but introduces routing instability and expert collapse risks in production [4][5].

**Hard follow-up:** If Qwen2.5-72B matches GPT-4 on MMLU, why would anyone still use the API?

> Benchmark parity does not imply production parity. GPT-4 excels on complex multi-step reasoning, instruction following edge cases, and safety alignment that MMLU does not capture [11]. Additionally, the API eliminates infrastructure burden -- no GPU procurement, no ops on-call, no quantization debugging. For teams without ML infrastructure expertise, the 5-10% quality premium and zero-ops overhead justify the per-token premium below the TCO crossover point.

### Q2: How does Mixture of Experts routing work, and why is it relevant to this comparison?

> **Quick answer:** MoE routes each token to a subset (typically 2) of N expert FFN layers via a learned gating function, activating only ~25% of total parameters per forward pass while maintaining quality of a much larger dense model [5][3].

The gating function computes router logits g(x) = W_g * x for each token, then selects the top-k experts via softmax [5]. The token is processed by only the selected experts, and outputs are combined weighted by the gate probabilities. This provides sub-linear compute scaling: Mixtral 8x7B has 46B total parameters but only activates 12B per token, achieving inference costs comparable to a 12B dense model with quality closer to a 46B dense model [3].

For the GPT vs Qwen comparison, MoE is the mechanism that allows open-weight models to compete on quality while maintaining cost advantages. Qwen2.5-MoE and DeepSeek-V2 [13] leverage this to deliver frontier-adjacent quality at 3-5x lower inference cost than equivalent dense models.

| Aspect | Dense (GPT-4) | MoE (Qwen/Mixtral) |
|--------|--------------|---------------------|
| Params activated/token | 100% | 20-30% [3][5] |
| Inference FLOPS | Linear in total params | Linear in active params |
| Memory footprint | Full model loaded | Full model loaded (same) |
| Routing overhead | None | 5-15ms per batch [4] |
| Expert collapse risk | N/A | Significant [4][5] |

**Hard follow-up:** Why does MoE require the full model in memory if only a fraction of parameters activate?

> Because routing is input-dependent -- you cannot predict which experts a future token will need. All expert weights must be resident in memory (or accessible via fast interconnect). This is why quantization [7][15] is critical for MoE: reducing 46B params from FP16 (92GB) to AWQ-4bit (23GB) makes single-GPU deployment feasible without sacrificing the sparse activation benefit.

### Q3: What is PagedAttention and why is it essential for self-hosted LLM serving?

> **Quick answer:** PagedAttention [6] manages KV cache memory like virtual memory pages -- allocating non-contiguous blocks on demand -- eliminating 60-80% of memory waste from pre-allocated contiguous buffers in naive implementations.

Traditional LLM serving pre-allocates KV cache for maximum sequence length per request, wasting memory on shorter sequences. vLLM's PagedAttention [6] divides KV cache into fixed-size blocks (pages) allocated dynamically as tokens are generated. This enables: (1) near-zero internal fragmentation, (2) efficient memory sharing across parallel sequences (beam search, parallel sampling), and (3) 2-4x higher throughput via better batching since freed memory serves more concurrent requests.

For the GPT vs Qwen decision, PagedAttention is what makes self-hosting economically viable. Without it, a 72B model on 8xA100 (640GB total) could serve ~8 concurrent requests at 8K context. With PagedAttention, the same hardware serves 50+ concurrent requests, dropping per-request cost by 6x and making self-hosted competitive with API pricing above the break-even volume [6].

**Hard follow-up:** How does PagedAttention interact with MoE serving?

> MoE adds complexity because different experts may have different KV cache access patterns. In practice, the KV cache is shared across experts (attention is not expert-specific -- only FFN layers are), so PagedAttention applies identically. The real MoE challenge is scheduling: expert computation creates uneven batch durations, and PagedAttention's preemption mechanism must account for tokens waiting on overloaded experts.

### Q4: Design a routing strategy for a hybrid GPT-API + self-hosted Qwen deployment.

> **Quick answer:** Route based on estimated task complexity and cost budget -- simple/bulk queries to self-hosted Qwen (80% of traffic), complex reasoning to GPT-4o API (20%), with quality monitoring to adjust routing thresholds dynamically.

The router operates in three stages. First, a lightweight classifier (~100M params, <5ms) estimates query complexity using features: token count, domain signal, presence of multi-step indicators, and user tier. Second, the cost-quality optimizer maps complexity to the cheapest model meeting the quality SLA for that request class. Third, a feedback loop compares routed responses against a held-out evaluation set weekly, adjusting classification thresholds when quality drift is detected.

Critical implementation details: (1) Cache routing decisions for repeated query patterns (40-60% cache hit rate). (2) Implement circuit breakers on the API path -- when GPT-4o rate limits hit, overflow to Qwen with a quality warning flag. (3) Track cost-per-quality-point as the primary optimization metric, not raw cost or raw quality independently.

> [!experience]
> The routing threshold should be calibrated on business impact, not benchmark scores -- a 5% quality difference on summarization may not matter, but 5% on code generation causes downstream failures.

**Hard follow-up:** What happens when the router misclassifies a complex query as simple?

> Implement async quality sampling: 5% of self-hosted responses are re-evaluated by GPT-4o as judge. When misrouting rate exceeds 3%, automatically tighten the complexity threshold. For critical paths, add a confidence gate -- if the self-hosted model's output perplexity exceeds a threshold, escalate to API before returning to the user.

### Q5: How do you quantize a 72B model for production serving without significant quality loss?

> **Quick answer:** Use activation-aware weight quantization (AWQ) [15] to compress to 4-bit with <1% quality loss by preserving salient weight channels that disproportionately affect output quality, then serve via vLLM [6] with group-wise quantization.

AWQ [15] observes that weight importance is not uniform -- a small fraction (1%) of weight channels carry disproportionate activation magnitude. Rather than quantizing all weights equally (as in naive RTN), AWQ scales salient channels before quantization, preserving their precision. This achieves 4-bit (INT4) compression with negligible perplexity increase on Qwen2.5-72B: MMLU drops <0.5 points vs FP16.

GPTQ [8] is an alternative that uses second-order information (Hessian) for per-column optimal quantization. It achieves slightly better perplexity than AWQ at 4-bit but requires a calibration dataset and is slower to quantize. For production, AWQ is preferred because: (1) faster quantization (minutes vs hours), (2) better integration with vLLM and TGI, (3) comparable quality at 4-bit group-128 [15].

| Method | Bits | MMLU (72B) | Quant Time | vLLM Support | Memory |
|--------|------|-----------|------------|--------------|--------|
| FP16 | 16 | 86.1 | N/A | Yes | 144GB |
| GPTQ [8] | 4 | 85.7 | ~4hr | Yes | 36GB |
| AWQ [15] | 4 | 85.6 | ~20min | Yes | 36GB |
| LLM.int8() [7] | 8 | 85.9 | Runtime | Limited | 72GB |

**Hard follow-up:** When does quantization fail badly?

> On tasks requiring precise numerical reasoning or rare-token generation. The 1% quality loss is averaged -- it concentrates on tail distributions. If your workload involves mathematical proof generation or low-resource language output, evaluate quantized quality specifically on those tasks before deploying.

### Q6: How would you extend a model's context window from 8K to 128K tokens?

> **Quick answer:** Apply RoPE frequency scaling [9] combined with YaRN (Yet Another RoPE Extension) [10] which interpolates rotary position embeddings with NTK-aware scaling, requiring minimal fine-tuning to extend context 16x while preserving short-context quality.

RoPE encodes position via rotation matrices at different frequencies [9]. Naive position interpolation (dividing position indices by the scaling factor) works but degrades quality on short contexts. YaRN [10] improves this with: (1) NTK-aware interpolation that scales different frequency dimensions differently -- high frequencies (local patterns) remain unchanged while low frequencies (global patterns) are interpolated. (2) A temperature scaling factor on attention logits to maintain entropy. (3) Only ~400 steps of fine-tuning needed on long documents.

For the GPT vs Qwen comparison, context extension is a major advantage of open-weight models -- you can apply YaRN to Qwen2.5-72B to reach 128K context, whereas GPT-4o's 128K window is fixed and untuneable. The trade-off: extended context increases KV cache memory linearly and attention compute quadratically. At 128K context with a 72B model, KV cache alone consumes ~32GB per request, limiting batch size to 1-2 on an A100-80GB [6].

**Hard follow-up:** Why not just use sliding window attention instead of RoPE scaling?

> Sliding window (used in Mistral/Mixtral [3]) limits attention to a fixed local window, losing global context beyond that window. RoPE scaling preserves full attention over all positions. The choice depends on task: sliding window works for streaming/chat where distant context is less relevant; RoPE scaling is necessary for document QA where answers depend on information anywhere in the input.

### Q7: How do you monitor MoE expert utilization in production and prevent collapse?

> **Quick answer:** Track per-expert token allocation fraction in real-time; alert when coefficient of variation exceeds 0.3; implement capacity-constrained routing with auxiliary load-balancing loss during any online fine-tuning [4][5].

Production monitoring requires three layers. First, per-request instrumentation: log which experts were activated for each token, compute per-batch expert load distribution. Second, time-series aggregation: track expert utilization fractions over 1-minute windows, compute CV (standard deviation / mean) of expert loads. Third, alerting: CV > 0.3 indicates emerging imbalance; CV > 0.5 indicates active collapse requiring intervention.

When collapse is detected at inference time (no retraining available), implement dynamic routing temperature adjustment -- increase gating temperature to spread load more uniformly. This trades routing optimality for stability. For systems with ongoing fine-tuning, the auxiliary loss L_aux = alpha * N * sum(f_i * P_i) [4] directly penalizes imbalanced routing during training.

> [!experience]
> Expert collapse manifests as latency spikes before quality degradation -- overloaded experts queue tokens while idle experts waste capacity. Monitor P99 latency per-expert, not just aggregate.

**Hard follow-up:** Can you rebalance experts without retraining the model?

> Yes, via inference-time interventions: (1) Add load-aware logit penalties to overloaded experts. (2) Implement expert capacity caps that force overflow tokens to secondary experts. (3) Use request-level routing diversity constraints. These are approximate -- they maintain throughput but may slightly degrade quality since tokens reach non-optimal experts.

### Q8: What are the failure modes of LLM benchmarks, and how do you evaluate models reliably?

> **Quick answer:** Static benchmarks suffer from contamination (training on test data) and saturation (ceiling effects); Chatbot Arena [11] provides decontaminated human preference signal but has high variance and style bias.

Contamination occurs when models are trained on benchmark questions -- open-weight models can be audited for this, but proprietary models cannot [11]. Saturation occurs when models approach 90%+ on benchmarks like MMLU, making discrimination impossible. Chatbot Arena [11] addresses both via live, blind pairwise comparisons generating ELO ratings, but introduces its own biases: verbosity preference, recency bias, and demographic skew in raters.

For production model selection, build a three-layer evaluation: (1) **Domain-specific held-out set** -- 1000+ examples from your actual workload that no model has seen. (2) **LLM-as-judge** -- use a stronger model (or ensemble) to rate outputs on your specific criteria. (3) **Business metric correlation** -- A/B test on real traffic measuring task completion, user satisfaction, or revenue impact. No single evaluation layer is sufficient.

**Hard follow-up:** How would you detect if a model has been contaminated on your evaluation set?

> Compare performance on your eval set vs a semantically equivalent paraphrase of the same questions. If the model scores significantly higher on verbatim questions than paraphrases, contamination is likely. Also track performance deltas across model versions -- suspicious jumps on specific question subsets suggest targeted optimization.

### Q9: Walk through the GPU memory planning for serving Qwen2.5-72B at production scale.

> **Quick answer:** At FP16 the model weights alone require 144GB; with AWQ-4bit [15] this drops to 36GB, leaving room on 2xA100-80GB (160GB total) for KV cache, activations, and vLLM overhead to serve ~32 concurrent requests at 4K context.

Memory breakdown for 2xA100-80GB serving Qwen2.5-72B-AWQ-4bit:
- Model weights (4-bit, group-128): 36GB
- vLLM runtime + CUDA overhead: ~8GB
- KV cache pool (remaining): ~116GB
- Per-request KV cache at 4K context: ~3.5GB (72 layers * 2 * hidden_dim * 4K * FP16)
- Maximum concurrent requests: 116 / 3.5 = ~32 requests

At 8K context, per-request KV doubles to ~7GB, halving concurrency to ~16. At 32K context, only ~4 concurrent requests fit. This is why context length management and PagedAttention [6] are critical -- without paging, pre-allocated buffers for max context waste memory on shorter requests.

For higher throughput, scale horizontally: 4 replicas of 2xA100 serve ~128 concurrent requests at 4K context, sufficient for ~500 requests/second with 250ms average generation time.

**Hard follow-up:** How does tensor parallelism vs pipeline parallelism affect this calculation?

> Tensor parallelism (TP=2 across the 2 GPUs) splits each layer's weights, halving per-GPU weight memory but requiring all-reduce communication per layer. Pipeline parallelism (PP=2) assigns different layers to different GPUs, halving per-GPU weight memory without per-layer communication but introducing pipeline bubbles. For inference, TP is preferred because it reduces per-token latency (both GPUs work on every token), while PP reduces throughput due to bubbles. vLLM uses TP by default for multi-GPU serving [6].

### Q10: How would you implement a cost-optimized self-hosted deployment that beats API pricing?

> **Quick answer:** The break-even requires >70% GPU utilization sustained; achieve this through request batching, autoscaling to zero during off-peak, spot/preemptible instances for batch workloads, and aggressive quantization [15] to maximize requests per GPU.

The TCO model has four components: (1) **GPU compute**: Reserved A100-80GB at ~$1.50/GPU-hr or 3-year reserved at ~$0.80/GPU-hr. (2) **Engineering**: 1-2 ML engineers for serving infrastructure (~$400K/year loaded). (3) **Overhead**: Networking, storage, monitoring ~20% of compute. (4) **Opportunity cost**: 2-3 month build time before first savings.

Break-even analysis vs GPT-4o ($5/1M input tokens): A 2xA100 node serving Qwen2.5-72B-AWQ processes ~2M tokens/hour at full utilization. At $3/hr node cost, that is $1.50/1M tokens -- already 3.3x cheaper than GPT-4o input pricing. At 70% utilization (realistic), effective cost is $2.14/1M tokens -- still 2.3x cheaper. Adding engineering amortized over 3 years: break-even at ~50M tokens/day.

**Hard follow-up:** What kills the TCO advantage in practice?

> Low utilization. If your traffic is spiky (10x peak-to-trough), average GPU utilization may be 20-30%, destroying economics. Solutions: multi-tenant serving (share GPUs across teams), autoscaling with cold-start optimization, or hybrid approach where baseline load runs self-hosted and spikes overflow to API.

### Q11: Compare vLLM and TGI (Text Generation Inference) for production LLM serving.

> **Quick answer:** vLLM excels at throughput via PagedAttention [6] and continuous batching; TGI (Hugging Face) offers simpler deployment with built-in safeguards and production features but lower peak throughput.

| Feature | vLLM [6] | TGI |
|---------|----------|-----|
| KV cache management | PagedAttention (optimal) | Pre-allocated blocks |
| Throughput (72B, 2xA100) | ~2000 tok/s | ~1400 tok/s |
| Continuous batching | Yes | Yes |
| Quantization support | AWQ, GPTQ, SqueezeLLM | GPTQ, AWQ, EETQ |
| Multi-model serving | Yes (recent) | Yes |
| Production readiness | Requires ops wrapper | Built-in metrics/health |
| Speculative decoding | Yes | Yes |
| Tensor parallelism | Seamless | Seamless |

Choose vLLM when maximizing throughput-per-dollar is the primary goal and you have ops capability to build production wrappers (health checks, graceful shutdown, request routing). Choose TGI when you need faster time-to-production with built-in Docker deployment, Prometheus metrics, and token streaming out of the box.

**Hard follow-up:** When would you use neither and build custom inference?

> When you need kernel-level optimizations for a specific model architecture -- for example, DeepSeek-V2's multi-head latent attention [13] required custom CUDA kernels for the latent projection that neither vLLM nor TGI initially supported. Also when serving MoE models with expert-parallel sharding across nodes, which requires custom scheduling logic beyond what general frameworks provide.

### Q12: How do you design a fair evaluation comparing a proprietary API model against a self-hosted open-weight model?

> **Quick answer:** Control for serving conditions (match temperature, max_tokens, system prompt), evaluate on held-out domain-specific data (not public benchmarks), and measure at three levels: automated metrics, LLM-as-judge, and business KPI correlation.

Fairness requires eliminating confounds. Use identical prompts (no model-specific formatting). Match generation parameters exactly (temperature=0.7, top_p=0.95). Disable safety filters on both sides for capability comparison (re-enable for deployment). Run sufficient samples for statistical power (>500 per category with 95% CI).

The evaluation hierarchy: (1) **Automated metrics** (BLEU, ROUGE, exact match): cheap but poorly correlated with quality. (2) **LLM-as-judge** [11]: use a third model to rate both outputs blind; correlates ~0.8 with human preference. (3) **Human A/B preference**: gold standard but expensive ($5-10 per comparison). (4) **Business metrics**: deploy both via A/B test in production, measure task completion rate and user retention.

Critical pitfall: Chatbot Arena ELO [11] conflates model quality with alignment style -- verbose, confident responses score higher regardless of accuracy. Your domain evaluation must penalize this if conciseness matters.

**Hard follow-up:** How do you handle the latency confound in live A/B testing?

> Users prefer faster responses independent of quality. To isolate quality from latency: (1) Buffer both responses and present simultaneously, or (2) Add artificial delay to match the slower model's latency, or (3) Measure only on evaluations where response time was within 20% between variants. Never compare raw user preference without controlling for speed.

## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): MoE Routing -- Load Balancing, Expert Collapse, and Auxiliary Loss Design</strong></summary>

Expert collapse occurs when the router's softmax gating function G(x) = softmax(W_g * x) converges to selecting the same k experts for all inputs, creating a degenerate sparse model [5][4]. The mathematical root cause is a positive feedback loop in gradient dynamics.

**Formal analysis.** Given router probability P(e_i | x) = exp(g_i(x)) / sum_j exp(g_j(x)), expert i receives gradient signal proportional to its selection frequency f_i. If expert i outperforms early in training:

```
f_i increases → more gradient signal to expert i → expert i improves →
P(e_i | x) increases → f_i increases further (runaway)
```

This is equivalent to the rich-get-richer dynamics of Polya urns. Without intervention, routing entropy H = -sum(f_i * log(f_i)) collapses from log(N) (uniform) toward 0 (degenerate).

**Switch Transformer auxiliary loss [4]:**
```
L_aux = alpha * N * sum_{i=1}^{N} f_i * P_i

where:
  f_i = (1/T) * sum_{t=1}^{T} 1[argmax(G(x_t)) == i]   (token fraction)
  P_i = (1/T) * sum_{t=1}^{T} P(e_i | x_t)              (probability mass)
  N = number of experts
  alpha = hyperparameter (typically 0.01-0.1)
```

The product f_i * P_i is minimized when routing is uniform (both equal 1/N), yielding L_aux = alpha. Any deviation increases the loss quadratically.

**Why this is insufficient for production.** The auxiliary loss operates at batch level during training. In production inference:
1. No training signal exists to correct drift
2. Real traffic has temporal correlation (morning = code, afternoon = chat) that creates systematic imbalance
3. Batch-level statistics are meaningless for single-request streaming

**Production-grade solution -- capacity-constrained routing with EMA tracking:**
```python
def production_moe_route(x, gate_weights, expert_load_ema, capacity_factor=1.25):
    logits = x @ gate_weights  # [batch, num_experts]
    # Penalize overloaded experts using EMA of recent load
    load_penalty = torch.clamp(expert_load_ema - 1.0/num_experts, min=0) * penalty_scale
    adjusted_logits = logits - load_penalty
    # Top-2 selection with capacity constraint
    top2 = torch.topk(adjusted_logits, k=2, dim=-1)
    # Hard capacity: max tokens per expert = batch_size * capacity_factor / N
    capacity = int(x.size(0) * capacity_factor / num_experts)
    # Overflow tokens route to next-best expert
    expert_counts = torch.zeros(num_experts)
    for token_idx in range(x.size(0)):
        primary = top2.indices[token_idx, 0]
        if expert_counts[primary] < capacity:
            expert_counts[primary] += 1
            # route to primary
        else:
            secondary = top2.indices[token_idx, 1]
            expert_counts[secondary] += 1
            # route to secondary (quality trade-off)
    # Update EMA
    expert_load_ema = 0.99 * expert_load_ema + 0.01 * (expert_counts / x.size(0))
    return routing_decisions, expert_load_ema
```

**Key design choice:** The capacity_factor > 1.0 allows some imbalance (specialization) while preventing catastrophic collapse. DeepSeek-V2 [13] uses capacity_factor=1.5 with 160 experts, finding this balances specialization and utilization. The EMA decay rate (0.99) must match traffic autocorrelation -- faster decay for variable traffic, slower for stable.

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): Self-Hosting Open-Weight Models -- vLLM, TGI, Quantization, GPU Memory Planning</strong></summary>

Self-hosting a 72B MoE model requires solving three simultaneous constraints: memory capacity (weights + KV cache + activations must fit), compute throughput (tokens/second must meet SLA), and cost efficiency (utilization must exceed break-even threshold) [6][7][15].

**Memory budget derivation for Qwen2.5-72B on 2xA100-80GB with TP=2:**

```
Total available: 2 * 80GB = 160GB
CUDA/driver overhead: ~4GB per GPU = 8GB
vLLM runtime buffers: ~4GB

Model weights (FP16): 72B * 2 bytes = 144GB  --> DOES NOT FIT
Model weights (AWQ-4bit, group-128): 72B * 0.5 bytes + scales = ~38GB  --> FITS

Remaining for KV cache: 160 - 8 - 4 - 38 = 110GB

KV cache per token per layer (GQA with 8 KV heads, dim=128):
  = 2 (K+V) * 8 heads * 128 dim * 2 bytes (FP16) = 4096 bytes = 4KB

KV cache per token (80 layers): 80 * 4KB = 320KB
KV cache per request at 4K context: 4096 * 320KB = 1.28GB
KV cache per request at 32K context: 32768 * 320KB = 10.24GB

Max concurrent requests:
  At 4K context: 110GB / 1.28GB = ~85 requests
  At 32K context: 110GB / 10.24GB = ~10 requests
```

**PagedAttention impact [6]:** Without paging, memory is pre-allocated for max_seq_len per request. If max=32K but average=2K, utilization is 2K/32K = 6.25%. PagedAttention allocates blocks on-demand, achieving ~95% KV cache utilization. For the 4K average case on 32K-capable model:

```
Effective concurrency without paging: 110GB / 10.24GB = 10 requests
Effective concurrency with paging:    110GB / 1.28GB  = 85 requests (8.5x improvement)
```

**Quantization selection framework:**

| Scenario | Method | Rationale |
|----------|--------|-----------|
| Latency-critical, single GPU | AWQ-4bit [15] | Fastest quantization, excellent vLLM integration, <1% quality loss |
| Quality-sensitive, 2+ GPUs available | GPTQ-4bit [8] | Slightly better perplexity via Hessian-based optimization |
| Memory-unconstrained (8xA100) | LLM.int8() [7] | 8-bit with outlier handling; zero calibration needed |
| Edge deployment (single GPU, 24GB) | AWQ-3bit | Aggressive compression; 2-3% quality loss acceptable |

**Production serving topology for 500 req/s at 4K context:**

```
Load Balancer (round-robin with health checks)
├── vLLM Instance 1: 2xA100-80GB, TP=2, Qwen-72B-AWQ4
├── vLLM Instance 2: 2xA100-80GB, TP=2, Qwen-72B-AWQ4
├── vLLM Instance 3: 2xA100-80GB, TP=2, Qwen-72B-AWQ4
├── vLLM Instance 4: 2xA100-80GB, TP=2, Qwen-72B-AWQ4
├── vLLM Instance 5: 2xA100-80GB, TP=2, Qwen-72B-AWQ4
└── vLLM Instance 6: 2xA100-80GB, TP=2, Qwen-72B-AWQ4

Per-instance: ~85 concurrent requests, ~140 req/s (600ms avg generation)
Total: 6 * 140 = 840 req/s capacity (67% target utilization for headroom)
Cost: 12 A100s * $1.50/hr = $18/hr = $13K/month
```

The critical operations decision: autoscale based on KV cache utilization percentage (not CPU/GPU compute utilization), because memory exhaustion causes OOM crashes while compute saturation just increases latency gracefully.

</details>

<details><summary><strong>DE Probe 3 (DATA): Training Data Composition -- Multilingual Balance, Code Mix, and Synthetic Data Quality</strong></summary>

Training data composition determines model capabilities more than architecture choices. The GPT vs Qwen divergence is fundamentally a data strategy divergence: GPT-4 optimizes for English-first general capability [1], while Qwen explicitly balances multilingual (Chinese/English/code) representation with publicly documented composition ratios [2].

**Qwen's disclosed data strategy [2]:**
- Total pre-training corpus: ~3T tokens
- Language balance: ~55% English, ~25% Chinese, ~10% code, ~10% other languages
- Quality filtering: classifier-trained on high-quality web pages (similar to GPT-3's approach but with Chinese-specific heuristics)
- Code mix: GitHub-sourced with license filtering, covering 30+ programming languages
- Deduplication: MinHash + exact substring matching, removing ~30% of raw crawl

**The multilingual trade-off.** Training on balanced multilingual data has a tax: performance on English benchmarks decreases ~2-3% compared to English-only training at the same compute budget (the "curse of multilinguality"). However, this enables: (1) zero-shot cross-lingual transfer, (2) code-switching capability, and (3) access to Chinese-language knowledge absent from English corpora.

**Synthetic data quality and the data flywheel:**

Modern training pipelines use synthetic data generated by stronger models to bootstrap weaker ones. The quality hierarchy:

```
Data Quality Pyramid:
┌─────────────────────┐
│ Human expert (gold) │  <1% of corpus, $50-500/example
├─────────────────────┤
│ Model-generated +   │  5-10% of corpus, $0.01/example
│ human-verified      │  Quality: 90% of human
├─────────────────────┤
│ Model-generated     │  20-30% of corpus, $0.001/example
│ filtered by reward  │  Quality: 80% of human
├─────────────────────┤
│ Web crawl filtered  │  60-70% of corpus, $0.0001/example
│ by quality model    │  Quality: variable
└─────────────────────┘
```

**Critical failure mode: model collapse from synthetic data loops.** If model M generates training data for model M+1, and M+1 generates data for M+2, quality degrades exponentially [12]. Prevention requires: (1) Always mixing real human data (>20% of each training batch). (2) Diversity metrics on synthetic outputs (reject samples with low embedding diversity). (3) Regular evaluation on held-out human-written data.

**Code data's outsized impact.** Llama 2 [12] and Qwen [2] both report that including code in pre-training improves reasoning capability on non-code tasks by 5-10% on benchmarks like GSM8K. The hypothesis: code requires precise logical reasoning, variable tracking, and compositional planning that transfers to natural language reasoning. The optimal code fraction appears to be 8-15% of total tokens -- below this, reasoning gains are minimal; above this, language fluency degrades.

**Implications for model selection:** When choosing between GPT-4 and Qwen2.5 for a specific task, the training data composition predicts capability gaps better than aggregate benchmarks. For Chinese e-commerce, Qwen's 25% Chinese pre-training gives it structural advantages no amount of English-trained capability can overcome. For English legal reasoning, GPT-4's presumed English-heavy training provides depth that Qwen's balanced approach trades away.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Benchmark Reliability -- Contamination, Saturation, and Chatbot Arena ELO Methodology</strong></summary>

Static benchmarks are fundamentally broken for frontier model comparison. Two failure modes dominate: contamination (training on test data) and saturation (models cluster near ceiling, making discrimination impossible) [11].

**Contamination detection and impact.** When MMLU questions appear in pre-training data, models memorize answers without genuine reasoning. Detection methods:

```
Contamination Test Protocol:
1. Canary insertion: Embed unique strings in eval set; search model outputs
2. Paraphrase gap: Compare score on verbatim questions vs semantic paraphrases
   Contamination signal: score_verbatim - score_paraphrase > 5%
3. Partial exposure: Present only first half of question; contaminated models
   generate the exact second half
4. N-gram overlap: Compute 8-gram overlap between eval set and known training corpora
```

Open-weight models (Qwen [2], Llama [12]) can be audited -- their training data pipelines are partially disclosed. Proprietary models (GPT-4 [1]) cannot be audited, creating an asymmetric evaluation problem.

**Saturation analysis on MMLU (2024):**
- GPT-4o: 88.7%, Qwen2.5-72B: 86.1%, Claude 3.5: 88.3%
- Discrimination at this range is dominated by noise (question ambiguity, prompt sensitivity)
- A 2% difference may reflect 1-2 lucky/unlucky questions per category, not genuine capability gap

**Chatbot Arena ELO methodology [11]:**

The Arena uses Bradley-Terry pairwise preference modeling:
```
P(model_A beats model_B) = 1 / (1 + 10^((R_B - R_A) / 400))

where R_A, R_B are ELO ratings updated per battle:
  R_A_new = R_A + K * (outcome - expected)
  K = 32 (standard), adjusted for confidence
```

Strengths: (1) Decontaminated by design (live user queries). (2) Captures holistic quality including style. (3) Continuous updating reflects model improvements.

Weaknesses: (1) **Verbosity bias** -- longer responses win 60% of ties, inflating scores of verbose models. (2) **Demographic skew** -- raters are disproportionately tech-savvy English speakers. (3) **Position bias** -- model presented first wins 55% of ties (partially mitigated by randomization). (4) **Style conflation** -- cannot separate factual accuracy from presentation quality.

**Practical evaluation framework for production model selection:**

| Layer | Method | Cost | Signal Quality | Latency |
|-------|--------|------|----------------|---------|
| Automated (base) | Held-out domain test set | $0.01/eval | Medium (correlation ~0.6 with human) | Minutes |
| LLM-as-judge | GPT-4 rates both outputs | $0.10/eval | High (correlation ~0.8) [11] | Hours |
| Human preference | Paid annotators, blind A/B | $5-10/eval | Very high | Days |
| Business metric | A/B test in production | $0 (incremental) | Ground truth | Weeks |

The key insight: no single evaluation method is sufficient. Automated metrics miss style and safety. LLM-as-judge inherits the judge model's biases. Human eval is expensive and slow. Business metrics are noisy and delayed. Production systems need all four layers with appropriate cadence.

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Cost Modeling -- API Pricing vs Self-Hosted TCO Breakeven Analysis</strong></summary>

The API vs self-hosted decision is a financial engineering problem with four variables: volume (tokens/day), utilization (% of provisioned capacity actually used), engineering cost (team to maintain infrastructure), and quality-adjusted cost (accounting for any quality delta between options).

**Full TCO model for self-hosted Qwen2.5-72B-AWQ vs GPT-4o API:**

```
API Cost (GPT-4o):
  Input:  $5.00 / 1M tokens
  Output: $15.00 / 1M tokens
  Assuming 1:1 input:output ratio, blended: $10.00 / 1M tokens
  At 100M tokens/day: $1,000/day = $30,000/month

Self-Hosted Cost (Qwen2.5-72B-AWQ on 2xA100-80GB nodes):
  Throughput per node: ~2M tokens/hr at 70% utilization
  Tokens/day per node: 2M * 24hr * 0.7 = 33.6M tokens/day
  Nodes needed for 100M tokens/day: ceil(100/33.6) = 3 nodes
  
  Hardware cost (AWS p4d.24xlarge, reserved 1-year):
    3 nodes * $12,000/month = $36,000/month
  
  Wait -- this is MORE expensive than API?
  
  Correction: p4d.24xlarge has 8xA100, not 2.
  With 8xA100, TP=2 gives 4 independent serving instances per node.
  Throughput per node: 4 * 2M = 8M tokens/hr = 134M tokens/day (at 70%)
  Nodes needed: 1 node handles 100M tokens/day
  
  Cost: 1 node * $12,000/month = $12,000/month (hardware)
  Engineering: 0.5 FTE * $200K/year / 12 = $8,300/month
  Monitoring/infra: $2,000/month
  Total: $22,300/month vs $30,000/month API
  Savings: 26%
```

**The utilization trap.** The calculation above assumes 70% steady-state utilization. Real traffic patterns:

```
Daily Traffic Pattern (typical B2B SaaS):
                    ┌──────┐
                    │      │
               ┌────┤      ├────┐
               │    │      │    │
          ┌────┤    │      │    ├────┐
     ─────┘    │    │ PEAK │    │    └─────
     2am       9am  12pm   3pm  6pm     11pm
     
Peak utilization: 95%
Average utilization: 35%
Effective cost at 35% util: $22,300/month at 35% util = $63,700 effective
vs API at $30,000/month (scales linearly with actual usage)
```

**Break-even formula:**
```
Break-even volume = Fixed_Cost_Monthly / (API_CPT - Self_Hosted_CPT_at_target_util)

where:
  Fixed_Cost_Monthly = Hardware + Engineering + Overhead
  API_CPT = API cost per token (blended)
  Self_Hosted_CPT = Hardware_Cost / (Throughput_Capacity * Utilization)
  
For our example at 70% utilization:
  Self_Hosted_CPT = $12,000 / (134M * 30 days) = $0.003 / 1M tokens
  Break-even = ($22,300 - $12,000) / ($10.00 - $0.003) per 1M tokens
            = $10,300 / $9.997 per 1M tokens
            = 1.03M tokens/day minimum (trivially met at 100M/day)
```

**The real break-even consideration** is not volume but utilization. If you cannot maintain >50% GPU utilization, the API wins. Strategies to maintain utilization: (1) Multi-tenant serving across teams. (2) Batch workloads scheduled during off-peak. (3) Spot instances for overflow with checkpoint-resume. (4) Autoscaling to zero during dead hours with 30-second cold start budget.

**Quality-adjusted TCO.** If Qwen2.5-72B-AWQ4 scores 95% of GPT-4o quality on your domain tasks, the quality-adjusted API cost is:
```
Quality-adjusted API cost = $30,000 / 0.95 * 1.0 = $31,579/month
(paying premium for 5% quality gap you don't capture with self-hosted)
```

If that 5% quality gap translates to measurable business impact (e.g., 2% lower conversion rate), factor in revenue loss to determine true break-even.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Long-Context Architectures -- RoPE Scaling, YaRN, and Sliding Window Attention</strong></summary>

Extending context windows beyond training length requires modifying positional encoding without destroying learned short-range patterns. Three architectures dominate: RoPE interpolation [9], YaRN (NTK-aware) [10], and sliding window attention [3].

**RoPE fundamentals [9].** Rotary Position Embedding encodes position m via rotation:
```
f(x_m, m) = R(m) * x_m

where R(m) is a block-diagonal rotation matrix:
R(m) = diag(R_1(m), R_2(m), ..., R_{d/2}(m))
R_k(m) = [[cos(m*theta_k), -sin(m*theta_k)],
           [sin(m*theta_k),  cos(m*theta_k)]]

theta_k = 10000^(-2k/d)   (frequency for dimension k)
```

This creates a spectrum of frequencies: low-k dimensions rotate slowly (capture global position), high-k dimensions rotate fast (capture local position).

**Naive linear interpolation.** To extend from trained length L to target L' = s*L, divide all positions by s:
```
m' = m / s  (position interpolation)
```

Problem: this compresses ALL frequencies by factor s, including high-frequency local patterns that are already well-learned. Result: short-context quality degrades 2-5% [10].

**YaRN NTK-aware interpolation [10].** Key insight: interpolate only the frequencies that would exceed the Nyquist limit at extended lengths, leaving well-behaved frequencies unchanged.

```
Partition dimensions into:
- High-frequency (local): theta_k > 1/L     --> NO interpolation
- Mid-frequency:          1/L' < theta_k < 1/L --> partial interpolation  
- Low-frequency (global): theta_k < 1/L'    --> full interpolation

Scaling rule:
theta_k' = theta_k * interpolation_factor(k)

where interpolation_factor(k) = 
  1.0                          if theta_k > 1/L    (high freq, unchanged)
  (1-alpha)*1 + alpha*(1/s)    if 1/L' < theta_k < 1/L  (linear blend)
  1/s                          if theta_k < 1/L'   (low freq, fully interpolated)

alpha = smooth interpolation based on frequency position
```

Additionally, YaRN applies attention scaling:
```
attention_scale = 0.1 * ln(s) + 1.0
```

This compensates for entropy increase at longer sequences (attention becomes more diffuse over more positions).

**YaRN fine-tuning requirement:** Only 400-1000 steps on long documents to adapt. This is dramatically cheaper than continued pre-training:
```
Cost comparison for 72B model, 8K→128K extension:
- Continued pre-training: ~$500K compute (trillions of tokens at 128K)
- YaRN fine-tune: ~$2K compute (1000 steps, batch=4, 128K sequences)
- Quality: YaRN achieves 95% of continued pre-training quality at 0.4% of cost
```

**Sliding window attention [3] (Mistral/Mixtral approach).** Each layer attends only to the W most recent tokens:
```
Attention mask for layer l, position m:
  A[m, n] = 1 if (m - W) < n <= m
           = 0 otherwise

With L layers and window W:
  Effective receptive field = L * W
  Mixtral: W=4096, L=32 → receptive field = 131,072 tokens
```

Memory advantage: KV cache is fixed at W tokens per layer regardless of sequence length. At W=4096 for 72B model: 4096 * 320KB = 1.28GB per request (constant, not growing with context).

**Trade-off comparison:**

| Property | RoPE/YaRN [9][10] | Sliding Window [3] |
|----------|-------------------|-------------------|
| Attention range | Full (all-to-all) | Local (W tokens) |
| Memory scaling | O(n) in context length | O(W) constant |
| Long-range retrieval | Exact (attends to all) | Approximate (via stacking) |
| Fine-tuning cost | 400-1000 steps | Zero (architectural) |
| Max practical context | 128K-1M tokens | Unlimited (memory-bounded only by W) |
| Needle-in-haystack perf | High (direct attention) | Degrades beyond L*W |
| Best for | Document QA, RAG, analysis | Chat, streaming, real-time |

**Production decision framework:** Use YaRN-extended RoPE when tasks require precise retrieval from arbitrary positions in long documents (legal search, codebase analysis). Use sliding window when tasks are streaming/conversational and distant context can be summarized rather than directly attended to. Many production systems combine both: sliding window for the majority of layers with a few global-attention layers interspersed (as in Longformer-style architectures).

</details>

## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Task Usage | Cost |
|-----------|-----------|----------------|------|
| GPT-4o API (blended) | $10/1M tokens | 2K tokens avg | $0.020 |
| Qwen2.5-72B-AWQ self-hosted | $0.80/1M tokens | 2K tokens avg | $0.0016 |
| vLLM inference (A100 node) | $12K/month | Amortized per request | $0.003 |
| Quantization (AWQ one-time) | $50 compute | Per model version | Negligible |
| Context extension (>8K) | 4x base cost | 15% of requests | +$0.006 |
| MoE routing overhead | +10% compute | MoE models only | +$0.0002 |
| Evaluation (LLM-as-judge) | $0.10/eval | 5% of requests sampled | +$0.005 |

### Monthly Cost at Scale

| Scale | GPT-4o API | Self-Hosted Qwen (AWQ) | Infrastructure | Break-Even? |
|-------|-----------|------------------------|----------------|-------------|
| 10M tok/day | $3,000 | $12,800 (underutilized) | $800 | API wins |
| 50M tok/day | $15,000 | $13,200 (50% util) | $800 | Near break-even |
| 100M tok/day | $30,000 | $13,600 (70% util) | $800 | Self-hosted wins |
| 1B tok/day | $300,000 | $18,000 (3 nodes, 85%) | $2,400 | Self-hosted 14x cheaper |

### Cost Optimization Priority Stack

1. **Quantization (AWQ-4bit)** — 75% memory reduction, <1% quality loss, enables 4x batch concurrency [15]
2. **Request routing** — Send 80% of simple queries to self-hosted, 20% complex to API — 60% total cost reduction
3. **Dynamic batching + PagedAttention** — 3-8x throughput improvement per GPU via vLLM [6]
4. **Autoscaling to demand** — Match GPU count to traffic pattern, save 30-50% vs fixed provisioning
5. **KV cache optimization** — Prefix caching for repeated system prompts, 20-30% token savings
6. **Spot instances for batch** — 60-70% discount for async/batch workloads with checkpoint-resume

### Build vs Buy

| Capability | Build Cost | Buy Option | Recommendation |
|------------|-----------|------------|----------------|
| LLM inference serving | $200K + 2 months | GPT-4o API, $10/1M tok | Buy until >100M tok/day |
| Fine-tuning pipeline | $150K + 3 months | OpenAI fine-tune API | Build if domain-specific |
| Long-context (128K) | $50K (YaRN fine-tune) | GPT-4o native 128K | Build for open-weight, buy for API |
| Evaluation framework | $100K + 2 months | Scale AI, $5/eval | Build (strategic differentiator) |
| MoE serving (expert-parallel) | $300K + 4 months | Fireworks.ai, Together.ai | Buy until 500M tok/day |

## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| P95 latency (self-hosted) | >2000ms for 3min | Auto-scale + page SRE |
| P95 latency (API) | >5000ms for 1min | Switch to self-hosted overflow |
| Error rate | >1% for 2min | Circuit breaker + Slack alert |
| GPU memory utilization | >92% for 2min | Reject new requests, scale out |
| MoE expert CV (coefficient of variation) | >0.3 sustained 5min | Routing temp increase |
| Quality score (LLM-judge sample) | <85% for 1hr | Route more traffic to API |
| Cost per 1M tokens | >120% budget | Rate limit + investigation |
| KV cache utilization | >95% | Evict oldest sequences, scale |
| Quantization outlier rate | >2% | Flag domain for FP16 routing |

### Debugging Walkthrough

```
SYMPTOM: Latency spike on self-hosted Qwen
│
├─ CHECK: GPU memory (nvidia-smi)
│  ├─ OOM pressure? → KV cache exhaustion → reduce max_seq_len or scale
│  └─ Normal? → continue
│
├─ CHECK: Batch queue depth (vLLM metrics)
│  ├─ Queue growing? → Throughput bottleneck → add replicas
│  └─ Queue stable? → continue
│
├─ CHECK: Request characteristics
│  ├─ Avg sequence length spike? → Long context surge → enable context routing
│  └─ Normal lengths? → continue
│
└─ CHECK: Expert load (MoE models)
   ├─ CV > 0.5? → Expert collapse → increase routing temperature
   └─ Balanced? → Check network/storage IO

SYMPTOM: Quality degradation detected by judge
│
├─ CHECK: Model version change? → Rollback
├─ CHECK: Input distribution shift? → Retune routing thresholds
├─ CHECK: Quantization mismatch? → Evaluate on failing examples at FP16
└─ CHECK: Prompt template change? → Revert template, A/B test
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|-----------------|-------------------|--------------|
| Model weights (quantized) | Blue-green with SHA256 verification | Full serving fleet |
| vLLM config (batch size, cache) | Instant config reload | Per-instance |
| Routing thresholds | Feature flag toggle (<1s) | Per-request-class |
| Quantization calibration | Rebuild from checkpoint (~20min) | All quantized instances |
| YaRN fine-tune weights | Swap model revision in config | Long-context requests only |
| Prompt templates | Git-based instant revert | Per-template scope |

## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| User preference (A/B winner) | Very high -- direct quality signal | Blind comparison in product |
| Task completion rate | High -- outcome-based | Event tracking pipeline |
| Routing accuracy (was model choice optimal?) | High -- cost optimization | Judge re-evaluation of 5% sample |
| Latency satisfaction (abandonment rate) | Medium -- proxy for UX | Client timeout tracking |
| Expert utilization patterns | Medium -- operational health | vLLM instrumentation |
| Cost-per-quality-point trend | High -- efficiency signal | Daily aggregation |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|----------------|---------------|
| Real-time | Routing thresholds, circuit breakers | Automated anomaly detection |
| Daily | KV cache config, batch sizes | Latency/throughput regression test |
| Weekly | LLM-as-judge evaluation refresh | Statistical significance on 500+ samples |
| Monthly | Quantization recalibration, YaRN tune | Full eval suite pass, <1% quality regression |
| Quarterly | Base model upgrade (new Qwen release) | 2-week shadow deployment, business metric validation |

## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Hybrid API + Self-hosted routing | Cost vs quality optimization | Variable complexity workloads | Uniform simple queries (self-host all) |
| AWQ-4bit with group quantization [15] | Memory reduction for large models | Any self-hosted model >13B | When <1% quality loss is unacceptable |
| PagedAttention (vLLM) [6] | KV cache memory waste | All production self-hosted serving | Single-request dev/debug scenarios |
| YaRN context extension [10] | Extending context beyond training | Document QA, code analysis | Chat/streaming (use sliding window) |
| Expert-parallel MoE serving [13] | Scaling MoE beyond single node | >100B total param models | Models that fit on 1-2 GPUs |
| Speculative decoding | Latency reduction (1.5-2x speedup) | Latency-critical applications | When draft model unavailable or throughput-bound |
| Prefix caching | Repeated system prompt cost | Same prompt prefix across requests | Highly diverse prompts |
| Cascading (small→large fallback) | Cost reduction with quality floor | When small model handles 70%+ traffic | Latency-sensitive (adds retry latency) |

## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/Director Says |
|-----------------|------------------------------|
| "Qwen matches GPT-4 on MMLU so we should self-host" | "Benchmark parity masks capability gaps on our domain tasks. We need held-out eval + A/B test before committing to 6-month infrastructure build" |
| "We should use the API because it's simpler" | "At 200M tokens/day, the API costs $60K/month. Self-hosted break-even is 3 months with our traffic shape. The simplicity argument has a dollar threshold" |
| "Let's quantize to 4-bit to save memory" | "AWQ-4bit loses <1% on aggregate benchmarks but we need to validate on our tail distribution -- rare-token domains may see 3-5% degradation [15]" |
| "MoE is more efficient because fewer params activate" | "MoE efficiency is theoretical until you solve expert load balancing. In production, 3 of 8 experts handle 80% of traffic, creating hotspots that negate the FLOP savings [4][5]" |
| "We need 128K context for document processing" | "128K context at 72B consumes 10GB KV cache per request, limiting us to 10 concurrent requests per node. We need YaRN [10] + retrieval augmentation to keep batch sizes viable" |
| "vLLM gives us best throughput" | "vLLM's PagedAttention [6] gives 8x throughput improvement, but we need to instrument KV cache utilization and autoscale on memory pressure, not compute utilization" |
| "GPT-4 is better at reasoning so use it for everything" | "Route 80% of traffic to self-hosted at $0.80/1M tokens; reserve GPT-4o at $10/1M for the 20% requiring multi-step reasoning. That is a 7x cost reduction at 95% quality parity" |

## Qwen3-32B vs GPT-OSS-120B: Direct Comparison

> **Added:** 2026-06-06 | **Source:** Web research (OpenAI model card arxiv:2508.10925, Qwen3 technical report arxiv:2505.09388)

### Architectural Context

These models are **not direct competitors** — they target fundamentally different niches:

| Feature | Qwen3-32B | GPT-OSS-120B |
|---------|-----------|--------------|
| Architecture | Dense Transformer | Mixture-of-Experts (MoE) |
| Total Parameters | 32B | 116.8B |
| Active Parameters | 32B (100%) | 5.1B (~4.4%) |
| Layers | 64 | 36 |
| Experts | N/A (dense) | 128 (top-4 selected) |
| Context Length | 128K | 131K |
| Reasoning Mode | Thinking/Non-thinking hybrid | Low/Medium/High levels |
| Quantization | BF16 (standard) | MXFP4 (4.25 bits for MoE weights) |
| Training Data | 36T tokens, 119 languages | Trillions (unspecified), CoT RL (o3-style) |
| Training Cost | Not disclosed | 2.1M H100-hours |
| License | Apache 2.0 | Apache 2.0 |

### Benchmark Head-to-Head

| Benchmark | Qwen3-32B (Base) | GPT-OSS-120B (High) | Winner |
|-----------|------------------|---------------------|--------|
| MMLU | 83.61 | 90.0 | GPT-OSS-120B |
| MMMLU (multilingual) | 83.83 | 81.3 | Qwen3-32B |
| GPQA Diamond | 49.49 | 80.1 | GPT-OSS-120B |
| GSM8K | 93.40 | — | — |
| AIME 2024 | <85.7* | 95.8 | GPT-OSS-120B |
| EvalPlus (code) | 72.05 | — | — |
| Codeforces Elo | — | 2463-2622 | GPT-OSS-120B |
| SWE-Bench Verified | — | 62.4 | GPT-OSS-120B |
| SimpleQA (hallucination) | — | 16.8% acc (78.2% hallucination) | Qwen3-32B |

*Qwen3-235B (flagship) achieves 85.7% on AIME'24; Qwen3-32B would score lower.

### MXFP4 Precision: Not a Compromise

GPT-OSS-120B ships in MXFP4 (4.25 bits) as its **release format** — all published benchmarks above were measured at this precision. There is no separate "full precision" checkpoint. MXFP4 works well for MoE because: (1) each expert specializes on narrow distributions (lower dynamic range), (2) top-4 ensemble dilutes per-expert quantization error, (3) microscaling blocks preserve local precision. Deployment: MXFP4 fits on 1× H100 (80GB); BF16 would require 3× H100s (~234GB) for marginal-if-any quality gain. vLLM supports both via `developers.openai.com/cookbook/articles/gpt-oss/run-vllm`.

### Where Qwen3-32B Wins

1. **Multilingual breadth** — 119 languages/dialects; MMMLU 83.83% vs 81.3%
2. **Lower hallucination** — GPT-OSS-120B's 5.1B active params limit factual recall (78.2% hallucination rate on SimpleQA)
3. **Consistent non-reasoning performance** — GPT-OSS-120B at "low" reasoning drops hard (AIME to 56.3%, MMLU to 85.9%)
4. **Fine-tuning flexibility** — Dense architecture works cleanly with standard LoRA/SFT methods
5. **Deployment simplicity** — Predictable compute, no MoE routing complexity

### Where GPT-OSS-120B Wins

1. **Math reasoning** — AIME 2024: 95.8% (even Qwen3-235B flagship only hits 85.7%)
2. **Graduate-level science** — GPQA Diamond: 80.1% vs ~49.5%
3. **Competitive coding** — Codeforces Elo 2463-2622 with tools
4. **Real-world coding** — SWE-Bench Verified: 62.4%
5. **MMLU** — 90.0% vs 83.6%
6. **Agentic tool use** — Custom "Harmony" format for function calling, web browsing, code execution (Tau-Bench Retail: 67.8%)
7. **Single-GPU deployment** — MXFP4 quantization fits 117B on one 80GB GPU

### Deployment Decision

```
Choose Qwen3-32B when:
  - Multilingual workloads (119 languages)
  - Fine-tuning to domain-specific tasks
  - Factual QA where hallucination is unacceptable
  - Budget-constrained local deployment
  - Simple, predictable inference latency

Choose GPT-OSS-120B when:
  - Complex reasoning tasks (math, science, logic)
  - Competitive programming / code generation
  - Agentic workflows with tool use
  - Maximum benchmark performance on English tasks
  - Single-GPU deployment with quantization
```

---

## Application Decision Framework: MoE (GPT-OSS-120B) vs Dense (Qwen3-32B)

> **Added:** 2026-06-06 | **Source:** Synthesized from existing knowledge base entries

### 5-Axis Decision Matrix

| Axis | → GPT-OSS-120B (MoE) | → Qwen3-32B (Dense) |
|------|----------------------|---------------------|
| Task complexity | Multi-step reasoning, math, competitive coding | Simple QA, translation, summarization, chat |
| Fine-tuning needs | No fine-tuning needed (use as-is) | Domain adaptation required (LoRA/SFT) |
| Latency profile | Variable OK (reasoning levels) | Predictable, consistent latency required |
| Language breadth | English-dominant | 119 languages, multilingual required |
| Hallucination tolerance | Acceptable (78.2% on SimpleQA) | Critical (factual accuracy paramount) |

### Application Routing Table

| Application | Best Model | Key Reason |
|-------------|-----------|-----------|
| Math/science reasoning | GPT-OSS-120B | AIME 95.8%, GPQA 80.1% |
| Competitive programming | GPT-OSS-120B | Codeforces Elo 2463-2622 |
| Agentic tool use | GPT-OSS-120B | Harmony format, Tau-Bench 67.8% |
| SWE-Bench coding | GPT-OSS-120B | 62.4% real-world bug fixing |
| Multilingual workloads | Qwen3-32B | 119 languages, MMMLU 83.83% |
| Domain fine-tuning | Qwen3-32B | Standard LoRA/SFT, predictable |
| Factual QA | Qwen3-32B | Lower hallucination (32B active vs 5.1B) |
| Customer support chatbot | Qwen3-32B | Consistent quality, lower cost |
| Document summarization | Qwen3-32B | Efficient, task doesn't need deep reasoning |

### Decision Tree (Quick Reference)

```
Reasoning-heavy (math/logic/coding)? → GPT-OSS-120B
Multilingual required?               → Qwen3-32B
Fine-tuning needed?                   → Qwen3-32B
Factual accuracy critical?            → Qwen3-32B
Agentic/tool-calling workflow?        → GPT-OSS-120B
Otherwise?                            → Either; route by infra preference
```

### Anti-Pattern: Using One Model for Everything

GPT-OSS-120B at "low" reasoning drops to AIME 56.3%, MMLU 85.9% — worse than Qwen3-32B on non-reasoning tasks. Qwen3-32B leaves 10-40% quality on the table for reasoning-heavy tasks. The optimal pattern is **hybrid routing** by task complexity.

---

## Reverse Distillation: Qwen3-32B → GPT-OSS-120B

> **Added:** 2026-06-06 | **Source:** arXiv:2312.09390, arXiv:2501.12948, arXiv:2407.01906, arXiv:2401.10491, arXiv:2405.09673

### When It's Possible

| Method | Feasibility | Conditions |
|--------|-------------|-----------|
| SFT on Qwen3 outputs + LoRA | **YES** | Target capability latent in GPT-OSS; mix with replay data to prevent forgetting [16][17] |
| Expert-targeted fine-tuning (ESFT) | **YES** | Requires routing analysis; freeze non-target experts [18] |
| GKD (on-policy distillation) | **YES** | GPT-OSS generates, Qwen3 corrects; avoids covariate shift [19] |
| Knowledge Fusion | **YES** | Architecture-agnostic via generative distributions [20] |
| Logit-level distillation | **NO** | Different tokenizers → misaligned vocabularies |
| Weight merging / task arithmetic | **NO** | Different architectures (32B dense ≠ 117B MoE) |

### When It Fails

- **Style mimicry without substance**: Student copies format but fails on novel tasks [arXiv:2305.15717]
- **Capability ceiling**: Cannot exceed Qwen3's quality on transferred domain via imitation alone
- **MoE routing disruption**: Fine-tuning shifts token distributions, breaking load balance
- **Insufficient data diversity**: Transfer only works on represented scenarios
- **Zero latent capacity**: Cannot inject knowledge with no representation in existing weights

### Recommended Pipeline

```
1. Generate diverse multilingual data from Qwen3-32B (50+ languages)
2. Mix: 30-50% new multilingual / 50-70% GPT-OSS replay (reasoning, math, coding)
3. LoRA fine-tune GPT-OSS-120B on single H100 (MXFP4)
4. Evaluate BOTH: multilingual (MMMLU) AND reasoning (AIME, GPQA)
5. Advanced: ESFT — identify multilingual experts via routing analysis, train only those
```

### Key Insight

This is **selective capability augmentation**, not classical distillation. Qwen3-32B's multilingual outputs serve as signal to **activate latent pathways** in GPT-OSS-120B's 128-expert pool. The 5.1B active params per token constrain expressiveness, but the full 117B param pool likely contains under-utilized multilingual experts.

### Licensing

Both Apache 2.0. Fully legal — no restrictions on using Qwen3 outputs to train GPT-OSS. Machine-generated outputs are not copyrightable.

---

## References

### Foundational Papers

- [1] OpenAI (2023) -- GPT-4 Technical Report -- arXiv:2303.08774 -- Establishes GPT-4 capabilities and evaluation methodology; architecture undisclosed
- [2] Bai et al. (2023) -- Qwen Technical Report -- arXiv:2309.16609 -- Documents Qwen architecture, training data composition, and multilingual design
- [3] Jiang et al. (2024) -- Mixtral of Experts -- arXiv:2401.04088 -- Demonstrates 8x7B MoE matching 70B dense quality at fraction of inference cost
- [4] Fedus et al. (2022) -- Switch Transformers -- arXiv:2101.03961 -- Introduces simplified MoE with top-1 routing and auxiliary load-balancing loss
- [5] Shazeer et al. (2017) -- Outrageously Large Neural Networks: The Sparsely-Gated MoE Layer -- arXiv:1701.06538 -- Foundational MoE paper establishing gating mechanisms and load balancing
- [6] Kwon et al. (2023) -- Efficient Memory Management for LLM Serving with PagedAttention -- arXiv:2309.06180 -- Introduces PagedAttention for vLLM; 2-4x throughput improvement
- [7] Dettmers et al. (2022) -- LLM.int8(): 8-bit Matrix Multiplication for Transformers -- arXiv:2208.07339 -- Enables 8-bit inference with outlier-aware mixed precision
- [8] Frantar et al. (2023) -- GPTQ: Accurate Post-Training Quantization for GPT -- arXiv:2210.17323 -- Hessian-based 4-bit quantization with minimal quality loss
- [9] Su et al. (2021) -- RoFormer: Enhanced Transformer with Rotary Position Embedding -- arXiv:2104.09864 -- Introduces RoPE; now standard in Llama, Qwen, Mistral families
- [10] Peng et al. (2023) -- YaRN: Efficient Context Window Extension -- arXiv:2309.00071 -- NTK-aware RoPE interpolation extending context 16-32x with minimal fine-tuning
- [11] Chiang et al. (2024) -- Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference -- arXiv:2403.04132 -- Live ELO-based evaluation via blind pairwise comparison
- [12] Touvron et al. (2023) -- Llama 2 -- arXiv:2307.09288 -- Open-weight 7B-70B models; establishes training data and RLHF methodology
- [13] DeepSeek (2024) -- DeepSeek-V2: A Strong, Economical, and Efficient MoE -- arXiv:2405.04434 -- Multi-head latent attention + MoE; 236B total / 21B active at lowest cost
- [14] Team GLM (2024) -- ChatGLM: A Family of Large Language Models -- arXiv:2406.12793 -- Chinese-English bilingual LLM with progressive training methodology
- [15] Lin et al. (2024) -- AWQ: Activation-aware Weight Quantization -- arXiv:2306.00978 -- 4-bit quantization preserving salient channels; <1% quality loss on LLMs
- [16] Burns et al. (2023) -- Weak-to-Strong Generalization -- arXiv:2312.09390 -- GPT-2 supervision on GPT-4 recovered near-GPT-3.5; proved smaller models can improve larger ones
- [17] Biderman et al. (2024) -- LoRA Learns Less and Forgets Less -- arXiv:2405.09673 -- LoRA preserves base model capabilities better than full fine-tuning during knowledge transfer
- [18] Xu et al. (2024) -- ESFT: Expert-Specialized Fine-Tuning for MoE -- arXiv:2407.01906 -- Selective expert training; routing is task-concentrated; freeze unrelated experts
- [19] Singh et al. (2023) -- GKD: Generalized Knowledge Distillation -- arXiv:2306.13649 -- On-policy distillation avoiding covariate shift; trains on student's own distribution
- [20] Wan et al. (2024) -- Knowledge Fusion of Large Language Models -- arXiv:2401.10491 (ICLR 2024) -- Cross-architecture transfer via generative distributions; architecture-agnostic

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1; added 6 diverse DE probes (MoE math, systems serving, data composition, evaluation reliability, cost modeling, long-context architecture); 15+ inline citations; removed appendix and sub-Q&A banks |
| 2026-06-06 | Added Qwen3-32B vs GPT-OSS-120B section | Direct comparison with benchmarks from OpenAI model card (arxiv:2508.10925) and Qwen3 technical report (arxiv:2505.09388); covers architecture, strengths/weaknesses, deployment decision framework |
| 2026-06-06 | Added reverse distillation section | Feasibility analysis of distilling Qwen3-32B capabilities into GPT-OSS-120B; covers when possible (SFT+LoRA, ESFT, GKD) vs impossible (logit distillation, weight merging); practical pipeline and 5 new references |
| 2026-06-06 | Added application decision framework | 5-axis decision matrix (complexity, fine-tuning, latency, language, hallucination), routing table, decision tree, and anti-pattern guidance for choosing MoE vs dense |
| 2026-06-06 | Added MXFP4 precision note | Clarified that benchmarks ARE at MXFP4 (release format), not a degraded version; vLLM support for both; memory requirements comparison |
