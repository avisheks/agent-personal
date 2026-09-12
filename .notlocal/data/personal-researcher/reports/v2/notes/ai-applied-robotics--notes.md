# AI Applied to Robotics: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-30 | **Read time:** ~18 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

> **Related reports:**
> - [[rl-for-llms--notes]] — RL techniques (PPO, GRPO) that underpin robot policy learning
> - [[self-improving-agents--notes]] — Self-improvement loops applicable to robotic skill acquisition
> - [[harness-engineering--notes]] — Harness optimization patterns (prompt/tool/workflow) relevant to robot orchestration

---

## Quick Catchup

> **Quick Catchup (July 2026):** LLMs and agentic AI in robotics have evolved from language-conditioned task planning (SayCan, 2022) through vision-language-action models (RT-2, 2023), open-vocabulary manipulation (VoxPoser, 2023), foundation models for robotics (Octo, 2024), to general-purpose humanoid policies trained on internet-scale data (π0, 2025-2026).
> Key players: Google DeepMind (RT-2, SayCan, Gemini Robotics), Physical Intelligence (π0), NVIDIA (GR00T), Toyota Research (Diffusion Policy), Stanford (Mobile ALOHA). Main open problem: sim-to-real transfer at scale — policies trained in simulation still degrade significantly when deployed on physical hardware.
> Recent breakthrough: π0 (Physical Intelligence, 2025) demonstrates a single vision-language-action model controlling multiple robot embodiments across diverse tasks via language instructions [1]. Trend: from task-specific controllers to general-purpose robot foundation models that understand language, perceive the world, and act.

## State of the Art

### Current Best Approaches

- **Vision-Language-Action (VLA) models** — single model takes language instruction + camera image → outputs robot actions; RT-2, π0, Octo [1][2][3]
- **LLM as task planner + low-level controller** — LLM decomposes high-level instructions into skill primitives; separate policy executes each skill (SayCan, Code as Policies) [4][5]
- **Diffusion Policy** — denoising diffusion models generate multi-modal action trajectories; handles multi-modal action distributions that regression policies cannot [6]
- **Simulation-to-real transfer** — train policies in massive simulation (Isaac Sim, MuJoCo) → transfer to physical robots with domain randomization [7]
- **Internet-scale pretraining for robotics** — leverage web-scale vision-language data (CLIP, LLaVA) as perceptual backbone, fine-tune on robot data [2][3]

### Recent Breakthroughs (last 12 months)

- **2025:** π0 (Physical Intelligence) — single VLA model controls folding, cooking, cleaning across multiple robot bodies [1]
- **2025:** Google Gemini Robotics — Gemini 2.0 directly outputs robot actions; "thinking" before acting for complex manipulation [8]
- **2025-2026:** NVIDIA GR00T — foundation model for humanoid robots; sim-trained at massive scale [9]
- **2025:** Mobile ALOHA — bimanual mobile manipulation with co-training on human demonstrations + autonomous practice [10]
- **2024:** Diffusion Policy achieves SOTA on contact-rich manipulation (cloth folding, insertion) where regression policies fail [6]

### Open Problems

- **Sim-to-real gap**: Policies trained in simulation still degrade on physical hardware due to unmodeled dynamics, sensor noise, and visual domain shift
- **Long-horizon task completion**: Current VLA models handle 10-30 step tasks; real-world tasks often require 100+ steps with error recovery
- **Safety and compliance**: Robots acting on LLM instructions must have hard physical safety constraints that language models cannot override
- **Data scarcity**: Robot interaction data is 1000x scarcer than internet text/image data; few-shot and sim-to-real approaches are critical
- **Generalization across embodiments**: Training one policy that works on different robot morphologies remains challenging despite π0's progress

### Benchmark Standings

| Benchmark | SOTA System | Score | Date |
|-----------|------------|-------|------|
| RT-2 evaluation (kitchen tasks) [2] | RT-2-X | ~75% success (novel objects) | 2023 |
| SIMPLER (simulated manip.) | Octo + fine-tune | ~60% zero-shot | 2024 |
| ALOHA bimanual tasks [10] | Mobile ALOHA co-training | ~90% (trained tasks) | 2025 |
| Calvin (language-conditioned) | 3D Diffusion Actor | ~70% (5-step chains) | 2024 |

