# Writing Style Guide

Reusable across sessions. Copy the quick-bootstrap block (end of doc) into any new prompt, or cite rules by number.

---

## 1. Tone

- **Decisions with justifications, not approvals.** State choices and invite feedback on specific dimensions. Never use "seeking alignment / sign-off / approval" framings.
- **Confidence over hedging.** Cut "targeted," "roughly," "may need to" when the fact is settled. Keep hedges only where uncertainty is real.
- **No aspirational filler.** Say what changed, then stop. Drop closers like "delivers a robust foundation for future work."
- **Positive framing over negative contrast.** State what the design achieves, not what it avoids. "One physical feed with training-shaped projections, reducing maintenance overhead (versus four parallel pipelines)" rather than "One physical feed, not four parallel pipelines to maintain."
- **Name the feedback dimension.** When soliciting review, specify what you want feedback on rather than asking a generic "thoughts?"

## 2. Structure

- **One point per section.** If two sections make the same claim, one is redundant. Cut or absorb.
- **State design commitments once.** Requirements, integrations, gates: state in the section that owns them. Later sections point back with "see §X."
- **Signpost between sections.** One-sentence transitions ("Section N spells out...") when the reader might lose the thread.
- **Compress on rewrite.** Target 20-50% word-count reduction. Second passes are almost always tighter.
- **Strategy docs end with the design.** Move open questions, TODOs, and checklists into a separate planning doc or ticket board.
- **Mirror a named reference doc.** When a template doc is cited, match its section shape, heading style, bullet format, and voice.
- **Problem-first, not method-first.** Organize around "what's broken and how we fix it," not around a menu of options leading to a recommendation.
- **Strategy in main body, implementation in appendix.** Main sections answer what, why, and how we know it works. Recipes, hyperparameters, threshold calibration: appendices.
- **Keep sections balanced in size.** If one section balloons, it contains implementation detail that belongs elsewhere.
- **Cross-reference explicitly.** Every problem maps to a goal, every goal maps to a section, every section forward-references the next. The reader traces: problem, goal, solution, section number.

## 3. Bullet-Narrative Format (Default for Lists)

The canonical bullet shape:

- **Bold lead-in phrase.** One to three sentences of narrative.

Each narrative bullet carries "what, why, implication": state the fact, add one sentence of reasoning, name the downstream consequence.

Additional rules:

- **Unnumbered over numbered.** Numbers imply strict ordering. Use them only when ordering is enforced (priority, dependency).
- **Intro sentence before every list.** One framing sentence before the first bullet. No naked bullet lists.
- **Explain schema-heavy bullets.** Field lists alone are unreadable. Add 1-2 lines: "what does this mean?" and "why do I care?"

## 4. Verbiage

- **No em-dashes in stakeholder content.** Use commas, colons, parentheses, semicolons, or start a new sentence. Em-dashes are acceptable in internal-only scratch notes.
- **No internal jargon in stakeholder artifacts.** No T-IDs, sprint numbers, owner initials, or ticket-tracker shorthand in slides, exec docs, or external content. Describe work by function.
- **Gloss acronyms on first use.** SME (subject-matter expert), PII (personally identifiable information). Once per doc.
- **Reference retained jargon.** When an internal term is unavoidable (Takt, bindle, P0, stage-6), link to the defining doc or wiki.
- **Plain words over code-ish nouns.** "Row-level truth" over "row-level record artifact"; "the layered design" over "the multi-tier storage architecture."
- **Italics for rhetorical emphasis only.** _what the system should do_ is fine. Scare quotes on ordinary phrasing are not.
- **No "for eg." or "for e.g."** Use "e.g.," directly.
- **No "On the contrary"** (often misused). Use "In contrast" or "In practice."
- **No ambiguous "This" to start sentences.** Specify the subject: "The precision-first design avoids..." not "This avoids..."
- **Always "i.e.," with comma after period.** Not "i.e," without the period.

## 5. Content Principles

