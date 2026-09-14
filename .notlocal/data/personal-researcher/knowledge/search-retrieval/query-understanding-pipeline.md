---
title: "query-understanding-pipeline"
summary: ""
sources:
  - search-retrieval/search-retrieval-ref.md
createdAt: 2026-05-28T20:02:54.019432+00:00
updatedAt: 2026-05-28T20:02:54.019432+00:00
---
# Query Understanding Pipeline

A **Query Understanding Pipeline** is a multi-stage preprocessing system that transforms raw user search queries into structured, disambiguated representations before they are sent to retrieval systems. The pipeline performs spell correction, entity detection, intent classification, and query rewriting to improve retrieval quality by bridging the gap between how users express their information needs and how search systems can best fulfill them. ^[search-retrieval-ref.md]

## Overview

Query understanding addresses the fundamental challenge that users often express their search intent using different vocabulary, ambiguous terms, or incomplete information compared to the indexed content. A raw query like "comfortable standing shoes" may need to be expanded to include related terms like "ergonomic footwear" and "cushioned work shoes" to achieve comprehensive retrieval coverage. ^[search-retrieval-ref.md]

The pipeline typically processes queries through several sequential stages: spell correction, entity detection, intent classification, and query rewriting or expansion. Each stage adds structure and context that improves downstream retrieval quality. ^[search-retrieval-ref.md]

## Core Components

### Spell Correction

The first stage corrects typographical errors and normalizes text. This is particularly critical for mobile queries, where typo rates can exceed 40%. The system transforms queries like "runing shoes" to "running shoes" using edit-distance algorithms with domain vocabulary boosting. ^[search-retrieval-ref.md]

### Entity Detection

Entity detection identifies and preserves important structured elements within queries. For a query like "Nike Air Max 90 size 10", the system extracts structured information: brand (Nike), product (Air Max 90), and attribute (size 10). Detected entities receive special treatment in retrieval, often bypassing semantic expansion to ensure exact matching. ^[search-retrieval-ref.md]

### Intent Classification

Intent classification categorizes queries into types that require different retrieval strategies. The three primary categories are:

- **Navigational**: User seeks one specific item (e.g., "Nike Air Max 90")
- **Transactional**: User wants to purchase from a category (e.g., "buy running shoes") 
- **Informational**: User seeks to learn about a topic (e.g., "best shoes for flat feet")

Each intent type routes to optimized retrieval approaches, with navigational queries prioritizing exact matches and informational queries emphasizing broad semantic coverage. ^[search-retrieval-ref.md]

### Query Rewriting and Expansion

The final stage expands queries with synonyms, related terms, or generated paraphrases. A query for "comfortable standing shoes" might be expanded to include "ergonomic footwear OR cushioned work shoes". This expansion can use rule-based synonym dictionaries, trained sequence-to-sequence models, or large language model calls for dynamic rewriting. ^[search-retrieval-ref.md]

## Advanced Techniques

### HyDE (Hypothetical Document Embeddings)

For vague or short queries, HyDE generates a hypothetical ideal answer using a language model, embeds that generated text, and uses it for retrieval. This technique bridges the gap between query language and document language, particularly effective for question-style queries. ^[search-retrieval-ref.md]

### Query Decomposition

Complex queries are broken into constituent parts for separate processing. A query like "Red Nike running shoes under $100 near me" gets decomposed into attribute filters (color=red), brand filters (Nike), category (running shoes), price constraints (<$100), and location filters. ^[search-retrieval-ref.md]

### Session-Aware Processing

For users who search iteratively, the pipeline incorporates previous queries in the session. If a user searches "running shoes" then "arch support", the second query is interpreted as "running shoes with arch support" rather than a standalone query about arch support. ^[search-retrieval-ref.md]

## Domain-Specific Challenges

Query understanding must handle domain-specific vocabulary that generic models often miss. In advertising systems, terms like "CPC" (cost per click), "RoAS" (return on ad spend), and product codes (ASINs) require specialized handling. These terms may need custom tokenization, synonym expansion, or dedicated processing paths to ensure accurate interpretation. ^[search-retrieval-ref.md]

The pipeline must also preserve exact-match requirements for certain query types. When an advertiser searches for their own product code, the system must return that exact product without semantic expansion that might introduce competitors' products. ^[search-retrieval-ref.md]

## Implementation Considerations

### Latency Management

Each pipeline stage adds processing time, with typical budgets of <5ms for spell correction and entity detection, and 10-200ms for query rewriting depending on the method used. Large language model-based rewriting provides the highest quality but requires careful latency management for real-time search applications. ^[search-retrieval-ref.md]

### Quality Safeguards

Query rewriting can inadvertently change user intent if expansion terms are too aggressive. The system typically adds expansion terms as OR conditions rather than replacements, ensuring original query terms maintain highest weight. Conservative expansion strategies only activate when initial retrieval returns insufficient results. ^[search-retrieval-ref.md]

### Evaluation and Monitoring

Pipeline effectiveness is measured through downstream retrieval quality metrics, including zero-result rates, query refinement rates, and user engagement signals. The system maintains evaluation sets of both clean, curated queries and production query samples that include real-world noise like typos and abbreviations. ^[search-retrieval-ref.md]

## Integration with Retrieval Systems

The query understanding pipeline feeds processed queries to both lexical retrieval systems (like [[BM25 Scoring Algorithm]]) and semantic retrieval systems using [[Dense Vector Retrieval]]. Different query types may route to different retrieval strategies - navigational queries emphasizing exact matching while informational queries prioritize semantic similarity. ^[search-retrieval-ref.md]

The pipeline's output provides structured information that retrieval systems can leverage: detected entities for exact matching, intent classifications for strategy selection, and expanded terms for comprehensive coverage. This preprocessing is particularly valuable in [[Hybrid Retrieval]] systems that combine multiple retrieval approaches. ^[search-retrieval-ref.md]
