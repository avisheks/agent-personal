#!/usr/bin/env python3
"""
Main entry point: reads all broker CSVs, computes CSP/CC PnL, outputs JSON summary.

Usage:
    python src/compute_pnl.py --input .local/options-pnl/inp --output .local/options-pnl/out/computed-pnl.json
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

from parsers import parse_fidelity, parse_tastytrade, parse_thinkorswim
from matcher import filter_csp_cc, match_trades


def get_week_start(date_str: str) -> str:
    """Get Monday of the week containing date_str."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def get_month(date_str: str) -> str:
    return date_str[:7] if date_str else "unknown"


def compute_summary(closed_trades: list) -> dict:
    """Compute aggregate summary metrics."""
    if not closed_trades:
        return {
            "total_gross_pnl": 0, "total_fees": 0, "total_net_pnl": 0,
            "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
            "win_rate": 0, "largest_win": 0, "largest_loss": 0,
            "avg_win": 0, "avg_loss": 0,
        }

    wins = [t for t in closed_trades if t["net_pnl"] > 0]
    losses = [t for t in closed_trades if t["net_pnl"] <= 0]

    return {
        "total_gross_pnl": round(sum(t["gross_pnl"] for t in closed_trades), 2),
        "total_fees": round(sum(t["fees"] for t in closed_trades), 2),
        "total_net_pnl": round(sum(t["net_pnl"] for t in closed_trades), 2),
        "total_trades": len(closed_trades),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "win_rate": round(len(wins) / len(closed_trades) * 100, 1) if closed_trades else 0,
        "largest_win": round(max((t["net_pnl"] for t in closed_trades), default=0), 2),
        "largest_loss": round(min((t["net_pnl"] for t in closed_trades), default=0), 2),
        "avg_win": round(sum(t["net_pnl"] for t in wins) / len(wins), 2) if wins else 0,
        "avg_loss": round(sum(t["net_pnl"] for t in losses) / len(losses), 2) if losses else 0,
    }


def compute_monthly_breakdown(closed_trades: list) -> list:
    """Group by month and compute per-month summary."""
    by_month = defaultdict(list)
    for t in closed_trades:
        month = get_month(t["date_closed"])
        by_month[month].append(t)

    result = []
    for month in sorted(by_month.keys()):
        trades = by_month[month]
        wins = [t for t in trades if t["net_pnl"] > 0]
        result.append({
            "month": month,
            "trades": len(trades),
            "gross_pnl": round(sum(t["gross_pnl"] for t in trades), 2),
            "fees": round(sum(t["fees"] for t in trades), 2),
            "net_pnl": round(sum(t["net_pnl"] for t in trades), 2),
            "win_rate": round(len(wins) / len(trades) * 100, 1) if trades else 0,
        })
    return result


def compute_broker_monthly(closed_trades: list) -> dict:
    """Group by broker then month."""
    by_broker = defaultdict(list)
    for t in closed_trades:
        by_broker[t["broker"]].append(t)

    result = {}
    for broker in sorted(by_broker.keys()):
        result[broker] = compute_monthly_breakdown(by_broker[broker])
    return result


def compute_weekly_trendline(closed_trades: list) -> list:
    """Compute weekly PnL and cumulative PnL."""
    by_week = defaultdict(float)
    for t in closed_trades:
        if t["date_closed"]:
            week = get_week_start(t["date_closed"])
            by_week[week] += t["net_pnl"]

    cumulative = 0
    result = []
    for week in sorted(by_week.keys()):
        cumulative += by_week[week]
        result.append({
            "week_starting": week,
            "net_pnl": round(by_week[week], 2),
            "cumulative_pnl": round(cumulative, 2),
        })
    return result


def compute_broker_weekly(closed_trades: list) -> dict:
    """Weekly trendline per broker."""
    by_broker = defaultdict(list)
    for t in closed_trades:
        by_broker[t["broker"]].append(t)

    result = {}
    for broker in sorted(by_broker.keys()):
        result[broker] = compute_weekly_trendline(by_broker[broker])
    return result


