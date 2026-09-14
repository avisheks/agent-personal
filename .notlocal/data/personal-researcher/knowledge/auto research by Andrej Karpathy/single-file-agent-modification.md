---
title: "Single-File Agent Modification"
summary: "A design pattern where AI agents are restricted to modifying only one specific file (train.py) containing the model, optimizer, and training loop to keep scope manageable and changes reviewable."
sources:
  - auto research by Andrej Karpathy/github-karpathy-autoresearch-ai-agents-running-research-on-single-gpu-nanochat-training-automatically-github.md
createdAt: 2026-05-25T16:00:59.404063+00:00
updatedAt: 2026-05-25T16:00:59.404063+00:00
---
# Single-File Agent Modification

**Single-File Agent Modification** is an approach to autonomous AI research where an AI agent is given permission to modify only a single source code file within a constrained experimental framework. This methodology enables AI agents to conduct iterative experiments on machine learning models while maintaining manageable scope and reviewable changes.

## Core Concept

The fundamental principle behind single-file agent modification is to provide AI agents with a focused, bounded environment for autonomous experimentation. Rather than allowing agents to modify entire codebases, this approach restricts modifications to a single critical file containing the model architecture, optimizer, and training loop. The agent operates within a fixed time budget and evaluates improvements using a consistent metric across all experiments. ^[autoresearch.md]

## Implementation Framework

### File Structure

A typical single-file agent modification setup consists of three primary components:

- **Preparation file** (`prepare.py`) - Contains fixed constants, one-time data preparation including dataset downloads and tokenizer training, and runtime utilities such as dataloaders and evaluation functions. This file remains unmodified by the agent.
- **Training file** (`train.py`) - The single file that the agent is permitted to edit. Contains the complete model implementation, optimizer configuration, and training loop. All aspects are available for modification including architecture, hyperparameters, optimizer choice, and batch size.
- **Program instructions** (`program.md`) - Baseline instructions that guide the agent's behavior and experimental approach. This file is edited by human researchers to refine the agent's research strategy. ^[autoresearch.md]

### Experimental Constraints

The framework operates under several key constraints designed to ensure fair comparison and manageable scope:

**Fixed Time Budget**: Training runs are limited to exactly 5 minutes of wall clock time, excluding startup and compilation phases. This constraint ensures that approximately 12 experiments can be conducted per hour, with roughly 100 experiments possible during an overnight session. ^[autoresearch.md]

**Single Metric Evaluation**: Performance is measured using validation bits per byte (val_bpb), where lower values indicate better performance. This metric is vocabulary-size-independent, allowing fair comparison across different architectural changes. ^[autoresearch.md]

**Isolated Modifications**: The agent can only modify the designated training file, keeping the experimental scope manageable and ensuring that all changes remain easily reviewable through standard diff tools. ^[autoresearch.md]

## Advantages and Design Benefits

### Scope Management

By restricting modifications to a single file, the approach prevents the complexity explosion that could occur if agents were permitted to modify entire codebases. This constraint ensures that human researchers can easily review and understand the changes made during autonomous experimentation. ^[autoresearch.md]

### Fair Comparison

The fixed time budget design ensures that all experiments are directly comparable regardless of the specific changes made by the agent. Whether the agent modifies model size, batch size, or architecture, each experiment operates under identical time constraints, enabling meaningful performance comparisons. ^[autoresearch.md]

### Platform Optimization

The time-constrained approach naturally leads agents to discover the most optimal model configuration for the specific hardware platform being used. This results in platform-specific optimizations that maximize performance within the given computational budget. ^[autoresearch.md]

## Limitations and Considerations

### Platform Dependency

Results obtained through single-file agent modification are inherently tied to the specific computational platform used for experiments. This means that optimal configurations discovered on one type of hardware may not transfer directly to other platforms, limiting the generalizability of findings across different computational environments. ^[autoresearch.md]

### Scope Restrictions

While the single-file constraint provides benefits in terms of manageability, it also limits the types of experiments that can be conducted. Certain research directions that require modifications to data preprocessing, evaluation metrics, or distributed training setups cannot be explored within this framework. ^[autoresearch.md]

## Autonomous Research Workflow

The typical workflow for single-file agent modification involves an iterative cycle where the AI agent modifies the training file, executes a 5-minute training run, evaluates the results against the validation metric, and decides whether to keep or discard the changes before proceeding to the next experiment. This process continues autonomously, allowing researchers to wake up to a log of experiments and potentially improved models after overnight runs. ^[autoresearch.md]

## Related Concepts

Single-file agent modification relates to several other concepts in machine learning and AI research, including [[Supervised Fine-Tuning (SFT)]] for model adaptation, [[Parameter-Efficient Fine-Tuning (PEFT)]] for constrained model modifications, and [[LLM-as-Judge Evaluation]] for automated assessment of model performance. The approach also connects to broader themes in [[Multi-Agent Orchestration]] and autonomous research systems.
