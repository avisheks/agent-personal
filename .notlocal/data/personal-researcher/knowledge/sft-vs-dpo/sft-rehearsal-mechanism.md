---
title: "sft-rehearsal-mechanism"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:38:05.132730+00:00
updatedAt: 2026-05-18T18:38:05.132730+00:00
---
# SFT Rehearsal Mechanism

The **SFT Rehearsal Mechanism** is a training strategy used in [[Supervised Fine-Tuning (SFT)]] to prevent [[Catastrophic Forgetting in Fine-Tuning]] when adapting large language models to multiple abilities simultaneously. This mechanism involves incorporating a small proportion of previously learned task data during subsequent training phases to maintain performance across different domains. ^[supervised-fine-tuning-sft.md]

## Overview

The rehearsal mechanism addresses a critical challenge in multi-ability SFT: when models are trained sequentially on different tasks or when general alignment data is added after specialized training, previously acquired capabilities can be degraded or lost entirely. This phenomenon is particularly problematic when training models on diverse skill sets such as mathematical reasoning, code generation, and general instruction following. ^[supervised-fine-tuning-sft.md]

## Implementation in Dual-Stage Mixed Fine-Tuning

The most prominent application of the SFT rehearsal mechanism is found in the **Dual-Stage Mixed Fine-Tuning (DMT)** strategy, which operates in two distinct phases:

### Stage 1: Specialized Training
Models are first fine-tuned exclusively on specialized skills such as mathematical reasoning and code generation, establishing strong performance in these targeted domains. ^[supervised-fine-tuning-sft.md]

### Stage 2: Rehearsal-Enhanced General Training
In the second stage, models are trained on general ability data while simultaneously incorporating a small fraction (typically k = 1/256) of the specialized data from Stage 1. This small proportion of specialized examples acts as the rehearsal mechanism, preventing the overwriting of previously learned code and mathematical capabilities during general alignment training. ^[supervised-fine-tuning-sft.md]

## Empirical Results

Quantitative experiments demonstrate the effectiveness of the rehearsal mechanism across different model sizes:

| Model Size | Training Strategy | Math (GSM8K) | Code (HumanEval) | General (MT-Bench) |
|------------|-------------------|--------------|------------------|-------------------|
| 7B | Mixed Sequential | 32.60 | 15.24 | 6.02 |
| 7B | DMT with Rehearsal (1/256) | **41.92** | **17.68** | **6.08** |
| 13B | Mixed Sequential | 40.48 | 18.30 | 5.93 |
| 13B | DMT with Rehearsal (1/256) | **46.47** | **19.50** | **6.03** |

These results show that the rehearsal mechanism enables models to maintain high performance across all abilities, outperforming both naive multi-task and sequential training methods. ^[supervised-fine-tuning-sft.md]

## Key Characteristics

### Proportion Sensitivity
The effectiveness of the rehearsal mechanism depends critically on the proportion of rehearsal data included. Setting the rehearsal fraction too high shifts the training dynamics back towards interference and forgetting, while setting it to zero results in catastrophic forgetting of specialized abilities. The optimal proportion is typically around 1/256 of the total training data in the rehearsal stage. ^[supervised-fine-tuning-sft.md]

### Domain-Specific Retention
Experimental analysis reveals that mathematical reasoning capabilities remain more distinct in the model's representation space after applying the rehearsal mechanism, compared to code generation and general abilities which show more entanglement. This geometric separation helps explain the observed interference patterns and the mechanism's effectiveness. ^[supervised-fine-tuning-sft.md]

### Sequential Training Effects
Without the rehearsal mechanism, sequential SFT exhibits a recency bias where the last trained ability is preferentially retained while prior abilities are diminished. The rehearsal mechanism mitigates this effect by maintaining active representations of all trained capabilities. ^[supervised-fine-tuning-sft.md]

## Applications and Recommendations

The SFT rehearsal mechanism is particularly recommended for:

- Multi-ability language model training where diverse skills must be preserved
- Sequential fine-tuning scenarios where new capabilities are added to existing models
- Scenarios involving specialized domains (mathematics, code) combined with general instruction following

The mechanism is most effective when the rehearsal proportion is set to a small, non-zero fraction, typically around 1/256 of the total training data in the rehearsal stage. ^[supervised-fine-tuning-sft.md]

## Future Directions

Open research areas for the SFT rehearsal mechanism include extending the framework to additional abilities beyond mathematics and coding, developing dynamic adaptation methods for the rehearsal proportion parameter, and exploring [[Parameter-Efficient Fine-Tuning (PEFT)]] implementations of the rehearsal strategy. ^[supervised-fine-tuning-sft.md]