def compute_by_underlying(closed_trades: list) -> dict:
    """PnL by underlying, returning top 10 (best) and bottom 10 (worst) by net PnL."""
    by_ticker = defaultdict(list)
    for t in closed_trades:
        by_ticker[t["underlying"]].append(t)

    all_tickers = []
    for ticker, trades in by_ticker.items():
        wins = [t for t in trades if t["net_pnl"] > 0]
        all_tickers.append({
            "underlying": ticker,
            "trades": len(trades),
            "net_pnl": round(sum(t["net_pnl"] for t in trades), 2),
            "avg_pnl": round(sum(t["net_pnl"] for t in trades) / len(trades), 2),
            "win_rate": round(len(wins) / len(trades) * 100, 1) if trades else 0,
        })

    all_tickers.sort(key=lambda x: x["net_pnl"], reverse=True)
    top_10 = all_tickers[:10]
    bottom_10 = all_tickers[-10:] if len(all_tickers) > 10 else []
    bottom_10.sort(key=lambda x: x["net_pnl"])

    return {"top_10": top_10, "bottom_10": bottom_10}


def compute_by_strategy(closed_trades: list) -> list:
    """PnL by strategy (CSP vs CC)."""
    by_strat = defaultdict(list)
    for t in closed_trades:
        by_strat[t["strategy"]].append(t)

    result = []
    for strat in ["CSP", "CC"]:
        trades = by_strat.get(strat, [])
        wins = [t for t in trades if t["net_pnl"] > 0]
        result.append({
            "strategy": strat,
            "label": "Cash-Secured Puts (CSP)" if strat == "CSP" else "Covered Calls (CC)",
            "trades": len(trades),
            "net_pnl": round(sum(t["net_pnl"] for t in trades), 2),
            "win_rate": round(len(wins) / len(trades) * 100, 1) if trades else 0,
            "avg_pnl": round(sum(t["net_pnl"] for t in trades) / len(trades), 2) if trades else 0,
        })
    return result


