---
title: "AutoResearch Framework"
summary: "An open-source project by Andrej Karpathy that demonstrates autonomous machine learning experimentation where AI agents iteratively modify code, run experiments, and evaluate results to improve performance."
sources:
  - recursive self improvement/rsi-andrej.md
  - auto research by Andrej Karpathy/autoresearch-by-karpathy-and-the-future-of-autonomous-ai-research.md
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T15:56:48.571033+00:00
updatedAt: 2026-05-25T15:56:48.571033+00:00
---
# AutoResearch Framework

The **AutoResearch Framework** is an autonomous machine learning experimentation system developed by [[Andrej Karpathy]] that enables AI agents to iteratively modify training code, execute experiments, and optimize model performance without human intervention. The framework represents a practical implementation of [[recursive self-improvement]] concepts in machine learning research, where AI systems participate directly in the experimental loop rather than requiring manual hypothesis testing and code modification. ^[rsi-andrej.md]

## Overview

AutoResearch automates the traditional machine learning research cycle of forming hypotheses, editing code, running training sessions, evaluating results, and iterating based on outcomes. Instead of researchers manually conducting 8-10 experimental cycles per day, the system enables AI agents to run continuous 5-minute experiments overnight, potentially executing hundreds of trials in a single session. ^[autoresearch-karpathy-autonomous-ai-research.md]

The framework gained significant attention after Karpathy demonstrated that an AI agent running 700 experiments over two days achieved an 11% performance improvement on his already-optimized GPT-2 training codebase, reducing time-to-GPT-2-quality from 2.02 hours to 1.80 hours. The agent also discovered implementation bugs that had been missed during manual optimization. ^[karpathy-autoresearch-explained.md]

## Architecture and Components

### Core Files Structure

The AutoResearch system consists of three essential files with distinct roles:

- **prepare.py**: Contains data download, tokenizer training, and evaluation functions. This file is locked after initial setup and cannot be modified by the agent, ensuring consistent scoring across experiments
- **train.py**: The primary target for agent modifications, containing model architecture, optimizer configuration, and training loop implementation. All components within this 630-line file are available for agent experimentation
- **program.md**: A plain English instruction file that defines the research agenda, experimental constraints, and agent operating parameters ^[karpathy-autoresearch-explained.md]

### Experimental Loop Process

The autonomous experimentation follows a structured cycle:

1. **Context Reading**: The agent reads program.md instructions and the complete train.py codebase
2. **Hypothesis Formation**: The agent decides on specific modifications to test
3. **Code Modification**: Direct editing of train.py to implement the proposed changes
4. **Experiment Execution**: A 5-minute training session with output logging
5. **Result Evaluation**: Extraction of validation score (val_bpb) and memory usage metrics
6. **Decision Making**: Improvements are committed via git; failures trigger automatic reversion
7. **Error Handling**: Crashed experiments prompt log analysis, attempted fixes, and re-execution ^[karpathy-autoresearch-explained.md]

## Technical Constraints and Design Principles

### Bounded Environment Design

AutoResearch operates within carefully designed constraints that enable reliable agent operation:

- **630-Line Limit**: The entire training codebase is maintained below 630 lines to ensure the agent can comprehend the full system within its context window
- **Single Metric Optimization**: All experiments are scored using validation bits per byte (val_bpb), which remains comparable across different architectures and vocabulary sizes
- **Hardware Constraints**: Experiments are designed for single GPU execution with 5-minute time budgets ^[karpathy-autoresearch-explained.md]

### Failure Mode Prevention

The framework incorporates specific constraints to prevent common autonomous system failures:

- **Evaluation Lock**: Agents cannot modify data pipelines or evaluation functions, preventing score manipulation
- **Package Restrictions**: No new dependencies can be installed beyond pre-declared requirements
- **Simplicity Criterion**: Minor improvements requiring significant code complexity are discouraged to maintain system coherence ^[karpathy-autoresearch-explained.md]

## Practical Applications and Results

### Real-World Performance

The framework has demonstrated practical value across multiple implementations:

- **Karpathy's Implementation**: 700 experiments yielding 20 genuine improvements and 11% performance gains on pre-optimized code
- **Shopify CEO Implementation**: Overnight optimization producing a 0.8B parameter model that outperformed a hand-tuned 1.6B baseline by 19%
- **Bug Discovery**: Automated detection of implementation errors missed during manual code review, including QK-Norm scalar multiplier issues ^[karpathy-autoresearch-explained.md]

### Target Use Cases

AutoResearch addresses specific challenges in machine learning development:

- **Small Teams**: Enables systematic experimentation without large research teams or compute clusters
- **Domain-Specific Optimization**: Finds hardware-specific configurations rather than relying on transferred hyperparameters
- **Hypothesis Testing Acceleration**: Removes execution bottlenecks for researchers with more ideas than time to test them ^[karpathy-autoresearch-explained.md]

## Relationship to Broader AI Trends

### Recursive Self-Improvement Context

AutoResearch represents a practical implementation of [[recursive self-improvement]] concepts, demonstrating "soft RSI" where AI systems accelerate AI engineering workflows rather than achieving full autonomous intelligence explosion. The framework exemplifies the transition from philosophical speculation about recursive self-improvement to deployable engineering systems. ^[rsi-andrej.md]

### Alternative Implementations

Similar concepts have been implemented in other frameworks, such as **AutoLab experiments** in MLJAR Studio, which provides structured problem definition through forms rather than direct code modification, generating experiments as Jupyter Notebooks with full transparency and dashboard monitoring. ^[autoresearch-karpathy-autonomous-ai-research.md]

## Limitations and Considerations

The AutoResearch framework operates as a research prototype with specific limitations:

- **Code-Based Interface**: Requires direct interaction with Python scripts, potentially limiting accessibility for users preferring structured workflows
- **Experiment Transparency**: Results are primarily observable through logs and metrics, with limited built-in experiment tracking and comparison capabilities
- **Scope Constraints**: Designed for short training experiments rather than complex, long-running research projects ^[autoresearch-karpathy-autonomous-ai-research.md]

## Future Implications

AutoResearch demonstrates a shift in machine learning research methodology, where human researchers focus on defining problems and research directions while AI agents handle the mechanical aspects of experimentation. This approach aligns with broader trends toward [[AI-assisted research and development]], where autonomous systems participate directly in the scientific process while maintaining human oversight and interpretation of results. ^[autoresearch-karpathy-autonomous-ai-research.md]

The framework's success suggests potential applications in various domains where systematic experimentation and optimization are required, particularly in scenarios involving measurable objectives and constrained search spaces.
