---
title: "What is RLGym? What are some success stories in industry and academia?"
summary: "RLGym = Rocket League reinforcement learning environment (not a general RL framework). 240 GitHub stars, Gym-like API + RocketSim physics. Key success: Nexto bot reached Grand Champion 1 (top 0.12% of players) using PPO + replay pretraining. No industry use outside gaming. No major academic papers. Community-driven."
type: query
createdAt: 2026-06-09
topic: rl
---

# What is RLGym?

## Quick Answer

**RLGym is the Rocket League reinforcement learning environment** — a Gym-like API for training RL bots to play the 3D physics-based car soccer game. It is NOT a general-purpose RL framework and has NO Google DeepMind variant. It's community-driven (240 GitHub stars) and produced the most impressive game-playing RL bots outside of DeepMind/OpenAI.

## Key Facts

| Property | Value |
|----------|-------|
| What | RL environment for Rocket League |
| GitHub | github.com/RLGym/rlgym, 240 stars |
| API | Gym-like step/reset (independent, not Gymnasium wrapper) |
| Physics | RocketSim: 114K ticks/sec, ~10 days of game per minute |
| Training | rlgym-learn (Rust), RLGymPPO_CPP (70K steps/sec) |
| Best algo | PPO + replay-based pretraining |
| License | Apache-2.0 |

## Success Stories

### Gaming (The Only Domain)

| Achievement | Year | Significance |
|-------------|------|-------------|
| **Nexto reaches Grand Champion 1** | 2023 | Top 0.12% of all Rocket League players in 1v1 |
| **Necto wins RLBot Championship** | 2022 | First RL-trained bot to win the tournament |
| **RocketSim achieves 10 days/min** | 2023 | Enables massive-scale training on consumer hardware |
| **RLGymPPO_CPP: 70K steps/sec** | 2024 | 5x faster than Python implementation |

### Nexto (V2) — The Headline Achievement

- **Level:** Grand Champion 1 (top 0.12% in 1v1, top 0.95% in 2v2, top 0.46% in 3v3)
- **Method:** Replay-based pretraining (behavioral cloning from human replays, inspired by OpenAI VPT) → PPO reinforcement learning
- **Significance:** Demonstrates RL can achieve near-professional performance in a complex continuous-action 3D physics game without human-designed heuristics
- **Training:** Streamed on Twitch, metrics on W&B

### No Industry Success Stories (Outside Gaming)

RLGym has **zero** known deployments in:
- Robotics (uses Isaac Lab, MuJoCo)
- Trading/Finance (uses custom Gymnasium envs)
- Ads/Recommendation (uses custom frameworks)
- Any non-Rocket-League context

### No Major Academic Papers

No peer-reviewed papers at NeurIPS, ICML, ICLR, or other top ML venues use RLGym as their primary experimental platform. The project lives in the hobbyist/competitive bot community.

## Why It Matters (Despite Being Niche)

1. **Proof of concept:** RL can achieve human-expert-level in complex 3D physics games with continuous actions — a harder problem than board games (Go, Chess)
2. **Engineering patterns:** The PPO + replay pretraining pipeline mirrors the SFT → RL pattern now dominant in LLM post-training
3. **Accessible:** RocketSim enables massive-scale RL training on consumer hardware (~$0 environment cost)
4. **Modular architecture:** Clean separation of API, environment, physics, training, and utilities — a reference design for custom RL environments

## How It Compares to Alternatives

| If you need... | Use... | Not RLGym because... |
|---------------|--------|---------------------|
| General RL research | Gymnasium (12K stars) | RLGym is Rocket League only |
| 3D game AI | Unity ML-Agents (19.5K stars) | RLGym is one game only |
| Robotics | Isaac Lab / MuJoCo | RLGym has no sim-to-real |
| Multi-agent research | PettingZoo | RLGym's multi-agent is game-specific |
| Rocket League bots | **RLGym** | It's the only option |

## Sources

- [[RLGym — Rocket League Reinforcement Learning Environment]]
- github.com/RLGym/rlgym (240 stars)
- github.com/ZealanL/RocketSim (119 stars)
- RLBot community (615 stars)
