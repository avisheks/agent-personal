---
title: "AutoML vs Autoresearch Distinction"
summary: "The difference between traditional AutoML systems that use random variations or evolutionary algorithms versus AI agents that can read research papers, develop hypotheses, and write arbitrary code."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:06:20.351374+00:00
updatedAt: 2026-05-25T16:06:20.351374+00:00
---
# AutoML vs Autoresearch Distinction

**AutoML vs Autoresearch Distinction** refers to the fundamental differences between traditional automated machine learning (AutoML) approaches and newer AI agent-driven research systems, particularly as highlighted by Andrej Karpathy's "autoresearch" experiment in early 2026.

## Overview

The distinction became prominent when AI researcher Andrej Karpathy conducted an experiment where he deployed an AI coding agent to run 700 experiments over two days to optimize the training of a small language model. This system, which Karpathy termed "autoresearch," discovered 20 optimizations that improved training time and achieved an 11% speed-up when applied to a larger model. ^[karpathy-loop-fortune.md]

## Key Differences

### AutoML Characteristics

AutoML represents traditional automated machine learning systems that have been used by researchers at Google, Microsoft, and other AI labs for years. These systems use optimization loops and series of experiments to find optimal data, model architectures, and hyperparameter tuning. However, AutoML systems typically depend on random variations or evolutionary algorithms to decide which changes to try, rather than intelligent reasoning about potential improvements. ^[karpathy-loop-fortune.md]

### Autoresearch Characteristics

Autoresearch systems, by contrast, employ AI agents that can read AI research papers and develop hypotheses for improvements. These systems feature an actual large language model writing arbitrary code, learning from previous experiments, and having access to the internet. The agent can modify code files, optimize for objectively testable metrics, and operate within fixed time limits for each experimental loop. ^[karpathy-loop-fortune.md]

## The Karpathy Loop Framework

The autoresearch approach has been characterized as following "the Karpathy Loop," which consists of three core components:

- An agent with access to a single file that it can modify
- A single, objectively testable metric that the agent can optimize for  
- A fixed time limit for how long each experiment can run

The framework also includes clear instructions for the agent, constraints defining what should not be changed, and stopping criteria indicating when to conclude experiments and report results. ^[karpathy-loop-fortune.md]

## Scalability and Future Implications

Karpathy noted that while his initial autoresearch system was designed for a single agent working on 630 lines of Python code, the approach could scale to frontier AI models with much larger codebases. He envisions future systems where multiple AI agents explore different optimizations in parallel, with swarms of agents collaborating to tune smaller models and promoting promising ideas to increasingly larger scales. ^[karpathy-loop-fortune.md]

The researcher emphasized that any metric that is reasonably efficient to evaluate can be "autoresearched" by an agent swarm, suggesting broad applicability beyond machine learning optimization to various process optimization challenges. ^[karpathy-loop-fortune.md]

## Critical Perspectives

Some critics argued that Karpathy had essentially rediscovered aspects of existing AutoML processes. However, Karpathy distinguished his approach from traditional methods like neural architecture search, describing older AutoML techniques as "such a weak version of this that it's in its own category of totally useless by comparison." He emphasized that autoresearch involves actual LLMs writing arbitrary code and learning from previous experiments with internet access, capabilities not present in traditional AutoML systems. ^[karpathy-loop-fortune.md]

## Broader Applications

The autoresearch framework has implications beyond machine learning research, with commentators noting that its basic components could be applied to many other agentic systems for process optimization. The approach represents a shift from algorithmic optimization methods to AI agent-driven research that can reason about and hypothesize improvements based on available knowledge and experimental results. ^[karpathy-loop-fortune.md]
