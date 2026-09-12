---
title: "How easy or hard is it to fine-tune an LLM for tool-calling and API calls? What are the key challenges? Which technique works best -- SFT or RL?"
summary: "Moderate difficulty for basic tool calling via SFT (works in days with ~1K examples). Hard for reliable multi-step tool orchestration. SFT is the dominant and proven approach for tool calling — it directly teaches the structured output format (JSON function calls). RL adds value ONLY for multi-tool sequencing and recovery from tool errors where verifiable rewards exist (did the sequence achieve the goal?). Key challenges: schema adherence, argument hallucination, multi-tool planning, error recovery, and parallel vs sequential call decisions."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
## Difficulty Assessment

| Capability Level | Difficulty | Data Needed | Time |
|-----------------|-----------|-------------|------|
| Basic single-tool calling (format learning) | **Easy** | 500-1K examples | Days |
| Multi-tool with correct argument extraction | **Moderate** | 5K-10K examples | 1 week |
| Parallel vs sequential tool decision | **Moderate-Hard** | 10K+ examples with both patterns | 1-2 weeks |
| Multi-step tool chains (output of tool A → input of tool B) | **Hard** | 10K+ trajectory examples | 2-4 weeks |
| Error recovery (tool fails → retry/alternative) | **Hard** | Requires RL or trajectory-level SFT | Weeks |
| Novel tool generalization (unseen tool schemas) | **Very Hard** | Diverse schemas + meta-learning | Research-stage |

## Key Challenges

### 1. Schema Adherence (Structured Output Fidelity)

The model must emit **valid JSON** conforming to the tool's schema — correct field names, types, required fields, enum values. A single typo in a function name or argument renders the call useless.

```
Challenge: Model generates {"function": "get_wether", "args": {"loc": "NYC"}}
Required:  {"function": "get_weather", "args": {"location": "New York, US", "format": "celsius"}}

Failure modes:
- Hallucinated function names (inventing tools that don't exist)
- Wrong argument types (string where int expected)
- Missing required fields
- Extra fields not in schema
```

**Why it's hard**: LLMs are trained on natural language, not structured output. The model must learn to suppress its natural text generation in favor of exact JSON conformance.

### 2. Argument Hallucination

The model invents plausible-sounding arguments that don't match what the user asked for, or fills in fields with guesses rather than extracting from context.

```
User: "What's the weather in my city?"
Bad:  {"location": "San Francisco, US"}  ← hallucinated, user didn't say this
Good: Ask the user for clarification OR leave location empty if optional
```

### 3. When to Call vs When to Respond

The model must learn WHEN a tool call is appropriate vs when to respond directly. Over-triggering tools wastes resources; under-triggering fails the task.

```
User: "What's 2+2?"
Bad:  Call calculator_tool(expression="2+2")  ← overkill
Good: "4"

User: "What's the current stock price of AAPL?"
Bad:  "The stock price is approximately $180"  ← hallucinated, stale
Good: Call get_stock_price(symbol="AAPL")
```

### 4. Multi-Step Tool Orchestration

Sequencing multiple tools where outputs feed into subsequent calls. Requires planning BEFORE the first call.

```
User: "Book me the cheapest flight from NYC to London next Tuesday"

Required sequence:
  1. search_flights(from="NYC", to="London", date="2026-06-10") → results
  2. sort_by_price(results) → cheapest
  3. book_flight(flight_id=cheapest.id, passenger=user) → confirmation

Failure modes:
- Calling book_flight before search (no flight_id yet)
- Losing context between calls (forgetting search results)
- Not handling errors (flight sold out → retry with next cheapest)
```

### 5. Parallel vs Sequential Decision

Some tool calls are independent (can run in parallel); others are dependent (must be sequential). The model must decide correctly.

```
Parallel-safe: "What's the weather in NYC and London?"
  → Call get_weather("NYC") AND get_weather("London") simultaneously

Sequential-required: "Find the CEO of Apple, then look up their net worth"
  → Call search_person("CEO", "Apple") → get result → Call net_worth(person_name)
```

### 6. Error Recovery

Tools fail in production (timeouts, invalid responses, rate limits). The model must detect failures and adapt.

```
Tool returns: {"error": "rate_limited", "retry_after": 5}
Bad: Present error to user
Good: Wait and retry, or use alternative tool, or inform user of delay
```

## SFT vs RL for Tool Calling: The Verdict

### SFT is the Dominant Approach (and Usually Sufficient)

| Dimension | SFT for Tool Calling |
|-----------|---------------------|
| **What it teaches** | Correct output FORMAT (JSON), schema adherence, argument extraction, when-to-call decision |
| **Data format** | JSONL with messages + tool_calls + tool definitions (OpenAI format) |
| **Examples needed** | 500-1K for basic; 5K-10K for robust multi-tool |
| **What it can't teach** | Multi-step PLANNING, error recovery STRATEGY, optimal tool SEQUENCING |
| **Cost** | $ (single GPU, days) |
| **Industry evidence** | OpenAI's fine-tuning API, Qwen3's tool-calling training, Mistral's function calling — all SFT-based |

**Why SFT works well for tool calling:**
- Tool calling is primarily a FORMAT problem (emit correct JSON) → SFT excels at format learning
- The "right answer" is deterministic and demonstrable → perfect SFT territory
- Schema adherence is a hard constraint → SFT with enough diverse examples converges quickly
- Benchmarks (BFCL, ToolBench) show SFT'd models achieve >90% format compliance with 5K examples

