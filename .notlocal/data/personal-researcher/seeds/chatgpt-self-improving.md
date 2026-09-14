# Evolution of Self-Improving Agents: A Curated Reading Roadmap

This roadmap traces the evolution of **self-improving AI agents**, starting from early ideas in reinforcement learning and planning, through LLM-powered agents, and ending with the latest work on autonomous software engineering, self-improving coding agents, and lifelong learning.

Unlike RLHF (which focuses primarily on improving model weights), this roadmap focuses on **improving the entire agent system**, including:

- Reflection
- Planning
- Memory
- Tool use
- Skill acquisition
- Curriculum learning
- Harness optimization
- Self-generated training data
- Lifelong learning

The overall evolution is:

```text
Planning
    ↓
Reasoning
    ↓
Reflection
    ↓
Memory
    ↓
Tool Use
    ↓
Skill Learning
    ↓
Self-Training
    ↓
Harness Optimization
    ↓
Autonomous Coding Agents
    ↓
Self-Improving Agent Platforms
```

---

# Stage 1 — Foundations: Planning Before LLMs

Before language models, autonomous agents were primarily studied in planning and reinforcement learning.

---

## 1. Sutton & Barto

**Reinforcement Learning: An Introduction**

### Learn

- Agent-environment interaction
- Policies
- Delayed rewards
- Credit assignment
- Long-term optimization

These ideas still underpin modern LLM agents.

---

## 2. AlphaGo

Silver et al., Nature (2016)

### Contribution

Combined

- Planning
- Search
- RL
- Neural networks

Introduced the idea that agents can improve by repeatedly interacting with an environment.

---

## 3. AlphaZero

Silver et al., Science (2018)

### Contribution

Self-play

↓

Improved policy

↓

Repeat

One of the earliest examples of autonomous improvement without human demonstrations.

---

## 4. MuZero

Schrittwieser et al. (2020)

### Contribution

Learned an internal world model instead of relying on a known simulator.

Introduced planning without explicit environment dynamics.

---

# Stage 2 — Chain-of-Thought and Deliberate Reasoning

LLMs become capable of reasoning.

---

## 5. Chain-of-Thought Prompting

Wei et al. (2022)

### Contribution

Reasoning becomes explicit.

The model now produces intermediate thoughts before acting.

---

## 6. Self-Consistency

Wang et al. (2022)

### Contribution

Generate multiple reasoning paths.

Choose the best one.

Introduces simple search over reasoning.

---

## 7. Least-to-Most Prompting

Zhou et al. (2022)

### Contribution

Automatically decompose complex tasks into smaller subtasks.

---

# Stage 3 — Search-Based Reasoning

Instead of producing one reasoning path, search over many.

---

## 8. Tree of Thoughts

Yao et al. (2023)

Pipeline

```text
Problem
 ↓
Multiple Thoughts
 ↓
Search
 ↓
Best Path
```

Introduces explicit search over reasoning.

---

## 9. Graph of Thoughts

Besta et al. (2023)

Generalizes Tree of Thoughts.

Reasoning becomes a graph rather than a tree.

---

## 10. RAP (Reasoning via Planning)

Hao et al. (2023)

LLMs perform planning over reasoning trajectories.

---

# Stage 4 — Reflection

The agent critiques itself.

---

## 11. Reflexion

Shinn et al. (NeurIPS 2023)

Pipeline

```text
Run
 ↓
Reflect
 ↓
Retry
```

Reflection is stored in memory for future tasks.

One of the foundational papers in self-improving agents.

---

## 12. Self-Refine

Madaan et al. (2023)

Pipeline

```text
Generate
 ↓
Critique
 ↓
Improve
```

Simple iterative self-improvement without additional training.

---

## 13. CRITIC

Gou et al. (2023)

Uses external tools to critique LLM outputs.

Introduces verifier-guided improvement.

---

# Stage 5 — Memory

Agents begin learning across tasks.

---

## 14. Generative Agents

Park et al. (CHI 2023)

Pipeline

```text
Experience
 ↓
Memory
 ↓
Reflection
 ↓
Planning
```

Introduces

- Long-term memory
- Reflection over memory
- Planning from memory

A landmark paper.

---

## 15. MemGPT

Packer et al. (2023)

Separates

- Working memory
- Long-term memory

Inspired by operating systems.

---

## 16. MemoryBank

Zhong et al. (2023)

Persistent memory across conversations.

---

# Stage 6 — Tool Use

LLMs begin interacting with software.

---

## 17. ReAct

Yao et al. (2023)

Pipeline

```text
Reason
 ↓
Act
 ↓
Observe
 ↓
Repeat
```

Still one of the most influential agent papers.

---

## 18. Toolformer

Schick et al. (2023)

LLMs learn when to call tools.

---

## 19. Gorilla

Patil et al. (2023)

Focuses on API selection.

Introduces retrieval over APIs.

---

## 20. APIBench

Evaluates tool-use capabilities.

---

# Stage 7 — Skill Learning

Agents begin accumulating reusable skills.

---

## 21. Voyager

Wang et al. (2023)

Pipeline

```text
Task
 ↓
Code Skill
 ↓
Skill Library
 ↓
Future Tasks
```

Introduces

- lifelong learning
- curriculum learning
- reusable skills

One of the most influential self-improving agent papers.

---

## 22. AdaPlanner

Adaptive planning through accumulated experience.

---

## 23. Skill Library Papers

Various works on

- reusable skills
- hierarchical agents
- experience replay

---

# Stage 8 — Self-Training

Reflections become training data.

---

## 24. ReST

Generate

↓

Filter

↓

Train

---

## 25. Re-ReST

Trajectory

↓

