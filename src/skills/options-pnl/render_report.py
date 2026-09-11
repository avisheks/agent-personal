#!/usr/bin/env python3
"""
Render the computed PnL JSON into .md and .html reports.
Uses ECharts for visualizations.

Usage:
    python3 src/render_report.py --input .local/options-pnl/out/computed-pnl.json --output-dir .local/options-pnl/out
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta


def fmt_dollar(val):
    if val >= 0:
        return f"${val:,.2f}"
    return f"-${abs(val):,.2f}"


def fmt_pct(val):
    return f"{val:.1f}%"


def load_sector_map(input_path):
    """Load sector mapping from config file. Returns (sector_map_dict, ticker_to_sector_dict)."""
    sector_map_path = Path(input_path).parent / "sector-map.json"
    if not sector_map_path.exists():
        sector_map_path = Path(".local/data/options-pnl/sector-map.json")
    if sector_map_path.exists():
        with open(sector_map_path) as f:
            sector_map = json.load(f)
    else:
        sector_map = {"Other": []}
        print(f"WARNING: sector-map.json not found. All tickers classified as 'Other'.")

    t2s = {}
    for sec, tickers in sector_map.items():
        for tk in tickers:
            t2s[tk] = sec
    return sector_map, t2s


def get_sector(ticker, t2s):
    """Get sector for a ticker from the lookup dict."""
    return data["_t2s"].get(ticker, "Other")


REPORT_SECTIONS = [
    ("PnL Summary", "summary"),
    ("Sector Insights", "sectors"),
    ("Detailed Performance", "details"),
    ("Strategy & Underlying", "strategy"),
    ("All Closed Trades", "trades"),
    ("Appendix A: Premium Only", "appendix-a"),
    ("Appendix B: Wheel Capital Gains", "appendix-b"),
    ("Appendix C: Additional Charts", "appendix-c"),
]


def generate_markdown(data: dict) -> str:
    s = data["summary"]
    full = data.get("full_pnl", {})
    ws = data.get("wheel_summary", {})
    wheel_gains = data.get("wheel_gains", [])

    lines = []
    lines.append(f"# Options PnL Report: CSP & Covered Calls (Full Wheel)\n")
    lines.append(f"**Generated:** {data['generated']}")
    lines.append(f"**Period:** {data['period_start']} to {data['period_end']}")
    lines.append(f"**Brokers:** Fidelity, Tastytrade, Thinkorswim\n")
    lines.append("---\n")

    # Table of Contents (derived from REPORT_SECTIONS — single source of truth)
    lines.append('<a id="top"></a>\n')
    lines.append("## Contents\n")
    for title, anchor in REPORT_SECTIONS:
        lines.append(f"- [{title}](#{anchor})")
    lines.append("")

    # Full PnL Summary
    lines.append("## Full PnL Summary\n")
    lines.append("| Component | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| Option Premium PnL (CSP + CC) | {fmt_dollar(full.get('premium_pnl', s['total_net_pnl']))} |")
    lines.append(f"| Wheel Capital Gains (stock) | {fmt_dollar(full.get('wheel_capital_gains', 0))} |")
    lines.append(f"| **Total Full PnL** | **{fmt_dollar(full.get('total_net_pnl', s['total_net_pnl']))}** |")
    lines.append(f"| Total Trades (options + stock sales) | {full.get('total_trades', s['total_trades'])} |")
    lines.append("")

    # Premium Summary
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## Premium PnL Breakdown\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Realized PnL | {fmt_dollar(s['total_gross_pnl'])} |")
    lines.append(f"| Total Commissions & Fees | {fmt_dollar(s['total_fees'])} |")
    lines.append(f"| Net PnL (after fees) | {fmt_dollar(s['total_net_pnl'])} |")
    lines.append(f"| Winning Trades | {s['winning_trades']} ({fmt_pct(s['win_rate'])}) |")
    lines.append(f"| Losing Trades | {s['losing_trades']} |")
    lines.append(f"| Largest Win | {fmt_dollar(s['largest_win'])} |")
    lines.append(f"| Largest Loss | {fmt_dollar(s['largest_loss'])} |")
    lines.append(f"| Average Win | {fmt_dollar(s['avg_win'])} |")
    lines.append(f"| Average Loss | {fmt_dollar(s['avg_loss'])} |")
    lines.append("")

    # Monthly Summary All
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## Monthly Summary (All Brokers)\n")
    lines.append("| Month | Trades | Gross PnL | Fees | Net PnL | Win Rate |")
    lines.append("|-------|--------|-----------|------|---------|----------|")
    for m in data["monthly_all"]:
        lines.append(f"| {m['month']} | {m['trades']} | {fmt_dollar(m['gross_pnl'])} | {fmt_dollar(m['fees'])} | {fmt_dollar(m['net_pnl'])} | {fmt_pct(m['win_rate'])} |")
    total_trades = sum(m['trades'] for m in data['monthly_all'])
    total_gross = sum(m['gross_pnl'] for m in data['monthly_all'])
    total_fees = sum(m['fees'] for m in data['monthly_all'])
    total_net = sum(m['net_pnl'] for m in data['monthly_all'])
    lines.append(f"| **Total** | **{total_trades}** | **{fmt_dollar(total_gross)}** | **{fmt_dollar(total_fees)}** | **{fmt_dollar(total_net)}** | **{fmt_pct(s['win_rate'])}** |")
    lines.append("")

    # Monthly by Broker
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## Monthly Summary by Broker\n")
    for broker, months in data["monthly_by_broker"].items():
        lines.append(f"### {broker}\n")
        lines.append("| Month | Trades | Gross PnL | Fees | Net PnL | Win Rate |")
        lines.append("|-------|--------|-----------|------|---------|----------|")
        for m in months:
            lines.append(f"| {m['month']} | {m['trades']} | {fmt_dollar(m['gross_pnl'])} | {fmt_dollar(m['fees'])} | {fmt_dollar(m['net_pnl'])} | {fmt_pct(m['win_rate'])} |")
        bt = sum(m['trades'] for m in months)
        bg = sum(m['gross_pnl'] for m in months)
        bf = sum(m['fees'] for m in months)
        bn = sum(m['net_pnl'] for m in months)
        bw = round(sum(1 for t in data['closed_trades'] if t['broker'] == broker and t['net_pnl'] > 0) / max(bt, 1) * 100, 1)
        lines.append(f"| **Total** | **{bt}** | **{fmt_dollar(bg)}** | **{fmt_dollar(bf)}** | **{fmt_dollar(bn)}** | **{fmt_pct(bw)}** |")
        lines.append("")

    # Strategy
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## Strategy Breakdown\n")
    lines.append("| Strategy | Trades | Net PnL | Win Rate | Avg PnL/Trade |")
    lines.append("|----------|--------|---------|----------|---------------|")
    for st in data["by_strategy"]:
        lines.append(f"| {st['label']} | {st['trades']} | {fmt_dollar(st['net_pnl'])} | {fmt_pct(st['win_rate'])} | {fmt_dollar(st['avg_pnl'])} |")
    lines.append("")

    # By Underlying
    by_und = data["by_underlying"]
    if isinstance(by_und, dict):
        lines.append("## PnL by Underlying (Top 10)\n")
        lines.append("| Underlying | Trades | Net PnL | Avg PnL/Trade | Win Rate |")
        lines.append("|------------|--------|---------|---------------|----------|")
        for u in by_und.get("top_10", []):
            lines.append(f"| {u['underlying']} | {u['trades']} | {fmt_dollar(u['net_pnl'])} | {fmt_dollar(u['avg_pnl'])} | {fmt_pct(u['win_rate'])} |")
        lines.append("")

        lines.append("## PnL by Underlying (Bottom 10)\n")
        lines.append("| Underlying | Trades | Net PnL | Avg PnL/Trade | Win Rate |")
        lines.append("|------------|--------|---------|---------------|----------|")
        for u in by_und.get("bottom_10", []):
            lines.append(f"| {u['underlying']} | {u['trades']} | {fmt_dollar(u['net_pnl'])} | {fmt_dollar(u['avg_pnl'])} | {fmt_pct(u['win_rate'])} |")
        lines.append("")
    else:
        lines.append("## PnL by Underlying (Top 15)\n")
        lines.append("| Underlying | Trades | Net PnL | Avg PnL/Trade | Win Rate |")
        lines.append("|------------|--------|---------|---------------|----------|")
        for u in by_und:
            lines.append(f"| {u['underlying']} | {u['trades']} | {fmt_dollar(u['net_pnl'])} | {fmt_dollar(u['avg_pnl'])} | {fmt_pct(u['win_rate'])} |")
        lines.append("")

    # Closed Trades - grouped by month
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## All Closed Trades\n")
    from collections import defaultdict
    trades_by_month = defaultdict(list)
    for t in data["closed_trades"]:
        month = (t['date_closed'] or "unknown")[:7]
        trades_by_month[month].append(t)

    # Load insights if available
    _insights = data.get("_insights", {})

    for month in sorted(trades_by_month.keys(), reverse=True):
        month_trades = trades_by_month[month]
        month_net = sum(t['net_pnl'] for t in month_trades)
        lines.append(f"<details><summary><strong>{month}</strong> — {len(month_trades)} trades, {fmt_dollar(month_net)} net</summary>\n")
        # Inject insights
        mi = _insights.get(month, {})
        if mi.get("repeat") or mi.get("improve"):
            if mi.get("repeat"):
                lines.append("**✓ Repeat**\n")
                for bullet in mi["repeat"]:
                    lines.append(f"- {bullet}")
                lines.append("")
            if mi.get("improve"):
                lines.append("**⚠ Improve**\n")
                for bullet in mi["improve"]:
                    # Support both old format (string) and new format (dict with risk flag)
                    if isinstance(bullet, dict):
                        text = bullet["text"]
                        if bullet.get("risk"):
                            lines.append(f"- ⚠️ {text}")
                        else:
                            lines.append(f"- {text}")
                    else:
                        lines.append(f"- {bullet}")
                lines.append("")
        lines.append("| Date Closed | Broker | Underlying | Strategy | Strike | Expiry | Qty | Open $ | Close $ | Net PnL |")
        lines.append("|-------------|--------|------------|----------|--------|--------|-----|--------|---------|---------|")
        for t in month_trades:
            dc = t['date_closed'] or "unknown"
            lines.append(f"| {dc} | {t['broker']} | {t['underlying']} | {t['strategy']} | ${t['strike']:.0f} | {t['expiry'] or '?'} | {t['qty']} | ${t['open_price']:.2f} | ${t['close_price']:.2f} | {fmt_dollar(t['net_pnl'])} |")
        lines.append("\n</details>\n")
    lines.append("")

    # Excluded
    lines.append("[↑ Back to Top](#top)\n")
    lines.append("## Excluded Trades\n")
    lines.append("| Category | Count | Reason |")
    lines.append("|----------|-------|--------|")
    lines.append(f"| Long options (Buy to Open) | {data['excluded']['long_options']} | Not CSP/CC |")
    lines.append(f"| Spread legs | {data['excluded']['spread_legs']} | Multi-leg strategy |")
    lines.append(f"| Stock trades | {data['excluded']['stock_trades']} | Non-options |")
    lines.append("")

    # Appendix A: Premium Only
    lines.append("---\n")
    lines.append("# Appendix A: CSP/CC Premium Only\n")
    lines.append("Option premium PnL only (excludes stock wheeling capital gains).\n")
    lines.append("## Premium-Only Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Net Premium PnL | {fmt_dollar(s['total_net_pnl'])} |")
    lines.append(f"| Total Option Trades | {s['total_trades']} |")
    lines.append(f"| Win Rate | {fmt_pct(s['win_rate'])} |")
    lines.append(f"| Average Win | {fmt_dollar(s['avg_win'])} |")
    lines.append(f"| Average Loss | {fmt_dollar(s['avg_loss'])} |")
    lines.append("")

    lines.append("## All Closed Option Trades\n")
    lines.append("(See main body 'All Closed Trades' section above for full detail table.)\n")

    if data.get("stock_trades"):
        lines.append("## Stock Trades (reference only, no PnL computed)\n")
        lines.append("| Date | Broker | Action | Ticker | Qty | Price | Amount |")
        lines.append("|------|--------|--------|--------|-----|-------|--------|")
        for st in data["stock_trades"]:
            lines.append(f"| {st['date']} | {st['broker']} | {st['action']} | {st['ticker']} | {st['qty']} | ${st['price']:.2f} | {fmt_dollar(st['amount'])} |")
        lines.append("")

    # Appendix B: Wheel Capital Gains
    lines.append("---\n")
    lines.append("# Appendix B: Stock Wheeling Capital Gains\n")
    lines.append("Capital gains from stocks acquired via CSP assignment and subsequently sold.\n")

    if wheel_gains:
        lines.append("## Wheel Summary\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Capital Gains | {fmt_dollar(ws.get('total_capital_gains', 0))} |")
        lines.append(f"| Completed Wheel Cycles | {ws.get('completed_cycles', 0)} |")
        lines.append(f"| Average Hold Period | {ws.get('avg_days_held', 0)} days |")
        lines.append(f"| Best Stock Trade | {fmt_dollar(ws.get('best_trade', 0))} |")
        lines.append(f"| Worst Stock Trade | {fmt_dollar(ws.get('worst_trade', 0))} |")
        lines.append("")

        lines.append("## Wheel Trades Detail\n")
        lines.append("| Date Sold | Broker | Ticker | Qty | Acquisition Price | Sale Price | Capital Gain | Assignment Date | Days Held |")
        lines.append("|-----------|--------|--------|-----|-------------------|------------|--------------|-----------------|-----------|")
        for w in wheel_gains:
            lines.append(f"| {w['sale_date']} | {w['broker']} | {w['ticker']} | {w['qty']} | ${w['acquisition_price']:.2f} | ${w['sale_price']:.2f} | {fmt_dollar(w['capital_gain'])} | {w['assignment_date']} | {w['days_held']} |")
        lines.append("")
    else:
        lines.append("No wheel capital gains found in this period (no stocks acquired via CSP assignment were sold).\n")

    return "\n".join(lines)


def generate_html(data: dict, args=None) -> str:
    s = data["summary"]
    weekly = data["weekly_all"]
    weekly_broker = data["weekly_by_broker"]
    monthly = data["monthly_all"]
    closed = data["closed_trades"]

    # Prepare chart data
    week_labels = json.dumps([w["week_starting"] for w in weekly])
    week_net = json.dumps([w["net_pnl"] for w in weekly])
    week_cum = json.dumps([w["cumulative_pnl"] for w in weekly])

    # Weekly bar colors
    bar_colors = json.dumps(["#22c55e" if w["net_pnl"] >= 0 else "#ef4444" for w in weekly])

    # Per-broker cumulative
    broker_datasets = []
    broker_colors = {"Fidelity": "#3b82f6", "Tastytrade": "#f97316", "Thinkorswim": "#8b5cf6"}
    for broker, wdata in weekly_broker.items():
        broker_datasets.append({
            "label": broker,
            "data": [w["cumulative_pnl"] for w in wdata],
            "labels": [w["week_starting"] for w in wdata],
            "color": broker_colors.get(broker, "#6b7280"),
        })

    # Calendar heatmap data (date -> pnl)
    daily_pnl = {}
    for t in closed:
        d = t["date_closed"]
        if d:
            daily_pnl[d] = daily_pnl.get(d, 0) + t["net_pnl"]
    cal_data = json.dumps([[d, round(v, 2)] for d, v in sorted(daily_pnl.items())])

    # PnL distribution buckets
    pnl_values = [t["net_pnl"] for t in closed]
    hist_buckets = {}
    for v in pnl_values:
        bucket = int(v // 50) * 50
        hist_buckets[bucket] = hist_buckets.get(bucket, 0) + 1
    hist_sorted = sorted(hist_buckets.items())
    hist_labels = json.dumps([f"${b}" for b, _ in hist_sorted])
    hist_values = json.dumps([c for _, c in hist_sorted])
    hist_colors = json.dumps(["#22c55e" if b >= 0 else "#ef4444" for b, _ in hist_sorted])

    # Scatter: days held vs PnL
    scatter_data = []
    for t in closed:
        if t["date_opened"] and t["date_closed"]:
            try:
                d1 = datetime.strptime(t["date_opened"], "%Y-%m-%d")
                d2 = datetime.strptime(t["date_closed"], "%Y-%m-%d")
                days = (d2 - d1).days
                scatter_data.append({"x": days, "y": round(t["net_pnl"], 2), "strategy": t["strategy"], "ticker": t["underlying"]})
            except:
                pass
    scatter_csp = json.dumps([{"x": p["x"], "y": p["y"]} for p in scatter_data if p["strategy"] == "CSP"])
    scatter_cc = json.dumps([{"x": p["x"], "y": p["y"]} for p in scatter_data if p["strategy"] == "CC"])

    # Win/loss streak
    streak_colors = json.dumps(["#22c55e" if t["net_pnl"] > 0 else "#ef4444" for t in closed])
    streak_values = json.dumps([round(t["net_pnl"], 2) for t in closed])

    # Drawdown
    cum = 0
    peak = 0
    drawdown_data = []
    cum_line = []
    for w in weekly:
        cum += w["net_pnl"]
        peak = max(peak, cum)
        dd = cum - peak
        cum_line.append(round(cum, 2))
        drawdown_data.append(round(dd, 2))
    drawdown_json = json.dumps(drawdown_data)
    cum_line_json = json.dumps(cum_line)

    # Monthly waterfall
    waterfall_labels = json.dumps([m["month"] for m in monthly])
    waterfall_values = json.dumps([round(m["net_pnl"], 2) for m in monthly])
    waterfall_colors = json.dumps(["#22c55e" if m["net_pnl"] >= 0 else "#ef4444" for m in monthly])

    # Sunburst data
    sunburst_data = []
    for t in closed:
        sunburst_data.append({"strategy": t["strategy"], "underlying": t["underlying"], "pnl": abs(t["net_pnl"])})

    # Strategy donut
    strat_labels = json.dumps([st["label"] for st in data["by_strategy"]])
    strat_values = json.dumps([st["net_pnl"] for st in data["by_strategy"]])

    # Broker donut
    broker_pnl = {}
    for t in closed:
        broker_pnl[t["broker"]] = broker_pnl.get(t["broker"], 0) + t["net_pnl"]
    broker_labels = json.dumps(list(broker_pnl.keys()))
    broker_values = json.dumps([round(v, 2) for v in broker_pnl.values()])

    # Top/Bottom trades
    sorted_by_pnl = sorted(closed, key=lambda x: x["net_pnl"], reverse=True)
    top3 = sorted_by_pnl[:3]
    bottom3 = sorted_by_pnl[-3:]

    def trade_card(t, is_win):
        color = "#22c55e" if is_win else "#ef4444"
        bg = "#f0fdf4" if is_win else "#fef2f2"
        return f"""<div class="trade-card" style="border-left:4px solid {color};background:{bg}">
            <div class="card-ticker">{t['underlying']}</div>
            <div class="card-pnl" style="color:{color}">{fmt_dollar(t['net_pnl'])}</div>
            <div class="card-detail">{t['strategy']} ${t['strike']:.0f} exp {t['expiry']}</div>
            <div class="card-detail">{t['date_opened']} → {t['date_closed']}</div>
        </div>"""

    top_cards = "\n".join(trade_card(t, True) for t in top3)
    bottom_cards = "\n".join(trade_card(t, False) for t in bottom3)

    # Build trades table rows grouped by month
    from collections import defaultdict as _defaultdict
    _trades_by_month = _defaultdict(list)
    for t in closed:
        _month = (t['date_closed'] or 'unknown')[:7]
        _trades_by_month[_month].append(t)

    # Load insights for HTML
    _html_insights = data.get("_insights", {})

    trades_rows = ""
    for _month in sorted(_trades_by_month.keys(), reverse=True):
        _mtrades = _trades_by_month[_month]
        _mnet = sum(t['net_pnl'] for t in _mtrades)
        _mnet_color = "#16a34a" if _mnet >= 0 else "#dc2626"
        trades_rows += f"""<details style="margin-bottom:0.5rem">
        <summary style="cursor:pointer;padding:0.5rem;font-weight:600">
            {_month} — {len(_mtrades)} trades, <span style="color:{_mnet_color}">{fmt_dollar(_mnet)}</span> net
        </summary>\n"""
        # Inject insights box
        _mi = _html_insights.get(_month, {})
        if _mi.get("repeat") or _mi.get("improve"):
            trades_rows += '<div style="margin:0.75rem 0;padding:0.75rem 1rem;border-radius:4px;background:#fdfdfd;border:1px solid #e6e6e6">\n'
            if _mi.get("repeat"):
                trades_rows += '<div style="margin-bottom:0.5rem"><strong style="color:#16a34a;font-size:0.8rem">✓ Repeat</strong><ul style="margin:0.25rem 0 0 1.2rem;font-size:0.82rem;line-height:1.6">'
                for _b in _mi["repeat"]:
                    trades_rows += f"<li>{_b}</li>"
                trades_rows += "</ul></div>\n"
            if _mi.get("improve"):
                trades_rows += '<div><strong style="color:#d97706;font-size:0.8rem">⚠ Improve</strong><ul style="margin:0.25rem 0 0 1.2rem;font-size:0.82rem;line-height:1.6">'
                for _b in _mi["improve"]:
                    if isinstance(_b, dict):
                        text = _b["text"]
                    else:
                        text = _b
                    if text.startswith("[Risk]"):
                        trades_rows += f'<li style="color:#d97706;font-weight:500">{text}</li>'
                    else:
                        trades_rows += f'<li>{text}</li>'
                trades_rows += "</ul></div>\n"
            trades_rows += "</div>\n"
        trades_rows += """<table style="margin-top:0.5rem">
        <thead><tr><th>Date Closed</th><th>Broker</th><th>Underlying</th><th>Strategy</th><th class="num">Strike</th><th>Expiry</th><th class="num">Qty</th><th class="num">Open $</th><th class="num">Close $</th><th class="num">Net PnL</th></tr></thead>
        <tbody>\n"""
        for t in _mtrades:
            pnl_color = "color:#16a34a" if t["net_pnl"] >= 0 else "color:#dc2626"
            trades_rows += f"""<tr>
                <td>{t['date_closed']}</td><td>{t['broker']}</td><td>{t['underlying']}</td>
                <td>{t['strategy']}</td><td>${t['strike']:.0f}</td><td>{t['expiry']}</td>
                <td>{t['qty']}</td><td>${t['open_price']:.2f}</td><td>${t['close_price']:.2f}</td>
                <td style="{pnl_color};font-weight:600">{fmt_dollar(t['net_pnl'])}</td>
            </tr>\n"""
        trades_rows += "</tbody></table></details>\n"

    # Monthly table rows (reverse chronological — latest first)
    monthly_rows = ""
    for m in reversed(monthly):
        pnl_color = "color:#22c55e" if m["net_pnl"] >= 0 else "color:#ef4444"
        monthly_rows += f"""<tr>
            <td>{m['month']}</td><td>{m['trades']}</td><td>{fmt_dollar(m['gross_pnl'])}</td>
            <td>{fmt_dollar(m['fees'])}</td><td style="{pnl_color};font-weight:600">{fmt_dollar(m['net_pnl'])}</td>
            <td>{fmt_pct(m['win_rate'])}</td>
        </tr>\n"""

    # Win rate bar
    wr = s['win_rate']

    # Full PnL headline values
    full_pnl_data = data.get("full_pnl", {})
    full_pnl_total = full_pnl_data.get("total_net_pnl", s["total_net_pnl"])
    full_trade_count = full_pnl_data.get("total_trades", s["total_trades"])

    # --- Sector mapping (loaded from config file) ---
    _input_path = args.input if args else "."
    _sector_result = load_sector_map(_input_path)
    SECTOR_MAP = _sector_result[0]
    data["_t2s"] = _sector_result[1]

    # --- Ticker x Month PnL Heatmap data ---
    from collections import defaultdict as _dd
    ticker_month_pnl = _dd(lambda: _dd(float))
    ticker_trade_count = _dd(int)
    all_months_set = set()
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            all_months_set.add(m)
            ticker_month_pnl[t["underlying"]][m] += t["net_pnl"]
            ticker_trade_count[t["underlying"]] += 1
    # Top 15 by trade count, sorted alphabetically by "[Sector] TICKER" label
    top_tickers_hm_raw = sorted(ticker_trade_count.keys(), key=lambda x: ticker_trade_count[x], reverse=True)[:15]
    _t2s_map = data["_t2s"]
    top_tickers_hm_labels = sorted(["[" + _t2s_map.get(tk, "Other") + "] " + tk for tk in top_tickers_hm_raw], reverse=True)
    # Derive ticker order from sorted labels
    top_tickers_hm = [lbl.split("] ")[1] for lbl in top_tickers_hm_labels]
    all_months_sorted = sorted(all_months_set)
    heatmap_data = []
    for mi, m in enumerate(all_months_sorted):
        for ti, tk in enumerate(top_tickers_hm):
            val = round(ticker_month_pnl[tk].get(m, 0), 2)
            if val != 0:
                heatmap_data.append([mi, ti, val])
    heatmap_data_json = json.dumps(heatmap_data)
    heatmap_months_json = json.dumps(all_months_sorted)
    heatmap_tickers_json = json.dumps(top_tickers_hm_labels)
    heatmap_max = max((abs(d[2]) for d in heatmap_data), default=500)

    # --- Sector x Month PnL Heatmap data ---
    sector_month_pnl = _dd(lambda: _dd(float))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            sec = data["_t2s"].get(t["underlying"], "Other")
            sector_month_pnl[sec][m] += t["net_pnl"]
    sectors_with_trades = sorted((sec for sec in sector_month_pnl if any(sector_month_pnl[sec].get(m, 0) != 0 for m in all_months_sorted)), reverse=True)
    sector_pnl_data = []
    for mi, m in enumerate(all_months_sorted):
        for si, sec in enumerate(sectors_with_trades):
            val = round(sector_month_pnl[sec].get(m, 0), 2)
            if val != 0:
                sector_pnl_data.append([mi, si, val])
    sector_pnl_data_json = json.dumps(sector_pnl_data)
    sectors_json = json.dumps(sectors_with_trades)
    sector_pnl_max = max((abs(d[2]) for d in sector_pnl_data), default=500)

    # --- Ticker x Win Rate Heatmap data ---
    ticker_month_wins = _dd(lambda: _dd(int))
    ticker_month_total = _dd(lambda: _dd(int))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            tk = t["underlying"]
            ticker_month_total[tk][m] += 1
            if t["net_pnl"] > 0:
                ticker_month_wins[tk][m] += 1
    winrate_data = []
    for mi, m in enumerate(all_months_sorted):
        for ti, tk in enumerate(top_tickers_hm):
            total = ticker_month_total[tk].get(m, 0)
            if total > 0:
                wr = round(ticker_month_wins[tk].get(m, 0) / total * 100, 1)
                winrate_data.append([mi, ti, wr])
    winrate_data_json = json.dumps(winrate_data)
    winrate_tickers_json = json.dumps(top_tickers_hm_labels)

    # --- Sector x Win Rate Heatmap data ---
    sector_month_wins = _dd(lambda: _dd(int))
    sector_month_total = _dd(lambda: _dd(int))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            sec = data["_t2s"].get(t["underlying"], "Other")
            sector_month_total[sec][m] += 1
            if t["net_pnl"] > 0:
                sector_month_wins[sec][m] += 1
    sector_winrate_data = []
    for mi, m in enumerate(all_months_sorted):
        for si, sec in enumerate(sectors_with_trades):
            total = sector_month_total[sec].get(m, 0)
            if total > 0:
                wr = round(sector_month_wins[sec].get(m, 0) / total * 100, 1)
                sector_winrate_data.append([mi, si, wr])
    sector_winrate_data_json = json.dumps(sector_winrate_data)

    # --- Ticker x Win/Loss Streak Heatmap data ---
    # For each ticker+month, compute longest streak (positive = win streak, negative = loss streak)
    ticker_month_trades_ordered = _dd(lambda: _dd(list))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            ticker_month_trades_ordered[t["underlying"]][m].append(1 if t["net_pnl"] > 0 else -1)

    def _longest_streak(results):
        if not results:
            return 0
        max_win = 0
        max_loss = 0
        cur = 0
        for r in results:
            if r > 0:
                cur = cur + 1 if cur > 0 else 1
                max_win = max(max_win, cur)
            else:
                cur = cur - 1 if cur < 0 else -1
                max_loss = min(max_loss, cur)
        return max_win if max_win >= abs(max_loss) else max_loss

    streak_data = []
    for mi, m in enumerate(all_months_sorted):
        for ti, tk in enumerate(top_tickers_hm):
            results = ticker_month_trades_ordered[tk].get(m, [])
            if results:
                streak = _longest_streak(results)
                if streak != 0:
                    streak_data.append([mi, ti, streak])
    streak_data_json = json.dumps(streak_data)
    streak_max = max((abs(d[2]) for d in streak_data), default=5)

    # --- Sector x Win/Loss Streak Heatmap data ---
    sector_month_trades_ordered = _dd(lambda: _dd(list))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            sec = data["_t2s"].get(t["underlying"], "Other")
            sector_month_trades_ordered[sec][m].append(1 if t["net_pnl"] > 0 else -1)
    sector_streak_data = []
    for mi, m in enumerate(all_months_sorted):
        for si, sec in enumerate(sectors_with_trades):
            results = sector_month_trades_ordered[sec].get(m, [])
            if results:
                streak = _longest_streak(results)
                if streak != 0:
                    sector_streak_data.append([mi, si, streak])
    sector_streak_data_json = json.dumps(sector_streak_data)
    sector_streak_max = max((abs(d[2]) for d in sector_streak_data), default=5)

    # --- Sector Distribution Over Months (stacked bar, % of trades) ---
    sector_month_trade_count = _dd(lambda: _dd(int))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            sec = data["_t2s"].get(t["underlying"], "Other")
            sector_month_trade_count[sec][m] += 1
    # Build series data: one series per sector (alphabetical A-Z for legend order)
    sectors_alpha = sorted(sectors_with_trades)
    sector_dist_series = []
    for sec in sectors_alpha:
        series_data = []
        for m in all_months_sorted:
            month_total = sum(sector_month_trade_count[s].get(m, 0) for s in sectors_with_trades)
            pct = round(sector_month_trade_count[sec].get(m, 0) / max(month_total, 1) * 100, 1)
            series_data.append(pct)
        sector_dist_series.append({"name": sec, "type": "bar", "stack": "total", "emphasis": {"focus": "series"}, "data": series_data})
    sector_dist_series_json = json.dumps(sector_dist_series)

    # --- Sector Distribution Over Months (stacked bar, % of PnL) ---
    sector_month_pnl_totals = _dd(lambda: _dd(float))
    for t in closed:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            sec = data["_t2s"].get(t["underlying"], "Other")
            sector_month_pnl_totals[sec][m] += t["net_pnl"]
    sector_dist_pnl_series = []
    for sec in sectors_alpha:
        series_data = []
        for m in all_months_sorted:
            month_total_pnl = sum(sector_month_pnl_totals[s].get(m, 0) for s in sectors_with_trades)
            pct = round(sector_month_pnl_totals[sec].get(m, 0) / max(abs(month_total_pnl), 1) * 100, 1)
            series_data.append(pct)
        sector_dist_pnl_series.append({"name": sec, "type": "bar", "stack": "total", "emphasis": {"focus": "series"}, "data": series_data})
    sector_dist_pnl_series_json = json.dumps(sector_dist_pnl_series)

    # --- Broker x Strategy PnL Matrix data ---
    broker_strat_pnl = _dd(lambda: _dd(float))
    for t in closed:
        broker_strat_pnl[t["broker"]][t["strategy"]] += t["net_pnl"]
    brokers_list = sorted(broker_strat_pnl.keys())
    strats_list = ["CSP", "CC"]
    matrix_data = []
    for bi, b in enumerate(brokers_list):
        for si, st in enumerate(strats_list):
            val = round(broker_strat_pnl[b].get(st, 0), 2)
            matrix_data.append([si, bi, val])
    matrix_data_json = json.dumps(matrix_data)
    matrix_brokers_json = json.dumps(brokers_list)
    matrix_strats_json = json.dumps(strats_list)
    matrix_max = max((abs(d[2]) for d in matrix_data), default=500)

    # --- Holding Period x PnL Outcome Matrix data ---
    hold_buckets = ["1-7d", "8-14d", "15-30d", "31+d"]
    outcome_buckets = ["Loss >$200", "Small Loss", "Breakeven", "Small Win", "Win >$200"]
    hold_outcome_matrix = [[0]*len(outcome_buckets) for _ in range(len(hold_buckets))]
    for t in closed:
        if t.get("date_opened") and t.get("date_closed"):
            try:
                d1 = datetime.strptime(t["date_opened"], "%Y-%m-%d")
                d2 = datetime.strptime(t["date_closed"], "%Y-%m-%d")
                days = (d2 - d1).days
            except:
                continue
            if days <= 7: hi = 0
            elif days <= 14: hi = 1
            elif days <= 30: hi = 2
            else: hi = 3

            pnl = t["net_pnl"]
            if pnl < -200: oi = 0
            elif pnl < 0: oi = 1
            elif pnl < 50: oi = 2
            elif pnl <= 200: oi = 3
            else: oi = 4

            hold_outcome_matrix[hi][oi] += 1

    hold_outcome_data = []
    for hi in range(len(hold_buckets)):
        for oi in range(len(outcome_buckets)):
            val = hold_outcome_matrix[hi][oi]
            if val > 0:
                hold_outcome_data.append([oi, hi, val])
    hold_outcome_json = json.dumps(hold_outcome_data)
    hold_buckets_json = json.dumps(hold_buckets)
    outcome_buckets_json = json.dumps(outcome_buckets)
    hold_outcome_max = max((d[2] for d in hold_outcome_data), default=1)

    # Pre-compute Appendix A HTML
    wheel_gains_list = data.get('wheel_gains', [])
    wheel_sum = data.get('wheel_summary', {})
    if wheel_gains_list:
        wg_total = wheel_sum.get('total_capital_gains', 0)
        wg_card_class = "positive" if wg_total >= 0 else "negative"
        wg_color = "#22c55e" if wg_total >= 0 else "#ef4444"
        wg_rows = "".join(
            f'<tr><td>{w["sale_date"]}</td><td>{w["broker"]}</td><td><strong>{w["ticker"]}</strong></td>'
            f'<td class="num">{w["qty"]}</td><td class="num">${w["acquisition_price"]:.2f}</td>'
            f'<td class="num">${w["sale_price"]:.2f}</td>'
            f'<td class="num {"pos" if w["capital_gain"]>=0 else "neg"}">{fmt_dollar(w["capital_gain"])}</td>'
            f'<td>{w["assignment_date"]}</td><td class="num">{w["days_held"]}</td></tr>'
            for w in wheel_gains_list
        )
        appendix_a_html = f"""
