---
title: "Supervised Fine-Tuning (SFT)"
source: "https://www.emergentmind.com/topics/supervised-fine-tuning-sft"
ingestedAt: "2026-05-18T00:28:24Z"
---
#  Supervised Fine-Tuning (SFT) 

Updated 30 June 2025 

  * Supervised Fine-Tuning (SFT) is a paradigm that optimizes large models with curated prompt-response pairs using cross-entropy loss.
  * It improves multi-skill performance in instruction following, code generation, and reasoning by carefully balancing data quantity and domain composition.
  * Advanced strategies like Dual-stage Mixed Fine-Tuning effectively mitigate catastrophic forgetting and cross-domain interference for robust model adaptation.



Supervised [Fine-Tuning](https://www.emergentmind.com/topics/fine-tuning-sft) (SFT) is a crucial post-training paradigm for adapting LLMs to complex, multi-ability instruction-following, code generation, and reasoning, as well as for fine-tuning vision and other [foundation models](https://www.emergentmind.com/topics/foundation-models-fms). SFT seeks to improve alignment, robustness, and capability coverage by optimizing model parameters using curated prompt-response pairs, typically via cross-entropy loss. Recent research has rigorously examined the influence of data composition, scaling, training strategies, and the interplay among various abilities sharpened by SFT, with special attention to [catastrophic forgetting](https://www.emergentmind.com/topics/catastrophic-forgetting), inter-ability interference, and optimal multi-skill acquisition.

## 1\. Data Composition and Scaling Laws in SFT

Empirical evidence demonstrates that SFT's effectiveness is highly sensitive to both the absolute **amount** and **composition** of training data. The impact is profoundly ability-dependent:

  * **Mathematical reasoning** and **code generation** abilities, benchmarked by [GSM8K](https://www.emergentmind.com/topics/arithmetic-reasoning-gsm8k) and [HumanEval](https://www.emergentmind.com/topics/humaneval) respectively, improve _monotonically and robustly_ as the amount of in-domain SFT data increases. Their scaling curves are often log-linear and unbounded within practical data volumes.
  * **General human-aligned abilities** (instruction following, alignment, e.g., [MT-Bench](https://www.emergentmind.com/topics/mt-bench-756edf8b-73a3-47a0-8a7a-1f34e95aacd1)) exhibit rapid improvement with as little as 1,000 samples, but performance quickly saturates, beyond which added data yields negligible gains (see Figure for single scaling curve).



Data **composition** experiments reveal that mixing SFT data types (e.g., math, code, general abilities) is especially beneficial in low-resource settings. When data is limited per skill, mixing different ability data leads to synergistic transfer and improved multi-task performance. However, as data quantities grow, interference emerges: additional data from unrelated domains can behave as noise, degrading the in-domain generalization of each ability type ([Dong et al., 2023](/papers/2310.05492)).

The **amount** of data for a given domain dominates the effect of _composition ratio_. Provided each skill receives a sufficient number of examples, the fraction of each type in the mix is secondary; sharp deterioration occurs only when particular domains become underrepresented.

## 2\. Model Size, Ability Scaling, and Generalization

Scaling experiments across model size (7B, 13B, 33B parameters) reveal distinct trends:

  * **Larger models consistently outperform smaller models across all abilities when provided equal amounts of data** , reflecting increased capacity to exploit SFT signals. This holds especially as data volumes grow, accentuating the scaling advantage of large LLMs.
  * In extremely low-data regimes, smaller models sometimes outperform due to large-model overfitting, but this advantage vanishes rapidly with additional data.
  * Each ability demonstrates a unique scaling law: math and code require substantial in-domain SFT data for continual improvements; general abilities plateau early, implying diminishing returns and a greater premium on data quality and coverage for these domains.



This separation of scaling regimes by ability suggests differential data investment strategies for multi-ability LLM training: prioritize volume for code/math, but prioritize curation and coverage for general alignment benchmarks.

## 3\. SFT Training Strategies and Catastrophic Forgetting

Sequential or naive multi-task SFT introduces critical challenges when learning multiple abilities:

  * **Multi-task mixing** —training on code, math, and general responses simultaneously—can **impair general ability** due to cross-domain interference.
  * **Sequential SFT** —training on one ability after another—risks **catastrophic forgetting** , where newly trained abilities overwrite previously learned ones, particularly if task domains overlap semantically.



The study introduces the **[Dual-stage Mixed Fine-tuning](https://www.emergentmind.com/topics/dual-stage-mixed-fine-tuning-dmt-e66b7d15-4054-4bde-8e52-50f0964e6300) ([DMT](https://www.emergentmind.com/topics/dual-stage-mixed-fine-tuning-dmt))** strategy for multi-ability SFT:

  * **Stage 1:** Fine-tune on specialized skills (math+code) exclusively, consolidating high performance in those areas.
  * **Stage 2:** Fine-tune on general ability data _plus_ a small proportion (kkk, e.g., 1/256) of specialized data. This acts as a rehearsal mechanism, preventing the overwriting of code/math capabilities by general alignment.



Quantitative results confirm that DMT preserves high performance across all abilities, outperforming both naive multi-task and sequential methods:

Model | Math (GSM8K) | Code (HumanEval) | General ([MT-Bench](https://www.emergentmind.com/topics/mt-bench))  
---|---|---|---  
7B, Mixed Sequential | 32.60 | 15.24 | 6.02  
7B, DMT (1/256) | **41.92** | **17.68** | **6.08**  
13B, Mixed Sequential | 40.48 | 18.30 | 5.93  
13B, DMT (1/256) | **46.47** | **19.50** | **6.03**  
  
These outcomes highlight the importance of strategic SFT recipe design for retaining and integrating multiple abilities without trade-offs ([Dong et al., 2023](/papers/2310.05492)).

## 4\. Fundamental Experimental Insights

Extensive t-SNE visualization and ablation reveal that the [representation geometry](https://www.emergentmind.com/topics/representation-geometry) for math queries remains more distinct post-DMT than code or general abilities, which remain more entangled—explaining the observed interference patterns. Removing code/math examples from general alignment SFT sets (e.g., ShareGPT) does not disrupt the core experimental conclusions, supporting the inference that _[diversity](https://www.emergentmind.com/topics/diversity-beta-recall)_ (rather than mere overlap) drives synergy in low-resource multi-skill settings.

Another finding is that, in sequential SFT, the last trained ability is preferentially retained, with prior abilities diminished in the absence of mixing.

Performance boosts on all abilities are observed when kkk in DMT is set to a small, nonzero fraction; setting kkk too high shifts the trade-off back towards interference and forgetting.

## 5\. Recommendations and Open Directions

Careful composition of SFT data and training order is essential for large-scale, multi-ability LLMs. Notably:

  * For general abilities that saturate with only a few thousand examples, further scaling up data quantity is inefficient; targeted, high-quality curation is advised.
  * For math/code, continuous scaling of in-domain examples brings continual improvements.
  * Data mixing should be managed with respect to absolute quantities per skill; arbitrary mixing or random sequencing of SFT domains risks losing key abilities, especially in data-rich settings.
  * The DMT strategy is recommended for practical SFT of LLMs aiming for balanced skill portfolios.



Important open areas include extending the DMT framework to acquisition of additional abilities (e.g., creative writing, planning), dynamic adaptation of the kkk parameter, and parameter-efficient extensions (e.g., adapter-based SFT).

## 6\. Summary Table: SFT Strategy Outcomes (LLaMA-7B Example)

Training Strategy | GSM8K (Math) | HumanEval (Code) | MT-Bench (General)  
---|---|---|---  
Math only | 49.10 | 6.71 | 2.53  
Code only | 4.51 | 18.40 | 4.30  
General only | 11.10 | 10.42 | 5.88  
Multi-task | 47.53 | 14.63 | 5.76  
Sequential | 31.39 | 15.85 | 5.72  
Mixed Sequential | 32.60 | 15.24 | 6.02  
**DMT (1/256)** | **41.92** | **17.68** | **6.08**  
  
## 7\. Broader Implications

This body of work elucidates the complex dependencies among data composition, scaling, and ability retention in SFT for LLMs. It establishes that _absolute data quantity for each domain is the primary determinant of ability enhancement_ , not the fractional mix, and that advanced SFT strategies like DMT are crucial for multi-ability alignment without destructive interference or forgetting. These results inform both open-source practice and proprietary model development, and provide a quantitative foundation for designing next-generation, versatile, and scalable SFT pipelines for instruction-following and complex, multi-domain LLMs.

Definition Search Book Streamline Icon: https://streamlinehq.com

References (1)