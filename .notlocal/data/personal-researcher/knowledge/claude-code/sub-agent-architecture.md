---
title: "sub-agent-architecture"
summary: ""
sources:
  - claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md
createdAt: 2026-07-30T17:00:12.187142+00:00
updatedAt: 2026-07-30T17:00:12.187142+00:00
---
# Sub-Agent Architecture

Sub-Agent Architecture is a design pattern in [[claude-code-agentic-system]] where a primary agent spawns isolated secondary agents to handle specific tasks or exploration work. This architecture enables parallel processing, context isolation, and specialized task handling while maintaining clear boundaries and preventing recursive complexity.

## Core Architecture

Sub-Agent Architecture operates on a hub-and-spoke model where one coordinator agent manages multiple worker sub-agents. The coordinator holds the complete context and orchestrates task distribution, while sub-agents operate in isolation with their own fresh context windows. Each sub-agent receives only the specific task description and returns a text summary to the coordinator. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

The architecture enforces a strict depth limit of one level - sub-agents cannot spawn additional sub-agents, preventing recursive explosion and maintaining predictable resource consumption. This "depth=1" constraint prevents agent-ception scenarios that would consume infinite resources and create debugging nightmares. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Implementation in Claude Code

In [[claude-code-agentic-system]], sub-agents are created using the `Task` tool, which spawns isolated agents with their own context windows. The spawned sub-agent has access to the same tool arsenal as the parent (except the Task tool itself) but operates independently. Only the final summary text from the sub-agent enters the main context, keeping the coordinator's context clean. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

Claude Code offers specialized sub-agent types through the `subagent_type` parameter:

- **Explore**: Codebase exploration with read-only tools
- **Plan**: Architecture planning with all tools except Edit/Write  
- **Bash**: Command execution with Bash tool only
- **general-purpose**: Complex multi-step tasks with all available tools

^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Context Isolation Principles

The critical architectural principle is that context is never inherited automatically between agents. When a coordinator spawns a sub-agent to analyze a specific file, other sub-agents receive no knowledge of that analysis unless the coordinator explicitly passes the information in their task descriptions. This isolation is by design and prevents context pollution between parallel tasks. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

Sub-agents receive only the task string provided to them - they have no access to the coordinator's conversation history, previous tool results, or findings from other sub-agents. This requires explicit context passing patterns where the coordinator must include all necessary information in each sub-agent's task description. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Multi-Agent Orchestration Patterns

The dominant pattern in production systems is hub-and-spoke orchestration, where the coordinator agent sits at the center and manages N worker sub-agents. The coordinator is the only entity that holds the full picture and makes cross-cutting decisions. Workers should never need to communicate with each other - if they do, that indicates incorrect task decomposition. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

Coordinator responsibilities include:
- **Decomposition**: Breaking goals into independent subtasks with clear boundaries
- **Explicit context passing**: Ensuring each worker task description is self-contained  
- **Aggregation**: Collecting and combining text results from all workers
- **Cross-cutting decisions**: Making decisions that span multiple worker outputs

^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Use Cases and Benefits

Sub-Agent Architecture provides several key advantages:

- **Context preservation**: Keeps the main agent's context clean during exploratory tasks
- **Parallel exploration**: Enables simultaneous searches across different areas
- **Error isolation**: Prevents errors in one exploration from polluting the main context
- **Specialized analysis**: Allows different "mindsets" for different task types

^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

Common use cases include searching large codebases, parallel exploration of different system components, risky exploration that might generate errors, and specialized analysis requiring focused attention on specific domains. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Architectural Constraints

Sub-Agent Architecture enforces several important constraints to maintain system stability:

1. **Single-level depth**: Sub-agents cannot spawn additional sub-agents
2. **Context isolation**: No automatic context sharing between agents
3. **Text-only communication**: Sub-agents return only summary text, not full context
4. **Resource boundaries**: Each sub-agent operates within its own token budget

^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

These constraints prevent recursive explosion, unpredictable costs, context pollution across levels, and debugging complexity that would arise from multi-level agent chains. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

## Best Practices

### Explicit Context Passing

The most common mistake in multi-agent design is assuming sub-agents share context. Coordinators must explicitly pass all necessary information in task descriptions:

```
# Wrong - Worker B won't know about Worker A's findings
task_a = Task("Analyze auth.py and find the session token logic")
task_b = Task("Find all callers of the session token logic")

# Correct - coordinator passes findings explicitly  
result_a = run_task("Analyze auth.py and return the exact function name(s) handling session tokens")
task_b = Task(f"Find all callers of {result_a} across the codebase")
```

^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]

### Task Decomposition

Effective sub-agent usage requires breaking goals into independent subtasks with clear boundaries. Each sub-agent should have a well-defined scope that doesn't require coordination with other sub-agents during execution. ^[claude-code-how-claude-code-works-architecture-internals-claude-code-guide.md]
