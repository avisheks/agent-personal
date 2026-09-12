---
title: "unified-thinking-and-non-thinking-modes"
summary: ""
sources:
  - general/2505.md
createdAt: 2026-05-29T05:04:11.096378+00:00
updatedAt: 2026-05-29T05:04:11.096378+00:00
---
# Unified Thinking and Non-Thinking Modes

Unified Thinking and Non-Thinking Modes refers to an architectural approach in large language models that integrates two distinct operational modes within a single model framework. This design allows users to dynamically control whether the model engages in explicit reasoning processes or provides direct responses without intermediate thinking steps. ^[2505.md]

## Overview

The unified approach eliminates the need to switch between different specialized models, such as chat-optimized models (e.g., GPT-4o) and dedicated reasoning models (e.g., QwQ-32B). Instead, users can control the model's behavior through chat templates and flags, enabling dynamic mode switching based on user queries or specific task requirements. ^[2505.md]

This integration represents a key innovation that allows developers and users to adapt the model's behavior to suit specific tasks efficiently, providing both high performance and efficient inference capabilities within a single model deployment. ^[2505.md]

## Architecture and Implementation

### Chat Template Design

The unified system employs specific chat templates to control mode switching. Users can specify their preferred mode through flags in the user query or system message:

- **Thinking Mode**: Uses `/think` flag or operates as default behavior
- **Non-Thinking Mode**: Uses `/no think` flag to disable reasoning processes

For non-thinking mode samples, the system retains an empty thinking block in the assistant's response to ensure internal format consistency within the model. This design allows developers to prevent the model from engaging in thinking behavior by concatenating an empty think block in the chat template. ^[2505.md]

### Technical Structure

In thinking mode, the model generates responses with explicit reasoning content enclosed in `<think>` and `</think>` tags, followed by the final response. In non-thinking mode, the model provides direct responses with empty thinking blocks, maintaining format consistency while bypassing the reasoning process. ^[2505.md]

For complex multi-turn dialogs, the system randomly inserts multiple `/think` and `/no think` flags into users' queries, with the model response adhering to the last flag encountered. This ensures consistent mode switching throughout extended conversations. ^[2505.md]

## Thinking Budget Mechanism

A key innovation in unified thinking and non-thinking modes is the [[thinking-budget-mechanism]], which provides users with fine-grained control over computational resource allocation during inference. This capability allows for balancing latency and performance based on task complexity. ^[2505.md]

When the length of the model's thinking reaches a user-defined threshold, the system manually halts the thinking process and inserts a stop-thinking instruction. The model then proceeds to generate a final response based on its accumulated reasoning up to that point. This ability emerges naturally as a result of the unified training approach rather than being explicitly trained. ^[2505.md]

Models demonstrate scalable and smooth performance improvements correlated to the allocated thinking budget. The thinking mode shows particular advantages in complex reasoning tasks, mathematics, and coding challenges where explicit reasoning steps provide value. ^[2505.md]

## Training Methodology

### Four-Stage Training Process

The unified thinking and non-thinking modes are developed through a sophisticated four-stage training process:

1. **[[long-cot-cold-start-training]]**: Initial training with long [[chain-of-thought-reasoning]] patterns
2. **Reasoning RL**: [[reinforcement-learning-from-human-feedback-rlhf]] focused on mathematical and coding tasks
3. **[[thinking-mode-fusion]]**: Integration of both thinking and non-thinking capabilities
4. **General RL**: Broad enhancement across diverse scenarios and tasks

This process ensures that models can effectively switch between modes while maintaining high performance in both operational states. ^[2505.md]

### Thinking Mode Fusion Stage

The integration of both modes occurs during a specific training stage called [[thinking-mode-fusion]]. This stage combines "thinking" and "non-thinking" data in the training dataset. The thinking data is generated via rejection sampling using the model itself, while non-thinking data covers diverse tasks including coding, mathematics, instruction-following, multilingual tasks, creative writing, question answering, and role-playing. ^[2505.md]

The SFT dataset combines both the "thinking" and "non-thinking" data. To ensure that the performance of previous training stages is not compromised by the additional SFT, the "thinking" data is generated via rejection sampling on earlier queries using the model itself. ^[2505.md]

## Performance Characteristics

### Mode-Specific Optimization

The unified approach allows models to handle both types of input effectively while maintaining competitive performance across diverse benchmarks. Models capable of handling both modes proficiently perform consistently well under different thinking budgets. ^[2505.md]

Empirical evaluations demonstrate that models with unified thinking and non-thinking modes achieve state-of-the-art results across diverse benchmarks. Performance scales consistently with increased thinking budget allocation across various tasks. ^[2505.md]

### Effectiveness Across Tasks

The system enables developers and users to adapt the model's behavior to suit specific tasks efficiently. For challenging tasks like mathematics and coding, the thinking mode provides significant advantages, while for rapid response scenarios, the non-thinking mode offers efficient direct answers. ^[2505.md]

## Strong-to-Weak Distillation

The unified approach enables efficient development of smaller models through [[strong-to-weak-distillation]]. This process leverages knowledge from flagship models to significantly reduce computational resources required for building smaller-scale models while ensuring competitive performance. The distillation approach eliminates the need for exhaustive four-stage training for every small-scale model, achieving better performance with approximately 1/10 of the GPU hours compared to full training methods. ^[2505.md]

The distillation process is divided into two primary phases: off-policy distillation that helps lightweight student models develop basic reasoning skills and mode-switching capabilities, followed by on-policy distillation where the student model generates sequences for fine-tuning by aligning its logits with those of a teacher model. ^[2505.md]

## Implementation in Qwen3

The [[qwen3-language-model]] series serves as a prominent implementation of unified thinking and non-thinking modes. The Qwen3 model family demonstrates how this approach can be successfully integrated across models ranging from 0.6 billion to 235 billion parameters, including both dense and [[mixture-of-experts-moe]] architectures. ^[2505.md]

The flagship Qwen3-235B-A22B model achieves 85.7 on AIME'24, 81.5 on AIME'25, 70.7 on LiveCodeBench v5, 2,056 on CodeForces, and 70.8 on BFCL v3, demonstrating the effectiveness of the unified approach across diverse evaluation benchmarks. ^[2505.md]

## Applications and Use Cases

The unified thinking and non-thinking modes approach is particularly valuable for:

- **Complex Reasoning Tasks**: Mathematics, logical reasoning, and multi-step problem solving
- **Rapid Response Scenarios**: Direct question answering and conversational interactions  
- **Resource-Constrained Environments**: Adaptive computational allocation based on task complexity
- **Multi-Domain Applications**: Flexible switching between reasoning-intensive and response-focused tasks

The system provides flexibility that ensures developers and users can adapt the model's behavior to suit specific tasks efficiently, delivering both high performance and efficient inference capabilities within a single model deployment. ^[2505.md]

## Technical Advantages

The unified approach offers several key technical advantages:

- **Elimination of Model Switching**: No need to alternate between different specialized models for different types of tasks
- **Dynamic Resource Allocation**: Fine-grained control over computational resources during inference through the thinking budget mechanism
- **Format Consistency**: Maintains internal format consistency while enabling mode switching
- **Training Efficiency**: Reduces computational requirements for developing smaller models through distillation techniques

These innovations establish unified thinking and non-thinking modes as a cutting-edge approach for building versatile large language models capable of addressing complex tasks across various domains and applications. ^[2505.md]
