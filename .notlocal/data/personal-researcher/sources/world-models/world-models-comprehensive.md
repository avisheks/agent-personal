---
title: "World Models — Comprehensive Deep Dive"
url: https://arxiv.org/abs/1803.10122
ingestedAt: 2026-06-09
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2301.04104
  - https://arxiv.org/abs/2402.15391
  - https://arxiv.org/abs/2405.15461
  - https://arxiv.org/abs/2310.06305
  - https://arxiv.org/abs/2309.02570
  - https://arxiv.org/abs/2310.16828
  - https://arxiv.org/abs/1911.01547
  - https://arxiv.org/abs/2010.06194
  - https://arxiv.org/abs/2209.00588
---

# World Models — Deep Dive

## Definition
Internal learned models predicting how environments evolve in response to actions. Enable agents to "imagine" future states for planning, decision-making, and sample-efficient learning.

## Spectrum
1. Simple latent dynamics (linear, MLP)
2. RSSM-based (Dreamer family: stochastic + deterministic)
3. Transformer-based (IRIS: autoregressive in latent space)
4. Diffusion-based (DIAMOND: full-fidelity visual prediction)
5. Foundation video world models (Sora, Cosmos, Genie 2: billions of params)

## Key Papers & Results
- Ha & Schmidhuber (2018): VAE+RNN+Controller (867 params), CarRacing 906
- DreamerV2 (2021): First human-level world model on Atari 55
- DreamerV3 (Nature 2024): 150+ tasks single config, first Minecraft diamonds
- MuZero (Nature 2020): Superhuman without game rules
- IRIS (ICLR 2023): HNS 1.046, 2hrs gameplay
- DIAMOND (NeurIPS 2024 Spotlight): HNS 1.46, neural game engine
- Genie (2024): 11B params, unsupervised latent actions
- Genie 2 (2024): Interactive 3D worlds, 1 min consistency
- Sora (2024): DiT, spacetime patches, "Video as World Simulators"
- GAIA-1 (Wayve): 9B+ params, driving scaling laws confirmed
- V-JEPA (Meta): 1.5-6x efficiency, predict representations not pixels
- Cosmos (NVIDIA, 2025): Open-weight world foundation model platform
- TD-MPC2 (ICLR 2024): 317M agent, 80 tasks
- R2I (ICLR 2024): SSMs in world models, superhuman Memory Maze

## Architecture Innovations
- VAE+RNN (2018) → RSSM (Dreamer) → Transformer (IRIS) → Diffusion (DIAMOND) → DiT (Sora)
- JEPA: predict in representation space, not pixels (Meta/LeCun)
- Scaling laws confirmed for driving (GAIA-1) and RL (TD-MPC2)

## Industry Success Stories
- OpenAI Sora: video generation as world simulation
- DeepMind Genie 2: interactive 3D world generation from single image
- NVIDIA Cosmos: open-weight physical AI world foundation model
- Wayve GAIA-1: 9B+ driving world model with confirmed scaling laws
- DeepMind MuZero: planning without rules (Nature 2020)

## Open Problems
- Long-horizon consistency (max ~1 minute for best models)
- Grounding in physical laws (learn correlations, not causality)
- Real-time inference for interactive applications
- Evaluation metrics (no consensus beyond FVD + agent scores)
- Sim-to-real transfer guarantees
