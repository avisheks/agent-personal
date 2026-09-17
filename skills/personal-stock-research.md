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
| `/batch --weekly` | Run weekly batch from `config/weekly-batch.yaml` (19 tickers, 10-min throttle) |
| `/batch TICKER1 TICKER2` | Run batch for specific tickers |
| `/batch --dry-run` | Preview what the batch would process |

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

**Reddit fetching strategy (tested Sep 2026):**

Reddit blocks Anthropic/Claude specifically (no API deal unlike Google/OpenAI). Tested workarounds:

| Method | Works? | Notes |
|--------|--------|-------|
| **www.reddit.com RSS** | ✅ Yes | Only reliable method. Full post content. Rate limit: ≥5s between requests |
| old.reddit.com JSON | ❌ No | Returns 403 (blocked) |
| old.reddit.com RSS | ❌ No | Returns HTML page, not RSS |
| Reddit JSON API | ❌ No | 403 without OAuth token |
| DuckDuckGo | ⚠️ Bursts | Works initially then CAPTCHAs after ~5-10 requests |
| Google | ⚠️ Bursts | Same CAPTCHA issue as DDG |
| curl (raw) | Same as httpx | curl doesn't bypass — it's the endpoint that matters, not the client |

**Engine order:** RSS (primary) → DDG (burst fallback) → Google (last resort). The Reddit JSON API and old.reddit.com are kept in the code but almost never succeed.

**Critical rate limit rule:** Reddit RSS returns 429 after rapid bursts. The ingestion MUST:
1. Wait ≥5 seconds between subreddit requests (not 2s as was originally set)
2. Process tickers sequentially, not in parallel
3. If 429'd, wait 60+ seconds before retrying
4. For 20 tickers × 10 subs each = 200 requests → at 5s each = ~17 minutes minimum

**Do NOT use WebFetch for Reddit.** WebFetch routes through a smaller model that compresses and sometimes invents content. Instead, use httpx (curl-style) to fetch raw RSS/JSON and parse it directly. This is why our reddit.py uses httpx+BeautifulSoup, not WebFetch.

**Per community research (Sep 2026):** "WebFetch uses a smaller, cheaper model and then the main model gets a summary. The smaller model compresses, guesses, and sometimes invents details." Fix: "Curl the raw page and grep/read the actual text yourself."
| Earnings (FMP) | >90 days | `python src/stock_research/ingestion/earnings.py TICKER` |

If `--refresh` flag is set, refresh all sources regardless of staleness.

Log what was refreshed and any errors. If a source fails, proceed with available data and note the gap.

**Data-before-report rule (mandatory):** ALL ingestion must complete and be stored in DuckDB BEFORE Step 3 (packet building) runs. The research packet reads from the DB, and the report reads from the packet. If Reddit ingestion returns N>0 posts, those posts MUST appear in the Reddit/Community Analysis section of the final report — not a stale "0 posts" message from a prior run. After ingestion, verify the DB has fresh data:

```bash
PYTHONPATH=src python3 -c "
from stock_research import db
conn = db.get_connection()
for src in ['sec_xbrl','yahoo_finance','reddit']:
    ts = db.get_freshness(conn, 'TICKER', src)
    count = conn.execute(\"SELECT record_count FROM data_freshness WHERE ticker='TICKER' AND source_name='\"+src+\"'\").fetchone()
    print(f'{src}: last_updated={ts}, records={count[0] if count else 0}')
"
```

If Reddit shows record_count > 0, the report MUST include those posts. If the report section says "0 posts" but the DB has posts, the report is WRONG — re-generate it.

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

**Post-ingestion verification (mandatory before writing any report text):**

Before writing the .md, read the research packet JSON and verify it reflects the latest ingested data. Specifically:
- If `recent_sentiment` in the packet has posts, the Reddit/Community Analysis section MUST list those posts with titles, subreddits, sentiment direction, and snippets
- If `fundamentals_10y` has N quarters, the quarterly history table MUST have N rows
- If `risk_metrics` has values, the Risk Analysis section MUST use those values (not invent them)
- Do NOT write "0 posts" or "data unavailable" for any field where the packet has data

**The research packet is the single source of truth for all data in the report.** The LLM adds interpretation (bull/bear/contrarian analysis) but does NOT override, omit, or contradict any data in the packet.

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
| `TICKER_YYYY-MM-DD.md` | Markdown report (source of truth, individual tickers) |
| `TICKER_YYYY-MM-DD.json` | Research packet snapshot (for longitudinal comparison) |
| `research-packet.json` | Latest research packet (overwritten each run) |
| `YYYY-MM-DD-master.md` | Master comparison report (markdown) |
| `YYYY-MM-DD-master.html` | Master comparison report (styled HTML with sortable tables) |

