---
title: "Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality"
source: "https://arxiv.org/html/2506.14681v2"
ingestedAt: "2026-05-18T00:12:15Z"
---
###### Abstract

Supervised fine-tuning (SFT) is a critical step in aligning large language models (LLMs) with human instructions and values, yet many aspects of SFT remain poorly understood. We trained a wide range of base models on a variety of datasets including code generation, mathematical reasoning, and general-domain tasks, resulting in 1,000+ SFT models under controlled conditions. We then identified the dataset properties that matter most and examined the layer-wise modifications introduced by SFT. Our findings reveal that some training–task synergies persist across all models while others vary substantially, emphasizing the importance of model-specific strategies. Moreover, we demonstrate that perplexity consistently predicts SFT effectiveness, often surpassing superficial similarity between the training data and the benchmark, and that mid-layer weight changes correlate most strongly with performance gains. We release these 1,000+ SFT models and benchmark results to accelerate further research. All resources are available at <https://github.com/llm-jp/massive-sft>.

Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality

Yuto Harada1,2*††thanks: Equal Contribution., Yusuke Yamauchi1,2*, Yusuke Oda1,3, Yohei Oseki1,2, Yusuke Miyao1,2††thanks: Corresponding authors: Yusuke Miyao and Yu Takagi, Yu Takagi4 1NII LLMC, 2The University of Tokyo, 3NAIST, 4Nagoya Institute of Technology, {harada-yuto, yamauchi_y}@nii.ac.jp yusuke@is.s.u-tokyo.ac.jp takagi.yu@nitech.ac.jp

##  1 Introduction

