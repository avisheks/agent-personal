# Options PnL Summarizer — Operating Instructions

## Role

Computes realized PnL for **Cash-Secured Puts (CSP) and Covered Calls (CC) only** across three brokerage accounts (Fidelity, Tastytrade, Thinkorswim). Produces a consolidated report with monthly/weekly breakdowns, trendline charts, and trade-level detail.

## Data Requirements for Wheel Tracking

For complete wheel PnL (premium + stock capital gains), the input data must include **both option trades AND stock transactions** for each broker. If only option order fills are available, the report will correctly compute premium PnL but will be missing stock capital gains from the wheel.

### Required Data by Broker

| Broker | Option Trades | Stock Assignments & Sales | Status |
|--------|--------------|--------------------------|--------|
| **Thinkorswim** | Account Statement CSV (new format includes "Assigned" + "Buy"/"Sell" entries) | Included in same file | Complete |
| **Fidelity** | History CSV (includes "EXPIRED" entries) | Not currently provided - need transaction history with stock buys/sells | Partial |
| **Tastytrade** | Order History CSV (STO/BTC fills only) | **NOT included** - need the "Transaction History" export (includes `Receive Deliver` type for assignments and `Trade`/`Equity` type for stock sales) | Incomplete |

### Tastytrade: Two Files Required

The Tastytrade data requires **two separate exports** per date range:

1. **Order History** (fills): `tastytrade_transactions_history_x*_YYMMDD_to_YYMMDD.csv`
   - Contains option STO/BTC fills with prices
   - Format: `Symbol, Status, MarketOrFill, Price, TIF, Time, TimeStampAtType, Order #, Description`
   - Provides: premium prices, fill dates, order IDs for spread detection

2. **Transaction History (assignments)**: `tastytrade_transactions_history_x*_YYMMDD_to_YYMMDD__assignments.csv`
   - Contains `Receive Deliver` entries for assignments and expirations
   - Format: `Date, Type, Sub Type, Action, Symbol, Instrument Type, Description, Value, Quantity, ...`
   - Provides: which options were assigned vs. expired, enabling wheel capital gain tracking
   - `Sub Type = "Assignment"` → stock was acquired (PUT) or called away (CALL)
   - `Sub Type = "Expiration"` → option expired worthless (no stock movement)

**Both files are required.** Without the assignments file:
- The system cannot distinguish assigned CSPs from expired CSPs
- Wheel capital gains from Tastytrade will be completely missing
- The system will flag this as a warning during execution

### Missing File Detection

When running `compute_pnl.py`, the system checks for the presence of an assignments file in `inp/tasty/`. If no file matching `*__assignments.csv` is found:
- Print a WARNING: "No Tastytrade assignments file found. Wheel capital gains from Tastytrade will be incomplete."
- Continue execution (premium PnL will still be computed correctly)
- The report will note the data gap in the Excluded Trades section

## Strategy Definitions

| Strategy | Open | Close | Identified by |
|----------|------|-------|---------------|
| **Cash-Secured Put (CSP)** | Sell to Open PUT | Buy to Close, expires worthless, or assignment | `Sell to Open` + `PUT` (not part of a spread) |
| **Covered Call (CC)** | Sell to Open CALL | Buy to Close, expires worthless, or assignment | `Sell to Open` + `CALL` (not part of a spread) |

**Excluded (not analyzed):**
- Long options (Buy to Open)
- Spread legs (detected via shared order ID or timestamp proximity)
- Stock trades (listed for reference, no PnL computed)
- Unclosed positions (only realized PnL is reported)

## Directory Structure

```
agent-personal/
├── src/
│   ├── parsers.py         # Broker-specific CSV parsers
│   ├── matcher.py         # Trade filtering, spread detection, FIFO matching, PnL math
│   ├── compute_pnl.py     # Main compute entry point → outputs JSON
│   └── render_report.py   # Reads JSON → generates .md and .html reports
├── tst/
│   └── test_parsers.py    # Unit and integration tests
├── skills/
│   └── options-pnl.md     # This file
└── .local/options-pnl/
    ├── inp/
    │   ├── fidelity/      # Fidelity transaction CSVs
    │   ├── tasty/         # Tastytrade transaction CSVs
    │   └── thinknswim/    # Thinkorswim account statement CSVs
    └── out/               # Generated reports + backups
```

