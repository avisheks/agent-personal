# Stock Research Report — Style Guide

This guide ensures consistency across individual ticker reports and the weekly master comparison. It is the formatting source of truth — the SKILL.md defines *what* to include; this guide defines *how* it looks.

---

## 1. Individual Ticker Reports

### File naming

```
TICKER_YYYY-MM-DD.md     ← source of truth
TICKER_YYYY-MM-DD.html   ← styled derivative
TICKER_YYYY-MM-DD.json   ← research packet snapshot
```

### Header block (every report)

```markdown
# Stock Research Report: TICKER (Company Name)

**Generated:** YYYY-MM-DD
**As-of:** YYYY-MM-DD (latest price data)
**Peers:** PEER1, PEER2, PEER3
**Sector:** SECTOR_KEY (from tickers.yaml)
**Dashboard Composite:** X.X/10
```

### Section numbering

Use `##` for all 16 sections. No numbering in the heading text — numbering is implicit from order:

```markdown
## Executive Summary
## Company Fundamentals
## Ten-Year Quarterly History
...
## Appendix: Glossary
```

### Anchor IDs (mandatory on every section heading)

```markdown
<a id="executive-summary"></a>
## Executive Summary
```

### Table of Contents (mandatory, immediately after header)

```markdown
## Contents

- [Executive Summary](#executive-summary)
- [Company Fundamentals](#fundamentals)
...
- [Appendix: Glossary](#glossary)
```

### Evidence labels (inline, not footnotes)

Use **bold** labels inline within the text:

```markdown
Revenue grew 168% YoY to $5.1B. **FACT** [SEC XBRL]
The market appears to be pricing in sustained 30%+ growth. **INFERENCE**
We expect EPS to reach $9+ by 2027. **FORECAST**
Analysts at Morgan Stanley rate it Overweight. **REPORTED OPINION** [MS Research]
```

Do NOT use brackets like `[FACT]` — use bold: `**FACT**`.

### Tables

- Right-align all numeric columns
- Use `$` prefix for dollar amounts, `x` suffix for multiples, `%` suffix for percentages
- Bold the total/summary row
- N/A for missing data (never leave blank)

### Back to Top link (every section)

```markdown
[↑ Back to Top](#top)
```

### Glossary appendix

- Appended verbatim from `config/glossary.md` — never modified per-ticker
- Verification: MD5 of glossary section must be identical across all reports from the same run

### What Changed appendix

- Only present if a prior report exists for the ticker
- If first report: include the section with text "First report — no prior data to compare"
- Score changes table: show only dimensions that changed, with delta and reason

---

## 2. Master Comparison Report

### File naming

```
YYYY-MM-DD-master.md     ← source of truth
YYYY-MM-DD-master.html   ← styled derivative with sortable tables
```

### Header block

```markdown
# Weekly Stock Research — Master Comparison (YYYY-MM-DD)

**Tickers:** N | **Reports generated:** N/N
**Sectors:** N unique sectors represented
**Batch source:** `config/weekly-batch.yaml`
```

### Fundamentals comparison table

- Sorted by dashboard composite score (highest first)
- Report links point to **.html** files (not .md): `[→](TICKER/TICKER_YYYY-MM-DD.html)`
- All 19 tickers present with no omissions
- Color-code dashboard scores in HTML: green (≥7), amber (5-6.9), red (<5)

### Sector grouping

- One subsection per sector that has ≥1 ticker in the batch
- Show ALL tickers in the sector — do not omit the ticker being compared
- Median row computed from ALL tickers in the sector (not N-1)
- Each ticker's "vs Median" shows the signed deviation from the full-sector median

### Similar Tickers section — "Explore These Next"

**Purpose:** For each ticker in our batch, suggest 2-3 tickers that are NOT in our 19-ticker batch but belong to the same sector and have similar fundamentals. These are "explore next" suggestions — stocks the user should research because they're structurally similar to ones they already track.

