---
title: "Autoresearch"
summary: "An AI system where an agent continuously runs experiments to optimize code or training processes, demonstrated by Karpathy's agent that conducted 700 experiments over two days to improve language model training."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:05:21.073941+00:00
updatedAt: 2026-05-25T16:05:21.073941+00:00
---
# Autoresearch

**Autoresearch** is an experimental AI system developed by Andrej Karpathy that uses autonomous AI agents to conduct iterative optimization experiments on machine learning models and training processes. The system represents an approach to automated research where AI agents can modify code, run experiments, and learn from results to improve model performance without direct human intervention. ^[karpathy-loop-fortune.md]

## Overview

Autoresearch operates by giving an AI agent access to modify a single file containing training code and neural network configurations, along with a specific metric to optimize and time constraints for each experimental iteration. The agent conducts experiments in a continuous loop, learning from previous results to inform subsequent modifications. ^[karpathy-loop-fortune.md]

In Karpathy's initial demonstration, the system ran continuously for two days and conducted 700 different experiments on a small language model's training process. Through this automated experimentation, it discovered 20 optimizations that improved training time, which when applied to a larger model resulted in an 11% speedup. ^[karpathy-loop-fortune.md]

## The Karpathy Loop

The autoresearch system has been characterized as following what some commentators call "the Karpathy Loop," which consists of three core components:

- An agent with access to a single file that it can modify
- A single, objectively testable metric that the agent can optimize for  
- A fixed time limit for how long each experiment can run

The system also requires clear instructions including what the agent should do, constraints on what it should not modify, and stopping criteria indicating when to halt experimentation and report results. ^[karpathy-loop-fortune.md]

## Real-World Applications

Beyond Karpathy's initial experiments, the system has been tested by other organizations. Tobias Lütke, CEO of Shopify, reported using autoresearch to optimize an AI model on internal company data, with instructions to improve both quality and speed. After running overnight, the system conducted 37 experiments and achieved a 19% performance gain. ^[karpathy-loop-fortune.md]

## Future Development

Karpathy envisions scaling autoresearch beyond single-agent optimization to involve multiple AI agents working collaboratively. He describes a future system where "you spin up a swarm of agents, you have them collaborate to tune smaller models, you promote the most promising ideas to increasingly larger scales, and humans (optionally) contribute on the edges." ^[karpathy-loop-fortune.md]

The next planned development involves making the system "asynchronously massively collaborative for agents," with the goal of emulating not just a single researcher but "a research community" of researchers working in parallel on different optimization paths. ^[karpathy-loop-fortune.md]

## Relationship to Existing Methods

Critics have noted similarities between autoresearch and existing AutoML techniques that have been used by major AI labs for years. AutoML also employs optimization loops and experimental series to find optimal data, model architectures, and hyperparameters. However, Karpathy distinguishes autoresearch from methods like neural architecture search, arguing that autoresearch represents "an *actual* LLM writing arbitrary code, learning from previous experiments, with access to the internet" rather than relying on random variations or evolutionary algorithms. ^[karpathy-loop-fortune.md]

## Implications for AI Research

Karpathy has suggested that autoresearch represents a significant shift in how AI research will be conducted, stating that "All LLM frontier labs will do this. It's the final boss battle." He notes that while scaling the approach to larger, more complex training codebases presents engineering challenges, the fundamental approach is viable and will be adopted across the industry. ^[karpathy-loop-fortune.md]

The system's potential extends beyond AI model optimization, as Karpathy noted that "any metric you care about that is reasonably efficient to evaluate (or that has more efficient proxy metrics such as training a smaller network) can be autoresearched by an agent swarm." ^[karpathy-loop-fortune.md]

## Concerns and Considerations

Some observers have noted that autoresearch approaches concepts of recursive self-improvement that have been discussed in AI safety research. While the current system optimizes separate, smaller models rather than improving itself directly, the automated nature of the optimization process has drawn attention from those concerned about potential "intelligence explosion" scenarios where AI systems rapidly improve beyond human control. ^[karpathy-loop-fortune.md]
