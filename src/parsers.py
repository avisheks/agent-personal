"""
Broker-specific CSV parsers for options trade data.
Each parser returns a list of normalized trade dicts.
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


def parse_amount(val: str) -> float:
    if not val:
        return 0.0
    return float(str(val).replace(",", "").replace('"', '').strip())


def parse_date_mdy(val: str) -> Optional[str]:
    """Parse MM/DD/YYYY or MM/DD/YY to YYYY-MM-DD."""
    val = val.strip()
    if not val:
        return None
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_fidelity_expiry(text: str) -> Optional[str]:
    """Parse expiry like 'OCT 03 25' or 'NOV 21 25' from Fidelity action string."""
    months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
              "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    m = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s+(\d{2})\s+\$', text)
    if m:
        mon = months[m.group(1)]
        day = int(m.group(2))
        year = 2000 + int(m.group(3))
        return f"{year}-{mon:02d}-{day:02d}"
    return None


def parse_fidelity(filepath: Path) -> List[Dict]:
    """Parse Fidelity transaction CSV."""
    trades = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    # Skip blank lines before header
    header_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("Run Date,"):
            header_idx = i
            break
    content = "".join(lines[header_idx:])
    import io
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
            action = row.get("Action") or ""
            if not action:
                continue

            is_expired = action.startswith("EXPIRED")
            if not is_expired and "OPENING TRANSACTION" not in action and "CLOSING TRANSACTION" not in action:
                continue
            if "CALL" not in action and "PUT" not in action:
                continue

            is_open = "OPENING" in action
            is_sell = "YOU SOLD" in action
            is_call = "CALL" in action
            option_type = "CALL" if is_call else "PUT"

            ticker_m = re.search(r'(CALL|PUT)\s+\(([A-Z]+)\)', action)
            ticker = ticker_m.group(2) if ticker_m else ""

            strike_m = re.search(r'\$(\d+(?:\.\d+)?)\s+\(100 SHS\)', action)
            if not strike_m:
                strike_m = re.search(r'\$(\d+(?:\.\d+)?)\s', action)
            strike = float(strike_m.group(1)) if strike_m else 0.0

            expiry = parse_fidelity_expiry(action)
            date = parse_date_mdy(row.get("Run Date", ""))
            price = parse_amount(row.get("Price ($)", "0"))
            qty = int(parse_amount(row.get("Quantity", "0"))) if row.get("Quantity") else 1
            commission = parse_amount(row.get("Commission ($)", "0"))
            fees = parse_amount(row.get("Fees ($)", "0"))
            amount = parse_amount(row.get("Amount ($)", "0"))

            if is_expired:
                direction = "EXPIRED"
            elif is_open and is_sell:
                direction = "STO"
            elif is_open and not is_sell:
                direction = "BTO"
            elif not is_open and not is_sell:
                direction = "BTC"
            else:
                direction = "STC"

            trades.append({
                "broker": "Fidelity",
                "date": date,
                "direction": direction,
                "underlying": ticker,
                "option_type": option_type,
                "strike": strike,
                "expiry": expiry,
                "qty": abs(qty),
                "price": price,
                "commission": commission,
                "fees": fees,
                "amount": amount,
                "order_id": None,
                "timestamp": date,
            })
    return trades


def parse_tastytrade(filepath: Path) -> List[Dict]:
    """Parse Tastytrade transaction CSV. Handles both old (transaction history) and new (order history) formats."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        first_line = f.readline().strip()

    if "Symbol" in first_line and "MarketOrFill" in first_line:
        return _parse_tasty_new_format(filepath)
    return _parse_tasty_old_format(filepath)


def _parse_tasty_new_format(filepath: Path) -> List[Dict]:
    """Parse new Tastytrade order-history format:
    Symbol, Status, MarketOrFill, Price, TIF, Time, TimeStampAtType, Order #, Description
    Description examples: '-1 Jul 17 Exp 80 Put STO', '1 Jun 26 Exp 350 Put BTC'
    """
    trades = []
    months_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                  "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Status") != "Filled":
                continue

            description = (row.get("Description") or "").strip()
            symbol = (row.get("Symbol") or "").strip()
            price_raw = (row.get("Price") or "").strip()
            time_raw = (row.get("Time") or "").strip()
            order_id = (row.get("Order #") or "").strip().lstrip("#")

            # Parse description: "-1 Jul 17 Exp 80 Put STO" or "1 Jun 26 Exp 350 Put BTC"
            # Can also be multi-leg: "-300 STC\n-3 May 15 Exp 470 Put STC"
            # Handle multi-line descriptions
            if "\n" in description:
                # Multi-leg order, take only option lines
                for sub_desc in description.split("\n"):
                    sub_desc = sub_desc.strip()
                    if "STO" in sub_desc or "BTC" in sub_desc:
                        _parse_tasty_new_desc(sub_desc, symbol, price_raw, time_raw, order_id, months_map, trades)
            else:
                _parse_tasty_new_desc(description, symbol, price_raw, time_raw, order_id, months_map, trades)

    return trades


