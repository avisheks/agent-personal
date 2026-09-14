---
title: "Autonomous Experiment Loop"
summary: "A self-contained cycle where an AI agent forms hypotheses, edits code, runs training sessions, evaluates results, and decides whether to keep or revert changes without human intervention."
sources:
  - auto research by Andrej Karpathy/how-to-set-up-karpathy-s-autoresearch-complete-guide-use-cases.md
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:02:35.333427+00:00
updatedAt: 2026-05-25T16:02:35.333427+00:00
---
# Autonomous Experiment Loop

An **Autonomous Experiment Loop** is a systematic approach where an AI agent continuously runs experiments to optimize a specific metric without human intervention. The pattern involves defining a measurable goal, giving an agent a single file to modify, and allowing it to iterate through hypothesis-experiment-measurement cycles until manually stopped.

## Core Pattern

The autonomous experiment loop follows a four-step process that repeats indefinitely. First, a specific goal with a measurable outcome is defined - not vague improvements, but concrete metrics like validation loss, conversion rate, or cost per lead. Second, an AI agent is given one file it can modify, such as a training script, landing page, or configuration file. Third, the agent runs a continuous loop where it reads the current state, forms a hypothesis, makes a change, runs an experiment on a fixed time budget, measures the result, and decides whether to keep or discard the change. Fourth, this process repeats without pause until manually stopped, with the agent accumulating improvements over time. ^[karpathy-autoresearch-setup-guide-use-cases.md]

The fundamental shift this represents is moving the bottleneck from human experiment design to automated execution at scale. Where traditional research might involve a few experiments per day, autonomous experiment loops can run hundreds of experiments overnight while researchers sleep. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Implementation Requirements

Three core components are needed to implement an autonomous experiment loop. An AI coding agent capable of reading instructions and running the loop autonomously - Claude Code is commonly used for this purpose. A computational environment, often requiring an NVIDIA GPU for machine learning applications, which can be rented through cloud services like Google Colab, Lambda Labs, or RunPod. Finally, a structured codebase with key files including data preparation scripts, the target file for modification, and instruction files that guide the agent's behavior. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Experiment Execution Process

The agent follows a systematic six-step process for each experiment cycle. It reads the current context including instruction files and target code, forms a hypothesis about what change might improve the metric, edits the target file directly, runs the experiment within a fixed time budget (typically 5 minutes for ML experiments), measures the result against the defined metric, and makes a binary decision to either keep the change if it improved performance or revert to the previous state if it didn't. ^[karpathy-autoresearch-explained.md]

When experiments crash or produce errors, the agent reads error logs, attempts fixes, and re-runs the experiment. After several failed attempts, it abandons that particular hypothesis and moves on to the next one, ensuring the overnight run continues regardless of individual experiment failures. ^[karpathy-autoresearch-explained.md]

## Notable Applications

The pattern gained prominence when Andrej Karpathy left an AI agent running for two days, during which it executed 700 experiments and found 20 genuine improvements that reduced training time for a GPT-2 quality model by 11%. The agent discovered issues including insufficient scalar multipliers in attention mechanisms, missing regularization in value embeddings, overly conservative attention windows, and incorrect AdamW beta parameters - bugs that had been missed during manual optimization. ^[karpathy-autoresearch-setup-guide-use-cases.md]

Similarly, Shopify CEO Tobi Lütke applied the same approach to an internal 0.8 billion parameter model, achieving a 19% improvement in model quality through 37 experiments run overnight without human involvement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Business Applications

The autonomous experiment loop pattern extends beyond machine learning to various business optimization scenarios. In conversion optimization, the target file becomes landing page HTML with conversion rate as the metric, allowing agents to test headlines, layouts, and calls-to-action continuously. For email marketing, templates serve as the modifiable file while open rates, click-through rates, or reply rates provide the optimization target. ^[karpathy-autoresearch-setup-guide-use-cases.md]

[[Prompt Template Encoding]] can be optimized using this pattern, where prompt structures serve as the target file and output quality measured by scoring rubrics provides the metric. Pricing optimization involves configuration files defining price points and bundles, with revenue per visitor or conversion rates as success metrics. Advertisement optimization targets creative and targeting parameters while measuring cost per acquisition or return on ad spend. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Design Constraints and Limitations

Effective autonomous experiment loops require carefully designed constraints to prevent failure modes. The target codebase must be small enough for the agent to understand completely - Karpathy's implementation limits the training script to 630 lines so the entire system fits within the agent's context window. The evaluation function and data pipeline remain locked and unmodifiable by the agent to ensure scoring remains honest across all experiments. ^[karpathy-autoresearch-explained.md]

Hard constraints prevent the agent from installing new packages beyond predefined dependencies and enforce simplicity criteria where minor improvements requiring complex code additions are rejected. These limitations close specific failure modes: without evaluation locks, agents could rewrite scoring functions to report false improvements; without simplicity rules, codebases become too complex for coherent agent understanding across successive sessions. ^[karpathy-autoresearch-explained.md]

## Target Applications and Users

The pattern particularly benefits small teams at startups who lack the headcount to run extensive manual experiments, founders building domain-specific models who need to find optimal configurations for their specific hardware and data rather than copying standard hyperparameters, and researchers with more hypotheses than time to test them systematically. ^[karpathy-autoresearch-explained.md]

The shift toward smaller, more efficient models optimized for specific tasks makes autonomous experiment loops increasingly relevant, as they can systematically find configurations that outperform larger general-purpose models for particular use cases. ^[karpathy-autoresearch-explained.md]

## Future Vision

The long-term vision extends beyond emulating individual researchers to creating collaborative research communities. Karpathy envisions AgentHub as "a stripped-down GitHub where there's no main branch, no PRs, no merges, a sprawling DAG of commits in every direction with a message board for agents to coordinate." This represents a shift from single-agent optimization to networked communities of agents running experiments in parallel. ^[karpathy-autoresearch-setup-guide-use-cases.md]
