---
title: "Numerical Representation"
source: "data/researcher/seeds/numerical-representation.md"
ingestedAt: "2026-05-26T13:54:50Z"
---
Training modern GenAI and LLM systems is now fundamentally a numerical representation problem as much as it is a modeling problem.

The industry has moved from:

FP32 everywhere
→ FP16 mixed precision
→ BF16 dominance
→ FP8 training
→ experimental FP4 / MXFP4 / NVFP4 pipelines.

This transition is driven by one thing: compute and memory efficiency at scale.

For trillion-token LLM training, the datatype determines:

GPU memory footprint
training throughput
interconnect bandwidth
stability
scaling efficiency
energy cost
convergence quality

Below is the practical landscape.

1. Core Number Representation Families
A. Full Precision Floating Point
FP32 (IEEE float32)
Property	Value
Bits	32
Exponent	8
Mantissa	23
Dynamic range	Very high
Precision	High
When used
Optimizer master weights
Critical reductions
Debugging
Numerically sensitive kernels
Pros
Very stable
Minimal underflow/overflow
Easy convergence
Cons
Extremely expensive
2× memory vs FP16/BF16
Slow tensor-core utilization
Today

Pure FP32 training for frontier LLMs is basically obsolete due to cost.

2. Half Precision Era
FP16 (IEEE float16)
Property	Value
Bits	16
Exponent	5
Mantissa	10

FP16 was the first major mixed-precision breakthrough.

Key idea

Use:

FP16 for forward/backward
FP32 master weights for optimizer updates

This became standard after NVIDIA Apex and AMP.

Why FP16 Was Revolutionary

It enabled:

~2× memory reduction
Tensor Core acceleration
Larger batch sizes
Faster training

This made GPT-scale training economically feasible.

FP16 Problems

Main issue:

Narrow exponent range

FP16 easily:

underflows gradients
overflows activations

This caused:

NaNs
unstable training
divergence
Loss Scaling

FP16 required:

static or dynamic loss scaling

Idea:
Multiply gradients before backward pass:

g
′
=g×S

Then unscale later.

This avoids underflow.

When FP16 Still Makes Sense
Use FP16 when:
Older GPUs (V100/T4)
Inference optimization
TensorRT pipelines
Compatibility constraints
Avoid FP16 when:
Very large transformers
RLHF instability
Long-context training
Sparse MoE routing
3. BF16 (BFloat16) — Current Industry Default
BF16 Structure
Property	Value
Bits	16
Exponent	8
Mantissa	7

Key insight:
BF16 keeps FP32’s exponent range.

Why BF16 Dominates LLM Training

Because it solves FP16’s instability problem.

BF16 Advantages
Advantage	Why it matters
Same exponent as FP32	Much more stable
No loss scaling	Simpler pipelines
Better gradient stability	Critical for transformers
Easy migration from FP32	Minimal tuning
BF16 Tradeoff

Less mantissa precision:

noisier arithmetic
slightly less accurate representation

But for deep learning:

dynamic range matters more than mantissa precision.
Current State

BF16 is the default training precision for:

Meta Llama
Google Gemini
Open-source transformer stacks
Most PyTorch large-scale training

Community consensus strongly favors BF16 over FP16 for stability.

4. Mixed Precision Training

This is the real production setup.

Typical BF16 Mixed Precision Pipeline
Component	Precision
Activations	BF16
Weights	BF16
Gradients	BF16
Optimizer states	FP32
Master weights	FP32
Reductions	FP32
Why Mixed Precision Works

Neural networks are surprisingly tolerant to noise.

Most tensors:

do not require FP32 precision
only require stable dynamic range
5. FP8 — The New Frontier

FP8 is now becoming mainstream for frontier LLM training.

Two common variants:

Format	Exponent	Mantissa
E4M3	4	3
E5M2	5	2
Why FP8 Matters

Compared to BF16:

2× lower memory
higher throughput
lower communication cost
better scaling efficiency

This becomes enormous at trillion-parameter scale.

FP8 Challenges

FP8 is much less forgiving.

Problems:

quantization noise
outliers
unstable gradients
attention sensitivity
optimizer instability
How FP8 Training Actually Works

Modern FP8 systems use:

per-channel scaling
tensor-wise scaling
delayed scaling
selective FP16/BF16 fallback
stochastic rounding
Real-World Example: DeepSeek-V3

DeepSeek pioneered production-scale FP8 mixed precision training for a 671B MoE model. Their report states they validated FP8 training feasibility at extreme scale.

Key innovations included:

FP8 mixed precision
hardware/software co-design
communication overlap
stable large-scale MoE optimization

This was a major moment in LLM systems engineering.

6. INT Quantization Family

These are mostly inference-oriented.

INT8

Common for:

inference
quantized serving
edge deployment
Pros
very efficient
mature kernels
Cons
difficult for full training
accuracy degradation
INT4 / INT2

Used heavily in:

