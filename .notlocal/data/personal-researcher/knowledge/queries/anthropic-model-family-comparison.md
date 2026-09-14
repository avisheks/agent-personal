---
title: "Compare Anthropic models: Mythos vs Opus vs Sonnet vs Haiku — innovations, size, cost, capabilities?"
summary: "5-tier hierarchy: Mythos 5 (restricted, 93.9% SWE-bench, autonomous vuln discovery, $10/$50) > Fable 5 (GA premium, multi-day autonomous, same base) > Opus 4.8 (adaptive thinking, $5/$25) > Sonnet 4.6 (hybrid reasoning, 70% efficient, $3/$15) > Haiku 4.5 (4-5x faster, $1/$5, 73% SWE-bench). Mythos IS real — Project Glasswing, ~150 orgs. All params undisclosed."
type: query
createdAt: 2026-06-10
topic: anthropic
---

# Anthropic Model Family Comparison

## Quick Answer

**5-tier hierarchy (most → least capable):** Mythos 5 > Fable 5 > Opus 4.8 > Sonnet 4.6 > Haiku 4.5

**Mythos IS real** — it's Anthropic's restricted frontier model for autonomous cybersecurity research (93.9% SWE-bench). Fable 5 is the same base model made generally available with safety guardrails. All parameter counts remain undisclosed.

## At a Glance

| Model | Released | Innovation | Cost (in/out $/MTok) | SWE-bench |
|-------|----------|-----------|:--------------------:|:---------:|
| **Mythos 5** | Jun 9, 2026 | Autonomous zero-day discovery | $10/$50 | 93.9% |
| **Fable 5** | Jun 9, 2026 | Multi-day autonomous work + sub-agents | $10/$50 | ~90%+ |
| **Opus 4.8** | May 28, 2026 | Adaptive thinking + self-correction | $5/$25 | ~83% |
| **Sonnet 4.6** | Feb 17, 2026 | Hybrid reasoning + 70% token efficiency | $3/$15 | 80.2% |
| **Haiku 4.5** | Oct 15, 2025 | Speed (4-5x) + near-frontier quality | $1/$5 | 73.3% |

## Key Innovations Each Unlocks

### Mythos 5 (Restricted)
- **Unlocks:** Autonomous vulnerability discovery without human steering
- Found >10,000 high/critical vulns; 27-year-old OpenBSD bug; 16-year-old FFmpeg bug
- Access: Project Glasswing only (~150 orgs)
- 94.6% GPQA Diamond, 83.1% CyberGym

### Fable 5 (GA Premium)
- **Unlocks:** Multi-day autonomous work sessions
- Plans across stages, delegates sub-agents, self-validates outputs
- "Senior research scientist grade" — Hex analytics first >90%
- Same base model as Mythos; cyber/bio queries routed to Opus 4.8

### Opus 4.8
- **Unlocks:** Adaptive thinking (auto-reasoning depth) + rigorous code review
- 4x less likely to let code flaws pass unremarked
- 61% cheaper than Opus 4.7; fast mode 2.5x speed available
- "The model for complex coding when quality matters"

### Sonnet 4.6
- **Unlocks:** Near-Opus quality at production cost + 1M context
- Hybrid reasoning (extended + adaptive thinking)
- 70% more token-efficient than predecessor
- Strong prompt injection resistance

### Haiku 4.5
- **Unlocks:** Speed for real-time + sub-agent orchestration
- 4-5x faster than Sonnet 4.5; matches Sonnet 4 quality at 1/3 cost
- Best cost-efficiency: $0.068 per SWE-bench percentage point per MTok

## Model Specifications

| Spec | Mythos/Fable 5 | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
|------|:--------------:|:--------:|:----------:|:---------:|
| Context (input) | 1M | 1M | 1M | 200K |
| Max output | 128K | 128K | 64K | 64K |
| Parameters | Undisclosed | Undisclosed | Undisclosed | Undisclosed |
| Reasoning | Adaptive (always on) | Adaptive | Extended + Adaptive | Extended |
| Vision | Yes | Yes (3.75MP) | Yes | Yes |
| Tool use | Yes | Yes (290 tok overhead) | Yes | Yes |

## When to Use Which

```
Need multi-day autonomous work?     → Fable 5
Need best reasoning + coding?       → Opus 4.8
Need production speed + quality?    → Sonnet 4.6
Need volume/speed/sub-agents?       → Haiku 4.5
Need security vulnerability research? → Mythos 5 (if approved)
Cost-optimized batch?               → Haiku 4.5 batch ($0.50/$2.50)
```

## Sources

- [[Anthropic Model Family — Mythos, Fable, Opus, Sonnet, Haiku]]
- docs.anthropic.com/en/docs/about-claude/models
- anthropic.com/news/project-glasswing
- anthropic.com/pricing
