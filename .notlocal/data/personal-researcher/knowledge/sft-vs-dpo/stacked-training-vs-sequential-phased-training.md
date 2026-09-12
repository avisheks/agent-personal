---
title: "stacked-training-vs-sequential-phased-training"
summary: ""
sources:
  - sft-vs-dpo/unveiling-the-secret-recipe-a-guide-for-supervised-fine-tuning-small-llms.md
createdAt: 2026-05-18T18:38:34.173762+00:00
updatedAt: 2026-05-18T18:38:34.173762+00:00
---
# Stacked Training vs Sequential Phased Training

**Stacked Training vs Sequential Phased Training** refers to two distinct approaches for organizing training data during [[Supervised Fine-Tuning (SFT)]] of language models. These strategies differ in how they expose the model to diverse datasets across training epochs.

## Training Strategies

### Stacked Training
Stacked training exposes the model to the entire dataset in each epoch, allowing simultaneous learning from all data types and domains. This approach maintains consistent exposure to the full diversity of training examples throughout the fine-tuning process. ^[2412.13337v1.md]

### Sequential Phased Training
Sequential phased training partitions the dataset into distinct phases, with the model learning from different subsets of data in sequence. Common partitioning strategies include splitting by task type, difficulty level, or response length. ^[2412.13337v1.md]

## Performance Comparison

### General Performance
Experimental results consistently show that stacked training achieves better or comparable performance to phased training across different batch sizes (128 and 4,000 samples). On MTBench evaluations, stacked training outperformed phased training by 0.01 points using optimal hyperparameter configurations. Similar improvements of 0.01 points were observed on MMLU benchmarks. ^[2412.13337v1.md]

### Sample Efficiency
Stacked training demonstrates superior sample efficiency compared to phased training. The approach reaches optimal performance points using fewer training samples, making it more computationally efficient. This efficiency advantage stems from the model's exposure to the entire dataset diversity in each epoch, even at smaller batch sizes. ^[2412.13337v1.md]

### Batch Size Independence
Contrary to initial hypotheses that stacked training might underperform at smaller batch sizes due to insufficient gradient stability, results show consistent performance advantages regardless of batch size. The performance difference between strategies remains stable across both small (128) and large (4,000) batch configurations. ^[2412.13337v1.md]

## Difficulty-Based Partitioning

### Experimental Setup
Researchers tested whether phased training might be effective when phases are split based on difficulty, using answer length as a proxy for complexity:
- **Phase I**: Bottom 50% of data containing short sentences
- **Phase II**: Top 50% of data containing long sentences, plus 1% subset of short sentences as replay buffer ^[2412.13337v1.md]

### Results
Even with careful difficulty-based partitioning, phased training showed no significant improvement over stacked training. Both approaches performed similarly across comprehensive benchmarks, with stacked training maintaining slight performance advantages and superior sample efficiency. ^[2412.13337v1.md]

## Cross-Architecture Validation

### Model Families Tested
The comparative analysis extended across multiple model architectures and sizes:
- Granite 7B and 3B models
- Mistral 7B model  
- LLaMA 3B model ^[2412.13337v1.md]

### Consistent Findings
Results demonstrate that stacked training advantages generalize across different model families, architectures, and sizes. The approach consistently outperforms phased training on benchmarks including MTBench, MMLU, GSM8K, ARC, and Open LLM Leaderboard v2 metrics. ^[2412.13337v1.md]

## Domain-Specific Applications

### Math, Reasoning, and Code (MRC) Dataset
Testing on specialized domain datasets confirmed the generalizability of findings. Using a Math, Reasoning, and Code dataset, stacked training maintained performance advantages over phased training across domain-specific evaluation metrics including GSM8K, ARC, MATH, and MuSR benchmarks. ^[2412.13337v1.md]

## Training Dynamics

### Gradient Behavior
Stacked training with larger batch sizes produces lower gradient norms and higher training loss values, which correlate with better downstream performance. This pattern suggests the model settles into flatter, more generalizable regions of the loss landscape while maintaining broader exploration to reduce overfitting risk. ^[2412.13337v1.md]

### Stability Mechanisms
The superior performance of stacked training appears to result from its exposure to diverse data types within each batch, reducing gradient variance and promoting stable parameter updates. This diversity helps maintain pre-trained knowledge while enabling effective adaptation to new tasks. ^[2412.13337v1.md]

## Learning Rate Interactions

### Optimal Configuration
Experiments across different model architectures consistently show that lower learning rates (2×10⁻⁵ for Granite models, 1×10⁻⁶ for Mistral models) yield better performance regardless of batch size. This finding contradicts training-from-scratch recommendations that suggest higher learning rates for larger batch sizes. ^[2412.13337v1.md]

### Fine-Tuning Considerations
The preference for lower learning rates in fine-tuning stems from starting at a pre-trained local minimum in the loss landscape. Lower learning rates help avoid moving too far from this minimum, preventing [[Catastrophic Forgetting in Fine-Tuning]] while allowing effective adaptation to new data. ^[2412.13337v1.md]

## Practical Implications

### Implementation Advantages
Stacked training offers practical benefits beyond performance improvements:
- Simplified training pipeline without phase transition management
- Reduced computational overhead from phase switching
- Elimination of checkpoint selection for optimal phase transitions ^[2412.13337v1.md]

### Hyperparameter Robustness
The effectiveness of stacked training appears independent of specific hyperparameter choices, maintaining advantages across different learning rates and batch size configurations. This robustness makes it a reliable default choice for [[Supervised Fine-Tuning (SFT)]] implementations. ^[2412.13337v1.md]

### Generalization Across Domains
Results from domain-specific datasets (Math, Reasoning, and Code) demonstrate that stacked training advantages extend beyond general instruction-following tasks to specialized applications, supporting broad applicability in fine-tuning scenarios. ^[2412.13337v1.md]