**Rules:**
1. Similar tickers MUST be from the **same sector** (per `config/tickers.yaml` sectors section)
2. Similar tickers MUST NOT be any of the 19 batch tickers
3. Similarity based on: market cap (log-scaled), EV/Sales, and volatility tier
4. For each suggestion: ticker, name (if known), and a one-line "why" explanation

**Format:**

```markdown
| Batch Ticker | Sector | Explore These (same sector, not in batch) | Why |
|-------------|--------|------------------------------------------|-----|
| SNPS | EDA | CDNS (Cadence Design) | Duopoly partner, similar EV/Sales ~8x |
| VRT | DATACENTER-INFRA | CARR, ETN, PWR, NEE | Same sector, VRT peers from tickers.yaml |
| CRWV | AI-INFRA | NBIS | Only other AI-INFRA ticker in universe |
```

If a sector has no other tickers beyond the batch ticker, say "No additional tickers in sector."

### Risk tier summary

- 4 tiers: Low (<30%), Medium (30-50%), High (50-75%), Very High (>75%)
- List tickers with vol % in parentheses
- Note the batch risk profile (% in each tier)

### Best/Worst table

- ~10 categories covering valuation, quality, risk, size extremes
- Include the ticker, value, and a one-line note

---

## 3. HTML Styling (both individual and master)

### CSS design system (v3)

All HTML reports use the same CSS:
- `max-width: 960px`, font: Inter/-apple-system, `font-size: 15px`, `line-height: 1.75`
- Sticky nav bar: `position: sticky; top: 0; z-index: 100; rgba(253,253,253,0.92)` + `backdrop-filter: blur(10px)`
- Tables: `font-variant-numeric: lining-nums tabular-nums`, `tr:hover #f5f5f5`
- Metric cards: `.dashboard` grid, `.metric-card` with colored left-border
- Responsive at 768px, print-safe (hide nav)

### Table header rendering (IMPORTANT — prevents hidden header rows)

**Do NOT use `position: sticky` on `thead`.** In multi-table documents, sticky theads at `top: 48px` (below the nav) cause header rows to be hidden behind the nav bar when scrolling to a table via anchor link or on initial render.

Instead:
- `thead { position: static; }` — headers render normally within the table flow
- `[id] { scroll-margin-top: 60px; }` — anchor link targets offset by nav height so the nav doesn't cover the content
- `h2, h3 { scroll-margin-top: 60px; }` — section headings also offset

This ensures that when a user clicks a nav link or scrolls to a table, the header row is always visible.

**For individual reports with a SINGLE main table:** Sticky thead is acceptable since there's less ambiguity. But for master reports with 12+ tables, use static thead.

### Individual report HTML additions

- ECharts for data visualization (revenue, EPS, FCF charts)
- Dashboard cards for investment scores
- Collapsible `<details>` for glossary and long tables
- Evidence badges: FACT (blue #3b82f6), INFERENCE (amber #f59e0b), FORECAST (purple #8b5cf6), REPORTED OPINION (pink #ec4899)

### Master report HTML additions

- Sortable table columns (JS onclick toggle asc/desc)
- Dashboard score color: `.score-green` (≥7), `.score-amber` (5-6.9), `.score-red` (<5)
- Risk tier badges: `.risk-green` (Medium), `.risk-amber` (High), `.risk-red` (Very High)
- Report links open .html files in same directory structure
- No ECharts — tables are the primary visualization

---

## 4. Consistency Rules

1. **Same run date across all files:** Individual reports, master report, and research packets all use the same YYYY-MM-DD
2. **Glossary identical:** Every report's glossary section produces the same MD5 hash
3. **Dashboard scores match:** The score in a ticker's individual report must match the score in the master comparison table
4. **Metrics match:** P/E, Fwd P/E, etc. in the master table must match the individual report's fundamentals section (both sourced from the research packet JSON)
5. **No invented data:** If a metric is N/A in the packet, it's N/A in both the individual report and the master table
6. **Links work:** Master table links to individual .html files; verify paths exist after generation
