---
title: "Five-Minute Training Budget"
summary: "A fixed wall-clock time constraint for each experiment that forces optimization within realistic compute limits and ensures results are comparable within a single hardware setup."
sources:
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:03:45.640001+00:00
updatedAt: 2026-05-25T16:03:45.640001+00:00
---
# Five-Minute Training Budget

A **Five-Minute Training Budget** is a constraint-based approach to machine learning experimentation where each training run is limited to exactly five minutes of wall-clock time on the available hardware. This approach enables rapid iteration cycles and systematic exploration of model configurations within a fixed computational envelope.

## Overview

The five-minute training budget serves as a fundamental constraint in automated ML research systems, particularly in frameworks like Karpathy's autoresearch. Rather than optimizing for absolute model performance, this approach optimizes for the best possible performance achievable within the strict time limit, creating a standardized unit of computational work that enables direct comparison across different experimental configurations. ^[karpathy-autoresearch-explained.md]

The constraint transforms the research question from "what is the best possible model?" to "what is the best model we can train in five minutes?" This reframing makes systematic experimentation tractable for researchers with limited computational resources while maintaining scientific rigor through consistent evaluation conditions. ^[karpathy-autoresearch-explained.md]

## Implementation in Automated Research

In automated research loops, the five-minute budget enables an AI agent to run sequential experiments throughout an overnight session. Each experiment follows a standardized cycle: the agent modifies training code, initiates a five-minute training run, evaluates the result using a single metric, and either commits the improvement or reverts the change before proceeding to the next hypothesis. ^[karpathy-autoresearch-explained.md]

This approach has demonstrated practical effectiveness in real deployments. Karpathy's own experiments using this constraint resulted in approximately 700 experiments over two days, yielding around 20 genuine improvements that collectively reduced training time to achieve GPT-2-quality results by 11%. Similarly, Shopify's CEO used the same pattern to develop a 0.8B parameter model that outperformed a hand-tuned 1.6B baseline by 19%. ^[karpathy-autoresearch-explained.md]

## Evaluation and Scoring

The five-minute budget works in conjunction with hardware-agnostic evaluation metrics. In autoresearch implementations, experiments are scored using validation bits per byte (val_bpb), which measures encoding efficiency independently of vocabulary size. This metric choice ensures that results remain comparable across different architectural changes, including modifications to tokenizers, layer counts, or attention mechanisms. ^[karpathy-autoresearch-explained.md]

The wall-clock nature of the time constraint means that optimal configurations discovered on different hardware will differ, which is intentional rather than a limitation. An optimal configuration for an H100 GPU will naturally differ from one optimized for an RTX 4090, reflecting the reality that practical ML deployment must account for available computational resources. ^[karpathy-autoresearch-explained.md]

## Design Constraints and Trade-offs

The five-minute budget operates within a broader constraint system designed to maintain experimental validity. The training codebase is typically limited to around 630 lines to ensure an AI agent can maintain coherent understanding of the full system. Data pipelines and evaluation functions remain locked throughout the experimental process to prevent gaming of the scoring metric. ^[karpathy-autoresearch-explained.md]

Within the time constraint, researchers must balance model size, architectural complexity, and training efficiency. More layers and wider embeddings generally produce higher quality results but consume more computational resources. The five-minute limit forces explicit consideration of these trade-offs, leading to architectures optimized for efficiency rather than simply maximizing parameters. ^[karpathy-autoresearch-explained.md]

## Applications and Use Cases

The five-minute training budget particularly benefits small teams and individual researchers who lack access to large compute clusters. Instead of requiring parallel GPU resources to run multiple experiments simultaneously, the sequential approach with short iterations enables systematic exploration using a single GPU over extended periods. ^[karpathy-autoresearch-explained.md]

This constraint model proves especially valuable for domain-specific model development, where standard hyperparameters from public repositories may not transfer effectively to new datasets or hardware configurations. The systematic exploration within the five-minute budget helps identify configurations optimized for specific use cases rather than general benchmarks. ^[karpathy-autoresearch-explained.md]

## Related Concepts

The five-minute training budget connects to several broader concepts in ML research methodology. It exemplifies [[parameter-efficient-fine-tuning-peft]] principles by forcing optimization within resource constraints. The approach aligns with [[supervised-fine-tuning-sft]] workflows where rapid iteration on smaller models can yield insights applicable to larger systems. The constraint-based methodology also relates to [[mixture-of-experts-moe]] architectures, where computational efficiency becomes a primary design consideration.
