#!/usr/bin/env python3
"""
Analyze computed PnL data and generate monthly insights (rule engine + LLM polish).

Usage:
    python3 src/analyze_insights.py \
        --input .local/data/options-pnl/out/computed-pnl.json \
        --sector-map .local/data/options-pnl/sector-map.json \
        --output .local/data/options-pnl/out/insights.json
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict


def load_sector_map(path):
    if Path(path).exists():
        with open(path) as f:
            sm = json.load(f)
        t2s = {}
        for sec, tickers in sm.items():
            for tk in tickers:
                t2s[tk] = sec
        return t2s
    return {}


def detect_streaks(results):
    """Given a list of +1 (win) / -1 (loss), return (max_win_streak, max_loss_streak)."""
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
    return max_win, abs(max_loss)


def analyze_month(month, trades, all_months_data, t2s, ticker_history):
    """Analyze a single month's trades and return signals."""
    signals = []
    if not trades:
        return signals

    month_net = sum(t["net_pnl"] for t in trades)
    month_wins = sum(1 for t in trades if t["net_pnl"] > 0)
    month_wr = month_wins / len(trades) * 100 if trades else 0

    # Group by ticker
    by_ticker = defaultdict(list)
    for t in trades:
        by_ticker[t["underlying"]].append(t)

    # Group by sector
    by_sector = defaultdict(list)
    for t in trades:
        sec = t2s.get(t["underlying"], "Other")
        by_sector[sec].append(t)

    # --- REPEAT signals ---

    # Hot streak: ticker with 3+ consecutive wins
    for ticker, ttrades in by_ticker.items():
        results = [1 if t["net_pnl"] > 0 else -1 for t in ttrades]
        win_streak, _ = detect_streaks(results)
        if win_streak >= 3:
            avg_pnl = sum(t["net_pnl"] for t in ttrades) / len(ttrades)
            strikes = sorted(set(t["strike"] for t in ttrades))
            strikes_str = f"${strikes[0]:.0f}-${strikes[-1]:.0f}" if len(strikes) > 1 else f"${strikes[0]:.0f}"
            signals.append({
                "category": "repeat",
                "signal": "hot_streak",
                "ticker": ticker,
                "detail": f"{win_streak} consecutive wins at {strikes_str} strikes",
                "data": {"streak_length": win_streak, "avg_pnl": round(avg_pnl, 2)}
            })

    # Best risk/reward: highest avg PnL with 100% win rate (min 2 trades)
    best_rr = None
    best_rr_avg = 0
    for ticker, ttrades in by_ticker.items():
        if len(ttrades) >= 2 and all(t["net_pnl"] > 0 for t in ttrades):
            avg = sum(t["net_pnl"] for t in ttrades) / len(ttrades)
            if avg > best_rr_avg:
                best_rr_avg = avg
                best_rr = (ticker, ttrades)
    if best_rr and best_rr_avg > 150:
        ticker, ttrades = best_rr
        signals.append({
            "category": "repeat",
            "signal": "best_risk_reward",
            "ticker": ticker,
            "detail": f"{len(ttrades)} trades, 100% win rate, avg ${best_rr_avg:.0f}/trade",
            "data": {"trades": len(ttrades), "avg_pnl": round(best_rr_avg, 2)}
        })

    # Sector strength: sector with 100% win rate and 3+ trades
    for sec, strades in by_sector.items():
        if len(strades) >= 3 and all(t["net_pnl"] > 0 for t in strades):
            sec_net = sum(t["net_pnl"] for t in strades)
            signals.append({
                "category": "repeat",
                "signal": "sector_strength",
                "ticker": sec,
                "detail": f"{len(strades)} trades, 100% win rate, ${sec_net:.0f} total",
                "data": {"trades": len(strades), "net_pnl": round(sec_net, 2)}
            })

    # New ticker success
    for ticker, ttrades in by_ticker.items():
        if ticker not in ticker_history and sum(t["net_pnl"] for t in ttrades) > 0:
            signals.append({
                "category": "repeat",
                "signal": "new_ticker_success",
                "ticker": ticker,
                "detail": f"First appearance, profitable (${sum(t['net_pnl'] for t in ttrades):.0f})",
                "data": {"net_pnl": round(sum(t["net_pnl"] for t in ttrades), 2)}
            })

    # --- IMPROVE signals ---

    months_sorted = sorted(all_months_data.keys())
    month_idx = months_sorted.index(month) if month in months_sorted else -1

    # Low volume month (fewer trades than average)
    avg_monthly_trades = sum(len(v) for v in all_months_data.values()) / max(len(all_months_data), 1)
    if len(trades) < avg_monthly_trades * 0.6:
        signals.append({
            "category": "improve",
            "signal": "low_volume",
            "ticker": None,
            "detail": f"Only {len(trades)} trades vs {avg_monthly_trades:.0f} avg — potential missed opportunities",
            "data": {"count": len(trades), "avg": round(avg_monthly_trades, 0)}
        })

    # Smallest avg PnL/trade compared to prior months (efficiency decline)
    if month_idx > 0:
        current_avg = sum(t["net_pnl"] for t in trades) / len(trades) if trades else 0
        prior_avgs = []
        for pm in months_sorted[:month_idx]:
            pt = all_months_data[pm]
            if pt:
                prior_avgs.append(sum(t["net_pnl"] for t in pt) / len(pt))
        if prior_avgs and current_avg < min(prior_avgs):
            signals.append({
                "category": "improve",
                "signal": "efficiency_decline",
                "ticker": None,
                "detail": f"Avg PnL/trade (${current_avg:.0f}) is lowest across all months — consider higher-premium opportunities",
                "data": {"avg_pnl": round(current_avg, 2)}
            })

    # Cold streak: ticker with 2+ consecutive losses
    for ticker, ttrades in by_ticker.items():
        results = [1 if t["net_pnl"] > 0 else -1 for t in ttrades]
        _, loss_streak = detect_streaks(results)
        if loss_streak >= 2:
            total_loss = sum(t["net_pnl"] for t in ttrades if t["net_pnl"] <= 0)
            signals.append({
                "category": "improve",
                "signal": "cold_streak",
                "ticker": ticker,
                "detail": f"{loss_streak} consecutive losses (${total_loss:.0f} total)",
                "data": {"streak_length": loss_streak, "total_loss": round(total_loss, 2)}
            })

    # Concentration risk: single ticker > 30% of month's PnL
    if month_net > 0:
        for ticker, ttrades in by_ticker.items():
            ticker_net = sum(t["net_pnl"] for t in ttrades)
            if ticker_net > 0 and ticker_net / month_net > 0.30:
                pct = ticker_net / month_net * 100
                signals.append({
                    "category": "improve",
                    "signal": "concentration_risk",
                    "ticker": ticker,
                    "detail": f"{pct:.0f}% of month's PnL from one ticker (${ticker_net:.0f}/${month_net:.0f})",
                    "data": {"pct": round(pct, 1), "ticker_pnl": round(ticker_net, 2)}
                })

    # Sector dominance: one sector > 50% of trades
    for sec, strades in by_sector.items():
        if len(strades) / len(trades) > 0.50:
            pct = len(strades) / len(trades) * 100
            signals.append({
                "category": "improve",
                "signal": "sector_dominance",
                "ticker": sec,
                "detail": f"{pct:.0f}% of trades in {sec} — consider diversifying",
                "data": {"pct": round(pct, 1), "trade_count": len(strades)}
            })

    # Win rate drop vs prior month
    if month_idx > 0:
        prior_month = months_sorted[month_idx - 1]
        prior_trades = all_months_data[prior_month]
        prior_wr = sum(1 for t in prior_trades if t["net_pnl"] > 0) / len(prior_trades) * 100 if prior_trades else 100
        if month_wr < prior_wr - 10:
            signals.append({
                "category": "improve",
                "signal": "win_rate_drop",
                "ticker": None,
                "detail": f"Win rate dropped from {prior_wr:.0f}% to {month_wr:.0f}% ({prior_wr - month_wr:.0f}pt decline)",
                "data": {"prior_wr": round(prior_wr, 1), "current_wr": round(month_wr, 1)}
            })

    # Recurring loser: ticker that lost money in 2+ prior months
    for ticker, ttrades in by_ticker.items():
        if sum(t["net_pnl"] for t in ttrades) < 0:
            loss_months = 0
            for m, m_trades in all_months_data.items():
                if m >= month:
                    break
                ticker_in_m = [t for t in m_trades if t["underlying"] == ticker]
                if ticker_in_m and sum(t["net_pnl"] for t in ticker_in_m) < 0:
                    loss_months += 1
            if loss_months >= 1:
                signals.append({
                    "category": "improve",
                    "signal": "recurring_loser",
                    "ticker": ticker,
                    "detail": f"Lost money this month AND in {loss_months} prior month(s)",
                    "data": {"prior_loss_months": loss_months}
                })

    return signals


