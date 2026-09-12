---
title: "Sandbox Threat Model Matrix"
summary: "A framework covering five concrete threats that sandbox tiers address: filesystem scope violations, network egress, kernel syscall exposure, cross-tenant leakage, and secret exfiltration."
sources:
  - agent-access-controls/ai-agent-sandboxing-3-isolation-patterns-for-2026.md
createdAt: 2026-06-15T11:34:07.553986+00:00
updatedAt: 2026-06-15T11:34:07.553986+00:00
---
# Sandbox Threat Model Matrix

The **Sandbox Threat Model Matrix** is a framework for evaluating AI agent isolation requirements by mapping specific security threats against available sandboxing technologies. It provides a systematic approach to selecting appropriate isolation tiers based on workload characteristics and risk tolerance, rather than defaulting to either minimal or maximum security measures.

## Overview

The matrix addresses five distinct threat vectors that AI agents can exploit: filesystem access beyond intended scope, network egress to arbitrary domains, exposure of host kernel syscall surfaces, cross-tenant data leakage in multi-tenant environments, and secret exfiltration via environment variables or system files. Each threat vector requires different isolation mechanisms, and no single sandboxing approach addresses all threats equally well. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The framework emerged from production deployments of AI coding agents where traditional security models proved insufficient. Unlike human developers who follow established security practices, AI agents can execute thousands of operations per minute and may be subject to [[prompt-injection-via-tool-responses]] attacks that cause them to act against their original instructions. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Threat Vector Analysis

### Filesystem Threats

Unrestricted filesystem access allows agents to read sensitive files like `.env` configurations, SSH keys, or credentials stored in `~/.ssh/id_rsa`. Agents can also modify source files in parent directories or system configuration files. [[Claude Code]] restricts writes to the project directory by default, but this represents policy enforcement rather than OS-level isolation. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Network Egress Threats

Agents capable of making arbitrary HTTP requests can exfiltrate data to external servers, receive instructions from remote attackers, or call unauthorized APIs. Some systems like [[Claude Code]] implement command blocklists that prevent `curl` and `wget` execution, while [[native-sandboxing]] approaches use network namespace isolation for stronger guarantees. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Kernel Surface Exposure

Docker containers share the host kernel, meaning a container escape vulnerability could expose the entire host system. Technologies like [[gVisor]] interpose a user-space kernel to prevent agent code from directly accessing host kernel syscalls, while [[Firecracker]] microVMs provide dedicated kernels per sandbox instance. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Multi-Tenant Data Leakage

In multi-tenant platforms where multiple users' agents run on shared infrastructure, namespace isolation becomes critical. Container-based solutions rely on kernel-level namespace separation, which may be insufficient for compliance-sensitive environments. MicroVMs represent the industry standard for addressing this threat class. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Prompt Injection Limitations

The matrix acknowledges that no sandboxing tier prevents compromised system prompts. If an attacker successfully injects malicious instructions into an agent's context window through poisoned code comments, malicious file reads, or adversarial tool responses, the agent will execute those instructions within whatever permissions the sandbox allows. Sandboxing reduces impact radius but does not prevent the injection itself. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Isolation Tier Classification

### OS Process Sandbox

The lightest isolation tier uses operating system process restrictions like Apple's Seatbelt on macOS or bubblewrap on Linux. [[Claude Code]] 1.3 implements this approach for its Sandboxed Bash tool, though file operations and MCP servers run with full process permissions unless the optional sandbox runtime is enabled. This tier provides configurable filesystem allowlists and partial network blocking but offers no protection against kernel exploits. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### User-Space Kernel (gVisor)

[[gVisor]] implements a user-space kernel written in Go that intercepts syscalls before they reach the host kernel. The Sentry component re-implements Linux-compatible syscalls while dramatically reducing the attack surface exposed to host kernel vulnerabilities. This approach provides security benefits approaching VMs while maintaining lower resource overhead and faster startup times than full virtualization. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Firecracker MicroVMs

[[Firecracker]] microVMs provide dedicated Linux kernels per sandbox instance using AWS's open-source virtual machine monitor. Each microVM operates with hardware-enforced isolation and excludes unnecessary virtual devices to minimize attack surface. [[Vercel]] Sandbox and [[E2B]] both use Firecracker-based infrastructure for production AI agent workloads, with sub-second provisioning times. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Development Containers

[[Dev containers]] using the `devcontainer.json` specification provide reproducible containerized environments but share the same kernel isolation limitations as standard Docker containers. They offer strong repeatability and easy reset semantics but are inappropriate for multi-tenant use cases or execution of arbitrary user-supplied code without additional hardening. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

### Full Virtual Machines

Hardware-virtualized VMs represent maximum isolation with dedicated kernels, virtual hardware, and hypervisor-enforced memory boundaries. While providing the strongest compliance story for regulated industries, full VMs typically require 30+ seconds to provision, making them unsuitable for per-request agent sandboxing. The emerging pattern uses full VMs as outer boundaries with microVMs for per-request execution. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Decision Framework

The matrix provides guidance for matching isolation tiers to specific workload profiles. For trusted in-house agents running known codebases, OS process sandboxes provide appropriate protection with minimal operational overhead. Multi-user platforms or agents executing AI-generated code require Firecracker microVMs as the 2026 baseline standard. Compliance-driven environments in regulated sectors typically need full VM outer boundaries with microVM inner execution and structured audit logging. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

High-performance multi-tenant environments with kernel-escape risks often select [[gVisor]] as a pragmatic middle ground, offering stronger isolation than containers with faster provisioning than microVMs. The framework emphasizes that isolation tiers are tools for different jobs rather than a simple progression from inadequate to excessive security. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Implementation Examples

[[Codex CLI]] implements a three-mode sandbox system: read-only mode for audit tasks, workspace-write mode as the recommended default, and danger-full-access mode intended only for use within already-isolated environments. [[Cursor]] cloud agents use isolated VM worktrees where each agent task receives its own contained environment that can be independently discarded or merged. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The matrix framework has influenced production architectures where teams building AI-powered applications integrate sandbox selection into initial system design rather than retrofitting isolation later. This approach proves particularly important for multi-tenant SaaS platforms where kernel-sharing risks are most acute. ^[ai-agent-sandboxing-isolation-patterns-2026.md]
