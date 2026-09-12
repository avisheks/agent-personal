---
title: "Karpathy's CLAUDE.md Skills File: The Complete Guide"
source: "https://agentpedia.codes/blog/karpathy-claude-code-skills-guide"
ingestedAt: "2026-05-25T15:41:48Z"
---
In the fast-evolving world of AI-assisted coding, one GitHub repo has emerged as the single most popular set of behavioral guidelines for AI coding agents: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills). Created by developer **Forrest Chang** , it distills Andrej Karpathy's viral observations about LLM coding pitfalls into a single, actionable `CLAUDE.md` file. We researched it across **GitHub, Twitter/X, Reddit, web articles, and the source code itself** — here's the definitive guide.

Get the latest on AI, LLMs & developer tools

New MCP servers, model updates, and guides like this one — delivered weekly.

### 🎬 Watch the Video Breakdown

VIDEO

Prefer reading? Keep scrolling for the full written guide with code examples.

## 1\. Why It Went Viral

Let's start with why this repo matters. It became one of the fastest-growing repositories on GitHub — tens of thousands of stars in its first weeks — for a repo that contains essentially **one file**.

Not a framework. Not a library. Not an app. A single set of behavioral guidelines for AI coding agents. Created on **January 27, 2026** , released under the **MIT license** , and still growing. That tells you something important about where the industry is heading.

Why This Matters

Many popular open-source tools with thousands of contributors and years of development have fewer stars. This repo went viral with **a handful of commits and zero runtime dependencies**. The value isn't in the code — it's in the _ideas_.

## 2\. The Origin Story

The repo traces directly to a viral tweet by **Andrej Karpathy** — co-founder of OpenAI, former AI lead at Tesla, and the person who coined the term “vibe coding.” In his post, Karpathy didn't share a tool or a repo. He shared _observations_ — a list of frustrations with how LLMs behave when writing code.

Developer **Forrest Chang** read these observations and did something practical: he converted them into a structured, machine-readable `CLAUDE.md` file. Not a vague blog post. Not a Twitter thread. A **configuration file** that AI agents actually read and follow.

The key insight was this: Karpathy identified problems. Forrest Chang encoded solutions. The community validated both — making it one of the most starred AI-workflow repos on GitHub.

## 3\. The Problems Karpathy Identified

Karpathy's observations weren't vague complaints. They were specific, reproducible patterns that every developer using AI coding agents has experienced. Here are his exact words:

Problem 1: Hidden Assumptions

“The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should.”

Problem 2: Over-Engineering

“They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do.”

Problem 3: Unintended Side Effects

“They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task.”

If you've used Claude Code, Copilot, Cursor, or any AI coding agent, you've felt this. You ask the agent to fix a bug, and it rewrites half the file. You ask it to add a feature, and it builds an entire abstraction layer. You ask it for help, and it confidently charges ahead with wrong assumptions.

The Reddit community (especially r/ClaudeAI and r/ClaudeCode) has a widely-used term for this behavior: **“the confident junior dev.”** The AI is fast, knowledgeable, and prone to making naive mistakes if left unsupervised. It's brilliant but unreliable — exactly the kind of engineer who needs clear guardrails.

## 4\. The Four Principles

Forrest Chang distilled Karpathy's observations into four principles. Each one directly addresses a specific class of LLM failure:

Principle| Addresses  
---|---  
**Think Before Coding**|  Wrong assumptions, hidden confusion, missing tradeoffs  
**Simplicity First**|  Overcomplication, bloated abstractions, speculative features  
**Surgical Changes**|  Orthogonal edits, touching code you shouldn't, style drift  
**Goal-Driven Execution**|  Vague implementation, no verification, weak success criteria  
  
Let's break down each one.

## Principle 1: Think Before Coding

**“Don't assume. Don't hide confusion. Surface tradeoffs.”**

This is the most fundamental principle. LLMs have a tendency to pick an interpretation silently and run with it. This principle forces explicit reasoning:

  * **State assumptions explicitly** — If uncertain, ask rather than guess
  * **Present multiple interpretations** — Don't pick silently when ambiguity exists
  * **Push back when warranted** — If a simpler approach exists, say so
  * **Stop when confused** — Name what's unclear and ask for clarification



### Example: The Hidden Assumption Trap

User request: **“Add a feature to export user data”**

❌ WHAT LLMs DO (WRONG ASSUMPTIONS)  
  
