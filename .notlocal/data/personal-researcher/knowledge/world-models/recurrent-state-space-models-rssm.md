---
title: "Recurrent State Space Models (RSSM)"
summary: "A world model architecture that combines stochastic and deterministic components to learn latent dynamics, used in the Dreamer family of algorithms."
sources:
  - world-models/world-models-comprehensive.md
createdAt: 2026-06-15T11:40:36.439935+00:00
updatedAt: 2026-06-15T11:40:36.439935+00:00
---
# Recurrent State Space Models (RSSM)

## Overview

Recurrent State Space Models (RSSM) are a key architectural innovation in [[World Models — Overview and SOTA]] that combine stochastic and deterministic components to learn latent dynamics of environments. RSSMs enable agents to predict future states in a compressed latent space, supporting efficient planning and decision-making without requiring full pixel-level predictions. ^[world-models-comprehensive-deep-dive.md]

## Architecture

RSSMs maintain both stochastic and deterministic state representations:

- **Stochastic state**: Captures uncertainty and variability in environment dynamics
- **Deterministic state**: Maintains consistent information across time steps through recurrent connections
- **Latent dynamics**: Predicts how states evolve in response to actions in compressed representation space

This dual-state design allows RSSMs to model complex, partially observable environments while maintaining computational efficiency. ^[world-models-comprehensive-deep-dive.md]

## Key Applications

### Dreamer Family

RSSMs form the core architecture of the Dreamer series of world models:

- **DreamerV2 (2021)**: Achieved first human-level performance using world models on Atari 55 tasks
- **DreamerV3 (Nature 2024)**: Demonstrated performance across 150+ tasks with single configuration, including first successful acquisition of diamonds in Minecraft

These models use RSSMs to learn environment dynamics and perform planning entirely in latent space, avoiding the computational overhead of pixel-level prediction. ^[world-models-comprehensive-deep-dive.md]

### Planning and Control

RSSMs enable sample-efficient reinforcement learning by allowing agents to:

- Learn environment dynamics from limited real experience
- Generate imagined trajectories for planning
- Train policies on synthetic rollouts in latent space
- Reduce the need for extensive environment interaction

## Evolution and Alternatives

The RSSM architecture represents an evolution from simpler approaches:

- **Early models**: VAE+RNN combinations with linear or MLP dynamics
- **RSSM innovation**: Introduction of stochastic-deterministic state separation
- **Modern alternatives**: Transformer-based models (IRIS) and diffusion-based approaches (DIAMOND) that operate in latent space

While newer architectures like transformers have shown promise, RSSMs remain influential for their balance of expressiveness and computational efficiency. ^[world-models-comprehensive-deep-dive.md]

## Technical Advantages

RSSMs offer several key benefits:

- **Compressed representation**: Learn dynamics in latent space rather than high-dimensional observations
- **Uncertainty modeling**: Stochastic components capture environment variability
- **Recurrent memory**: Deterministic states maintain information across time steps
- **Sample efficiency**: Enable learning from limited real environment interaction

## Related Concepts

RSSMs are closely related to other approaches in [[World Models — Overview and SOTA]], including [[Memory-Augmented Neural Networks (MANNs)]] and various [[Transformer Architecture]] adaptations for sequential prediction tasks.
