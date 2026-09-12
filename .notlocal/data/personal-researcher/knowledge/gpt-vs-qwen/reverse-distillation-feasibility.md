---
title: "Reverse Distillation: Qwen3-32B → GPT-OSS-120B Feasibility"
summary: "Distilling Qwen3-32B capabilities into GPT-OSS-120B is feasible via SFT on teacher outputs + LoRA, but NOT via logit distillation (tokenizer mismatch) or weight merging (architecture mismatch). Works when the target capability is latent in the student. Fails for style mimicry without genuine signal, or when MoE routing is disrupted."
sources:
  - gpt-vs-qwen/reverse-distillation-qwen-to-gpt-oss.md
  - general/strong-to-weak-distillation.md
  - reasoning-llms/reasoning-distillation.md
  - reasoning-llms/reasoning-model-distillation.md
createdAt: "2026-06-06T00:00:00Z"
updatedAt: "2026-06-06T00:00:00Z"
---
# Reverse Distillation: Qwen3-32B → GPT-OSS-120B

Transferring specific capabilities from Qwen3-32B (dense, 32B, strong multilingual) INTO GPT-OSS-120B (MoE, 117B/5.1B active, strong reasoning) is a form of **weak-to-strong** and **cross-architecture** distillation. ^[reverse-distillation-qwen-to-gpt-oss.md]

## When It IS Possible

| Condition | Why It Works | Example |
|-----------|-------------|---------|
| Target capability is **latent** in student | Weak signal elicits dormant capacity | OpenAI: GPT-2 supervision on GPT-4 recovered near-GPT-3.5 [arXiv:2312.09390] |
| Cross-architecture SFT on outputs | Architecture-agnostic via text-level transfer | DeepSeek-R1: 671B MoE → dense Qwen2.5/Llama3 [arXiv:2501.12948] |
| Selective expert fine-tuning (MoE) | Can isolate change to specific experts | ESFT: routing is task-concentrated; freeze unrelated experts [arXiv:2407.01906] |
| LoRA-based fine-tuning | Low-rank preserves existing capabilities | "Learns less, forgets less" [arXiv:2405.09673] |
| Both models Apache 2.0 | No legal barriers to output-based training | Qwen3 + GPT-OSS both Apache 2.0 |
| Teacher provides **genuine signal** | Not style but capability | Works for multilingual: Qwen3 trained on 119 languages, 36T tokens |

## When It Does NOT Work

| Failure Mode | Why It Fails | Mitigation |
|-------------|-------------|------------|
| Style mimicry without substance | Student copies format, not capability [arXiv:2305.15717] | Evaluate on diverse held-out tasks; use GKD (on-policy) |
| Logit-level distillation | Different tokenizers between Qwen3 and GPT-OSS → misaligned vocabularies | Use output-level (text) distillation only |
| Direct weight merging | Completely different architectures/dimensions | Impossible — use output-based methods |
| MoE routing disruption | Fine-tuning shifts token distributions, breaking load balance | ESFT (freeze router, train specific experts) or LoRA |
| Insufficient data coverage | Transfer only works on represented scenarios | Use diverse, multi-task multilingual data |
| Capability ceiling | Cannot exceed teacher quality on transferred domain | Augment with RL after distillation |
| Active params too few (5.1B) | Per-token capacity limit regardless of total params | May cap multilingual performance inherently |

## Practical Methods (Ranked by Feasibility)

### A. SFT on Qwen3 Outputs + LoRA (BEST for this case)
1. Generate multilingual data from Qwen3-32B (diverse tasks, languages)
2. Mix 30-50% new data / 50-70% replay data (GPT-OSS reasoning/coding)
3. LoRA fine-tune on GPT-OSS-120B (fits single H100)
4. Evaluate both multilingual AND reasoning benchmarks

### B. Expert-Specialized Fine-Tuning (ESFT)
1. Analyze GPT-OSS-120B routing patterns for multilingual tokens
2. Identify which of 128 experts activate for multilingual content
3. Fine-tune only those experts; freeze all others + router
4. Maximum preservation of reasoning capability

### C. GKD (On-Policy Distillation)
1. GPT-OSS generates multilingual outputs
2. Qwen3-32B scores/corrects them
3. Train GPT-OSS on its own corrected outputs
4. Avoids covariate shift; maintains student's distribution

### D. Knowledge Fusion
1. Use both models' output distributions as training signal
2. Architecture-agnostic (works through outputs) [arXiv:2401.10491]
3. Proven across Llama-2, MPT, OpenLLaMA

### NOT viable:
- Logit-level distillation (tokenizer mismatch)
- Weight merging / task arithmetic (architecture mismatch)
- Direct expert transplant (incompatible dimensions)

## Key Insight

This is NOT classical "small teacher → large student" distillation. It's **selective capability augmentation**: using Qwen3-32B's multilingual outputs as high-quality training signal to activate **latent multilingual pathways** already present in GPT-OSS-120B's 117B parameters. The 5.1B active params per token limit what can be expressed, but the 128-expert pool may contain under-utilized multilingual experts that can be strengthened.

## Related

- [[Strong-to-Weak Distillation]] — Qwen3's approach for its smaller models
- [[Reasoning Model Distillation]] — DeepSeek-R1's cross-architecture method
- [[Cross-Architecture Generalization]] — SFT strategies that transfer across architectures
- [[GPT-OSS-120B]] — Student model architecture details
- [[Qwen3 Language Model]] — Teacher model capabilities
