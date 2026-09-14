---
title: "AutoML vs Agent-Based Optimization"
summary: "The distinction between traditional AutoML systems that use random variations or evolutionary algorithms versus AI agents that can read research papers, develop hypotheses, and write arbitrary code for optimization."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:04:36.938911+00:00
updatedAt: 2026-05-25T16:04:36.938911+00:00
---
# AutoML vs Agent-Based Optimization

**AutoML vs Agent-Based Optimization** refers to the distinction between traditional automated machine learning approaches and newer AI agent-driven optimization systems that can autonomously conduct research and experimentation.

## Traditional AutoML Approach

AutoML represents an established methodology that uses optimization loops and series of experiments to find optimal configurations for AI systems. AutoML systems focus on finding the best data to use for AI, determining optimal model architectures, and tuning those architectures for improved performance. These systems typically depend on random variations or various evolutionary algorithms to decide which changes to try during the optimization process. ^[karpathy-loop-fortune.md]

Researchers at major technology companies including Google and Microsoft have been using AutoML approaches for years as part of their standard machine learning workflows. One specific AutoML method, neural architecture search, provides an automated way to optimize the design of AI models. ^[karpathy-loop-fortune.md]

## Agent-Based Optimization

Agent-based optimization represents a more recent approach that leverages AI agents capable of reading research papers, developing hypotheses, and making informed decisions about which improvements to implement. Unlike traditional AutoML systems, these agents can write arbitrary code, learn from previous experiments, and access internet resources to inform their optimization strategies. ^[karpathy-loop-fortune.md]

A notable example of this approach is the "autoresearch" system developed by AI researcher Andrej Karpathy. In his experiment, an AI coding agent ran continuously for two days, conducting 700 different experiments to improve the training of a small [[Qwen3 Language Model]]. The agent discovered 20 optimizations that improved training time, and when applied to a larger model, resulted in an 11% speed improvement. ^[karpathy-loop-fortune.md]

## The Karpathy Loop Framework

The agent-based approach has been formalized into what some analysts call "the Karpathy Loop," which consists of three core components:

- An agent with access to a single file that it can modify
- A single, objectively testable metric that the agent can optimize for  
- A fixed time limit for how long each experiment can run

The framework also emphasizes clear instruction design, including constraints that specify what the agent should not do or change, and stopping criteria that indicate when the agent should cease experimentation and report results. ^[karpathy-loop-fortune.md]

## Key Differences

The fundamental distinction between AutoML and agent-based optimization lies in their decision-making capabilities. Traditional AutoML methods like neural architecture search have been characterized as "such a weak version" compared to agent-based systems that represent "an actual LLM writing arbitrary code, learning from previous experiments, with access to the internet." ^[karpathy-loop-fortune.md]

Agent-based systems can potentially scale to collaborative multi-agent environments where multiple AI agents explore different optimizations and experiments in parallel, emulating "a research community" rather than a single researcher. This approach can theoretically be applied to any metric that is reasonably efficient to evaluate or has efficient proxy metrics. ^[karpathy-loop-fortune.md]

## Implications for AI Research

The shift toward agent-based optimization has significant implications for how AI laboratories conduct research. The approach represents what some consider "the final boss battle" for frontier AI labs, as it enables automated research processes that could accelerate progress in AI development. While current implementations work on relatively simple codebases, the underlying principles can scale to larger, more complex systems through collaborative agent swarms. ^[karpathy-loop-fortune.md]