Individual ticker outputs go to `.notlocal/data/personal-investor/reports/TICKER/`.
Master report goes to `.notlocal/data/personal-investor/reports/`.

Naming convention mirrors options-pnl-v3: `{ticker}_{date}.{ext}` — no `-latest` alias needed since the research packet snapshot serves as the canonical state.

## Report Structure

Follow this exact structure. Sections are ordered quality-first, then valuation, then sentiment, then synthesis.

1. **Executive Summary** — one page, conclusion-first. Must include quality gate verdict: "passes/fails quality screen on ROIC > WACC, positive FCF, D/E < 1.5." If quality fails, state it upfront. Include valuation range visualization (ASCII bar showing bear/base/bull and where current price sits).
2. **Earnings Quality** — Reported EPS vs Adjusted EPS (strip SBC, normalize CapEx, exclude one-timers). P/E on reported vs P/E on adjusted. SBC as % of revenue. SBC-adjusted FCF = FCF - SBC. Flag SBC > 15% of revenue. **Operating leverage trajectory**: show gross margin vs operating margin gap and whether it's narrowing over last 8 quarters. For high-gross-margin businesses (>60%), this is THE value driver.
3. **Company Fundamentals** — current profile + peer comparison. Must include SBC line item and **institutional ownership %** (from Yahoo Finance) with direction (increasing/decreasing/stable). Flag "under-owned by institutions" (<50%) as potential catalyst. **P/E vs historical range**: current P/E vs 5-year average P/E, show percentile ("cheapest/most expensive in 5 years"). Sector-specific primary metric highlighted. **Technical price signals** (mandatory sub-section):
   - **52-week high / 52-week low**: from price history in research packet. Show current price as % from high and % from low.
   - **Golden cross / Death cross**: 50-day SMA vs 200-day SMA. State which occurred most recently and the date. Golden cross (50 > 200) = bullish; Death cross (50 < 200) = bearish.
   - **Entry/Exit recommendation**: Based on valuation range + technical signals, provide one of: 🟢 **Good entry point** (near bear case + golden cross or oversold), 🟡 **Hold / wait** (fair value zone, no strong signal), 🔴 **Consider exit** (above bull case + death cross or overbought). Include a one-sentence rationale.
   - Data source: compute from `prices` table in research packet (252 trading days for 52-week, 50/200-day SMAs). If insufficient price history, state "N/A — insufficient data" for each.
4. **Ten-Year Quarterly History** — table with Revenue, YoY Growth, EPS, Adjusted EPS, Margins (gross AND operating — show the gap), FCF, SBC-adjusted FCF, Beat/Miss
5. **Historical Sentiment (5 years)** — year-by-year: narrative → evidence → outcome → was it correct?
6. **Sentiment vs. Subsequent Returns** — quantitative: sentiment bucket → forward 1M/3M/6M/12M
7. **Recent Sentiment** — 6m/3m/1m narratives with evidence quality assessment
8. **Reddit/Community Analysis** — signal vs. noise separation; recurring theses with verification status
9. **Valuation vs. Expectations** — THREE components:
   - (a) **Reverse DCF**: Given current price, what revenue CAGR and margin does the market imply? Is that realistic?
   - (b) **Forward DCF**: Bear/base/bull 5-year projections (our existing 5-model approach)
   - (c) **Sector-appropriate metric**: Lead with the primary metric for this sector (not always P/E)
   - (d) **Valuation range**: Present as a visual range, not a point estimate:
     ```
     $150 ───[████████████████████]─── $450
              Bear    Base    Bull
              $180    $280    $420
              Current: $287 ← sits here
     ```
10. **3/6/12-Month Outlook** — per-horizon scenarios with probabilities and key drivers
11. **Contrarian Analysis** — mandatory: for every consensus claim, the counter-evidence. **Insider buying/selling**: check for recent insider transactions (cite OpenInsider.com). Cluster buys (3+ insiders in same month) are the strongest signal per community consensus.
12. **Things the Market May Be Missing** — underestimated risks AND opportunities
13. **Risk Analysis** — top 10 risks ranked by probability × impact
14. **Catalysts** — 0-3m / 3-6m / 6-12m with timing and confirmation/invalidation signals
15. **Investment Dashboard** — scores (1-10) ordered QUALITY FIRST: business quality, financial strength, competitive position, **durability** (NEW: 10+ year compounder probability — switching costs, network effects, regulatory moat, disruption risk), THEN growth, management, valuation, sentiment, risk + bottom line. **10 dimensions total** (was 8).
16. **Appendix: What Changed** — mandatory if a prior report exists; diff vs previous report

