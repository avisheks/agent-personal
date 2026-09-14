---
title: "DPO supported infra -- veRL vs NeMo-RL? When to use what?"
summary: "veRL does NOT support offline DPO — it's an online RL framework (PPO/GRPO/DAPO). NeMo-RL DOES support DPO (with LoRA) alongside GRPO. For pure DPO: use TRL (easiest, 75+ variants) or NeMo-RL (Megatron scale). For GRPO/online RL: veRL (more flexible, multi-hardware) or NeMo-RL (faster on NVIDIA, 6D parallelism). For PPO: only veRL or OpenRLHF (NeMo-RL dropped it)."
type: "query"
createdAt: "2026-06-08T00:00:00Z"
---
## Critical Clarification: veRL Does NOT Do DPO

**veRL is an online RL framework.** It supports PPO, GRPO, DAPO, REINFORCE++, RLOO, etc. — all on-policy methods that generate samples and optimize against rewards. It does NOT natively support offline DPO/KTO/SimPO.

**NeMo-RL DOES support DPO** (with LoRA), alongside GRPO, DAPO, GDPO.

If your primary need is DPO specifically:

| Framework | DPO Support | Scale | Ease |
|-----------|-------------|-------|------|
| **TRL** (HuggingFace) | **75+ variants** (DPO, KTO, ORPO, SimPO, CPO...) | 1-8 GPUs | Easiest (pip install) |
| **NeMo-RL** | Yes (with LoRA, Megatron backend) | 8-512 GPUs | Medium-High |
| **LLaMA-Factory** | Yes (with Web UI) | 1-8 GPUs | Very easy |
| **Axolotl** | Yes (single YAML config) | 1-multi-node | Easy |
| **veRL** | **NO** | — | — |
| **OpenRLHF** | Yes (DPO/IPO/cDPO) | 1-multi-node | Medium |

## veRL vs NeMo-RL: When to Use Each

### Use veRL When:

- You need **GRPO, PPO, or DAPO** (online RL with generation + reward)
- You want **algorithm flexibility** — easy to add custom algorithms (modular API)
- You're on **non-NVIDIA hardware** (AMD MI300X, Ascend NPUs)
- You want **multiple rollout backends** (vLLM, SGLang, TRT-LLM)
- You're a **research team** building novel RL algorithms
- Your scale is **8-64 GPUs** with Ray cluster
- **Budget**: Open-source, community-supported

### Use NeMo-RL When:

- You need **DPO + GRPO in one framework** (NeMo-RL supports both)
- You're on **NVIDIA hardware** (H100, GB200) and want maximum performance
- Your model is **200B+** (Megatron Core 6D parallelism is unmatched)
- You want **FP8 end-to-end** (training + generation in FP8)
- You need **Megatron-native inference** (no weight conversion overhead)
- You want **enterprise support path** (NVIDIA backing)
- Your scale is **32-512 GPUs**
- **Budget**: Open-source, NVIDIA ecosystem

### Use Neither — Use TRL When:

- You **ONLY need DPO** (offline preference optimization)
- Your model fits in **1-8 GPUs** (7B-13B full, or 70B LoRA)
- You want the **simplest possible setup** (`pip install trl`)
- You want to **experiment with many DPO variants** (75+ methods)
- You're **not doing online RL** (no generation loop needed)

## Detailed Comparison for DPO/GRPO Workloads (8-64 GPUs)

| Criterion | veRL | NeMo-RL | TRL | OpenRLHF |
|-----------|------|---------|-----|----------|
| **DPO** | NO | Yes (LoRA) | **Yes (75+ variants)** | Yes |
| **GRPO** | Yes | Yes | Yes (vLLM backend) | Yes |
| **PPO** | Yes | NO | Experimental | Yes |
| **DAPO** | Yes | Yes | No | Yes |
| **8-GPU setup time** | Hours (Ray cluster) | Hours (uv venv + recipe) | Minutes (pip install) | Hours (Docker) |
| **64-GPU performance** | Strong (FSDP/Megatron) | **Strongest** (Megatron 6D, published benchmarks) | Not designed for this | Good (DeepSpeed ZeRO-3) |
| **Model support** | Any HuggingFace + MoE | Llama/Qwen/Nemotron + MoE | Any HuggingFace | Llama/Qwen/Mistral |
| **Hardware** | NVIDIA + AMD + Ascend | NVIDIA only | Any (CPU offload too) | NVIDIA (primary) |
| **Async training** | Yes (fully async) | Yes | No | Yes |
| **Community** | 21.8k stars, very active | 1.7k stars, NVIDIA-backed | 18.6k stars, HF ecosystem | 9.6k stars, proven at scale |

## Decision Tree

```
Need ONLY offline DPO?
  YES → TRL (simplest, most variants)
       → NeMo-RL if model > 32B and on NVIDIA hardware
  NO ↓

Need online RL (GRPO/PPO/DAPO)?
  ├─ Need PPO specifically? → veRL or OpenRLHF (NeMo-RL dropped PPO)
  ├─ Need GRPO at scale? → veRL (8-64 GPUs) or NeMo-RL (64-512 GPUs)
  └─ Need both DPO AND GRPO in one pipeline?
       → NeMo-RL (supports both)
       → Or: TRL for DPO → veRL for GRPO (common in practice)

On NVIDIA-only hardware?
  YES → NeMo-RL (Megatron performance advantage)
  NO → veRL (AMD, Ascend support)

Model size?
  < 70B → Any framework works; choose by algorithm
  70-200B → veRL or NeMo-RL
  200B+ → NeMo-RL (Megatron 6D parallelism essential)
```

## Performance Numbers (Verified)

| Benchmark | veRL | NeMo-RL |
|-----------|------|---------|
| Throughput vs baselines | 1.53-20.57x (EuroSys 2025, peer-reviewed) | — |
| DeepSeek V3 671B | Demonstrated, no published tok/s | 12.1-30.2 tok/s/GPU (published) |
| Qwen3-235B | Demonstrated | 37.4-163 tok/s/GPU (published) |
| 70B Megatron vs DTensor | — | Megatron 36-56% faster |
| DAPO on AIME 2024 | 50 points (surpasses DeepSeek-R1-Zero) | — |

**No head-to-head comparison exists** on the same hardware/model/algorithm between veRL and NeMo-RL.

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| "Use veRL for DPO" | veRL doesn't support offline DPO | Use TRL or NeMo-RL |
| "NeMo-RL for PPO" | NeMo-RL intentionally dropped PPO for critic-free methods | Use veRL or OpenRLHF |
| "TRL for 70B online RL" | TRL's generation loop isn't optimized for multi-node | Use veRL/NeMo-RL at this scale |
| "DeepSpeed-Chat in 2026" | Effectively legacy (last update Aug 2023) | Migrate to veRL/OpenRLHF |
| "One framework for everything" | DPO and online RL have different infra needs | TRL for DPO + veRL for GRPO (common pattern) |

## Related

- [[RL Post-Training Frameworks: veRL vs NeMo-RL vs Alternatives]]
- [[SFT vs RL Pros Cons and Industry Cases]]
- [[Distillation vs DPO vs GRPO vs PPO]]
- [[Fine-Tuning Decision Framework]]