def _parse_tasty_new_desc(description: str, symbol: str, price_raw: str, time_raw: str,
                          order_id: str, months_map: dict, trades: list):
    """Parse a single description line from new Tasty format."""
    # Pattern: "{-qty} {Mon} {DD} Exp {Strike} {Put|Call} {STO|BTC}"
    # or: "{qty} {Mon} {DD} Exp {Strike} {Put|Call} {BTC|STC}"
    desc_m = re.match(
        r'(-?\d+)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s+(?:(\d{1,2})d\s+)?Exp\s+([\d.]+)\s+(Put|Call)\s+(STO|BTC|STC)',
        description, re.IGNORECASE
    )
    if not desc_m:
        return

    qty = abs(int(desc_m.group(1)))
    exp_mon = months_map[desc_m.group(2)]
    exp_day = int(desc_m.group(3))
    strike = float(desc_m.group(5))
    option_type = desc_m.group(6).upper()
    action = desc_m.group(7).upper()

    # Determine year from time field (e.g., "3/27, 11:43a" means 2026)
    # Since file covers 2026, assume 2026
    year = 2026
    expiry = f"{year}-{exp_mon:02d}-{exp_day:02d}"

    # Parse price: "2.50 cr" or "0.01 db"
    price_val = 0.0
    price_m = re.match(r'([\d.]+)\s*(cr|db)', price_raw)
    if price_m:
        price_val = float(price_m.group(1))

    # Parse date from Time field: "3/27, 11:43a" -> 2026-03-27
    date = None
    time_m = re.match(r'(\d{1,2})/(\d{1,2}),', time_raw)
    if time_m:
        mon = int(time_m.group(1))
        day = int(time_m.group(2))
        date = f"2026-{mon:02d}-{day:02d}"

    if action == "STO":
        direction = "STO"
    elif action in ("BTC", "STC"):
        direction = "BTC"
    else:
        return

    trades.append({
        "broker": "Tastytrade",
        "date": date,
        "direction": direction,
        "underlying": symbol,
        "option_type": option_type,
        "strike": strike,
        "expiry": expiry,
        "qty": qty,
        "price": price_val,
        "commission": 0.0,
        "fees": 0.0,
        "amount": 0.0,
        "order_id": order_id,
        "timestamp": time_raw,
    })


