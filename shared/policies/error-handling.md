# Error Handling Policy (v1)

Cross-skill standards for how skills should handle errors and edge cases.

## Input Validation

- Validate all required inputs exist before execution begins.
- If a required input is missing, stop and report clearly — do not guess.
- If an optional input is malformed, log a warning and continue without it.

## Execution Errors

- Log errors with enough context to reproduce (input state, step that failed).
- Distinguish between recoverable errors (continue with degraded output) and
  fatal errors (stop execution, report to user).
- Never silently swallow errors — at minimum, log them.

## External Dependencies

- Network requests (web fetch, API calls) may fail. Always handle timeouts.
- If a URL is unreachable, log and skip — do not halt the entire execution.
- Cache external data when possible to reduce flakiness on re-runs.

## Graceful Degradation

- If a non-critical section cannot be generated, output the rest and note
  what's missing (e.g., "Section X skipped: insufficient data").
- Prefer partial correct output over no output.
