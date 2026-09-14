---
title: "cross-lingual-sft-transfer"
summary: ""
sources:
  - sft-vs-dpo/2506.md
createdAt: 2026-05-21T01:46:06.515061+00:00
updatedAt: 2026-05-21T01:46:06.515061+00:00
---
# Cross-Lingual SFT Transfer

Cross-Lingual SFT Transfer refers to the phenomenon where [[Supervised Fine-Tuning (SFT)]] conducted exclusively in one language produces performance improvements on evaluation tasks in different languages, even when no multilingual training data is used during fine-tuning. This transfer effect demonstrates that instruction-following capabilities learned through SFT can generalize across linguistic boundaries without explicit cross-lingual supervision. ^[2506.md]

## Overview

Cross-lingual transfer in SFT occurs when models fine-tuned exclusively on English instruction data show improved performance on non-English evaluation benchmarks. Research has demonstrated that this transfer is robust and occurs consistently across different model architectures and language pairs, suggesting that the underlying mechanisms of instruction-following are largely language-independent. The phenomenon has been observed across models with different pre-training languages, including English, Chinese, and Japanese variants. ^[2506.md]

The strength of cross-lingual transfer appears to be driven more by content overlap between benchmarks than by surface-level language similarity. This indicates that the conceptual knowledge and reasoning patterns learned during SFT transfer effectively across languages, even when the linguistic surface forms differ significantly. ^[2506.md]

## Empirical Evidence

Large-scale experiments involving multiple base models trained on English-only SFT datasets have revealed strong correlations between performance gains on English benchmarks and corresponding improvements on Chinese and Japanese variants of the same evaluation tasks. Specifically, performance gains on MMLU (English) show substantial positive correlations with gains on MMLU-zh (Chinese) and MMLU-jp (Japanese). ^[2506.md]

When models are grouped by their pre-training language (English, Chinese, Japanese), pairwise correlations between MMLU-family scores across all three languages demonstrate strong positive relationships. This pattern holds even though every SFT run used exclusively English training data, indicating robust zero-shot transfer capabilities. The correlations remain substantial across different model families, suggesting that cross-lingual transfer is a general property of instruction-following rather than an artifact of specific architectures. ^[2506.md]

## Mechanisms and Underlying Factors

The effectiveness of cross-lingual SFT transfer suggests that instruction-following capabilities operate at a conceptual level that transcends specific linguistic representations. The transfer appears to be mediated by shared semantic and reasoning structures rather than surface-level linguistic features. This aligns with findings that [[perplexity-as-sft-predictor]] serves as a stronger indicator of transfer success than direct semantic similarity between training and evaluation data. ^[2506.md]

Analysis of [[mid-layer-weight-change-analysis]] during SFT reveals that the most significant modifications occur in middle layers of the network, which may be where language-independent conceptual representations are formed and modified. These mid-layer changes show strong correlations with performance improvements across languages, suggesting that the neural mechanisms underlying cross-lingual transfer are localized to specific architectural components. ^[2506.md]

The phenomenon appears to be particularly effective for knowledge-based tasks that rely on factual information and logical reasoning, where the underlying cognitive processes are similar across languages. However, the extent of transfer may vary for tasks requiring language-specific cultural knowledge or linguistic nuances. ^[2506.md]

## Relationship to Model Architecture

Cross-lingual transfer effectiveness varies somewhat across different model families, but the general pattern remains consistent. Models within the same architectural family (such as Llama variants adapted for different languages) tend to show similar cross-lingual transfer patterns, suggesting that the base architecture influences how effectively instruction-following knowledge transfers across languages. ^[2506.md]

The phenomenon occurs across models with different pre-training languages, indicating that the capacity for cross-lingual transfer is not limited to models originally trained on multilingual data. Even models primarily trained on a single language can effectively transfer instruction-following capabilities to other languages through English-only SFT. This suggests that the multilingual capabilities emerge from the shared conceptual structures learned during pre-training rather than explicit multilingual supervision. ^[2506.md]

## Training Data Properties and Transfer Quality

Research has shown that the quality of cross-lingual transfer is influenced by the same factors that affect monolingual SFT performance. Training datasets with lower [[perplexity-as-sft-predictor]] relative to the base model tend to produce stronger cross-lingual transfer effects, while factors such as average token length or surface-level semantic similarity between training and evaluation data show weaker correlations with transfer success. ^[2506.md]

The robustness of cross-lingual transfer across different training datasets suggests that the phenomenon is not dependent on specific types of instruction data, but rather emerges from the general process of learning to follow instructions in a structured format. This has important implications for the design of multilingual instruction-tuning datasets. ^[2506.md]

## Implications for Training Strategy

Cross-lingual SFT transfer has important implications for multilingual model development. It suggests that high-quality English instruction data can serve as an effective foundation for improving model performance across multiple languages, potentially reducing the need for extensive multilingual SFT datasets. This finding can significantly reduce the cost and complexity of developing multilingual instruction-following models. ^[2506.md]

However, the extent and quality of cross-lingual transfer may vary depending on the specific tasks and languages involved. While the transfer is robust for knowledge-based tasks like MMLU variants, its effectiveness for more language-specific tasks or those requiring cultural knowledge remains an area for further investigation. Practitioners should consider the specific requirements of their target languages and tasks when relying on cross-lingual transfer. ^[2506.md]

## Relationship to Other SFT Phenomena

Cross-lingual transfer demonstrates similar patterns to other forms of [[cross-domain-transfer-in-sft]], where knowledge learned in one domain benefits performance in related but distinct domains. The phenomenon also relates to findings about [[dataset-task-synergy-patterns]], where certain training datasets provide benefits that extend beyond their apparent domain boundaries. ^[2506.md]

The effectiveness of cross-lingual transfer supports broader observations about the generalizability of instruction-following capabilities learned through SFT. This connects to research on [[sft-embedding-space-visualization]], which shows how fine-tuning modifies model representations in ways that can benefit multiple downstream applications. ^[2506.md]

## Limitations and Future Directions

Current research on cross-lingual SFT transfer has primarily focused on a limited set of languages and evaluation tasks, particularly those with substantial representation in multilingual pre-training data. The generalizability of these findings to a broader range of languages, particularly those with different writing systems, linguistic structures, or limited pre-training representation, requires further investigation. ^[2506.md]

Additionally, while cross-lingual transfer is effective for certain types of tasks, comprehensive investigation into how it affects highly specialized tasks or those requiring deep cultural knowledge remains a subject for future work. The development of more diverse multilingual instruction-tuning datasets could provide additional insights into optimizing cross-lingual transfer effects and understanding its boundaries. ^[2506.md]

Future research directions include investigating the optimal balance between English-only and multilingual training data, understanding the role of pre-training language distribution in transfer effectiveness, and developing methods to enhance cross-lingual transfer for underrepresented languages and specialized domains. The relationship between cross-lingual transfer and other fine-tuning phenomena such as [[catastrophic-forgetting-in-fine-tuning]] also warrants further exploration. ^[2506.md]
