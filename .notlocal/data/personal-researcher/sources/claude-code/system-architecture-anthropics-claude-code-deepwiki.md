---
title: "System Architecture | anthropics/claude-code | DeepWiki"
source: "https://deepwiki.com/anthropics/claude-code/1.1-system-architecture"
ingestedAt: "2026-05-28T19:34:13Z"
---
# System Architecture

Relevant source files

This document provides a technical overview of Claude Code's high-level architecture, covering the core agent system, session management, tool execution engine, and the extensible plugin/MCP ecosystem. It describes how the system bridges natural language commands to codebase operations through a modular, agentic framework.

## Overview

Claude Code is an agentic coding tool built around a hierarchical configuration system, a robust tool execution engine with built-in permissions, and a multi-agent orchestration layer.

The system serves two primary environments:

  1. **Interactive CLI** : A terminal application (`claude`) providing an AI coding assistant with session persistence and tool execution [README.md7-11](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L7-L11) [README.md46](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L46-L46)
  2. **GitHub Automation** : Workflows that use Claude as an engine for issue triage, duplicate detection, and lifecycle management via GitHub Actions [README.md7-8](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L7-L8)



## Core Architecture

The following diagram illustrates the primary components and their relationships, mapping the user's natural language space to the internal code entities.

### System Components & Data Flow


**Sources:** [CHANGELOG.md3-70](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L3-L70) [README.md7-11](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L7-L11)

## Entry Point and CLI Layer

The primary entry point is the `claude` command. It handles argument parsing, environment variable processing, and routing to subcommands or the interactive agent session.

Command| Purpose  
---|---  
`claude`| Start interactive session in current directory [README.md46](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L46-L46)  
`claude agents`| List live Claude sessions as JSON or terminal list; shows awaiting-input count in tab titles [CHANGELOG.md24](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L24-L24) [CHANGELOG.md41](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L41-L41)  
`claude --bg`| Run as a background service; supports `/resume` with a `bg` marker [CHANGELOG.md47](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L47-L47) [CHANGELOG.md56](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L56-L56)  
`claude plugin validate`| Validates plugin structure; flags `skills:` pointing at files instead of directories [CHANGELOG.md41](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L41-L41)  
`claude mcp list`| Shows configuration errors if `.mcp.json` is unparseable [CHANGELOG.md71](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L71-L71)  
  
**Sources:** [README.md13-46](https://github.com/anthropics/claude-code/blob/1573399b/README.md?plain=1#L13-L46) [CHANGELOG.md24-71](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L24-L71)

## Session Management

Sessions persist conversation history and metadata. Each session is stored in `~/.claude/sessions/`.

  * **Resuming Sessions** : The `/resume` command supports both interactive and background (`bg`) sessions [CHANGELOG.md47](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L47-L47) Resumed sessions retain their specific model choice [CHANGELOG.md62](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L62-L62)
  * **Backgrounding** : Sessions can be started in the background via `claude --bg`. On macOS, these sessions handle Full Disk Access protection gracefully [CHANGELOG.md56](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L56-L56)
  * **Persistence & Metadata**: Session titles are generated from the user's first prompt [CHANGELOG.md68](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L68-L68)
  * **Security Policies** : Managed settings like `forceLoginOrgUUID` and `forceLoginMethod` are enforced across all session types, including third-party API key sessions [CHANGELOG.md16](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L16-L16)



**Sources:** [CHANGELOG.md16-68](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L16-L68)

## Agent Orchestration

Claude Code uses a multi-agent architecture where a "Main Agent" can delegate specialized work to "Subagents" via the `Task` tool.

### Subagents and Monitoring

  * **Tracing** : OpenTelemetry spans for tools include `agent_id` and `parent_agent_id`, ensuring background subagent spans nest correctly under the dispatching Agent tool [CHANGELOG.md25](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L25-L25)
  * **Environment Forwarding** : `CLAUDE_CODE_SUBAGENT_MODEL` is forwarded to child processes to maintain model consistency in multi-agent sessions [CHANGELOG.md18](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L18-L18)
  * **Notifications** : Background subagents provide completion notifications including the total elapsed duration (e.g., "3h 2m 5s") [CHANGELOG.md48](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L48-L48)



**Sources:** [CHANGELOG.md18-48](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L18-L48)

Tools are the primary way agents interact with the filesystem and shell.

  * **PowerShell Support** : Fixed Windows PowerShell tool failures when `pwsh` is installed via winget or Microsoft Store [CHANGELOG.md7](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L7-L7)
  * **Read Tool Optimization** : When a file exceeds the token limit, the Read tool returns a truncated first page with a "PARTIAL view" notice instead of a hard error [CHANGELOG.md43](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L43-L43)
  * **Permission Security** : Fixed a bypass where bare variable assignments in Bash commands were auto-approved even for non-allowlisted environment variables [CHANGELOG.md31](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L31-L31)
  * **Search Robustness** : `head`/`tail` commands now satisfy the "read-before-edit" check, and exit code 1 from grep-like tools is no longer treated as a command failure [CHANGELOG.md58](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L58-L58)



**Sources:** [CHANGELOG.md7-58](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L7-L58)

## Extension Mechanisms

### Plugin System

Plugins extend functionality with custom commands, agents, and hooks.

  * **Discovery** : The `/plugin` Discover and Browse screens display a plugin's commands, agents, skills, hooks, and MCP/LSP servers prior to installation [CHANGELOG.md27](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L27-L27)
  * **Hooks** : `Stop` and `SubagentStop` hooks receive detailed input including `background_tasks` and `session_crons` [CHANGELOG.md30](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L30-L30)
  * **Skill Loading** : Skills are loaded from directories. Loading now ignores non-`.md` files to prevent file descriptor exhaustion during builds [CHANGELOG.md67](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L67-L67)



### MCP (Model Context Protocol)

  * **Pagination** : Fixed issues where `resources/list`, `prompts/list`, and `tools/list` dropped items past the first page on paginating servers [CHANGELOG.md8](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L8-L8) [CHANGELOG.md65](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L65-L65)
  * **Error Handling** : Improved validation errors for MCP prompt slash commands; errors now explicitly name missing arguments and show expected usage [CHANGELOG.md32](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L32-L32)
  * **Media Handling** : MCP images with unsupported MIME types (like SVG) are saved to disk and referenced in tool results to prevent breaking the conversation [CHANGELOG.md66](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L66-L66)



**Sources:** [CHANGELOG.md8-67](https://github.com/anthropics/claude-code/blob/1573399b/CHANGELOG.md?plain=1#L8-L67)