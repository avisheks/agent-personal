---
title: "strong-to-weak-distillation"
summary: ""
sources:
  - general/2505.md
createdAt: 2026-05-29T05:04:41.116857+00:00
updatedAt: 2026-05-29T05:04:41.116857+00:00
---
# Strong-to-Weak Distillation

Strong-to-Weak Distillation is a training methodology that leverages knowledge from larger, more capable teacher models to enhance the performance of smaller student models while maintaining computational efficiency. This approach enables the development of lightweight models with competitive capabilities by transferring both reasoning abilities and mode-switching functionalities from flagship models to smaller variants.

## Overview

Strong-to-Weak Distillation addresses the challenge of building high-performing smaller models without requiring the full computational resources typically needed for extensive multi-stage training processes. By utilizing knowledge from advanced teacher models, this technique significantly outperforms traditional [[Reinforcement Learning from Human Feedback (RLHF)]] approaches in both performance metrics and training efficiency, requiring approximately only 1/10 of the GPU hours compared to conventional four-stage training methods. ^[2505.md]

The methodology is particularly effective for optimizing lightweight models, encompassing both dense architectures and [[Mixture-of-Experts (MoE)]] variants. In practical implementations, this approach has been successfully applied to models ranging from 0.6 billion to 30 billion parameters, demonstrating consistent performance improvements across different model scales. ^[2505.md]

## Training Process

### Two-Phase Approach

Strong-to-Weak Distillation operates through a structured two-phase training process:

**Off-policy Distillation**: In the initial phase, the methodology combines outputs from teacher models generated in both thinking and non-thinking modes for response distillation. This phase helps lightweight student models develop fundamental reasoning skills and the ability to switch between different cognitive modes, establishing a solid foundation for subsequent training stages. ^[2505.md]

**On-policy Distillation**: During this phase, the student model generates sequences for fine-tuning using its own policy. Prompts are sampled, and the student model produces responses in either thinking or non-thinking mode. The student model is then fine-tuned by aligning its logits with those of a teacher model to minimize KL divergence, enabling more sophisticated knowledge transfer. ^[2505.md]

### Knowledge Transfer Mechanisms

The distillation process involves transferring output logits from teacher models directly into student models, which effectively enhances performance while maintaining fine-grained control over reasoning processes. This approach eliminates the necessity of performing exhaustive multi-stage training individually for every small-scale model, leading to better immediate performance as indicated by higher Pass@1 scores. ^[2505.md]

Additionally, distillation from teacher logits enables student models to expand their exploration space and enhance reasoning potential, as evidenced by improved Pass@64 results. This capability demonstrates the method's effectiveness in not only improving immediate performance but also enhancing the model's ability for broader exploration during inference. ^[2505.md]

## Performance Benefits

### Efficiency Gains

Strong-to-Weak Distillation achieves significant computational savings compared to traditional training approaches. The methodology requires substantially fewer GPU hours while delivering superior performance outcomes. In comparative evaluations, distillation achieved significantly better performance than [[Reinforcement Learning from Human Feedback (RLHF)]] while requiring approximately only 1/10 of the computational resources. ^[2505.md]

### Capability Transfer

The approach successfully transfers complex capabilities from larger models to smaller ones, including the ability to handle both thinking and non-thinking modes dynamically. This enables smaller models to maintain sophisticated reasoning capabilities while operating with reduced computational overhead. The distilled models demonstrate improved performance across various benchmarks, including mathematical reasoning tasks and coding challenges. ^[2505.md]

### Exploration Enhancement

Unlike traditional reinforcement learning approaches that may not improve exploration capabilities, Strong-to-Weak Distillation enhances the student model's ability to explore different solution paths. This is particularly evident in improved Pass@64 scores on challenging benchmarks, indicating that distilled models can generate more diverse and potentially correct solutions during multiple sampling attempts. ^[2505.md]

## Experimental Results

Empirical evaluations demonstrate the effectiveness of Strong-to-Weak Distillation across multiple dimensions. When comparing reinforcement learning and on-policy distillation on Qwen3-8B models, distillation consistently outperformed reinforcement learning across various benchmarks including AIME'24, AIME'25, MATH500, LiveCodeBench v5, MMLU-Redux, and GPQA-Diamond, while requiring significantly fewer computational resources. ^[2505.md]

The distillation approach also enables student models to maintain and improve their exploration capabilities, as demonstrated by enhanced Pass@64 scores on mathematical reasoning benchmarks. This contrasts with reinforcement learning approaches that showed no improvement in exploration metrics despite requiring substantially more computational resources. ^[2505.md]

## Applications

Strong-to-Weak Distillation has been successfully implemented across various model architectures and scales. The methodology proves particularly valuable for developing edge-side models that require efficient performance while maintaining competitive capabilities. It enables the creation of lightweight models that can operate effectively in resource-constrained environments while preserving essential reasoning and problem-solving abilities derived from larger teacher models. ^[2505.md]

The approach also facilitates the development of models with dynamic mode-switching capabilities, allowing users to control computational resource allocation during inference based on task complexity requirements. This flexibility makes the methodology especially suitable for applications requiring adaptive performance optimization. ^[2505.md]

## Implementation in Qwen3

The [[Qwen3 Language Model Family]] successfully implements Strong-to-Weak Distillation for optimizing lightweight models, encompassing 5 dense models (ranging from 0.6B to 14B parameters) and one [[Mixture-of-Experts (MoE)]] model (30B total parameters with 3B activated). This implementation enhances model performance while effectively imparting robust mode-switching capabilities between thinking and non-thinking modes. ^[2505.md]

## Comparison with Traditional Methods

Strong-to-Weak Distillation demonstrates superior effectiveness compared to traditional reinforcement learning approaches. In experimental comparisons, distillation achieved significantly better performance than reinforcement learning while requiring approximately only 1/10 of the GPU hours. Furthermore, distillation from teacher logits enables student models to expand their exploration space and enhance their reasoning potential, as evidenced by improved Pass@64 scores, while reinforcement learning does not lead to any improvement in Pass@64 scores. ^[2505.md]
