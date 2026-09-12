---
title: "Surgical Code Changes Principle"
summary: "A coding guideline that requires touching only the code necessary to fulfill a request, avoiding drive-by refactoring or orthogonal improvements to maintain focused, traceable changes."
sources:
  - claude code config by Andrej Karpathy/karpathy-s-claude-md-skills-file-the-complete-guide.md
createdAt: 2026-05-25T15:55:30.960457+00:00
updatedAt: 2026-05-25T15:55:30.960457+00:00
---
# Surgical Code Changes Principle

The **Surgical Code Changes Principle** is a behavioral guideline for AI coding agents that emphasizes making minimal, targeted modifications to existing codebases. This principle addresses the common tendency of large language models to make unnecessary changes to code that is orthogonal to the requested task.

## Overview

The Surgical Code Changes Principle is one of four core principles outlined in the widely-adopted `CLAUDE.md` behavioral guidelines, which were created to address specific failure patterns identified in AI-assisted coding workflows. The principle specifically targets the problem where AI agents make unintended side effects by changing or removing comments and code they don't sufficiently understand, even when these changes are orthogonal to the primary task. ^[karpathy-claude-code-skills-guide.md]

## Core Guidelines

The principle follows a simple directive: **"Touch only what you must. Clean up only your own mess."** This translates into specific behavioral rules for AI coding agents:

### What Not to Change
- Don't "improve" adjacent code, comments, or formatting that wasn't part of the request
- Don't refactor things that aren't broken
- Match existing style, even if you would do it differently
- If you notice unrelated dead code, mention it but don't delete it

### What You Can Change
When your changes create orphans, you may:
- Remove imports, variables, or functions that **your changes** made unused
- Clean up dependencies that are no longer needed due to your specific modifications
- Don't remove pre-existing dead code unless explicitly asked ^[karpathy-claude-code-skills-guide.md]

## The Verification Test

The principle includes a simple verification test: **Every changed line should trace directly to the user's request.** This helps ensure that modifications remain focused and don't introduce unnecessary complexity or potential bugs through unrelated changes. ^[karpathy-claude-code-skills-guide.md]

## Common Anti-Patterns

### Drive-By Refactoring
A common violation occurs when an AI agent is asked to fix a specific bug but also:
- Adds docstrings that weren't requested
- Changes code style (quotes, spacing, formatting)
- Adds type hints or other "improvements"
- Restructures logic that was working correctly

### Style Drift
Another frequent issue is when agents change the existing code style while making functional changes. For example, when asked to add logging to a function, an agent might also convert single quotes to double quotes, add type hints, reformat whitespace, and restructure return logic - all of which are orthogonal to the logging request. ^[karpathy-claude-code-skills-guide.md]

## Implementation Examples

### Correct Surgical Approach
When asked to "Fix the bug where empty emails crash the validator":

**✅ Surgical Changes (3 lines changed):**
- Added empty-string guard for email
- Changed variable reference to avoid crash
- Nothing else touched

### Incorrect Drive-By Refactoring
**❌ Too Many Changes (15 lines changed):**
- Added docstring (not requested)
- Added username validation (not requested)  
- Changed comments (not requested)
- "Improved" email validation logic (not requested)
- Added .strip() calls everywhere (not requested) ^[karpathy-claude-code-skills-guide.md]

## Relationship to Other Principles

The Surgical Code Changes Principle works in conjunction with three other core principles in the behavioral framework:

- **[[Think Before Coding]]** - Addresses wrong assumptions and hidden confusion
- **[[Simplicity First]]** - Combats overcomplication and bloated abstractions  
- **[[Goal-Driven Execution]]** - Transforms tasks into verifiable success criteria

Together, these principles address what the AI community commonly refers to as the "confident junior dev" problem - where AI agents are fast and knowledgeable but prone to making naive mistakes if left unsupervised. ^[karpathy-claude-code-skills-guide.md]

## Benefits and Trade-offs

### Benefits
- Reduces unintended side effects in code changes
- Maintains code stability by avoiding unnecessary modifications
- Creates cleaner, more focused diffs for code review
- Preserves existing code style and conventions
- Minimizes the risk of introducing new bugs through orthogonal changes

### Trade-offs
The principle biases toward caution over speed. For trivial tasks like simple typo fixes or obvious one-liners, the full rigor may not be necessary. The goal is reducing costly mistakes on non-trivial work rather than slowing down simple tasks. ^[karpathy-claude-code-skills-guide.md]

## Implementation Context

This principle emerged from observations about [[LLM-as-Judge Quality Scoring]] patterns and the broader challenge of maintaining code quality in AI-assisted development workflows. It represents part of the evolution from "vibe coding" to "agentic engineering" - a more disciplined approach to working with AI coding agents that emphasizes clear boundaries and rigorous constraints. ^[karpathy-claude-code-skills-guide.md]

The principle is typically implemented through project memory cards (CLAUDE.md files) that provide persistent behavioral context for AI agents across coding sessions, helping maintain consistency and reduce the cognitive overhead of repeatedly instructing agents about desired behavior patterns.
