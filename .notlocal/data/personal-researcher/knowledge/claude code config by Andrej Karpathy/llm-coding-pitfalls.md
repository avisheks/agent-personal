---
title: "LLM Coding Pitfalls"
summary: "Common problems in LLM-generated code including wrong assumptions, overcomplication, bloated abstractions, and orthogonal edits to unrelated code."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:54:23.782420+00:00
updatedAt: 2026-05-25T15:54:23.782420+00:00
---
# LLM Coding Pitfalls

LLM Coding Pitfalls refer to systematic problems that occur when large language models generate, modify, or refactor code. These issues stem from fundamental limitations in how LLMs approach programming tasks and can lead to overcomplicated solutions, unintended changes, and poor code quality.

## Core Problems

### Silent Assumptions and Hidden Confusion

LLMs frequently make wrong assumptions on behalf of users and proceed with implementation without seeking clarification. They tend to pick an interpretation silently when ambiguity exists, rather than surfacing uncertainty or presenting multiple possible approaches. This behavior leads to implementations that may not match the user's actual intent, as the model doesn't manage its confusion or seek clarifications when encountering unclear requirements. ^[andrej-karpathy-skills.md]

### Overcomplication and Bloated Abstractions

A persistent tendency among LLMs is to overcomplicate code and APIs, creating bloated abstractions where simpler solutions would suffice. Models often implement constructions spanning 1000 lines when 100 would adequately solve the problem. This includes adding unnecessary features beyond what was requested, creating abstractions for single-use code, and introducing "flexibility" or "configurability" that wasn't needed. ^[andrej-karpathy-skills.md]

### Orthogonal Code Changes

LLMs sometimes change or remove comments and code they don't sufficiently understand as side effects of their primary task, even when these elements are orthogonal to the requested changes. This includes "improving" adjacent code, comments, or formatting that weren't part of the original request, and refactoring functional code that wasn't broken. ^[andrej-karpathy-skills.md]

### Lack of Tradeoff Presentation

Models often fail to present tradeoffs or push back when they should, missing opportunities to suggest simpler approaches or highlight potential issues with the requested implementation. They don't surface inconsistencies in requirements or propose alternative solutions that might better serve the user's goals. ^[andrej-karpathy-skills.md]

## Mitigation Strategies

### Explicit Assumption Management

Effective mitigation requires forcing LLMs to state assumptions explicitly rather than proceeding with silent interpretations. This involves asking for clarification when uncertain, presenting multiple interpretations when ambiguity exists, and pushing back when simpler approaches are available. ^[andrej-karpathy-skills.md]

### Simplicity-First Approach

Combating overengineering requires enforcing minimum code that solves the problem without speculative additions. This means avoiding features beyond what was asked, eliminating abstractions for single-use code, and removing unnecessary error handling for impossible scenarios. The test is whether a senior engineer would consider the solution overcomplicated. ^[andrej-karpathy-skills.md]

### Surgical Code Modifications

When editing existing code, LLMs should touch only what is necessary for the requested changes. This involves matching existing style even if different approaches might be preferred, and ensuring every changed line traces directly to the user's request. Clean-up should be limited to orphaned code created by the changes themselves. ^[andrej-karpathy-skills.md]

### Goal-Driven Execution

Transforming imperative tasks into verifiable goals helps LLMs focus on measurable outcomes. Instead of "add validation," the instruction becomes "write tests for invalid inputs, then make them pass." This approach leverages LLMs' strength at looping until they meet specific criteria, as noted in observations about their exceptional ability to work toward defined success metrics. ^[andrej-karpathy-skills.md]

## Implementation Framework

### Success Criteria Definition

Effective LLM coding requires defining clear success criteria that enable independent verification loops. Strong criteria allow models to iterate without constant clarification, while weak criteria like "make it work" require ongoing user intervention. Multi-step tasks benefit from brief plans with verification checkpoints for each step. ^[andrej-karpathy-skills.md]

### Quality Indicators

These mitigation strategies are working effectively when code diffs show fewer unnecessary changes, implementations are simple on the first attempt, clarifying questions precede implementation rather than following mistakes, and pull requests remain clean without drive-by refactoring or unsolicited improvements. ^[andrej-karpathy-skills.md]

The framework recognizes that these guidelines bias toward caution over speed, making them most valuable for non-trivial work where costly mistakes are more likely to occur. For simple tasks like typo fixes or obvious one-liners, full rigor may not be necessary. ^[andrej-karpathy-skills.md]
