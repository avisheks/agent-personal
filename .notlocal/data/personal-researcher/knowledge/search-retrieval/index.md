# Knowledge Base Index

## General
- [BM25 Scoring Algorithm](bm25-scoring-algorithm.md) — A probabilistic ranking function based on term frequency and inverse document frequency with saturation and length normalization, serving as the foundation for lexical retrieval systems.
- [Cross-Encoder Reranking](cross-encoder-reranking.md) — A reranking technique that uses transformer models to jointly encode query and document pairs for fine-grained relevance scoring, typically applied to a smaller candidate set retrieved by faster methods.
- [Dense Vector Retrieval](dense-vector-retrieval.md) — A semantic retrieval approach using neural embeddings and approximate nearest neighbor search to find documents similar to query embeddings in high-dimensional vector space.
- [HNSW (Hierarchical Navigable Small World)](hnsw-hierarchical-navigable-small-world.md) — A graph-based approximate nearest neighbor algorithm that builds multi-layer navigable graphs for efficient similarity search in high-dimensional vector spaces.
- [Hybrid Retrieval](hybrid-retrieval.md) — A retrieval approach that combines sparse (BM25) and dense (embedding-based) retrieval methods using fusion techniques like Reciprocal Rank Fusion to leverage the complementary strengths of both systems.
- [Query Understanding Pipeline](query-understanding-pipeline.md) — A preprocessing system that performs spell correction, entity detection, intent classification, and query expansion before retrieval to improve search quality and coverage.
- [Reciprocal Rank Fusion (RRF)](reciprocal-rank-fusion-rrf.md) — A rank-based fusion method that combines results from multiple retrieval systems by summing reciprocal ranks, providing a parameter-free way to merge sparse and dense retrieval results.
- [SPLADE (Sparse Lexical and Expansion)](splade-sparse-lexical-and-expansion.md) — A learned sparse representation method that produces vocabulary-sized sparse vectors for documents and queries, combining the efficiency of inverted indexes with semantic understanding through term expansion.
