---
title: "Hermes Agent - NousResearch Autonomous AI Agent Framework"
url: "https://github.com/NousResearch/hermes-agent"
ingestedAt: "2026-06-06T00:00:00Z"
type: "project"
---

# Hermes Agent

**Hermes Agent** is an autonomous, self-improving AI agent framework with a built-in learning loop, developed by NousResearch. Tagline: "The agent that grows with you."

## Overview

- Creator/Maintainer: NousResearch (same team behind Hermes LLM model series)
- Repository: github.com/NousResearch/hermes-agent
- Stars: ~184k, Forks: ~31.6k, Commits: 10,746
- License: MIT
- Latest version: v0.16.0 (June 2026), 17 releases total
- Primary language: Python (83.6%) + TypeScript (12.6%)

## Installation

- Linux/macOS: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
- Windows: PowerShell one-liner; bundles uv, Python 3.11, Node.js, ripgrep, ffmpeg, portable Git Bash (~45MB)
- Post-install: `hermes setup` runs a configuration wizard
- Dependencies: Python 3.11, Node.js (auto-installed by installer)

## LLM Requirements

Needs API key for at least one provider:
- Nous Portal
- OpenRouter
- OpenAI
- HuggingFace
- NVIDIA NIM
- Custom endpoint

## Infrastructure

- Runs on a $5 VPS, GPU cluster, or serverless (Modal/Daytona for hibernating environments)
- Platforms: Linux, macOS, WSL2, Termux, native Windows

## Architecture

```
User <-> Messaging Gateway (Telegram/Discord/Slack/WhatsApp/...)
              |
         Agent Core (Python)
              |
    +----+----+----+----+
    |    |    |    |    |
  Memory  Skills  Tools  Subagents
  (FTS5 + (agentskills.io (Web, Browser, (Parallel
   Honcho   standard)    Code Exec,   workstreams)
   user                  Vision, TTS)
   modeling)
              |
         Terminal Backend
    (Local/Docker/SSH/Modal/Daytona/Singularity)
              |
         LLM Provider
```

## Key Features

- Closed learning loop: tasks -> skill creation -> skill refinement -> better task execution
- Dialectic user modeling via Honcho (cross-session personalization)
- FTS5 full-text search with LLM summarization for memory recall
- Six terminal backends decouple execution from the user's machine
- Subagent spawning for parallel execution
- Batch trajectory generation for training tool-calling models (research feature)
- Skills auto-created during use; can also browse/install from agentskills.io hub
- 20+ messaging platforms supported

## CLI Interface

- `hermes` starts interactive CLI with multiline editing, slash-command autocomplete, conversation history
- `hermes model` (switch LLM)
- `hermes gateway` (launch messaging)
- `hermes setup` (config wizard)
- `hermes claw migrate` (import from OpenClaw)

## Configuration

- Minimal: primarily API keys and model selection
- Persona via SOUL.md
- Skills conform to AgentSkills.io standard

## Maintenance

- 17 releases to date, rapid iteration (younger project)
- Migration tool for OpenClaw users
- Built-in cron scheduler, `/usage` command for token tracking
- Self-improvement reduces manual maintenance of skill definitions
- Community: NousResearch Discord