## Executive Summary

AI applied to robotics is the use of LLMs, vision-language models, and agentic AI systems to enable robots to understand natural language instructions, perceive their environment, plan multi-step actions, and execute physical manipulation — replacing hand-coded controllers with learned, generalizable policies.

The core architectural question: **how much intelligence goes into the robot's neural policy vs. into an external LLM planner?**

- **Choose LLM-as-planner + skill primitives** (SayCan) when you have reliable low-level skills and need flexible high-level task composition
- **Choose end-to-end VLA** (RT-2, π0) when you want a single model that perceives and acts, avoiding the planner-controller interface
- **Choose Diffusion Policy** when tasks are contact-rich with multi-modal action distributions (assembly, folding, insertion)
- **Choose sim-to-real** when real-robot data is scarce and the task physics can be simulated accurately
- **Choose foundation model fine-tuning** (Octo) when you want fast adaptation to new tasks/robots from limited demonstrations

**The killer insight:** "Robotics is undergoing its 'GPT moment' — the shift from task-specific models trained on small datasets to foundation models pretrained on internet-scale data and fine-tuned on robot experience. The LLM provides the 'what to do'; the policy model provides the 'how to move.'"

```
Robot AI Architecture Spectrum
──────────────────────────────────────────────────────────────────────
Modular (LLM + controller)              End-to-end (single model)
───────────────────────────              ─────────────────────────
SayCan, Code as Policies                RT-2, π0, Gemini Robotics
LLM plans, skill executes              One model: language → action
Easy to debug, composable              Simpler deployment, emergent
Hard ceiling (skill library)            Needs massive data
```

---

## Evolutionary Stages

### Stage 1 — Language-Conditioned Task Planning (2022-2023)

**Goal:** Use LLMs to decompose natural language instructions into sequences of available robot skills.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| SayCan [4] | 2022 | LLM proposes actions; value functions ground them in physical feasibility ("I can do this") |
| Inner Monologue | 2022 | LLM receives environment feedback (success/failure) and replans — first closed-loop LLM planning for robots |
| Code as Policies [5] | 2023 | LLM writes executable code (Python) that calls robot APIs; compositional and verifiable |
| ProgPrompt | 2023 | LLM generates programmatic task plans with assertions and recovery |

**Key transition:** LLMs bridge natural language to robot actions for the first time. The key insight from SayCan: the LLM knows what's useful (language prior), the robot knows what's possible (affordance model). Combined: grounded task planning. But limited to pre-defined skill libraries — the robot can only do what it was already trained to do.

### Stage 2 — Vision-Language Models for Robotics (2023)

**Goal:** Give robots visual understanding by leveraging pretrained vision-language models (CLIP, PaLI) — enabling open-vocabulary object recognition and spatial reasoning.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| VoxPoser [11] | 2023 | LLM + vision model compose 3D value maps for manipulation; zero-shot spatial reasoning |
| CLIP-Fields | 2023 | CLIP features in 3D neural fields for open-vocabulary object detection in robot scenes |
| SQA3D | 2023 | Situated question answering in 3D scenes; grounding language in physical space |

**Key transition:** Robots gain open-vocabulary perception — they can recognize and reason about objects never seen during training, using internet-pretrained vision-language models. VoxPoser shows LLMs can reason about 3D space and generate manipulation affordances without any robot training data.

### Stage 3 — Vision-Language-Action (VLA) Models (2023-2024)

**Goal:** Train a single model that takes language + image → robot action, end-to-end.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| RT-2 [2] | 2023 | Fine-tune PaLM-E (vision-language model) to output robot actions as text tokens; transfer from web knowledge to manipulation |
| RT-2-X | 2023 | Cross-robot training: one VLA model trained on data from multiple robot platforms |
| Octo [3] | 2024 | Open-source robot foundation model; transformer policy pretrained on 800K episodes from Open X-Embodiment |
| OpenVLA | 2024 | Open-source 7B VLA (fine-tuned Llama-based); democratizes VLA research |

**Key transition:** The "GPT moment" for robotics — large pretrained models fine-tuned on robot data, enabling transfer from internet-scale knowledge to physical manipulation. RT-2 shows a PaLM-E model can generalize to novel objects and instructions it never saw during robot training, by leveraging its web pretraining. Octo provides an open-source foundation for the community.

