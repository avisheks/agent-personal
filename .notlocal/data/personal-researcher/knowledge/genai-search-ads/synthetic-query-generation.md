---
title: "Synthetic Query Generation"
summary: "Amazon's approach of using fine-tuned LLMs to generate 8 queries per product for cold-start scenarios and search system testing."
sources:
  - genai-search-ads/llm-behavior-simulators-ads-search.md
createdAt: 2026-06-15T11:49:31.386817+00:00
updatedAt: 2026-06-15T11:49:31.386817+00:00
---
# Synthetic Query Generation

## Overview

Synthetic query generation refers to the automated creation of search queries using computational methods, particularly [[large language models|autoregressive-language-model]], to simulate realistic user search behavior for training, evaluation, and testing purposes in information retrieval systems. This approach addresses the challenge of obtaining diverse, high-quality query datasets without relying solely on expensive human annotation or privacy-sensitive real user data. ^[llm-based-behavior-simulators-ads-search.md]

## Technical Approaches

### LLM-Based Generation

The most prominent approach involves prompting large language models with specific personas or contexts to generate realistic search queries. Companies like Amazon have demonstrated generating 8 queries per product using fine-tuned LLMs, showing how product-specific context can drive targeted query creation. ^[llm-based-behavior-simulators-ads-search.md]

### Persona-Driven Methods

Systems like BASES (Microsoft) and Agent4Rec create diverse user profiles at scale, with each profile generating queries that reflect specific user characteristics, preferences, and search patterns. This approach helps capture the heterogeneity of real user behavior across different demographics and use cases. ^[llm-based-behavior-simulators-ads-search.md]

### Adversarial Generation

Amazon has developed adversarial query generation techniques using GAN-like approaches for robustness testing. This method creates challenging or edge-case queries that help evaluate system performance under difficult conditions. ^[llm-based-behavior-simulators-ads-search.md]

## Applications

### Training Data Augmentation

Synthetic queries serve as training data for [[query-understanding-pipeline]] systems, helping improve model performance when real query data is limited or biased toward certain patterns.

### Offline Evaluation

Generated queries enable offline policy evaluation without requiring live user experiments. Google's work with YouTube Music demonstrates using synthetic queries within RecSim NG for counterfactual preference elicitation policy evaluation. ^[llm-based-behavior-simulators-ads-search.md]

### A/B Test Acceleration

Synthetic query generation supports rapid prototyping and initial testing of search algorithms before deploying to real users, reducing the cost and time of live experimentation. ^[llm-based-behavior-simulators-ads-search.md]

### Privacy-Safe Development

By generating synthetic queries that capture realistic patterns without exposing actual user data, this approach enables privacy-preserving development and research in search systems. ^[llm-based-behavior-simulators-ads-search.md]

## Industry Implementations

### Amazon

Amazon has implemented synthetic query generation for e-commerce search, creating product-specific queries and developing adversarial generation methods for robustness testing. Their approach includes both [[supervised-fine-tuning-sft]] of language models and reinforcement learning-based user simulation for query rewriting tasks. ^[llm-based-behavior-simulators-ads-search.md]

### Microsoft

Microsoft's BASES system represents a large-scale implementation for web search user simulation, focusing on generating diverse user profiles and corresponding query patterns that reflect real search behavior diversity. ^[llm-based-behavior-simulators-ads-search.md]

### Google

Google has integrated synthetic query generation within their RecSim NG framework, particularly for YouTube Music applications, demonstrating how generated queries can support sophisticated recommendation system evaluation. ^[llm-based-behavior-simulators-ads-search.md]

## Challenges and Limitations

### Calibration Issues

[[LLM-based behavior simulators|llm-hallucination]] tend to converge toward generating queries representing a "positive average person," potentially missing edge cases or minority user behaviors that are crucial for comprehensive system evaluation. ^[llm-based-behavior-simulators-ads-search.md]

### Scale Disparities

Current implementations typically generate thousands of synthetic queries, while real systems handle billions of user queries, creating potential gaps in coverage and diversity that may not fully represent production-scale challenges. ^[llm-based-behavior-simulators-ads-search.md]

### Realism Validation

Ensuring that synthetic queries accurately reflect real user intent and behavior patterns remains an ongoing challenge, requiring careful validation against actual user data and continuous refinement of generation methods. ^[llm-based-behavior-simulators-ads-search.md]

## Related Concepts

Synthetic query generation is closely related to [[chain-of-thought-reasoning]] for query understanding, [[constitutional-ai]] for ensuring appropriate query generation, and [[mixture-of-experts-moe]] architectures that can specialize in different types of query generation tasks.
