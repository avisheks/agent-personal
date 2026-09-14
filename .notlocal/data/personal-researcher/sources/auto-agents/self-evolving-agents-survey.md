---
title: Self-Evolving Agents — Survey and Industry Analysis
url: https://arxiv.org/abs/2507.21046
ingestedAt: 2026-06-08
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2508.07407
  - https://arxiv.org/abs/2305.16291
  - https://arxiv.org/abs/2310.02304
  - https://arxiv.org/abs/2408.08435
  - https://arxiv.org/abs/2308.10144
  - https://arxiv.org/abs/2303.11366
  - https://arxiv.org/abs/2401.10020
  - https://arxiv.org/abs/2604.16968
  - https://arxiv.org/abs/2605.16233
  - https://arxiv.org/abs/2605.23019
  - https://arxiv.org/abs/2605.25430
  - https://arxiv.org/abs/2605.10663
  - https://arxiv.org/abs/2604.20133
  - https://arxiv.org/abs/2507.02004
---

# Self-Evolving Agents — Survey and Industry Analysis

## Definition

Self-evolving agents are AI systems that autonomously improve their capabilities through interaction and experience, without requiring explicit retraining. The 2025 survey by Gao et al. (TMLR) defines the field around: what to evolve (models, memory, tools, architecture), when to evolve (intra vs inter test-time), and how to evolve (scalar rewards, textual feedback, single/multi-agent).

## Spectrum of Self-Evolution

- **Weak (no weight updates)**: Prompt refinement, skill library growth, memory accumulation. Examples: Voyager, FORGE, Reflexion, PACE.
- **Medium (RL on scaffolding)**: Reinforcement learning optimizes experience extraction policies, base model frozen. Examples: CODESKILL, Evolving-RL.
- **Strong (weight updates)**: Parameter-level meta-learning. Examples: SOLAR, Self-Rewarding LMs.

## Key Mechanisms

1. Skill auto-creation: Generate executable code/procedures stored in libraries (Voyager, CODESKILL, EvoAgent)
2. Experience memory + retrieval: Textual episodic memory of successes/failures (ExpeL, FORGE, ExpGraph)
3. Self-critique loops: Verbal reflection on failures stored for future (Reflexion)
4. Reward-driven adaptation: Self-generated reward signals guide improvement (Self-Rewarding LMs, Eureka)
5. Meta-agent design: Agent programs new agents from archive of discoveries (ADAS)

## Industry Examples

- **Voyager** (NVIDIA/Jim Fan, 2023): Minecraft lifelong learning agent, 3.3x more items, 15.3x faster milestones. Skill library transfers to new worlds.
- **Self-Rewarding LMs** (Meta, ICML 2024): 3 iterations of Llama 2 70B outperforms Claude 2, Gemini Pro, GPT-4 0613.
- **EvoAgent** (2026): Production foreign trade, 28% improvement with GPT-5.2. Structured skills with evolutionary metadata.
- **STELLA** (2025): Biomedical research, ~26% on Humanity's Last Exam: Biomedicine. Dynamic Tool Ocean for auto-discovering bioinformatics tools.
- **Hermes Agent** (NousResearch): Commercial autonomous skill creation + refinement loop.

## Academic Examples

- **Voyager** (arXiv:2305.16291, NeurIPS 2023): Open-ended embodied lifelong learning
- **ADAS** (arXiv:2408.08435): Meta Agent Search that programs new agents; outperforms SOTA hand-designed agents
- **ExpeL** (arXiv:2308.10144, AAAI 2024): Experiential learning without parametric updates
- **Reflexion** (arXiv:2303.11366): 91% pass@1 on HumanEval via verbal reinforcement
- **STOP** (arXiv:2310.02304, COLM 2024): Recursively self-improving code generation scaffold
- **CODESKILL** (arXiv:2605.25430, 2026): RL-trained skill management policy, +9.69% over no-skill
- **FORGE** (arXiv:2605.16233, 2026): Population-based memory broadcast, 1.7-7.7x improvement
- **PACE** (arXiv:2605.23019, 2026): Two-timescale evolution for frozen SLMs
- **Evolving-RL** (arXiv:2605.10663, 2026): 98.7% relative improvement over GRPO baseline
- **SOLAR** (AAAI 2026): Parameter-level meta-learning treating weights as environment

## Safety Findings

From Zhao et al. (ACL 2026 Findings, arXiv:2604.16968):
- "Experience gathered solely from benign tasks can still compromise safety in high-risk scenarios"
- Root cause: execution-oriented accumulated experience reinforces tendency to act rather than refuse
- Fundamental safety-utility trade-off: adding refusal experience causes over-refusal
- Alignment must be continuously re-evaluated as agent evolves

## Dominant Design Pattern

Skill accumulation + retrieval: generate reusable artifacts → store with retrieval metadata → compose for future tasks. Used by Voyager through CODESKILL to EvoMaster.
