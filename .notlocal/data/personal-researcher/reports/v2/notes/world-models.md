# World Models: Learned Environment Simulation

> **Last Updated:** 2026-06-09 | **Read time:** ~15 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#What Are World Models]] | [[#Architecture Evolution]] | [[#SOTA Models]] | [[#Industry Success]] | [[#Academic Success]] | [[#Open Problems]] | [[#References]]

---



## References

- [1] Ha & Schmidhuber (2018) — "World Models" — arXiv:1803.10122
- [2] Hafner et al. (2023) — "DreamerV3: Mastering Diverse Domains" — Nature 2024
- [3] Schrittwieser et al. (2020) — "MuZero" — Nature 2020
- [4] Alonso et al. (2024) — "DIAMOND" — NeurIPS 2024 Spotlight
- [5] Micheli et al. (2023) — "IRIS" — ICLR 2023 Notable Top 5%
- [6] Bruce et al. (2024) — "Genie" — arXiv:2402.15391
- [7] DeepMind (2024) — "Genie 2" — deepmind.google/discover/blog
- [8] OpenAI (2024) — "Sora: Video Generation Models as World Simulators" — openai.com
- [9] Hu et al. (2023) — "GAIA-1" — arXiv:2309.17080
- [10] Meta AI (2024) — "V-JEPA" — ai.meta.com/blog
- [11] NVIDIA (2025) — "Cosmos World Foundation Model" — arXiv
- [12] Yang et al. (2023) — "UniSim" — arXiv:2310.06305
- [13] Hansen et al. (2024) — "TD-MPC2" — ICLR 2024
- [14] Samsami et al. (2024) — "R2I: Recall to Imagine" — ICLR 2024
- [15] LeCun (2022) — "A Path Towards Autonomous Machine Intelligence" — openreview.net

---



## Quick Catchup

> **Quick Catchup (June 2026):** World models evolved from toy latent dynamics (Ha 2018, 867 params) to billion-parameter foundation models (Sora, Genie 2, Cosmos). Three paradigm shifts: (1) DreamerV3 proved one config works across 150+ domains (Nature 2024), (2) DIAMOND proved diffusion > discrete tokenization for agent performance (NeurIPS 2024), (3) V-JEPA proved predicting representations > predicting pixels (1.5-6x efficiency).
> Key players: OpenAI (Sora), DeepMind (Genie 2, MuZero), NVIDIA (Cosmos), Wayve (GAIA-1), Meta (V-JEPA). Open problem: long-horizon consistency limited to ~1 minute.

---



## What Are World Models

Internal learned models that predict how environments evolve in response to actions. They enable agents to "imagine" futures for planning without real-world interaction.

| Property | World Model | Physics Engine | Video Generator |
|----------|:-----------:|:--------------:|:---------------:|
| Learned from data | Yes | Can be (e.g., MuZero) | Yes |
| Action-conditioned | Yes | Not necessarily | Usually no |
| Interactive/controllable | Some are (open problems remain) | Yes | Limited |
| Compact latent state | Yes | No (full state) | No |
| Supports planning | Yes | Yes | No |

**Key insight (Ha & Schmidhuber 2018):** A controller trained entirely in an imagined world can transfer to reality, though larger models (~100M+ params) are typically needed for robust performance. SFT and world models can both contribute to learning format and dynamics, but their specific roles depend on the context and architecture.


## Architecture Evolution

```
2018: VAE + RNN (Ha & Schmidhuber) — CarRacing 906, dream training
2019: RSSM (Dreamer V1) — stochastic + deterministic, continuous control
2021: Discrete RSSM (DreamerV2) — first human-level Atari world model agent
2023: Transformer (IRIS) — autoregressive latent tokens, HNS 1.046
2023: Universal Sim (UniSim) — multi-modal, zero-shot sim-to-real
2024: Diffusion (DIAMOND) — full-fidelity visual, HNS 1.46
2024: DiT (Sora) — spacetime patches, video as world simulation
2024: JEPA (V-JEPA) — predict representations not pixels, 1.5-6x efficiency
2024: Foundation (Genie 2) — interactive 3D worlds from single image
2025: Platform (Cosmos) — open-weight world foundation model
```

### Three Key Design Decisions

| Decision | Option A | Option B | Winner |
|----------|----------|----------|--------|
| Latent space | Continuous (Gaussian) | Discrete (categorical) | Discrete — DreamerV2 breakthrough |
| Generation | Pixel-level (diffusion) | Representation-level (JEPA) | Depends: JEPA for efficiency, diffusion for fidelity |
| Tokenization | VQ-VAE (discrete) | Full resolution (diffusion) | Diffusion — DIAMOND +40% agent performance (visual fidelity matters) |


## SOTA Models (2024-2026)

### RL/Planning World Models

| Model | Venue | Architecture | Key Achievement |
|-------|-------|:------------:|-----------------|
| **DreamerV3** | Nature 2024 | Discrete RSSM | 150+ tasks single config; first Minecraft diamonds |
| **DIAMOND** | NeurIPS 2024 Spotlight | Diffusion | HNS 1.46 (best) |
| **TD-MPC2** | ICLR 2024 | Implicit (no decoder) | 317M agent, 80 tasks, scaling laws for MBRL |
| **R2I** | ICLR 2024 | SSM + world model | Superhuman Memory Maze; long-term credit assignment |
| **IRIS** | ICLR 2023 | Transformer + VQ-VAE | HNS 1.046 |
| **MuZero** | Nature 2020 | Learned dynamics | Superhuman Go/Chess/Shogi/Atari without rules |

