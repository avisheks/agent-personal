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

### Known Limitation: Spread Detection in Tastytrade Order History Format

The Tastytrade **Order History** format (`Symbol, Status, MarketOrFill, Price, TIF, Time, ...`) encodes multi-leg orders as a single row with a multi-line Description field (e.g., `"-5 Feb 27 Exp 430 Put STO\n5 Feb 27 Exp 420 Put BTO"`). The parser extracts individual legs from these descriptions but **does not currently mark them as spread legs**.

As a result, the short leg of a spread (the STO side) is parsed identically to a standalone CSP/CC. If a matching BTC exists in the data, it forms a "closed trade" and its premium PnL is included in the report.

**Impact:** ~19 trades in the Jan–Jun 2026 period are short legs of spreads (Bull Put Spreads, Bear Call Spreads) reported as standalone CSPs/CCs. Net PnL impact: approximately -$625. These same trades appear in the manually-verified reference spreadsheet, so the pipeline correctly reproduces the reference.

**Affected tickers (Jan–Jun 2026):** APP, BABA, GOOG, LLY, MSFT, AMD, GE, SPOT, SLV, LULU

**Fix applied (2026-08-08):** The parser now detects multi-leg Description fields (containing both `STO` and `BTO`, or both `BTC` and `STC`) and skips the entire order. This correctly excludes spread legs from the CSP/CC report.

**Note:** This fix means computed results will diverge from reference reports created before this fix. When Phase 5 validation fails because the reference included spread legs, override with: "Reference includes spread legs that are now correctly excluded. Spread-leg exclusion is the correct behavior per SOP strategy definitions."

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
│   └── personal-options-pnl.md     # This file
└── .local/options-pnl/
    ├── inp/
    │   ├── fidelity/      # Fidelity transaction CSVs
    │   ├── tasty/         # Tastytrade transaction CSVs
    │   └── thinknswim/    # Thinkorswim account statement CSVs
    └── out/               # Generated reports + backups
```

## Report Versioning Rules

**NEVER overwrite an existing report.** Instead:

1. When a report file already exists at the target path, rename the existing file by appending a version suffix: `-v0`, `-v1`, `-v2`, etc. (use the next available version number).
2. The **most recent** (current) report always gets the `-latest` suffix.
3. When generating a new report that would conflict with an existing `-latest` file:
   - Rename the current `-latest` file to the next version number (e.g., `-latest` → `-v1`)
   - Write the new report with the `-latest` suffix

**Example progression:**
```
# First report generated:
pnl-report-20260112_to_20260630-latest.md

# Second run produces an updated report for the same date range:
pnl-report-20260112_to_20260630-v0.md      ← (was -latest, now versioned)
pnl-report-20260112_to_20260630-latest.md   ← (new, current)

