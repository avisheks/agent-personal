---
title: "Agentic Engineering"
summary: "A disciplined approach to working with AI coding agents that treats them as partners requiring clear objectives, defined boundaries, and rigorous testing rather than loose conversational prompting."
sources:
  - claude code config by Andrej Karpathy/karpathy-s-claude-md-skills-file-the-complete-guide.md
createdAt: 2026-05-25T15:56:42.563917+00:00
updatedAt: 2026-05-25T15:56:42.563917+00:00
---
# Agentic Engineering

**Agentic Engineering** is a software development discipline that emerged in 2026, focusing on the structured collaboration between human developers and AI coding agents. The field evolved from Andrej Karpathy's concept of "vibe coding" into a more rigorous approach that treats AI agents as partners requiring clear objectives, defined boundaries, and systematic verification processes. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Overview

Agentic Engineering addresses the fundamental challenge of AI-assisted development: while AI agents can rapidly generate code, they often exhibit behaviors similar to a "confident junior developer" - producing fast, knowledgeable output while being prone to overengineering, making unwarranted assumptions, and introducing unintended side effects. The discipline provides frameworks and principles to channel AI capabilities productively while mitigating these failure modes. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

The field represents a shift from implementation-focused programming to architecture and evaluation-focused development, where the primary bottleneck has moved from "how do I write this code?" to "do I understand what the agent built well enough to maintain it?" ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Core Principles

Agentic Engineering is built around four foundational principles that directly address common AI agent failure patterns:

### Think Before Coding
This principle combats AI agents' tendency to make silent assumptions and proceed without clarification. It requires agents to state assumptions explicitly, present multiple interpretations when ambiguity exists, and surface tradeoffs before implementation begins. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

### Simplicity First
Addresses the over-engineering tendency of AI agents by enforcing minimum viable implementations. The principle prohibits speculative features, unnecessary abstractions for single-use code, and complexity that wasn't explicitly requested. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

### Surgical Changes
Prevents orthogonal modifications by requiring agents to touch only code directly related to the requested change. This principle maintains code stability by avoiding drive-by refactoring, style changes, or "improvements" to adjacent code. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

### Goal-Driven Execution
Transforms imperative tasks into declarative success criteria, leveraging AI agents' strength at iterative improvement toward specific objectives. Rather than prescribing implementation steps, this approach defines verification criteria and allows agents to loop until goals are met. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Implementation Methods

### Project Memory Cards
Agentic Engineering commonly uses `CLAUDE.md` files as **Project Memory Cards** - structured documentation that AI agents automatically read at session start. These files encode behavioral guidelines, project context, and coding standards that persist across conversations. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

The hierarchy typically includes:
- Project root `CLAUDE.md` for shared context
- `CLAUDE.local.md` for developer-specific notes  
- Global `~/.claude/CLAUDE.md` for cross-project preferences
- Subdirectory files for component-specific context ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

### Behavioral Guidelines
The most widely adopted implementation is the `andrej-karpathy-skills` repository, which distills the four core principles into a concise behavioral specification. This "idea file" pattern shares principles rather than code, allowing teams to adapt guidelines to their specific contexts. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Industry Impact

The emergence of Agentic Engineering reflects a broader maturation in AI-assisted development. The field has gained significant traction, with behavioral guideline repositories achieving tens of thousands of GitHub stars despite containing minimal code - indicating strong community validation of the underlying principles. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

The discipline addresses what practitioners call "AI psychosis" - a state of hyper-productive yet draining constant agent direction that can lead to unmaintainable code if not properly structured. By providing systematic approaches to agent collaboration, Agentic Engineering aims to capture AI productivity benefits while maintaining code quality and developer sanity. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Success Metrics

Effective Agentic Engineering implementation is typically measured by:
- Reduced unnecessary changes in code diffs
- Fewer rewrites due to overcomplication  
- Increased clarifying questions before implementation
- Cleaner, more focused pull requests without drive-by modifications ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

The field acknowledges tradeoffs between caution and speed, with guidelines designed to prevent costly mistakes on complex work while allowing judgment-based shortcuts for trivial tasks. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Evolution from Vibe Coding

Agentic Engineering evolved from Karpathy's earlier concept of "vibe coding" - a loose, conversational approach to AI prompting. By 2026, the community had matured this into a more disciplined methodology that treats AI as a partner requiring structured collaboration rather than informal direction. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

This evolution represents a shift from the "idea file" pattern of sharing principles rather than implementations, enabling teams to adapt core concepts to their specific technical and organizational contexts. ^[karpathy-s-claude-md-skills-file-the-complete-guide.md]

## Related Concepts

- [[Constitutional AI for Ads]] - Systematic approaches to AI behavior modification
- [[LLM as Judge Quality Scoring]] - Evaluation frameworks for AI-generated content
- [[Human-in-the-Loop Agent Design]] - Architectural patterns for human-AI collaboration
- [[Multi-Agent Orchestration]] - Coordination strategies for multiple AI agents
