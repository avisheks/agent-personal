# Stock Research — Operating Instructions

## Role

Investment research agent that produces evidence-driven, contrarian stock analysis. Separates facts from inference, challenges consensus narratives, and grounds every claim in data. Two-stage architecture: deterministic data pipeline (Python) produces a structured research packet; LLM analyst agents consume it and produce the report.

**Audience:** Model fine-tuning team and personal investment decision-making. The benchmark is whether the report enables a confident hold/buy/sell decision with explicit falsification triggers.

## Commands

| Command | Description |
|---------|-------------|
| `/research-stock TICKER` | Full research report (auto-refreshes stale data) |
| `/research-stock TICKER --quick` | Executive summary + investment dashboard only |
| `/research-stock TICKER --refresh` | Force full data refresh before analysis |
| `/compare-stocks T1 T2 T3` | Peer comparison across fundamentals, valuation, sentiment |
| `/contrarian TICKER` | Contrarian-only deep dive (skip bull case, focus on what could go wrong) |

## Architecture

```
           Ticker config (peers, sources)
                      │
                      ▼
        ┌──────────────────────────┐
        │    STAGE 1: DATA         │
        │    (deterministic Python) │
        ├──────────────────────────┤
        │  SEC/XBRL fundamentals   │
        │  Yahoo Finance prices    │
        │  Alpha Vantage (optional)│
        │  FMP earnings (optional) │
        │  Reddit posts            │
        └────────────┬─────────────┘
                     │
          normalize / join / validate
                     │
                     ▼
        ┌──────────────────────────┐
        │   RESEARCH DB (DuckDB)   │
        │                          │
        │  company_fundamentals    │
        │  earnings                │
        │  prices                  │
        │  valuation               │
        │  sentiment_observations  │
        │  investor_claims         │
        └────────────┬─────────────┘
                     │
              feature generation
                     │
                     ▼
        ┌──────────────────────────┐
        │   RESEARCH PACKET (JSON) │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │    STAGE 2: LLM          │
        │    (reasoning only)       │
        ├──────────────────────────┤
        │                          │
        │  ┌────────┐ ┌─────────┐ │
        │  │  Bull   │ │Contrarian│ │
        │  │ Analyst │ │ Analyst  │ │
        │  └───┬────┘ └────┬────┘ │
        │      └─────┬─────┘      │
        │            ▼            │
        │      Adjudicator        │
        └────────────┬────────────┘
                     │
                     ▼
           Investment Report (.md)
```

## Workflow

When the user runs `/research-stock TICKER`:

### Step 1 — Load configuration

Read `config/tickers.yaml` for peer list and `config/sources.yaml` for API settings. If the ticker is not in tickers.yaml, use a default config with auto-discovered SIC peers.

### Step 2 — Check data freshness and refresh

For each data source, query `research.duckdb` for `last_updated`:

| Source | Stale threshold | Refresh command |
|--------|----------------|-----------------|
| Prices (Yahoo) | >1 trading day | `python src/stock_research/ingestion/market_data.py TICKER` |
| Fundamentals (SEC XBRL) | >30 days | `python src/stock_research/ingestion/sec.py TICKER` |
| Reddit sentiment | >3 days | `python src/stock_research/ingestion/reddit.py TICKER` |

**Reddit subreddit discovery:** The Reddit ingestion automatically searches both general subreddits (wallstreetbets, stocks, investing, StockMarket, options) AND ticker-dedicated subreddits discovered via pattern matching (r/TICKER, r/TICKER_Stock, r/TICKERstock, r/TICKERDiscussion, r/TICKER_investors). Additional subreddits from `tickers.yaml` are also searched. Non-existent subreddits return 0 results and are silently skipped.

**Reddit multi-engine fallback:** Reddit ingestion uses a multi-engine fallback: DuckDuckGo (primary, less rate-limited) -> Reddit JSON API (direct, most reliable but occasionally 429s) -> Google (last resort, frequently CAPTCHAd). The engine that succeeds is logged per subreddit.
| Earnings (FMP) | >90 days | `python src/stock_research/ingestion/earnings.py TICKER` |

