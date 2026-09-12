---
title: "dataset-packing"
summary: ""
sources:
  - general/supervised-fine-tuning-hugging-face.md
createdAt: 2026-05-28T22:22:27.979368+00:00
updatedAt: 2026-05-28T22:22:27.979368+00:00
---
# Dataset Packing

Dataset packing is an optimization technique used in supervised fine-tuning that allows multiple short examples to be combined into the same input sequence, maximizing GPU utilization during training. This approach is particularly valuable when working with datasets containing examples of varying lengths, as it reduces computational waste from padding tokens and improves training efficiency. ^[supervised-fine-tuning-hugging-face.md]

## Overview

The [[SFTTrainer]] supports example packing to optimize training efficiency by combining multiple short examples into single input sequences. When packing is enabled, the trainer automatically handles the combination of examples while maintaining proper formatting and attention masks. This technique is especially beneficial when training on datasets with significant variation in example lengths, as it minimizes the need for padding tokens that would otherwise consume GPU memory without contributing to learning. ^[supervised-fine-tuning-hugging-face.md]

## Implementation

To enable dataset packing in the [[SFTTrainer]], simply set `packing=True` in the SFTConfig constructor. The basic implementation requires minimal configuration changes to existing training setups. ^[supervised-fine-tuning-hugging-face.md]

```python
training_args = SFTConfig(packing=True)

trainer = SFTTrainer(model=model, train_dataset=dataset, args=training_args)

trainer.train()
```

When using packed datasets with `max_steps`, training may run for more epochs than expected depending on the packing configuration. This occurs because packing changes the effective number of examples processed per step, potentially requiring more iterations to reach the specified maximum steps. ^[supervised-fine-tuning-hugging-face.md]

## Custom Formatting Functions

For datasets with multiple fields, custom formatting functions can be defined to control how examples are combined during packing. These functions take a list of examples and return a dictionary with the packed input sequence, allowing precise control over how different data fields are merged. ^[supervised-fine-tuning-hugging-face.md]

```python
def formatting_func(example):
    text = f"### Question: {example['question']}\n ### Answer: {example['answer']}"
    return text

training_args = SFTConfig(packing=True)
trainer = SFTTrainer(
    "facebook/opt-350m",
    train_dataset=dataset,
    args=training_args,
    formatting_func=formatting_func,
)
```

A formatting function should handle the combination of fields like question-answer pairs into a single coherent input sequence. This approach is particularly useful when working with structured datasets that require specific formatting patterns to maintain training effectiveness. ^[supervised-fine-tuning-hugging-face.md]

## Evaluation Considerations

For evaluation datasets, packing can be disabled by setting `eval_packing=False` in the SFTConfig. This separation allows for more controlled evaluation while still benefiting from packing efficiency during training phases. The ability to configure packing separately for training and evaluation provides flexibility in balancing efficiency with evaluation accuracy. ^[supervised-fine-tuning-hugging-face.md]

## Benefits and Trade-offs

Dataset packing offers significant computational advantages by reducing wasted GPU cycles on padding tokens. However, it requires careful consideration of how examples are combined to ensure that the packed sequences maintain meaningful training signals. The technique is most effective with datasets containing substantial length variation, where traditional padding would result in significant computational overhead. ^[supervised-fine-tuning-hugging-face.md]
