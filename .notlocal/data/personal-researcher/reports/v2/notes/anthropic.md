# Anthropic Model Family: Mythos, Fable, Opus, Sonnet, Haiku

> **Last Updated:** 2026-06-10 | **Read time:** ~12 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#Model Hierarchy]] | [[#Innovations]] | [[#Specifications]] | [[#Benchmarks]] | [[#Pricing]] | [[#Decision Framework]] | [[#References]]

---



## References

- [1] Anthropic (2026) — Claude Models Documentation — docs.anthropic.com/en/docs/about-claude/models
- [2] Anthropic (2026) — Project Glasswing — anthropic.com/news/project-glasswing
- [3] Anthropic (2026) — Claude Fable 5 Announcement — anthropic.com/news/claude-fable-5
- [4] Anthropic (2026) — Claude Opus 4.8 — anthropic.com/news/claude-opus-4-8
- [5] Anthropic (2026) — Pricing — anthropic.com/pricing

---



## Quick Catchup

> **Quick Catchup (June 2026):** Anthropic's model family expanded to 5 tiers with the June 9 launch of Fable 5 and Mythos 5. Mythos is the first restricted-access frontier model from a major lab — scores 93.9% SWE-bench and autonomously discovers zero-day vulnerabilities (>10,000 found). Fable 5 (same base, GA) works autonomously for DAYS. Opus 4.8 introduced adaptive thinking (auto-adjusts reasoning depth). The hierarchy: Mythos > Fable > Opus > Sonnet > Haiku.
> Key shift: "adaptive thinking" (always-on reasoning that auto-scales) replaces manual "extended thinking" configuration in newest models.

---



## Model Hierarchy

```
RESTRICTED    Mythos 5  ─── 93.9% SWE-bench, autonomous vuln discovery
              │              Access: Project Glasswing only (~150 orgs)
GA PREMIUM    Fable 5   ─── Same base model, safety-routed
              │              Multi-day autonomous sessions
GA HIGH-END   Opus 4.8  ─── Adaptive thinking, self-correction
              │              Best for complex reasoning + coding
GA WORKHORSE  Sonnet 4.6 ── Hybrid reasoning, 70% token-efficient
              │              Near-Opus at 60% cost
GA FAST       Haiku 4.5  ── 4-5x faster than Sonnet 4.5, matches Sonnet 4
                             Best cost-efficiency, sub-agents
```


## Innovations By Model

| Model | Key Innovation | What It Unlocks |
|-------|---------------|-----------------|
| **Mythos 5** | Autonomous zero-day discovery | Finds vulns in every major OS/browser without human steering; 27-year-old OpenBSD bug |
| **Fable 5** | Multi-day autonomous work | Plans across stages, delegates sub-agents, self-validates; "senior research scientist grade" |
| **Opus 4.8** | Adaptive thinking + code rigor | Auto-adjusts reasoning depth; 4x fewer code flaws missed; 61% cheaper than 4.7 |
| **Sonnet 4.6** | Hybrid reasoning + efficiency | Both extended AND adaptive thinking; 70% more token-efficient; strong prompt injection resistance |
| **Haiku 4.5** | Speed without quality sacrifice | 4-5x faster than Sonnet 4.5; matches Sonnet 4 quality at 1/3 cost |

### Reasoning Modes

| Mode | How It Works | Models |
|------|-------------|--------|
| **Extended thinking** | Explicit CoT; user sets budget; tokens visible | Sonnet 4.6, Haiku 4.5, Opus 4.6, Sonnet 4.5 |
| **Adaptive thinking** | Auto-adjusts depth per query; always on for Fable/Mythos | Opus 4.8, Opus 4.7, Sonnet 4.6, Fable 5, Mythos 5 |


## Specifications

| Spec | Mythos/Fable 5 | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
|------|:--------------:|:--------:|:----------:|:---------:|
| Context (input) | 1M tokens | 1M tokens | 1M tokens | 200K tokens |
| Max output | 128K tokens | 128K tokens | 64K tokens | 64K tokens |
| Parameters | Undisclosed | Undisclosed | Undisclosed | Undisclosed |
| Knowledge cutoff | Not stated | Jan 2026 | Aug 2025 | Feb 2025 |
| Vision | Yes | Yes (3.75MP) | Yes | Yes |
| Tool use overhead | Low | 290 tokens | Standard | Standard |
| Tokenizer | New (30-35% more tokens) | New | Standard | Standard |