If `--refresh` flag is set, refresh all sources regardless of staleness.

Log what was refreshed and any errors. If a source fails, proceed with available data and note the gap.

### Step 3 — Build research packet

Run: `python src/stock_research/packet_builder.py TICKER`

This produces a JSON research packet containing:
- `snapshot` — current fundamentals, valuation ratios, price
- `fundamentals_10y` — quarterly operating history
- `earnings_history` — beat/miss, guidance changes, stock reactions
- `peer_comparison` — relative valuation and fundamental ranking
- `valuation_models` — Owner-Earnings, DCF (bear/base/bull), EV/EBITDA
- `risk_metrics` — volatility, VaR, max drawdown
- `sentiment_history` — sentiment bucket per period
- `recent_sentiment` — last 6m/3m/1m Reddit narratives
- `investor_claims` — extracted claims with verification status
- `historical_sentiment_returns` — sentiment bucket → forward 1M/3M/6M/12M return
- `upcoming_events` — next earnings, ex-dividend, known catalysts
- `data_quality` — which sources succeeded, which failed, data gaps

### Step 4 — Run Bull Analyst

Spawn a sub-agent with the Bull Analyst prompt (see §Prompts below). It receives the full research packet and produces:
- Strongest evidence-based bull case
- Key growth drivers with supporting data
- Favorable valuation arguments
- Positive catalysts with timing
- Why current pessimism (if any) may be overdone

### Step 5 — Run Contrarian Analyst

Spawn a sub-agent with the Contrarian Analyst prompt. It receives the research packet AND the bull case from Step 4, and produces:
- For each bull claim: specific evidence that contradicts it
- Hidden assumptions the bull case requires to be true
- Historical precedents where similar narratives were wrong
- Risks the market may be underpricing
- Falsification triggers: what data would prove the bull case wrong

### Step 6 — Run Adjudicator

Spawn a sub-agent that receives:
- The research packet (raw data)
- The bull thesis
- The contrarian thesis

It produces the final synthesis:
- Where the bull case is strongest / weakest
- Where the contrarian case is strongest / weakest
- Probability-weighted 3/6/12-month scenarios
- Investment dashboard (§14 of the report)
- Bottom-line recommendation

### Step 7 — Generate report (two-stage rendering)

Generate output in two stages, matching the options-pnl-v3 pattern:

**Stage A — Markdown (.md)**

Write the Markdown report first. This is the source of truth.

```
.notlocal/data/personal-investor/reports/TICKER/TICKER_YYYY-MM-DD.md
```

The `.md` must include:
- Anchor IDs on every `##` heading (e.g., `<a id="fundamentals"></a>`)
- Table of Contents with clickable `[Section](#anchor)` links at the top
- Every section ends with `[↑ Back to Top](#top)`
- All tables in standard markdown pipe format
- Evidence labels (FACT/OPINION/INFERENCE/FORECAST) inline
- Source citations as inline links or footnotes

**Stage B — Styled HTML (.html)**

Convert the `.md` into a styled, self-contained HTML file:

```
.notlocal/data/personal-investor/reports/TICKER/TICKER_YYYY-MM-DD.html
```

**Implementation rule:** Any feature in the `.md` MUST also appear in the `.html`. Never assume the HTML nav bar satisfies a TOC requirement — verify by inspecting rendered output.

The `.html` must use the same CSS design system as options-pnl-v3:
- `max-width: 960px`, system font stack (Inter, -apple-system, ...), `font-size: 15px`, `line-height: 1.75`
- **Sticky nav bar** at top with section links (frosted glass: `rgba(253,253,253,0.92)` + `backdrop-filter: blur(10px)`)
- **Metric dashboard cards** (grid layout) for the Investment Dashboard scores — green left-border for positive, red for negative
- **ECharts** (`https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js`) for:
  - Revenue + EPS over 10 years (dual-axis line chart)
  - Revenue growth vs peers (grouped bar chart)
  - Margin trajectory vs peers (line chart)
  - Stock performance vs peers (indexed line chart, base=100)
  - Sentiment vs subsequent 3/6/12-month returns (scatter or grouped bar)
  - Current valuation vs historical valuation (percentile chart)
  - Bull/base/bear valuation scenarios (waterfall or bar chart)