def compute_wheel_capital_gains(all_trades: list, stock_trades: list, closed_option_trades: list) -> list:
    """
    Identify stocks acquired via CSP assignment and compute capital gains when sold.
    Links CSP assignments to stock sales by (broker, ticker) using FIFO.
    Also handles CC assignments (stock called away).
    """
    # Find CSP assignments: option trades with direction "ASSIGNED" and option_type "PUT"
    # These result in stock acquisition at the strike price
    assignments = []
    for t in all_trades:
        if t.get("direction") == "ASSIGNED" and t.get("option_type") == "PUT":
            assignments.append({
                "broker": t["broker"],
                "ticker": t["underlying"],
                "qty": t["qty"] * 100,  # each contract = 100 shares
                "acquisition_price": t["strike"],
                "assignment_date": t["date"],
            })

    # Also check stock_trades for "BOT" entries that match assignment patterns
    # In new TOS format, assignment shows as "Assigned" on option + "Buy" on stock
    # Look for stock buys that correspond to put strikes on the same date
    for st in stock_trades:
        if st["action"] == "BOT":
            # Check if this buy matches a known assignment date+ticker+price
            for a in assignments:
                if (a["broker"] == st["broker"] and a["ticker"] == st["ticker"]
                        and a["assignment_date"] == st["date"]
                        and abs(a["acquisition_price"] - st["price"]) < 0.01):
                    # Already captured via the option assignment entry
                    break
            else:
                # Check if there's a closed CSP at this strike that expired/was assigned
                # on or near this date
                for ct in closed_option_trades:
                    if (ct["broker"] == st["broker"] and ct["underlying"] == st["ticker"]
                            and ct["strategy"] == "CSP"
                            and abs(ct["strike"] - st["price"]) < 0.01
                            and ct.get("close_price", 0) == 0
                            and ct.get("date_closed") == st["date"]):
                        assignments.append({
                            "broker": st["broker"],
                            "ticker": st["ticker"],
                            "qty": st["qty"],
                            "acquisition_price": st["price"],
                            "assignment_date": st["date"],
                        })
                        break

    # Find stock sales (SOLD entries, or CC assignments that result in stock sale)
    stock_sales = []
    for st in stock_trades:
        if st["action"] == "SOLD":
            stock_sales.append({
                "broker": st["broker"],
                "ticker": st["ticker"],
                "qty": st["qty"],
                "sale_price": st["price"],
                "sale_date": st["date"],
            })

    # Also check for CC assignments (stock called away at strike)
    for t in all_trades:
        if t.get("direction") == "ASSIGNED" and t.get("option_type") == "CALL":
            stock_sales.append({
                "broker": t["broker"],
                "ticker": t["underlying"],
                "qty": t["qty"] * 100,
                "sale_price": t["strike"],
                "sale_date": t["date"],
            })

    # Sort both by date for FIFO matching
    assignments.sort(key=lambda x: x["assignment_date"] or "")
    stock_sales.sort(key=lambda x: x["sale_date"] or "")

    # Match assignments to sales (FIFO by broker+ticker)
    wheel_gains = []
    assignment_pool = defaultdict(list)
    for a in assignments:
        key = (a["broker"], a["ticker"])
        assignment_pool[key].append(dict(a))

    for sale in stock_sales:
        key = (sale["broker"], sale["ticker"])
        pool = assignment_pool.get(key, [])
        remaining_sale_qty = sale["qty"]

        while remaining_sale_qty > 0 and pool:
            assignment = pool[0]
            match_qty = min(remaining_sale_qty, assignment["qty"])

            capital_gain = (sale["sale_price"] - assignment["acquisition_price"]) * match_qty
            days_held = 0
            if assignment["assignment_date"] and sale["sale_date"]:
                try:
                    from datetime import datetime as dt
                    d1 = dt.strptime(assignment["assignment_date"], "%Y-%m-%d")
                    d2 = dt.strptime(sale["sale_date"], "%Y-%m-%d")
                    days_held = (d2 - d1).days
                except:
                    pass

            wheel_gains.append({
                "broker": sale["broker"],
                "ticker": sale["ticker"],
                "qty": match_qty,
                "acquisition_price": assignment["acquisition_price"],
                "sale_price": sale["sale_price"],
                "capital_gain": round(capital_gain, 2),
                "assignment_date": assignment["assignment_date"],
                "sale_date": sale["sale_date"],
                "days_held": days_held,
            })

            remaining_sale_qty -= match_qty
            assignment["qty"] -= match_qty
            if assignment["qty"] <= 0:
                pool.pop(0)

    return wheel_gains


