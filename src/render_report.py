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

    # Closed Trades
    lines.append("## All Closed Trades\n")
    lines.append("| Date Closed | Month | Broker | Underlying | Strategy | Strike | Expiry | Qty | Open $ | Close $ | Net PnL |")
    lines.append("|-------------|-------|--------|------------|----------|--------|--------|-----|--------|---------|---------|")
    for t in data["closed_trades"]:
        dc = t['date_closed'] or "unknown"
        lines.append(f"| {dc} | {dc[:7]} | {t['broker']} | {t['underlying']} | {t['strategy']} | ${t['strike']:.0f} | {t['expiry'] or '?'} | {t['qty']} | ${t['open_price']:.2f} | ${t['close_price']:.2f} | {fmt_dollar(t['net_pnl'])} |")
    lines.append("")

    # Excluded
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


def generate_html(data: dict) -> str:
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

    # Build trades table rows
    trades_rows = ""
    for t in closed:
        pnl_color = "color:#22c55e" if t["net_pnl"] >= 0 else "color:#ef4444"
        trades_rows += f"""<tr>
            <td>{t['date_closed']}</td><td>{t['broker']}</td><td>{t['underlying']}</td>
            <td>{t['strategy']}</td><td>${t['strike']:.0f}</td><td>{t['expiry']}</td>
            <td>{t['qty']}</td><td>${t['open_price']:.2f}</td><td>${t['close_price']:.2f}</td>
            <td style="{pnl_color};font-weight:600">{fmt_dollar(t['net_pnl'])}</td>
        </tr>\n"""

    # Monthly table rows
    monthly_rows = ""
    for m in monthly:
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
    # Top 15 by trade count
    top_tickers_hm = sorted(ticker_trade_count.keys(), key=lambda x: ticker_trade_count[x], reverse=True)[:15]
    all_months_sorted = sorted(all_months_set)
    heatmap_data = []
    for mi, m in enumerate(all_months_sorted):
        for ti, tk in enumerate(top_tickers_hm):
            val = round(ticker_month_pnl[tk].get(m, 0), 2)
            if val != 0:
                heatmap_data.append([mi, ti, val])
    heatmap_data_json = json.dumps(heatmap_data)
    heatmap_months_json = json.dumps(all_months_sorted)
    heatmap_tickers_json = json.dumps(top_tickers_hm)
    heatmap_max = max((abs(d[2]) for d in heatmap_data), default=500)

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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Options PnL Report: CSP & Covered Calls</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; font-size: 16px; line-height: 1.6; background: #ffffff; color: #1f2937; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
nav {{ position: sticky; top: 0; background: #ffffff; border-bottom: 1px solid #e9ecef; padding: 0.75rem 2rem; z-index: 100; display: flex; gap: 1.5rem; flex-wrap: wrap; }}
nav a {{ text-decoration: none; color: #6b7280; font-size: 0.875rem; font-weight: 500; }}
nav a:hover {{ color: #3b82f6; }}
h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; }}
h2 {{ font-size: 1.25rem; font-weight: 600; margin: 2.5rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e9ecef; }}
h3 {{ font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 0.75rem; }}
.meta {{ color: #6b7280; font-size: 0.875rem; margin-bottom: 1.5rem; }}
.dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
.metric-card {{ background: #f8f9fa; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.metric-card.positive {{ background: #f0fdf4; border: 1px solid #bbf7d0; }}
.metric-card.negative {{ background: #fef2f2; border: 1px solid #fecaca; }}
.metric-value {{ font-size: 1.5rem; font-weight: 700; }}
.metric-label {{ font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }}
.win-bar {{ background: #e5e7eb; border-radius: 999px; height: 8px; margin-top: 0.5rem; overflow: hidden; }}
.win-bar-fill {{ background: #22c55e; height: 100%; border-radius: 999px; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.875rem; }}
thead {{ position: sticky; top: 48px; }}
th {{ background: #f1f5f9; padding: 0.75rem 0.5rem; text-align: left; font-weight: 600; border-bottom: 2px solid #e2e8f0; }}
td {{ padding: 0.6rem 0.5rem; border-bottom: 1px solid #f1f5f9; }}
tr:nth-child(even) {{ background: #f8fafc; }}
tr:hover {{ background: #eff6ff; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.pos {{ color: #22c55e; font-weight: 600; }}
.neg {{ color: #ef4444; font-weight: 600; }}
.chart-container {{ width: 100%; height: 300px; margin: 1.5rem 0; }}
.chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
.chart-row .chart-container {{ height: 280px; }}
.trade-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1rem 0; }}
.trade-card {{ padding: 1rem; border-radius: 8px; }}
.card-ticker {{ font-size: 1.1rem; font-weight: 700; }}
.card-pnl {{ font-size: 1.25rem; font-weight: 700; margin: 0.25rem 0; }}
.card-detail {{ font-size: 0.8rem; color: #6b7280; }}
.section {{ margin-bottom: 2rem; }}
details summary {{ cursor: pointer; user-select: none; }}
details summary h2 {{ color: #3b82f6; }}
details[open] summary h2::after {{ content: ''; }}
details {{ border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; }}
@media (max-width: 768px) {{
    .chart-row {{ grid-template-columns: 1fr; }}
    .dashboard {{ grid-template-columns: 1fr 1fr; }}
    nav {{ padding: 0.5rem 1rem; }}
    .container {{ padding: 1rem; }}
}}
@media print {{
    nav {{ display: none; }}
    .chart-container {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>

<nav>
    <a href="#summary">Summary</a>
    <a href="#charts">Charts</a>
    <a href="#monthly">Monthly</a>
    <a href="#strategy">Strategy</a>
    <a href="#underlying">By Ticker</a>
    <a href="#trades">All Trades</a>
    <a href="#appendix-a">Appendix A</a>
    <a href="#appendix-b">Appendix B</a>
</nav>

<div class="container">

<h1>Options PnL Report: CSP & Covered Calls</h1>
<div class="meta">Generated {data['generated']} | Period: {data['period_start']} to {data['period_end']} | Fidelity, Tastytrade, Thinkorswim</div>

<section id="summary" class="section">
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
</section>

<section id="charts" class="section">
<h2>Performance Charts</h2>

<h3>Cumulative PnL with Drawdown</h3>
<div class="chart-container" id="chart-cumulative"></div>

<h3>Monthly PnL Waterfall</h3>
<div class="chart-container" id="chart-waterfall" style="height:250px"></div>

<div class="chart-row">
<div>
<h3>Weekly Net PnL</h3>
<div class="chart-container" id="chart-weekly-bar"></div>
</div>
<div>
<h3>Cumulative PnL by Broker</h3>
<div class="chart-container" id="chart-broker-lines"></div>
</div>
</div>

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

<h3>Win/Loss Streak</h3>
<div class="chart-container" id="chart-streak" style="height:120px"></div>

<h3>Ticker x Month PnL Heatmap</h3>
<div class="chart-container" id="chart-ticker-month" style="height:380px"></div>

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

</section>

<section id="monthly" class="section">
<h2>Monthly Summary</h2>
<table>
<thead><tr><th>Month</th><th class="num">Trades</th><th class="num">Gross PnL</th><th class="num">Fees</th><th class="num">Net PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>{monthly_rows}</tbody>
</table>
</section>

<section id="strategy" class="section">
<h2>Strategy Breakdown</h2>
<table>
<thead><tr><th>Strategy</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Win Rate</th><th class="num">Avg PnL/Trade</th></tr></thead>
<tbody>
{"".join(f'<tr><td>{st["label"]}</td><td class="num">{st["trades"]}</td><td class="num {"pos" if st["net_pnl"]>=0 else "neg"}">{fmt_dollar(st["net_pnl"])}</td><td class="num">{fmt_pct(st["win_rate"])}</td><td class="num">{fmt_dollar(st["avg_pnl"])}</td></tr>' for st in data['by_strategy'])}
</tbody>
</table>
</section>

<section id="underlying" class="section">
<h2>PnL by Underlying (Top 10)</h2>
<table>
<thead><tr><th>Underlying</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Avg PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>
{"".join(f'<tr><td><strong>{u["underlying"]}</strong></td><td class="num">{u["trades"]}</td><td class="num pos">{fmt_dollar(u["net_pnl"])}</td><td class="num">{fmt_dollar(u["avg_pnl"])}</td><td class="num">{fmt_pct(u["win_rate"])}</td></tr>' for u in (data['by_underlying'].get('top_10', []) if isinstance(data['by_underlying'], dict) else data['by_underlying'][:10]))}
</tbody>
</table>

<h2>PnL by Underlying (Bottom 10)</h2>
<table>
<thead><tr><th>Underlying</th><th class="num">Trades</th><th class="num">Net PnL</th><th class="num">Avg PnL</th><th class="num">Win Rate</th></tr></thead>
<tbody>
{"".join(f'<tr><td><strong>{u["underlying"]}</strong></td><td class="num">{u["trades"]}</td><td class="num neg">{fmt_dollar(u["net_pnl"])}</td><td class="num">{fmt_dollar(u["avg_pnl"])}</td><td class="num">{fmt_pct(u["win_rate"])}</td></tr>' for u in (data['by_underlying'].get('bottom_10', []) if isinstance(data['by_underlying'], dict) else data['by_underlying'][-10:]))}
</tbody>
</table>
</section>

<section id="trades" class="section">
<details>
<summary><h2 style="display:inline;cursor:pointer">All Closed Trades ({len(closed)}) &#9660;</h2></summary>
<table id="trades-table">
<thead><tr><th>Date Closed</th><th>Broker</th><th>Underlying</th><th>Strategy</th><th class="num">Strike</th><th>Expiry</th><th class="num">Qty</th><th class="num">Open $</th><th class="num">Close $</th><th class="num">Net PnL</th></tr></thead>
<tbody>{trades_rows}</tbody>
</table>
</details>
</section>

<section class="section">
<h2>Excluded Trades</h2>
<table>
<thead><tr><th>Category</th><th class="num">Count</th><th>Reason</th></tr></thead>
<tbody>
<tr><td>Long options (Buy to Open)</td><td class="num">{data['excluded']['long_options']}</td><td>Not CSP/CC</td></tr>
<tr><td>Spread legs</td><td class="num">{data['excluded']['spread_legs']}</td><td>Multi-leg strategy</td></tr>
<tr><td>Stock trades</td><td class="num">{data['excluded']['stock_trades']}</td><td>Non-options</td></tr>
</tbody>
</table>
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
</section>

<section id="appendix-b" class="section">
<h2>Appendix B: Stock Wheeling Capital Gains</h2>
<p>Capital gains from stocks acquired via CSP assignment and subsequently sold.</p>
{appendix_a_html}
</section>

</div>

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
    grid: {{left:80, right:40, top:10, bottom:60}},
    xAxis: {{type:'category', data:{heatmap_months_json}, splitArea:{{show:true}}}},
    yAxis: {{type:'category', data:{heatmap_tickers_json}, splitArea:{{show:true}}}},
    visualMap: {{min:-{heatmap_max}, max:{heatmap_max}, calculable:true, orient:'horizontal', left:'center', bottom:0,
        inRange:{{color:['#ef4444','#fecaca','#ffffff','#bbf7d0','#22c55e']}}}},
    series: [{{type:'heatmap', data:{heatmap_data_json}, label:{{show:true, formatter:function(p){{return p.data[2]?'$'+Math.round(p.data[2]):''}}, fontSize:10}},
        emphasis:{{itemStyle:{{shadowBlur:5,shadowColor:'rgba(0,0,0,0.3)'}}}}
    }}]
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

    html_content = generate_html(data)
    html_path = out_dir / f"{base_name}.html"
    html_path.write_text(html_content)
    print(f"Written: {html_path}")


if __name__ == "__main__":
    main()