- **Table styling:** `font-variant-numeric: lining-nums tabular-nums`, alternating rows on hover, sticky thead
- **Collapsible sections** (`<details><summary>`) for lengthy subsections (e.g., individual Reddit claims, full 40-quarter table)
- **Responsive:** mobile breakpoint at 768px (single-column charts, tighter padding)
- **Print:** hide nav, full-width, page-break-avoid on charts

**Stage C — Persist snapshot**

Also write the research packet JSON alongside the report:

```
.notlocal/data/personal-investor/reports/TICKER/TICKER_YYYY-MM-DD.json
```

This enables longitudinal comparison: "You told me this last year. Was it right?"

## Output Files

| File | Description |
|------|-------------|
| `TICKER_YYYY-MM-DD.md` | Markdown report (source of truth) |
| `TICKER_YYYY-MM-DD.html` | Styled HTML report with charts |
| `TICKER_YYYY-MM-DD.json` | Research packet snapshot (for longitudinal comparison) |
| `research-packet.json` | Latest research packet (overwritten each run) |

All outputs go to `.notlocal/data/personal-investor/reports/TICKER/`.

Naming convention mirrors options-pnl-v3: `{ticker}_{date}.{ext}` — no `-latest` alias needed since the research packet snapshot serves as the canonical state.

## Report Structure

Follow this exact structure (derived from the seed prompt):

1. **Executive Summary** — one page, conclusion-first
2. **Company Fundamentals** — current profile + peer comparison table
3. **Ten-Year Quarterly History** — table with Revenue, YoY Growth, EPS, Margins, FCF, Beat/Miss
4. **Historical Sentiment (5 years)** — year-by-year: narrative → evidence → outcome → was it correct?
5. **Sentiment vs. Subsequent Returns** — quantitative: sentiment bucket → forward 1M/3M/6M/12M
6. **Recent Sentiment** — 6m/3m/1m narratives with evidence quality assessment
7. **Reddit/Community Analysis** — signal vs. noise separation; recurring theses with verification status
8. **Valuation vs. Expectations** — reverse-engineered implied assumptions + bear/base/bull scenarios
9. **3/6/12-Month Outlook** — per-horizon scenarios with probabilities and key drivers
10. **Contrarian Analysis** — mandatory: for every consensus claim, the counter-evidence
11. **Things the Market May Be Missing** — underestimated risks AND opportunities
12. **Risk Analysis** — top 10 risks ranked by probability × impact
13. **Catalysts** — 0-3m / 3-6m / 6-12m with timing and confirmation/invalidation signals
14. **Investment Dashboard** — scores (1-10) for business quality, financial strength, growth, competitive position, management, valuation, sentiment, risk + bottom line
15. **Appendix: What Changed** — mandatory if a prior report exists; diff vs previous report

## Appendix: What Changed (mandatory for repeat reports)

When generating a report for a ticker that already has a prior report in `.notlocal/data/personal-investor/reports/TICKER/`, add an appendix section:

```markdown
## Appendix: What Changed vs Prior Report (YYYY-MM-DD)

### Score Changes
| Dimension | Previous | Current | Delta | Why |
|-----------|----------|---------|-------|-----|
| Valuation | 5/10 | 4/10 | -1 | P/E expanded from 45x to 58x |
| Growth | 7/10 | 8/10 | +1 | Q4 2025 EPS $3.41 exceeded expectations |

### Key Narrative Shifts
- **Previous:** "Growth story just beginning — early data center cycle"
- **Current:** "Growth proven but pricing in perfection — Cisco analogy emerging"

### New Data Since Last Report
- 2 new quarters of fundamentals (Q1-Q2 2026)
- 180 new daily price records
- N new Reddit posts from dedicated subreddits

### Thesis Changes
| Thesis element | Previous | Current | Changed? |
|----------------|----------|---------|----------|
| Bull case core | AI capex accelerating | AI capex sustained but priced in | ⚠️ Weakened |
| Bear case core | Unproven at scale | Great business, dangerous price | ↗ Strengthened |
| Falsification triggers | EPS < $5 TTM | EPS deceleration, multiple compression | Updated |
```

