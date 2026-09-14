---
title: "Goal-Driven Execution Principle"
summary: "A development methodology that transforms imperative tasks into verifiable success criteria with test-driven approaches and clear verification loops."
sources:
  - claude code config by Andrej Karpathy/github-multica-ai-andrej-karpathy-skills-a-single-claude-md-file-to-improve-claude-code-behavior-derived-from-andrej-karpathy-s-observations-on-llm-coding-pitfalls-github.md
createdAt: 2026-05-25T15:54:41.868656+00:00
updatedAt: 2026-05-25T15:54:41.868656+00:00
---
# Goal-Driven Execution Principle

The **Goal-Driven Execution Principle** is a software development methodology that transforms imperative task instructions into verifiable success criteria, enabling autonomous execution loops until objectives are met. This principle addresses the tendency of language models and developers to follow instructions without clear verification mechanisms. ^[andrej-karpathy-skills.md]

## Core Philosophy

The principle is based on the observation that "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go." Rather than providing step-by-step instructions, this approach defines clear success metrics and allows autonomous iteration until those criteria are satisfied. ^[andrej-karpathy-skills.md]

## Implementation Framework

### Task Transformation Strategy

The principle requires converting imperative commands into declarative goals with verification mechanisms:

- **"Add validation"** becomes **"Write tests for invalid inputs, then make them pass"**
- **"Fix the bug"** becomes **"Write a test that reproduces it, then make it pass"**  
- **"Refactor X"** becomes **"Ensure tests pass before and after"** ^[andrej-karpathy-skills.md]

### Multi-Step Planning Structure

For complex tasks, the principle advocates stating a brief plan with verification checkpoints:

1. [Step] → verify: [check]
2. [Step] → verify: [check]  
3. [Step] → verify: [check] ^[andrej-karpathy-skills.md]

## Success Criteria Design

### Strong vs. Weak Criteria

**Strong success criteria** enable independent looping and autonomous verification, while **weak criteria** (such as "make it work") require constant clarification and manual oversight. The principle emphasizes that well-defined success metrics allow systems to operate with minimal supervision. ^[andrej-karpathy-skills.md]

### Verification Mechanisms

Each step in the execution process must include explicit verification methods that can be independently validated. This creates a feedback loop where progress can be measured objectively rather than subjectively assessed. ^[andrej-karpathy-skills.md]

## Integration with Development Practices

The Goal-Driven Execution Principle is designed to work alongside other software development methodologies. It can be integrated into existing project workflows and combined with project-specific guidelines while maintaining its core focus on verifiable outcomes. ^[andrej-karpathy-skills.md]

## Effectiveness Indicators

The principle is working effectively when development processes exhibit:

- **Fewer unnecessary changes in diffs** — Only requested changes appear
- **Fewer rewrites due to overcomplication** — Code is simple the first time
- **Clarifying questions come before implementation** — Not after mistakes
- **Clean, minimal PRs** — No drive-by refactoring or "improvements" ^[andrej-karpathy-skills.md]

## Practical Considerations

The principle biases toward **caution over speed** and is most valuable for non-trivial work where costly mistakes are likely. For simple tasks such as typo fixes or obvious one-liners, the full rigor may not be necessary, and judgment should be applied to balance thoroughness with efficiency. ^[andrej-karpathy-skills.md]
