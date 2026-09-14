---
title: "tool-selection-as-contextual-bandit"
summary: ""
sources:
  - agentic-systems/agentic-systems-ref.md
createdAt: 2026-05-28T19:56:20.965805+00:00
updatedAt: 2026-05-28T19:56:20.965805+00:00
---
# Tool Selection as Contextual Bandit

Tool selection as contextual bandit is a formal machine learning approach to choosing which tools an AI agent should use at each step of a multi-step task. This framework treats tool selection as a contextual bandit problem, where the agent must select one tool from a set of available options based on the current context (task description, conversation history, partial results) and learn from the outcomes to improve future selections. ^[agentic-systems-ref.md]

## Problem Formulation

In the contextual bandit formulation, tool selection is defined as:

- **State** s_t = (task, conversation, partial_results) - the current context
- **Action** a_t ∈ {tool_1, tool_2, ..., tool_K} - selecting one of K available tools  
- **Reward** r_t = contribution_to_task_completion(tool_response) - how much the tool call helped accomplish the user's goal
- **Policy** π(a|s) = P(choose tool a given state s) - the learned selection strategy

This differs from traditional LLM-based tool selection where a language model reads tool descriptions and picks a tool based on reasoning, which is non-deterministic and cannot guarantee improvement over time. ^[agentic-systems-ref.md]

## When to Use Bandit-Based Selection

**Bandit-based tool selection** is appropriate when:
- There is sufficient historical data of tool selections and outcomes
- Task types are recurring and can be classified
- Deterministic, fast selection is preferred over flexible reasoning
- The system needs to improve tool selection accuracy over time through learning

**LLM-based tool selection** remains better for:
- Novel or ambiguous situations requiring flexible reasoning
- Tasks with insufficient historical data
- Situations requiring natural language understanding of tool descriptions ^[agentic-systems-ref.md]

## Hybrid Approach

The most practical production approach combines both methods:

1. For known task types with sufficient historical data → bandit selects tool (fast, calibrated)
2. For novel/ambiguous situations → LLM selects tool (flexible, expensive)  
3. The bandit model is continuously trained on the LLM's successful selections
4. Over time, more tasks shift from the expensive LLM path to the efficient bandit path ^[agentic-systems-ref.md]

## LinUCB Implementation

[[Linear Upper Confidence Bound]] (LinUCB) is a common algorithm for contextual bandits that can be applied to tool selection:

```
For each tool k:
  Score(k) = x_t^T θ_k + α * sqrt(x_t^T A_k^{-1} x_t)
  
  where:
    x_t = feature vector of current state
    θ_k = learned parameters for tool k  
    A_k = accumulated context matrix
    α = exploration coefficient

Select tool with highest Score
```

The exploration term ensures under-tried tools get selected occasionally, building data for better future decisions. ^[agentic-systems-ref.md]

## Cold Start Problem

When adding new tools to the system, several strategies address the lack of initial data:

- **Forced exploration**: Route a percentage of applicable tasks to the new tool regardless of bandit score
- **Transfer learning**: Initialize parameters from similar existing tools
- **LLM fallback**: Use LLM-based selection during cold-start until sufficient data accumulates ^[agentic-systems-ref.md]

## Production Considerations

At scale, bandit-based tool selection offers significant advantages. For systems serving millions of users, the deterministic nature and ability to improve over time make it more suitable than LLM-based selection for common patterns. However, the hybrid approach ensures flexibility is maintained for edge cases while optimizing the common path. ^[agentic-systems-ref.md]
