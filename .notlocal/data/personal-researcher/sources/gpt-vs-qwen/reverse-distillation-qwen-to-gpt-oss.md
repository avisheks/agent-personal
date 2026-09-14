---
title: "Reverse Distillation Feasibility: Qwen3-32B into GPT-OSS-120B"
url: "multiple (arXiv:2312.09390, arXiv:2305.15717, arXiv:2501.12948, arXiv:2306.13649, arXiv:2407.01906, arXiv:2401.10491, arXiv:2405.09673)"
ingestedAt: "2026-06-06T00:00:00Z"
type: "paper"
---

# Reverse Distillation: Qwen3-32B → GPT-OSS-120B

## Key Papers

### Weak-to-Strong Generalization (OpenAI, arXiv:2312.09390)
- Burns et al. 2023
- GPT-4 finetuned with GPT-2-level supervision + auxiliary confidence loss recovered near-GPT-3.5 performance
- Critical insight: weak-to-strong works because the strong model has LATENT capabilities the weak signal helps elicit
- Not injection of new knowledge but activation of dormant capability

### The False Promise of Imitating Proprietary LLMs (arXiv:2305.15717)
- Gudibande et al.
- Models trained on another model's outputs learn to mimic style/format but fail to close genuine capability gaps
- "Closes little to none of the gap on tasks not heavily supported in the imitation data"
- Failure mode: style mimicry without substance

### DeepSeek-R1 Cross-Architecture Distillation (arXiv:2501.12948)
- Distilled 671B MoE (37B active) into dense Qwen2.5 and Llama3 variants
- Method: SFT on teacher-generated reasoning data
- DeepSeek-R1-Distill-Qwen-32B outperformed o1-mini
- Proved cross-architecture distillation works at scale

### GKD: Generalized Knowledge Distillation (arXiv:2306.13649)
- Singh et al.
- Addresses covariate shift: trains on student's own distribution
- Student generates outputs, teacher scores/corrects them
- Better for maintaining student's existing capabilities

### ESFT: Expert-Specialized Fine-Tuning for MoE (arXiv:2407.01906)
- "Routing distribution for a specific task tends to be highly concentrated"
- "Varies significantly across different tasks"
- Can selectively fine-tune only task-relevant experts while freezing others
- Preserves other capabilities

### Knowledge Fusion (arXiv:2401.10491, ICLR 2024)
- Cross-architecture transfer via generative distributions
- Tested across Llama-2, MPT, OpenLLaMA (different architectures)
- Improves reasoning, commonsense, and code generation
- Architecture-agnostic: works through outputs, not weights

### LoRA Learns Less and Forgets Less (arXiv:2405.09673)
- LoRA preserves base model capabilities better than full fine-tuning
- Lower forgetting on prior knowledge
- Ideal for selective capability addition

### Somerstep et al. Refinement-Based Weak-to-Strong (arXiv:2405.16236)
- Auxiliary confidence loss mitigates imitation of teacher errors
- Naive SFT on teacher outputs has "fundamental limitations"

### PESC: Dense-to-MoE Conversion (arXiv:2401.02731)
- Integrates adapters into MoE layers
- Differentiates experts without altering individual weights

## Licensing

- Qwen3-32B: Apache 2.0 — allows commercial use, modification, derivative works
- GPT-OSS-120B: Apache 2.0 — same permissions
- No conflict. Machine-generated outputs not copyrightable. Fully legal to use Qwen3-32B outputs to train GPT-OSS-120B.

## Architecture Mismatch Challenges

- Different tokenizers → logit-level distillation impractical
- Direct weight merging impossible (different architectures/dimensions)
- MoE routing disruption risk when shifting token distributions
- Only 5.1B active params per forward pass limits per-token capacity

## Recommended Practical Approach

1. Generate multilingual data from Qwen3-32B (diverse tasks, languages, difficulty)
2. Mix with GPT-OSS-120B capability demonstrations (30-50% new / 50-70% replay)
3. Fine-tune with LoRA on GPT-OSS-120B (single H100)
4. Evaluate on both multilingual AND existing reasoning/coding benchmarks
5. If expert-level access available: ESFT-style targeted expert training
