---
title: "Simplicity First Principle"
summary: "A development approach that emphasizes minimum viable code solutions without speculative features, unnecessary abstractions, or overengineering beyond the requested requirements."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:54:22.537465+00:00
updatedAt: 2026-05-25T15:54:22.537465+00:00
---
# Simplicity First Principle

The **Simplicity First Principle** is a software development guideline that emphasizes writing the minimum code necessary to solve a problem, without speculative features or unnecessary abstractions. This principle directly addresses the tendency of large language models and developers to overcomplicate solutions and create bloated code architectures.

## Core Philosophy

The Simplicity First Principle operates on the fundamental belief that code should be written with "minimum code that solves the problem. Nothing speculative." This approach combats the natural tendency toward overengineering by establishing clear boundaries around what should and should not be included in a solution. ^[andrej-karpathy-skills.md]

The principle includes a practical test for evaluating code complexity: "Would a senior engineer say this is overcomplicated? If yes, simplify." This provides a concrete benchmark for assessing whether a solution has crossed the line from appropriate to excessive. ^[andrej-karpathy-skills.md]

## Implementation Guidelines

### What to Avoid

The Simplicity First Principle explicitly prohibits several common forms of overengineering:

- No features beyond what was specifically requested
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- Avoiding implementations that use significantly more lines than necessary (e.g., "If 200 lines could be 50, rewrite it") ^[andrej-karpathy-skills.md]

### Practical Application

The principle encourages developers to question every addition to their code. Rather than building for hypothetical future needs or adding layers of abstraction "just in case," it advocates for solving only the immediate problem at hand with the most direct approach possible. ^[andrej-karpathy-skills.md]

## Relationship to Other Development Practices

The Simplicity First Principle works in conjunction with other disciplined development approaches. It pairs particularly well with surgical change practices that limit modifications to only what is necessary, and goal-driven execution that focuses on verifiable success criteria rather than feature accumulation. ^[andrej-karpathy-skills.md]

## Origins and Context

This principle emerged from observations about common pitfalls in AI-assisted coding, where language models tend to "overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do." The Simplicity First Principle directly addresses these tendencies by establishing clear constraints on code complexity. ^[andrej-karpathy-skills.md]

## Evaluation Criteria

The effectiveness of applying the Simplicity First Principle can be measured through several indicators:

- Fewer unnecessary changes appearing in code diffs
- Reduced need for rewrites due to overcomplication
- Code that is appropriately simple on the first implementation
- Clean, minimal pull requests without excessive refactoring ^[andrej-karpathy-skills.md]
