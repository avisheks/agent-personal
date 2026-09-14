---
title: "five-layer-evaluation-stack"
summary: ""
sources:
  - evaluation-safety/evaluation-safety-ref.md
createdAt: 2026-05-28T20:04:19.833919+00:00
updatedAt: 2026-05-28T20:04:19.833919+00:00
---
# Five-Layer Evaluation Stack

The **Five-Layer Evaluation Stack** is a hierarchical evaluation framework for large language models (LLMs) and AI agents that addresses the fundamental challenge that no single evaluation method can catch all failure modes in AI systems. The framework organizes evaluation into five sequential layers with increasing semantic depth and cost, where each layer catches different classes of failures that previous layers miss.

## Overview

The Five-Layer Evaluation Stack was developed to solve the core problem of AI system evaluation: traditional single-metric approaches miss critical failures that only become apparent in production. The framework operates on the principle that early automated filters catch regressions cheaply, while more sophisticated methods catch nuanced quality issues, and human review catches remaining edge cases. ^[evaluation-safety-ref.md]

The stack addresses the organizational challenge that evaluation systems must be both technically rigorous and trusted by all stakeholders (science, product, policy, leadership) while being fast enough not to kill shipping velocity. Each layer serves as a filter with different cost profiles, latency requirements, and failure detection capabilities. ^[evaluation-safety-ref.md]

## The Five Layers

### Layer 1: Deterministic Tests
**Latency**: <1 second  
**Cost**: ~$0  
**Pass Rate**: 98%+ of outputs

Layer 1 consists of fast, rule-based checks that catch obvious failures instantly. These include format validation, regex safety checks, length limits, prohibited term detection, and schema compliance. This layer functions as unit tests for model outputs, providing immediate feedback on basic correctness. ^[evaluation-safety-ref.md]

### Layer 2: Automated Benchmarks
**Latency**: Minutes  
**Cost**: ~$0  
**Pass Rate**: 90%+ accuracy on golden set

Layer 2 employs domain-specific test suites rather than public benchmarks. These include regression tests from past failures and golden-set accuracy measurements. Unlike generic benchmarks such as MMLU or HumanEval, Layer 2 focuses on domain-specific behavior that matters for the particular application. The framework emphasizes that public benchmarks measure generic capabilities but tell nothing about domain-specific behavior such as ads policy compliance, advertiser-specific reasoning, or locale-specific safety requirements. ^[evaluation-safety-ref.md]

### Layer 3: LLM-as-Judge
**Latency**: Minutes  
**Cost**: ~$1-5 per evaluation run  
**Pass Rate**: Mean score above threshold per dimension

Layer 3 uses calibrated LLM judges to score outputs on structured rubric dimensions including accuracy, safety, usefulness, and policy compliance. The implementation requires cross-family judging (using different model families to avoid self-preference bias) and regular calibration against human experts to maintain reliability. ^[evaluation-safety-ref.md]

### Layer 4: SME Review
**Latency**: Hours to days  
**Cost**: $$$  
**Pass Rate**: >85% SME approval rate

Layer 4 involves human subject matter experts reviewing a stratified sample of outputs. Rather than random sampling, this layer over-samples high-risk cases, difficult scenarios, and instances where automated layers showed uncertainty. The review uses calibrated rubrics with inter-rater agreement tracking to ensure consistency. ^[evaluation-safety-ref.md]

### Layer 5: UAT / Shadow Production
**Latency**: Days to weeks  
**Cost**: Operational cost  
**Pass Rate**: No regression on key business metrics

Layer 5 runs the model in shadow mode on production traffic, comparing outputs against the current production model. This includes A/B testing on live users to validate that laboratory improvements translate to real-world performance gains. This layer catches failures that only manifest under real-world conditions including load, distribution, and user behavior patterns. ^[evaluation-safety-ref.md]

## Implementation Framework

### Cost and Coverage Distribution

The framework operates on empirically-derived coverage statistics: Layer 1-2 catch 70% of issues at near-zero cost, Layer 3 catches 20% at moderate cost, Layer 4 catches 8% at high cost, and Layer 5 catches the remaining 2% that only appear under real traffic conditions. This distribution allows organizations to match evaluation rigor to release risk. ^[evaluation-safety-ref.md]

### LLM-as-Judge Calibration