def main():
    parser = argparse.ArgumentParser(description="Compute CSP/CC options PnL")
    parser.add_argument("--input", required=True, help="Input directory containing broker subdirs")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--start-date", help="Filter: only include trades closed on or after this date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Filter: only include trades closed on or before this date (YYYY-MM-DD)")
    args = parser.parse_args()

    inp_dir = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_trades = []
    all_stock_trades = []

    fidelity_dir = inp_dir / "fidelity"
    if fidelity_dir.exists():
        for f in sorted(fidelity_dir.glob("*.csv")):
            all_trades.extend(parse_fidelity(f))

    tasty_dir = inp_dir / "tasty"
    tasty_has_assignments = False
    if tasty_dir.exists():
        for f in sorted(tasty_dir.glob("*.csv")):
            if "__assignments" in f.name:
                tasty_has_assignments = True
            all_trades.extend(parse_tastytrade(f))
        if not tasty_has_assignments:
            print("WARNING: No Tastytrade assignments file found (*__assignments.csv).")
            print("         Wheel capital gains from Tastytrade will be incomplete.")
            print("         Export Tastytrade Transaction History (Receive Deliver entries) and save as:")
            print("         inp/tasty/tastytrade_transactions_history_x*_YYMMDD_to_YYMMDD__assignments.csv")
            print()

    tos_dir = inp_dir / "thinknswim"
    if tos_dir.exists():
        for f in sorted(tos_dir.glob("*.csv")):
            opt_trades, stk_trades = parse_thinkorswim(f)
            all_trades.extend(opt_trades)
            all_stock_trades.extend(stk_trades)

    filtered_trades, excluded = filter_csp_cc(all_trades)
    excluded["stock_trades"] = len(all_stock_trades)

    # Deep copy all_trades before matching (match_trades mutates qty)
    import copy
    all_trades_for_wheel = copy.deepcopy(all_trades)

    closed_trades, unmatched = match_trades(filtered_trades)

    # Compute wheel capital gains using the unmutated copy
    wheel_gains = compute_wheel_capital_gains(all_trades_for_wheel, all_stock_trades, closed_trades)

    # Apply date range filter if specified
    if args.start_date:
        closed_trades = [t for t in closed_trades if t["date_closed"] and t["date_closed"] >= args.start_date]
        wheel_gains = [w for w in wheel_gains if w["sale_date"] and w["sale_date"] >= args.start_date]
    if args.end_date:
        closed_trades = [t for t in closed_trades if t["date_closed"] and t["date_closed"] <= args.end_date]
        wheel_gains = [w for w in wheel_gains if w["sale_date"] and w["sale_date"] <= args.end_date]

    closed_trades.sort(key=lambda x: x["date_closed"] or "9999")
    wheel_gains.sort(key=lambda x: x["sale_date"] or "9999")

    # Compute summaries
    premium_summary = compute_summary(closed_trades)
    total_wheel_gain = round(sum(w["capital_gain"] for w in wheel_gains), 2)
    full_net_pnl = round(premium_summary["total_net_pnl"] + total_wheel_gain, 2)

    valid_dates = [t["date_closed"] for t in closed_trades if t["date_closed"]]
    wheel_dates = [w["sale_date"] for w in wheel_gains if w["sale_date"]]
    all_dates = valid_dates + wheel_dates

    output = {
        "generated": datetime.now().strftime("%Y-%m-%d"),
        "period_start": min(all_dates) if all_dates else None,
        "period_end": max(all_dates) if all_dates else None,
        "full_pnl": {
            "total_net_pnl": full_net_pnl,
            "premium_pnl": premium_summary["total_net_pnl"],
            "wheel_capital_gains": total_wheel_gain,
            "total_trades": premium_summary["total_trades"] + len(wheel_gains),
        },
        "summary": premium_summary,
        "monthly_all": compute_monthly_breakdown(closed_trades),
        "monthly_by_broker": compute_broker_monthly(closed_trades),
        "weekly_all": compute_weekly_trendline(closed_trades),
        "weekly_by_broker": compute_broker_weekly(closed_trades),
        "by_strategy": compute_by_strategy(closed_trades),
        "by_underlying": compute_by_underlying(closed_trades),
        "closed_trades": closed_trades,
        "wheel_gains": wheel_gains,
        "wheel_summary": {
            "total_capital_gains": total_wheel_gain,
            "completed_cycles": len(wheel_gains),
            "avg_days_held": round(sum(w["days_held"] for w in wheel_gains) / len(wheel_gains), 1) if wheel_gains else 0,
            "best_trade": max((w["capital_gain"] for w in wheel_gains), default=0),
            "worst_trade": min((w["capital_gain"] for w in wheel_gains), default=0),
        },
        "excluded": excluded,
        "stock_trades": all_stock_trades,
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Done. {len(closed_trades)} closed CSP/CC trades + {len(wheel_gains)} wheel stock sales written to {out_path}")
    print(f"Excluded: {excluded}")
    print(f"Premium PnL: ${premium_summary['total_net_pnl']:,.2f}")
    print(f"Wheel Capital Gains: ${total_wheel_gain:,.2f}")
    print(f"Full PnL: ${full_net_pnl:,.2f}")


if __name__ == "__main__":
    main()