<div class="dashboard" style="margin-bottom:1.5rem">
    <div class="metric-card {wg_card_class}">
        <div class="metric-value" style="color:{wg_color}">{fmt_dollar(wg_total)}</div>
        <div class="metric-label">Total Capital Gains</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{wheel_sum.get('completed_cycles', 0)}</div>
        <div class="metric-label">Wheel Cycles</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{wheel_sum.get('avg_days_held', 0)} days</div>
        <div class="metric-label">Avg Hold Period</div>
    </div>
</div>
<table>
<thead><tr><th>Date Sold</th><th>Broker</th><th>Ticker</th><th class="num">Qty</th><th class="num">Acquisition $</th><th class="num">Sale $</th><th class="num">Capital Gain</th><th>Assignment Date</th><th class="num">Days Held</th></tr></thead>
<tbody>{wg_rows}</tbody>
</table>"""
    else:
        appendix_a_html = "<p>No wheel capital gains found in this period.</p>"

    # Pre-compute annotation JSON for the f-string template
    _chart_ann = data.get("_chart_annotations", {})
    _ann_simple = {k: v for k, v in _chart_ann.items() if k not in ("sector_dist_pnl_monthly", "sector_dist_trades_monthly")}
    _ann_simple_json = json.dumps(_ann_simple)
    _ann_monthly_pnl_json = json.dumps(_chart_ann.get("sector_dist_pnl_monthly", {}))
    _ann_monthly_trades_json = json.dumps(_chart_ann.get("sector_dist_trades_monthly", {}))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Options PnL Report: CSP & Covered Calls</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ color: #1a1a1a; background-color: #fdfdfd; }}
body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0 auto; max-width: 960px; padding: 50px 60px; font-size: 15px; line-height: 1.75; hyphens: auto; overflow-wrap: break-word; text-rendering: optimizeLegibility; font-kerning: normal; -webkit-font-smoothing: antialiased; }}
nav {{ position: sticky; top: 0; background: rgba(253,253,253,0.92); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid #e6e6e6; padding: 0.6rem 0; margin: 0 -60px; padding-left: 60px; padding-right: 60px; z-index: 100; display: flex; gap: 1.5rem; flex-wrap: wrap; }}
nav a {{ text-decoration: none; color: #606060; font-size: 0.78rem; font-weight: 500; }}
nav a:hover {{ color: #1a1a1a; }}
h1 {{ font-size: 1.5rem; font-weight: 700; margin-top: 0; margin-bottom: 0.3rem; }}
h2 {{ font-size: 1.15rem; font-weight: 600; margin-top: 2.5em; margin-bottom: 0.8em; padding-bottom: 0.4em; border-bottom: 1px solid #1a1a1a; }}
h3 {{ font-size: 0.92rem; font-weight: 600; margin-top: 1.8em; margin-bottom: 0.6em; color: #333; }}
.meta {{ color: #606060; font-size: 0.82rem; margin-bottom: 2em; }}
.dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; margin: 1.5em 0; }}
.metric-card {{ background: #fdfdfd; border: 1px solid #e6e6e6; border-radius: 6px; padding: 1.1rem 1.3rem; }}
.metric-card.positive {{ border-left: 3px solid #16a34a; }}
.metric-card.negative {{ border-left: 3px solid #dc2626; }}
.metric-value {{ font-size: 1.3rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
.metric-label {{ font-size: 0.68rem; color: #606060; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }}
.win-bar {{ background: #e6e6e6; border-radius: 999px; height: 4px; margin-top: 0.5rem; overflow: hidden; }}
.win-bar-fill {{ background: #16a34a; height: 100%; border-radius: 999px; }}
table {{ width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 0.82rem; font-variant-numeric: lining-nums tabular-nums; }}
thead {{ position: sticky; top: 38px; }}
tbody {{ border-top: 1px solid #1a1a1a; border-bottom: 1px solid #1a1a1a; }}
th {{ padding: 0.4em 0.5em; text-align: left; font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.03em; color: #333; border-top: 1px solid #1a1a1a; }}
td {{ padding: 0.3em 0.5em; }}
tr:hover {{ background: #f5f5f5; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.pos {{ color: #16a34a; font-weight: 600; }}
.neg {{ color: #dc2626; font-weight: 600; }}
.chart-container {{ width: 100%; height: 300px; margin: 1.5em 0; }}
.chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
.chart-row .chart-container {{ height: 260px; }}
.trade-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.8rem; margin: 1em 0; }}
.trade-card {{ padding: 0.9rem 1rem; border-radius: 4px; border: 1px solid #e6e6e6; }}
.card-ticker {{ font-size: 0.95rem; font-weight: 700; }}
.card-pnl {{ font-size: 1.05rem; font-weight: 700; margin: 0.15rem 0; }}
.card-detail {{ font-size: 0.72rem; color: #606060; }}
.section {{ margin-bottom: 2.5em; }}
details {{ border: 1px solid #e6e6e6; border-radius: 4px; padding: 0.5rem 0.8rem; margin: 0.3rem 0; }}
details summary {{ cursor: pointer; user-select: none; font-weight: 600; font-size: 0.82rem; padding: 0.3rem 0; }}
details summary:hover {{ color: #000; }}
details[open] {{ padding-bottom: 0.6rem; }}
.back-to-top {{ text-align: right; margin-top: 1.2em; }}
.back-to-top a {{ color: #606060; font-size: 0.72rem; text-decoration: none; }}
.back-to-top a:hover {{ color: #1a1a1a; }}
#TOC {{ margin: 2em 0; padding: 1.2em 1.5em; border: 1px solid #e6e6e6; border-radius: 4px; }}
#TOC h3 {{ margin: 0 0 0.8em; font-size: 0.78rem; color: #606060; text-transform: uppercase; letter-spacing: 0.05em; }}
#TOC ul {{ list-style: none; padding-left: 0; }}
#TOC li {{ padding: 0.2em 0; }}
#TOC a {{ color: #1a1a1a; text-decoration: none; font-size: 0.85rem; }}
#TOC a:hover {{ text-decoration: underline; }}
@media (max-width: 768px) {{
    body {{ padding: 20px; max-width: 100%; }}
    nav {{ margin: 0 -20px; padding-left: 20px; padding-right: 20px; }}
    .chart-row {{ grid-template-columns: 1fr; }}
    .dashboard {{ grid-template-columns: 1fr 1fr; }}
}}
@media print {{
    nav {{ display: none; }}
    body {{ max-width: 100%; padding: 0; }}
    .chart-container {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body id="top">
<nav>
    <a href="#summary">PnL Summary</a>
    <a href="#sectors">Sectors</a>
    <a href="#details">Performance</a>
    <a href="#strategy">Strategy</a>
    <a href="#trades">Trades</a>
    <a href="#appendix-a">Appendix A</a>
    <a href="#appendix-b">Appendix B</a>
    <a href="#appendix-c">Appendix C</a>
</nav>

<h1>Options PnL Report: CSP & Covered Calls</h1>
<div class="meta">Generated {data['generated']} | Period: {data['period_start']} to {data['period_end']} | Fidelity, Tastytrade, Thinkorswim</div>

<div id="TOC">
<h3>Contents</h3>
<ul>
{"".join(f'<li><a href="#{anchor}">{title}</a></li>' for title, anchor in REPORT_SECTIONS)}
</ul>
</div>

<!-- Section 1: PnL Summary -->
<section id="summary" class="section">
<h2>PnL Summary</h2>

<h3>Summary</h3>
<div class="dashboard">
    <div class="metric-card {'positive' if full_pnl_total >= 0 else 'negative'}">
        <div class="metric-value" style="color:{'#22c55e' if full_pnl_total >= 0 else '#ef4444'}">{fmt_dollar(full_pnl_total)}</div>
        <div class="metric-label">Total Full PnL</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{full_trade_count}</div>
        <div class="metric-label">Total Trades</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{fmt_pct(s['win_rate'])}</div>
        <div class="metric-label">Win Rate</div>
        <div class="win-bar"><div class="win-bar-fill" style="width:{s['win_rate']}%"></div></div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{fmt_dollar(full_pnl_total / max(full_trade_count, 1))}</div>
        <div class="metric-label">Avg PnL / Trade</div>
    </div>
</div>

<h3>Top Winners & Losers</h3>
<div class="trade-cards">
{top_cards}
{bottom_cards}
</div>

<h3>Monthly Breakdown</h3>
<table>
<thead><tr><th>Month</th><th class="num">Trades</th><th class="num">Gross PnL</th><th class="num">Fees</th><th class="num">Net PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>{monthly_rows}</tbody>
</table>

<h3>Cumulative PnL</h3>
<div class="chart-container" id="chart-cumulative"></div>

<h3>Monthly PnL Waterfall</h3>
<div class="chart-container" id="chart-waterfall" style="height:250px"></div>

<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<!-- Section 2: Sector Insights -->
<section id="sectors" class="section">
<h2>Sector Insights</h2>

<h3>Distribution Over Months (% of PnL)</h3>
<div class="chart-container" id="chart-sector-dist-pnl" style="height:350px"></div>

<h3>Sector x Month PnL Heatmap</h3>
<div class="chart-container" id="chart-sector-month" style="height:300px"></div>

<h3>Distribution Over Months (% of trades)</h3>
<div class="chart-container" id="chart-sector-dist" style="height:350px"></div>

<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<!-- Section 3: Detailed Performance Breakdown -->
<section id="details" class="section">
<h2>Detailed Performance Breakdown</h2>

<h3>Cumulative PnL by Broker</h3>
<div class="chart-container" id="chart-broker-lines"></div>

<div class="chart-row">
<div>
<h3>PnL Distribution</h3>
<div class="chart-container" id="chart-histogram"></div>
</div>
<div>
<h3>Days Held vs PnL</h3>
<div class="chart-container" id="chart-scatter"></div>
</div>
</div>

<h3>Ticker x Month PnL Heatmap</h3>
<div class="chart-container" id="chart-ticker-month" style="height:380px"></div>

<h3>Ticker x Win Rate Heatmap</h3>
<div class="chart-container" id="chart-ticker-winrate" style="height:380px"></div>

<div class="chart-row">
<div>
<h3>Broker x Strategy PnL</h3>
<div class="chart-container" id="chart-broker-strat" style="height:220px"></div>
</div>
<div>
<h3>Holding Period x PnL Outcome</h3>
<div class="chart-container" id="chart-hold-outcome" style="height:220px"></div>
</div>
</div>

<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<!-- Strategy & Underlying (part of Section 1 conceptually, kept as sub-sections for nav) -->
<section id="strategy" class="section">
<h3>Strategy Breakdown</h3>
<table>
<thead><tr><th>Strategy</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Win Rate</th><th class="num">Avg PnL/Trade</th></tr></thead>
<tbody>
{"".join(f'<tr><td>{st["label"]}</td><td class="num">{st["trades"]}</td><td class="num {"pos" if st["net_pnl"]>=0 else "neg"}">{fmt_dollar(st["net_pnl"])}</td><td class="num">{fmt_pct(st["win_rate"])}</td><td class="num">{fmt_dollar(st["avg_pnl"])}</td></tr>' for st in data['by_strategy'])}
</tbody>
</table>

<h3>PnL by Underlying (Top 10)</h3>
<table>
<thead><tr><th>Underlying</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Avg PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>
{"".join(f'<tr><td><strong>{u["underlying"]}</strong></td><td class="num">{u["trades"]}</td><td class="num pos">{fmt_dollar(u["net_pnl"])}</td><td class="num">{fmt_dollar(u["avg_pnl"])}</td><td class="num">{fmt_pct(u["win_rate"])}</td></tr>' for u in (data['by_underlying'].get('top_10', []) if isinstance(data['by_underlying'], dict) else data['by_underlying'][:10]))}
</tbody>
</table>

<h3>PnL by Underlying (Bottom 10)</h3>
<table>
<thead><tr><th>Underlying</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Avg PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>
{"".join(f'<tr><td><strong>{u["underlying"]}</strong></td><td class="num">{u["trades"]}</td><td class="num neg">{fmt_dollar(u["net_pnl"])}</td><td class="num">{fmt_dollar(u["avg_pnl"])}</td><td class="num">{fmt_pct(u["win_rate"])}</td></tr>' for u in (data['by_underlying'].get('bottom_10', []) if isinstance(data['by_underlying'], dict) else data['by_underlying'][-10:]))}
</tbody>
</table>
<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<!-- Section 4: All Closed Trades -->
<section id="trades" class="section">
<h2>All Closed Trades ({len(closed)})</h2>
{trades_rows}

<h3>Excluded Trades</h3>
<table>
<thead><tr><th>Category</th><th class="num">Count</th><th>Reason</th></tr></thead>
<tbody>
<tr><td>Long options (Buy to Open)</td><td class="num">{data['excluded']['long_options']}</td><td>Not CSP/CC</td></tr>
<tr><td>Spread legs</td><td class="num">{data['excluded']['spread_legs']}</td><td>Multi-leg strategy</td></tr>
<tr><td>Stock trades</td><td class="num">{data['excluded']['stock_trades']}</td><td>Non-options</td></tr>
</tbody>
</table>
<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<section id="appendix-a" class="section">
<h2>Appendix A: CSP/CC Premium Only</h2>
<p>Option premium PnL only (excludes stock wheeling capital gains).</p>
<div class="dashboard" style="margin-bottom:1.5rem">
    <div class="metric-card {'positive' if s['total_net_pnl']>=0 else 'negative'}">
        <div class="metric-value" style="color:{'#22c55e' if s['total_net_pnl']>=0 else '#ef4444'}">{fmt_dollar(s['total_net_pnl'])}</div>
        <div class="metric-label">Net Premium PnL</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{s['total_trades']}</div>
        <div class="metric-label">Total Option Trades</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{fmt_pct(s['win_rate'])}</div>
        <div class="metric-label">Win Rate</div>
        <div class="win-bar"><div class="win-bar-fill" style="width:{s['win_rate']}%"></div></div>
    </div>
</div>
<table>
<thead><tr><th>Metric</th><th class="num">Value</th></tr></thead>
<tbody>
<tr><td>Average Win</td><td class="num pos">{fmt_dollar(s['avg_win'])}</td></tr>
<tr><td>Average Loss</td><td class="num neg">{fmt_dollar(s['avg_loss'])}</td></tr>
<tr><td>Largest Win</td><td class="num pos">{fmt_dollar(s['largest_win'])}</td></tr>
<tr><td>Largest Loss</td><td class="num neg">{fmt_dollar(s['largest_loss'])}</td></tr>
</tbody>
</table>
<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<section id="appendix-b" class="section">
<h2>Appendix B: Stock Wheeling Capital Gains</h2>
<p>Capital gains from stocks acquired via CSP assignment and subsequently sold.</p>
{appendix_a_html}
<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<section id="appendix-c" class="section">
<h2>Appendix C: Additional Charts</h2>
<p style="font-size:0.82rem;color:#606060;margin-bottom:1.5rem">Charts moved from the main body — redundant with main-section charts or uninformative at current win rate ({fmt_pct(s['win_rate'])}). Re-evaluate if win rate drops below 92%.</p>

<h3>Weekly Net PnL</h3>
<div class="chart-container" id="chart-weekly-bar"></div>

<h3>Sector x Win Rate Heatmap</h3>
<div class="chart-container" id="chart-sector-winrate" style="height:300px"></div>

<h3>Sector x Win/Loss Streak Heatmap</h3>
<div class="chart-container" id="chart-sector-streak" style="height:300px"></div>

<h3>Ticker x Win/Loss Streak Heatmap</h3>
<div class="chart-container" id="chart-ticker-streak" style="height:380px"></div>

<h3>Win/Loss Streak</h3>
<div class="chart-container" id="chart-streak" style="height:120px"></div>

<div class="chart-row">
<div>
<h3>Calendar Heatmap</h3>
<div class="chart-container" id="chart-calendar" style="height:200px"></div>
</div>
<div>
<h3>Broker Allocation</h3>
<div class="chart-container" id="chart-broker-donut" style="height:250px"></div>
</div>
</div>

<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>
</section>

<script>
// Cumulative PnL with Drawdown
echarts.init(document.getElementById('chart-cumulative')).setOption({{
    tooltip: {{trigger:'axis'}},
    xAxis: {{type:'category', data:{week_labels}, axisLabel:{{rotate:45,fontSize:10}}}},
    yAxis: {{type:'value', axisLabel:{{formatter:'${{}}'}} }},
    series: [
        {{name:'Cumulative PnL', type:'line', data:{cum_line_json}, smooth:true, lineStyle:{{width:3,color:'#3b82f6'}}, areaStyle:{{color:'rgba(59,130,246,0.05)'}}}},
        {{name:'Drawdown', type:'line', data:{drawdown_json}, smooth:true, lineStyle:{{width:2,color:'#ef4444',type:'dashed'}}, areaStyle:{{color:'rgba(239,68,68,0.1)'}}}},
    ]
}});

// Monthly Waterfall
echarts.init(document.getElementById('chart-waterfall')).setOption({{
    tooltip: {{}},
    xAxis: {{type:'category', data:{waterfall_labels}}},
    yAxis: {{type:'value', axisLabel:{{formatter:'${{}}'}}}},
    series: [{{
        type:'bar', data:{json.dumps([{"value": round(m["net_pnl"],2), "itemStyle":{"color":"#22c55e" if m["net_pnl"]>=0 else "#ef4444"}} for m in monthly])},
        barWidth:'60%', label:{{show:true, position:'top', formatter:function(p){{return '$'+p.value.toLocaleString()}}}}
    }}]
}});

// Weekly Bar
echarts.init(document.getElementById('chart-weekly-bar')).setOption({{
    tooltip: {{trigger:'axis'}},
    xAxis: {{type:'category', data:{week_labels}, axisLabel:{{rotate:45,fontSize:9}}}},
    yAxis: {{type:'value', axisLabel:{{formatter:'${{}}'}}}},
    series: [{{type:'bar', data:{json.dumps([{"value":w["net_pnl"],"itemStyle":{"color":"#22c55e" if w["net_pnl"]>=0 else "#ef4444"}} for w in weekly])}}}]
}});

// Broker Lines
var brokerChart = echarts.init(document.getElementById('chart-broker-lines'));
brokerChart.setOption({{
    tooltip: {{trigger:'axis'}},
    legend: {{top:0}},
    xAxis: {{type:'category', data:{json.dumps(max((bd["labels"] for bd in broker_datasets), key=len) if broker_datasets else [])}, axisLabel:{{rotate:45,fontSize:9}}}},
    yAxis: {{type:'value', axisLabel:{{formatter:'${{}}'}}}},
    series: {json.dumps([{"name":bd["label"],"type":"line","data":bd["data"],"smooth":True,"lineStyle":{"width":2,"color":bd["color"]},"itemStyle":{"color":bd["color"]}} for bd in broker_datasets])}
}});

// Histogram
echarts.init(document.getElementById('chart-histogram')).setOption({{
    tooltip: {{}},
    xAxis: {{type:'category', data:{hist_labels}, axisLabel:{{rotate:45,fontSize:9}}}},
    yAxis: {{type:'value', name:'Count'}},
    series: [{{type:'bar', data:{json.dumps([{"value":c,"itemStyle":{"color":"#22c55e" if b>=0 else "#ef4444"}} for b,c in hist_sorted])}}}]
}});

// Scatter
echarts.init(document.getElementById('chart-scatter')).setOption({{
    tooltip: {{trigger:'item'}},
    legend: {{top:0}},
    xAxis: {{type:'value', name:'Days Held'}},
    yAxis: {{type:'value', name:'Net PnL ($)', axisLabel:{{formatter:'${{}}'}}}},
    series: [
        {{name:'CSP', type:'scatter', data:{scatter_csp}, itemStyle:{{color:'#f97316',opacity:0.7}}, symbolSize:8}},
        {{name:'CC', type:'scatter', data:{scatter_cc}, itemStyle:{{color:'#3b82f6',opacity:0.7}}, symbolSize:8}}
    ]
}});

// Calendar Heatmap
var calData = {cal_data};
var startDate = calData.length > 0 ? calData[0][0] : '2025-09-01';
var endDate = calData.length > 0 ? calData[calData.length-1][0] : '2025-12-31';
echarts.init(document.getElementById('chart-calendar')).setOption({{
    tooltip: {{formatter: function(p){{return p.data[0]+': $'+p.data[1].toLocaleString()}}}},
    visualMap: {{min:-500, max:500, show:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    calendar: {{range:[startDate.slice(0,7), endDate.slice(0,7)], cellSize:['auto',15], top:30, left:50, right:30}},
    series: [{{type:'heatmap', coordinateSystem:'calendar', data:calData}}]
}});

// Broker Donut
echarts.init(document.getElementById('chart-broker-donut')).setOption({{
    tooltip: {{}},
    series: [{{type:'pie', radius:['45%','75%'], label:{{formatter:'{{b}}\\n${{c}}'}},
        data:{json.dumps([{"name":k,"value":round(v,2),"itemStyle":{"color":broker_colors.get(k,"#6b7280")}} for k,v in broker_pnl.items()])}
    }}]
}});

// Win/Loss Streak
echarts.init(document.getElementById('chart-streak')).setOption({{
    tooltip: {{trigger:'item', formatter:function(p){{return 'Trade '+p.dataIndex+': $'+p.value.toLocaleString()}}}},
    xAxis: {{type:'category', show:false, data:Array.from({{length:{len(closed)}}},(_,i)=>i)}},
    yAxis: {{show:false}},
    series: [{{type:'bar', data:{json.dumps([{"value":abs(t["net_pnl"]),"itemStyle":{"color":"#22c55e" if t["net_pnl"]>0 else "#ef4444"}} for t in closed])}, barWidth:'80%'}}]
}});

// Sortable table
document.querySelectorAll('#trades-table th').forEach((th, i) => {{
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {{
        const table = document.getElementById('trades-table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
        th.dataset.dir = dir;
        rows.sort((a, b) => {{
            let av = a.cells[i].textContent.replace(/[$,]/g,'');
            let bv = b.cells[i].textContent.replace(/[$,]/g,'');
            let an = parseFloat(av), bn = parseFloat(bv);
            if (!isNaN(an) && !isNaN(bn)) return dir==='asc' ? an-bn : bn-an;
            return dir==='asc' ? av.localeCompare(bv) : bv.localeCompare(av);
        }});
        rows.forEach(r => tbody.appendChild(r));
    }});
}});

// Ticker x Month PnL Heatmap
echarts.init(document.getElementById('chart-ticker-month')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return p.data[2] ? {heatmap_tickers_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': $' + p.data[2].toLocaleString() : ''; }} }},
    grid: {{left:140, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{heatmap_tickers_json}, splitArea:{{show:true}}}},
    visualMap: {{min:-{heatmap_max}, max:{heatmap_max}, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{heatmap_data_json}, label:{{show:true, formatter:function(p){{return p.data[2]?'$'+Math.round(p.data[2]):''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Sector x Month PnL Heatmap
echarts.init(document.getElementById('chart-sector-month')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return p.data[2] ? {sectors_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': $' + p.data[2].toLocaleString() : ''; }} }},
    grid: {{left:120, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{sectors_json}, splitArea:{{show:true}}}},
    visualMap: {{min:-{sector_pnl_max}, max:{sector_pnl_max}, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{sector_pnl_data_json}, label:{{show:true, formatter:function(p){{return p.data[2]?'$'+Math.round(p.data[2]):''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Ticker x Win Rate Heatmap
echarts.init(document.getElementById('chart-ticker-winrate')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return p.data[2]!=null ? {winrate_tickers_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': ' + p.data[2] + '%' : ''; }} }},
    grid: {{left:140, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{winrate_tickers_json}, splitArea:{{show:true}}}},
    visualMap: {{min:0, max:100, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fbbf24','#22c55e']}}}},
    series: [{{type:'heatmap', data:{winrate_data_json}, label:{{show:true, formatter:function(p){{return p.data[2]!=null?p.data[2]+'%':''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Sector x Win Rate Heatmap
echarts.init(document.getElementById('chart-sector-winrate')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return p.data[2]!=null ? {sectors_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': ' + p.data[2] + '%' : ''; }} }},
    grid: {{left:120, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{sectors_json}, splitArea:{{show:true}}}},
    visualMap: {{min:0, max:100, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fbbf24','#22c55e']}}}},
    series: [{{type:'heatmap', data:{sector_winrate_data_json}, label:{{show:true, formatter:function(p){{return p.data[2]!=null?p.data[2]+'%':''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Ticker x Win/Loss Streak Heatmap
echarts.init(document.getElementById('chart-ticker-streak')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ var v=p.data[2]; return v ? {heatmap_tickers_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': ' + (v>0?'+':'')+v+' streak' : ''; }} }},
    grid: {{left:140, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{heatmap_tickers_json}, splitArea:{{show:true}}}},
    visualMap: {{min:-{streak_max}, max:{streak_max}, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{streak_data_json}, label:{{show:true, formatter:function(p){{var v=p.data[2]; return v?(v>0?'+':'')+v:''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Sector x Win/Loss Streak Heatmap
echarts.init(document.getElementById('chart-sector-streak')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ var v=p.data[2]; return v ? {sectors_json}[p.data[1]] + ' / ' + {heatmap_months_json}[p.data[0]] + ': ' + (v>0?'+':'')+v+' streak' : ''; }} }},
    grid: {{left:120, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{sectors_json}, splitArea:{{show:true}}}},
    visualMap: {{min:-{sector_streak_max}, max:{sector_streak_max}, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{sector_streak_data_json}, label:{{show:true, formatter:function(p){{var v=p.data[2]; return v?(v>0?'+':'')+v:''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
}});

// Sector Distribution Over Months (stacked bar %)
echarts.init(document.getElementById('chart-sector-dist')).setOption({{
    tooltip: {{trigger:'axis', axisPointer:{{type:'shadow'}}, formatter: function(params){{
        var s = params[0].axisValue + '<br/>';
        params.forEach(function(p){{ if(p.data>0) s += p.marker + p.seriesName + ': ' + p.data + '%<br/>'; }});
        return s;
    }} }},
    legend: {{type:'plain', top:0, left:'center', itemWidth:12, itemHeight:12, textStyle:{{fontSize:10}}, itemGap:8, width:'90%'}},
    grid: {{left:50, right:20, top:60, bottom:20}},
    xAxis: {{type:'category', data:{heatmap_months_json}}},
    yAxis: {{type:'value', max:100, axisLabel:{{formatter:'{{value}}%'}}}},
    series: {sector_dist_series_json}
}});

// Sector Distribution Over Months (stacked bar % of PnL)
echarts.init(document.getElementById('chart-sector-dist-pnl')).setOption({{
    tooltip: {{trigger:'axis', axisPointer:{{type:'shadow'}}, formatter: function(params){{
        var s = params[0].axisValue + '<br/>';
        params.forEach(function(p){{ if(p.data!=0) s += p.marker + p.seriesName + ': ' + p.data + '%<br/>'; }});
        return s;
    }} }},
    legend: {{type:'plain', top:0, left:'center', itemWidth:12, itemHeight:12, textStyle:{{fontSize:10}}, itemGap:8, width:'90%'}},
    grid: {{left:50, right:20, top:60, bottom:20}},
    xAxis: {{type:'category', data:{heatmap_months_json}}},
    yAxis: {{type:'value', axisLabel:{{formatter:'{{value}}%'}}}},
    series: {sector_dist_pnl_series_json}
}});

// Broker x Strategy PnL Matrix
echarts.init(document.getElementById('chart-broker-strat')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return {matrix_strats_json}[p.data[0]] + ' / ' + {matrix_brokers_json}[p.data[1]] + ': $' + p.data[2].toLocaleString(); }} }},
    grid: {{left:100, right:40, top:10, bottom:40}},
    xAxis: {{type:'category', data:{matrix_strats_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{matrix_brokers_json}, splitArea:{{show:true}}}},
    visualMap: {{show:false, min:-{matrix_max}, max:{matrix_max}, inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{matrix_data_json}, label:{{show:true, formatter:function(p){{return '$'+p.data[2].toLocaleString()}}, fontSize:13, fontWeight:'bold'}},
        itemStyle:{{borderColor:'#fff', borderWidth:2}}
    }}]
}});

// Holding Period x PnL Outcome Matrix
echarts.init(document.getElementById('chart-hold-outcome')).setOption({{
    tooltip: {{position:'top', formatter: function(p){{ return {hold_buckets_json}[p.data[1]] + ' / ' + {outcome_buckets_json}[p.data[0]] + ': ' + p.data[2] + ' trades'; }} }},
    grid: {{left:60, right:20, top:10, bottom:60}},
    xAxis: {{type:'category', data:{outcome_buckets_json}, splitArea:{{show:true}}, axisLabel:{{fontSize:10,rotate:20}}}},
    yAxis: {{type:'category', data:{hold_buckets_json}, splitArea:{{show:true}}}},
    visualMap: {{show:false, min:0, max:{hold_outcome_max}, inRange:{{color:['#ffffff','#bfdbfe','#3b82f6','#1e3a5f']}}}},
    series: [{{type:'heatmap', data:{hold_outcome_json}, label:{{show:true, formatter:function(p){{return p.data[2]||''}}, fontSize:12, fontWeight:'bold'}},
        itemStyle:{{borderColor:'#fff', borderWidth:2}}
    }}]
}});

// Responsive resize
window.addEventListener('resize', () => {{
    document.querySelectorAll('.chart-container').forEach(el => {{
        const chart = echarts.getInstanceByDom(el);
        if (chart) chart.resize();
    }});
}});

// Inject chart annotations
(function() {{
    var annotations = {_ann_simple_json};
    var monthlyPnl = {_ann_monthly_pnl_json};
    var monthlyTrades = {_ann_monthly_trades_json};
    var mapping = {{
        'cumulative_pnl': 'chart-cumulative',
        'waterfall': 'chart-waterfall',
        'weekly_pnl': 'chart-weekly-bar',
        'broker_lines': 'chart-broker-lines',
        'histogram': 'chart-histogram',
        'scatter': 'chart-scatter',
        'calendar': 'chart-calendar',
        'broker_donut': 'chart-broker-donut',
        'streak': 'chart-streak',
        'sector_distribution': 'chart-sector-dist',
        'sector_dist_pnl': 'chart-sector-dist-pnl',
        'sector_pnl': 'chart-sector-month',
        'ticker_month_pnl': 'chart-ticker-month',
        'sector_winrate': 'chart-sector-winrate',
        'ticker_winrate': 'chart-ticker-winrate',
        'sector_streak': 'chart-sector-streak',
        'ticker_streak': 'chart-ticker-streak',
        'broker_strat': 'chart-broker-strat',
        'hold_outcome': 'chart-hold-outcome'
    }};
    for (var key in mapping) {{
        if (annotations[key]) {{
            var el = document.getElementById(mapping[key]);
            if (el) {{
                var p = document.createElement('p');
                var text = annotations[key];
                var isRisk = text.indexOf('[Risk]') === 0;
                p.style.cssText = 'font-size:0.78rem;font-style:italic;margin:-0.75rem 0 1.5rem;padding:0 0.25rem;color:' + (isRisk ? '#d97706' : '#606060');
                if (isRisk) p.style.fontWeight = '500';
                p.textContent = text;
                el.parentNode.insertBefore(p, el.nextSibling);
            }}
        }}
    }}
    // Inject monthly sector PnL breakdown below sector-dist-pnl chart
    var pnlEl = document.getElementById('chart-sector-dist-pnl');
    if (pnlEl && Object.keys(monthlyPnl).length > 0) {{
        var details = document.createElement('details');
        details.style.cssText = 'margin:-0.5rem 0 1.5rem;font-size:0.78rem;color:#606060';
        var summary = document.createElement('summary');
        summary.style.cssText = 'cursor:pointer;font-style:italic';
        summary.textContent = annotations['sector_dist_pnl'] || 'Monthly sector PnL breakdown';
        details.appendChild(summary);
        var container = document.createElement('div');
        container.style.cssText = 'margin:0.6rem 0 0;line-height:2';
        var months = Object.keys(monthlyPnl).sort().reverse();
        months.forEach(function(m) {{
            var div = document.createElement('div');
            div.style.cssText = 'margin-bottom:0.5rem;padding:0.4rem 0;border-bottom:1px solid #f0f0f0';
            var top3 = monthlyPnl[m].top3.map(function(s){{
                return '<span style="color:#16a34a;font-weight:600">• ' + s.sector + '</span> <span style="color:#16a34a">$' + s.pnl.toLocaleString(undefined,{{maximumFractionDigits:0}}) + ' (' + s.pct + '%)</span>';
            }}).join('&nbsp;&nbsp;');
            var bot3 = monthlyPnl[m].bottom3.map(function(s){{
                return '<span style="color:#dc2626;font-weight:600">• ' + s.sector + '</span> <span style="color:#dc2626">$' + s.pnl.toLocaleString(undefined,{{maximumFractionDigits:0}}) + ' (' + s.pct + '%)</span>';
            }}).join('&nbsp;&nbsp;');
            var riskLine = monthlyPnl[m].risk ? '<br><span style="font-size:0.72rem;color:#d97706;font-weight:500">' + monthlyPnl[m].risk + '</span>' : '';
            div.innerHTML = '<strong>' + m + '</strong><br><span style="font-size:0.72rem">Top: ' + top3 + '</span><br><span style="font-size:0.72rem">Bottom: ' + bot3 + '</span>' + riskLine;
            container.appendChild(div);
        }});
        details.appendChild(container);
        pnlEl.parentNode.insertBefore(details, pnlEl.nextSibling);
    }}
    // Inject monthly sector TRADES breakdown below sector-dist chart
    var tradesEl = document.getElementById('chart-sector-dist');
    if (tradesEl && Object.keys(monthlyTrades).length > 0) {{
        var details2 = document.createElement('details');
        details2.style.cssText = 'margin:-0.5rem 0 1.5rem;font-size:0.78rem;color:#606060';
        var summary2 = document.createElement('summary');
        summary2.style.cssText = 'cursor:pointer;font-style:italic';
        summary2.textContent = annotations['sector_distribution'] || 'Monthly sector trades breakdown';
        details2.appendChild(summary2);
        var container2 = document.createElement('div');
        container2.style.cssText = 'margin:0.6rem 0 0;line-height:2';
        var months2 = Object.keys(monthlyTrades).sort().reverse();
        months2.forEach(function(m) {{
            var div = document.createElement('div');
            div.style.cssText = 'margin-bottom:0.5rem;padding:0.4rem 0;border-bottom:1px solid #f0f0f0';
            var top3 = monthlyTrades[m].top3.map(function(s){{
                return '<span style="color:#16a34a;font-weight:600">• ' + s.sector + '</span> <span style="color:#16a34a">' + s.count + ' trades (' + s.pct + '%)</span>';
            }}).join('&nbsp;&nbsp;');
            var bot3 = monthlyTrades[m].bottom3.map(function(s){{
                return '<span style="color:#dc2626;font-weight:600">• ' + s.sector + '</span> <span style="color:#dc2626">' + s.count + ' trades (' + s.pct + '%)</span>';
            }}).join('&nbsp;&nbsp;');
            var riskLine2 = monthlyTrades[m].risk ? '<br><span style="font-size:0.72rem;color:#d97706;font-weight:500">' + monthlyTrades[m].risk + '</span>' : '';
            div.innerHTML = '<strong>' + m + '</strong><br><span style="font-size:0.72rem">Top: ' + top3 + '</span><br><span style="font-size:0.72rem">Bottom: ' + bot3 + '</span>' + riskLine2;
            container2.appendChild(div);
        }});
        details2.appendChild(container2);
        tradesEl.parentNode.insertBefore(details2, tradesEl.nextSibling);
    }}
}})();
</script>
</body>
</html>"""

    return html


