---
title: "batch-size-learning-rate-relationship"
summary: ""
sources:
  - sft-vs-dpo/unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md
createdAt: 2026-05-18T18:39:12.613653+00:00
updatedAt: 2026-05-18T18:39:12.613653+00:00
---
# Batch Size Learning Rate Relationship

The **Batch Size Learning Rate Relationship** refers to the interdependent connection between batch size and learning rate in training neural networks, particularly in the context of [[Supervised Fine-Tuning (SFT)]] of large language models. This relationship challenges conventional wisdom about scaling learning rates with batch sizes when fine-tuning pre-trained models.

## Core Relationship

### Traditional Scaling vs Fine-Tuning

In training from scratch, conventional wisdom suggests that larger batch sizes necessitate higher learning rates. The premise is that with a larger batch size, the model processes more samples before each gradient step, potentially benefiting from a higher learning rate to make more significant updates and maintain gradient variance when compared to smaller batch sizes. Additionally, since larger batches result in fewer gradient steps over the same number of epochs, increasing the learning rate might improve training efficiency. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

However, for fine-tuning pre-trained models, research indicates that lower learning rates are preferable regardless of batch size to minimize [[Catastrophic Forgetting]] and maintain downstream performance. This discrepancy arises because, starting from a pre-trained model at a local minimum in the loss landscape, the goal is to avoid moving too far from that minimum during fine-tuning to prevent forgetting what was learned during pre-training. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

### Stabilization Effects

Larger batch sizes and lower learning rates reduce stochasticity in the optimization process, leading to smaller, more stable updates that help the model stay closer to the pre-trained parameters while effectively adapting to new data. Large batches yield more stable gradient estimates by averaging over more samples, which allows effective progress at lower learning rates without risking instability. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

Higher learning rates with large batches can cause the model to take larger steps that risk moving too far from the pre-trained parameters, potentially overshooting the minima. Using larger batch sizes and/or lower learning rates helps preserve the pre-trained knowledge while allowing the model to adapt to new tasks. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

## Empirical Findings

### Consistent Performance Across Batch Sizes

Research demonstrates that the lowest learning rate of 2×10^-5 yielded the best performance across different batch sizes. Experiments comparing models trained with different learning rates across batch sizes of 128, 3,840, and 7,680 samples showed that regardless of batch size, the lower learning rate of 2×10^-5 consistently resulted in better or comparable performance on both MMLU and MTBench benchmarks. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

For instance, with a batch size of 128, performances were similar for both learning rates. For larger batch sizes of 3,840 and 7,680, the 2×10^-5 learning rate performed on par or better than higher learning rates. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

### Architecture-Specific Adaptations

The relationship holds across different model architectures. For the Mistral 7B model, a batch size of 4k combined with a learning rate of 1×10^-6 yields the best results, as higher batch sizes and lower learning rates have a stabilizing effect on training. Conversely, increasing the learning rate or reducing the batch size negatively impacts downstream performance. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

## Training Dynamics Indicators

### Gradient Norm and Loss Patterns

Effective batch size and learning rate combinations exhibit specific training dynamics patterns. For the most effective learning rates, the gradient norm starts at its lowest value and increases towards the end of training. Despite the higher gradient norm in later stages, the associated loss remains higher throughout training, which suggests that higher loss values may be an indicator of better model generalization. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

The lower gradient norm in larger batch size settings suggests that the model is settling into a flatter, more generalizable region of the loss landscape, while the higher loss indicates reduced risk of overfitting by maintaining broader exploration. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

## Practical Implications

### Hyperparameter Selection Strategy

A systematic methodology for identifying optimal hyperparameters involves starting with a baseline and iteratively testing slightly higher and lower values to detect performance improvements. For learning rate optimization, practitioners should begin the search at established baselines (such as 2×10^-5) and adjust incrementally to refine the optimal range based on empirical results. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

### Batch Size Benefits

Larger batch sizes improve performance by increasing data diversity within each batch, covering a range of tasks, skills, and knowledge. This diversity reduces gradient variance, promoting stable updates and helping the model retain pre-trained knowledge without significant forgetting. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]

## Cross-Model Generalization

The batch size learning rate relationship generalizes across different model families, architectures, and sizes. Findings have been validated on Granite 7B, Granite 3B, Mistral 7B, and LLaMA 3B models, demonstrating that the correlation between early training dynamics and final performance holds consistently across different model architectures and sizes. ^[unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md]
