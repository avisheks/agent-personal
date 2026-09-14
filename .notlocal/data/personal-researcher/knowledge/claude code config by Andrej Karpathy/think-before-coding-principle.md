---
title: "Think Before Coding Principle"
summary: "A coding principle that requires explicit reasoning, stating assumptions, presenting multiple interpretations, and seeking clarification rather than making silent assumptions."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:54:12.363805+00:00
updatedAt: 2026-05-25T15:54:12.363805+00:00
---
# Think Before Coding Principle

The **Think Before Coding Principle** is a software development guideline designed to address common pitfalls in AI-assisted coding, particularly the tendency for language models to make assumptions and proceed with implementation without proper clarification or consideration of alternatives.

## Overview

The Think Before Coding Principle emerged from observations about how large language models approach coding tasks. Rather than making silent assumptions and proceeding with implementation, this principle emphasizes explicit reasoning, clarification-seeking, and transparent decision-making before writing code. ^[andrej-karpathy-skills.md]

The principle specifically addresses the problem where models "make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should." ^[andrej-karpathy-skills.md]

## Core Components

The Think Before Coding Principle consists of four key practices that force explicit reasoning and prevent silent assumption-making:

### State Assumptions Explicitly
Rather than silently choosing an interpretation when requirements are ambiguous, practitioners should explicitly state their assumptions and seek confirmation when uncertain. This transforms the typical pattern of "pick an interpretation silently and run with it" into transparent decision-making. ^[andrej-karpathy-skills.md]

### Present Multiple Interpretations
When ambiguity exists in requirements or specifications, the principle requires presenting multiple possible interpretations rather than picking one silently and proceeding. This ensures stakeholders can make informed decisions about which approach to pursue. ^[andrej-karpathy-skills.md]

### Push Back When Warranted
If a simpler approach exists or if the requested solution seems unnecessarily complex, practitioners should advocate for the better approach rather than blindly implementing what was asked. This component directly counters the tendency to overcomplicate solutions. ^[andrej-karpathy-skills.md]

### Stop When Confused
When encountering unclear requirements or conflicting information, the principle requires explicitly naming what is unclear and asking for clarification rather than making assumptions and continuing with implementation. ^[andrej-karpathy-skills.md]

## Implementation Context

The Think Before Coding Principle is part of a broader framework that includes three other complementary principles designed to address systematic issues in AI-assisted development:

- **Simplicity First**: Combating overengineering and unnecessary complexity by implementing minimum code that solves the problem with nothing speculative
- **Surgical Changes**: Making minimal, targeted modifications to existing code without touching unrelated components
- **[[Goal-Driven Execution]]**: Defining verifiable success criteria before implementation and looping until those criteria are met

Together, these principles address the observation that AI models "really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do." ^[andrej-karpathy-skills.md]

## Practical Application

The principle transforms the typical development workflow from assumption-driven implementation to clarification-driven planning. Instead of immediately beginning to code when given a task, practitioners first:

1. Identify areas of ambiguity or uncertainty in the requirements
2. Explicitly state their understanding and assumptions about the task
3. Present alternative approaches when multiple valid options exist
4. Seek clarification on unclear requirements or conflicting information
5. Only proceed with implementation after achieving clarity on the approach

This approach is designed to reduce costly mistakes on non-trivial work by ensuring proper understanding before implementation begins. The principle acknowledges that "LLMs often pick an interpretation silently and run with it" and forces a more deliberate, transparent process. ^[andrej-karpathy-skills.md]

## Effectiveness Indicators

The principle is working effectively when development exhibits several key characteristics. Clarifying questions should come before implementation rather than after mistakes have been made. There should be fewer rewrites due to misunderstood requirements, as the upfront clarification process catches ambiguities early. Decision-making processes become more transparent, with explicit reasoning replacing silent assumptions. Overall, there should be a reduction in assumption-based errors in code implementation. ^[andrej-karpathy-skills.md]

## Design Philosophy

The Think Before Coding Principle is built on the recognition that effective software development requires managing uncertainty and complexity through explicit communication rather than implicit assumptions. It acknowledges that while speed is valuable, "the goal is reducing costly mistakes on non-trivial work, not slowing down simple tasks." ^[andrej-karpathy-skills.md]

The principle biases toward caution over speed, recognizing that the cost of rework due to misunderstood requirements typically exceeds the cost of upfront clarification. However, it maintains that for trivial tasks like simple typo fixes or obvious one-liners, practitioners should use judgment rather than applying the full rigor of the principle. ^[andrej-karpathy-skills.md]