# Third run:
pnl-report-20260112_to_20260630-v0.md
pnl-report-20260112_to_20260630-v1.md      ← (was -latest, now versioned)
pnl-report-20260112_to_20260630-latest.md   ← (new, current)
```

**Naming convention:** `pnl-report-YYYYMMDD_to_YYYYMMDD-{version}.{md,html}` where:
- Dates represent the earliest and latest trade close dates in the dataset
- Version is either `-latest` (current) or `-v0`, `-v1`, `-v2`, etc. (historical)

## How to Run

The pipeline has **six phases** organized into two stages: a **validation stage** (Phases 1–3) that confirms the SOP and data are correct, followed by the **production stage** (Phases 4–6) that generates the final report.

### User-Provided Inputs

Before running, the user MUST provide three inputs. If any are missing from the user's request, **STOP and ask** before proceeding. Use the prompt template below.

| Symbol | What it is | Why it's needed |
|--------|-----------|-----------------|
| **VAL_DATA** | Path to a directory of broker CSVs for a **prior period** that has already been validated against a known-correct report. | Used in Phase 1 to confirm the pipeline still works correctly — acts as a regression test before processing new data. |
| **VAL_REPORT** | Path to the **reference report** (xlsx) that was produced from VAL_DATA and manually verified as correct. | The ground truth for Phase 1 cross-checking and Phase 5 combined-output validation. |
| **INP_DATA** | Path to a directory of broker CSVs for the **new period** you want to generate a report for. | The new data to be processed. Phase 2 validates its format; Phase 3 computes it standalone; Phases 4–6 combine it with VAL_DATA for the final report. |

#### Prompt Template (use when parameters are missing)

If the user asks to run this SOP but does not specify all three inputs, ask:

> To run the Options PnL pipeline I need three things:
>
> 1. **VAL_DATA** — Where are the broker CSVs for a period you've already validated?
>    This is the "known-good" dataset I'll use to confirm the pipeline is working before touching new data.
>    *(Example: `.local/options-pnl/inp/` with your Jan–Mar 2026 Fidelity/Tasty/ToS files)*
>
> 2. **VAL_REPORT** — Where is the reference report (xlsx) for that same period?
>    This is the manually-verified ground truth I'll compare against to confirm correctness.
>    *(Example: `.local/options-pnl/ref/[Options] Ultimate Options Tracking Spreadsheet - Version 2 - Q12026.xlsx`)*
>
> 3. **INP_DATA** — Where are the broker CSVs for the new period you want reported?
>    These are the new trades I'll validate, compute, and merge into the final report.
>    *(Example: a new directory with Apr–Jun 2026 exports from each broker)*
>
> All three paths can be directories or files. For Tastytrade, remember both the Order History and the assignments CSV are needed in each directory (see the two-file requirement above).

---

### Stage 1: Validation (Phases 1–3)

#### Phase 1: SOP Self-Validation

**Purpose:** Confirm the pipeline (parsers, matcher, compute, render) produces correct output by re-running it on known data and cross-checking against the known reference.

```bash
cd agent-personal

# 1a. Compute PnL from VAL_DATA
python3 src/compute_pnl.py --input <VAL_DATA_DIR> --output .local/options-pnl/out/val-computed-pnl.json

# 1b. Validate computed output against VAL_REPORT
python3 src/validate_pnl.py \
    --computed .local/options-pnl/out/val-computed-pnl.json \
    --reference "<VAL_REPORT_PATH>" \
    --output .local/options-pnl/out/val-validation-report.json

# 1c. Render report from VAL_DATA (for visual comparison)
python3 src/render_report.py --input .local/options-pnl/out/val-computed-pnl.json --output-dir .local/options-pnl/out/val
```

**Gate:** Phase 1 MUST pass (exit code 0 from validate_pnl.py, or all discrepancies explained) before proceeding. If validation fails:
- Investigate discrepancies (parser changes, spread detection issues, format drift)
- Fix the source code
- Re-run Phase 1 until it passes

**Outcome:** Confidence that the SOP/pipeline is working correctly for the data formats in use.

---

#### Phase 2: Data-Format Validation

**Purpose:** Ensure INP_DATA has the correct format, structure, and completeness to produce a report equivalent in quality to VAL_REPORT. Uses VAL_DATA as the format reference.

```bash
cd agent-personal

# 2a. Inspect VAL_DATA structure (columns, date ranges, broker coverage)
python3 src/compute_pnl.py --input <VAL_DATA_DIR> --dry-run --output .local/options-pnl/out/val-data-schema.json

