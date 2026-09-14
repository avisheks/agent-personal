# RL for LLMs and Self-Improving Agents: A Curated Reading Roadmap

This reading list is organized chronologically based on how the field has evolved. Rather than reading papers in publication order, the papers are grouped by the major ideas they introduced. If read in sequence, you'll see the field evolve from:

> **RLHF → Preference Optimization → Reasoning RL → Reflection → Self-Training → Harness Optimization → Self-Improving Agents → World Models**

---

# Stage 1 — RLHF: Teaching Models to Follow Instructions

**Goal:** Understand why supervised fine-tuning (SFT) alone is insufficient.

## 1. Learning to Summarize from Human Feedback (2020)

**Paper**

> Stiennon et al., *Learning to Summarize from Human Feedback*, NeurIPS 2020

### Why read it?

Arguably the first modern RLHF paper.

Introduces:

- Human preference collection
- Reward models
- PPO for language models
- RLHF pipeline

---

## 2. Training Language Models to Follow Instructions with Human Feedback (InstructGPT)

**Paper**

> Ouyang et al., *Training Language Models to Follow Instructions with Human Feedback*, NeurIPS 2022

### Learn

- SFT
- Reward Model
- PPO
- RLHF pipeline

This paper established the now-standard three-stage post-training recipe.

---

## 3. Constitutional AI

**Paper**

> Bai et al., *Constitutional AI: Harmlessness from AI Feedback*, 2022

### Learn

- AI-generated critiques
- Self-critique
- AI feedback
- Preference optimization

This is one of the earliest papers suggesting that models can help improve themselves.

---

# Stage 2 — Preference Optimization

The next question the community asked:

> Can we remove PPO entirely?

---

## 4. Direct Preference Optimization (DPO)

**Paper**

> Rafailov et al., *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*, NeurIPS 2023

### Learn

- Implicit reward models
- KL constraints
- Preference optimization
- Why DPO replaces PPO

---

## 5. IPO

**Paper**

> *IPO: Your Language Model is Secretly a Preference Classifier*

### Learn

- Improvements over DPO objectives
- Preference optimization variants

---

## 6. ORPO

**Paper**

> *ORPO: Monolithic Preference Optimization without Reference Model*

### Learn

- Eliminating the reference model
- Simplified alignment pipeline

---

## 7. SimPO

**Paper**

> *SimPO: Simple Preference Optimization with a Reference-Free Reward*

### Learn

- Reference-free optimization
- Simpler objectives

---

## 8. KTO

**Paper**

> *KTO: Model Alignment as Prospect Theoretic Optimization*

### Learn

- Prospect theory
- Utility-based preference optimization

---

# Stage 3 — RL for Reasoning

RL begins shifting from **alignment** to **reasoning**.

---

## 9. DeepSeek-R1

**Paper**

> *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning*

### Learn

- RL-first reasoning
- GRPO
- Process rewards
- Long-chain reasoning

---

## 10. Qwen Reasoning Reports

### Learn

- GRPO
- Reasoning data generation
- Scaling reasoning models

---

## 11. RLVR (Reinforcement Learning with Verifiable Rewards)

Rather than a single paper, study the growing body of work on RLVR.

### Applications

- Mathematics
- Code generation
- Theorem proving

### Key idea

Replace noisy human feedback with deterministic verification.

---

# Stage 4 — Reflection

The next major question:

> Can models critique themselves?

---

## 12. Reflexion

**Paper**

> Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, NeurIPS 2023

Pipeline

```text
Run
 ↓
Reflect
 ↓
Retry
```

### Learn

- Reflection
- Episodic memory
- Retry strategies

---

## 13. Self-Refine

**Paper**

> *Self-Refine: Iterative Refinement with Self-Feedback*

### Learn

- Self-feedback
- Iterative refinement
- No additional training

---

## 14. Tree of Thoughts

**Paper**

> *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*

### Learn

- Search
- Deliberate reasoning
- Planning

---

## 15. Graph of Thoughts

### Learn

- Graph-based reasoning
- Flexible planning
- Multi-path reasoning

---

# Stage 5 — Self-Training

Reflection begins generating training data.

---

## 16. ReST

**Paper**

> *ReST: Reinforced Self-Training*

Pipeline

```text
Generate
 ↓
Filter
 ↓
Train
```

### Learn

- Self-generated datasets
- Filtering
- Iterative improvement

---

## 17. Re-ReST

**Paper**

> *Reflection-Reinforced Self-Training for Language Agents*

Pipeline

```text
Trajectory
 ↓
Reflection
 ↓
Corrected Trajectory
 ↓
SFT
```

### Learn

- Reflection-generated supervision
- Automatic SFT dataset generation

---

## 18. Agent-R

### Learn

- Failure localization
- Trajectory repair
- Automatic supervision generation

---

# Stage 6 — Harness Optimization

Instead of improving model weights, improve the surrounding system.

---

