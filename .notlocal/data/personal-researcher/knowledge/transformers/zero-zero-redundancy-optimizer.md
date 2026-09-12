---
title: "ZeRO (Zero Redundancy Optimizer)"
summary: "Microsoft's approach to distributed training that progressively shards optimizer states, gradients, and model weights across GPUs to eliminate redundant storage while maintaining data parallelism."
sources:
  - transformers/large-language-model-llm-training-intro-final.md
createdAt: 2026-06-16T14:44:33.390509+00:00
updatedAt: 2026-06-16T14:44:33.390509+00:00
---
# ZeRO (Zero Redundancy Optimizer)

ZeRO (Zero Redundancy Optimizer) is a memory optimization technique developed by Microsoft that enables training of large language models by eliminating redundant memory usage across distributed GPUs. ZeRO addresses the fundamental memory bottleneck that occurs when training large models where traditional data parallelism requires each GPU to store identical copies of model parameters, gradients, and optimizer states.

## The Memory Problem

During training, large language models require significantly more memory than during inference. For a 70B parameter model, the memory requirements include weights (140GB), gradients (140GB), and AdamW optimizer states (560GB), totaling 840GB—far exceeding the capacity of even the largest available GPUs with 141GB of memory. The optimizer state alone consumes 4× more memory than the model weights themselves, making this the primary bottleneck for distributed training. ^[Large Language Model (LLM) Training - Intro - final.pdf]

Traditional data parallelism exacerbates this problem by requiring each GPU to maintain complete copies of all training states. With eight GPUs storing eight identical copies of a 560GB optimizer state, the redundancy becomes a critical limitation for scaling model training. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## ZeRO Stages

ZeRO progressively eliminates memory redundancy through three stages of optimization:

### Stage 1: Optimizer State Partitioning
Each GPU stores only its assigned slice of optimizer states rather than complete copies. For example, with 8 GPUs training a model with parameters numbered 0 to 70B, GPU 0 handles parameters 0-8.75B, GPU 1 handles 8.75B-17.5B, and so forth. This approach reduces optimizer memory usage by 8× across the cluster. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Stage 2: Gradient Partitioning  
After computing gradients during backpropagation, instead of performing an all-reduce operation where every GPU receives all gradients, ZeRO uses reduce-scatter so each GPU only retains gradients for its assigned parameters. This eliminates gradient redundancy and provides another 8× memory reduction. ^[Large Language Model (LLM) Training - Intro - final.pdf]

### Stage 3: Parameter Partitioning
The most aggressive optimization shards the model weights themselves across GPUs. During the forward pass, each GPU gathers only the weights it needs for computation, processes them, then discards them. This requires gathering weights twice per layer (forward and backward passes), but enables a 70B model to fit within 105GB per GPU. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Key Characteristics

ZeRO maintains the computational pattern of data parallelism while optimizing memory usage. Each GPU continues to process different data samples and runs the complete model, but temporarily gathers whatever weights it needs rather than storing everything permanently. This distinguishes ZeRO from [[mixture-of-experts-moe]] architectures or model parallelism approaches that fundamentally change how computation is distributed. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The technique preserves training dynamics identical to standard data parallelism since gradients are computed and aggregated in the same manner—only the storage and communication patterns change. This ensures that ZeRO-trained models achieve the same convergence properties as traditional approaches while dramatically reducing memory requirements. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Implementation and Adoption

Microsoft's DeepSpeed framework implements ZeRO along with additional memory optimizations like CPU offloading for cases where models exceed GPU memory capacity entirely. The combination of ZeRO with other techniques enables training of models that would otherwise be impossible on available hardware. ^[Large Language Model (LLM) Training - Intro - final.pdf]

ZeRO is frequently combined with other parallelism strategies in production systems. A typical 650B parameter model deployment across 512 GPUs might use tensor parallelism within nodes, pipeline parallelism across nodes, and ZeRO for memory optimization, creating a three-dimensional parallelism approach that matches the hierarchical structure of modern GPU clusters. ^[Large Language Model (LLM) Training - Intro - final.pdf]

## Trade-offs and Considerations

While ZeRO dramatically reduces memory usage, it increases communication overhead compared to traditional data parallelism. Stage 3 particularly requires careful consideration since gathering weights multiple times per layer can impact training speed depending on the interconnect bandwidth between GPUs. ^[Large Language Model (LLM) Training - Intro - final.pdf]

The memory savings enable larger batch sizes and longer sequence lengths that often compensate for the additional communication costs by improving GPU utilization. The technique becomes essential for training models beyond what single-GPU memory can accommodate, making it a critical enabler for large-scale [[transformer-architecture]] training. ^[Large Language Model (LLM) Training - Intro - final.pdf]
