---
title: "AutoLab Experiments"
summary: "A practical implementation of autonomous experimentation in MLJAR Studio that uses structured problem definitions and AI agents to iteratively build and evaluate ML solutions while maintaining transparency through notebooks."
sources:
  - auto research by Andrej Karpathy/autoresearch-by-karpathy-and-the-future-of-autonomous-ai-research.md
createdAt: 2026-05-25T15:59:09.680024+00:00
updatedAt: 2026-05-25T15:59:09.680024+00:00
---
# AutoLab Experiments

**AutoLab Experiments** is an autonomous machine learning experimentation system that allows AI agents to iteratively build and evaluate machine learning solutions without manual intervention. The system is designed to automate the experimental loop of machine learning research while maintaining transparency and reproducibility through structured workflows and comprehensive documentation.

## Overview

AutoLab Experiments represents a practical implementation of autonomous experimentation concepts, where AI agents participate directly in the machine learning research process. Instead of manually modifying code, training models, and evaluating results, the system allows AI agents to iteratively perform these steps and search for better solutions automatically. ^[autoresearch-karpathy-autonomous-ai-research.md]

The system is built around the principle of structured problem definition combined with autonomous execution. Users describe their machine learning problem through a form-based interface, which generates instructions for AI agents that then conduct experiments systematically. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Core Workflow

### Problem Definition

The AutoLab workflow begins with a structured description of the machine learning task. Users complete a form that defines key elements including the dataset, evaluation metric, validation strategy, and number of trials to perform. Additional context can be provided such as feature specifications and requirements for feature engineering and model interpretation. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Agent Instructions Generation

From the problem definition, the system generates a file called `AGENTS.md` containing instructions that describe the machine learning problem and objectives for the AI agents. This file serves as a specification guiding how agents should approach the experiment and what metrics they should optimize. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Autonomous Execution

Once instructions are generated and reviewed, AI agents begin iteratively constructing and evaluating solutions. Each trial represents a proposed approach that may include changes in model configuration, feature processing, or training strategy. The agents explore different solutions automatically without requiring constant human supervision. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Key Features

### Transparency and Documentation

Every experiment trial is saved as a Jupyter Notebook containing the full plan, generated code, and resulting outputs. This design ensures that users can inspect how solutions were constructed and understand the reasoning behind each experiment. The approach treats transparency as essential for autonomous systems to maintain verifiability and reproducibility. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Real-time Monitoring

The system provides a dashboard where users can monitor experiment progress, displaying information such as completed trials, current best metrics, and overall execution status. This makes it easier to observe how the system explores different solutions over time. ^[autoresearch-karpathy-autonomous-ai-research.md]

### Structured Artifacts

Beyond basic model training, AutoLab experiments can generate additional artifacts including feature research analysis and model explainability outputs. These provide insights into feature importance and prediction drivers, supporting better decision-making in machine learning projects. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Relationship to AutoResearch

AutoLab Experiments shares conceptual foundations with [[AutoResearch]], created by Andrej Karpathy, which demonstrates autonomous machine learning experimentation through AI agents modifying training code directly. While AutoResearch serves as a minimal research prototype focusing on demonstrating the concept, AutoLab aims to integrate similar ideas into structured machine learning workflows suitable for practical development. ^[autoresearch-karpathy-autonomous-ai-research.md]

The key differences include AutoLab's form-based problem definition versus AutoResearch's code-based setup, comprehensive notebook outputs versus logs and results, and integrated dashboard tracking versus manual inspection. These differences reflect AutoLab's focus on providing a practical experimentation workflow for data scientists and ML practitioners. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Implementation Context

AutoLab Experiments is implemented within MLJAR Studio as part of a broader automated machine learning framework. The system builds upon concepts from traditional [[AutoML]] by extending automation beyond model selection and hyperparameter tuning to include feature engineering strategies, training procedures, and modeling logic exploration. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Practical Example

The system can be demonstrated through tasks such as predicting house prices from tabular datasets. In such cases, users define the regression problem through the form interface, specifying the target variable (such as `SalePrice`), evaluation metric (such as RMSE), and validation strategy (such as 5-fold cross-validation). The AI agents then automatically explore different approaches including feature engineering, model selection, and training configurations while generating comprehensive documentation of each trial. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Future Implications

AutoLab Experiments represents part of a broader trend toward AI-assisted research and development in machine learning. Rather than replacing data scientists, such systems change their role from running individual experiments to defining problems, selecting objectives, and interpreting results. The experimental loop of trying variations, training models, and evaluating metrics becomes increasingly automated while maintaining human oversight and understanding. ^[autoresearch-karpathy-autonomous-ai-research.md]

The approach extends traditional [[AutoML]] concepts by allowing AI agents to explore not only parameters but also feature engineering strategies, training procedures, and modeling logic. This evolution points toward systems that combine structured problem definitions, autonomous experimentation, reproducible outputs, and human-readable explanations as standard components of machine learning workflows. ^[autoresearch-karpathy-autonomous-ai-research.md]
