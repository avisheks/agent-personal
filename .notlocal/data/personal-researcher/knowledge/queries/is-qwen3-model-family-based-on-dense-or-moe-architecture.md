---
title: "is qwen3 model family based on dense or moe architecture?"
summary: "Based on the knowledge pages, the **Qwen3 model family uses both dense and MoE (Mixture of Experts) architectures**.

## Dense Models

The Qwen3 family includes **six dense models** ranging from 0.6B to 32B parameters:
- Qwen3-0.6B (0.6B parameters, 32K context)
- Qwen3-1.7B (1.7B parameters, 32K context)  
- Qwen3-4B (4B parameters, 128K context)
- Qwen3-8B (8B parameters, 128K context)
- Qwen3-14B (14B parameters, 128K context)
- Qwen3-32B (32B parameters, 128K context)

These dense models utilize 100% of their parameters for every token processed, following traditional transformer architectures."
type: "query"
createdAt: "2026-05-18T18:37:08Z"
---
Based on the knowledge pages, the **Qwen3 model family uses both dense and MoE (Mixture of Experts) architectures**.

## Dense Models

The Qwen3 family includes **six dense models** ranging from 0.6B to 32B parameters:
- Qwen3-0.6B (0.6B parameters, 32K context)
- Qwen3-1.7B (1.7B parameters, 32K context)  
- Qwen3-4B (4B parameters, 128K context)
- Qwen3-8B (8B parameters, 128K context)
- Qwen3-14B (14B parameters, 128K context)
- Qwen3-32B (32B parameters, 128K context)

These dense models utilize 100% of their parameters for every token processed, following traditional transformer architectures. [[Qwen3 Language Model]]

## MoE Models

The family also includes **two MoE variants**:
- **Qwen3-30B-A3B**: 30B total parameters with 3B activated per token
- **Qwen3-235B-A22B**: 235B total parameters with 22B activated per token

Both MoE models employ 128 experts with Top-2 expert routing, where each token is dynamically routed to its two most relevant experts. This enables only 5-10% of total model parameters to be active per inference step. [[Qwen3 Language Model Family]]

## Architecture Choice Benefits

The dual approach allows users to choose based on their needs:
- **Dense models** offer predictable compute patterns, consistent latency, and simpler deployment
- **MoE models** provide enhanced capabilities while maintaining computational efficiency, making large-scale performance accessible on more modest hardware

So rather than being based on a single architecture, Qwen3 strategically employs both dense and MoE designs to serve different use cases and deployment scenarios.