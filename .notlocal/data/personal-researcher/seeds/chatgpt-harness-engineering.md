# Harness Engineering for Agentic AI

## Improving Agent Performance Without Changing the Model

> **Key idea:** Modern agent performance depends as much on the *execution harness* as on the underlying LLM itself.

A useful mental model is:

```text
Agent Performance = Model × Harness
```

The **harness** encompasses everything surrounding the model, including:

* Prompt and context construction
* Tool selection and orchestration
* Planning
* Retrieval
* Memory
* Verification
* Retry policies
* Execution control
* Observability
* Continuous optimization

Over the past two years, frontier AI teams have increasingly shifted their focus from **prompt engineering** toward **harness (or agent) engineering**, recognizing that substantial gains can be achieved without retraining or fine-tuning the underlying foundation model.

---

# Harness Engineering Maturity Model

| Level | Technique                            | Human Effort | Automation      |
| ----- | ------------------------------------ | ------------ | --------------- |
| 0     | Prompt Engineering                   | High         | None            |
| 1     | Context Engineering                  | High         | Low             |
| 2     | Workflow / Orchestration Engineering | Medium       | Low             |
| 3     | Retrieval & Memory Engineering       | Medium       | Medium          |
| 4     | Verification & Self-Correction       | Medium       | Medium          |
| 5     | Observability-Driven Optimization    | Low          | High            |
| 6     | Automatic Harness Optimization       | Very Low     | High            |
| 7     | Self-Evolving Harnesses              | Minimal      | Fully Automated |

---

# Level 0 — Prompt Engineering

The simplest form of harness engineering is improving the prompts presented to the model.

Typical techniques include:

* Better system prompts
* Few-shot examples
* Structured outputs (JSON/XML)
* Role prompting
* Explicit reasoning instructions
* Planning prompts
* Chain-of-thought prompting (when appropriate)

Representative research includes:

* Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*
* Yao et al. (2023), *ReAct: Synergizing Reasoning and Acting in Language Models*
* Yao et al. (2023), *Tree of Thoughts*
* Khattab et al. (2023), *DSPy*

While prompt engineering remains valuable, most production systems quickly reach diminishing returns.

---

# Level 1 — Context Engineering

Rather than changing prompt wording, context engineering focuses on **improving the information provided to the model**.

Typical improvements include:

* Higher-quality retrieval
* Context compression
* Dynamic prompt assembly
* Relevant few-shot example selection
* Instruction hierarchy
* Separation of immutable policies from mutable task context
* Token budget optimization

The guiding principle is:

> Provide the model with the smallest amount of information that maximizes task performance.

Major organizations including Anthropic, OpenAI, and LangChain increasingly describe context engineering as more impactful than prompt engineering for complex agents.

Typical examples include:

* Claude Code
* OpenAI Codex Agent
* LangGraph / Deep Agents
* Enterprise RAG systems

---

# Level 2 — Workflow Engineering

Rather than issuing a single LLM call, redesign the execution graph.

Typical workflow:

```text
Plan
 ↓
Retrieve
 ↓
Execute
 ↓
Verify
 ↓
Repair
 ↓
Return
```

Common techniques include:

* Planner/executor architectures
* Multi-agent systems
* Specialist agents
* Reviewer agents
* Task decomposition
* Parallel execution
* Dynamic routing
* Branch-and-bound search

Representative work:

* ReAct
* Reflexion
* CodeAct
* AutoGen
* LangGraph

In practice, workflow engineering often yields larger gains than prompt optimization.

---

# Level 3 — Retrieval & Memory Engineering

Instead of making every decision from scratch, agents begin accumulating experience.

## Short-term memory

* Conversation history
* Scratchpads
* Intermediate reasoning
* Execution traces

## Long-term memory

* Vector memories
* Successful trajectories
* Reusable plans
* Tool usage history
* Cached computations
* Prior failures

Representative systems include:

* Voyager
* Generative Agents
* MemGPT

The model itself remains frozen while the surrounding memory system continuously improves.

---

# Level 4 — Verification & Self-Correction

Modern production agents rarely trust their first response.

Typical execution loop:

```text
Generate
 ↓
Critique
 ↓
Repair
 ↓
Verify
 ↓
Return
```

Verification commonly combines:

* Rule-based validators
* Syntax validation
* Business-rule validation
* Security checks
* Citation validation
* Unit tests
* LLM-as-a-Judge
* Retry policies

Representative research:

* Reflexion
* Self-Refine
* Constitutional AI

Verification layers substantially improve reliability in coding, enterprise automation, and structured reasoning tasks.

---

# Level 5 — Observability-Driven Harness Engineering

Once thousands of executions are available, the harness itself becomes observable.

Instead of asking:

> "How do I improve my prompt?"

the question becomes:

> "Where does the execution pipeline fail?"

Typical telemetry includes:

* Trace collection
* Tool success rates
* Retrieval quality
* Retry statistics
* Latency breakdown
* Hallucination causes
* Token consumption
* Execution graphs

