# V2 Report Generation Guide

## Key Changes from V1

| Change | V1 Behavior | V2 Requirement | Rationale |
|--------|-------------|----------------|-----------|
| Length cap | No limit (813–3,534 lines) | ≤1,200 lines total | Short-form reports scored 85%+ vs 61-68% for long-form |
| DE Probe diversity | Generated independently → duplicates | 6 probes across 6 DIFFERENT skill categories | 10/15 v1 reports had 3–6 duplicate probes (generation bug) |
| Inline citations | 1/15 reports had them | Mandatory `[N]` for all factual claims, ≥15 per report | Readers cannot trace claims to sources |
| Reference verification | Many hallucinated | All URLs must resolve; arXiv IDs must exist | claude-code.md cited non-existent 2025–2026 papers |
| State of the Art section | Did not exist | Required (15–25 lines, updated quarterly) | Biggest content gap — 0% of v1 reports had this |
| Quick Catchup box | Did not exist | Required (3–5 lines at top) | Enables 10-second orientation for busy readers |
| Appendix | Repeated main body (50–70% overlap) | ELIMINATED entirely | Redundant content inflated reports by ~900 lines |
| Experience callouts | Formulaic, every section | Max 4 per report, only when domain-relevant | "Amazon Ads 300M+ MAU" appeared 8-12x per report |
| Q&A format | Two incompatible formats | Unified: Quick answer + full answer (≤250w) + Hard follow-up | Consistency across all reports |
| Sub-Q&A banks | Embedded in Cost/Observability sections | PROHIBITED — one Q&A section only | Created confusion and duplicated main Q&A content |
| Verbose prose in framework | Steps 1-7 as multi-paragraph prose | Table-only format, 1-2 sentences per cell | Framework section was 500+ lines in some reports |

## Section Budgets

| Section | Max Lines | Max Chars |
|---------|-----------|-----------|
| Quick Catchup | 5 | 400 |
| State of the Art | 25 | 2,000 |
| Executive Summary | 15 | 1,200 |
| Design Flow Framework | 30 | 2,400 |
| System Design Walkthrough | 60 | 4,800 |
| Interview Q&A Bank (12 Qs) | 500 | 40,000 |
| DE Probes (6 probes) | 250 | 20,000 |
| Cost Model | 60 | 4,800 |
| Observability | 80 | 6,400 |
| Data Flywheel | 60 | 4,800 |
| Advanced Patterns | 40 | 3,200 |
| Seniority Signals | 30 | 2,400 |
| References | 50 | 4,000 |
| **Total** | **~1,205** | **~96,400** |

## Generation Pipeline Changes

### DE Probe Diversity Enforcement

Before generating probes, the pipeline MUST:

1. Generate a list of 6 distinct sub-topics for the report's domain
2. Verify no two sub-topics share >30% semantic overlap (use embedding similarity)
3. Pass each sub-topic as a separate generation call WITH the other 5 topics as exclusion context
4. Post-generation: run pairwise similarity check; regenerate any probe with >40% overlap

Example exclusion prompt:
```
Generate DE Probe 3 on "{sub_topic_3}".
DO NOT cover: {sub_topic_1}, {sub_topic_2} (already covered).
DO NOT repeat: {list of formulas/concepts from probes 1-2}.
```

### Reference Verification

After generation, before finalizing:

1. For each reference with an arXiv ID: verify via `https://arxiv.org/abs/{id}` returns 200
2. For each reference with a URL: verify the URL resolves (non-404)
3. For each reference with a DOI: verify via `https://doi.org/{doi}`
4. Remove any reference that fails verification
5. Flag any inline citation `[N]` whose reference was removed — regenerate that claim with a valid source or remove the claim

### Inline Citation Rules

- Every factual claim (number, benchmark result, paper finding, system behavior attributed to a specific source) MUST have `[N]`
- Opinion, general knowledge, and architectural recommendations do NOT need citations
- Target: 15–30 inline citations per report
- Each reference should be cited at least once; remove uncited references

### Experience Callout Rules

- Only include `[!experience]` callouts when the domain genuinely connects to the anecdote
- Each callout must contain a SPECIFIC, verifiable claim (not "At Amazon Ads, we scaled this")
- Maximum 4 experience callouts per report
- Callouts must add insight not available from the technical content alone

## Quality Gates

A v2 report passes quality review when ALL of the following are true:

### Hard Gates (any failure = reject)
- [ ] Total lines ≤ 1,200
- [ ] All 6 DE Probes address distinct sub-topics (no two share a loss function or formula)
- [ ] All references resolve (automated URL check — no fabricated papers)
- [ ] ≥15 inline citations `[N]` present across Q&A and DE Probes
- [ ] No embedded sub-Q&A banks in Cost/Observability/Flywheel sections
- [ ] No individual Q&A answer exceeds 250 words

### Soft Gates (failure = flag for review, not auto-reject)
- [ ] Quick Catchup box present and ≤5 lines with dated content
- [ ] State of the Art section present with ≥3 dated breakthroughs
- [ ] Executive Summary present with ONE visual aid
- [ ] Every Q&A has a "Quick answer" blockquote
- [ ] ≤4 experience callouts total, each ≤2 sentences
- [ ] Design Flow Framework uses table format (not prose paragraphs)

### Target Score (LLM-as-Judge)
- [ ] Consensus score ≥ 64/75 (85%, grade A-) to ship
- [ ] No single dimension below 60% (≥15/25 per judge)
- [ ] DE Probe Diversity score ≥ 4/5 (never 1)

## Iterative Improvement Loop

If a generated report scores below A- (64/75):
1. Identify the lowest-scoring criteria across all 3 judges
2. Regenerate ONLY the failing sections (not the entire report)
3. Re-run judge evaluation on the updated report
4. Repeat until A- threshold is met (max 3 iterations)
5. If still failing after 3 iterations, escalate for manual review
