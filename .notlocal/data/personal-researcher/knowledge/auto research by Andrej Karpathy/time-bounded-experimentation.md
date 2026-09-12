---
title: "Time-Bounded Experimentation"
summary: "A methodology where each experiment runs on a fixed time budget (like 5 minutes) to enable rapid iteration and prevent agents from getting stuck on long-running tests."
sources:
  - auto research by Andrej Karpathy/how-to-set-up-karpathy-s-autoresearch-complete-guide-use-cases.md
createdAt: 2026-05-25T16:03:11.419491+00:00
updatedAt: 2026-05-25T16:03:11.419491+00:00
---
# Time-Bounded Experimentation

Time-bounded experimentation is a systematic approach to optimization where an AI agent runs rapid, iterative experiments within fixed time constraints to improve measurable outcomes. The methodology emerged from machine learning research but applies broadly to any domain where performance can be quantified and tested systematically.

## Core Methodology

Time-bounded experimentation follows a four-step pattern that enables autonomous optimization at scale. First, practitioners define a goal with a measurable outcome - not subjective improvements, but specific metrics like validation loss, conversion rate, cost per lead, or open rate. Second, they provide an AI agent with one file it can modify, such as a training script, landing page, email template, or configuration file. Third, the agent runs a continuous loop where it reads the current state, forms a hypothesis, makes a change, runs an experiment within a fixed time budget, measures the result, and decides whether to keep or discard the modification. Fourth, this process repeats indefinitely without human intervention, accumulating improvements through volume rather than individual insight. ^[karpathy-autoresearch-setup-guide-use-cases.md]

The methodology represents a fundamental shift from traditional experimentation approaches. Instead of expensive, slow experiments requiring deep expertise where researchers might run a few experiments per day, time-bounded experimentation enables hundreds of experiments to run overnight while practitioners sleep. The bottleneck moves from human design capacity to computational throughput. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Implementation Requirements

The technical implementation requires three core components. An AI coding agent serves as the autonomous experimenter, with Claude Code being the recommended choice for reading instructions and running the entire optimization loop. A GPU provides the computational infrastructure, specifically NVIDIA GPUs which can be rented through cloud services like Google Colab, Lambda Labs, Vast.ai, or RunPod when local hardware is unavailable. The experimental framework consists of minimal code - typically around 630 lines including data preparation scripts, the modifiable target file, and instruction documents that guide the agent's behavior. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Demonstrated Results

Real-world applications have shown significant performance improvements across different domains. In machine learning research, an AI agent running for two days executed 700 experiments and found 20 genuine improvements, reducing training time for a GPT-2 quality model by 11% on code that had already been hand-optimized by an expert researcher. The agent discovered overlooked issues including insufficient scalar multipliers in attention mechanisms, missing regularization in value embeddings, overly conservative attention windows, and incorrect AdamW beta parameters. In a separate case, the same methodology applied to an internal 0.8 billion parameter model achieved a 19% improvement in model quality through 37 experiments run overnight with no human involvement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Business Applications

The pattern extends beyond machine learning to various business optimization scenarios. For conversion optimization, the target file becomes landing page HTML with conversion rate as the metric, enabling automated testing of headlines, layouts, calls-to-action, and offers. Email marketing applications use email templates as the modifiable file while measuring open rates, click-through rates, or reply rates to optimize subject lines, body copy, send times, and personalization approaches. [[LLM-as-Judge Quality Scoring]] systems can be optimized by treating prompts as the target file and using output quality scores as the metric to iterate on prompt structure, examples, and system instructions. ^[karpathy-autoresearch-setup-guide-use-cases.md]

Pricing optimization treats configuration files defining price points, bundles, and discount structures as the target, measuring revenue per visitor or conversion rates to converge on optimal pricing strategies. Advertising optimization modifies creative and targeting parameters while measuring cost per acquisition or return on ad spend to identify effective combinations. Content strategy optimization uses templates and posting strategies as the modifiable elements while tracking engagement rates, subscription conversions, or reach metrics. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Scalability Vision

The long-term vision extends beyond individual agent optimization to collaborative research communities. Rather than emulating a single researcher, the goal involves creating networks of agents that coordinate experiments and share findings. This approach envisions platforms where agents operate without traditional version control constraints, creating sprawling networks of experimental branches with coordination mechanisms for sharing discoveries across the agent community. ^[karpathy-autoresearch-setup-guide-use-cases.md]
