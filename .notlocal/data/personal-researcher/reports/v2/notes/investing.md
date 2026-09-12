# Market Cycles, Elections & Macro Patterns

> **Last Updated:** 2026-06-06 | **Read time:** ~12 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (June 2026):** The presidential election cycle theory (Yale Hirsch, 1833+) shows Year 2 (midterm) as the weakest for equities (-0.1% S&P avg) and Year 3 as the strongest (+12.3%) [1][2].
> Key data: 88% of post-midterm years were positive since 1960. Nasdaq amplifies the pattern (~-0.5% midterm, +28.8% Year 3) [3].
> Main open problem: the pattern is NOT statistically significant per formal testing — economic fundamentals dominate [2]. Trend: pattern held again in 2022→2023 (-14.5% → +18.3%).

## State of the Art

### Current Best Approaches

- **Presidential Election Cycle Theory** — 4-year pattern with Year 2 weakest, Year 3 strongest; proposed by Yale Hirsch in *Stock Trader's Almanac* [1]
- **Uncertainty Premium Model** — Markets discount policy uncertainty before midterms; premium dissipates after election resolves congressional control [4]
- **Divided Government Alpha** — Hypothesis that gridlock (common post-midterm) reduces legislative risk, favoring equities [2]
- **Mean Reversion After Political Stress** — Beaten-down valuations during midterm year create mechanical buying opportunities [2]

### Recent Breakthroughs (last 12 months)

- **2022→2023 confirmation** (Oct 2022→Dec 2023): S&P 500 went from -14.5% midterm year to +18.3% post-midterm, consistent with historical pattern [2]
- **U.S. Bank statistical analysis** (2024): Formal testing concluded the pattern is directionally correct but not statistically significant given variance and sample size [2]
- **Ameriprise volatility study** (2026): Confirmed volatility peaks ~60 trading days before midterm election day [4]

### Open Problems

- **Statistical insignificance**: Wide variability (from -30% to +24% in midterm years) means the pattern cannot reliably predict [2]
- **Sample size**: Only 16 midterm cycles since 1960 (31 since 1900); too few for robust inference
- **Confounders**: Monetary policy, exogenous shocks, and global macro often overwhelm the cycle signal
- **Survivorship bias**: Pattern documented primarily in U.S. markets; limited evidence of election cycle effects in other democracies

### Benchmark Standings

| Pattern | Avg Midterm Return | Avg Post-Midterm Return | Hit Rate (Post-Midterm Positive) | Source |
|---------|-------------------|------------------------|----------------------------------|--------|
| S&P 500 (1960-2024) | -0.1% | +12.3% | 88% (14/16) | [1][2] |
| Nasdaq (1971-2024) | -0.5% | +28.8% | ~85% | [3] |
| DJIA (1943-2024) | ~+2% | +15% | ~90% | [1] |

## Executive Summary

The presidential election cycle theory documents a real but statistically weak pattern: U.S. markets tend to underperform in midterm election years (Year 2) and outperform in the following year (Year 3). The S&P 500 averaged -0.1% in midterm years vs +12.3% in post-midterm years since 1960 [1][2].

- **The pattern exists**: 56% of midterm years negative; 88% of post-midterm years positive
- **But it's not predictive**: U.S. Bank's formal statistical tests show the differences are not significant [2]
- **The post-midterm rally is more reliable**: Every midterm since 1950 was followed by positive 12-month returns
- **Nasdaq amplifies**: Higher beta means deeper midterm lows (~-0.5%) and stronger Year 3 rallies (+28.8%) [3]

**The killer framing:** "The midterm effect is a directional bias, not a trading signal. It tells you the base rate favors patience through midterm weakness, but any individual cycle can be dominated by Fed policy, recession, or geopolitical shocks."

```
Presidential Cycle Pattern (S&P 500, 1960-2024):
                          Year 1    Year 2    Year 3    Year 4
                          (Post-    (Midterm) (Pre-     (Election)
                           Elect)             Elect)
──────────────────────────────────────────────────────────────────
Average return            +8.6%     -0.1%     +12.3%    +7.3%
Hit rate (positive)        69%       44%       88%       75%
──────────────────────────────────────────────────────────────────
Key driver               Honeymoon  Pain      Stimulus  Caution
                         optimism   front-    ramp-up   + hope
                                    loaded
```