Reflection

↓

Corrected Trajectory

↓

SFT

---

## 26. Agent-R

Automatically repairs trajectories.

Creates supervision.

---

# Stage 9 — Harness Optimization

Instead of improving weights,

improve the system.

---

## 27. Retrospective Harness Optimization (RHO)

Microsoft Research (2026)

Pipeline

```text
Trajectory
 ↓
Reflection
 ↓
Harness Patch
 ↓
Regression Tests
 ↓
Deploy
```

Optimizes

- prompts
- planning
- workflows
- routing
- retrieval

without changing model weights.

---

## 28. DSPy

Although not a research paper,

DSPy introduces automatic optimization of

- prompts
- demonstrations
- workflows

A practical harness optimization framework.

---

# Stage 10 — Autonomous Software Engineering

Agents improve code.

---

## 29. SWE-agent

Princeton NLP

Automatically fixes GitHub issues.

Pipeline

```text
Issue
 ↓
Plan
 ↓
Edit
 ↓
Test
 ↓
Retry
```

---

## 30. OpenHands (formerly OpenDevin)

General-purpose software engineering agent.

Focuses on

- coding
- debugging
- planning
- tool use

---

## 31. MetaGPT

Multi-agent software company simulation.

Agents specialize into

- PM
- Architect
- Engineer
- QA

---

## 32. Devin (Cognition AI)

Technical report and engineering blogs.

Shows autonomous software engineering workflows.

---

# Stage 11 — Multi-Agent Collaboration

Improvement through cooperation.

---

## 33. AutoGen

Microsoft

Conversation among agents.

---

## 34. CAMEL

Role-playing agents.

---

## 35. CrewAI

Production orchestration.

---

## 36. LangGraph

Graph-based orchestration.

Supports

- memory
- planning
- reflection
- retries

---

# Stage 12 — Self-Improving Reasoning Models

Reflection begins improving model weights.

---

## 37. DeepSeek-R1

RL for reasoning.

---

## 38. Teaching Large Reasoning Models Effective Reflection

Introduces

- SCFT
- RLERR

Reflection becomes part of RL.

---

## 39. Reflect, Retry, Reward

Reflection

↓

Reward

↓

RL

---

# Stage 13 — World Models

Agents learn predictive models of environments.

---

## 40. DreamerV3

Latent world models.

---

## 41. Genie

Interactive world models from video.

---

## 42. SIMA (Google DeepMind)

General game-playing agent using natural language.

Bridges LLM agents and embodied environments.

---

# Stage 14 — Towards Self-Improving Agent Platforms (Emerging Research)

The next frontier is likely to combine all previous ideas.

Proposed architecture:

```text
Task
 ↓
Execution
 ↓
Trajectory Store
 ↓
Reflection
 ↓
Reflection Router
 ↓
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │
Harness       SFT            RL
 │              │              │
 ▼              ▼              ▼
Prompt      New Data      Better Policy
Planning
Memory
Tools
```

Characteristics:

- Automatic trajectory collection
- Reflection
- Harness optimization
- Automatic SFT generation
- RL dataset generation
- Continuous evaluation
- Regression testing
- Safe deployment

This represents the convergence of agent engineering, RL, and continual learning.

---

# Recommended Reading Schedule

| Week | Papers | Main Question |
|------|---------|---------------|
| **1** | Sutton & Barto, AlphaGo, AlphaZero, MuZero | What is an intelligent agent? |
| **2** | Chain-of-Thought, Self-Consistency, Least-to-Most | How do LLMs reason? |
| **3** | Tree of Thoughts, Graph of Thoughts, RAP | How do agents search over reasoning? |
| **4** | ReAct, Toolformer, Gorilla | How do agents interact with external tools? |
| **5** | Reflexion, Self-Refine, CRITIC | How do agents critique themselves? |
| **6** | Generative Agents, MemGPT, MemoryBank | How do agents remember and learn over time? |
| **7** | Voyager, AdaPlanner, Skill Library papers | How do agents accumulate reusable skills? |
| **8** | ReST, Re-ReST, Agent-R | How do reflections become training data? |
| **9** | Retrospective Harness Optimization, DSPy | How do agents improve without changing model weights? |
| **10** | SWE-agent, OpenHands, MetaGPT, Devin | How do autonomous coding agents work? |
| **11** | AutoGen, CAMEL, CrewAI, LangGraph | How do multiple agents collaborate? |
| **12** | DeepSeek-R1, Teaching Large Reasoning Models Effective Reflection, Reflect-Retry-Reward | How does reflection improve policies? |
| **13** | DreamerV3, Genie, SIMA | How do agents learn world models? |

---

# The Overall Evolution

```text
Planning
    ↓
Reasoning
    ↓
Search
    ↓
Reflection
    ↓
Memory
    ↓
Tool Use
    ↓
Skill Learning
    ↓
Self-Training
    ↓
Harness Optimization
    ↓
Autonomous Coding Agents
    ↓
Multi-Agent Systems
    ↓
Reflection-Guided RL
    ↓
World Models
    ↓
Self-Improving Agent Platforms
```

## Future Research Direction

A compelling next step is to unify these ideas into a **Self-Improving Agent Platform** that continuously:

1. Executes tasks.
2. Collects trajectories.
3. Reflects on failures and successes.
4. Routes improvements to:
   - **Harness** (prompts, planning, memory, tools)
   - **SFT** (corrected demonstrations)
   - **RL** (reward signals or preferences)
5. Validates changes through automated regression testing.
6. Deploys only improvements that demonstrably increase overall agent performance.

Such a platform would integrate the major advances from the last decade into a single continual-learning architecture and is an active direction of research across both academia and industry.