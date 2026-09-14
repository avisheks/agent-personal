---
title: "World Models — Overview and SOTA"
summary: "Internal learned models predicting environment evolution. Spectrum: latent dynamics → RSSM (Dreamer) → Transformer (IRIS) → Diffusion (DIAMOND) → Foundation (Sora/Genie 2/Cosmos). SOTA: DreamerV3 (150+ tasks, Minecraft diamonds, Nature 2024), DIAMOND (HNS 1.46, NeurIPS 2024), Genie 2 (3D interactive worlds), Sora (DiT video world sim). Industry: OpenAI, DeepMind, NVIDIA, Wayve."
sources:
  - sources/world-models/world-models-comprehensive.md
createdAt: 2026-06-09
updatedAt: 2026-06-09
---

# World Models

## Definition

Internal learned models that predict how environments evolve in response to actions. They enable "imagination" — agents plan by simulating future states without interacting with the real environment.

## The Spectrum (Simplest → Most Ambitious)

| Level | Architecture | Example | Scale |
|-------|-------------|---------|-------|
| Latent dynamics | MLP/Linear | Simple MBRL | <1M params |
| RSSM (stochastic+deterministic) | RNN-based | Dreamer v1/v2/v3 | ~100M params |
| Transformer world model | Autoregressive tokens | IRIS, Genie | 100M-11B params |
| Diffusion world model | Denoising process | DIAMOND, UniSim | 100M-1B params |
| Foundation video world model | DiT / large diffusion | Sora, Cosmos, Genie 2 | 1B-100B+ params |

## Key Technological Innovations

### Architecture Evolution

```
VAE + RNN (Ha 2018) → RSSM (Dreamer 2019) → Discrete RSSM (DreamerV2 2021)
    → Transformer (IRIS 2023) → Diffusion (DIAMOND 2024) → DiT (Sora 2024)
    → JEPA (V-JEPA 2024: predict representations, not pixels)
```

### Critical Design Choices

| Choice | Impact | Evidence |
|--------|--------|----------|
| Predict in latent space vs pixels | 1.5-6x efficiency | V-JEPA (Meta 2024) |
| Discrete vs continuous latents | Enables autoregressive; DreamerV2 breakthrough | ICLR 2021 |
| Diffusion vs discrete tokenization | +40% agent performance (visual fidelity matters) | DIAMOND (NeurIPS 2024) |
| Scaling model size | Power-law improvement (like LLMs) | GAIA-1, TD-MPC2 |
| Single config across domains | Removes per-domain tuning entirely | DreamerV3 (Nature 2024) |

### The JEPA Insight (LeCun/Meta)

Generative models waste capacity predicting unpredictable details (individual leaf movements). JEPA predicts in **abstract representation space**, discarding irrelevant variation. V-JEPA achieves 1.5-6x training efficiency over pixel-prediction approaches.

## SOTA World Models (2024-2026)

### For RL/Planning

| Model | Venue | Key Achievement |
|-------|-------|----------------|
| **DreamerV3** | Nature 2024 | 150+ tasks single config; first Minecraft diamonds without human data |
| **DIAMOND** | NeurIPS 2024 Spotlight | HNS 1.46 on Atari 100k (best world-model agent); neural game engine |
| **TD-MPC2** | ICLR 2024 | Single 317M agent across 80 tasks; scaling laws for MBRL |
| **R2I** | ICLR 2024 | SSMs in world models; superhuman Memory Maze |
| **IRIS** | ICLR 2023 | HNS 1.046 from 2hrs gameplay; Transformer world model |

### For Video/Interactive Worlds

| Model | Lab | Key Achievement |
|-------|-----|----------------|
| **Sora** | OpenAI | DiT video generation as world simulation; emergent 3D + physics |
| **Genie 2** | DeepMind | Interactive 3D worlds from single image; 1 min consistency |
| **Genie** | DeepMind | 11B params; learns latent actions unsupervised from video |
| **UniSim** | DeepMind | Zero-shot sim-to-real from learned simulator |
| **GameGen-X** | 2024 | 1M+ gameplay clips from 150 games; diffusion transformer |
| **Cosmos** | NVIDIA 2025 | Open-weight world foundation model for physical AI |

### For Autonomous Driving

| Model | Lab | Key Achievement |
|-------|-----|----------------|
| **GAIA-1** | Wayve | 9B+ params; scaling laws confirmed; action+text conditioned |
| **DriveDreamer** | 2023 | First real-world driving world model (nuScenes) |
| **ViDAR** | 2023 | Visual point cloud forecasting; -15% collision rate |

## Industry Success Stories

| Company | Achievement | Significance |
|---------|-------------|-------------|
| **OpenAI** | Sora: "Video Generation Models as World Simulators" | Established video-as-world-model paradigm |
| **DeepMind** | Genie 2: interactive 3D worlds from single image | Unlimited training environments for agents |
| **DeepMind** | MuZero: superhuman without game rules (Nature 2020) | Learned world model replaces hand-coded simulator |
| **NVIDIA** | Cosmos: open-weight world foundation model | Infrastructure for physical AI (robotics, driving) |
| **Wayve** | GAIA-1: 9B+ driving world model | Confirmed LLM-like scaling laws for world models |

## Academic Success Stories

| Work | Venue | Contribution |
|------|-------|-------------|
| Ha & Schmidhuber (2018) | NeurIPS Workshop | Founded the field; dream training; 867-param controller |
| Dreamer v1/v2/v3 | ICLR/Nature | Proved world models are general-purpose; Minecraft diamonds |
| MuZero (2020) | Nature | Unified planning + model-free via learned model |
| JEPA (LeCun, 2022) | Position paper | Theoretical framework: predict representations, not pixels |
| DIAMOND (2024) | NeurIPS Spotlight | Visual fidelity matters; diffusion > discrete tokenization |
| R2I (2024) | ICLR | Long-term memory via SSMs; superhuman Memory Maze |

## Open Problems

1. **Long-horizon consistency**: Best models maintain physics for ~1 minute max
2. **Physical law grounding**: Learn correlations, not causality
3. **Real-time inference**: Billion-param models too slow for interactive use
4. **Evaluation metrics**: No consensus beyond FVD + agent performance
5. **Sim-to-real transfer**: UniSim showed zero-shot works, but remains fragile
6. **Action conditioning**: Tension between unconditional quality and precise control

## Related

- [[Multi-Agent RL Ecosystems and Advertising Applications]]
- [[RLGym — Rocket League Reinforcement Learning Environment]]
- [[Self-Evolving Agents]]
