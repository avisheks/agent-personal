---
title: "thinking-mode-fusion"
summary: ""
sources:
  - general/2505.md
createdAt: 2026-05-29T05:05:37.013589+00:00
updatedAt: 2026-05-29T05:05:37.013589+00:00
---
# Thinking Mode Fusion

**Thinking Mode Fusion** is a training technique that integrates two distinct operational modes—"thinking mode" and "non-thinking mode"—into a single large language model. This approach allows users to dynamically control whether a model engages in explicit reasoning processes without requiring separate models for different types of tasks. ^[2505.md]

## Overview

Thinking Mode Fusion eliminates the need to switch between different specialized models, such as chat-optimized models (e.g., GPT-4o) and dedicated reasoning models (e.g., QwQ-32B). Instead, it enables dynamic mode switching based on user queries or chat templates within a unified framework. ^[2505.md]

The technique was developed as part of the [[Qwen3 Language Model]] series, where it serves as the third stage in a [[Four-Stage Post-Training Pipeline]]. The approach allows developers to manage and control reasoning behaviors while reducing the cost and complexity of deploying separate models for thinking and non-thinking tasks. ^[2505.md]

## Technical Implementation

### Chat Template Design

Thinking Mode Fusion uses specially designed chat templates to enable mode switching. The system introduces `/think` and `/no think` flags in user queries or system messages to control the model's behavior:

- **Thinking Mode**: Uses `/think` flag (or operates as default behavior) and generates responses with explicit reasoning content enclosed in `<think>` tags
- **Non-thinking Mode**: Uses `/no think` flag and generates responses with empty thinking blocks while maintaining internal format consistency ^[2505.md]

### Training Data Construction

The training process combines both thinking and non-thinking data through [[Supervised Fine-Tuning (SFT)]]. Thinking data is generated via rejection sampling using the model from the previous reasoning stage, while non-thinking data covers diverse tasks including coding, mathematics, instruction-following, multilingual tasks, creative writing, question answering, and role-playing. ^[2505.md]

### Multi-turn Dialog Support

For complex multi-turn conversations, the system randomly inserts multiple `/think` and `/no think` flags into user queries, with the model adhering to the last flag encountered in the conversation. ^[2505.md]

## Thinking Budget Mechanism

A key advantage of Thinking Mode Fusion is the emergence of **[[Thinking Budget Mechanism]]**—the ability to generate responses based on incomplete thinking when computational resources are limited. When the model's thinking reaches a user-defined threshold, the system can manually halt the thinking process and insert a stop-thinking instruction, allowing the model to generate responses based on accumulated reasoning up to that point. ^[2505.md]

This capability enables users to allocate computational resources adaptively during inference, balancing latency and performance based on task complexity. Notably, this ability emerges naturally from the training process rather than being explicitly trained. ^[2505.md]

## Performance Impact

Evaluation results demonstrate that models trained with Thinking Mode Fusion can handle both modes proficiently and perform consistently well under different thinking budgets. The technique shows particular effectiveness in:

- **Instruction Following**: Improved accuracy in interpreting and following user instructions
- **Format Following**: Consistent adherence to designated tokens and mode-switching conventions  
- **Agent Abilities**: Enhanced performance in tool calling and multi-turn interactions ^[2505.md]

However, the integration process may result in some performance trade-offs. For specialized tasks like complex mathematics and coding (e.g., AIME'24 and LiveCodeBench), thinking mode performance may decrease slightly after fusion training, as the model is trained on a broader range of general tasks. ^[2505.md]

## Applications

Thinking Mode Fusion is particularly valuable for:

- **Resource Optimization**: Allowing single models to handle both quick responses and complex reasoning tasks
- **Cost Reduction**: Eliminating the need to deploy and maintain separate reasoning and chat models
- **Adaptive Inference**: Enabling dynamic adjustment of computational effort based on task requirements
- **User Control**: Providing fine-grained control over model reasoning behavior ^[2505.md]

## Training Pipeline Integration

Thinking Mode Fusion operates as Stage 3 in the four-stage post-training pipeline:

1. **Long-CoT Cold Start**: Initial reasoning pattern development
2. **Reasoning RL**: Reinforcement learning for mathematical and coding tasks
3. **Thinking Mode Fusion**: Integration of thinking and non-thinking capabilities
4. **General RL**: Broad capability enhancement across diverse scenarios ^[2505.md]

The fusion stage specifically focuses on integrating non-thinking capabilities into previously developed thinking models through continual [[Supervised Fine-Tuning (SFT)]] and specialized chat template design. ^[2505.md]

## Experimental Results

Performance evaluations show that Thinking Mode Fusion successfully enables models to switch between modes while maintaining competitive performance. The flagship Qwen3-235B-A22B model demonstrates state-of-the-art results in both thinking and non-thinking modes across diverse benchmarks including mathematics, coding, and agent tasks. ^[2505.md]

The technique also shows scalable performance improvements correlated to allocated thinking budgets, with models demonstrating smooth performance curves as computational resources are increased for reasoning tasks. ^[2505.md]

## Related Concepts

- [[Chain-of-Thought Reasoning]]: The underlying reasoning approach used in thinking mode
- [[Supervised Fine-Tuning (SFT)]]: The training methodology used to implement mode fusion
- [[Qwen3 Language Model]]: The model family where this technique was first implemented
- [[Four-Stage Post-Training Pipeline]]: The broader training framework containing thinking mode fusion
- [[Thinking Budget Mechanism]]: The resource allocation capability that emerges from fusion training
