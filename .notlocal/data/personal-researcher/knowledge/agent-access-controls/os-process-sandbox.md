---
title: "OS Process Sandbox"
summary: "Lightweight isolation using Apple's Seatbelt on macOS and bubblewrap on Linux to restrict subprocess capabilities without creating separate OS or kernel boundaries."
sources:
  - agent-access-controls/ai-agent-sandboxing-3-isolation-patterns-for-2026.md
createdAt: 2026-06-15T11:32:37.449530+00:00
updatedAt: 2026-06-15T11:32:37.449530+00:00
---
# OS Process Sandbox

An **OS Process Sandbox** is a lightweight isolation mechanism that restricts what a spawned subprocess can do without creating a separate operating system or kernel boundary. This approach operates at the process level, using operating system facilities to constrain filesystem access, network operations, and system calls for individual processes and their children. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

OS process sandboxes represent the baseline tier in the five-tier isolation hierarchy for AI agent systems, providing meaningful protection against accidental damage while maintaining minimal operational overhead. They are particularly well-suited for trusted in-house agents running known codebases on developer machines. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Implementation Approaches

### Seatbelt (macOS)

Apple's Seatbelt framework, implemented via the `sandbox-exec` subsystem, provides process-level sandboxing on macOS systems. This system allows fine-grained control over what resources a process can access, including filesystem paths, network endpoints, and system services. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Bubblewrap (Linux)

Bubblewrap (`bwrap`) is a user-namespace tool available on Linux and WSL2 that creates sandboxed environments for processes. It leverages Linux namespaces and seccomp to restrict process capabilities without requiring root privileges or kernel modifications. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Claude Code Integration

[[Claude Code]] 1.3 ships with OS process sandbox capabilities through its Sandboxed Bash tool. This tool uses Seatbelt on macOS and bubblewrap on Linux/WSL2 to isolate bash commands and their child processes. The scope is intentionally narrow - the Sandboxed Bash tool does not sandbox file tools (Read, Write, Edit), [[Model Context Protocol (MCP)]] servers, or hooks, which run with the full permissions of the Claude Code process itself. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

Anthropic also provides an opt-in `@anthropic-ai/sandbox-runtime` package that wraps the entire Claude Code process in Seatbelt or bubblewrap. This is configured via `~/.srt-settings.json` with filesystem and network allowlists, but is not enabled by default. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Threat Coverage

OS process sandboxes provide protection against several categories of threats:

### Filesystem Scope Violations
Configurable allowlists can restrict read and write operations to specific filesystem paths, preventing agents from accessing sensitive files like `.env` files, SSH keys, or system directories outside the intended project scope. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Network Egress Control
Partial network egress blocking through deny-lists can prevent specific commands like `curl` and `wget` from making unauthorized outbound connections. However, this protection is policy-based rather than comprehensive network isolation. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Limitations
OS process sandboxes do not provide meaningful protection against kernel exploits, as both Seatbelt and bubblewrap run in the same kernel as the host process. They also cannot prevent data exfiltration through network egress in sandboxes that permit outbound connections, and they do not protect against compromised system prompts or prompt injection attacks. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Use Cases

OS process sandboxes are appropriate for trusted environments where the agent executes code written by known teams on trusted machines. They provide a balance between security and operational simplicity, with negligible startup overhead since they wrap existing processes rather than creating new virtual environments. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

For agents executing user-supplied code, AI-generated code, or operating in multi-tenant environments, stronger isolation tiers such as [[native-sandboxing]] with microVMs or container-based solutions are required. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Comparison with Other Isolation Tiers

OS process sandboxes sit at the baseline of the isolation hierarchy, below container-based solutions, user-space kernels like gVisor, and microVM approaches. While they offer the fastest startup times and lowest resource overhead, they provide the most limited threat protection compared to kernel-level or hardware-level isolation mechanisms. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The choice of isolation tier should match the specific threat model and operational constraints of the deployment, with OS process sandboxes serving as the appropriate choice for low-risk, trusted environments where operational simplicity is prioritized. ^[ai-agent-sandboxing-isolation-patterns-2026.md]
