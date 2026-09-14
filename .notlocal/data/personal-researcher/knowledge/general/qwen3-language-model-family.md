---
title: "qwen3-language-model-family"
summary: ""
sources:
  - general/github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md
  - general/qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md
createdAt: 2026-05-29T05:06:36.904780+00:00
updatedAt: 2026-05-29T05:06:36.904780+00:00
---
# Qwen3 Language Model Family

The **Qwen3 Language Model Family** is a series of large language models developed by the Qwen team at Alibaba Cloud, released in April 2025. The family represents a significant advancement over previous Qwen generations, featuring both dense and [[Mixture of Experts (MoE)]] architectures with a unique dual-mode reasoning system that allows seamless switching between thinking and non-thinking modes. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

## Model Architecture and Variants

### Dense Models

Qwen3 includes six dense model sizes ranging from 0.6B to 32B parameters. The dense models include 0.6B, 1.7B, 4B, 8B, 14B, and 32B parameter variants, each designed for different computational requirements and use cases. All dense models maintain consistent architecture while scaling parameters to balance performance with resource requirements. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

### Mixture of Experts Models

The family includes two [[Mixture of Experts (MoE)]] models: Qwen3-30B-A3B and Qwen3-235B-A22B. The 30B-A3B model contains 30B total parameters with 3B active parameters per token, while the flagship 235B-A22B model contains 235B total parameters with 22B active parameters per token. These MoE architectures provide enhanced capabilities while maintaining computational efficiency compared to equivalent dense models. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

## Dual-Mode Reasoning System

### Thinking and Non-Thinking Modes

Qwen3 models feature a unique dual-mode system that allows seamless switching between thinking mode for complex logical reasoning and non-thinking mode for efficient general-purpose chat. Users can control this behavior through `/think` and `/no_think` instructions in system or user messages, with the latest instruction being followed in multi-turn conversations. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

In thinking mode, models generate visible [[Chain-of-Thought Reasoning]] within `<think></think>` blocks before providing their final response. This mode is optimized for mathematics, code generation, and complex logical reasoning tasks. Non-thinking mode provides direct responses without visible reasoning chains, making it suitable for general conversation, creative writing, and simple queries. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

### Updated 2507 Variants

The Qwen3-2507 series introduced specialized variants: Qwen3-Instruct-2507 supports only non-thinking mode and does not generate thinking blocks, while Qwen3-Thinking-2507 supports only thinking mode with automatically included thinking prompts in the chat template. These variants provide optimized performance for their respective use cases with enhanced capabilities in their specialized modes. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

## Technical Capabilities

### Training and Data

Qwen3 models were trained on 36 trillion tokens, doubling the training data compared to Qwen 2.5's 18 trillion tokens. The training encompasses over 100 languages and dialects with strong multilingual instruction following and translation capabilities. The models demonstrate significant improvements in reasoning capabilities, surpassing previous QwQ thinking models and Qwen2.5 instruct models in mathematics, code generation, and commonsense logical reasoning. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md] ^[qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md]

### Context Length and Performance

The models support [[Long Context Scaling]] with 256K-token context windows, extendable up to 1 million tokens for certain variants. Qwen3 demonstrates substantial gains in long-tail knowledge coverage across multiple languages and markedly better alignment with user preferences in subjective and open-ended tasks. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

## Specialized Variants

### Qwen3-Coder Series

The family includes specialized coding models: Qwen3-Coder 480B-A35B and Qwen3-Coder 30B-A3B. The 480B variant serves as an agentic coding model with 256K native context, while the 30B variant provides practical coding capabilities for consumer hardware. These models were trained on code-heavy datasets and include integration with agentic coding workflows. ^[qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md]

### Vision Models

Qwen3-VL variants provide multimodal capabilities across different parameter scales, including 4B, 8B, 32B dense models and a 30B-A3B MoE variant. These models combine the language capabilities of Qwen3 with image understanding functionality. ^[qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md]

## Deployment and Integration

### Inference Frameworks

Qwen3 is supported by multiple inference frameworks including [[vLLM Inference Engine]], SGLang, TensorRT-LLM, and llama.cpp. The models can be deployed using various serving solutions with OpenAI-compatible APIs. Specific configurations are required for thinking mode support in different frameworks, with reasoning parsers needed for proper handling of thinking content. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]

### Hardware Requirements

The models have varying VRAM requirements depending on size and quantization level. Qwen3-4B requires approximately 3GB VRAM at Q4 quantization, while the flagship 235B-A22B model requires approximately 143GB VRAM. The MoE models provide efficiency advantages, with the 30B-A3B requiring around 18GB VRAM while delivering performance comparable to larger dense models. ^[qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md]

## Performance and Benchmarks

Qwen3 demonstrates significant performance improvements across benchmarks. The 4B model achieves 83.7 on MMLU-Redux and 97.0 on MATH-500, while the flagship 235B-A22B model scores 95.6 on Arena-Hard, 85.7 on AIME'24, and 81.4 on AIME'25, outperforming comparable models including DeepSeek-R1 and o1 on several benchmarks. ^[qwen3-complete-guide-every-model-from-0-6b-to-235b-insiderllm.md]

## Licensing and Availability

All Qwen3 models are released under the Apache 2.0 license, making them available for both commercial and personal use without restrictions. The models are distributed through [[Hugging Face Transformers Library]] and ModelScope, with comprehensive documentation and deployment guides provided for various use cases and hardware configurations. ^[github-qwenlm-qwen3-qwen3-is-the-large-language-model-series-developed-by-qwen-team-alibaba-cloud-github.md]
