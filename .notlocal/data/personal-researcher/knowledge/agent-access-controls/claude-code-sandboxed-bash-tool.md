---
title: "Claude Code Sandboxed Bash Tool"
summary: "Anthropic's isolation feature in Claude Code 1.3 that uses OS-level sandboxing to isolate bash commands while file tools and MCP servers run with full process permissions."
sources:
  - agent-access-controls/ai-agent-sandboxing-3-isolation-patterns-for-2026.md
createdAt: 2026-06-15T11:32:54.810747+00:00
updatedAt: 2026-06-15T11:32:54.810747+00:00
---
# Claude Code Sandboxed Bash Tool

The **Claude Code Sandboxed Bash Tool** is a security feature introduced in [[Claude Code]] 1.3 that provides process-level isolation for bash commands executed by AI agents. The tool uses operating system-level sandboxing to restrict what spawned subprocesses can do, without creating separate OS or kernel boundaries. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Architecture

The Sandboxed Bash tool implements different isolation mechanisms depending on the operating system. On macOS, it uses Apple's Seatbelt framework through the `sandbox-exec` subsystem. On Linux and WSL2, it employs bubblewrap (`bwrap`), a user-namespace tool that provides process-level containment. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The tool operates at the OS process sandbox tier, which is the lightest-weight isolation approach available. This tier restricts subprocess capabilities through configurable allowlists for filesystem paths and network access controls, while maintaining minimal performance overhead with approximately zero milliseconds of startup time. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Scope and Limitations

### Coverage

The Sandboxed Bash tool specifically isolates bash commands and their child processes. This covers the most common [[AI Coding Agent]] action of running shell commands within a controlled environment. The scope is intentionally narrow and focused on command execution isolation. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### What Is Not Sandboxed

The tool does not sandbox other [[Claude Code]] components including file tools (Read, Write, Edit), [[Model Context Protocol (MCP)]] servers, or hooks. These components run with the full permissions of the Claude Code process itself unless additional isolation measures are implemented. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Additional Isolation Options

### Sandbox Runtime Beta

Anthropic provides an opt-in `@anthropic-ai/sandbox-runtime` package that extends sandboxing to the entire Claude Code process. This beta feature wraps file tools, MCP servers, and hooks in addition to bash commands. The runtime is configured through `~/.srt-settings.json` with filesystem and network allowlists, but must be explicitly enabled by users. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Web-Based Claude Code

[[Claude Code]] on the web uses a different isolation approach entirely, employing Anthropic-managed VMs with default-deny networking, branch-restricted git push, secure-proxy GitHub tokens, full audit logging, and automatic VM teardown after each session. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Threat Coverage

The Sandboxed Bash tool provides protection against specific threat vectors while having notable limitations:

### Protected Against
- Filesystem scope violations through configurable allowlists for read/write paths
- Partial network egress blocking via deny-list for specific commands
- Accidental filesystem and network damage during command execution

### Not Protected Against
- Kernel exploits, as both Seatbelt and bubblewrap run in the same kernel as the host process
- [[Prompt Injection]] attacks that compromise the system prompt
- Cross-tenant data leakage in multi-tenant environments
- Sophisticated network-based data exfiltration

^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Use Cases

The OS process sandbox tier is appropriate for trusted in-house agents running on known codebases where the agent executes code written by the development team. For agents executing user-supplied or AI-generated code from untrusted sources, stronger isolation tiers such as [[Firecracker]] microVMs are required. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Comparison with Other Tools

The Sandboxed Bash tool represents one approach among several isolation strategies used by AI coding tools. [[Cursor]] cloud agents use isolated VMs rather than process-level sandboxes, while [[Codex CLI]] offers three sandbox modes ranging from read-only to full access. The choice between these approaches depends on the specific threat model and operational requirements of the deployment. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Security Considerations

While the Sandboxed Bash tool provides meaningful protection for many use cases, it operates within the limitations of process-level sandboxing. Teams requiring stronger isolation guarantees, particularly for multi-tenant environments or when executing untrusted code, should consider higher isolation tiers such as [[gVisor]] or microVM-based solutions. ^[ai-agent-sandboxing-isolation-patterns-2026.md]
