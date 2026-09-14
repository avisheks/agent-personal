---
title: "session-persistence-and-management"
summary: ""
sources:
  - claude-code/system-architecture-anthropics-claude-code-deepwiki.md
createdAt: 2026-07-30T17:05:33.752093+00:00
updatedAt: 2026-07-30T17:05:33.752093+00:00
---
# Session Persistence and Management

Session Persistence and Management refers to the system's ability to maintain conversation state, metadata, and context across multiple interactions in Claude Code. This enables users to pause, resume, and manage long-running coding sessions while preserving the full conversation history and agent state.

## Core Session Architecture

Sessions in Claude Code are stored as persistent files in the `~/.claude/sessions/` directory. Each session maintains conversation history, metadata, and configuration state that allows for seamless resumption of work. Session titles are automatically generated from the user's first prompt to provide meaningful identification. ^[system-architecture-anthropics-claude-code-deepwiki.md]

The system supports multiple session types including interactive CLI sessions and background service sessions. Sessions can be started in the background via `claude --bg`, which is particularly useful for long-running tasks that don't require immediate user interaction. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Session Management Commands

The CLI provides several commands for session management and monitoring:

- `claude agents` - Lists all live Claude sessions in JSON or terminal format, displaying awaiting-input counts in tab titles for easy monitoring
- `claude --bg` - Runs sessions as background services with support for later resumption
- `/resume` - Resumes both interactive and background sessions, with special `bg` markers for background sessions

^[system-architecture-anthropics-claude-code-deepwiki.md]

## Session Resumption and Continuity

When resuming sessions, the system preserves critical configuration including the specific model choice that was used in the original session. This ensures consistency in agent behavior and capabilities across session boundaries. The `/resume` command supports both interactive sessions and background sessions marked with `bg` identifiers. ^[system-architecture-anthropics-claude-code-deepwiki.md]

Background sessions provide completion notifications that include detailed timing information, such as total elapsed duration displayed in formats like "3h 2m 5s". This helps users track the progress of long-running tasks even when not actively monitoring the session. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Multi-Agent Session Management

In [[multi-agent-decomposition]] scenarios, session management becomes more complex as the system must coordinate state across multiple agent instances. The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable is forwarded to child processes to maintain model consistency across all agents in a multi-agent session. ^[system-architecture-anthropics-claude-code-deepwiki.md]

[[Agent State Space Explosion]] can occur when managing multiple concurrent sessions, requiring careful resource management and state isolation between different session contexts.

## Security and Access Control

Session management integrates with the [[permission-gating-system]] to enforce security policies across all session types. Managed settings like `forceLoginOrgUUID` and `forceLoginMethod` are enforced consistently, even in sessions using third-party API keys. This ensures that organizational security policies remain in effect regardless of how sessions are initiated or resumed. ^[system-architecture-anthropics-claude-code-deepwiki.md]

On macOS systems, background sessions handle Full Disk Access protection gracefully, ensuring that security restrictions don't interfere with session persistence and resumption capabilities. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Integration with Tool Execution

Session persistence works closely with the [[tool-execution-engine-with-permissions]] to maintain context about previous operations. The system tracks tool usage patterns and maintains state that enables features like "read-before-edit" checks across session boundaries. This integration ensures that [[supervisory-software-engineering]] workflows can span multiple sessions without losing important context about codebase state and previous modifications. ^[system-architecture-anthropics-claude-code-deepwiki.md]

## Tracing and Monitoring

The system provides comprehensive observability for session management through [[opentelemetry-agent-tracing]]. OpenTelemetry spans for tools include `agent_id` and `parent_agent_id` attributes, ensuring that background subagent spans nest correctly under the dispatching Agent tool. This enables detailed monitoring of multi-agent workflows across session boundaries. ^[system-architecture-anthropics-claude-code-deepwiki.md]
