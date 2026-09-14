---
title: "What Is Grouped-Query Attention (GQA)? | AI/TLDR"
source: "https://ai-tldr.dev/learn/llm-fundamentals/transformers-and-attention/grouped-query-attention/"
ingestedAt: "2026-07-30T13:37:21Z"
---
## // In plain English

Inside a [transformer](/learn/llm-fundamentals/transformers-and-attention/what-is-a-transformer/), the [attention](/learn/llm-fundamentals/transformers-and-attention/how-attention-works/) mechanism is split into many parallel _heads_. Each head looks at the sentence in its own way â one might track grammar, another might track who _he_ or _she_ refers to. To do its job, every head builds three things from the tokens: **queries** (what this token is looking for), **keys** (what each other token offers), and **values** (the actual content each token carries). The head matches queries against keys to decide where to look, then pulls in the matching values.

Grouped-Query Attention â machinelearningmastery.com

In classic **multi-head attention (MHA)** , every head gets its own private set of queries, keys, and values. That is powerful, but it is also expensive â during text generation the model must keep every key and value in memory for every head, for every token it has seen so far. **Grouped-query attention (GQA)** keeps a separate query for each head, but makes _several heads share one set of keys and values_. Fewer key/value sets means less memory to store and less data to move.

Picture a busy library reading room. In MHA, every reader (a query head) has their own personal copy of every book (keys and values) on their own desk â accurate, but the room runs out of space fast. GQA seats readers in small groups and gives each group _one shared shelf_ of books. The readers still ask their own questions and reach their own conclusions; they just consult a shared reference instead of hoarding private copies. You lose almost nothing in understanding, and the room holds far more readers.

NOTE

The name is literal: query heads are sorted into **groups** , and all the query heads in a group share the same keys and values. "Grouped-query attention" = group the query heads, share the keys/values within each group.

## // Why it matters

GQA exists to attack one specific, painful bottleneck in running large language models: the **KV cache**. When a model generates text one token at a time, it would be wasteful to recompute the keys and values for every previous token on every step, so it stores them in memory and reuses them. That store is the KV cache, and it grows with the conversation length, the number of layers, and â crucially â the number of key/value heads.

  * **Memory pressure.** On long conversations the KV cache can grow to gigabytes and rival or exceed the size of the model weights themselves. It often decides how many users you can serve on one GPU at once. Halving or quartering the key/value heads shrinks the cache by the same factor.
  * **Speed.** Generating each new token is usually limited not by raw math but by how fast keys and values can be read from GPU memory (it is _memory-bandwidth bound_). Fewer key/value sets means less data to fetch each step, so tokens come out faster.
  * **Quality.** The obvious way to save memory â collapse all heads down to a single shared key/value set (multi-query attention) â saves the most but can hurt accuracy and training stability. GQA keeps several groups, recovering almost all of MHA's quality while keeping most of the savings.



Who should care? Anyone who serves or fine-tunes open models, anyone reading model architecture cards, and anyone trying to understand [why LLMs need GPUs](/learn/llm-fundamentals/llm-basics/why-llms-need-gpus/) and why long contexts get slow and costly. GQA is now the default attention design in most widely used open models, so understanding it explains a line you will see in nearly every modern config: a query-head count that is larger than the key/value-head count.

## // How it works

Start from standard multi-head attention. Say a model has 32 attention heads. In MHA there are 32 query heads, 32 key heads, and 32 value heads â a private key/value pair for each query. GQA changes only the key and value side: it keeps all 32 query heads but defines a smaller number of key/value heads, say 8, and assigns each one to a _group_ of 4 query heads. Every query head in a group reads from the same shared key/value head.

// Same 8 query heads, different key/value sharing

Multi-head (MHA)

  * 8 query heads
  * 8 key/value sets
  * 1 K/V per query
  * Biggest KV cache
  * Best quality



Grouped-query (GQA)

  * 8 query heads
  * 2 key/value sets
  * 4 queries share each K/V
  * Small KV cache
  * Near-MHA quality



Multi-query (MQA)

  * 8 query heads
  * 1 key/value set
  * All queries share 1 K/V
  * Smallest KV cache
  * Some quality loss



Seen this way, GQA is a dial, not a new mechanism. Set the number of key/value groups equal to the number of query heads and you are back to plain MHA. Set it to exactly 1 and you have **multi-query attention (MQA)** , where every head shares a single key/value set. GQA lives in the useful middle â typically 4 or 8 groups â capturing most of MQA's savings while keeping most of MHA's quality.

