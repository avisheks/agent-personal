---
title: "Research Agenda Programming"
summary: "The practice of writing plain English instructions in a program.md file that directs an AI agent's experimental search strategy and constraints rather than writing code directly."
sources:
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:04:08.548159+00:00
updatedAt: 2026-05-25T16:04:08.548159+00:00
---
# Research Agenda Programming

Research Agenda Programming is a methodology for automating machine learning experimentation where human researchers write plain-language research directions that guide AI agents through systematic hypothesis testing and code modification. Rather than manually running experiments, researchers define the search space and constraints in natural language, allowing agents to autonomously execute hundreds of experiments overnight while maintaining scientific rigor through locked evaluation functions and git-based result tracking. ^[karpathy-autoresearch-explained.md]

## Core Methodology

Research Agenda Programming shifts the researcher's role from executing individual experiments to designing the overall search strategy. The human writes a research agenda in plain English that specifies what hypotheses to explore, what constraints to respect, and how to handle edge cases. An AI agent then reads this agenda alongside the full training codebase and autonomously runs experiment cycles: forming hypotheses, editing code, executing training runs, evaluating results, and either committing improvements or reverting failures. ^[karpathy-autoresearch-explained.md]

The methodology requires three distinct components with locked responsibilities. The preparation file handles data processing and evaluation functions that the agent cannot modify, ensuring consistent scoring across all experiments. The training file contains the model architecture and optimization code that the agent can freely edit. The program file contains the human-written research agenda in Markdown format that guides the agent's exploration strategy. ^[karpathy-autoresearch-explained.md]

## Implementation Architecture

### Experiment Loop Structure

The automated experiment loop follows a fixed sequence that maintains scientific validity while enabling autonomous operation. The agent reads the research agenda and current training code before forming each hypothesis. It then modifies the training file directly, executes a time-bounded training session, and extracts quantitative results including validation scores and memory usage. If the experiment improves the baseline metric, the changes are committed to version control and become the new starting point. Failed experiments trigger automatic rollback via git reset, preserving only successful modifications. ^[karpathy-autoresearch-explained.md]

Error handling within the loop allows for autonomous recovery from code failures. When training crashes produce no output, the agent reads error logs, attempts fixes, and re-runs the experiment. After multiple failed repair attempts, the agent abandons the current hypothesis and continues with the next experiment, ensuring overnight runs complete regardless of individual failures. ^[karpathy-autoresearch-explained.md]

### Constraint Design

The methodology relies on carefully designed constraints that prevent common failure modes in autonomous experimentation. The entire training codebase is limited to approximately 630 lines, small enough for the agent to maintain coherent understanding of all component interactions across successive modifications. The agent cannot modify data pipelines or evaluation functions, preventing gaming of the scoring metric. Package installation is restricted to pre-declared dependencies, avoiding environment drift that could invalidate comparisons between experiments. ^[karpathy-autoresearch-explained.md]

A simplicity criterion requires that minor improvements adding significant code complexity be rejected, preventing the codebase from growing unwieldy over extended sessions. These constraints collectively ensure that the search remains honest, results stay comparable, and the system maintains effectiveness across hundreds of experiments rather than degrading after initial runs. ^[karpathy-autoresearch-explained.md]

## Evaluation and Metrics

Research Agenda Programming uses single-metric optimization to maintain comparability across diverse architectural changes. The validation bits per byte metric measures encoding efficiency independent of vocabulary size, allowing agents to experiment with different tokenizers, layer counts, and attention mechanisms while keeping all results directly comparable. This metric choice prevents agents from gaming evaluation through vocabulary manipulation while supporting exploration of fundamental architectural variations. ^[karpathy-autoresearch-explained.md]

The locked evaluation function ensures scoring consistency across all experiments within a session. By preventing agent modification of the scoring logic, the methodology maintains scientific validity even when the agent makes radical changes to model architecture or training procedures. Results remain meaningful comparisons of actual model performance rather than artifacts of evaluation manipulation. ^[karpathy-autoresearch-explained.md]

## Applications and Results

### Production Deployments

Real-world applications of Research Agenda Programming have demonstrated significant improvements over manually optimized baselines. In documented cases, overnight runs have produced 11% training speedups on already well-optimized codebases and enabled smaller models to outperform larger hand-tuned alternatives through systematic architecture optimization. The methodology has successfully identified implementation bugs that human researchers missed, including missing scalar multipliers in attention mechanisms that affected model performance. ^[karpathy-autoresearch-explained.md]

The approach proves particularly valuable for small teams and startups that lack the headcount to run extensive manual experimentation. Single researchers can leverage overnight GPU time to explore hypothesis spaces that would require weeks of manual testing, equalizing access to systematic optimization against larger research organizations. ^[karpathy-autoresearch-explained.md]

### Domain-Specific Optimization

Research Agenda Programming enables systematic optimization for specific hardware and data combinations rather than relying on transferred hyperparameters from different contexts. The methodology finds configurations optimized for particular GPU memory constraints, training time budgets, and dataset characteristics through empirical search rather than theoretical assumptions. This capability becomes increasingly relevant as the field shifts toward smaller, task-specific models that require hardware-aware optimization. ^[karpathy-autoresearch-explained.md]

## Relationship to Automated Machine Learning

Research Agenda Programming differs from traditional [[AutoML]] approaches by operating at the source code level rather than within predefined hyperparameter grids. While tools like Optuna search specified parameter spaces, Research Agenda Programming allows agents to rewrite attention mechanisms, modify optimizers, and restructure training loops through direct code manipulation. This enables exploration of architectural variations that cannot be expressed as hyperparameter choices within fixed frameworks. ^[karpathy-autoresearch-explained.md]

The methodology maintains the systematic search benefits of AutoML while expanding the search space to include fundamental design decisions typically reserved for human researchers. By combining natural language research direction with autonomous code modification, it bridges the gap between high-level research strategy and low-level implementation optimization. ^[karpathy-autoresearch-explained.md]

## Limitations and Scope

Research Agenda Programming operates effectively within constrained environments but faces scalability challenges as complexity increases. The requirement for agents to maintain coherent understanding of the full codebase limits applicability to relatively small, focused training implementations. As codebases grow beyond the agent's context window capacity, the methodology's effectiveness degrades due to loss of global coherence in modifications. ^[karpathy-autoresearch-explained.md]

The approach works best for experiments that can produce meaningful results within short training windows, typically 5-minute sessions. This constraint makes it suitable for architecture search and hyperparameter optimization but less applicable to research requiring extended training runs or complex multi-stage procedures. The methodology also requires careful constraint design to prevent failure modes, making it more suitable for experienced researchers who understand the potential pitfalls of autonomous experimentation. ^[karpathy-autoresearch-explained.md]
