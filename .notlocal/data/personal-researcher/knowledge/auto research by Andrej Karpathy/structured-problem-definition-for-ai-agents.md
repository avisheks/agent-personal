---
title: "Structured Problem Definition for AI Agents"
summary: "The approach of defining machine learning tasks through forms and specifications that generate instructions for AI agents rather than requiring direct code modification."
sources:
  - auto research by Andrej Karpathy/autoresearch-by-karpathy-and-the-future-of-autonomous-ai-research.md
createdAt: 2026-05-25T15:59:01.535772+00:00
updatedAt: 2026-05-25T15:59:01.535772+00:00
---
# Structured Problem Definition for AI Agents

**Structured Problem Definition for AI Agents** refers to the systematic approach of describing machine learning tasks in a formal, standardized way that enables AI agents to autonomously conduct experiments and research. Rather than requiring direct code modification, this approach uses structured specifications to guide AI systems in exploring solutions, running experiments, and optimizing results.

## Overview

The concept emerged from the need to make autonomous AI experimentation more accessible and practical for everyday machine learning workflows. Instead of AI agents directly editing training scripts, structured problem definition involves creating formal descriptions of machine learning tasks that serve as instructions for autonomous systems. ^[autoresearch-karpathy-autonomous-ai-research.md]

This approach transforms the traditional experimental loop where humans manually modify code, train models, and evaluate results. By providing clear specifications, AI agents can iteratively perform these steps and search for better solutions without constant human supervision. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Key Components

### Problem Specification Forms

Structured problem definition typically begins with users filling forms that define key elements of the experiment, such as the dataset, evaluation metric, validation strategy, and number of trials to be performed. Users can also provide additional context, including which features should be used or whether feature engineering and model interpretation should be explored. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Instruction Generation

From the structured input, systems generate instruction files (such as `AGENTS.md`) that contain detailed descriptions of the machine learning problem and objectives for AI agents. These files serve as specifications that guide how agents should approach the experiment and what metrics they should optimize. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Experimental Parameters

The structured definition includes critical experimental parameters such as:
- Target variables and evaluation metrics
- Validation strategies (e.g., cross-validation settings)
- Feature engineering requirements
- Model explainability needs
- Number of trials to perform

## Implementation Approaches

### Code-Based Systems

Some implementations, like [[AutoResearch]], allow AI agents to modify training code directly. These systems require users to prepare the training environment, define the experiment setup, and configure files that the AI agent can modify. This approach works well for researchers comfortable with Python scripts but may be less accessible for data scientists preferring structured workflows. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Form-Based Systems

Alternative implementations use structured forms to capture problem definitions, which are then converted into instructions for AI agents. This approach, exemplified by AutoLab experiments, makes autonomous experimentation more accessible by providing a graphical interface for problem specification rather than requiring direct code interaction. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Advantages

### Accessibility

Structured problem definition makes autonomous experimentation accessible to data scientists who prefer structured workflows over direct code manipulation. By using forms and standardized specifications, practitioners can define complex machine learning problems without needing to write experimental scripts from scratch. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Transparency and Reproducibility

This approach enables better experiment tracking and organization compared to direct code modification systems. Each experiment can be documented with clear specifications, making it easier to understand the reasoning behind specific changes and reproduce results. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Systematic Exploration

By providing clear objectives and constraints, structured definitions enable AI agents to systematically explore solution spaces rather than making random modifications. This leads to more efficient experimentation and better optimization of machine learning solutions. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Relationship to AutoML

Structured problem definition extends traditional [[AutoML]] concepts beyond model selection and hyperparameter tuning. While traditional AutoML systems automate specific aspects of model development, structured problem definition allows AI agents to explore feature engineering strategies, training procedures, and even parts of the modeling logic. ^[autoresearch-karpathy-autonomous-ai-research.md]

This represents an evolution from manually driven experimentation toward AI-assisted research and development, where practitioners focus on defining problems and interpreting results while AI agents handle the experimental loop. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Future Directions

The approach points toward systems that combine structured problem definitions, autonomous experimentation, reproducible outputs, and human-readable explanations. These systems may become standard parts of machine learning workflows, especially for tasks requiring exploration of many possible solutions. ^[autoresearch-karpathy-autonomous-ai-research.md]

As the field evolves, structured problem definition is expected to play an increasingly important role in making AI-driven experimentation both powerful and accessible to a broader range of machine learning practitioners. ^[autoresearch-karpathy-autonomous-ai-research.md]
