---
title: "[2305.18290] Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
source: "https://arxiv.org/abs/2305.18290"
ingestedAt: "2026-05-22T11:54:16Z"
---
[Submitted on 29 May 2023 (

[v1](https://arxiv.org/abs/2305.18290v1)

), last revised 29 Jul 2024 (this version, v3)]

# Title:Direct Preference Optimization: Your Language Model is Secretly a Reward Model

View a PDF of the paper titled Direct Preference Optimization: Your Language Model is Secretly a Reward Model, by Rafael Rafailov and 5 other authors

[View PDF](/pdf/2305.18290) [HTML (experimental)](https://arxiv.org/html/2305.18290v3)

> Abstract:While large-scale unsupervised language models (LMs) learn broad world knowledge and some reasoning skills, achieving precise control of their behavior is difficult due to the completely unsupervised nature of their training. Existing methods for gaining such steerability collect human labels of the relative quality of model generations and fine-tune the unsupervised LM to align with these preferences, often with reinforcement learning from human feedback (RLHF). However, RLHF is a complex and often unstable procedure, first fitting a reward model that reflects the human preferences, and then fine-tuning the large unsupervised LM using reinforcement learning to maximize this estimated reward without drifting too far from the original model. In this paper we introduce a new parameterization of the reward model in RLHF that enables extraction of the corresponding optimal policy in closed form, allowing us to solve the standard RLHF problem with only a simple classification loss. The resulting algorithm, which we call Direct Preference Optimization (DPO), is stable, performant, and computationally lightweight, eliminating the need for sampling from the LM during fine-tuning or performing significant hyperparameter tuning. Our experiments show that DPO can fine-tune LMs to align with human preferences as well as or better than existing methods. Notably, fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations, and matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train. 

## Submission history

From: Archit Sharma [

[view email](/show-email/8595333e/2305.18290)

] 

**[[v1]](/abs/2305.18290v1)**

Mon, 29 May 2023 17:57:46 UTC (982 KB) 

**[[v2]](/abs/2305.18290v2)**

Wed, 13 Dec 2023 18:48:48 UTC (983 KB) 

**[v3]**

Mon, 29 Jul 2024 22:26:36 UTC (999 KB)