# Knowledge Base Index

## General
- [Contextual Chunking](contextual-chunking.md) — A chunking strategy that prepends document-level context to each chunk to make them self-contained and improve retrieval accuracy.
- [Cross-Encoder Reranking](cross-encoder-reranking.md) — A two-stage retrieval architecture where a cross-encoder model jointly scores query-document pairs to improve precision after initial retrieval.
- [Hierarchical Chunking](hierarchical-chunking.md) — A document processing strategy that uses small chunks for retrieval precision and expands to larger parent chunks for generation context.
- [Hybrid Retrieval](hybrid-retrieval.md) — A retrieval approach that combines sparse (BM25) and dense (embedding-based) search methods to capture both exact keyword matches and semantic similarity.
- [Lost in the Middle](lost-in-the-middle.md) — A phenomenon where language models perform worse on information placed in the middle of long context windows due to attention patterns and training biases.
- [Multi-Hop Reasoning](multi-hop-reasoning.md) — A capability for handling complex queries that require joining information across multiple documents through iterative retrieval and structured synthesis.
- [Self-RAG](self-rag.md) — An adaptive RAG system that uses reflection tokens to decide when to retrieve, assess relevance, and critique its own outputs.
- [Token Economics](token-economics.md) — The cost optimization principle that generation token costs dominate RAG system expenses, making prompt size reduction the highest-leverage optimization.