def export_users(format='json'):  
users = User.query.all()  
# Assumed ALL users, file location, fields,  
# CSV fieldnames — without asking anything  


✅ WHAT SHOULD HAPPEN (SURFACE ASSUMPTIONS)  
  
Before implementing, I need to clarify:  
  
1\. **Scope** : Export all users or filtered subset?  
(privacy implications)  
2\. **Format** : Download file? Background job?  
API endpoint?  
3\. **Fields** : Which user fields?  
(some might be sensitive)  
4\. **Volume** : How many users typically?  
  
Simplest approach: Add an API endpoint that  
returns paginated JSON. What's your preference?  


## Principle 2: Simplicity First

**“Minimum code that solves the problem. Nothing speculative.”**

This combats the LLM's tendency toward over-engineering. The rules are strict:

  * No features beyond what was asked
  * No abstractions for single-use code
  * No “flexibility” or “configurability” that wasn't requested
  * No error handling for impossible scenarios
  * If 200 lines could be 50, rewrite it



**The test:** Would a senior engineer say this is overcomplicated? If yes, simplify.

### Example: The Over-Abstraction Trap

User request: **“Add a function to calculate discount”**

❌ WHAT LLMs DO (OVERENGINEERED)  
  
class DiscountStrategy(ABC):  
@abstractmethod  
def calculate(self, amount): ...  
  
class PercentageDiscount(DiscountStrategy): ...  
class FixedDiscount(DiscountStrategy): ...  
class DiscountConfig: ...  
class DiscountCalculator: ...  
  
# 50+ lines for a single calculation  
# Usage requires 30+ lines of setup  


✅ WHAT SHOULD HAPPEN (SIMPLE)  
  
def calculate_discount(amount, percent):  
"""Calculate discount. percent is 0-100."""  
return amount * (percent / 100)  
  
# Usage  
discount = calculate_discount(100.0, 10.0) # $10 off  


Key Insight from the Repo

“The ‘overcomplicated’ examples aren't obviously wrong — they follow design patterns and best practices. The problem is **timing** : they add complexity before it's needed.” Good code solves today's problem simply, not tomorrow's problem prematurely.

## Principle 3: Surgical Changes

**“Touch only what you must. Clean up only your own mess.”**

This is the principle that most directly addresses Karpathy's frustration with LLMs making orthogonal changes. When editing existing code:

  * Don't “improve” adjacent code, comments, or formatting
  * Don't refactor things that aren't broken
  * Match existing style, even if you'd do it differently
  * If you notice unrelated dead code, mention it — don't delete it



When your changes create orphans:

  * Remove imports/variables/functions that **YOUR changes** made unused
  * Don't remove pre-existing dead code unless asked



**The test:** Every changed line should trace directly to the user's request.

### Example: The Drive-By Refactoring Trap

User request: **“Fix the bug where empty emails crash the validator”**

❌ WHAT LLMs DO (TOO MUCH)  
  
Changed 15 lines:  
\- Added docstring (not asked)  
\- Added username validation (not asked)  
\- Changed comments (not asked)  
\- “Improved” email validation logic (not asked)  
\- Added .strip() calls everywhere (not asked)  


✅ WHAT SHOULD HAPPEN (SURGICAL)  
  
Changed 3 lines:  
\- Added empty-string guard for email  
\- Changed variable reference to avoid crash  
\- **Nothing else touched.**  


### Example: The Style Drift Trap

User request: **“Add logging to the upload function”**

The LLM adds logging — but also changes single quotes to double quotes, adds type hints nobody asked for, adds a docstring, reformats whitespace, and restructures the boolean return logic. The correct approach: add _only_ the logging lines, using the **existing style** (single quotes, no type hints, same spacing).

## Principle 4: Goal-Driven Execution

**“Define success criteria. Loop until verified.”**

This principle captures what Karpathy considers the highest-leverage insight about working with LLMs:

Karpathy's Key Insight

“LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go.”

The principle transforms imperative tasks into declarative goals:

Instead of...| Transform to...  
---|---  
“Add validation”| “Write tests for invalid inputs, then make them pass”  
“Fix the bug”| “Write a test that reproduces it, then make it pass”  
“Refactor X”| “Ensure tests pass before and after”  
  
For multi-step tasks, the model should state a brief plan:

GOAL-DRIVEN PLAN FORMAT  
  
1\. [Step] → verify: [check]  
2\. [Step] → verify: [check]  
3\. [Step] → verify: [check]  
  
Strong success criteria let the LLM loop  
independently. Weak criteria (“make it work”)  
require constant clarification.  


