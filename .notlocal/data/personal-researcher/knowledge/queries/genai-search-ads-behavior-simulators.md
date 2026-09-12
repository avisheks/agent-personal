---
title: "What are latest innovations from top companies for leveraging gen-AI/LLM to build shopper/advertiser behavior simulators in online search and ads?"
summary: "Google leads (RecSim NG + YouTube Music for offline testing, SIGIR 2024). Amazon uses LLM synthetic queries for cold-start. Microsoft's BASES simulates web search at scale. ByteDance builds four-twin digital twins for platform policy evaluation. Meta has no public papers. Key papers: Agent4Rec (1K agents, 349 citations), Shop-r1 (RL-aligned shopping). Main gap: advertiser-side simulation is underdeveloped vs user simulation."
type: query
createdAt: 2026-06-08
topic: genai-search-ads
---

# LLM-Based Shopper/Advertiser Behavior Simulators — Company Innovations

## Quick Answer

LLM-based behavior simulation uses persona-prompted language models to generate realistic user/advertiser interaction sequences for **offline A/B testing, policy evaluation, and adversarial testing** — replacing expensive live experiments.

**Google** is furthest ahead (RecSim NG deployed on YouTube Music, SIGIR 2024). **ByteDance** has the most ambitious architecture (four-twin digital twin). **Amazon** focuses on synthetic query generation for cold-start. **Microsoft** does large-scale web search simulation (BASES). **Meta** has no public papers on this despite likely internal work.

## By Company

### Google (Leader)
- **RecSim NG + YouTube Music** (SIGIR 2024): Production deployment — "Minimizing Live Experiments in Recommender Systems" using counterfactual user models
- **Controllable User Simulation** (DeepMind, 2026): Formalizes simulation as causal inference
- **Generative Agents** (Stanford/Google, 2023): Foundation paper proving LLMs can simulate believable behavior

### Amazon
- **Synthetic Query Generation** (WWW 2024): 8 LLM-generated queries per product for cold-start
- **MiniELM User Simulation** (ACL 2025): RL-based user sim for query rewriting training
- **Adversarial Query Generation** (ACL 2025): GAN-like robustness testing on ESCI dataset

### Microsoft
- **BASES** (EMNLP 2024): Novel framework generating diverse user profiles → diverse search behaviors at scale (bilingual Chinese/English)
- **LLM User Simulator for News Rec** (SIGIR 2025): Eliminates need for real user data

### ByteDance/TikTok
- **LLM-Augmented Digital Twin** (Mar 2026): Four-twin architecture (User, Content, Interaction, Platform) for counterfactual policy evaluation in short-video
- **PersonaAct** (2026): Personalized agents for filter bubble auditing

### Meta
- No published behavior simulation systems (likely proprietary)
- RL-enhanced ad text generation tested via live A/B tests (2025)

### OpenAI
- Indirect: models power most third-party research; Operator demonstrates intent modeling
- No published simulation-specific work

## Top Academic Systems

| System | Venue/Year | What It Does |
|--------|-----------|-------------|
| **Agent4Rec** | SIGIR 2024, 349 cites | 1,000 LLM agents simulate real human behavior |
| **RecAgent** | ACM 2025, 258 cites | LLM agent framework + sandbox environment |
| **EconAgent** | ACL 2024, 244 cites | LLM agents for macroeconomic/market simulation |
| **Shop-r1** | 2025 | RL-trained LLMs replicate human shopping behavior |
| **SimGym** | 2026 | Traffic-grounded browser agents for offline A/B testing |
| **CXSimulator** | CIKM 2024 | Web-marketing campaign assessment without live tests |
| **Learning from Synthetic Labs** | 2025 | LLMs with CoT replicate risk-averse auction bidding |
| **LBM** | 2026 | Hierarchical LLM for auto-bidding strategy |

## Four Simulation Approaches

1. **LLM-as-User**: Persona → generate queries, clicks, purchases (most developed)
2. **LLM-as-Advertiser**: Simulate bidding, budgets, creative strategies (emerging)
3. **Generative Environment**: LLMs model entire marketplace dynamics (ambitious)
4. **Hybrid**: LLM personas + classical simulation engines (practical)

## Key Gaps

1. **Advertiser simulation underdeveloped** — most work focuses on demand side (users)
2. **Calibration**: LLMs converge toward "positive average person" (SYN-DIGITS shows 50% improvement with correction)
3. **Scale**: Agent4Rec = 1K agents vs billions of real users
4. **Meta opacity**: Likely has advanced systems but nothing published
5. **Full marketplace simulation** (supply + demand + platform) just beginning (2026)

## Sources

- [[LLM-Based Behavior Simulators for Ads & Search]] (knowledge page)
- [[Gen-AI Applied to Search and Advertising (2024-2026)]]
- Google SIGIR 2024: Hsu, Mladenov et al. "Minimizing Live Experiments"
- Agent4Rec (SIGIR 2024), RecAgent (ACM 2025), BASES (EMNLP 2024)
- Shop-r1 (arXiv 2025), SimGym (2026), LLM-Augmented Digital Twin (2026)