Recent advances in large language models (LLMs) have greatly improved natural language understanding and generation. However, pretrained LLMs often fail to align with human intentions or specific tasks (Ouyang et al., [2022](https://arxiv.org/html/2506.14681v2#bib.bib42)), motivating alignment methods. Supervised fine-tuning (SFT) trains models to follow human instructions and remains a widely used and effective approach for improving downstream performance (Wei et al., [2022](https://arxiv.org/html/2506.14681v2#bib.bib53); Guan et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib24)).

Although recent works have explored how model size and training-data characteristics influence downstream tasks in the context of SFT (Jin and Ren, [2024](https://arxiv.org/html/2506.14681v2#bib.bib34); Dong et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib19)), large-scale research specifically examining which aspects of SFT datasets benefit different base models remains limited. While some studies compare or analyze publicly available models (Oyama et al., [2025](https://arxiv.org/html/2506.14681v2#bib.bib43)), these are not controlled experiments and often introduce biases, such as favoring certain model families. Consequently, it remains unclear how SFT of various models on different datasets affects benchmark performance, how relationships among datasets and benchmarks vary across models, and which internal weights are most responsible for these effects. Furthermore, there are several SFT training approaches including Low-Rank Adaptation (LoRA) (Hu et al., [2022](https://arxiv.org/html/2506.14681v2#bib.bib29)), and there is ongoing debate about the optimal amount of data required (Zhou et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib64); Chen et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib6)); however, there has yet to be a comprehensive, quantitative comparison. Hence, a comprehensive examination of these issues on SFT is urgently needed.

Figure 1: Overview of this study. We conduct SFT on numerous combinations of base models and training data. These models are evaluated on a variety of benchmark tasks to comprehensively examine the relationships among the base models, training data, and benchmark tasks.

In this study, we trained twelve base models on multi-domain datasets, produced a large suite of SFT models, and evaluated them across diverse tasks (Figure [1](https://arxiv.org/html/2506.14681v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality")). Specifically, we address the following Research Questions (RQs):

  1. 1.

How do models, training data, and benchmarks interact for downstream performance? Do any training datasets yield consistent gains across models, or are improvements model-specific? Are relationships between datasets and benchmarks stable across models?

  2. 2.

Which properties of the training data used for SFT affect downstream performance?

  3. 3.

Which layers in the model are most critical for SFT? Are there universal patterns across different models?

  4. 4.

How do factors debated in SFT, including training method, sample size, and cross-lingual transfer, relate to performance?




In summary, our contributions are as follows:

#### Large-Scale, Integrated Evaluation

By systematically performing SFT on multiple base models and various training datasets, we uncover the complexity of relationships among models, data, and downstream tasks. While the relationships between training data and evaluation tasks follow broadly similar patterns across models, they also exhibit model-specific characteristics.

#### Revealing a Simple “Perplexity Is Key” Law

We find that training data with lower perplexity for the base model consistently leads to greater improvements in downstream performance. In contrast, factors once considered crucial, such as content similarity between training and evaluation data or tokenizer compatibility, do not exhibit as strong an effect as perplexity.

#### Strong Correlation Between Mid-Layer Weight Changes and Performance

We observe that changes in mid-layer weights correlate more strongly with downstream performance gains than changes in either the top or bottom layers. Indeed, intrinsic dimensionality analysis of embeddings revealed that the embedding space begins to diverge substantially from the base model at mid-layer positions, suggesting these layers actively expand the model’s representational subspace during SFT. This pattern appears consistent across multiple models, offering critical insights for efficient fine-tuning and model monitoring.

#### Embedding the SFT Landscape

Projecting the log-likelihood vectors of fine-tuned models into a common latent space lets us compare diverse training dynamics in one coordinate system. The resulting map shows that the global layout is determined by model family rather than training corpus, that checkpoints from successive epochs converge toward a shared instruction-following region, that enlarging the instruction set from 1k to 20k nudges models only slightly outward from this center, and that LoRA trajectories almost perfectly overlap those of full-parameter tuning.

#### Resource Release for Future Research

All fine-tuned models produced in this study are publicly released. We expect this comprehensive set of models to accelerate deeper investigations of SFT and to foster rapid progress in the field.

##  2 Related Work

The role of training data characteristics in SFT has been highlighted in many prior studies. For instance, mixing code-generation data has been suggested to enhance a model’s reasoning and logical abilities (Dong et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib19)). Similarly, incorporating instruction data that includes procedural knowledge could improve mathematical reasoning (Ruis et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib46)). Furthermore, considering task relevance when selecting datasets can lead to more robust performance (Huang et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib30); Zhang et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib59)).

While early work focused on how to fine-tune, comparing full-parameter updates against LoRA (Ivison et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib32); Zhuo et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib65); Dettmers et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib16); Zhao et al., [2024b](https://arxiv.org/html/2506.14681v2#bib.bib61); Biderman et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib3)), or debating sample size (Zhou et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib64); Zhao et al., [2024a](https://arxiv.org/html/2506.14681v2#bib.bib60); Chen et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib6)). More recent studies have shifted attention to the statistics of the training data itself. For example, Jin and Ren ([2024](https://arxiv.org/html/2506.14681v2#bib.bib34)) and Wu et al. ([2025](https://arxiv.org/html/2506.14681v2#bib.bib55)) independently show that lower perplexity and moderate sequence length are stronger predictors of SFT success than sheer volume.

Overall, most studies focus on particular models or tasks, and there remains a lack of comprehensive, large-scale evaluations across multiple models. This study aims to offer a broader perspective by controlling for model, data, and fine-tuning methods on a larger scale, thus providing more integrated insights into SFT behavior.

##  5 Discussion and Conclusion

We conducted a comprehensive set of SFT experiments involving multiple 7B-scale base models, diverse training datasets, and a wide array of downstream tasks. Our analysis revealed that, while certain dataset–task synergies are observed consistently across models, their effects can vary greatly depending on the specific model in question. Notably, perplexity emerged as a particularly robust predictor of SFT success, outperforming both topic similarity and average sequence length. Perplexity can be shaped by multiple latent properties of both the data and the model. Accordingly, we view it as a practical proxy for compatibility between the model and the data rather than a causal factor. Identifying the causal drivers behind this association is an important direction for future work.

Furthermore, mid-layer weight changes were found to correlate most strongly with performance improvements, indicating that critical adaptations often take place in these layers. By embedding every model checkpoint into a common latent space, we found that (i) model architecture exerts a stronger influence than the SFT corpus, (ii) training epochs drive diverse runs toward a shared instruction-compatible region, (iii) large instruction sets tend to relocate models toward the periphery—often reducing accuracy relative to smaller sets—and (iv) LoRA trajectories almost coincide with full-parameter ones, diverging only slightly on the periphery; this mirrors the small but systematic trade-off we observed between knowledge-heavy tasks (full-parameter advantaged) and open-ended QA (LoRA advantaged).

Contrary to the typical assumption that a dataset closely resembling the target task is best, we find data with a lower perplexity (where the model requires minimal additional learning or unlearning) generally yields more robust improvements. Additionally, our observations of code data helping math tasks suggest significant cross-domain transfer beyond simple topic alignment.

Discovering the importance of mid-layer changes could reshape fine-tuning strategies. Updating the mid-layers, or monitoring them closely, could provide more efficient or interpretable SFT. Observing common mid-layer change patterns across models suggests a shared mechanism for task-related knowledge acquisition.

## Limitations

In this study, we conducted comprehensive fine-tuning experiments on pre-trained models in the 7-9B parameter class. Due to limited computational resources, we were unable to extend our verification to larger models (e.g., 70B, 175B, or MoE architectures). It is unclear whether the findings obtained in this research can be generalized to these larger models.

We emphasize the transparency and reproducibility of our analysis, and therefore, we trained our models using only open-access training datasets. Compared to existing publicly available English corpora, there are still limited multilingual instruction-tuning datasets. Consequently, our study used only English training datasets. A comprehensive investigation into cross-lingual knowledge transfer and its differing effects remains a subject for future work. We use about 10 popular training datasets for SFT, possibly limiting generality for highly specialized tasks or broader multilingual corpora.

While perplexity proved insightful, it can fluctuate based on tokenizer design and base training distributions, indicating a need for more nuanced measures.

## Ethical Considerations

This work uses only publicly available and properly licensed datasets and base models. Their licenses permit research use and redistribution. All datasets and models were used in accordance with their intended research purposes, and our released models will maintain this intended use.

We did not collect any new data. While we did not manually inspect all samples, we acknowledge the possibility of residual personally identifiable or harmful content in the original datasets and rely on the original curators’ filtering processes.

We will release over 1,000 fine-tuned models as part of this study. While we do not anticipate major risks, we acknowledge the potential for misuse—such as generating harmful or misleading content. To mitigate this, all released models will include a responsible use clause and detailed model cards describing limitations. We encourage responsible use.

We used AI tools to assist in writing training and evaluation scripts, and to support basic analysis tasks such as summarizing experimental results.

##  Appendix A Description of Base Models

Table 1: Overview of the 12 base models employed for SFT experiments. The table summarizes their parameter sizes, primary training language, and maximum supported context lengths.

OLMo (Groeneveld et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib23)) is developed by _Allen Institute for AI_. An English-centric, 7B-parameter decoder model pre-trained on a carefully filtered mix of web pages, books, and code (totaling 2.5 trillion tokens). Flash-Attention 2 support was added in later versions, enabling fast, memory-efficient inference. Model-card results show competitive GSM8K and MMLU scores, rivaling some 10B-class models.

