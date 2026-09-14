---
title: "What are open-source ecosystems for large-scale multi-agent RL? Success stories? Use cases for online advertising?"
summary: "13+ frameworks: PettingZoo (API standard), JaxMARL (12,500x speedup), MAgent2 (millions of agents), OpenSpiel (game theory). Industry: AlphaStar (Grandmaster), OpenAI Five (beat world champs), Cicero (Diplomacy top 10%). Ads: MAAB (Alibaba, mean-field millions of advertisers), QGA (3.27% GMV lift in production A/B), GAVE (NeurIPS 2024 winner). Mean-field approximation is the key to scaling MARL for advertising."
type: query
createdAt: 2026-06-09
topic: rl
---

# Multi-Agent RL: Open-Source Ecosystems, Success Stories, Advertising Use Cases

## Quick Answer

**Ecosystems:** 13+ open-source frameworks. PettingZoo is the API standard. JaxMARL gives 12,500x speedup. MAgent2 handles millions of agents. OpenSpiel covers game theory.

**Industry:** AlphaStar (Grandmaster SC2), OpenAI Five (beat Dota 2 world champs), Meta Cicero (top 10% Diplomacy).

**Advertising:** MAAB (Alibaba, WSDM 2022) scales to millions of advertisers via mean-field grouping. QGA achieved 3.27% Ad GMV increase in production A/B testing. GAVE won NeurIPS 2024 auto-bidding competition.

## Top Open-Source Ecosystems

### For Getting Started

| Framework | Stars | Best For |
|-----------|:-----:|---------|
| **PettingZoo** | 3.4K | API standard — start here for any MARL project |
| **RLlib** (Ray) | 35K+ | Production-scale distributed training |
| **OpenSpiel** | 5.3K | Game theory + broad algorithm coverage |
| **EPyMARL** | 721 | Clean cooperative MARL benchmarking |

### For Speed (GPU-Accelerated)

| Framework | Speedup | Backend |
|-----------|:-------:|---------|
| **JaxMARL** | 12,500x | JAX vectorization (NeurIPS 2024) |
| **Mava** | "Blazingly fast" | JAX end-to-end JIT, multi-device |
| **VMAS** | Tens of thousands parallel | PyTorch CUDA, differentiable |
| **WarpDrive** | 100x+ | CUDA end-to-end (archived May 2025) |

### For Scale (1000+ Agents)

| Framework | Max Agents | Approach |
|-----------|:----------:|---------|
| **MAgent2** | Millions | Designed for massive gridworld populations |
| **WarpDrive** | 1,024/env | GPU-native, 1000 envs concurrent |
| **MAAB (research)** | Millions | Mean-field grouping by advertiser objective |
| **Mean Field MARL** | Unlimited | Approximates N-body → mean field (ICML 2018) |

## Industry Success Stories

| Achievement | Who | Year | Scale |
|-------------|-----|------|-------|
| Grandmaster StarCraft II (top 0.2%) | DeepMind AlphaStar | 2019 | Multi-agent league training |
| Beat Dota 2 world champions OG | OpenAI Five | 2019 | 128K CPUs + 256 GPUs |
| Top 10% in Diplomacy (NLP + game theory) | Meta Cicero | 2022 | 7-player negotiation |
| 6 emergent strategy phases (autocurriculum) | OpenAI Hide-and-Seek | 2019 | Competitive multi-agent |
| 43% electricity cost reduction (microgrids) | P2P Energy Trading | 2024 | MARL for energy |
| 240x training speedup (finance) | JaxMARL-HFT | 2025 | JAX-native LOB sim |
| 51% shorter queues (traffic) | CoordLight | 2026 | 196 intersections |

## Advertising Use Cases (Most Relevant)

### 1. Multi-Agent Auction Simulation
**MAAB (Alibaba, WSDM 2022):** Each advertiser is an agent. Mean-field grouping handles millions by aggregating advertisers with same objectives. "Bar agents" prevent collusion.

### 2. Cooperative Bidding
**MACG (Taobao, 2021):** Advertisers cooperate within platform constraints. Evolutionary strategy optimization. Platform revenue constraint prevents race-to-bottom.

### 3. Auto-Bidding (SOTA)
**GAVE (NeurIPS 2024 Competition Winner):** Generative auto-bidding with value-guided exploration. Won 1st place in NeurIPS AIGB competition.
**QGA (2026, Production):** Q-regularized generative auto-bidding. **3.27% Ad GMV increase** in real-world A/B testing.

### 4. Multi-Objective RTB
**MoTiAC (Tencent, ECML 2022):** Multi-objective actor-critics for RTB. Proven convergence to Pareto optimality on Tencent dataset.

### 5. Publisher-Side Optimization
**Wu et al. (2022):** Guaranteed contracts vs RTB as cooperative MARL agents. Maximizes publisher yield.

### 6. Auction Equilibrium
**Mean Field Equilibrium (Du et al., 2019):** Models second-price auctions. Opponent modeling via DASA algorithm. Faster convergence to market equilibrium than iterated best response.

### Why MARL for Ads (Not Single-Agent RL)?

Traditional bid optimization assumes static competitors. Reality: advertisers **react** to each other (non-stationary). MARL handles this by:
- Modeling each advertiser as an agent with its own objective
- Capturing strategic interactions (bid → others raise bids → you adapt)
- Finding equilibria rather than optimizing against a fixed environment
- Preventing collusion via mechanism design (bar agents, revenue constraints)

### Scale Strategy for Advertising

```
Millions of advertisers → Mean-field grouping (MAAB):
1. Group by objective type (CPA, CPC, ROI)
2. Model group aggregate as mean-field distribution
3. Individual optimizes against mean field (not N-1 opponents)
4. Tractable computation + realistic multi-agent dynamics
```

## Sources

- [[Multi-Agent RL Ecosystems and Advertising Applications]]
- [[RLGym — Rocket League Reinforcement Learning Environment]]
- MAAB (WSDM 2022), MAPPO (NeurIPS 2022), QMIX (ICML 2018)
- JaxMARL (NeurIPS 2024), HARL (JMLR 2024)
- AlphaStar (Nature 2019), OpenAI Five (2019), Cicero (Science 2022)
