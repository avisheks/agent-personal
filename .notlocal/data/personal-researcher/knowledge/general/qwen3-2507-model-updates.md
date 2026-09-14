---
title: "qwen3-2507-model-updates"
summary: ""
sources:
  - general/github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md
createdAt: 2026-05-29T05:07:13.612384+00:00
updatedAt: 2026-05-29T05:07:13.612384+00:00
---
# Qwen3-2507 Model Updates

Qwen3-2507 represents the updated version of the [[Qwen3 Language Model]] series, released over three months after the initial Qwen3 launch. The 2507 updates introduce significant enhancements across two distinct model variants and multiple size configurations. ^[github-qwenlm-qwen3.md]

## Model Variants

### Qwen3-Instruct-2507

Qwen3-Instruct-2507 is the updated version of the previous Qwen3 non-thinking mode, featuring several key improvements. The model demonstrates significant enhancements in general capabilities, including instruction following, logical reasoning, text comprehension, mathematics, science, coding and tool usage. It also provides substantial gains in long-tail knowledge coverage across multiple languages and markedly better alignment with user preferences in subjective and open-ended tasks, enabling more helpful responses and higher-quality text generation. ^[github-qwenlm-qwen3.md]

The Instruct variant supports only non-thinking mode and does not generate `<think></think>` blocks in its output. Users no longer need to specify `enable_thinking=False` when using this model. ^[github-qwenlm-qwen3.md]

### Qwen3-Thinking-2507

Qwen3-Thinking-2507 continues the development of the Qwen3 thinking model with improved quality and depth of reasoning. The model achieves significantly improved performance on reasoning tasks, including logical reasoning, mathematics, science, coding, and academic benchmarks that typically require human expertise, achieving state-of-the-art results among open-weight thinking models. It also demonstrates markedly better general capabilities such as instruction following, tool usage, text generation, and alignment with human preferences. ^[github-qwenlm-qwen3.md]

The Thinking variant supports only thinking mode and features an increased thinking length. The default [[Chat Template Formatting]] automatically includes `<think>` tags, making it normal for the model's output to contain only `</think>` without an explicit opening `<think>` tag. ^[github-qwenlm-qwen3.md]

## Model Sizes

The Qwen3-2507 updates are available in three size configurations:

- **235B-A22B**: The largest model using [[Mixture of Experts (MoE)]] architecture
- **30B-A3B**: A medium-sized MoE model  
- **4B**: A smaller dense model for efficient deployment

All variants support enhanced 256K long-context understanding capabilities, extendable up to 1 million tokens. ^[github-qwenlm-qwen3.md]

## Release Timeline

The Qwen3-2507 models were released in a staged rollout:

- **July 21, 2025**: Qwen3-235B-A22B-Instruct-2507 released with significant enhancements and 256K-token long-context support
- **July 25, 2025**: Qwen3-235B-A22B-Thinking-2507 released  
- **July 30, 2025**: Qwen3-30B-A3B-Instruct-2507 released
- **July 31, 2025**: Qwen3-30B-A3B-Thinking-2507 released
- **August 6, 2025**: Final release of Qwen3-4B-Instruct-2507 and Qwen3-4B-Thinking-2507
- **August 8, 2025**: Ultra-long input support of 1 million tokens enabled ^[github-qwenlm-qwen3.md]

## Technical Implementation

### Inference Support

The Qwen3-2507 models are supported by multiple inference frameworks including [[vLLM Inference Engine]], SGLang, and TensorRT-LLM. The models require specific configuration parameters for optimal performance, particularly for thinking mode models which need reasoning parser settings. ^[github-qwenlm-qwen3.md]

### Long Context Capabilities

A significant enhancement in the 2507 updates is the extended context support. While the models natively support 256K tokens, they can be extended to handle ultra-long inputs of up to 1 million tokens through specific configuration settings. ^[github-qwenlm-qwen3.md]

### Training Framework Compatibility

The models support training with various frameworks including Axolotl, UnSloth, Swift, and Llama-Factory for [[Supervised Fine-Tuning (SFT)]], [[Direct Preference Optimization (DPO)]], and [[Group Relative Policy Optimization (GRPO)]]. ^[github-qwenlm-qwen3.md]

## Deployment Considerations

The Qwen3-2507 models maintain compatibility with existing deployment infrastructure while introducing enhanced capabilities. For thinking models, special consideration must be given to multi-step tool use scenarios, where the presence of thinking content is crucial for optimal performance. Some inference frameworks may require workarounds to preserve reasoning content during API preprocessing. ^[github-qwenlm-qwen3.md]

## Local Deployment Options

The models support various local deployment options including [[Ollama Model Runtime]], llama.cpp, LM Studio, and MLX for Apple Silicon. Each deployment method offers different optimization strategies and hardware compatibility options for running the models efficiently on consumer hardware. ^[github-qwenlm-qwen3.md]
