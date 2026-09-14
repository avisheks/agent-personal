---
title: "World Models in Recommendation Systems"
summary: "Emerging field (rapid growth 2024-2026). World models ARE used in rec systems under different names (user simulators, environment models). RecSim NG (Google) is functionally a world model for YouTube Music. Explicit adoption: GoalRec (AAAI 2021), DARLR (SIGIR 2025), diffusion-based world models (WWW 2025), MedDreamer (KDD 2026, Dreamer for clinical recs). Direct Dreamer/MuZero application fails due to million-item action spaces and per-user dynamics."
sources:
  - sources/world-models/world-models-in-recommendation-systems.md
createdAt: 2026-06-09
updatedAt: 2026-06-09
---

# World Models in Recommendation Systems

## Status: Yes, But Under Different Names

World models ARE used in recommendation systems — primarily as "user simulators" and "environment models." The explicit "world model" framing emerged in 2021 (GoalRec, AAAI) and is now mainstream (10+ papers/year at top venues by 2025-2026).

## The Concept Mapping

| World Model | Recommendation |
|-------------|---------------|
| Environment | User + platform + catalog |
| State | Latent preferences + history |
| Action | What to recommend |
| Transition | How preferences evolve after seeing rec |
| Reward | Engagement (click, watch, buy) |
| Imagination/rollout | Simulate multi-step user trajectories |
| Planning | Select recs maximizing long-term engagement |

## Key Systems

### RecSim NG (Google) = The Industry World Model

RecSim NG (2021) is functionally a world model: probabilistic, differentiable, multi-agent simulator for recommender ecosystems. Applied to YouTube Music (SIGIR 2024) for offline policy evaluation — reducing need for live A/B tests.

### Explicit "World Model" Papers for Rec

| Paper | Year | Venue | What's Novel |
|-------|------|-------|-------------|
| GoalRec | AAAI 2021 | First explicit "world model" for rec; item-independent; disentangled value |
| Sim2Rec | ICDE 2023 | Zero-shot policy transfer; handles sim-to-real gap |
| DARLR | SIGIR 2025 | Dual-agent offline RL with "frozen world models" |
| Reward Balancing | WWW 2025 | **Diffusion-based** world model for user uncertainty |
| MedDreamer | KDD 2026 | **Dreamer architecture** adapted for clinical treatment rec |
| RecoWorld | ACM 2026 | Blueprint for agentic recommender simulation environments |
| AlignUSER | 2026 | World modeling = next-state prediction for rec evaluation |

### LLM-Based World Models for Rec (2025-2026)

LLMs serving as user simulators = world models for recommendation:
- AAAI 2025: LLM-powered user simulator (74 citations) — ensemble logical + statistical
- 2026: RL with LLM-augmented user simulations; LifeSim (long-horizon life simulator)
- Survey (2026): "LLM as virtual user or world model responsible for generating feedback"

## Why Dreamer/MuZero Don't Work Directly

| Challenge | Games/Robotics | Recommendation |
|-----------|:--------------:|:--------------:|
| Action space | Small (≤100) | Millions of items |
| Environments | One | Millions of users |
| Observability | Often full | Deeply partial (latent preferences) |
| Noise | Low (physics) | High (mood, context, time) |
| Data | Unlimited sim | Biased offline logs only |
| Dynamics | Stationary | Non-stationary (preference drift) |

## What "DreamerV3 for Rec" Would Need

1. **Hierarchical action space**: Categories → items (not flat millions)
2. **User-conditional dynamics**: World model conditioned on user embedding
3. **Non-stationarity handling**: Continual learning of dynamics
4. **Multi-objective reward**: Engagement + diversity + satisfaction + fairness
5. **Offline learning**: Must learn from biased logged data

MedDreamer (KDD 2026) is the closest existing adaptation — uses Dreamer's latent imagination for treatment recommendation.

## Industry Success Stories

| Company | System | Application |
|---------|--------|------------|
| Google | RecSim NG + YouTube Music (SIGIR 2024) | Offline preference elicitation evaluation |
| Spotify | RL for long-term audio optimization (2023) | Real-world deployment of model-based planning |
| General | LLM user simulators as world models | A/B test acceleration, offline policy evaluation |

## Growth Trajectory

```
2019: RecSim (Google) — configurable simulator, no "world model" label
2020: Pseudo Dyna-Q — Dyna-Q with learned user model (implicit world model)
2021: GoalRec — first explicit "world model" for rec (AAAI)
2023: Sim2Rec, Adversarial environment models (ICDE, NeurIPS)
2024: ROLER, CIKM — offline RL with world model evaluation
2025: Diffusion world models (WWW), dual-agent (SIGIR), LLM simulators (AAAI)
2026: MedDreamer (KDD), RecoWorld (ACM), LLM-RL surveys — mainstream
```

**Verdict: Emerging area with clear institutional momentum, not a dead end.**

## Related

- [[World Models — Overview and SOTA]]
- [[LLM-Based Behavior Simulators for Ads & Search]]
- [[Multi-Agent RL Ecosystems and Advertising Applications]]
- [[LLM Quality for User Behavior Modeling and Sequence Prediction]]
