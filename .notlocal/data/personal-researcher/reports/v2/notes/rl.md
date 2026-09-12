# Reinforcement Learning: Environments, Algorithms, and Applications

> **Last Updated:** 2026-06-09 | **Read time:** ~12 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#RLGym]] | [[#RL Environments Landscape]] | [[#Multi-Agent RL Ecosystems]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** The RL environments landscape split into two worlds: (1) game/robotics RL using Gymnasium/Isaac Lab/MuJoCo with PPO/SAC, and (2) LLM post-training RL using veRL/TRL/NeMo-RL with GRPO/DPO. The game world's headline: RLGym's Nexto bot reached Grand Champion 1 in Rocket League (top 0.12%). The LLM world's headline: DeepSeek-R1 showed pure GRPO produces emergent reasoning. For multi-agent: JaxMARL (NeurIPS 2024) achieves 12,500x speedup; MAAB scales advertising MARL to millions via mean-field.

---

## RLGym — Rocket League RL Environment

### What It Is

The only RL environment for training bots to play Rocket League — a 3D physics-based car soccer game with continuous action spaces.

| Property | Value |
|----------|-------|
| GitHub | github.com/RLGym/rlgym, 240 stars |
| API | Gym-like step/reset (independent implementation) |
| Physics | RocketSim (C++): 114K ticks/sec, ~10 days of game per minute |
| Training | rlgym-learn (Rust): parallel, or RLGymPPO_CPP: 70K steps/sec |
| Algorithm | PPO + replay-based pretraining |
| License | Apache-2.0 |

### Key Achievements

| Bot | Level | Human Percentile | Year |
|-----|-------|:----------------:|------|
| Necto (V1) | Diamond | Top ~15% | 2022 |
| Nexto (V2) | Grand Champion 1 | Top 0.12% (1v1) | 2023 |