def _parse_tasty_old_format(filepath: Path) -> List[Dict]:
    """Parse old Tastytrade transaction-history format.
    Handles both Trade entries and Receive Deliver (assignment/expiration) entries."""
    trades = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rtype = row.get("Type", "")
            sub_type = row.get("Sub Type", "")
            instrument = row.get("Instrument Type", "")

            # Handle assignment/expiration entries
            if rtype == "Receive Deliver" and instrument == "Equity Option":
                if sub_type == "Assignment":
                    underlying = row.get("Underlying Symbol", "").strip()
                    option_type = row.get("Call or Put", "").upper()
                    strike = float(row.get("Strike Price", "0") or "0")
                    expiry_raw = row.get("Expiration Date", "")
                    expiry = parse_date_mdy(expiry_raw)
                    qty = int(parse_amount(row.get("Quantity", "0")))
                    date_raw = row.get("Date", "")
                    date = date_raw[:10] if date_raw else None

                    trades.append({
                        "broker": "Tastytrade",
                        "date": date,
                        "direction": "ASSIGNED",
                        "underlying": underlying,
                        "option_type": option_type,
                        "strike": strike,
                        "expiry": expiry,
                        "qty": abs(qty),
                        "price": 0.0,
                        "commission": 0.0,
                        "fees": 0.0,
                        "amount": 0.0,
                        "order_id": None,
                        "timestamp": date_raw,
                    })
                elif sub_type == "Expiration":
                    underlying = row.get("Underlying Symbol", "").strip()
                    option_type = row.get("Call or Put", "").upper()
                    strike = float(row.get("Strike Price", "0") or "0")
                    expiry_raw = row.get("Expiration Date", "")
                    expiry = parse_date_mdy(expiry_raw)
                    qty = int(parse_amount(row.get("Quantity", "0")))
                    date_raw = row.get("Date", "")
                    date = date_raw[:10] if date_raw else None

                    trades.append({
                        "broker": "Tastytrade",
                        "date": date,
                        "direction": "EXPIRED",
                        "underlying": underlying,
                        "option_type": option_type,
                        "strike": strike,
                        "expiry": expiry,
                        "qty": abs(qty),
                        "price": 0.0,
                        "commission": 0.0,
                        "fees": 0.0,
                        "amount": 0.0,
                        "order_id": None,
                        "timestamp": date_raw,
                    })
                continue

            if rtype != "Trade":
                continue
            if instrument != "Equity Option":
                continue

            sub_type = row.get("Sub Type", "")
            action = row.get("Action", "")

            if "Sell to Open" in sub_type:
                direction = "STO"
            elif "Buy to Open" in sub_type:
                direction = "BTO"
            elif "Buy to Close" in sub_type:
                direction = "BTC"
            elif "Sell to Close" in sub_type:
                direction = "STC"
            else:
                continue

            underlying = row.get("Underlying Symbol", "").strip()
            option_type = row.get("Call or Put", "").upper()
            strike = float(row.get("Strike Price", "0") or "0")
            expiry_raw = row.get("Expiration Date", "")
            expiry = parse_date_mdy(expiry_raw)
            value = parse_amount(row.get("Value", "0"))
            qty = int(parse_amount(row.get("Quantity", "0")))
            commission = parse_amount(row.get("Commissions", "0"))
            fees_val = parse_amount(row.get("Fees", "0"))
            total = parse_amount(row.get("Total", "0"))
            order_id = row.get("Order #", "").strip()

            date_raw = row.get("Date", "")
            date = date_raw[:10] if date_raw else None

            trades.append({
                "broker": "Tastytrade",
                "date": date,
                "direction": direction,
                "underlying": underlying,
                "option_type": option_type,
                "strike": strike,
                "expiry": expiry,
                "qty": abs(qty),
                "price": abs(value) / max(abs(qty), 1) / 100 if qty else abs(value) / 100,
                "commission": abs(commission),
                "fees": abs(fees_val),
                "amount": total,
                "order_id": order_id,
                "timestamp": date_raw,
            })
    return trades


def parse_thinkorswim(filepath: Path) -> tuple:
    """Parse Thinkorswim account statement CSV. Returns (option_trades, stock_trades).
    Handles both old format (Cash Balance section with TRD rows) and new format
    (Date, Action, Symbol, Description, Quantity, Price, Fees & Comm, Amount)."""
    option_trades = []
    stock_trades = []

    with open(filepath, "r", encoding="utf-8-sig") as f:
        first_line = f.readline().strip().strip('"')
        f.seek(0)
        lines = f.readlines()

    # Detect format by first line
    if first_line.startswith("Date") and "Action" in first_line:
        return _parse_tos_new_format(lines)
    else:
        return _parse_tos_old_format(lines)


def _parse_tos_new_format(lines: List[str]) -> tuple:
    """Parse new TOS format: Date, Action, Symbol, Description, Quantity, Price, Fees & Comm, Amount"""
    import io
    option_trades = []
    stock_trades = []

    reader = csv.DictReader(io.StringIO("".join(lines)))
    for row in reader:
        action = (row.get("Action") or "").strip()
        symbol = (row.get("Symbol") or "").strip()
        description = (row.get("Description") or "").strip()
        qty_raw = row.get("Quantity") or "0"
        price_raw = (row.get("Price") or "").replace("$", "").replace(",", "").strip()
        fees_raw = (row.get("Fees & Comm") or "").replace("$", "").replace(",", "").strip()
        amount_raw = (row.get("Amount") or "").replace("$", "").replace(",", "").strip()
        date_raw = (row.get("Date") or "").strip()

        # Handle "06/15/2026 as of 06/12/2026" date format
        if " as of " in date_raw:
            date_raw = date_raw.split(" as of ")[0].strip()
        date = parse_date_mdy(date_raw)

        qty = int(parse_amount(qty_raw)) if qty_raw else 0
        price = float(price_raw) if price_raw else 0.0
        fees = abs(float(fees_raw)) if fees_raw else 0.0
        amount = float(amount_raw) if amount_raw else 0.0

        # Determine if option by checking symbol pattern: "TICKER MM/DD/YYYY STRIKE C/P"
        is_option = action in ("Sell to Open", "Buy to Close", "Expired", "Assigned") and (" P" in symbol or " C" in symbol)

        if action in ("Buy", "Sell") and not is_option:
            stock_trades.append({
                "date": date,
                "broker": "Thinkorswim",
                "action": "BOT" if action == "Buy" else "SOLD",
                "ticker": symbol.split()[0] if symbol else "",
                "qty": abs(qty),
                "price": price,
                "amount": amount,
            })
            continue

        if not is_option:
            continue

        # Parse symbol: "TICKER MM/DD/YYYY STRIKE P/C" e.g. "SMCI 06/18/2026 28.00 P"
        sym_m = re.match(r'([A-Z]+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([PC])', symbol)
        if not sym_m:
            continue

        ticker = sym_m.group(1)
        expiry = parse_date_mdy(sym_m.group(2))
        strike = float(sym_m.group(3))
        option_type = "PUT" if sym_m.group(4) == "P" else "CALL"

        if action == "Sell to Open":
            direction = "STO"
        elif action == "Buy to Close":
            direction = "BTC"
        elif action == "Expired":
            direction = "EXPIRED"
        elif action == "Assigned":
            direction = "ASSIGNED"
        else:
            continue

        option_trades.append({
            "broker": "Thinkorswim",
            "date": date,
            "direction": direction,
            "underlying": ticker,
            "option_type": option_type,
            "strike": strike,
            "expiry": expiry,
            "qty": abs(qty),
            "price": price,
            "commission": fees,
            "fees": 0.0,
            "amount": amount,
            "order_id": None,
            "timestamp": date_raw,
        })

    return option_trades, stock_trades


