---
title: "sample-efficiency-in-fine-tuning"
summary: ""
sources:
  - sft-vs-dpo/unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md
createdAt: 2026-05-18T18:36:34.229781+00:00
updatedAt: 2026-05-18T18:36:34.229781+00:00
---
# Sample Efficiency in Fine-Tuning

Sample efficiency in fine-tuning refers to the ability of a model to achieve optimal performance while using fewer training samples during the [[Supervised Fine-Tuning (SFT)]] process. This concept is crucial for reducing computational costs and training time while maintaining or improving model quality.

## Training Strategy Impact on Sample Efficiency

Research comparing different training approaches has revealed significant differences in sample efficiency between stacked and sequential phased training methods. Stacked training, which exposes the model to the entire dataset in each epoch, demonstrates superior sample efficiency compared to phased training approaches that partition data into sequential phases. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

In comparative studies using MTBench evaluations, stacked training consistently achieved better performance points with fewer samples required to reach optimal results. The sample efficiency advantage of stacked training applies even when phased training uses difficulty-based partitioning, where datasets are split based on response length as a proxy for complexity. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

## Hyperparameter Configuration Effects

### Batch Size Impact

Larger batch sizes contribute significantly to improved sample efficiency in fine-tuning. Experiments across different batch sizes (128, 3,840, 4,000, and 7,680 samples) consistently show that larger batches lead to better sample efficiency outcomes. This improvement occurs because larger batch sizes provide more stable gradient estimates by averaging over more samples, allowing for more effective progress with fewer total training steps. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

The larger batch size likely improves performance by increasing data diversity within each batch, covering a range of tasks, skills, and knowledge. This diversity reduces gradient variance, promoting stable updates and helping the model retain pre-trained knowledge without significant forgetting. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

### Learning Rate Considerations

Lower learning rates demonstrate better sample efficiency in fine-tuning scenarios. Across various batch sizes, a learning rate of 2×10^-5 consistently resulted in better or comparable performance compared to higher learning rates. This finding contrasts with training from scratch, where higher learning rates are often beneficial with larger batch sizes. The difference arises because fine-tuning starts from a pre-trained model at a local minimum, requiring careful parameter updates to avoid [[Catastrophic Forgetting in Fine-Tuning]]. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

Large batches yield more stable gradient estimates by averaging over more samples, which allows effective progress at lower learning rates without risking instability. Higher learning rates with large batches can cause the model to take larger steps that risk moving too far from the pre-trained parameters, potentially overshooting the minima. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

## Cross-Architecture Generalization

Sample efficiency improvements generalize across different model architectures and sizes. Testing on Mistral 7B, Granite 3B, and LLaMA 3B models confirms that the principles of improved sample efficiency through larger batch sizes and appropriate learning rates hold consistently. For the Mistral 7B model, a batch size of 4,000 combined with a learning rate of 1×10^-6 yielded optimal sample efficiency results. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

The correlation between early training dynamics and final downstream performance is consistent across different model architectures, suggesting that sample efficiency principles are broadly applicable rather than model-specific. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

## Domain-Specific Applications

Sample efficiency benefits extend to domain-specific fine-tuning scenarios. When applied to Math, Reasoning, and Code (MRC) datasets, the same principles that improve sample efficiency on general datasets continue to provide advantages. Stacked training with larger batch sizes maintains superior sample efficiency compared to phased approaches even in specialized domains. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

These findings demonstrate that recommendations regarding training strategies and hyperparameters generalize to domain-specific datasets, supporting their applicability in specialized fine-tuning scenarios. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

## Training Dynamics Indicators

Early training dynamics serve as reliable predictors of sample efficiency outcomes. Models that exhibit lower gradient norms and higher loss values during early training phases typically achieve better final performance with fewer samples. This pattern appears consistently across different model architectures and sizes, providing practitioners with early indicators of training efficiency. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

The correlation between these training dynamics and sample efficiency suggests that models settling into flatter, more generalizable regions of the loss landscape require fewer samples to achieve optimal performance while maintaining better generalization capabilities. The lower gradient norm suggests that the model is settling into a flatter, more generalizable region of the loss landscape, while the higher loss indicates reduced risk of overfitting by maintaining a broader exploration. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]

## Practical Implications

For practitioners seeking to optimize sample efficiency in fine-tuning:

- Use stacked training approaches that expose models to the entire dataset in each epoch
- Employ larger batch sizes when computationally feasible
- Start with lower learning rates and adjust incrementally based on empirical results
- Monitor early training dynamics as predictors of final sample efficiency

These principles apply across different model families, architectures, and specialized domains, making them broadly applicable for efficient fine-tuning workflows. ^[unveiling-secret-recipe-guide-supervised-fine-tuning-small-llms.md]
