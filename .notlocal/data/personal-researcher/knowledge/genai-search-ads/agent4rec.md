---
title: "Agent4Rec"
summary: "A research system that uses 1,000 LLM agents to simulate real human behavior for movie recommendations, achieving 349 citations as a foundational work."
sources:
  - genai-search-ads/llm-behavior-simulators-ads-search.md
createdAt: 2026-06-15T11:48:49.019052+00:00
updatedAt: 2026-06-15T11:48:49.019052+00:00
---
# Agent4Rec

**Agent4Rec** is a large-scale user simulation framework that employs 1,000 LLM agents to simulate realistic human behavior for recommender system evaluation. The system demonstrates that LLM-based agents can replicate authentic user interaction patterns, providing a scalable alternative to expensive live experiments in recommendation systems.

## Overview

Agent4Rec represents a breakthrough in [[LLM-Based Behavior Simulators for Ads & Search]], using persona-prompted language models to generate realistic user behavior sequences including queries, clicks, and preferences. The framework addresses the challenge of offline policy evaluation in recommender systems by creating synthetic but realistic user interactions at scale. ^[llm-based-behavior-simulators-for-ads-search.md]

The system was presented at SIGIR 2024 and has garnered 349 citations, establishing it as a foundational work in the field of LLM-based user simulation for recommendation systems. ^[llm-based-behavior-simulators-for-ads-search.md]

## Technical Architecture

Agent4Rec employs an **LLM-as-User** approach, where each of the 1,000 agents is equipped with distinct personas that guide their behavior generation. The agents are prompted to simulate realistic user interactions including:

- Query generation and refinement
- Item preference expression  
- Click-through behavior patterns
- Purchase decision simulation

The framework demonstrates that LLM agents can achieve behavioral authenticity that closely matches real human user patterns in movie recommendation scenarios. ^[llm-based-behavior-simulators-for-ads-search.md]

## Applications

### Offline Policy Evaluation

Agent4Rec's primary application is in **offline policy evaluation** for recommender systems. By generating large-scale synthetic user behavior data, the system enables researchers and practitioners to test recommendation algorithms without requiring expensive live experiments or access to sensitive user data. ^[llm-based-behavior-simulators-for-ads-search.md]

### Scalable Testing

The framework addresses a critical scalability challenge in recommendation system evaluation. While real-world systems serve billions of users, Agent4Rec demonstrates that 1,000 carefully designed LLM agents can provide meaningful behavioral simulation for algorithm testing and validation. ^[llm-based-behavior-simulators-for-ads-search.md]

## Industry Context

Agent4Rec is part of a broader trend of LLM-based behavior simulation across major technology companies. Google's RecSim NG framework and YouTube Music applications, Amazon's synthetic query generation systems, and ByteDance's PersonaAct all represent similar approaches to using [[Chain-of-Thought Reasoning]] and persona-based prompting for user behavior modeling. ^[llm-based-behavior-simulators-for-ads-search.md]

## Limitations and Challenges

Despite its success, Agent4Rec faces several key limitations common to LLM-based simulation systems:

### Scale Gap
The system uses 1,000 agents compared to billions of real users in production systems, raising questions about coverage of behavioral diversity at true scale. ^[llm-based-behavior-simulators-for-ads-search.md]

### Calibration Challenges  
Like other LLM-based simulators, Agent4Rec agents may converge toward a "positive average person" behavior pattern, potentially missing edge cases and diverse user segments that are critical for robust recommendation system evaluation. ^[llm-based-behavior-simulators-for-ads-search.md]

## Related Systems

Agent4Rec is closely related to other academic and industry frameworks including **RecAgent** (ACM Trans. 2025), **AgentCF** (WWW 2024), and **BASES** (EMNLP 2024 Findings). These systems collectively demonstrate the growing maturity of LLM-based user simulation for recommendation and search applications. ^[llm-based-behavior-simulators-for-ads-search.md]
