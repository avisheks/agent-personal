---
title: "AutoML"
summary: "An automated machine learning process that uses optimization loops and experiments to find optimal data, model architectures, and hyperparameters, typically relying on random variations or evolutionary algorithms."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:04:52.346812+00:00
updatedAt: 2026-05-25T16:04:52.346812+00:00
---
# AutoML

**AutoML** (Automated Machine Learning) is a process that uses optimization loops and series of experiments to automatically find the best data, model architecture, and hyperparameters for AI systems. AutoML systems have been used by researchers at major AI labs including Google and Microsoft for years to automate various aspects of machine learning model development. ^[fortune-karpathy-loop.md]

## Core Components

AutoML typically focuses on three main areas of optimization:

- **Data selection**: Finding the optimal datasets to use for training
- **Model architecture**: Determining the best neural network structure
- **Hyperparameter tuning**: Optimizing model configuration settings

These systems generally rely on random variations or evolutionary algorithms to decide which changes to try, rather than using AI agents that can develop hypotheses based on research literature. ^[fortune-karpathy-loop.md]

## Relationship to Modern AI Agent Systems

Recent developments have extended the AutoML concept by incorporating [[LLM-as-Judge Evaluation]] capabilities and agentic systems. Andrej Karpathy's "autoresearch" experiment demonstrated a more sophisticated approach where an AI agent could read research papers, develop hypotheses, and write arbitrary code to optimize model training. This represents a significant advancement over traditional AutoML methods. ^[fortune-karpathy-loop.md]

The key difference is that modern agentic AutoML systems can leverage large language models to understand research literature and make informed decisions about optimization strategies, rather than relying solely on random search or evolutionary approaches. ^[fortune-karpathy-loop.md]

## Neural Architecture Search

One specific AutoML technique is **neural architecture search**, which automatically optimizes the design of AI models. However, this approach has been characterized as significantly less powerful than agent-based systems that can write code and learn from previous experiments with internet access. ^[fortune-karpathy-loop.md]

## The Karpathy Loop Framework

A modern interpretation of AutoML principles, called "the Karpathy Loop," consists of three components:

- An agent with access to a single file that it can modify
- A single, objectively testable metric that the agent can optimize for  
- A fixed time limit for how long each experiment can run

This framework can potentially be applied to optimize any metric that is reasonably efficient to evaluate or has efficient proxy metrics available. ^[fortune-karpathy-loop.md]

## Future Directions

The evolution of AutoML toward collaborative multi-agent systems represents a significant advancement in automated research capabilities. Future systems may involve swarms of AI agents exploring different optimizations in parallel, with promising ideas promoted to increasingly larger scales of experimentation. ^[fortune-karpathy-loop.md]
