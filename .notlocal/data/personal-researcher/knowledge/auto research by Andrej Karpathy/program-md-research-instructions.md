---
title: "Program.md Research Instructions"
summary: "A plain English Markdown file that serves as the research agenda, telling the AI agent what to explore, what constraints to respect, and how to handle edge cases during autonomous experimentation."
sources:
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:03:10.612295+00:00
updatedAt: 2026-05-25T16:03:10.612295+00:00
---
# Program.md Research Instructions

**Program.md Research Instructions** refers to the plain English instruction file that serves as the research agenda in automated machine learning experimentation systems. This approach represents a shift from direct code manipulation to high-level research direction specification, where human researchers define experimental objectives and constraints in natural language rather than implementing individual experiments manually.

## Overview

The program.md file functions as the primary interface between human researchers and AI agents conducting automated experiments. Rather than editing training code directly, researchers write comprehensive instructions that guide an agent's exploration of the experimental space. This methodology emerged as part of broader trends toward [[agentic-planning-as-search]] and represents a fundamental change in how ML research productivity is achieved. ^[karpathy-autoresearch-explained.md]

The instruction file contains the complete operating parameters for a research session: what the research is trying to accomplish, what kinds of experiments to run, what the hard limits are, and how to handle edge cases. Karpathy describes this as "programming the research org in Markdown," capturing how the durable artifact from an overnight experimental run isn't the code changes made by the agent, but the instruction file that produced them. ^[karpathy-autoresearch-explained.md]

## Core Components

### Research Objectives
The instruction file specifies the primary goals of the experimental session, including target metrics for optimization and success criteria. These objectives must be concrete enough for an automated agent to evaluate progress systematically. ^[karpathy-autoresearch-explained.md]

### Experimental Constraints
Hard constraints define the boundaries of acceptable experimentation, preventing the agent from modifying critical components like data pipelines or evaluation functions. These constraints close specific failure modes - without evaluation locks, agents could rewrite scoring functions to report false improvements, and without simplicity rules, codebases grow too complex for coherent agent understanding across successive sessions. ^[karpathy-autoresearch-explained.md]

### Hypothesis Generation Guidelines
The file provides direction on what types of changes to explore, from architectural modifications to optimization strategies. The sharper and more specific these guidelines, the more targeted the agent's search becomes. ^[karpathy-autoresearch-explained.md]

## Implementation in Practice

### Autoresearch Framework
In Karpathy's autoresearch system, the program.md file works alongside two other components: prepare.py (locked after first run, handling data and evaluation) and train.py (the only file the agent modifies). The instruction file serves as the human-maintained component that persists across experimental sessions, while the training code evolves based on successful experiments. ^[karpathy-autoresearch-explained.md]

### Constraint Design
Effective program.md files incorporate constraints that maintain experimental integrity while allowing meaningful exploration. The [[supervised-fine-tuning-sft]] process benefits from similar constraint-based approaches, where clear boundaries prevent [[catastrophic-forgetting-in-fine-tuning]] while enabling productive parameter updates. ^[karpathy-autoresearch-explained.md]

## Research Impact

### Productivity Transformation
The program.md approach changes the fundamental economics of ML experimentation for small teams and individual researchers. Instead of manually running 8-10 experimental cycles per day with significant waiting time, researchers can specify objectives once and let automated systems execute hundreds of experiments overnight. ^[karpathy-autoresearch-explained.md]

### Skill Reorientation
This methodology shifts researcher productivity from experiment execution to search design. The critical skills become writing clear experimental objectives, encoding domain knowledge in natural language, and designing constraint systems that guide productive exploration while preventing failure modes. ^[karpathy-autoresearch-explained.md]

## Applications Beyond Core Framework

### Domain-Specific Adaptation
The program.md pattern extends beyond the original autoresearch implementation to any scenario where systematic experimentation can be automated. Founders building domain-specific models can use this approach to find configurations optimized for their specific data and hardware rather than relying on transferred hyperparameters from public repositories. ^[karpathy-autoresearch-explained.md]

### Integration with Modern Architectures
The instruction file approach works particularly well with contemporary model architectures that support rapid experimentation. Systems using [[mixture-of-experts-moe]] or [[parameter-efficient-fine-tuning-peft]] can benefit from automated exploration of architectural configurations guided by well-designed program.md files. ^[karpathy-autoresearch-explained.md]

## Related Concepts

The program.md methodology connects to broader themes in automated ML research, including [[llm-as-judge-quality-scoring]] for evaluation automation and [[trajectory-level-evaluation]] for assessing experimental sequences. The approach also relates to [[human-in-the-loop-architecture]] patterns, where human judgment focuses on high-level direction while automated systems handle execution details.
