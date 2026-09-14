---
title: "3D Parallelism"
summary: "A distributed training strategy that combines tensor parallelism (within nodes), pipeline parallelism (across nodes), and data parallelism (replicas) to efficiently train massive models on hundreds of GPUs."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:44:53.662548+00:00
updatedAt: 2026-06-16T14:44:53.662548+00:00
---
# 3D Parallelism

**3D Parallelism** is a distributed training strategy that combines three complementary parallelization techniques to train extremely large language models across hundreds or thousands of GPUs. The approach addresses the fundamental memory constraints that make training models with hundreds of billions of parameters impossible on single devices.

## Overview

3D Parallelism emerged as a solution to the memory explosion problem in large language model training. A 70B parameter model requires approximately 840GB of memory during training (140GB for weights, 140GB for gradients, and 560GB for AdamW optimizer state), while the largest available GPUs have only 141GB of memory. Traditional approaches like [[Data Parallel]] training fail at this scale because each GPU would need to store the complete model. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The "3D" refers to the three orthogonal dimensions of parallelization that can be combined:
- **Data Parallel (DP)**: Different GPUs process different batches of training data
- **Tensor Parallel (TP)**: Individual weight matrices are split across GPUs  
- **Pipeline Parallel (PP)**: Sequential layers are distributed across different GPUs

## Component Techniques

### Data Parallel
[[Data Parallel]] training replicates the complete model on each GPU, with different GPUs processing different training samples. After computing gradients, all GPUs perform an all-reduce operation to average gradients before applying identical weight updates. This approach works well for smaller models but becomes impossible when the model itself exceeds single-GPU memory capacity. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Tensor Parallel  
Tensor Parallel splits individual weight matrices across multiple GPUs. For example, a 16384×16384 attention matrix becomes eight 16384×2048 slices distributed across eight GPUs. Each GPU computes only its slice of the matrix multiplication, never storing the complete matrix. This requires communication after every layer, making it viable only within single machines where GPUs connect via high-speed NVLink at 900GB/s. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Pipeline Parallel
[[Pipeline Parallel]] distributes sequential transformer layers across different GPUs, creating an assembly-line computation flow. GPU 0 might compute transformer blocks 1-10, GPU 1 computes blocks 11-20, and so forth. Each GPU only stores and computes its assigned layers. The main drawback is pipeline bubbles where GPUs wait for data to arrive from previous stages. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Implementation Strategy

A typical 3D Parallelism configuration for a 650B parameter model across 512 GPUs combines all three techniques hierarchically:

- **TP=8** within each 8-GPU node (utilizing fast NVLink connections)
- **PP=8** across 8 nodes (one pipeline stage per node)  
- **DP=8** data parallel replicas

This configuration results in each GPU handling approximately 650B ÷ (8×8) = 10.15B parameters, requiring about 51GB of memory per GPU—comfortably fitting within a 141GB H200's capacity. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Communication Hierarchy

The communication patterns in 3D Parallelism are designed to match hardware topology:

- **Tensor Parallel communication** occurs every layer and requires the fastest interconnect (NVLink within nodes)
- **Pipeline Parallel communication** happens between pipeline stages and works over slower network connections
- **Data Parallel communication** occurs once per batch and can operate over any network topology

This hierarchy ensures that the most frequent communications use the fastest available connections. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Memory vs Communication Trade-offs

3D Parallelism represents a fundamental trade-off between memory usage and communication overhead. Every technique that reduces per-GPU memory requirements increases the amount of inter-GPU communication needed. The viability of different configurations depends heavily on the underlying hardware capabilities—900GB/s NVLink can handle aggressive tensor parallelism, while 10GB/s Ethernet cannot. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Fault Tolerance Considerations

As the number of GPUs increases, system reliability becomes a critical concern. With 512 GPUs each having 99.9% uptime, there is only a 60% probability that all GPUs are functioning simultaneously. The complexity of 3D Parallelism makes fault recovery more challenging compared to simpler approaches like pure [[Data Parallel]] training, which can easily redistribute work when nodes fail. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Implementation Frameworks

Several frameworks provide 3D Parallelism capabilities:

- **[[Megatron-LM]]** (NVIDIA): Pioneered efficient tensor and pipeline parallelism with optimized communication patterns
- **DeepSpeed** (Microsoft): Implements [[ZeRO]] optimization along with memory management features
- **Megatron-DeepSpeed**: Combines Megatron's model parallelism with DeepSpeed's memory optimizations, powering most 100B+ parameter model training
- **FSDP**: PyTorch's native implementation providing simpler APIs with fewer features

The choice of framework depends on the specific requirements and scale of the training job. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Related Concepts

3D Parallelism builds upon and integrates with several other distributed training concepts including [[ZeRO]], [[Mixed Precision Training]], [[Gradient Accumulation]], and [[Activation Checkpointing]]. It is essential for training the largest language models in families like [[GPT-OSS-120B]] and [[Qwen3 Language Model]].
