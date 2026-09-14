---
title: "Claude Code Agent"
summary: "An AI coding agent that can read program instructions and autonomously execute the entire autoresearch loop without human intervention."
sources:
  - auto research by Andrej Karpathy/how-to-set-up-karpathy-s-autoresearch-complete-guide-use-cases.md
createdAt: 2026-05-25T16:02:07.620095+00:00
updatedAt: 2026-05-25T16:02:07.620095+00:00
---
# Claude Code Agent

**Claude Code Agent** is an AI coding agent developed by Anthropic that can autonomously execute code, run experiments, and iterate on solutions without human intervention. The agent gained significant attention when AI researcher [[Andrej Karpathy]] used it to implement an "autoresearch" pattern that discovered genuine improvements to machine learning models through automated experimentation. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Overview

Claude Code Agent operates by reading instructions from a program file and executing a continuous loop of hypothesis formation, experimentation, measurement, and iteration. Unlike traditional AI assistants that require human guidance for each step, Claude Code Agent can run autonomously for extended periods, making decisions about whether to keep or discard experimental changes based on measurable outcomes. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## The Autoresearch Pattern

The autoresearch pattern represents a systematic approach to automated experimentation that consists of four core steps:

1. **Goal Definition**: Establishing a measurable outcome metric such as validation loss, conversion rate, or performance benchmarks
2. **Single File Modification**: Providing the agent with one specific file to modify, such as a training script, configuration file, or template
3. **Experimental Loop**: The agent reads current state, forms hypotheses, implements changes, runs experiments within a fixed time budget, and measures results
4. **Continuous Iteration**: The process repeats indefinitely without human intervention until manually stopped ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Notable Applications

### Machine Learning Research

Andrej Karpathy demonstrated the agent's capabilities by letting it run for two days on his hand-optimized GPT-2 training code. The agent executed 700 experiments and discovered 20 genuine improvements, reducing training time by 11%. The improvements included corrections to attention mechanism scaling, value embedding regularization, attention window parameters, and AdamW optimizer settings that Karpathy had overlooked. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Commercial Implementation

Shopify CEO Tobi Lütke applied the same approach to an internal 0.8 billion parameter model, achieving a 19% improvement in model quality through 37 experiments conducted overnight without human involvement. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Technical Requirements

Claude Code Agent requires three primary components for autoresearch implementation:

- **AI Coding Agent**: Claude Code serves as the autonomous executor that reads instructions and manages the experimental loop
- **NVIDIA GPU**: The system requires NVIDIA GPU hardware, tested on H100s but compatible with other NVIDIA cards, available through cloud providers like Google Colab, Lambda Labs, Vast.ai, or RunPod
- **Repository Structure**: A minimal codebase consisting of data preparation scripts, the target file for modification, and instruction files for the agent ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Business Applications

The autoresearch pattern extends beyond machine learning to various business optimization scenarios:

### Marketing Optimization
- **Landing Page Testing**: Iterating on HTML elements, headlines, layouts, and calls-to-action with conversion rate as the target metric
- **Email Campaign Optimization**: Testing subject lines, body copy, send times, and personalization approaches for improved open and click-through rates
- **Advertising Optimization**: Experimenting with creative elements and targeting parameters to optimize cost per acquisition or return on ad spend ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Product and Pricing
- **Prompt Engineering**: Optimizing AI system prompts for customer service, content generation, or internal tools based on output quality metrics
- **Pricing Strategy**: Testing price points, bundle configurations, and discount structures to maximize revenue per visitor or conversion rates ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Future Vision

Karpathy envisions expanding beyond single-agent experimentation to "emulate a research community" through AgentHub, described as a collaboration platform featuring a decentralized structure without traditional version control constraints, allowing multiple agents to coordinate and share experimental results. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Related Concepts

- [[Supervised Fine-Tuning (SFT)]]
- [[Reinforcement Learning from Human Feedback (RLHF)]]
- [[Multi-Agent Orchestration]]
- [[Human-in-the-Loop Agent Design]]
- [[Trajectory-Level Evaluation]]
