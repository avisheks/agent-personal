#!/usr/bin/env python3
"""
Render a weekly report .md into a styled, self-contained .html file.

Reads the markdown source, converts to HTML via the `markdown` library,
wraps in the standard CSS template with topic-grouped P0/P1/P2 styling,
and writes the output alongside the source.

Usage:
    python3 src/skills/tpm/render_weekly_report.py \
        --input .local/data/tpm/e2e-evals/weekly-reports/2026-W42-weekly-report.md

    # Custom output path:
    python3 src/skills/tpm/render_weekly_report.py \
        --input report.md --output report.html
"""

import argparse
import re
from pathlib import Path

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    print("ERROR: 'markdown' package not installed. Run: pip install markdown")
    raise SystemExit(1)

CSS = """\
:root {
  --bg: #fcfcfb; --surface: #fff; --text: #1a1a1a; --text-muted: #6b7280;
  --border: #e5e7eb; --accent: #2563eb; --green: #059669; --amber: #d97706;
  --red: #dc2626; --purple: #7c3aed; --code-bg: #f4f4f5;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.7; max-width: 1092px; margin: 0 auto; padding: 2rem;
  padding-top: 0;
}
.content { }
h1 { font-size: 1.8rem; margin: 2rem 0 .5rem; border-bottom: 2px solid var(--accent); padding-bottom: .3rem; }
h2 { font-size: 1.4rem; margin: 1.8rem 0 .5rem; color: var(--accent); }
h3 { font-size: 1.15rem; margin: 1.4rem 0 .4rem; }
h4 { font-size: 1rem; margin: 1rem 0 .3rem; color: var(--text-muted); }
p { margin: .6rem 0; }
ul, ol { margin: .5rem 0 .5rem 1.5rem; }
li { margin: .2rem 0; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code {
  background: var(--code-bg); padding: .15rem .4rem; border-radius: 4px;
  font-family: 'SF Mono', 'Consolas', monospace; font-size: .88rem;
}
pre {
  background: #1e1e2e; color: #cdd6f4; padding: 1rem; border-radius: 8px;
  overflow-x: auto; margin: .8rem 0; font-size: .85rem; line-height: 1.5;
}
pre code { background: none; padding: 0; color: inherit; }
table { border-collapse: collapse; width: 100%; margin: .8rem 0; }
th {
  background: var(--accent); color: white;
  padding: .5rem .8rem; text-align: left; font-size: .9rem;
}
td { padding: .5rem .8rem; border-bottom: 1px solid var(--border); font-size: .9rem; }
tr:nth-child(even) { background: #f9fafb; }
blockquote {
  border-left: 4px solid var(--accent); padding: .8rem 1rem;
  margin: .8rem 0; background: #eff6ff; border-radius: 0 6px 6px 0;
}
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(248, 250, 252, 0.95); backdrop-filter: blur(8px);
  padding: .6rem 1rem; margin: 0 -2rem 1.5rem -2rem;
  border-bottom: 1px solid var(--border);
  font-size: .8rem; line-height: 1.3;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
nav ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .3rem .6rem; }
nav li { margin: 0; }
nav a {
  display: inline-block; padding: .2rem .5rem; border-radius: 4px;
  white-space: nowrap;
}
nav a:hover { background: #e5e7eb; }
nav .toc-title {
  font-weight: 700; font-size: .82rem; color: var(--accent);
  margin-right: .6rem; display: inline;
}
.back-to-top {
  display: block; text-align: right; font-size: .78rem;
  color: var(--text-muted); margin-top: .5rem; padding-top: .3rem;
  border-top: 1px solid var(--border);
}
.back-to-top:hover { color: var(--accent); }
.meta {
  color: var(--text-muted); font-size: .85rem;
  margin-bottom: 1.5rem; padding-bottom: .5rem; border-bottom: 1px solid var(--border);
}
details { margin: .6rem 0; font-size: .95rem; }
details table { font-size: .9rem; }
details h3 { font-size: 1.1rem; }
summary {
  cursor: pointer; font-weight: 600; padding: .6rem .8rem;
  background: #f3f4f6; border-radius: 6px; font-size: 1rem;
}
summary:hover { background: #e5e7eb; }
.citation {
  font-size: .75rem; color: var(--text-muted); vertical-align: super;
  text-decoration: none; border-bottom: 1px dotted var(--text-muted);
  margin-left: .1rem;
}
.citation:hover { color: var(--accent); border-bottom-color: var(--accent); }

/* Priority sections */
.p0-section {
  background: #fef2f2; border-left: 4px solid var(--red);
  padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;
}
.p1-section {
  background: #fffbeb; border-left: 4px solid var(--amber);
  padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;
}
.p2-section {
  background: #ecfdf5; border-left: 4px solid var(--green);
  padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;
}

/* Status and tags */
.status-green { color: var(--green); font-weight: 700; }
.status-amber { color: var(--amber); font-weight: 700; }
.status-red { color: var(--red); font-weight: 700; }
.why-tag {
  display: inline-block; padding: .1rem .5rem; border-radius: 4px;
  font-size: .78rem; font-weight: 500; margin-right: .3rem;
}
.why-partner { background: #dbeafe; color: #1e40af; }
.why-pm { background: #fce7f3; color: #9d174d; }
.why-industry { background: #e0e7ff; color: #3730a3; }
.why-quality { background: #fef3c7; color: #92400e; }

/* Badges and warnings */
.badge {
  display: inline-block; padding: .15rem .6rem; border-radius: 12px;
  font-size: .78rem; font-weight: 600; color: white;
}
.badge-green { background: var(--green); }
.badge-amber { background: var(--amber); }
.badge-red { background: var(--red); }
.badge-purple { background: var(--purple); }
.badge-blue { background: var(--accent); }
.warning-box {
  background: #fffbeb; border: 1px solid var(--amber);
  padding: .8rem 1rem; border-radius: 8px; margin: 1rem 0;
}
.topic-header {
  font-size: 1rem; margin: 1rem 0 .5rem; padding: .3rem .6rem;
  background: #f3f4f6; border-radius: 6px; display: inline-block;
}
.no-items { color: var(--text-muted); font-style: italic; margin: .5rem 0; }
.overdue { color: var(--red); font-weight: 600; }
.carried { font-style: italic; }
.new-item { font-weight: 700; color: var(--accent); }

/* Science vs Engineering task badges */
.task-type {
  display: inline-block; padding: .1rem .45rem; border-radius: 4px;
  font-size: .72rem; font-weight: 700; letter-spacing: .03em;
  margin-right: .3rem; vertical-align: middle;
}
.task-sci { background: #ede9fe; color: #5b21b6; } /* purple tint for science */
.task-engg { background: #dbeafe; color: #1e40af; } /* blue tint for engineering */

/* Strategic vs Tactical badges */
.ai-type {
  display: inline-block; padding: .1rem .45rem; border-radius: 4px;
  font-size: .72rem; font-weight: 700; letter-spacing: .03em;
  margin-right: .3rem; vertical-align: middle;
}
.ai-str { background: #ccfbf1; color: #0f766e; } /* teal for strategic */
.ai-tac { background: #ffedd5; color: #9a3412; } /* orange for tactical */

/* Asana and code review links */
a[href*="app.asana.com"] {
  background: #f0f4ff; padding: .1rem .4rem; border-radius: 4px;
  font-size: .85rem; border: 1px solid #dbeafe;
}
a[href*="app.asana.com"]::before { content: "📋 "; }
a[href*="code.amazon.com/reviews"] {
  background: #f0fdf4; padding: .1rem .4rem; border-radius: 4px;
  font-size: .85rem; border: 1px solid #bbf7d0;
}
a[href*="code.amazon.com/reviews"]::before { content: "🔗 "; }
"""


