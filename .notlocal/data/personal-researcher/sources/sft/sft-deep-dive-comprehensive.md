---
title: "Supervised Fine-Tuning for LLMs — Comprehensive Deep Dive"
url: https://arxiv.org/abs/2305.11206
ingestedAt: 2026-06-09
type: synthesis
additional_sources:
  - https://arxiv.org/abs/2305.16264
  - https://arxiv.org/abs/2203.02155
  - https://arxiv.org/abs/2212.08073
  - https://arxiv.org/abs/2407.21783
  - https://arxiv.org/abs/2312.15685
  - https://arxiv.org/abs/2310.05914
  - https://arxiv.org/abs/2404.10830
  - https://arxiv.org/abs/2106.09685
  - https://arxiv.org/abs/2305.20050
  - https://arxiv.org/abs/2207.14255
  - https://arxiv.org/abs/2412.15115
  - https://arxiv.org/abs/2501.12948
  - https://huggingface.co/docs/trl/sft_trainer
  - https://huggingface.co/blog/personal-copilot
---

# SFT Deep Dive — Data, Loss Functions, Design Choices, Applications, Industry Differences

## Data Preparation

### Quality vs Quantity
- LIMA (2023): 1K examples → 43% preferred over GPT-4 on some benchmarks
- DEITA (ICLR 2024): 6K samples match SOTA (7.55 MT-Bench) via complexity/quality/diversity scoring
- Yi: <10K examples, each verified by ML engineers
- Scaling Data-Constrained (2023): 4 epochs of repetition is free; beyond decays to zero
- Llama 3.1: 10M+ human-annotated across all post-training
- Qwen 2.5: 1M+ SFT samples

### Packing (Critical for Efficiency)
- Best-Fit Decreasing (BFD): TRL's default bin-packing (ICML 2024)
- Results: 2x throughput, 20% memory reduction, 58% hallucination reduction
- Requires flash_attn_varlen_func with cu_seqlens to prevent cross-example attention

### Train-on-Responses-Only
- Standard for chat: loss only on assistant tokens (TRL: assistant_only_loss=True)
- Prevents model from learning to generate user prompts
- Full-sequence loss only for continued pretraining

### Synthetic Data
- Evol-Instruct (WizardLM, ICLR 2024): iterative complexity escalation
- Orca: GPT-4 explanation traces → 13B matches ChatGPT on BBH
- Phi-3: "Textbooks Are All You Need" + heavy web filtering → 3.8B achieves 69% MMLU

## Loss Functions

- Standard CE (next-token): -sum log p(y_t | y_<t) — the default
- Answer-only loss: mask prompt tokens (label=-100)
- NEFTune (2023): noise in embeddings → 29.8% to 64.7% AlpacaEval (massive free improvement)
- Chunked NLL (TRL v1.5.1): 30-50% less VRAM via dropping masked positions before lm_head
- ORPO (2024): combines SFT + preference in single step
- DFT (2025): rectified reward signal during SFT (RL perspective)
- Label smoothing: rarely used in SFT (short training → early stopping suffices)

## Design Choices That Matter

| Choice | Optimal Range | Source |
|--------|--------------|--------|
| Learning rate (7B full) | 1e-5 to 5e-5 | TRL default 2e-5 |
| Learning rate (LoRA) | 1e-4 to 3e-4 | TRL docs |
| Epochs | 1-3 (rarely more) | LIMA, Scaling paper |
| Batch size (effective) | 32-128 | Standard practice |
| Scheduler | Cosine with warmup | StarCoder recipe |
| Precision | BF16 (A100/H100) | TRL default |
| Weight decay | 0 to 0.01 | StarCoder: 0.01 |
| Dropout | Off (0) | LoRA paper: PEFT is better regularizer |
| NEFTune | Enable (+8-35% free) | arXiv:2310.05914 |

## Application Quirks

### Code: FIM (fill-in-middle) at 50% rate, PSM/SPM modes. Does NOT harm autoregressive performance.
### Math: Process supervision (step-level labels) >> outcome-only. PRM800K: 78% MATH.
### Chat: assistant_only_loss, system prompt handling, multi-turn position_ids.
### Tool use: OpenAI JSON schema format, parallel calls, ToolLLM (16K real APIs).
### Long context: LongLoRA extends 7B to 100K on single 8xA100; embedding+norm must be trainable.
### Vision: CLIP encoder + MLP projection; "image encoder/resolution matters most, connector design negligible" (MM1).

## Industry Approaches

| Lab | Pre-training Scale | SFT Data | Unique Approach |
|-----|-------------------|----------|-----------------|
| OpenAI | Undisclosed | Human demos | SFT→RM→PPO (InstructGPT) |
| Anthropic | Undisclosed | Self-critique/revision | Constitutional AI (RLAIF) |
| Meta (Llama 3.1) | 15T+ tokens | 10M+ annotations | SFT→Rejection Sampling→PPO→DPO |
| Google (Gemma 2) | Large | Undisclosed | Knowledge distillation for small models |
| DeepSeek | 14.8T tokens | Cold-start SFT | Pure RL after minimal SFT (GRPO) |
| Qwen 2.5 | 18T tokens | 1M+ curated | 29+ languages, domain variants |
| Mistral | Undisclosed | Undisclosed | Architectural efficiency (SWA, GQA) |