**NOTE: Individual ticker reports NO LONGER include the Glossary appendix.** The glossary lives in the master report only (see Stage 3). This reduces per-report size by ~200 lines while keeping the glossary available as a shared reference.

## Glossary (master report only — NOT in individual reports)

The glossary is hardcoded at `config/glossary.md` (34 terms, 7 categories, Acme Corp worked examples). It is appended **only to the master comparison report**, not to individual ticker reports. This saves ~200 lines per report while keeping one shared reference.

**Master report glossary workflow:**
1. After all master sections are written, read `config/glossary.md`
2. Append verbatim as a master appendix section
3. In HTML: render inside `<details open>` with nav bar link "Glossary"

**Adding new terms:** Add to `config/glossary.md` in the correct category. The next master report picks it up automatically.

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

## Weekly Batch Job

### Config

The weekly ticker list is stored in an editable config file:

```
config/weekly-batch.yaml
```

Edit this file to add/remove tickers. The batch runner reads it when invoked with `--weekly`. Format:

```yaml
tickers:
  - SNPS
  - TSLA
  - VRT
  # ... add/remove tickers here

delay_seconds: 600  # 10 min between tickers
```

### Schedule

**Cron: Sunday 9:03 AM PT** (durable — survives session restarts)

The weekly job runs Stage 1 only (deterministic data pipeline):
- SEC XBRL fundamentals
- Yahoo Finance prices + valuation
- Reddit sentiment (RSS → DDG → Reddit API → Google fallback)
- Research packet JSON assembly

The weekly cron job runs both Stage 1 (data ingestion) and Stage 2 (LLM report generation) for all tickers in the weekly batch config.

### Prerequisites

Before running any batch or research command, ensure:

1. **AWS credentials** (needed for Bedrock LLM calls in Stage 2):
   ```bash
   ada credentials update --account=237287177058 --provider=conduit --role=IibsAdminAccess-DO-NOT-DELETE --profile=default --once
   ```

2. **SEC EDGAR User-Agent** (required by SEC for API access):
   ```bash
   export EDGAR_USER_AGENT="Avishek Saha avisaha@example.com"
   ```

3. **Python dependencies**:
   ```bash
   pip install duckdb yfinance httpx beautifulsoup4 pyyaml
   ```

### CLI

```bash
# Weekly mode (reads config/weekly-batch.yaml)
PYTHONPATH=src EDGAR_USER_AGENT="Avishek Saha avisaha@example.com" \
  python3 -m stock_research.batch_runner --weekly

# Specific tickers (ignores weekly config)
python3 -m stock_research.batch_runner CRWV VRT NVDA

# Preview without running
python3 -m stock_research.batch_runner --weekly --dry-run

# Custom throttle (5 min instead of 10)
python3 -m stock_research.batch_runner --weekly --delay 300

# Explicit date (for backfill or corrections)
python3 -m stock_research.batch_runner --weekly --date 2026-09-13
```

### Report Date Convention (IMPORTANT)

**All report filenames use the most recent Sunday date, not the execution date.**

The batch runner defaults to `_most_recent_sunday()` which returns the prior Sunday (or today if today is Sunday). This ensures that a batch fired on Sunday at 9AM, or re-run on Tuesday to fix an issue, produces the same filename date.

Examples:
- Cron fires Sunday Sep 13 at 9AM → report date: `2026-09-13`
- Manual re-run on Tuesday Sep 16 → report date: `2026-09-13` (same Sunday)
- Override with `--date 2026-09-13` to force a specific date

**Why:** Reports are weekly snapshots tied to the Sunday schedule. Using the execution date causes mismatches when re-runs happen mid-week (as happened with the 2026-09-16 dated files that should have been 2026-09-13).

**The LLM report generation (Stage 2) must also use the Sunday date** for .md and .html filenames. When generating reports, use the same date as the research packet JSON — do NOT use `date +%Y-%m-%d`.

### What it produces

For each ticker: a research packet JSON at `.notlocal/data/personal-investor/reports/TICKER/TICKER_YYYY-MM-DD.json` (where YYYY-MM-DD is the Sunday date), plus updated DuckDB records for fundamentals, prices, and sentiment.

### Event logging

The batch runner emits events to `.local/logs/super-agent/events.jsonl`:
- `batch_start` — ticker list, delay, dry_run flag
- `batch_ticker_complete` — per-ticker: sources refreshed/failed, record counts, duration
- `batch_end` — success/failure counts

### Format Verification Gate (mandatory — between Stage 2 and Stage 3)

**Before generating the master report, verify that ALL individual ticker reports follow the standardized format.** The master report compilation MUST NOT begin until every ticker report passes this check.

#### Standardized Report Format (16 sections, in order)

