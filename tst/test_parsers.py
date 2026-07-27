"""Tests for broker parsers and matcher logic."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parsers import parse_fidelity, parse_tastytrade, parse_thinkorswim, parse_amount, parse_date_mdy
from matcher import filter_csp_cc, match_trades, detect_spreads_tasty


def test_parse_amount():
    assert parse_amount("1,260.00") == 1260.00
    assert parse_amount("-4,490.00") == -4490.00
    assert parse_amount("0") == 0.0
    assert parse_amount("") == 0.0
    assert parse_amount("78.00") == 78.00
    print("  parse_amount: PASS")


def test_parse_date():
    assert parse_date_mdy("09/30/2025") == "2025-09-30"
    assert parse_date_mdy("9/1/25") == "2025-09-01"
    assert parse_date_mdy("11/21/25") == "2025-11-21"
    assert parse_date_mdy("") is None
    print("  parse_date_mdy: PASS")


def test_fidelity_parser():
    inp = Path(__file__).parent.parent / ".local/options-pnl/inp/fidelity"
    files = sorted(inp.glob("*.csv"))
    if not files:
        print("  fidelity parser: SKIP (no input files)")
        return

    trades = parse_fidelity(files[0])
    assert len(trades) > 0, "Expected at least one trade"
    t = trades[0]
    assert t["broker"] == "Fidelity"
    assert t["direction"] in ("STO", "BTO", "BTC", "STC")
    assert t["option_type"] in ("CALL", "PUT")
    assert t["underlying"] != ""
    assert t["strike"] > 0
    assert t["expiry"] is not None
    print(f"  fidelity parser: PASS ({len(trades)} trades)")


def test_tastytrade_parser():
    inp = Path(__file__).parent.parent / ".local/options-pnl/inp/tasty"
    files = sorted(inp.glob("*.csv"))
    if not files:
        print("  tastytrade parser: SKIP (no input files)")
        return

    trades = parse_tastytrade(files[0])
    assert len(trades) > 0, "Expected at least one trade"
    t = trades[0]
    assert t["broker"] == "Tastytrade"
    assert t["direction"] in ("STO", "BTO", "BTC", "STC")
    assert t["option_type"] in ("CALL", "PUT")
    print(f"  tastytrade parser: PASS ({len(trades)} trades)")


def test_thinkorswim_parser():
    inp = Path(__file__).parent.parent / ".local/options-pnl/inp/thinknswim"
    files = sorted(inp.glob("*.csv"))
    if not files:
        print("  thinkorswim parser: SKIP (no input files)")
        return

    opt_trades, stk_trades = parse_thinkorswim(files[0])
    assert len(opt_trades) + len(stk_trades) > 0, "Expected at least one trade"
    if opt_trades:
        t = opt_trades[0]
        assert t["broker"] == "Thinkorswim"
        assert t["option_type"] in ("CALL", "PUT")
    print(f"  thinkorswim parser: PASS ({len(opt_trades)} options, {len(stk_trades)} stocks)")


def test_filter_csp_cc():
    trades = [
        {"broker": "Test", "direction": "STO", "option_type": "PUT", "underlying": "AAPL",
         "expiry": "2025-10-01", "strike": 150, "order_id": "100", "date": "2025-09-01",
         "qty": 1, "price": 2.0, "commission": 0, "fees": 0, "amount": 200, "timestamp": "2025-09-01"},
        {"broker": "Test", "direction": "BTO", "option_type": "PUT", "underlying": "AAPL",
         "expiry": "2025-10-01", "strike": 145, "order_id": "100", "date": "2025-09-01",
         "qty": 1, "price": 1.0, "commission": 0, "fees": 0, "amount": -100, "timestamp": "2025-09-01"},
        {"broker": "Test", "direction": "STO", "option_type": "CALL", "underlying": "MSFT",
         "expiry": "2025-10-01", "strike": 400, "order_id": "200", "date": "2025-09-02",
         "qty": 1, "price": 3.0, "commission": 0, "fees": 0, "amount": 300, "timestamp": "2025-09-02"},
        {"broker": "Test", "direction": "BTO", "option_type": "CALL", "underlying": "GOOG",
         "expiry": "2025-10-01", "strike": 180, "order_id": "300", "date": "2025-09-03",
         "qty": 1, "price": 5.0, "commission": 0, "fees": 0, "amount": -500, "timestamp": "2025-09-03"},
    ]

    # Trade 0+1 = spread (same order_id, one STO one BTO). Should be excluded.
    # Trade 2 = standalone STO CALL (CC). Should be included.
    # Trade 3 = standalone BTO. Should be excluded as long option.

    # Mock tastytrade broker for spread detection
    for t in trades:
        t["broker"] = "Tastytrade"

    filtered, excluded = filter_csp_cc(trades)

    assert excluded["spread_legs"] == 2, f"Expected 2 spread legs, got {excluded['spread_legs']}"
    assert excluded["long_options"] == 1, f"Expected 1 long option, got {excluded['long_options']}"
    assert len(filtered) == 1, f"Expected 1 filtered trade, got {len(filtered)}"
    assert filtered[0]["underlying"] == "MSFT"
    print("  filter_csp_cc: PASS")


def test_match_trades():
    trades = [
        {"broker": "Test", "direction": "STO", "underlying": "AAPL", "option_type": "PUT",
         "strike": 150, "expiry": "2025-10-01", "qty": 2, "price": 3.0, "date": "2025-09-01",
         "commission": 1.0, "fees": 0.5},
        {"broker": "Test", "direction": "BTC", "underlying": "AAPL", "option_type": "PUT",
         "strike": 150, "expiry": "2025-10-01", "qty": 2, "price": 1.0, "date": "2025-09-15",
         "commission": 1.0, "fees": 0.5},
    ]

    closed, unmatched = match_trades(trades)
    assert len(closed) == 1
    assert closed[0]["strategy"] == "CSP"
    assert closed[0]["qty"] == 2
    # PnL = (3.0 * 2 * 100) - (1.0 * 2 * 100) = 600 - 200 = 400 gross
    assert closed[0]["gross_pnl"] == 400.0
    # Fees = (1.0 + 0.5) + (1.0 + 0.5) = 3.0
    assert closed[0]["fees"] == 3.0
    assert closed[0]["net_pnl"] == 397.0
    assert len(unmatched) == 0
    print("  match_trades: PASS")


def test_full_pipeline():
    """Integration test: run compute_pnl on real data."""
    inp = Path(__file__).parent.parent / ".local/options-pnl/inp"
    if not inp.exists():
        print("  full pipeline: SKIP (no input dir)")
        return

    from compute_pnl import main as compute_main
    import tempfile
    out_file = Path(tempfile.mktemp(suffix=".json"))

    sys.argv = ["compute_pnl.py", "--input", str(inp), "--output", str(out_file)]
    compute_main()

    assert out_file.exists()
    with open(out_file) as f:
        data = json.load(f)

    assert "closed_trades" in data
    assert "summary" in data
    assert "monthly_all" in data
    assert "weekly_all" in data
    assert data["summary"]["total_trades"] > 0
    print(f"  full pipeline: PASS ({data['summary']['total_trades']} trades, net ${data['summary']['total_net_pnl']:,.2f})")

    out_file.unlink()


if __name__ == "__main__":
    print("Running tests...")
    test_parse_amount()
    test_parse_date()
    test_fidelity_parser()
    test_tastytrade_parser()
    test_thinkorswim_parser()
    test_filter_csp_cc()
    test_match_trades()
    test_full_pipeline()
    print("\nAll tests passed!")
