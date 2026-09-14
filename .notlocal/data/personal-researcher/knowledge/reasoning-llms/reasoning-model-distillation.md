---
title: "reasoning-model-distillation"
summary: ""
sources:
  - reasoning-llms/demystifying-reasoning-models-by-cameron-r-wolfe-ph-d.md
createdAt: 2026-05-29T04:54:10.107771+00:00
updatedAt: 2026-05-29T04:54:10.107771+00:00
---
# Reasoning Model Distillation

**Reasoning Model Distillation** is a knowledge transfer technique that enables smaller, more efficient language models to acquire the complex reasoning capabilities of larger reasoning models through supervised fine-tuning on reasoning trajectories. This approach has emerged as a highly effective method for creating cost-efficient reasoning models that maintain strong performance while requiring significantly less computational resources than their teacher models.

## Overview

Reasoning model distillation follows the traditional knowledge distillation paradigm but is specifically adapted for models that generate long chains of thought (CoT) during their reasoning process. The technique involves training smaller dense models on the reasoning trajectories produced by larger, more capable reasoning models, effectively transferring the reasoning patterns and problem-solving strategies discovered through large-scale reinforcement learning. ^[demystifying-reasoning-models.md]

The distillation process has proven remarkably effective for reasoning models, often outperforming direct application of reinforcement learning techniques to smaller models. This effectiveness stems from the fact that reasoning patterns discovered by large models are crucial for improving the reasoning capabilities of smaller, dense models. ^[demystifying-reasoning-models.md]

## Training Process

### Data Collection

The distillation process begins with collecting high-quality reasoning trajectories from a powerful teacher model. These trajectories typically consist of long chains of thought that demonstrate detailed problem-solving approaches, including problem decomposition, error detection, and solution exploration. The teacher model generates these trajectories on diverse reasoning-based prompts, which are then filtered through rejection sampling to select only the highest-quality examples. ^[demystifying-reasoning-models.md]

### Student Model Training

Student models are trained using [[Supervised Fine-Tuning (SFT)]] on the curated dataset of reasoning trajectories. The training data typically includes both reasoning-oriented examples and general-purpose data to maintain broad capabilities. For example, in the creation of distilled models from DeepSeek-R1, researchers used 800,000 supervised training examples that combined reasoning trajectories with non-reasoning data. ^[demystifying-reasoning-models.md]

### Base Model Selection

The choice of base model significantly impacts distillation effectiveness. Researchers have successfully distilled reasoning capabilities into various model families, including [[Qwen3 Language Model]] and LLaMA-3 architectures. The distillation process has been demonstrated across multiple model sizes, from 7 billion to 70 billion parameters, with larger student models generally achieving better performance. ^[demystifying-reasoning-models.md]

## Performance Characteristics

### Effectiveness Compared to Direct Training

Reasoning model distillation consistently outperforms direct application of [[Reinforcement Learning from Human Feedback (RLHF)]] or other RL techniques to smaller models. For instance, distilling a Qwen2.5-32B model from DeepSeek-R1 using supervised fine-tuning achieved better performance than directly training the same model via large-scale reinforcement learning. ^[demystifying-reasoning-models.md]

### Scaling Properties

The effectiveness of distillation scales with both teacher model capability and student model size. Distilled models of 32 billion and 70 billion parameters have been shown to exceed the performance of specialized reasoning models like o1-mini on most benchmarks, while even smaller distilled models can outperform standard closed language models that are not optimized for reasoning. ^[demystifying-reasoning-models.md]

### Capability Transfer

Distilled reasoning models successfully transfer key reasoning behaviors from their teachers, including:
- Problem decomposition strategies
- Error detection and correction patterns  
- Alternative solution exploration
- Self-reflection and verification processes

These capabilities emerge in the student models without explicit programming, demonstrating the effectiveness of the knowledge transfer process. ^[demystifying-reasoning-models.md]

## Applications and Impact

### Cost-Effective Deployment

Reasoning model distillation addresses the practical challenge of deploying large [[Mixture of Experts (MoE)]] reasoning models in production environments. Distilled models provide comparable reasoning performance while being more cost-sensitive and easier to deploy, making advanced reasoning capabilities accessible to a broader range of applications. ^[demystifying-reasoning-models.md]

### Research Acceleration

The simplicity and effectiveness of reasoning model distillation has led to an explosion of research activity, with numerous distilled reasoning models being released by the research community. This trend mirrors the post-LLaMA era of language model research, where the availability of strong open models catalyzed widespread innovation and experimentation. ^[demystifying-reasoning-models.md]

## Limitations and Considerations

### Generalization Boundaries

While distillation is highly effective for transferring existing reasoning patterns, it may not enable student models to fully match the breadth of capabilities of their teachers. The technique is particularly effective for replicating learned reasoning strategies but may be limited in advancing beyond the boundaries of intelligence established by the teacher model. ^[demystifying-reasoning-models.md]

### Training Data Requirements

Effective reasoning model distillation requires access to high-quality reasoning trajectories from capable teacher models. The process of generating and curating these trajectories can be computationally expensive, though still more efficient than training reasoning capabilities from scratch through reinforcement learning. ^[demystifying-reasoning-models.md]

## Future Directions

Research suggests that distilled reasoning models could potentially be further improved through additional training with reinforcement learning techniques. However, advancing beyond current performance boundaries will likely still require powerful base models and large-scale training with RL for the teacher models that serve as the source of distillation knowledge. ^[demystifying-reasoning-models.md]

The field continues to explore optimal combinations of distillation with other training techniques, as well as methods for improving the efficiency and effectiveness of the knowledge transfer process in reasoning model distillation.