Llama3 (Dubey et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib20)) is developed by _Meta AI_. An 8B English model trained on multi-trillion-token mixed-domain data with a byte-level BPE tokenizer and scaled RoPE. Safety alignment combines RLHF and rejection sampling. Delivers strong, well-rounded performance across reasoning, code, and chat benchmarks.

Mistral (Jiang et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib33)) is developed by _Mistral AI_. An English 7B model whose pre-training corpus mixes web, academic text, and code. Grouped-query and sliding-window attention enable very long-sequence processing while retaining high speed. Matches or exceeds Llama-2-13B on many English tasks.

Gemma2 (Team et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib51)) is developed by _Google DeepMind_. An English 9B model trained on a large quality-filtered corpus and enhanced with internal architectural refinements such as improved normalization and position encoding, building on modern Transformer techniques. Public reports show it surpasses most open 7–13B baselines on language-understanding leaderboards.

Qwen2.5 (Yang et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib56)) is developed by _Alibaba’s Qwen team_. A Chinese–English bilingual 7B model further pre-trained on high-quality proprietary Chinese data. RoPE extrapolation enables extremely long inputs. The model card provides agent-style prompting templates and strong results on tool use and code generation.

Chinese-Llama3 (Cui et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib13)) is developed by _Harbin NLP (HFL)_. An 8B Chinese model obtained by continual pre-training of Llama-3 on an extensive Chinese corpus with vocabulary augmentation. Significantly boosts Chinese QA and CMMLU scores over the original Llama-3.

