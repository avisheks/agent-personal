---
title: "Claude Code writing itself?"
summary: "Confirmed: Anthropic dogfoods Claude Code to develop Claude Code. Analogous to a self-hosting compiler, not recursive self-improvement. Human-in-the-loop with standard code review/CI."
type: query
createdAt: 2026-06-07
topic: claude-code
---

# Claude Code Writing Itself

## Short Answer

**Yes, confirmed.** Anthropic uses Claude Code to develop Claude Code itself. This is publicly documented in their engineering blog ("Claude Code: Best Practices for Agentic Coding") and discussed by their engineering lead Boris Cherny. It is human-directed tool-assisted development, not autonomous self-modification.

## How It Works

- Anthropic engineers use Claude Code to write features, fix bugs, write tests, and refactor Claude Code's own TypeScript/Node.js codebase
- The Claude Code repository contains its own `CLAUDE.md` that instructs Claude Code how to work on itself (coding conventions, test commands, architecture)
- Standard CI/CD: Jest/Vitest tests, human code review, conventional build system
- No autonomous self-modification — always human-in-the-loop

## Analogy: Self-Hosting Compiler

Like GCC compiling itself or Rust bootstrapping its own compiler:
- You need a working version N to efficiently build version N+1
- The tool assists but doesn't autonomously decide to improve itself
- Build infrastructure is conventional (npm install / npm run build)

## What This Is NOT

- **Not recursive self-improvement** in the AGI safety sense — the model powering Claude Code is not being retrained by this process
- **Not autonomous** — engineers direct the changes, review output, merge PRs
- **Not a closed loop** — the Claude model (Sonnet/Opus) is trained separately; code changes to the CLI don't affect the model

## Confirmed vs Unconfirmed

| Claim | Status |
|-------|--------|
| Claude Code is used to develop Claude Code | Confirmed (Anthropic blog, engineer statements) |
| Majority of Claude Code's code is AI-written | Plausible (~75% AI-assisted company-wide per Dario Amodei) |
| Claude Code autonomously fixes its own bugs | Not confirmed / unlikely |
| This is "recursive self-improvement" | No — tool-assisted development |

## Sources

- Anthropic Engineering Blog: "Claude Code: Best Practices for Agentic Coding"
- Boris Cherny (Claude Code engineering lead) — Twitter/X statements
- Dario Amodei interviews (2025) — ~75% of Anthropic code AI-assisted

## Related

- [[Claude Code CLI Tool]]
- [[Recursive Self-Improvement (RSI)]]
- [[Soft RSI vs Hard RSI]]