## 19. Retrospective Harness Optimization (RHO)

**Paper**

> Microsoft Research, 2026

Pipeline

```text
Trajectory
 ↓
Reflection
 ↓
Prompt Patch
 ↓
Regression Test
 ↓
Deploy
```

### Learn

- Harness evolution
- Prompt optimization
- Workflow optimization
- Regression testing

---

## 20. Voyager

**Paper**

> *Voyager: An Open-Ended Embodied Agent with Large Language Models*

### Learn

- Skill libraries
- Automatic curriculum
- Lifelong learning

---

## 21. Generative Agents

**Paper**

> *Generative Agents: Interactive Simulacra of Human Behavior*

### Learn

- Memory
- Reflection
- Planning
- Agent architectures

---

# Stage 7 — Reflection Meets RL

Reflection becomes part of policy optimization.

---

## 22. Teaching Large Reasoning Models Effective Reflection

### Learn

- Self-Critique Fine-Tuning (SCFT)
- RL with Effective Reflection Rewards (RLERR)
- Reflection-guided RL

---

## 23. Reflect, Retry, Reward

Pipeline

```text
Failure
 ↓
Reflection
 ↓
Retry
 ↓
Reward
 ↓
RL
```

### Learn

- Reflection-based reward shaping
- Reflection-guided reinforcement learning

---

# Stage 8 — World Models & Long-Horizon Agents

Where the field appears to be heading.

---

## 24. DreamerV3

### Learn

- World models
- Latent planning
- Model-based RL

---

## 25. MuZero

### Learn

- Planning without explicit environment models
- Learned dynamics
- Search

---

## 26. EfficientZero

### Learn

- Sample-efficient planning
- World models

---

## 27. Genie

### Learn

- Interactive world models
- Video-to-world modeling
- Agent simulation

---

# Stage 9 — Reflection Router (Open Research Direction)

To the best of my knowledge, no published paper currently proposes the following unified architecture:

```text
Trajectory
 ↓
Reflection
 ↓
Reflection Router
 ↓
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │
Harness       SFT            RL
```

Instead, existing work typically routes reflections into **one** optimization pathway.

| Paper | Harness | SFT | RL |
|-------|:--------:|:---:|:--:|
| InstructGPT | ❌ | ✅ | ✅ |
| Constitutional AI | ❌ | ✅ | ✅ |
| DPO | ❌ | ✅ | ❌ |
| ORPO | ❌ | ✅ | ❌ |
| SimPO | ❌ | ✅ | ❌ |
| DeepSeek-R1 | ❌ | ❌ | ✅ |
| Reflexion | ✅ | ❌ | ❌ |
| Self-Refine | ✅ | ❌ | ❌ |
| ReST | ❌ | ✅ | ❌ |
| Re-ReST | ❌ | ✅ | ❌ |
| Agent-R | ❌ | ✅ | ❌ |
| Voyager | ✅ | ❌ | ❌ |
| Generative Agents | ✅ | ❌ | ❌ |
| Retrospective Harness Optimization | ✅ | ❌ | ❌ |
| Teaching Large Reasoning Models Effective Reflection | ❌ | ✅ | ✅ |
| Reflect, Retry, Reward | ❌ | ❌ | ✅ |

---

# Recommended Reading Schedule

| Week | Papers | Main Question |
|------|---------|---------------|
| **1** | Learning to Summarize from Human Feedback, InstructGPT, Constitutional AI | How do we align language models? |
| **2** | DPO, IPO, ORPO, SimPO, KTO | Can PPO be replaced? |
| **3** | DeepSeek-R1, Qwen Reasoning Reports, RLVR | How do we use RL to improve reasoning? |
| **4** | Reflexion, Self-Refine, Tree of Thoughts, Graph of Thoughts | How can models critique and improve themselves? |
| **5** | ReST, Re-ReST, Agent-R | How do reflections become training data? |
| **6** | Voyager, Generative Agents, Retrospective Harness Optimization | How do agents improve without changing model weights? |
| **7** | Teaching Large Reasoning Models Effective Reflection, Reflect, Retry, Reward | How does reflection integrate with RL? |
| **8** | DreamerV3, MuZero, EfficientZero, Genie | How do agents learn world models and plan over long horizons? |

---

# Overall Story of the Field

The literature tells a coherent story:

```text
Human Feedback
        ↓
RLHF
        ↓
Preference Optimization
        ↓
Reasoning RL
        ↓
Reflection
        ↓
Self-Training
        ↓
Harness Optimization
        ↓
Self-Improving Agents
        ↓
World Models
```

The natural next step—and a promising research direction—is a **Reflection Router** that automatically determines whether each reflection should produce:

1. **Harness improvements** (prompts, planning, memory, orchestration)
2. **SFT training examples** (corrected demonstrations)
3. **RL training data** (state/action/reward or preference signals)

This unified routing architecture does not yet appear to be explicitly explored in the current literature and represents an interesting opportunity for future research.