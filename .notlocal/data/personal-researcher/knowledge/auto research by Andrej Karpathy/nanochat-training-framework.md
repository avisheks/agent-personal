---
title: "Nanochat Training Framework"
summary: "A simplified single-GPU implementation for training small language models that serves as the foundation for autonomous research experiments."
sources:
  - auto research by Andrej Karpathy/github-karpathy-autoresearch-ai-agents-running-research-on-single-gpu-nanochat-training-automatically-github.md
createdAt: 2026-05-25T16:01:51.929799+00:00
updatedAt: 2026-05-25T16:01:51.929799+00:00
---
# Nanochat Training Framework

The **Nanochat Training Framework** is an autonomous AI research system designed to enable AI agents to conduct machine learning experiments independently on single-GPU setups. The framework allows agents to modify training code, run experiments, evaluate results, and iterate automatically without human intervention during the research process. ^[autoresearch-github.md]

## Overview

The framework operates on the principle of giving an AI agent a small but real [[LLM]] training setup and allowing it to experiment autonomously overnight. The agent modifies the code, trains for 5 minutes, checks if the result improved, keeps or discards changes, and repeats this cycle. Users wake up to a log of experiments and potentially improved models. ^[autoresearch-github.md]

The training code is a simplified single-GPU implementation of nanochat, where researchers do not directly modify Python files as they normally would. Instead, they program `program.md` Markdown files that provide context to AI agents and configure the autonomous research organization. ^[autoresearch-github.md]

## Architecture

### Core Components

The framework consists of three essential files:

- **`prepare.py`** - Contains fixed constants, one-time data preparation (downloads training data, trains a BPE tokenizer), and runtime utilities (dataloader, evaluation). This file is not modified by agents.
- **`train.py`** - The single file that agents edit, containing the full GPT model, optimizer ([[Muon]] + [[AdamW]]), and training loop. All aspects are modifiable including architecture, hyperparameters, optimizer, and batch size.
- **`program.md`** - Baseline instructions for agents that are edited and iterated on by humans. ^[autoresearch-github.md]

### Design Principles

The framework follows several key design principles:

**Single File Modification**: Agents only modify `train.py`, keeping the scope manageable and diffs reviewable. ^[autoresearch-github.md]

**Fixed Time Budget**: Training always runs for exactly 5 minutes regardless of the specific platform. This enables approximately 12 experiments per hour and around 100 experiments during overnight runs. The fixed duration makes experiments directly comparable regardless of agent changes to model size, batch size, or architecture, and ensures the system finds the most optimal model for the available platform within the time constraint. ^[autoresearch-github.md]

**Self-Contained Operation**: The framework has no external dependencies beyond [[PyTorch]] and a few small packages, with no distributed training or complex configurations required. It operates with one GPU, one file, and one metric. ^[autoresearch-github.md]

## Evaluation Methodology

The framework uses **val_bpb** (validation bits per byte) as its primary metric, where lower values indicate better performance. This metric is vocabulary-size-independent, allowing fair comparison of architectural changes. Training runs operate under a fixed 5-minute time budget measured in wall clock time, excluding startup and compilation phases. ^[autoresearch-github.md]

## Platform Requirements

The system currently requires a single NVIDIA GPU (tested on H100) with Python 3.10+ and the uv package manager. While designed for high-end hardware, the framework can be adapted for smaller compute platforms through various parameter adjustments including dataset selection, vocabulary size reduction, sequence length modification, and model depth scaling. ^[autoresearch-github.md]

## Adaptation for Smaller Platforms

For deployment on smaller compute platforms such as consumer hardware, several modifications are recommended:

- **Dataset Selection**: Using lower-entropy datasets like TinyStories (GPT-4 generated short stories) for better results with smaller models
- **Vocabulary Size Reduction**: Decreasing `vocab_size` from 8192 down to 4096, 2048, 1024, or even byte-level tokenization with 256 possible bytes
- **Sequence Length Adjustment**: Lowering `MAX_SEQ_LEN` significantly, potentially down to 256 tokens depending on hardware constraints
- **Model Complexity Control**: Reducing the `DEPTH` parameter (default 8) to smaller values like 4 for less complex models
- **Batch Size Optimization**: Decreasing `TOTAL_BATCH_SIZE` while maintaining powers of 2, potentially down to 2^14 (~16K) tokens ^[autoresearch-github.md]

## Research Applications

The framework enables autonomous experimentation across multiple dimensions of machine learning research including model architecture modifications, hyperparameter optimization, optimizer selection, and training methodology exploration. The system is designed to evolve the research process itself through iterative improvements to the `program.md` instructions and the addition of multiple agents to the research organization. ^[autoresearch-github.md]