To generate the diff: read the prior `.json` research packet and compare dashboard scores, key metrics, and thesis elements. Highlight only material changes — not every data point update.

## Quarterly Rollup (report lifecycle management)

### Retention Policy

- **Current quarter:** Keep individual per-day reports (e.g., `CRWV_2026-09-13.md`, `CRWV_2026-09-14.md`)
- **Previous quarters:** Assimilate into a single quarterly report per ticker
- **Naming convention:** `TICKER_YYYY-QN_quarterly.md` (e.g., `CRWV_2026-Q3_quarterly.md`)

### Quarterly Assimilation Process

At the start of each new quarter, for each ticker with multiple reports from the prior quarter:

1. **Collect** all daily reports from the prior quarter: `TICKER_YYYY-MM-DD.{md,html,json}`
2. **Synthesize** into a quarterly report following this structure:

```markdown
# Quarterly Research Report: TICKER (YYYY QN)

**Period:** YYYY-MM-DD to YYYY-MM-DD
**Reports assimilated:** N daily reports

## Quarter Summary
{One-page synthesis: What changed over the quarter? What did we get right/wrong?}

## Prediction Scorecard
| Prediction (from earliest report) | Made | Outcome | Accuracy |
|-----------------------------------|------|---------|----------|
| "EPS will exceed $9 TTM by year-end" | Sep 13 | ⏳ Too early | — |
| "Multiple compression to 40x by Dec" | Sep 13 | ❌ Expanded to 58x | Wrong |

## Score Trajectory
| Dimension | Start of Quarter | End of Quarter | Trend |
|-----------|-----------------|---------------|-------|
| Business Quality | 9/10 | 9/10 | → Stable |
| Valuation | 5/10 | 4/10 | ↘ Deteriorated |

## Key Data Changes Over Quarter
{Summary of new fundamentals, price movement, sentiment shifts}

## Thesis Evolution
{How the bull/bear/contrarian thesis evolved week by week}

## Lessons Learned
{What the quarter taught us about this stock that the prior quarter didn't}
```

3. **Archive** daily reports into `reports/TICKER/archive/YYYY-QN/`
4. **Keep** the quarterly `.md`, `.html`, and the latest `.json` packet in the main ticker directory

### Calendar

This follows the same pattern as the news-summarizer skill's quarterly retrospectives:
- Q1: Jan–Mar → quarterly rollup generated in first week of April
- Q2: Apr–Jun → quarterly rollup generated in first week of July
- Q3: Jul–Sep → quarterly rollup generated in first week of October
- Q4: Oct–Dec → quarterly rollup generated in first week of January

## Evidence Rules

### Labeling (mandatory in every section)

- **FACT** — directly supported by a reliable source (cite it)
- **REPORTED OPINION** — analyst/investor/media opinion (attribute it)
- **INFERENCE** — your interpretation of the evidence (label it)
- **FORECAST** — your estimate of what is likely to happen (label it)

### Source hierarchy

| Tier | Sources | Use for |
|------|---------|---------|
| 1 (strongest) | SEC filings, audited financials, company disclosures, FRED | Financial facts |
| 2 | Earnings transcripts, analyst research, established data providers | Estimates, context |
| 3 | Reputable financial media | Industry context |
| 4 | Reddit, StockTwits, X, investor forums | Sentiment only — verify claims against Tier 1-2 |

### Integrity requirements

