---
title: "Surgical Changes Principle"
summary: "A code modification strategy that touches only necessary code for the specific task while avoiding drive-by refactoring, style changes, or improvements to unrelated code sections."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:54:32.559901+00:00
updatedAt: 2026-05-25T15:54:32.559901+00:00
---
# Surgical Changes Principle

The **Surgical Changes Principle** is one of four core coding guidelines designed to address common pitfalls in LLM-assisted programming. This principle specifically targets the tendency of language models to make unnecessary modifications to existing code beyond what was explicitly requested. ^[andrej-karpathy-skills.md]

## Overview

The Surgical Changes Principle operates on the fundamental rule: "Touch only what you must. Clean up only your own mess." This approach prevents the common LLM behavior of making orthogonal edits or modifying code that should remain unchanged during focused development tasks. ^[andrej-karpathy-skills.md]

## Core Guidelines

### Minimal Modification Approach

When editing existing code, the principle enforces strict boundaries on what should be changed:

- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken  
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it ^[andrej-karpathy-skills.md]

### Cleanup Responsibility

The principle distinguishes between different types of cleanup based on causation:

**Your Changes**: Remove imports, variables, or functions that YOUR changes made unused
**Pre-existing Issues**: Don't remove pre-existing dead code unless asked ^[andrej-karpathy-skills.md]

## Verification Method

The principle includes a practical test for adherence: "Every changed line should trace directly to the user's request." This verification method ensures that all modifications can be justified as necessary for completing the specific task at hand. ^[andrej-karpathy-skills.md]

## Context and Purpose

This principle addresses Andrej Karpathy's observation that LLMs "still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task." The Surgical Changes Principle is designed to prevent these unintended modifications that can introduce bugs or confusion in codebases. ^[andrej-karpathy-skills.md]

## Implementation

The principle is typically implemented through project guidelines that can be added to development workflows via CLAUDE.md files or integrated development environment plugins. The goal is reducing costly mistakes on non-trivial work while maintaining development velocity on simple tasks. ^[andrej-karpathy-skills.md]

## Related Principles

The Surgical Changes Principle works alongside three other core principles in the Karpathy-inspired coding framework:

- **Think Before Coding**: Addresses wrong assumptions and hidden confusion
- **Simplicity First**: Combats overcomplication and bloated abstractions  
- **[[goal-driven-execution]]**: Focuses on verifiable success criteria ^[andrej-karpathy-skills.md]

## Expected Outcomes

When properly applied, the Surgical Changes Principle should result in:

- Fewer unnecessary changes in code diffs
- Clean, minimal pull requests without drive-by refactoring
- Only requested changes appearing in version control
- Reduced introduction of bugs through unintended modifications ^[andrej-karpathy-skills.md]