### Stage 4 — Diffusion Policy & Action Generation (2024)

**Goal:** Generate robot action trajectories using denoising diffusion, handling multi-modal distributions that regression policies cannot.

| Paper/System | Year | Core Contribution |
|--------------|------|-------------------|
| Diffusion Policy [6] | 2023-2024 | Predicts action sequences via denoising; handles multi-modal actions (multiple valid ways to grasp) |
| 3D Diffusion Actor | 2024 | Diffusion in 3D action space with point-cloud conditioning |
| ALOHA Unleashed | 2024 | Diffusion Policy + bimanual ALOHA hardware for dexterous manipulation |

**Key transition:** Diffusion models solve a fundamental problem in robot learning: many tasks have multiple valid solutions (there are many ways to fold a towel). Regression policies average these modes, producing invalid actions. Diffusion models capture the full distribution, sampling one coherent trajectory. This enables SOTA on contact-rich tasks like folding, insertion, and bimanual coordination [6].

### Stage 5 — Simulation-Scale Training & Sim-to-Real (2024-2025)

**Goal:** Train robot policies in massively parallelized simulation, then transfer to physical robots.

| System | Year | Core Contribution |
|--------|------|-------------------|
| NVIDIA Isaac Lab [7] | 2024 | GPU-accelerated robotics simulation at 10,000+ environments in parallel |
| NVIDIA GR00T [9] | 2025 | Foundation model for humanoid robots; trained on simulation at massive scale |
| Eureka | 2024 | LLM auto-generates reward functions for sim RL; eliminates manual reward engineering |
| DrEureka | 2024 | LLM generates sim-to-real transfer configs (domain randomization parameters) |

**Key transition:** Simulation becomes the data engine for robotics. With GPU-accelerated physics (Isaac, MuJoCo MJX), you can generate millions of robot interactions per hour — equivalent to years of physical robot time. LLMs assist by designing reward functions (Eureka) and sim-to-real transfer parameters (DrEureka), automating the most manual parts of the sim-to-real pipeline.

### Stage 6 — General-Purpose Robot Foundation Models (2025-2026)

**Goal:** One model, many robots, many tasks — trained on internet-scale data and robot demonstrations, instructed via natural language.

| System | Year | Core Contribution |
|--------|------|-------------------|
| π0 (Physical Intelligence) [1] | 2025 | Single VLA model controls multiple embodiments (folding, cooking, cleaning); language-conditioned |
| Gemini Robotics [8] | 2025 | Gemini 2.0 directly outputs robot actions with "thinking" for complex reasoning about manipulation |
| GR00T N1 (NVIDIA) [9] | 2025-2026 | Humanoid foundation model: perception + planning + control in one architecture |
| 1X NEO | 2025 | Humanoid trained via learned world model for household tasks |

**Key transition:** The emergence of true robot foundation models — single models that generalize across tasks and embodiments, instructed in natural language, with emergent capabilities (novel object handling, error recovery) from internet-scale pretraining. π0 demonstrates that web-pretrained VLMs, fine-tuned on diverse robot data, produce policies that generalize in ways task-specific models cannot [1].

### Stage 7 — Agentic Robotics: Autonomous Long-Horizon Execution (2026 — Emerging)

**Goal:** Robots that autonomously plan, execute, monitor, recover from failures, and improve over extended task horizons without human intervention.

| Concept | Year | Core Contribution |
|---------|------|-------------------|
| Robot self-improvement loops | 2025-2026 | Robots practice autonomously, self-evaluate, and retrain on successful trajectories |
| LLM-based failure recovery | 2025+ | When execution fails, LLM diagnoses cause and replans (Inner Monologue extended) |
| Human-robot collaborative learning | 2025-2026 | Humans provide sparse corrections; robot generalizes via foundation model |
| Fleet learning | 2025+ | Multiple robots share experience; skills transfer across the fleet |

