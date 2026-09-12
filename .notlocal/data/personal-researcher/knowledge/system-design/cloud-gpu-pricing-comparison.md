---
title: "Cloud GPU Pricing Comparison"
summary: "Comparative analysis of GPU rental costs across providers like RunPod, GCP, and Lambda Labs, ranging from $0.50 to $10.20 per GPU-hour."
sources:
  - system-design/gpu-hours-fine-tuning-reference.md
createdAt: 2026-06-15T11:55:38.972068+00:00
updatedAt: 2026-06-15T11:55:38.972068+00:00
---
# Cloud GPU Pricing Comparison

Cloud GPU pricing for machine learning workloads varies significantly across providers, hardware types, and deployment models. Understanding these pricing structures is essential for optimizing costs when training or fine-tuning large language models and other AI systems.

## GPU Hardware Categories

### Consumer-Grade GPUs
RTX 4090 (24GB) represents the high-end consumer option, offering 165 TFLOP/s FP16 performance with approximately 82 TFLOP/s effective training throughput. These GPUs provide cost-effective solutions for smaller models and experimentation. ^[gpu-hours-for-fine-tuning-llms.md]

### Professional Data Center GPUs
A100 GPUs are available in two memory configurations: 40GB and 80GB variants. The A100 delivers 120-180 TFLOP/s performance, with 150 TFLOP/s being typical when using Flash Attention optimizations. H100 GPUs provide approximately 300-400 TFLOP/s, representing roughly 2x the performance of A100 hardware. ^[gpu-hours-for-fine-tuning-llms.md]

## Cloud Provider Pricing Structure

### Major Cloud Providers
Google Cloud Platform (GCP) offers both on-demand and spot pricing models. A100 40GB instances cost $2.93 per GPU-hour on-demand, dropping to $0.88 per GPU-hour for spot instances. A100 80GB pricing reaches $3.67 per GPU-hour on-demand and $1.10 per GPU-hour for spot instances. H100 80GB represents the premium tier at $10.20 per GPU-hour on-demand and $3.06 per GPU-hour for spot pricing. ^[gpu-hours-for-fine-tuning-llms.md]

### Specialized GPU Cloud Providers
RunPod provides competitive pricing with RTX 4090 instances at $0.69 per GPU-hour, A100 80GB at $1.39-1.49 per GPU-hour, and H100 80GB at $2.89-3.29 per GPU-hour. Lambda Labs offers A100 40GB at approximately $1.10 per GPU-hour, A100 80GB at around $1.50 per GPU-hour, and RTX 4090 at roughly $0.50 per GPU-hour. ^[gpu-hours-for-fine-tuning-llms.md]

## Managed Fine-Tuning Services

### Together AI Pricing Model
Together AI structures pricing based on model size tiers and training tokens consumed. For models up to 16B parameters, [[Low-Rank Adaptation (LoRA)]] costs $0.48 per million training tokens, while full [[Supervised Fine-Tuning (SFT)]] costs $0.54 per million tokens. Models in the 17-69B parameter range cost $1.50 for LoRA and $1.65 for full SFT per million tokens. Large models from 70-100B parameters require $2.90 for LoRA and $3.20 for full SFT per million tokens. ^[gpu-hours-for-fine-tuning-llms.md]

Specialized large models command premium pricing, with [[GPT-OSS-120B]] LoRA fine-tuning at $5.00 per million training tokens and [[Qwen3 Language Model]] 235B variant at $6.00 per million training tokens. Full SFT is not available for these largest models. ^[gpu-hours-for-fine-tuning-llms.md]

## Cost Optimization Strategies

### Hardware Selection by Model Size
For 7-8B parameter models, single RTX 4090 instances provide the most cost-effective solution at $1-4 total cost using [[QLoRA (Quantized LoRA)]] 4-bit quantization. Models in the 13-14B range benefit from A100 40GB instances, while 32B models require A100 80GB hardware. Models exceeding 70B parameters necessitate multiple GPU configurations or H100 hardware for reasonable training times. ^[gpu-hours-for-fine-tuning-llms.md]

### Training Method Impact on Costs
[[Parameter-Efficient Fine-Tuning (PEFT)]] methods dramatically reduce both memory requirements and training costs. QLoRA 4-bit quantization enables training of 70-72B models on 2x A100 80GB hardware for 12-30 hours at $20-60 total cost, compared to full SFT requiring 16-32x A100 80GB for 320-640 GPU-hours at $400-1,000 cost. ^[gpu-hours-for-fine-tuning-llms.md]

## Performance and Cost Trade-offs

### Spot vs On-Demand Pricing
Spot instances offer substantial savings, with GCP spot pricing representing approximately 30% of on-demand costs for A100 hardware. However, spot instances carry interruption risk that may extend total training time if checkpointing and resumption are required. ^[gpu-hours-for-fine-tuning-llms.md]

### Hardware Performance Scaling
H100 GPUs deliver 1.7-2.5x faster training compared to A100 hardware, but at 2-3x higher hourly costs. This creates a break-even point where H100 becomes cost-effective for longer training runs despite higher per-hour pricing. ^[gpu-hours-for-fine-tuning-llms.md]