Chinese-Mistral (Hsu et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib28)) is developed by _itpossible_. A 7B Chinese variant of Mistral-v0.1, additionally trained on Chinese Wikipedia, news, and conversation data. Improves cross-lingual performance on Chinese benchmarks while preserving the original architecture.

Yi1.5 (AI et al., [2025](https://arxiv.org/html/2506.14681v2#bib.bib1)) is developed by _01.AI_. A 9B multilingual model (Chinese + English focus) based on the original Yi model trained on 3.1 trillion tokens, with an additional 500 billion tokens used for continual pretraining, including substantial code and low-resource-language data. Shows solid zero-shot transfer to many Asian and European languages as well as code-related tasks.

LLMjp-3 (LLM-jp et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib41)) is developed by _LLM-jp_. A 7.2B Japanese-centric model built from scratch on a 2.1 trillion token multilingual corpus, predominantly composed of Japanese web, book, and dialogue texts, along with a smaller portion of English and other languages. Public experiments indicate it surpasses Llama-2-13B on Japanese QA and summarization.

Llama3-Swallow (Fujii et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib22)) is developed by _TokyoTech LLM Group_. An 8B Japanese model produced by continual pre-training of Llama-3-8B on large Japanese corpora plus vocabulary extension. Reports notable gains for Japanese NER and academic-paper summarization.

Swallow-Mistral (Fujii et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib22)) is developed by _TokyoTech LLM Group_. A 7B Japanese follow-up to Mistral-7B with memory-footprint optimizations. Excels at Japanese dialogue and technical writing according to model-card evaluations.

Sarashina-2 is developed by _sbintuitions_. A 7B Japanese Llama derivative further trained on Japanese text and code. Distributed with LoRA adapters, making domain-specific fine-tuning straightforward.

##  Appendix B Description of Training Datasets

Table 2: Repository is the original source of the data used and Samples represents its total number of samples. Lengths indicates the average number of words in each data at 1k sample pre-processing.

Alpaca (Taori et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib50)) is a 52k-example English corpus obtained by filtering the original Stanford Alpaca to remove hallucinating prompts, merged instructions, empty outputs, and other defects. The resulting instruction/input/output triples serve as a cleaner general-purpose starting point for instruction tuning.

LIMA (Zhou et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib64)) is a compact set of 1000 prompt–response pairs—750 mined from Stack Exchange, wikiHow, and r/WritingPrompts plus 250 author-written items—selected for diversity and a consistent assistant style. It probes how well a strong language model can be aligned with minimal but high-quality supervision.

UltraChat (Ding et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib17)) is a 774k multi-turn English dialogue corpus synthesized by two ChatGPT-Turbo agents. We use a reformatted version of the original release . In our preprocessing pipeline, we extract only the initial user prompt and the first assistant reply as each training sample.