Popular tooling includes:

* LangSmith
* Langfuse
* MLflow
* Galileo
* Helicone
* OpenTelemetry

The resulting insights guide systematic improvements to the harness rather than the model.

---

# Level 6 — Automatic Harness Optimization

Rather than manually modifying prompts and workflows, optimization becomes automated.

Typical optimization loop:

```text
Run benchmark
 ↓
Collect failures
 ↓
Cluster failures
 ↓
Infer root causes
 ↓
Modify harness
 ↓
Re-run benchmark
 ↓
Accept improvements
```

Representative approaches include:

### SPEAR (2026)

SPEAR treats prompt optimization as an autonomous agent capable of:

* analyzing benchmark failures
* generating new prompts
* writing helper code
* computing diagnostics
* rolling back regressions

This represents a significant advance beyond earlier automatic prompt engineering systems.

---

### Retrospective Harness Optimization (Microsoft Research)

Rather than relying on human labels, the optimizer learns from historical execution trajectories.

Typical workflow:

1. Replay failed trajectories
2. Generate candidate improvements
3. Evaluate automatically
4. Retain only improvements

This enables continual harness improvement with minimal human supervision.

---

# Level 7 — Self-Evolving Harnesses

The newest research direction extends optimization beyond prompts.

Instead of optimizing only prompt text, the system continuously improves:

* Tool selection
* Workflow policies
* Middleware
* Context construction
* Memory
* Retry logic
* Routing policies
* Verification pipelines

Representative work includes **Agentic Harness Engineering (AHE)**, which treats every editable component of the execution stack as an optimization target.

Key observations from this work include:

* Better tools often outperform better prompts.
* Middleware improvements can transfer across models.
* Memory architecture frequently contributes more than prompt wording.
* Harness improvements generalize even when the underlying LLM remains fixed.

---

# Industry Perspective

## Anthropic

Anthropic emphasizes:

* Context engineering
* Long-running execution
* Tool use
* Memory management
* Agent reliability

Their engineering blog argues that context construction is often more important than prompt wording for production systems.

---

## OpenAI

OpenAI's agent systems emphasize:

* Tool orchestration
* Planning
* Execution policies
* Multi-step workflows
* Structured outputs

The focus is increasingly on reliable execution rather than isolated model capability.

---

## LangChain

LangChain popularized the concept of **Harness Engineering** through its work on Deep Agents.

Key themes include:

* Execution traces
* Workflow design
* Observability
* Evaluation
* Continuous optimization

---

## Microsoft Research

Current research emphasizes:

* Learning from trajectories
* Automatic workflow improvement
* Self-improving agents
* Retrospective optimization

---

## Google DeepMind

DeepMind's recent agent research focuses on:

* Planning
* Tool use
* Multi-step reasoning
* Verification
* General-purpose agent architectures

---

# Practical Roadmap for Enterprise AI Systems

For production systems (e.g., Search, Ads, Customer Support, Coding Assistants), an effective progression is:

1. Establish strong prompt engineering.
2. Improve context assembly and retrieval.
3. Introduce planning and workflow orchestration.
4. Add verification and repair loops.
5. Instrument comprehensive observability.
6. Automate harness optimization using benchmark failures.
7. Enable continuous self-improvement of the execution harness.

Organizations that have already invested in evaluation infrastructure, trace collection, and agent observability are particularly well-positioned to adopt Levels 5–7. At this stage, the harness becomes a continuously evolving software artifact that can deliver significant quality improvements while leaving the underlying foundation model unchanged.

---

# References

## Academic Papers

1. Wei, J., et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS.
2. Yao, S., et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR.
3. Yao, S., et al. (2023). *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*. NeurIPS.
4. Shinn, N., et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*.
5. Madaan, A., et al. (2023). *Self-Refine: Iterative Refinement with Self-Feedback*.
6. Park, J., et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. ACM UIST.
7. Wang, G., et al. (2023). *Voyager: An Open-Ended Embodied Agent with Large Language Models*. arXiv.
8. Packer, C., et al. (2023). *MemGPT: Towards LLMs as Operating Systems*. arXiv.
9. Khattab, O., et al. (2023). *DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines*. arXiv.
10. SPEAR (2026). *SPEAR: Autonomous Prompt Optimization via Agentic Search*. arXiv.
11. Microsoft Research (2026). *Retrospective Harness Optimization from Agent Trajectories*. arXiv.
12. *Agentic Harness Engineering (AHE)* (2026). arXiv.

## Industry Blogs

* Anthropic Engineering Blog. *Building Effective Long-Running AI Agents*.
* LangChain Blog. *Improving Deep Agents with Harness Engineering*.
* OpenAI Engineering Blog. Articles on Codex, Agents SDK, and tool-using agents.
* Microsoft Research Blog. Articles on autonomous agents and trajectory optimization.
* Google DeepMind Blog. Research updates on Gemini agents, planning, and tool use.
