#!/usr/bin/env python3
"""
Generate a self-contained HTML dashboard from super-agent eval JSON files.

Usage:
    pip install plotly
    python3 src/dashboard/generate.py \
        --evals-dir .local/logs/super-agent/evals/ \
        --output .local/logs/super-agent/dashboard.html
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    import plotly.graph_objects as go
    import plotly.offline
except ImportError:
    print("Error: plotly is required. Install with: pip install plotly", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Design tokens (from dataviz palette -- status colors for state encoding,
# categorical slots for identity encoding)
# ---------------------------------------------------------------------------

# Status colors -- used for PASS/FAIL/SKIP state encoding
COLOR_GOOD = "#0ca30c"       # PASS
COLOR_CRITICAL = "#d03b3b"   # FAIL
COLOR_SKIP_GRAY = "#898781"  # SKIP (muted)

# Pass-rate tier colors (status semantics)
COLOR_RATE_HIGH = "#0ca30c"    # >= 90%
COLOR_RATE_MED = "#fab219"     # 70-90%
COLOR_RATE_LOW = "#d03b3b"     # < 70%

# Categorical slots (fixed order from palette.md) for dimensions / gap codes
CAT_BLUE = "#2a78d6"
CAT_ORANGE = "#eb6834"
CAT_AQUA = "#1baf7a"
CAT_YELLOW = "#eda100"
CAT_MAGENTA = "#e87ba4"
CAT_GREEN = "#008300"
CAT_VIOLET = "#4a3aa7"
CAT_RED = "#e34948"

CATEGORICAL_SLOTS = [
    CAT_BLUE, CAT_ORANGE, CAT_AQUA, CAT_YELLOW,
    CAT_MAGENTA, CAT_GREEN, CAT_VIOLET, CAT_RED,
]

# Dimension color mapping (fixed assignment -- color follows entity, never rank)
DIMENSION_COLORS = {
    "efficiency": CAT_BLUE,
    "routing": CAT_ORANGE,
    "protocol": CAT_AQUA,
    "prerequisite": CAT_YELLOW,
    "completeness": CAT_MAGENTA,
    "quality": CAT_GREEN,
}

# Chrome
SURFACE = "#fcfcfb"
PAGE_PLANE = "#f9f9f7"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

FONT_STACK = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# Plotly layout defaults -- recessive grid, thin marks, light theme
LAYOUT_DEFAULTS = dict(
    font=dict(family=FONT_STACK, color=PRIMARY_INK, size=13),
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    margin=dict(l=60, r=30, t=50, b=50),
    xaxis=dict(
        gridcolor=GRIDLINE, gridwidth=1, linecolor=BASELINE, linewidth=1,
        zerolinecolor=BASELINE, zerolinewidth=1,
    ),
    yaxis=dict(
        gridcolor=GRIDLINE, gridwidth=1, linecolor=BASELINE, linewidth=1,
        zerolinecolor=BASELINE, zerolinewidth=1,
    ),
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_evals(evals_dir: Path) -> list[dict]:
    """Load and sort eval JSON files chronologically."""
    evals = []
    for p in sorted(evals_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            evals.append(data)
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"  warning: skipping {p.name}: {exc}", file=sys.stderr)
    # Sort by session label (lexicographic works for YYYY-MM-DD and suffixed variants)
    evals.sort(key=lambda e: e.get("session", ""))
    return evals


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def pass_rate(ev: dict) -> float:
    """Compute pass / (pass + fail), ignoring skips. Returns 0-100."""
    c = ev.get("combined", ev.get("tier1", {}))
    p = c.get("total_pass", c.get("pass", 0))
    f = c.get("total_fail", c.get("fail", 0))
    denom = p + f
    return (p / denom * 100) if denom > 0 else 100.0


def rate_color(rate: float) -> str:
    if rate >= 90:
        return COLOR_RATE_HIGH
    if rate >= 70:
        return COLOR_RATE_MED
    return COLOR_RATE_LOW


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def _base_layout(**overrides) -> dict:
    """Merge LAYOUT_DEFAULTS with per-chart overrides."""
    layout = {}
    for k, v in LAYOUT_DEFAULTS.items():
        if isinstance(v, dict):
            layout[k] = {**v, **overrides.pop(k, {})}
        else:
            layout[k] = v
    layout.update(overrides)
    return layout


def chart_session_timeline(evals: list[dict]) -> go.Figure:
    """Horizontal bar chart -- one bar per session, colored by pass rate."""
    sessions = [e["session"] for e in evals]
    rates = [pass_rate(e) for e in evals]
    colors = [rate_color(r) for r in rates]

    hover_texts = []
    for e, r in zip(evals, rates):
        c = e.get("combined", e.get("tier1", {}))
        p = c.get("total_pass", c.get("pass", 0))
        f = c.get("total_fail", c.get("fail", 0))
        s = c.get("total_skip", c.get("skip", 0))
        gaps = c.get("all_gaps", [])
        gap_str = ", ".join(gaps) if gaps else "none"
        hover_texts.append(
            f"<b>{e['session']}</b><br>"
            f"Pass: {p}  Fail: {f}  Skip: {s}<br>"
            f"Rate: {r:.1f}%<br>"
            f"Gaps: {gap_str}"
        )

    fig = go.Figure(go.Bar(
        y=sessions,
        x=rates,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
        hovertext=hover_texts,
        hoverinfo="text",
        width=0.6,
    ))
    fig.update_layout(
        **_base_layout(
            title=None,
            xaxis=dict(
                title="Pass Rate (%)", range=[0, 105],
                gridcolor=GRIDLINE, linecolor=BASELINE,
            ),
            yaxis=dict(
                title=None, autorange="reversed",
                gridcolor=GRIDLINE, linecolor=BASELINE,
            ),
            height=max(250, len(evals) * 50 + 100),
        )
    )
    return fig


def chart_pass_rate_trend(evals: list[dict]) -> go.Figure:
    """Line chart of pass rate over sessions with a 90% target reference line."""
    sessions = [e["session"] for e in evals]
    rates = [pass_rate(e) for e in evals]

    fig = go.Figure()

    # 90% target reference line
    fig.add_hline(
        y=90, line=dict(color=MUTED_INK, width=1, dash="dot"),
        annotation_text="90% target",
        annotation_position="top left",
        annotation_font=dict(color=MUTED_INK, size=11),
    )

    fig.add_trace(go.Scatter(
        x=sessions,
        y=rates,
        mode="lines+markers",
        line=dict(color=CAT_BLUE, width=2),
        marker=dict(size=8, color=CAT_BLUE, line=dict(color=SURFACE, width=2)),
        hovertemplate="<b>%{x}</b><br>Pass rate: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=None,
            xaxis=dict(title=None, gridcolor=GRIDLINE, linecolor=BASELINE),
            yaxis=dict(
                title="Pass Rate (%)", range=[0, 105],
                gridcolor=GRIDLINE, linecolor=BASELINE,
            ),
            height=320,
            showlegend=False,
        )
    )
    return fig


def chart_gap_frequency(evals: list[dict]) -> go.Figure:
    """Bar chart of gap code frequency across all sessions."""
    gap_counter: Counter[str] = Counter()
    for e in evals:
        c = e.get("combined", e.get("tier1", {}))
        for g in c.get("all_gaps", []):
            gap_counter[g] += 1

    if not gap_counter:
        # Empty state -- single text annotation
        fig = go.Figure()
        fig.add_annotation(
            text="No gaps recorded", xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=MUTED_INK),
        )
        fig.update_layout(**_base_layout(height=320))
        return fig

    codes = sorted(gap_counter.keys())
    counts = [gap_counter[c] for c in codes]
    colors = [CATEGORICAL_SLOTS[i % len(CATEGORICAL_SLOTS)] for i, _ in enumerate(codes)]

    fig = go.Figure(go.Bar(
        x=codes,
        y=counts,
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{x}</b><br>Occurrences: %{y}<extra></extra>",
        width=0.5,
    ))
    fig.update_layout(
        **_base_layout(
            title=None,
            xaxis=dict(title="Gap Code", gridcolor=GRIDLINE, linecolor=BASELINE),
            yaxis=dict(
                title="Count", dtick=1,
                gridcolor=GRIDLINE, linecolor=BASELINE,
            ),
            height=320,
        )
    )
    return fig


def chart_rule_heatmap(evals: list[dict]) -> go.Figure:
    """Heatmap: rules (Y) x sessions (X), colored PASS/FAIL/SKIP."""
    sessions = [e["session"] for e in evals]

    # Collect all rules in stable order from the first eval that has results
    all_rules: list[str] = []
    seen = set()
    for e in evals:
        for r in e.get("tier1", {}).get("results", []):
            rid = r["rule"]
            if rid not in seen:
                seen.add(rid)
                all_rules.append(rid)

    # Build verdict matrix: 1=PASS, -1=FAIL, 0=SKIP
    verdict_map = {"PASS": 1, "FAIL": -1, "SKIP": 0, "MINOR": 0.5}
    z = []
    hover = []
    for rule in reversed(all_rules):  # reversed so top rule is first alphabetically
        row_z = []
        row_h = []
        for e in evals:
            results = {r["rule"]: r for r in e.get("tier1", {}).get("results", [])}
            r = results.get(rule)
            if r:
                v = r.get("verdict", "SKIP")
                row_z.append(verdict_map.get(v, 0))
                evidence = r.get("evidence", "")
                row_h.append(
                    f"<b>{rule}</b> ({e['session']})<br>"
                    f"Verdict: {v}<br>"
                    f"Evidence: {evidence}"
                )
            else:
                row_z.append(0)
                row_h.append(f"<b>{rule}</b> ({e['session']})<br>Not evaluated")
        z.append(row_z)
        hover.append(row_h)

    # Discrete colorscale: -1=red, 0=gray, 0.5=yellow, 1=green
    colorscale = [
        [0.0, COLOR_CRITICAL],     # -1 -> FAIL
        [0.375, COLOR_CRITICAL],
        [0.375, COLOR_SKIP_GRAY],  # 0 -> SKIP
        [0.625, COLOR_SKIP_GRAY],
        [0.625, COLOR_RATE_MED],   # 0.5 -> MINOR
        [0.75, COLOR_RATE_MED],
        [0.75, COLOR_GOOD],        # 1 -> PASS
        [1.0, COLOR_GOOD],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=sessions,
        y=list(reversed(all_rules)),
        colorscale=colorscale,
        zmin=-1,
        zmax=1,
        hovertext=hover,
        hoverinfo="text",
        showscale=False,
        xgap=2,
        ygap=2,
    ))

    fig.update_layout(
        **_base_layout(
            title=None,
            xaxis=dict(title=None, side="bottom", gridcolor=GRIDLINE, linecolor=BASELINE),
            yaxis=dict(title=None, gridcolor=GRIDLINE, linecolor=BASELINE),
            height=max(400, len(all_rules) * 28 + 100),
        )
    )
    return fig


def chart_dimension_breakdown(evals: list[dict]) -> go.Figure:
    """Stacked bar chart: per dimension, showing pass/fail/skip totals."""
    dim_totals: dict[str, dict[str, int]] = {}

    for e in evals:
        by_dim = e.get("tier1", {}).get("by_dimension", {})
        if by_dim:
            for dim, counts in by_dim.items():
                if dim not in dim_totals:
                    dim_totals[dim] = {"pass": 0, "fail": 0, "skip": 0}
                dim_totals[dim]["pass"] += counts.get("pass", 0)
                dim_totals[dim]["fail"] += counts.get("fail", 0)
                dim_totals[dim]["skip"] += counts.get("skip", 0)
        else:
            # Fallback: derive from results list
            for r in e.get("tier1", {}).get("results", []):
                dim = r.get("dimension", "unknown")
                if dim not in dim_totals:
                    dim_totals[dim] = {"pass": 0, "fail": 0, "skip": 0}
                v = r.get("verdict", "SKIP").lower()
                if v in dim_totals[dim]:
                    dim_totals[dim][v] += 1

    dims = sorted(dim_totals.keys())
    pass_vals = [dim_totals[d]["pass"] for d in dims]
    fail_vals = [dim_totals[d]["fail"] for d in dims]
    skip_vals = [dim_totals[d]["skip"] for d in dims]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Pass", x=dims, y=pass_vals,
        marker=dict(color=COLOR_GOOD, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{x}</b><br>Pass: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Fail", x=dims, y=fail_vals,
        marker=dict(color=COLOR_CRITICAL, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{x}</b><br>Fail: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Skip", x=dims, y=skip_vals,
        marker=dict(color=COLOR_SKIP_GRAY, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{x}</b><br>Skip: %{y}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=None,
            barmode="stack",
            xaxis=dict(title=None, gridcolor=GRIDLINE, linecolor=BASELINE),
            yaxis=dict(title="Rule Evaluations", gridcolor=GRIDLINE, linecolor=BASELINE),
            height=320,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=12),
            ),
        )
    )
    return fig


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def compute_summary(evals: list[dict]) -> dict:
    total_sessions = len(evals)
    rates = [(e["session"], pass_rate(e)) for e in evals]

    if not rates:
        return {
            "total_sessions": 0,
            "overall_pass_rate": 0,
            "most_common_gap": "N/A",
            "cleanest_session": "N/A",
            "worst_session": "N/A",
        }

    overall_pass = sum(
        e.get("combined", e.get("tier1", {})).get("total_pass", e.get("tier1", {}).get("pass", 0))
        for e in evals
    )
    overall_fail = sum(
        e.get("combined", e.get("tier1", {})).get("total_fail", e.get("tier1", {}).get("fail", 0))
        for e in evals
    )
    overall_rate = (overall_pass / (overall_pass + overall_fail) * 100) if (overall_pass + overall_fail) > 0 else 100.0

    gap_counter: Counter[str] = Counter()
    for e in evals:
        c = e.get("combined", e.get("tier1", {}))
        for g in c.get("all_gaps", []):
            gap_counter[g] += 1

    most_common_gap = gap_counter.most_common(1)[0][0] if gap_counter else "None"

    cleanest = max(rates, key=lambda x: (x[1], x[0]))
    worst = min(rates, key=lambda x: (x[1], x[0]))

    return {
        "total_sessions": total_sessions,
        "overall_pass_rate": overall_rate,
        "most_common_gap": most_common_gap,
        "cleanest_session": f"{cleanest[0]} ({cleanest[1]:.0f}%)",
        "worst_session": f"{worst[0]} ({worst[1]:.0f}%)",
    }


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def _chart_div(fig: go.Figure) -> str:
    """Render a Plotly figure to a raw HTML div string (no full page wrapper)."""
    return plotly.offline.plot(fig, output_type="div", include_plotlyjs=False)


def build_html(evals: list[dict], summary: dict) -> str:
    """Assemble all charts and cards into a single self-contained HTML page."""

    # Generate chart divs
    timeline_div = _chart_div(chart_session_timeline(evals))
    trend_div = _chart_div(chart_pass_rate_trend(evals))
    gap_div = _chart_div(chart_gap_frequency(evals))
    heatmap_div = _chart_div(chart_rule_heatmap(evals))
    dimension_div = _chart_div(chart_dimension_breakdown(evals))

    # Get plotly.js source for embedding
    plotly_js = plotly.offline.get_plotlyjs()

    rate_pct = f'{summary["overall_pass_rate"]:.1f}%'
    rate_color = (
        COLOR_RATE_HIGH if summary["overall_pass_rate"] >= 90
        else COLOR_RATE_MED if summary["overall_pass_rate"] >= 70
        else COLOR_RATE_LOW
    )

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Super-Agent Evaluation Dashboard</title>
<script>{plotly_js}</script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px;
    background: {PAGE_PLANE};
    color: {PRIMARY_INK};
    font-family: {FONT_STACK};
    font-size: 14px;
    line-height: 1.5;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 20px 0;
    color: {PRIMARY_INK};
  }}

  /* Summary cards row */
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }}
  .card {{
    background: {SURFACE};
    border: 1px solid {GRIDLINE};
    border-radius: 8px;
    padding: 16px;
  }}
  .card-label {{
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: {MUTED_INK};
    margin: 0 0 4px 0;
  }}
  .card-value {{
    font-size: 26px;
    font-weight: 700;
    margin: 0;
    color: {PRIMARY_INK};
  }}
  .card-value.rate {{ color: {rate_color}; }}

  /* Chart grid */
  .chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }}
  .chart-box {{
    background: {SURFACE};
    border: 1px solid {GRIDLINE};
    border-radius: 8px;
    padding: 16px;
    overflow: hidden;
  }}
  .chart-box.full-width {{
    grid-column: 1 / -1;
  }}
  .chart-subtitle {{
    font-size: 15px;
    font-weight: 600;
    color: {PRIMARY_INK};
    margin: 0 0 8px 0;
  }}
  .chart-desc {{
    font-size: 12px;
    color: {SECONDARY_INK};
    margin: 0 0 12px 0;
  }}

  /* Legend for heatmap */
  .heatmap-legend {{
    display: flex;
    gap: 16px;
    margin-top: 8px;
    font-size: 12px;
    color: {SECONDARY_INK};
  }}
  .heatmap-legend span {{
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .legend-swatch {{
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 3px;
  }}

  /* Responsive: single column on narrow screens */
  @media (max-width: 860px) {{
    .chart-grid {{ grid-template-columns: 1fr; }}
  }}

  /* Plotly overrides -- remove unnecessary whitespace */
  .js-plotly-plot .plotly .modebar {{ display: none !important; }}
</style>
</head>
<body>

<h1>&#127919; Super-Agent Evaluation Dashboard</h1>

<div class="cards">
  <div class="card">
    <p class="card-label">Total Sessions</p>
    <p class="card-value">{summary['total_sessions']}</p>
  </div>
  <div class="card">
    <p class="card-label">Overall Pass Rate</p>
    <p class="card-value rate">{rate_pct}</p>
  </div>
  <div class="card">
    <p class="card-label">Most Common Gap</p>
    <p class="card-value">{summary['most_common_gap']}</p>
  </div>
  <div class="card">
    <p class="card-label">Cleanest Session</p>
    <p class="card-value" style="font-size: 18px;">{summary['cleanest_session']}</p>
  </div>
  <div class="card">
    <p class="card-label">Worst Session</p>
    <p class="card-value" style="font-size: 18px;">{summary['worst_session']}</p>
  </div>
</div>

<div class="chart-grid">

  <div class="chart-box">
    <p class="chart-subtitle">Session Timeline</p>
    <p class="chart-desc">One bar per session, colored by pass rate (green &ge;90%, yellow 70-90%, red &lt;70%)</p>
    {timeline_div}
  </div>

  <div class="chart-box">
    <p class="chart-subtitle">Pass Rate Trend</p>
    <p class="chart-desc">Pass rate over sessions with 90% target reference</p>
    {trend_div}
  </div>

  <div class="chart-box">
    <p class="chart-subtitle">Gap Frequency</p>
    <p class="chart-desc">Gap codes across all sessions (only codes with &gt;0 occurrences)</p>
    {gap_div}
  </div>

  <div class="chart-box">
    <p class="chart-subtitle">Dimension Breakdown</p>
    <p class="chart-desc">Pass / fail / skip distribution per evaluation dimension</p>
    {dimension_div}
  </div>

  <div class="chart-box full-width">
    <p class="chart-subtitle">Rule Heatmap</p>
    <p class="chart-desc">Rules (Y) vs sessions (X) &mdash; shows at a glance which rules fail on which sessions</p>
    {heatmap_div}
    <div class="heatmap-legend">
      <span><span class="legend-swatch" style="background:{COLOR_GOOD};"></span> Pass</span>
      <span><span class="legend-swatch" style="background:{COLOR_CRITICAL};"></span> Fail</span>
      <span><span class="legend-swatch" style="background:{COLOR_SKIP_GRAY};"></span> Skip</span>
    </div>
  </div>

</div>

</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a self-contained HTML dashboard from super-agent eval JSON files."
    )
    parser.add_argument(
        "--evals-dir", required=True, type=Path,
        help="Directory containing eval JSON files",
    )
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Output path for the HTML dashboard",
    )
    args = parser.parse_args()

    if not args.evals_dir.is_dir():
        print(f"Error: evals directory not found: {args.evals_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading evals from: {args.evals_dir}")
    evals = load_evals(args.evals_dir)

    if not evals:
        print("Error: no valid eval JSON files found.", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(evals)} eval file(s)")

    summary = compute_summary(evals)
    html = build_html(evals, summary)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)

    print(f"\nDashboard written to: {args.output}")
    print(f"  Total sessions:    {summary['total_sessions']}")
    print(f"  Overall pass rate: {summary['overall_pass_rate']:.1f}%")
    print(f"  Most common gap:   {summary['most_common_gap']}")
    print(f"  Cleanest session:  {summary['cleanest_session']}")
    print(f"  Worst session:     {summary['worst_session']}")


if __name__ == "__main__":
    main()
