---
title: "Autoresearch Pattern"
summary: "An autonomous AI research methodology where agents continuously run experiments by modifying a single file, measuring outcomes against a defined metric, and iterating without human intervention."
sources:
  - auto research by Andrej Karpathy/how-to-set-up-karpathy-s-autoresearch-complete-guide-use-cases.md
createdAt: 2026-05-25T16:02:11.696690+00:00
updatedAt: 2026-05-25T16:02:11.696690+00:00
---
# Autoresearch Pattern

The **Autoresearch Pattern** is an autonomous experimentation framework where an AI agent continuously iterates on a single modifiable file to optimize a measurable outcome. The pattern was developed and demonstrated by Andrej Karpathy, who used it to run 700 experiments over two days, achieving an 11% improvement in training time for a GPT-2 quality model on code he had already hand-optimized. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Core Components

The autoresearch pattern consists of four essential elements that work together to create an autonomous optimization loop:

### 1. Measurable Goal Definition
The pattern requires a specific, quantifiable objective rather than vague improvements. Examples include validation loss, conversion rate, cost per lead, or open rate. The goal must produce a clear numeric signal that the agent can use to evaluate success or failure. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### 2. Single Modifiable File
The agent operates on exactly one file that it can modify. In Karpathy's original implementation, this was a 630-line training script called `train.py`. The constraint to a single file prevents the agent from making overly complex changes and maintains experimental control. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### 3. Autonomous Execution Loop
The agent follows a continuous cycle: read current state, form hypothesis, make change, run experiment within a fixed time budget (typically 5 minutes per experiment), measure results, and decide whether to keep or discard the change. This loop runs without human intervention. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### 4. Indefinite Iteration
The system continues running until explicitly stopped by a human. As stated in Karpathy's `program.md` instructions: "Do NOT pause to ask the human if you should continue." This allows the agent to accumulate improvements through volume and persistence. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Implementation Requirements

### Technical Infrastructure
The pattern requires three core components:

- **AI Coding Agent**: Claude Code is the recommended agent, capable of reading instructions and executing the autonomous loop
- **GPU Access**: NVIDIA GPU required (tested on H100s but compatible with other NVIDIA cards), available through cloud providers like Google Colab, Lambda Labs, Vast.ai, or RunPod
- **Code Repository**: Contains three key files - `prepare.py` (data preparation), `train.py` (the modifiable file), and `program.md` (agent instructions) ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Business Applications

### Marketing Optimization
The pattern can optimize landing pages by treating the HTML file as the modifiable component and conversion rate as the metric. The agent generates variants of headlines, layouts, CTAs, and offers, testing them against live traffic to identify optimal combinations. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Email Campaign Enhancement
Email templates serve as the modifiable file while open rates, click-through rates, or reply rates provide the optimization metric. The agent iterates on subject lines, body copy, send times, and personalization approaches to maximize engagement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Prompt Engineering
For AI-powered applications, prompt templates become the modifiable file with output quality (measured by scoring rubrics) as the metric. The agent optimizes prompt structure, examples, and system instructions to improve AI performance. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Pricing Strategy
Configuration files defining price points, bundles, and discount structures can be optimized using revenue per visitor or conversion rate as metrics. The agent tests various pricing combinations to identify optimal strategies. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Advertising Optimization
Ad creative and targeting parameters serve as the modifiable file with cost per acquisition or return on ad spend as the metric. The agent tests different angles, audiences, and creatives to minimize customer acquisition costs or maximize advertising returns. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Content Strategy
Content templates and posting strategies become the modifiable file with engagement rate, subscription conversions, or reach as metrics. The agent iterates on formats, hooks, posting times, and hashtag strategies to optimize content performance. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Demonstrated Results

Karpathy's original experiment discovered multiple genuine improvements including:
- Attention mechanism fixes (missing scalar multiplier)
- Value embedding regularization requirements
- Overly conservative banded attention windows
- Incorrect AdamW beta parameters ^[karpathy-autoresearch-setup-guide-use-cases.md]

Shopify CEO Tobi Lütke applied the same approach to an internal 0.8 billion parameter model, achieving a 19% improvement in model quality through 37 experiments run overnight without human involvement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Paradigm Shift

The fundamental insight of the autoresearch pattern is shifting the bottleneck from human experiment design and execution to autonomous volume-based optimization. Where human researchers might run a few experiments per day, the pattern enables hundreds of experiments overnight, leveraging computational persistence rather than human expertise as the primary driver of improvement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Future Vision

Karpathy envisions scaling beyond individual agents to "emulate a research community" through AgentHub, described as "a stripped-down GitHub where there's no main branch, no PRs, no merges, a sprawling DAG of commits in every direction with a message board for agents to coordinate." This would enable parallel experimentation by multiple agents working collaboratively. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Key Principle

As Karpathy stated, "You don't 'use it' directly, it's just a recipe/idea — give it to your agent and apply to what you care about." The autoresearch pattern is not a product but a methodology that can be applied to any domain where measurable optimization is possible through iterative experimentation. ^[karpathy-autoresearch-setup-guide-use-cases.md]
