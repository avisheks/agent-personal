#!/usr/bin/env python3
"""
Apply v3 compact formatting to a .docx file.

Reduces page count while maintaining readability — adjusts margins,
font sizes, line spacing, paragraph spacing, table formatting, and
blockquote styling.
"""

import argparse
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Twips
from docx.oxml.ns import qn
from docx.enum.text import WD_LINE_SPACING
import copy


def compact(input_path: Path, output_path: Path):
    doc = Document(str(input_path))

    # --- Page margins: 0.7" all sides ---
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # --- Detect which paragraphs are in the "detailed itinerary" (Day sections) ---
    in_day_section = False
    day_paras = set()
    for i, p in enumerate(doc.paragraphs):
        if 'Heading' in p.style.name and 'Day' in p.text and ':' in p.text:
            in_day_section = True
        elif 'Heading' in p.style.name and 'Day' not in p.text:
            in_day_section = False
        if in_day_section and 'Heading' not in p.style.name:
            day_paras.add(i)

    # --- Process paragraphs ---
    for i, p in enumerate(doc.paragraphs):
        style_name = p.style.name

        if style_name == 'Heading 2':
            for run in p.runs:
                run.font.size = Pt(17)
                run.bold = True
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.space_before = Pt(18)

        elif style_name == 'Heading 3':
            for run in p.runs:
                run.font.size = Pt(13)
                run.bold = True
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.space_before = Pt(18)

        elif style_name == 'Block Text':
            for run in p.runs:
                run.font.size = Pt(9.5)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = Pt(12.5)

        elif style_name == 'Compact':
            for run in p.runs:
                run.font.size = Pt(10)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

        elif i in day_paras:
            # Detailed itinerary body: 10.5pt, 1.35 line spacing, 6pt after
            for run in p.runs:
                if run.font.size is None or run.font.size > Pt(11):
                    run.font.size = Pt(10.5)
            p.paragraph_format.space_after = Pt(6)
            # 1.35 line spacing (expressed as proportion)
            p.paragraph_format.line_spacing = 1.35

        else:
            # Other body text: 10.5pt, tighter spacing
            for run in p.runs:
                if run.font.size is None or run.font.size > Pt(11):
                    run.font.size = Pt(10.5)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25

    # --- Tables: 9.5pt, comfortable padding ---
    for table in doc.tables:
        tbl = table._tbl
        tblPr = tbl.tblPr
        if tblPr is None:
            tblPr = tbl._new_tblPr()
        cellMar = tblPr.find(qn('w:tblCellMar'))
        if cellMar is None:
            cellMar = tblPr.makeelement(qn('w:tblCellMar'), {})
            tblPr.append(cellMar)
        for side in ['top', 'bottom', 'left', 'right']:
            el = cellMar.find(qn(f'w:{side}'))
            if el is None:
                el = cellMar.makeelement(qn(f'w:{side}'), {})
                cellMar.append(el)
            if side in ('top', 'bottom'):
                el.set(qn('w:w'), '40')  # ~4px
            else:
                el.set(qn('w:w'), '80')  # ~8px
            el.set(qn('w:type'), 'dxa')

        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # --- Adaptive column widths ---
    # Identify tables by header content and set narrow first column
    page_width_twips = 12240 - 2 * 1008  # letter width minus 0.7" margins * 2 (in twips)

    col_width_rules = {
        'What to Wear': [5, 12, 20, 63],
        'Rainy Day': [10, 20, 70],
        'Packing': [4, 40, 20, 36],
        'Things to Remember': [4, 40, 15, 41],
        'Day-of Reminders': [8, 92],
    }

    for table in doc.tables:
        header_text = ' '.join(cell.text for cell in table.rows[0].cells) if table.rows else ''

        widths = None
        if 'Weather' in header_text and 'What to Wear' in header_text:
            widths = col_width_rules['What to Wear']
        elif 'Swap' in header_text and 'Alternative' in header_text:
            widths = col_width_rules['Rainy Day']
        elif '☐' in header_text and 'Item' in header_text:
            widths = col_width_rules['Packing']
        elif '☐' in header_text and 'Action' in header_text:
            widths = col_width_rules['Things to Remember']
        elif 'Key Reminder' in header_text:
            widths = col_width_rules['Day-of Reminders']
        elif header_text.strip().startswith('#') or header_text.strip().startswith('\\#'):
            # Cross-reference and booking tables with # as first col
            num_cols = len(table.rows[0].cells)
            widths = [4] + [96 // (num_cols - 1)] * (num_cols - 1)

        if widths:
            tbl_grid = table._tbl.find(qn('w:tblGrid'))
            if tbl_grid is not None:
                grid_cols = tbl_grid.findall(qn('w:gridCol'))
                for i, gc in enumerate(grid_cols):
                    if i < len(widths):
                        tw = int(page_width_twips * widths[i] / 100)
                        gc.set(qn('w:w'), str(tw))

    doc.save(str(output_path))
    print(f"Compact formatting applied: {output_path}")

    # Verification
    doc2 = Document(str(output_path))
    print(f"  Margins: {doc2.sections[0].left_margin.inches:.2f}\" all sides")
    h2_count = sum(1 for p in doc2.paragraphs if p.style.name == 'Heading 2')
    h3_count = sum(1 for p in doc2.paragraphs if p.style.name == 'Heading 3')
    body_105 = sum(1 for p in doc2.paragraphs for r in p.runs if r.font.size == Pt(10.5))
    table_95 = sum(1 for t in doc2.tables for row in t.rows for c in row.cells
                   for p in c.paragraphs for r in p.runs if r.font.size == Pt(9.5))
    print(f"  H2 headings (15pt): {h2_count}")
    print(f"  H3 headings (13pt): {h3_count}")
    print(f"  Body runs at 10.5pt: {body_105}")
    print(f"  Table runs at 9.5pt: {table_95}")


def main():
    parser = argparse.ArgumentParser(description="Apply v3 compact formatting to docx")
    parser.add_argument("--input", required=True, help="Input .docx path")
    parser.add_argument("--output", required=True, help="Output .docx path")
    args = parser.parse_args()
    compact(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
