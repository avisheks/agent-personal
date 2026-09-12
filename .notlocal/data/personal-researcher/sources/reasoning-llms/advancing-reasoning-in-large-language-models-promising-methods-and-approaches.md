---
title: "Advancing Reasoning in Large Language Models: Promising Methods and Approaches"
source: "https://arxiv.org/html/2502.03671"
ingestedAt: "2026-05-28T19:28:51Z"
---
# Advancing Reasoning in Large Language Models: Promising Methods and Approaches

1st Avinash Patil  Juniper Networks Inc.   
Sunnyvale, USA   
patila@juniper.net   
ORCID: 0009-0002-6004-370X  2nd Aryan Jadon  Juniper Networks Inc.   
Sunnyvale, USA   
aryanj@juniper.net   
ORCID: 0000-0002-2991-9913 

###### Abstract

Large Language Models (LLMs) have succeeded remarkably in various natural language processing (NLP) tasks, yet their reasoning capabilities remain a fundamental challenge. While LLMs exhibit impressive fluency and factual recall, their ability to perform complex reasoning—spanning logical deduction, mathematical problem-solving, commonsense inference, and multi-step reasoning—often falls short of human expectations. This survey provides a comprehensive review of emerging techniques enhancing reasoning in LLMs. We categorize existing methods into key approaches, including prompting strategies (e.g., Chain-of-Thought reasoning, Self-Consistency, and Tree-of-Thought reasoning), architectural innovations (e.g., retrieval-augmented models, modular reasoning networks, and neuro-symbolic integration), and learning paradigms (e.g., fine-tuning with reasoning-specific datasets, reinforcement learning, and self-supervised reasoning objectives). Additionally, we explore evaluation frameworks used to assess reasoning in LLMs and highlight open challenges, such as hallucinations, robustness, and reasoning generalization across diverse tasks. By synthesizing recent advancements, this survey aims to provide insights into promising directions for future research and practical applications of reasoning-augmented LLMs.

###### Index Terms: 

Large Language Models (LLMs), Reasoning, Logical Deduction, Mathematical Problem-Solving, Commonsense Inference, Multi-Step Reasoning, Prompting Strategies, Chain-of-Thought Reasoning, Self-Consistency, Tree-of-Thought Reasoning, Retrieval-Augmented Models, Modular Reasoning Networks, Neuro-Symbolic Integration, Reinforcement Learning, Self-Supervised Learning, Hallucinations, AI Reasoning. 

##  I Introduction

