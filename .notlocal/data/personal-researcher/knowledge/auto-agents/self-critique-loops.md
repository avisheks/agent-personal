---
title: "Self-Critique Loops"
summary: "Verbal reflection mechanisms where agents analyze their failures and store insights for future improvement."
sources:
  - auto-agents/self-evolving-agents-survey.md
createdAt: 2026-06-15T11:27:28.768326+00:00
updatedAt: 2026-06-15T11:27:28.768326+00:00
---
# Self-Critique Loops

Self-critique loops are a mechanism within [[Self-Evolving Agents]] where AI systems engage in verbal reflection on their failures and store these reflections for future reference and improvement. This approach enables agents to learn from mistakes without requiring parameter updates to the underlying model. ^[self-evolving-agents.md]

## Core Mechanism

Self-critique loops operate through a cyclical process where agents analyze their own performance, identify failure modes, and generate textual feedback that can be retrieved in similar future situations. The agent reflects on what went wrong, why it failed, and how it might approach similar problems differently. ^[self-evolving-agents.md]

## Implementation in Reflexion

The most prominent example of self-critique loops is **Reflexion**, which demonstrates verbal reinforcement learning without parameter updates. In this system, agents generate self-reflective feedback about their failures, which is then stored and retrieved to guide future decision-making. This approach achieved 91% pass@1 on HumanEval, showing significant improvement through iterative self-reflection. ^[self-evolving-agents.md]

## Relationship to Other Evolution Mechanisms

Self-critique loops represent one approach within the broader spectrum of [[Self-Evolving Agents]] mechanisms. They fall into the "weak" category of self-evolution, as they do not involve weight updates to the base model. Instead, they rely on accumulating textual experience that can be retrieved and applied to new situations. ^[self-evolving-agents.md]

Other related mechanisms include:
- Experience memory and retrieval systems (ExpeL, FORGE)
- Skill auto-creation and library management
- Reward-driven adaptation approaches ^[self-evolving-agents.md]

## Safety Considerations

Research has identified potential safety risks with experience accumulation mechanisms, including self-critique loops. Studies show that "experience gathered solely from benign tasks can still compromise safety in high-risk scenarios" due to execution-oriented accumulated experience reinforcing the tendency to act rather than refuse. This creates a fundamental safety-utility trade-off where adding refusal experience can cause over-refusal behavior. ^[self-evolving-agents.md]

## Industry Applications

Self-critique loops have been implemented in various commercial and research contexts as part of broader [[Self-Evolving Agents]] systems. They are particularly valuable in scenarios where continuous learning from mistakes is important but full model retraining is impractical or expensive. ^[self-evolving-agents.md]
