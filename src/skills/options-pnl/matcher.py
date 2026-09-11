"""
Trade matching logic: filters CSP/CC, excludes spreads, matches opens to closes (FIFO),
computes realized PnL for closed positions only.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


def detect_spreads_tasty(trades: List[Dict]) -> set:
    """Detect spread legs in Tastytrade by Order #."""
    order_groups = defaultdict(list)
    for i, t in enumerate(trades):
        if t["order_id"]:
            order_groups[t["order_id"]].append(i)

    spread_indices = set()
    for order_id, indices in order_groups.items():
        if len(indices) < 2:
            continue
        group = [trades[i] for i in indices]
        has_sto = any(t["direction"] == "STO" for t in group)
        has_bto = any(t["direction"] == "BTO" for t in group)
        if has_sto and has_bto:
            spread_indices.update(indices)
    return spread_indices


def detect_spreads_timestamp(trades: List[Dict], broker: str) -> set:
    """Detect spread legs by timestamp proximity (within 5 seconds) for Fidelity/TOS."""
    spread_indices = set()
    broker_trades = [(i, t) for i, t in enumerate(trades) if t["broker"] == broker]

    for idx_a, (i, t_a) in enumerate(broker_trades):
        if t_a["direction"] not in ("STO", "BTO"):
            continue
        for idx_b, (j, t_b) in enumerate(broker_trades):
            if i >= j:
                continue
            if t_a["underlying"] != t_b["underlying"]:
                continue
            if t_a["expiry"] != t_b["expiry"]:
                continue
            if t_a["date"] != t_b["date"]:
                continue
            dirs = {t_a["direction"], t_b["direction"]}
            if "STO" in dirs and "BTO" in dirs:
                spread_indices.add(i)
                spread_indices.add(j)
    return spread_indices


def filter_csp_cc(trades: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Filter trades to CSP/CC only, excluding spreads and long options.
    Returns (filtered_trades, excluded_counts).
    """
    excluded = {"long_options": 0, "spread_legs": 0, "stock_trades": 0}

    tasty_trades_idx = [i for i, t in enumerate(trades) if t["broker"] == "Tastytrade"]
    tasty_spread_idx = detect_spreads_tasty(trades) if tasty_trades_idx else set()

    fidelity_spread_idx = detect_spreads_timestamp(trades, "Fidelity")
    tos_spread_idx = detect_spreads_timestamp(trades, "Thinkorswim")

    all_spread_idx = tasty_spread_idx | fidelity_spread_idx | tos_spread_idx
    excluded["spread_legs"] = len(all_spread_idx)

    filtered = []
    for i, t in enumerate(trades):
        if i in all_spread_idx:
            continue
        if t["direction"] == "BTO":
            excluded["long_options"] += 1
            continue
        if t["direction"] in ("STO", "BTC", "EXPIRED", "ASSIGNED"):
            filtered.append(t)

    return filtered, excluded


def match_trades(trades: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Match STO with BTC (FIFO) to produce closed trades.
    Returns (closed_trades, unmatched_opens).
    """
    opens = defaultdict(list)
    closes = defaultdict(list)

    for t in trades:
        key = (t["broker"], t["underlying"], t["expiry"], t["strike"], t["option_type"])
        if t["direction"] == "STO":
            opens[key].append(t)
        elif t["direction"] in ("BTC", "EXPIRED", "ASSIGNED"):
            # Expired/Assigned close at price 0 (or the recorded price)
            if t["direction"] in ("EXPIRED", "ASSIGNED") and t["price"] == 0:
                t["price"] = 0.0
            closes[key].append(t)

    for key in opens:
        opens[key].sort(key=lambda x: x["date"] or "")
    for key in closes:
        closes[key].sort(key=lambda x: x["date"] or "")

    closed_trades = []
    unmatched_opens = []

    for key, open_list in opens.items():
        close_list = closes.get(key, [])
        close_idx = 0

        for open_trade in open_list:
            remaining_qty = open_trade["qty"]

            while remaining_qty > 0 and close_idx < len(close_list):
                close_trade = close_list[close_idx]
                match_qty = min(remaining_qty, close_trade["qty"])

                open_credit = open_trade["price"] * match_qty * 100
                close_debit = close_trade["price"] * match_qty * 100
                gross_pnl = open_credit - close_debit

                open_fee_share = (open_trade["commission"] + open_trade["fees"]) * match_qty / open_trade["qty"]
                close_fee_share = (close_trade["commission"] + close_trade["fees"]) * match_qty / close_trade["qty"] if close_trade["qty"] > 0 else 0
                total_fees = open_fee_share + close_fee_share
                net_pnl = gross_pnl - total_fees

                strategy = "CC" if open_trade["option_type"] == "CALL" else "CSP"

                closed_trades.append({
                    "date_closed": close_trade["date"],
                    "date_opened": open_trade["date"],
                    "broker": open_trade["broker"],
                    "underlying": open_trade["underlying"],
                    "strategy": strategy,
                    "strike": open_trade["strike"],
                    "expiry": open_trade["expiry"],
                    "qty": match_qty,
                    "open_price": open_trade["price"],
                    "close_price": close_trade["price"],
                    "gross_pnl": round(gross_pnl, 2),
                    "fees": round(total_fees, 2),
                    "net_pnl": round(net_pnl, 2),
                })

                remaining_qty -= match_qty
                close_trade["qty"] -= match_qty
                if close_trade["qty"] <= 0:
                    close_idx += 1

            if remaining_qty > 0:
                expiry_date = open_trade["expiry"]
                # Only treat as expired if we have explicit EXPIRED/ASSIGNED
                # data in the closes list for this key. Never infer expiry from
                # the current date — without closing data we cannot confirm
                # whether the option expired, was assigned, or was closed.
                unmatched_opens.append({**open_trade, "qty": remaining_qty})

    return closed_trades, unmatched_opens
