---
title: "sft-data-composition-scaling-laws"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-sft.md
createdAt: 2026-05-18T18:36:50.480199+00:00
updatedAt: 2026-05-18T18:36:50.480199+00:00
---
# SFT Data Composition Scaling Laws

**SFT Data Composition Scaling Laws** refer to the empirical relationships governing how the amount and composition of training data affect performance in [[Supervised Fine-Tuning (SFT)]] across different abilities and model sizes. These scaling laws reveal that different capabilities exhibit distinct data requirements and scaling behaviors, with profound implications for multi-skill model development. ^[supervised-fine-tuning-sft.md]

## Overview

Research has demonstrated that SFT effectiveness is highly sensitive to both the absolute amount and composition of training data, with the impact being profoundly ability-dependent. The scaling laws provide quantitative guidance for optimizing data investment strategies across different domains and model sizes. ^[supervised-fine-tuning-sft.md]

## Ability-Specific Scaling Patterns

### Mathematical Reasoning and Code Generation

Mathematical reasoning and code generation abilities exhibit robust, monotonic improvement as the amount of in-domain SFT data increases. Their scaling curves are often log-linear and unbounded within practical data volumes, meaning that continuous scaling of in-domain examples brings continual improvements. ^[supervised-fine-tuning-sft.md]

### General Human-Aligned Abilities

General human-aligned abilities, such as instruction following and alignment, demonstrate a fundamentally different scaling pattern. These abilities exhibit rapid improvement with as little as 1,000 samples, but performance quickly saturates beyond this point, with additional data yielding negligible gains. ^[supervised-fine-tuning-sft.md]

## Data Composition Effects

### Low-Resource Settings

Data composition experiments reveal that mixing SFT data types (mathematics, code, general abilities) is especially beneficial in low-resource settings. When data is limited per skill, mixing different ability data leads to synergistic transfer and improved multi-task performance. ^[supervised-fine-tuning-sft.md]

### High-Resource Settings

As data quantities grow, interference emerges where additional data from unrelated domains can behave as noise, degrading the in-domain generalization of each ability type. The amount of data for a given domain dominates the effect of composition ratio - provided each skill receives sufficient examples, the fraction of each type in the mix becomes secondary. ^[supervised-fine-tuning-sft.md]

## Model Size Dependencies

Scaling experiments across model sizes (7B, 13B, 33B parameters) reveal consistent trends:

- **Larger models consistently outperform smaller models** across all abilities when provided equal amounts of data, reflecting increased capacity to exploit SFT signals
- In extremely low-data regimes, smaller models sometimes outperform due to large-model overfitting, but this advantage vanishes rapidly with additional data
- Each ability demonstrates a unique scaling law, with math and code requiring substantial in-domain data while general abilities plateau early ^[supervised-fine-tuning-sft.md]

## Training Strategy Implications

### Multi-Task Interference

The scaling laws reveal critical challenges in multi-ability training:

- **Multi-task mixing** can impair general ability due to cross-domain interference
- **Sequential SFT** risks [[Catastrophic Forgetting in Fine-Tuning]], where newly trained abilities overwrite previously learned ones ^[supervised-fine-tuning-sft.md]

### Dual-Stage Mixed Fine-Tuning

To address these challenges, research has developed strategies like dual-stage mixed fine-tuning:

- **Stage 1**: Fine-tune on specialized skills (math+code) exclusively
- **Stage 2**: Fine-tune on general ability data plus a small proportion of specialized data as rehearsal ^[supervised-fine-tuning-sft.md]

## Practical Recommendations

Based on the scaling laws, different data investment strategies are recommended:

- **For general abilities**: Prioritize curation and coverage over volume, as performance saturates with few thousand examples
- **For math/code**: Prioritize volume, as continuous scaling brings continual improvements
- **Data mixing**: Manage with respect to absolute quantities per skill rather than arbitrary ratios ^[supervised-fine-tuning-sft.md]

## Quantitative Results

Experimental results demonstrate the effectiveness of scaling law-informed strategies:

| Model | Math (GSM8K) | Code (HumanEval) | General (MT-Bench) |
|-------|--------------|------------------|-------------------|
| 7B, Mixed Sequential | 32.60 | 15.24 | 6.02 |
| 7B, DMT (1/256) | **41.92** | **17.68** | **6.08** |
| 13B, Mixed Sequential | 40.48 | 18.30 | 5.93 |
| 13B, DMT (1/256) | **46.47** | **19.50** | **6.03** |

^[supervised-fine-tuning-sft.md]

## Key Insights

The fundamental insight from SFT data composition scaling laws is that **absolute data quantity for each domain is the primary determinant of ability enhancement**, not the fractional mix. Sharp deterioration occurs only when particular domains become severely underrepresented. ^[supervised-fine-tuning-sft.md]

## Future Directions

Important open areas include extending scaling law frameworks to additional abilities, dynamic adaptation of mixing parameters, and [[Parameter-Efficient Fine-Tuning (PEFT)]] extensions that leverage these scaling insights for more efficient multi-ability model development. ^[supervised-fine-tuning-sft.md]
