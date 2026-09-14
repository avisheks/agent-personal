---
title: "Hermes Agent"
summary: "NousResearch's autonomous, self-improving AI agent framework with built-in learning loops, skill auto-creation, and dialectic user modeling."
sources:
  - auto-agents/hermes-agent-nousresearch.md
createdAt: 2026-06-15T11:24:06.172541+00:00
updatedAt: 2026-06-15T11:24:06.172541+00:00
---
# Hermes Agent

**Hermes Agent** is an autonomous AI agent framework developed by NousResearch (the team behind the Hermes LLM model series). Its distinguishing feature is a closed learning loop where the agent autonomously creates skills from experience, improves them during use, and maintains persistent memory across sessions. The framework is designed with the tagline "The agent that grows with you," emphasizing its self-improving capabilities. ^[hermes-agent-nousresearch.md]

## Architecture

Hermes Agent uses a Python-based core (83.6% of codebase) with TypeScript components (12.6%) and supports six interchangeable terminal backends: Local, Docker, SSH, Modal, Daytona, and Singularity. The agent connects to 20+ messaging platforms via a gateway layer and stores memory using FTS5 full-text search with LLM summarization for recall. User modeling is handled by Honcho, which builds a dialectic profile across sessions to enable cross-session personalization. ^[hermes-agent-nousresearch.md]

The architecture follows a modular design where the user interfaces through messaging platforms, which connect to the agent core that manages memory, skills, tools, and subagents. The terminal backend layer decouples execution from the user's machine, while LLM providers handle the language model inference. ^[hermes-agent-nousresearch.md]

## Self-Improvement Loop

The key differentiator is autonomous skill evolution through a closed learning loop:

1. Agent encounters a task
2. Creates a skill to handle it (conforming to [[AgentSkills Standard]])
3. Refines the skill on subsequent encounters
4. Skills accumulate, reducing future manual configuration

This means maintenance burden decreases over time as the agent becomes more capable. Skills can also be browsed and installed from the agentskills.io hub, and the framework includes batch trajectory generation for training tool-calling models as a research feature. ^[hermes-agent-nousresearch.md]

## Setup & Deployment

Hermes Agent offers streamlined installation across platforms:

- **One-liner install**: Linux/macOS via curl script, Windows via PowerShell
- **Dependencies**: Python 3.11 + Node.js (auto-installed by installer)
- **Configuration**: Requires API key for at least one LLM provider (Nous Portal, OpenRouter, OpenAI, HuggingFace, NVIDIA NIM, or custom endpoint) plus `hermes setup` wizard
- **Deployment options**: $5 VPS, GPU cluster, or serverless environments (Modal/Daytona for hibernating setups)
- **Migration support**: Can import settings from [[OpenClaw]] via `hermes claw migrate`

The installer bundles necessary components including uv, Python 3.11, Node.js, ripgrep, ffmpeg, and portable Git Bash in approximately 45MB. ^[hermes-agent-nousresearch.md]

## Command Line Interface

The framework provides several CLI commands for operation and management:

- `hermes` - Interactive CLI with multiline editing, slash-command autocomplete, and conversation history
- `hermes model` - Switch between LLM providers
- `hermes gateway` - Launch messaging platform integration
- `hermes setup` - Configuration wizard
- `hermes claw migrate` - Import configurations from OpenClaw

Additional features include built-in cron scheduling, `/usage` command for token tracking, and minimal configuration requirements focused primarily on API keys and model selection. ^[hermes-agent-nousresearch.md]

## Development Status

Hermes Agent is actively maintained by NousResearch with 17 releases as of June 2026 (latest v0.16.0). The project has gained significant community traction with approximately 184k stars and 31.6k forks on GitHub, along with 10,746 commits. It operates under an MIT license and maintains a community presence through the NousResearch Discord server. ^[hermes-agent-nousresearch.md]

## Related

- [[OpenClaw]] — Competing personal AI assistant platform; Hermes offers migration path
- [[AgentSkills Standard]] — Shared skill format between Hermes and OpenClaw (agentskills.io)
