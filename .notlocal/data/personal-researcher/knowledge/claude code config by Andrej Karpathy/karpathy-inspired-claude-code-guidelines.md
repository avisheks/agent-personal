---
title: "Karpathy-Inspired Claude Code Guidelines"
summary: "A systematic approach to improving LLM coding behavior through four core principles that address common pitfalls like wrong assumptions, overcomplication, and unnecessary code changes."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:53:55.910246+00:00
updatedAt: 2026-05-25T15:53:55.910246+00:00
---
# Karpathy-Inspired Claude Code Guidelines

The **Karpathy-Inspired Claude Code Guidelines** are a set of four coding principles designed to address common pitfalls in LLM-generated code, derived from observations by Andrej Karpathy about problematic patterns in AI coding assistance. These guidelines aim to improve code quality by encouraging explicit reasoning, simplicity, surgical changes, and goal-driven execution. ^[andrej-karpathy-skills.md]

## Background

The guidelines emerged from Karpathy's observations about systematic issues in LLM coding behavior. He noted that models "make wrong assumptions on your behalf and just run along with them without checking" and "don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should." Additionally, he observed that LLMs "really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do." ^[andrej-karpathy-skills.md]

## The Four Core Principles

### Think Before Coding

This principle addresses the tendency of LLMs to make silent assumptions and hide confusion. It requires explicit reasoning through several practices: stating assumptions explicitly rather than guessing when uncertain, presenting multiple interpretations instead of picking silently when ambiguity exists, pushing back when warranted if simpler approaches exist, and stopping when confused to name what's unclear and ask for clarification. ^[andrej-karpathy-skills.md]

### Simplicity First

The second principle combats overengineering by enforcing minimum code that solves the problem with nothing speculative. This means no features beyond what was asked, no abstractions for single-use code, no "flexibility" or "configurability" that wasn't requested, and no error handling for impossible scenarios. The guideline states that if 200 lines could be 50, it should be rewritten. The test is whether a senior engineer would consider the code overcomplicated. ^[andrej-karpathy-skills.md]

### Surgical Changes

When editing existing code, this principle mandates touching only what is necessary. It prohibits "improving" adjacent code, comments, or formatting, refactoring things that aren't broken, and requires matching existing style even if different approaches would be preferred. If unrelated dead code is noticed, it should be mentioned but not deleted unless specifically requested. The test is that every changed line should trace directly to the user's request. ^[andrej-karpathy-skills.md]

### Goal-Driven Execution

The fourth principle transforms imperative tasks into verifiable goals by defining success criteria and looping until verified. Instead of "Add validation," the approach becomes "Write tests for invalid inputs, then make them pass." For multi-step tasks, it requires stating a brief plan with verification steps. Strong success criteria enable independent LLM looping, while weak criteria require constant clarification. ^[andrej-karpathy-skills.md]

## Implementation Methods

The guidelines can be implemented through two primary approaches. Option A involves using a Claude Code plugin by adding the marketplace and installing the andrej-karpathy-skills plugin, which makes the skill available across all projects. Option B uses a per-project CLAUDE.md file that can be downloaded or appended to existing project documentation. ^[andrej-karpathy-skills.md]

## Integration with Development Tools

The guidelines include support for Cursor IDE through a committed project rule file, allowing the same principles to apply when opening projects in Cursor. The guidelines are designed to be merged with project-specific instructions and can accommodate additional rules for specific technologies or patterns. ^[andrej-karpathy-skills.md]

## Effectiveness Indicators

The guidelines are working effectively when several patterns emerge: fewer unnecessary changes in diffs with only requested changes appearing, fewer rewrites due to overcomplication as code is simple the first time, clarifying questions coming before implementation rather than after mistakes, and clean, minimal pull requests without drive-by refactoring or "improvements." ^[andrej-karpathy-skills.md]

## Design Philosophy

The guidelines bias toward caution over speed, recognizing that not every change needs full rigor for trivial tasks like simple typo fixes or obvious one-liners. The goal is reducing costly mistakes on non-trivial work rather than slowing down simple tasks. As Karpathy noted, "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go." ^[andrej-karpathy-skills.md]
