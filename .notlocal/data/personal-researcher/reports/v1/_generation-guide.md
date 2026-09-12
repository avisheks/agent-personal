# Report Generation Guide

How interview-prep reports are generated, updated, and maintained.

## Architecture

```
Knowledge Pages (8 per topic)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  /generate-report --topic <name>                        │
│                                                         │
│  Phase 1: Parallel Section Generation                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Section A   │  │ Section B   │  │ Section C   │    │
│  │ (us-west-2) │  │ (us-east-1) │  │ (us-west-2) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│        │                │                │              │
│        └────────────────┼────────────────┘              │
│                         ▼                               │
│  Phase 2: Merge Pass (coherent header + cross-refs)     │
│                         │                               │
│                         ▼                               │
│  Phase 3: Assemble + Write to reports/<topic>-ref.md    │
└─────────────────────────────────────────────────────────┘
```

## Execution Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `MAX_SECTION_TOKENS` | 16384 | Enough for full-depth Q&A (12 questions) and detailed architecture diagrams |
| `MAX_MERGE_TOKENS` | 4096 | Merge pass only produces header/navigation |
| `max_workers` | 2 | Avoids Bedrock throttling on a single region |
| Regions | us-west-2, us-east-1 | Round-robin to distribute load. Only US regions support `us.anthropic.*` cross-region inference profiles |
| Bedrock read timeout | 300s | Long-form generation (16K tokens) takes 60-120s per section |
| Retry | 3 attempts, exponential backoff (1s, 4s, 16s) | Handles transient throttling |

## Section Generation Strategy

### Standard sections (10 of 12)

Each section gets one parallel LLM call with:
- Full knowledge pages as context
- Section-specific template from `_template.md`
- Depth instructions in the user message
- Post-processing trim to prevent section bleed

### New sections for readability

- **Executive Summary**: concise TL;DR (8-12 lines) with decision bullets and killer framing
- **System Design Walkthrough (Summary)**: condensed version (3-5K chars) with ONE diagram and tables
- **Decision Matrix**: embedded in Design Flow Framework — quick reference for key trade-offs
- **Quick answers**: every Q&A question starts with `> **Quick answer:**` blockquote

### Appendix: Full System Design Walkthrough (special handling)

The appendix walkthrough is split into **8 sub-section calls** (Opening Frame + subsections 1-7), each running in parallel with:
- Full 16K token budget per subsection
- A **depth exemplar** from an existing report showing expected detail level
- Subsections assembled in order after generation

This ensures the appendix matches the depth of hand-written reports (~25K chars with detailed ASCII architecture diagrams, experience anecdotes, and design choice rationale per subsection).

The **main body summary** references the appendix, letting readers get the high-level architecture in 2 minutes and dive deep only when preparing for a specific question.

## Two Modes

### `/generate-report` — Full generation from scratch

Use when: creating a report for a new topic that has compiled knowledge pages but no existing report.

1. All 10 sections generated in parallel (round-robin across regions)
2. Walkthrough section uses sub-section parallelism with exemplar
3. Merge pass produces coherent header
4. Output: `reports/<topic>-ref.md`

### `/update-report` — Incremental update

Use when: refreshing an existing report after new knowledge is ingested/compiled (e.g., weekly cadence).

1. Existing report parsed into sections
2. Each section updated in parallel (one LLM call per section)
3. Update prompt preserves existing content, adds new information, removes contradictions
4. Original header preserved
5. Output overwrites existing `reports/<topic>-ref.md`

## Weekly Update Cadence

```
1. /ingest <new-sources> --topic <name>     # Add new material
2. /compile                                  # Recompile knowledge pages
3. /update-report --topic <name>            # Refresh report sections
```

Each section is updated independently (one LLM call) receiving:
- The existing section content (to preserve)
- All latest knowledge pages (to incorporate)

## Quality Targets

| Section | Target chars | Key quality signals |
|---------|-------------|---------------------|
| Executive Summary | 0.5-1K | 8-12 lines, TL;DR, key trade-off, decision bullets, killer framing |
| Design Flow Framework | 1-2K | 7-row table (concise cells) + decision matrix table |
| System Design Walkthrough (Summary) | 3-5K | ONE diagram, gaps/improvements table, scaling bullets, link to appendix |
| Interview Q&A Bank | 25-30K | 12 questions, each with `> **Quick answer:**` then full answer |
| DE Depth Probes | 20-25K | Cross-cutting architectural insight, math/code where relevant |
| Cost Model | 3-5K | Concrete numbers, per-task breakdown, optimization priority |
| Observability | 5-15K | JSON trace examples, dashboard metrics, debugging walkthroughs |
| Data Flywheel | 3-10K | Feedback signals, active learning, improvement cadence |
| Advanced Patterns | 5-10K | Table + interaction diagrams |
| Seniority Signals | 2-5K | Staff vs Principal reframe table |
| References | 3-5K | Numbered citations with URLs |
| Appendix: Full Walkthrough | 25-30K | Full depth, ASCII diagrams per subsection, experience anecdotes, risk framing |

## File Layout

```
data/researcher/reports/
├── _template.md              # Section structure + guidance comments
├── _generation-guide.md      # This file — execution documentation
├── agentic-systems-ref.md    # Generated/maintained reports
├── content-generation-ref.md
├── enterprise-rag-ref.md
├── evaluation-safety-ref.md
├── recommendation-ranking-ref.md
└── search-retrieval-ref.md
```

## Implementation

Source code: `agent_platform/domains/researcher/report_generator.py`

Key functions:
- `generate_report()` — full parallel generation + merge
- `update_report()` — incremental section-by-section update
- `_generate_one_section()` — single section generation with retry
- `_generate_walkthrough_subsections()` — sub-section parallelism for walkthrough
- `_build_llm_pool()` in signal_tools.py — creates multi-region provider pool
