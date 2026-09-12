---
title: "The Karpathy Loop"
summary: "A three-component framework for autonomous optimization consisting of an agent with file modification access, a single testable metric to optimize, and a fixed time limit for experiments."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:05:37.611047+00:00
updatedAt: 2026-05-25T16:05:37.611047+00:00
---
# The Karpathy Loop

**The Karpathy Loop** is a framework for autonomous AI optimization systems, named after AI researcher Andrej Karpathy's viral experiment in March 2026. The concept describes a systematic approach where AI agents continuously optimize processes through iterative experimentation and learning. ^[karpathy-loop-fortune.md]

## Core Components

The Karpathy Loop consists of three essential elements:

- **An agent with access to a single file that it can modify** - The AI system has the ability to make changes to a specific codebase or configuration
- **A single metric, objectively testable metric, that the agent can optimize for** - There must be a clear, measurable goal that can be automatically evaluated
- **A fixed time limit for how long each experiment can run** - Each optimization cycle has defined boundaries to prevent runaway processes ^[karpathy-loop-fortune.md]

## The Autoresearch Experiment

Karpathy demonstrated the concept through his "autoresearch" system, where he deployed an AI coding agent to optimize the training of a small language model. The agent ran continuously for two days, conducting 700 different experiments and discovering 20 optimizations that improved training time. When applied to a larger model, these optimizations resulted in an 11% speed improvement. ^[karpathy-loop-fortune.md]

The system operated on a relatively simple codebase of just 630 lines of Python code, allowing the AI agent to make modifications and test their effectiveness systematically. ^[karpathy-loop-fortune.md]

## Industrial Applications

Tobias Lütke, CEO of Shopify, replicated the approach using autoresearch to optimize an AI model on internal company data. After running overnight, the system conducted 37 experiments and achieved a 19% performance gain, demonstrating the framework's broader applicability beyond Karpathy's original use case. ^[karpathy-loop-fortune.md]

## Future Vision and Scaling

Karpathy envisions scaling the approach through collaborative multi-agent systems. Rather than emulating a single researcher, the goal is to "emulate a research community" of AI agents working in parallel on different optimization paths. This would involve spinning up swarms of agents that collaborate to tune smaller models, with the most promising ideas promoted to increasingly larger scales. ^[karpathy-loop-fortune.md]

The framework's potential extends beyond AI model optimization. According to Karpathy, "any metric you care about that is reasonably efficient to evaluate (or that has more efficient proxy metrics such as training a smaller network) can be autoresearched by an agent swarm." ^[karpathy-loop-fortune.md]

## Implementation Guidelines

Effective implementation of the Karpathy Loop requires clear instruction design for AI agents, including:

- **Clear instructions** for what the agent should accomplish
- **Constraints** defining what the agent should not do or change  
- **Stopping criteria** indicating how long each loop should run and when to report results ^[karpathy-loop-fortune.md]

## Relationship to Existing Methods

While critics noted similarities to existing AutoML approaches used by major tech companies, Karpathy distinguished his method as fundamentally more powerful. Unlike traditional AutoML systems that rely on random variations or evolutionary algorithms, the Karpathy Loop employs "an actual LLM writing arbitrary code, learning from previous experiments, with access to the internet." ^[karpathy-loop-fortune.md]

## Implications for AI Development

The framework represents a significant step toward autonomous AI research systems. Karpathy predicted that "all LLM frontier labs will do this," describing it as "the final boss battle" in AI development. While acknowledging the engineering complexity of scaling to larger systems, he characterized the implementation as achievable through systematic engineering work. ^[karpathy-loop-fortune.md]

The concept raises important questions about recursive self-improvement in AI systems, though Karpathy's implementation focuses on optimizing separate, smaller models rather than direct self-modification. ^[karpathy-loop-fortune.md]
