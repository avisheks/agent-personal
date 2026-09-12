---
title: "multi-resolution-bucketing"
summary: ""
sources:
  - general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md
createdAt: 2026-05-28T19:53:23.126391+00:00
updatedAt: 2026-05-28T19:53:23.126391+00:00
---
# Multi-Resolution Bucketing

Multi-Resolution Bucketing is a training optimization technique used in the LongCat-Image system to efficiently batch images with similar aspect ratios during [[Supervised Fine-Tuning (SFT)]]. This approach enables training on images of varying dimensions while maintaining computational efficiency and memory usage. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Overview

The bucketing system addresses the challenge of training diffusion models on datasets containing images with diverse aspect ratios and resolutions. Rather than resizing all images to a single square resolution (which can cause distortion), multi-resolution bucketing groups images into predefined aspect ratio categories, allowing the model to learn from images in their natural proportions. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Bucketing Strategies

The LongCat-Image system supports three bucketing strategies, each optimized for different base resolutions:

### MAR-256 Strategy
Designed for 256×256 base resolution training with lower computational requirements.

### MAR-512 Strategy  
Optimized for 512×512 base resolution, providing a balance between quality and efficiency.

### MAR-1024 Strategy
The default strategy for high-resolution 1024×1024 training, supporting aspect ratios including 1:1 (square), 3:4 (portrait), and 16:9 (landscape) formats. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Implementation in Training Pipeline

### Data Processing Flow

The bucketing system integrates into the [[Supervised Fine-Tuning (SFT)]] data pipeline through the following process:

1. **Dimension Analysis**: Each training sample's `width` and `height` fields are parsed from the JSONL data format
2. **Bucket Assignment**: The `MultiResolutionDistributedSampler` calculates the aspect ratio and assigns the image to the appropriate bucket
3. **Aspect-Aware Resizing**: Images undergo resizing and center cropping to match their assigned bucket dimensions
4. **Batch Formation**: Samples from the same bucket are grouped together for efficient GPU processing ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Configuration Parameters

The bucketing behavior is controlled through several configuration parameters:

| Parameter | Type | Description |
|---|---|---|
| `aspect_ratio_type` | string | Bucketing strategy: `mar_256`, `mar_512`, or `mar_1024` |
| `resolution` | integer | Target base resolution (e.g., 1024) |
| `width` | integer | Image width in pixels (from data) |
| `height` | integer | Image height in pixels (from data) |

^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Benefits and Advantages

### Computational Efficiency
By grouping images with similar aspect ratios, the system minimizes padding and wasted computation that would occur when batching images of vastly different shapes. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

### Reduced Distortion
Images maintain their natural proportions rather than being forced into a single square format, preserving important visual relationships and preventing training artifacts.

### Memory Optimization
Consistent tensor shapes within each batch enable more predictable memory usage patterns and better GPU utilization during training. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Integration with Training Components

Multi-resolution bucketing works in conjunction with several other training system components:

- **Data Loading**: The `MultiResolutionDistributedSampler` coordinates with the DataLoader to ensure proper batch formation
- **Distributed Training**: Bucket assignments are coordinated across multiple GPUs to maintain balanced workloads
- **Loss Computation**: The bucketing strategy ensures consistent tensor dimensions for efficient loss computation ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

## Technical Implementation

The bucketing system operates at the dataset level, analyzing image dimensions before training begins. The `MultiResolutionDistributedSampler` maintains separate queues for each aspect ratio bucket and ensures that batches contain only images from the same bucket. This approach eliminates the need for dynamic padding during training while maintaining the benefits of batch processing. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]

The system automatically handles edge cases where certain buckets may have fewer samples, implementing strategies to balance training across all aspect ratios to prevent bias toward more common image shapes. ^[general/supervised-fine-tuning-sft-meituan-longcat-longcat-image-deepwiki.md]
