---
title: "Cross-Domain Transfer in SFT"
summary: "The phenomenon where training on one domain (like code) improves performance on seemingly unrelated tasks (like mathematics), suggesting significant knowledge transfer beyond simple topic alignment."
sources:
  - sft-vs-dpo/massive-supervised-fine-tuning-experiments-reveal-how-data-layer-and-training-factors-shape-llm-alignment-quality.md
  - general/massive-supervised-fine-tuning-experiments-reveal-how-data-layer-and-training-factors-shape-llm-alignment-quality.md
createdAt: 2026-05-18T00:30:40.476209+00:00
updatedAt: 2026-05-18T00:30:40.476209+00:00
---
# Cross-Domain Transfer in SFT

Cross-domain transfer in [[Supervised Fine-Tuning (SFT)]] refers to the phenomenon where training data from one domain can improve model performance on tasks in different domains. This challenges the conventional assumption that training data should closely match the target evaluation domain to achieve optimal results.

## Key Findings

Research has revealed that cross-domain transfer effects can be substantial and sometimes counterintuitive. For instance, code generation datasets have been shown to enhance mathematical reasoning capabilities, suggesting significant knowledge transfer beyond simple topic alignment. This indicates that the relationships between training domains and evaluation tasks are more complex than surface-level similarity would suggest. ^[2506.14681v2.md]

The effectiveness of cross-domain transfer appears to vary significantly across different base models. While some training-task synergies persist consistently across all models, others exhibit substantial model-specific variations. This emphasizes the importance of developing model-specific strategies rather than assuming universal transfer patterns. ^[2506.14681v2.md]

## Perplexity as a Predictor

A critical discovery in cross-domain transfer research is that [[Perplexity as SFT Predictor|perplexity]] serves as a more reliable predictor of SFT success than domain similarity. Training data with lower perplexity for the base model consistently leads to greater improvements in downstream performance, even when the content domains appear unrelated. ^[2506.14681v2.md]

This finding challenges traditional approaches that prioritize content similarity between training and evaluation data. Instead, it suggests that the model's existing familiarity with the data format and structure, as measured by perplexity, is more important than topical alignment. Perplexity can be viewed as a practical proxy for compatibility between the model and the data rather than a causal factor itself. ^[2506.14681v2.md]

## Mechanisms and Layer Analysis

Cross-domain transfer appears to be mediated primarily through changes in the model's mid-layers. Research has shown that [[Mid-Layer Weight Change Analysis|mid-layer weight changes]] correlate more strongly with performance improvements than changes in either the top or bottom layers. This pattern remains consistent across multiple models, suggesting a shared mechanism for cross-domain knowledge acquisition. ^[2506.14681v2.md]

[[Intrinsic Dimensionality Analysis]] reveals that the embedding space begins to diverge substantially from the base model at mid-layer positions during SFT. This suggests that these layers actively expand the model's representational subspace, enabling the integration of knowledge from different domains. ^[2506.14681v2.md]

## Implications for Training Strategies

The discovery of robust cross-domain transfer effects has important implications for SFT strategies. Rather than focusing exclusively on domain-matched training data, practitioners should consider:

- Prioritizing datasets with low perplexity relative to the base model
- Including diverse training domains that may provide unexpected benefits
- Monitoring mid-layer changes as indicators of effective knowledge transfer
- Recognizing that model-specific effects require tailored approaches

These findings suggest that effective SFT may benefit from a more holistic approach that considers the model's existing knowledge distribution and capacity for cross-domain generalization. ^[2506.14681v2.md]

## Research Implications

Cross-domain transfer challenges the assumption that dataset similarity to target tasks is the primary factor in SFT effectiveness. The observation that code data helps mathematical reasoning tasks demonstrates that cross-domain benefits can emerge from shared underlying cognitive processes rather than surface-level content overlap. This has led researchers to reconsider how training datasets should be selected and combined for optimal performance across diverse evaluation tasks. ^[2506.14681v2.md]
