---
title: "CLAUDE.md Project Configuration"
summary: "A project-level instruction file that Claude Code reads at the start of every session to define persistent behavior guidelines and coding principles for a specific codebase."
sources:
  - claude code config by Andrej Karpathy/andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md
createdAt: 2026-05-25T15:52:24.587381+00:00
updatedAt: 2026-05-25T15:52:24.587381+00:00
---
# CLAUDE.md Project Configuration

CLAUDE.md is a project-level instruction file that Claude Code reads at the start of every session, functioning as a persistent system prompt for codebases. The file tells Claude how to behave before any coding begins, addressing common failure modes in AI-assisted development through specific engineering principles. ^[karpathy-claude-md-rules.md]

## Background and Development

The CLAUDE.md approach was popularized by Andrej Karpathy in December 2024, when he transitioned from 80% manual coding to 80% agent-driven development. Karpathy identified this shift as "the biggest change to my basic coding workflow in two decades" and documented specific failure modes he encountered with Claude Code. ^[karpathy-claude-md-rules.md]

Karpathy's key insight was that "LLMs are exceptionally good at looping until they meet specific goals. Don't tell it what to do, give it success criteria and watch it go." This observation became the foundation for a systematic approach to AI coding configuration. ^[karpathy-claude-md-rules.md]

## Common Failure Modes Addressed

The CLAUDE.md configuration targets four documented failure patterns in AI-assisted coding:

- Models make wrong assumptions and run with them silently
- They don't surface confusion, inconsistencies, or tradeoffs  
- They overcomplicate code through bloated abstractions and skipped cleanup
- They touch code orthogonal to the requested task ^[karpathy-claude-md-rules.md]

## The Four Core Principles

### Think Before Coding

This principle addresses wrong assumptions, hidden confusion, and missing tradeoffs by forcing explicit reasoning before implementation. It requires Claude to state assumptions explicitly, present multiple interpretations when ambiguity exists, push back when simpler approaches exist, and name unclear elements rather than guessing through them. ^[karpathy-claude-md-rules.md]

### Simplicity First

The simplicity principle counters overcomplication, bloated abstractions, and speculative features. It enforces no features beyond what was explicitly requested, no abstractions for single-use code, no unrequested configurable options, and rewriting when 200 lines could be 50. The test is whether a senior engineer would consider the code overcomplicated. ^[karpathy-claude-md-rules.md]

### Surgical Changes

This principle establishes boundaries against orthogonal edits, touching unrelated code, and style drift. It requires touching only what the user's request requires, matching existing style even when different approaches might be preferred, mentioning but not deleting unrelated dead code, and ensuring every changed line traces directly to the request. ^[karpathy-claude-md-rules.md]

### Goal-Driven Execution

The goal-driven principle operationalizes Karpathy's key insight by providing success criteria rather than imperative instructions. Instead of "Add validation," it suggests "Write tests for invalid inputs, then make them pass." For multi-step tasks, it requires Claude to state a brief plan with verification steps before touching code. ^[karpathy-claude-md-rules.md]

## Implementation Methods

### Claude Code Plugin Installation

The recommended approach uses a Claude Code plugin that works across all projects:
```
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills@karpathy-skills
```
^[karpathy-claude-md-rules.md]

### Per-Project Configuration

For individual projects, the CLAUDE.md file can be installed directly:
```
curl -o CLAUDE.md https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md
```
^[karpathy-claude-md-rules.md]

The configuration also works with Cursor through `.cursor/rules/karpathy-guidelines.mdc` files. ^[karpathy-claude-md-rules.md]

## Effectiveness Indicators

Successful CLAUDE.md implementation produces observable changes in development workflows:

- Fewer unnecessary changes with only requested edits appearing
- Claude asks clarifying questions before implementing rather than after mistakes
- Code is simple on first implementation rather than after pushback
- Pull requests are clean and minimal without drive-by refactoring ^[karpathy-claude-md-rules.md]

## Usage Considerations

The guidelines bias toward caution over speed, making them most valuable for non-trivial, multi-file work where silent wrong assumptions compound quickly. For trivial changes like typo fixes or obvious one-liners, the full rigor may not be necessary. ^[karpathy-claude-md-rules.md]

## Adoption and Impact

The `andrej-karpathy-skills` repository has achieved 144k GitHub stars and 14.7k forks, reflecting genuine word-of-mouth adoption rather than promotional hype. The widespread adoption indicates that many developers have encountered these exact failure modes and have been addressing them manually through individual debugging sessions. ^[karpathy-claude-md-rules.md]
