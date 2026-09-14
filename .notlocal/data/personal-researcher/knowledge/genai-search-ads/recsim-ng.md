---
title: "RecSim NG"
summary: "Google's probabilistic, differentiable multi-agent recommender ecosystem simulation framework used for counterfactual policy evaluation."
sources:
  - genai-search-ads/llm-behavior-simulators-ads-search.md
createdAt: 2026-06-15T11:48:31.605245+00:00
updatedAt: 2026-06-15T11:48:31.605245+00:00
---
# RecSim NG

**RecSim NG** is a probabilistic, differentiable multi-agent recommender ecosystem simulation framework developed by Google Research. It enables researchers to model complex interactions between users, content, and recommendation algorithms in a controlled environment for offline policy evaluation and experimentation. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Overview

RecSim NG represents a significant advancement in [[LLM-Based Behavior Simulators for Ads & Search]], providing a framework for simulating entire recommender ecosystems rather than individual user behaviors. The system allows researchers to test recommendation policies without requiring expensive live experiments or risking negative user experiences. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Technical Architecture

The framework is built on probabilistic and differentiable foundations, enabling gradient-based optimization of recommendation policies. RecSim NG supports multi-agent simulations where different entities (users, advertisers, content creators) can interact within the same ecosystem, creating emergent behaviors that mirror real-world dynamics. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Industry Applications

### YouTube Music Integration

Google demonstrated RecSim NG's practical value through integration with YouTube Music for counterfactual preference elicitation policy evaluation. This application, presented at SIGIR 2024, showed how the framework could minimize the need for live experiments while maintaining policy evaluation accuracy. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

### Offline Policy Evaluation

The framework enables researchers to evaluate recommendation policies offline by simulating user interactions and measuring policy performance without deploying changes to production systems. This approach significantly reduces the cost and risk associated with traditional A/B testing methodologies. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Relationship to LLM-Based Simulation

While RecSim NG predates the widespread adoption of [[Chain-of-Thought Reasoning]] and modern [[LLM-Based Behavior Simulators for Ads & Search]], it provides the foundational architecture that newer LLM-powered simulation systems build upon. The framework's multi-agent approach aligns with contemporary research in [[Multi-Agent Orchestration]] for recommendation systems. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Comparison with Other Approaches

RecSim NG differs from pure LLM-based simulation approaches by providing a more structured, probabilistic foundation. While systems like Agent4Rec use LLM personas to generate user behaviors, RecSim NG focuses on the mathematical modeling of ecosystem dynamics, making it complementary to rather than competitive with LLM-based approaches. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]

## Research Impact

The framework has influenced subsequent research in recommendation system simulation, particularly in the development of hybrid approaches that combine classical simulation engines with LLM-generated behaviors. Its emphasis on differentiable simulation has also contributed to advances in gradient-based policy optimization for recommendation systems. ^[llm-based-shopper-advertiser-behavior-simulators-in-online-search-ads.md]