## How to Run

```bash
cd agent-personal

# Phase 1: Compute (deterministic, ~2 seconds)
python3 src/compute_pnl.py --input .local/options-pnl/inp --output .local/options-pnl/out/computed-pnl.json

# Phase 2: Validate (compare against reference, ~1 second)
python3 src/validate_pnl.py \
    --computed .local/options-pnl/out/computed-pnl.json \
    --reference ".local/options-pnl/ref/[Options] Ultimate Options Tracking Spreadsheet - Version 2 - Q12026.xlsx" \
    --output .local/options-pnl/out/validation-report.json

# Phase 3: Render (generates .md + .html, backs up prior reports)
# Only run after validation passes or discrepancies are understood
python3 src/render_report.py --input .local/options-pnl/out/computed-pnl.json --output-dir .local/options-pnl/out
```

All three phases run sequentially. Phase 1 does parsing and arithmetic. Phase 2 catches errors before publishing. Phase 3 generates the final report.

### Phase 2: Validation Details

`validate_pnl.py` compares computed output against a manually-maintained reference spreadsheet (ground truth):

- **Compares at three levels:** total PnL, monthly totals, and individual trade matching
- **Trade matching:** exact match on (broker, ticker, strategy, strike, qty, close date), then fuzzy match without date
- **Tolerance:** $5 per trade (accounts for rounding, fee differences)
- **Exit code:** 0 = PASS, 1 = FAIL (discrepancies found)
- **Output:** prints a human-readable report to stdout; optionally writes JSON to `--output`

**When validation fails:** Investigate before rendering. Common causes:
- Parser not handling a new CSV format variant
- Spread detection incorrectly excluding a standalone CSP/CC
- Cross-month matching failure (position opened in a month without available data)
- Reference spreadsheet includes BPS (Bull Put Spreads) that should be excluded

**Reference file location:** `.local/options-pnl/ref/` (xlsx format, manually maintained)

## Backup Before Overwrite

Before generating new reports, `render_report.py` automatically backs up existing `-latest` reports:

```
pnl-report-latest.md  →  pnl-report-YYYY-MM-DD-HH.md
pnl-report-latest.html  →  pnl-report-YYYY-MM-DD-HH.html
```

Suffix uses current date and hour (24h). If no prior `-latest` reports exist, the backup step is skipped silently.

## Output Files

| File | Description |
|------|-------------|
| `computed-pnl.json` | Structured data (all trades, aggregations, weekly/monthly breakdowns) |
| `validation-report.json` | Trade-level comparison against reference (discrepancies, matches, missing) |
| `pnl-report-latest.md` | Current Markdown report (always at this predictable path) |
| `pnl-report-latest.html` | Current styled HTML with ECharts visualizations |
| `pnl-report-YYYY-MM-DD-HH.*` | Timestamped backups of prior runs |

## PnL Scope

The report computes **full wheel PnL** which includes:

1. **Option premium PnL** — credit received at open minus debit paid at close (CSP and CC)
2. **Stock wheeling capital gains** — for stocks acquired via CSP assignment ONLY, the gain/loss when the stock is subsequently sold (either via CC assignment/call-away or a direct stock sale)

Stocks purchased independently (not via CSP assignment) are excluded from PnL. The system links CSP assignments to subsequent stock dispositions by matching (broker, ticker, assignment date to sale date) using FIFO.

### Wheel Lifecycle Tracking

A complete wheel cycle:
- CSP sold → assigned → stock acquired at strike → CC sold on stock → stock called away (or sold)
- Total PnL = CSP premium + CC premium(s) + (stock sale price - stock acquisition cost) x qty

The system tracks partial wheels too:
- CSP assigned but stock not yet sold → stock acquisition recorded, no capital gain PnL yet
- Stock sold without prior CC → capital gain still included (stock was acquired via assignment)

