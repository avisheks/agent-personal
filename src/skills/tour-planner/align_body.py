#!/usr/bin/env python3
"""
Align the detailed body of a .docx itinerary with the content from a .md file.
Replaces day-by-day body paragraphs while preserving the docx style patterns.

Usage:
    python3 src/tour-planner/align_body.py \
        --docx output/trip-itinerary-v2.docx \
        --md output/trip-itinerary-latest.md \
        --output output/trip-itinerary-latest.docx
"""

import argparse
import re
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ACTIVITY_EMOJIS = {
    'landmark': '🏛️', 'museum': '🎨', 'park': '🌳', 'walk': '🚶',
    'lunch': '🍽️', 'dinner': '🍽️', 'cafe': '☕', 'activity': '🎡',
    'shopping': '🛍️', 'hotel': '🏨', 'transit': '🚇', 'flight': '✈️',
}


def parse_day_sections_from_md(md_path: Path) -> dict:
    """Parse the .md file and extract each day's detailed body content.
    Returns dict: day_number -> list of (text, style_hint) tuples."""

    lines = md_path.read_text().splitlines()
    days = {}
    current_day = None
    current_lines = []

    for line in lines:
        # Match day headings like "## Day 2: The Heart of Old Vienna..."
        day_match = re.match(r'^## Day (\d+):', line)
        if day_match:
            if current_day is not None:
                days[current_day] = current_lines
            current_day = int(day_match.group(1))
            current_lines = [line]
            continue

        # End of days section (hit next major section)
        if current_day and line.startswith('## ') and 'Day' not in line:
            days[current_day] = current_lines
            current_day = None
            continue

        if current_day is not None:
            current_lines.append(line)

    if current_day is not None:
        days[current_day] = current_lines

    return days


def classify_line(line: str) -> str:
    """Classify a markdown line into a docx style."""
    stripped = line.strip()

    if not stripped:
        return 'blank'
    if stripped.startswith('## Day'):
        return 'heading3'
    if stripped.startswith('**Weather:**') or stripped.startswith('☀️') or stripped.startswith('⛅') or stripped.startswith('🌧️') or stripped.startswith('🌤️'):
        return 'first_paragraph'
    if stripped.startswith('📍'):
        return 'body_text'
    if stripped.startswith('---'):
        return 'separator'

    # Check for indented sub-bullets BEFORE top-level bullets
    # (indented lines start with spaces in the raw line, not stripped)
    if line.startswith('  ') and stripped.startswith('-'):
        return 'compact'

    # Top-level activity bullets
    if re.match(r'^- \*\*\d+', stripped):
        return 'normal_activity'
    if stripped.startswith('- **'):
        return 'normal_activity'
    if stripped.startswith('- '):
        return 'normal_activity'

    return 'normal'


def create_paragraph(text: str, style: str) -> OxmlElement:
    """Create an OxmlElement paragraph with appropriate formatting."""
    new_p = OxmlElement('w:p')

    if style == 'heading3':
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'Heading3')
        pPr.append(pStyle)
        new_p.append(pPr)
        # Strip markdown ## prefix
        clean_text = text.lstrip('#').strip()
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = clean_text
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    elif style == 'first_paragraph':
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'FirstParagraph')
        pPr.append(pStyle)
        new_p.append(pPr)
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = text.strip()
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    elif style == 'body_text':
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'BodyText')
        pPr.append(pStyle)
        new_p.append(pPr)
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = text.strip()
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    elif style == 'compact':
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'Compact')
        pPr.append(pStyle)
        new_p.append(pPr)
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        # Strip leading "  - " from sub-bullets
        clean = re.sub(r'^\s*-\s*', '', text)
        t.text = clean
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    elif style == 'normal_activity':
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        # Strip leading "- " from markdown bullets
        clean = re.sub(r'^-\s*', '', text.strip())
        # Strip markdown bold markers
        clean = clean.replace('**', '')
        t.text = clean
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    elif style == 'blank':
        pass

    else:  # 'normal'
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = text.strip()
        t.set(qn('xml:space'), 'preserve')
        run.append(t)
        new_p.append(run)

    return new_p


def find_day_boundaries(doc: Document) -> dict:
    """Find paragraph index boundaries for each day section in the docx.
    Returns dict: day_number -> (start_idx, end_idx)."""

    boundaries = {}
    day_starts = []

    for i, para in enumerate(doc.paragraphs):
        day_match = re.match(r'Day (\d+):', para.text)
        if day_match and 'Heading' in para.style.name:
            day_starts.append((int(day_match.group(1)), i))

    # Find end-of-days (first non-day heading after all days)
    last_day_end = len(doc.paragraphs)
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip().startswith('🍽️ Restaurant Summary') or \
           para.text.strip().startswith('🏛️ Attraction Summary') or \
           para.text.strip().startswith('🎒 Packing'):
            last_day_end = i
            break

    for idx, (day_num, start) in enumerate(day_starts):
        if idx + 1 < len(day_starts):
            end = day_starts[idx + 1][1]
        else:
            end = last_day_end
        boundaries[day_num] = (start, end)

    return boundaries


def align_body(docx_path: Path, md_path: Path, output_path: Path):
    """Replace day body sections in the docx with aligned content from .md."""

    doc = Document(str(docx_path))
    md_days = parse_day_sections_from_md(md_path)
    boundaries = find_day_boundaries(doc)

    body = doc.element.body

    # Process days in reverse order (so index shifts don't affect earlier days)
    for day_num in sorted(boundaries.keys(), reverse=True):
        if day_num not in md_days:
            continue

        start_idx, end_idx = boundaries[day_num]
        md_lines = md_days[day_num]

        # Get the element AFTER this day section (insertion anchor)
        if end_idx < len(doc.paragraphs):
            anchor = doc.paragraphs[end_idx]._element
        else:
            anchor = None

        # Remove old paragraphs for this day
        for i in range(end_idx - 1, start_idx - 1, -1):
            elem = doc.paragraphs[i]._element
            body.remove(elem)

        # Insert new paragraphs from .md content in forward order
        new_elements = []
        for line in md_lines:
            style = classify_line(line)
            if style == 'separator':
                continue
            if style == 'blank' and not line.strip():
                continue
            new_p = create_paragraph(line, style)
            new_elements.append(new_p)

        # Insert in forward order: first element goes right before anchor,
        # then each subsequent element goes after the previous one
        prev_elem = None
        for elem in new_elements:
            if prev_elem is None:
                if anchor is not None:
                    anchor.addprevious(elem)
                else:
                    body.append(elem)
            else:
                prev_elem.addnext(elem)
            prev_elem = elem

    doc.save(str(output_path))
    print(f"Body aligned. {len(md_days)} days processed. Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Align docx body with .md content")
    parser.add_argument("--docx", required=True, help="Base .docx file")
    parser.add_argument("--md", required=True, help="Aligned .md source file")
    parser.add_argument("--output", required=True, help="Output .docx path")
    args = parser.parse_args()

    align_body(Path(args.docx), Path(args.md), Path(args.output))


if __name__ == "__main__":
    main()
