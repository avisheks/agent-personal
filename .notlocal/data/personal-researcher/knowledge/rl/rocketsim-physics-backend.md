---
title: "RocketSim Physics Backend"
summary: "C++ physics engine for Rocket League simulation achieving 114,481 ticks/sec and approximately 10 days of game time per minute with 12 threads."
sources:
  - rl/rlgym-rocket-league-rl-environment.md
createdAt: 2026-06-15T12:00:51.053394+00:00
updatedAt: 2026-06-15T12:00:51.053394+00:00
---
# RocketSim Physics Backend

**RocketSim** is a high-performance C++ physics simulation backend designed specifically for Rocket League reinforcement learning environments. It serves as the core physics engine that powers the [[RLGym — Rocket League Reinforcement Learning Environment]], providing dramatically accelerated simulation speeds for training AI agents in Rocket League scenarios. ^[rlgym-rocket-league-rl-environment.md]

## Overview

RocketSim is developed by ZealanL and hosted on GitHub at github.com/ZealanL/RocketSim. The physics backend is engineered to replicate Rocket League's game mechanics with high fidelity while achieving exceptional performance benchmarks that make large-scale reinforcement learning feasible. ^[rlgym-rocket-league-rl-environment.md]

## Performance Characteristics

The RocketSim physics backend delivers remarkable simulation speeds that enable practical reinforcement learning training:

- **Tick Rate**: 114,481 ticks per second
- **Time Compression**: Approximately 10 days of game time simulated per minute of real time (using 12 threads)
- **Training Acceleration**: Enables the high-speed training loops required for [[reinforcement-learning-from-human-feedback-rlhf]] and other RL algorithms ^[rlgym-rocket-league-rl-environment.md]

## Integration with RLGym

RocketSim functions as the physics computation layer within the broader RLGym ecosystem architecture:

- **RLGym** (meta-package) → **rlgym-api** (zero-dependency API) → **rlgym-rocket-league** (implementation using RocketSim)
- **RLGymPPO_CPP**: A C++ implementation that leverages RocketSim to achieve 70,000 steps per second, representing a 5x performance improvement over Python-based alternatives ^[rlgym-rocket-league-rl-environment.md]

## Technical Architecture

RocketSim implements a modular component-based design that separates physics simulation from the reinforcement learning interface. This separation allows the physics backend to be optimized independently while maintaining compatibility with standard RL training frameworks and the OpenAI Gym-inspired API used by RLGym. ^[rlgym-rocket-league-rl-environment.md]

The backend supports multi-threaded execution, enabling parallel simulation of multiple game instances simultaneously. This parallelization is crucial for modern RL training approaches that require large batch sizes and extensive environment interaction. ^[rlgym-rocket-league-rl-environment.md]

## Applications in Bot Development

RocketSim has been instrumental in training several notable Rocket League AI agents:

- **Necto (V1)**: Diamond-level bot that won the 2022 RLBot Championship
- **Nexto (V2)**: Grand Champion 1 level bot achieving top percentile rankings (1v1: top 0.12%, 2v2: top 0.95%, 3v3: top 0.46%)

These bots utilize training approaches that combine [[supervised-fine-tuning-sft]] through behavioral cloning from human replays with reinforcement learning, similar to methodologies used in OpenAI's VPT (Video Pre-Training). ^[rlgym-rocket-league-rl-environment.md]

## Ecosystem Position

Within the broader landscape of physics simulation backends for reinforcement learning, RocketSim occupies a specialized niche focused exclusively on Rocket League mechanics. While other frameworks like MuJoCo serve robotics applications and Unity ML-Agents targets general game AI, RocketSim provides domain-specific optimizations that make it uniquely suited for Rocket League RL research and bot development. ^[rlgym-rocket-league-rl-environment.md]

The backend integrates with the wider RLBot community ecosystem, which includes tournament frameworks, streaming infrastructure for training visualization, and integration with Weights & Biases for metrics tracking. ^[rlgym-rocket-league-rl-environment.md]
