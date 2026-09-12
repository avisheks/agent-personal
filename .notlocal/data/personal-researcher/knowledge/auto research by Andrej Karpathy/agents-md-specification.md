---
title: "AGENTS.md Specification"
summary: "A structured file format that contains instructions describing machine learning problems and objectives to guide AI agents in autonomous experimentation workflows."
sources:
  - auto research by Andrej Karpathy/autoresearch-by-karpathy-and-the-future-of-autonomous-ai-research.md
createdAt: 2026-05-25T15:58:45.299822+00:00
updatedAt: 2026-05-25T15:58:45.299822+00:00
---
# AGENTS.md Specification

The **AGENTS.md Specification** is a structured file format that serves as an instruction set for AI agents conducting autonomous machine learning experiments. This specification defines how machine learning problems should be approached, what objectives should be optimized, and what artifacts should be generated during automated experimentation processes. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Overview

The AGENTS.md file acts as a specification that guides AI agents in performing machine learning research tasks. Rather than requiring direct code modification, this approach allows practitioners to describe their machine learning problem in a structured format that AI systems can interpret and act upon. The specification contains detailed instructions about the experimental objectives, evaluation metrics, validation strategies, and expected outputs. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Purpose and Function

The primary purpose of the AGENTS.md specification is to bridge the gap between human problem definition and autonomous AI experimentation. It transforms a structured description of a machine learning task into actionable instructions that AI agents can follow to conduct experiments systematically. ^[autoresearch-karpathy-autonomous-ai-research.md]

The specification enables AI agents to understand not only what model to build, but also how to approach feature engineering, what validation strategy to use, and what types of analysis should be included in the results. This comprehensive approach makes autonomous experimentation more than just automated model training—it becomes a structured research process. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Implementation in AutoLab

In [[MLJAR Studio]]'s AutoLab experiments, the AGENTS.md file is automatically generated from a structured form where users define key elements of their machine learning experiment. This includes the dataset, evaluation metric, validation strategy, and number of trials to be performed. Users can also specify additional requirements such as feature engineering exploration and model interpretation needs. ^[autoresearch-karpathy-autonomous-ai-research.md]

The generated specification contains instructions that describe the machine learning problem and the objectives for the AI agents. It serves as a comprehensive guide that determines how agents should approach the experiment and what metric they should optimize throughout the autonomous experimentation process. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Key Components

The AGENTS.md specification typically includes several essential components:

- **Problem Definition**: Clear description of the machine learning task and objectives
- **Evaluation Metrics**: Specific metrics that should be optimized during experimentation
- **Validation Strategy**: How model performance should be assessed (e.g., cross-validation)
- **Feature Requirements**: Guidelines for feature engineering and selection
- **Output Specifications**: What artifacts and explanations should be generated
- **Experimental Constraints**: Number of trials, time limits, or other boundaries

These components ensure that AI agents have sufficient context to conduct meaningful experiments while maintaining focus on the defined objectives. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Relationship to Autonomous Experimentation

The AGENTS.md specification is closely related to the broader concept of autonomous machine learning experimentation, as demonstrated in projects like [[AutoResearch]] by Andrej Karpathy. While AutoResearch focuses on direct code modification by AI agents, the AGENTS.md approach provides a more structured interface between human problem definition and AI-driven experimentation. ^[autoresearch-karpathy-autonomous-ai-research.md]

This specification-based approach enables [[Multi-Agent Orchestration]] where different AI agents can work together on various aspects of the machine learning pipeline, each guided by the same comprehensive instruction set. The structured nature of the specification also supports better [[trajectory-level-evaluation]] of the autonomous experimentation process. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Transparency and Reproducibility

One of the key advantages of the AGENTS.md specification is its support for transparent and reproducible autonomous experimentation. By clearly defining the problem, objectives, and expected outputs, the specification ensures that AI agents generate comprehensive documentation of their experimental process. ^[autoresearch-karpathy-autonomous-ai-research.md]

In implementations like AutoLab, each experiment trial guided by the AGENTS.md specification is saved as a complete Jupyter Notebook containing the full plan, generated code, and resulting outputs. This approach maintains transparency throughout the autonomous experimentation process, allowing practitioners to inspect how solutions were constructed and understand the reasoning behind each experimental step. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Future Implications

The AGENTS.md specification represents an evolution in how machine learning experiments are conducted, moving from manually driven processes toward AI-assisted research and development. This approach combines structured problem definitions with autonomous experimentation while maintaining human oversight and interpretability. ^[autoresearch-karpathy-autonomous-ai-research.md]

As autonomous experimentation systems continue to evolve, specifications like AGENTS.md may become standard components of machine learning workflows, particularly for tasks requiring exploration of many possible solutions. The specification format provides a foundation for more sophisticated [[agentic-planning-as-search]] approaches where AI agents can systematically explore the space of possible machine learning solutions. ^[autoresearch-karpathy-autonomous-ai-research.md]
