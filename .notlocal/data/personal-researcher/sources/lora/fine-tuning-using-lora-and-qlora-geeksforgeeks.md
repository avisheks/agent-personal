---
title: "Fine-Tuning using LoRA and QLoRA - GeeksforGeeks"
source: "https://www.geeksforgeeks.org/deep-learning/fine-tuning-using-lora-and-qlora/"
ingestedAt: "2026-05-28T19:15:43Z"
---
Fine tuning updates all the parameters of a pre-trained model to adapt it for a specific task, offering high accuracy but requiring significant computational resources and memory. In contrast, LoRA (Low-Rank Adaptation) is a [parameter-efficient technique](https://www.geeksforgeeks.org/artificial-intelligence/what-is-parameter-efficient-fine-tuning-peft/) that introduces small trainable matrices into certain layers, allowing most of the original model parameters to remain unchanged. This approach drastically reduces memory and compute requirements, making LoRA much faster and more efficient than full finetuning, especially for large language models, while still achieving comparable performance on many tasks.

LoRA vs QLoRA

## What is Fine-Tuning?

[Fine-tuning](https://www.geeksforgeeks.org/deep-learning/what-is-fine-tuning/) involves taking a pre-trained language model (which has already learned a vast amount of general knowledge and language patterns from a diverse dataset) and further training it on a smaller, task-specific, or domain-specific dataset.This process “adjusts” the model’s internal parameters (weights) to better understand and generate text aligned with the nuances, jargon, style, or specific tasks of the new data.

### Traditional Fine-Tuning

In its original form, fine-tuning involves updating all, or a significant portion, of a pre-trained model’s parameters.For models with hundreds of millions or even billions of parameters, this is a computationally intensive and resource-demanding process. It requires substantial GPU power, memory, and time, making it less practical for frequent updates or for users with limited hardware. The output is a new, specialized version of the entire model.

Simple vs Base vs Fine-Tuned Model

## LoRA (Low-Rank Adaptation)

### How LoRA Works 

The below image shows a [transformer ](https://www.geeksforgeeks.org/machine-learning/getting-started-with-transformers/)block architecture where ****adapters**** are inserted after the feed-forward network and before layer normalization. In [LoRA](https://www.geeksforgeeks.org/deep-learning/what-is-low-rank-adaptation-lora/), these adapters are implemented as low-rank matrices. During fine-tuning, only these adapter parameters are updated, while the core model weights (multi-head attention, feed-forward network, etc.) stay fixed.

Adapter Layer in LoRA

  * ****Adapters in the Stack:**** Each transformer block contains a small adapter module.
  * ****Parameter Update:**** Only the adapters (the low-rank matrices) are updated during training, greatly reducing the number of trainable parameters.



## Key Features of LoRA (Low-Rank Adaptation) for Fine-Tuning Large Models

  * ****Parameter-Efficient Fine-Tuning**** : LoRA introduces small, trainable low-rank matrices into specific layers of a pre-trained model, allowing only these adapters to be updated during fine-tuning, while the vast majority of the model's parameters remain frozen.
  * ****Reduced Trainable Parameters**** : Typically, only 0.5–5% of the model’s parameters are updated, as opposed to 100% in full finetuning. This makes LoRA much faster and less resource intensive.
  * ****Memory Efficiency**** : LoRA significantly reduces memory and hardware requirements. For example, a 1GB model may need just 2GB of VRAM for LoRA finetuning, compared to 16GB+ for full finetuning.
  * ****Implementation Simplicity**** : LoRA is widely supported in libraries like HuggingFace PEFT, making it easy to integrate into existing workflows.
  * ****Low Overfitting Risk**** : By training fewer parameters, LoRA helps avoid overfitting, especially with smaller datasets.
  * ****Modularity**** : LoRA adapters can be swapped in and out for different tasks, enabling flexible multi-task deployment without retraining the entire model.
  * ****No Inference Latency**** : Once fine-tuned, LoRA adapters can be merged into the main model weights, so there is no additional inference cost.



Below are the three scenarios compared where each scenario reduces the number of trainable parameters and resource requirements, with LoRA and QLoRA being the most efficient for fine-tuning large models.

Scenarios Compared

  * ****Scenario 1:**** [Full finetuning](https://www.geeksforgeeks.org/deep-learning/fine-tuning-large-language-model-llm/) All 345M model parameters are updated.
  * ****Scenario 2:**** Adapter tuning Only 24M adapter parameters are updated (1M per adapter × 24).
  * ****Scenario 3:**** LoRA Just 12M low-rank adapter parameters are updated (0.5M × 12 × 2).
  * ****QLoRA:**** Like LoRA, but with quantized (lower precision) weights, further reducing parameter count and memory use.



## QLoRA (Quantized LoRA)

[QLoRA](https://www.geeksforgeeks.org/nlp/fine-tuning-large-language-models-llms-using-qlora/) (Quantized LoRA) works by loading the base language model in a highly compressed 4-bit quantized format, drastically reducing memory usage, while training small LoRA adapters in higher precision. During fine-tuning, only these adapters are updated, compensating for any quantization errors and preserving model performance. This approach allows you to efficiently fine-tune massive models on standard GPUs, combining aggressive memory savings with the parameter efficiency of LoRA and maintaining competitive results.

****Training Process**** :

  * The pretrained model is loaded with quantized 4-bit weights.
  * Only the LoRA adapters are updated during training.
  * Libraries like BitsAndBytes (for quantization) and PEFT (for LoRA) are used together for implementation.
  * Example code involves setting up quantization configs, enabling gradient checkpointing, and applying LoRA adapters to target modules (e.g., query, key, value layers).



## Key Features of QLoRA

  * ****Further Memory Reduction**** : QLoRA extends LoRA by quantizing the main model weights to 4 bits (using methods like NF4), while keeping the LoRA adapters in higher precision (e.g., 16-bit).
  * ****Ultra-Low Resource Requirements**** : QLoRA can fine-tune very large models (billions of parameters) on consumer-grade GPUs or even CPUs by reducing VRAM needs to as little as 0.5GB per 1GB model.
  * ****Performance**** : QLoRA has been shown to maintain comparable accuracy to standard LoRA and full fine-tuning, even on very large models. In many cases, performance loss is negligible or non-existent.
  * ****Adapter Placement**** : For QLoRA, it is often recommended to apply LoRA adapters to all linear transformer blocks, not just the query/key/value layers, especially for larger models.
  * ****Double Quantization**** : QLoRA may use double quantization techniques to further compress storage, especially for scale/offset constants.
  * ****Mitigating Quantization Loss**** : QLoRA uses LoRA as an accessory to correct for any errors introduced by quantization, ensuring high accuracy is maintained.
  * ****Trade-offs**** : While QLoRA is slightly slower than LoRA due to quantization/dequantization steps, the memory savings are substantial, and the method is highly scalable.



## ****Benchmarks and Findings****

### ****LoRA vs. Full Fine-Tuning****

  * LoRA achieves ****competitive performance**** relative to full fine-tuning in tasks like text classification, summarization, and question answering, often matching accuracy while training ****0.2–0.3% of total parameters****. For example, adapter-based LoRA models achieve GLUE scores within 1% of fully fine-tuned models.
  * Full fine-tuning retains an advantage in ****complex domains**** (e.g., mathematics, programming) where precise parameter adjustments are critical, though this gap narrows with proper hyperparameter tuning.
  * LoRA reduces memory usage by ****70%**** compared to full fine-tuning, enabling cost-effective deployment on consumer-grade GPUs.



### ****Adapters and Efficiency Trade-offs****

  * Adapters deliver robust performance with ****substantially lower computational requirements**** , achieving accuracy comparable to full fine-tuning in tasks like sentiment analysis and legal document processing.
  * The primary trade-off for adapters is a ****marginal increase in inference latency**** (10–20%) due to additional layers processed during prediction