## 5\. The Actual CLAUDE.md File

Here's the complete, unabridged `CLAUDE.md` file from the repo. It's intentionally short — under 70 lines. That brevity is a feature, not a limitation:

# CLAUDE.md  
  
Behavioral guidelines to reduce common LLM coding  
mistakes. Merge with project-specific instructions  
as needed.  
  
**Tradeoff:** These guidelines bias toward caution  
over speed. For trivial tasks, use judgment.  
  
## 1. Think Before Coding  
**Don't assume. Don't hide confusion. Surface tradeoffs.**  
  
Before implementing:  
\- State your assumptions explicitly. If uncertain, ask.  
\- If multiple interpretations exist, present them.  
\- If a simpler approach exists, say so.  
\- If something is unclear, stop. Name what's confusing.  
  
## 2. Simplicity First  
**Minimum code that solves the problem. Nothing speculative.**  
  
\- No features beyond what was asked.  
\- No abstractions for single-use code.  
\- No “flexibility” that wasn't requested.  
\- No error handling for impossible scenarios.  
\- If 200 lines could be 50, rewrite it.  
  
## 3. Surgical Changes  
**Touch only what you must. Clean up only your own mess.**  
  
\- Don't “improve” adjacent code or formatting.  
\- Don't refactor things that aren't broken.  
\- Match existing style, even if you'd do it differently.  
\- If you notice dead code, mention it — don't delete it.  
  
## 4. Goal-Driven Execution  
**Define success criteria. Loop until verified.**  
  
Transform tasks into verifiable goals:  
\- “Add validation” → “Write tests, then make them pass”  
\- “Fix the bug” → “Reproduce it in a test, then fix”  
\- “Refactor X” → “Ensure tests pass before and after”  


That's it. The entire file. Its power is in its conciseness — short enough to fit in the agent's context window without crowding out project-specific instructions, long enough to encode the critical behavioral guardrails.

## 6\. Real-World Examples

The repo includes an [EXAMPLES.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/EXAMPLES.md) file with detailed before/after comparisons. Here's the key “anti-patterns summary” from the file:

Principle| Anti-Pattern| Fix  
---|---|---  
**Think Before Coding**|  Silently assumes file format, fields, scope| List assumptions explicitly, ask for clarification  
**Simplicity First**|  Strategy pattern for a single discount calculation| One function until complexity is actually needed  
**Surgical Changes**|  Reformats quotes, adds type hints while fixing a bug| Only change lines that fix the reported issue  
**Goal-Driven**|  “I'll review and improve the code”| “Write test for bug X → make it pass → verify no regressions”  
  
## 7\. How to Install

The repo offers two installation methods:

### Option A: Claude Code Plugin (Recommended)

This installs the guidelines as a Claude Code plugin, making the skill available across **all your projects** :

# First, add the marketplace  
/plugin marketplace add forrestchang/andrej-karpathy-skills  
  
# Then install the plugin  
/plugin install andrej-karpathy-skills@karpathy-skills  


### Option B: CLAUDE.md (Per-Project)

For a single project:

# New project  
curl -o CLAUDE.md https://raw.githubusercontent.com/  
forrestchang/andrej-karpathy-skills/main/CLAUDE.md  


# Existing project (append)  
echo "" >> CLAUDE.md  
curl https://raw.githubusercontent.com/forrestchang/  
andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md  


Customization

These guidelines are designed to be **merged with project-specific instructions**. Add your own sections for TypeScript config, API standards, testing conventions, or whatever your project needs. The four principles provide the behavioral floor; your project rules build on top.

## 8\. What is CLAUDE.md?

For those unfamiliar with the concept: `CLAUDE.md` is a **Project Memory Card** for AI coding agents. It is automatically read by Claude Code at the start of every session, providing persistent context that carries across conversations.

Think of it as the AI equivalent of onboarding documentation for a new developer — except the AI reads it _every single time_ it starts working on your project.

### Best Practices for CLAUDE.md (2026)

Section| Content  
---|---  
**Project Overview**|  2-3 sentence summary of what the project does  
**Tech Stack**|  Languages, frameworks, key libraries  
**Architecture**|  Codebase map (source, components, config)  
**Commands**|  dev, build, test, lint commands  
**Coding Standards**|  Naming conventions, patterns, style rules  
**Safety Rules**|  “Never hardcode API keys,” “Don't edit /config”  
  