- **Compress duplication ruthlessly.** If the same idea appears in §A intro, §B closer, and §C bullet, keep it in one place only.
- **Convert bare fields into meaning.** Turn column dumps into "what the row says" prose. Schema tables belong in appendices; main-body sections use narrative.
- **What, why, implication for every diagnosis.** Name the failure, hypothesize why, state the downstream effect.
- **Thread a concrete example through complex sections.** For schema-heavy docs, run one real example (with stable identifiers) from raw layer to gold layer, and reference it in later sections.
- **Name source-of-truth datasets, not intermediate code paths.** In stakeholder docs, cite the data (E2E evals, production trace schema, telemetry schema), not the code that produces it (package names, notebook paths, .py files).
- **Label stop-gaps explicitly.** When something is temporary, say so and name the canonical replacement.
- **Cite the source for every specific number.** Percentages, case counts, dates: every stat lands with a citation to the report or dataset that produced it.
- **Ground in real data, not placeholders.** Fill in actual numbers from available sources. Leave [TBD] only for genuinely unavailable data, and flag those as explicit gaps with a plan to fill them.
- **Real examples over hypotheticals.** Use actual eval cases (with ticket IDs, verbatim traces, scores) rather than invented scenarios.
- **Verbatim citations from sources.** When referencing eval data or ticket content, copy-paste verbatim and cite the source. Do not paraphrase operational data.
- **Weave narrative into the doc; punt raw data to appendix.** Main body gets the story (what happened, why it matters). Appendix gets the evidence (full traces, MLflow links, score tables).
- **Trim to what's referenced.** If a supporting case or data point is not used in the main narrative, cut it from the appendix.
- **Back-reference the diagnostic foundation.** Every recommendation traces back to the error decomposition or data inventory that justifies it (e.g., "§1 shows agent selection is 29-40% of errors, so SFT targets this").

## 6. Metrics and Thresholds

- **Every metric passes the "so what?" test.** If it regresses, you know which component to investigate. Metrics that fail this test are not tracked.
- **State severity ordering explicitly.** When listing items of different importance, say which matters most and why.
- **Quantify decision gates.** "Sufficient," "reliable," and "mature" are not thresholds. Specify numbers (at least 60 pairs, kappa at least 0.80, r at least 0.70) with rationale.
- **Qualify thresholds as initial.** Never present a threshold as derived from first principles. Say it is calibrated against a validation set and will be adjusted.
- **Distinguish pseudo-GT from gold GT.** Ensemble-generated labels are silver/pseudo until independently validated. Use the terms consistently.

## 7. Risks and Limitations

- **Name known risks; do not hide them.** An empty Limitations section undermines credibility. Four honest bullets is sufficient.
- **Answer risks, do not just list them.** Each risk gets: what it is, what triggers it, how we detect it, what we do about it. A list of open questions is not a risk analysis.
- **Recommendations should be falsifiable.** If a recommendation wins on every dimension, the analysis reads as advocacy. State where the chosen approach is worse than alternatives, and under what conditions you would revisit.

## 8. Document Hygiene

- **Delete struck-out content once superseded.** Struck-out text is for in-progress editing, not for the review version.
- **Resolve all TBDs before requesting review.** Every TBD is a question the document admits it has not answered.
- **Fix section numbering after restructuring.** Cross-references go stale when sections move. Do a full pass.
- **Remove duplicate content.** If a paragraph appears twice with slight variation, keep one.
- **Update stale appendix references.** If you remove an appendix, update every reference that pointed to it.
- **Separate frozen content from growing content.** When maintaining validation/calibration sets, distinguish frozen benchmarks (never modified) from growing calibration sets (refreshed each cycle).

## 9. Parallelization (Multi-Agent Authoring)

- **Use sub-agents for independent sections.** Break large documents into section-level agents that run in parallel, then stitch. Each agent gets the terminology guide and component framework.
- **Include a terminology brief in every sub-agent prompt.** This ensures consistency across parallel outputs (e.g., the 4-stage progression, L1/L2/L3 definitions).
- **Validation agent runs last.** After assembly, an independent agent checks classification accuracy, citation validity, internal consistency, and progression labeling.

## 10. Anti-Patterns to Reject

- "Executive summary" or "TL;DR" as a scattered mini-restatement. Either it earns its keep or cut it.
- Pipeline/architecture diagrams that duplicate the following prose. Diagram or prose, not both.
- Repeating design commitments across multiple sections. State once.
- Enumerating the same axes/consequences/requirements twice in adjacent sections.
- Trailing "Section N is the design that delivers these outcomes" closers on every section. Trust the reader.
- Appendices titled "Open questions" / "Punch list" / "TODOs." Those belong in a planning doc or ticket board.

---

## Quick Prompt-Bootstrap Block

Copy this into any new session:

```
Follow my house style: bullet-narrative bullets (**Bold lead.** narrative),
decisions-with-justifications tone (never approval-seeking), no em-dashes
in stakeholder content, no internal jargon in outward-facing artifacts,
first-use glosses for acronyms and references for retained jargon. State
design commitments once and point back with §-references. Cut duplication
ruthlessly on rewrites. Strategy docs end on the design, not on a TODO list.
Refer to source-of-truth datasets, not the code that produces them.
Problem-first structure. Strategy in main body, implementation in appendix.
Ground in real data. Thread concrete examples. Cite sources for every number.
Every metric passes the "so what?" test. Quantify decision gates. Answer
risks, do not just list them. Recommendations should be falsifiable.
Active voice. Short sentences. No aspirational filler.
```