def extract_title(md_text: str) -> str:
    """Extract the first H1 as the page title."""
    m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    return m.group(1).strip() if m else "Weekly Report"


SHORT_LABELS = {
    "executive summary": "📋 Summary",
    "top 3 bottlenecks": "🚧 Bottlenecks",
    "key risks": "🔑 Risks",
    "action items for next week": "🎯 AIs",
    "scorecard improvements": "📊 Scorecard",
    "jtbd scoring improvements": "🎯 JTBD",
    "partner evals / gov model": "🤝 Partner",
    "partner evals  gov model": "🤝 Partner",
    "fai annotations": "🏷️ FAI",
    "misc": "📦 Misc",
    "untracked commitments": "⚠️ Untracked",
    "appendix a: references & citations": "📎 Refs",
    "appendix a references  citations": "📎 Refs",
    "appendix b: gaps & maturity": "📎 Gaps",
    "appendix b gaps  maturity": "📎 Gaps",
    "appendix c: literature & news": "📎 Lit",
    "appendix c literature  news": "📎 Lit",
    "week-over-week cross-check": "📊 WoW",
    "completed this week": "✅ Done",
    "p0": "🔴 P0",
    "p1": "🟡 P1",
    "p2": "🟢 P2",
    "week-over-week": "📊 WoW",
}