def _parse_tos_old_format(lines: List[str]) -> tuple:
    """Parse old TOS format: Cash Balance section with TRD rows."""
    option_trades = []
    stock_trades = []

    in_cash_section = False
    headers = None

    for line in lines:
        line = line.strip()
        if "Cash Balance" in line and "DATE" not in line:
            in_cash_section = True
            continue
        if in_cash_section and line.startswith("DATE,"):
            headers = line
            continue
        if not in_cash_section or not headers:
            continue

        parts = line.split(",")
        if len(parts) < 8:
            continue

        row_type = parts[2].strip() if len(parts) > 2 else ""
        if row_type != "TRD":
            continue

        date_raw = parts[0].strip()
        description = parts[4].strip().strip('"')
        misc_fees = parse_amount(parts[5]) if len(parts) > 5 else 0.0
        commissions = parse_amount(parts[6]) if len(parts) > 6 else 0.0
        amount = parse_amount(parts[7]) if len(parts) > 7 else 0.0

        date = parse_date_mdy(date_raw)

        is_option = "CALL" in description.upper() or "PUT" in description.upper()

        if not is_option:
            action_m = re.match(r'(BOT|SOLD)\s+([+-]?\d+)\s+([A-Z]+)\s+@([\d.]+)', description)
            if action_m:
                stock_trades.append({
                    "date": date,
                    "broker": "Thinkorswim",
                    "action": action_m.group(1),
                    "ticker": action_m.group(3),
                    "qty": abs(int(action_m.group(2))),
                    "price": float(action_m.group(4)),
                    "amount": amount,
                })
            continue

        opt_m = re.match(
            r'(BOT|SOLD)\s+([+-]?\d+)\s+([A-Z]+)\s+100\s+(?:\(Weeklys\)\s+)?(\d{1,2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{2})\s+([\d.]+)\s+(CALL|PUT)\s+@([\d.]+)',
            description, re.IGNORECASE
        )
        if not opt_m:
            continue

        bot_sold = opt_m.group(1).upper()
        qty = abs(int(opt_m.group(2)))
        ticker = opt_m.group(3)
        day = int(opt_m.group(4))
        months_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
        mon = months_map[opt_m.group(5).upper()]
        year = 2000 + int(opt_m.group(6))
        strike = float(opt_m.group(7))
        option_type = opt_m.group(8).upper()
        price = float(opt_m.group(9))

        expiry = f"{year}-{mon:02d}-{day:02d}"

        if bot_sold == "SOLD":
            direction = "STO"
        else:
            direction = "BTC"

        option_trades.append({
            "broker": "Thinkorswim",
            "date": date,
            "direction": direction,
            "underlying": ticker,
            "option_type": option_type,
            "strike": strike,
            "expiry": expiry,
            "qty": qty,
            "price": price,
            "commission": abs(commissions),
            "fees": abs(misc_fees),
            "amount": amount,
            "order_id": None,
            "timestamp": f"{date_raw} {parts[1].strip()}" if len(parts) > 1 else date_raw,
        })

    return option_trades, stock_trades