def generate_prose(month, signals, trades):
    """Convert signals into bullet points (rule-based prose, no LLM needed for deterministic output)."""
    repeat_bullets = []
    improve_bullets = []

    repeat_signals = [s for s in signals if s["category"] == "repeat"]
    improve_signals = [s for s in signals if s["category"] == "improve"]

    # Pick up to 3 repeat signals
    priority_order = ["hot_streak", "best_risk_reward", "sector_strength", "new_ticker_success"]
    repeat_sorted = sorted(repeat_signals, key=lambda s: priority_order.index(s["signal"]) if s["signal"] in priority_order else 99)
    for s in repeat_sorted[:3]:
        d = s["data"]
        if s["signal"] == "hot_streak":
            repeat_bullets.append(f"{s['ticker']}: {d['streak_length']} consecutive wins, avg ${d['avg_pnl']:,.0f}/trade at {s['detail'].split(' at ')[-1]}")
        elif s["signal"] == "best_risk_reward":
            repeat_bullets.append(f"{s['ticker']}: {d['trades']} trades at 100% win rate, avg ${d['avg_pnl']:,.0f}/trade")
        elif s["signal"] == "sector_strength":
            repeat_bullets.append(f"{s['ticker']}: {d['trades']} trades, 100% win rate, ${d['net_pnl']:,.0f} total PnL")
        elif s["signal"] == "new_ticker_success":
            repeat_bullets.append(f"{s['ticker']}: first month traded, +${d['net_pnl']:,.0f} net")

    # Pick up to 3 improve signals
    RISK_RATIONALES = {
        "cold_streak": "repeated losses suggest mispricing of risk at chosen strikes/expiries",
        "recurring_loser": "repeated losses on same name indicate structural issue with strike/expiry selection",
        "win_rate_drop": "abrupt WR decline may signal market regime change requiring recalibration",
        "concentration_risk": "single-name failure would wipe 30%+ of gains; diversification reduces this risk",
        "sector_dominance": "sector-wide drawdown would impact majority of positions simultaneously",
        "low_volume": "fewer trades means less premium income and potentially missed opportunities",
        "efficiency_decline": "declining avg PnL/trade may indicate strike selection drift or tighter premiums",
    }
    improve_priority = ["cold_streak", "recurring_loser", "win_rate_drop", "concentration_risk", "sector_dominance", "low_volume", "efficiency_decline"]
    improve_sorted = sorted(improve_signals, key=lambda s: improve_priority.index(s["signal"]) if s["signal"] in improve_priority else 99)
    for s in improve_sorted[:3]:
        d = s["data"]
        rationale = RISK_RATIONALES.get(s["signal"], "")
        if s["signal"] == "cold_streak":
            improve_bullets.append(f"[Risk] {s['ticker']}: {d['streak_length']} consecutive losses, ${d['total_loss']:,.0f} total loss — {rationale}")
        elif s["signal"] == "recurring_loser":
            improve_bullets.append(f"[Risk] {s['ticker']}: negative PnL this month + {d['prior_loss_months']} prior month(s) — {rationale}")
        elif s["signal"] == "win_rate_drop":
            improve_bullets.append(f"[Risk] Win rate: {d['current_wr']:.0f}% (down from {d['prior_wr']:.0f}% prior month, -{d['prior_wr']-d['current_wr']:.0f}pt) — {rationale}")
        elif s["signal"] == "concentration_risk":
            improve_bullets.append(f"[Risk] {s['ticker']}: {d['pct']:.0f}% of month's PnL (${d['ticker_pnl']:,.0f}) — {rationale}")
        elif s["signal"] == "sector_dominance":
            improve_bullets.append(f"[Risk] {s['ticker']}: {d['pct']:.0f}% of trades ({d['trade_count']}) in one sector — {rationale}")
        elif s["signal"] == "low_volume":
            improve_bullets.append(f"[Risk] Volume: {d['count']} trades vs {d['avg']:.0f} monthly avg ({d['count']/d['avg']*100:.0f}% of normal) — {rationale}")
        elif s["signal"] == "efficiency_decline":
            improve_bullets.append(f"[Risk] Avg PnL/trade: ${d['avg_pnl']:,.0f} — lowest across all months — {rationale}")

    # Ensure minimum 1 of each — generate quantitative fallbacks
    if not repeat_bullets:
        month_net = sum(t["net_pnl"] for t in trades)
        month_wr = sum(1 for t in trades if t["net_pnl"] > 0) / len(trades) * 100 if trades else 0
        repeat_bullets.append(f"Month net: +${month_net:,.0f} across {len(trades)} trades ({month_wr:.0f}% win rate)")
    if not improve_bullets:
        trade_count = len(trades)
        month_net = sum(t["net_pnl"] for t in trades)
        avg_per_trade = month_net / trade_count if trade_count else 0
        improve_bullets.append(f"No risk flags. Avg ${avg_per_trade:,.0f}/trade across {trade_count} trades")

    return repeat_bullets, improve_bullets


