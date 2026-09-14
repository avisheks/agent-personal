---
title: "CLAUDE.md Project Memory Card"
summary: "A configuration file automatically read by AI coding agents at the start of every session to provide persistent behavioral guidelines and project context across conversations."
sources:
  - claude code config by Andrej Karpathy/karpathy-s-claude-md-skills-file-the-complete-guide.md
createdAt: 2026-05-25T15:55:12.139449+00:00
updatedAt: 2026-05-25T15:55:12.139449+00:00
---
# CLAUDE.md Project Memory Card

A **CLAUDE.md Project Memory Card** is a configuration file that provides persistent behavioral guidelines and project context for AI coding agents, particularly Claude Code. The concept emerged from developer Forrest Chang's systematization of Andrej Karpathy's observations about common LLM coding pitfalls into a structured, machine-readable format. ^[karpathy-claude-code-skills-guide.md]

## Overview

The CLAUDE.md file functions as an AI equivalent of onboarding documentation for new developers, except the AI reads it at the start of every session to maintain consistent behavior across conversations. It serves as a **Project Memory Card** that carries context and behavioral constraints across multiple coding sessions. ^[karpathy-claude-code-skills-guide.md]

The file format addresses what the community describes as the **"confident junior dev"** problem - AI agents that are fast and knowledgeable but prone to making naive mistakes, over-engineering solutions, or making unintended changes if left unsupervised. ^[karpathy-claude-code-skills-guide.md]

## Core Principles

The CLAUDE.md approach is built on four fundamental principles that directly address specific classes of LLM failures:

### Think Before Coding
This principle combats wrong assumptions and hidden confusion by requiring explicit reasoning before implementation. AI agents must state assumptions explicitly, present multiple interpretations when ambiguity exists, and ask for clarification rather than proceeding with uncertain requirements. ^[karpathy-claude-code-skills-guide.md]

### Simplicity First
Addresses the tendency toward over-engineering by enforcing minimum viable implementations. The principle prohibits features beyond what was requested, abstractions for single-use code, and speculative "flexibility" that wasn't explicitly needed. ^[karpathy-claude-code-skills-guide.md]

### Surgical Changes
Prevents orthogonal edits by requiring that changes touch only what is necessary to fulfill the request. This includes matching existing code style, avoiding drive-by refactoring, and not "improving" adjacent code or formatting. ^[karpathy-claude-code-skills-guide.md]

### Goal-Driven Execution
Transforms imperative tasks into declarative goals with verifiable success criteria. Instead of telling the AI what to do, this approach provides success criteria and allows the AI to loop until those criteria are met. ^[karpathy-claude-code-skills-guide.md]

## File Structure and Hierarchy

The CLAUDE.md system operates through a hierarchical structure:

- **Project root CLAUDE.md** - Shared context committed to version control
- **CLAUDE.local.md** - Private developer-specific notes (typically gitignored)
- **Global ~/.claude/CLAUDE.md** - User preferences across all projects
- **Subdirectory CLAUDE.md files** - Context specific to particular code sections ^[karpathy-claude-code-skills-guide.md]

## Best Practices

Effective CLAUDE.md files typically include sections for project overview, tech stack, architecture mapping, development commands, coding standards, and safety rules. The content should be concise enough to fit in the agent's context window without crowding out project-specific instructions. ^[karpathy-claude-code-skills-guide.md]

The rule of thumb for content inclusion is: if an instruction needs to be repeated in chat more than twice, it should be promoted into the CLAUDE.md file. ^[karpathy-claude-code-skills-guide.md]

## Implementation

The concept can be implemented through two primary methods: as a Claude Code plugin for cross-project availability, or as a per-project file downloaded directly from repositories like the popular `andrej-karpathy-skills` collection. ^[karpathy-claude-code-skills-guide.md]

## Impact and Adoption

The CLAUDE.md approach represents an evolution from "vibe coding" to what the community terms **"agentic engineering"** - a discipline where developers treat AI as a partner requiring clear objectives, defined boundaries, and rigorous testing protocols. ^[karpathy-claude-code-skills-guide.md]

The effectiveness of this approach is measured by fewer unnecessary changes in code diffs, reduced rewrites due to overcomplication, more clarifying questions before implementation, and cleaner, more focused pull requests. ^[karpathy-claude-code-skills-guide.md]

## Related Concepts

The CLAUDE.md Project Memory Card concept relates to broader patterns in AI system design, including [[Constitutional AI for Ads]] for behavioral constraint systems, [[LLM as Judge Quality Scoring]] for evaluation frameworks, [[Supervised Fine-Tuning (SFT)]] for training approaches that could incorporate these principles, and [[Human-in-the-Loop Agent Design]] for frameworks enabling effective AI-human collaboration in software development.