def backup_existing(out_dir: Path):
    """Backup existing -latest reports with -YYYY-MM-DD-HH suffix before overwriting."""
    import shutil
    now = datetime.now()
    suffix = now.strftime("-%Y-%m-%d-%H")

    for name in ["pnl-report-latest.md", "pnl-report-latest.html"]:
        existing = out_dir / name
        if existing.exists():
            ext = name.rsplit(".", 1)[1]
            backup_name = f"pnl-report{suffix}.{ext}"
            backup_path = out_dir / backup_name
            shutil.copy2(existing, backup_path)
            print(f"Backup: {existing.name} -> {backup_name}")


def main():
    parser = argparse.ArgumentParser(description="Render PnL report from JSON")
    parser.add_argument("--input", required=True, help="Path to computed-pnl.json")
    parser.add_argument("--output-dir", required=True, help="Output directory for .md and .html")
    parser.add_argument("--start-date", help="Start date for filename suffix (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for filename suffix (YYYY-MM-DD)")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    # Load insights.json if present (same directory as input)
    insights_path = Path(args.input).parent / "insights.json"
    if insights_path.exists():
        with open(insights_path) as f:
            raw_insights = json.load(f)
        # Support both old format (flat month keys) and new format (monthly + chart_annotations)
        if "monthly" in raw_insights:
            data["_insights"] = raw_insights["monthly"]
            data["_chart_annotations"] = raw_insights.get("chart_annotations", {})
        else:
            data["_insights"] = raw_insights
            data["_chart_annotations"] = {}
        print(f"Loaded insights from: {insights_path}")
    else:
        data["_insights"] = {}
        data["_chart_annotations"] = {}

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Determine filename
    if args.start_date and args.end_date:
        base_name = f"pnl-report-{args.start_date}-to-{args.end_date}"
    else:
        base_name = "pnl-report-latest"

    backup_existing(out_dir)

    md_content = generate_markdown(data)
    md_path = out_dir / f"{base_name}.md"
    md_path.write_text(md_content)
    print(f"Written: {md_path}")

    html_content = generate_html(data, args)
    html_path = out_dir / f"{base_name}.html"
    html_path.write_text(html_content)
    print(f"Written: {html_path}")


if __name__ == "__main__":
    main()