Large Language Models (LLMs) have revolutionized the field of Natural Language Processing (NLP), enabling breakthroughs in machine translation, text generation, question-answering, and other complex linguistic tasks. Despite their remarkable fluency and knowledge retention, these models often struggle with systematic reasoning—an essential capability for tasks requiring logical inference, problem-solving, and decision-making [[1](https://arxiv.org/html/2502.03671v2#bib.bib1)]. While LLMs can generate plausible-sounding responses, they frequently exhibit reasoning errors, inconsistencies, and hallucinations, limiting their reliability in critical domains such as scientific discovery, law, and medicine [[2](https://arxiv.org/html/2502.03671v2#bib.bib2)] [[3](https://arxiv.org/html/2502.03671v2#bib.bib3)].

Reasoning in AI broadly encompasses multiple cognitive processes, including deductive, inductive, abductive, and commonsense reasoning [[4](https://arxiv.org/html/2502.03671v2#bib.bib4), [5](https://arxiv.org/html/2502.03671v2#bib.bib5), [6](https://arxiv.org/html/2502.03671v2#bib.bib6), [7](https://arxiv.org/html/2502.03671v2#bib.bib7), [8](https://arxiv.org/html/2502.03671v2#bib.bib8)]. Unlike retrieval-based knowledge synthesis, reasoning requires multi-step logical transformations, contextual generalization, and structured problem-solving. Classical AI approaches have addressed reasoning through rule-based symbolic systems [[9](https://arxiv.org/html/2502.03671v2#bib.bib9)] [[10](https://arxiv.org/html/2502.03671v2#bib.bib10)], yet integrating such structured reasoning with the data-driven paradigm of LLMs remains an ongoing challenge.

Recent research has explored diverse methodologies to enhance the reasoning abilities of LLMs. These approaches can categorized into three domains: (1) Prompting Strategies, such as Chain-of-Thought (CoT) reasoning [[11](https://arxiv.org/html/2502.03671v2#bib.bib11)], Self-Consistency [[12](https://arxiv.org/html/2502.03671v2#bib.bib12)], and Tree-of-Thought [[13](https://arxiv.org/html/2502.03671v2#bib.bib13)] methods, which leverage structured prompts to guide step-by-step reasoning; (2) Architectural Innovations, including retrieval-augmented models [[14](https://arxiv.org/html/2502.03671v2#bib.bib14)], neuro-symbolic hybrid frameworks [[15](https://arxiv.org/html/2502.03671v2#bib.bib15)], and modular reasoning architectures that integrate structured knowledge and logic [[16](https://arxiv.org/html/2502.03671v2#bib.bib16)]; and (3) Learning Paradigms, involving fine-tuning with specialized datasets [[17](https://arxiv.org/html/2502.03671v2#bib.bib17)], reinforcement learning for reasoning consistency [[18](https://arxiv.org/html/2502.03671v2#bib.bib18)], and self-supervised objectives that encourage logical generalization [[19](https://arxiv.org/html/2502.03671v2#bib.bib19)].

Among recent advancements, the newly released LLM DeepSeek-R1 [[18](https://arxiv.org/html/2502.03671v2#bib.bib18)] has demonstrated superior reasoning performance, particularly in complex domains such as mathematics and coding. By effectively simulating human-like analytical thinking, DeepSeek-R1 enhances multi-step reasoning in mathematical problem-solving, logical inference, and programming tasks, showcasing the potential of fine-tuned architectures and novel training paradigms to improve structured reasoning in LLMs. This survey systematically reviews these advancements in LLM reasoning, assessing their effectiveness, limitations, and applications. It covers evaluation benchmarks, key challenges like adversarial robustness, cross-domain generalization, and reasoning biases. By synthesizing recent progress, we provide a comprehensive overview of promising techniques and future research directions.

The paper is structured as follows: Section 2 covers the foundations of reasoning, while Section 3 explores prompt-based reasoning enhancements. Section 4 discusses architectural innovations, and Section 5 examines learning-based approaches. Section 6 focuses on evaluation and benchmarking, Section 7 highlights challenges and open research directions, and Section 8 concludes the paper.

##  II Foundations of Reasoning in AI and LLMs

###  II-A Definitions and Types of Reasoning

Reasoning is the cognitive process of deriving conclusions from premises or evidence. It can classified into the following types:

  * •

Deductive Reasoning: Drawing specific conclusions from general premises. If the premises are true, the conclusion must be true. This method is fundamental in formal logic and automated theorem proving.

  * •

Inductive Reasoning: Deriving general principles from specific examples or observations. This approach is common in machine learning for pattern recognition and forecasting.

  * •

Abductive Reasoning: Inferring the most likely explanation for a given set of observations, frequently used in diagnostics and hypothesis formation.

  * •

Commonsense Reasoning: Applying general world knowledge to infer reasonable conclusions is crucial for understanding implicit meanings in human communication.

  * •

Probabilistic Reasoning: Handling uncertainty in logical inference using probability theory, often implemented in Bayesian networks and Markov models.




###  II-B Classical AI Approaches to Reasoning

Traditional AI research has long focused on formal reasoning techniques incorporating structured knowledge representations. Some of the key classical approaches include [[9](https://arxiv.org/html/2502.03671v2#bib.bib9), [10](https://arxiv.org/html/2502.03671v2#bib.bib10)]:

  * •

Symbolic Logic: Formal rule-based systems that use first-order logic (FOL) and propositional logic to derive conclusions.

  * •

Rule-Based Systems: AI models that apply predefined rules to infer logical conclusions, used in expert systems and decision trees.

  * •

Knowledge Graphs: Structured representations of entities and their relationships, supporting reasoning through graph traversal and inference mechanisms.

  * •

Automated Theorem Proving (ATP): Algorithms designed to prove mathematical theorems using logical deduction, such as the resolution principle in propositional logic.

  * •

Bayesian Networks: Probabilistic graphical models that enable reasoning under uncertainty by representing dependencies between variables.




While these classical approaches provide strong logical foundations, they struggle with scalability and adaptability when applied to open-ended, unstructured problems such as natural language understanding.

###  II-C Reasoning in Large Language Models

Large Language Models (LLMs) such as GPT-4, PaLM, and LLaMA utilize deep learning architectures, primarily transformers, to process and generate human-like text. However, their reasoning capabilities differ significantly from traditional AI approaches [[4](https://arxiv.org/html/2502.03671v2#bib.bib4), [5](https://arxiv.org/html/2502.03671v2#bib.bib5), [6](https://arxiv.org/html/2502.03671v2#bib.bib6), [7](https://arxiv.org/html/2502.03671v2#bib.bib7), [8](https://arxiv.org/html/2502.03671v2#bib.bib8)]:

  * •

Statistical Learning vs. Symbolic Logic: Unlike symbolic AI, which follows explicit logical rules, LLMs learn probabilistic patterns in language data, making their reasoning implicit and non-deterministic.

  * •

Emergent Reasoning Abilities: Studies suggest that scaling LLMs improves their ability to perform multi-step reasoning tasks despite the lack of explicit logical constraints.

  * •

Contextual and Prompt-Driven Reasoning: LLMs rely heavily on context windows and external prompt engineering techniques (e.g., Chain-of-Thought prompting) to generate reasoned responses.




###  II-D Challenges of Reasoning in LLMs

Despite their progress, LLMs face several challenges when it comes to robust and reliable reasoning [[20](https://arxiv.org/html/2502.03671v2#bib.bib20), [21](https://arxiv.org/html/2502.03671v2#bib.bib21), [22](https://arxiv.org/html/2502.03671v2#bib.bib22)]:

  * •

Hallucinations: LLMs sometimes generate plausible but incorrect information, leading to unreliable reasoning.

  * •

Lack of Explicit Memory: Unlike knowledge graphs or rule-based systems, LLMs lack structured long-term memory, making reasoning consistency difficult.

  * •

Difficulty with Multi-Step Reasoning: Although techniques like Chain-of-Thought prompting help, LLMs often fail to follow multi-step logical structures correctly.

  * •

Bias and Interpretability Issues: Since LLMs train on vast text corpora, they inherit biases from data, which can influence reasoning outputs in unpredictable ways.

  * •

Limitations in Logical Deduction: While LLMs excel at recognizing language patterns, they struggle with formal logic, mathematical proofs, and systematically verifying conclusions.

  * •

Limited Generalization Across Domains: LLMs trained on diverse datasets still struggle with transferring reasoning skills across vastly different domains (e.g., legal reasoning vs. scientific inference).




###  II-E Bridging the Gap Between AI Reasoning and LLMs

To enhance reasoning in LLMs, recent research [[14](https://arxiv.org/html/2502.03671v2#bib.bib14), [15](https://arxiv.org/html/2502.03671v2#bib.bib15), [23](https://arxiv.org/html/2502.03671v2#bib.bib23), [18](https://arxiv.org/html/2502.03671v2#bib.bib18)] has explored hybrid models that integrate traditional reasoning techniques with deep learning. Key directions include :

  * •

Fine-Tuning with Structured Reasoning Data: Training LLMs on specialized datasets that explicitly focus on logical inference and mathematical problem-solving.

  * •

Retrieval-Augmented Reasoning: Enhancing LLMs with knowledge retrieval mechanisms, allowing them to ground their responses in external facts.

  * •

Neuro-Symbolic AI: Combining neural networks with symbolic reasoning frameworks to leverage the strengths of both approaches.

  * •

Self-Supervised and Reinforcement Learning Techniques: Encouraging models to refine their reasoning through iterative self-training and reward mechanisms.




These advancements aim to push LLMs toward more reliable, explainable, and human-like reasoning capabilities.

##  III Prompting-Based Reasoning Enhancement

Large Language Models (LLMs) demonstrate emergent reasoning through structured prompts, bypassing the need for fine-tuning [[2](https://arxiv.org/html/2502.03671v2#bib.bib2), [24](https://arxiv.org/html/2502.03671v2#bib.bib24)]. This section examines key prompting techniques, illustrated in Figure [1](https://arxiv.org/html/2502.03671v2#S3.F1 "Figure 1 ‣ III Prompting-Based Reasoning Enhancement ‣ Advancing Reasoning in Large Language Models: Promising Methods and Approaches") and summarized in Table [I](https://arxiv.org/html/2502.03671v2#S3.T1 "TABLE I ‣ III-D Program-aided Language Models \(PAL\) ‣ III Prompting-Based Reasoning Enhancement ‣ Advancing Reasoning in Large Language Models: Promising Methods and Approaches").

Figure 1: Approaches to Prompting-Based Reasoning Enhancement.

###  III-A Chain-of-Thought (CoT) Reasoning

Chain-of-Thought (CoT) reasoning is a prompting technique used in large language models (LLMs) to improve their ability to solve complex reasoning problems. It involves breaking down a problem into a series of intermediate steps, allowing the model to reason more effectively and arrive at accurate conclusions [[11](https://arxiv.org/html/2502.03671v2#bib.bib11)]. This technique has been particularly effective for complex mathematical problem-solving, logical reasoning, and commonsense inference.

  * •

Step-by-Step Reasoning: Instead of answering immediately, the model generates a sequence of logical steps to work through the problem, improving accuracy in multi-step problem-solving.

  * •

Intermediate Reasoning: The approach mimics human problem-solving by considering subproblems before reaching the final answer.

  * •

Performance Gains: Studies show that CoT prompting improves performance on arithmetic and logical tasks compared to standard prompting [[11](https://arxiv.org/html/2502.03671v2#bib.bib11)].

  * •

Limitations: While CoT enhances interpretability, its effectiveness depends on prompt design and model size. In some cases, models may still generate incorrect intermediate steps [[12](https://arxiv.org/html/2502.03671v2#bib.bib12)].




###  III-B Self-Consistency Prompting

Self-Consistency prompting is an advanced prompting technique that improves reasoning accuracy by generating multiple diverse reasoning paths and selecting the most consistent answer [[12](https://arxiv.org/html/2502.03671v2#bib.bib12)]. This method is useful in complex reasoning tasks where a single Chain-of-Thought (CoT) might be prone to errors. This technique reduces variability in responses and increases accuracy by aggregating outputs.

  * •

Multiple Reasoning Paths: Instead of generating a single step-by-step solution, the model produces multiple different reasoning chains.

  * •

Diverse Thought Processes: Each reasoning chain might follow a different logical approach, reducing biases in a single trajectory.

  * •

Majority Voting on Final Answer: The final response is determined based on the most frequently occurring correct answer across generated samples.




###  III-C Tree-of-Thought (ToT) Reasoning

Tree-of-Thought (ToT) reasoning is an advanced problem-solving framework that extends CoT reasoning by exploring multiple possible reasoning paths in a tree-like structure [[13](https://arxiv.org/html/2502.03671v2#bib.bib13)]. Instead of following a single linear reasoning path, ToT allows branching and evaluation at each step, leading to more robust and optimal solutions.

  * •

Structured Exploration: The model explores different paths in a tree-like structure, selecting the optimal reasoning route.

  * •

Decision Evaluation & Pruning: ToT reasoning is particularly effective in combinatorial and planning tasks.

  * •

Final Answer Selection: The best reasoning path is selected based on a scoring or majority selection process [[13](https://arxiv.org/html/2502.03671v2#bib.bib13)].




###  III-D Program-aided Language Models (PAL)

Program-Aided Language Models (PAL) is a technique that enhances a language model’s reasoning capabilities by allowing it to call external computational tools—such as Python or symbolic solvers—to perform calculations, execute logic-based steps, or verify solutions. Instead of relying purely on internal token-based reasoning, PAL leverages external code execution for improved accuracy and reliability [[25](https://arxiv.org/html/2502.03671v2#bib.bib25)].

  * •

Execution-Based Verification: The model generates reasoning steps in code format, which is executed to verify correctness.

  * •

Higher Accuracy in Mathematical Reasoning: PAL has demonstrated superior performance in tasks requiring precise calculations.

  * •

Dependence on External Tools: This approach requires integration with external computing environments, limiting its scalability [[25](https://arxiv.org/html/2502.03671v2#bib.bib25)].




Empirical studies indicate that CoT and self-consistency prompting significantly improve reasoning performance, particularly in structured domains such as mathematics and logic [[11](https://arxiv.org/html/2502.03671v2#bib.bib11), [12](https://arxiv.org/html/2502.03671v2#bib.bib12)].

TABLE I: Comparison of Chain-of-Thought (CoT), Self-Consistency CoT (SC-CoT), Tree-of-Thought (ToT), and Program-Aided Language Models (PAL)

##  IV Architectural Innovations for Enhanced Reasoning

While prompting-based techniques have improved the reasoning capabilities of Large Language Models (LLMs), architectural innovations play a crucial role in enhancing their ability to perform structured and complex reasoning. This section explores various model architectures and modifications to improve logical inference, multi-step reasoning, and knowledge integration.

###  IV-A Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is an AI framework that combines information retrieval with text generation. It enhances LLM reasoning by incorporating external knowledge sources. This approach improves the accuracy, relevance, and factual grounding of responses compared to relying solely on parametric memory[[14](https://arxiv.org/html/2502.03671v2#bib.bib14)].

  * •

Query Processing: The input query is processed and embedded into a vector space. The model searches for relevant documents using a retrieval system (e.g., dense passage retrieval, BM25). The retrieved documents are appended to the input.

  * •

Knowledge-Enhanced Reasoning: RAG-based models supplement their reasoning process based on both the query and retrieved information.

  * •

Reduction of Hallucinations: By grounding responses in external data, RAG helps mitigate hallucinations often observed in purely generative models [[26](https://arxiv.org/html/2502.03671v2#bib.bib26)].




###  IV-B Neuro-Symbolic Hybrid Models

Neuro-Symbolic Hybrid Models combine neural networks (which excel at pattern recognition and learning from data) with symbolic AI (which enables reasoning, logic, and explicit knowledge representation). This fusion aims to create more explainable, generalizable, and robust AI systems [[15](https://arxiv.org/html/2502.03671v2#bib.bib15)].

  * •

Integration of Logic and Learning: These models use neural networks to process unstructured text while employing symbolic logic for rule-based reasoning. Neural models extract features, while symbolic systems provide logical inference.

  * •

Enhanced Interpretability: Symbolic components improve transparency, making reasoning steps more explainable. Rule-based systems, knowledge graphs, and formal logic enable structured reasoning.




###  IV-C Memory-Augmented Neural Networks

Memory-Augmented Neural Networks (MANNs) are AI models that integrate external memory with neural networks, enabling them to store, retrieve, and manipulate information dynamically. MANNs can read from and write to an external memory module, making them more adaptable for reasoning consistency over long sequences, lifelong learning, and few-shot learning tasks [[21](https://arxiv.org/html/2502.03671v2#bib.bib21)].

  * •

Controller (Neural Network Core): A neural network (typically an RNN or Transformer) that processes inputs and manages interactions with memory, determining when and how to read/write data.

  * •

External Memory Storage: A structured memory component (e.g., a differentiable memory matrix or key-value store) that holds information over time. Unlike standard RNNs, which rely only on hidden states, MANNs explicitly retrieve and update memory.

  * •

Memory Access Mechanism: Read/write operations in memory-augmented neural networks are typically differentiable, enabling gradient-based learning. Addressing mechanisms include content-based addressing, which retrieves memory by assessing similarity to stored data, and location-based addressing, which accesses memory based on positional or sequential order.




###  IV-D Graph Neural Networks (GNNs) and Knowledge Graphs

Graph Neural Networks (GNNs) offer a structured framework for reasoning by explicitly representing entities and their relationships, enabling logical inference and multi-hop question-answering.

  * •

Structured Representation: Graph Neural Networks are neural models designed to operate on graph-structured data. Unlike traditional deep learning models (which work on grids like images or sequences like text), GNNs can model complex relationships between interconnected entities [[27](https://arxiv.org/html/2502.03671v2#bib.bib27)].

  * •

Reasoning over Knowledge Graphs: Knowledge Graphs represent facts as entities and relationships in a structured format, typically as a triple (subject, predicate, object). When GNNs are applied to Knowledge Graphs, they enable reasoning, inference, and discovery of hidden relationships.[[28](https://arxiv.org/html/2502.03671v2#bib.bib28)].

  * •

Improvements in Explainability: Knowledge graph-based reasoning enhances transparency by making inference paths explicit.




###  IV-E Tool-Use and API Augmentations

LLMs can be augmented with external tools and APIs to improve reasoning capabilities, leveraging specialized computational resources beyond language modeling [[29](https://arxiv.org/html/2502.03671v2#bib.bib29)].

  * •

Programmatic Reasoning: Models invoke external calculators, theorem solvers, or search engines to validate reasoning steps.

  * •

Dynamic Data Integration: As illustrated in Table [II](https://arxiv.org/html/2502.03671v2#S4.T2 "TABLE II ‣ IV-E Tool-Use and API Augmentations ‣ IV Architectural Innovations for Enhanced Reasoning ‣ Advancing Reasoning in Large Language Models: Promising Methods and Approaches"), APIs enable real-time access to updated knowledge, improving the factual accuracy of reasoning [[30](https://arxiv.org/html/2502.03671v2#bib.bib30)].

  * •

Limitations: Dependence on external services introduces latency and requires access control mechanisms.




TABLE II: Common API Types Used in AI Systems

Empirical results suggest that retrieval-augmented and neuro-symbolic models outperform standard transformer architectures in structured reasoning tasks [[14](https://arxiv.org/html/2502.03671v2#bib.bib14), [15](https://arxiv.org/html/2502.03671v2#bib.bib15)].

##  V Learning-Based Approaches for Reasoning

Beyond prompting and architectural innovations, learning-based approaches are critical in improving reasoning capabilities in Large Language Models (LLMs). These approaches involve training paradigms such as fine-tuning with reasoning-specific datasets, reinforcement learning for consistency, and self-supervised learning for logical inference. This section explores various learning-based methodologies that enhance the reasoning abilities of LLMs.

###  V-A Supervised Fine-Tuning on Reasoning-Specific Datasets

Fine-tuning LLMs on high-quality reasoning datasets allows models to improve their logical, mathematical, and commonsense reasoning capabilities.

  * •

Mathematical and Logical Reasoning: Fine-tuning on datasets such as MATH and GSM8K enhances mathematical problem-solving and logical inference skills [[31](https://arxiv.org/html/2502.03671v2#bib.bib31), [32](https://arxiv.org/html/2502.03671v2#bib.bib32)].

  * •

Commonsense and Causal Reasoning: Datasets like SWAG and Abductive NLI (aNLI) help models learn commonsense reasoning and abductive inference [[33](https://arxiv.org/html/2502.03671v2#bib.bib33), [6](https://arxiv.org/html/2502.03671v2#bib.bib6)].

  * •

Scientific and Multi-Hop Reasoning: Fine-tuning on datasets like ARC and HotpotQA improves multi-step reasoning and question-answering [[34](https://arxiv.org/html/2502.03671v2#bib.bib34), [35](https://arxiv.org/html/2502.03671v2#bib.bib35)].




While fine-tuning can significantly improve model performance, it requires careful dataset curation to prevent overfitting and ensure generalizability.

###  V-B Reinforcement Learning from Human Feedback

Methods such as Reinforcement Learning from Human Feedback (RLHF) train models to align their reasoning with human preferences [[36](https://arxiv.org/html/2502.03671v2#bib.bib36)]. A PPO-based RLHF training algorithm is Algorithm [1](https://arxiv.org/html/2502.03671v2#alg1 "Algorithm 1 ‣ V-B Reinforcement Learning from Human Feedback ‣ V Learning-Based Approaches for Reasoning ‣ Advancing Reasoning in Large Language Models: Promising Methods and Approaches").

  * •

Reward Models for Logical Consistency: RLHF optimizes model outputs based on human evaluators’ feedback, reducing errors in logical reasoning [[37](https://arxiv.org/html/2502.03671v2#bib.bib37)].

  * •

Reward Model (RM) Training: Human annotators assess multiple model outputs based on preference. A dedicated neural network, known as the Reward Model, is trained on these rankings to capture human preferences. The models generate and assess their reasoning steps, refining correct solutions through iterative learning [[17](https://arxiv.org/html/2502.03671v2#bib.bib17)].

  * •

Reinforcement Learning via Proximal Policy Optimization (PPO): PPO, a reinforcement learning algorithm, is used to optimize the model while preventing drastic deviations from its base performance [[18](https://arxiv.org/html/2502.03671v2#bib.bib18)].




Algorithm 1 RLHF Training Pipeline using PPO

1: Input: Pre-trained language model ℳℳ\mathcal{M}caligraphic_M, Supervised fine-tuning dataset 𝒟SFTsubscript𝒟SFT\mathcal{D}_{\text{SFT}}caligraphic_D start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT, Reward model dataset 𝒟RMsubscript𝒟RM\mathcal{D}_{\text{RM}}caligraphic_D start_POSTSUBSCRIPT RM end_POSTSUBSCRIPT, Learning rate α𝛼\alphaitalic_α, Temperature τ𝜏\tauitalic_τ 2: Output: RLHF-tuned model ℳRLHFsubscriptℳRLHF\mathcal{M}_{\text{RLHF}}caligraphic_M start_POSTSUBSCRIPT RLHF end_POSTSUBSCRIPT 3: 4: Step 1: Supervised Fine-Tuning (SFT) 5: Load pre-trained language model ℳℳ\mathcal{M}caligraphic_M 6: Load supervised fine-tuning dataset 𝒟SFTsubscript𝒟SFT\mathcal{D}_{\text{SFT}}caligraphic_D start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT 7: Train ℳℳ\mathcal{M}caligraphic_M on 𝒟SFTsubscript𝒟SFT\mathcal{D}_{\text{SFT}}caligraphic_D start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT using cross-entropy loss  8: Save fine-tuned model as ℳSFTsubscriptℳSFT\mathcal{M}_{\text{SFT}}caligraphic_M start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT 9: Step 2: Train Reward Model 10: Initialize reward model ℛℛ\mathcal{R}caligraphic_R 11: Load ranked preference dataset 𝒟RMsubscript𝒟RM\mathcal{D}_{\text{RM}}caligraphic_D start_POSTSUBSCRIPT RM end_POSTSUBSCRIPT 12: Train ℛℛ\mathcal{R}caligraphic_R to predict reward scores from human-ranked data  13: Save trained reward model as ℛtrainedsubscriptℛtrained\mathcal{R}_{\text{trained}}caligraphic_R start_POSTSUBSCRIPT trained end_POSTSUBSCRIPT 14: Step 3: Reinforcement Learning with PPO 15: Initialize PPO agent using ℳSFTsubscriptℳSFT\mathcal{M}_{\text{SFT}}caligraphic_M start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT 16: Set up PPO hyperparameters: batch size B𝐵Bitalic_B, policy update steps K𝐾Kitalic_K 17: for each training iteration do 18: Sample batch {xi}∈𝒟SFTsubscript𝑥𝑖subscript𝒟SFT\\{x_{i}\\}\in\mathcal{D}_{\text{SFT}}{ italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT } ∈ caligraphic_D start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT 19: Generate responses yi=ℳSFT⁢(xi)subscript𝑦𝑖subscriptℳSFTsubscript𝑥𝑖y_{i}=\mathcal{M}_{\text{SFT}}(x_{i})italic_y start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT = caligraphic_M start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT ( italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT ) 20: Compute rewards ri=ℛtrained⁢(yi)subscript𝑟𝑖subscriptℛtrainedsubscript𝑦𝑖r_{i}=\mathcal{R}_{\text{trained}}(y_{i})italic_r start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT = caligraphic_R start_POSTSUBSCRIPT trained end_POSTSUBSCRIPT ( italic_y start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT ) 21: Update policy πθsubscript𝜋𝜃\pi_{\theta}italic_π start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT using PPO objective:  ℒPPO=𝔼t⁢[min⁡(rt⁢(θ)⁢At,clip⁢(rt⁢(θ),1−ϵ,1+ϵ)⁢At)]subscriptℒPPOsubscript𝔼𝑡delimited-[]subscript𝑟𝑡𝜃subscript𝐴𝑡clipsubscript𝑟𝑡𝜃1italic-ϵ1italic-ϵsubscript𝐴𝑡\mathcal{L}_{\text{PPO}}=\mathbb{E}_{t}\left[\min\left(r_{t}(\theta)A_{t},% \text{clip}(r_{t}(\theta),1-\epsilon,1+\epsilon)A_{t}\right)\right]caligraphic_L start_POSTSUBSCRIPT PPO end_POSTSUBSCRIPT = blackboard_E start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT [ roman_min ( italic_r start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ( italic_θ ) italic_A start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , clip ( italic_r start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ( italic_θ ) , 1 - italic_ϵ , 1 + italic_ϵ ) italic_A start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) ] 22: Perform gradient updates on ℳSFTsubscriptℳSFT\mathcal{M}_{\text{SFT}}caligraphic_M start_POSTSUBSCRIPT SFT end_POSTSUBSCRIPT 23: end for 24: Save final RLHF-trained model as ℳRLHFsubscriptℳRLHF\mathcal{M}_{\text{RLHF}}caligraphic_M start_POSTSUBSCRIPT RLHF end_POSTSUBSCRIPT

###  V-C Self-Supervised and Contrastive Learning for Reasoning

Self-supervised learning (SSL) and contrastive learning (CL) have gained traction as effective ways to train large-scale language models for reasoning tasks. Unlike supervised learning, which relies on human-labeled data, SSL and CL leverage inherent structures in data to create useful representations and improve reasoning capabilities [[19](https://arxiv.org/html/2502.03671v2#bib.bib19)].

  * •

Contrastive Learning for Logical Inference: By training models to distinguish between valid and invalid reasoning chains, contrastive learning improves logical consistency [[38](https://arxiv.org/html/2502.03671v2#bib.bib38)]. Contrastive learning optimizes a contrastive loss, such as InfoNCE (Noise Contrastive Estimation) or Triplet Loss, which encourages correct reasoning pairs to have higher similarity scores. The InfoNCE loss function is defined as:

| L=−∑ilog⁡exp⁡(sim⁢(xi,xi+)/τ)∑jexp⁡(sim⁢(xi,xj)/τ)𝐿subscript𝑖simsubscript𝑥𝑖superscriptsubscript𝑥𝑖𝜏subscript𝑗simsubscript𝑥𝑖subscript𝑥𝑗𝜏L=-\sum_{i}\log\frac{\exp\left(\text{sim}(x_{i},x_{i}^{+})/\tau\right)}{\sum_{% j}\exp\left(\text{sim}(x_{i},x_{j})/\tau\right)}italic_L = - ∑ start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT roman_log divide start_ARG roman_exp ( sim ( italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT start_POSTSUPERSCRIPT + end_POSTSUPERSCRIPT ) / italic_τ ) end_ARG start_ARG ∑ start_POSTSUBSCRIPT italic_j end_POSTSUBSCRIPT roman_exp ( sim ( italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT italic_j end_POSTSUBSCRIPT ) / italic_τ ) end_ARG |   
---|---|---  
  
where:

    * –

xisubscript𝑥𝑖x_{i}italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT is the anchor sample,

    * –

xi+superscriptsubscript𝑥𝑖x_{i}^{+}italic_x start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT start_POSTSUPERSCRIPT + end_POSTSUPERSCRIPT is the positive (similar) sample,

    * –

xjsubscript𝑥𝑗x_{j}italic_x start_POSTSUBSCRIPT italic_j end_POSTSUBSCRIPT represents all samples in the denominator, including both positive and negative samples,

    * –

sim⁢(⋅,⋅)sim⋅⋅\text{sim}(\cdot,\cdot)sim ( ⋅ , ⋅ ) denotes a similarity function (e.g., cosine similarity),

    * –

τ𝜏\tauitalic_τ is the temperature parameter.

  * •

Self-Training with Synthetic Data: Models generate synthetic reasoning paths and verify their correctness, iteratively refining their reasoning abilities [[17](https://arxiv.org/html/2502.03671v2#bib.bib17)].

  * •

Zero-Shot and Few-Shot Reasoning Improvement: Self-supervised learning enhances a model’s ability to generalize to novel reasoning tasks by enabling it to extract abstract reasoning patterns directly from raw data [[19](https://arxiv.org/html/2502.03671v2#bib.bib19)].




###  V-D Automated Verifiers and Critic Models

To further enhance reasoning accuracy, LLMs can be paired with automated verifiers that critically assess their outputs [[39](https://arxiv.org/html/2502.03671v2#bib.bib39)].

  * •

Secondary Verification Models: A separate model evaluates the reasoning output of an LLM, filtering out incorrect inferences.

  * •

Formal Proof Checking: Integration with theorem provers allows models to verify logical deductions rigorously [[40](https://arxiv.org/html/2502.03671v2#bib.bib40)].

  * •

Limitations: Automated verification remains challenging due to the difficulty of formalizing natural language reasoning.




##  VI Evaluation and Benchmarking of Reasoning in LLMs

Assessing the reasoning capabilities of Large Language Models (LLMs) requires systematic evaluation using standardized benchmarks and performance metrics. This section explores various evaluation methodologies, including reasoning benchmarks, key performance metrics, comparative analysis with human reasoning, and limitations of current evaluation strategies.

###  VI-A Popular Reasoning Benchmarks

Several benchmarks have been developed to assess different aspects of reasoning in LLMs, ranging from mathematical problem-solving to logical inference and commonsense reasoning.

  * •

ARC (AI2 Reasoning Challenge) – Measures commonsense and logical inference abilities by requiring multi-step reasoning across different knowledge domains [[34](https://arxiv.org/html/2502.03671v2#bib.bib34)].

  * •

LogiQA – A dataset evaluating logical reasoning skills, particularly in deductive and abductive reasoning scenarios [[41](https://arxiv.org/html/2502.03671v2#bib.bib41)].

  * •

GSM8K – A dataset focused on grade-school mathematical reasoning problems, evaluating multi-step arithmetic reasoning capabilities [[31](https://arxiv.org/html/2502.03671v2#bib.bib31)].

  * •

MATH – A benchmark designed to test models on high-school and competition-level mathematics, assessing formal mathematical reasoning [[32](https://arxiv.org/html/2502.03671v2#bib.bib32)].

  * •

BIG-Bench – A broad dataset covering a variety of reasoning tasks, including logical reasoning, abstraction, and multi-hop inference [[42](https://arxiv.org/html/2502.03671v2#bib.bib42)].

  * •

ProofWriter – Evaluates the model’s ability to perform automated theorem proving and logical deduction [[39](https://arxiv.org/html/2502.03671v2#bib.bib39)].

  * •

HotpotQA – A dataset focused on multi-hop question-answering requiring models to combine information from multiple sources for reasoning [[35](https://arxiv.org/html/2502.03671v2#bib.bib35)].

  * •

HumanEval – Evaluates the code-generating abilities of LLMs. It evaluates models’ capacity to understand programming-related tasks and generate syntactically correct and functionally accurate code according to the provided specifications. [[43](https://arxiv.org/html/2502.03671v2#bib.bib43)]

  * •

ANLI (Adversarial NLI) – Designed to test models on natural language inference through adversarially generated reasoning tasks [[44](https://arxiv.org/html/2502.03671v2#bib.bib44)].

  * •

HellaSwag – A benchmark designed to test commonsense natural language inference. It requires the model to predict the most likely ending of a sentence. [[33](https://arxiv.org/html/2502.03671v2#bib.bib33)].

  * •

Measuring Massive Multitask Language Understanding (MMLU) – Evaluates general knowledge and problem-solving abilities across 57 subjects, including elementary mathematics, US history, computer science, and law. [[45](https://arxiv.org/html/2502.03671v2#bib.bib45)].




###  VI-B Metrics for Measuring Reasoning Performance

Evaluating reasoning in LLMs involves multiple performance metrics tailored to different reasoning tasks.

  * •

Accuracy: Measures the correctness of model responses, often evaluated using Exact Match (EM) and F1-score, particularly in mathematical and logical reasoning tasks [[32](https://arxiv.org/html/2502.03671v2#bib.bib32)].

  * •

Logical Consistency: Assesses whether a model’s reasoning follows coherent logical steps across multiple queries. Often evaluated using theorem-proving datasets such as ProofWriter [[39](https://arxiv.org/html/2502.03671v2#bib.bib39)].

  * •

Explainability and Interpretability: Evaluates the transparency of reasoning steps, especially in Chain-of-Thought (CoT) models, by assessing the faithfulness of intermediate steps to the final answer [[11](https://arxiv.org/html/2502.03671v2#bib.bib11)].

  * •

Self-Consistency: Measures reasoning reliability by generating multiple independent responses to the same query and assessing agreement among outputs [[12](https://arxiv.org/html/2502.03671v2#bib.bib12)].

  * •

Multi-Hop Reasoning Score: Used in datasets like HotpotQA to assess the model’s ability to integrate multiple pieces of evidence in complex reasoning tasks [[35](https://arxiv.org/html/2502.03671v2#bib.bib35)].

  * •

Adversarial Robustness: Tests the model’s ability to maintain reasoning accuracy under adversarial perturbations, as evaluated in the ANLI dataset [[44](https://arxiv.org/html/2502.03671v2#bib.bib44)].

  * •

Faithfulness and Verifiability: Measures whether the model-generated reasoning steps can be independently verified and logically aligned with the final answer [[40](https://arxiv.org/html/2502.03671v2#bib.bib40)].

  * •

Confidence Calibration: Evaluates whether the model’s confidence in its predictions correlates with correctness, commonly measured using log-likelihood scores and Brier Score [[46](https://arxiv.org/html/2502.03671v2#bib.bib46)].

  * •

Reasoning Generalization: Assesses how well the model performs on out-of-distribution (OOD) reasoning tasks, testing adaptability beyond its training data [[47](https://arxiv.org/html/2502.03671v2#bib.bib47)].




##  VII Challenges and Open Research Directions

Despite significant advancements in enhancing the reasoning capabilities of Large Language Models (LLMs), several challenges persist. These limitations hinder their reliability, robustness, and applicability in high-stakes domains. This section discusses key challenges and proposes open research directions to address them.

###  VII-A Hallucinations and Misinformation

One of the critical challenges in LLM reasoning is the generation of hallucinated or factually incorrect information [[20](https://arxiv.org/html/2502.03671v2#bib.bib20)].

  * •

Unverified Reasoning Steps: LLMs sometimes generate plausible but incorrect reasoning chains, leading to logical inconsistencies [[48](https://arxiv.org/html/2502.03671v2#bib.bib48)].

  * •

Fact-Checking Mechanisms: Existing fact-checking techniques fail to filter misinformation in multi-step reasoning tasks [[30](https://arxiv.org/html/2502.03671v2#bib.bib30)].

  * •

Open Research Direction: Developing automated verifiers and integrating LLMs with structured databases to improve factual accuracy.




###  VII-B Generalization Across Domains

LLMs often struggle to generalize reasoning capabilities across different domains, limiting their adaptability to novel scenarios [[49](https://arxiv.org/html/2502.03671v2#bib.bib49)].

  * •

Domain-Specific Overfitting: Fine-tuning on specific reasoning datasets may improve performance in targeted tasks but hinders adaptability to unseen domains [[32](https://arxiv.org/html/2502.03671v2#bib.bib32)].

  * •

Cross-Domain Transfer Learning: Current transfer learning approaches have limitations in maintaining reasoning coherence across diverse contexts [[19](https://arxiv.org/html/2502.03671v2#bib.bib19)].

  * •

Open Research Direction: Investigating meta-learning and continual learning strategies for cross-domain generalization.




###  VII-C Robustness to Adversarial Attacks

LLMs are vulnerable to adversarial perturbations that exploit reasoning weaknesses, leading to incorrect or misleading outputs [[44](https://arxiv.org/html/2502.03671v2#bib.bib44)].

  * •

Sensitivity to Input Variations: Small modifications in prompts can lead to significantly different reasoning outputs, impacting reliability.

  * •

Adversarial Robustness Testing: Existing benchmarks do not sufficiently evaluate LLMs against adversarial reasoning challenges [[27](https://arxiv.org/html/2502.03671v2#bib.bib27)].

  * •

Open Research Direction: Developing robust adversarial training techniques to improve resistance to input manipulations.




###  VII-D Integrating Symbolic and Neural Reasoning

LLMs rely on statistical pattern recognition rather than formal logical reasoning, leading to errors in complex inferencing tasks [[15](https://arxiv.org/html/2502.03671v2#bib.bib15)].

  * •

Limitations of Purely Neural Approaches: LLMs struggle with structured logic, formal proofs, and abstract symbolic reasoning [[40](https://arxiv.org/html/2502.03671v2#bib.bib40)].

  * •

Neuro-Symbolic AI: Combining neural networks with symbolic reasoning frameworks enhances logical consistency and interpretability [[15](https://arxiv.org/html/2502.03671v2#bib.bib15)].

  * •

Open Research Direction: Advancing hybrid neuro-symbolic architectures for reasoning-augmented AI models.




##  VIII Conclusion

Advancing reasoning in Large Language Models (LLMs) is a key milestone in AI development. Despite improvements in prompting, architecture, and learning-based methods, challenges remain in logical consistency, generalization, robustness, and interpretability. This survey reviews key approaches to enhancing LLM reasoning, categorized into prompting techniques, architectural innovations, and learning-driven strategies.

###  VIII-A Summary of Key Findings

The key takeaways from this survey can be summarized as follows:

  * •

Prompting Strategies: Techniques such as Chain-of-Thought (CoT) prompting, Self-Consistency, and Tree-of-Thought (ToT) reasoning have shown significant improvements in structured problem-solving, logical inference, and multi-step reasoning [[11](https://arxiv.org/html/2502.03671v2#bib.bib11), [12](https://arxiv.org/html/2502.03671v2#bib.bib12), [13](https://arxiv.org/html/2502.03671v2#bib.bib13)].

  * •

Architectural Innovations: Enhancements such as Retrieval-Augmented Generation (RAG), Neuro-Symbolic AI, Memory-Augmented Models, and Graph Neural Networks (GNNs) contribute to better structured and explainable reasoning [[14](https://arxiv.org/html/2502.03671v2#bib.bib14), [15](https://arxiv.org/html/2502.03671v2#bib.bib15)].

  * •

Learning-Based Approaches: Fine-tuning on reasoning-specific datasets, Reinforcement Learning from Human Feedback (RLHF), self-supervised learning, and automated verifiers improve logical consistency and generalization [[32](https://arxiv.org/html/2502.03671v2#bib.bib32), [37](https://arxiv.org/html/2502.03671v2#bib.bib37), [17](https://arxiv.org/html/2502.03671v2#bib.bib17)].

  * •

Evaluation and Benchmarking: Current benchmarks such as GSM8K, MATH, LogiQA, and ARC provide valuable insights into LLM reasoning capabilities, but existing evaluation methodologies require improvements in adversarial robustness and dynamic reasoning assessment [[31](https://arxiv.org/html/2502.03671v2#bib.bib31), [32](https://arxiv.org/html/2502.03671v2#bib.bib32), [41](https://arxiv.org/html/2502.03671v2#bib.bib41)].

  * •

Challenges and Open Research Directions: Key challenges include hallucinations, reasoning generalization, adversarial robustness, computational efficiency, ethical considerations, and the need for explainable reasoning models [[20](https://arxiv.org/html/2502.03671v2#bib.bib20), [49](https://arxiv.org/html/2502.03671v2#bib.bib49), [15](https://arxiv.org/html/2502.03671v2#bib.bib15)].




###  VIII-B Final Thoughts

The future of AI reasoning depends on developing models that generate fluent text while ensuring robust, verifiable, and adaptable reasoning across domains. Advancements in prompting, architecture, and learning can bring LLMs closer to human-like reasoning. However, addressing challenges requires collaboration among AI researchers, cognitive scientists, ethicists, and domain experts. The goal is to create AI systems that reason accurately, ethically, and transparently for safer real-world deployment.

##  IX Acknowledgments

We thank the research community for their contributions to reasoning in LLMs and developing benchmarking datasets. This survey has been informed by a wide range of studies, and we acknowledge the valuable work that has advanced the field.

## References

  * [1] Z. Wu, L. Qiu, A. Ross, E. Akyürek, B. Chen, B. Wang, N. Kim, J. Andreas, and Y. Kim, “Reasoning or reciting? exploring the capabilities and limitations of language models through counterfactual tasks,” in _Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)_ , 2024, pp. 1819–1862. 
  * [2] T. Brown _et al._ , “Language models are few-shot learners,” _Advances in Neural Information Processing Systems_ , 2020. 
  * [3] T. Kojima, S. S. Gu, M. Reid, Y. Matsuo, and Y. Iwasawa, “Large language models are zero-shot reasoners,” _Advances in neural information processing systems_ , vol. 35, pp. 22 199–22 213, 2022. 
  * [4] P. Clark, O. Tafjord, and K. Richardson, “Transformers as soft reasoners over language,” in _Proceedings of the Twenty-Ninth International Conference on International Joint Conferences on Artificial Intelligence_ , 2021, pp. 3882–3890. 
  * [5] Z. Yang, L. Dong, X. Du, H. Cheng, E. Cambria, X. Liu, J. Gao, and F. Wei, “Language models as inductive reasoners,” in _Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers)_ , 2024, pp. 209–225. 
  * [6] C. Bhagavatula, R. L. Bras, C. Malaviya, K. Sakaguchi, A. Holtzman, H. Rashkin, D. Downey, S. W.-t. Yih, and Y. Choi, “Abductive commonsense reasoning,” _arXiv preprint arXiv:1908.05739_ , 2019. 
  * [7] X. Zhou, Y. Zhang, L. Cui, and D. Huang, “Evaluating commonsense in pre-trained language models,” in _Proceedings of the AAAI Conference on Artificial Intelligence_ , vol. 34, no. 05, 2020, pp. 9733–9740. 
  * [8] Q. Liu, H. Jiang, A. Evdokimov, Z.-H. Ling, X. Zhu, S. Wei, and Y. Hu, “Probabilistic reasoning via deep learning: Neural association models,” _arXiv preprint arXiv:1603.07704_ , 2016. 
  * [9] R. R. Yager, “Approximate reasoning as a basis for rule-based expert systems,” _IEEE Transactions on Systems, Man, and Cybernetics_ , no. 4, pp. 636–643, 1984. 
  * [10] R. Sun, “Robust reasoning: integrating rule-based and similarity-based reasoning,” _Artificial Intelligence_ , vol. 75, no. 2, pp. 241–295, 1995. 
  * [11] J. Wei, X. Wang, D. Schuurmans, M. Bosma, F. Xia, E. Chi, Q. V. Le, D. Zhou _et al._ , “Chain-of-thought prompting elicits reasoning in large language models,” _Advances in neural information processing systems_ , vol. 35, pp. 24 824–24 837, 2022. 
  * [12] X. Wang _et al._ , “Self-consistency improves chain of thought reasoning in language models,” _arXiv preprint arXiv:2203.11171_ , 2022. 
  * [13] S. Yao, D. Yu, J. Zhao, I. Shafran, T. Griffiths, Y. Cao, and K. Narasimhan, “Tree of thoughts: Deliberate problem solving with large language models,” _Advances in Neural Information Processing Systems_ , vol. 36, 2024. 
  * [14] P. Lewis _et al._ , “Retrieval-augmented generation for knowledge-intensive nlp tasks,” _Advances in Neural Information Processing Systems_ , 2020. 
  * [15] A. d. Garcez and L. C. Lamb, “Neurosymbolic ai: The 3 rd wave,” _Artificial Intelligence Review_ , vol. 56, no. 11, pp. 12 387–12 406, 2023. 
  * [16] A. Santoro, D. Raposo, D. G. Barrett, M. Malinowski, R. Pascanu, P. Battaglia, and T. Lillicrap, “A simple neural network module for relational reasoning,” in _Advances in Neural Information Processing Systems_ , I. Guyon, U. V. Luxburg, S. Bengio, H. Wallach, R. Fergus, S. Vishwanathan, and R. Garnett, Eds., vol. 30. Curran Associates, Inc., 2017. 
  * [17] E. Zelikman, Y. Wu, J. Mu, and N. Goodman, “Star: Bootstrapping reasoning with reasoning,” _Advances in Neural Information Processing Systems_ , vol. 35, pp. 15 476–15 488, 2022. 
  * [18] D. Guo, D. Yang, H. Zhang, J. Song, R. Zhang, R. Xu, Q. Zhu, L. Li, Z. Shao, P. Wang _et al._ , “Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning,” _arXiv preprint arXiv:2501.12948_ , 2025. 
  * [19] A. Talmor, O. Tafjord, P. Clark, Y. Goldberg, and J. Berant, “Leap-of-thought: Teaching pre-trained models to systematically reason over implicit knowledge,” _Advances in Neural Information Processing Systems_ , vol. 33, pp. 20 227–20 237, 2020. 
  * [20] L. Huang, W. Yu, W. Ma, W. Zhong, Z. Feng, H. Wang, Q. Chen, W. Peng, X. Feng, B. Qin _et al._ , “A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions,” _ACM Transactions on Information Systems_ , 2024. 
  * [21] W. Wang, L. Dong, H. Cheng, X. Liu, X. Yan, J. Gao, and F. Wei, “Augmenting language models with long-term memory,” _Advances in Neural Information Processing Systems_ , vol. 36, 2024. 
  * [22] Z. C. Lipton, “The mythos of model interpretability: In machine learning, the concept of interpretability is both important and slippery.” _Queue_ , vol. 16, no. 3, pp. 31–57, 2018. 
  * [23] A. Kumar, V. Zhuang, R. Agarwal, Y. Su, J. D. Co-Reyes, A. Singh, K. Baumli, S. Iqbal, C. Bishop, R. Roelofs _et al._ , “Training language models to self-correct via reinforcement learning,” _arXiv preprint arXiv:2409.12917_ , 2024. 
  * [24] J. Wei _et al._ , “Emergent abilities of large language models,” _arXiv preprint arXiv:2206.07682_ , 2022. 
  * [25] L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig, “Pal: Program-aided language models,” in _International Conference on Machine Learning_. PMLR, 2023, pp. 10 764–10 799. 
  * [26] K. Shuster, S. Poff, M. Chen, D. Kiela, and J. Weston, “Retrieval augmentation reduces hallucination in conversation,” in _Findings of the Association for Computational Linguistics: EMNLP 2021_ , 2021, pp. 3784–3803. 
  * [27] S. Ji, S. Pan, E. Cambria, P. Marttinen, and S. Y. Philip, “A survey on knowledge graphs: Representation, acquisition, and applications,” _IEEE transactions on neural networks and learning systems_ , vol. 33, no. 2, pp. 494–514, 2021. 
  * [28] W. L. Hamilton _et al._ , “Inductive representation learning on large graphs,” _Advances in Neural Information Processing Systems_ , 2017. 
  * [29] T. Schick, J. Dwivedi-Yu, R. Dessì, R. Raileanu, M. Lomeli, E. Hambro, L. Zettlemoyer, N. Cancedda, and T. Scialom, “Toolformer: Language models can teach themselves to use tools,” _Advances in Neural Information Processing Systems_ , vol. 36, pp. 68 539–68 551, 2023. 
  * [30] G. Mialon, R. Dessi, M. Lomeli, C. Nalmpantis, R. Pasunuru, R. Raileanu, B. Roziere, T. Schick, J. Dwivedi-Yu, A. Celikyilmaz, E. Grave, Y. LeCun, and T. Scialom, “Augmented language models: a survey,” _Transactions on Machine Learning Research_ , 2023, survey Certification. [Online]. Available: <https://openreview.net/forum?id=jh7wH2AzKK>
  * [31] K. Cobbe _et al._ , “Training verifiers to solve math word problems,” _arXiv preprint arXiv:2110.14168_ , 2021. 
  * [32] D. Hendrycks, C. Burns, S. Kadavath, A. Arora, S. Basart, E. Tang, D. Song, and J. Steinhardt, “Measuring mathematical problem solving with the math dataset,” _Sort_ , vol. 2, no. 4, pp. 0–6, 2021. 
  * [33] R. Zellers, Y. Bisk, R. Schwartz, and Y. Choi, “Swag: A large-scale adversarial dataset for grounded commonsense inference,” _arXiv preprint arXiv:1808.05326_ , 2018. 
  * [34] P. Clark, I. Cowhey, O. Etzioni, T. Khot, A. Sabharwal, C. Schoenick, and O. Tafjord, “Think you have solved question answering? try arc, the ai2 reasoning challenge,” _arXiv preprint arXiv:1803.05457_ , 2018. 
  * [35] Z. Yang, P. Qi, S. Zhang, Y. Bengio, W. Cohen, R. Salakhutdinov, and C. D. Manning, “Hotpotqa: A dataset for diverse, explainable multi-hop question answering,” in _Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing_ , 2018, pp. 2369–2380. 
  * [36] J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Altenschmidt, S. Altman, S. Anadkat _et al._ , “Gpt-4 technical report,” _arXiv preprint arXiv:2303.08774_ , 2023. 
  * [37] L. Ouyang, J. Wu, X. Jiang, D. Almeida, C. Wainwright, P. Mishkin, C. Zhang, S. Agarwal, K. Slama, A. Ray _et al._ , “Training language models to follow instructions with human feedback,” _Advances in neural information processing systems_ , vol. 35, pp. 27 730–27 744, 2022. 
  * [38] C. Durkan, I. Murray, and G. Papamakarios, “On contrastive learning for likelihood-free inference,” in _International conference on machine learning_. PMLR, 2020, pp. 2771–2781. 
  * [39] O. Tafjord, B. Dalvi, and P. Clark, “Proofwriter: Generating implications, proofs, and abductive statements over natural language,” in _Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021_ , 2021, pp. 3621–3634. 
  * [40] E. First, M. N. Rabe, T. Ringer, and Y. Brun, “Baldur: Whole-proof generation and repair with large language models,” in _Proceedings of the 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering_ , 2023, pp. 1229–1241. 
  * [41] J. Liu, L. Cui, H. Liu, D. Huang, Y. Wang, and Y. Zhang, “Logiqa: a challenge dataset for machine reading comprehension with logical reasoning,” in _Proceedings of the Twenty-Ninth International Conference on International Joint Conferences on Artificial Intelligence_ , 2021, pp. 3622–3628. 
  * [42] A. Srivastava _et al._ , “Beyond the imitation game: Quantifying and extrapolating the capabilities of language models,” _arXiv preprint arXiv:2206.04615_ , 2022. 
  * [43] M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. D. O. Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman _et al._ , “Evaluating large language models trained on code,” _arXiv preprint arXiv:2107.03374_ , 2021. 
  * [44] Y. Nie, A. Williams, E. Dinan, M. Bansal, J. Weston, and D. Kiela, “Adversarial nli: A new benchmark for natural language understanding,” in _Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics_. Association for Computational Linguistics, 2020. 
  * [45] D. Hendrycks, C. Burns, S. Basart, A. Zou, M. Mazeika, D. Song, and J. Steinhardt, “Measuring massive multitask language understanding,” _arXiv preprint arXiv:2009.03300_ , 2020. 
  * [46] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern neural networks,” in _International Conference on Machine Learning (ICML)_ , 2017, pp. 1321–1330. 
  * [47] B. Lake and M. Baroni, “Generalization without systematicity: On the compositional skills of sequence-to-sequence recurrent networks,” in _International conference on machine learning_. PMLR, 2018, pp. 2873–2882. 
  * [48] M. Mitchell and D. C. Krakauer, “The debate over understanding in ai’s large language models,” _Proceedings of the National Academy of Sciences_ , vol. 120, no. 13, p. e2215907120, 2023. 
  * [49] R. Bommasani, D. A. Hudson, E. Adeli, R. Altman, S. Arora, S. von Arx, M. S. Bernstein, J. Bohg, A. Bosselut, E. Brunskill _et al._ , “On the opportunities and risks of foundation models,” _arXiv preprint arXiv:2108.07258_ , 2021.