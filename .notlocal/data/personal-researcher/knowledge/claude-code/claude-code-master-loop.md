---
title: "claude-code-master-loop"
summary: ""
sources:
  - claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md
createdAt: 2026-07-30T16:58:50.718656+00:00
updatedAt: 2026-07-30T16:58:50.718656+00:00
---
# Claude Code Master Loop

The **Claude Code Master Loop** is the core architectural pattern underlying Claude Code's agentic behavior. It represents a simplified approach to AI agent orchestration that relies on a single `while` loop rather than complex routing systems or task planners. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Overview

Claude Code operates on a fundamentally simple principle: the AI model itself decides when to call tools, which tools to call, and when a task is complete. This approach contrasts sharply with traditional agent architectures that employ intent classifiers, task routers, or directed acyclic graph (DAG) orchestrators. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

The master loop can be expressed in pseudocode as:
```
while (claude_response.has_tool_call):
    result = execute_tool(tool_call)
    claude_response = send_to_claude(result)
return claude_response.text
```

## Architecture Components

### Stop Reason Control Flow

The [[Anthropic API]] exposes the loop through concrete `stop_reason` values that determine the next action:

| `stop_reason` | Meaning | Loop Action |
|---------------|---------|-------------|
| `tool_use` | Claude wants to call one or more tools | Execute tools, feed results back, continue loop |
| `end_turn` | Claude decided it has finished | Exit loop, return the text response |
| `max_tokens` | Context limit reached before finishing | Rethink context strategy, likely need summarization |

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Tool Arsenal Integration

The master loop operates with Claude Code's eight core tools:
- **Bash**: Universal adapter for shell commands
- **Read**: File content retrieval
- **Edit**: Diff-based file modification  
- **Write**: File creation/overwriting
- **Grep**: Regex-based content search
- **Glob**: File pattern matching
- **Task**: [[Multi-Agent Orchestration]] via sub-agents
- **TodoWrite**: Structured task management

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Context Management

### Token Budget Allocation

The master loop operates within a fixed [[Context Window Evolution]] of approximately 200K tokens, distributed across:

- System Prompt: ~5-15K tokens
- [[CLAUDE.md Configuration File]]: ~1-10K tokens  
- Conversation History: Variable
- Tool Results: Variable
- Reserved for Response: ~40-45K tokens

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Auto-Compaction Behavior

When context usage exceeds threshold levels (typically 75-92% capacity), Claude Code automatically summarizes older conversation turns to preserve recent context. This process can degrade performance quality by 50-70% on complex tasks, making manual context management preferable. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Sub-Agent Architecture

The [[Task]] tool enables the master loop to spawn isolated sub-agents with their own context windows. Key constraints include:

- **Depth Limitation**: Sub-agents cannot spawn additional sub-agents (depth=1)
- **Context Isolation**: Sub-agents receive only task descriptions, not full conversation history
- **Summary Return**: Only text summaries from sub-agents enter the main context

This design prevents recursive explosion while enabling parallel exploration and specialized analysis tasks. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Design Philosophy

### Less Scaffolding, More Model

The master loop embodies Claude Code's core philosophy of "less scaffolding, more model" - trusting Claude's reasoning capabilities rather than building complex orchestration systems. This approach offers several advantages:

- **Simplicity**: Fewer components reduce failure modes
- **Model-driven**: Claude's reasoning surpasses hand-coded heuristics  
- **Flexibility**: No rigid pipeline constraints
- **Debuggability**: Single point of failure analysis

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Performance Characteristics

The master loop's effectiveness degrades under certain conditions:

| Condition | Threshold | Symptom |
|-----------|-----------|---------|
| Conversation turns | 15-25 turns | Loses track of earlier constraints |
| Token accumulation | 80-100K tokens | Ignores early requirements |
| Problem scope | >5 files simultaneously | Inconsistent changes, missed files |

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Advanced Features

### MCP Integration

The master loop seamlessly integrates with [[Model Context Protocol (MCP)]] servers through lazy loading via Tool Search functionality. This prevents context pollution from large tool definition sets while maintaining access to extended capabilities. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Permission System

The loop operates within a layered [[Permission Gating System]]:
1. Interactive prompts for dangerous commands
2. Allow/deny rules in configuration
3. Pre/post execution hooks
4. Optional sandbox isolation

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Comparison with Alternatives

Unlike traditional agent architectures that employ:
- Intent classifiers → routers → specialists
- RAG with embeddings for search
- Complex state machines
- Tool-specific planners

The Claude Code Master Loop relies entirely on the model's native reasoning to make routing decisions, representing a paradigm shift toward model-centric rather than framework-centric agent design. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]
