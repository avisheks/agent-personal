---
title: "RLGym — Rocket League Reinforcement Learning Environment"
summary: "The only RL environment for Rocket League. Gym-like API + RocketSim physics (10 days/min simulation). Produced Nexto bot reaching Grand Champion 1 (top 0.12% of players). 240 GitHub stars, community-driven, no academic papers at top venues. Best algorithm: PPO + replay-based pretraining."
sources:
  - sources/rl/rlgym-rocket-league-rl-environment.md
createdAt: 2026-06-09
updatedAt: 2026-06-09
---

# RLGym — Rocket League RL Environment

## What It Is

A Gym-like reinforcement learning environment specifically for Rocket League. Not a general RL framework — exclusively for training bots to play the 3D physics-based car soccer game.

- **Website:** rlgym.org
- **GitHub:** 240 stars, Apache-2.0
- **API:** OpenAI Gym-inspired (step/reset/obs/reward), but independent implementation
- **Physics:** RocketSim (C++, 114K ticks/sec, ~10 days of game time per minute on 12 threads)
- **Training:** rlgym-learn (Rust-based parallelization) or RLGymPPO_CPP (70K steps/sec, 5x Python)

## Key Achievement: Grand Champion Bots

| Bot | Level | Percentile | Method |
|-----|-------|:----------:|--------|
| Necto (V1, 2022) | Diamond | Top ~15% | PPO via RLGym |
| Nexto (V2, 2023) | Grand Champion 1 | Top 0.12-0.95% | Replay pretraining + PPO |

Nexto demonstrates that RL can achieve near-professional human performance in a complex 3D physics environment with continuous action spaces.

## Architecture (Modular)

```
rlgym (meta) → rlgym-api (zero-dep) → rlgym-rocket-league (impl)
                                      → RocketSim (C++ physics)
             → rlgym-learn (Rust parallel training)
             → rlgym-learn-algos (PPO)
             → rlgym-tools (SB3 compat, rewards, obs builders)
```

Components are pluggable: custom ActionParsers, ObsBuilders, RewardFunctions, DoneConditions, StateMutators.

## What Works (Algorithm-wise)

- **PPO** is overwhelmingly the algorithm of choice
- **Replay-based pretraining** (behavioral cloning from human replays → then RL) significantly accelerates learning
- Combination mirrors the SFT → RL pattern from LLM post-training

## Limitations

- No non-gaming industry usage (robotics uses Isaac Lab/MuJoCo, finance uses custom envs)
- No major papers at NeurIPS/ICML/ICLR — community-driven, not academic
- Main bot project (Nexto) development stopped; framework still maintained
- Niche: 240 stars vs Gymnasium 12K, Unity ML-Agents 19.5K

## Broader RL Environment Landscape

| Framework | Stars | Focus | Best For |
|-----------|:-----:|-------|----------|
| Gymnasium | 12K | Standard API | Any single-agent RL research |
| Unity ML-Agents | 19.5K | Game AI | 3D game environments |
| MuJoCo | 13.8K | Physics | Robotics, locomotion |
| Isaac Lab (NVIDIA) | 7.4K | GPU-accelerated robotics | Sim-to-real transfer |
| PettingZoo | 3.4K | Multi-agent | Competitive/cooperative games |
| Brax | 3.2K | JAX physics | Massively parallel training |
| **RLGym** | 240 | Rocket League | The only option for RL bots |

## Related

- [[Group Relative Policy Optimization (GRPO)]]
- [[PPO Training Policy]]
- [[Reinforcement Learning from Human Feedback (RLHF)]]
