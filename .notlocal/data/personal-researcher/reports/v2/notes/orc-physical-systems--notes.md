# AI (LLM + Agentic AI) for Planning & Orchestration in Physical Systems

> **Last Updated:** 2026-08-02 | **Read time:** ~20 min | **Version:** 1.0

> **Navigation**: [[#Executive Summary]] | [[#Robotics]] | [[#Autonomous Driving]] | [[#Manufacturing & Supply Chain]] | [[#Scientific Discovery]] | [[#Healthcare]] | [[#Architecture Patterns]] | [[#Key Papers]] | [[#References]]

> **Related reports:**
> - [[orc-evolution--notes]] — Full 13-phase evolution of LLM planning & orchestration (the "meta" report)
> - [[ai-applied-robotics--notes]] — Deeper dive on VLA models, diffusion policy, foundation models for robots

---

## Executive Summary

This report covers applications of AI planning and orchestration techniques — originally developed for LLM-based agentic systems — to **non-agentic domains**: robotics, autonomous driving, manufacturing, scientific discovery, and healthcare. These domains share the same planning challenges (decomposition, dependency management, replanning under uncertainty) but operate in physical environments with safety constraints, real-time requirements, and irreversible actions.

**Key insight:** The same architecture patterns (plan-execute-verify-replan, hierarchical decomposition, world-model-guided search, multi-agent coordination) that power coding agents and enterprise automation are being adapted for physical systems — but with stricter latency, safety, and reliability requirements.

**Current state (July 2026):**
- Robotics: LLMs as high-level task planners → low-level controllers execute; world models bridge the gap
- Autonomous driving: LLMs for scene understanding + planning rationale; classical planners still execute
- Manufacturing: LLM-orchestrated multi-step processes with digital twin simulation
- Scientific discovery: LLM agents plan experiments, analyze results, iterate hypotheses

---

## Robotics

### How AI Planning Applies

```
Human instruction ("make me a sandwich")
  ↓
LLM Task Planner (decomposes into subtasks)
  ↓
Skill Library (pick, place, open, pour, cut)
  ↓
Motion Planner (trajectory optimization)
  ↓
Low-Level Controller (joint torques)
  ↓
Physical Execution + Feedback
```

### Key Systems & Papers

| System | Lab | Planning Approach | Key Innovation |
|--------|-----|-------------------|----------------|
| SayCan (2022) | Google | LLM proposes; affordance model filters feasible actions | Grounds language plans in physical capability |
| Code as Policies (2023) | Google | LLM generates executable robot code directly | Bypasses skill library; code IS the plan |
| RT-2 (2023) | Google DeepMind | Vision-Language-Action model; end-to-end | Planning implicit in the model |
| TidyBot (2023) | Stanford | LLM assigns objects to locations using commonsense | Semantic planning for manipulation |
| VoxPoser (2023) | Stanford | LLM generates 3D value maps; planner follows gradients | Spatial planning without training |
| NVIDIA Cosmos + Physics (2026) | NVIDIA | Hybrid classical physics (1,300 Hz) + generative world model (60 Hz) | Safety-critical planning with simulation |
| FeelWorld (2026) | — | Visuo-tactile world model for contact prediction + planning | Multimodal world-model-guided planning |
| DC-WAM (2026) | — | Dynamics-centric world-action models for manipulation | Focus on interaction dynamics, not appearance |
| HiFi-UMI (2026) | — | High-fidelity portable data eliminates sim-to-real gap | Data quality > domain randomization |

### Planning Paradigms in Robotics

| Paradigm | How It Works | Latency | Safety |
|----------|-------------|---------|--------|
| **LLM as task planner** | LLM decomposes; skill library executes | 1-5s per plan | Medium (skill library constrains) |
| **LLM generates code** | LLM writes control code directly | 2-10s per plan | Low (unconstrained code) |
| **World-model-guided** | Simulate outcomes in learned dynamics; plan over predictions | 3-50ms (INTACT) | High (simulate before act) |
| **Hybrid classical + learned** | Physics sim for safety; learned model for diversity | Real-time | Highest (physics guarantees) |
| **End-to-end VLA** | Single model maps observation → action | 50-200ms | Depends on training distribution |

### Recent Advances (July 2026)

- **[INTACT](https://arxiv.org/abs/2607.26056):** Search-free world model planning in 2.9-5.5ms — removes MCTS overhead for real-time control
- **[Temporal-Distance JEPA](https://arxiv.org/abs/2607.25337):** Plan-aware representations unify perception and planning
- **[NVIDIA Cosmos hybrid](https://developer.nvidia.com/blog/developing-healthcare-robotics-with-gpu-native-medical-physics-simulation/):** 512 parallel RL environments at 60 Hz; Torch-Warp interop
- **[FeelWorld](https://arxiv.org/abs/2607.24267):** First visuo-tactile world model (81.7% zero-shot planning with touch)
- **[DC-WAM](https://arxiv.org/abs/2607.25918):** Dynamics-centric supervision outperforms pixel reconstruction
- **[Embodied GPT-5.1](https://arxiv.org/abs/2607.23899):** Evidence LLMs develop world-model behaviors without embodiment training

### Open Problems
- **Sim-to-real transfer:** Learned world models don't perfectly match reality
- **Long-horizon manipulation:** Planning 20+ step tasks with branching outcomes
- **Safety verification:** Proving plans won't cause harm before execution
- **Multi-robot coordination:** Scaling planning to teams of robots with shared workspaces

---

## Autonomous Driving

### How AI Planning Applies

```
Sensors (camera, lidar, radar)
  ↓
Perception (3D detection, tracking, mapping)
  ↓
Prediction (other agents' future trajectories)
  ↓
LLM-Enhanced Planning (route + behavior + trajectory)
  ↓
Control (steering, throttle, brake)
```

### The LLM Role in Driving

LLMs don't directly control the vehicle (latency too high, safety too critical) but increasingly contribute to:

| Layer | LLM Contribution | Example |
|-------|-----------------|---------|
| **Scene understanding** | Natural language reasoning about complex scenarios | "The cyclist is wobbling — they may fall" |
| **Planning rationale** | Explain why a behavior is chosen (for debugging/audit) | "Yielding because pedestrian has right of way" |
| **Edge case handling** | Commonsense reasoning for rare situations | "Construction zone with human flaggers — follow hand signals" |
| **Scenario generation** | Generate test scenarios in natural language → simulation | "Create a scenario where a child chases a ball into the street" |
| **Knowledge retrieval** | Retrieve relevant traffic rules, local regulations | Region-specific driving norms |

### Key Systems

| System | Approach | Planning Innovation |
|--------|----------|---------------------|
| DriveGPT4 (2024) | Multimodal LLM for driving explanation | Interpretable planning rationale |
| LMDrive (2024) | LLM-based end-to-end driving with language commands | Natural language as planning interface |
| GPT-Driver (2023) | LLM as motion planner (chain-of-thought trajectory) | CoT reasoning for trajectory generation |
| DiLu (2024) | Dual-process: System 1 (fast, habitual) + System 2 (LLM reasoning for novel) | Cognitive architecture for driving |
| NVIDIA DriveOS | Classical planner with LLM-based scenario analysis | Safety-critical hybrid |
| Wayve GAIA-1 (2023) | Video world model for driving simulation | Learned dynamics for planning validation |

### Architecture Pattern: Safety-Critical Hybrid

```
┌────────────────────────────────────────────────┐
│ LLM Layer (non-safety-critical)                │
│  - Scene interpretation                        │
│  - Behavior suggestion                         │
│  - Scenario reasoning                          │
└──────────────────┬─────────────────────────────┘
                   │ Suggestions (not commands)
                   ▼
┌────────────────────────────────────────────────┐
│ Classical Planner (safety-critical)            │
│  - Trajectory optimization                     │
│  - Constraint satisfaction                     │
│  - Safety envelope enforcement                 │
└──────────────────┬─────────────────────────────┘
                   │ Verified trajectory
                   ▼
┌────────────────────────────────────────────────┐
│ Controller (real-time, deterministic)          │
│  - PID / MPC                                  │
│  - Hardware safety layer                       │
└────────────────────────────────────────────────┘
```

**Key principle:** LLMs SUGGEST; classical systems DECIDE and EXECUTE. The LLM is advisory, not authoritative, in safety-critical physical systems.

### Open Problems
- **Latency:** LLM inference too slow for reactive driving (need <50ms)
- **Verification:** Cannot formally verify LLM-generated plans
- **Corner cases:** LLMs hallucinate; hallucinated driving plans are lethal
- **Liability:** Who is responsible when an LLM-suggested plan causes an accident?

---

## Manufacturing & Supply Chain

### How AI Planning Applies

```
Production order
  ↓
LLM Planner (sequences operations, assigns machines, schedules)
  ↓
Digital Twin (simulates plan before execution)
  ↓
PLC / Robot Controller (executes verified plan)
  ↓
Quality inspection + feedback → replan if needed
```

### Applications

| Application | Planning Challenge | AI Approach |
|-------------|-------------------|-------------|
| **Job shop scheduling** | Sequence N jobs across M machines minimizing makespan | LLM generates initial schedule; RL optimizes; world model simulates |
| **Assembly planning** | Order of operations for complex products | LLM decomposes from CAD; precedence graph generation |
| **Supply chain orchestration** | Multi-tier coordination under demand uncertainty | LLM agents per tier; central orchestrator manages dependencies |
| **Predictive maintenance** | Schedule maintenance to minimize downtime | World model predicts failure; planner schedules intervention |
| **Quality control** | Route defective items for rework/scrap | LLM classifies defect → plans corrective action |
| **Warehouse automation** | Multi-robot pick/pack/ship coordination | Multi-agent planning with collision avoidance |

### Digital Twin as World Model

The manufacturing digital twin IS a world model — it predicts future states of the production system given actions. LLMs orchestrate queries to the digital twin:

```
LLM: "What happens if we move Job B ahead of Job A on Machine 3?"
Digital Twin: [simulates] → "Makespan increases by 4 hours; Machine 5 becomes bottleneck"
LLM: "What about splitting Job B across Machines 3 and 4?"
Digital Twin: [simulates] → "Makespan decreases by 2 hours; quality risk on split boundary"
LLM: [selects best plan based on multi-objective criteria]
```

---

## Scientific Discovery

### How AI Planning Applies

```
Hypothesis
  ↓
LLM Agent plans experiments (what to test, in what order, with what controls)
  ↓
Lab automation executes (liquid handlers, sequencers, microscopes)
  ↓
LLM Agent analyzes results
  ↓
Update hypothesis → replan next experiments
```

### Key Systems

| System | Domain | Planning Innovation |
|--------|--------|---------------------|
| Coscientist (2024) | Chemistry | Multi-agent system plans and executes chemical synthesis autonomously |
| ChemCrow (2024) | Chemistry | LLM with chemistry tools plans reaction sequences |
| BioPlanner (2023) | Biology | LLM generates experimental protocols from papers |
| NVIDIA Genesis Mission (2026) | Scientific imaging | SAM 3 + DINOv3 on 300 A100s; automated annotation pipeline |
| Xaira X-Cell (2026) | Drug discovery | CRISPR-based causal data generation; world model for cell behavior |

### The Planning Pattern for Scientific Discovery

```
1. Literature review (RAG over papers) → identify gaps
2. Hypothesis generation (LLM reasoning) → candidate hypotheses
3. Experiment design (LLM planning) → protocol with controls
4. Resource allocation (orchestrator) → schedule equipment, reagents
5. Execution (lab automation) → run experiment
6. Analysis (LLM + statistical models) → interpret results
7. Update world model → revise understanding
8. Replan → next experiment targeting remaining uncertainty
```

This is the **Plan-Execute-Observe-Replan** pattern from agentic AI applied to physical experiments. Key difference: experiments are expensive and slow (hours to weeks), so planning quality matters enormously.

---

## Healthcare

### Applications of AI Planning

| Application | Planning Challenge | Approach |
|-------------|-------------------|----------|
| **Treatment planning** | Sequence therapies; manage drug interactions; adapt to response | LLM reasons over guidelines + patient history; physician approves |
| **Surgical planning** | Sequence of incisions, instrument changes, tissue manipulation | World model of anatomy; [NVIDIA Cosmos for surgical simulation](https://developer.nvidia.com/blog/developing-healthcare-robotics-with-gpu-native-medical-physics-simulation/) |
| **Clinical trials** | Patient recruitment, protocol adherence, adaptive design | Multi-agent orchestration of trial sites |
| **Hospital operations** | OR scheduling, bed management, staff allocation | Combinatorial optimization + LLM for exception handling |
| **Rehabilitation** | Progressive exercise plans adapted to patient recovery | World model of recovery trajectory; replan based on progress |

### Safety Pattern: Human-in-the-Loop Planning

In healthcare, AI plans are NEVER executed without human approval:

```
AI Planner generates options → Clinician reviews → Clinician selects/modifies → System executes
```

This is the same pattern as [COVENANT](https://arxiv.org/abs/2607.25400) (SOP-as-code) applied to clinical protocols: the AI must follow the documented process, with explicit approval gates before irreversible actions.

---

## Cross-Domain Architecture Patterns

### Pattern: Safety-Critical Hybrid (Most Common in Physical Systems)

```
┌─────────────────────┐     ┌─────────────────────┐
│ LLM / Agent Layer   │     │ World Model         │
│ (non-real-time)     │◄───►│ (simulation)        │
│ - Task planning     │     │ - Predict outcomes  │
│ - Reasoning         │     │ - Verify safety     │
│ - Exception handling│     │ - Generate options  │
└────────┬────────────┘     └─────────────────────┘
         │ Verified plan
         ▼
┌─────────────────────┐
│ Classical Planner   │
│ (real-time, safe)   │
│ - Trajectory opt    │
│ - Constraint check  │
│ - Safety envelope   │
└────────┬────────────┘
         │ Executable commands
         ▼
┌─────────────────────┐
│ Physical Controller │
│ (deterministic)     │
│ - PID / MPC        │
│ - Hardware safety   │
└─────────────────────┘
```

### Pattern: Digital Twin Loop

```
Real World ──sensors──► Perception ──state──► Digital Twin
                                                   │
                                              simulate
                                                   │
                                                   ▼
LLM Planner ◄──outcomes── Digital Twin ──validate──► Plan OK?
     │                                                  │
     │ Yes                                             No
     ▼                                                  │
Execute in Real World                           Replan ─┘
```

### Pattern: Hierarchical Physical Planning

```
Level 1: Strategic (LLM)     "Build a house"           [hours-days planning horizon]
Level 2: Tactical (Planner)  "Pour foundation first"    [minutes-hours]
Level 3: Operational (MPC)   "Move arm to position X"   [milliseconds-seconds]
Level 4: Reactive (PID)      "Maintain force at 5N"     [microseconds]
```

Each level operates at a different timescale. LLMs operate at Level 1-2 (strategic/tactical); real-time controllers handle Level 3-4. The interface between levels is the key design challenge.

---

## Comparison: Agentic vs Non-Agentic Planning

| Dimension | Agentic (Software) | Non-Agentic (Physical) |
|-----------|--------------------|-----------------------|
| **Reversibility** | Usually reversible (git revert, undo) | Often irreversible (cut metal, inject drug) |
| **Latency** | Seconds acceptable | Milliseconds required |
| **Safety** | Data loss, wrong output | Physical harm, death |
| **Verification** | Run tests, check output | Cannot test in reality; must simulate |
| **Cost of failure** | Retry cheaply | Expensive (damaged equipment, wasted materials) |
| **World model** | Optional (can explore) | Essential (must predict before acting) |
| **Human oversight** | Optional in low-stakes | Mandatory in most domains |
| **Planning horizon** | Minutes to hours | Milliseconds to months |
| **Environment** | Deterministic (computers) | Stochastic (physics) |

**Key insight:** Physical systems REQUIRE world models. In software agents, you can afford to try-and-fail. In robotics/driving/healthcare, you simulate-then-act. This is why world model research (JEPA, Dreamer, Cosmos) is critical for non-agentic applications.

---

## Key Papers (2026)

| Paper | Domain | Planning Contribution |
|-------|--------|----------------------|
| [INTACT](https://arxiv.org/abs/2607.26056) | Robotics | Search-free world model planning (2.9ms) |
| [Temporal-Distance JEPA](https://arxiv.org/abs/2607.25337) | Robotics | Plan-aware representation learning |
| [NVIDIA Cosmos + Physics](https://developer.nvidia.com/blog/developing-healthcare-robotics-with-gpu-native-medical-physics-simulation/) | Healthcare Robotics | Hybrid classical + generative (512 envs @ 60Hz) |
| [FeelWorld](https://arxiv.org/abs/2607.24267) | Manipulation | Visuo-tactile world model planning (81.7%) |
| [DC-WAM](https://arxiv.org/abs/2607.25918) | Manipulation | Dynamics > appearance for control |
| [False Prophets](https://arxiv.org/abs/2607.23147) | All physical systems | Security risks of world models in deployment |
| [Persistent Computational State](https://arxiv.org/abs/2607.21686) | Infrastructure | World model serving (1,024 sessions) |
| [Wonder](https://arxiv.org/abs/2607.26037) | Simulation/Preview | Video world model at 16 FPS |
| [HiFi-UMI](https://arxiv.org/abs/2607.25895) | Robotics | Data quality eliminates sim-to-real gap |
| [Embodied GPT-5.1](https://arxiv.org/abs/2607.23899) | Robotics | LLMs develop world-model behaviors without embodiment |

---

## References

### Robotics Planning with LLMs
- Ahn et al. (2022) — *SayCan: Do As I Can, Not As I Say* — Grounding language in robot affordances
- Liang et al. (2023) — *Code as Policies* — LLM generates executable robot control code
- Brohan et al. (2023) — *RT-2: Vision-Language-Action Models* — End-to-end robotic control
- Huang et al. (2023) — *VoxPoser: Composable 3D Value Maps for Robotic Manipulation* — Spatial planning

### Autonomous Driving with LLMs
- Mao et al. (2023) — *GPT-Driver: Learning to Drive with GPT* — CoT trajectory planning
- Wen et al. (2024) — *DiLu: A Knowledge-Driven Approach to Autonomous Driving* — Dual-process cognitive architecture
- Sha et al. (2024) — *LMDrive: Closed-Loop End-to-End Driving with Language* — Language-conditioned driving

### World Models for Planning
- Hafner et al. (2023) — *DreamerV3: Mastering Diverse Domains through World Models* — General model-based RL
- Ha & Schmidhuber (2018) — *World Models* — Original world model paper for planning
- LeCun (2022) — *A Path Towards Autonomous Machine Intelligence* — JEPA architecture proposal

### Manufacturing & Scientific Discovery
- Boiko et al. (2023) — *Coscientist: Autonomous Chemical Research with LLMs* — Multi-agent lab automation
- M. Bran et al. (2024) — *ChemCrow: Augmenting LLMs with Chemistry Tools* — Tool-using chemistry agent

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-30 | Initial creation | User request: AI planning/orchestration for non-agentic applications (robotics, autonomous driving) |
