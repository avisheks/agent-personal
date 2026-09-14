---
title: "Andrej Karpathy's CLAUDE.md Rules: The File That Fixes Claude Code | AI Builder Club"
source: "https://www.aibuilderclub.com/blog/karpathy-claude-md-rules"
ingestedAt: "2026-05-25T15:41:48Z"
---
## What Karpathy Said Was Broken

Andrej Karpathy stopped typing code manually in December 2024. He went from 80% manual coding to 80% agent-driven in a matter of weeks - and called it "the biggest change to my basic coding workflow in two decades."

But he also named exactly what was broken.

In a now-viral post, Karpathy listed the failure modes he kept hitting with Claude Code:

  * Models make wrong assumptions and run with them silently
  * They don't surface confusion, inconsistencies, or tradeoffs
  * They overcomplicate code - bloating abstractions, skipping cleanup
  * They touch code they shouldn't, even when it's orthogonal to the task



His diagnosis was precise. But he didn't just complain - he also gave the fix:

> "LLMs are exceptionally good at looping until they meet specific goals. Don't tell it what to do, give it success criteria and watch it go."

That insight became the basis for `andrej-karpathy-skills` \- a single CLAUDE.md file distilling Karpathy's observations into four engineering principles that you can drop into any project.

## What Is CLAUDE.md?

CLAUDE.md is a project-level instruction file that Claude Code reads at the start of every session. Think of it as a persistent system prompt for your codebase - it tells Claude how to behave before you've typed a single word.

Most developers either leave it empty or fill it with vague instructions like "write clean code." Karpathy's version is different. It targets specific, documented failure modes with specific countermeasures.

## The Four Principles

### 1\. Think Before Coding

_Addresses: wrong assumptions, hidden confusion, missing tradeoffs_

The single most common failure mode Karpathy identified: Claude picks an interpretation and runs with it, never surfacing the assumption.

This principle forces explicit reasoning before any implementation:

  * State assumptions explicitly - if uncertain, ask rather than guess
  * Present multiple interpretations when ambiguity exists
  * Push back when a simpler approach exists
  * Stop and name what's unclear rather than guessing through it



In practice: instead of getting 200 lines of code that solves the wrong problem, you get a brief planning exchange that catches the misread upfront.

### 2\. Simplicity First

_Addresses: overcomplication, bloated abstractions, speculative features_

Claude's default instinct is to over-engineer. It adds error handling for scenarios that can't happen, builds abstractions for single-use code, and layers in "flexibility" nobody asked for.

Karpathy's test: would a senior engineer look at this and say it's overcomplicated? If yes, simplify.

The principle enforces:

  * No features beyond what was explicitly asked
  * No abstractions for single-use code
  * No configurable options that weren't requested
  * If 200 lines could be 50, rewrite it



### 3\. Surgical Changes

_Addresses: orthogonal edits, touching unrelated code, style drift_

Claude has a bad habit of "improving" adjacent code while completing a task. It reformats comments, refactors things that weren't broken, and removes dead code it doesn't fully understand.

This principle draws a hard boundary:

  * Touch only what the user's request requires
  * Match existing style even if you'd do it differently
  * If you notice unrelated dead code, mention it - don't delete it
  * Every changed line should trace directly to the request



The result: diffs that are clean and reviewable instead of sprawling across the codebase.

### 4\. Goal-Driven Execution

_Addresses: imperative task drift, weak success criteria, constant clarification loops_

This is Karpathy's key insight operationalized. Instead of telling Claude _what to do_ , you give it _success criteria_ and let it loop.

The transformation:

  * Instead of "Add validation" - write "Write tests for invalid inputs, then make them pass"
  * Instead of "Fix the bug" - write "Write a test that reproduces it, then make it pass"
  * Instead of "Refactor X" - write "Ensure all tests pass before and after"



For multi-step tasks, the principle asks Claude to state a brief plan with verification steps before touching any code. Strong success criteria let the model loop independently. Weak criteria require constant interruption.

## How to Install It

You have two options:

**Option A: Claude Code Plugin (recommended - works across all projects)**

From within Claude Code:
    
    
    /plugin marketplace add forrestchang/andrej-karpathy-skills
    /plugin install andrej-karpathy-skills@karpathy-skills

**Option B: Per-project CLAUDE.md**

For a new project:
    
    
    curl -o CLAUDE.md https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md

To append to an existing CLAUDE.md:
    
    
    echo "" >> CLAUDE.md
    curl https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md

It also works with Cursor via `.cursor/rules/karpathy-guidelines.mdc`.

## How to Know It's Working

You'll see the difference in your diffs:

  * Fewer unnecessary changes - only requested edits appear
  * Claude asks clarifying questions before implementing, not after mistakes
  * Code is simple the first time, not after you push back
  * PRs are clean and minimal with no drive-by refactoring



One caveat from the project itself: these guidelines bias toward caution over speed. For trivial changes (a typo fix, an obvious one-liner), you don't need the full rigor. The value is on non-trivial, multi-file work where silent wrong assumptions compound fast.

## Why This Matters

The `andrej-karpathy-skills` repo has 144k GitHub stars and 14.7k forks - numbers that reflect genuine word-of-mouth adoption, not hype.

Most builders have already hit these exact failure modes and have been patching them manually, one frustrated debugging session at a time. A single CLAUDE.md file won't make Claude Code perfect, but it systematically targets the four behaviors that waste the most time.

Karpathy's framing is the right one: AI coding is now about giving success criteria and watching the model loop, not about writing the code yourself. The builders who internalize that mental model first are the ones who get the leverage.

Want to go deeper on Claude Code workflows? [Join AI Builder Club](https://www.aibuilderclub.com/pricing?utm_source=blog&utm_medium=seo&utm_campaign=karpathy-claude-md-rules) \- weekly workshops on tools like this, plus a community of 1,200+ builders shipping AI products.