---
title: "Self-Taught Optimizer (STOP)"
summary: "A language-model-driven system that improves code scaffolds recursively, representing a partial form of recursive self-improvement in practice."
sources:
  - recursive self improvement/rsi-andrej.md
createdAt: 2026-05-25T15:57:44.409890+00:00
updatedAt: 2026-05-25T15:57:44.409890+00:00
---
# Self-Taught Optimizer (STOP)

**Self-Taught Optimizer (STOP)** is a framework for recursive self-improvement in AI systems where language models autonomously optimize and improve code scaffolds through iterative experimentation. STOP represents a practical implementation of bounded recursive self-improvement, moving the concept from theoretical speculation to deployable engineering systems. ^[rsi-andrej.md]

## Overview

STOP demonstrates how [[LLM-as-Judge Quality Scoring]] systems can be used to create feedback loops where AI models propose modifications to training code, evaluate the results, and iteratively improve performance with minimal human intervention. The system operates within constrained experimental environments, making it a form of "soft RSI" rather than full autonomous intelligence explosion. ^[rsi-andrej.md]

## Technical Approach

The STOP framework follows a cyclical process:

- An LLM proposes changes to ML training code
- The system runs experiments automatically  
- Performance metrics are evaluated programmatically
- Improvements are retained while unsuccessful changes are discarded
- The cycle repeats with the enhanced codebase

This approach leverages [[Supervised Fine-Tuning (SFT)]] principles and [[Parameter-Efficient Fine-Tuning (PEFT)]] techniques to optimize model training pipelines recursively. ^[rsi-andrej.md]

## Relationship to Recursive Self-Improvement

STOP represents a bounded form of recursive self-improvement that focuses on optimizing specific components rather than rewriting entire architectures. The system demonstrates practical RSI capabilities including:

- Hyperparameter search automation
- Training pipeline optimization  
- Code generation and refinement
- Experiment orchestration
- [[Agentic Planning as Search]] for improvement strategies

However, STOP explicitly operates within constrained domains and does not attempt full architectural redesign or escape from human oversight. ^[rsi-andrej.md]

## Applications in Foundation Models

For foundation model development, STOP-like systems enable automation of traditionally manual workflows:

- Model evaluation pipelines
- [[Reward Modeling]] optimization
- Feature engineering automation
- [[Hybrid Retrieval]] system tuning
- Prompt optimization cycles
- [[Synthetic Preference Dataset Generation]]

These applications are particularly relevant for systems requiring continuous optimization, such as recommendation engines and advertising platforms. ^[rsi-andrej.md]

## Distinction from Full RSI

STOP represents "soft RSI" focused on engineering workflow acceleration rather than "hard RSI" involving fully autonomous intelligence explosion. The system maintains human oversight and operates within predefined experimental boundaries, making it a practical stepping stone toward more advanced self-improving systems. ^[rsi-andrej.md]

## Related Concepts

STOP builds upon several foundational concepts in AI optimization and [[Multi-Agent Orchestration]], representing a convergence of automated experimentation, [[Constitutional AI for Ads]], and iterative improvement methodologies. The framework demonstrates how [[Chain-of-Thought Reasoning]] can be applied to systematic code optimization tasks. ^[rsi-andrej.md]
