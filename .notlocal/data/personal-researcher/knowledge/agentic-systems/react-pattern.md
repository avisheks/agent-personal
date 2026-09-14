---
title: "react-pattern"
summary: ""
sources:
  - agentic-systems/agentic-systems-ref.md
createdAt: 2026-05-28T19:55:11.028511+00:00
updatedAt: 2026-05-28T19:55:11.028511+00:00
---
# ReAct Pattern

The **ReAct Pattern** (Reasoning and Acting) is an architectural approach for agentic AI systems that interleaves explicit reasoning steps with action execution and observation of results. Rather than planning all actions upfront or executing without visible reasoning, ReAct creates a structured loop of Thought → Action → Observation that makes agent behavior transparent and debuggable.

## Overview

The ReAct pattern addresses a fundamental challenge in agentic systems: the need for both adaptive planning and auditability. Traditional approaches either generate complete plans before execution (brittle when assumptions change) or execute actions without explicit reasoning (opaque and hard to debug). ReAct provides a middle path where agents reason about each step before taking it, then incorporate new information into subsequent reasoning.

The pattern creates a structured trace that serves multiple purposes: it guides the agent's decision-making process, provides transparency for human oversight, and enables systematic debugging when tasks fail. This makes ReAct particularly valuable for enterprise applications where explainability and reliability are critical requirements. ^[agentic-systems-ref.md]

## Core Components

### Thought Step
The agent explicitly articulates its reasoning about the current situation and what action to take next. This is not just internal processing but a documented reasoning step that becomes part of the permanent trace. The thought step should address: what information is currently available, what the next logical step should be, and why that step serves the overall goal. ^[agentic-systems-ref.md]

### Action Step  
Based on the reasoning in the thought step, the agent executes a specific action. This could be calling a tool, making an API request, or performing any other concrete operation. Actions should be atomic and well-defined, with clear success/failure conditions. ^[agentic-systems-ref.md]

### Observation Step
The agent processes and documents the results of the action. This includes not just the raw output, but the agent's interpretation of what the results mean for the overall task. Observations feed directly into the next thought step, creating the reasoning loop. ^[agentic-systems-ref.md]

## Implementation Example

```
Thought: The advertiser wants to increase reach. I should check current keyword coverage first.
Action: call_analytics(advertiser_id=123, metric="keyword_coverage")
Observation: Coverage is 34% of addressable queries.

Thought: Coverage is low. I should recommend high-relevance keywords from organic queries.
Action: call_keyword_recommender(advertiser_id=123, source="organic_queries", min_relevance=0.8)
Observation: 15 keywords returned with predicted CTR > 2%.

Thought: I have high-confidence recommendations. Present to advertiser with expected impact.
Action: format_recommendation(keywords=..., predicted_impact=...)
```

This structure makes the agent's decision-making process completely transparent while allowing it to adapt based on what it discovers at each step. ^[agentic-systems-ref.md]

## Benefits

### Auditability and Transparency
The explicit reasoning traces created by ReAct serve as documentation for why the agent made specific decisions. When an agent task fails or produces unexpected results, the thought steps provide a clear path for understanding where the reasoning went wrong. This is particularly valuable for compliance and debugging in enterprise environments. ^[agentic-systems-ref.md]

### Adaptive Planning
Unlike plan-then-execute approaches, ReAct allows agents to modify their strategy based on intermediate results. If step 3 reveals information that invalidates the original plan, the agent can adjust course in step 4 rather than continuing with a flawed strategy. ^[agentic-systems-ref.md]

### Error Recovery
The structured loop makes it easier to implement recovery mechanisms. When an action fails, the agent can reason about alternative approaches in the next thought step rather than blindly retrying the same action. ^[agentic-systems-ref.md]

### Human Oversight Integration
The explicit reasoning steps provide natural checkpoints for human review and intervention. Supervisors can examine the agent's reasoning before it takes high-risk actions, or step in when the reasoning appears flawed. ^[agentic-systems-ref.md]

## Trade-offs and Limitations

### Increased Latency
ReAct requires additional LLM calls for the explicit reasoning steps, increasing both latency and cost compared to direct action execution. Each thought step adds 200-500ms and $0.002-$0.008 in LLM costs. ^[agentic-systems-ref.md]

### Token Overhead
The reasoning traces consume significant context window space, which can become problematic for long-running tasks. Agents may need summarization strategies to prevent context overflow. ^[agentic-systems-ref.md]

### Reasoning Quality Dependency
The pattern's effectiveness depends heavily on the quality of the agent's reasoning in the thought steps. Poor reasoning leads to poor actions, regardless of the structural benefits of the pattern. ^[agentic-systems-ref.md]

## When to Use ReAct

ReAct is most appropriate for:

- **High-stakes applications** where explainability is required for compliance or trust
- **Multi-step tasks** where intermediate results may change the optimal strategy  
- **Debugging-intensive environments** where understanding failure modes is critical
- **Human-supervised workflows** where reasoning transparency enables better oversight

ReAct may be unnecessary for:

- **Simple single-step tasks** where the reasoning is obvious
- **High-volume, low-stakes operations** where the cost overhead isn't justified
- **Well-understood workflows** where plan templates are more efficient ^[agentic-systems-ref.md]

## Production Considerations

### Cost Management
The additional LLM calls for reasoning can significantly increase per-task costs. Production implementations often use model routing, sending simple reasoning steps to cheaper models while reserving expensive models for complex synthesis tasks. ^[agentic-systems-ref.md]

### Trace Storage and Analysis
ReAct generates substantial trace data that must be stored, indexed, and made searchable for debugging and analysis. This requires infrastructure for log management and trace replay capabilities. ^[agentic-systems-ref.md]

### Verification Integration
The explicit reasoning steps provide natural points for verification and safety checks. Production systems often validate that the reasoning is consistent with the proposed action before execution. ^[agentic-systems-ref.md]

## Alternative Patterns

ReAct can be compared to other agentic planning approaches:

- **Plan-then-execute**: Generates complete plans upfront but lacks adaptability when assumptions change
- **Direct action**: Executes without explicit reasoning, offering speed but sacrificing transparency
- **Hierarchical planning**: Decomposes complex tasks into sub-goals, balancing lookahead with adaptability ^[agentic-systems-ref.md]

## See Also

- [[Multi-Agent Orchestration]]
- [[Human-in-the-Loop Agent Design]]
- [[trajectory-level-evaluation]]
- [[Prompt Injection via Tool Responses]]
