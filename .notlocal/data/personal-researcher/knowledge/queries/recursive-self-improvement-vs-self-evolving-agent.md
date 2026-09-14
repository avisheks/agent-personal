---
title: "Recursive self-improvement (RSI) vs self-evolving agent?"
summary: "RSI (recursive self-improvement) is a theoretical/research concept where AI systems modify themselves to become better at self-modification (feedback loop on CAPABILITY). Self-evolving agents are a practical engineering pattern where agents accumulate skills/knowledge from experience (feedback loop on BEHAVIOR). RSI changes the MODEL; self-evolving agents change the SCAFFOLDING around a fixed model. Most 'self-improving' agent products (Hermes Agent, AutoResearch) are self-evolving agents implementing soft RSI, not hard RSI."
type: "query"
createdAt: "2026-06-08T00:00:00Z"
---
## Core Distinction

| Dimension | Recursive Self-Improvement (RSI) | Self-Evolving Agent |
|-----------|----------------------------------|---------------------|
| **What changes** | The MODEL itself (weights, architecture, training process) | The SCAFFOLDING around a fixed model (skills, memory, tools, prompts) |
| **Feedback loop** | Improved system → better at improving itself → recursive acceleration | Experience → new skills → better task performance → more experience |
| **Scope** | Capability enhancement (fundamentally more intelligent) | Behavioral adaptation (same intelligence, more knowledge/skills) |
| **Theoretical origin** | I.J. Good (1965), Yudkowsky (Seed AI), Bostrom (Superintelligence) | Software engineering patterns (plugin systems, knowledge bases) |
| **Risk profile** | Potentially unbounded ("intelligence explosion") | Bounded (model capability is fixed ceiling) |
| **Current status** | Soft RSI exists; hard RSI is theoretical | Widely deployed (Hermes Agent, OpenClaw, coding agents) |
| **Examples** | AutoResearch (modifies training code), STOP (improves own scaffolds) | Hermes Agent (creates skills from experience), Claude Code (learns repo patterns) |

## The Spectrum

```
                    Self-Evolving Agent              Soft RSI                Hard RSI
                    (scaffolding changes)            (workflow changes)       (intelligence changes)
                    ────────────────────────────────────────────────────────────────────────→
                    
What changes:       Skills, memory, prompts          Training code,          Architecture,
                    around FIXED model               eval pipelines          weights, goals
                    
Bounded?            Yes (model is ceiling)           Yes (human oversight)   Theoretically unbounded
                    
Exists today?       YES (Hermes, OpenClaw)           YES (AutoResearch)      NO (theoretical)
                    
Example:            Agent encounters task →          LLM proposes training   System rewrites own
                    creates reusable skill →         change → runs exp →     architecture → becomes
                    refines on next encounter        keeps if metric improves fundamentally smarter
```

## Self-Evolving Agent (Practical Pattern)

The self-evolving agent is a **software engineering pattern** where an agent accumulates capabilities over time without changing its underlying model:

**Mechanism (e.g., Hermes Agent):**
```
1. Agent encounters task T for the first time
2. Solves T using raw LLM reasoning (slow, potentially suboptimal)
3. Extracts a reusable "skill" from the successful solution
4. Stores skill in skill library (conforming to AgentSkills.io standard)
5. Next time T (or similar) appears → retrieves and applies skill (fast, reliable)
6. If skill fails → refines skill based on failure context
7. Over time: skill library grows → agent handles more tasks → less raw reasoning needed
```

**What DOESN'T change:**
- Model weights (same LLM throughout)
- Model architecture (no fine-tuning in the loop)
- Fundamental reasoning capability (bounded by the base model)

**What DOES change:**
- Skill library (grows with experience)
- Memory (accumulates user preferences, task context)
- Prompt templates (refined for specific tasks)
- Tool configurations (learns which tools work for what)

**Products implementing this:** Hermes Agent (NousResearch), coding agents that learn repo patterns, personal assistants with persistent memory.

^[[Hermes Agent]], [[AgentSkills Standard]]

## Recursive Self-Improvement (Research Concept)

