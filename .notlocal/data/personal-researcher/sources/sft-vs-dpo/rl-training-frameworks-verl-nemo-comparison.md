---
title: "RL Post-Training Framework Comparison: veRL vs NeMo-RL and Alternatives"
url: "multiple (GitHub repos, EuroSys 2025, NVIDIA docs, HuggingFace TRL, OpenRLHF)"
ingestedAt: "2026-06-08T00:00:00Z"
type: "article"
---

# RL Post-Training Frameworks: veRL vs NeMo-RL

## veRL (ByteDance/Volcengine)
- GitHub: volcengine/verl, 21,848 stars, Apache 2.0
- Latest: v0.8.0 (June 2026)
- Paper: HybridFlow (EuroSys 2025)
- Algorithms: PPO, GRPO, GSPO, DAPO, DrGRPO, REINFORCE++, RLOO, PRIME, ReMax, SPPO, On-Policy Distillation
- NO native offline DPO/KTO/SimPO — primarily online RL
- Architecture: Hybrid-controller (Ray orchestration + NCCL collectives)
- Backends: FSDP, FSDP2, Megatron-LM, TorchTitan
- Rollout: vLLM, SGLang, TensorRT-LLM
- Hardware: NVIDIA, AMD MI300X/MI325X/MI355X, Ascend NPUs
- Scale: Demonstrated on 671B DeepSeek, Qwen3-235B, 64 H800 GPUs
- Performance: 1.53x to 20.57x vs baselines (EuroSys peer-reviewed)
- Key features: 3D-HybridEngine (zero-redundancy resharding), flexible device mapping, multi-backend, VeOmni (multimodal RL), fully async trainer
- Production: ByteDance internal, 150+ community projects, DAPO achieved 50 on AIME 2024

## NeMo-RL (NVIDIA, formerly NeMo-Aligner)
- GitHub: NVIDIA/NeMo-RL, 1,709 stars, Apache 2.0
- Latest: v0.6.0 (April 2026)
- Algorithms: GRPO, GSPO, DAPO, GDPO, SFT (LoRA), DPO (LoRA), On-Policy Distillation, Reward Modeling
- NO PPO/REINFORCE/RLOO — focuses on critic-free methods
- Architecture: DTensor (FSDP2, TP, SP, PP, CP) and Megatron Core (6D parallelism: TP, PP, SP, CP, EP, FSDP)
- Rollout: vLLM, Megatron-native inference (no weight conversion)
- Hardware: NVIDIA only (H100, GB200)
- Scale: 512 H100 GPUs tested; GB200-NVL72 (256 GPUs)
- Benchmarks: DeepSeek V3 671B at 12.1-30.2 tok/s/GPU; Qwen3-235B at 37.4-163 tok/s/GPU; Megatron 36-56% faster than DTensor at 70B
- Key features: Megatron-native inference (no conversion), FP8 end-to-end, GB200 first-mover, async GRPO, speculative decoding for rollout
- Production: Trained Nemotron-3-Nano/Super/Ultra (NVIDIA flagship models)

## Other Frameworks

### HuggingFace TRL
- 18,577 stars, Apache 2.0, 3M downloads/month
- DPO, GRPO, PPO, RLOO, KTO, ORPO, CPO, SimPO, Online DPO + 75 methods
- Built on Transformers + Accelerate (DDP, DeepSpeed, FSDP)
- Easiest setup (pip install trl)
- Best for: offline DPO, algorithm experimentation, single-node
- Limitation: not optimized for 70B+ online RL

### OpenRLHF
- 9,612 stars, Apache 2.0
- PPO, REINFORCE++, GRPO, RLOO, DAPO, DPO/IPO
- Ray + vLLM + DeepSpeed ZeRO-3
- Used by Google, ByteDance, Tencent, Alibaba, Baidu
- Good middle ground between TRL (simple) and veRL/NeMo-RL (scale)

### LLaMA-Factory
- 72,001 stars, Apache 2.0
- DPO, KTO, ORPO, SimPO, PPO, GRPO
- Web UI (LLaMA Board), zero-code training
- 100+ models supported
- Best for: beginners, quick experiments, single-node

### Axolotl
- 12,024 stars, Apache 2.0
- DPO, IPO, KTO, ORPO, GRPO, GDPO
- FSDP, DeepSpeed, single YAML config
- GPT-OSS, Llama, Mistral, Qwen supported

### DeepSpeed-Chat
- Part of DeepSpeed (36k+ stars)
- PPO only (InstructGPT 3-stage pipeline)
- EFFECTIVELY LEGACY — last major update Aug 2023
- Was 6-19x faster than Colossal-AI; now superseded

## Decision Matrix

By scale:
- 1 GPU: TRL or LLaMA-Factory
- 1-8 GPUs: TRL (DPO), veRL/OpenRLHF (online RL)
- 8-32 GPUs: veRL or OpenRLHF
- 32-64 GPUs: veRL or NeMo-RL
- 64-512 GPUs: NeMo-RL (Megatron) or veRL (Megatron backend)

By algorithm:
- DPO only (offline): TRL, Axolotl, LLaMA-Factory
- GRPO: veRL, NeMo-RL, TRL, OpenRLHF (all good)
- PPO (with critic): veRL, OpenRLHF (NeMo-RL dropped PPO)
- DAPO/state-of-art: veRL, NeMo-RL, OpenRLHF

No head-to-head benchmark exists on same hardware/model/algorithm.
