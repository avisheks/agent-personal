---
title: "PPO + Replay Pretraining"
summary: "Training methodology combining Proximal Policy Optimization with behavioral cloning from human replay data, inspired by OpenAI VPT, used successfully in RLGym bots."
sources:
  - rl/rlgym-rocket-league-rl-environment.md
createdAt: 2026-06-15T12:01:18.875405+00:00
updatedAt: 2026-06-15T12:01:18.875405+00:00
---
# PPO + Replay Pretraining

PPO + Replay Pretraining is a hybrid training methodology that combines behavioral cloning from human demonstration data with reinforcement learning optimization. This approach first pretains a model using supervised learning on replay data, then fine-tunes it using Proximal Policy Optimization (PPO) to achieve superhuman performance.

## Overview

The methodology involves a two-stage training process where models are initially trained on human demonstration data through behavioral cloning, followed by reinforcement learning refinement. This approach has been notably successful in complex game environments where pure reinforcement learning from scratch would be computationally prohibitive or unstable. ^[rlgym-rocket-league-rl-environment.md]

## Implementation in RLGym

The most prominent implementation of PPO + Replay Pretraining occurs in the [[RLGym — Rocket League Reinforcement Learning Environment]], where it has been used to create competitive AI agents for Rocket League. The Nexto bot (V2) achieved Grand Champion 1 level performance using this methodology, ranking in the top 0.12% in 1v1 matches, top 0.95% in 2v2, and top 0.46% in 3v3 gameplay. ^[rlgym-rocket-league-rl-environment.md]

The training process combines:
- **Behavioral cloning phase**: Learning from human replay data to establish baseline competency
- **PPO refinement phase**: Using reinforcement learning to optimize beyond human-level performance
- **Parallel training infrastructure**: Leveraging RocketSim's high-speed physics simulation (114,481 ticks/sec) for efficient data generation

## Technical Architecture

The approach utilizes modular components within the RLGym ecosystem:

### Pretraining Stage
- Human replay parsing through rlgym-tools
- Supervised learning on demonstration trajectories
- Establishment of reasonable baseline policies

### RL Fine-tuning Stage
- [[Proximal Policy Optimization (PPO)]] implementation via rlgym-learn-algos
- High-throughput training using RLGymPPO_CPP (70,000 steps/sec)
- Parallel environment execution for sample efficiency

## Inspiration and Connections

This methodology draws inspiration from OpenAI's Video Pre-Training (VPT) approach, which demonstrated the effectiveness of combining imitation learning with reinforcement learning for complex control tasks. The technique represents a practical solution to the cold-start problem in reinforcement learning, where agents must learn complex behaviors from scratch. ^[rlgym-rocket-league-rl-environment.md]

## Performance Results

The Nexto bot represents the most successful application of this methodology, achieving:
- Diamond to Grand Champion level gameplay
- Competitive performance against human players across multiple game modes
- Significant improvement over pure RL approaches (previous Necto V1 bot)

However, development challenges led to the cancellation of the Tecko (V3) project due to "lack of improvement" over Nexto, suggesting potential limitations in scaling this approach further. ^[rlgym-rocket-league-rl-environment.md]

## Limitations and Considerations

While successful in the gaming domain, PPO + Replay Pretraining faces several constraints:
- Heavy dependence on high-quality human demonstration data
- Computational requirements for both pretraining and RL phases
- Limited documented applications outside of game environments
- Potential performance plateaus as demonstrated by the Tecko project cancellation

The methodology remains primarily community-driven rather than academically validated, with limited peer-reviewed research at major machine learning venues. ^[rlgym-rocket-league-rl-environment.md]
