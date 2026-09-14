---
title: "For GPT-OSS-120B, does MXFP4 significantly degrade performance vs BF16? Does vLLM support both?"
summary: "No significant degradation — GPT-OSS-120B's published benchmarks (AIME 95.8%, MMLU 90.0%, Codeforces 2463 Elo) were measured AT MXFP4 precision. MXFP4 is the intended release format, not a post-hoc compression. MoE expert weights tolerate 4-bit well because each expert specializes on narrow distributions. vLLM supports both: MXFP4 on 1× H100 (80GB), BF16 would need 3× H100s (~234GB)."
type: "query"
createdAt: "2026-06-06T00:00:00Z"
---
## Short Answer

**No degradation to measure** — MXFP4 IS the release format. All published GPT-OSS-120B benchmarks reflect MXFP4 performance. There is no public BF16 checkpoint to compare against.

**vLLM supports both**, but MXFP4 is the practical deployment path (1× H100). BF16 requires 3× H100s minimum.

## Why MXFP4 Works Well for GPT-OSS-120B

| Factor | Why MoE Tolerates MXFP4 |
|--------|------------------------|
| Expert specialization | Each of 128 experts handles a narrow domain → weights have lower dynamic range per expert |
| Ensemble dilution | Top-4 routing means any single expert's quantization error is diluted across 4 contributors |
| Microscaling blocks | Shared scaling factors within small blocks (16-32 elements) preserve local precision |
| OpenAI's design choice | Model was explicitly designed for MXFP4 — architecture and training account for this precision |

## Memory Requirements

| Format | VRAM Required | GPUs Needed | Practical? |
|--------|-------------|-------------|-----------|
| **MXFP4** (4.25 bits) | ~62GB | **1× H100 (80GB)** | YES — intended deployment |
| BF16 (16 bits) | ~234GB | 3× H100 (240GB) | Possible but defeats purpose |
| FP32 (32 bits) | ~468GB | 6× H100 | Impractical |

## vLLM Support

- **MXFP4**: Supported. OpenAI provides explicit vLLM deployment documentation at `developers.openai.com/cookbook/articles/gpt-oss/run-vllm` ^[[GPT-OSS-120B]]
- **BF16**: Supported by vLLM generically, but no specific GPT-OSS BF16 checkpoint is publicly distributed
- **Recommendation**: Use MXFP4. The benchmarks were measured at this precision — running BF16 would use 3× the hardware for marginal (if any) quality gain

## Benchmarks ARE at MXFP4

These numbers reflect MXFP4, not some "degraded" version:

| Benchmark | GPT-OSS-120B (MXFP4) |
|-----------|----------------------|
| AIME 2024 | 95.8% |
| MMLU | 90.0% |
| GPQA Diamond | 80.1% |
| Codeforces Elo | 2463 |
| SWE-Bench Verified | 62.4% |

## When You Might Want BF16 Anyway

- **Fine-tuning**: LoRA adapters typically train in BF16/FP16 even if base weights are MXFP4
- **Research**: Measuring quantization impact on novel tasks not in the benchmark suite
- **Extreme precision tasks**: If you detect quality issues on your specific workload (unlikely given benchmarks)

## Contrast with Dense Model Quantization

For dense models like Qwen3-32B, 4-bit quantization (AWQ/GPTQ) typically shows <1% quality loss on aggregate benchmarks but can show 3-5% degradation on tail distributions. GPT-OSS-120B's MoE architecture is MORE tolerant of quantization than dense models because:
1. Each expert only handles a subset of the token distribution
2. Routing ensures the most relevant expert activates — even if slightly degraded, it's still the best match
3. The ensemble of 4 experts per token provides error correction

## Related

- [[Microscaling FP4 (MXFP4)]] — The format's technical details
- [[GPT-OSS-120B]] — Model architecture
- [[Qwen3-32B vs GPT-OSS-120B Strengths and Weaknesses]]
