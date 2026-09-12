# Multi-Teacher Online Policy Distillation: Evolution & Reading Roadmap

> **Last Updated:** 2026-07-29 | **Read time:** ~16 min | **Version:** 2.0

> **Navigation**: [[#Quick Catchup]] | [[#State of the Art]] | [[#Executive Summary]] | [[#Evolutionary Stages]] | [[#Key Themes & Connections]] | [[#Reading Schedule]] | [[#References]]

---

## Quick Catchup

> **Quick Catchup (July 2026):** Model merging has evolved from simple weight averaging (Model Soups, 2022) through task arithmetic and TIES/DARE (2023) to behavior-space approaches like Multi-Teacher Online Policy Distillation (MT-OPD), which trains a student by interacting with specialist teachers rather than averaging parameters.
> Key players: Wortsman et al. (Model Soups), Ilharco et al. (Task Arithmetic), Yadav et al. (TIES), Meta (Llama post-training), DeepMind (policy distillation from AlphaGo onward). Main open problem: teacher conflict resolution — when specialist teachers disagree, the student learns a blurry average that satisfies none.
> Recent breakthrough: Multi-teacher OPD enables architecture-agnostic merging (combine Qwen + Llama + Claude behaviors into one student) — impossible with weight-space methods. Trend: from parameter-space merging to behavior-space merging to adaptive policy composition with learned routing.

## State of the Art

### Current Best Approaches

- **Model Soups** [1] — average weights of multiple fine-tuned checkpoints from the same base; cheap, improves robustness when checkpoints are close in parameter space
- **Task Arithmetic** [2] — add/subtract task vectors (weight deltas) to compose capabilities; simple but sensitive to interference
- **TIES / DARE** [3] — resolve parameter conflicts via trimming, sign election, and rescaling; better than naive averaging but still weight-space bound
- **MoE Composition** — preserve specialist expertise via mixture-of-experts routing; maintains quality but increases inference cost
- **Multi-Teacher Online Policy Distillation (MT-OPD)** — train a student by routing prompts to specialist teachers, scoring responses, and updating the student on the best policy; architecture-agnostic but expensive [4]

### Recent Breakthroughs (last 12 months)

- **2025-2026:** Frontier labs (OpenAI, Anthropic, DeepMind) converge on iterative distillation + preference optimization pipelines that implicitly perform behavior-space merging without calling it "merging"
- **2026:** Multi-teacher OPD demonstrated with heterogeneous architectures — combining outputs from models of different families (Qwen, Llama, DeepSeek) into a unified student
- **2026:** Adaptive policy composition research shows students can learn "which teacher to trust under which conditions" via uncertainty estimates and task classification

### Open Problems

- **Teacher conflict resolution**: Contradictory policies (concise vs. verbose, reveal CoT vs. hide CoT) produce blurry averages that satisfy no use case
- **Policy collapse / mode collapse**: Student imitates whichever teacher dominates the training distribution; minority capabilities vanish
- **Capacity bottleneck**: A 7B student cannot faithfully absorb four 70B experts — knowledge interference becomes inevitable
- **Safety inconsistency**: Different teachers encode different refusal styles, alignment policies, and tool permissions → student inherits fuzzy safety behavior
- **Computational cost**: Online distillation requires N teacher inference calls per prompt — much more expensive than offline SFT

## Executive Summary

Multi-Teacher Online Policy Distillation (MT-OPD) is a model merging paradigm that consolidates capabilities from multiple specialist models by training a student on their *behaviors* rather than averaging their *parameters*. This is behavior-space merging vs. parameter-space merging.

The core architectural question: **should you merge in weight space (cheap, fast, architecture-dependent) or behavior space (expensive, flexible, architecture-independent)?**

- **Choose weight averaging (Model Soups)** when checkpoints are close in parameter space (same base, similar tasks)
- **Choose TIES/DARE** when tasks are complementary but interference is a concern
- **Choose MoE composition** when you need preserved specialist quality and can afford larger inference
- **Choose MT-OPD** when teachers are heterogeneous architectures, new specialists arrive frequently, and you need a single deployable model
- **Choose mixed-dataset SFT** as the simplest strong baseline — merge the training data, not the models

**The killer insight:** "Weight merging asks 'how do I average these parameters?' — MT-OPD asks 'how do I learn the best behavior from all teachers?' The second question is harder but more powerful: it crosses architectures, resolves conflicts through routing, and supports continual integration."

```
Model Merging Spectrum
──────────────────────────────────────────────────────────────────
Parameter space                                    Behavior space
(weight-centric)                                   (policy-centric)
──────────────────                                 ──────────────────
Model Soups  Task Arith  TIES/DARE  MoE    Mixed-SFT    MT-OPD
   │              │          │        │         │           │
Cheapest      Simple     Better     Keeps    Retrain     Most
One-shot      Linear     conflict   experts  on merged   expensive
Same arch     Same arch  Same arch  Same     Same arch   Any arch
              only       only       arch     (data only)  (behavior)
```

---

## Evolutionary Stages

### Stage 1 — Weight Averaging / Model Soups (2022)

**Goal:** Combine multiple fine-tuned checkpoints without retraining.

| Paper/Method | Year | Core Contribution |
|--------------|------|-------------------|
| Model Soups [1] | 2022 | Average weights of multiple fine-tuned models from same base; improves robustness and OOD accuracy |
| Uniform soup | 2022 | Simple `W_soup = (1/N) Σ W_i`; works when checkpoints are close in loss landscape |
| Greedy soup | 2022 | Iteratively add checkpoints only if they improve validation accuracy |

**Key transition:** Established that you CAN merge model weights and get improvements — but only when checkpoints share the same base model and remain close in parameter space. Fails catastrophically for models trained on very different tasks.

### Stage 2 — Task Arithmetic (2023)

**Goal:** Compose capabilities by adding/subtracting task vectors (weight deltas from the base model).

| Paper/Method | Year | Core Contribution |
|--------------|------|-------------------|
| Task Arithmetic [2] | 2023 | Task vector = fine-tuned weights - base weights. Add vectors to compose skills; negate to remove behaviors |
| Linear mode connectivity | 2023 | Theoretical justification: fine-tuned models connected by low-loss paths enable interpolation |

**Key transition:** Weight merging becomes composable — you can add "coding ability" and subtract "verbosity" using arithmetic on task vectors. But interference between tasks remains: adding two task vectors can degrade both capabilities.

### Stage 3 — Conflict Resolution in Weight Space (2023-2024)

**Goal:** Handle the interference problem — when task vectors conflict, resolve gracefully.

| Paper/Method | Year | Core Contribution |
|--------------|------|-------------------|
| TIES [3] | 2023 | Trim small-magnitude changes, resolve sign conflicts by election, merge only agreed-upon directions |
| DARE | 2023 | Randomly drop delta parameters + rescale; reduces interference through sparsification |
| DARE + TIES | 2024 | Combine both: drop → trim → sign-elect → merge. Current best weight-space method |

**Key transition:** Weight-space merging becomes more robust through principled conflict resolution. But all methods remain architecture-dependent (same base model required) and one-shot (no continual updates).

### Stage 4 — Mixture-of-Experts Composition (2023-2024)

**Goal:** Preserve specialist expertise without averaging away capabilities.

| System/Method | Year | Core Contribution |
|---------------|------|-------------------|
| MoE routing | 2023+ | Each expert handles its domain; router selects which expert processes each input |
| Branch-Train-Merge | 2023 | Train domain experts separately, compose via routing layer |
| MoLoRA | 2024 | Multiple LoRA adapters with learned routing — lightweight specialist composition |

**Key transition:** Instead of merging INTO one model, keep specialists separate and route dynamically. Preserves quality but requires all experts deployed simultaneously (memory cost) and adds routing complexity.

### Stage 5 — Mixed-Dataset SFT (Baseline That Works) (2022-2024)

**Goal:** Merge the training DATA rather than the model weights, then retrain.

| Approach | Year | Core Contribution |
|----------|------|-------------------|
| Multi-task SFT | 2022+ | Combine training datasets from all specialists, train one model on the mixture |
| Balanced sampling | 2023+ | Control task mix via dataset ratios to prevent dominant-task bias |

**Key transition:** Often the strongest simple baseline. Produces a unified representation (no weight conflicts) and generalizes well for complementary tasks. Requires retraining (more compute than weight merging) but avoids the fundamental incompatibility problems. Closer to how production models are actually trained.

### Stage 6 — Offline Policy Learning: Learning from Logs (2017-2024)

**Goal:** Learn a decision policy entirely from historical interaction logs, without collecting new online feedback during training.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Swaminathan et al. [9] | 2017 | Off-policy evaluation for slate recommendation — OPE foundations for ranking/slates |
| Zhao et al. [10] | 2018 | Deep RL for sponsored search real-time bidding — ads/bidding as sequential offline RL |
| Kumar et al. (CQL) [11] | 2020 | Conservative Q-Learning — penalizes OOD actions to prevent extrapolation error |
| Kidambi et al. (MOReL) [12] | 2020 | Model-based offline RL — learns pessimistic MDP from offline data |
| Sachdeva et al. [13] | 2020 | Off-policy bandits with deficient support — when logging policy doesn't explore enough |
| Saito et al. [14] | 2021 | Open Bandit Dataset & Pipeline — reproducible offline policy evaluation benchmark |
| Zhang et al. [15] | 2023 | Unified off-policy learning-to-rank as MDP — connects counterfactual LTR with offline RL |
| Chen et al. [16] | 2023 | Adversarial counterfactual environment model learning — addresses bias in learned world models |

**Key transition:** Offline policy learning solves "how to improve a policy from historical data without live experimentation." This is the precursor to online policy distillation — if MT-OPD asks "learn from teacher behaviors in real time," offline PL asks "learn from historical behavior logs after the fact." The core challenge is **distribution shift**: the learned policy may select actions unseen in logs, causing extrapolation error.

#### Offline Policy Learning Hierarchy

```
Historical interaction logs
        │
        ▼
┌───────────────────────────────┐
│ 1. Off-Policy Evaluation (OPE)│  "Would policy π work?"
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 2. Counterfactual Policy      │  "Learn a better π from logs"
│    Learning (OPL)             │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 3. Offline RL                 │  "Learn sequential policy with
│                               │   long-term rewards"
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 4. Model-Based Offline RL /   │  "Learn how the environment
│    World Model                │   responds to actions"
└───────────────────────────────┘
```

#### Applications to Search & Advertising

| Domain | State | Action | Offline PL Application |
|--------|-------|--------|----------------------|
| Search ranking | Query + user context | Ranked list | Learn better ranker from click logs, correcting for position bias [15] |
| Ad bidding | Campaign state + budget | Bid amount | Learn bidding policy from spend/conversion logs without risking budget [10] |
| Ad selection | Eligible ads + context | Ad ranking | Counterfactual "what-if" evaluation of different selection policies [14] |
| Campaign optimization | Advertiser + market state | Budget/audience/keyword actions | Sequential offline RL with world model for long-horizon strategy [12][16] |

**Key insight:** The hardest problem in offline PL is not "which algorithm?" but "does the historical data contain enough evidence?" If the logging policy never explored an action, no offline method can reliably evaluate it. This **support deficiency** problem [13] is why offline PL naturally leads to online approaches (MT-OPD) when live experimentation becomes affordable.

### Stage 7 — Online Policy Distillation: Learning from the Student's Own Mistakes (2024-2026)

**Goal:** Let the student generate its own trajectories, then have a stronger teacher provide dense, step-level guidance on the student's actual behavior — correcting mistakes where they happen.

| Paper | Year | Core Contribution |
|-------|------|-------------------|
| Agarwal et al. (GKD) [19] | 2024 | *On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes* — ICLR — foundational LLM OPD; addresses train-test distribution mismatch by distilling on student-generated outputs |
| Czarnecki et al. [20] | 2019 | *Distilling Policy Distillation* — AISTATS — theoretical background on policy distillation objectives and KL-based losses |
| Zhang et al. [21] | 2026 | *Fast and Effective On-Policy Distillation from Reasoning Prefixes* — ACL Findings — reduces OPD cost by focusing teacher guidance on reasoning prefixes only |
| Jang et al. [22] | 2026 | *Stable On-Policy Distillation through Adaptive Target Reformulation* — ACL Findings — addresses OPD instability when teacher/student distributions diverge |

**Key transition:** OPD solves the **train-test distribution mismatch** inherent in offline distillation. Standard KD trains the student on teacher-generated outputs, but the student deploys on its own distribution — mistakes compound because the student never practiced recovering from its own errors. OPD flips this: `τ ~ π_student`, then optimize student to match teacher on the visited states/tokens via KL-based objective [19].

#### OPD vs. Other Training Methods

| Method | Training data | Feedback | Distribution Match |
|--------|--------------|----------|-------------------|
| SFT | Human/teacher demonstrations | Correct answer | Teacher distribution (mismatch at deployment) |
| Offline KD | Teacher-generated trajectories | Teacher distribution | Teacher distribution (mismatch) |
| RL | Student trajectories | Sparse reward (end of trajectory) | Student distribution (matched) ✓ |
| **OPD** | **Student's own trajectories** | **Dense teacher guidance at each step/token** | **Student distribution (matched) ✓** |

#### Core Benefit: Dense Credit Assignment

If a student makes a bad decision at step 7 of a 50-step trajectory:
- **RL** provides only a final scalar reward after the full trajectory — which step caused the failure?
- **OPD** provides dense teacher signal *at step 7* — directly correcting the mistake where it happened

#### Applications to Search & Advertising

| Application | Teacher | Student | Trajectory | OPD Advantage |
|-------------|---------|---------|-----------|---------------|
| Search-agent distillation | Large agent (query reformulation + retrieval + synthesis) | Smaller production model | query → results → reformulation → retrieval | Teaches recovery from poor queries on student's own search paths |
| Ad campaign strategy | Expensive multi-agent policy | Low-latency production model | goal → budget → audience → bid → creative | Corrects student's own intermediate decisions step-by-step |
| Behavior preservation after domain adaptation | Pre-adaptation model | Post-adaptation model | Normal operation trajectories | Recovers capabilities lost during domain mid-training |
| Multi-teacher specialist → single model | Multiple domain experts | Unified model | Domain-specific task trajectories | Each specialist corrects student in their domain |

#### Key Challenge: Instability

OPD becomes unstable when teacher and student distributions are far apart — the KL objective can have high variance when the student generates outputs the teacher considers very unlikely. Active research addresses this via trust-region methods [22] and prefix-focused distillation [21].

### Stage 8 — Multi-Teacher Online Policy Distillation (2024-2026)

**Goal:** Train a student by learning from multiple specialist teachers' behaviors — not their weights.

| Concept | Year | Core Contribution |
|---------|------|-------------------|
| MT-OPD [4] | 2024-2026 | Route prompts to specialist teachers → collect responses → score → select/aggregate best policy → update student. Behavior-space merging. |
| Competence-aware routing | 2025+ | Route each prompt to the teacher with highest expected competence, avoiding wasted capacity on poor-domain outputs |
| Heterogeneous distillation | 2025+ | Distill from teachers of different architectures (Qwen, Llama, DeepSeek, Claude) into one student |

**Key transition:** Merging moves entirely from parameter space to behavior space. The student never sees teacher weights — only their outputs. This enables: (1) cross-architecture merging, (2) continual integration (add new teachers anytime), (3) conflict resolution through routing rather than averaging. But at 10x+ the compute cost of weight merging.

#### MT-OPD Pipeline

```
For each prompt:
 ↓
Route to relevant teacher(s)
 ↓
Collect teacher responses
 ↓
Score responses (reward model / verifier / preference)
 ↓
Select or aggregate best policy signal
 ↓
Update student (SFT on best response, or DPO on ranked pairs)
 ↓
Repeat
```

### Stage 9 — Adaptive Policy Composition (Emerging Research)

**Goal:** The student learns WHEN to trust WHICH teacher, using uncertainty and task classification.

| Concept | Year | Core Contribution |
|---------|------|-------------------|
| Learned routing | 2026 | Student develops an internal meta-policy for teacher selection based on input characteristics |
| Uncertainty-weighted distillation | 2025+ | Weight teacher influence by confidence/calibration; ignore teachers on out-of-domain inputs |
| Continual replay | 2026 | Periodically replay previously distilled skills to prevent catastrophic forgetting |

**Key transition:** MT-OPD evolves from "copy all teachers equally" to "learn conditional competence" — the student infers which teacher to imitate based on task type, difficulty, and domain. This unifies MoE routing, continual learning, online RL, and policy distillation into one framework. No publicly documented end-to-end system from a frontier lab fully realizes this architecture yet — making it a promising research direction.

---

## Key Themes & Connections

### Theme 1: Parameter Space vs. Behavior Space — A Fundamental Design Choice

| Dimension | Parameter-Space Merging | Behavior-Space Merging (MT-OPD) |
|-----------|------------------------|--------------------------------|
| What's merged | Weight matrices | Output distributions / behaviors |
| Architecture requirement | Same base model | Any architecture (heterogeneous OK) |
| Compute cost | Negligible (one-shot average) | High (N teacher inferences per prompt) |
| Continual updates | Requires full re-merge | Just add new teacher |
| Conflict resolution | Statistical (trim, elect, sparsify) | Learned (routing, scoring, selection) |
| Capacity limit | Bounded by parameter count | Bounded by student capacity to absorb |
| Production adoption | Low (too brittle for production) | High (how frontier labs actually consolidate) |

### Theme 2: Frontier Labs Are Already Doing Implicit MT-OPD

No frontier lab calls their approach "multi-teacher online policy distillation," but their post-training pipelines are functionally equivalent:

| Lab | What They Do | How It Maps to MT-OPD |
|-----|-------------|----------------------|
| OpenAI | Synthetic data from specialists → preference optimization → iterative distillation | Teacher = specialist generator; scoring = preference model; update = DPO/PPO |
| Anthropic | Constitutional AI → self-critique → RLAIF → iterative refinement | Teacher = self-critique (model-as-teacher); scoring = constitutional principles |
| DeepMind | AlphaGo → AlphaZero distillation; Gemini multi-task training | Explicit policy distillation heritage; joint training = implicit multi-teacher |
| Meta | DPO + SFT + continual pretraining + synthetic instructions | Mixed-dataset SFT + preference optimization = simplified MT-OPD |

The convergence: all labs consolidate many skills/teachers into one deployed model using iterative behavior-based training rather than weight merging.

### Theme 3: The Ten Risks of MT-OPD

| Risk | Description | Mitigation |
|------|-------------|-----------|
| Teacher conflicts | Contradictory policies (concise vs. verbose) | Competence-aware routing; domain-specific prompts |
| Policy collapse | Dominant teacher drowns out minority skills | Balanced sampling; skill-specific evaluation gates |
| Catastrophic forgetting | New teachers erase old capabilities | Continual replay; periodic evaluation across all domains |
| Teacher quality mismatch | Weak teachers inject bad habits | Confidence-weighted scoring; minimum quality threshold |
| Distribution mismatch | Teachers produce garbage outside their domain | Route only in-domain prompts to each teacher |
| Reasoning style averaging | Step-by-step + implicit + tree-search → blurry mix | Style-specific routing; don't mix incompatible reasoning |
| Capacity bottleneck | Small student can't absorb large teacher ensemble | Match student size to task complexity; staged distillation |
| Safety inconsistency | Different refusal/permission policies across teachers | Unified safety constitution applied post-merge |
| Reward hacking | Student optimizes for teacher preference, not task quality | Diverse reward signals; held-out evaluation |
| Computational cost | N teacher calls per prompt | Batch efficiently; cache teacher responses; use offline + online hybrid |

### Theme 4: Offline → Online Policy Learning Spectrum

The field spans a continuum from fully offline (learn from logs) to fully online (learn from live teacher interactions):

| Approach | Data Source | Counterfactual Problem | Compute Cost | Risk |
|----------|-------------|----------------------|-------------|------|
| Off-Policy Evaluation (OPE) | Historical logs | "Would this policy work?" | Low | Can't evaluate unseen actions |
| Offline Policy Learning | Historical logs | "Learn better policy from logs" | Medium | Distribution shift / OOD actions |
| Offline RL | Sequential logs | "Optimize long-term from logs" | Medium-High | Extrapolation error compounds over steps |
| World-Model Offline RL | Logs + learned dynamics | "Simulate before acting" | High | Model bias under behavior-policy selection |
| MT-OPD (online) | Live teacher responses | "Learn from teacher behaviors now" | Very High | Teacher conflicts, capacity limits |

**Key insight for Search/Ads:** The hard research problem is not "which algorithm?" but "can we build a sufficiently faithful counterfactual model of user/market response?" If historical data doesn't cover an action, no offline method can reliably evaluate it — this support deficiency [13] is why online approaches (MT-OPD) become necessary when you can afford the compute.

### Theme 5: When to Use Which Merging Strategy

```
Decision Tree:
────────────────
Are teachers the same architecture + same base model?
 ├── YES: Are they trained on similar/complementary tasks?
 │    ├── YES → Model Soups / TIES (cheapest, good enough)
 │    └── NO → Mixed-dataset SFT (retrain on combined data)
 │
 └── NO (different architectures / vendors):
      ├── Can you afford N× inference during training?
      │    ├── YES → MT-OPD (most flexible, best long-term)
      │    └── NO → MoE / retrieval-augmented routing (keep experts separate)
      │
      └── Do you need continual updates as new experts arrive?
           ├── YES → MT-OPD (just add new teacher)
           └── NO → One-time mixed-dataset SFT
```

---

## Reading Schedule

| Week | Papers/Concepts | Central Question |
|------|----------------|-----------------|
| **1** | Model Soups [1], linear mode connectivity | Can we merge model weights and get improvements? When does it work? |
| **2** | Task Arithmetic [2], task vectors, negation/addition | How do we compose/remove capabilities via weight arithmetic? |
| **3** | TIES [3], DARE, DARE+TIES | How do we resolve conflicts when merging incompatible weight deltas? |
| **4** | MoE composition, Branch-Train-Merge, MoLoRA | What if we route instead of merge — keeping experts separate? |
| **5** | Mixed-dataset SFT, multi-task training, balanced sampling | Is the simplest approach (merge data, retrain) actually the best baseline? |
| **6** | CQL [11], MOReL [12], Sachdeva [13], Open Bandit [14] | How do you learn a policy from historical logs without live experimentation? |
| **7** | Swaminathan [9], Zhang [15], Chen [16] | How does offline policy learning apply to search ranking and advertising? |
| **8** | Knowledge distillation basics, Czarnecki [20], policy distillation (AlphaGo → AlphaZero) | How does distillation work, and what are the theoretical foundations? |
| **9** | GKD / Agarwal [19], Zhang [21], Jang [22] | How does OPD fix distribution mismatch by distilling on student-generated trajectories? |
| **10** | MT-OPD architecture, competence-aware routing, heterogeneous distillation | How do you train a student from multiple teacher behaviors across architectures? |
| **11** | Adaptive policy composition, continual learning, uncertainty-weighted routing | What's the frontier — learned routing, continual replay, unified frameworks? |

---

## References

### Weight-Space Merging

- [1] Wortsman et al. (2022) — *Model Soups: Averaging Weights of Multiple Fine-tuned Models Improves Accuracy without Increasing Inference Time* — ICML — Simple weight averaging improves robustness
- [2] Ilharco et al. (2023) — *Editing Models with Task Arithmetic* — ICLR — Add/subtract task vectors to compose capabilities
- [3] Yadav et al. (2023) — *TIES-Merging: Resolving Interference When Merging Models* — NeurIPS — Trim, sign-elect, and merge for better conflict resolution

### Policy Distillation

- [4] Multi-Teacher Online Policy Distillation (MT-OPD) — Behavior-space merging via routing prompts to specialist teachers and training student on scored responses
- [5] Hinton et al. (2015) — *Distilling the Knowledge in a Neural Network* — Original knowledge distillation paper
- [6] Silver et al. (2018) — *AlphaZero* — Policy distillation via self-play: stronger policy → distill → train again

### Offline Policy Learning

- [9] Swaminathan et al. (2017) — *Off-Policy Evaluation for Slate Recommendation* — NeurIPS — OPE foundations for ranking and slates
- [10] Zhao et al. (2018) — *Deep Reinforcement Learning for Sponsored Search Real-time Bidding* — KDD — Bidding as sequential RL with offline eval + online A/B
- [11] Kumar et al. (2020) — *Conservative Q-Learning for Offline Reinforcement Learning (CQL)* — NeurIPS — https://arxiv.org/abs/2006.04779 — Penalizes OOD actions to prevent extrapolation error
- [12] Kidambi et al. (2020) — *MOReL: Model-Based Offline Reinforcement Learning* — NeurIPS — Learns pessimistic MDP from offline data
- [13] Sachdeva et al. (2020) — *Off-Policy Bandits with Deficient Support* — KDD — When logging policy doesn't explore enough; critical for search/ads
- [14] Saito et al. (2021) — *Open Bandit Dataset and Pipeline* — NeurIPS Datasets & Benchmarks — Reproducible offline policy evaluation from multiple logged policies
- [15] Zhang et al. (2023) — *Unified Off-Policy Learning to Rank: A Reinforcement Learning Perspective* — NeurIPS — Connects counterfactual LTR directly with offline RL
- [16] Chen et al. (2023) — *Adversarial Counterfactual Environment Model Learning* — NeurIPS — Addresses selection bias in learned world models for counterfactual reasoning

### Online Policy Distillation (OPD)

- [19] Agarwal et al. (2024) — *On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes* — ICLR 2024 — Foundational LLM OPD paper; introduces GKD; distills on student-generated outputs to fix train-test distribution mismatch
- [20] Czarnecki et al. (2019) — *Distilling Policy Distillation* — AISTATS — Theoretical analysis of policy distillation objectives and KL-based losses
- [21] Zhang et al. (2026) — *Fast and Effective On-Policy Distillation from Reasoning Prefixes* — Findings of ACL 2026 — Reduces OPD cost by focusing teacher guidance on reasoning prefixes
- [22] Jang et al. (2026) — *Stable On-Policy Distillation through Adaptive Target Reformulation* — Findings of ACL 2026 — Addresses OPD instability via adaptive target reformulation when distributions diverge

### Frontier Lab Post-Training

- [23] Ouyang et al. (2022) — *InstructGPT* — https://arxiv.org/abs/2203.02155 — SFT → RM → PPO pipeline; implicit multi-signal consolidation
- [24] Bai et al. (2022) — *Constitutional AI* — https://arxiv.org/abs/2212.08073 — Self-critique as teacher; RLAIF for scalable distillation

---

## Practitioner Appendix

| Insight | Source |
|---------|--------|
| Mixed-dataset SFT is the strongest simple baseline for complementary tasks (Q&A + classification) — try this BEFORE weight merging or MT-OPD | ChatGPT MT-OPD seed discussion |
| For weight merging, evaluate in order: Mixed-SFT → TIES/DARE (training-free) → Multi-task SFT from best merged checkpoint | ChatGPT MT-OPD seed discussion |
| Frontier labs don't call it "MT-OPD" but their post-training pipelines (synthetic data from specialists → preference scoring → iterative distillation) are functionally equivalent | ChatGPT MT-OPD seed discussion |
| Student capacity is the hard ceiling — a 7B student cannot faithfully absorb four 70B experts regardless of method | ChatGPT MT-OPD seed discussion |
| The dominant failure mode is not catastrophic forgetting but policy collapse: the student converges to the most-sampled teacher and minority skills vanish | ChatGPT MT-OPD seed discussion |
| For Ads/Search offline PL: build the stack in order: (1) counterfactual evaluation, (2) conservative offline policy, (3) campaign world model, (4) offline RL/planning. Don't jump to RL. | ChatGPT offline PL discussion |
| The hard problem in offline PL for ads is not "which RL algorithm" but "can the counterfactual model faithfully predict market response to unseen actions?" — this is why world models matter more than policy optimizers | ChatGPT offline PL discussion |
| Search logs are severely biased by the current ranker — the "support problem" makes standard IPS methods fail when the logging policy doesn't explore the action space | ChatGPT offline PL discussion |
| OPD is a promising bridge between SFT/distillation and RL: retains dense supervision (easier to optimize than sparse reward) while being aligned with student's deployment distribution (unlike offline KD) | ChatGPT OPD discussion |
| For Ads FM: OPD could serve as a behavior-preservation / capability-recovery stage after domain adaptation — the pre-adaptation model acts as teacher on the post-adaptation student's own outputs | ChatGPT OPD discussion |
| OPD's one-sentence mental model: "Let the student make its own mistakes, then have the teacher provide dense, step-level guidance on the student's actual behavior" | ChatGPT OPD discussion |

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-29 | Integrated Online Policy Distillation (OPD) as Stage 7 + refs [19-22] | check-and-integrate: GKD/on-policy distillation, train-test mismatch fix, applications to search/ads, stability challenges |
| 2026-07-29 | Integrated offline policy learning as Stage 6 + Theme 4 + refs [9-16] | check-and-integrate: offline PL content covering OPE, counterfactual learning, offline RL, world models; applications to search/ads |
| 2026-07-29 | Initial v2 generation (study-notes format) | Generated from seed: chatgpt-mt-opd.md; covers weight merging → task arithmetic → TIES → MoE → mixed-SFT → MT-OPD → adaptive policy composition |
| 2026-07-29 | Filed | [UNVERIFIED] — run /verify-report --topic policy-dist when runtime available |
