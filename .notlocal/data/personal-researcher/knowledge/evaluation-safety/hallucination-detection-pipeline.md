---
title: "hallucination-detection-pipeline"
summary: ""
sources:
  - evaluation-safety/evaluation-safety-ref.md
createdAt: 2026-05-28T13:22:38.019499+00:00
updatedAt: 2026-05-28T13:22:38.019499+00:00
---
# Hallucination Detection Pipeline

A **Hallucination Detection Pipeline** is a systematic framework for identifying and preventing factual inaccuracies, fabricated information, and unsupported claims in outputs from large language models (LLMs) and AI agents. These pipelines are critical components of [[evaluation-safety-ref|evaluation and safety systems]] that ensure model outputs are grounded in provided source material and do not contain fabricated information.

## Overview

Hallucination detection requires decomposing the broad concept of "hallucination" into specific, measurable failure types that can be systematically identified and prevented. Unlike general quality evaluation, hallucination detection focuses specifically on factual accuracy and groundedness rather than subjective qualities like usefulness or tone. ^[evaluation-safety-ref.md]

## Types of Hallucinations

Hallucination detection pipelines typically address several distinct categories of factual errors:

**Intrinsic Hallucinations** directly contradict the provided source material. These are detected using Natural Language Inference (NLI) models where the source serves as the premise and the generated claim as the hypothesis, checking for contradiction relationships. ^[evaluation-safety-ref.md]

**Extrinsic Hallucinations** involve claims that are not present in any provided source material - essentially fabricated information. Detection involves claim extraction followed by source lookup to verify whether each claim appears in the provided context. ^[evaluation-safety-ref.md]

**Semantic Hallucinations** subtly distort meaning while using correct words, creating wrong implications from accurate source material. These require LLM-based judges with structured rubrics asking whether claims preserve the original meaning. ^[evaluation-safety-ref.md]

**Entity Hallucinations** present correct facts about wrong entities, such as attributing one person's achievements to another. Detection involves entity extraction and verification against source material. ^[evaluation-safety-ref.md]

**Temporal Hallucinations** involve correct facts presented with wrong timeframes or outdated information. These require timestamp checking against source recency and temporal consistency validation. ^[evaluation-safety-ref.md]

**Numerical Hallucinations** include fabricated statistics, dates, or amounts. Detection uses regex extraction of all numerical claims followed by source verification for each number. ^[evaluation-safety-ref.md]

## Pipeline Architecture

### Core Detection Process

The standard hallucination detection pipeline follows a multi-step process:

1. **Claim Extraction**: Model outputs are decomposed into atomic claims, with one fact per claim to enable granular verification
2. **Source Mapping**: Each extracted claim is mapped to potential supporting source documents
3. **Entailment Checking**: NLI models or LLM judges determine whether sources actually support specific claims
4. **Unsupported Claim Rate Calculation**: The percentage of claims without source support provides the hallucination rate ^[evaluation-safety-ref.md]

### Technical Implementation

**NLI-Based Faithfulness Checking** applies Natural Language Inference models to detect hallucinations by classifying relationships between source material (premise) and generated claims (hypothesis). The classification yields entailment (supported), contradiction (intrinsic hallucination), or neutral (extrinsic hallucination). ^[evaluation-safety-ref.md]

**Model Selection** varies by use case: Cross-encoder NLI models like DeBERTa-v3-large-mnli provide highest accuracy for release evaluation, while bi-encoder approaches offer faster processing for production monitoring. LLM-as-NLI provides flexibility for ambiguous cases but at higher cost. ^[evaluation-safety-ref.md]

## Evaluation Metrics

**FActScore** measures the percentage of atomic facts in model output that are supported by source material. This metric provides granular assessment of factual accuracy at the claim level. ^[evaluation-safety-ref.md]

**Groundedness** (used in RAGAS framework) calculates the fraction of answer sentences that are traceable to retrieved context, focusing on overall output reliability. ^[evaluation-safety-ref.md]

**Hallucination Rate** is calculated as 1 minus FActScore, with enterprise systems typically targeting rates below 5% for acceptable performance. ^[evaluation-safety-ref.md]

## Integration with Evaluation Systems

Hallucination detection pipelines integrate into broader [[evaluation-safety-ref|layered evaluation frameworks]] as automated components that can process high volumes of outputs. They typically operate at Layer 2 (automated benchmarks) and Layer 3 (LLM-as-judge) of five-layer evaluation stacks, providing fast, scalable screening before human review. ^[evaluation-safety-ref.md]

The pipelines must be calibrated against human expert judgment to ensure reliability, with Cohen's κ agreement scores above 0.75 considered acceptable for production use. Regular recalibration prevents drift as models and domains evolve. ^[evaluation-safety-ref.md]

## Failure Modes and Limitations

**Paraphrase Confusion** occurs when NLI models incorrectly classify valid paraphrases as unsupported because they don't match source text verbatim. Mitigation requires semantic similarity thresholds as fallbacks. ^[evaluation-safety-ref.md]

**Multi-hop Claims** that require combining information from multiple sources can be incorrectly flagged as unsupported when each source is checked independently. Solutions involve concatenating related source chunks before NLI checking. ^[evaluation-safety-ref.md]

**Compositional Hallucination** represents a particularly challenging case where individual claims are grounded but their combination creates false impressions. For example, separately true facts about CTR increases and budget decreases might be combined to imply causation that doesn't exist in the source material. ^[evaluation-safety-ref.md]

## Production Considerations

**Confident Hallucination** poses the greatest risk - when models generate fabricated information with high confidence, making it more likely to be believed by users. Mitigation strategies include citation enforcement, confidence calibration, and adversarial training of detection systems specifically targeting high-confidence false claims. ^[evaluation-safety-ref.md]

**Incident Response** for production hallucinations involves immediate blocking of similar input patterns, root cause analysis of detection gaps, addition of failure cases to regression test suites, and process improvements to prevent similar failures. ^[evaluation-safety-ref.md]