inference quantization
mobile deployment
memory-constrained serving

Examples:

GPTQ
AWQ
QLoRA
GGUF ecosystems
7. QLoRA and 4-bit Fine-Tuning

One of the most important breakthroughs.

Paper:

QLoRA

Core idea:

freeze 4-bit quantized base model
train small LoRA adapters in higher precision

This enabled:

fine-tuning 65B models on consumer GPUs.
QLoRA Precision Stack
Component	Precision
Base weights	NF4
LoRA adapters	BF16
Optimizer	FP32
NF4 (NormalFloat4)

Specialized 4-bit format optimized for Gaussian-distributed weights.

Better than naive INT4.

Why QLoRA Worked

Because pretrained weights have:

predictable distributions
redundancy
low intrinsic update rank
8. FP4 / MXFP4 / NVFP4

This is the newest generation.

MXFP4 (Microscaling FP4)

Uses:

shared scaling factors
block-level scaling
tiny 4-bit floats

Goal:
Make training/inference feasible at ultra-low precision.

Why Microscaling Exists

Pure FP4 is too unstable.

Microscaling introduces:

local scaling
adaptive normalization
reduced quantization error
NVIDIA NVFP4

NVIDIA introduced NVFP4 for Blackwell GPUs. It uses:

4-bit floating point
hierarchical scaling
smaller microblocks
improved accuracy retention.

NVIDIA reports:

3.5× memory reduction vs FP16
<1% degradation for some LLM tasks.
Research Frontier: Training in FP4

Recent papers now explore actual FP4 training.

Example:
Training LLMs with MXFP4

Key result:
Near-lossless GPT training using MXFP4 with:

stochastic rounding
Hadamard transforms
variance stabilization.

This is important because:
FP4 training was previously considered impractical.

9. Emerging Direction: Adaptive Precision

New research direction:
dynamic precision selection.

Instead of one datatype globally:

easy tensors → FP4/FP8
sensitive tensors → BF16

Example:

MoR: Mixture Of Representations For Mixed-Precision Training

This dynamically selects FP8 vs BF16 based on tensor properties.

This is likely where the industry is heading.

10. Precision Strategy by Training Stage
Pretraining
Recommended today
Scale	Recommended
Small (<7B)	BF16
Mid (7B–70B)	BF16 or FP8
Frontier (>100B)	FP8 mixed precision
Fine-Tuning
Recommended
Scenario	Precision
Full finetuning	BF16
PEFT / LoRA	BF16
Consumer GPU QLoRA	NF4 + BF16
RLHF	BF16 strongly preferred

RLHF is numerically unstable.
Avoid aggressive low precision there.

Inference
Constraint	Best choice
Highest quality	BF16
High throughput	FP8
Low memory	INT4/NF4
Edge/mobile	INT4/INT2
11. Best Practices
A. Use BF16 by Default

Unless:

hardware lacks support
you explicitly optimize for FP8

BF16 is currently the safest large-scale default.

B. Keep Optimizer States in FP32

Critical for:

Adam moments
stability
convergence
C. Use Selective Precision

Do NOT quantize everything equally.

Sensitive components:

embeddings
attention logits
normalization layers
router logits (MoE)

often need higher precision.

D. Watch Outliers

Outliers destroy low-precision stability.

Common fixes:

clipping
scaling
normalization
SmoothQuant-style transformations
E. Use Stochastic Rounding

Important for:

FP8
FP4
MXFP4

Reduces bias accumulation.

F. Validate Long-Horizon Stability

Low precision can:

look stable early
collapse late in training

Always test:

long training runs
loss spike behavior
downstream eval drift
12. Real-World LLM Examples
Model/System	Precision Strategy
GPT-3 era	FP16 mixed precision
PaLM	BF16 on TPUs
Llama family	BF16
DeepSeek-V3	FP8 mixed precision
QLoRA finetuning	NF4 + BF16
TensorRT-LLM	FP8/NVFP4 inference
Blackwell systems	NVFP4 optimized
13. Key Industry Trend

The trend is clear:

FP32→BF16→FP8→FP4

But importantly:

The future is probably heterogeneous precision, not a single datatype.

Different tensors, layers, and phases will use:

different numerical formats
dynamically selected during training.
14. Important Papers and Resources
Foundational
Mixed Precision Training
QLoRA
LLM.int8()
FP8 / Low Precision
FP8 Formats for Deep Learning
DeepSeek-V3 Technical Report
Training LLMs with MXFP4
MicroMix
MoR: Mixture Of Representations
Practical Recommendation

If you are building GenAI systems today:

Use Case	Recommendation
Stable LLM training	BF16
Frontier-scale efficiency	FP8
Consumer GPU finetuning	QLoRA (NF4)
Production inference	FP8 or INT4
Experimental cutting-edge research	MXFP4/NVFP4

The most important lesson:
Lower precision is not merely compression anymore — it is now a core systems-design dimension for scaling intelligence itself.