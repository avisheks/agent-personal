---
title: LLM-Based Behavior Simulators for Ads & Search
summary: Using LLMs to simulate shopper/advertiser behavior for offline testing of search ranking, ad systems, and marketplace dynamics. Key systems: Agent4Rec (1K agents, SIGIR 2024), Google RecSim NG + YouTube Music (SIGIR 2024), BASES (web search simulation, EMNLP 2024), Shop-r1 (RL-aligned shopping).
sources:
  - sources/genai-search-ads/llm-behavior-simulators-ads-search.md
createdAt: 2026-06-08
updatedAt: 2026-06-08
---

# LLM-Based Behavior Simulators for Ads & Search

## What It Is

Prompting LLMs with user/advertiser personas to generate realistic interaction sequences (queries, clicks, bids, conversions) for **offline policy evaluation** — replacing expensive live A/B tests.

## Four Technical Approaches

| Approach | How It Works | Example Systems |
|----------|-------------|-----------------|
| LLM-as-User | Persona-prompted LLM generates queries, clicks, purchases | Agent4Rec, BASES, Shop-r1, Customer-R1 |
| LLM-as-Advertiser | Simulates bidding, budget allocation, creative decisions | InfoBid, LBM, Synthetic Labs |
| Generative Environment | LLMs generate full marketplace dynamics | RecSim NG, LLM-Augmented Digital Twin |
| Hybrid | LLM personas + classical simulation engines | CXSimulator, Lusifer |

## Company Map

| Company | Published System | Venue | What It Simulates |
|---------|-----------------|-------|------------------|
| **Google** | RecSim NG + YouTube Music | SIGIR 2024 | Preference elicitation policies without live experiments |
| **Google** | Controllable User Simulation | 2026 | Simulation as causal inference (DeepMind) |
| **Amazon** | Synthetic Query Gen | WWW 2024 | 8 queries/product for cold-start |
| **Amazon** | MiniELM User Simulation | ACL 2025 | E-commerce shopper RL training |
| **Microsoft** | BASES | EMNLP 2024 | Large-scale web search behavior |
| **ByteDance** | PersonaAct | 2026 | Short-video users for filter bubble auditing |
| **ByteDance** | LLM-Augmented Digital Twin | 2026 | Four-twin platform policy evaluation |
| **Meta** | (No public papers) | — | Likely proprietary internal |

## Seminal Papers

| Paper | Year | Impact | Key Result |
|-------|------|--------|-----------|
| Agent4Rec | SIGIR 2024 | 349 citations | 1,000 LLM agents simulate movie rec behavior |
| RecAgent | 2023/2025 | 258 citations | Sandbox environment for user behavior |
| EconAgent | ACL 2024 | 244 citations | LLM agents for macroeconomic simulation |
| CXSimulator | CIKM 2024 | 17 citations | Marketing campaign assessment offline |
| Shop-r1 | 2025 | 14 citations | RL-aligned shopping behavior |
| Learning from Synthetic Labs | 2025 | 12 citations | LLMs replicate risk-averse auction bidding |

## Practical Applications

1. **Offline policy evaluation**: Test ranking/bidding changes without live traffic (Google YouTube Music)
2. **A/B test acceleration**: Simulate outcomes before expensive live test (SimGym, CXSimulator)
3. **Adversarial testing**: Simulate bad actors, policy violations (TruthMarketTwin, Amazon adversarial queries)
4. **RL training environments**: Train agents against simulated users (Lusifer, Shop-r1)
5. **Privacy-safe synthetic data**: Generate interaction data without real user PII (BASES, GLIDE)

## Key Challenges

1. **Calibration**: LLMs converge toward "positive average person" — systematically diverge from real tail behavior (SYN-DIGITS shows 50% improvement with calibration framework)
2. **Scale**: Agent4Rec = 1,000 agents vs billions of real users
3. **Advertiser side underdeveloped**: Most work simulates demand (users) not supply (advertisers)
4. **Validation**: How to prove simulated results predict real A/B test outcomes?
5. **Meta's opacity**: Likely has advanced internal systems but nothing published

## Decision Framework: When to Use Simulation vs Live A/B

| Signal | → Simulation | → Live A/B |
|--------|-------------|-----------|
| Risk of change | High (could lose revenue) | Low (safe to test) |
| Traffic availability | Insufficient for statistical power | Abundant |
| Speed requirement | Need results in hours, not weeks | Can wait 2-4 weeks |
| Privacy constraints | Cannot expose users to untested system | Standard consent applies |
| Change magnitude | Large (new algorithm) | Small (parameter tweak) |

## Related

- [[Gen-AI Applied to Search and Advertising (2024-2026)]]
- [[Double-Randomized Experimentation]]
- [[Adoption Ceiling Problem]]
- [[Multi-Stage Recommendation Pipeline]]