Every individual ticker `.md` file must contain these sections with matching anchor IDs:

| # | Section | Anchor ID | Required Elements |
|---|---------|-----------|-------------------|
| 1 | Executive Summary | `executive-summary` | Quality gate verdict, key metrics table, ASCII valuation range bar (bear/base/bull) |
| 2 | Earnings Quality | `earnings-quality` | SBC-adjusted EPS, FCF quality, operating leverage trajectory |
| 3 | Company Fundamentals | `fundamentals` | Peer comparison table, P/E vs 5yr historical percentile, institutional ownership %, 52-week high/low, golden/death cross, entry/exit recommendation |
| 4 | Ten-Year Quarterly History | `history` | Revenue + EPS table (≥8 quarters), gross AND operating margin gap |
| 5 | Historical Sentiment (5Y) | `sentiment-5y` | Sentiment distribution table |
| 6 | Sentiment vs Returns | `sentiment-returns` | Bucket analysis |
| 7 | Recent Sentiment | `recent-sentiment` | Last 30-day posts |
| 8 | Reddit / Community | `reddit` | Sub-reddit sources, narrative themes |
| 9 | Valuation vs Expectations | `valuation` | Reverse DCF, forward DCF (bear/base/bull), sector comparison |
| 10 | 3/6/12-Month Outlook | `outlook` | Probability-weighted scenarios |
| 11 | Contrarian Analysis | `contrarian` | Counter-arguments, insider buying signal |
| 12 | Things Market May Miss | `market-missing` | ≥3 underappreciated factors |
| 13 | Risk Analysis | `risk` | Top risks ranked by probability × impact |
| 14 | Catalysts | `catalysts` | Near/medium/long-term buckets |
| 15 | Investment Dashboard | `dashboard` | 10 dimensions (incl. durability), composite score |
| 16 | Appendix: What Changed | `what-changed` | Delta vs prior report (or "First report") |

#### Verification Script

```bash
# Run from reports/ directory after all individual .md files are generated
PASS=0; FAIL=0; DATE="YYYY-MM-DD"
for dir in */; do
  ticker="${dir%/}"
  f="$ticker/${ticker}_${DATE}.md"
  [ ! -f "$f" ] && continue
  errors=""
  # Check all 16 required sections exist
  for section in "Executive Summary" "Earnings Quality" "Company Fundamentals" \
    "Ten-Year Quarterly History" "Historical Sentiment" "Sentiment vs Returns" \
    "Recent Sentiment" "Reddit" "Valuation" "Outlook" "Contrarian" \
    "Market May Be Missing" "Risk Analysis" "Catalysts" "Investment Dashboard" \
    "What Changed"; do
    grep -qi "$section" "$f" || errors="$errors MISSING:$section"
  done
  # Check no SOP v2 jargon
  grep -qi "SOP v2\|SOPv2" "$f" && errors="$errors HAS:SOP-v2-jargon"
  # Check no glossary (individual reports)
  grep -qi "## Glossary\|## Appendix.*Glossary" "$f" && errors="$errors HAS:glossary"
  # Check TOC exists
  grep -qi "Contents\|Table of Contents" "$f" || errors="$errors MISSING:TOC"
  # Check Back to Top links
  BTT=$(grep -ci "back to top" "$f")
  [ "$BTT" -lt 8 ] && errors="$errors LOW:BackToTop($BTT)"
  # Check technical indicators (52-week, cross, entry/exit)
  grep -qi "52-week\|52.week" "$f" || errors="$errors MISSING:52-week-range"
  grep -qi "golden cross\|death cross" "$f" || errors="$errors MISSING:golden-death-cross"
  grep -qi "entry point\|exit point\|entry\|Hold.*wait\|Good entry\|Consider exit" "$f" || errors="$errors MISSING:entry-exit-signal"

  if [ -z "$errors" ]; then
    echo "✅ $ticker"; PASS=$((PASS+1))
  else
    echo "❌ $ticker:$errors"; FAIL=$((FAIL+1))
  fi
done
echo "---"
echo "PASS: $PASS | FAIL: $FAIL"
[ "$FAIL" -gt 0 ] && echo "⛔ FIX FAILURES BEFORE GENERATING MASTER REPORT"
```

**If ANY ticker fails format verification:** Fix the report before proceeding.

### Numeric Verification Gate (mandatory — after format gate, before master report)

After all reports pass the format gate, run the numeric verifier to catch stale/hallucinated values:

```bash
cd $REPO_ROOT
python -m stock_research.report_verifier --date YYYY-MM-DD
```

