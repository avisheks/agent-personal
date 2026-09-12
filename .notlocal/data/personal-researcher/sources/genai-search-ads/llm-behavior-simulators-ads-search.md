---
title: LLM-Based Shopper & Advertiser Behavior Simulators in Online Search & Ads
url: https://arxiv.org/abs/2306.02552
ingestedAt: 2026-06-08
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2305.16291
  - https://arxiv.org/abs/2310.10108
  - https://arxiv.org/abs/2402.01135
  - https://arxiv.org/abs/2306.02552
  - https://arxiv.org/abs/2310.01949
  - https://dl.acm.org/doi/10.1145/3627043.3659573
  - https://arxiv.org/abs/2604.08891
  - https://arxiv.org/abs/2605.02879
---

# LLM-Based Behavior Simulators for Ads & Search

## Definition

LLM-based behavior simulators prompt LLMs with user/advertiser personas to generate realistic interaction sequences (queries, clicks, bids, purchases) for offline policy evaluation, A/B test acceleration, and adversarial testing — replacing expensive live experiments.

## Company Innovations

### Google
- **RecSim NG** (Mladenov et al., 2021): Probabilistic, differentiable multi-agent recommender ecosystem simulation
- **SIGIR 2024** (Hsu, Mladenov et al.): "Minimizing Live Experiments" — uses RecSim NG with YouTube Music for counterfactual preference elicitation policy evaluation
- **Controllable User Simulation** (May 2026, DeepMind): Formalizes controllable simulation as causal inference problem

### Meta
- No public "Whole Economy Simulation" papers; likely proprietary internal systems
- RL-enhanced ad text generation tested via large-scale A/B tests (2025)
- AI Agents for Business (WhatsApp/Messenger) demonstrate user intent modeling

### OpenAI
- Indirect contributions via Generative Agents foundation (Stanford/Google co-authored)
- Operator agent demonstrates user intent simulation for shopping
- Models power most third-party simulation research

### ByteDance/TikTok
- **PersonaAct** (2026): Personalized agents simulating short-video users for filter bubble auditing
- **LLM-Augmented Digital Twin** (Mar 2026): Four-twin architecture (User, Content, Interaction, Platform)
- Multi-Agent Video Recommenders (ACM 2026): Emergent behavior accuracy metrics

### Amazon
- Synthetic query generation (WWW 2024): 8 queries per product via fine-tuned LLMs
- RL-based user simulation for query rewriting (ACL 2025 Industry)
- LLMEvalRec (2026): Agentic framework simulating users for news rec evaluation
- Adversarial query generation (ACL 2025): GAN-like robustness testing

### Microsoft
- **BASES** (EMNLP 2024 Findings): Large-scale web search user simulation, generates diverse profiles at scale
- LLM as User Simulator for News Recommendation (SIGIR 2025)

## Key Academic Papers

| Paper | Venue | Citations | Key Contribution |
|-------|-------|-----------|-----------------|
| Agent4Rec | SIGIR 2024 | 349 | 1,000 LLM agents simulate real human behavior for movies |
| RecAgent | ACM Trans. 2025 | 258 | LLM agent framework + sandbox for user behavior simulation |
| AgentCF | WWW 2024 | 226 | Agent-based collaborative filtering (both user + item sides) |
| EconAgent | ACL 2024 | 244 | LLM agents for macroeconomic simulation |
| CXSimulator | CIKM 2024 | 17 | LLM embeddings for web-marketing campaign assessment |
| Shop-r1 | 2025 | 14 | RL-trained LLMs replicating human shopping behavior |
| Learning from Synthetic Labs | 2025 | 12 | LLMs with CoT agree with auction experimental literature |
| SimGym | 2026 | — | Traffic-grounded browser agents for offline A/B testing |
| LBM | 2026 | — | Hierarchical LLM for auto-bidding strategy |

## Technical Approaches

1. **LLM-as-User**: Persona-prompted LLM generates queries, clicks, purchases (Agent4Rec, BASES, Shop-r1)
2. **LLM-as-Advertiser**: Simulates bidding, budget allocation, creative decisions (InfoBid, LBM, Synthetic Labs)
3. **Generative Environment**: LLMs generate full marketplace dynamics (RecSim NG, LLM-Augmented Digital Twin)
4. **Hybrid**: LLM personas + classical simulation engines (CXSimulator, Lusifer)

## Applications

- **Offline policy evaluation**: YouTube Music (Google SIGIR 2024), Agent4Rec
- **A/B test acceleration**: SimGym, CXSimulator, Multi-Modal LLM A/B Testing
- **Adversarial testing**: TruthMarketTwin, Tacit Bidder Collusion, Amazon adversarial queries
- **RL training environments**: Lusifer, Shop-r1
- **Privacy-safe synthetic data**: BASES, GLIDE

## Key Gaps

1. Advertiser behavior simulation underdeveloped vs user simulation
2. Meta's internal systems remain opaque
3. LLMs converge toward "positive average person" (calibration challenge)
4. Scale: Agent4Rec uses 1,000 agents vs billions of real users
5. Auction/marketplace-level simulation just emerging (2025-2026)
