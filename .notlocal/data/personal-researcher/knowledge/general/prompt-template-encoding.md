---
title: "prompt-template-encoding"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:54:47.170117+00:00
updatedAt: 2026-05-28T19:54:47.170117+00:00
---
# Prompt Template Encoding

Prompt Template Encoding is a text preprocessing technique used in the [[Supervised Fine-Tuning (SFT)]] pipeline of LongCat-Image to structure and format input prompts before they are tokenized and fed to the model. This approach wraps raw text prompts in a standardized template format to provide consistent context and improve model understanding during training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Template Structure

The prompt template system uses four configuration parameters to define how raw prompts are transformed:

- **`prompt_template_encode_prefix`**: Text prepended before the prompt content
- **`prompt_template_encode_suffix`**: Text appended after the prompt content  
- **`prompt_template_encode_start_idx`**: Token index where the actual prompt content begins
- **`prompt_template_encode_end_idx`**: Token index where the actual prompt content ends

These parameters allow the training system to wrap prompts in structured dialogue formats while maintaining precise control over token boundaries. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Default Template Format

The default template configuration wraps prompts in a system-user-assistant dialogue structure:

```
<|im_start|>system
As an image captioning expert, generate a descriptive text prompt based on an image content, suitable for input to a text-to-image model.<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
```

This format provides explicit context about the task (image captioning) and establishes a conversational framework that helps the model understand its role in the generation process. The `{prompt}` placeholder is replaced with the actual text description from the training data. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Integration with Training Pipeline

Prompt Template Encoding operates within the broader [[Supervised Fine-Tuning (SFT)]] data processing pipeline. After images are loaded and processed through [[Multi-Resolution Bucketing]], text prompts undergo template encoding before tokenization. The system applies the template structure to each prompt, then tokenizes the result with a maximum length of 512 tokens. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The template encoding occurs before the null text replacement process, where prompts are replaced with empty strings at a probability defined by `null_text_ratio` (typically 0.1) to enable [[Classifier-Free Guidance Training]] during training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Purpose and Benefits

Prompt Template Encoding serves several key functions in the training process:

### Contextual Consistency
By wrapping all prompts in the same template structure, the system ensures that the model receives consistent contextual cues about its task and role, leading to more stable training dynamics. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Task Specification  
The system message in the template explicitly defines the model's role as an "image captioning expert," providing clear guidance about the expected behavior and output format. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Dialogue Format Alignment
The conversational structure aligns with common instruction-following patterns used in language model training, potentially improving the model's ability to understand and respond to text-to-image generation requests. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Implementation

The template encoding system processes prompts during the data loading phase of [[Supervised Fine-Tuning (SFT)]]. Each training sample's prompt field is wrapped in the configured template before being passed to the tokenizer. The start and end index parameters allow the system to identify which tokens correspond to the actual prompt content versus the template structure, enabling precise control over attention mechanisms and loss computation. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The encoded prompts are then tokenized with the text encoder's maximum sequence length of 512 tokens, ensuring compatibility with the model's input requirements while maintaining the structured format throughout the training process. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Configuration Parameters

The template encoding behavior is controlled through four key parameters in the training configuration:

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt_template_encode_prefix` | string | Text prepended before the prompt content |
| `prompt_template_encode_suffix` | string | Text appended after the prompt content |
| `prompt_template_encode_start_idx` | integer | Token index where actual prompt content begins |
| `prompt_template_encode_end_idx` | integer | Token index where actual prompt content ends |

These parameters provide flexibility to customize the template structure while maintaining precise token-level control for training optimization. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Data Processing Flow

Within the SFT data processing pipeline, Prompt Template Encoding follows this sequence:

1. **Image Loading**: Images are loaded and processed through multi-resolution bucketing
2. **Template Application**: Raw prompts are wrapped in the configured template structure
3. **Tokenization**: The templated prompts are tokenized with a 512-token maximum length
4. **Null Text Processing**: Templates may be replaced with empty strings based on `null_text_ratio`
5. **Batch Formation**: Processed samples are batched for training

This integration ensures that all text inputs maintain consistent formatting while preserving the flexibility to customize the template structure for different training objectives. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