**What it checks (3 layers):**
1. **DuckDB source-of-truth** — report-stated price vs latest price in `prices` table (>5% deviation = FAIL)
2. **Live spot-check** — report-stated price vs current yfinance price (>5% deviation = FAIL)
3. **Sanity bounds** — non-positive prices, MCap; vol >200%; dashboard score out of 0-10; 52wk high < low; price >150% of 52wk high

**Exit code:** 0 = all pass, 1 = one or more tickers fail.

**If ANY ticker fails numeric verification:** The report's price/metrics are stale or hallucinated. Re-run the data pipeline (Stage 1) for the failed tickers, regenerate their individual reports (Stage 2), then re-run verification. Do NOT proceed to master report generation until all tickers pass.

**Event emitted:** `report_verification` with pass/fail counts and failed ticker list.

```bash
# To verify specific tickers only:
python -m stock_research.report_verifier --date YYYY-MM-DD --tickers RDDT,TSLA

# To skip live yfinance check (offline mode):
python -m stock_research.report_verifier --date YYYY-MM-DD --no-live

# Custom tolerance (default 5%):
python -m stock_research.report_verifier --date YYYY-MM-DD --tolerance 0.10
```

### Stage 3: Master Report (mandatory — fires after all individual reports pass BOTH gates)

**⛔ CRITICAL: The master report must NOT invent, fetch, or synthesize any new data.**

The master report is a **compilation-only** document. Every number, score, metric, valuation range, risk tier, and sector grouping must be extracted directly from the existing individual ticker `.md` reports and/or research packet `.json` files. Specifically:

- **DO NOT** call any API, scrape any website, or run any data pipeline during master report generation
- **DO NOT** estimate, interpolate, or guess missing values — if a ticker's report says "N/A", the master says "N/A"
- **DO NOT** recalculate dashboard scores, valuation ranges, or risk metrics — copy them from the individual reports
- **DO NOT** add "explore" ticker data (price, MCap, multiples) that isn't already in the individual reports or tickers.yaml — use approximate values with `~` prefix only from tickers.yaml sector peers
- **Source of truth:** Individual ticker `.md` report → research packet `.json` → tickers.yaml (in that priority order)
- **Verification:** After generating the master, spot-check 3 random tickers — their master-row values must match their individual report values exactly

#### Mandatory Parallel Agent Pipeline for Master Report Generation

**This is the REQUIRED workflow for generating the master report. Do NOT write the master report inline or with a single agent. Always use this 3-phase pipeline.**

The master report is too large for a single-pass write (typically 35-70KB .md + 60-100KB .html). Single-agent generation causes stalls, context overflow, and data inconsistencies. The pipeline below ensures correctness via separation of concerns.

---

**Phase 1 — Data Extraction (single agent, MUST run first, blocking)**

Launch ONE agent with `run_in_background: false` that:
1. Reads all individual ticker `.md` reports (header + fundamentals + dashboard + valuation range sections)
2. Extracts per-ticker: Price, MCap, P/E, Fwd P/E, EV/EBITDA, EV/Sales, Vol%, Dashboard score, Sector, Bear price, Bull price, 52-week High, 52-week Low, Signal (🟢/🟡/🔴), Most recent cross (Golden/Death + date)
3. Writes a structured pipe-delimited data file to `/tmp/master-data-YYYY-MM-DD.txt`
4. This file is the **SINGLE SOURCE OF TRUTH** for all Phase 2 agents — no agent reads individual reports directly

**Enforcement:** If `/tmp/master-data-YYYY-MM-DD.txt` does not exist when Phase 2 starts, STOP. Phase 1 was skipped.

---

**Phase 2 — Parallel Section Writers (4 agents, launched simultaneously)**

Launch ALL FOUR agents in a single tool-call message so they run concurrently:

| Agent | Output File | Section(s) | Input |
|-------|------------|-----------|-------|
| Agent A | `/tmp/master-A-risk-comparison.md` | §1 Risk Tier Summary + §2 Comparison Table (with Valuation Range) | Data file |
| Agent B | `/tmp/master-B-explore.md` | §3 Explore These Next | Data file + `config/tickers.yaml` |
| Agent C | `/tmp/master-C-sectors-bestworst.md` | §4 Sector Grouping + §5 Best/Worst | Data file |
| Agent D | `/tmp/master-D-appendix.md` | §6+§7 Appendix (worked example + glossary) | EXPE individual report + `config/glossary.md` |

**Rules for each agent:**
- Output ≤25KB per file
- Use ONLY data from the extraction file (Phase 1) — no external fetches, no re-reading individual reports
- Agent B may read `config/tickers.yaml` for explore-ticker sector peers (with `~` approximations)
- Agent D may read the EXPE individual report and `config/glossary.md` for the appendix content
- Include proper anchor IDs and Back to Top links in each section

---

**Phase 3 — Compilation + Cross-Check (single agent, MUST run after Phase 2 completes)**

