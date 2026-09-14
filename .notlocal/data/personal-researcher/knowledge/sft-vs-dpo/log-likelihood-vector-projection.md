---
title: "log-likelihood-vector-projection"
summary: ""
sources:
  - sft-vs-dpo/2506.md
createdAt: 2026-05-21T01:45:42.126878+00:00
updatedAt: 2026-05-21T01:45:42.126878+00:00
---
# Log-Likelihood Vector Projection

**Log-Likelihood Vector Projection** is a technique for mapping fine-tuned language models into a common latent space to enable comparative analysis of their training dynamics and representational properties. This method allows researchers to visualize and compare diverse models that have undergone different training procedures within a unified coordinate system.

## Overview

Log-likelihood vector projection creates a high-dimensional representation of each model by computing token-level log-likelihoods across a standardized set of evaluation tasks. These vectors are then projected into a lower-dimensional space using dimensionality reduction techniques, typically t-SNE, to create interpretable visualizations of model relationships and training trajectories. ^[2506.md]

The technique enables researchers to analyze how different factors—such as base model architecture, training datasets, fine-tuning methods, and training duration—influence the final model representations in a systematic way. ^[2506.md]

## Methodology

### Vector Construction

For each model being analyzed, researchers construct a log-likelihood vector by:

1. Randomly sampling a fixed number of questions from each evaluation task (e.g., 150 questions from each of 13 evaluation tasks)
2. Computing token-level log-likelihoods for these samples using the model
3. Concatenating these log-likelihoods into a single high-dimensional vector (e.g., 1,950 dimensions)

This process creates a standardized representation that captures how each model assigns probabilities to the same set of evaluation content. ^[2506.md]

### Dimensionality Reduction

The high-dimensional log-likelihood vectors are then embedded into a lower-dimensional space (typically two dimensions) using t-SNE or similar techniques. This projection preserves local neighborhood relationships while making the data suitable for visualization and analysis. ^[2506.md]

## Key Findings from Large-Scale Analysis

Research using log-likelihood vector projection has revealed several important patterns in [[Supervised Fine-Tuning (SFT)]] dynamics through comprehensive experiments involving over 1,000 fine-tuned models:

### Model Architecture Dominance

When models are colored by their base architecture in the projected space, clusters group almost perfectly by model family rather than by training data. This indicates that the inductive biases of the base model architecture exert a stronger influence on the final representation than the specific SFT corpus used for training. The global layout is determined by model family rather than training corpus, suggesting that architectural choices have lasting effects even after fine-tuning. ^[2506.md]

### Convergent Training Trajectories

Analysis of epoch-wise trajectories shows that models trained on different datasets gradually converge toward a shared "instruction-following" region in the latent space, regardless of their starting training corpus. For checkpointed models, trajectories spiral toward a common sub-region, suggesting that SFT gradually aligns representations toward a shared instruction-compatible direction. This convergence occurs irrespective of the specific dataset used for training. ^[2506.md]

### Sample Size Effects

Models trained on larger datasets (e.g., 20k samples) tend to occupy positions on the outer rim of the manifold, while those trained on smaller datasets (e.g., 1k samples) cluster closer to the core. Surprisingly, the larger training sets do not consistently provide accuracy advantages over smaller ones, suggesting that compact instruction sets may be sufficient for effective fine-tuning. The 20k-sample-trained points occupy the outer rim more often, whereas 1k-sample-trained points cluster nearer the core, indicating that scaling up can sometimes pull representations away from the optimum. ^[2506.md]

### Training Method Comparison

When comparing full-parameter fine-tuning versus [[Parameter-Efficient Fine-Tuning (PEFT)]] methods like LoRA, the projected representations show minimal separation. LoRA trajectories almost perfectly overlap with full-parameter tuning trajectories, with only slight differences toward the periphery of the manifold. Shape-coding reveals that LoRA points are only slightly more peripheral, with quantitative evaluations showing that full-parameter tuning excels on reasoning-heavy math tasks while LoRA enjoys advantages on open-ended QA benchmarks. ^[2506.md]

## Comprehensive Experimental Validation

The technique has been validated through large-scale experiments mapping 757 fine-tuned models covering 10 base architectures × 10 training datasets, spanning different training methods (LoRA vs. full-parameter), epochs (1-10), and sample sizes (1k or 20k) into a unified latent space. This comprehensive analysis provides five complementary perspectives on SFT dynamics through different visualization approaches. ^[2506.md]

The resulting visualizations provide insights into:
- Model family clustering patterns
- Training data influence assessment  
- Epoch-wise trajectory convergence
- Sample size impact analysis
- Training method effectiveness comparison

## Applications

Log-likelihood vector projection serves multiple research purposes:

- **Training Dynamics Analysis**: Visualizing how models evolve during training across different epochs
- **Method Comparison**: Comparing the effects of different fine-tuning approaches in a unified framework
- **Architecture Studies**: Understanding how base model differences influence fine-tuning outcomes
- **Dataset Impact Assessment**: Analyzing how different training corpora affect model representations

## Relationship to Other Analysis Techniques

This projection method complements other analysis techniques used in fine-tuning research, such as [[Mid-Layer Weight Change Analysis]] and [[Intrinsic Dimensionality Analysis]]. While weight change analysis focuses on parameter modifications and intrinsic dimensionality examines embedding space geometry, log-likelihood vector projection provides a model-agnostic view of representational changes that can compare diverse architectures and training procedures. ^[2506.md]

## Cross-Lingual Transfer Insights

The technique has revealed that cross-lingual transfer effects persist even when using English-only training datasets. Performance gains on English benchmarks show strong correlations with improvements on Japanese and Chinese evaluation tasks, suggesting that content overlap between benchmarks, rather than surface-level language similarity, governs cross-lingual transfer in SFT. This finding has important implications for multilingual model development strategies. ^[2506.md]

## Practical Implications

### Efficient Fine-Tuning Strategy

The finding that compact 1k instruction sets often perform as well as larger 20k sets suggests that careful dataset curation may be more important than scale for effective instruction tuning. This has significant implications for computational efficiency and resource allocation in model training, indicating that practitioners should focus on data quality over quantity. ^[2506.md]

### Architecture Selection

The dominance of model architecture over training data in determining final representations indicates that base model selection may be more critical than previously assumed for achieving specific fine-tuning objectives. This suggests that architectural choices should be prioritized in model development pipelines. ^[2506.md]

### Training Method Optimization

The minimal separation between LoRA and full-parameter fine-tuning trajectories suggests that parameter-efficient methods can achieve comparable representational changes with significantly reduced computational costs. This supports the adoption of PEFT methods for most fine-tuning applications. ^[2506.md]

## Limitations and Considerations

The technique requires careful selection of evaluation tasks and sampling procedures to ensure representative log-likelihood vectors. The choice of dimensionality reduction method and its hyperparameters can also influence the resulting projections and interpretations. Additionally, the method provides insights into relative model relationships but may not capture all aspects of model behavior or performance differences. ^[2506.md]

Current research has been primarily validated on models in the 7-9B parameter range, and generalization to larger models or mixture-of-experts architectures remains to be established. Furthermore, the analysis has focused on English training datasets, limiting insights into multilingual fine-tuning dynamics. The technique also relies on the assumption that log-likelihood patterns reflect meaningful representational differences, which may not hold across all model types or tasks. ^[2506.md]

## Future Directions

Future work could extend this analysis to larger models, explore multilingual training scenarios, and investigate the relationship between log-likelihood patterns and specific model capabilities. Additionally, developing more sophisticated dimensionality reduction techniques tailored to language model representations could improve the interpretability and utility of these projections. ^[2506.md]
