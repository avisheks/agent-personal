"""Render a news-summarizer markdown report into the canonical HTML template.

Usage:
    python3 src/news-report/render_html.py --input .local/data/news-rl-in-ai/rl-in-ai-2026-07-WK30-news.md

Parses the structured markdown and injects content into the fixed HTML
template (CSS, JS, layout) without regenerating the template each time.
"""

import argparse
import re
import html as html_mod
from pathlib import Path


SCORE_THRESHOLDS = {"high": 8, "mid": 5}

# Fixed section IDs and TOC labels per SOP. Keys are lowercase normalized title fragments.
SECTION_REGISTRY = [
    {"match": "executive briefing", "id": "executive-briefing", "toc": "📋 Executive Briefing"},
    {"match": "what changed", "id": "what-changed", "toc": "⚡ What Changed"},
    {"match": "top technical", "id": "top-technical", "toc": "🔬 Top Technical"},
    {"match": "frontier lab", "id": "lab-scorecards", "toc": "🏢 Lab Scorecards"},
    {"match": "open-source", "id": "open-source", "toc": "🌐 Open-Source"},
    {"match": "business", "id": "business", "toc": "💰 Business & Market"},
    {"match": "research papers", "id": "research", "toc": "📄 Research Papers"},
    {"match": "research blogs", "id": "research-blogs", "toc": "🧬 Research Blogs"},
    {"match": "engineering blogs", "id": "blogs", "toc": "🛠️ Engineering Blogs"},
    {"match": "github", "id": "github", "toc": "📦 GitHub Projects"},
    {"match": "videos", "id": "media", "toc": "🎙️ Videos & Podcasts"},
    {"match": "community", "id": "community", "toc": "💬 Community"},
    {"match": "emerging themes", "id": "themes", "toc": "📈 Emerging Themes"},
    {"match": "trend tracking", "id": "trends", "toc": "📊 Trend Tracking"},
    {"match": "implications", "id": "implications-1", "toc": "🏗️ Implications 1", "is_implications_1": True},
    {"match": "implications", "id": "implications-2", "toc": "🔍 Implications 2", "is_implications_2": True},
    {"match": "watch list", "id": "watchlist", "toc": "👀 Watch List"},
    {"match": "contrarian", "id": "contrarian", "toc": "🔮 Contrarian View"},
    {"match": "strategic analysis", "id": "strategy", "toc": "🧭 Strategic Analysis"},
    {"match": "personalized", "id": "relevance", "toc": "🎯 Personalized"},
    {"match": "recommendations", "id": "recommendations", "toc": "✅ Recommendations"},
    {"match": "executive takeaways", "id": "takeaways", "toc": "🏆 Takeaways"},
    {"match": "what leaders", "id": "next-week", "toc": "📌 Next Week"},
]


CANONICAL_ORDER = [e["id"] for e in SECTION_REGISTRY if not e.get("is_implications_2")]
# Expand: implications-1 is followed by implications-2
_expanded = []
for sid in CANONICAL_ORDER:
    _expanded.append(sid)
    if sid == "implications-1":
        _expanded.append("implications-2")
CANONICAL_ORDER = _expanded


def resolve_section_id_and_toc(title: str, implications_count: list) -> tuple[str, str]:
    """Match a section title to its fixed ID and TOC label."""
    title_lower = title.lower()
    for entry in SECTION_REGISTRY:
        if entry["match"] in title_lower:
            if entry.get("is_implications_1") and implications_count[0] == 0:
                implications_count[0] += 1
                clean_title = re.sub(r'^[\U0001F300-\U0001FAFF☀-➿︀-️‍]+\s*', '', title).strip()
                short = clean_title[:15].strip()
                return entry["id"], f"🏗️ {short}"
            elif entry.get("is_implications_2") and implications_count[0] > 0:
                clean_title = re.sub(r'^[\U0001F300-\U0001FAFF☀-➿︀-️‍]+\s*', '', title).strip()
                short = clean_title[:15].strip()
                return entry["id"], f"🔍 {short}"
            elif entry.get("is_implications_1") or entry.get("is_implications_2"):
                continue
            return entry["id"], entry["toc"]
    # Fallback: auto-generate
    slug = re.sub(r'[^a-z0-9]+', '-', title_lower).strip('-')
    return slug, title