Launch ONE agent that:
1. Reads all 4 section files from `/tmp/master-{A,B,C,D}-*.md`
2. Assembles into `YYYY-MM-DD-master.md` with TOC, header, and section ordering
3. Generates `YYYY-MM-DD-master.html` with CSS design system v3 (score pills, sortable tables, emoji headings, risk badges)
4. Runs these **mandatory cross-checks:**
   - [ ] All 20 tickers present in comparison table
   - [ ] Spot-check 3 random tickers: master-row values match extraction file
   - [ ] Section numbering is sequential (1-5 + Appendix)
   - [ ] No "SOP v2" or internal jargon anywhere
   - [ ] All report links point to existing `.md` files
   - [ ] HTML has score pill badges, sortable JS, emoji headings, static thead
5. If any check fails: fix inline before writing final output
6. Writes both .md (≤25KB chunks) and .html (≤25KB chunks) to the reports directory

---

**Cleanup:** After successful generation, delete `/tmp/master-*.md` and `/tmp/master-data-*.txt`.

After ALL individual ticker reports (.md) are generated AND pass the format verification gate, produce a master comparison doc:

```
.notlocal/data/personal-investor/reports/YYYY-MM-DD-master.md
.notlocal/data/personal-investor/reports/YYYY-MM-DD-master.html
```

The date matches the weekly run date (same as the individual report dates).

**Master report structure (sections in this order):**

#### 1. Header + Signal Summary

```markdown
# Weekly Stock Research — Master Comparison (YYYY-MM-DD)

**Tickers:** N | **Reports generated:** N/N
**Sectors:** N unique sectors represented
**Source:** All data extracted from individual ticker .md reports — no external data fetched.

**Signal Breakdown:** 🟢 Good entry (N tickers: AAA, BBB, ...) | 🟡 Hold (N: CCC, ...) | 🔴 Consider exit (N: DDD, ...)
```

The signal breakdown is a top-level summary computed from the Entry/Exit Signal in each ticker's Technical Price Signals sub-section. It gives the reader an instant portfolio-level view before they dive into details.

#### 2. Risk Tier Summary (FIRST after header)

Group all tickers into risk tiers. This goes first because it's the quickest way to orient the reader on the risk profile of the entire batch.

| Risk Tier | Tickers | Characteristics |
|-----------|---------|-----------------|
| Low (Vol <30%) | — | — |
| Medium (30-50%) | BKNG, SNPS, EXPE | Profitable, established |
| High (50-75%) | VRT, TSLA, UUUU, MP, HOOD | Growth premium, cyclical |
| Very High (>75%) | CRWV, IREN, IONQ, ASTS, ... | Pre-profit, speculative |

#### 3. Fundamentals Comparison Table

One row per ticker, sorted by dashboard composite score (highest first). **Links point to .md files** (individual tickers are .md only).

| Ticker | Sector | Price | 52wk Range | MCap | P/E | Fwd P/E | EV/EBITDA | EV/Sales | Vol | Valuation Range | Signal | Dashboard | Report |
|--------|--------|-------|-----------|------|-----|---------|-----------|----------|-----|-----------------|--------|-----------|--------|
| BKNG | TRAVEL | $171 | $120–$195 | $133B | 19.1x | 13.9x | 12.7x | 4.7x | 33% | $120–$171–$240 | 🟢 Entry | 7.6/10 | [→](BKNG/BKNG_YYYY-MM-DD.md) |

**Valuation Range column:** Shows `$Bear–$Current–$Bull` from each ticker's Executive Summary valuation range bar. Format: `$BEAR–$CURRENT–$BULL`. If the current price is below bear, prefix with ⬇️. If above bull, prefix with ⬆️.

**52wk Range column:** Shows `$Low–$High` (52-week low and high) from each ticker's Company Fundamentals section.

**Signal column:** Entry/exit recommendation from each ticker's Company Fundamentals section. One of: 🟢 Entry, 🟡 Hold, 🔴 Exit.

**Rules:**
- Links use `.md` extension — individual tickers are generated as .md only
- All 20 tickers must be present — no omissions
- Data source: read each ticker's research packet JSON and individual .md report (for valuation range). Do NOT re-derive.
- Valuation Range: extract bear/bull values from the ASCII valuation bar in each ticker's Executive Summary section

#### 5. Sector Grouping

Group tickers by sector. Within each sector, show ALL tickers — do not omit any ticker from its own sector table. Median is computed from ALL tickers in the sector group.

