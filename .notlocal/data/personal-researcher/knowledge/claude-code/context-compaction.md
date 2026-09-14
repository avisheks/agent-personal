---
title: "context-compaction"
summary: ""
sources:
  - claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md
createdAt: 2026-07-30T16:59:50.802238+00:00
updatedAt: 2026-07-30T16:59:50.802238+00:00
---
# Context Compaction

Context compaction is an automatic memory management mechanism in [[Claude Code]] that summarizes older conversation turns when the context window approaches capacity limits. This process helps maintain system performance while preserving recent conversational context, though it can impact the quality of long-running sessions. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Overview

Context compaction addresses the fundamental constraint of [[Large Context Window]] systems operating within fixed token budgets. When a conversation accumulates sufficient history—including tool results, file contents, and previous exchanges—the system must choose between truncating content or summarizing it to make room for new interactions. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

The mechanism operates as part of Claude Code's broader [[Context Window Evolution]] strategy, where the system dynamically manages approximately 200,000 tokens distributed across system prompts, conversation history, tool results, and response buffers. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Technical Implementation

### Automatic Triggering Thresholds

Context compaction triggers automatically when token usage exceeds specific thresholds, though the exact values vary by implementation:

- **VS Code extension**: ~75% usage (25% remaining capacity)
- **CLI version**: 1-5% remaining (more conservative approach)
- **Historical observations**: 92-95% in community analysis

The system provides a manual override through the `/compact` command, allowing users to trigger summarization at logical breakpoints rather than waiting for automatic activation. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Compaction Process

When triggered, the system performs several operations:

1. **Summarization**: Older conversation turns are condensed into brief summaries
2. **Tool result compression**: Large outputs from previous [[Bash]] commands or file reads are abbreviated
3. **Context preservation**: Recent interactions remain in full detail
4. **Signal injection**: The model receives notification that context was compacted

This process maintains conversational continuity while freeing tokens for new interactions. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Performance Impact

Research and practitioner observations document significant quality degradation following context compaction:

### Measured Degradation

- **LLM performance drops 50-70%** on complex tasks as context grows from 1K to 32K tokens
- **11 out of 12 models fall below 50%** of their short-context performance at 32K tokens
- **Auto-compaction loses nuance** and breaks references through repeated compression cycles

The degradation stems from the [[Transformer Architecture]]'s attention mechanism struggling with retrieval burden in high-context scenarios, compounded by information loss during summarization. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Context Rot Phenomenon

Extended conversations experience "context rot" where the model gradually loses track of earlier constraints and requirements. This manifests as:

- **Conversation turns**: Effectiveness degrades after 15-25 turns
- **Token accumulation**: Quality drops significantly beyond 80-100K tokens  
- **Scope limitations**: Success rates fall when managing more than 5 files simultaneously

Success rates by scope demonstrate this pattern clearly: 1-3 files achieve ~85% success, 4-7 files drop to ~60%, and 8+ files fall to ~40%. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Mitigation Strategies

### Proactive Management

The community consensus favors manual intervention over automatic compaction:

| Context Usage | Recommended Action | Rationale |
|---------------|-------------------|-----------|
| 70% | Warning - Plan cleanup | Early awareness |
| 85% | Manual handoff recommended | Prevent auto-compact degradation |
| 95% | Force handoff | Severe quality degradation |

### Alternative Approaches

Several strategies can reduce reliance on context compaction:

- **[[Sub-Agent Architecture]]**: Use the `Task` tool for exploratory work with isolated context
- **Session handoffs**: Start fresh sessions for new major tasks using `/clear`
- **Targeted reads**: Access specific files rather than broad directory exploration
- **[[CLAUDE.md Configuration File]]**: Store persistent project context in memory files

### Error Recovery Patterns

A distinct degradation mode occurs through repeated tool failures, where error output accumulates and dilutes the original task intent. The solution involves re-injecting core task instructions after each failure, maintaining signal-to-noise ratio even within bounded context windows. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Relationship to Long-Context Scaling

Context compaction represents a practical compromise in [[Long-Context Scaling]] challenges. While models theoretically support large context windows, the [[LLM Hallucination]] and attention degradation problems make aggressive summarization necessary for maintaining usable performance.

The mechanism reflects broader tensions in [[Memory-Centric Agentic AI]] systems between comprehensive context retention and computational efficiency. As [[Inference-Time Compute Scaling]] techniques evolve, the balance between context preservation and processing speed continues to shift.

## See Also

- [[Session Persistence and Management]] - Related session handling mechanisms
- [[Multi-Agent Orchestration Architecture]] - Alternative approaches to context management
- [[Long-Horizon Context Management]] - Strategies for extended interactions
- [[Hierarchical Memory Architecture]] - Structured approaches to information retention
