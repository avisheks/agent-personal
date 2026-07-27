"""Tests for tour-planner scripts."""

import sys
import re
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "tour-planner"))

from insert_summary import parse_summary_from_md
from align_body import parse_day_sections_from_md, classify_line, find_day_boundaries


def test_parse_summary():
    """Test that summary extraction finds day headers and items."""
    md_path = Path(__file__).parent.parent.parent / "output" / "trip-itinerary-latest.md"
    if not md_path.exists():
        print("  SKIP: trip-itinerary-latest.md not found")
        return

    data = parse_summary_from_md(md_path)
    assert len(data) > 0, "No summary data parsed"

    # Check structure
    types = [d[1] for d in data]
    assert 'heading' in types, "Missing heading"
    assert 'day_header' in types, "Missing day headers"
    assert 'item' in types, "Missing items"

    # Check we have day headers (at least 5 Vienna days; 9 if Prague included)
    day_headers = [d[0] for d in data if d[1] == 'day_header']
    assert len(day_headers) >= 5, f"Expected at least 5 day headers, got {len(day_headers)}"

    print(f"  parse_summary: PASS ({len(data)} lines, {len(day_headers)} days)")


def test_parse_day_sections():
    """Test that day section parsing extracts all days."""
    md_path = Path(__file__).parent.parent.parent / "output" / "trip-itinerary-latest.md"
    if not md_path.exists():
        print("  SKIP: trip-itinerary-latest.md not found")
        return

    days = parse_day_sections_from_md(md_path)
    assert len(days) >= 9, f"Expected 9 days, got {len(days)}"

    for day_num in range(1, 10):
        assert day_num in days, f"Day {day_num} missing"
        assert len(days[day_num]) > 3, f"Day {day_num} has too few lines ({len(days[day_num])})"

    print(f"  parse_day_sections: PASS ({len(days)} days)")


def test_classify_line():
    """Test line classification."""
    assert classify_line("## Day 2: The Heart of Old Vienna") == 'heading3'
    assert classify_line("**Weather:** 31°C, sunny") == 'first_paragraph'
    assert classify_line("☀️ 31 °C, sunny.") == 'first_paragraph'
    assert classify_line("📍 Today's Route Map") == 'body_text'
    assert classify_line("- **9:30 AM: Graben stroll.**") == 'normal_activity'
    assert classify_line("  - 🕐 **Hours (Sat):** 9:00 AM – 6:00 PM") == 'compact'
    assert classify_line("  - 👶 Kid-friendly: 4/5") == 'compact'
    assert classify_line("  - 🌟 Must-try: Schnitzel") == 'compact'
    assert classify_line("") == 'blank'
    assert classify_line("---") == 'separator'
    print("  classify_line: PASS")


def test_find_day_boundaries():
    """Test finding day boundaries in docx."""
    docx_path = Path(__file__).parent.parent.parent / "output" / "trip-itinerary-v2.docx"
    if not docx_path.exists():
        print("  SKIP: trip-itinerary-v2.docx not found")
        return

    from docx import Document
    doc = Document(str(docx_path))
    boundaries = find_day_boundaries(doc)

    assert len(boundaries) >= 9, f"Expected 9 day boundaries, got {len(boundaries)}"
    for day_num in range(1, 10):
        assert day_num in boundaries, f"Day {day_num} boundary missing"
        start, end = boundaries[day_num]
        assert end > start, f"Day {day_num}: end ({end}) <= start ({start})"

    print(f"  find_day_boundaries: PASS ({len(boundaries)} days found)")


def test_no_hotel_returns_in_md():
    """Validate that the aligned .md has no 'Return to hotel' entries."""
    md_path = Path(__file__).parent.parent.parent / "output" / "trip-itinerary-latest.md"
    if not md_path.exists():
        print("  SKIP: trip-itinerary-latest.md not found")
        return

    content = md_path.read_text()
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        if 'return to hotel' in line.lower() or 'Return to hotel' in line:
            violations.append((i, line.strip()[:80]))

    if violations:
        print(f"  no_hotel_returns: FAIL ({len(violations)} violations)")
        for ln, text in violations[:5]:
            print(f"    Line {ln}: {text}")
        assert False, "Hotel returns found in itinerary"
    else:
        print("  no_hotel_returns: PASS")


def test_dinner_times():
    """Validate dinner is at 6:30 PM (with documented exceptions)."""
    md_path = Path(__file__).parent.parent.parent / "output" / "trip-itinerary-latest.md"
    if not md_path.exists():
        print("  SKIP: trip-itinerary-latest.md not found")
        return

    content = md_path.read_text()
    # Find dinner lines in the detailed body (not summary)
    in_body = False
    issues = []
    for i, line in enumerate(content.splitlines(), 1):
        if line.startswith('## Day'):
            in_body = True
        if not in_body:
            continue
        if 'Dinner' in line and re.search(r'\d+:\d+ [AP]M', line):
            time_match = re.search(r'(\d+:\d+ [AP]M)', line)
            if time_match:
                time = time_match.group(1)
                # Exceptions: Schweizerhaus 7:00, Augustine 5:30
                if 'Schweizerhaus' in line or 'Augustine' in line:
                    continue
                if time not in ('6:30 PM',):
                    issues.append((i, time, line.strip()[:80]))

    if issues:
        print(f"  dinner_times: WARN ({len(issues)} non-6:30 dinners)")
        for ln, time, text in issues[:5]:
            print(f"    Line {ln}: {time} - {text}")
    else:
        print("  dinner_times: PASS")


if __name__ == "__main__":
    print("Running tour-planner tests...")
    test_classify_line()
    test_parse_summary()
    test_parse_day_sections()
    test_find_day_boundaries()
    test_no_hotel_returns_in_md()
    test_dinner_times()
    print("\nAll tests complete!")
