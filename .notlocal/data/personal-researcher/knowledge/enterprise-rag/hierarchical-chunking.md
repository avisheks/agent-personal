---
title: "hierarchical-chunking"
summary: ""
sources:
  - enterprise-rag/enterprise-rag-ref.md
createdAt: 2026-05-18T18:34:53.525428+00:00
updatedAt: 2026-05-18T18:34:53.525428+00:00
---
# Hierarchical Chunking

Hierarchical chunking is an advanced document processing strategy for Retrieval-Augmented Generation (RAG) systems that addresses the fundamental tradeoff between retrieval precision and generation context quality. Unlike traditional fixed-size chunking, hierarchical chunking creates multiple granularity levels within the same document, allowing systems to retrieve at fine-grained levels while expanding to broader context for generation. ^[enterprise-rag-ref.md]

## Overview

Traditional chunking approaches force a compromise: small chunks provide precise retrieval but lack sufficient context for coherent answer generation, while large chunks preserve context but dilute retrieval focus and waste context window space. Hierarchical chunking decouples these concerns by maintaining parent-child relationships between chunks of different sizes. ^[enterprise-rag-ref.md]

The approach typically involves creating small chunks (sentence or paragraph level) for retrieval precision, then expanding to larger parent chunks (section level) when constructing prompts for generation. This allows the system to "retrieve small, generate large" — finding the most relevant specific information while providing the language model with sufficient surrounding context. ^[enterprise-rag-ref.md]

## Implementation Architecture

### Two-Level Structure

The most common implementation uses a two-level hierarchy:

- **Child chunks**: 100-200 tokens at sentence or paragraph boundaries for precise retrieval
- **Parent chunks**: 400-800 tokens at section boundaries for generation context

Each child chunk maintains metadata linking it to its parent, enabling the system to retrieve specific information and then expand to the full contextual section during prompt construction. ^[enterprise-rag-ref.md]

### Retrieval and Expansion Process

1. **Initial retrieval**: Query embeddings are matched against the smaller child chunks to identify the most relevant specific passages
2. **Parent expansion**: Retrieved child chunks are expanded to their parent sections to provide fuller context
3. **Deduplication**: If multiple child chunks from the same parent are retrieved, the system serves the parent only once to avoid redundancy

This process ensures that the language model receives coherent, complete sections rather than fragmented pieces that may lack necessary context for accurate generation. ^[enterprise-rag-ref.md]

## Advantages

### Precision Without Context Loss

Hierarchical chunking solves the core tension in chunk size selection. Small chunks enable precise matching between queries and specific facts or statements, while parent expansion ensures the generation model has sufficient context to understand the retrieved information's meaning and relationships. ^[enterprise-rag-ref.md]

### Adaptive Context

The approach naturally adapts to different query types. Factual lookup queries benefit from the precision of small chunk retrieval, while synthesis questions requiring broader understanding benefit from the expanded parent context during generation. ^[enterprise-rag-ref.md]

### Reduced Hallucination

By providing more complete contextual sections rather than fragmented pieces, hierarchical chunking reduces the likelihood that language models will hallucinate connections between unrelated information or misinterpret partial context. ^[enterprise-rag-ref.md]

## Implementation Considerations

### Storage Requirements

Hierarchical chunking requires additional storage overhead compared to single-level approaches, as both child and parent chunks must be indexed. The system must also maintain parent-child relationship metadata, increasing the complexity of the indexing pipeline. ^[enterprise-rag-ref.md]

### Retrieval Logic Complexity

The retrieval system must handle the expansion step, mapping from retrieved child chunks to their parents. This adds complexity to the query processing pipeline and requires careful handling of deduplication when multiple children from the same parent are retrieved. ^[enterprise-rag-ref.md]

### Document Structure Dependency

Effective hierarchical chunking relies on documents having clear structural boundaries (headings, sections, paragraphs) that can serve as natural parent chunk boundaries. Documents with poor structure may not benefit as much from this approach. ^[enterprise-rag-ref.md]

## Alternative Approaches

### Contextual Chunking

[[Contextual Chunking]] represents an alternative approach where each chunk is prepended with document-level context, making individual chunks self-contained rather than relying on hierarchical relationships. ^[enterprise-rag-ref.md]

### Fixed-Size with Overlap

Traditional fixed-size chunking with 10-20% overlap attempts to address boundary issues but doesn't provide the same level of contextual expansion as hierarchical approaches. ^[enterprise-rag-ref.md]

## Production Considerations

### Query Routing Integration

Hierarchical chunking works particularly well with query routing systems that can determine whether a query requires precise factual lookup (benefiting from small chunk retrieval) or broader synthesis (benefiting from parent expansion). ^[enterprise-rag-ref.md]

### Evaluation Metrics

Systems using hierarchical chunking should measure both retrieval precision at the child level and generation quality with expanded parent context. The approach typically improves answer coherence while maintaining or improving retrieval recall. ^[enterprise-rag-ref.md]

### Cost Implications

While hierarchical chunking may increase storage and indexing costs, it often reduces generation costs by providing more relevant context, potentially allowing for fewer chunks in the final prompt while maintaining answer quality. ^[enterprise-rag-ref.md]
