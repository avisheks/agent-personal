# World Models Weekly Briefing (Week 36)
**Week 36 | August 30–September 5, 2026**
⏱️ 18 min read

---

## 📋 Executive Briefing

World model research hit an inflection point this week with **three convergent waves**: autonomous driving WAMs reached production quality, digital world models arrived for web agents, and the evaluation/safety infrastructure matured to match.

**[ZimaBlue](https://arxiv.org/abs/2609.00188) scaled WAMs to 120,000+ hours of egocentric video**, achieving 36.1% to 77.8% zero-shot real-robot success via a Slow+Fast architecture that separates high-capacity dynamics modeling from real-time 30 Hz control. This extends the Riemann-1.0 pattern from WK35 with a cleaner scaling story.

**Autonomous driving became the dominant WAM application domain** — four papers ([SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [StyleDrive](https://arxiv.org/abs/2609.03225), [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111)) delivered surround-view, hierarchical, and multi-style driving world models in a single week, with SV-WAM achieving SOTA on NAVSIMv2 while maintaining six-camera coverage.

**Digital world models emerged as a distinct subfield** — [Discriminative World Models for Web Agents](https://arxiv.org/abs/2609.02885) introduced predicted-state matching that improves web agent task success, while [WebWorld](https://arxiv.org/abs/2608.30530) proposed using the browser itself as a world model for code verification.

**World model evaluation infrastructure matured significantly** — [VeriPhy](https://arxiv.org/abs/2609.03153) deployed agentic physical reasoning to catch 228/304 physics failures in generated video, [WorldReward](https://arxiv.org/abs/2609.03952) introduced VLM-based reward modeling, and [RIWM](https://arxiv.org/abs/2609.03774) proposed risk-informed world models for safety-critical systems.

---

## ⚡ What Changed Since Last Week

- [ZimaBlue](https://arxiv.org/abs/2609.00188): WAM via scalable video pre-training; 120K+ hours; 36.1% to 77.8% zero-shot robot success; Slow+Fast architecture at 30 Hz
- [WM-LOCO](https://arxiv.org/abs/2609.02542): world-model-augmented humanoid locomotion; 93.3% real-world deployment success on Unitree G1
- [WISE](https://arxiv.org/abs/2609.03681): world-model-guided imagination scheduling for VLA post-training; 80% GPU reduction
- [SV-WAM](https://arxiv.org/abs/2609.03602): surround-view WAM for autonomous driving; SOTA NAVSIMv2; six-camera preservation
- [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885): predicted-state matching objective; WebArena-Lite improvements
- [Puffin-World](https://arxiv.org/abs/2609.04196): unified multimodal model with native 3D world states; 15M triplets; physics+geometry+appearance
- [VeriPhy](https://arxiv.org/abs/2609.03153): agentic physical reasoning for WM evaluation; 228/304 failures detected with full provenance
- [WorldReward](https://arxiv.org/abs/2609.03952): VLM-based reward modeling for camera-conditioned WMs; outperforms GPT-4.5-Vision
- [RIWM](https://arxiv.org/abs/2609.03774): risk-informed world models for safety-critical embodied systems; counterfactual + safety memory
- [SolarWM](https://arxiv.org/abs/2609.02886): open data + scalable training for video WMs; 1.43M clips; 5B-33B models; fully open
- [Drive-HWM](https://arxiv.org/abs/2609.03572): hierarchical slow-fast WMs for autonomous driving; dynamic-aware latents via optical flow
- [Physically Grounded JEPA](https://arxiv.org/abs/2609.03565): JEPA + inverse dynamics + state alignment; 100% TwoRoom, 98% PushT; accepted IROS 2026
- [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910): real-time streaming interactive WMs with patch memory; minute-long generation
- [WebWorld](https://arxiv.org/abs/2608.30530): browser as world model; quality ratchet for web code verification
- [H3-World](https://arxiv.org/abs/2609.01560): language as natural control interface for video world models; 0.199% trainable parameters
- [GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) released on OpenRouter — new frontier model from OpenAI

---

## 🔬 Top Technical Developments

### 1. ZimaBlue — Scaling WAMs Through Video Pre-Training
| Metric | Score |
|--------|-------|
| Strategic Importance | 10 |
| Technical Innovation | 9 |
| Practical Adoption | 9 |
| Business Impact | 9 |

**Source:** [arXiv:2609.00188](https://arxiv.org/abs/2609.00188) | **Confidence:** High | **Reading time:** 25 min | 🚀 Production-ready

Three-stage WAM training pipeline: causal video pre-training on large-scale egocentric footage, mid-training grounding with unified action representation, and specialization for target robots. Employs a high-capacity Slow world model paired with a lightweight Fast branch for real-time 30 Hz control. Scaling from target-robot data alone to 120,000+ hours of embodied video improves zero-shot real-robot success from 36.1% to 77.8%.

> 💡 **Key Insight:** ZimaBlue provides the clearest evidence yet of a scaling law for WAMs — more diverse egocentric video yields monotonically better zero-shot robot performance. The Slow+Fast architecture solves the capacity-vs-latency tradeoff that has limited real-time WAM deployment.

---

### 2. WM-LOCO — Humanoid Locomotion with World Models Achieves 93% Real Deployment
| Metric | Score |
|--------|-------|
| Strategic Importance | 9 |
| Technical Innovation | 8 |
| Practical Adoption | 9 |
| Business Impact | 8 |

**Source:** [arXiv:2609.02542](https://arxiv.org/abs/2609.02542) | **Confidence:** High | **Reading time:** 20 min | 🚀 Production-ready

Jointly trains a recurrent world model and PPO policy processing proprioception and depth imagery for anticipatory foot-placement on stepping stones, gaps, and stairs. Achieves 93.3% deployment success on a physical [Unitree G1](https://arxiv.org/abs/2609.02542) humanoid without requiring explicit foothold labels — the world model learns to predict terrain affordances from raw depth.

> 🚀 **Opportunity:** 93.3% real-world deployment on a commercial humanoid validates world-model-augmented locomotion as production-ready. Unitree G1 is widely available — this is immediately reproducible.

---

### 3. WISE — 80% GPU Reduction for VLA Post-Training via Imagination Scheduling
| Metric | Score |
|--------|-------|
| Strategic Importance | 9 |
| Technical Innovation | 8 |
| Practical Adoption | 9 |
| Business Impact | 9 |

**Source:** [arXiv:2609.03681](https://arxiv.org/abs/2609.03681) | **Confidence:** High | **Reading time:** 20 min | 🧪 Early prototype

Selectively activates world-model imagination at task-critical states during VLA policy refinement rather than imagining everywhere. Constrains rollout horizons to prevent prediction error accumulation. Achieves ~80% reduction in GPU computation versus full imagination while maintaining consistent performance gains across diverse manipulation tasks on both pi-0 and pi-0.5 models. Validated in real-world conditions with distribution shifts.

> 💡 **Key Insight:** Not all states benefit equally from world-model imagination. WISE's selective scheduling is the training analog of test-time compute allocation — spend imagination budget where it matters most.

---

### 4. Discriminative World Models for Web Agents
| Metric | Score |
|--------|-------|
| Strategic Importance | 9 |
| Technical Innovation | 8 |
| Practical Adoption | 8 |
| Business Impact | 9 |

**Source:** [arXiv:2609.02885](https://arxiv.org/abs/2609.02885) | **Confidence:** High | **Reading time:** 20 min | 🧪 Early prototype

Introduces predicted-state matching — the world model must distinguish the true resulting state from those reached by alternative actions, fixing the objective mismatch between generative training and discriminative use. Outperforms supervised next-state prediction on [WebPRMBench](https://arxiv.org/abs/2609.02885) and improves end-to-end task success on [WebArena-Lite](https://arxiv.org/abs/2609.02885) when used for test-time action selection.

> 💡 **Key Insight:** World models for digital agents don't need to generate — they need to discriminate. Predicted-state matching is a fundamentally better training objective for action selection in web/GUI environments.

---

### 5. SV-WAM — Surround-View WAM for Autonomous Driving
| Metric | Score |
|--------|-------|
| Strategic Importance | 9 |
| Technical Innovation | 8 |
| Practical Adoption | 8 |
| Business Impact | 9 |

**Source:** [arXiv:2609.03602](https://arxiv.org/abs/2609.03602) | **Confidence:** High | **Reading time:** 20 min | 🧪 Early prototype

Preserves full six-camera surround-view coverage while maintaining efficient inference via action-centered causal masking that prevents action tokens from attending to future-video tokens. Video generation component can be removed at deployment. Achieves SOTA on [NAVSIMv2](https://arxiv.org/abs/2609.03602) closed-loop benchmark with strong zero-shot transfer across datasets. Includes safety penalty when corners approach drivable boundaries.

> ⚠️ **Risk:** Most driving world models sacrifice spatial coverage for efficiency (front-camera only). SV-WAM shows this tradeoff is unnecessary — deploying coverage-limited driving WMs risks blind spots in safety-critical scenarios.

---

## 🏢 Frontier Lab Scorecards

| Lab | World Model Activity | Research | Strategic Direction |
|-----|---------------------|----------|---------------------|
| **[NVIDIA](https://developer.nvidia.com/blog/)** | [Omniverse NuRec](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec/) for AV perception scaling | AV simulation infrastructure | Post-HuggingFace acquisition integration underway |
| **[OpenAI](https://openrouter.ai/openai/gpt-6-astra)** | [GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) released on OpenRouter; agent message board [discovered](https://collusion.wiki/) | Frontier LLM as implicit world model backbone | New model generation; agent infrastructure expanding |
| **[Anthropic](https://anthropic.com/research/formalizing-fermats-last-theorem)** | [Formalizing Fermat's Last Theorem](https://anthropic.com/research/formalizing-fermats-last-theorem) (663 HN points) | Formal reasoning and proof verification | Mathematical reasoning capabilities as planning foundation |
| **[Qwen (Alibaba)](https://arxiv.org/abs/2609.00111)** | [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111): VLA foundation model for autonomous driving | VLM + driving world models | Expanding from language to embodied driving |
| **[Tencent](https://arxiv.org/abs/2608.29910)** | [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910): real-time streaming interactive WMs with patch memory | Persistent real-time world generation | Continued gaming-native world model investment (WK35: GameWAM) |
| **[ByteDance](https://arxiv.org/abs/2608.30821)** | [Lucida](https://arxiv.org/abs/2608.30821): composable real-to-sim scene modeling | Scene reconstruction for simulation | Sim data generation for world model training |
| **[ACE Robotics](https://arxiv.org/abs/2609.04196)** | [Puffin-World](https://arxiv.org/abs/2609.04196): unified multimodal model with native 3D world states; 15M dataset released | Physics+geometry+appearance unification | Emerging lab with ambitious open-source world model release |
| **Google DeepMind** | No new world model-specific releases this week | — | Sustaining Gemini Robotics ecosystem |
| **Meta FAIR** | No new world model releases (post-LpWM from WK35) | — | Consolidating sparse JEPA representation theory |

**Power Ranking Shift:** OpenAI re-enters the conversation with GPT-6 Astra — while not world-model-specific, each frontier model upgrade strengthens LLM-as-implicit-world-model capabilities. Qwen expands into autonomous driving. ACE Robotics emerges as a new player with Puffin-World's ambitious 15M-sample open release. Tencent ships its second consecutive week of world model research (Matrix-Game 3.5 after GameWAM).

---

## 🌐 Open-Source Ecosystem Tracking

| Project | Category | This Week | Trajectory |
|---------|----------|-----------|------------|
| **[SolarWM](https://arxiv.org/abs/2609.02886)** | Video World Model | NEW: fully open; 1.43M clips; 5B-33B models; training recipes released | 📈 Accelerating |
| **[Puffin-World](https://arxiv.org/abs/2609.04196)** | 3D World Model | NEW: code + models + Puffin-16M dataset (15M triplets) released | 📈 Accelerating |
| **[ZimaBlue](https://arxiv.org/abs/2609.00188)** | World Action Model | NEW: Slow+Fast WAM; 120K+ hours video pre-training | 📈 Accelerating |
| **[Matrix-Game 3.5](https://arxiv.org/abs/2608.29910)** | Interactive World Model | NEW: patch memory; real-time streaming; minute-long generation | 📈 Accelerating |
| **JEPA implementations** | Representation Learning | [Physically Grounded JEPA](https://arxiv.org/abs/2609.03565) accepted at IROS 2026; 7th consecutive week of JEPA variants | 📈 Accelerating |
| **[Riemann-1.0](https://arxiv.org/abs/2608.27033)** | World Action Model | Cited as baseline by multiple WK36 papers; ZimaBlue extends pattern | ➡️ Stable (baseline) |
| **[DreamerV3](https://github.com/danijar/dreamerv3)** | Model-based RL | Referenced by WM-LOCO and LEAP | ➡️ Stable (baseline) |
| **[HuggingFace](https://huggingface.co/)** | Model Hub | Post-NVIDIA acquisition; SolarWM and Puffin-World hosted | ➡️ Stable |

---

## 💰 Business & Market Intelligence

### GPT-6 Astra Released

- **[GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra)** appeared on OpenRouter (258 HN points). Each frontier model upgrade strengthens LLM-as-implicit-world-model capabilities for planning, state tracking, and counterfactual reasoning. Relevant as backbone for hybrid LLM+world model systems.

### Corporate America Embraces Open-Source AI

- **[Corporate America is getting hooked on open-source AI](https://www.nytimes.com/2026/09/04/technology/open-source-ai-anthropic-openai.html)** (305 HN points). Enterprise adoption of open-weight models accelerates. For world models: [SolarWM](https://arxiv.org/abs/2609.02886)'s fully open release (datasets, code, weights, recipes) and [Puffin-World](https://arxiv.org/abs/2609.04196)'s 15M-sample dataset align with this enterprise trend toward open infrastructure.

### NVIDIA Omniverse NuRec for AV Simulation

- **[NVIDIA Omniverse NuRec](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec/)** scales AV perception across vehicle platforms via re-rendering. Complements this week's driving WAM papers (SV-WAM, Drive-HWM, StyleDrive) by providing simulation infrastructure for world model training data generation.

### OpenAI Agent Infrastructure Discovery

- **[OpenAI agent message board discovered](https://collusion.wiki/)** (1,833 HN points — week's top story). Reveals internal agent coordination infrastructure. Relevant to multi-agent world model architectures where agents must share and negotiate world state representations.

---

## 📄 Research Papers

**1. [ZimaBlue: Evolving Generalizable World Action Models through Scalable Video Pre-training](https://arxiv.org/abs/2609.00188)**
- *Authors:* Xionghao Wu, Yijun Yang, Shiyang Zhou et al. (20 authors)
- *TL;DR:* Three-stage WAM training on 120K+ hours of egocentric video. Slow+Fast architecture enables 30 Hz real-time control. Zero-shot success improves from 36.1% to 77.8% with scale.
- *Why it matters:* Clearest WAM scaling law evidence — more diverse video yields monotonically better zero-shot performance. The Slow+Fast split solves the capacity-vs-latency problem.
- *Strengths:* Massive scale; real-time deployment; strong zero-shot. *Limitations:* Training compute requirements at 120K+ hours.
- Strategic: 10 | Innovation: 9 | Adoption: 9 | Business: 9 | 🚀 Production-ready

**2. [WM-LOCO: World-Model-Augmented Visual Locomotion for Humanoids on Foothold-Constrained Terrain](https://arxiv.org/abs/2609.02542)**
- *Authors:* Yuxi Liu, Lijun Han, Ziming Wang, Ao Zhang, Cong Yang, Wei Sui
- *TL;DR:* Recurrent world model + PPO policy for humanoid locomotion on stepping stones, gaps, stairs. 93.3% real-world success on Unitree G1 without explicit foothold labels.
- *Why it matters:* Validates world-model-augmented locomotion as production-ready on commercial hardware. No foothold annotations needed — world model learns terrain affordances from raw depth.
- *Strengths:* 93.3% real deployment; no annotations; commercial hardware. *Limitations:* Tested on structured terrains only.
- Strategic: 9 | Innovation: 8 | Adoption: 9 | Business: 8 | 🚀 Production-ready

**3. [WISE: World-model-guided Imagination Scheduling for Efficient VLA Post-training](https://arxiv.org/abs/2609.03681)**
- *Authors:* Chenhao Zhang, Hanyu Zhao, Hang Cheng, Tengfei Pan, Long Zeng
- *TL;DR:* Selective imagination at task-critical states during VLA refinement. 80% GPU reduction vs. full imagination. Validated on pi-0 and pi-0.5 with real-world distribution shifts.
- *Why it matters:* Makes world-model-guided training economically viable. The selective scheduling principle applies broadly to any imagination-augmented training loop.
- *Strengths:* 80% compute savings; architecture-agnostic; real-world validated. *Limitations:* Requires identifying task-critical states.
- Strategic: 9 | Innovation: 8 | Adoption: 9 | Business: 9 | 🧪 Early prototype

**4. [Discriminative World Models for Web Agents](https://arxiv.org/abs/2609.02885)**
- *Authors:* Kelvin Li, Dhruv Pendharkar, Anish Pahilajani, Chuyi Shang, Leon Oks, Leonid Karlinsky, Rogerio Feris, Trevor Darrell, Roei Herzig
- *TL;DR:* Predicted-state matching objective replaces generative next-state prediction. Improves action ranking on [WebPRMBench](https://arxiv.org/abs/2609.02885) and task success on [WebArena-Lite](https://arxiv.org/abs/2609.02885).
- *Why it matters:* World models for digital agents should discriminate, not generate. This reframes the training objective for all non-physical world model applications.
- *Strengths:* Novel objective; strong WebArena results; principled fix. *Limitations:* Tested on web domain only; transfer to other digital domains unclear.
- Strategic: 9 | Innovation: 8 | Adoption: 8 | Business: 9 | 🧪 Early prototype

**5. [SV-WAM: Surround-View World-Action Model for End-to-End Autonomous Driving](https://arxiv.org/abs/2609.03602)**
- *Authors:* Jinyang Wang, Shiwei Li, Junjian Wang et al. (15 authors)
- *TL;DR:* Six-camera surround-view WAM with action-centered causal masking. SOTA on NAVSIMv2 closed-loop. Video branch removable at deployment for efficiency. Safety penalty at drivable boundaries.
- *Why it matters:* Proves WAMs can maintain full spatial coverage without sacrificing efficiency. Front-camera-only driving WMs are now insufficient.
- *Strengths:* Full coverage; SOTA; deployment-friendly. *Limitations:* Requires surround-view training data.
- Strategic: 9 | Innovation: 8 | Adoption: 8 | Business: 9 | 🧪 Early prototype

**6. [Puffin-World: Scaling a Unified Multimodal Model with Native 3D World States](https://arxiv.org/abs/2609.04196)**
- *Authors:* Kang Liao, Yihang Luo, Xiao-Ming Wu et al. (10 authors)
- *TL;DR:* Integrates physics, geometry, and appearance as native 3D world states without external modules. Puffin-16M dataset: 15M vision-language-camera triplets. Code, models, data released.
- *Why it matters:* First unified architecture coupling all three world state dimensions. The 15M open dataset is a major community resource.
- *Strengths:* Comprehensive world state modeling; massive open dataset. *Limitations:* Evaluation of cross-modal coherence still developing.
- Strategic: 9 | Innovation: 8 | Adoption: 8 | Business: 7 | 🧪 Early prototype

**7. [VeriPhy: Agentic Physical Reasoning for World Model Evaluation and Refinement](https://arxiv.org/abs/2609.03153)**
- *Authors:* Wenzhuo Xu, Yuchen Zhu, Chongjian Ge et al. (11 authors)
- *TL;DR:* Text-only planner compiles typed physical obligations before frame observation. Low-level experts generate evidence with full provenance. Three-valued resolver (plausible/implausible/abstain). Detected 228/304 physics failures.
- *Why it matters:* First auditable, traceable WM evaluation system. Every verdict links to supporting evidence — essential for safety-critical deployment.
- *Strengths:* Auditable provenance; 228/304 detection; modular. *Limitations:* Expert modules add pipeline complexity.
- Strategic: 9 | Innovation: 8 | Adoption: 7 | Business: 8 | 🧪 Early prototype

**8. [WorldReward: Reward Modeling for Camera-Conditioned World Models](https://arxiv.org/abs/2609.03952)**
- *Authors:* Yibin Wang, Zehan Wang, Junshu Tang et al. (16 authors)
- *TL;DR:* VLM-based preference rewards evaluating action consistency (+3.42pp over GPT-4.5-Vision), appearance quality (+1.45pp), and motion quality (+3.56pp). WorldReward-Bench released.
- *Why it matters:* Bridges the gap between trajectory-based and visual-quality rewards. Enables RL post-training that improves both action execution and visual fidelity simultaneously.
- *Strengths:* Outperforms GPT-4.5-Vision; multi-dimensional evaluation. *Limitations:* Requires VLM inference overhead.
- Strategic: 8 | Innovation: 8 | Adoption: 7 | Business: 8 | 🧪 Early prototype

**9. [RIWM: Rethinking World Models for Safety-Critical Embodied Systems](https://arxiv.org/abs/2609.03774)**
- *Authors:* Kailang Ma, Heye Huang, Inhi Kim, Kitae Jang
- *TL;DR:* Identifies three structural mismatches (likelihood vs. risk, prediction vs. intervention, finite-horizon vs. accumulated consequences). Proposes Risk-Informed World Model with counterfactual reasoning and safety memory.
- *Why it matters:* The first principled framework shifting world model objectives from "predict accurately" to "identify which futures matter for safety." Required reading before deploying WMs in safety-critical applications.
- *Strengths:* Principled framework; addresses fundamental gaps. *Limitations:* Perspective paper — no implementation yet.
- Strategic: 8 | Innovation: 7 | Adoption: 6 | Business: 8 | 🔬 Research-only

**10. [SolarWM: Open Data and Scalable Training for Long-Horizon Video World Models](https://arxiv.org/abs/2609.02886)**
- *Authors:* Junchao Huang, Guian Fang, Shengju Qian et al. (18 authors)
- *TL;DR:* Fully open video WM framework: 1.43M clips from 10 datasets in unified format. 5B-33B parameter models across 3 architectures. Three-stage training (bidirectional adaptation, teacher-forced init, distribution matching). Trains on 5-second clips, generates minutes to hours.
- *Why it matters:* Democratizes long-horizon video world model training. The fully open stack (data, code, recipes, weights) is the most complete open WM training resource to date.
- *Strengths:* Fully open; 4 model sizes; 3 architectures. *Limitations:* Long-horizon quality at hour-scale still limited.
- Strategic: 8 | Innovation: 7 | Adoption: 9 | Business: 7 | 🧪 Early prototype

### Noteworthy

| Paper | Key Contribution | Signal |
|-------|-----------------|--------|
| [Drive-HWM](https://arxiv.org/abs/2609.03572) | Hierarchical slow-fast WMs for driving; dynamic-aware latents via optical flow | 🧪 |
| [Physically Grounded JEPA](https://arxiv.org/abs/2609.03565) | JEPA + inverse dynamics + state alignment; 100% TwoRoom, 98% PushT; IROS 2026 | 🧪 |
| [GIFT](https://arxiv.org/abs/2609.04193) | Action-oriented structural supervision; +12.6pp on LIBERO-Plus; +12.6pp on RoboCasa | 🧪 |
| [StyleDrive](https://arxiv.org/abs/2609.03225) | Long-horizon consistent WMs; multi-style driving policies; interaction disentanglement | 🧪 |
| [H3-World](https://arxiv.org/abs/2609.01560) | Language as natural WM control interface; 0.199% trainable params; MiniMax-H3 adapted | 🧪 |
| [WebWorld](https://arxiv.org/abs/2608.30530) | Browser as WM; quality ratchet for web code; +14.9pp on MiniAppBench | 🧪 |
| [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910) | Patch memory + progressive distillation; minute-long real-time interactive generation | 🧪 |
| [LEAP](https://arxiv.org/abs/2609.03294) | Latent energy action planning; differentiable action horizons; terminal energy minimization | 🔬 |
| [Statebench](https://arxiv.org/abs/2609.03673) | Video continuation state tracking benchmark; Stateagent with entity-state representations | 🔬 |
| [Unreal Engine WM Pipeline](https://arxiv.org/abs/2609.03557) | 8,767 hours synthetic action-conditioned video via two-stage UE pipeline | 🧪 |
| [Semantic Bayesian WMs](https://arxiv.org/abs/2609.03834) | Knowledge graphs + Bayesian conditioning; ontological axioms constrain priors | 🔬 |
| [GPU Astrodynamics WMs](https://arxiv.org/abs/2609.03067) | World models for spacecraft rendezvous; flow matching for orbital dynamics | 🔬 |
| [Principia](https://arxiv.org/abs/2609.04200) | Relational physics tests for video models; physics understanding evaluation | 🔬 |

---

## 🧬 Research Blogs

**1. [WISE: Imagination Scheduling Changes the VLA Training Economics](https://arxiv.org/abs/2609.03681)**
- Framework demonstrating that selective world-model imagination during VLA post-training achieves comparable performance at 80% lower GPU cost. Applies to both [pi-0](https://arxiv.org/abs/2609.03681) and [pi-0.5](https://arxiv.org/abs/2609.03681) models. The scheduling principle — spend imagination where it matters — is broadly applicable.
- Strategic: 9 | Innovation: 8 | 🧪 Early prototype

**2. [Rethinking World Models for Safety-Critical Systems](https://arxiv.org/abs/2609.03774)**
- Perspective article reframing WM objectives from predictive accuracy to consequence-awareness. The three structural mismatches (likelihood vs. risk, prediction vs. intervention, finite-horizon vs. consequences) provide a rigorous vocabulary for the emerging WM safety debate.
- Strategic: 8 | Innovation: 7 | 🔬 Research-only

**3. [Unified Robot Learning Survey: Representation + VLA + World Models](https://arxiv.org/abs/2609.03927)**
- Comprehensive survey organizing the robot learning landscape across three axes. Identifies uncertainty quantification and long-horizon planning as key integration challenges. Essential map for teams positioning world models within the broader robot learning stack.
- Strategic: 8 | Innovation: 5 | 🔬 Research-only

**4. [VeriPhy: Auditable World Model Evaluation](https://arxiv.org/abs/2609.03153)**
- Agentic physical reasoning system providing traceable verdicts on generated video physics. The text-only planning + low-level expert architecture creates auditable chains linking every verdict to evidence. 228/304 failure detection rate sets a new bar.
- Strategic: 9 | Innovation: 8 | 🧪 Early prototype

**5. [Discriminative vs. Generative World Models for Web Agents](https://arxiv.org/abs/2609.02885)**
- Theoretical and empirical argument that web agent world models should be trained with discriminative (state-matching) rather than generative objectives. The predicted-state matching objective is a paradigm shift for digital world model applications.
- Strategic: 9 | Innovation: 8 | 🧪 Early prototype

**6. [SolarWM: The Most Open Video World Model Stack](https://arxiv.org/abs/2609.02886)**
- Fully open release covering datasets (1.43M clips), pipeline code, training recipes, and model weights from 5B to 33B parameters. Three-stage training methodology achieves long-horizon generation (minutes to hours) from 5-second training clips.
- Strategic: 8 | Innovation: 7 | 🧪 Early prototype

**7. [WorldReward: VLM-Based Reward Modeling for World Models](https://arxiv.org/abs/2609.03952)**
- Introduces structured pairwise comparison via VLMs for evaluating world model outputs. Action-aligned chunking + visual evidence aggregation outperforms GPT-4.5-Vision on action consistency, appearance quality, and motion quality. [WorldReward-Bench](https://arxiv.org/abs/2609.03952) released.
- Strategic: 8 | Innovation: 8 | 🧪 Early prototype

**8. [Anthropic: Formalizing Fermat's Last Theorem](https://anthropic.com/research/formalizing-fermats-last-theorem)**
- While not world-model-specific, Anthropic's formal mathematical reasoning achievement (663 HN points) demonstrates the planning and proof-search capabilities that underpin world-model-based reasoning in abstract spaces.
- Strategic: 7 | Innovation: 7 | 🔬 Research-only

**9. [Semantic Bayesian World Models](https://arxiv.org/abs/2609.03834)**
- Proposes integrating knowledge graphs with probabilistic reasoning for world models where ontological axioms constrain priors and observations update beliefs via Bayesian conditioning. A theoretical bridge between symbolic AI and learned dynamics.
- Strategic: 7 | Innovation: 7 | 🔬 Research-only

**10. [NVIDIA Omniverse NuRec for AV Perception Scaling](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec/)**
- NVIDIA ships infrastructure for re-rendering AV perception data across vehicle platforms. Complements this week's driving WAM papers by providing the simulation backbone for training data generation.
- Strategic: 7 | Innovation: 6 | 🚀 Production-ready

---

## 🛠️ Engineering Blogs

| # | Post | Source | Signal | Key Insight |
|---|------|--------|--------|-------------|
| 1 | [SolarWM: Open Data and Scalable Training](https://arxiv.org/abs/2609.02886) | CUHK-Shenzhen | 🧪 | Fully open 5B-33B video WMs; 1.43M clips; 3-stage training from 5s to hours |
| 2 | [SV-WAM: Surround-View Driving WAM](https://arxiv.org/abs/2609.03602) | SV-WAM Team | 🧪 | Six-camera WAM; SOTA NAVSIMv2; action-centered causal masking |
| 3 | [Puffin-World: Native 3D World States](https://arxiv.org/abs/2609.04196) | ACE Robotics | 🧪 | Physics+geometry+appearance unified; Puffin-16M dataset released |
| 4 | [GIFT: Action-Oriented Feature Training](https://arxiv.org/abs/2609.04193) | GIFT Team | 🧪 | Bridging VLMs and WAMs; +12.6pp LIBERO-Plus; +12.6pp RoboCasa |
| 5 | [Matrix-Game 3.5: Streaming Interactive WMs](https://arxiv.org/abs/2608.29910) | Tencent | 🧪 | Patch memory + progressive distillation; minute-long real-time generation |
| 6 | [Drive-HWM: Hierarchical Driving WMs](https://arxiv.org/abs/2609.03572) | Drive-HWM Team | 🧪 | Slow-fast hierarchy; dynamic-aware latents via optical flow; NAVSIM v1+v2 |
| 7 | [Unreal Engine WM Data Pipeline](https://arxiv.org/abs/2609.03557) | UE-WM Team | 🧪 | 8,767 hours synthetic action-conditioned video; two-stage trajectory+rendering |
| 8 | [WebWorld: Browser as World Model](https://arxiv.org/abs/2608.30530) | IQuest | 🧪 | Quality ratchet for web code; +14.9pp MiniAppBench; browser-backed certificates |
| 9 | [WM-LOCO: Humanoid Locomotion](https://arxiv.org/abs/2609.02542) | WM-LOCO Team | 🚀 | Recurrent WM + PPO; 93.3% real Unitree G1 deployment; no foothold labels |
| 10 | [NVIDIA Omniverse NuRec](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec/) | NVIDIA | 🚀 | AV perception re-rendering across vehicle platforms |

---

## 📦 GitHub Projects

| Project | Stars | This Week | Category |
|---------|-------|-----------|----------|
| [SolarWM](https://arxiv.org/abs/2609.02886) | NEW | Fully open: data + code + weights + recipes | Video World Model (5B-33B) |
| [Puffin-World](https://arxiv.org/abs/2609.04196) | NEW | Code + models + Puffin-16M dataset | 3D World Model |
| [ZimaBlue](https://arxiv.org/abs/2609.00188) | NEW | Slow+Fast WAM; 120K+ hours training | World Action Model |
| [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910) | NEW | Patch memory for real-time interactive WMs | Interactive World Model |
| [WorldReward](https://arxiv.org/abs/2609.03952) | NEW | VLM-based reward model + WorldReward-Bench | WM Evaluation |
| [Riemann-1.0](https://arxiv.org/abs/2608.27033) | — | Cited as baseline by ZimaBlue, GIFT | World Action Model (WK35) |
| [DreamerV3](https://github.com/danijar/dreamerv3) | — | Referenced by WM-LOCO, LEAP | Model-based RL reference |
| [HuggingFace](https://huggingface.co/) | — | Hosting SolarWM, Puffin-World releases | Model Hub |

---

## 🎙️ Videos & Podcasts

**1. [OpenAI Agent Message Board Discovery](https://collusion.wiki/)** (HN, Sep 4, 1,833 points)
- Discovery of internal OpenAI agent coordination infrastructure. Reveals how agents negotiate shared state — a core world model concern in multi-agent systems where agents must maintain consistent environment representations.
- **Relevance: 7**

**2. [Anthropic: Formalizing Fermat's Last Theorem](https://anthropic.com/research/formalizing-fermats-last-theorem)** (HN, Sep 4, 663 points)
- Anthropic demonstrates formal mathematical proof capabilities. Planning and proof-search in abstract spaces parallels world model planning in physical spaces — both require lookahead, state tracking, and counterfactual reasoning.
- **Relevance: 7**

**3. [Can AI Design Circuit Boards Yet?](https://eebench.org/blog/can-ai-design-circuit-boards-yet/)** (HN, Sep 4, 294 points)
- Benchmarking AI capabilities in hardware design. Circuit board design requires spatial reasoning and physical constraint satisfaction — core world model capabilities applied to EDA.
- **Relevance: 6**

---

## 💬 Community Insights

### Consensus
- **Autonomous driving is the WAM proving ground** — four driving papers in one week ([SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [StyleDrive](https://arxiv.org/abs/2609.03225), [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111)) confirm that WAMs are reaching production quality for autonomous driving. The automotive domain has well-defined benchmarks ([NAVSIMv2](https://arxiv.org/abs/2609.03602)), safety requirements, and abundant data — making it the natural deployment frontier.
- **World model evaluation is no longer optional** — [VeriPhy](https://arxiv.org/abs/2609.03153), [WorldReward](https://arxiv.org/abs/2609.03952), [Statebench](https://arxiv.org/abs/2609.03673), [Principia](https://arxiv.org/abs/2609.04200), and the [WM evaluation study](https://arxiv.org/abs/2609.02811) all address evaluation gaps. The field has matured past "can we build it?" to "how do we know it works?"
- **Open-source world model infrastructure is viable** — [SolarWM](https://arxiv.org/abs/2609.02886) and [Puffin-World](https://arxiv.org/abs/2609.04196) provide fully open training stacks, aligning with the [broader enterprise open-source trend](https://www.nytimes.com/2026/09/04/technology/open-source-ai-anthropic-openai.html) (305 HN points).

### Disagreements
- **Generative vs. discriminative world models** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885) argues digital world models should use predicted-state matching instead of generation. The robotics community (ZimaBlue, Riemann-1.0) doubles down on generative WAMs. The optimal objective may be domain-dependent.
- **Full-coverage vs. efficient driving WMs** — [SV-WAM](https://arxiv.org/abs/2609.03602) maintains six cameras while [Drive-HWM](https://arxiv.org/abs/2609.03572) and most prior work use front-camera only. Is surround-view necessary or is front-camera sufficient for deployment?
- **Open-loop vs. closed-loop WM evaluation** — the [controlled study](https://arxiv.org/abs/2609.02811) shows measurement-update schedule significantly affects metric reliability, challenging the assumption that better open-loop prediction means better control.

### Emerging Viewpoints
- **Safety-first world modeling** — [RIWM](https://arxiv.org/abs/2609.03774)'s argument that WMs should optimize for consequence-awareness rather than predictive accuracy is gaining traction. Expect "risk-informed" to become a modifier as common as "physics-informed."
- **Browser/digital environments as world model training grounds** — [WebWorld](https://arxiv.org/abs/2608.30530) and [Discriminative WMs](https://arxiv.org/abs/2609.02885) suggest digital environments may be easier and more impactful WM deployment targets than physical robotics.

---

## 📈 Emerging Themes

1. **Autonomous driving WAM convergence** — 4 driving papers in one week ([SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [StyleDrive](https://arxiv.org/abs/2609.03225), [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111)); surround-view, hierarchical, and multi-style architectures all reaching [NAVSIMv2](https://arxiv.org/abs/2609.03602) SOTA quality
2. **World model evaluation infrastructure wave** — [VeriPhy](https://arxiv.org/abs/2609.03153) (auditable physics verification), [WorldReward](https://arxiv.org/abs/2609.03952) (VLM-based rewards), [Statebench](https://arxiv.org/abs/2609.03673) (state tracking), [Principia](https://arxiv.org/abs/2609.04200) (physics tests), [WM eval study](https://arxiv.org/abs/2609.02811) (open vs. closed loop) — 5 evaluation-focused contributions
3. **Digital world models as distinct subfield** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885), [WebWorld](https://arxiv.org/abs/2608.30530), [H3-World](https://arxiv.org/abs/2609.01560) all apply world model frameworks to digital environments (web, browser, video game)
4. **WAM scaling law evidence mounts (week 2)** — [ZimaBlue](https://arxiv.org/abs/2609.00188)'s 36.1% to 77.8% with 120K+ hours extends [Riemann-1.0](https://arxiv.org/abs/2608.27033)'s 200K+ hour result from WK35; Slow+Fast architecture addresses real-time deployment
5. **Safety-first world modeling** — [RIWM](https://arxiv.org/abs/2609.03774) (risk-informed framework), [SV-WAM](https://arxiv.org/abs/2609.03602) (safety boundary penalty), [VeriPhy](https://arxiv.org/abs/2609.03153) (auditable verification) collectively push world models toward consequence-awareness
6. **Open WM training infrastructure** — [SolarWM](https://arxiv.org/abs/2609.02886) (fully open 5B-33B stack) and [Puffin-World](https://arxiv.org/abs/2609.04196) (15M triplets) democratize world model development

---

## 📊 Trend Tracking Over Time

| Theme | First Noted | Consecutive Weeks | Momentum |
|-------|-------------|-------------------|----------|
| JEPA paradigm dominance | WK30 | 7 (WK30–WK36) | 📈 Accelerating — [Physically Grounded JEPA](https://arxiv.org/abs/2609.03565) accepted IROS 2026 |
| Search-free world model deployment | WK30 | 7 | ➡️ Stable — pattern established; no new papers |
| Dynamics-centric supervision | WK30 | 7 | 📈 Accelerating — [WorldReward](https://arxiv.org/abs/2609.03952) dynamics-based reward modeling |
| World model security | WK30 | 7 | ➡️ Stable — no new papers |
| Code as world model | WK30 | 7 | ➡️ Stable — [WebWorld](https://arxiv.org/abs/2608.30530) uses browser but different pattern |
| Hybrid classical + generative | WK30 | 7 | ➡️ Stable — [Semantic Bayesian WMs](https://arxiv.org/abs/2609.03834) bridges symbolic + learned |
| Multi-modal world models | WK30 | 7 | 📈 Accelerating — [Puffin-World](https://arxiv.org/abs/2609.04196) native 3D; 3 modalities |
| LLMs as implicit world models | WK30 | 7 | 📈 Accelerating — [H3-World](https://arxiv.org/abs/2609.01560); [GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) strengthens backbone |
| Continuous-time world models | WK31 | 6 | ➡️ Stable — no new papers |
| Context Collapse in WMs | WK31 | 6 | ➡️ Stable — sparse representations from WK35 not extended |
| Mental world modeling | WK31 | 6 | ➡️ Stable — no new papers |
| Environment co-evolution | WK31 | 6 | 📈 Accelerating — [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910) persistent environments |
| Action-conditioned video WMs | WK34 | 3 | 📈 Accelerating — [SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [ZimaBlue](https://arxiv.org/abs/2609.00188) |
| WM-guided test-time compute | WK34 | 3 | 📈 Accelerating — [WISE](https://arxiv.org/abs/2609.03681) selective imagination scheduling |
| World model benchmarking | WK34 | 3 | 📈 Accelerating — [VeriPhy](https://arxiv.org/abs/2609.03153), [WorldReward](https://arxiv.org/abs/2609.03952), [Statebench](https://arxiv.org/abs/2609.03673), [Principia](https://arxiv.org/abs/2609.04200) — 4 evaluation papers |
| Physical AI funding surge | WK34 | 3 | ➡️ Stable — no new major deals; post-NVIDIA-HF acquisition digestion |
| WAM paradigm (policy+simulator) | WK35 | 2 | 📈 Accelerating — [ZimaBlue](https://arxiv.org/abs/2609.00188) extends with 120K+ hours; [SV-WAM](https://arxiv.org/abs/2609.03602) for driving |
| Sparse world model representations | WK35 | 2 | ➡️ Stable — no new papers; WK35 [LpWM](https://arxiv.org/abs/2608.22764) not yet extended |
| Action adherence alignment | WK35 | 2 | ➡️ Stable — [WorldReward](https://arxiv.org/abs/2609.03952) addresses action consistency but different framing |
| In-context embodied learning | WK35 | 2 | ➡️ Stable — no new papers extending [Zero-WAM](https://arxiv.org/abs/2608.26103) |
| **Autonomous driving WAMs** | **WK36** | **1** | **📈 NEW — 4 driving papers; [SV-WAM](https://arxiv.org/abs/2609.03602) SOTA NAVSIMv2** |
| **Digital world models (web/browser)** | **WK36** | **1** | **📈 NEW — [Discriminative WMs](https://arxiv.org/abs/2609.02885); [WebWorld](https://arxiv.org/abs/2608.30530)** |
| **WM evaluation infrastructure** | **WK36** | **1** | **📈 NEW — 5 evaluation papers; auditable verification** |
| **Safety-first world modeling** | **WK36** | **1** | **📈 NEW — [RIWM](https://arxiv.org/abs/2609.03774); consequence > prediction** |

---

## 🏗️ Implications for Search, Recommendation & Ads

1. **Discriminative world models for recommendation ranking** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885)'s predicted-state matching objective maps directly to recommendation: train world models to distinguish the true user response from counterfactual responses to alternative rankings, rather than generating predicted user behavior. This could improve off-policy evaluation for search ranking and ad placement.

2. **WorldReward as recommendation reward model** — [WorldReward](https://arxiv.org/abs/2609.03952)'s VLM-based preference framework decomposes evaluation into action consistency and quality dimensions. For search/ads: decompose reward into query relevance (action consistency) and user experience quality, training preference models that optimize both simultaneously.

3. **Risk-informed user simulation** — [RIWM](https://arxiv.org/abs/2609.03774)'s framework applies to ads: shift from predicting the most likely user behavior to identifying which user behaviors matter for business outcomes (conversions, lifetime value, churn risk). Safety-critical thinking translates to business-critical user modeling.

4. **Open training infrastructure for recommendation WMs** — [SolarWM](https://arxiv.org/abs/2609.02886)'s fully open stack and [Puffin-World](https://arxiv.org/abs/2609.04196)'s 15M dataset demonstrate viable open training infrastructure. Adapt the three-stage training recipe (pre-train on broad data, mid-train on task-aligned data, specialize) for recommendation world models.

5. **Imagination scheduling for A/B test optimization** — [WISE](https://arxiv.org/abs/2609.03681)'s selective imagination principle applies to counterfactual evaluation: don't simulate all user sessions — focus world model compute on sessions at decision boundaries where the ranking change most impacts outcomes.

**Action items:**
- Prototype [Discriminative WMs](https://arxiv.org/abs/2609.02885) predicted-state matching for recommendation off-policy evaluation
- Adapt [WorldReward](https://arxiv.org/abs/2609.03952) preference decomposition for search relevance + experience quality
- Apply [WISE](https://arxiv.org/abs/2609.03681) selective scheduling to focus counterfactual simulation on high-impact sessions
- Evaluate [RIWM](https://arxiv.org/abs/2609.03774) consequence-aware framework for business-critical user modeling

---

## 🔍 Implications for Agentic AI & Planning

1. **Discriminative world models change agent planning** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885) shows agents don't need generative world models for action selection — predicted-state matching is more compute-efficient and more aligned with the actual use case (choosing the best action). This applies to any agent that uses world models for lookahead.

2. **Imagination scheduling reduces agent planning cost** — [WISE](https://arxiv.org/abs/2609.03681)'s 80% GPU reduction via selective imagination applies directly to agent planning: don't imagine at every step — allocate world model compute to decision points where lookahead changes the selected action.

3. **Safety-first agent planning** — [RIWM](https://arxiv.org/abs/2609.03774)'s risk-informed framework shifts agent planning from "predict the most likely outcome" to "identify which outcomes matter." For safety-critical agents (autonomous driving, medical, financial), this means world models that flag dangerous action sequences rather than merely predicting likely ones.

4. **Browser as agent world model** — [WebWorld](https://arxiv.org/abs/2608.30530) demonstrates that the execution environment itself can serve as the world model, providing objective verification via browser certificates. For web agents, this eliminates the need for learned world models entirely — the browser gives exact state transitions.

5. **Auditable world model evaluation for agent certification** — [VeriPhy](https://arxiv.org/abs/2609.03153)'s traceable verification chains enable auditing agent world models before deployment. Each physics verdict links to supporting evidence — essential for agent certification in regulated domains.

**Action items:**
- Adopt [Discriminative WMs](https://arxiv.org/abs/2609.02885) predicted-state matching for agent action selection — more efficient than generative lookahead
- Implement [WISE](https://arxiv.org/abs/2609.03681) imagination scheduling in agent planning loops to reduce compute cost
- Apply [VeriPhy](https://arxiv.org/abs/2609.03153) auditable evaluation to agent world models before deployment
- Use [WebWorld](https://arxiv.org/abs/2608.30530) browser-as-WM pattern for web agent verification

---

## 👀 Watch List

| Technology | First Noted | Status | This Week's Movement |
|-----------|-------------|--------|---------------------|
| Search-free world models ([INTACT](https://arxiv.org/abs/2607.26056)) | WK30 | 🚀 Breakout | Stable; pattern established |
| JEPA for planning ([TD-JEPA](https://arxiv.org/abs/2607.25337)) | WK30 | 🚀 Breakout | [Physically Grounded JEPA](https://arxiv.org/abs/2609.03565) accepted IROS 2026; 7th consecutive week |
| Code as world model ([VisualPatchWorld](https://arxiv.org/abs/2607.25236)) | WK30 | 🧪 Early | [WebWorld](https://arxiv.org/abs/2608.30530) uses browser but different execution pattern |
| World model security ([False Prophets](https://arxiv.org/abs/2607.23147)) | WK30 | 🚀 Breakout | Stable |
| Hybrid physics + generative ([NVIDIA Cosmos](https://developer.nvidia.com/blog/post-train-nvidia-cosmos-3-edge-for-on-device-robot-control/)) | WK30 | 🚀 Breakout | Stable; post-acquisition integration underway |
| Visuo-tactile world models ([FeelWorld](https://arxiv.org/abs/2607.24267)) | WK30 | 🧪 Early | No new evidence; 7 weeks without progress |
| Video world models at interactive speed | WK30 | 🧪 Early → 📈 Growing | [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910) minute-long real-time with patch memory |
| World model serving ([PCS](https://arxiv.org/abs/2607.21686)) | WK30 | 🚀 Breakout | Stable |
| Continuous-time world models ([ODEWorld](https://arxiv.org/abs/2607.27924)) | WK31 | 🔬 Research → 🧪 Early | No new papers; stable |
| Context Collapse diagnosis ([ActSWM](https://arxiv.org/abs/2607.26712)) | WK31 | 🧪 Early → 📈 Growing | Stable; WK35 LpWM not yet extended |
| Mental world modeling ([MENTIS](https://arxiv.org/abs/2607.27201)) | WK31 | 🔬 Research | No new papers; 6 weeks without progress |
| Environment co-evolution ([Echoverse](https://www.microsoft.com/en-us/research/blog/echoverse-deep-evolving-environments-for-computer-use-agents/)) | WK31 | 🧪 Early → 📈 Growing | [Matrix-Game 3.5](https://arxiv.org/abs/2608.29910) persistent environments |
| Action-conditioned video WMs ([DreamX-Phi](https://arxiv.org/abs/2608.13489)) | WK34 | 🧪 Early → 📈 Growing | 4 driving WAMs + [ZimaBlue](https://arxiv.org/abs/2609.00188) all action-conditioned |
| WM-guided test-time compute ([tau-zero-VLA](https://arxiv.org/abs/2608.16885)) | WK34 | 🧪 Early → 📈 Growing | [WISE](https://arxiv.org/abs/2609.03681) selective imagination scheduling |
| World model benchmarking ([PlayWorld](https://arxiv.org/abs/2608.13552)) | WK34 | 🧪 Early → 📈 Growing | 5 evaluation papers; approaching graduation to mainstream |
| WAM paradigm ([Riemann-1.0](https://arxiv.org/abs/2608.27033)) | WK35 | 🧪 Early → 📈 Growing | [ZimaBlue](https://arxiv.org/abs/2609.00188), [SV-WAM](https://arxiv.org/abs/2609.03602), [GIFT](https://arxiv.org/abs/2609.04193) all WAM-framed |
| Sparse world model representations ([LpWM](https://arxiv.org/abs/2608.22764)) | WK35 | 🔬 Research | No new papers; monitoring |
| Action adherence alignment ([WorldSync](https://arxiv.org/abs/2608.24885)) | WK35 | 🧪 Early | [WorldReward](https://arxiv.org/abs/2609.03952) addresses action consistency via reward |
| **Autonomous driving WAMs** | **WK36** | **🧪 Early** | **NEW: 4 papers; [SV-WAM](https://arxiv.org/abs/2609.03602) SOTA NAVSIMv2** |
| **Digital world models (web/browser)** | **WK36** | **🧪 Early** | **NEW: [Discriminative WMs](https://arxiv.org/abs/2609.02885); [WebWorld](https://arxiv.org/abs/2608.30530)** |
| **WM evaluation infrastructure** | **WK36** | **🧪 Early** | **NEW: 5 papers; auditable [VeriPhy](https://arxiv.org/abs/2609.03153)** |
| **Safety-first world modeling ([RIWM](https://arxiv.org/abs/2609.03774))** | **WK36** | **🔬 Research** | **NEW: consequence > prediction; framework only** |

---

## 🔮 Contrarian View

### What the field may be overestimating
- **Generative world models for digital agents** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885) shows predicted-state matching outperforms generative next-state prediction for action selection. The field's default assumption — that world models must generate — may be wrong for non-physical domains. Generating full web page states is expensive and unnecessary when the goal is to rank actions.
- **Driving WAM benchmark saturation** — Four driving papers in one week ([SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [StyleDrive](https://arxiv.org/abs/2609.03225), [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111)) converging on similar benchmarks ([NAVSIMv2](https://arxiv.org/abs/2609.03602), [nuScenes](https://arxiv.org/abs/2609.03602)). When multiple architectures achieve SOTA simultaneously, the benchmark may be saturating rather than the problem being solved. Real-world driving safety requires evaluation beyond these closed-loop simulators.
- **Open-loop prediction quality** — The [controlled study](https://arxiv.org/abs/2609.02811) showing that measurement-update schedule significantly affects rollout metric reliability challenges the widespread use of open-loop prediction accuracy (FID, FVD) as the primary WM metric. Teams optimizing for these metrics may not be optimizing for control quality.

### What the field may be underestimating
- **Discriminative objectives for world models** — [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885) may represent a broader paradigm shift. Many world model applications (recommendation, search ranking, ad placement, agent action selection) fundamentally require discrimination, not generation. The field's generative default may be costing both compute efficiency and alignment with actual use cases.
- **Safety-consequence alignment** — [RIWM](https://arxiv.org/abs/2609.03774)'s three structural mismatches (likelihood vs. risk, prediction vs. intervention, finite-horizon vs. consequences) suggest most world models are optimizing for the wrong objective in safety-critical settings. The gap between "predicts accurately" and "identifies dangerous futures" may be larger than assumed.
- **Browser/digital environment world models** — [WebWorld](https://arxiv.org/abs/2608.30530) (+14.9pp on MiniAppBench) and [Discriminative WMs](https://arxiv.org/abs/2609.02885) (WebArena-Lite improvements) suggest digital world models may reach production deployment faster than physical world models because digital environments provide exact state transitions and objective verification.
- **Imagination scheduling efficiency** — [WISE](https://arxiv.org/abs/2609.03681)'s 80% GPU reduction via selective imagination suggests most current world-model-augmented training wastes compute on uninformative imagination at low-decision-impact states.

---

## 🧭 Strategic Analysis

### Short-term (0-6 months)
- Autonomous driving WAMs ([SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572)) reach pilot deployment; surround-view coverage becomes table stakes
- [WISE](https://arxiv.org/abs/2609.03681) imagination scheduling adopted to reduce VLA training costs across robotics labs
- [VeriPhy](https://arxiv.org/abs/2609.03153) auditable evaluation becomes standard for world model certification in safety-critical applications
- [SolarWM](https://arxiv.org/abs/2609.02886) open stack enables academic/startup world model research without massive data collection
- [WM-LOCO](https://arxiv.org/abs/2609.02542) pattern replicated on other humanoid platforms beyond [Unitree G1](https://arxiv.org/abs/2609.02542)

### Mid-term (6-18 months)
- Discriminative world models ([predicted-state matching](https://arxiv.org/abs/2609.02885)) become default for digital agent planning, displacing generative WMs in web/GUI domains
- [WorldReward](https://arxiv.org/abs/2609.03952) VLM-based reward modeling enables RL post-training loops for world models analogous to RLHF for language models
- [RIWM](https://arxiv.org/abs/2609.03774) risk-informed framework adopted as regulatory requirement for autonomous driving world models
- WAM scaling laws ([ZimaBlue](https://arxiv.org/abs/2609.00188) pattern) drive investment in large-scale egocentric video collection

### Long-term (2-5 years)
- World model evaluation infrastructure ([VeriPhy](https://arxiv.org/abs/2609.03153), [WorldReward](https://arxiv.org/abs/2609.03952), [Statebench](https://arxiv.org/abs/2609.03673)) matures into certification frameworks for embodied AI
- Discriminative and generative world models coexist: generative for physical simulation, discriminative for digital agent planning and recommendation
- Safety-first world modeling ([RIWM](https://arxiv.org/abs/2609.03774) lineage) becomes mandatory for deployment in regulated industries
- Open world model training stacks ([SolarWM](https://arxiv.org/abs/2609.02886), [Puffin-World](https://arxiv.org/abs/2609.04196)) create a vibrant open ecosystem parallel to the LLM open-weight movement

---

## 🎯 Personalized Relevance

| Development | Relevance Areas | Score |
|-------------|-----------------|-------|
| [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885) | Agentic AI, Search/Recommendation, Planning | 10 |
| [ZimaBlue](https://arxiv.org/abs/2609.00188) (WAM scaling) | World Models, Agentic AI, Training methodology | 10 |
| [WISE](https://arxiv.org/abs/2609.03681) (imagination scheduling) | World Models, Agentic AI, Training efficiency | 10 |
| [WorldReward](https://arxiv.org/abs/2609.03952) (VLM rewards) | Evaluation frameworks, World Models, RL | 9 |
| [VeriPhy](https://arxiv.org/abs/2609.03153) (auditable evaluation) | Evaluation frameworks, Safety, World Models | 9 |
| [SV-WAM](https://arxiv.org/abs/2609.03602) (driving WAM) | World Models, Autonomous driving, Planning | 9 |
| [RIWM](https://arxiv.org/abs/2609.03774) (safety-first WMs) | Evaluation frameworks, Safety, Architecture | 8 |
| [SolarWM](https://arxiv.org/abs/2609.02886) (open stack) | World Models, Enterprise AI adoption | 8 |
| [WM-LOCO](https://arxiv.org/abs/2609.02542) (humanoid locomotion) | World Models, Robotics, Deployment | 8 |
| [WebWorld](https://arxiv.org/abs/2608.30530) (browser-as-WM) | Agentic AI, Search, Verification | 8 |

---

## ✅ Recommendations

### For Research Scientists
1. **Read [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885)** — predicted-state matching is a fundamentally different training objective that may be superior for all non-physical world model applications. Evaluate whether your domain needs generation or discrimination.
2. **Study [ZimaBlue](https://arxiv.org/abs/2609.00188)'s scaling curve** — the 36.1% to 77.8% improvement with video scale provides the clearest WAM scaling law evidence. Use this to estimate data requirements for your target performance.
3. **Adopt [VeriPhy](https://arxiv.org/abs/2609.03153) auditable evaluation** for world model research — traceable verdicts with evidence provenance set a new standard for evaluation rigor.
4. **Read [RIWM](https://arxiv.org/abs/2609.03774)** before deploying world models in safety-critical settings — the three structural mismatches (likelihood vs. risk, prediction vs. intervention, finite-horizon vs. consequences) reframe evaluation priorities.
5. **Benchmark on [WorldReward-Bench](https://arxiv.org/abs/2609.03952)** — the first standardized reward model benchmark for world models.

### For Applied Scientists & Engineers
1. **Implement [WISE](https://arxiv.org/abs/2609.03681) imagination scheduling** in VLA training loops — 80% GPU reduction is immediately actionable.
2. **Follow the [SV-WAM](https://arxiv.org/abs/2609.03602) pattern** for autonomous driving — surround-view coverage with action-centered causal masking maintains safety without sacrificing efficiency.
3. **Use [SolarWM](https://arxiv.org/abs/2609.02886) open stack** for video world model prototyping — fully open data, code, weights, and recipes from 5B to 33B parameters.
4. **Deploy [WM-LOCO](https://arxiv.org/abs/2609.02542) pattern** for humanoid locomotion — 93.3% real deployment on commercially available [Unitree G1](https://arxiv.org/abs/2609.02542).
5. **Use [WebWorld](https://arxiv.org/abs/2608.30530) browser-as-WM** for web agent verification — the browser provides exact state transitions, eliminating learned WM errors.

### For Search & Ads Teams
1. **Prototype [Discriminative WMs](https://arxiv.org/abs/2609.02885) for recommendation** — predicted-state matching could replace generative user simulation for off-policy evaluation.
2. **Adapt [WorldReward](https://arxiv.org/abs/2609.03952) preference decomposition** — separate relevance (action consistency) from experience quality when training recommendation reward models.
3. **Apply [WISE](https://arxiv.org/abs/2609.03681) selective scheduling** to focus counterfactual simulation compute on high-impact user sessions at decision boundaries.
4. **Evaluate [RIWM](https://arxiv.org/abs/2609.03774) consequence-aware modeling** for business-critical outcomes — shift from predicting likely user behavior to identifying behaviors that impact revenue and retention.

---

## 🏆 Executive Takeaways

### Top 5 Technical Advances
1. **[ZimaBlue](https://arxiv.org/abs/2609.00188)** — WAM scaling via 120K+ hours video; 36.1% to 77.8% zero-shot success; Slow+Fast at 30 Hz | 25 min
2. **[Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885)** — Predicted-state matching outperforms generative WMs for digital agent action selection | 20 min
3. **[WISE](https://arxiv.org/abs/2609.03681)** — 80% GPU reduction for VLA post-training via selective imagination scheduling | 20 min
4. **[WM-LOCO](https://arxiv.org/abs/2609.02542)** — World-model-augmented humanoid locomotion; 93.3% real deployment on Unitree G1 | 20 min
5. **[VeriPhy](https://arxiv.org/abs/2609.03153)** — Auditable physics verification for world models; 228/304 failures detected with traceable provenance | 20 min

### Top 5 Business Developments
1. **[GPT-6 Astra released](https://openrouter.ai/openai/gpt-6-astra)** — New OpenAI frontier model; strengthens LLM-as-implicit-world-model backbone
2. **[SolarWM fully open release](https://arxiv.org/abs/2609.02886)** — First complete open video WM stack (data + code + weights + recipes, 5B-33B)
3. **[Corporate America embraces open-source AI](https://www.nytimes.com/2026/09/04/technology/open-source-ai-anthropic-openai.html)** — Enterprise open-source adoption accelerates; aligns with SolarWM/Puffin-World releases
4. **[4 driving WAMs in one week](https://arxiv.org/abs/2609.03602)** — Autonomous driving WAMs reach benchmark maturity; deployment imminent
5. **[NVIDIA Omniverse NuRec](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec/)** — AV simulation infrastructure for world model training data

### Top 5 Must-Read Resources
1. **[ZimaBlue](https://arxiv.org/abs/2609.00188)** — WAM scaling law evidence via video pre-training | 25 min
2. **[Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885)** — Paradigm shift: discriminate, don't generate | 20 min
3. **[WISE](https://arxiv.org/abs/2609.03681)** — Imagination scheduling for efficient VLA training | 20 min
4. **[VeriPhy](https://arxiv.org/abs/2609.03153)** — Auditable world model evaluation | 20 min
5. **[RIWM](https://arxiv.org/abs/2609.03774)** — Safety-first world model framework | 15 min

---

## 📌 What Leaders Should Do Next Week

1. **Read [Discriminative WMs for Web Agents](https://arxiv.org/abs/2609.02885)** — evaluate whether your world model applications need generation or discrimination; predicted-state matching may be fundamentally better for digital domains
2. **Study [ZimaBlue](https://arxiv.org/abs/2609.00188)'s scaling curve** — the clearest WAM scaling law evidence; use to plan data collection and compute investment
3. **Implement [WISE](https://arxiv.org/abs/2609.03681) imagination scheduling** — 80% GPU reduction in VLA training is immediately actionable for any team using world-model-augmented training
4. **Evaluate [VeriPhy](https://arxiv.org/abs/2609.03153) for world model certification** — auditable verification with traceable provenance is the new standard for safety-critical deployment
5. **Read [RIWM](https://arxiv.org/abs/2609.03774)** before deploying world models in regulated settings — the consequence-vs-prediction distinction is fundamental
6. **Use [SolarWM](https://arxiv.org/abs/2609.02886) open stack** for prototyping — the most complete open world model training resource available
7. **Track autonomous driving WAM convergence** — [SV-WAM](https://arxiv.org/abs/2609.03602), [Drive-HWM](https://arxiv.org/abs/2609.03572), [StyleDrive](https://arxiv.org/abs/2609.03225), and [Qwen-Drive-1.0](https://arxiv.org/abs/2609.00111) signal imminent deployment
8. **Assess [GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra) capabilities** for hybrid LLM+world model systems — each frontier model upgrade strengthens the implicit world model backbone

---

*Report generated: September 5, 2026 | Covering: August 30–September 5, 2026 (WK36)*
*Topic: World Models | Sources: arXiv cs.LG/cs.AI/cs.RO, HuggingFace Papers, NVIDIA Developer, Hacker News, Google Scholar*
*Prior reports: [WK30](world-models-2026-07-WK30-news.md), [WK31](world-models-2026-08-WK31-news.md), [WK34](world-models-2026-08-WK34-news.md), [WK35](world-models-2026-08-WK35-news.md) | Next report: WK37*
