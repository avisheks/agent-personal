---
title: "Managed Fine-Tuning Services Pricing"
summary: "Commercial fine-tuning services that charge per million training tokens, with costs ranging from $0.48 to $6.00 depending on model size and method."
sources:
  - system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-15T11:55:22.308435+00:00
updatedAt: 2026-06-15T11:55:22.308435+00:00
---
# Managed Fine-Tuning Services Pricing

Managed fine-tuning services provide cloud-based infrastructure for customizing large language models without requiring users to manage GPU clusters, training frameworks, or optimization pipelines. These services typically charge based on the number of training tokens processed and the size of the base model being fine-tuned.

## Pricing Models

### Token-Based Pricing

Most managed fine-tuning services use a token-based pricing model where costs scale with the amount of training data processed. The standard unit is typically per million training tokens, calculated as:

```
Training Tokens = Dataset Examples × Average Tokens per Example × Number of Epochs
```

For example, fine-tuning on 10,000 examples with an average of 1,000 tokens each for 3 epochs would consume 30 million training tokens. ^[gpu-hours-for-fine-tuning-llms.md]

### Model Size Tiers

Pricing typically increases with model parameter count, reflecting the higher computational requirements for larger models. Common tiers include:

- **Small models** (up to 16B parameters): Lowest cost tier
- **Medium models** (17-69B parameters): Mid-tier pricing  
- **Large models** (70-100B parameters): Higher cost tier
- **Extra-large models** (100B+ parameters): Premium pricing

The cost difference between tiers can be substantial, with large models costing 3-6x more than small models per training token. ^[gpu-hours-for-fine-tuning-llms.md]

## Representative Pricing Examples

### Together AI Pricing Structure

Together AI offers managed fine-tuning with the following pricing per million training tokens:

- **Up to 16B parameters**: $0.48 for [[Low-Rank Adaptation (LoRA)]], $0.54 for full [[Supervised Fine-Tuning (SFT)]]
- **17-69B parameters**: $1.50 for LoRA, $1.65 for full SFT
- **70-100B parameters**: $2.90 for LoRA, $3.20 for full SFT
- **[[GPT-OSS-120B]]**: $5.00 for LoRA (full SFT not available)
- **[[Qwen3 Language Model]] 235B**: $6.00 for LoRA (full SFT not available)

The pricing reflects the computational complexity of training larger models, with the largest models requiring specialized infrastructure and longer training times. ^[gpu-hours-for-fine-tuning-llms.md]

## Training Method Cost Differences

### LoRA vs Full Fine-Tuning

[[Parameter-Efficient Fine-Tuning (PEFT)]] methods like LoRA typically cost slightly less than full fine-tuning because they require fewer trainable parameters. However, the cost difference is often modest (10-15%) because the forward pass still processes the entire model during training.

For very large models (100B+ parameters), managed services may only offer LoRA fine-tuning due to the prohibitive memory and computational requirements of full fine-tuning. ^[gpu-hours-for-fine-tuning-llms.md]

### Memory and Time Considerations

The pricing reflects underlying resource requirements:

- **Full SFT**: Requires storing model weights, gradients, and optimizer states, leading to high memory usage
- **LoRA**: Reduces memory requirements by 3-10x but still processes the full model during forward passes
- **[[QLoRA (Quantized LoRA)]]**: Further reduces memory usage through quantization but may not be offered by all managed services

## Cost Comparison with Self-Hosted Training

Managed services typically charge a premium over raw GPU costs to cover infrastructure, maintenance, and profit margins. For example, training a 7B model on 10K examples might cost:

- **Managed service**: $15-30 total
- **Self-hosted on cloud GPUs**: $5-15 total (plus setup time and expertise)
- **Self-hosted on owned hardware**: $2-8 in electricity costs

The premium reflects the convenience of not managing training infrastructure, automatic scaling, and integrated tooling for dataset preparation and model deployment. ^[gpu-hours-for-fine-tuning-llms.md]

## Factors Affecting Pricing

### Dataset Characteristics

- **Sequence length**: Longer sequences require more memory and computation
- **Dataset size**: More examples increase total training tokens
- **Number of epochs**: Multiple passes through data multiply token count

### Model Architecture

- **Dense vs [[Mixture of Experts (MoE)]]**: MoE models may have different pricing due to activation patterns
- **Context window**: Models with longer context windows require more memory

### Training Configuration

- **Batch size**: Larger batches may improve efficiency but require more memory
- **Learning rate scheduling**: More complex schedules may extend training time
- **Convergence criteria**: Stricter convergence requirements increase training duration

The combination of these factors determines the final cost, with managed services typically providing cost estimation tools based on dataset characteristics and training configuration. ^[gpu-hours-for-fine-tuning-llms.md]