### What actually changes in the model

The math of attention is identical; only the _shapes_ shrink. The weight matrices that project tokens into keys and values become smaller, because they now produce fewer key/value heads. At runtime, before each group of query heads does its dot-product matching, the shared key/value head is conceptually _repeated_ (broadcast) across the queries in its group so the dimensions line up. The model stores one copy in the KV cache but uses it for several query heads.

// One GQA group at generation time

4 query headseach its own query1 shared K/V headstored once in cacheBroadcast K/Vreused by all 4 queriesAttention output4 separate results

what GQA looks like in a model configjsonCOPY
    
    
    {
      "hidden_size": 4096,
      "num_attention_heads": 32,
      "num_key_value_heads": 8,
      "comment": "32 query heads, 8 K/V heads => groups of 4. 4x smaller KV cache than MHA."
    }

That single field, `num_key_value_heads`, is how you spot GQA in the wild. When it equals `num_attention_heads`, the model uses plain MHA. When it is smaller, the model uses GQA with that many groups. When it equals 1, the model uses MQA.

### Where existing models get GQA from

You do not always have to train a GQA model from scratch. The original work showed you can **uptrain** an existing multi-head model: average each group of key/value heads from the trained checkpoint into one shared head, then continue training for a small fraction of the original compute. The model adapts to the shared keys/values and recovers nearly all of its quality cheaply. This is part of why GQA spread so quickly â it was easy to retrofit, not just to design in.

## // MHA vs MQA vs GQA at a glance

All three are the _same_ attention operation. They differ only in how many key/value heads exist behind the query heads. Reading them as one spectrum makes the tradeoff obvious.

Scheme| K/V heads (for 32 query heads)| KV-cache size| Quality| Typical use  
---|---|---|---|---  
Multi-head (MHA)| 32 (one per query)| Largest| Best| Older / smaller models  
Grouped-query (GQA)| 4 or 8 (shared in groups)| Small| Near-MHA| Most modern open models  
Multi-query (MQA)| 1 (shared by all)| Smallest| Slight drop| Latency-critical, some models  
  
The headline numbers: going from MHA to MQA on a 32-head model cuts the key/value heads by 32x; GQA with 8 groups cuts them by 4x. Both shrink the KV cache by exactly that factor, since the cache size scales with the number of key/value heads. GQA's pitch is that 4x smaller is already a huge win, and you keep almost all the quality you would lose by going all the way to 1.

TIP

A clean mental model: MHA and MQA are the two ends, GQA is the dial in between. "Number of groups" is the only knob â set it high for quality, low for memory.

## // GQA is not FlashAttention

These two often get mentioned together because both make attention faster, but they work at completely different levels and they stack â most fast models use both.

// Two different kinds of speedup

Make attention faster

GQA: change the architecturefewer K/V heads, smaller cache

FlashAttention: change the implementationsame math, smarter memory access

**GQA** is an _architectural_ change. It alters what the model is â how many key/value heads it has â so it changes the model's weights and its KV-cache size. A GQA model and an MHA model are genuinely different models with different numbers of parameters.

[**FlashAttention**](/learn/llm-fundamentals/transformers-and-attention/flash-attention-explained/) is an _implementation_ change. It computes the exact same attention math, bit for bit, but reorders the memory reads and writes on the GPU so far less data shuttles back and forth. It does not change the model's weights or its cache size at all â you can apply it to an MHA or a GQA model without retraining. GQA shrinks _what_ you store; FlashAttention speeds up _how_ you compute over it.

## // Practical notes and pitfalls

GQA is mostly a free win, but a few things trip people up when reading configs or tuning models.

  * **Query heads still cost the same.** GQA only shrinks the key/value side. The number of query heads, and the attention math they do, is unchanged â so GQA mainly helps memory and generation speed, not the raw compute of a forward pass.
  * **The win is biggest at long context and high batch size.** The KV cache grows with sequence length and concurrent users. If your prompts are short and you serve one request at a time, the cache was never your bottleneck and GQA's benefit is smaller.
  * **Number of query heads must divide evenly into groups.** You cannot pick any combination â `num_attention_heads` must be a whole-number multiple of `num_key_value_heads`, since every group holds the same number of query heads.
  * **Too few groups can hurt.** Pushing toward MQA (1 group) maximizes savings but risks quality loss and less stable training. GQA's whole point is that a handful of groups recovers almost all of that quality â do not assume fewer is always better.
  * **It is invisible to your prompts.** GQA is a model-internal detail. As a user calling an API you never see it; it only matters when you choose, host, or fine-tune a model.

