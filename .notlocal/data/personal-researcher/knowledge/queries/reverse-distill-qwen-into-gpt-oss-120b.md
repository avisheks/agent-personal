---
title: "Suppose I want to (reverse) distill qwen performance into gpt-oss-120b. When is that possible vs. not?"
summary: "Possible via SFT on Qwen3-32B outputs + LoRA when the target capability (e.g., multilingual) is latent in GPT-OSS-120B's 117B parameters. NOT possible via logit distillation (tokenizer mismatch) or weight merging (architecture mismatch). Fails when the transfer is style mimicry without genuine capability signal, or when MoE routing is disrupted. Recommended: generate multilingual data from Qwen3, mix with replay data, LoRA fine-tune GPT-OSS on single H100."
type: "query"
createdAt: "2026-06-06T00:00:00Z"
---
## Short Answer

**Yes, it's feasible — but only via output-level methods, not weight-level methods.**

You CAN:
- Fine-tune GPT-OSS-120B on Qwen3-32B-generated data (SFT on outputs)
- Use LoRA to add capabilities while preserving existing ones
- Target specific MoE experts for selective fine-tuning (ESFT)

You CANNOT:
- Do logit-level distillation (different tokenizers)
- Merge weights directly (different architectures: dense vs MoE)
- Transfer capabilities the student has zero latent capacity for

## When It Works

| Scenario | Method | Why It Works |
|----------|--------|-------------|
| Add multilingual to GPT-OSS | SFT on Qwen3 multilingual outputs | GPT-OSS's 117B params likely have latent multilingual capacity in unused experts |
| Improve coding style/patterns | SFT + replay data | Signal is genuine and evaluable |
| Transfer dual thinking modes | Off-policy distillation (thinking + non-thinking outputs) | Qwen3's documented approach for its own smaller models |
| Domain-specific capability boost | LoRA on targeted experts | ESFT shows routing is task-concentrated |

**Key principle**: Weak-to-strong works when the strong model has **latent capabilities** the weak signal helps *elicit*. GPT-OSS-120B has 117B total params but only uses 5.1B per token — massive untapped capacity.

## When It Does NOT Work

| Scenario | Why It Fails |
|----------|-------------|
| Qwen3 knows languages GPT-OSS was never trained on | Cannot inject knowledge that has zero representation in weights |
| Style-only transfer (format without substance) | Student mimics output patterns but fails on novel tasks [arXiv:2305.15717] |
| Logit distillation | Qwen3 and GPT-OSS have incompatible tokenizers/vocabularies |
| Weight merging / task arithmetic | Architecturally impossible (32B dense ≠ 117B MoE) |
| Full fine-tune without replay | Catastrophic forgetting destroys reasoning capability |
| Exceeding teacher ceiling | Cannot beat Qwen3's multilingual quality through imitation alone |

## Recommended Approach

```
Step 1: Generate data
  └─ Use Qwen3-32B to generate diverse multilingual outputs
     (translation, QA, summarization, coding) across 50+ languages

Step 2: Mix with replay data
  └─ 30-50% Qwen3 multilingual data
  └─ 50-70% GPT-OSS existing capability data (reasoning, math, coding)
     → Prevents catastrophic forgetting

Step 3: Fine-tune with LoRA
  └─ LoRA on GPT-OSS-120B (fits single H100 with MXFP4)
  └─ "Learns less, forgets less" — preserves reasoning [arXiv:2405.09673]

Step 4: Evaluate BOTH dimensions
  └─ Multilingual benchmarks (MMMLU, translation quality)
  └─ Reasoning benchmarks (AIME, GPQA, Codeforces)
  └─ If reasoning degrades >2%, reduce multilingual data ratio

Step 5 (Advanced): Expert-targeted training
  └─ Analyze routing: which of 128 experts handle multilingual tokens?
  └─ ESFT: fine-tune only those experts; freeze rest [arXiv:2407.01906]
```

## Licensing

Both Qwen3-32B and GPT-OSS-120B are **Apache 2.0**. Fully legal to:
- Generate training data from Qwen3
- Fine-tune GPT-OSS on that data
- Distribute the resulting model
- Use commercially

Machine-generated outputs are not copyrightable. No restrictions apply.

## Precedents

| Example | Direction | Method | Result |
|---------|-----------|--------|--------|
| OpenAI weak-to-strong (2023) | GPT-2 → GPT-4 | SFT + confidence loss | Recovered near-GPT-3.5 |
| DeepSeek-R1 (2025) | 671B MoE → Qwen2.5 32B dense | SFT on reasoning traces | Beat o1-mini |
| Knowledge Fusion (ICLR 2024) | Llama-2 + MPT + OpenLLaMA | Generative distributions | Exceeded individual sources |
| Alpaca/Vicuna ecosystem | ChatGPT → larger base models | SFT on outputs | Widespread success |

## Key Insight

This is **selective capability augmentation**, not classical distillation. You're using Qwen3-32B's multilingual outputs as high-quality training signal to **activate latent multilingual pathways** in GPT-OSS-120B's 128-expert pool. The 5.1B active params per token limit expressiveness, but the full 117B param pool likely contains under-utilized multilingual experts that can be strengthened via targeted fine-tuning.

## Related

- [[Reverse Distillation: Qwen3-32B → GPT-OSS-120B Feasibility]]
- [[Strong-to-Weak Distillation]]
- [[Reasoning Model Distillation]]
- [[Cross-Architecture Generalization]]
