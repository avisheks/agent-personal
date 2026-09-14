---
title: "Idea File Pattern"
summary: "An open-source approach that shares principles and behavioral guidelines rather than implementations, allowing recipients to adapt ideas to their specific needs."
sources:
  - claude code config by Andrej Karpathy/karpathy-s-claude-md-skills-file-the-complete-guide.md
createdAt: 2026-05-25T15:56:59.312254+00:00
updatedAt: 2026-05-25T15:56:59.312254+00:00
---
# Idea File Pattern

The **Idea File Pattern** is a method of sharing structured behavioral guidelines and principles rather than executable code or implementations. This pattern emerged prominently in the AI development community as a way to encode best practices and decision-making frameworks into reusable, adaptable formats that can be consumed by both human developers and AI agents. ^[karpathy-claude-code-skills-guide.md]

## Overview

The Idea File Pattern represents a shift from traditional open-source sharing of code implementations to sharing conceptual frameworks and behavioral guidelines. Rather than distributing libraries or applications, practitioners create structured documents that encode principles, decision trees, and behavioral constraints that recipients can adapt to their specific contexts. ^[karpathy-claude-code-skills-guide.md]

This pattern gained significant attention through repositories like `andrej-karpathy-skills`, which distilled complex coding principles into a single, machine-readable configuration file that AI coding agents could automatically consume and follow. The approach demonstrates what creator Andrej Karpathy termed "open ideas" rather than traditional "open code." ^[karpathy-claude-code-skills-guide.md]

## Key Characteristics

### Structure Over Implementation

Idea files focus on encoding decision-making frameworks and behavioral guidelines rather than specific code implementations. They typically contain:

- Explicit principles and constraints
- Decision trees for common scenarios  
- Success criteria and verification methods
- Anti-patterns to avoid

^[karpathy-claude-code-skills-guide.md]

### Adaptability

Unlike rigid code libraries, idea files are designed to be customized and merged with project-specific requirements. Recipients modify the guidelines to fit their particular domain, technology stack, or organizational constraints while preserving the core behavioral principles. ^[karpathy-claude-code-skills-guide.md]

### Machine and Human Readable

Effective idea files serve dual purposes - they can be consumed automatically by AI agents as behavioral constraints while remaining human-readable for review and modification. This dual accessibility enables both automated enforcement and human oversight of the encoded principles. ^[karpathy-claude-code-skills-guide.md]

## Implementation Examples

### CLAUDE.md Files

The most prominent example of the Idea File Pattern is the `CLAUDE.md` format used by AI coding agents. These files encode behavioral guidelines that AI agents automatically read and follow at the start of each coding session. A typical structure includes:

- Project overview and context
- Coding standards and conventions
- Safety rules and constraints  
- Architecture guidelines
- Success criteria definitions

^[karpathy-claude-code-skills-guide.md]

### Behavioral Principle Encoding

The `andrej-karpathy-skills` repository demonstrates encoding complex behavioral principles into four core guidelines:

1. **Think Before Coding** - Surface assumptions and tradeoffs explicitly
2. **Simplicity First** - Minimum viable implementation without speculation
3. **Surgical Changes** - Modify only what is necessary
4. **Goal-Driven Execution** - Define verifiable success criteria

Each principle addresses specific failure modes observed in AI-assisted development while remaining general enough for broad application. ^[karpathy-claude-code-skills-guide.md]

## Advantages

### Viral Distribution

Idea files can achieve rapid adoption because they require minimal technical infrastructure to implement. The `andrej-karpathy-skills` repository became one of the fastest-growing repositories on GitHub despite containing essentially a single configuration file, demonstrating the power of well-structured ideas over complex implementations. ^[karpathy-claude-code-skills-guide.md]

### Context Preservation

Unlike verbal instructions that must be repeated in each interaction, idea files provide persistent context that carries across sessions. This is particularly valuable for AI agents that lack memory between conversations, as the files serve as a form of "project memory card." ^[karpathy-claude-code-skills-guide.md]

### Reduced Cognitive Load

By encoding common decision-making patterns into reusable formats, idea files reduce the cognitive burden on practitioners who would otherwise need to repeatedly communicate the same principles and constraints. ^[karpathy-claude-code-skills-guide.md]

## Evolution from "Vibe Coding"

The Idea File Pattern represents an evolution from what Karpathy initially termed "vibe coding" - a loose, conversational approach to directing AI agents - toward more structured "agentic engineering." This maturation reflects the community's recognition that AI agents require clear objectives, defined boundaries, and rigorous constraints to produce maintainable outcomes. ^[karpathy-claude-code-skills-guide.md]

The pattern acknowledges that while AI has lowered barriers to code generation, the real bottleneck has shifted to architecture and evaluation. Idea files address this by providing frameworks for maintaining quality and consistency in AI-assisted development workflows. ^[karpathy-claude-code-skills-guide.md]

## Related Concepts

The Idea File Pattern intersects with several related approaches in AI-assisted development, including [[Constitutional AI for Ads]] for encoding behavioral constraints, [[LLM as Judge Quality Scoring]] for automated evaluation frameworks, and [[Chain of Thought Reasoning]] for structured decision-making processes. It also relates to broader software engineering practices around [[Trade-off Literacy]] and systematic approaches to managing technical complexity.
