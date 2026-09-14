---
title: "World Models in Online Recommendation Systems"
url: https://arxiv.org/abs/2010.12142
ingestedAt: 2026-06-09
type: synthesis
additional_sources:
  - https://dl.acm.org/doi/10.1145/3627043.3659573
  - https://arxiv.org/abs/2103.04357
  - https://arxiv.org/abs/2306.00543
  - https://arxiv.org/abs/2402.01135
---

# World Models in Recommendation Systems

## Status: Emerging Field (Rapid Growth 2024-2026)

World models ARE being used in recommendation — but mostly under different names ("user simulators," "environment models," "interaction models"). Explicit "world model" framing emerged 2021, accelerated 2024-2026. Now 10+ papers per year at top venues.

## The Mapping

| World Model Concept | Recommendation Equivalent |
|---|---|
| World/Environment | User behavior + platform dynamics + catalog |
| State | Latent user preferences + interaction history |
| Action | What to recommend (item/slate selection) |
| Transition | How preferences evolve after receiving recs |
| Reward | Engagement (clicks, watch time, purchases) |
| Rollout/Imagination | Simulating multi-step user trajectories |

## RecSim / RecSim NG (Google)

RecSim NG IS functionally a world model framework — probabilistic, differentiable, multi-agent simulator for recommender ecosystems. Used for YouTube Music preference elicitation (SIGIR 2024).

## Papers Explicitly Using "World Model" for Rec

| Paper | Year | Venue | Key Innovation |
|-------|------|-------|---------------|
| GoalRec | 2021 | AAAI | Item-independent world model + disentangled value function |
| Sim2Rec | 2023 | ICDE | Zero-shot policy transfer from simulator, handles reality gap |
| ROLER | 2024 | CIKM | Non-parametric reward > world model reward estimation |
| DARLR | 2025 | SIGIR | Dual-agent with "frozen world models" as environments |
| Reward Balancing | 2025 | WWW | **Diffusion-based world model** for user uncertainty |
| WorldModel-Rec | 2025 | ResearchGate | 4-component architecture with ethics regularization |
| Affective Music | 2026 | arXiv | Causal transformer world model for music feedback prediction |
| AlignUSER | 2026 | arXiv | World modeling = next-state prediction for rec evaluation |
| RecoWorld | 2026 | ACM | Blueprint for agentic recommender system environments |
| MedDreamer | 2026 | KDD | **Dreamer architecture** adapted for treatment recommendation |

## Industry

- Google: RecSim NG for YouTube Music (SIGIR 2024) — offline policy evaluation
- Spotify: RL for long-term audio recommendation optimization (2023)
- LLM-based user simulators as world models (AAAI 2025, 74 citations)

## Why Dreamer/MuZero Don't Work Directly

1. Action space: millions of items (vs small discrete/continuous in games)
2. Per-user dynamics: each user is a different environment
3. Extreme partial observability: preferences are deeply latent
4. Stochasticity: mood/context/time effects make transitions noisy
5. Offline only: can't freely explore (biased logged data)
6. Multi-agent: users, creators, platform interact

## Growth Trajectory

- 2019-2020: Implicit (RecSim, Pseudo Dyna-Q) without terminology
- 2021-2023: First explicit uses (GoalRec, Sim2Rec)
- 2024-2025: Rapid proliferation (diffusion, causal, offline RL)
- 2025-2026: LLM-based world models + explicit mainstream framing
