---
title: "Anthropic Model Family Comparison — Mythos, Fable, Opus, Sonnet, Haiku"
url: https://docs.anthropic.com/en/docs/about-claude/models
ingestedAt: 2026-06-10
type: article
additional_sources:
  - https://www.anthropic.com/news/project-glasswing
  - https://www.anthropic.com/news/claude-fable-5
  - https://www.anthropic.com/news/claude-opus-4-8
  - https://www.anthropic.com/pricing
---

# Anthropic Model Family (June 2026)

## Hierarchy: Mythos > Fable > Opus > Sonnet > Haiku

### Claude Mythos 5 (Restricted)
- Released: June 9, 2026
- Access: Invitation-only via Project Glasswing (~150 orgs, 15+ countries)
- Purpose: Autonomous cybersecurity vulnerability discovery + biology research
- Key: 93.9% SWE-bench Verified, 94.6% GPQA Diamond, 83.1% CyberGym
- Found >10,000 high/critical vulns including 27-year-old OpenBSD bug
- Pricing: $10/$50 (GA), $25/$125 (Preview/research)
- Context: 1M input, 128K output

### Claude Fable 5 (GA, Premium)
- Released: June 9, 2026
- Same base model as Mythos, with safety routing (cyber/bio queries → Opus 4.8)
- Multi-day autonomous work sessions; self-validation; sub-agent delegation
- "Adaptive thinking" always on (no extended thinking toggle)
- Pricing: $10/$50 per MTok
- Context: 1M input, 128K output
- Partner benchmarks: SOTA on CursorBench, FrontierBench, Finance, Analytics (first >90%)

### Claude Opus 4.8
- Released: May 28, 2026
- Adaptive thinking (auto-adjusts reasoning depth)
- 4x less likely to let code flaws pass unremarked
- 61% cheaper than Opus 4.7
- Fast mode: 2.5x speed at $10/$50
- Pricing: $5/$25 per MTok
- Context: 1M input, 128K output
- Knowledge cutoff: Jan 2026

### Claude Sonnet 4.6
- Released: Feb 17, 2026
- Hybrid reasoning (extended + adaptive thinking)
- 70% more token-efficient than Sonnet 4.5
- 1M context window, 64K output
- Major computer use improvements
- Strong prompt injection resistance
- Pricing: $3/$15 per MTok
- 80.2% SWE-bench (with prompt mod)

### Claude Haiku 4.5
- Released: Oct 15, 2025
- Matches Sonnet 4 performance at 1/3 cost and 2x speed
- 73.3% SWE-bench, 4-5x faster than Sonnet 4.5
- Excellent for sub-agent orchestration
- Pricing: $1/$5 per MTok
- Context: 200K input, 64K output

## Pricing Summary (per MTok)

| Model | Input | Output | Batch Input | Batch Output |
|-------|-------|--------|-------------|-------------|
| Mythos/Fable 5 | $10 | $50 | $5 | $25 |
| Opus 4.8 | $5 | $25 | $2.50 | $12.50 |
| Sonnet 4.6 | $3 | $15 | $1.50 | $7.50 |
| Haiku 4.5 | $1 | $5 | $0.50 | $2.50 |

## Benchmark Comparison

| Benchmark | Mythos 5 | Opus 4.6 | Sonnet 4.6 | Haiku 4.5 |
|-----------|:--------:|:--------:|:----------:|:---------:|
| SWE-bench Verified | 93.9% | 81.4% | 80.2% | 73.3% |
| GPQA Diamond | 94.6% | 91.3% | — | — |
| Humanity's Last Exam (tools) | 64.7% | 53.0% | — | — |
| CyberGym | 83.1% | 66.6% | — | — |
| Terminal-Bench 2.0 | 82.0% | 65.4% | — | — |

## Key Innovations by Model

| Model | Innovation | What It Unlocks |
|-------|-----------|-----------------|
| Mythos 5 | Autonomous zero-day discovery | Finds vulns in every major OS/browser without human steering |
| Fable 5 | Multi-day autonomous sessions | Plans across stages, delegates sub-agents, self-validates |
| Opus 4.8 | Adaptive thinking + self-correction | Auto-adjusts reasoning; 4x fewer code flaws missed |
| Sonnet 4.6 | Hybrid reasoning + token efficiency | Near-Opus at 60% cost; 70% more efficient |
| Haiku 4.5 | Speed at near-frontier quality | Matches Sonnet 4 at 1/3 cost, 4-5x faster |