**SFT training data structure:**
```json
{
  "messages": [
    {"role": "user", "content": "What's the weather in Tokyo?"},
    {"role": "assistant", "tool_calls": [
      {"type": "function", "function": {"name": "get_weather", "arguments": "{\"location\":\"Tokyo, JP\",\"format\":\"celsius\"}"}}
    ]}
  ],
  "tools": [{"type": "function", "function": {"name": "get_weather", ...schema...}}],
  "parallel_tool_calls": false
}
```

### When RL Adds Value (Beyond SFT)

| Dimension | RL for Tool Calling |
|-----------|---------------------|
| **What it teaches** | Multi-step PLANNING, tool SEQUENCING optimization, error RECOVERY strategy |
| **Reward signal** | Task completion (did the sequence achieve the user's goal?) |
| **When needed** | Multi-tool chains, agentic workflows, recovery from failures |
| **What it can't fix** | Basic format compliance (use SFT for that first) |
| **Cost** | $$$ (multi-GPU, weeks) |
| **Industry evidence** | GPT-OSS-120B's "Harmony" training, Tau-Bench 67.8% (likely RL-refined) |

**Why RL helps for MULTI-STEP tool use:**
- Multi-step sequencing has a VERIFIABLE reward: did the final outcome match the user's intent?
- Error recovery is hard to demonstrate (you'd need examples of every failure type) but easy to REWARD
- Optimal tool ordering is a planning problem → RL explores and finds better sequences than static demos
- The "correct" sequence may not exist in your SFT data (novel tool combinations)

**RL reward for tool-calling:**
```
Reward = (
  +1.0 if final task completed successfully
  +0.5 if partial completion (some sub-goals met)
  -0.2 per unnecessary tool call (efficiency penalty)
  -0.5 per hallucinated tool call (called non-existent function)
  -1.0 if task failed completely
)
```

### The Recommended Pipeline

```
Phase 1: SFT (Always — this is mandatory)
  └─ Teach format: JSON structure, schema adherence, argument extraction
  └─ Teach when-to-call: distinguish tool-worthy queries from direct answers
  └─ Data: 5K-10K examples covering your tool set
  └─ Cost: $500-2K, days

Phase 2: RL (Only if multi-step/agentic — optional for basic tool calling)
  └─ Teach sequencing: optimal tool ordering for multi-step tasks
  └─ Teach recovery: handle tool failures gracefully
  └─ Reward: task completion rate on eval trajectories
  └─ Method: GRPO with task-completion reward
  └─ Cost: $5K-20K, weeks
  
Skip Phase 2 if:
  - All your tools are single-call (no chaining needed)
  - Format compliance is the only gap (SFT solves this alone)
  - Budget/timeline is tight
```

## Comparison Table: SFT vs RL for Each Tool-Calling Challenge

| Challenge | SFT Effectiveness | RL Effectiveness | Winner |
|-----------|-------------------|------------------|--------|
| Schema adherence (JSON format) | **Excellent** (learns format directly) | Poor (format is not a reward-optimizable property) | **SFT** |
| Argument extraction | **Excellent** | Moderate | **SFT** |
| When to call vs respond | **Good** (with enough examples) | Good (can reward correct decisions) | **SFT** (simpler) |
| Parallel vs sequential decision | **Good** (with `parallel_tool_calls` flag in data) | Good | **SFT** (simpler) |
| Multi-step tool chains | Moderate (needs trajectory examples) | **Excellent** (can optimize full sequence) | **RL** |
| Error recovery | Poor (hard to demonstrate every failure) | **Excellent** (reward surviving failures) | **RL** |
| Novel tool generalization | Moderate (needs diverse schema exposure) | Moderate | **Tie** (both limited) |
| Efficiency (minimal tool calls) | Poor (imitates demos, doesn't optimize) | **Good** (can penalize unnecessary calls) | **RL** |

## Practical Advice

### If You're Starting from Zero:

1. Start with SFT on 1K-5K examples of your specific tools
2. Use OpenAI's JSONL format (most tooling supports it)
3. Include diverse examples: different query phrasings, edge cases, "don't call" examples
4. Evaluate on held-out tool-calling benchmarks (BFCL format)
5. If accuracy > 90% on format + argument extraction → DONE (no RL needed)
6. If multi-step sequencing is poor → add RL with task-completion reward

### If You're Fine-Tuning Qwen3-32B or GPT-OSS-120B:

- **Qwen3-32B**: Already has strong tool-calling from pre-training (BFCL leader). SFT with your specific tool schemas (500 examples) should suffice for domain adaptation.
- **GPT-OSS-120B**: Already has Harmony format for agentic tool use (Tau-Bench 67.8%). Fine-tuning with ESFT (target tool-related experts) for your specific API set.

### Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| "RL for basic tool calling" | RL can't teach JSON format — it needs SFT first | SFT for format, RL only for sequencing |
| "Only 50 examples" | Models underfit on format with <500 examples | Minimum 500; ideally 5K for robustness |
| "Same tool in all examples" | Model overfits to one schema | Diverse tools, diverse arguments, diverse phrasings |
| "No negative examples" | Model doesn't learn WHEN NOT to call | Include 20-30% "don't call" examples |
| "Skip evaluation on format compliance" | Ship model that hallucinates tool names | Test: exact match on function name + valid JSON parse rate |

## Related

- [[Function Calling Training Examples]] — JSONL format details
- [[Tool Schema Definition]] — Schema structure for training data
- [[Parallel Tool Calls Configuration]] — Sequential vs parallel training
- [[SFT vs RL Pros Cons and Industry Cases]] — General SFT vs RL decision
- [[GPT-OSS-120B]] — Harmony format for agentic tool use
- [[Qwen3 Language Model]] — BFCL benchmark leader for tool calling