def sort_sections_canonical(sections: list[dict]) -> list[dict]:
    """Reorder sections to match CANONICAL_ORDER."""
    id_to_section = {s["slug"]: s for s in sections}
    ordered = []
    for sid in CANONICAL_ORDER:
        if sid in id_to_section:
            ordered.append(id_to_section.pop(sid))
    # Append any unrecognized sections at the end
    for s in sections:
        if s["slug"] in id_to_section:
            ordered.append(s)
            del id_to_section[s["slug"]]
    return ordered


def score_class(val: int) -> str:
    if val >= SCORE_THRESHOLDS["high"]:
        return "score-high"
    if val >= SCORE_THRESHOLDS["mid"]:
        return "score-mid"
    return "score-low"


def md_links_to_html(text: str) -> str:
    """Convert markdown [text](url) to <a href="url">text</a>."""
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)


def escape(text: str) -> str:
    """HTML-escape then convert markdown links."""
    text = html_mod.escape(text, quote=False)
    text = md_links_to_html(text)
    text = text.replace("&amp;mdash;", "&mdash;").replace("&amp;ndash;", "&ndash;")
    text = text.replace("&amp;times;", "&times;").replace("&amp;rarr;", "&rarr;")
    text = text.replace("&amp;alpha;", "&alpha;").replace("&amp;sup2;", "&sup2;")
    text = text.replace("&amp;ldquo;", "&ldquo;").replace("&amp;rdquo;", "&rdquo;")
    text = text.replace("&amp;rsquo;", "&rsquo;")
    return text


def parse_sections(md_text: str) -> list[dict]:
    """Parse markdown into sections by ## headers, using fixed IDs from SECTION_REGISTRY."""
    sections = []
    current = None
    implications_count = [0]  # mutable counter for implications tracking

    for line in md_text.split("\n"):
        if line.startswith("## "):
            if current:
                sections.append(current)
            title = line[3:].strip()
            emoji_match = re.match(r'^([\U0001F300-\U0001FAFF☀-➿✀-➿]+)\s*(.+)', title)
            if emoji_match:
                emoji = emoji_match.group(1)
                title_text = emoji_match.group(2)
            else:
                emoji = ""
                title_text = title
            fixed_id, toc_label = resolve_section_id_and_toc(title_text, implications_count)
            current = {"title": title_text, "emoji": emoji, "slug": fixed_id, "toc_label": toc_label, "lines": []}
        elif current is not None:
            current["lines"].append(line)
    if current:
        sections.append(current)
    return sections


