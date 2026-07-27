#!/usr/bin/env python3
"""
Look up opening hours for attractions in an itinerary and add 🕐 lines.

Usage:
    python3 src/tour-planner/lookup_hours.py \
        --md output/trip-itinerary-latest.md \
        --output output/trip-itinerary-latest.md

This script reads the .md, identifies attractions without 🕐 lines,
and adds placeholder hours that should be verified against official sites.

For production use, this would integrate with WebFetch to pull live hours.
Currently generates placeholders based on known Vienna/Prague hours.
"""

import argparse
import re
from pathlib import Path

# Known hours database (extend as needed)
KNOWN_HOURS = {
    "St. Stephen's Cathedral": {
        "hours": "6:00 AM – 10:00 PM (cathedral); North Tower elevator 9:00 AM – 5:30 PM",
        "closed": None,
    },
    "Naturhistorisches Museum": {
        "hours": "9:00 AM – 6:00 PM (Wed until 8:00 PM)",
        "closed": "Tuesday",
    },
    "Hofburg Imperial Apartments": {
        "hours": "9:00 AM – 5:30 PM",
        "closed": None,
    },
    "Schönbrunn Palace": {
        "hours": "8:30 AM – 6:00 PM (last admission 5:15 PM)",
        "closed": None,
    },
    "Upper Belvedere": {
        "hours": "9:00 AM – 7:00 PM (summer extended through Aug 31)",
        "closed": None,
    },
    "Wiener Riesenrad": {
        "hours": "9:00 AM – 11:45 PM (summer)",
        "closed": None,
    },
    "Prague Castle": {
        "hours": "Grounds 6:00 AM – 10:00 PM; Historic buildings 9:00 AM – 5:00 PM",
        "closed": None,
    },
    "Petřín Tower": {
        "hours": "10:00 AM – 10:00 PM (summer Apr-Sep)",
        "closed": None,
    },
    "Naschmarkt": {
        "hours": "Mon-Fri 6:00 AM – 9:00 PM, Sat 6:00 AM – 6:00 PM",
        "closed": "Sunday",
    },
    "Café Savoy": {
        "hours": "Mon-Fri 8:00 AM – 10:00 PM, Sat-Sun 9:00 AM – 10:00 PM",
        "closed": None,
    },
    "Schweizerhaus": {
        "hours": "11:00 AM – 11:00 PM (kitchen closes 10:15 PM)",
        "closed": None,
    },
}


def add_hours_to_md(md_path: Path, output_path: Path):
    """Add 🕐 hours lines to activities that don't have them."""
    lines = md_path.read_text().splitlines()
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is an activity line (starts with "- **TIME:")
        if re.match(r'^- \*\*\d+', line.strip()):
            # Check if next line already has hours
            has_hours = False
            j = i + 1
            while j < len(lines) and lines[j].startswith('  '):
                if '🕐' in lines[j]:
                    has_hours = True
                    break
                j += 1

            if not has_hours:
                # Try to match an attraction name
                for name, info in KNOWN_HOURS.items():
                    if name.lower() in line.lower():
                        hours_line = f'  - 🕐 **Hours:** {info["hours"]}'
                        # Insert after current line but before sub-bullets
                        new_lines.append(hours_line)
                        break

        i += 1

    output_path.write_text('\n'.join(new_lines))
    print(f"Hours lookup complete. Written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Add opening hours to itinerary")
    parser.add_argument("--md", required=True, help="Input .md file")
    parser.add_argument("--output", required=True, help="Output .md file (can be same as input)")
    args = parser.parse_args()

    add_hours_to_md(Path(args.md), Path(args.output))


if __name__ == "__main__":
    main()