- Do NOT invent historical data — say "data unavailable"
- Do NOT fabricate analyst estimates
- Do NOT claim statistical significance without sufficient observations
- Do NOT treat price targets as facts
- Do NOT assume sentiment caused a stock move
- Do NOT blindly extrapolate recent growth
- When sources disagree, show the disagreement explicitly

## Prompts

### Bull Analyst

```
You are a senior investment analyst constructing the strongest evidence-based
bull case for {TICKER}. You receive a structured research packet — do NOT
recalculate metrics already provided.

Rules:
1. Every claim must cite a specific data point from the packet
2. Distinguish FACT from INFERENCE from FORECAST
3. Identify the 3 strongest growth/value drivers with supporting data
4. State what must be true for the bull case to play out
5. Acknowledge the strongest counter-argument but explain why you think
   the bull case prevails despite it
6. Provide explicit 3/6/12-month price-relevant catalysts with timing
```

### Contrarian Analyst

```
You are a forensic investment skeptic (Munger + Taleb lens). You receive
a research packet AND a bull thesis. Your job is to destroy the bull case
by finding evidence that contradicts it.

Rules:
1. For each bull claim, find specific contradicting evidence in the packet
2. Identify hidden assumptions the bull case requires
3. Find historical precedents where similar narratives were wrong
4. Calculate what the stock price assumes and whether those assumptions
   are realistic
5. List the top 5 risks that are NOT currently popular among investors
6. For each risk: probability, impact, leading indicator, falsification trigger
7. Do NOT be contrarian for its own sake — only when evidence supports it
```

### Adjudicator

```
You are a chief investment officer synthesizing two competing analyses.
You receive: the raw research packet, a bull thesis, and a contrarian thesis.

Rules:
1. Do NOT simply split the difference — weigh evidence quality
2. Where the bull and bear disagree, determine which has stronger data support
3. Assign probability-weighted scenarios for 3/6/12 months
4. Produce the investment dashboard (§14 scores)
5. State the single most important thing to monitor each quarter
6. End with: "What would change my mind" — specific, measurable triggers
```

## Data Pipeline Details

### DuckDB Schema

The research database lives at `.notlocal/data/personal-investor/db/research.duckdb`. See `src/stock_research/db.py` for the full schema. Core tables:

- `company_fundamentals` — quarterly: revenue, margins, EPS, FCF, debt, shares
- `earnings` — per-quarter: actual vs estimate, beat/miss, guidance, stock reaction
- `prices` — daily OHLCV + adjusted close
- `valuation` — daily/quarterly: P/E, forward P/E, EV/EBITDA, EV/Sales, FCF yield
- `sentiment_observations` — per-post: source, sentiment, narrative, engagement
- `investor_claims` — extracted claims with verification status
- `research_snapshots` — point-in-time packet snapshots for longitudinal comparison

### Python Code

All deterministic calculations live in `src/stock_research/`:

| Module | Responsibility |
|--------|---------------|
| `ingestion/sec.py` | SEC EDGAR XBRL API → raw fundamentals |
| `ingestion/market_data.py` | Yahoo Finance → prices + basic fundamentals |
| `ingestion/reddit.py` | Reddit via Google search → posts with metadata |
| `ingestion/earnings.py` | FMP API → earnings transcripts + estimates |
| `analytics/valuation.py` | 5-model intrinsic value (Owner-Earnings, DCF, Graham, Yield, PEG) |
| `analytics/risk.py` | Volatility, VaR, max drawdown |
| `analytics/returns.py` | CAGR, forward returns, peer-relative performance |
| `analytics/peers.py` | SIC-based peer discovery + median ratio comparison |
| `analytics/sentiment_returns.py` | Sentiment bucket → forward return analysis |
| `extraction/claim_classifier.py` | LLM: Reddit post → structured claim (Stage 1.5) |
| `packet_builder.py` | Assemble all data into research packet JSON |

### What the LLM should NOT do