```markdown
### TRAVEL-SPACE (3 tickers)
| Ticker | P/E | vs Median | Fwd P/E | vs Median | Dashboard |
|--------|-----|-----------|---------|-----------|-----------|
| RKLB   | N/A | —         | 1398x   | +1311x    | 4.0/10    |
| SPCX   | N/A | —         | 86.6x   | —         | 4.5/10    |
| ASTS   | N/A | —         | -46x    | -133x     | 3.0/10    |
| **Median** | — | —      | 86.6x   | —         | 4.0       |
```

#### 4. Explore These Next (same-sector, not in batch)

**Comes before Sector Grouping** — the user sees "what else to look at" before the detailed per-sector breakdown.

**Purpose:** For each batch ticker, show 2-3 tickers from the same sector that are NOT in the 19-ticker batch, with fundamentals compared against the batch ticker as benchmark.

**Rules:**
1. Explore tickers MUST be from the **same sector** (per `config/tickers.yaml` sectors section)
2. Explore tickers MUST NOT be any of the 19 batch tickers
3. Each explore group is a **multi-row sub-table grouped by the batch ticker**
4. The batch ticker's fundamentals appear as the **benchmark row** (bolded), and each explore ticker shows its own fundamentals alongside for direct comparison

**Format — multi-row grouped table:**

```markdown
### SNPS (EDA) — Explore: CDNS

| Ticker | Price | MCap | Fwd P/E | EV/EBITDA | EV/Sales | Vol | Note |
|--------|-------|------|---------|-----------|----------|-----|------|
| **SNPS (benchmark)** | **$378** | **$73B** | **21.6x** | **37.4x** | **8.3x** | **37%** | **In batch** |
| CDNS | — | ~$80B | ~25x | ~35x | ~15x | ~30% | Duopoly partner; similar margin profile |

### VRT (DATACENTER-INFRA) — Explore: CARR, ETN, PWR

| Ticker | Price | MCap | Fwd P/E | EV/EBITDA | EV/Sales | Vol | Note |
|--------|-------|------|---------|-----------|----------|-----|------|
| **VRT (benchmark)** | **$239** | **$92B** | **26.2x** | **33.8x** | **7.9x** | **56%** | **In batch** |
| CARR | — | ~$70B | ~25x | ~20x | ~4x | ~30% | HVAC/thermal peer, lower growth premium |
| ETN | — | ~$130B | ~28x | ~22x | ~5x | ~25% | Power mgmt, similar datacenter exposure |
| PWR | — | ~$45B | ~30x | ~18x | ~2x | ~35% | Infrastructure services, different model |
```

**Data for explore tickers:** Since explore tickers are NOT in the batch (no research packet), use approximate fundamentals from the `config/tickers.yaml` sector context or note "data not available — research recommended." The point is to show the batch ticker's numbers as a benchmark and flag the explore tickers for future research.

**If a sector has NO other tickers beyond the batch ticker(s):**

```markdown
### QURE (MISC) — No additional tickers in sector
| Ticker | Price | MCap | Fwd P/E | EV/EBITDA | EV/Sales | Vol | Note |
|--------|-------|------|---------|-----------|----------|-----|------|
| **QURE (benchmark)** | **$42** | **$3B** | **-14.0x** | **-14.9x** | **146.3x** | **96%** | **In batch — sole sector member** |
```

Read the `sectors:` section of `config/tickers.yaml` to find sector members. The explore suggestions are sector members NOT in the weekly batch.

#### 6. Best/Worst Table

| Category | Ticker | Value | Note |
|----------|--------|-------|------|
| Cheapest (Fwd P/E) | EXPE | 11.7x | Travel recovery play |
| Most Expensive (Fwd P/E) | RKLB | 1398x | Space, pre-scale |
| Highest FCF Yield | EXPE | 9.0% | Cash machine |
| Best Dashboard | BKNG | 7.6/10 | Quality + value |
| Worst Dashboard | IONQ | 2.8/10 | Quantum, pre-revenue |
| Most Volatile | IREN | 115% | AI infra, max drawdown 99% |
| Least Volatile | BKNG | 33% | Established travel |

**HTML rendering:** Same v3 CSS as individual reports. Sticky nav, sortable tables (add `onclick` sort for each column header), links to individual reports open in same directory. No ECharts needed — tables are the primary visualization.

**Trigger:** The master report is generated AFTER the `batch_end` event confirms all tickers succeeded. If some tickers failed, generate the master with available data and note the missing tickers.

**Link validation (mandatory before committing):** After generating the master, verify that EVERY linked file actually exists:

```bash
# Run from the reports/ directory
cd .notlocal/data/personal-investor/reports
for link in $(grep -oP '\]\(\K[^)]+\.md' YYYY-MM-DD-master.md); do
  if [ ! -f "$link" ]; then echo "BROKEN: $link"; fi
done
```

