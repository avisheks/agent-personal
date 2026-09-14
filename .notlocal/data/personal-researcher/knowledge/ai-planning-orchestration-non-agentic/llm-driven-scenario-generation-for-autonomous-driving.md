---
title: "LLM-Driven Scenario Generation for Autonomous Driving"
summary: "Using large language models to automatically generate diverse, regulation-compliant test scenarios for validating autonomous driving systems in simulation."
sources:
  - ai-planning-orchestration-non-agentic/search-arxiv-e-print-repository.md
createdAt: 2026-07-30T13:57:19.994870+00:00
updatedAt: 2026-07-30T13:57:19.994870+00:00
---
# LLM-Driven Scenario Generation for Autonomous Driving

**LLM-Driven Scenario Generation for Autonomous Driving** refers to the use of [[Large Language Model]]s to automatically create, modify, and enhance driving scenarios for testing and validating autonomous vehicle systems. This approach leverages the natural language understanding and reasoning capabilities of LLMs to generate diverse, realistic, and safety-critical scenarios that can be used in simulation environments or real-world testing protocols.

## Overview

Traditional scenario generation for autonomous driving relies heavily on manual design processes, mathematical models, or simple rule-based systems. LLM-driven approaches represent a paradigm shift by utilizing the semantic understanding and contextual reasoning capabilities of large language models to create more sophisticated and contextually appropriate driving scenarios. These systems can interpret natural language descriptions, regulatory requirements, and safety specifications to generate executable scenario scripts.

## Key Applications

### Regulatory Compliance Testing

LLM-driven systems excel at translating regulatory documents and safety standards into testable scenarios. The Chat2Scenic framework demonstrates this capability by generating scenario scripts from regulatory descriptions, achieving a 76.42% Compilation Success Rate when processing scenarios from NHTSA and United Nations Vehicle Regulations. This approach addresses the fundamental challenge of automatically converting regulatory text into executable Domain Specific Language (DSL) scripts for simulation testing. ^[arxiv-search-results.md]

### Safety-Critical Scenario Generation

LLMs are particularly effective at generating long-tail and safety-critical scenarios that are underrepresented in naturalistic driving data. The K-Risk dataset exemplifies this application, combining structured driving trajectories with LLM-generated semantic annotations for 31,398 high-risk events, including a subset of 1,036 extreme near-collision cases. Each scenario includes synchronized trajectory data, metadata, and language descriptions containing structured scenario descriptions, abnormal-behavior notifications, and causal risk analyses. ^[arxiv-search-results.md]

### Real-World Failure Analysis

LLM-driven approaches can process historical failure records to generate new test scenarios. Research demonstrates the use of categorical and contextual information from historical records in natural language format, with modular LLM-based synthetic scenario generation that remains compatible with testing constraints of specific systems. This method successfully generates diverse scenarios covering multiple road types, vehicle movement patterns, and on-road anomalies within limited testing budgets. ^[arxiv-search-results.md]

## Technical Approaches

### Retrieval-Augmented Generation

The Chat2Scenic framework implements an iterative [[Retrieval-Augmented Generation]] approach that grounds scenario generation in regulatory knowledge and DSL syntax. This system provides a chatbot interface supporting interactive scenario refinement while integrating RAG to ensure generated scenarios comply with both regulatory requirements and technical syntax constraints. ^[arxiv-search-results.md]

### Multi-Stage Processing Pipelines

Effective LLM-driven scenario generation typically employs multi-stage processing. The D-V2S framework operates through two distinct stages: a Driving Record Analyzer that uses [[Vision-Language Model]]s to produce natural-language descriptions from input videos, followed by a Scenario Generator that uses LLMs to translate these descriptions into executable scenarios. This approach achieves 90% semantic element preservation from original videos while maintaining executability. ^[arxiv-search-results.md]

### Alignment and Fine-Tuning

TrafficAlign represents an advanced approach that synthesizes traffic scenarios based on real-world driving videos, performs data validation, and aligns LLMs with synthesized scenarios. This framework demonstrates significant effectiveness, revealing up to 10.8% more collisions across autonomous driving models compared to state-of-the-art methods, while fine-tuning with generated scenarios reduces collision rates by 36.1%. ^[arxiv-search-results.md]

## Integration with Simulation Systems

### Agent-Driven Simulation

LLM-driven scenario generation extends beyond static scenario creation to dynamic, agent-driven simulation. Research demonstrates frameworks where surrounding road participants are controlled by instruction-following large language models through structured action interfaces, enabling intentional and reactive behaviors while preserving physical plausibility. This approach facilitates the creation of semantically rich scenarios that augment real driving data with multiple interactive agents following diverse language instructions. ^[arxiv-search-results.md]

### Closed-Loop Evaluation

Generated scenarios must support closed-loop evaluation where autonomous driving systems can interact dynamically with the simulated environment. The SemanticPlan benchmark exemplifies this requirement, providing closed-loop planning evaluation in long-tail scenarios that challenge state-of-the-art planners to achieve safe and effective task completion. ^[arxiv-search-results.md]

## Challenges and Limitations

### Compilation Success Rates

One significant challenge in LLM-driven scenario generation is achieving high compilation success rates for generated scripts. While Chat2Scenic achieves 76.42% compilation success, this indicates that nearly a quarter of generated scenarios fail to compile properly, requiring additional refinement or validation steps. ^[arxiv-search-results.md]

### Physical Plausibility

Ensuring that LLM-generated scenarios maintain physical plausibility and realistic vehicle dynamics remains challenging. Systems must incorporate constraints and validation mechanisms to prevent the generation of scenarios that violate physical laws or realistic driving behaviors. ^[arxiv-search-results.md]

### Evaluation Metrics

Developing appropriate evaluation metrics for LLM-generated scenarios presents ongoing challenges. Traditional metrics may not capture the semantic richness and contextual appropriateness that LLM-driven approaches aim to achieve, necessitating new evaluation frameworks that consider both technical correctness and scenario realism. ^[arxiv-search-results.md]

## Future Directions

The field continues to evolve toward more sophisticated integration of [[Chain-of-Thought Reasoning]], [[Constitutional AI]], and [[Multi-Agent Orchestration]] approaches. Research indicates growing interest in combining LLM-driven scenario generation with [[World Models]] and [[Reinforcement Learning]] frameworks to create more adaptive and intelligent testing environments for autonomous driving systems.
