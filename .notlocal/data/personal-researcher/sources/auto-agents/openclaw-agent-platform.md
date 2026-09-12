---
title: "OpenClaw - Personal AI Assistant Platform"
url: "https://github.com/openclaw/openclaw"
ingestedAt: "2026-06-06T00:00:00Z"
type: "project"
---

# OpenClaw

**OpenClaw** is a personal AI assistant platform that runs locally and interfaces through messaging channels. Originally released as "Clawdbot" in November 2025, rebranded to OpenClaw.

## Overview

- Creator/Maintainer: Peter Steinberger and open-source community (500+ contributors)
- Repository: github.com/openclaw/openclaw
- Stars: ~377k, Forks: ~78.8k, Commits: 57,651
- License: MIT
- Runtime: Node.js 24 (recommended) or Node.js 22.19+
- Primary language: TypeScript/Node.js

## Installation

- `curl -fsSL https://openclaw.im/install.sh | bash`
- Guided setup: `openclaw onboard --install-daemon` walks through gateway, workspace, channel, and skill configuration
- Development setup: `git clone`, `pnpm install`, `pnpm openclaw setup`, `pnpm gateway:watch`
- Dependencies: Node.js 24 (recommended) or Node.js 22.19+

## LLM Support

Any provider (BYOM - Bring Your Own Model):
- OpenAI
- Anthropic Claude
- Google Gemini
- Meta Llama
- Ollama (local)
- DeepSeek

## Infrastructure

- Local-first design; data stays on your hardware
- Also supports Docker, Kubernetes (Helm charts, Terraform modules available)
- Platforms: macOS, Linux, Windows
- Companion apps for iOS/Android

## Architecture

```
User <-> Messaging Channels (30+ platforms)
              |
         Gateway (Node.js, port 18789)
              |
    +----+----+----+----+
    |    |    |    |    |
  Sessions  Skills  Tools  Workflow Engine
  (Stateful (100+ plugins) (Browser,  (TypeScript/YAML
   context,              Shell,     triggers &
   SQLite/              Calendar,   conditions)
   Postgres/            Email...)
   Redis)
              |
         Agent Runtime
    (Multi-agent routing, isolated workspaces)
              |
         LLM Provider (BYOM)
```

## Key Features

- Local-first gateway as single control plane
- Multi-agent routing: inbound channels route to isolated agents with separate workspaces
- Pluggable storage backends (SQLite, PostgreSQL, Redis) for session state
- Programmable workflow engine (TypeScript or YAML)
- Plugin architecture with 100+ built-in integrations
- A2UI (Agent-to-UI) framework for "Live Canvas" visual workspace
- Voice capabilities with wake words (macOS/iOS) and continuous voice (Android)
- pnpm workspace monorepo structure for development
- 30+ messaging platforms (including iMessage, WeChat, QQ)

## CLI Interface

- `openclaw agent --message "query"` for direct interaction
- `openclaw gateway` for persistent service
- `openclaw install [skill]` for skill management
- `openclaw message send` for messaging
- Operator commands: /status, /new, /reset, /think

## Configuration

- `~/.openclaw/openclaw.json` (minimal JSON)
- Workspace files: AGENTS.md, SOUL.md, TOOLS.md for context injection
- Skills conform to AgentSkills.io standard

## Maintenance

- 57,651 commits, 3 release channels (stable, beta, dev)
- Very active development with 500+ contributors
- Recent OAuth regression fix (v202656) demonstrates mature release process
- Community: Dedicated Discord, multiple community sites (clawbot.blog, clawdocs.org, openclaw-ai.dev)
- Heartbeat system for 24/7 operation
- Monitoring: /status, /trace on|off, /verbose on|off

## Security

- Gateway exposure runbook
- DM pairing-mode verification
- Sandboxing for non-main sessions (Docker/SSH/OpenShell)
