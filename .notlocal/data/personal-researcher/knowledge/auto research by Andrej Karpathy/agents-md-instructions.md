---
title: "AGENTS.md Instructions"
summary: "A structured specification file that contains instructions describing the machine learning problem and objectives to guide AI agents in autonomous experimentation workflows."
sources:
  - auto research by Andrej Karpathy/autoresearch-by-karpathy-and-the-future-of-autonomous-ai-research.md
createdAt: 2026-05-25T15:59:49.894858+00:00
updatedAt: 2026-05-25T15:59:49.894858+00:00
---
# AGENTS.md Instructions

**AGENTS.md Instructions** is a structured specification format used in autonomous machine learning experimentation systems to guide AI agents in conducting research and model development tasks. The format serves as a bridge between human-defined machine learning problems and AI-driven experimental workflows.

## Overview

AGENTS.md Instructions represent a key component in systems that enable AI agents to participate directly in the machine learning research loop. Rather than requiring manual modification of training scripts, these instructions provide a structured way to describe machine learning problems, objectives, and constraints that AI agents can interpret and act upon. ^[autoresearch-karpathy-autonomous-ai-research.md]

The concept emerged from the need to make autonomous experimentation more accessible and structured for practical machine learning development. Instead of editing training scripts directly, practitioners can describe their machine learning task through structured forms, which are then converted into instructions for AI agents. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Structure and Components

AGENTS.md Instructions typically contain several key elements that define the experimental framework:

### Problem Definition
The instructions include a clear description of the machine learning task, including the dataset, target variable, and evaluation metrics. This provides the foundational context that guides how agents should approach the experiment. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Experimental Objectives
The file specifies what the AI agents should optimize for, such as minimizing RMSE using cross-validation, and may include additional requirements like feature engineering and model explainability. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Constraints and Requirements
Instructions define how results should be reported, what artifacts should be generated, and any specific methodological requirements that must be followed during experimentation. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Implementation in AutoLab

In [[AutoLab]] experiments within MLJAR Studio, AGENTS.md Instructions are generated automatically from structured problem descriptions. The workflow begins with users filling a form that defines key elements such as the dataset, evaluation metric, validation strategy, and number of trials to be performed. ^[autoresearch-karpathy-autonomous-ai-research.md]

The system converts this structured input into comprehensive instructions that serve as specifications for AI agents. These instructions guide how agents should approach the experiment and what metrics they should optimize, ensuring that the autonomous experimentation process remains aligned with the user's objectives. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Relationship to AutoResearch

The concept builds upon ideas demonstrated in [[AutoResearch]] by Andrej Karpathy, which showed how AI agents can modify training code, run experiments, and iteratively search for improvements. While AutoResearch focuses on direct code modification, AGENTS.md Instructions provide a more structured approach that separates problem definition from implementation details. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Transparency and Reproducibility

A key design principle of AGENTS.md Instructions is maintaining transparency in autonomous experimentation. Systems using this approach typically generate full documentation of each experimental trial, including the reasoning behind decisions and the complete experimental setup. ^[autoresearch-karpathy-autonomous-ai-research.md]

Each trial performed by AI agents following these instructions is often saved as a complete record (such as a Jupyter Notebook) containing the experiment plan, generated code, and all outputs. This ensures that every experiment remains transparent and reproducible, allowing practitioners to inspect exactly how solutions were constructed. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Applications

AGENTS.md Instructions enable AI agents to conduct comprehensive machine learning research that goes beyond simple model training. Agents can be instructed to perform feature research, model explainability analysis, and structured exploration of different modeling approaches while maintaining detailed documentation of their process. ^[autoresearch-karpathy-autonomous-ai-research.md]

The format supports complex experimental workflows where agents must balance multiple objectives, such as optimizing predictive performance while ensuring model interpretability and generating comprehensive feature analysis. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Future Implications

AGENTS.md Instructions represent part of a broader evolution in machine learning development, where AI agents increasingly participate in the experimental process. This approach changes the role of data scientists from manually running individual experiments to defining problems, selecting objectives, and interpreting results while the experimental loop becomes increasingly automated. ^[autoresearch-karpathy-autonomous-ai-research.md]

The format supports the development of systems that combine structured problem definitions, autonomous experimentation, reproducible outputs, and human-readable explanations - elements that may become standard components of future machine learning workflows. ^[autoresearch-karpathy-autonomous-ai-research.md]
