---
title: "RLGym — Rocket League RL Environment"
summary: "The only RL environment for Rocket League. Gym-like API + RocketSim (10 days/min). Nexto bot: Grand Champion 1 (top 0.12%). 240 stars, community-driven, PPO + replay pretraining. No non-gaming usage."
sources:
  - rl/rlgym-rocket-league-rl-environment.md
createdAt: 2026-06-15T12:00:38.636783+00:00
updatedAt: 2026-06-15T12:00:38.636783+00:00
---
# RLGym — Rocket League RL Environment

RLGym is a reinforcement learning environment specifically designed for training AI agents to play Rocket League, the popular vehicular soccer video game. It provides a modular, high-performance framework that enables researchers and developers to create AI bots capable of competing at professional skill levels. ^[rlgym-rocket-league-rl-environment.md]

## Overview

RLGym serves as the primary reinforcement learning framework for Rocket League AI development, with no other competing frameworks targeting this specific domain. The project consists of 123 related GitHub repositories, all focused on the Rocket League ecosystem, making it the definitive solution for RL-based Rocket League bot development. ^[rlgym-rocket-league-rl-environment.md]

The framework follows an OpenAI Gym-inspired step/reset interface but operates as an independent system rather than a Gymnasium wrapper. This design choice allows for optimizations specific to Rocket League's unique physics and gameplay requirements. ^[rlgym-rocket-league-rl-environment.md]

## Architecture

RLGym employs a modular component-based architecture that separates concerns across multiple specialized packages:

- **RLGym (meta-package)** → **rlgym-api (zero-dependency API)** → **rlgym-rocket-league (implementation)**
- **rlgym-learn (Rust-based parallel training)** → **rlgym-learn-algos (PPO)**
- **rlgym-tools** provides Stable Baselines3 compatibility, replay parsing, and pre-built rewards/observations

The system leverages **RocketSim**, a C++ physics backend capable of 114,481 ticks per second, effectively simulating approximately 10 days of gameplay per minute when running on 12 threads. For training acceleration, **RLGymPPO_CPP** delivers 70,000 steps per second, representing a 5x performance improvement over Python implementations. ^[rlgym-rocket-league-rl-environment.md]

## Notable AI Achievements

RLGym has produced several high-performing AI agents that demonstrate the framework's capabilities:

### Necto (V1) - 2022
- **Skill Level**: Diamond rank
- **Achievement**: Won the 2022 RLBot Championship
- **Significance**: First major competitive success for RLGym-trained agents

### Nexto (V2) - 2023
- **Skill Level**: Grand Champion 1 rank
- **Performance**: 1v1 (top 0.12%), 2v2 (top 0.95%), 3v3 (top 0.46%)
- **Training Method**: Combined imitation learning with [[reinforcement-learning-from-human-feedback-rlhf]] using replay-based pretraining

### Tecko (V3)
- **Status**: Development cancelled
- **Reason**: "Lack of improvement" over Nexto's performance ceiling

The training methodology combines [[chain-of-thought-reasoning]] through PPO algorithms with behavioral cloning from human gameplay replays, inspired by OpenAI's Video Pre-Training (VPT) approach. ^[rlgym-rocket-league-rl-environment.md]

## Ecosystem and Community

RLGym operates within a broader ecosystem centered around the RLBot community framework (615 GitHub stars), which provides infrastructure for custom bot development in Rocket League. The community organizes competitive events including the RLBot Championship and braacket leagues, fostering continued development and benchmarking of AI agents. ^[rlgym-rocket-league-rl-environment.md]

Several variant implementations extend the core framework:
- **RLGym-Rust** and **rlgym-sim-rs**: Rust-based implementations
- **RLGymPPO_CPP**: C++ optimization for training performance
- Community-driven streaming of training sessions with public Weights & Biases metrics

## Limitations and Scope

Despite its success within the Rocket League domain, RLGym faces several constraints that limit its broader applicability:

RLGym has not demonstrated significant adoption outside gaming applications. Robotics applications typically utilize Isaac Lab or MuJoCo, while financial trading systems employ custom Gymnasium environments. The framework lacks major peer-reviewed publications at top-tier machine learning venues, positioning it primarily as a community-driven rather than academic research tool. ^[rlgym-rocket-league-rl-environment.md]

Development of the main bot projects (Necto/Nexto series) has ceased, and the framework's 240 GitHub stars reflect its niche status compared to broader RL frameworks like Gymnasium (12,000 stars) or Unity ML-Agents (19,500 stars). ^[rlgym-rocket-league-rl-environment.md]

## Comparison with Other RL Frameworks

RLGym occupies a unique position in the reinforcement learning environment landscape:

| Framework | Focus | Key Differentiator |
|-----------|-------|-------------------|
| Gymnasium (Farama) | Standard single-agent API | Industry standard (12K stars) |
| Unity ML-Agents | Game AI | Unity integration (19.5K stars) |
| MuJoCo (DeepMind) | Physics/robotics | High-fidelity simulation (13.8K stars) |
| Isaac Lab (NVIDIA) | GPU-accelerated robotics | Sim-to-real transfer (7.4K stars) |
| RLGym | Rocket League | Only RL framework for vehicular soccer (240 stars) |

This specialization allows RLGym to achieve exceptional performance within its domain while limiting its applicability to other reinforcement learning tasks. ^[rlgym-rocket-league-rl-environment.md]
