---
title: "DeepSeek R1 Distilled Models"
summary: "Practical fine-tuning variants of DeepSeek's frontier reasoning model, ranging from 1.5B to 70B parameters with strong mathematical capabilities."
sources:
  - open-weight-fms/open-weight-models-catalog-2026.md
createdAt: 2026-06-15T12:02:39.818085+00:00
updatedAt: 2026-06-15T12:02:39.818085+00:00
---
# DeepSeek R1 Distilled Models

**DeepSeek R1 Distilled Models** are a family of smaller, more efficient language models that have been trained to replicate the reasoning capabilities of the larger [[deepseek-r1-reasoning-model|DeepSeek R1]] model through [[reasoning-distillation|reasoning distillation]] techniques. These models provide a practical alternative for deployment scenarios where the full 671B parameter DeepSeek R1 model would be computationally prohibitive.

## Architecture and Variants

The DeepSeek R1 Distilled family spans multiple model sizes, ranging from 1.5B to 70B parameters. Unlike the original DeepSeek R1 which uses a [[mixture-of-experts-moe|Mixture of Experts (MoE)]] architecture with 671B total parameters and 37B active parameters, the distilled variants employ dense transformer architectures based on established foundations such as [[qwen3-language-model|Qwen2.5]] and Llama3 base models. ^[open-weight-foundation-models-catalog-mid-2026.md]

The distilled models maintain the core reasoning capabilities of the original R1 model while being significantly more accessible for fine-tuning and deployment. The largest 70B variant achieves strong performance on mathematical reasoning tasks, scoring 90.2% on MATH-500 benchmarks, while the smaller variants provide graduated trade-offs between computational requirements and reasoning performance. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Training Methodology

The distillation process involves training smaller dense models to mimic the reasoning patterns and outputs of the larger DeepSeek R1 model. This approach leverages [[chain-of-thought-reasoning|chain-of-thought reasoning]] techniques, where the distilled models learn to replicate the step-by-step reasoning processes that make the original R1 model effective at complex problem-solving tasks. ^[open-weight-foundation-models-catalog-mid-2026.md]

The distilled models inherit the dual thinking/non-thinking modes capability from their larger counterpart, allowing them to engage in explicit reasoning when needed while maintaining efficiency for simpler tasks. This architectural feature enables the models to scale their computational effort based on problem complexity. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Performance Characteristics

DeepSeek R1 Distilled models demonstrate strong performance across multiple domains, particularly excelling in mathematical reasoning and code generation tasks. The 32B variant achieves competitive results on mathematical benchmarks while requiring significantly fewer computational resources than the full R1 model. In code generation, the models score 82.6% on HumanEval-Mul, demonstrating their effectiveness for programming applications. ^[open-weight-foundation-models-catalog-mid-2026.md]

The models support 128K context length and are designed to work effectively with modern inference frameworks like [[vllm-inference-engine|vLLM]]. Their dense architecture makes them more straightforward to deploy compared to MoE models, which require specialized infrastructure for efficient expert routing. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Deployment and Fine-tuning

The distilled models are particularly well-suited for fine-tuning applications due to their manageable parameter counts and dense architectures. The smaller variants (1.5B-8B) can be fine-tuned using [[qwen3-language-model|QLoRA]] techniques on consumer hardware, while the larger variants (32B-70B) are accessible for full [[supervised-fine-tuning-sft|supervised fine-tuning]] on enterprise-grade hardware. ^[open-weight-foundation-models-catalog-mid-2026.md]

For organizations requiring strong reasoning capabilities but lacking the infrastructure to deploy the full 671B parameter R1 model, the 32B distilled variant represents an optimal balance between performance and computational requirements. It can be deployed on single high-end GPUs while maintaining much of the reasoning capability of the original model. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Licensing and Availability

The DeepSeek R1 Distilled models are released under the MIT license, making them freely available for both research and commercial applications without the usage restrictions that apply to some other frontier models. This permissive licensing, combined with their practical deployment characteristics, makes them attractive options for production systems requiring advanced reasoning capabilities. ^[open-weight-foundation-models-catalog-mid-2026.md]

## Related Concepts

- [[reasoning-model-distillation|Reasoning Model Distillation]]
- [[inference-time-reasoning|Inference-Time Reasoning]]
- [[long-chain-of-thought-long-cot|Long Chain-of-Thought]]
- [[process-reward-model-prm|Process Reward Models]]
