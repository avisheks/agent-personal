---
title: "OpenClaw"
summary: "Local-first personal AI assistant platform with 30+ messaging integrations, programmable workflow engine, multi-agent routing, and enterprise deployment options (K8s, Helm, Terraform). Node.js-based, MIT licensed, 500+ contributors."
sources:
  - auto-agents/openclaw-agent-platform.md
createdAt: "2026-06-06T00:00:00Z"
updatedAt: "2026-06-06T00:00:00Z"
---
# OpenClaw

**OpenClaw** is a local-first personal AI assistant platform that interfaces through 30+ messaging channels. Originally released as "Clawdbot" (November 2025), it rebranded to OpenClaw and has grown to 500+ contributors and 377k GitHub stars. ^[openclaw-agent-platform.md]

## Architecture

OpenClaw runs a Node.js gateway (port 18789) that acts as a single control plane. Inbound messages from any channel are routed to isolated agent sessions with separate workspaces. State is stored in pluggable backends (SQLite, PostgreSQL, Redis). The platform includes a programmable workflow engine (TypeScript or YAML) for complex automation. ^[openclaw-agent-platform.md]

## Key Capabilities

- **Multi-agent routing**: Each channel/user gets an isolated agent with its own workspace and context
- **Workflow engine**: TypeScript or YAML-based triggers, conditions, and actions
- **100+ plugin integrations**: Browser, shell, calendar, email, and more
- **A2UI framework**: "Live Canvas" visual workspace for agent-to-UI interactions
- **Voice**: Wake words (macOS/iOS), continuous voice (Android)
- **BYOM**: Supports any LLM provider including local Ollama

^[openclaw-agent-platform.md]

## Setup & Deployment

- One-liner install + `openclaw onboard --install-daemon`
- Dependencies: Node.js 24 only
- Configuration: `~/.openclaw/openclaw.json` + workspace files (AGENTS.md, SOUL.md, TOOLS.md)
- Enterprise: Docker, Kubernetes (Helm charts), Terraform modules
- Companion apps: macOS, Windows, iOS, Android

^[openclaw-agent-platform.md]

## Maintenance & Operations

- 3 release channels (stable, beta, dev)
- Heartbeat system for 24/7 operation
- Built-in monitoring: /status, /trace, /verbose
- Security: Gateway exposure runbook, DM pairing-mode, sandboxing (Docker/SSH/OpenShell)

^[openclaw-agent-platform.md]

## Related

- [[Hermes Agent]] — Competing framework with self-improvement loop; offers migration FROM OpenClaw
- [[AgentSkills Standard]] — Shared skill format between OpenClaw and Hermes (agentskills.io)
