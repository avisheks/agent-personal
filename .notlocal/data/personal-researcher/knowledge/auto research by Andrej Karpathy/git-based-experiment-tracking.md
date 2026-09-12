---
title: "Git-Based Experiment Tracking"
summary: "A version control approach where successful experiments are committed to git while failures are reverted, creating a clean history of only improvements that actually worked."
sources:
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:03:29.785523+00:00
updatedAt: 2026-05-25T16:03:29.785523+00:00
---
# Git-Based Experiment Tracking

Git-based experiment tracking is a methodology for managing machine learning experiments where version control serves as the primary mechanism for recording, organizing, and evaluating experimental results. This approach leverages Git's branching and commit history to maintain a clean record of successful improvements while automatically reverting failed experiments.

## Core Methodology

The fundamental principle involves using Git commits to represent successful experiments and Git resets to discard failures. Each experiment begins from a known baseline state, applies a single modification to the training code, evaluates the result against a consistent metric, and either commits the change (if performance improved) or reverts to the previous state (if performance degraded). This creates a linear history where every commit represents a genuine improvement over the previous baseline. ^[karpathy-autoresearch-explained.md]

The approach differs from traditional hyperparameter optimization tools by allowing modifications to the entire training codebase rather than just predefined parameter grids. An AI agent can rewrite attention mechanisms, change optimizers, or restructure training loops while maintaining experimental integrity through version control. ^[karpathy-autoresearch-explained.md]

## Implementation Architecture

A typical implementation consists of three core components with distinct access controls. The preparation module handles data download, tokenizer training, and evaluation functions, remaining locked after initial setup to ensure scoring consistency across all experiments. The training module contains the model architecture, optimizer, and training loop, serving as the only file the agent can modify. The instruction file provides plain English directions that specify research objectives, experimental constraints, and edge case handling procedures. ^[karpathy-autoresearch-explained.md]

The experiment loop operates by reading the full context, forming a hypothesis, editing the training code directly, running a time-bounded training session, extracting performance metrics, and either committing improvements or reverting failures. Error handling involves reading crash logs, attempting fixes, and abandoning experiments that cannot be resolved after multiple attempts. ^[karpathy-autoresearch-explained.md]

## Constraint Design

Effective git-based experiment tracking relies on carefully designed constraints that prevent common failure modes. Codebase size limits ensure the entire training file fits within an AI agent's context window, enabling coherent understanding of how components interact. Evaluation function locks prevent agents from gaming metrics by rewriting scoring functions. Package installation restrictions maintain reproducible environments across experiments. ^[karpathy-autoresearch-explained.md]

The constraint framework follows a "one GPU, one file, one metric" philosophy that keeps the search space manageable while maintaining experimental validity. These limitations are not arbitrary restrictions but essential design elements that enable reliable autonomous operation across hundreds of experiments. ^[karpathy-autoresearch-explained.md]

## Scoring and Evaluation

Git-based experiment tracking typically employs a single, architecture-agnostic metric for comparing results across diverse experimental modifications. Validation bits per byte serves as an effective choice because it measures encoding efficiency independently of vocabulary size, allowing direct comparison between experiments that modify tokenizers, layer counts, or attention mechanisms. This metric prevents agents from achieving apparent improvements through evaluation gaming while maintaining comparability across the full range of possible architectural changes. ^[karpathy-autoresearch-explained.md]

## Practical Applications

The methodology has demonstrated effectiveness in real-world scenarios where researchers achieved significant performance improvements through overnight autonomous experimentation. One documented case involved running approximately 700 experiments over two days, discovering around 20 genuine improvements that collectively reduced training time by 11% on already-optimized code. Another application found architectural optimizations that enabled a smaller model to outperform a baseline twice its size. ^[karpathy-autoresearch-explained.md]

The approach proves particularly valuable for small teams and individual researchers who lack the resources for large-scale parallel experimentation. By utilizing overnight GPU time for sequential experiments, the methodology equalizes access to high-throughput ML experimentation regardless of team size or compute budget. ^[karpathy-autoresearch-explained.md]

## Integration with AI Agents

Modern implementations leverage coding agents that can read, understand, and modify training code autonomously. The agent operates within the git-based framework by reading instruction files, forming hypotheses about potential improvements, implementing changes directly in source code, and evaluating results according to predefined metrics. The version control system provides automatic rollback capabilities when experiments fail, enabling continuous operation without human intervention. ^[karpathy-autoresearch-explained.md]

The instruction file serves as the primary interface between human researchers and the autonomous system, containing research agendas written in plain English rather than code. This design shifts human effort from manual experiment execution toward higher-level research direction and constraint specification. ^[karpathy-autoresearch-explained.md]

## Advantages and Limitations

Git-based experiment tracking offers several advantages over traditional approaches. The methodology provides automatic experiment logging through commit history, ensures reproducibility through version control, enables autonomous operation for extended periods, and maintains clean separation between successful improvements and failed attempts. The approach scales effectively on single-GPU setups while producing results comparable to more resource-intensive parallel experimentation. ^[karpathy-autoresearch-explained.md]

However, the methodology requires careful constraint design to prevent failure modes and works best with codebases small enough to fit within AI agent context windows. Results are hardware-specific due to time-bounded training sessions, making cross-machine comparisons invalid. The approach also depends on having a single, reliable metric that accurately reflects model quality across diverse architectural modifications. ^[karpathy-autoresearch-explained.md]