The LLM must not calculate: P/E, CAGR, returns, earnings surprise, sentiment-vs-return statistics, peer ranking, valuation percentile, VaR, drawdown, or any other metric that Python already computes. If the research packet says `revenue_cagr_5y: 0.27`, use it — do not re-derive.

## Markdown Report Template

The `.md` report MUST follow this exact header and TOC pattern (matching options-pnl-v3):

```markdown
# Stock Research Report: {TICKER} ({COMPANY NAME})

**Generated:** YYYY-MM-DD
**As-of:** YYYY-MM-DD (data freshness date)
**Peers:** {PEER1}, {PEER2}, {PEER3}

---

<a id="top"></a>

## Contents

- [Executive Summary](#executive-summary)
- [Company Fundamentals](#fundamentals)
- [Ten-Year Quarterly History](#history)
- [Historical Sentiment (5Y)](#historical-sentiment)
- [Sentiment vs Returns](#sentiment-returns)
- [Recent Sentiment](#recent-sentiment)
- [Reddit / Community Analysis](#reddit)
- [Valuation vs Expectations](#valuation)
- [3/6/12-Month Outlook](#outlook)
- [Contrarian Analysis](#contrarian)
- [Things the Market May Be Missing](#missing)
- [Risk Analysis](#risks)
- [Catalysts](#catalysts)
- [Investment Dashboard](#dashboard)
- [Bottom Line](#bottom-line)

## Executive Summary

{one-page conclusion-first summary}

[↑ Back to Top](#top)

## Company Fundamentals

{current profile + peer comparison table}

[↑ Back to Top](#top)

...
```

**Sync rule:** The TOC entries MUST match the actual section headings. When adding, removing, or renaming a section, update the TOC at the same time. In HTML, both the nav bar AND a visible boxed Contents card at the top must match.

## HTML Report Spec

The `.html` MUST include these elements (matching options-pnl-v3 design system):

### Dashboard Cards (at top, after header)

```html
<div class="dashboard">
  <div class="metric-card positive">
    <div class="metric-value">8/10</div>
    <div class="metric-label">Business Quality</div>
  </div>
  <div class="metric-card negative">
    <div class="metric-value">4/10</div>
    <div class="metric-label">Valuation</div>
  </div>
  <!-- ... all 8 dashboard scores -->
</div>
```

Cards use green left-border (`.positive`) for scores ≥7, red (`.negative`) for ≤4, neutral for 5-6.

### Required Charts (ECharts)

| Chart | Type | Section |
|-------|------|---------|
| Revenue + EPS 10Y | Dual-axis line | Fundamentals |
| Revenue growth vs peers | Grouped bar | Fundamentals |
| Margin trajectory vs peers | Multi-line | Ten-Year History |
| Stock performance vs peers (indexed) | Line, base=100 | Ten-Year History |
| Sentiment vs forward returns | Grouped bar by bucket | Sentiment vs Returns |
| Valuation vs historical range | Percentile band | Valuation |
| Bull/Base/Bear scenarios | Waterfall or horizontal bar | Valuation |
| Cumulative price performance | Line with MA | Outlook |

### Collapsible Sections

Use `<details><summary>` for:
- Full 40-quarter history table (show summary row, collapse detail)
- Individual Reddit claims (show narrative summary, collapse individual posts)
- Per-risk detail in Risk Analysis (show risk name + severity, collapse evidence)

## Logging Requirements (mandatory)

**This skill MUST be invoked through the super-agent orchestrator.** Direct execution bypasses event logging and produces untraced sessions that cannot be evaluated or improved.

If you find yourself about to run data ingestion or generate a report without first going through `skills/super-agent.md` → plan → approve → execute, STOP. Go back and route through the orchestrator.

### Events to emit

The super-agent handles outer-protocol events (query, plan, approval). The skill is responsible for emitting **step-level events** at each workflow stage.

### Event Log Path

```
.local/logs/super-agent/events.jsonl
```

This is the SAME file the super-agent orchestrator writes to. All events — protocol-level (session_start, query, plan) and skill-level (data_refresh, agent_run, report_generated) — go into one shared log. Create the directory if it doesn't exist: `mkdir -p .local/logs/super-agent`.

