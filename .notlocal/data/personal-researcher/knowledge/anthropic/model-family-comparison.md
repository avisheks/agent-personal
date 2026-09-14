---
title: "Anthropic Model Family — Mythos, Fable, Opus, Sonnet, Haiku"
summary: "5-tier hierarchy: Mythos (restricted, 93.9% SWE-bench, autonomous vuln discovery) > Fable (GA premium, multi-day autonomous, same base as Mythos) > Opus 4.8 (adaptive thinking, $5/$25) > Sonnet 4.6 (hybrid reasoning, 70% efficient, $3/$15) > Haiku 4.5 (4-5x faster, $1/$5). Mythos IS real — released June 9, 2026 via Project Glasswing."
sources:
  - sources/anthropic/anthropic-model-family-comparison.md
createdAt: 2026-06-10
updatedAt: 2026-06-10
---

# Anthropic Model Family Comparison

## The Hierarchy (June 2026)

```
Mythos 5 (restricted) > Fable 5 (GA premium) > Opus 4.8 > Sonnet 4.6 > Haiku 4.5
```

## Quick Comparison

| Model | Released | Best For | Input/Output Cost | SWE-bench | Context |
|-------|----------|----------|:-----------------:|:---------:|:-------:|
| **Mythos 5** | Jun 9, 2026 | Autonomous security research | $10/$50 | 93.9% | 1M/128K |
| **Fable 5** | Jun 9, 2026 | Multi-day autonomous work | $10/$50 | ~90%+ | 1M/128K |
| **Opus 4.8** | May 28, 2026 | Complex reasoning + coding | $5/$25 | ~83% | 1M/128K |
| **Sonnet 4.6** | Feb 17, 2026 | Production workhorse | $3/$15 | 80.2% | 1M/64K |
| **Haiku 4.5** | Oct 15, 2025 | Speed + volume + sub-agents | $1/$5 | 73.3% | 200K/64K |

## Key Innovations Per Model

### Mythos 5 — Autonomous Vulnerability Discovery
- Finds zero-days in every major OS/browser without human steering
- >10,000 high/critical vulns found including 27-year-old OpenBSD bug, 16-year-old FFmpeg bug
- 93.9% SWE-bench, 94.6% GPQA Diamond, 83.1% CyberGym
- Restricted access via Project Glasswing (~150 orgs, 15+ countries)
- Same base model as Fable 5

### Fable 5 — Multi-Day Autonomous Sessions
- Works autonomously for DAYS: plans across stages, delegates to sub-agents, self-validates
- Adaptive thinking always on (no toggle)
- Safety routing: cyber/bio queries redirected to Opus 4.8
- SOTA on: CursorBench, FrontierBench (Cognition), Finance (Hebbia), Analytics (Hex, first >90%)
- Same pricing as Mythos ($10/$50)

### Opus 4.8 — Adaptive Thinking + Self-Correction
- Adaptive thinking: auto-adjusts reasoning depth per query (no manual configuration)
- 4x less likely to let code flaws pass unremarked
- 61% cheaper token cost vs Opus 4.7
- Fast mode: 2.5x speed at $10/$50 (same pricing as Fable)
- Lowest tool-use system prompt overhead (290 tokens vs 675 for Opus 4.7)

### Sonnet 4.6 — Hybrid Reasoning at Production Cost
- Hybrid reasoning: supports BOTH extended thinking AND adaptive thinking
- 70% more token-efficient than Sonnet 4.5 (same quality, fewer tokens)
- 1M context window
- Major computer use improvements
- Strong prompt injection resistance
- Near-Opus quality at 60% of Opus cost

### Haiku 4.5 — Speed Without Compromise
- Matches Sonnet 4 performance at 1/3 the cost and 2x the speed
- 4-5x faster than Sonnet 4.5
- 73.3% SWE-bench Verified
- Excellent for sub-agent orchestration (fast, cheap, capable)
- Extended thinking supported

## Reasoning Modes

| Mode | Models | How It Works |
|------|--------|-------------|
| **Extended thinking** | Sonnet 4.6, Haiku 4.5, Opus 4.6, Sonnet 4.5 | Explicit CoT; user configures budget; tokens visible |
| **Adaptive thinking** | Opus 4.8, Opus 4.7, Sonnet 4.6, Fable 5, Mythos 5 | Auto-adjusts depth per query; always on for Fable/Mythos |

## When to Use Which

| Scenario | Model | Rationale |
|----------|-------|-----------|
| Multi-day autonomous projects | Fable 5 | Self-validates, delegates, sustains days-long sessions |
| Complex reasoning / agentic coding | Opus 4.8 | Best Opus; adaptive thinking; strong self-correction |
| Production workloads / real-time | Sonnet 4.6 | Near-Opus quality at 60% cost; fast; 1M context |
| High-volume / sub-agents / latency | Haiku 4.5 | 4-5x faster; 1/3 cost; still 73% SWE-bench |
| Security vulnerability research | Mythos 5 | 93.9% SWE-bench; autonomous zero-day discovery |
| Bulk batch (cost-optimized) | Haiku 4.5 batch | $0.50/$2.50 per MTok |

## Cost-Efficiency Analysis

| Model | Output $/MTok | SWE-bench % | $ per SWE-bench point per MTok |
|-------|:-------------:|:-----------:|:------------------------------:|
| Haiku 4.5 | $5 | 73.3% | **$0.068** (most efficient) |
| Sonnet 4.6 | $15 | 80.2% | $0.187 |
| Opus 4.8 | $25 | ~83% | $0.301 |
| Fable 5 | $50 | ~90%+ | $0.556 (highest absolute quality) |

## Project Glasswing (Mythos Context)

- **What:** Consortium of 12+ major tech/security companies (AWS, Apple, Cisco, CrowdStrike, Google, JPMorgan, Microsoft, NVIDIA, Palo Alto Networks)
- **Purpose:** Use Mythos for defensive cybersecurity at scale
- **Scale:** ~150 organizations in 15+ countries by June 2026
- **Results:** >10,000 high/critical vulnerabilities found
- **Access:** Invitation-only; mandatory 30-day data retention
- **Significance:** First restricted model tier from a frontier lab — capability withheld from general public for safety

## Related

- [[Claude Code CLI Tool]]
- [[Claude Opus 4.7]]
- [[SWE-bench Verified]]
