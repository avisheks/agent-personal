# FAQ Report Generation Guide

## Purpose

FAQ reports distill complex technical topics into question-answer pairs that demonstrate **principal+ level thinking**. Each answer goes beyond textbook definitions to reveal production-scale insights, quantitative trade-offs, and system-level implications.

## What Makes a Principal+ Answer

A principal+ answer differs from lower seniority levels in these ways:

1. **Addresses "when NOT to use"** — not just what it is, but where it fails or is inappropriate
2. **Quantitative** — specific numbers (latency, memory, throughput) rather than "faster" or "more efficient"
3. **System-level thinking** — connects to adjacent concerns (cost, ops burden, failure modes)
4. **Production-aware** — mentions gotchas only visible at scale or in real deployments
5. **Trade-off-centered** — every technique has costs; a principal names them explicitly
6. **Non-obvious connections** — links to related mechanisms that a textbook explanation wouldn't mention

## What a Junior/Mid Would Say

- Correct definition from documentation or blog posts
- "It makes things faster/cheaper"
- No quantitative claims
- No failure modes or limitations
- No "when NOT to use"

## What a Senior Would Say

- Correct mechanism + basic trade-offs
- Some quantitative reasoning ("reduces latency by roughly X")
- Knows the primary limitation
- But may miss: system-level cost implications, interaction with other components, production failure modes, when the technique is counterproductive

## Format Rules

- Each FAQ: 150-300 word answer (concise, dense)
- Seniority table: 1-2 sentences per level (not full answers)
- Key signals: 2-3 bullets showing principal-differentiating insight
- No filler, no preambles ("Great question!"), no repetition
- Inline citations [N] for specific claims (benchmarks, paper results)
- Maximum 10 FAQs per report file

## Quality Gates

- [ ] Every answer includes at least ONE quantitative trade-off
- [ ] Every answer mentions at least ONE "when NOT to use" scenario
- [ ] Seniority table clearly shows progression (not just "knows more")
- [ ] Key signals are genuinely non-obvious (not restatements of the answer)
- [ ] Total file ≤ 400 lines