**Why one file:** The evaluator (`src/evals/evaluate.py`) reads a single `events.jsonl` to reconstruct the full session trace. Splitting events across files would break eval and make debugging harder.

### Pre-Flight Check (mandatory before any execution)

Before running Step 1 or any subsequent step, verify:

```bash
# Must find a session_start event for today
grep "session_start" .local/logs/super-agent/events.jsonl 2>/dev/null | grep "$(date +%Y-%m-%d)" | tail -1
```

If this returns nothing, the super-agent orchestrator was NOT invoked. **STOP.** Go back to `skills/super-agent.md` and start the protocol from scratch. Do NOT proceed with data ingestion or report generation without a logged session.

### Step-Level Events

| Step | Event type | Key fields |
|------|-----------|------------|
| Step 2 (data freshness) | `skill_data_refresh` | `ticker`, `sources_refreshed` (list), `sources_skipped` (list), `errors` (list), `duration_ms` |
| Step 3 (build packet) | `skill_packet_built` | `ticker`, `fundamentals_quarters`, `price_days`, `sentiment_posts`, `claims_count`, `data_gaps` (list) |
| Step 4 (bull analyst) | `skill_agent_run` | `ticker`, `agent` ("bull"), `input_size_tokens` (approx), `output_size_tokens`, `duration_ms` |
| Step 5 (contrarian analyst) | `skill_agent_run` | `ticker`, `agent` ("contrarian"), `input_size_tokens`, `output_size_tokens`, `duration_ms` |
| Step 6 (adjudicator) | `skill_agent_run` | `ticker`, `agent` ("adjudicator"), `input_size_tokens`, `output_size_tokens`, `duration_ms` |
| Step 7 (generate report) | `skill_report_generated` | `ticker`, `report_path`, `html_path`, `json_path`, `sections_count`, `report_lines`, `quality_checks_passed` (list), `quality_checks_failed` (list) |

### Event format

```json
{"ts":"2026-09-13T19:15:00Z","session":"2026-09-13","turn":5,"event":"skill_data_refresh","skill":"personal-stock-research","ticker":"CRWV","sources_refreshed":["sec_xbrl","yahoo_finance"],"sources_skipped":["reddit"],"errors":[],"duration_ms":4200}
```

### Post-run eval hook

After the report is generated (Step 7), emit a `skill_report_generated` event that includes which quality checks passed and which failed. This enables the evaluator to assess report completeness without re-reading the report.

## Quality Checks

Before finalizing a report:

1. Every section present and non-empty
2. Every material factual claim has a source citation
3. Evidence labels (FACT/OPINION/INFERENCE/FORECAST) used in every section
4. Contrarian section contains specific counter-evidence, not vague skepticism
5. 3/6/12-month scenarios have explicit assumptions and falsification triggers
6. Investment dashboard scores are justified by evidence in the report body
7. "What would change my mind" lists measurable developments, not vague conditions

## Directory Structure

```
config/
├── tickers.yaml           # Active tickers + peers
└── sources.yaml           # API keys + source config
src/stock_research/
├── db.py                  # DuckDB schema + connection
├── ingestion/             # Stage 1A: raw data fetch
├── normalization/         # Stage 1B: canonical tables
├── analytics/             # Stage 1C: derived metrics
├── extraction/            # Stage 1.5: LLM claim extraction
└── packet_builder.py      # Stage 1D: research packet assembly
.notlocal/data/personal-investor/
├── db/research.duckdb     # Longitudinal research DB
├── raw/                   # Raw ingested data (provenance)
└── reports/{TICKER}/
    ├── NVDA_2026-09-13.md    # Markdown report (source of truth)
    ├── NVDA_2026-09-13.html  # Styled HTML with ECharts
    ├── NVDA_2026-09-13.json  # Research packet snapshot
    └── research-packet.json  # Latest packet (overwritten each run)
```
