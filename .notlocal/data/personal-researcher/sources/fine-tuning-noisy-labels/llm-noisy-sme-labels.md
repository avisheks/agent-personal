---
title: "Llm Noisy Sme Labels"
source: "data/researcher/seeds/llm_noisy_sme_labels.md"
ingestedAt: "2026-05-20T02:51:44Z"
---
# LLM Fine-Tuning with Noisy SME Labels

## Key takeaway (short answer)
Yes—**you should use SME labels**, but only as **noisy supervision**, not ground truth.

Modern LLM fine-tuning systems (OpenAI / Google / Anthropic-style pipelines) consistently show:

> Raw SME labels degrade performance if used directly; they must be filtered, reweighted, or corrected before training. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/35254993/?utm_source=chatgpt.com))

---

# 1) Should we use SME data?
### Yes — but treat it as weak supervision

SME labels are still valuable because they provide:
- domain expertise
- task-specific judgment (ads relevance, ranking, safety)
- coverage of rare edge cases

However, real-world annotation is inherently noisy, and label noise significantly reduces generalization in deep models. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/35254993/?utm_source=chatgpt.com))

Even in modern LLM pipelines, human labels are explicitly treated as **imperfect preference signals rather than truth** (e.g., RLHF, reward modeling systems).

---

# 2) Do we need post-processing?
### Yes — this is now standard practice in all SOTA pipelines

Across 2023–2025 research, there are four dominant post-processing strategies:

---

## (A) Filtering / reweighting (must-have baseline)

### What you do
- drop high-loss or inconsistent SME samples
- downweight uncertain labels during training

### Why it works
Neural models overfit noisy labels if trained directly; filtering improves generalization stability. ([ijcai.org](https://www.ijcai.org/proceedings/2024/403?utm_source=chatgpt.com))

### Evidence
Recent fine-tuning studies show explicit noise-robust filtering significantly improves performance on corrupted datasets. ([ijcai.org](https://www.ijcai.org/proceedings/2024/403?utm_source=chatgpt.com))

---

## (B) Label correction using LLMs (modern SOTA)

### What you do
- use a strong LLM as a critic/judge
- compare SME label vs model reasoning
- rewrite or correct labels when inconsistent

### Why it works
SME noise is often semantic (interpretation mismatch), not random

### Evidence
LLM-guided fine-tuning methods explicitly improve robustness by using external LLMs to detect and correct noisy labels during training. ([arxiv.org](https://arxiv.org/abs/2311.01108?utm_source=chatgpt.com))

---

## (C) Weak supervision / aggregation (multi-SME setting)

### What you do
- treat each SME as a noisy annotator
- infer latent true labels via agreement modeling

### Why it works
Aggregating multiple noisy sources reduces variance and individual bias.

### Evidence
Surveys on noisy label learning confirm sample selection + label aggregation are core methods for robust training under label corruption. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/35254993/?utm_source=chatgpt.com))

---

## (D) Rubric-based scoring (frontier lab practice)

### What you do
- replace single label with structured rubric dimensions:
  - correctness
  - relevance
  - completeness
- use SME or LLM to score each dimension

### Why it works
It reduces ambiguity and converts subjective labels into decomposable signals.

### Evidence
Modern noise-aware fine-tuning methods explicitly incorporate structured scoring / contrastive / adversarial strategies to improve robustness in real-world noisy settings. ([researchgate.net](https://www.researchgate.net/publication/400449821_Noise-Aware_Fine-Tuning_of_LLMs_for_Robust_Text_Classification?utm_source=chatgpt.com))

---

# 3) Practical decision rule

## If you only remember one thing:

> Never fine-tune directly on SME labels without noise handling.

---

## Choose post-processing based on your setting:

| Situation | What to do |
|----------|------------|
| Single SME per sample | LLM critique + filtering |
| Multiple SMEs | Aggregation + disagreement modeling |
| Subjective tasks (ranking, relevance) | Rubric + LLM judge |
| Small dataset | filtering + synthetic augmentation |
| Large dataset | hybrid (filter + LLM relabel + weighting) |

---

# 4) One-line mental model

> SME labels are not training targets—they are noisy observations of an underlying preference function, and modern LLM training pipelines explicitly denoise them before learning. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/35254993/?utm_source=chatgpt.com))

---

# 5) Strong supporting consensus from literature

Across surveys and ACL/IJCAI work:

- Label noise systematically hurts generalization in deep networks ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/35254993/?utm_source=chatgpt.com))
- Sample selection + label correction are dominant strategies ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S2405959524001103?utm_source=chatgpt.com))
- LLM-assisted denoising improves robustness in real-world fine-tuning settings ([arxiv.org](https://arxiv.org/abs/2311.01108?utm_source=chatgpt.com))
- Fine-tuning methods explicitly designed for noisy labels outperform naïve SFT on corrupted datasets ([ijcai.org](https://www.ijcai.org/proceedings/2024/403?utm_source=chatgpt.com))

---

# Bottom line

- Yes use SME labels
- But only after:
  - filtering
  - reweighting
  - or LLM-based correction
- Best modern systems combine all three
