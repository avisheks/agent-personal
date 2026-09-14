---
title: "Multi-Agent RL Ecosystems, Success Stories, and Advertising Applications"
url: https://github.com/Farama-Foundation/PettingZoo
ingestedAt: 2026-06-09
type: synthesis
additional_sources:
  - https://github.com/google-deepmind/open_spiel
  - https://github.com/google-deepmind/meltingpot
  - https://github.com/instadeepai/Mava
  - https://github.com/FLAIROx/JaxMARL
  - https://github.com/Farama-Foundation/MAgent2
  - https://github.com/salesforce/warp-drive
  - https://github.com/PKU-MARL/HARL
  - https://arxiv.org/abs/2202.03634
  - https://arxiv.org/abs/2106.06135
---

# Multi-Agent RL: Ecosystems, Success Stories, Advertising Use Cases

## Top Frameworks (by Stars, June 2026)

| Framework | Stars | Key Differentiator | Max Agents | Status |
|-----------|-------|-------------------|:----------:|--------|
| Unity ML-Agents | 19.5K | 3D game engine integration | Variable | Active |
| OpenSpiel (DeepMind) | 5.3K | Game theory + MARL, broadest game coverage | N-player | Active |
| PettingZoo (Farama) | 3.4K | API standard for MARL | Variable | Active |
| RLlib (Ray) | 35K+ | Production-scale distributed | No limit | Active |
| MAgent2 (Farama) | 333 | Designed for 100s to millions of agents | Millions | Active |
| MARLlib | 1.3K | Unifies 18 algos across 17 envs | 1000s (MAgent) | Low activity |
| HARL (PKU) | 920 | Heterogeneous agents, theoretical guarantees | Variable | Active (JMLR 2024) |
| Mava (InstaDeep) | 915 | JAX-native distributed MARL | Variable | Active |
| MeltingPot (DeepMind) | 841 | Social dilemma eval (50+ substrates) | Multi-player | Active |
| JaxMARL | 814 | Up to 12,500x speedup via JAX | Variable | Active (NeurIPS 2024) |
| BenchMARL (Meta) | 632 | Standardized benchmarking, TorchRL | Variable | Active |
| VMAS | 575 | Vectorized differentiable 2D physics | Up to 100 | Active |
| WarpDrive (Salesforce) | 502 | GPU-accelerated end-to-end MARL | 1,024/env | Archived May 2025 |

## Industry Success Stories

- **AlphaStar** (DeepMind, 2019): Grandmaster StarCraft II (top 0.2%), league-based multi-agent training
- **OpenAI Five** (2019): Defeated Dota 2 world champions OG; 128K CPUs + 256 GPUs; 180 years/day
- **Meta Cicero** (2022): Top 10% human Diplomacy; NLP + game-theoretic planning
- **Hide-and-Seek** (OpenAI, 2019): 6 emergent phases of strategy without explicit programming
- **Energy**: P2P microgrid trading: 43% cost reduction; EV charging: 5-12% higher profit
- **Finance**: JaxMARL-HFT: 240x training speedup; ABIDES-MARL: heterogeneous LOB simulation
- **Traffic**: CoordLight: 196 intersections; 51% shorter queues, 38% higher speeds

## Advertising Applications (MARL)

| Paper | Year | Platform | Key Innovation |
|-------|------|----------|---------------|
| MAAB | 2022 (WSDM) | Alibaba | Cooperative-competitive auto-bidding; mean-field for millions of advertisers; bar agents prevent collusion |
| MACG | 2021 | Taobao | Multi-agent cooperative bidding; evolutionary strategy; platform revenue constraint |
| MoTiAC | 2022 (ECML) | Tencent | Multi-objective RTB; Pareto convergence proved |
| GAVE | 2025 (NeurIPS) | Competition | Won NeurIPS 2024 AIGB competition; value-guided exploration |
| QGA | 2026 | Production | Q-regularized generative auto-bidding; 3.27% Ad GMV increase in A/B test |
| Mean Field Auctions | 2019 | — | Mean field equilibrium for second-price auctions; opponent modeling |
| Impression Allocation | 2022 | — | Publisher-side MARL: guaranteed vs RTB as cooperative agents |

## Scale by Framework

| Scale | Frameworks |
|-------|-----------|
| 2-20 agents | PettingZoo, EPyMARL, SMAC, JaxMARL, HARL, BenchMARL |
| 20-100 | VMAS, RLlib, Unity ML-Agents |
| 100-1,000 | WarpDrive (1,024/env), MAgent2, RLlib |
| 1,000-1M+ | MAgent2, Mean Field MARL |
| Millions (advertising) | MAAB (mean-field grouping by objective) |

## GPU-Accelerated MARL

| Framework | Backend | Speedup |
|-----------|---------|---------|
| JaxMARL | JAX | 12,500x vectorized |
| WarpDrive | CUDA | 100x+ over CPU |
| Mava | JAX | End-to-end JIT |
| VMAS | PyTorch CUDA | Tens of thousands parallel envs |
| JaxMARL-HFT | JAX | 240x for trading |