def generate_chart_annotations(closed_trades, all_months_data, t2s):
    """Generate objective, quantitative inline annotations for each chart.
    All annotations use templatized language with concrete numbers."""
    annotations = {}
    from datetime import datetime, timedelta

    by_ticker = defaultdict(list)
    by_sector = defaultdict(list)
    for t in closed_trades:
        by_ticker[t["underlying"]].append(t)
        by_sector[t2s.get(t["underlying"], "Other")].append(t)

    months_sorted = sorted(all_months_data.keys())
    n_months = len(months_sorted)
    monthly_nets = [(m, sum(t["net_pnl"] for t in all_months_data[m])) for m in months_sorted]

    # --- Cumulative PnL ---
    best_month = max(monthly_nets, key=lambda x: x[1])
    worst_month = min(monthly_nets, key=lambda x: x[1])
    if n_months >= 2:
        mom_changes = [(monthly_nets[i][1] - monthly_nets[i-1][1]) / max(abs(monthly_nets[i-1][1]), 1) * 100 for i in range(1, n_months)]
        avg_mom = sum(mom_changes) / len(mom_changes)
        annotations["cumulative_pnl"] = f"PnL grew {avg_mom:+.0f}% MoM on average. Peak: {best_month[0]} (${best_month[1]:,.0f}). Trough: {worst_month[0]} (${worst_month[1]:,.0f})."
    else:
        annotations["cumulative_pnl"] = f"Single month: ${best_month[1]:,.0f}."

    # --- Weekly PnL ---
    weekly_data = defaultdict(float)
    for t in closed_trades:
        if t["date_closed"]:
            dt = datetime.strptime(t["date_closed"], "%Y-%m-%d")
            monday = dt - timedelta(days=dt.weekday())
            weekly_data[monday.strftime("%Y-%m-%d")] += t["net_pnl"]
    weeks_sorted = sorted(weekly_data.keys())
    n_weeks = len(weeks_sorted)
    pos_weeks = sum(1 for w in weeks_sorted if weekly_data[w] > 0)
    neg_weeks = n_weeks - pos_weeks
    avg_weekly = sum(weekly_data.values()) / n_weeks if n_weeks else 0
    annotations["weekly_pnl"] = f"{pos_weeks}/{n_weeks} weeks positive ({pos_weeks/n_weeks*100:.0f}%). Avg weekly PnL: ${avg_weekly:,.0f}. {neg_weeks} red week(s)."

    # --- Sector Distribution (% trades) ---
    sectors_per_month = [len(set(t2s.get(t["underlying"], "Other") for t in all_months_data[m])) for m in months_sorted]
    if n_months >= 2:
        sector_mom_changes = [(sectors_per_month[i] - sectors_per_month[i-1]) / max(sectors_per_month[i-1], 1) * 100 for i in range(1, n_months)]
        avg_sector_mom = sum(sector_mom_changes) / len(sector_mom_changes)
        sector_trend = f"Sectors/month: {sectors_per_month[0]} → {sectors_per_month[-1]} ({avg_sector_mom:+.0f}% MoM avg)."
    else:
        sector_trend = f"{sectors_per_month[0]} sectors active."
    top_sector = max(defaultdict(int, {t2s.get(t["underlying"], "Other"): 0 for t in closed_trades}), key=lambda s: sum(1 for t in closed_trades if t2s.get(t["underlying"], "Other") == s))
    top_pct = sum(1 for t in closed_trades if t2s.get(t["underlying"], "Other") == top_sector) / len(closed_trades) * 100
    if top_pct > 30:
        annotations["sector_distribution"] = f"[Risk] Top sector by volume: {top_sector} ({top_pct:.0f}% of trades) — sector-wide event would impact {top_pct:.0f}% of positions. {sector_trend}"
    else:
        annotations["sector_distribution"] = f"Top sector by volume: {top_sector} ({top_pct:.0f}% of trades). {sector_trend}"

    # --- Sector Distribution (% PnL) ---
    sector_pnl_totals = defaultdict(float)
    for t in closed_trades:
        sector_pnl_totals[t2s.get(t["underlying"], "Other")] += t["net_pnl"]
    total_pnl = sum(sector_pnl_totals.values())
    profitable_sectors = sum(1 for v in sector_pnl_totals.values() if v > 0)
    sorted_sectors_pnl = sorted(sector_pnl_totals.items(), key=lambda x: x[1], reverse=True)
    top3_sec = sorted_sectors_pnl[:3]
    bot3_sec = sorted_sectors_pnl[-3:] if len(sorted_sectors_pnl) > 3 else []
    top3_str = ", ".join(f"{s} ${v:,.0f} ({v/total_pnl*100:.0f}%)" for s, v in top3_sec) if total_pnl > 0 else ""
    bot3_str = ", ".join(f"{s} ${v:,.0f}" for s, v in bot3_sec) if bot3_sec else ""
    top1_pct = top3_sec[0][1] / total_pnl * 100 if total_pnl > 0 and top3_sec else 0
    if top1_pct > 30:
        annotations["sector_dist_pnl"] = f"[Risk] Top 3: {top3_str}. Bottom 3: {bot3_str}. {profitable_sectors}/{len(sector_pnl_totals)} sectors profitable — top sector at {top1_pct:.0f}% is concentration risk."
    else:
        annotations["sector_dist_pnl"] = f"Top 3: {top3_str}. Bottom 3: {bot3_str}. {profitable_sectors}/{len(sector_pnl_totals)} sectors profitable."

    # --- Sector Distribution (% PnL) per month (top 3 / bottom 3) ---
    sector_dist_pnl_monthly = {}
    for m in months_sorted:
        m_sector_pnl = defaultdict(float)
        for t in all_months_data[m]:
            m_sector_pnl[t2s.get(t["underlying"], "Other")] += t["net_pnl"]
        m_total = sum(m_sector_pnl.values())
        m_sorted = sorted(m_sector_pnl.items(), key=lambda x: x[1], reverse=True)
        m_top3 = m_sorted[:3]
        m_bot3 = m_sorted[-3:] if len(m_sorted) > 3 else m_sorted
        m_top1_pct = m_top3[0][1] / m_total * 100 if m_total > 0 and m_top3 else 0
        m_risk = None
        if m_top1_pct > 40:
            m_risk = f"[Risk] {m_top3[0][0]}: {m_top1_pct:.0f}% of month's PnL — single-sector dependency; adverse sector event would erase majority of month's gains"
        sector_dist_pnl_monthly[m] = {
            "top3": [{"sector": s, "pnl": round(v, 2), "pct": round(v / m_total * 100, 1) if m_total > 0 else 0} for s, v in m_top3],
            "bottom3": [{"sector": s, "pnl": round(v, 2), "pct": round(v / m_total * 100, 1) if m_total > 0 else 0} for s, v in m_bot3],
            "risk": m_risk,
        }
    annotations["sector_dist_pnl_monthly"] = sector_dist_pnl_monthly

    # --- Sector Distribution (% of trades) per month (top 3 / bottom 3) ---
    sector_dist_trades_monthly = {}
    for m in months_sorted:
        m_sector_counts = defaultdict(int)
        for t in all_months_data[m]:
            m_sector_counts[t2s.get(t["underlying"], "Other")] += 1
        m_total_trades = sum(m_sector_counts.values())
        m_sorted_tr = sorted(m_sector_counts.items(), key=lambda x: x[1], reverse=True)
        m_top3_tr = m_sorted_tr[:3]
        m_bot3_tr = m_sorted_tr[-3:] if len(m_sorted_tr) > 3 else m_sorted_tr
        m_top1_tr_pct = m_top3_tr[0][1] / m_total_trades * 100 if m_total_trades > 0 and m_top3_tr else 0
        m_tr_risk = None
        if m_top1_tr_pct > 50:
            m_tr_risk = f"[Risk] {m_top3_tr[0][0]}: {m_top1_tr_pct:.0f}% of month's trades — sector-correlated positions; drawdown in this sector impacts majority of portfolio"
        sector_dist_trades_monthly[m] = {
            "top3": [{"sector": s, "count": c, "pct": round(c / m_total_trades * 100, 1) if m_total_trades > 0 else 0} for s, c in m_top3_tr],
            "bottom3": [{"sector": s, "count": c, "pct": round(c / m_total_trades * 100, 1) if m_total_trades > 0 else 0} for s, c in m_bot3_tr],
            "risk": m_tr_risk,
        }
    annotations["sector_dist_trades_monthly"] = sector_dist_trades_monthly

    # --- Sector x PnL Heatmap ---
    sector_nets = {sec: sum(t["net_pnl"] for t in trades) for sec, trades in by_sector.items()}
    best_sec = max(sector_nets, key=sector_nets.get)
    worst_sec = min(sector_nets, key=sector_nets.get)
    annotations["sector_pnl"] = f"Best: {best_sec} (${sector_nets[best_sec]:,.0f}, {len(by_sector[best_sec])} trades). Worst: {worst_sec} (${sector_nets[worst_sec]:,.0f}, {len(by_sector[worst_sec])} trades)."

    # --- Ticker x Month PnL ---
    top_tk = max(by_ticker.items(), key=lambda x: sum(t["net_pnl"] for t in x[1]))
    top_tk_pnl = sum(t["net_pnl"] for t in top_tk[1])
    top_tk_months = len(set((t["date_closed"] or "")[:7] for t in top_tk[1]))
    top_tk_avg = top_tk_pnl / len(top_tk[1])
    annotations["ticker_month_pnl"] = f"Top earner: {top_tk[0]} (${top_tk_pnl:,.0f} over {len(top_tk[1])} trades in {top_tk_months} months, ${top_tk_avg:,.0f}/trade avg)."

    # --- Ticker x Win Rate ---
    perfect_tickers = [(tk, len(tr)) for tk, tr in by_ticker.items() if len(tr) >= 3 and all(t["net_pnl"] > 0 for t in tr)]
    perfect_tickers.sort(key=lambda x: x[1], reverse=True)
    total_tickers = len(by_ticker)
    pct_perfect = len(perfect_tickers) / total_tickers * 100 if total_tickers else 0
    if perfect_tickers:
        annotations["ticker_winrate"] = f"{len(perfect_tickers)}/{total_tickers} tickers ({pct_perfect:.0f}%) at 100% win rate (≥3 trades). Top: {perfect_tickers[0][0]} ({perfect_tickers[0][1]} trades)."
    else:
        annotations["ticker_winrate"] = f"0/{total_tickers} tickers achieved 100% win rate with ≥3 trades."

    # --- Sector x Win Rate ---
    sector_wrs = {}
    for sec, strades in by_sector.items():
        wins = sum(1 for t in strades if t["net_pnl"] > 0)
        sector_wrs[sec] = (wins / len(strades) * 100, len(strades))
    perfect_secs = [(s, n) for s, (wr, n) in sector_wrs.items() if wr == 100 and n >= 2]
    avg_sector_wr = sum(wr for wr, _ in sector_wrs.values()) / len(sector_wrs) if sector_wrs else 0
    annotations["sector_winrate"] = f"Avg sector win rate: {avg_sector_wr:.0f}%. {len(perfect_secs)}/{len(sector_wrs)} sectors at 100% (≥2 trades)."

    # --- Ticker x Streak ---
    best_streak_tk, best_streak_len = "", 0
    worst_streak_tk, worst_streak_len = "", 0
    for tk, tr in by_ticker.items():
        results = [1 if t["net_pnl"] > 0 else -1 for t in sorted(tr, key=lambda x: x["date_closed"] or "")]
        ws, ls = detect_streaks(results)
        if ws > best_streak_len:
            best_streak_len, best_streak_tk = ws, tk
        if ls > worst_streak_len:
            worst_streak_len, worst_streak_tk = ls, tk
    annotations["ticker_streak"] = f"Max win streak: {best_streak_tk} (+{best_streak_len} consecutive). Max loss streak: {worst_streak_tk} (-{worst_streak_len})."

    # --- Sector x Streak ---
    best_ss_name, best_ss_len = "", 0
    for sec, strades in by_sector.items():
        results = [1 if t["net_pnl"] > 0 else -1 for t in sorted(strades, key=lambda x: x["date_closed"] or "")]
        ws, _ = detect_streaks(results)
        if ws > best_ss_len:
            best_ss_len, best_ss_name = ws, sec
    annotations["sector_streak"] = f"Longest sector win streak: {best_ss_name} (+{best_ss_len}). Across {len(by_sector[best_ss_name])} total trades."

    # --- Waterfall ---
    growth_months = sum(1 for _, net in monthly_nets if net > 0)
    avg_monthly = sum(net for _, net in monthly_nets) / n_months if n_months else 0
    if n_months >= 2:
        pnl_growth = (monthly_nets[-1][1] - monthly_nets[0][1]) / max(abs(monthly_nets[0][1]), 1) * 100
        annotations["waterfall"] = f"{growth_months}/{n_months} months positive. Avg: ${avg_monthly:,.0f}/month. Last vs first month: {pnl_growth:+.0f}%."
    else:
        annotations["waterfall"] = f"${avg_monthly:,.0f} in the single reported month."

    # --- Broker lines ---
    broker_nets = defaultdict(float)
    broker_counts = defaultdict(int)
    for t in closed_trades:
        broker_nets[t["broker"]] += t["net_pnl"]
        broker_counts[t["broker"]] += 1
    broker_sorted = sorted(broker_nets.items(), key=lambda x: x[1], reverse=True)
    if len(broker_sorted) >= 2:
        b1, v1 = broker_sorted[0]
        b2, v2 = broker_sorted[1]
        annotations["broker_lines"] = f"{b1}: ${v1:,.0f} ({broker_counts[b1]} trades, ${v1/broker_counts[b1]:,.0f}/trade). {b2}: ${v2:,.0f} ({broker_counts[b2]} trades, ${v2/broker_counts[b2]:,.0f}/trade)."
    else:
        annotations["broker_lines"] = ""

    # --- Broker donut ---
    top_broker = broker_sorted[0][0] if broker_sorted else ""
    top_broker_pct = broker_nets[top_broker] / sum(broker_nets.values()) * 100 if sum(broker_nets.values()) > 0 else 0
    annotations["broker_donut"] = f"{top_broker}: {top_broker_pct:.0f}% of PnL, {broker_counts[top_broker]/len(closed_trades)*100:.0f}% of trades."

    # --- Histogram ---
    pnls = sorted(t["net_pnl"] for t in closed_trades)
    median_pnl = pnls[len(pnls) // 2] if pnls else 0
    avg_pnl = sum(pnls) / len(pnls) if pnls else 0
    p10 = pnls[int(len(pnls) * 0.1)] if len(pnls) > 10 else pnls[0] if pnls else 0
    p90 = pnls[int(len(pnls) * 0.9)] if len(pnls) > 10 else pnls[-1] if pnls else 0
    annotations["histogram"] = f"Median: ${median_pnl:,.0f}. Mean: ${avg_pnl:,.0f}. P10/P90 range: ${p10:,.0f} to ${p90:,.0f}."

    # --- Scatter (hold period) ---
    hold_days = []
    for t in closed_trades:
        if t["date_opened"] and t["date_closed"]:
            try:
                d1 = datetime.strptime(t["date_opened"], "%Y-%m-%d")
                d2 = datetime.strptime(t["date_closed"], "%Y-%m-%d")
                hold_days.append((d2 - d1).days)
            except:
                pass
    if hold_days:
        avg_hold = sum(hold_days) / len(hold_days)
        short_pct = sum(1 for d in hold_days if d <= 7) / len(hold_days) * 100
        annotations["scatter"] = f"Avg hold: {avg_hold:.1f} days. {short_pct:.0f}% of trades held ≤7 days. Median hold: {sorted(hold_days)[len(hold_days)//2]} days."
    else:
        annotations["scatter"] = ""

    # --- Calendar ---
    daily_totals = defaultdict(float)
    for t in closed_trades:
        if t["date_closed"]:
            daily_totals[t["date_closed"]] += t["net_pnl"]
    green_days = sum(1 for v in daily_totals.values() if v > 0)
    total_days = len(daily_totals)
    best_day = max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else ("", 0)
    annotations["calendar"] = f"{green_days}/{total_days} active days profitable ({green_days/total_days*100:.0f}%). Best: {best_day[0]} (${best_day[1]:,.0f})."

    # --- Win/Loss streak ---
    all_results = [1 if t["net_pnl"] > 0 else -1 for t in sorted(closed_trades, key=lambda x: x["date_closed"] or "")]
    ow, ol = detect_streaks(all_results)
    total_wins = sum(1 for r in all_results if r > 0)
    annotations["streak"] = f"Overall: {total_wins}/{len(all_results)} wins ({total_wins/len(all_results)*100:.0f}%). Longest win run: {ow}. Longest loss run: {ol}."

    # --- Broker x Strategy ---
    broker_strat = defaultdict(lambda: defaultdict(float))
    broker_strat_count = defaultdict(lambda: defaultdict(int))
    for t in closed_trades:
        broker_strat[t["broker"]][t["strategy"]] += t["net_pnl"]
        broker_strat_count[t["broker"]][t["strategy"]] += 1
    best_combo_val, best_combo = 0, ""
    for b, strats in broker_strat.items():
        for st, val in strats.items():
            if val > best_combo_val:
                best_combo_val, best_combo = val, f"{b}/{st}"
    best_count = 0
    if "/" in best_combo:
        b, st = best_combo.split("/")
        best_count = broker_strat_count[b][st]
    annotations["broker_strat"] = f"Top combo: {best_combo} (${best_combo_val:,.0f} from {best_count} trades, ${best_combo_val/max(best_count,1):,.0f}/trade)."

    # --- Hold outcome ---
    if hold_days:
        short_win_pnl = sum(t["net_pnl"] for t in closed_trades if t["date_opened"] and t["date_closed"] and t["net_pnl"] > 0 and (datetime.strptime(t["date_closed"], "%Y-%m-%d") - datetime.strptime(t["date_opened"], "%Y-%m-%d")).days <= 7)
        long_win_pnl = sum(t["net_pnl"] for t in closed_trades if t["date_opened"] and t["date_closed"] and t["net_pnl"] > 0 and (datetime.strptime(t["date_closed"], "%Y-%m-%d") - datetime.strptime(t["date_opened"], "%Y-%m-%d")).days > 7)
        annotations["hold_outcome"] = f"Short holds (≤7d) PnL: ${short_win_pnl:,.0f}. Longer holds (>7d) PnL: ${long_win_pnl:,.0f}. {('Short holds more profitable per-day.' if short_win_pnl / max(sum(1 for d in hold_days if d <= 7), 1) > long_win_pnl / max(sum(1 for d in hold_days if d > 7), 1) else 'Longer holds more profitable per-day.')}"
    else:
        annotations["hold_outcome"] = ""

    return annotations


def main():
    parser = argparse.ArgumentParser(description="Generate monthly insights from computed PnL")
    parser.add_argument("--input", required=True, help="Path to computed-pnl.json")
    parser.add_argument("--sector-map", default=".local/data/options-pnl/sector-map.json", help="Path to sector-map.json")
    parser.add_argument("--output", required=True, help="Output insights.json path")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    t2s = load_sector_map(args.sector_map)

    # Group trades by month
    all_months_data = defaultdict(list)
    for t in data["closed_trades"]:
        if t["date_closed"]:
            m = t["date_closed"][:7]
            all_months_data[m].append(t)

    insights = {}
    ticker_history = set()

    for month in sorted(all_months_data.keys()):
        trades = all_months_data[month]
        signals = analyze_month(month, trades, all_months_data, t2s, ticker_history)
        repeat_bullets, improve_bullets = generate_prose(month, signals, trades)

        insights[month] = {
            "repeat": repeat_bullets,
            "improve": improve_bullets,
            "signals": signals,
        }

        # Update ticker history for "new ticker" detection in subsequent months
        for t in trades:
            ticker_history.add(t["underlying"])

    # Generate chart-level annotations
    chart_annotations = generate_chart_annotations(data["closed_trades"], all_months_data, t2s)

    # Identify risk signals per month
    RISK_SIGNALS = {"concentration_risk", "sector_dominance", "recurring_loser", "win_rate_drop", "low_volume", "efficiency_decline", "cold_streak"}

    # Write output
    output = {
        "monthly": {},
        "chart_annotations": chart_annotations,
    }
    for month, data_m in insights.items():
        # Tag each improve bullet as risk=True if its source signal is a risk type
        improve_with_risk = []
        improve_signals = [s for s in data_m["signals"] if s["category"] == "improve"]
        for bullet in data_m["improve"]:
            is_risk = any(s["signal"] in RISK_SIGNALS for s in improve_signals)
            improve_with_risk.append({"text": bullet, "risk": is_risk})
        output["monthly"][month] = {
            "repeat": data_m["repeat"],
            "improve": improve_with_risk,
        }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written: {out_path}")
    for month in sorted(output["monthly"].keys()):
        r = len(output["monthly"][month]["repeat"])
        i = len(output["monthly"][month]["improve"])
        print(f"  {month}: {r} repeat, {i} improve")
    print(f"  Chart annotations: {len(chart_annotations)} charts")


if __name__ == "__main__":
    main()
