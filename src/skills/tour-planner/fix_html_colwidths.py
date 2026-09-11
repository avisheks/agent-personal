#!/usr/bin/env python3
"""Post-process pandoc HTML to apply col-widths from <!-- col-widths: --> comments.

Pandoc generates equal-width <colgroup> elements by default.
This script finds each <!-- col-widths: X,Y,Z --> comment in the HTML and
replaces the immediately following <colgroup>...</colgroup> block with
correctly-sized <col> elements matching the specified percentages.

Usage:
    python3 fix_html_colwidths.py --input FILE.html --output FILE.html
"""

import argparse
import re


def fix_colwidths(html: str) -> str:
    pattern = re.compile(
        r'(<!--\s*col-widths:\s*([\d,\s]+)\s*-->)'
        r'(.*?)'
        r'(<colgroup>)(.*?)(</colgroup>)',
        re.DOTALL
    )

    def replacer(m):
        comment = m.group(1)
        widths_str = m.group(2)
        between = m.group(3)
        widths = [w.strip() for w in widths_str.split(',')]
        cols = ''.join(f'<col style="width:{w}%" />' for w in widths)
        return f'{comment}{between}<colgroup>\n{cols}\n</colgroup>'

    return pattern.sub(replacer, html)


def main():
    parser = argparse.ArgumentParser(description='Fix HTML table column widths from col-widths comments')
    parser.add_argument('--input', required=True, help='Input HTML file')
    parser.add_argument('--output', required=True, help='Output HTML file')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        html = f.read()

    fixed = fix_colwidths(html)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(fixed)

    comment_count = len(re.findall(r'<!-- col-widths:', html))
    print(f'Processed {comment_count} col-widths directives.')


if __name__ == '__main__':
    main()