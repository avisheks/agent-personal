---
title: "trajectory-evaluation"
summary: ""
sources:
  - evaluation-safety/evaluation-safety-ref.md
createdAt: 2026-05-28T20:05:17.858714+00:00
updatedAt: 2026-05-28T20:05:17.858714+00:00
---
# Trajectory Evaluation

**Trajectory Evaluation** is a specialized evaluation methodology for assessing multi-step AI systems, particularly [[Agentic Systems]] and conversational AI, where the quality of the entire sequence of actions or responses is evaluated rather than just the final output. Unlike traditional model evaluation that focuses on individual predictions, trajectory evaluation examines the path taken to reach a conclusion, including intermediate steps, decision-making processes, and the overall coherence of the multi-turn interaction.

## Overview

Trajectory evaluation addresses the fundamental limitation of output-only evaluation methods when applied to systems that perform multi-step reasoning, tool usage, or extended conversations. In these systems, an agent might arrive at a correct final answer through an inefficient, unsafe, or suboptimal path, making the evaluation of the entire trajectory critical for assessing true system quality. ^[evaluation-safety-ref.md]

The methodology is essential for evaluating [[Agent Systems]] where the sequence of tool calls, intermediate reasoning steps, and error recovery mechanisms are as important as the final outcome. A model that produces correct results via dangerous intermediate steps—such as accessing unauthorized data or making unnecessary tool calls—represents a different risk profile than one that follows an optimal path. ^[evaluation-safety-ref.md]

## Core Components

### Trajectory Decomposition

Trajectory evaluation begins with breaking down the multi-step sequence into discrete, evaluable components. For an agent trajectory τ = (s₀, a₁, o₁, s₁, a₂, o₂, ..., sₙ), where s_i represents states, a_i represents actions, and o_i represents observations, each step is analyzed independently before aggregating into an overall trajectory score. ^[evaluation-safety-ref.md]

### Scoring Dimensions

Trajectory evaluation typically assesses multiple dimensions simultaneously:

- **Goal Achievement**: Whether the final state accomplishes the user's objective
- **Path Efficiency**: The optimality of the route taken, measured against the minimum steps required
- **Tool Correctness**: Accuracy of tool selection and parameter usage at each step
- **Safety Compliance**: Whether any step violates safety constraints or policies
- **Recovery Quality**: How gracefully the system handles errors or unexpected responses
- **Explainability**: Whether a human can follow the reasoning chain from the trace

Each dimension is scored independently, with safety treated as a hard constraint rather than a tradeable dimension. ^[evaluation-safety-ref.md]

## Evaluation Framework

### Per-Step Analysis

For each step in the trajectory, evaluators assess:

1. **Tool Selection**: Was the chosen tool optimal for the current state and goal?
2. **Parameter Quality**: Were the tool parameters correct and appropriate?
3. **Interpretation**: Did the agent correctly interpret the tool's response?
4. **Necessity**: Was this step required, or could the goal have been achieved more efficiently?

### Aggregation Methods

Trajectory scores are typically computed using multiplicative aggregation: R_quality(τ) = Πᵢ P(step_i correct). This approach naturally penalizes longer trajectories, as each additional step introduces potential for error. For example, a 5-step trajectory with 95% per-step accuracy yields an overall quality score of 0.77, while a 10-step trajectory with the same per-step quality drops to 0.60. ^[evaluation-safety-ref.md]

## Implementation Approaches

### Automated Evaluation

[[LLM-as-Judge Quality Scoring]] systems can be adapted for trajectory evaluation by scoring each step on the defined dimensions. This requires careful prompt engineering to ensure the judge model understands the context of multi-step interactions and can assess path optimality. Cross-family judging (using different model families for evaluation than the system being tested) helps reduce self-preference bias. ^[evaluation-safety-ref.md]

### Human Expert Review

Human evaluators score complete trajectories using structured rubrics that define what constitutes optimal behavior for each dimension. Calibration sets ensure consistency between human reviewers, with inter-rater agreement tracked using metrics like Cohen's κ. ^[evaluation-safety-ref.md]

### Hybrid Approaches

Production systems often combine automated screening for obvious failures (safety violations, format errors) with human review of complex cases requiring nuanced judgment about path optimality or strategic quality.

## Challenges and Considerations

### Non-Deterministic Behavior

Agent systems often exhibit non-deterministic behavior, producing different trajectories for identical inputs. Trajectory evaluation must account for this variability through statistical testing approaches. Safety requirements typically demand that unsafe actions occur in 0% of runs, while quality metrics may accept statistical thresholds such as task completion in 90% of attempts within a specified step limit. ^[evaluation-safety-ref.md]

### Evaluation Set Construction

Building effective trajectory evaluation sets requires capturing the full range of multi-step scenarios the system may encounter. This includes recording production trajectories (with appropriate consent), creating synthetic adversarial scenarios, and ensuring coverage of different complexity levels and failure modes. ^[evaluation-safety-ref.md]

### Scalability

Trajectory evaluation is inherently more expensive than single-output evaluation, as it requires assessing multiple steps per interaction. Organizations must balance evaluation thoroughness with practical constraints around time and cost.

## Applications

Trajectory evaluation is particularly critical for:

- **Autonomous agents** performing complex tasks requiring multiple tool interactions
- **Conversational AI systems** where dialogue coherence and progression matter
- **Planning systems** where the reasoning process is as important as the final plan
- **Multi-step reasoning tasks** in domains like mathematics, coding, or strategic analysis

The methodology has proven essential in enterprise applications where both correctness and process compliance are required, such as financial analysis tools or medical decision support systems. ^[evaluation-safety-ref.md]

## Integration with Evaluation Frameworks

Trajectory evaluation typically operates as part of a layered evaluation stack, where it serves as a specialized component for multi-step systems. It integrates with [[Five-Layer Evaluation Stack]] architectures by providing the trajectory-specific assessment capabilities needed for Layer 3 (automated judgment) and Layer 4 (expert review) when evaluating agentic systems. ^[evaluation-safety-ref.md]

The methodology complements traditional [[Safety Evaluation]] approaches by ensuring that safety compliance is maintained throughout the entire interaction sequence, not just at the final output. This is particularly important for systems that might access sensitive data or perform privileged operations during intermediate steps. ^[evaluation-safety-ref.md]
