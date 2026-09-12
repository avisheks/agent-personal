---
title: "Why does GPT-OSS-120B have 78% hallucination rate? Does that make it a poor model for QnA tasks?"
summary: "The 78.2% hallucination rate on SimpleQA is an architectural consequence of MoE sparse activation: only 5.1B of 117B parameters activate per token, so the router may not select the expert storing the needed fact. This makes GPT-OSS-120B poor for FACTUAL QA (closed-book knowledge retrieval) but NOT poor for REASONING QA (math proofs, logic, multi-step analysis) where it dominates. Mitigation: route factual QA to Qwen3-32B (32B active = 6x more factual recall per token) or add retrieval augmentation to ground GPT-OSS in external knowledge."
type: "query"
createdAt: "2026-06-06T00:00:00Z"
---
## Why 78.2% Hallucination?

The hallucination rate is an **architectural consequence** of MoE sparse activation, not a training failure:

```
GPT-OSS-120B architecture:
  Total parameters:    117B (stored across 128 experts)
  Active per token:    5.1B (top-4 of 128 experts selected)
  Utilization ratio:   4.4% of total params active per token
```

**The mechanism:**
1. Facts are distributed across 128 expert networks during training
2. At inference, the router selects 4 experts per token based on the input
3. If the needed fact is stored in expert #87 but the router selects experts #12, #34, #56, #91 → the fact is inaccessible
4. The model confabulates a plausible-sounding answer from the 4 available experts

**Why dense models hallucinate less:**
- Qwen3-32B uses ALL 32B parameters for every token
- Every fact stored anywhere in the model is accessible at every inference step
- 32B active > 5.1B active = 6x more factual recall capacity per token

^[[Qwen3-32B vs GPT-OSS-120B Strengths and Weaknesses]]

## Is It a Poor Model for QnA?

**It depends on what kind of QnA:**

| QnA Type | GPT-OSS-120B Quality | Why |
|----------|---------------------|-----|
| **Factual QA** ("What year was X founded?") | POOR — high hallucination | Needs closed-book recall; 5.1B active params insufficient |
| **Reasoning QA** ("Prove that X implies Y") | EXCELLENT — AIME 95.8% | Deep CoT reasoning, not factual recall |
| **Math QA** ("Solve this equation") | EXCELLENT — GPQA 80.1% | Computation, not knowledge retrieval |
| **Code QA** ("Fix this bug") | EXCELLENT — SWE-Bench 62.4% | Logic + pattern matching, not facts |
| **Agentic QA** ("Search for X, then do Y") | EXCELLENT — Tau-Bench 67.8% | Tool use grounds answers in external data |
| **Open-book QA** (with retrieval) | GOOD — grounded by context | Retrieved context bypasses the routing problem |

**Key insight:** The 78.2% hallucination rate is measured on **SimpleQA** — a benchmark specifically testing closed-book factual recall ("Who directed [movie]?", "What is the capital of [country]?"). This is the WORST case for MoE sparse models. On reasoning-heavy QA, GPT-OSS-120B is among the best models available.

## Mitigations

| Strategy | How It Helps | Trade-off |
|----------|-------------|-----------|
| **Route factual QA to Qwen3-32B** | 32B active params = 6x more factual recall | Requires routing classifier |
| **Add retrieval (RAG)** | External knowledge grounds answers regardless of active params | Added latency + infra |
| **Use "high" reasoning mode** | Longer CoT can self-check factual claims | 2-10x more tokens generated |
| **Ensemble verification** | Generate from both models; flag disagreements | 2x compute cost |
| **Fine-tune with factual LoRA** | May improve expert routing for factual tokens | Uncertain effectiveness for MoE |

## The 78% Number in Context

| Model | SimpleQA Accuracy | Hallucination Rate | Architecture | Active Params |
|-------|------------------|-------------------|--------------|---------------|
| GPT-OSS-120B | 16.8% | 78.2% | MoE (5.1B active) | 5.1B |
| Qwen3-32B | Not published | Lower (estimated) | Dense (32B active) | 32B |

The correlation is clear: **more active parameters = less hallucination on factual recall**. This is not a "quality" issue — it's a fundamental architectural trade-off. GPT-OSS-120B traded factual breadth per token for depth of reasoning via specialist experts.

## Summary Decision

```
Is your QnA task primarily about FACTUAL RECALL?
  YES → Use Qwen3-32B (or GPT-OSS + RAG)
  NO ↓

Is your QnA task primarily about REASONING/LOGIC/MATH?
  YES → Use GPT-OSS-120B (even at "medium" reasoning, it excels)
  NO ↓

Is your QnA task grounded in provided context (documents, search results)?
  YES → Either model works (both good at reading comprehension)
  NO → Default to Qwen3-32B for lower hallucination risk
```

## Related

- [[Qwen3-32B vs GPT-OSS-120B Strengths and Weaknesses]]
- [[When to Use MoE (GPT-OSS-120B) vs Dense (Qwen3-32B)]]
- [[GPT-OSS-120B MXFP4 vs BF16]]
- [[Reverse Distillation: Qwen3-32B → GPT-OSS-120B Feasibility]]