def _shorten_toc_label(text: str) -> str:
    """Map a heading to a short TOC label for the sticky top-bar."""
    clean = re.sub(r"[^\w\s]", "", text.lower()).strip()
    for key, short in SHORT_LABELS.items():
        if key in clean:
            return short
    # Fallback: take first 2 words + emoji if present
    emoji = re.match(r"^([^\w\s]+)", text)
    prefix = emoji.group(1) + " " if emoji else ""
    words = re.sub(r"^[^\w\s]+\s*", "", text).split()
    return prefix + " ".join(words[:2])


def build_toc(html_body: str) -> str:
    """Build a nav TOC from all <h2> elements with short labels for top-bar."""
    headings = re.findall(r'<h2[^>]*id="([^"]*)"[^>]*>(.*?)</h2>', html_body, re.DOTALL)
    if not headings:
        headings = re.findall(r"<h2>(.*?)</h2>", html_body)
        items = []
        for text in headings:
            slug = re.sub(r"[^\w\s-]", "", text.lower())
            slug = re.sub(r"[\s]+", "-", slug).strip("-")
            items.append((slug, text))
        headings = items

    if not headings:
        return ""

    links = "\n".join(
        f'  <li><a href="#{slug}">{_shorten_toc_label(text)}</a></li>'
        for slug, text in headings
    )
    return f'<nav id="toc">\n<ul>\n{links}\n</ul>\n</nav>\n'


def add_ids_to_headings(html_body: str) -> str:
    """Add id attributes to h2 elements for TOC linking."""
    def make_id(match):
        tag = match.group(1)
        text = match.group(2)
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s]+", "-", slug).strip("-")
        return f'<h{tag} id="{slug}">{text}</h{tag}>'

    return re.sub(r"<h([23])>(.*?)</h\1>", make_id, html_body)


