# Agent Personal

Multi-skill personal and professional agent platform. All skill invocations MUST be routed through the super-agent orchestrator for observability.

## Mandatory Routing Rule

**Before doing any work**, check whether the user's request matches a skill in `skills/skills-catalog.yaml`. If it does:

1. Read and follow `skills/super-agent.md` as the orchestrator
2. Execute the full protocol: plan → approve → execute
3. Emit all events to `$REPO_ROOT/.local/logs/super-agent/events.jsonl` (where `REPO_ROOT` is resolved via `git rev-parse --show-toplevel` at session start — ensures worktree-correct paths)
4. Print the session-close banner when done

**Do NOT** execute skill-related work directly — even if you know which skill to use and what to do. The super-agent protocol exists for observability and approval tracking. Bypassing it produces untraced sessions that cannot be evaluated or improved.

**Enforcement check:** Before running ANY Python script in `src/stock_research/`, generating ANY report file, or calling ANY data ingestion module, run: `grep "session_start" .local/logs/super-agent/events.jsonl 2>/dev/null | grep "$(date +%Y-%m-%d)"`. If this returns nothing, you skipped the orchestrator — STOP and route through `skills/super-agent.md` first. No exceptions.

**What counts as "matches a skill":** Any request involving project status, interview prep/feedback, document writing/review, paper review, codebase analysis, ML experiments, career advice, news briefings, options trading, stock research/analysis, travel planning, or knowledge-base research (ingesting sources, compiling knowledge, generating reports, querying topics). When in doubt, check the catalog's `triggers` field.

**What does NOT need routing:** General questions about the codebase, file editing that doesn't invoke a skill's workflow, git operations, and meta-work on the skills themselves (editing skill files, updating the catalog).

## Project Layout

```
skills/
  super-agent.md             # Orchestrator — entry point for all skill invocations
  skills-catalog.yaml        # Machine-readable skill index (routing source of truth)
  sample-config.yaml         # Config template (safe to commit)
  coworker-*.md              # Professional/work skills (require .local/skills-config.yaml)
  personal-*.md              # Personal productivity skills
  news-topics/               # Topic configs for news-summarizer
.notlocal/data/              # Non-sensitive skill data (tracked by git)
  personal-news/             # AI news briefing reports
  personal-career/           # Career state, study plans
  tour-planner/              # Trip itineraries
  personal-researcher/       # Knowledge base: sources, knowledge pages, reports, seeds
  personal-investor/         # DuckDB research DB, raw data, generated reports
.local/                      # Sensitive data (gitignored)
  skills-config.yaml         # Org-specific config (internal URLs, Asana GIDs)
  data/options-pnl/          # Brokerage CSVs, PnL reports
  logs/super-agent/          # Event log (events.jsonl)
```

## Environment

- No virtual environment required for skill execution (skills are prompt-based, not code)
- Python scripts in `src/` use system Python 3 (no venv)
- `render_html.py` for news reports, `compute_pnl.py` / `render_report.py` for options PnL
- Stock research requires: `pip install duckdb yfinance httpx beautifulsoup4 pyyaml`
- Stock research env vars: `EDGAR_USER_AGENT` (required), `FMP_API_KEY` / `ALPHA_VANTAGE_API_KEY` (optional)
- AWS credentials (for Bedrock LLM): `ada credentials update --account=237287177058 --provider=conduit --role=IibsAdminAccess-DO-NOT-DELETE --profile=default --once`
