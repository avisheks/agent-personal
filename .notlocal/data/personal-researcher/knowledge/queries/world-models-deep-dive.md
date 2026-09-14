---
title: "What are world models? Key innovations? SOTA? Industry and academia success stories?"
summary: "Internal learned models predicting environment evolution from actions. Architecture evolution: VAE+RNN (2018) → RSSM (Dreamer) → Transformer (IRIS) → Diffusion (DIAMOND HNS 1.46) → DiT (Sora) → JEPA (predict representations not pixels, 1.5-6x efficiency). SOTA: DreamerV3 (Nature, 150+ tasks), Genie 2 (interactive 3D worlds), Cosmos (open-weight physical AI). Industry: OpenAI, DeepMind, NVIDIA, Wayve. Open problem: long-horizon consistency (max ~1 min)."
type: query
createdAt: 2026-06-09
topic: world-models
---

# World Models — Deep Dive

## What Are World Models?

Internal learned models that predict how environments evolve in response to actions. They enable agents to "imagine" future states without real interaction — supporting planning, sample-efficient learning, and safe exploration.

**Not the same as:** Physics engines (hand-coded), video generation (unconditional), or simulators (explicit state).

## Key Technological Innovations

### Architecture Evolution

```
VAE+RNN (2018) → RSSM (Dreamer 2019) → Transformer (IRIS 2023) →
Diffusion (DIAMOND 2024) → DiT (Sora 2024) → JEPA (V-JEPA 2024)
```

### The Three Breakthroughs

1. **Discrete representations** (DreamerV2, 2021): Replaced Gaussian latents with categorical → first human-level world model on Atari

2. **Diffusion > discrete tokenization** (DIAMOND, 2024): Visual fidelity directly improves agent performance (+40% over tokenized approaches). "The bottleneck was information loss in compression."

3. **Predict representations, not pixels** (JEPA/V-JEPA, 2024): Discard unpredictable details → 1.5-6x training efficiency. LeCun's path toward Advanced Machine Intelligence.

### Confirmed Scaling Laws

GAIA-1 (Wayve, 9B+ params): Validation loss follows power-law vs compute, exactly like LLMs. "Significant room for improvement by scaling data and compute." TD-MPC2 confirmed similar scaling for model-based RL.

## SOTA World Models

### For RL/Planning (Agent Performance)

| Model | Venue | Key Number |
|-------|-------|-----------|
| DreamerV3 | Nature 2024 | 150+ tasks, single config, first Minecraft diamonds |
| DIAMOND | NeurIPS 2024 | HNS 1.46 on Atari 100k (best world-model agent) |
| TD-MPC2 | ICLR 2024 | 317M agent, 80 tasks, scaling laws |
| R2I | ICLR 2024 | Superhuman Memory Maze via SSMs |
| MuZero | Nature 2020 | Superhuman Go/Chess/Shogi without game rules |

### For Video/Interactive Worlds

| Model | Lab | Key Achievement |
|-------|-----|----------------|
| Sora | OpenAI | DiT video generation; emergent 3D + physics understanding |
| Genie 2 | DeepMind | Interactive 3D worlds from single image; 1 min consistency |
| Genie | DeepMind | 11B params; unsupervised latent actions from video |
| UniSim | DeepMind | Zero-shot sim-to-real transfer from learned simulator |
| Cosmos | NVIDIA | Open-weight world foundation model for physical AI |

### For Autonomous Driving

| Model | Lab | Scale |
|-------|-----|-------|
| GAIA-1 | Wayve | 9B+ params, 4,700 hrs London driving, scaling laws |
| DriveDreamer | 2023 | First real-world driving world model |

## Industry Success Stories

| Company | What They Did | Why It Matters |
|---------|--------------|----------------|
| **OpenAI** | Framed video generation as world simulation (Sora) | Paradigm: scale video models → emergent world understanding |
| **DeepMind** | Genie 2: interactive 3D worlds from one image | Unlimited training environments for embodied AI |
| **DeepMind** | MuZero: superhuman without game rules | Learned world model fully replaces hand-coded rules |
| **NVIDIA** | Cosmos: open-weight foundation world model | Infrastructure layer for all physical AI |
| **Wayve** | GAIA-1: confirmed world models scale like LLMs | Investment thesis: just scale data + compute |
| **Meta** | V-JEPA: 1.5-6x efficiency via representation prediction | Alternative to expensive pixel-level generation |

## Academic Success Stories

| Work | Year | Contribution |
|------|------|-------------|
| Ha & Schmidhuber | 2018 | Founded field: VAE+RNN, dream training, 867-param controller |
| DreamerV3 | 2023/Nature 2024 | General-purpose: 150+ tasks single config; Minecraft diamonds |
| MuZero | 2020/Nature | Planning via learned model; unified board games + Atari |
| DIAMOND | NeurIPS 2024 | Proved visual fidelity → agent performance; neural game engine |
| R2I | ICLR 2024 | SSMs solve long-term memory in world models |
| JEPA/V-JEPA | 2022/2024 | Theoretical + practical: predict abstractions not pixels |

## Open Problems

1. **Long-horizon consistency** — max ~1 minute (Genie 2); physics breaks over longer horizons
2. **Physical law grounding** — learns correlations, not causality; violates conservation laws
3. **Real-time inference** — billion-param models too slow for interactive applications
4. **Evaluation metrics** — no consensus beyond FVD + agent performance scores
5. **Sim-to-real transfer** — UniSim showed zero-shot possible but remains fragile

## Sources

- [[World Models — Overview and SOTA]]
- Ha & Schmidhuber (arXiv:1803.10122), DreamerV3 (Nature 2024), MuZero (Nature 2020)
- DIAMOND (NeurIPS 2024), IRIS (ICLR 2023), V-JEPA (Meta 2024)
- Sora (OpenAI 2024), Genie 2 (DeepMind 2024), GAIA-1 (Wayve 2023), Cosmos (NVIDIA 2025)