def apply_priority_sections(html: str) -> str:
    """Wrap P0/P1/P2 content blocks in colored section divs."""
    # P0 section
    html = re.sub(
        r"(<h2[^>]*>.*?P0.*?</h2>)",
        r'<div class="p0-section">\n\1',
        html,
    )
    # P1 section
    html = re.sub(
        r"(<h2[^>]*>.*?P1.*?</h2>)",
        lambda m: '</div>\n<div class="p1-section">\n' + m.group(1),
        html,
    )
    # P2 section
    html = re.sub(
        r"(<h2[^>]*>.*?P2.*?</h2>)",
        lambda m: '</div>\n<div class="p2-section">\n' + m.group(1),
        html,
    )
    # Close last priority section before the next h2
    html = re.sub(
        r'(<div class="p2-section">.*?)(<h2[^>]*>(?:(?!P[012]).)*</h2>)',
        lambda m: m.group(1) + "</div>\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )
    return html


def apply_why_tags(html: str) -> str:
    """Color-code WHY justification tags."""
    html = html.replace("🤝 Partner:", '<span class="why-tag why-partner">🤝 Partner</span>')
    html = html.replace("📋 PM:", '<span class="why-tag why-pm">📋 PM</span>')
    html = html.replace("📊 Industry:", '<span class="why-tag why-industry">📊 Industry</span>')
    html = html.replace("🔧 Quality:", '<span class="why-tag why-quality">🔧 Quality</span>')
    return html


def apply_status_badges(html: str) -> str:
    """Style status indicators."""
    html = html.replace(
        "🟡 At Risk",
        '<span class="status-amber">🟡 At Risk</span>',
    )
    html = html.replace(
        "🟢 On Track",
        '<span class="status-green">🟢 On Track</span>',
    )
    html = html.replace(
        "🔴 Off Track",
        '<span class="status-red">🔴 Off Track</span>',
    )
    return html


def apply_item_markers(html: str) -> str:
    """Style carried-over and new-this-week markers."""
    html = html.replace("🔁", '<span class="carried">🔁</span>')
    html = html.replace("🆕", '<span class="new-item">🆕</span>')
    return html


def apply_citations(html: str) -> str:
    """Convert [^source](#ref-source) citation markers to hyperlinked superscript.
    Also handles bare [^source] without explicit link (falls back to title-only)."""
    # First: handle [^source](#ref-source) — linked citations
    html = re.sub(
        r'\[\^([^\]]+)\]\(#(ref-[^\)]+)\)',
        r'<a class="citation" href="#\2" title="\1">[\1]</a>',
        html,
    )
    # Then: handle bare [^source] — unlinked (title-only tooltip)
    html = re.sub(
        r"\[\^([^\]]+)\]",
        r'<a class="citation" title="\1">[\1]</a>',
        html,
    )
    return html


def apply_task_type_badges(html: str) -> str:
    """Convert [Sci], [Engg], [Str], [Tac] markers to colored badges."""
    for marker, cls, label in [
        ("[Sci]", "task-type task-sci", "Sci"),
        ("[sci]", "task-type task-sci", "Sci"),
        ("[SCI]", "task-type task-sci", "Sci"),
        ("[Engg]", "task-type task-engg", "Engg"),
        ("[engg]", "task-type task-engg", "Engg"),
        ("[ENGG]", "task-type task-engg", "Engg"),
        ("[Str]", "ai-type ai-str", "Str"),
        ("[str]", "ai-type ai-str", "Str"),
        ("[STR]", "ai-type ai-str", "Str"),
        ("[Tac]", "ai-type ai-tac", "Tac"),
        ("[tac]", "ai-type ai-tac", "Tac"),
        ("[TAC]", "ai-type ai-tac", "Tac"),
    ]:
        html = html.replace(marker, f'<span class="{cls}">{label}</span>')
    return html


def apply_overdue(html: str) -> str:
    """Highlight OVERDUE items."""
    html = re.sub(
        r"(OVERDUE[^<]*)",
        r'<span class="overdue">\1</span>',
        html,
    )
    return html


def wrap_appendix(html: str) -> str:
    """Wrap the Appendix section in a collapsible details element."""
    html = re.sub(
        r'(<h2[^>]*id="[^"]*appendix[^"]*"[^>]*>)(.*?)(</h2>)',
        r'<details><summary>\2</summary>',
        html,
        flags=re.IGNORECASE,
    )
    return html


def add_back_to_top(html: str) -> str:
    """Insert a 'back to top' link before each <h2> (except the first) and at the end."""
    parts = re.split(r"(<h2[^>]*>)", html)
    result = []
    h2_count = 0
    for part in parts:
        if re.match(r"<h2[^>]*>", part):
            h2_count += 1
            if h2_count > 1:
                result.append('<a href="#toc" class="back-to-top">↑ Back to top</a>\n')
        result.append(part)
    # Add one at the very end
    result.append('<a href="#toc" class="back-to-top">↑ Back to top</a>\n')
    return "".join(result)


def apply_warning_boxes(html: str) -> str:
    """Style blockquotes containing ⚠️ as warning boxes."""
    html = re.sub(
        r"<blockquote>\s*<p>⚠️",
        '<div class="warning-box"><p>⚠️',
        html,
    )
    html = re.sub(
        r"(⚠️.*?)</p>\s*</blockquote>",
        r"\1</p></div>",
        html,
        flags=re.DOTALL,
    )
    return html


def render(md_path: Path, out_path: Path) -> None:
    """Convert markdown to styled HTML."""
    md_text = md_path.read_text(encoding="utf-8")
    title = extract_title(md_text)

    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        "markdown.extensions.sane_lists",
    ]
    body = markdown.markdown(md_text, extensions=extensions)

    body = add_ids_to_headings(body)
    toc = build_toc(body)

    body = apply_priority_sections(body)
    body = apply_why_tags(body)
    body = apply_status_badges(body)
    body = apply_item_markers(body)
    body = apply_overdue(body)
    body = apply_task_type_badges(body)
    body = apply_citations(body)
    body = wrap_appendix(body)
    body = apply_warning_boxes(body)
    body = add_back_to_top(body)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{CSS}
</style>
</head>
<body>
{toc}
<div class="content">
{body}
</div>
</body>
</html>
"""

    out_path.write_text(html, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"🌐 {out_path} ({size_kb:.1f}K)")


def main():
    parser = argparse.ArgumentParser(description="Render weekly report .md → styled .html")
    parser.add_argument("--input", required=True, help="Path to the .md source file")
    parser.add_argument("--output", help="Output .html path (default: same name, .html extension)")
    args = parser.parse_args()

    md_path = Path(args.input)
    if not md_path.exists():
        print(f"ERROR: {md_path} not found")
        raise SystemExit(1)

    out_path = Path(args.output) if args.output else md_path.with_suffix(".html")
    render(md_path, out_path)


if __name__ == "__main__":
    main()
