# Data Validation Policy (v1)

Cross-skill standards for validating input data before processing.

## File Presence

- Check that all expected input files exist in the designated directory.
- Report missing files explicitly with the expected filename pattern.

## Format Validation

- Verify file format matches expectations (CSV headers, JSON schema, markdown structure).
- On format mismatch, report the discrepancy and stop — do not attempt to parse malformed data.

## Data Freshness

- For time-sensitive skills (news-summarizer), verify input data covers the target date range.
- Flag stale data (e.g., brokerage exports that don't cover the requested period).

## Cross-Reference

- When multiple input sources exist for the same data, cross-reference for consistency.
- Report discrepancies between sources rather than silently picking one.

## Bounds Checking

- Validate that numerical values fall within reasonable ranges.
- Flag outliers that may indicate parsing errors (e.g., a $1M single-trade PnL).