If ANY link is broken, the master report is WRONG — do not commit it. Individual tickers are `.md` only; only the master report itself has both `.md` and `.html` versions.

#### 7. Appendix: How the Numbers Work — Using EXPE

**The entire appendix uses ONE real ticker's numbers.** No fictional "Acme Corp" — every definition, formula, and worked example uses EXPE's actual financials from the current batch. This makes the appendix a single coherent reference where the reader follows one company from start to finish.

**Ticker selection:** Use the most "textbook" profitable ticker in the batch — one with positive earnings, positive FCF, reasonable multiples, and enough data to compute all metrics. EXPE is the default; if EXPE is removed from a future batch, substitute BKNG or VRT.

**Structure:** Every glossary term gets a one-line definition followed by the computation using EXPE's real numbers. Group by category (same 7 categories as `config/glossary.md`). Then add the three SOP v2 computation chains at the end.

```markdown
## Appendix: How the Numbers Work — EXPE (Expedia Group)

**Reference numbers (from research packet):**
> Price = $287 | Shares = 120M | Revenue (TTM) = $14.73B | Net Income (TTM) = $1.86B
> EBITDA = $2.89B | FCF = $3.11B | OCF = $4.35B | CapEx = $1.24B | Total Debt = $8.7B
> Cash = $3.7B | Equity = ~$3.8B | EPS = $15.86 | Market Cap = $34.4B | EV = $39.4B
> SBC (est.) = ~$700M | Fwd EPS (est.) = $24.50

### 1. Valuation Metrics
**P/E** = Price ÷ EPS = $287 ÷ $15.86 = **18.1x**
**Forward P/E** = Price ÷ Fwd EPS = $287 ÷ $24.50 = **11.7x**
**EV/EBITDA** = EV ÷ EBITDA = $39.4B ÷ $2.89B = **13.6x**
**EV/Sales** = EV ÷ Revenue = $39.4B ÷ $14.73B = **2.7x**
**FCF Yield** = FCF ÷ Market Cap = $3.11B ÷ $34.4B = **9.0%**
[... all 34 terms computed with EXPE numbers ...]

### SOP v2 Computations

#### Earnings Quality
- Reported EPS: $15.86 → P/E = 18.1x
- SBC: ~$700M → SBC/share = $5.83 → Adjusted EPS = $10.03 → Adj P/E = 28.6x
- Delta: 10.5x — this is the hidden cost of SBC

#### Reverse DCF
- EV = $39.4B, FCF = $3.11B, WACC = 10%, terminal = 2.5%
- Market implies ~1% annual FCF growth for 5 years
- Historical: ~8-12% → stock is priced for near-zero growth (potential upside)

#### SBC-Adjusted FCF
- FCF $3.11B − SBC $0.70B = Adjusted FCF $2.41B
- Yield: 9.0% reported → 7.0% adjusted (still strong)
```

**Implementation:** Do NOT use `config/glossary.md` (which has Acme Corp). Instead, generate the glossary content fresh each week using the selected ticker's actual numbers from its research packet JSON. The 34 term definitions stay the same; only the numbers change.

**In HTML:** Render inside a `<details open>` collapsible section with nav bar link "How It Works".

**Style guide:** Follow `config/report-style-guide.md` for all formatting decisions (header blocks, evidence labels, table alignment, HTML CSS, color-coding, link extensions). The style guide is the formatting source of truth — this SKILL.md defines *what* to include; the style guide defines *how* it looks.

### Pre-commit checklist (mandatory — do NOT commit until ALL pass)

Before committing any weekly batch output, verify ALL of the following exist:

```bash
REPORT_DATE="YYYY-MM-DD"  # the Sunday date

# 1. Every ticker has BOTH .json AND .md
for t in $(cat config/weekly-batch.yaml | grep '^ *- ' | sed 's/.*- //'); do
  [ ! -f "reports/$t/${t}_${REPORT_DATE}.json" ] && echo "MISSING JSON: $t"
  [ ! -f "reports/$t/${t}_${REPORT_DATE}.md" ] && echo "MISSING MD: $t"
done

# 2. Master .md exists
[ ! -f "reports/${REPORT_DATE}-master.md" ] && echo "MISSING: master .md"

# 3. Master .html exists
[ ! -f "reports/${REPORT_DATE}-master.html" ] && echo "MISSING: master .html"
```

**If ANY file is missing, do NOT commit.** Generate the missing file first.

The most common failures:
- Master .html not generated (agent wrote .md but nobody generated .html)
- Individual .html not generated (Stage 2 only produced .md)
- Master .md links to .html files that don't exist

**This checklist is the final gate.** No exceptions.

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
- [Appendix: What Changed](#what-changed)
- [Appendix: Glossary](#glossary)

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
