# Agent Personal

Multi-skill personal and professional agent platform. All skill invocations MUST be routed through the super-agent orchestrator for observability.

## Mandatory Routing Rule

**Before doing any work**, check whether the user's request matches a skill in `skills/skills-catalog.yaml`. If it does:

1. Read and follow `skills/super-agent.md` as the orchestrator
2. Execute the full protocol: plan → approve → execute
3. Emit all events to `.local/logs/super-agent/events.jsonl`
4. Print the session-close banner when done

**Do NOT** execute skill-related work directly — even if you know which skill to use and what to do. The super-agent protocol exists for observability and approval tracking. Bypassing it produces untraced sessions that cannot be evaluated or improved.

**What counts as "matches a skill":** Any request involving project status, interview prep/feedback, document writing/review, paper review, codebase analysis, ML experiments, career advice, news briefings, options trading, or travel planning. When in doubt, check the catalog's `triggers` field.

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
.local/                      # Sensitive data (gitignored)
  skills-config.yaml         # Org-specific config (internal URLs, Asana GIDs)
  data/options-pnl/          # Brokerage CSVs, PnL reports
  logs/super-agent/          # Event log (events.jsonl)
```

## Environment

- No virtual environment required for skill execution (skills are prompt-based, not code)
- Python scripts in `src/` use system Python 3 (no venv)
- `render_html.py` for news reports, `compute_pnl.py` / `render_report.py` for options PnL