**Key transition:** The agentic loop comes to physical robots: Act → Observe → Reflect → Improve. Key differences from digital agents: physical safety constraints are non-negotiable (can't "undo" a dropped glass), latency requirements are tight (real-time control at 10-100Hz), and the cost of failure is physical damage rather than just a bad output.

---

## Key Themes & Connections

### Theme 1: The Data Bottleneck Drives Architecture Choices

| Data Source | Scale | Quality | How It's Used |
|-------------|-------|---------|---------------|
| Internet text/images | Trillions of tokens | High diversity, no actions | Pretrain perception + language understanding |
| Simulated robot interactions | Billions of steps (cheap) | Imperfect physics, no real-world noise | Pretrain policies; learn skills at scale |
| Teleoperation demonstrations | 100K-1M episodes (expensive) | Real-world, high quality | Fine-tune foundation models |
| Autonomous robot practice | Growing (robot generates own data) | Real-world, variable quality | Self-improvement; fill distribution gaps |

The field's central constraint: real robot data is 1000x scarcer than internet data. Every architectural choice (sim-to-real, VLA pretraining, diffusion from few demos) is a strategy to overcome this data gap.

### Theme 2: Modular vs. End-to-End — A Converging Spectrum

| Dimension | Modular (LLM + controller) | End-to-End (VLA) |
|-----------|---------------------------|-----------------|
| Architecture | LLM planner → skill primitive | Single model: image + language → action |
| Debugging | Interpretable (which step failed?) | Black box |
| Compositionality | Flexible (new skills = new primitives) | Emergent (from data) |
| Data efficiency | Low (pretrained skills) | High (needs large datasets) |
| Ceiling | Bounded by skill library | Bounded by model capacity + data |
| Production readiness (2026) | More mature | Rapidly catching up |

The frontier is converging: Gemini Robotics adds "thinking" (internal planning) to end-to-end VLA; modular systems use VLA sub-policies instead of hand-coded skills. The boundary is dissolving.

### Theme 3: The Sim-to-Real Gap Is the Central Engineering Challenge

```
Simulation (fast, cheap, safe)
 ↓ Domain randomization (visual, dynamics, sensor noise)
 ↓ Learned sim-to-real transfer (DrEureka)
 ↓ Fine-tune on small real data
 ↓
Real world (slow, expensive, fragile)
```

Every production robotics system that trains in simulation faces: (1) visual gap (rendering vs. real cameras), (2) dynamics gap (simulated vs. real physics), (3) sensor gap (noise, calibration). LLMs are now being used to automate the gap-bridging process (Eureka for rewards, DrEureka for transfer parameters).

### Theme 4: Safety Is Non-Negotiable in Physical AI

| Digital Agents | Physical Robots |
|---------------|----------------|
| Bad output → user annoyed | Bad action → physical damage/injury |
| Undo is cheap (regenerate) | Undo is impossible (broken object) |
| Latency flexible (seconds OK) | Real-time required (10-100Hz) |
| Sandbox testing easy | Physical testing expensive |
| Failure = bad text | Failure = collision, drop, crush |

This means: LLM-based planning MUST be grounded in physical feasibility models (SayCan's insight). Action outputs MUST be bounded by safety controllers. No "reward hacking" is acceptable when the reward hack results in physical harm.

### Theme 5: From Single Tasks to Household-Scale Autonomy

```
2022: Pick up the red block (one object, one action)
 → 2023: Make me a sandwich (multi-step, known objects)
  → 2024: Fold the laundry (contact-rich, deformable objects)
   → 2025: Clean the kitchen (long-horizon, multiple tools, error recovery)
    → 2026: Maintain the household (days-long autonomy, learning new skills, fleet coordination)
```

Each step increases: task horizon, object diversity, dexterity requirements, error recovery needs, and autonomy duration. The 2026 frontier (household-scale) requires all previous stages working together: foundation model perception + diffusion policy execution + LLM planning + self-improvement loops.

---

## Reading Schedule

| Week | Papers/Systems | Central Question |
|------|---------------|-----------------|
| **1** | SayCan [4], Code as Policies [5], Inner Monologue | How do LLMs plan robot actions from language? |
| **2** | VoxPoser [11], CLIP-Fields, SQA3D | How do vision-language models give robots spatial reasoning? |
| **3** | RT-2 [2], Octo [3], OpenVLA | What are VLA models and how do they generalize? |
| **4** | Diffusion Policy [6], 3D Diffusion Actor, ALOHA Unleashed | How do diffusion models solve multi-modal action generation? |
| **5** | Isaac Lab [7], Eureka, DrEureka, NVIDIA sim-to-real | How do we train at simulation scale and transfer to reality? |
| **6** | π0 [1], Gemini Robotics [8], GR00T [9] | What do general-purpose robot foundation models look like? |
| **7** | Mobile ALOHA [10], 1X NEO, fleet learning | How do robots learn from demonstrations and autonomous practice? |
| **8** | Robot self-improvement, failure recovery, safety constraints | How do agentic robots improve autonomously while remaining safe? |

---

## References

### Foundation Models for Robotics

- [1] Black et al. (2025) — *π0: A Vision-Language-Action Flow Model for General Robot Control* — Physical Intelligence — https://arxiv.org/abs/2410.24164 — Single VLA model across multiple embodiments and tasks
- [2] Brohan et al. (2023) — *RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control* — Google DeepMind — https://arxiv.org/abs/2307.15818 — Fine-tunes PaLM-E to output robot actions
- [3] Ghosh et al. (2024) — *Octo: An Open-Source Generalist Robot Policy* — https://arxiv.org/abs/2405.12213 — Open-source foundation model pretrained on Open X-Embodiment (800K episodes)

### LLM Planning for Robots

- [4] Ahn et al. (2022) — *Do As I Can, Not As I Say: Grounding Language in Robotic Affordances (SayCan)* — Google — https://arxiv.org/abs/2204.01691 — LLM proposes + affordance model grounds; first LLM-to-robot system
- [5] Liang et al. (2023) — *Code as Policies: Language Model Programs for Embodied Control* — https://arxiv.org/abs/2209.07753 — LLM writes executable code calling robot APIs

### Action Generation

- [6] Chi et al. (2024) — *Diffusion Policy: Visuomotor Policy Learning via Action Diffusion* — RSS — https://arxiv.org/abs/2303.04137 — Denoising diffusion for multi-modal robot action trajectories

### Simulation & Transfer

- [7] NVIDIA (2024) — *Isaac Lab* — GPU-accelerated robotics simulation framework for policy training at scale
- [8] Google DeepMind (2025) — *Gemini Robotics* — Gemini 2.0 directly outputs robot actions with internal reasoning
- [9] NVIDIA (2025) — *GR00T* — Foundation model for humanoid robots; simulation-scale training

### Demonstrations & Hardware

- [10] Fu et al. (2024) — *Mobile ALOHA: Learning Bimanual Mobile Manipulation with Low-Cost Whole-Body Teleoperation* — Stanford — https://arxiv.org/abs/2401.02117 — Bimanual mobile manipulation from human demonstrations

### Spatial Reasoning

- [11] Huang et al. (2023) — *VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language Models* — https://arxiv.org/abs/2307.05973 — LLM + vision compose 3D affordance maps; zero-shot manipulation

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| Start with LLM-as-planner + existing skill library (SayCan pattern) — it works TODAY with production robots and doesn't require retraining | Google Everyday Robots deployment (2022-2023) |
| Diffusion Policy outperforms behavioral cloning on any task with multiple valid solutions — if you're doing folding, insertion, or bimanual tasks, switch to diffusion | Chi et al. RSS 2024 results |
| The real bottleneck is demonstration data collection, not model architecture — invest in teleoperation infrastructure (ALOHA is $20K for bimanual setup) | Stanford Mobile ALOHA, industry consensus |
| Sim-to-real works best for locomotion and simple manipulation; degrades significantly for contact-rich tasks (deformable objects, friction-sensitive grasping) | NVIDIA GR00T deployment observations |
| Foundation models (π0, Octo) are useful for fast adaptation (10-50 demos to new task) but don't yet replace task-specific training for production reliability | Physical Intelligence, UC Berkeley evaluations |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-30 | Initial v2 generation (study-notes format) | Created from query on LLM + agentic AI applications in robotics; covers LLM planning → VLM perception → VLA models → Diffusion Policy → Sim-to-Real → Foundation Models → Agentic Robotics |
| 2026-07-30 | Filed | [UNVERIFIED] — run /verify-report --topic ai-applied-robotics when runtime available |
