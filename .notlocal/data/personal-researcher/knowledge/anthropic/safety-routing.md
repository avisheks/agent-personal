---
title: "Safety Routing"
summary: "A mechanism that redirects potentially dangerous queries (cybersecurity/biology) from advanced models to safer alternatives while maintaining functionality."
sources:
  - anthropic/anthropic-model-family-comparison.md
createdAt: 2026-06-15T11:58:52.776885+00:00
updatedAt: 2026-06-15T11:58:52.776885+00:00
---
# Safety Routing

Safety routing is a mechanism used in advanced AI systems to automatically redirect potentially harmful queries to more appropriate models or safety-constrained versions. This approach allows AI providers to deploy powerful models while maintaining safety guardrails for sensitive domains.

## Overview

Safety routing operates by analyzing incoming queries and determining whether they fall into restricted categories that require special handling. When a query is identified as potentially sensitive, the system automatically routes it to a different model or applies additional safety constraints rather than processing it with the primary model. ^[anthropic-model-family-comparison.md]

The most prominent implementation of safety routing is found in [[Claude Fable 5]], which uses the same base model as the restricted [[Claude Mythos 5]] but implements safety routing for cybersecurity and biology-related queries. When Fable 5 detects queries in these domains, it automatically routes them to [[Claude Opus 4.8]] instead of processing them with its full capabilities. ^[anthropic-model-family-comparison.md]

## Implementation in Anthropic Models

[[Claude Fable 5]] represents the first major commercial deployment of safety routing technology. Despite being based on the same underlying model as the invitation-only Mythos 5, Fable 5 uses safety routing to prevent access to certain capabilities while maintaining general performance. Specifically, cybersecurity vulnerability discovery and advanced biology research queries are automatically redirected to Opus 4.8, which has more constrained capabilities in these areas. ^[anthropic-model-family-comparison.md]

This approach allows Anthropic to offer the advanced reasoning and autonomous capabilities of their most powerful model while preventing misuse in domains where the model has demonstrated concerning capabilities, such as discovering zero-day vulnerabilities or conducting advanced biological research. ^[anthropic-model-family-comparison.md]

## Technical Approach

Safety routing systems must balance several competing requirements: they need to accurately identify potentially harmful queries without creating excessive false positives that would degrade user experience. The routing decision must also be made quickly enough to maintain responsive performance. ^[anthropic-model-family-comparison.md]

The routing mechanism appears to operate at the query level, analyzing the intent and domain of incoming requests before determining the appropriate model to handle the response. This suggests the use of specialized classifiers or rule-based systems that can rapidly categorize queries by risk level and domain. ^[anthropic-model-family-comparison.md]

## Advantages and Limitations

Safety routing offers several advantages over alternative safety approaches. It allows providers to deploy powerful models more broadly while maintaining domain-specific restrictions. Users can access advanced capabilities for most use cases while being automatically protected from accessing potentially dangerous functionality. ^[anthropic-model-family-comparison.md]

However, safety routing also introduces complexity in model deployment and may create inconsistent user experiences when queries are unexpectedly routed to different models with varying capabilities. The effectiveness of the approach depends heavily on the accuracy of the routing classifier and the appropriateness of the fallback model for restricted domains. ^[anthropic-model-family-comparison.md]

## Relationship to Other Safety Approaches

Safety routing represents a middle ground between completely restricting access to powerful models and relying solely on [[Constitutional AI]] or other training-time safety measures. While [[Constitutional AI]] attempts to build safety directly into model behavior during training, safety routing provides an additional layer of protection by controlling which model processes specific types of queries. ^[anthropic-model-family-comparison.md]

This approach complements other safety mechanisms rather than replacing them, as the fallback models (like Opus 4.8 in the Fable 5 implementation) still rely on their own safety training and constitutional principles to handle redirected queries appropriately. ^[anthropic-model-family-comparison.md]