def render_section_content(lines: list[str]) -> str:
    """Convert markdown content lines to HTML."""
    html_parts = []
    in_table = False
    in_list = False
    list_type = None
    in_blockquote = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
            if in_blockquote:
                html_parts.append("</div>")
                in_blockquote = False
            i += 1
            continue

        # Blockquote / callout
        if line.startswith("> "):
            content = line[2:]
            if "💡" in content or "Key Insight" in content:
                cls = "callout callout-insight"
            elif "⚠️" in content or "Risk" in content:
                cls = "callout callout-risk"
            elif "🚀" in content or "Opportunity" in content:
                cls = "callout callout-opportunity"
            else:
                cls = "callout callout-insight"
            if not in_blockquote:
                html_parts.append(f'<div class="{cls}">')
                in_blockquote = True
            html_parts.append(f"<p>{md_links_to_html(content)}</p>")
            i += 1
            continue

        if in_blockquote and not line.startswith(">"):
            html_parts.append("</div>")
            in_blockquote = False

        # Table
        if line.startswith("|"):
            if not in_table:
                html_parts.append("<table>")
                in_table = True
                # Header row
                cells = [c.strip() for c in line.split("|")[1:-1]]
                html_parts.append("<thead><tr>" + "".join(f"<th>{md_links_to_html(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                i += 1
                # Skip separator row
                if i < len(lines) and lines[i].startswith("|") and "---" in lines[i]:
                    i += 1
            else:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                html_parts.append("<tr>" + "".join(f"<td>{md_links_to_html(c)}</td>" for c in cells) + "</tr>")
                i += 1
            continue
        elif in_table:
            html_parts.append("</tbody></table>")
            in_table = False

        # Headers
        if line.startswith("### "):
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
            html_parts.append(f"<h3>{md_links_to_html(line[4:])}</h3>")
            i += 1
            continue
        if line.startswith("#### "):
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
            html_parts.append(f"<h4>{md_links_to_html(line[5:])}</h4>")
            i += 1
            continue

        # Unordered list
        if line.startswith("- ") or line.startswith("* "):
            if not in_list or list_type != "ul":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            content = line[2:]
            html_parts.append(f"<li>{md_links_to_html(content)}</li>")
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if ol_match:
            if not in_list or list_type != "ol":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            content = ol_match.group(2)
            html_parts.append(f"<li>{md_links_to_html(content)}</li>")
            i += 1
            continue

        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False

        # Horizontal rule
        if line.strip() == "---":
            html_parts.append('<hr class="section-divider">')
            i += 1
            continue

        # Paragraph
        html_parts.append(f"<p>{md_links_to_html(line)}</p>")
        i += 1

    if in_table:
        html_parts.append("</tbody></table>")
    if in_list:
        html_parts.append(f"</{list_type}>")
    if in_blockquote:
        html_parts.append("</div>")

    return "\n".join(html_parts)


def extract_metadata(md_text: str, display_name: str | None = None) -> dict:
    """Extract title, subtitle, reading time from the markdown header."""
    lines = md_text.split("\n")
    title = "Intelligence Report"
    subtitle = ""
    reading_time = "15 min"
    is_first_report = False
    week_number = ""

    for line in lines[:20]:
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
        if "Week" in line and "|" in line:
            parts = line.split("|")
            subtitle = parts[0].replace("**", "").strip()
            # Extract week number
            wk_match = re.search(r'Week\s*(\d+)', line)
            if wk_match:
                week_number = wk_match.group(1)
        if "Reading time:" in line.lower() or "min read" in line.lower():
            m = re.search(r'(\d+)\s*min', line)
            if m:
                reading_time = f"{m.group(1)} min"
        if "First report" in line or "baseline established" in line:
            is_first_report = True

    # Try to extract from subtitle line
    for line in lines[:10]:
        if line.startswith("**Week"):
            subtitle = line.replace("**", "").strip()
            wk_match = re.search(r'Week\s*(\d+)', line)
            if wk_match:
                week_number = wk_match.group(1)

    # Build display title: use display_name override if given, otherwise keep title from # line
    if display_name and week_number:
        title = f"{display_name} (Week {week_number})"

    return {
        "title": title,
        "subtitle": subtitle,
        "reading_time": reading_time,
        "is_first_report": is_first_report,
    }


CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
.progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, #2563eb, #7c3aed); z-index: 1000; transition: width 0.1s; }
body { font-family: 'Georgia', 'Times New Roman', serif; line-height: 1.7; color: #1a1a2e; background: #fafafa; padding: 2rem 1.5rem; margin: 0; }
.layout { display: flex; max-width: 1200px; margin: 0 auto; gap: 2rem; }
.toc { position: sticky; top: 1rem; width: 220px; min-width: 220px; height: fit-content; max-height: calc(100vh - 2rem); overflow-y: auto; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.75rem; padding: 1rem; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; scrollbar-width: thin; }
.toc h4 { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-bottom: 0.75rem; }
.toc a { display: block; padding: 0.3rem 0.5rem; color: #475569; text-decoration: none; border-radius: 4px; margin-bottom: 2px; transition: all 0.2s; }
.toc a:hover, .toc a.active { background: #eff6ff; color: #2563eb; }
.main-content { flex: 1; max-width: 900px; min-width: 0; }
h1 { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 2rem; font-weight: 700; color: #0f0f23; margin-bottom: 0.25rem; letter-spacing: -0.5px; }
.header-meta { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.subtitle { font-style: italic; color: #555; font-size: 0.95rem; }
.reading-time { display: inline-block; background: #eff6ff; color: #2563eb; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 12px; }
h2 { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 1.4rem; font-weight: 600; color: #16213e; margin-top: 2.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e8e8f0; }
h3 { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 1.1rem; font-weight: 600; color: #1a1a2e; margin-top: 1.5rem; margin-bottom: 0.5rem; }
h4 { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 1rem; font-weight: 600; color: #333; margin-top: 1rem; margin-bottom: 0.4rem; }
p { margin-bottom: 1rem; }
a { color: #2563eb; text-decoration: none; }
a:hover { text-decoration: underline; }
.baseline-note { background: #f0f4ff; border-left: 4px solid #2563eb; padding: 0.75rem 1rem; margin-bottom: 2rem; font-size: 0.9rem; color: #1e40af; }
.executive-briefing { background: #f8f9fc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; }
.executive-briefing p { margin-bottom: 0.75rem; }
.executive-briefing strong { color: #0f0f23; }
.hero-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0 2rem; }
.hero-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; text-align: center; transition: box-shadow 0.2s; }
.hero-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.hero-card .hero-emoji { font-size: 2rem; margin-bottom: 0.5rem; }
.hero-card .hero-title { font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; font-size: 0.9rem; color: #1a1a2e; margin-bottom: 0.4rem; }
.hero-card .hero-link { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.75rem; }
.callout { border-radius: 8px; padding: 0.9rem 1.1rem; margin: 1rem 0; font-size: 0.92rem; }
.callout-insight { background: #eff6ff; border-left: 4px solid #2563eb; }
.callout-risk { background: #fef2f2; border-left: 4px solid #dc2626; }
.callout-opportunity { background: #f0fdf4; border-left: 4px solid #16a34a; }
.callout-number { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; text-align: center; margin: 1rem 0; }
.callout-number .big-number { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 2.2rem; font-weight: 700; color: #0f0f23; }
.callout-number .number-label { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.8rem; color: #64748b; margin-top: 0.25rem; }
.key-numbers-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin: 1.25rem 0; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0 1.5rem; font-size: 0.88rem; font-family: 'Helvetica Neue', Arial, sans-serif; }
th { background: #f1f5f9; padding: 0.6rem 0.75rem; text-align: left; font-weight: 600; color: #334155; border-bottom: 2px solid #cbd5e1; }
td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
tr:hover td { background: #eff6ff; }
ul, ol { margin: 0.75rem 0 1rem 1.5rem; }
li { margin-bottom: 0.4rem; }
.score-pill { display: inline-block; border-radius: 4px; padding: 0.2rem 0.5rem; font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.8rem; font-weight: 600; margin-right: 0.4rem; margin-bottom: 0.25rem; }
.score-high { background: #dcfce7; color: #166534; }
.score-mid { background: #fef9c3; color: #854d0e; }
.score-low { background: #fee2e2; color: #991b1b; }
.dev-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.25rem; }
.dev-card h3 { margin-top: 0; color: #0f0f23; }
.signal { display: inline-block; font-size: 0.8rem; padding: 0.15rem 0.5rem; border-radius: 12px; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 500; }
.signal-research { background: #ede9fe; color: #6d28d9; }
.signal-prototype { background: #fef3c7; color: #92400e; }
.signal-production { background: #d1fae5; color: #065f46; }
.section-divider { border: none; border-top: 1px solid #e8e8f0; margin: 2.5rem 0; }
.action-list { background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 1.25rem; margin: 1rem 0; }
.action-list li { font-size: 0.95rem; }
.contrarian { background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 1.25rem; margin: 1rem 0; }
.watch-list-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1.25rem; margin: 1rem 0; }
details { margin: 1rem 0; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
details summary { padding: 0.75rem 1rem; background: #f8fafc; cursor: pointer; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; font-size: 0.95rem; color: #334155; }
details summary:hover { background: #f1f5f9; }
details[open] summary { border-bottom: 1px solid #e2e8f0; }
details .details-content { padding: 1rem; }
.back-to-top { position: fixed; bottom: 2rem; right: 2rem; width: 40px; height: 40px; border-radius: 50%; background: #2563eb; color: #fff; border: none; font-size: 1.2rem; cursor: pointer; display: none; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(37,99,235,0.3); z-index: 999; }
.back-to-top.visible { display: flex; }
.meta { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 0.8rem; color: #64748b; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
@media (max-width: 768px) { .layout { flex-direction: column; } .toc { display: none; } .hero-grid { grid-template-columns: 1fr; } body { padding: 1rem; } h1 { font-size: 1.5rem; } h2 { font-size: 1.2rem; } table { font-size: 0.8rem; } .key-numbers-grid { grid-template-columns: repeat(2, 1fr); } }"""

JS = """window.addEventListener('scroll', () => {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    document.getElementById('progressBar').style.width = scrolled + '%';
    const btn = document.getElementById('backToTop');
    btn.classList.toggle('visible', winScroll > 400);
});
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            document.querySelectorAll('.toc a').forEach(a => a.classList.remove('active'));
            const id = entry.target.id;
            const link = document.querySelector(`.toc a[href="#${id}"]`);
            if (link) link.classList.add('active');
        }
    });
}, { rootMargin: '-20% 0px -70% 0px' });
document.querySelectorAll('h2[id]').forEach(h2 => observer.observe(h2));"""


COLLAPSIBLE_SECTIONS = {"research-blogs", "engineering-blogs", "eng-blogs", "github-projects", "github", "videos-podcasts", "media"}
SPECIAL_WRAPPERS = {
    "contrarian-view": "contrarian",
    "contrarian": "contrarian",
    "watch-list": "watch-list-box",
    "watchlist": "watch-list-box",
}


def build_html(md_text: str, display_name: str | None = None) -> str:
    meta = extract_metadata(md_text, display_name=display_name)
    sections = parse_sections(md_text)
    sections = sort_sections_canonical(sections)

    # Build TOC using fixed labels
    toc_links = []
    for s in sections:
        label = s.get("toc_label", f"{s['emoji']} {s['title']}" if s['emoji'] else s['title'])
        toc_links.append(f'    <a href="#{s["slug"]}">{label}</a>')

    toc_html = "\n".join(toc_links)

    # Build section content
    sections_html = []
    for s in sections:
        section_id = s["slug"]
        header = f'{s["emoji"]} {s["title"]}' if s["emoji"] else s["title"]
        content = render_section_content(s["lines"])

        # Check for special wrappers
        wrapper_class = SPECIAL_WRAPPERS.get(section_id)
        is_collapsible = section_id in COLLAPSIBLE_SECTIONS

        if is_collapsible:
            sections_html.append(f'<h2 id="{section_id}">{header}</h2>')
            sections_html.append(f'<details><summary>{s["title"]}</summary><div class="details-content">{content}</div></details>')
        elif wrapper_class:
            sections_html.append(f'<h2 id="{section_id}">{header}</h2>')
            sections_html.append(f'<div class="{wrapper_class}">{content}</div>')
        else:
            sections_html.append(f'<h2 id="{section_id}">{header}</h2>')
            sections_html.append(content)

        sections_html.append('<hr class="section-divider">')

    body_content = "\n".join(sections_html)

    # Baseline note
    baseline = ""
    if meta["is_first_report"]:
        baseline = '<div class="baseline-note"><strong>First report &mdash; baseline established.</strong> All trend tracking, Watch List, and prediction scoring begin from this issue.</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_mod.escape(meta['title'])}</title>
    <style>{CSS}</style>
</head>
<body>
<div class="progress-bar" id="progressBar"></div>
<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>
<div class="layout">
<nav class="toc" id="toc">
    <h4>Contents</h4>
{toc_html}
</nav>
<main class="main-content">
<h1>{html_mod.escape(meta['title'])}</h1>
<div class="header-meta"><span class="subtitle">{meta['subtitle']}</span><span class="reading-time">⏱️ {meta['reading_time']} read</span></div>
{baseline}
{body_content}
<div class="meta"><p>Generated by render_html.py from markdown source.</p></div>
</main>
</div>
<script>{JS}</script>
</body>
</html>"""

    return html


TOPIC_DISPLAY_NAMES = {
    "rl-in-ai": "RL in AI Weekly Briefing",
    "agentic-ai": "Agentic AI Weekly Briefing",
}


def detect_display_name(input_path: Path) -> str | None:
    """Auto-detect display name from file path by matching topic slugs."""
    path_str = str(input_path)
    for slug, name in TOPIC_DISPLAY_NAMES.items():
        if slug in path_str:
            return name
    return None


def main():
    parser = argparse.ArgumentParser(description="Render news report markdown to HTML")
    parser.add_argument("--input", required=True, help="Path to markdown report file")
    parser.add_argument("--output", default=None, help="Output HTML path (default: same name with .html)")
    parser.add_argument("--display-name", default=None, help="Display name for h1/title (auto-detected from path if omitted)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        return

    output_path = Path(args.output) if args.output else input_path.with_suffix(".html")
    display_name = args.display_name or detect_display_name(input_path)

    md_text = input_path.read_text()
    html = build_html(md_text, display_name=display_name)
    output_path.write_text(html)

    print(f"HTML rendered: {output_path} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
