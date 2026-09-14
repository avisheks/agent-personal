---
title: "Program.md Agent Instructions"
summary: "Markdown files that serve as lightweight skills or instructions for AI agents, defining their research objectives and operational parameters in natural language."
sources:
  - auto research by Andrej Karpathy/github-karpathy-autoresearch-ai-agents-running-research-on-single-gpu-nanochat-training-automatically-github.md
createdAt: 2026-05-25T16:01:36.062804+00:00
updatedAt: 2026-05-25T16:01:36.062804+00:00
---
# Program.md Agent Instructions

**Program.md Agent Instructions** refers to a novel approach for directing autonomous AI agents in machine learning research, where human researchers write markdown files containing instructions that guide AI agents to iteratively modify and improve neural network training code.

## Overview

The program.md file serves as a lightweight "skill" that provides context and instructions to AI agents operating within an autonomous research framework. Rather than directly modifying Python training code, human researchers program the behavior of AI agents through these markdown instruction files, effectively creating an autonomous research organization that can experiment overnight without human intervention. ^[autoresearch-github.md]

## Core Design Philosophy

The approach represents a fundamental shift from traditional research methodology, where humans directly modify code, to a meta-programming paradigm where humans write instructions for AI agents that then modify the code. The system is designed around three key files: a fixed preparation script, a training file that agents can modify, and the program.md instruction file that humans iterate on to improve research progress. ^[autoresearch-github.md]

## Implementation Framework

The program.md instructions operate within a constrained environment designed for reproducible autonomous experimentation. AI agents work with a single-file training implementation that includes the full [[GPT-OSS-20B]] model architecture, [[Supervised Fine-Tuning (SFT)]] optimizer components, and training loop. The system enforces a fixed 5-minute time budget for each experiment, making results directly comparable regardless of architectural changes or hyperparameter modifications. ^[autoresearch-github.md]

## Autonomous Research Workflow

The instruction system enables a continuous experimentation cycle where agents modify training code, execute 5-minute training runs, evaluate results using validation bits per byte metrics, and decide whether to keep or discard changes. This process can run autonomously overnight, potentially completing approximately 100 experiments during an 8-hour period, with each experiment generating reviewable diffs and performance metrics. ^[autoresearch-github.md]

## System Architecture

The framework consists of three core components:

- **prepare.py**: Fixed constants, one-time data preparation including training data downloads and BPE tokenizer training, plus runtime utilities for data loading and evaluation
- **train.py**: The single file that agents modify, containing the complete GPT model, optimizer (Muon + AdamW), and training loop
- **program.md**: Baseline instructions for agents that humans iterate on to improve research outcomes ^[autoresearch-github.md]

## Scope and Constraints

The program.md instructions operate within a deliberately constrained scope to maintain manageability and reproducibility. Agents can only modify the single training file, which contains everything from model architecture to [[Hugging Face Transformers Library]] components and training hyperparameters. This constraint keeps the experimental space focused while still allowing for significant architectural and optimization innovations. ^[autoresearch-github.md]

## Platform Requirements

The instruction framework currently requires specific hardware configurations, including a single NVIDIA GPU and Python 3.10+ environment. The system uses fixed time budgets rather than fixed computational resources, meaning that results become platform-specific but directly comparable within the same hardware setup. This design choice optimizes for finding the best model architecture for a specific compute platform within the given time constraints. ^[autoresearch-github.md]

## Scaling Considerations

For deployment on smaller compute platforms, the instruction framework can be adapted by modifying dataset complexity, reducing vocabulary sizes, decreasing sequence lengths, and adjusting model depth parameters. These modifications require updating the program.md instructions to guide agents toward architectures appropriate for the available computational resources. ^[autoresearch-github.md]

## Research Methodology

The system evaluates progress using validation bits per byte (val_bpb) as the primary metric, which remains vocabulary-size-independent and allows fair comparison across different architectural changes. The fixed time budget approach ensures that approximately 12 experiments can be completed per hour, with around 100 experiments possible during an overnight research session. ^[autoresearch-github.md]
