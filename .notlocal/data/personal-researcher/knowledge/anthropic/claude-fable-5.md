---
title: "Claude Fable 5"
summary: "Anthropic's premium general availability model based on Mythos 5 but with safety routing, enabling multi-day autonomous work sessions with sub-agent delegation."
sources:
  - anthropic/anthropic-model-family-comparison.md
createdAt: 2026-06-15T11:57:37.436811+00:00
updatedAt: 2026-06-15T11:57:37.436811+00:00
---
# Claude Fable 5

**Claude Fable 5** is Anthropic's premium general availability model released on June 9, 2026. It represents the same base model as [[Claude Mythos 5]] but with safety routing that redirects cybersecurity and biology research queries to [[Claude Opus 4.7]]. Fable 5 is designed for multi-day autonomous work sessions with advanced capabilities including self-validation and sub-agent delegation. ^[anthropic-model-family-comparison.md]

## Architecture and Capabilities

Claude Fable 5 features "adaptive thinking" that is always enabled, automatically adjusting reasoning depth without requiring an extended thinking toggle. The model can conduct autonomous work sessions spanning multiple days, with built-in capabilities for planning across stages, delegating tasks to sub-agents, and performing self-validation of its work. ^[anthropic-model-family-comparison.md]

The model shares the same underlying architecture as Mythos 5 but implements safety routing to ensure that sensitive cybersecurity vulnerability discovery and biology research queries are automatically redirected to the more constrained Opus 4.8 model. ^[anthropic-model-family-comparison.md]

## Performance and Benchmarks

Fable 5 has achieved state-of-the-art performance on several partner benchmarks, becoming the first model to exceed 90% on analytics tasks. It demonstrates superior performance on CursorBench, FrontierBench, Finance, and Analytics benchmarks compared to previous models in the [[Claude 3 Model Family]]. ^[anthropic-model-family-comparison.md]

## Technical Specifications

### Context and Output
- **Input context window**: 1 million tokens
- **Output capacity**: 128,000 tokens
- **Knowledge cutoff**: Updated as of June 2026

### Pricing Structure
- **Input tokens**: $10 per million tokens (MTok)
- **Output tokens**: $50 per million tokens (MTok)
- **Batch processing**: $5 input / $25 output per MTok

^[anthropic-model-family-comparison.md]

## Positioning in Model Hierarchy

Within Anthropic's model hierarchy, Fable 5 sits as the premium general availability option, positioned between the restricted [[Claude Mythos 5]] and the more accessible [[Claude Opus 4.7]]. It offers near-Mythos capabilities while maintaining broader availability compared to the invitation-only Mythos model. ^[anthropic-model-family-comparison.md]

The model is designed for users who require advanced autonomous capabilities but do not need the specialized cybersecurity and biology research features that are exclusive to Mythos 5. For less demanding tasks, users can opt for the more cost-effective [[Claude Sonnet 4.6]] or [[Claude Haiku 4.5]] models. ^[anthropic-model-family-comparison.md]

## Safety and Routing

The safety routing system in Fable 5 represents a key architectural decision to balance capability with responsible deployment. When the model detects queries related to cybersecurity vulnerability discovery or advanced biology research, it automatically routes these requests to Opus 4.8, which has more restrictive safety measures for these sensitive domains. ^[anthropic-model-family-comparison.md]
