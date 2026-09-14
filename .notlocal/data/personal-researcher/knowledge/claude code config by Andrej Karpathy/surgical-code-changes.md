---
title: "Surgical Code Changes"
summary: "A principle that constrains AI code modifications to only touch files and lines directly required by the user's request, avoiding orthogonal edits and style drift."
sources:
  - claude code config by Andrej Karpathy/andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md
createdAt: 2026-05-25T15:53:06.440508+00:00
updatedAt: 2026-05-25T15:53:06.440508+00:00
---
# Surgical Code Changes

**Surgical Code Changes** is a software engineering principle that emphasizes making minimal, targeted modifications to codebases during development tasks. The concept gained prominence through Andrej Karpathy's CLAUDE.md rules, which identified the tendency of AI coding assistants to make unnecessary modifications to code that is orthogonal to the requested task. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Core Principle

The surgical changes approach requires developers and AI assistants to touch only the code that is directly necessary to fulfill a specific request. This principle draws a hard boundary around modifications, ensuring that every changed line can be traced directly back to the original requirement. The approach enforces strict discipline: match existing code style even when personal preferences would differ, and mention unrelated issues (such as dead code) rather than automatically fixing them. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Common Anti-Patterns

### Orthogonal Edits
AI coding assistants frequently exhibit a tendency to "improve" adjacent code while completing a primary task. This includes reformatting comments, refactoring functional code, and removing dead code that may not be fully understood by the assistant. These modifications occur even when they are completely unrelated to the user's original request. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

### Style Drift
Another common violation occurs when assistants modify existing code to match their preferred coding style rather than maintaining consistency with the existing codebase patterns. This creates unnecessary changes that make code reviews more difficult and can introduce subtle bugs. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

### Drive-By Refactoring
AI assistants often perform unsolicited refactoring of working code, adding abstractions, error handling for impossible scenarios, or "flexibility" that wasn't requested. This behavior stems from the AI's tendency to over-engineer solutions beyond what was explicitly asked for. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Implementation Guidelines

The surgical changes principle enforces several specific behaviors that directly address common failure modes:

- Touch only what the user's request requires
- Match existing code style even when personal preferences would differ  
- Mention unrelated issues (such as dead code) rather than automatically fixing them
- Ensure all modifications directly serve the user's explicit request
- Maintain clean, reviewable diffs that focus solely on the requested changes ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Benefits

### Clean Diffs
By limiting changes to only what is necessary, surgical modifications produce diffs that are easier to review and understand. This reduces the cognitive load on code reviewers and makes it simpler to identify the actual changes being made. The result is pull requests that are clean and minimal with no drive-by refactoring. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

### Reduced Risk
Touching minimal code reduces the likelihood of introducing unintended side effects or breaking existing functionality that was working correctly. This is particularly important when AI assistants might not fully understand the context or dependencies of code they're modifying. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

### Focused Development
The principle helps maintain focus on the specific task at hand rather than allowing scope creep through tangential improvements. This prevents the common scenario where a simple bug fix turns into a major refactoring effort. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Relationship to AI Coding Workflows

Surgical code changes represent a shift in how developers work with AI coding assistants. Rather than allowing the AI to make broad modifications across a codebase, this principle constrains the AI to surgical precision. The approach is part of a larger framework that includes thinking before coding, maintaining simplicity, and using [[goal-driven-execution]] rather than imperative instructions. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Implementation Through Configuration

The principle can be systematically enforced through [[CLAUDE.md]] configuration files that provide persistent instructions to AI coding assistants. This allows teams to embed the surgical changes principle directly into their development workflow, ensuring consistent behavior across all AI-assisted coding sessions. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]

## Measuring Effectiveness

Teams can identify when surgical code changes are working effectively by observing specific indicators in their development process. Successful implementation results in fewer unnecessary changes appearing in diffs, with only requested edits visible in code reviews. Additionally, AI assistants begin asking clarifying questions before implementing changes rather than making assumptions and requiring corrections afterward. ^[andrej-karpathy-s-claude-md-rules-the-file-that-fixes-claude-code-ai-builder-club.md]