### Video/Interactive World Models

| Model | Lab | Architecture | Key Achievement |
|-------|-----|:------------:|-----------------|
| **Sora** | OpenAI | Diffusion Transformer (DiT) | 60s HD video; emergent 3D + physics |
| **Genie 2** | DeepMind | Autoregressive latent diffusion | 3D interactive worlds; 1 min consistency; action-controllable |
| **Genie** | DeepMind | Spatiotemporal tokenizer + AR | 11B params; unsupervised latent actions |
| **UniSim** | DeepMind | Video conditioned on action+text | Zero-shot sim-to-real transfer |
| **GameGen-X** | 2024 | Diffusion Transformer | 1M+ gameplay clips from 150 games |
| **Cosmos** | NVIDIA 2025 | World foundation model | Open-weight platform for physical AI |

### Autonomous Driving

| Model | Lab | Scale | Key Achievement |
|-------|-----|-------|----------------|
| **GAIA-1** | Wayve | 9B+ params, 4,700 hrs | Confirmed scaling laws for driving world models |
| **DriveDreamer** | 2023 | nuScenes | First real-world driving world model |
| **ViDAR** | 2023 | — | -15% collision rate via visual point cloud forecasting |


## Industry Success Stories

| Company | System | What It Proved |
|---------|--------|---------------|
| **OpenAI** | Sora | Scale video generation → emergent world understanding; "Video Generation Models as World Simulators" |
| **DeepMind** | Genie 2 | Single image → interactive 3D world; unlimited training environments for agents |
| **DeepMind** | MuZero | Learned world model fully replaces hand-coded game rules (Nature 2020) |
| **NVIDIA** | Cosmos | World models as infrastructure layer — open-weight foundation for robotics + driving |
| **Wayve** | GAIA-1 | GAIA-1 confirms LLM-like scaling laws for world models; 9B+ params from 4,700hrs London driving |
| **Meta** | V-JEPA | Predicting representations (not pixels) = 1.5-6x efficiency; LeCun's AMI path |


## Academic Success Stories

| Work | Venue | Foundational Contribution |
|------|-------|--------------------------|
| **Ha & Schmidhuber** | 2018 | Dream training and VAE+RNN framework; 867-param controller that transfers to reality |
| **DreamerV3** | Nature 2024 | Achieved 150+ tasks single config and first Minecraft diamonds without human data, demonstrating the general-purpose nature of world models |
| **MuZero** | Nature 2020 | Unified planning (board games) and model-free RL (visual) via learned model |
| **DIAMOND** | NeurIPS 2024 | Visual fidelity directly → agent performance; diffusion > discrete tokenization |
| **JEPA** (LeCun) | 2022 position paper | Theoretical: predict abstractions not pixels; discard unpredictable information |
| **R2I** | ICLR 2024 | State Space Models solve long-term memory in world models |
| **IRIS** | ICLR 2023 | First Transformer world model competitive on Atari without lookahead |


## Open Problems

| Problem | Current State | Why It's Hard |
|---------|--------------|---------------|
| **Long-horizon consistency** | Max ~1 minute (Genie 2) | Errors compound; no mechanism to enforce global consistency |
| **Physical law grounding** | Some models like Sora show emergent physics, but most learn correlations not causality | Conservation laws, rigid body constraints challenging to emerge consistently from video |
| **Real-time inference** | Billion-param models like Genie 2 may require distillation or optimizations for real-time use, potentially with quality reduction | Billion params + autoregressive = too slow for interactive |
| **Evaluation metrics** | FVD + agent scores (no consensus) | Physics accuracy, causality, consistency all unmeasured standardly |
| **Sim-to-real transfer** | UniSim: zero-shot works but fragile | Distribution shift between learned world and physical reality |
| **Action conditioning** | Tension: quality vs controllability | Unconditional models like Sora can achieve high fidelity in specific tasks; conditioned models may lose some quality but offer precise control depending on implementation |


## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-09 | Added World Models in Recommendation section | Emerging field: RecSim NG (Google YouTube Music), GoalRec (AAAI 2021), diffusion WMs (WWW 2025), MedDreamer (KDD 2026). Why Dreamer fails directly for rec. LLM-based world models. Growth trajectory 2019→2026. |
| 2026-06-09 | Verified | Score: 81% (21 claims corrected across 7 sections) |
| 2026-06-09 | Initial v2 generation | World models comprehensive: definition, architecture evolution, SOTA, industry, academia, open problems |

---

## Verification

| Metric | Value |
|--------|-------|
| Verification score | 81% |
| Verification model | GPT-OSS-120b (Bedrock) |
| Total claims | 126 |
| Correct | 87 |
| Corrected | 21 |
| Unverifiable | 18 |
| Verified at | 2026-06-09 18:45 UTC |
| Sections corrected | What Are World Models, Architecture Evolution, Academic Success Stories, Industry Success Stories, SOTA Models (2024-2026), Open Problems, Changelog |