## Report Contents

The report is organized into a main body and two appendices:

### Main Body (Full PnL)

**Headline metrics (dashboard cards at top):**
- Total Full PnL (premium + capital gains)
- Total Trades (options + stock sales)
- Overall Win Rate
- Avg PnL/Trade

Followed by:
1. **Top 3 Winners / Bottom 3 Losers** — highlight cards
2. **Monthly summary** — all brokers combined, then per broker (includes both premium and capital gains)
3. **Charts** (HTML only, ECharts):
   - Cumulative PnL with drawdown shading
   - Monthly PnL waterfall
   - Weekly net PnL bars (green/red)
   - Cumulative PnL by broker (multi-line)
   - PnL distribution histogram
   - Days held vs PnL scatter (CSP vs CC)
   - Calendar heatmap (daily PnL intensity)
   - Broker allocation donut
   - Win/loss streak
   - **Ticker x Month PnL heatmap** (top 15 active tickers as rows, months as columns, color intensity = net PnL; green = profit, red = loss)
   - **Broker x Strategy PnL matrix** (3x2 grid showing PnL for each broker/strategy combination; compact dashboard widget)
   - **Holding Period x PnL Outcome matrix** (rows = hold period buckets [1-7d, 8-14d, 15-30d, 31+d], columns = outcome buckets [loss >$200, small loss, breakeven, small win, win >$200], cell = trade count with color intensity)
4. **Strategy breakdown** — CSP vs CC vs Wheel Capital Gains
5. **PnL by underlying** — top 10 (best) and bottom 10 (worst) tickers by net PnL
6. **All closed trades** — collapsible detail table (collapsed by default in HTML via `<details>` element)
7. **Excluded trades** — counts with reasons

### Appendix A: CSP/CC Premium Only

**Headline metrics (dashboard cards at top of appendix):**
- Net Premium PnL
- Total Option Trades
- Win Rate

Followed by:
- Premium-only summary table
- Reference to main body for full trade detail

### Appendix B: Stock Wheeling Capital Gains

**Headline metrics (dashboard cards at top of appendix):**
- Total Capital Gains
- Wheel Cycles Completed
- Avg Hold Period (days)

Followed by the detail table:

| Date Sold | Broker | Ticker | Qty | Acquisition Price | Sale Price | Capital Gain | Assignment Date | Days Held |
|-----------|--------|--------|-----|-------------------|------------|--------------|-----------------|-----------|

## HTML Styling

- Light theme only (white background, gray headers, no dark mode)
- System font stack (Inter, -apple-system, sans-serif)
- ECharts via CDN for all visualizations
- Green (#22c55e) for positive PnL, red (#ef4444) for negative
- Sticky navigation bar with section anchors
- Sortable detail table (click column headers)
- Responsive layout, print-friendly

## Source Code Reference

Implementation details (parsing logic, FIFO matching, spread detection algorithms) live in the Python source files. The code is the source of truth:

| File | What it does |
|------|-------------|
| `src/parsers.py` | Reads each broker's CSV format, normalizes to a common trade dict |
| `src/matcher.py` | Filters CSP/CC, detects spreads by order ID or timestamp, matches opens to closes via FIFO, computes PnL per closed position |
| `src/compute_pnl.py` | Orchestrates: reads all files, calls parsers and matcher, aggregates by month/week/broker/underlying/strategy, writes JSON |
| `src/validate_pnl.py` | Compares computed JSON against reference xlsx; reports matched, mismatched, missing, and extra trades |
| `src/render_report.py` | Reads JSON, generates .md tables and .html with charts, handles backup |
| `tst/test_parsers.py` | Unit tests for parsing, filtering, and matching; integration test on real data |

## Adding a New Broker

To support a new brokerage:
1. Add a parser function in `src/parsers.py` that returns the same normalized trade dict format
2. Add the broker's directory scan in `src/compute_pnl.py`
3. Add tests in `tst/test_parsers.py`
4. Add a color for the broker in `src/render_report.py` (for chart lines)