**Nexto** combined behavioral cloning from human replays (inspired by OpenAI's Video PreTraining paper) with PPO reinforcement learning. This mirrors the SFT → RL pipeline now standard in LLM post-training.

### Architecture

```
rlgym (meta-package)
├── rlgym-api (zero-dep Gym-like interface)
├── rlgym-rocket-league (game-specific implementation)
│   └── RocketSim (C++ physics backend)
├── rlgym-learn (Rust-based parallel training)
│   └── rlgym-learn-algos (PPO)
└── rlgym-tools (SB3 compat, replay parsing, rewards)
```

### Limitations

- No non-gaming industry usage
- No major papers at NeurIPS/ICML/ICLR — community-driven
- Main bot project (Nexto) development stopped; framework still maintained
- 240 stars (niche vs Gymnasium 12K, Unity ML-Agents 19.5K)

---

## RL Environments Landscape (2026)

### Game / Robotics RL

| Framework | Stars | Focus | Best For |
|-----------|:-----:|-------|----------|
| Gymnasium (Farama) | 12K | Standard single-agent API | Any RL research (de facto standard) |
| Unity ML-Agents | 19.5K | Game AI training | 3D game environments |
| MuJoCo (DeepMind) | 13.8K | Physics simulation | Robotics, locomotion |
| Isaac Lab (NVIDIA) | 7.4K | GPU-accelerated robotics | Sim-to-real transfer at scale |
| PettingZoo (Farama) | 3.4K | Multi-agent RL | Competitive/cooperative games |
| Brax (Google) | 3.2K | JAX physics | Massively parallel (millions steps/sec on TPU) |
| RLGym | 240 | Rocket League | The only option for RL bots |

### LLM Post-Training RL

| Framework | Stars | Key Feature |
|-----------|:-----:|------------|
| veRL (ByteDance) | 21.9K | HybridFlow, 15+ algorithms, multi-hardware |
| TRL (HuggingFace) | 18.6K | GRPO/DPO/SFT, HF ecosystem |
| NeMo-RL (NVIDIA) | 1.7K | Ray-based, multi-backend, FP8 |

### Key Trend

The two RL worlds are converging: game RL's "pretrain → RL" (Nexto) and LLM RL's "SFT → RLHF" are the same pattern. The difference is just the environment (physics sim vs token generation).

---

## Multi-Agent RL Ecosystems

### Framework Selection Guide

| Need | Framework | Why |
|------|-----------|-----|
| API standard | PettingZoo (3.4K) | De facto MARL API, framework-agnostic |
| Game theory | OpenSpiel (5.3K) | Broadest game + algorithm coverage |
| GPU speed | JaxMARL (814) | 12,500x speedup, NeurIPS 2024 |
| Production scale | RLlib (35K+) | Distributed, flexible policy mapping |
| Millions of agents | MAgent2 (333) | Only framework for 100K-1M+ |
| Heterogeneous agents | HARL (920) | Monotonic improvement guarantees, JMLR 2024 |
| Advertising/auctions | RLlib + mean-field | MAAB's approach for advertiser-scale |

### Industry Landmarks

| System | Achievement | Scale |
|--------|-------------|-------|
| AlphaStar (DeepMind) | Grandmaster StarCraft (top 0.2%) | Multi-agent league training |
| OpenAI Five | Beat Dota 2 world champs OG | 128K CPUs, 180 yrs gameplay/day |
| Meta Cicero | Top 10% human Diplomacy | NLP + game theory |
| OpenAI Hide-and-Seek | 6 emergent strategy phases | Autocurriculum |

### Advertising Applications

| System | Platform | Result |
|--------|----------|--------|
| MAAB (WSDM 2022) | Alibaba | Mean-field scales to millions; bar agents prevent collusion |
| MACG (2021) | Taobao | Cooperative bidding + platform revenue constraint |
| MoTiAC (ECML 2022) | Tencent | Multi-objective RTB, Pareto convergence |
| GAVE (NeurIPS 2024) | Competition | Won AIGB auto-bidding competition |
| QGA (2026) | Production | **3.27% Ad GMV increase** in real A/B test |

### Why MARL for Ads?

Traditional RL assumes static environment. Reality: advertisers **react** to each other. MARL captures strategic interactions, non-stationarity, and enables collusion prevention via mechanism design (bar agents, revenue constraints).

**Scale strategy:** Mean-field approximation — group millions of advertisers by objective type, model aggregate, optimize against distribution (not N-1 individuals).

### Scale by Framework

| Scale | Frameworks |
|-------|-----------|
| 2-20 agents | PettingZoo, EPyMARL, SMAC, JaxMARL, HARL |
| 20-100 | VMAS, RLlib, Unity ML-Agents |
| 100-1,000 | WarpDrive (1,024/env), MAgent2, RLlib |
| 1,000-1M+ | MAgent2, Mean Field MARL |
| Millions (ads) | MAAB mean-field grouping |

### GPU-Accelerated MARL

| Framework | Backend | Speedup |
|-----------|---------|:-------:|
| JaxMARL | JAX | 12,500x |
| WarpDrive | CUDA | 100x+ |
| Mava | JAX | End-to-end JIT |
| VMAS | PyTorch CUDA | Tens of thousands parallel |

---

## References

- [1] RLGym — github.com/RLGym/rlgym — Apache-2.0, 240 stars
- [2] RocketSim — github.com/ZealanL/RocketSim — C++ physics, 119 stars
- [3] RLBot — github.com/RLBot/RLBot — Bot framework, 615 stars
- [4] Gymnasium — github.com/Farama-Foundation/Gymnasium — v1.3.0, 12K stars
- [5] Isaac Lab — github.com/isaac-sim/IsaacLab — v3.0.0-beta, 7.4K stars
- [6] MAAB — Wen et al. (WSDM 2022) — Multi-agent auto-bidding for Alibaba; mean-field scaling
- [7] JaxMARL — FLAIROx (NeurIPS 2024) — 12,500x speedup via JAX vectorization
- [8] PettingZoo — Farama Foundation — v1.26.1, 3.4K stars, MARL API standard
- [9] MAgent2 — Farama Foundation — v0.3.4, designed for 100K-1M+ agents
- [10] HARL — PKU (JMLR 2024) — Heterogeneous-agent RL with monotonic improvement guarantees

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-09 | Added Multi-Agent RL Ecosystems section | 13+ MARL frameworks, industry landmarks (AlphaStar, OpenAI Five, Cicero), advertising applications (MAAB, QGA 3.27% GMV, GAVE NeurIPS winner), scale strategies |
| 2026-06-09 | Verified | Score: 82% → report corrected in-place (12 claims across 5 sections) |
| 2026-06-09 | Initial v2 generation | RLGym deep dive + RL environments landscape |
