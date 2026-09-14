---
title: "opentelemetry-agent-tracing"
summary: ""
sources:
  - claude-code/system-architecture-anthropics-claude-code-deepwiki.md
createdAt: 2026-07-30T17:06:29.497663+00:00
updatedAt: 2026-07-30T17:06:29.497663+00:00
---
# OpenTelemetry Agent Tracing

OpenTelemetry Agent Tracing is a distributed tracing mechanism used in multi-agent systems to track and monitor the execution flow across different agent processes. It provides visibility into agent interactions, tool executions, and hierarchical relationships between parent and child agents through structured span data.

## Core Concepts

OpenTelemetry spans serve as the fundamental unit for tracking agent operations. Each span represents a discrete unit of work performed by an agent, such as tool execution or task delegation. The tracing system captures metadata that enables reconstruction of the complete execution flow across distributed agent processes. ^[system-architecture-anthropics-claude-code-deepwiki.md]

In [[Multi-Agent Orchestration]] systems, tracing becomes essential for understanding complex workflows where a main agent delegates specialized work to subagents. The hierarchical nature of these interactions requires careful span management to maintain proper parent-child relationships in the trace data. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Agent Identification and Hierarchy

The tracing system uses specific identifiers to track agent relationships. OpenTelemetry spans for tools include `agent_id` and `parent_agent_id` fields, which ensure that background subagent spans nest correctly under the dispatching Agent tool. This hierarchical structure allows operators to trace the complete execution path from the initial request through all delegated subtasks. ^[system-architecture-anthropics-claude-code-deepwiki.md]

When agents operate in background mode, the tracing system maintains the proper nesting structure even when subagents run as separate processes. This ensures that distributed traces remain coherent and provide accurate visibility into the multi-agent workflow execution. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Integration with Agent Systems

OpenTelemetry tracing integrates seamlessly with [[terminal-native-agent-architecture]] systems that support background execution and session management. The tracing data provides crucial insights for debugging complex agent interactions and understanding performance characteristics across the distributed system. ^[system-architecture-anthropics-claude-code-deepwiki.md]

The system forwards environment variables like `CLAUDE_CODE_SUBAGENT_MODEL` to child processes to maintain consistency in multi-agent sessions, and this configuration propagation is also captured in the tracing metadata for complete observability. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Monitoring and Observability

Background subagents provide completion notifications that include total elapsed duration information, which complements the detailed timing data captured in OpenTelemetry spans. This dual approach to monitoring ensures that both high-level workflow progress and detailed execution metrics are available to system operators. ^[system-architecture-anthropics-claude-code-deepwiki.md]

The tracing system enables comprehensive monitoring of [[agentic-planning-as-search]] workflows, where complex task decomposition and execution patterns benefit from detailed observability into agent decision-making and tool usage patterns. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Tool Execution Tracing

The tracing system captures detailed information about tool executions within the agent workflow. Each tool invocation generates spans that include metadata about the tool type, execution context, and relationship to the parent agent. This granular tracking enables operators to understand how agents interact with external systems and identify performance bottlenecks in tool usage. ^[system-architecture-anthropics-claude-code-deepwiki.md]

When tools are executed by background subagents, the tracing system ensures that these operations are properly attributed to the correct agent hierarchy, maintaining the complete audit trail of distributed agent activities. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Implementation Details

The OpenTelemetry implementation in multi-agent systems requires careful coordination between the main agent process and spawned subagents. The tracing infrastructure must handle process boundaries while preserving span relationships, ensuring that distributed traces accurately reflect the logical flow of work across the agent hierarchy. ^[system-architecture-anthropics-claude-code-deepwiki.md]

Environment variable propagation plays a crucial role in maintaining trace consistency, as configuration parameters like model selection must be preserved across agent boundaries to ensure coherent behavior tracking throughout the distributed execution. ^[system-architecture-anthropics-claude-code-deepwiki.md]