## Midterm Year Data: S&P 500 (1962-2022)

| Midterm Year | S&P 500 Return | Post-Midterm Year | Return | Swing |
|---|---|---|---|---|
| 1962 | -9.3% | 1963 | +14.0% | +23.3pp |
| 1966 | -12.8% | 1967 | +12.8% | +25.6pp |
| 1970 | -0.3% | 1971 | +6.1% | +6.4pp |
| 1974 | -30.2% | 1975 | +22.2% | +52.4pp |
| 1978 | +6.5% | 1979 | +8.1% | +1.6pp |
| 1982 | +18.8% | 1983 | +13.9% | -4.9pp |
| 1986 | +19.4% | 1987 | -8.9% | -28.3pp |
| 1990 | -3.3% | 1991 | +19.4% | +22.7pp |
| 1994 | -3.8% | 1995 | +32.1% | +35.9pp |
| 1998 | +23.5% | 1999 | +14.4% | -9.1pp |
| 2002 | -21.1% | 2003 | +20.6% | +41.7pp |
| 2006 | +10.8% | 2007 | +3.9% | -6.9pp |
| 2010 | +10.5% | 2011 | -3.1% | -13.6pp |
| 2014 | +12.7% | 2015 | +1.3% | -11.4pp |
| 2018 | -8.0% | 2019 | +21.8% | +29.8pp |
| 2022 | -14.5% | 2023 | +18.3% | +32.8pp |

## Counter-Examples & Pattern Failures

**Post-midterm rally failures:**
- 1987 (post-1986): -8.9% — Black Monday crash overwhelmed pattern
- 2011 (post-2010): -3.1% — European debt crisis + U.S. credit downgrade

**Strong midterm years (pattern broke):**
- 1982: +18.8% (Volcker rate cuts)
- 1986: +19.4% (bull market continuation)
- 1998: +23.5% (dot-com bubble inflating despite LTCM)
- 2014: +12.7% (QE bull market)

**Common factor**: In both failure types, macroeconomic forces (monetary policy, sovereign debt crisis, asset bubble) dominated the political cycle.

## Why the Pattern Exists (Proposed Mechanisms)

| Mechanism | Explains Pre-Midterm Weakness | Explains Post-Midterm Rally |
|-----------|------------------------------|----------------------------|
| Front-loaded fiscal pain | Presidents push unpopular policies early when capital highest | Pain ends → economy recovers |
| Policy uncertainty | Unknown congressional outcome → risk premium | Outcome known → premium dissipates |
| Divided government | N/A | Gridlock = fewer surprises = lower risk premium |
| Re-election stimulus | N/A | Year 3 spending ramp-up boosts economy |
| Mean reversion | Selloff creates cheap valuations | Cheap valuations attract buyers |

## Nasdaq vs S&P 500 Amplification

| Metric | S&P 500 | Nasdaq | Difference |
|--------|---------|--------|------------|
| Midterm year avg | -0.1% | -0.5% | Nasdaq weaker |
| Post-midterm avg | +12.3% | +28.8% | Nasdaq much stronger |
| Worst midterm | -30.2% (1974) | -33.1% (2022) | Similar magnitude |
| Best post-midterm | +32.1% (1995) | +85.6% (1999) | Nasdaq 2.5x amplification |

Explanation: Nasdaq's concentration in growth/tech stocks makes it more rate-sensitive (midterm years often coincide with tightening) and more responsive to easing/stimulus in Year 3 [3].

## Do Markets Tank Before Big IPOs?

**Answer: No. The opposite is true.** Markets are typically strong before major IPOs [8][9].

### S&P 500 Performance Before Largest IPOs

