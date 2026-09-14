---
title: "RLGym — Rocket League Reinforcement Learning Environment"
url: https://github.com/RLGym/rlgym
ingestedAt: 2026-06-09
type: article
additional_sources:
  - https://rlgym.org
  - https://github.com/ZealanL/RocketSim
  - https://github.com/ZealanL/RLGymPPO_CPP
  - https://github.com/RLBot/RLBot
---

# RLGym — Rocket League RL Environment

## Identity

RLGym is exclusively the Rocket League reinforcement learning environment. No Google DeepMind "RLGym" or general-purpose framework exists. All 123 GitHub repos matching "rlgym" relate to the Rocket League ecosystem.

- Website: rlgym.org
- GitHub: github.com/RLGym/rlgym (240 stars, Apache-2.0)
- Creators: Lucas Emery, Matthew Allen (AechPro)
- API: OpenAI Gym-inspired step/reset interface, but independent (not a Gymnasium wrapper)

## Architecture

Modular component-based design:
- RLGym (meta-package) → rlgym-api (zero-dep API) → rlgym-rocket-league (implementation)
- rlgym-learn (Rust-based parallel training) → rlgym-learn-algos (PPO)
- rlgym-tools (SB3 compat, replay parsing, pre-built rewards/obs)
- RocketSim (C++ physics backend): 114,481 ticks/sec, ~10 days of game per minute (12 threads)
- RLGymPPO_CPP: 70,000 steps/sec (5x faster than Python)

## Notable Bots

| Bot | Year | Level | Achievement |
|-----|------|-------|-------------|
| Necto (V1) | 2022 | Diamond | Won 2022 RLBot Championship |
| Nexto (V2) | 2023 | Grand Champion 1 | 1v1: top 0.12%, 2v2: top 0.95%, 3v3: top 0.46% |
| Tecko (V3) | — | Cancelled | "Lack of improvement" over Nexto |

Training: PPO + replay-based pretraining (behavioral cloning from human replays, inspired by OpenAI VPT). Nexto combines imitation learning + RL.

## Ecosystem

- RLBot community (615 stars): framework for custom bots in Rocket League
- Tournaments: RLBot Championship, braacket leagues
- Variants: RLGym-Rust, rlgym-sim-rs (Rust), RLGymPPO_CPP (C++)
- Twitch streaming of training, W&B metrics published

## Limitations

- No known non-gaming industry usage (robotics uses Isaac Lab/MuJoCo, trading uses custom Gymnasium)
- No major peer-reviewed academic papers at top ML venues
- Community/hobbyist-driven, not academic
- Main bot project (Necto/Nexto) development has stopped
- 240 stars (niche vs Gymnasium 12K, Unity ML-Agents 19.5K)

## RL Environments Landscape Comparison

| Framework | Stars | Focus | Differentiator |
|-----------|-------|-------|---------------|
| Gymnasium (Farama) | 12K | Standard single-agent API | Industry standard |
| Unity ML-Agents | 19.5K | Game AI | Unity integration |
| MuJoCo (DeepMind) | 13.8K | Physics/robotics | High-fidelity, JAX branch |
| Isaac Lab (NVIDIA) | 7.4K | GPU-accelerated robotics | Sim-to-real, replaces Isaac Gym |
| PettingZoo (Farama) | 3.4K | Multi-agent | AEC games API |
| Brax (Google) | 3.2K | JAX physics | Differentiable, TPU/GPU |
| RLGym | 240 | Rocket League | Only RL framework for RL |
