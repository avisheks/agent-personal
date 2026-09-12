---
title: "RobustFT Framework"
summary: "A noise-robust supervised fine-tuning framework designed to enhance Large Language Model performance in the presence of noisy training data through multi-expert collaborative noise detection, context-enhanced relabeling, and response entropy-based data selection."
sources:
  - fine-tuning-noisy-labels/2412-14922-robustft-robust-supervised-fine-tuning-for-large-language-models-under-noisy-response.md
  - fine-tuning-noisy-labels/robustft-readme-md-at-main-luo-junyu-robustft-github.md
createdAt: 2026-05-20T02:59:22.253379+00:00
updatedAt: 2026-05-20T02:59:22.253379+00:00
---
# RobustFT Framework

**RobustFT** is a noise-robust [[Supervised Fine-Tuning (SFT)]] framework designed to enhance the performance of Large Language Models (LLMs) when training data contains noisy responses. The framework addresses the challenge that noisy training data can significantly impact model performance during domain adaptation. ^[RobustFT/README.md]

## Overview

[[Supervised Fine-Tuning (SFT)]] is essential for adapting LLMs to specific domains, but the presence of noisy training data poses significant challenges to model performance. RobustFT provides a comprehensive solution to this problem through a multi-stage approach that detects, corrects, and filters noisy data before fine-tuning. ^[RobustFT/README.md]

## Core Components

### Multi-Expert Collaborative Noise Detection

RobustFT implements a multi-expert collaborative system with inference-enhanced models to identify noisy responses in training data. This component serves as the first line of defense against data quality issues. ^[RobustFT/README.md]

### Context-Enhanced Relabeling Strategy

The framework employs a context-enhanced strategy for reliable annotation generation, which helps correct identified noisy labels rather than simply discarding them. This denoising approach maximizes the utility of available training data. ^[RobustFT/README.md]

### Response Entropy-Based Data Selection

RobustFT features response entropy-based filtering for high-quality sample selection. This mechanism helps identify and prioritize the most reliable training examples based on their entropy characteristics. ^[RobustFT/README.md]

## Technical Implementation

The framework is built around three key processes:

- **Noise Detection**: Uses multiple expert models to collaboratively identify potentially noisy responses
- **Denoising**: Applies context-enhanced relabeling to generate more reliable annotations
- **Data Selection**: Employs entropy-based metrics to filter and select high-quality training samples

^[RobustFT/README.md]

## Dataset Support

RobustFT supports multiple datasets for evaluation and training, including:

- ARC (AI2 Reasoning Challenge)
- DROP (Discrete Reasoning Over Paragraphs)
- FPB (Financial PhraseBank)
- MMLU (Massive Multitask Language Understanding)
- PubMedQA (PubMed Question Answering)

^[RobustFT/README.md]

## Integration with Existing Tools

The framework is designed to work with existing fine-tuning infrastructures. It integrates with the [[VLLM Inference Engine]] for model serving and can be used with frameworks like Llama-Factory for the actual fine-tuning process. The framework generates denoised datasets in standard formats that can be consumed by popular training frameworks. ^[RobustFT/README.md]

## Workflow

The typical RobustFT workflow involves:

1. Running inference models using [[VLLM Inference Engine]]
2. Applying the RobustFT noise detection and correction pipeline
3. Converting the cleaned data to standard training formats
4. Performing [[Supervised Fine-Tuning (SFT)]] using the denoised dataset
5. Evaluating the resulting model performance

^[RobustFT/README.md]