| IPO | Date | Raised | 30d Before | 60d Before | 90d Before |
|-----|------|--------|-----------|-----------|-----------|
| Facebook | May 2012 | $16B | -3.3% | -0.2% | +3.1% |
| Alibaba | Sep 2014 | $25B | +1.6% | +1.0% | +2.4% |
| Uber | May 2019 | $8.1B | -1.7% | +1.8% | +9.5% |
| Saudi Aramco | Dec 2019 | $25.6B | +2.3% | +6.7% | +6.5% |
| Rivian | Nov 2021 | $13.5B | +4.6% | +5.0% | +4.8% |
| ARM | Sep 2023 | $4.87B | -0.4% | -2.2% | +1.5% |
| **Average** | | | **+0.5%** | **+2.0%** | **+4.6%** |

### Why Markets Are Strong Before IPOs (Not Weak)

- Companies **deliberately time** IPOs for bull markets ("IPO window") [8]
- IPO volume surges in strong markets: 1,035 in 2021 (bull); collapses to 181 in 2022 (bear) — 83% decline [9]
- Academic evidence (Loughran & Ritter): positive correlation between IPO volume and market level in 14/15 countries [8]

### The Liquidity Drain Myth

Mega-IPOs absorb $10-25B, but relative to $40-50T total U.S. market cap, this is ~0.05%. Effects are **sector-level**, not market-wide [10]:
- After Facebook IPO: Zynga -13.4%
- After Alibaba IPO: Amazon -2.1%, eBay -1.4%
- Broad S&P 500 impact: minimal

### The Real Signal: IPO Booms as Market Top Indicators

The legitimate concern is different — IPO **clusters** may signal market tops (declines come AFTER, not before) [10]:

| Period | IPO Activity | What Followed |
|--------|-------------|---------------|
| 1999-2000 | 480 IPOs, $69B raised | Nasdaq -78% |
| 2021-2022 | 1,035 IPOs (record) | S&P -20%, Nasdaq -33% |
| 1993-1997 | High activity | No crash (counter-example) |

Statistical hit rate: crash probability after IPO wave ~20% vs base rate ~14%. Meaningful but not deterministic [10].

### Common Misconception

People confuse two claims:
1. "Markets decline BEFORE big IPOs" → **FALSE**
2. "Markets decline AFTER IPO booms" → **SOMETIMES TRUE** (20% rate)

The second gets misremembered as the first.

## References

- [1] Hirsch, Yale (1967-present) — *Stock Trader's Almanac* — Originated the Presidential Election Cycle Theory with data back to 1833; documents 4-year pattern across DJIA, S&P 500, and later Nasdaq
- [2] U.S. Bank Wealth Management (2024) — "Stock Market Performance After Midterm Elections" — Analysis of 31 midterm elections over 125 years; includes statistical significance testing
- [3] MarketWatch (2022) — Nasdaq midterm year performance compilation — Average returns by index type during election cycle years
- [4] Ameriprise Financial (2026) — "Midterm Election Market Impacts" — Volatility patterns around midterm elections; confirms below-average returns and elevated vol
- [5] Landmark Wealth Management — "S&P 500 Midterm Election Performance" — First-3-months post-midterm average (+6.5%) and long-term pattern data
- [6] Capital Group / First Trust / Hartford Funds — Aggregated election cycle research — S&P 500 gained average of +15.4% one year after midterms (since 1950)
- [7] Nickles, Marshall (Pepperdine University) — "Presidential Elections and Stock Market Cycles" — Academic paper documenting the presidential cycle effect
- [8] Loughran & Ritter (University of Florida) — IPO statistics 1980-2025 — Positive correlation between IPO volume and market level in 14/15 countries; companies time IPOs for strong markets
- [9] StockAnalysis.com — IPO Statistics 2000-2026 — Volume data showing 83% collapse from bull (2021: 1,035) to bear (2022: 181)
- [10] Bank of America / TradingKey / JPMorgan — IPO liquidity analysis — Sector-level effects documented; market-wide impact minimal relative to total cap

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-06 | Initial v2 generation | New topic: Midterm elections and market performance. Covers presidential cycle theory, pre/post-midterm data, Nasdaq amplification, counter-examples, and mechanisms |
| 2026-06-06 | Added IPO market timing section | Query: "do markets tank before big IPOs?" — Answer: No, markets are strong before IPOs. Added data table, liquidity drain analysis, IPO boom top signal |