---



## Benchmarks

| Benchmark | Mythos 5 | Opus 4.8 | Sonnet 4.6 | Haiku 4.5 |
|-----------|:--------:|:--------:|:----------:|:---------:|
| **SWE-bench Verified** | **93.9%** | ~83% | 80.2% | 73.3% |
| **GPQA Diamond** | **94.6%** | — | — | — |
| **Humanity's Last Exam (tools)** | **64.7%** | — | — | — |
| **CyberGym** | **83.1%** | — | — | — |
| **Terminal-Bench 2.0** | **82.0%** | — | — | — |
| **SWE-bench Pro** | **77.8%** | — | — | — |
| **OSWorld-Verified** | **79.6%** | — | — | — |
| **BrowseComp** | **86.9%** | — | — | — |
| **ARC-AGI-2 (high effort)** | — | — | 60.4% | — |

Fable 5 partner benchmarks: SOTA on CursorBench, FrontierBench, Finance (Hebbia), Analytics (Hex, first >90%), AutomationBench (Zapier), ViBench (Replit).


## Pricing (per Million Tokens, June 2026)

| Model | Input | Output | Batch Input | Batch Output | Cache Write | Cache Read |
|-------|:-----:|:------:|:-----------:|:------------:|:-----------:|:----------:|
| **Mythos/Fable 5** | $10 | $50 | — | — | — | — |
| **Opus 4.8** | $5 | $25 | — | — | — | — |
| **Opus 4.8 Fast** | $10 | $50 | — | — | — | — |
| **Sonnet 4.6** | $3 | $15 | — | — | — | — |
| **Haiku 4.5** | $1 | $5 | $0.50 | $2.50 | — | — |

**Relative cost (output):** Fable = 10x Haiku. Opus = 5x Haiku. Sonnet = 3x Haiku.


## Decision Framework

| Scenario | Model | Rationale |
|----------|-------|-----------|
| Multi-day autonomous projects | **Fable 5** | Self-validates, delegates, sustains days-long sessions |
| Security vulnerability research | **Mythos 5** | 93.9% SWE-bench, autonomous zero-day discovery |
| Complex reasoning / daily coding | **Opus 4.8** | Strong adaptive thinking; excellent self-correction |
| Production workloads / real-time | **Sonnet 4.6** | Near-Opus quality at 60% cost; fast; 1M context |
| High-volume / sub-agents / latency | **Haiku 4.5** | 4-5x faster than Sonnet 4.5; 1/3 cost; still 73.3% SWE-bench |
| Cost-optimized batch processing | **Haiku 4.5 batch** | $0.50/$2.50 — cheapest per token |
| Maximum capability (general) | **Mythos 5** | Highest SWE-bench score across all benchmarks |

### Cost-Efficiency ($ per SWE-bench percentage point per MTok output)

| Model | Efficiency |
|-------|:----------:|
| Haiku 4.5 | **$0.068** (best) |
| Sonnet 4.6 | $0.187 |
| Opus 4.8 | $0.301 |
| Fable 5 | $0.556 (highest quality) |

---


## Project Glasswing (Mythos Context)

- **What:** Consortium for AI-powered defensive cybersecurity
- **Partners:** AWS, Apple, Cisco, CrowdStrike, Google, JPMorgan, Microsoft, NVIDIA, Palo Alto Networks
- **Scale:** ~150 organizations in 15+ countries (as of June 2026)
- **Results:** >10,000 high/critical vulnerabilities found
- **Significance:** First restricted-access model tier from a frontier lab — capability withheld for safety while deployed through vetted partners


## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-09 | Initial v2 generation | [UNVERIFIED] Full model family comparison: Mythos/Fable/Opus/Sonnet/Haiku. Hierarchy, innovations, specifications, benchmarks (Mythos 93.9% SWE-bench), pricing, decision framework, Project Glasswing. Run /verify-report --topic anthropic. |

---

## Verification

| Metric | Value |
|--------|-------|
| Verification score | 81% |
| Verification model | GPT-OSS-120b (Bedrock) |
| Total claims | 131 |
| Correct | 83 |
| Corrected | 19 |
| Unverifiable | 29 |
| Verified at | 2026-06-10 14:06 UTC |
| Sections corrected | Innovations By Model, Model Hierarchy, Benchmarks, Pricing (per Million Tokens, June 2026), Project Glasswing (Mythos Context), Changelog, Decision Framework |