# 2b. Inspect INP_DATA structure
python3 src/compute_pnl.py --input <INP_DATA_DIR> --dry-run --output .local/options-pnl/out/inp-data-schema.json
```

If `--dry-run` is not implemented, perform the validation manually by checking:

1. **File presence:** For each broker directory in VAL_DATA, confirm INP_DATA has a corresponding directory with at least one CSV file. Specifically:
   - `fidelity/` — at least one History CSV
   - `tasty/` — Order History CSV + assignments CSV (both required, per the Tastytrade two-file rule above)
   - `thinknswim/` — at least one Account Statement CSV

2. **Column schema:** Parse the header row of each INP_DATA file and confirm all required columns from VAL_DATA are present (order may differ but names must match).

3. **Date range continuity:** Confirm INP_DATA covers a contiguous period that starts at or after VAL_DATA's end date (no gaps, no overlap unless intentional).

4. **Content sanity:** Confirm INP_DATA contains `Sell to Open` entries (i.e., there are actual CSP/CC trades to report on).

5. **Deduplication check:** Hash each row by `(Date, Symbol, Order#, Action, Value)` across all input files. WARN if any duplicates are detected — overlapping date ranges across files will cause double-counting. Remove or exclude duplicates before proceeding.

6. **Broker coverage gap detection:** If VAL_DATA has data from broker X but INP_DATA does not, flag it explicitly: "WARNING: No [Broker] data provided for [period]. Report will be incomplete for this broker."

**Gate:** ALL checks must pass. If any fail:
- Report which check failed and what is missing/malformed
- Ask the user to provide corrected INP_DATA
- Do NOT proceed to Phase 3 until all checks pass

**Outcome:** Confidence that INP_DATA will produce a complete, well-formed report.

---

#### Phase 3: Compute & Validate INP_DATA

**Purpose:** Run the pipeline on INP_DATA alone to confirm it produces valid output before combining with VAL_REPORT.

```bash
cd agent-personal

# 3a. Compute PnL from INP_DATA
python3 src/compute_pnl.py --input <INP_DATA_DIR> --output .local/options-pnl/out/inp-computed-pnl.json

# 3b. Render INP_DATA report (standalone, for inspection)
python3 src/render_report.py --input .local/options-pnl/out/inp-computed-pnl.json --output-dir .local/options-pnl/out/inp-preview
```

**Gate:** Compute must succeed without errors. Review the preview report for obvious anomalies (negative trade counts, impossible PnL values, missing brokers expected from Phase 2).

---

### Stage 2: Production (Phases 4–6)

#### Phase 4: Combined Compute

**Purpose:** Generate the final combined dataset that includes all trades from VAL_DATA's period plus INP_DATA's period.

```bash
cd agent-personal

# 4a. Compute PnL from BOTH input sets combined
python3 src/compute_pnl.py \
    --input <VAL_DATA_DIR> --input <INP_DATA_DIR> \
    --output .local/options-pnl/out/computed-pnl.json
```

If `--input` does not support multiple directories, copy/symlink all broker CSVs from both VAL_DATA and INP_DATA into a single combined input directory first:

```bash
# Create combined input directory
mkdir -p .local/options-pnl/inp-combined/{fidelity,tasty,thinknswim}
cp <VAL_DATA_DIR>/fidelity/* .local/options-pnl/inp-combined/fidelity/
cp <VAL_DATA_DIR>/tasty/* .local/options-pnl/inp-combined/tasty/
cp <VAL_DATA_DIR>/thinknswim/* .local/options-pnl/inp-combined/thinknswim/
cp <INP_DATA_DIR>/fidelity/* .local/options-pnl/inp-combined/fidelity/
cp <INP_DATA_DIR>/tasty/* .local/options-pnl/inp-combined/tasty/
cp <INP_DATA_DIR>/thinknswim/* .local/options-pnl/inp-combined/thinknswim/

python3 src/compute_pnl.py --input .local/options-pnl/inp-combined --output .local/options-pnl/out/computed-pnl.json
```

**CRITICAL: Deduplication.** When combining directories, ensure no CSV file appears twice (e.g., a June-only file alongside a full Jan-Jun file that contains the same June data). Before running compute:
- List all CSVs that will be processed
- Verify no overlapping date ranges for the same broker
- If overlap exists, use only the superset file and exclude the subset

---

#### Phase 5: Validate Combined Output

**Purpose:** Cross-check the combined output against VAL_REPORT to ensure the previously-validated data is still correctly represented in the combined report.

```bash
cd agent-personal

python3 src/validate_pnl.py \
    --computed .local/options-pnl/out/computed-pnl.json \
    --reference "<VAL_REPORT_PATH>" \
    --output .local/options-pnl/out/validation-report.json
```

**Gate:** All trades from VAL_REPORT's period must match (within $5 tolerance). New trades from INP_DATA will appear as "extra" — this is expected and correct. Only mismatches or missing trades from the reference period indicate a problem.

**Additional assertions (run programmatically):**

1. **Arithmetic consistency:**
   - Sum of all monthly trade counts = total closed trade count
   - Sum of all broker-monthly trade counts = total closed trade count
   - Sum of strategy trades (CSP + CC) = total closed trade count
   - Sum of individual `net_pnl` values = reported total net PnL (within $0.01)
   - `gross_pnl - fees = net_pnl` for every individual trade

2. **Cross-section totals:**
   - Sum of broker "Total" net PnLs = overall total net PnL
   - Sum of strategy net PnLs = overall total net PnL

3. **Win/loss count matches:**
   - Count of trades with `net_pnl > 0` = reported winning trades
   - Count of trades with `net_pnl <= 0` = reported losing trades
   - `winning + losing = total trades`

4. **Wheel capital gain formula verification:**
   - For each wheel trade: `capital_gain = (sale_price - acquisition_price) * qty`
   - `acquisition_price` matches the strike of an assigned CSP for the same (broker, ticker)

5. **Excluded trades consistency:**
   - Excluded counts must reflect the FULL input set (all brokers, all files)
   - If excluded counts are zero for categories that historically have entries, flag as WARNING

---

#### Phase 6: Render Final Report

**Purpose:** Generate the combined report. Apply versioning rules (never overwrite).

```bash
cd agent-personal

# Determine date range from the combined data
# START_DATE = earliest trade close date across all data
# END_DATE = latest trade close date across all data
# Format: YYYYMMDD

python3 src/render_report.py \
    --input .local/options-pnl/out/computed-pnl.json \
    --output-dir .local/options-pnl/out
```

After rendering, apply versioning:
```bash
# Target filename
TARGET="pnl-report-<START_DATE>_to_<END_DATE>"

# If -latest already exists, version it
if [ -f ".local/options-pnl/out/${TARGET}-latest.md" ]; then
    # Find next version number
    N=0
    while [ -f ".local/options-pnl/out/${TARGET}-v${N}.md" ]; do N=$((N+1)); done
    mv ".local/options-pnl/out/${TARGET}-latest.md" ".local/options-pnl/out/${TARGET}-v${N}.md"
    mv ".local/options-pnl/out/${TARGET}-latest.html" ".local/options-pnl/out/${TARGET}-v${N}.html"
fi

# Move the new report to -latest
mv .local/options-pnl/out/pnl-report-latest.md ".local/options-pnl/out/${TARGET}-latest.md"
mv .local/options-pnl/out/pnl-report-latest.html ".local/options-pnl/out/${TARGET}-latest.html"
```

**Outcome:** A versioned report that preserves all prior runs and makes the current version clearly identifiable.

---

### Quick Reference: Full Pipeline

```bash
cd agent-personal

# --- Stage 1: Validation ---
# Phase 1: SOP self-validation
python3 src/compute_pnl.py --input <VAL_DATA_DIR> --output .local/options-pnl/out/val-computed-pnl.json
python3 src/validate_pnl.py --computed .local/options-pnl/out/val-computed-pnl.json --reference "<VAL_REPORT_PATH>" --output .local/options-pnl/out/val-validation-report.json

# Phase 2: Data-format validation (manual inspection + dedup check)

# Phase 3: Compute & validate INP_DATA standalone
python3 src/compute_pnl.py --input <INP_DATA_DIR> --output .local/options-pnl/out/inp-computed-pnl.json

# --- Stage 2: Production ---
# Phase 4: Combined compute (with dedup guard)
python3 src/compute_pnl.py --input .local/options-pnl/inp-combined --output .local/options-pnl/out/computed-pnl.json

# Phase 5: Validate combined + run assertions
python3 src/validate_pnl.py --computed .local/options-pnl/out/computed-pnl.json --reference "<VAL_REPORT_PATH>" --output .local/options-pnl/out/validation-report.json

# Phase 6: Render + version
python3 src/render_report.py --input .local/options-pnl/out/computed-pnl.json --output-dir .local/options-pnl/out
# (apply versioning script above)
```

---

## Post-Render Validation Checklist

After generating a report, run these checks before delivering to the user:

### Mandatory Assertions (FAIL = do not deliver)

- [ ] Sum of monthly trades = total closed trades
- [ ] Sum of broker-monthly trades = total closed trades
- [ ] Sum of individual net_pnl = reported total (within $0.01)
- [ ] `gross_pnl - fees = net_pnl` for every trade
- [ ] Win count + Loss count = Total trades
- [ ] CSP net + CC net = Total premium net
- [ ] Sum of broker totals = Overall total
- [ ] Wheel: `capital_gain = (sale_price - acquisition_price) * qty` for each
- [ ] **No inferred closures** — every trade with `close_price = 0` must have a matching EXPIRED or ASSIGNED entry in the input data
- [ ] **Independent spread detection** (see below)

### No Inferred Closures (only report what the data explicitly confirms)

A trade is closed ONLY when there is explicit evidence in the input data:
- A BTC (Buy to Close) fill matching the STO
- An EXPIRED entry (Receive Deliver / Expiration)
- An ASSIGNED entry (Receive Deliver / Assignment)

**NEVER infer expiry from the current date.** If an STO has a past expiry date but no matching close/expiration/assignment entry in the data, it MUST remain unmatched (open/unresolvable). The absence of a close record does NOT mean it expired — it could have been:
- Bought to close (BTC data in a file we don't have)
- Assigned (assignment data in a file we don't have)
- Rolled to a new position

**Why this matters:** When broker data for a period is missing (e.g., no July Thinkorswim file), positions opened before that period with expiry dates in that period would be falsely reported as "expired at $0" — inflating PnL with phantom profits.

**Validation check:** After matching, scan all closed trades. If any have `close_price = 0.0` and NO corresponding EXPIRED/ASSIGNED entry in the input data, they are phantom closures and MUST be rejected.

### Independent Spread Detection (prevents circular validation)

The reference report may itself contain spread legs. Validating only against the reference creates a circular trust problem. This check catches spreads **independently of the reference**:

1. **Raw file scan:** Before parsing, scan all Tastytrade Order History CSVs for multi-leg orders. A row is multi-leg if its Description field contains both an opening action (STO/BTO) and a closing action (BTC/STC), or contains `\n` with legs in both directions.

2. **Order ID cross-reference:** Extract order IDs from multi-leg rows. After the pipeline runs, verify NONE of these order IDs appear in the closed trades list (check both open and close sides).

3. **Qty-5 heuristic:** In this account, qty=5 is a strong signal for index/ETF spread trades (Bull Put Spreads on LLY, APP, BABA, GOOG, MSFT). If a "CSP" trade has qty=5 on a high-priced underlying ($300+), flag it for manual review.

4. **Cross-period order matching:** If a closed trade's STO was opened in month M but the same order ID appears as a multi-leg order in ANY input file, exclude it. Spread legs opened in one file may close via data in another file.

**When this check fails:** The parser has a bug. Do NOT override with the reference report — fix the parser and re-run. This check exists precisely because the reference report cannot be trusted for spread exclusion.

### Warnings (flag in report, don't block delivery)

- [ ] Excluded counts = 0 for a category that previously had entries → "NOTE: Zero excluded [category] may indicate missing input data"
- [ ] Broker present in prior period but absent in new period → "NOTE: No [Broker] data for [month(s)]"
- [ ] Assignments in the new period with no corresponding stock sale → "NOTE: X assignments pending disposition (wheel gains incomplete)"
- [ ] Fee structure change between periods (e.g., Tastytrade $0 → $31) → "NOTE: Fee pattern changed for [Broker] in [month]"
- [ ] Any trade with net_pnl = $0.00 → counted as loss (intended behavior, flag count)

### Report Content Requirements

The report MUST include these sections (beyond the standard body):

1. **Data Coverage Notice** (top of report, after period/brokers):
   - Which brokers have data for which months
   - Any gaps or incomplete coverage explicitly noted

2. **Excluded Trades** (enhanced):
   - Count per category
   - At least one example per non-zero category (ticker, date, reason)
   - If a category is zero, note whether this is expected or a potential data gap

3. **Pending Wheel Inventory** (Appendix B addition):
   - Stocks acquired via assignment in the report period that have NOT been sold
   - Format: `| Assignment Date | Broker | Ticker | Qty | Acquisition Price | Status |`
   - Status = "Pending sale"

4. **Delta Section** (when extending a prior report):
   - New trades added (count by month/broker)
   - PnL change from prior version
   - New tickers appearing for the first time

---

## validate_pnl.py Reference

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

## Output Files

| File | Description |
|------|-------------|
| `val-computed-pnl.json` | Phase 1 output: computed PnL from VAL_DATA (for self-validation) |
| `val-validation-report.json` | Phase 1 output: validation result against VAL_REPORT |
| `inp-computed-pnl.json` | Phase 3 output: computed PnL from INP_DATA alone (preview) |
| `computed-pnl.json` | Phase 4 output: combined structured data (VAL_DATA + INP_DATA) |
| `validation-report.json` | Phase 5 output: validation of combined data against VAL_REPORT |
| `pnl-report-YYYYMMDD_to_YYYYMMDD-latest.md` | Current Markdown report |
| `pnl-report-YYYYMMDD_to_YYYYMMDD-latest.html` | Current styled HTML report |
| `pnl-report-YYYYMMDD_to_YYYYMMDD-v0.md` | First historical version |
| `pnl-report-YYYYMMDD_to_YYYYMMDD-v1.md` | Second historical version |

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

**Data Coverage Notice (required, immediately after header):**
```
## Data Coverage
| Broker | Months with data | Gaps |
|--------|-----------------|------|
| Fidelity | Jan, Feb, May, Jun | Mar, Apr, Jul (no data provided) |
| Tastytrade | Jan–Jul | None |
| Thinkorswim | Jan–Jul | None |
```

**Table of Contents / Outline** (at the very top of the report body, immediately after the title/period header):
- Clickable anchor links to every major section
- In HTML: a visible boxed outline section at the top of the page content (NOT just the nav bar — the nav bar is supplementary). Styled as a bordered card with section links.
- In Markdown: standard `[Section](#anchor)` links
- Each section ends with a "Back to Top" link (`↑ Back to Top`) that scrolls to the top
- **Implementation rule:** Any feature described in this SOP MUST be implemented in BOTH `generate_markdown()` AND `generate_html()` in `render_report.py`. Never assume the HTML nav bar or any existing element satisfies a requirement — verify by inspecting the rendered output.
- **Sync rule:** The outline entries MUST match the actual section headings in the report body. When adding, removing, or renaming a section, update the outline in BOTH formats (markdown TOC and HTML Contents card) at the same time. Never hardcode outline entries — derive them from the same section list used to generate the headings, or verify after rendering that every outline link resolves to an existing section.

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
   **Heatmap section** (all Y-axis row labels sorted alphabetically A→Z from top to bottom; all chart legends sorted alphabetically A→Z):
   - **Sector Distribution Over Months (% of trades)** (stacked bar chart; X-axis = months, Y-axis = % of total trades; each sector is a colored band. Shows concentration risk and diversification trends. This is ALWAYS the first heatmap. Sector stacking order within each bar is fixed and alphabetical A→Z from bottom to top — the same sector always occupies the same vertical position across all month columns, making month-to-month comparison easy.)
   - **Sector Distribution Over Months (% of PnL)** (stacked bar chart; X-axis = months, Y-axis = % of total net PnL; each sector's share of that month's profit/loss. Same fixed alphabetical stacking order. Placed immediately after the % of trades chart for side-by-side comparison.)
   - **Sector x Month PnL heatmap** (sectors as rows, months as columns, cell = aggregate net PnL; green/red color scale)
   - **Ticker x Month PnL heatmap** (top 15 active tickers as rows, months as columns, color intensity = net PnL. Y-axis label format: `[SECTOR] TICKER`)
   - **Sector x Win Rate heatmap** (sectors as rows, months as columns, cell = aggregate win rate; red 0% → yellow 50% → green 100%)
   - **Ticker x Win Rate heatmap** (same top 15 tickers, months as columns, cell = win rate %. Y-axis: `[SECTOR] TICKER`)
   - **Sector x Win/Loss Streak heatmap** (sectors as rows, months as columns, cell = longest streak; green/red intensity)
   - **Ticker x Win/Loss Streak heatmap** (same top 15 tickers, months as columns, cell = longest streak. Y-axis: `[SECTOR] TICKER`)
   - **Broker x Strategy PnL matrix** (3x2 grid showing PnL for each broker/strategy combination; compact dashboard widget)

   **Sector Classification** is loaded from a data config file at `.local/data/options-pnl/sector-map.json`. This file can be edited without code changes. Format:

   ```json
   {
     "Technology": ["AAPL","MSFT","AVGO","GOOG","AMZN","SNPS","IONQ","RGTI","QBTS","QUBT","SMCI","DDOG","SNOW","PLTR","HOOD","COIN","RDDT","DRAM","INOD"],
     "Software/Cloud": ["CRWV","OKLO","NBIS","VCX","IREN"],
     "Space/Defense": ["ASTS","RKLB","SPCE"],
     "Consumer": ["LULU","NFLX","DASH","UBER"],
     "Semiconductors": ["AMD","MU","VRT"],
     "Healthcare/Biotech": ["MRNA","HUM","ABBV","QURE"],
     "Energy/Materials": ["MP","UUUU","BE","SPCX"],
     "Financials": ["C","GE"],
     "Industrial": ["TSLA","DAL","UAL","IBM"],
     "Other": ["LLY","BABA","APP","WDC","SLV","SPOT","NVO","TTD"]
   }
   ```

   When a ticker is not in the mapping, classify it as "Other" and log a warning so the mapping can be updated. The config file is the single source of truth — the code reads it at render time.
   - **Holding Period x PnL Outcome matrix** (rows = hold period buckets [1-7d, 8-14d, 15-30d, 31+d], columns = outcome buckets [loss >$200, small loss, breakeven, small win, win >$200], cell = trade count with color intensity)
4. **Strategy breakdown** — CSP vs CC vs Wheel Capital Gains
5. **PnL by underlying** — top 10 (best) and bottom 10 (worst) tickers by net PnL
6. **All closed trades** — grouped by month, each month in its own collapsible `<details>` element (collapsed by default in HTML). Each month heading shows trade count and net PnL as a summary line visible without expanding.
7. **Excluded trades** — counts with reasons AND at least one example per non-zero category
8. **Notes & Warnings** — any warnings from the validation checklist (fee changes, missing brokers, etc.)

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

**Pending Wheel Inventory (required):**

| Assignment Date | Broker | Ticker | Qty | Acquisition Price | Status |
|-----------------|--------|--------|-----|-------------------|--------|
| 2026-07-17 | Tastytrade | ASTS | 100 | $70.00 | Pending sale |

## HTML Styling

The HTML report follows a **document-forward, financial report** aesthetic (reference: `.local/data/options-pnl/out/sample/pnl-report-latest.html`). Key principles:

- **Layout:** 960px max-width, centered body, generous padding (50px sides), no wrapper div
- **Background:** Near-white `#fdfdfd` — clean, no tinted backgrounds
- **Typography:** Inter/system sans-serif, 15px, line-height 1.75, `text-rendering: optimizeLegibility`, `font-kerning: normal`, `hyphens: auto`
- **Headings:** `h2` with solid `#1a1a1a` bottom border (document divider style), generous top margin (2.5em)
- **Tables:** Minimal — borders only on `tbody` top/bottom and `th` top (no alternating row colors, no rounded corners). Tabular-nums for alignment.
- **Metric cards:** Flat with 1px border, left-accent-only color (green `#16a34a` for positive, red `#dc2626` for negative). No shadows, no hover transforms.
- **Nav:** Sticky, frosted glass (`backdrop-filter: blur`), muted gray text (`#606060`). Minimal — not the primary navigation (TOC is).
- **TOC:** Styled as `#TOC` block — bordered box, no bullet list-style, clean links in dark `#1a1a1a`
- **Charts:** Full-width, no container border/background — charts float on the page
- **Colors:** Monochrome (#1a1a1a text, #606060 secondary, #e6e6e6 borders) with green/red ONLY for PnL values
- **Details/expand:** Minimal border, flush styling, no card elevation
- **Back-to-top:** Right-aligned, small muted text, unobtrusive
- **ECharts via CDN** for all visualizations
- **Responsive** (mobile-friendly) and **print-friendly** (nav hidden, full-width)

Any changes to the HTML styling MUST preserve these principles. When in doubt, reference the sample report file.

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