RSI is a **feedback loop on capability itself** — the system becomes fundamentally more capable at self-modification:

**Soft RSI (exists today):**
```
1. LLM agent proposes change to ML training code
2. Runs experiment, evaluates metric
3. If improvement: commit change, model/pipeline is now better
4. Better model → better at proposing next change → accelerating loop
```

Example: Karpathy's AutoResearch ran 700+ experiments, modifying training code autonomously. The system improved a model's val_bpb metric iteratively.

**Hard RSI (theoretical, doesn't exist):**
```
1. System rewrites its own architecture
2. New architecture is fundamentally more intelligent
3. More intelligent system redesigns itself even better
4. Intelligence increases without bound → "intelligence explosion"
```

^[[Recursive Self-Improvement (RSI)]], [[Soft RSI vs Hard RSI]], [[Bounded Recursive Self-Improvement]]

## Key Differences in Practice

### What Breaks

| | Self-Evolving Agent | Soft RSI | Hard RSI |
|---|---|---|---|
| **Ceiling** | Base model capability | Available compute + human oversight | Theoretically none |
| **Failure mode** | Skill ossification (learns wrong patterns) | Metric hacking (optimizes proxy, not goal) | Unaligned superintelligence |
| **Time scale** | Hours-days (skill accumulation) | Days-weeks (experiment cycles) | Theoretical (unknown timeline) |
| **Control** | Fully controlled (can delete skills) | Human-in-the-loop (approve changes) | Open question |
| **Reversibility** | Easy (revert skill library) | Medium (revert code commits) | Unknown |

### What They Share

Both self-evolving agents and soft RSI:
- Use LLMs as the reasoning engine
- Improve over time without explicit human programming
- Have feedback loops (experience → improvement → better experience)
- Are bounded by current LLM capability ceilings
- Require evaluation metrics to measure improvement

### The Confusion Source

People conflate these because both are described as "self-improving AI." The distinction matters:
- **Self-evolving agent**: Your chatbot gets better at answering YOUR specific questions over time (learns your preferences, builds skills for your workflows). The model is the same; the context around it improves.
- **RSI**: The AI system makes the NEXT VERSION of itself fundamentally more capable (modifies training data, code, architecture). The model itself changes.

## When Each Applies

| Your Scenario | Pattern | Why |
|---------------|---------|-----|
| Personal assistant that learns your preferences | Self-evolving agent | Model stays fixed; memory/skills accumulate |
| Coding agent that learns a codebase | Self-evolving agent | Builds codebase-specific knowledge, not new capabilities |
| Automated ML research (AutoResearch, Karpathy Loop) | Soft RSI | Actually modifies training code → model improves |
| LLM that generates training data for next version | Soft RSI | Model output feeds into next model's training |
| Agent that creates tools it didn't have before | Borderline | If tools are prompts/scripts → self-evolving. If tools modify model → RSI |
| Theoretical AGI improving itself | Hard RSI | Fundamental architecture changes; doesn't exist yet |

## Implications for Agent Design

### If You're Building a Self-Evolving Agent:
- Accept the base model as your ceiling — invest in choosing the best model
- Focus on skill quality control (validation gates, success rate tracking)
- Design for graceful degradation (bad skills can be deleted)
- Memory management becomes the hard problem (not capability)
- No safety concerns beyond normal LLM risks

### If You're Building Toward Soft RSI:
- Human-in-the-loop is essential (approve code changes before they affect training)
- Evaluation metrics must be robust (avoid Goodhart's Law / metric hacking)
- Version control everything (each experiment must be reversible)
- Rate-limit the improvement loop (don't let it run 1000 experiments without review)
- Safety concerns: experiment code could consume excessive compute, corrupt datasets

## Related

- [[Recursive Self-Improvement (RSI)]]
- [[Soft RSI vs Hard RSI]]
- [[Bounded Recursive Self-Improvement]]
- [[Hermes Agent]] — Self-evolving agent pattern (skill auto-creation)
- [[AutoResearch Framework]] — Soft RSI pattern (modifies training code)
- [[Self-Taught Optimizer (STOP)]] — LLM-driven recursive scaffold improvement
