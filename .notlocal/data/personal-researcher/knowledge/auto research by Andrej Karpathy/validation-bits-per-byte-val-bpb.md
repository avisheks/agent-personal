---
title: "Validation Bits Per Byte (val_bpb)"
summary: "A vocabulary-size-independent metric for evaluating language model performance that measures compression efficiency and enables fair comparison across different architectures."
sources:
  - auto research by Andrej Karpathy/github-karpathy-autoresearch-ai-agents-running-research-on-single-gpu-nanochat-training-automatically-github.md
  - auto research by Andrej Karpathy/karpathy-autoresearch-explained-100-experiments-overnight.md
createdAt: 2026-05-25T16:01:14.916653+00:00
updatedAt: 2026-05-25T16:01:14.916653+00:00
---
# Validation Bits Per Byte (val_bpb)

**Validation Bits Per Byte (val_bpb)** is a metric used to evaluate language model performance that measures how efficiently a model encodes text during validation. Lower values indicate better performance, as they represent more efficient compression of the validation data. The metric is particularly valuable in automated machine learning research because it provides vocabulary-size-independent scoring, allowing fair comparison across different model architectures and tokenization schemes.

## Definition and Calculation

Validation bits per byte quantifies the average number of bits required to encode each byte of text in the validation dataset using the model's learned probability distribution. The metric is derived from the model's cross-entropy loss on validation data, converted to a bits-per-byte representation that normalizes for different vocabulary sizes and tokenization approaches. ^[autoresearch-explained.md]

## Key Properties

### Vocabulary Independence

The primary advantage of val_bpb over traditional perplexity metrics is its independence from vocabulary size. This property enables direct comparison between models that use different tokenizers, vocabulary sizes, or even completely different architectures. An agent optimizing for val_bpb can experiment with changing the tokenizer, number of layers, or attention mechanisms while maintaining comparable results across all configurations. ^[autoresearch-explained.md]

### Gaming Resistance

Unlike metrics tied to vocabulary size, val_bpb prevents agents from artificially improving scores by simply adjusting vocabulary parameters. This constraint ensures that improvements reflect genuine advances in model quality rather than metric manipulation. ^[autoresearch-explained.md]

## Applications in Automated Research

### Autoresearch Framework

Val_bpb serves as the primary evaluation metric in automated machine learning research systems, particularly in frameworks where AI agents autonomously modify training code. In these systems, every experiment is scored using val_bpb as the single decisive metric for determining whether to keep or revert code changes. The metric's consistency across architectural variations makes it suitable for overnight autonomous experimentation where agents may test hundreds of different configurations. ^[autoresearch-explained.md]

### Fixed-Time Budget Evaluation

In time-constrained training scenarios, val_bpb provides a reliable comparison metric regardless of the specific model configuration chosen by an optimization agent. Whether an agent selects a larger model with fewer training steps or a smaller model with more iterations within the same time budget, val_bpb scores remain directly comparable. ^[autoresearch-explained.md]

## Implementation in Practice

### Karpathy's Autoresearch

In Andrej Karpathy's autoresearch framework, val_bpb is calculated during a fixed 5-minute training window and serves as the sole metric for autonomous experiment evaluation. The agent reads the validation score after each training run and uses it to decide whether to commit changes to the codebase or revert to the previous state. This approach enabled the discovery of genuine improvements through systematic overnight experimentation, with agents running approximately 700 experiments and finding around 20 measurable improvements. ^[github-karpathy-autoresearch.md] ^[autoresearch-explained.md]

### Real-World Results

The metric has proven effective in practical applications, with researchers reporting significant improvements when optimizing for val_bpb. In documented cases, overnight optimization sessions have achieved performance gains such as 11% speedups in time-to-convergence and smaller models outperforming larger baselines by 19% when optimized specifically for the val_bpb metric. ^[autoresearch-explained.md]

## Relationship to Other Metrics

Val_bpb relates closely to [[Perplexity as SFT Predictor]] and other language modeling evaluation approaches, but offers distinct advantages in automated research contexts. While perplexity measures average uncertainty per token, val_bpb normalizes this uncertainty to a per-byte basis that remains consistent across different tokenization schemes. ^[autoresearch-explained.md]

## Technical Considerations

The metric requires careful implementation of the evaluation pipeline to ensure consistency across experiments. In automated research frameworks, the evaluation function is typically locked and cannot be modified by optimization agents, preventing manipulation of the scoring mechanism while allowing full flexibility in model architecture and training procedures. The fixed evaluation ensures that all improvements measured by val_bpb represent genuine advances in model compression efficiency rather than artifacts of changing evaluation criteria. ^[autoresearch-explained.md] ^[github-karpathy-autoresearch.md]
