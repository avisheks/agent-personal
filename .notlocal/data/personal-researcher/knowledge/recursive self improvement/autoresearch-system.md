---
title: "AutoResearch System"
summary: "Karpathy's open-source project where an LLM autonomously proposes changes to ML training code, runs experiments, evaluates metrics, and iterates improvements."
sources:
  - recursive self improvement/rsi-andrej.md
createdAt: 2026-05-25T15:57:22.824678+00:00
updatedAt: 2026-05-25T15:57:22.824678+00:00
---
# AutoResearch System

The **AutoResearch System** is an open-source project developed by Andrej Karpathy that demonstrates practical recursive self-improvement in AI systems. The system represents a concrete implementation of AI-driven research automation, where language models autonomously propose, execute, and evaluate machine learning experiments. ^[rsi-andrej.md]

## Overview

AutoResearch operates as an automated research loop where an LLM proposes changes to ML training code, runs experiments, evaluates metrics, keeps improvements, and repeats the process automatically. The system has been described as "recursive self improvement… something you can actually run," moving the concept from philosophical speculation to practical engineering systems. ^[rsi-andrej.md]

According to reports, the system has demonstrated the ability to run hundreds of experiments autonomously, modify training code, and optimize models with minimal human intervention while operating in a constrained experimental loop. ^[rsi-andrej.md]

## Technical Architecture

The AutoResearch system implements a bounded form of [[Recursive Self-Improvement]] through the following workflow:

- **Proposal Generation**: An LLM analyzes existing training code and proposes modifications
- **Experiment Execution**: The system automatically runs the proposed experiments
- **Metric Evaluation**: Results are evaluated against predefined performance criteria
- **Iterative Improvement**: Successful modifications are retained for future iterations
- **Autonomous Looping**: The process repeats without human intervention

This architecture represents what Karpathy has termed the "loopy era" of AI systems, where agents continuously improve code and research workflows. ^[rsi-andrej.md]

## Relationship to Recursive Self-Improvement

AutoResearch serves as a practical example of bounded recursive self-improvement, distinct from theoretical "hard RSI" scenarios. The system demonstrates current capabilities in:

- Optimizing training pipelines
- [[Hyperparameter Search]]
- Code generation and modification
- Experiment automation
- Agentic software engineering

However, it operates within constrained boundaries and does not involve rewriting entire architectures independently, inventing radically new intelligence, or escaping human control. ^[rsi-andrej.md]

## Significance for AI Development

The AutoResearch system addresses key bottlenecks in AI progress, including researcher productivity, experimentation speed, infrastructure tuning, data curation, and evaluation loops. By enabling AI agents to accelerate these workflows, the system demonstrates how frontier model development can be sped up with fewer humans needed per experiment, leading to compounding research throughput. ^[rsi-andrej.md]

## Applications in Foundation Models

For foundation model development, AutoResearch-style systems show particular promise in automating measurable workflows such as:

- Model evaluation and [[LLM-as-Judge Quality Scoring]]
- Reward optimization
- Feature engineering
- Retrieval tuning
- Prompt optimization
- [[Synthetic Preference Dataset Generation]]
- Policy tuning
- Agent-based experimentation

These applications represent practical implementations of "soft RSI" - AI accelerating AI engineering workflows rather than fully autonomous intelligence explosion. ^[rsi-andrej.md]

## Historical Context

AutoResearch builds upon decades of research into self-improving systems, including I.J. Good's "intelligence explosion" concept from 1965, Seed AI ideas, and modern self-improving code generation systems. Recent technical work such as the Self-Taught Optimizer (STOP) paper has shown language-model-driven systems improving code scaffolds recursively, though these remain partial forms of RSI rather than full recursive self-improvement. ^[rsi-andrej.md]

## See Also

- [[Recursive Self-Improvement]]
- [[LLM-as-Judge Quality Scoring]]
- [[Synthetic Preference Dataset Generation]]
- [[Hyperparameter Search]]
