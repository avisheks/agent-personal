---
title: "what are key differences in applying LoRA to attention-only vs. attention+FFN layer"
summary: "Based on the provided knowledge pages, I can identify some key differences in applying LoRA to attention-only versus attention+FFN layers:

## Layer Targeting Strategy

The knowledge base indicates that [[Layer Targeting]] best practice involves **starting with narrow layer targeting (typically attention projections) and expanding only if needed**, rather than applying LoRA broadly across all layers.

## Attention-Only Application

When applying LoRA to attention layers only, the typical targets are [[LORA.md]]:
- q_proj (query projection)
- v_proj (value projection) 
- k_proj (key projection)
- o_proj (output projection)

## Attention+FFN Application

When expanding beyond attention layers, LoRA can also target [[LORA.md]]:
- MLP projections (the FFN components)
- Embedding layers

## Adaptive Approaches

The knowledge base mentions that [[LORA.md]] **AdaLoRA dynamically reallocates rank budget during training, assigning higher rank to important layers and lower rank to unimportant layers**."
type: "query"
createdAt: "2026-05-28T19:12:25Z"
---
Based on the provided knowledge pages, I can identify some key differences in applying LoRA to attention-only versus attention+FFN layers:

## Layer Targeting Strategy

The knowledge base indicates that [[Layer Targeting]] best practice involves **starting with narrow layer targeting (typically attention projections) and expanding only if needed**, rather than applying LoRA broadly across all layers.

## Attention-Only Application

When applying LoRA to attention layers only, the typical targets are [[LORA.md]]:
- q_proj (query projection)
- v_proj (value projection) 
- k_proj (key projection)
- o_proj (output projection)

## Attention+FFN Application

When expanding beyond attention layers, LoRA can also target [[LORA.md]]:
- MLP projections (the FFN components)
- Embedding layers

## Adaptive Approaches

The knowledge base mentions that [[LORA.md]] **AdaLoRA dynamically reallocates rank budget during training, assigning higher rank to important layers and lower rank to unimportant layers**. This suggests that when applying LoRA to both attention and FFN layers, different layers may require different rank allocations based on their importance.

## Recommended Approach

The [[LORA.md]] recommended approach is to **start with narrow layer targeting and expand only if needed**, which implies starting with attention-only targeting before considering FFN layers.

However, I don't have enough information in the knowledge base to provide more specific details about performance differences, computational overhead comparisons, or detailed implementation considerations when choosing between attention-only versus attention+FFN targeting strategies.