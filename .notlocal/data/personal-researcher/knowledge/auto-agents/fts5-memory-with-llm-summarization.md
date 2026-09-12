---
title: "FTS5 Memory with LLM Summarization"
summary: "A hybrid memory system combining SQLite's full-text search capabilities with LLM-powered summarization for efficient agent memory recall."
sources:
  - auto-agents/hermes-agent-nousresearch.md
createdAt: 2026-06-15T11:25:10.527165+00:00
updatedAt: 2026-06-15T11:25:10.527165+00:00
---
# FTS5 Memory with LLM Summarization

**FTS5 Memory with LLM Summarization** is a hybrid memory architecture that combines SQLite's FTS5 (Full-Text Search 5) indexing capabilities with large language model summarization to provide efficient storage, retrieval, and contextual understanding of conversational and task-based memory in AI agent systems.

## Architecture Overview

The system uses SQLite's FTS5 extension as the underlying storage and indexing layer, which provides fast full-text search capabilities across stored conversations, documents, and interaction histories. When memory retrieval is needed, the FTS5 index returns relevant text segments based on keyword matching and ranking algorithms. These retrieved segments are then processed by a large language model to generate contextual summaries and extract key insights relevant to the current query or task context. ^[hermes-agent.md]

## Implementation in Hermes Agent

[[Hermes Agent]] implements FTS5 memory with LLM summarization as part of its core memory architecture. The system stores user interactions, task outcomes, and learned behaviors in an FTS5-indexed database, enabling rapid retrieval of relevant historical context. When the agent needs to recall information, it queries the FTS5 index and uses LLM summarization to distill the most pertinent details for the current situation. ^[hermes-agent.md]

This approach supports the agent's [[dialectic user modeling]] capabilities, allowing it to maintain personalized understanding across sessions while efficiently managing large volumes of conversational history. ^[hermes-agent.md]

## Technical Benefits

### Search Performance
FTS5 provides efficient full-text search with ranking algorithms that can quickly identify relevant content from large memory stores without requiring vector embeddings or semantic search infrastructure. ^[hermes-agent.md]

### Contextual Processing
The LLM summarization layer adds semantic understanding to the raw search results, enabling the system to extract meaningful patterns and relationships that pure keyword matching might miss. ^[hermes-agent.md]

### Scalability
The hybrid approach balances storage efficiency with retrieval quality, avoiding the computational overhead of maintaining large vector databases while still providing contextually relevant memory recall. ^[hermes-agent.md]

## Integration with Agent Workflows

In [[Hermes Agent]]'s architecture, FTS5 memory with LLM summarization works alongside other memory components including [[Honcho]] for user modeling and the [[AgentSkills Standard]] for skill storage and retrieval. This creates a comprehensive memory system that supports both factual recall and behavioral adaptation. ^[hermes-agent.md]

The system enables [[cross-session personalization]] by maintaining persistent memory of user preferences, interaction patterns, and successful task completion strategies, all accessible through the FTS5 search interface and processed through LLM summarization for contextual relevance. ^[hermes-agent.md]
