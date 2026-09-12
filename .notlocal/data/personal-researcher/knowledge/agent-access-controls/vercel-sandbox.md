---
title: "Vercel Sandbox"
summary: "A GA compute primitive designed to safely run untrusted code using Firecracker microVMs on Amazon Linux 2023 with Node.js and Python runtimes pre-installed."
sources:
  - agent-access-controls/ai-agent-sandboxing-3-isolation-patterns-for-2026.md
createdAt: 2026-06-15T11:33:14.565110+00:00
updatedAt: 2026-06-15T11:33:14.565110+00:00
---
# Vercel Sandbox

Vercel Sandbox is a compute primitive designed to safely run untrusted or user-generated code on Vercel's platform, supporting dynamic, real-time workloads for AI agents, code generation, and developer experimentation. Each sandbox runs in its own Firecracker microVM on Amazon Linux 2023 with Node.js and Python runtimes pre-installed. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Architecture

Vercel Sandbox uses [[Firecracker microVMs]] as its underlying isolation technology. Unlike Docker containers, each sandbox runs in its own Firecracker microVM with a dedicated kernel, providing stronger isolation than container-based solutions which makes sandboxes ideal for running untrusted code. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The platform excludes unnecessary virtual devices — no USB, no GPU pass-through, no PCI hot-plug — to reduce both memory footprint and attack surface. Each microVM gets a dedicated Linux kernel, which is the key distinction from Docker containers that share the host kernel. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Runtime Environment

Vercel Sandbox comes with pre-installed runtimes including Node.js (node26, node24, node22) and Python 3.13. The default timeout is 5 minutes, and persistent sandboxes auto-snapshot on stop. Provisioning runs in the `iad1` region and is covered by Vercel's SOC 2 Type II compliance. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Security Model

The security model is built around the principle that a kernel exploit inside a Firecracker sandbox cannot reach the host kernel by construction. This addresses several key threat vectors:

- **Filesystem isolation**: Prevents read/write access outside the intended scope
- **Network containment**: Controls egress to arbitrary domains  
- **Kernel surface protection**: Eliminates exposure of host kernel syscalls to agent-executed code
- **Multi-tenant separation**: Prevents cross-tenant data leakage in multi-tenant environments

^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Performance Characteristics

Firecracker microVMs boot in sub-second time according to AWS design documentation, making them suitable for per-request agent sandboxing where full VMs would be too slow. This represents a significant improvement over full VM provisioning which typically takes 30 seconds or more. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Use Cases

Vercel Sandbox is positioned for workloads involving:

- [[AI Coding Agents]] executing user-generated code
- Code generation and experimentation platforms
- Multi-tenant developer environments
- Any scenario requiring execution of untrusted code with strong isolation guarantees

^[ai-agent-sandboxing-isolation-patterns-2026.md]

## Industry Context

Vercel Sandbox reached General Availability in January 2026, making managed microVM infrastructure production-ready for teams without the operational budget to run their own Firecracker fleet. It represents part of a broader trend where microVM-grade isolation is becoming the 2026 baseline expectation for AI coding services where users submit prompts that generate code. ^[ai-agent-sandboxing-isolation-patterns-2026.md]

The platform competes with other microVM-based solutions like [[E2B]] (open-source) and is part of a broader ecosystem that includes Fly.io, Modal, and Docker Desktop's sandbox feature, all of which use microVM-grade isolation with Firecracker or Firecracker-compatible VMMs. ^[ai-agent-sandboxing-isolation-patterns-2026.md]
