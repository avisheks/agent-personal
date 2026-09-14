# Study Notes Generation Guide

## Purpose

Study notes distill a **literature survey or reading roadmap** into a structured, navigable reference. Unlike the standard v2/notes template (designed for system-design topics with cost models, observability, and DE probes), study notes focus on **evolutionary arcs, paper relationships, and cross-cutting themes**.

## When to Use This Template

Use `_study-notes-template.md` instead of `_template.md` when the source material is:

- A curated reading list or paper roadmap
- A literature survey or meta-analysis
- A historical evolution of a research area
- A "landscape" overview spanning many techniques or systems

**Do NOT use** for:
- System-design topics (use standard template — needs Cost Model, Observability, DE Probes)
- FAQ/interview prep (use `v2/faqs/` template)
- Single-paper deep dives (use knowledge pages in `knowledge/{topic}/`)

## Format Selection Decision

```
Is the content primarily a literature survey / reading list / historical evolution?
  ├── YES → Use _study-notes-template.md
  └── NO
       ├── Is it a single system or technique to design/operate?
       │     └── YES → Use _template.md (standard v2/notes)
       └── Is it a set of discrete questions with seniority contrast?
             └── YES → Use v2/faqs/_template.md
```

## Section Budgets

| Section | Max Lines | Notes |
|---------|-----------|-------|
| Quick Catchup | 5 | Same as standard template |
| State of the Art | 25 | Same as standard template |
| Executive Summary | 15 | Includes 1 visual aid (taxonomy/spectrum, not architecture diagram) |
| Evolutionary Stages | 300 | Core section — 8-15 stages, each with table + transition sentence |
| Key Themes & Connections | 100 | 3-5 cross-cutting themes with tables/diagrams |
| Reading Schedule | 40 | Weekly plan with progressive questions |
| References | 100 | Grouped by sub-area, verified, annotated |
| Practitioner Appendix | 30 | Optional — informal heuristics from talks/blogs/industry posts with source links |
| **Total** | **~630** | Hard cap: 800 lines |

## Key Differences from Standard Template

| Standard Template Section | Study Notes Equivalent | Why |
|--------------------------|----------------------|-----|
| Design Flow Framework | *Dropped* | No system to design — this is a survey |
| System Design Walkthrough | *Dropped* | Same reason |
| Interview Q&A Bank | *Dropped* | Use faqs/ template if needed separately |
| DE Depth Probes | *Dropped* | Depth is in the themes and reading schedule |
| Cost Model | *Dropped* | No production system to cost |
| Observability | *Dropped* | No production system to monitor |
| Data Flywheel | *Dropped* | No feedback loop to engineer |
| Advanced Patterns | *Dropped* | Patterns emerge in themes section |
| Seniority Signals | *Dropped* | Not interview-oriented |
| *New:* Evolutionary Stages | — | Core contribution: structured chronological arc |
| *New:* Key Themes | — | Cross-cutting insights that span the whole survey |
| *New:* Reading Schedule | — | Actionable study plan with progressive questions |

## Quality Gates

### Hard Gates (any failure = reject)

- [ ] Total lines ≤ 800
- [ ] Evolutionary Stages section has ≥ 5 stages with distinct capability transitions
- [ ] Each stage has a "Key transition" sentence that names the NEW mechanism introduced
- [ ] All references verified (same rules as standard template)
- [ ] ≥ 15 inline citations spread across State of the Art and Evolutionary Stages
- [ ] Reading Schedule questions build progressively (not random)

### Soft Gates (flag for review)

- [ ] Quick Catchup present and ≤ 5 lines
- [ ] State of the Art has ≥ 3 dated breakthroughs
- [ ] Executive Summary has ONE visual aid
- [ ] Key Themes section has ≥ 3 themes, each with a supporting table or diagram
- [ ] References grouped by sub-area (not one flat list)

## Generation Tips

1. **Start with the arc, not the papers.** Identify the evolutionary stages first, then slot papers into them. A paper that spans two stages goes in the stage where its PRIMARY contribution lands.

2. **Key transition sentences are the highest-value content.** A reader who only reads these sentences should understand the full evolutionary arc. Write them like a news headline: what changed and why it matters.

3. **Themes emerge from stages.** After writing all stages, look for patterns that recur: verification approaches, expanding surfaces, failure modes, convergence patterns. These become your themes.

4. **The Reading Schedule is not just a list.** Each week's "Central Question" should logically follow from the prior week. A reader following the schedule should build cumulative understanding.

5. **Executive Summary visual aid** should be a taxonomy, spectrum, or routing table — something that shows relationships between the stages/approaches. Not an architecture diagram (there's no single system being designed).

6. **Don't duplicate the seed.** If the seed is a reading list, the study notes add value by: structuring into stages with transitions, extracting cross-cutting themes, providing a progressive reading plan, and writing a state-of-the-art summary. If your output is just the seed reformatted, you've failed.