The framework addresses known biases in LLM-based evaluation through systematic calibration protocols. Key biases include position bias (first response in pairwise comparisons receiving higher scores), self-preference (models preferring outputs from their own family), verbosity bias (longer outputs scoring higher regardless of quality), and sycophancy (judges following implied preferences rather than independent assessment). ^[evaluation-safety-ref.md]

Mitigation strategies include cross-family judging, position randomization, calibration sets of 200+ examples scored by both LLM judges and human experts, drift monitoring through monthly re-runs of calibration sets, and rubric anchoring with structured criteria rather than subjective quality assessments. ^[evaluation-safety-ref.md]

### Segment-Aware Evaluation

The framework emphasizes that aggregate metrics can hide critical failures. A model scoring 95% overall may score only 60% on critical segments such as medical claims, high-spend advertisers, or non-English locales. The evaluation requires mandatory slicing across dimensions including content type, risk level, locale/language, user segment, and query complexity. ^[evaluation-safety-ref.md]

A fundamental rule of the framework states that a model cannot pass evaluation if any critical segment regresses, even if the aggregate improves. This prevents scenarios where models become "better on average but worse for our largest customers." ^[evaluation-safety-ref.md]

## Specialized Applications

### Trajectory Evaluation for Agents

For agentic systems, the framework extends beyond output evaluation to [[trajectory-level-evaluation]], scoring multi-step sequences of actions. This includes task decomposition into discrete steps, per-step scoring for correctness and appropriateness, trajectory scoring for overall path efficiency and safety, and counterfactual assessment of whether better paths existed. ^[evaluation-safety-ref.md]

The framework recognizes that agents can produce correct final recommendations through dangerous paths—accessing unauthorized data, making unnecessary tool calls, or building on hallucinated intermediate results. Trajectory evaluation catches these "correct but unsafe" paths that output-only evaluation would miss. ^[evaluation-safety-ref.md]

### Safety and Policy Compliance

Safety evaluation within the framework is treated as fundamentally different from quality evaluation. Quality exists on a spectrum (better/worse), while safety is binary (safe/unsafe). The framework implements safety as a hard constraint rather than a dimension to trade off, with any safety violation resulting in automatic failure regardless of performance on other dimensions. ^[evaluation-safety-ref.md]

## Meta-Evaluation and System Health

The framework includes systematic evaluation of the evaluation system itself through [[meta-evaluation]], addressing the question of "who watches the watchmen." This meta-evaluation framework includes judge calibration tracking through monthly re-runs of calibration sets, evaluation-production correlation monitoring, [[adversarial-red-teaming]] of the evaluation system, evaluation set coverage analysis, and inter-rater reliability tracking for human evaluation components. ^[evaluation-safety-ref.md]

## Scaling and Organizational Adoption

### Release Risk Matching

The framework provides guidance for matching evaluation rigor to release risk. Different release types require different evaluation depths: hotfixes requiring only Layer 1 (deterministic checks), minor updates using Layers 1-3 (automated evaluation), model version updates employing Layers 1-4 (including human review), and new capability launches utilizing all five layers including user acceptance testing. ^[evaluation-safety-ref.md]

### Cost Optimization

Cost optimization strategies include LLM-judge model routing (using less expensive models for binary safety checks), stratified human review (over-sampling high-risk cases rather than random sampling), incremental evaluation (re-evaluating only affected dimensions for minor changes), and shared evaluation infrastructure across teams to amortize costs. ^[evaluation-safety-ref.md]

The framework positions evaluation as a platform capability rather than research overhead. When positioned as a platform with SLAs and organizational ownership, evaluation systems receive proper engineering investment and stakeholder trust necessary for effective release gating. ^[evaluation-safety-ref.md]

## Continuous Improvement

The framework incorporates feedback loops for continuous improvement, where every production failure becomes a regression test case, evaluation-production correlation is monitored to ensure metrics predict business outcomes, and the evaluation suite grows organically from real failures. This creates a data flywheel where the evaluation system becomes more comprehensive and accurate over time. ^[evaluation-safety-ref.md]

The system includes provisions for evaluation drift detection and correction, recognizing that models change, data distributions shift, policies evolve, and judge models get updated. Monthly calibration re-runs and quarterly fresh human annotations maintain system reliability over time. ^[evaluation-safety-ref.md]