WATCH OUT

GQA reduces the KV cache by a fixed factor, but it does not stop the cache from growing with context length. A very long conversation can still exhaust GPU memory even with GQA â it just takes longer to get there. For long contexts you usually combine GQA with other tricks like cache quantization or sliding-window attention.

## // Going deeper

GQA was introduced in a 2023 paper from Google researchers (Ainslie and colleagues), building directly on Noam Shazeer's earlier multi-query attention work. It landed at exactly the moment the field hit a wall on inference cost, and it spread fast: it became the standard attention design across most major open model families because it is cheap to adopt, easy to uptrain into, and nearly lossless. If you read the architecture notes of almost any recent open model, you will find a query-head count larger than its key/value-head count â that is GQA.

A few threads worth following once the basics click:

  * **Choosing the group count.** The original work found that going from MHA straight to MQA hurt quality, but a modest number of groups (often 8) recovered nearly all of it while keeping most of the speedup. The sweet spot depends on model size and how memory-bound your serving is.
  * **Stacking with quantization.** Even a GQA cache can be large at long context. A common next step is to store the keys and values in lower precision (8-bit or 4-bit), cutting cache memory further on top of the head sharing.
  * **Interaction with attention variants.** GQA combines cleanly with sliding-window or local attention (which bounds how far back each token looks) and with FlashAttention (which optimizes the compute). These address different costs and are routinely used together.
  * **Not the same as Mixture-of-Experts.** GQA shares key/value _heads_ within the attention block to save memory. [Mixture-of-experts](/learn/llm-fundamentals/transformers-and-attention/mixture-of-experts-explained/) instead routes each token to a subset of feed-forward "expert" sublayers to save compute. They live in different parts of the transformer and are often used in the same model.



The durable lesson is that a lot of modern LLM progress is not about making models smarter but about making them _cheaper to run_ â and GQA is a textbook example. It is a small, almost obvious architectural tweak that, by sharing keys and values across query heads, made long-context, high-throughput serving practical. If you want the surrounding picture, see [how attention works](/learn/llm-fundamentals/transformers-and-attention/how-attention-works/) and the broader story of [how LLMs work](/learn/llm-fundamentals/llm-basics/how-llms-work/).

## // FAQ

What is grouped-query attention in simple terms?

Grouped-query attention (GQA) is a way to run a transformer's attention more cheaply. Each attention head still has its own query, but heads are sorted into groups, and all heads in a group share one set of keys and values. Sharing the keys and values shrinks the memory the model needs (the KV cache) and speeds up text generation, with almost no loss in quality.

What is the difference between multi-query and grouped-query attention?

Multi-query attention (MQA) makes _all_ query heads share a single set of keys and values, saving the most memory but sometimes hurting quality. Grouped-query attention (GQA) keeps several groups â say 8 shared key/value sets instead of 1 â so it saves a bit less memory but recovers almost all of the quality. GQA is the middle ground between MQA and standard multi-head attention.

Why does GQA speed up LLM inference?

During generation, producing each token is mostly limited by how fast keys and values can be read from GPU memory, not by raw math. GQA stores far fewer key/value sets in the KV cache, so there is less data to fetch on every step. Less memory traffic means faster tokens and, because the cache is smaller, room to serve more users at once.

Does grouped-query attention reduce model quality?

Only slightly, if at all. The original GQA research showed that a modest number of groups (often 8) recovers nearly all the accuracy of full multi-head attention while keeping most of the memory savings. That favorable tradeoff is exactly why GQA became the default in most modern open models.

How can I tell if a model uses GQA?

Look at its config for two fields: the number of attention heads and the number of key/value heads. If the key/value-head count is smaller than the attention-head count, the model uses GQA. If they are equal, it uses standard multi-head attention; if the key/value count is 1, it uses multi-query attention.

Is GQA the same as FlashAttention?

No. GQA is an architectural change â it reduces how many key/value heads the model has, which shrinks the KV cache. FlashAttention computes the exact same attention math but reorders GPU memory access to run faster, without changing the model or its cache. They solve different problems and are commonly used together.