### The Hierarchy

  * `CLAUDE.md` (project root) — Shared context, committed to Git
  * `CLAUDE.local.md` (project root) — Private dev-specific notes (add to .gitignore)
  * `~/.claude/CLAUDE.md` — Global preferences across all projects
  * Subdirectory `CLAUDE.md` files — Context pulled only when working in that directory



**The rule of thumb:** If you have to repeat an instruction in chat more than twice, promote it into your `CLAUDE.md`.

We researched discussions across **Reddit (r/ClaudeAI, r/ClaudeCode), Twitter/X, and technical blogs**. Here's what the community thinks:

### The “Confident Junior Dev” Consensus

The Reddit community frequently describes Claude Code as a brilliant but sometimes unreliable **“junior developer.”** It's fast and knowledgeable, but prone to taking dangerous shortcuts, hallucinating, or making naive mistakes if left unsupervised. The Karpathy skills file directly addresses this by adding the guardrails a junior dev needs.

### The “Skill Issue” Argument

A prevailing sentiment on Reddit: the quality of AI-generated code is **directly proportional to the user's own engineering judgment** and “context engineering” skills. Advanced users who master prompt structure, context management, and verification loops report dramatically higher success rates. The Karpathy skills file is one of the most popular “context engineering” tools.

### The “AI Psychosis” Debate

Karpathy's description of “perpetual AI psychosis” — a constant state of hyper-productive yet draining agent-direction — resonated deeply. Some see AI agents as a competitive advantage you can't afford to ignore. Others call it “productivity theater” — feeling fast while producing unmaintainable code. The skills file sits in the middle: it acknowledges that AI agents are powerful but argues they need **disciplined constraints**.

### The Human Bottleneck Shift

The community consensus: AI has lowered the barrier to _writing_ code. But the real bottleneck has shifted from implementation to **architecture and evaluation**. The challenge is no longer “how do I write this?” but “do I understand what the agent just built well enough to maintain it?”

## 10\. The Bigger Picture

### From “Vibe Coding” to “Agentic Engineering”

When Karpathy coined “vibe coding” in early 2025, it described a loose, conversational way of prompting AI. By 2026, the community has matured this into **“agentic engineering”** — a discipline where developers treat AI as a partner requiring clear objectives, defined boundaries, and rigorous testing.

The `andrej-karpathy-skills` repo represents this evolution. It's not about limiting what AI can do. It's about **channeling what it can do** through principles that produce better outcomes.

### The “Idea File” Pattern

This repo also exemplifies what Karpathy calls the **“idea file”** pattern — sharing ideas rather than implementations. The `CLAUDE.md` file isn't a library anyone imports. It's a set of principles anyone can adapt. The recipient's agent customizes it for their specific needs. This is a new kind of open source: not open code, but **open ideas**.

### How to Know It's Working

From the repo's README, these guidelines are working if you see:

  * **Fewer unnecessary changes in diffs** — Only requested changes appear
  * **Fewer rewrites due to overcomplication** — Code is simple the first time
  * **Clarifying questions come before implementation** — Not after mistakes
  * **Clean, minimal PRs** — No drive-by refactoring or “improvements”



### The Tradeoff Note

The repo is honest about its tradeoffs: **“These guidelines bias toward caution over speed.”** For trivial tasks (simple typo fixes, obvious one-liners), use judgment — not every change needs the full rigor. The goal is reducing costly mistakes on non-trivial work, not slowing down simple tasks.

## 11\. All Sources & Links

This article was researched using **multi-source research** across GitHub, Twitter/X, Reddit, web articles, and the source code itself. Here are all the primary sources:

### Primary Sources

### Community Discussions

  * **Reddit r/ClaudeAI** — Community discussions on Claude Code workflows and the “confident junior dev” consensus
  * **Reddit r/ClaudeCode** — Threads on CLAUDE.md best practices and spec systems
  * **Twitter/X** — Developer reactions, workflow sharing, and adoption reports



### Web Sources

  * **Medium** — Technical reviews and implementation guides
  * **dev.to** — Developer community tutorials
  * **Forbes** — Coverage of “vibe coding” evolution to “agentic engineering”
  * **VentureBeat** — Analysis of Karpathy's “compiler” analogy for context management
  * **Analytics Vidhya** — Technical analysis of the skills file's approach



### Documentation

### Related Articles on This Site

### Get the Ultimate Antigravity Cheat Sheet

Join 5,000+ developers and get our exclusive PDF guide to mastering Gemini 3 shortcuts and agent workflows.