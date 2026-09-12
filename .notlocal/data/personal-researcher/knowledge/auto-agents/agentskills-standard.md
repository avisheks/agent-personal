---
title: "AgentSkills Standard"
summary: "An open standard for portable AI agent skills shared between platforms like OpenClaw and Hermes Agent, accessible at agentskills.io."
sources:
  - auto-agents/hermes-agent-nousresearch.md
  - auto-agents/openclaw-agent-platform.md
createdAt: 2026-06-15T11:24:38.878519+00:00
updatedAt: 2026-06-15T11:24:38.878519+00:00
---
# AgentSkills Standard

**AgentSkills** (agentskills.io) is an open standard for defining portable AI agent skills that can be shared across different agent frameworks. The standard enables skills created for one agent platform to be reused by others, fostering a marketplace/hub model for agent capabilities. ^[hermes-agent-nousresearch.md] ^[openclaw-agent-platform.md]

## Framework Adoption

Both [[Hermes Agent]] and [[OpenClaw]] conform to the AgentSkills standard, demonstrating cross-platform compatibility. This shared standard allows skills developed in one framework to work seamlessly in the other, creating a unified ecosystem for agent capabilities. ^[hermes-agent-nousresearch.md] ^[openclaw-agent-platform.md]

## Usage Patterns

### Hermes Agent Implementation

In [[Hermes Agent]], skills are automatically generated during task execution and published to the agentskills.io hub. Users can also manually browse and install skills from the hub to extend their agent's capabilities. The framework's closed learning loop means that skills are continuously refined through use, improving their effectiveness over time. ^[hermes-agent-nousresearch.md]

### OpenClaw Implementation

[[OpenClaw]] users install skills via the command `openclaw install [skill-name]` or by pasting skill definitions directly into their configuration files. The platform's plugin architecture supports over 100 built-in integrations that conform to the AgentSkills standard. ^[openclaw-agent-platform.md]

## Standard Benefits

The AgentSkills standard addresses the fragmentation problem in the AI agent ecosystem by providing a common format for skill definition and sharing. This standardization enables:

- **Portability**: Skills work across different agent frameworks without modification
- **Community Development**: Developers can contribute skills that benefit the entire ecosystem
- **Reduced Duplication**: Common capabilities don't need to be reimplemented for each platform
- **Quality Improvement**: Popular skills receive community feedback and refinement

The standard is hosted at agentskills.io, which serves as both the specification repository and the central hub for skill discovery and distribution. ^[hermes-agent-nousresearch.md] ^[openclaw-agent-platform.md]