CodeAlpaca 20k (Chaudhary, [2023](https://arxiv.org/html/2506.14681v2#bib.bib5)) is a collection of 20k English programming instructions generated with the Self-Instruct pipeline using text-davinci-003. About 40% of the samples include an input field, and the schema mirrors Alpaca but focuses exclusively on code generation and editing.

Magicoder (Wei et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib54)) contains 111k licence-clean code-centric instructions obtained by de-contaminating the Evol-CodeAlpaca corpus. Every example is a single-turn instruction→response pair, offering a larger companion to CodeAlpaca.

OpenMathInstruct (Toshniwal et al., [2024](https://arxiv.org/html/2506.14681v2#bib.bib52)) is a 1.8M mathematics corpus whose step-by-step solutions were generated with Mixtral-8×7B and a Python interpreter, then automatically validated.

MathInstruct (Yue et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib57)) aggregates 262k math-reasoning problems from 13 sources and augments them with both chain-of-thought and program-of-thought rationales, supplying lightweight yet generalizable coverage for mathematical fine-tuning.

FLAN Collection (Wei et al., [2022](https://arxiv.org/html/2506.14681v2#bib.bib53)) is the remix file flan2021_zsnoopt_submix_data.json. Specifically, it corresponds to the FLAN‑2021 sub‑mix and employs the zero‑shot, no‑options template variant (i.e., prompts contain only the instruction without in‑context examples or candidate options). We follow the taxonomy of Dubey et al. ([2024](https://arxiv.org/html/2506.14681v2#bib.bib20)); Contributors ([2023](https://arxiv.org/html/2506.14681v2#bib.bib12)) and split the data into three thematic subsets.

FLAN Knowledge uses BoolQ (bool_q:1.0.0), NaturalQuestions (natural_questions_open:1.0.0), and TriviaQA (trivia_qa/rc:1.1.0). Samples whose output field is "none" are discarded.

FLAN Reasoning combines ARC-Easy (ai2_arc/ARC-Easy:1.0.0), ARC-Challenge (ai2_arc/ARC-Challenge:1.0.0), HellaSwag (hellaswag:1.1.0), WinoGrande (winogrande:1.1.0), and PIQA (piqa:1.0.0).

FLAN Comprehension contains QuAC (quac:1.0.0) and SQuAD v2.0 (squad/v2.0:3.0.0). Samples with an output of ‘none‘ are omitted.

##  Appendix C Preliminary Experiments

In our main experiments, we conduct SFT using various base models and diverse training datasets. To ensure valid and reliable results across different configurations, it is crucial to select appropriate hyperparameters. Therefore, we conducted preliminary experiments aimed at determining suitable hyperparameters. 

These preliminary experiments were carried out under the following conditions. We employed the Llama3-8B model and utilized six different datasets, each comprising approximately 1,000 samples: Magicoder, LIMA, Code Alpaca, FLAN, Openmath, and Alpaca.

We examined several hyperparameter settings: learning rate = {2e-7, 1e-6, 2e-6, 1e-5, 2e-5, 1e-4}, batch size = {32, 64, 128, 256}, weight decay = {0, 0.1}, training method = {LoRA, full-parameter tuning}.

This combination of hyperparameters resulted in 96 unique experimental conditions. For each condition, we trained for 10 epochs and saved a checkpoint after every epoch (epochs 1 to 10). We treated these per-epoch checkpoints as distinct candidate models, yielding 960 models per dataset. Given that we utilized six datasets, the total number of trained models reached 5,760, consuming at least 23,040 GPU-hours.

For evaluation purposes, we utilized two benchmarks: MMLU and MT-bench, ensuring comprehensive performance assessment across diverse tasks.

##  Appendix D Description of Training Settings

This section summarizes the training configurations, computational cost, and other implementation details used in our supervised fine-tuning experiments.

Out of a total of 1,070 training runs, 1,059 models were successfully trained. Training failed in 11 cases, all related to out-of-memory (OOM) errors involving the Gemma model trained on the Magicoder dataset. Specifically, one failure occurred in a single-dataset setting, while the remaining ten failures arose during the All Dataset setting, where checkpoints were saved at every epoch (resulting in ten distinct training jobs).

We used separate hyperparameter settings for full-parameter fine-tuning and LoRA. Full-parameter fine-tuning was conducted with a learning rate of 1.0×10−51.0\times 10^{-5}, batch size of 32, weight decay of 0.0, and 10 training epochs. For LoRA, we used a learning rate of 2.0×10−62.0\times 10^{-6}, batch size of 128, weight decay of 0.0, and the same number of epochs. These values were determined based on preliminary grid-search experiments.

The computational time for fine-tuning on 1k samples varied depending on the model, batch size, and training method, but on average, each run took approximately 30 minutes. To accelerate training, we employed Flash Attention 2 (Dao, [2023](https://arxiv.org/html/2506.14681v2#bib.bib14)) and DeepSpeed (Rasley et al., [2020](https://arxiv.org/html/2506.14681v2#bib.bib45)) for all models. Training these 1,059 runs required at least 530 GPU-hours.

To investigate the impact of individual datasets, we conducted a dataset ablation study using three representative models: OLMo, Qwen, and LLM-jp. In this setting, we trained models on nine datasets at a time, excluding one dataset in each run (i.e., leave-one-out strategy). This allowed us to observe how the absence of specific datasets affected downstream performance. The ablation experiments were performed under the same conditions as regular 1k-sample training, using both full-parameter and LoRA-based fine-tuning.

As noted in Section [3.2](https://arxiv.org/html/2506.14681v2#S3.SS2 "3.2 Training Datasets ‣ 3 Methods ‣ Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality"), all datasets were preprocessed under consistent conditions. During training, we formatted all samples using a standardized instruction-response template:
    
    
    ###Question: {instruction}
    ###Answer: {response}
    

##  Appendix E Description of the Evaluation Dataset

This appendix provides an overview of the datasets used for evaluation. The test cases and evaluation settings follow the format provided by OpenCompass.

MATH (Hendrycks et al., [2021c](https://arxiv.org/html/2506.14681v2#bib.bib27)) consists of 12,500 problems from high school math competitions. Each problem in MATH has a full step-by-step solution and models are tasked with generating tokens to construct the final answer.

GSM8K (Cobbe et al., [2021](https://arxiv.org/html/2506.14681v2#bib.bib11)) is a dataset of 8,500 high quality linguistically diverse grade school math word problems created by human problem writers. Compared to MATH, the problems are easier and include basic knowledge questions, such as asking for the number of days in a week.

HumanEval (Chen et al., [2021](https://arxiv.org/html/2506.14681v2#bib.bib7)) consists of 164 hand written programming problems. It assesses language comprehension, reasoning, algorithms, and simple mathematics.

MBPP (Austin et al., [2021](https://arxiv.org/html/2506.14681v2#bib.bib2)) consists of 974 programming tasks, designed to be solvable by entry-level programmers. The problems range from basic computations to those requiring external mathematical knowledge.

BoolQ (Clark et al., [2019](https://arxiv.org/html/2506.14681v2#bib.bib9)) is a question answering dataset for yes/no questions containing 15942 examples. The questions are real user queries—unprompted and written without knowing the answers—making them more inferential and challenging than synthetic datasets.

NaturalQuestion (Kwiatkowski et al., [2019a](https://arxiv.org/html/2506.14681v2#bib.bib36)) consists of over 300,000 questions. This corpus features questions posed by actual users and challenges QA systems to read and understand a full Wikipedia article, which might or might not include the answer.

MMLU (Hendrycks et al., [2021b](https://arxiv.org/html/2506.14681v2#bib.bib26), [a](https://arxiv.org/html/2506.14681v2#bib.bib25)) consists of multiple-choice question-answer pairs divided into 57 subjects spanning STEM fields, the humanities, social sciences, and beyond. The questions vary in complexity, from elementary to expert-level, and assess both factual knowledge and reasoning skills.

MMLU-zh (Li et al., [2023a](https://arxiv.org/html/2506.14681v2#bib.bib38)) contains 11,528 multiple-choice questions across 67 diverse subjects, including STEM, humanities, social sciences, and China-specific topics (e.g., Chinese law, traditional medicine, and ancient Chinese). The dataset is specifically constructed to reflect the linguistic and cultural nuances of Chinese, with many questions that are not easily translatable from English benchmarks like MMLU.

MMLU-jp We evaluated the models’ Japanese generation ability using the Japanese-translated version of the multilingual MMLU test set . While the content of the questions remains the same as the original MMLU, both the questions and answers are presented in Japanese.

TruthfulQA (Lin et al., [2022](https://arxiv.org/html/2506.14681v2#bib.bib40)) comprises 817 questions that span 38 categories, including health, law, finance and politics. The questions are carefully crafted to trigger imitative falsehoods—answers that are commonly believed but factually incorrect.

MTBench (Zheng et al., [2023](https://arxiv.org/html/2506.14681v2#bib.bib63)) is a benchmark designed to evaluate a model’s instruction-following capabilities in a multi-turn dialogue format, consisting of 80 two-turn question sets. We conducted evaluations using the LLM-as-a-Judge framework, employing gpt-4o-2024-08-06 as the evaluator LLM.

AlpacaEval v2 (Li et al., [2023b](https://arxiv.org/html/2506.14681v2#bib.bib39)) AlpacaEval v2 is an instruction-following benchmark consisting of 805 questions, created by integrating existing benchmarks and incorporating insights from real user interactions. We conducted pairwise evaluations by comparing the responses of our fine-tuned models against those of GPT-4-Turbo, and report the win rate as the evaluation metric. We used gpt-4o-2024-07-18 as the evaluator LLM.

All models evaluated in this experiment used the same prompt across all benchmarks. Therefore, it should be noted that the scores on downstream tasks may differ from those reported in technical reports, as the pre-trained models used a prompt template that differs from the one originally provided. Among the trained models, the following models failed to produce results for certain tasks:

  * •

Swallow-Mistral-7B: All 41 trained models encountered out-of-memory errors across all tasks.

  * •

Mistral-7B: The 20 LoRA-tuned models encountered out-of-memory errors on few-shot tasks.

  * •

Gemma2-9B: For the models trained with all data using LoRA (from epoch 1 to epoch 4), responses that made evaluation with Alpaca Eval v2 impossible (extremely long, repetitive outputs) were generated. As a result, the win rates were recorded as NaN.




The completion of the evaluation process required approximately 16,700 GPU-hours, including the results from models and downstream tasks not described in the paper.

Category | Dataset | queries | metric  
---|---|---|---  
Math | MATH | 5000 | Exact Match Accuracy  
GSM8K | 1319 | Exact Match Accuracy  
Coding | HumanEval | 164 | pass@1  
MBPP | 257 | pass@1  
Knowledge | BoolQ | 3270 | Exact Match Accuracy  
NaturalQuestions | 3610 | Lenient Matching Accuracy  
TruthfulQA | 817 | BLEU Accuracy  
Examination | MMLU | 14042 | Exact Match Accuracy  
MMLU-zh | 11582 | Exact Match Accuracy  
MMLU-jp | 14042 | Exact Match Accuracy  
Instruction-following | MT Bench | 160 | Total Score  
Alpaca Eval v2 | 805 | Win rate  
Table 3: The list of downstream tasks used to evaluate the fine-tuned models is shown. All tasks are supported by the OpenCompass library, and the evaluation metrics are consistent with those used in OpenCompass.