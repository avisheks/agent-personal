---
title: "A Tutorial on LLM Reasoning: Relevant Methods behind ChatGPT o1"
source: "https://arxiv.org/html/2502.10867v1"
ingestedAt: "2026-05-28T19:52:58Z"
---
##  1 Background

OpenAI has recently unveiled ChatGPT o1 [[17](https://arxiv.org/html/2502.10867v1#bib.bib17)], a groundbreaking Large Language Model (LLM) that represents a giant leap forward in strong AI. Trained using reinforcement learning techniques, o1 excels in complex reasoning tasks by explicitly embedding a _native_ “Chain-of-Thought” (NCoT) process, which allows it to “deep think” through step-by-step reasoning before generating responses. The model is reported to be five times more proficient in math and coding compared to the previous ChatGPT 4o, specifically displaying exceptional performance across various domains: it ranks in the 89th percentile for competitive programming, places among the top 500 students in a prestigious US math olympiad qualifier, and surpasses human PhD-level accuracy in physics, biology, and chemistry benchmarks. A key innovation of o1 is that it allows spending more time reasoning during the inference process, marking a shift from fast, direct responses to slow, deliberate, multi-step inference-time computation (Fig. [1](https://arxiv.org/html/2502.10867v1#S0.F1 "Figure 1 ‣ A Tutorial on LLM Reasoning: Relevant Methods behind ChatGPT o1")).

Interestingly, in human cognition, two correlated yet distinct modes of cognitive processing are presented to guide human decision-making and behaviours [[8](https://arxiv.org/html/2502.10867v1#bib.bib8)], each of which has partially distinction brain circuits and neural pathways ( Fig. [2](https://arxiv.org/html/2502.10867v1#S1.F2 "Figure 2 ‣ 1 Background ‣ A Tutorial on LLM Reasoning: Relevant Methods behind ChatGPT o1") and also see [[28](https://arxiv.org/html/2502.10867v1#bib.bib28)]). System 1 thinking is fast, automatic, and intuitive, operating effortlessly and often unconsciously. It relies on neural pathways that enable rapid processing, especially in situations needing quick reactions or when cognitive resources are constrained. System 2 thinking is deliberate, effortful, and conscious, involving focused attention and analytical reasoning. It processes information more slowly and is used for complex problem-solving, logical reasoning, and decision-making tasks. o1 is an exciting development for AI, as LLMs can now not only generate rapid responses using learned patterns but, more significantly, simulate complex reasoning processes through mechanisms like chain of thought or other forms of search, similar to how humans engage in deeper, step-by-step thinking.

(a) System 1 nonconscious control.

(b) System 2 conscious control.

Figure 2: An analogy between human cognition and LLMs. (a) and (b) human actions controlled consciously or unconsciously rely on partially distinct brain circuits. (a) Unconscious control in humans is maintained by a few specialised brain regions, such as the anterior insula and the presupplementary motor area (pre-SMA). (b) while voluntary control engages a broader network, activating many regions within the parietal and prefrontal lobes [[28](https://arxiv.org/html/2502.10867v1#bib.bib28)]. Unconscious control is typically fast and instinctive, often driven by automatic processes, whereas conscious control tends to involve more deliberate, computational, and in-depth thinking, allowing for careful reflection and thorough analysis. 

ChatGPT o1’s improved reasoning skills have many implications for multiple fields, including science, coding, and mathematics. In coding competitions, a specialised version of o1 achieved impressive results, scoring in the 49th percentile in the 2024 International Olympiad in Informatics and outperforming 93% of human competitors in simulated Codeforces contests. Beyond its technical capabilities, o1 also represents progress in AI safety and alignment. The model’s chain of thought reasoning provides new opportunities for integrating human values and principles, resulting in improved performance on safety evaluations and jailbreak tests.

The idea of chain of thought reasoning and step-by-step thinking in Large Language Models (LLMs) is not new. Previous research has shown that simply adding instructions like “describe your reasoning in steps” or “explain your answer step by step” to the input questions or providing few shot examples can trigger LLMs to generate intermediate reasoning steps (as illustrated in Fig. [1](https://arxiv.org/html/2502.10867v1#S0.F1 "Figure 1 ‣ A Tutorial on LLM Reasoning: Relevant Methods behind ChatGPT o1")) and subsequently improve problem-solving, especially in tasks like math and coding [[32](https://arxiv.org/html/2502.10867v1#bib.bib32), [16](https://arxiv.org/html/2502.10867v1#bib.bib16)]. However, these approaches build on existing LLMs without truly embedding the chain of thought ability within the models themselves. As a result, LLMs cannot inherently learn this reasoning capability, leading to active research on how to integrate it directly into model training. Proposed methods range from collecting specialised training data to building reward models [[18](https://arxiv.org/html/2502.10867v1#bib.bib18), [11](https://arxiv.org/html/2502.10867v1#bib.bib11), [15](https://arxiv.org/html/2502.10867v1#bib.bib15)] and increasing the computational complexity of decoding [[24](https://arxiv.org/html/2502.10867v1#bib.bib24), [33](https://arxiv.org/html/2502.10867v1#bib.bib33)], but none have yet achieved significant performance breakthroughs at scale.

It remains unclear whether OpenAI’s o1 innovation is rooted in the model itself, rather than relying on external prompting systems. If it indeed involves explicitly embedding step-by-step reasoning natively within the architecture, this would represent a significant breakthrough. Building on substantial performance gains, OpenAI o1 has shown that the scaling principles traditionally applied during training [[9](https://arxiv.org/html/2502.10867v1#bib.bib9), [24](https://arxiv.org/html/2502.10867v1#bib.bib24)] are now relevant to the inference phase. We should reallocate our computational focus, balancing pre-training efforts with efficient use of inference-time computation. Allowing LLMs to enhance their outputs with increased test-time computing is an essential step towards creating generally self-improving agents capable of managing open-ended strong reasoning and decision-making tasks. This direction, which we refer to as LLM-Native Chain-of-Thought (NativeCoT), should be able to inherently mirror the deliberate, analytical process possessed by human’s System 2 thinking [[8](https://arxiv.org/html/2502.10867v1#bib.bib8)].

Given that o1 is a closed-source system, the precise techniques used to achieve such strong reasoning capabilities remain largely a mystery. In this article, we will provide a comprehensive overview of the relevant literature and offer insights into what we believe are the core techniques and methods underpinning this breakthrough. Additionally, we will propose our ideas for implementing an open-source counterpart, which could accelerate research in this area. Our proposals will draw inspiration from recent work, including ours on data acquisition, reinforcement learning based training, and search and MCTS-based decoding for improving reasoning capabilities in existing models.

In the next section, we will discuss two challenges commonly encountered by typical autoregressive LLMs, highlighting the need for a world model and a chain-of-thought mechanism. We will then present an MDP formulation for incorporating native CoT within LLMs (resulting in o1-like reasoning models) and explore its implementation details. Finally, we conclude with bibliographic remarks and suggest future research directions.

##  2 The Challenges with Autoregressive LLMs

Autoregressive language models (LLMs) generate sequences of text by predicting the next token (e.g., word) in the sequence given the previous tokens [[29](https://arxiv.org/html/2502.10867v1#bib.bib29)]. Mathematically, they are based on the principle of conditional probability. The task is to model the joint probability of a sequence of tokens 𝐱=(x1,x2,…,xT)𝐱subscript𝑥1subscript𝑥2…subscript𝑥𝑇\mathbf{x}=(x_{1},x_{2},\dots,x_{T})bold_x = ( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT ), where T𝑇Titalic_T is the length of the sequence, by factorising it into a product of conditional probabilities using the chain rule of probability.

Given a sequence of tokens 𝐱=(x1,x2,…,xT)𝐱subscript𝑥1subscript𝑥2…subscript𝑥𝑇\mathbf{x}=(x_{1},x_{2},\dots,x_{T})bold_x = ( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT ), an autoregressive language model estimates the joint probability P⁢(𝐱)𝑃𝐱P(\mathbf{x})italic_P ( bold_x ) as:

| P⁢(𝐱)=P⁢(x1,x2,…,xT)=∏t=1TP⁢(xt∣x1,x2,…,xt−1),𝑃𝐱𝑃subscript𝑥1subscript𝑥2…subscript𝑥𝑇superscriptsubscriptproduct𝑡1𝑇𝑃conditionalsubscript𝑥𝑡subscript𝑥1subscript𝑥2…subscript𝑥𝑡1P(\mathbf{x})=P(x_{1},x_{2},\dots,x_{T})=\prod_{t=1}^{T}P(x_{t}\mid x_{1},x_{2% },\dots,x_{t-1}),italic_P ( bold_x ) = italic_P ( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT ) = ∏ start_POSTSUBSCRIPT italic_t = 1 end_POSTSUBSCRIPT start_POSTSUPERSCRIPT italic_T end_POSTSUPERSCRIPT italic_P ( italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) , |   
---|---|---  
  
where the model predicts the probability of each token xtsubscript𝑥𝑡x_{t}italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT based on all preceding tokens in the sequence x1,x2,…,xt−1subscript𝑥1subscript𝑥2…subscript𝑥𝑡1x_{1},x_{2},\dots,x_{t-1}italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT. Typically, this is achieved using neural networks like transformers [[29](https://arxiv.org/html/2502.10867v1#bib.bib29)], which are trained to minimise the negative log-likelihood of the training data. For an explanation of the training steps, please refer to Appendix A.

At inference time, the model generates text by typically sampling tokens sequentially from the probability distribution P⁢(xt∣x1,x2,…,xt−1)𝑃conditionalsubscript𝑥𝑡subscript𝑥1subscript𝑥2…subscript𝑥𝑡1P(x_{t}\mid x_{1},x_{2},\dots,x_{t-1})italic_P ( italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) until a stop token is reached or a predefined maximum length is achieved. The model works as follows: Firstly, start with a given sequence or a start token (if generating from scratch). Secondly, at each step t𝑡titalic_t, predict the next token xtsubscript𝑥𝑡x_{t}italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT based on the previously generated tokens (x1,x2,…,xt−1)subscript𝑥1subscript𝑥2…subscript𝑥𝑡1(x_{1},x_{2},\dots,x_{t-1})( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ). At last, continue sampling until the sequence is complete. For a simple three-token sequence 𝐱=(x1,x2,x3)𝐱subscript𝑥1subscript𝑥2subscript𝑥3\mathbf{x}=(x_{1},x_{2},x_{3})bold_x = ( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 3 end_POSTSUBSCRIPT ), the probability of the sequence would be:

| P⁢(𝐱)=P⁢(x1)⋅P⁢(x2∣x1)⋅P⁢(x3∣x1,x2).𝑃𝐱⋅⋅𝑃subscript𝑥1𝑃conditionalsubscript𝑥2subscript𝑥1𝑃conditionalsubscript𝑥3subscript𝑥1subscript𝑥2P(\mathbf{x})=P(x_{1})\cdot P(x_{2}\mid x_{1})\cdot P(x_{3}\mid x_{1},x_{2}).italic_P ( bold_x ) = italic_P ( italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT ) ⋅ italic_P ( italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT ) ⋅ italic_P ( italic_x start_POSTSUBSCRIPT 3 end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT ) . |   
---|---|---  
  
This formulation underpins the operation of autoregressive LLMs like GPT-style models. The learning is achieved by minimising mistakes in predicting subsequent tokens (words). The first challenges is this _predicting next tokens_ objective. While some people propose that predicting next tokens might pave the way for general intelligence (AGI), we intend to argue is that solely focusing on predicting the next word caps the potential for intelligence. A different optimisation target and learning paradigm might be necessary to foster deeper intelligence.

To illustrate the limitations of purely predictive models, let’s consider the domain of chess mastery. In this context, each chess move can be conceptualised as a token, with a complete chess representing a ”sentence” in the ”language of chess” - a sequence of moves from the opening to the endgame. Suppose we have access to an extensive dataset of chess games, but all from players with Elo ratings below 2000 (a standardised measure of player skill) [[5](https://arxiv.org/html/2502.10867v1#bib.bib5)]. If we train a chess agent solely by minimising token prediction errors based on these games, we would likely constrain the agent’s performance to within the ability range of these sub-2000 Elo players. This approach would essentially optimise the agent towards emulating the average or typical play of these players, potentially incorporating their mistakes and suboptimal strategies. This phenomenon can be characterised as what we called an ”intelligence upper bound,” a concept that can be rigorously derived from recent research in offline reinforcement learning and imitation learning [[10](https://arxiv.org/html/2502.10867v1#bib.bib10)]. The agent, in this case, is limited by the quality of the demonstrations it learns from, unable to surpass the skill level present in its training data. This limitation underscores a crucial challenge in AI development: how to enable systems to transcend the boundaries of their training data and develop novel, potentially superior strategies.

Conversely, when data is leveraged to develop a deeper understanding, or a _world model_ , of chess dynamics, it may pave the way for the evolution of sophisticated strategies and tactics that go beyond mere imitation of behaviours observed in the training data. A world model presents the agent’s understanding of the environment, in this case, the chess rules, i.e., how a move would change the status of the game and what the winning chance of a given move is. Learning and refining this world model, coupled with the ability to simulate potential outcomes, could potentially empower an AI agent to surpass the 2000 Elo benchmark. The simulation capabilities afforded by these internal world models would enable deep thinking (simulation), thereby enhancing the agent’s reasoning and generalisation capabilities. Model-based strategies like Monte Carlo Tree Search (MCTS) serve as classic illustrations of this approach [[23](https://arxiv.org/html/2502.10867v1#bib.bib23)]. The transition to System 2 type reasoning, as potentially exemplified by ChatGPT o1, likely relies on establishing a certain type of World Model and utilising reinforcement learning (reward maximisation) rather than solely minimising prediction errors. This shift in approach may be one of the key transitional techniques behind ChatGPT o1’s enhanced reasoning capabilities.

By combining the predictive power of large language models with the strategic depth of reinforcement learning and World Modelling, AI systems like o1 can potentially engage in more sophisticated problem-solving and decision-making processes. This hybrid approach allows for both rapid pattern recognition (akin to System 1 thinking) and deliberate, step-by-step reasoning (characteristic of System 2 thinking), potentially explaining the significant leap in performance observed in o1.

The second challenge, from a computational complexity perspective, is that Large Language Models (LLMs) inherently operate within the constraints of quadratic computational complexity [[13](https://arxiv.org/html/2502.10867v1#bib.bib13)]. This limitation becomes particularly apparent when LLMs encounter multi-step mathematical challenges. However, the ”chain of thoughts” concept offers a potential mitigation to this constraint [[32](https://arxiv.org/html/2502.10867v1#bib.bib32)]. It extends responses through a series of ”thought” outputs, therefore allows a certain amount of additional computation resources; it essentially acts as a _limited memory_ that supports writing but lacks the capacity for deletion or overwriting. While this approach has shown promise, it still falls short of a fully dynamic memory system and is not natively incorporated into the decoding stage. This necessity underscores the demand for advanced computational architectures that transcend the capabilities of current transformer decoder networks. Indeed, there is a need to implement sophisticated model-based strategies akin to Monte Carlo Tree Search (MCTS) witnin the inference and decoding stage [[6](https://arxiv.org/html/2502.10867v1#bib.bib6)].

Such an advanced inference-time computation system would enable AI models to maintain and dynamically update a representation of the problem space, facilitating more complex reasoning processes. This approach [[3](https://arxiv.org/html/2502.10867v1#bib.bib3)] aligns with the concept of working memory in cognitive science, which is crucial for complex problem-solving and deliberative thinking. By integrating these capabilities, AI systems could potentially simulate multiple steps ahead, evaluate different scenarios, and make more informed decisions — mirroring the deliberative processes observed in human expert reasoning.

Figure 3: In this MDP formulation, the LLM is tasked with generating reasoning steps and the final answer to a question in a step-by-step manner. The LLM policy operates by generating tokens, which form higher-level reasoning constructs. The states represent the sequence of reasoning steps so far, and actions correspond to the selection of new reasoning steps or the final answer. The LLM policy governs the choice of actions, and the process-reward model (PRM) provides feedback on the quality of reasoning steps and the final answer. By optimising the policy to maximise the reward, the LLM can be guided by PRM to generate accurate and meaningful reasoning processes. 

##  3 LLM Reasoning as a Markov Decision Process

To model the process of reasoning in tasks such as question answering or problem solving, we structure the reasoning task using the Q → {R} → A sequence, where:

  * •

Q: Represents the question or prompt that initiates the reasoning process.

  * •

R: Represents the sequence of intermediate reasoning steps the model generates to build toward the solution.

  * •

A: Represents the final answer or solution produced after the reasoning steps.




This structure allows the LLM to generate a sequence of reasoning steps that logically connect the question Q𝑄Qitalic_Q to the final answer A𝐴Aitalic_A.

We can define the reasoning process as a Markov Decision Process (MDP) [[1](https://arxiv.org/html/2502.10867v1#bib.bib1)]. A MDP representation offers a flexible framework for modelling reasoning. It allows the model to autoregressively generate sequential reasoning steps toward the final answer, while also enabling a tree structure by sampling multiple paths at each step for alternative reasoning trajectories. By combining both approaches-sequential and branching reasoning-the model can explore diverse solutions, creating a versatile and comprehensive reasoning process.

We are now ready to describe the reasoning process in terms of states, actions, policies, and rewards, where the LLM’s task is to incrementally generate a coherent sequence of tokens that correspond to reasoning steps and the final answer.

The state stsubscript𝑠𝑡s_{t}italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT at timestep t𝑡titalic_t represents the current state of the reasoning process, including the question and the reasoning steps generated so far. Formally, the state is defined as:

| st=(Q,R1,…,Rt−1),subscript𝑠𝑡𝑄subscript𝑅1…subscript𝑅𝑡1s_{t}=(Q,R_{1},\dots,R_{t-1}),italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT = ( italic_Q , italic_R start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , … , italic_R start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) , |   
---|---|---  
  
where Q𝑄Qitalic_Q is the initial question or prompt, and R1,…,Rt−1subscript𝑅1…subscript𝑅𝑡1R_{1},\dots,R_{t-1}italic_R start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , … , italic_R start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT are the reasoning steps generated up to timestep t𝑡titalic_t. The initial state s0subscript𝑠0s_{0}italic_s start_POSTSUBSCRIPT 0 end_POSTSUBSCRIPT contains just the question:

| s0=Q.subscript𝑠0𝑄s_{0}=Q.italic_s start_POSTSUBSCRIPT 0 end_POSTSUBSCRIPT = italic_Q . |   
---|---|---  
  
As reasoning progresses, the intermediate states include both the question and the reasoning steps generated so far. The process continues until the final answer is generated.

An action at∈Asubscript𝑎𝑡𝐴a_{t}\in Aitalic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∈ italic_A at timestep t𝑡titalic_t corresponds to the selection of the next reasoning step or the final answer. The action space A𝐴Aitalic_A consists of two types of actions:

  * •

Reasoning Step (R): The action selects a reasoning step Rtsubscript𝑅𝑡R_{t}italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT to append to the current state.

  * •

Final Answer (A): The action selects the final answer A𝐴Aitalic_A, which concludes the reasoning process.




For intermediate steps, the action is:

| at=Rt,subscript𝑎𝑡subscript𝑅𝑡a_{t}=R_{t},italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT = italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , |   
---|---|---  
  
and the new state becomes:

| st+1=st+Rt.subscript𝑠𝑡1subscript𝑠𝑡subscript𝑅𝑡s_{t+1}=s_{t}+R_{t}.italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT = italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT + italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT . |   
---|---|---  
  
For the final step, the action selects the final answer:

| aT=A,subscript𝑎𝑇𝐴a_{T}=A,italic_a start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT = italic_A , |   
---|---|---  
  
and the final state becomes:

| sT=sT−1+A.subscript𝑠𝑇subscript𝑠𝑇1𝐴s_{T}=s_{T-1}+A.italic_s start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT = italic_s start_POSTSUBSCRIPT italic_T - 1 end_POSTSUBSCRIPT + italic_A . |   
---|---|---  
  
The policy π𝜋\piitalic_π defines the strategy the model uses to choose the next action (i.e., reasoning step or final answer) given the current state. The policy is essentially the LLM, learned during training and represents the probability distribution over possible reasoning steps or the final answer, conditioned on the tokens generated so far:

| πL⁢L⁢M⁢(at∣st)=P⁢(at∣Q,R1,…,Rt−1).subscript𝜋𝐿𝐿𝑀conditionalsubscript𝑎𝑡subscript𝑠𝑡𝑃conditionalsubscript𝑎𝑡𝑄subscript𝑅1…subscript𝑅𝑡1\pi_{LLM}(a_{t}\mid s_{t})=P(a_{t}\mid Q,R_{1},\dots,R_{t-1}).italic_π start_POSTSUBSCRIPT italic_L italic_L italic_M end_POSTSUBSCRIPT ( italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) = italic_P ( italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_Q , italic_R start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , … , italic_R start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) . |   
---|---|---  
  
At each timestep, the model uses this policy to select the next action based on the current state, incrementally building towards the final answer.

Given the autoregressive nature of the LLM, the transition from one state to the next is deterministic and also given. The next state st+1subscript𝑠𝑡1s_{t+1}italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT is fully determined by appending the selected action atsubscript𝑎𝑡a_{t}italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT (a reasoning step or the final answer) to the current state stsubscript𝑠𝑡s_{t}italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT. Therefore, the transition function is:

| st+1=st+at.subscript𝑠𝑡1subscript𝑠𝑡subscript𝑎𝑡s_{t+1}=s_{t}+a_{t}.italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT = italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT + italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT . |   
---|---|---  
  
This means that once a reasoning step Rtsubscript𝑅𝑡R_{t}italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT or final answer A𝐴Aitalic_A is selected, the state st+1subscript𝑠𝑡1s_{t+1}italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT is uniquely defined by concatenating this action to the existing sequence of tokens.

The reward provides feedback on the quality of the generated reasoning steps and the final answer. In this context, the reward is obtained as the model generates reasoning steps and the final answer. The rewards can be defined as:

  * •

Intermediate Reward: For generating correct or meaningful reasoning steps, intermediate rewards are assigned positive values. Incorrect or irrelevant steps may yield negative rewards.

  * •

Final Reward: The largest reward is given when the model generates the correct final answer A𝐴Aitalic_A, completing the reasoning process.




Thus, the reward at each timestep t𝑡titalic_t is:

| vt=v⁢(Rt∣Q,R1,…,Rt−1),subscript𝑣𝑡𝑣conditionalsubscriptR𝑡𝑄subscript𝑅1…subscript𝑅𝑡1v_{t}=v(\text{R}_{t}\mid Q,R_{1},\dots,R_{t-1}),italic_v start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT = italic_v ( R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_Q , italic_R start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , … , italic_R start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) , |   
---|---|---  
  
and for the final step:

| vT=v⁢(A∣Q,R1,…,Rn).subscript𝑣𝑇𝑣conditional𝐴𝑄subscript𝑅1…subscript𝑅𝑛v_{T}=v(A\mid Q,R_{1},\dots,R_{n}).italic_v start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT = italic_v ( italic_A ∣ italic_Q , italic_R start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , … , italic_R start_POSTSUBSCRIPT italic_n end_POSTSUBSCRIPT ) . |   
---|---|---  
  
The model learns to optimise its policy to maximise the cumulative expected reward over the entire reasoning process.

Relationship Between Token Generation and Reasoning The LLM operates at two levels simultaneously: the level of token generation and the level of reasoning steps and final answers. At the most granular level, the LLM generates tokens autoregressively, meaning it generates one token at a time, conditioned on the previously generated tokens:

| P⁢(xt∣x1,x2,…,xt−1).𝑃conditionalsubscript𝑥𝑡subscript𝑥1subscript𝑥2…subscript𝑥𝑡1P(x_{t}\mid x_{1},x_{2},\dots,x_{t-1}).italic_P ( italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t - 1 end_POSTSUBSCRIPT ) . |   
---|---|---  
  
At each timestep t𝑡titalic_t, the LLM generates a token xtsubscript𝑥𝑡x_{t}italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT from its vocabulary based on the context provided by previous tokens. These tokens form higher-level constructs such as reasoning steps Rtsubscript𝑅𝑡R_{t}italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT and the final answer A𝐴Aitalic_A.

  * •

Reasoning Steps (R): Each reasoning step Rtsubscript𝑅𝑡R_{t}italic_R start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT is composed of a sequence of tokens {xt1,xt2,…,xtk}subscript𝑥subscript𝑡1subscript𝑥subscript𝑡2…subscript𝑥subscript𝑡𝑘\\{x_{t_{1}},x_{t_{2}},\dots,x_{t_{k}}\\}{ italic_x start_POSTSUBSCRIPT italic_t start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT italic_t start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_t start_POSTSUBSCRIPT italic_k end_POSTSUBSCRIPT end_POSTSUBSCRIPT } generated by the LLM. These tokens represent a coherent step in the reasoning process, such as a logical deduction or intermediate conclusion.

  * •

Final Answer (A): The final answer A𝐴Aitalic_A is similarly composed of a sequence of tokens that form the solution or response to the question. Once the LLM has generated sufficient reasoning steps, it produces the final answer in an autoregressive manner, token by token.




We are now ready to a world model for LLMs exactly: 

######  Definition 1 (World Model of LLM)

A _world model of LLM_ is defined as (𝒯,ℛ)𝒯ℛ(\mathcal{T},\mathcal{R})( caligraphic_T , caligraphic_R ), where:

  * •

The transition model 𝒯⁢(st,at)𝒯subscript𝑠𝑡subscript𝑎𝑡\mathcal{T}(s_{t},a_{t})caligraphic_T ( italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) is deterministic as the next state st+1subscript𝑠𝑡1s_{t+1}italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT is uniquely defined by the current state stsubscript𝑠𝑡s_{t}italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT and the action atsubscript𝑎𝑡a_{t}italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT (i.e., the generated token or reasoning step), so:

| st+1=st+at.subscript𝑠𝑡1subscript𝑠𝑡subscript𝑎𝑡s_{t+1}=s_{t}+a_{t}.italic_s start_POSTSUBSCRIPT italic_t + 1 end_POSTSUBSCRIPT = italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT + italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT . |   
---|---|---  
  
  * •

𝒱⁢(st,at)𝒱subscript𝑠𝑡subscript𝑎𝑡\mathcal{V}(s_{t},a_{t})caligraphic_V ( italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) is the process-reward model (PRM) that evaluates the quality of the action atsubscript𝑎𝑡a_{t}italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT taken in state stsubscript𝑠𝑡s_{t}italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT. It reflects how appropriate or effective the generated reasoning step or token is in progressing towards the final answer:

| 𝒱⁢(st,at)=vt.𝒱subscript𝑠𝑡subscript𝑎𝑡subscript𝑣𝑡\mathcal{V}(s_{t},a_{t})=v_{t}.caligraphic_V ( italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) = italic_v start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT . |   
---|---|---  
  



Since the transition is deterministic and follows directly from the policy, the process-reward model (PRM) ℛ⁢(st,at)ℛsubscript𝑠𝑡subscript𝑎𝑡\mathcal{R}(s_{t},a_{t})caligraphic_R ( italic_s start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , italic_a start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ) encapsulates the entire interaction between the LLM and its environment, evaluating how well each reasoning step or token contributes to reaching the final answer.

##  Appendix A Standard Training Pipelines of LLMs

The training procedure for LLM typically involves several stages, each building upon the previous one. In the pre-training stage, the model is trained on a massive online corpus using an autoregressive language modelling objective. The goal is to predict the next token given the previous tokens. For a given sequence of tokens {x1,x2,…,xT}subscript𝑥1subscript𝑥2…subscript𝑥𝑇\\{x_{1},x_{2},\dots,x_{T}\\}{ italic_x start_POSTSUBSCRIPT 1 end_POSTSUBSCRIPT , italic_x start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT , … , italic_x start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT }, the token-level cross-entropy loss sums the negative log-probabilities of the true tokens at each position:

| ℒpretrain=−∑t=1Tlog⁡P⁢(xt|x<t;θ),subscriptℒpretrainsuperscriptsubscript𝑡1𝑇𝑃conditionalsubscript𝑥𝑡subscript𝑥absent𝑡𝜃\mathcal{L}_{\text{pretrain}}=-\sum_{t=1}^{T}\log P(x_{t}|x_{<t};\theta),caligraphic_L start_POSTSUBSCRIPT pretrain end_POSTSUBSCRIPT = - ∑ start_POSTSUBSCRIPT italic_t = 1 end_POSTSUBSCRIPT start_POSTSUPERSCRIPT italic_T end_POSTSUPERSCRIPT roman_log italic_P ( italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT | italic_x start_POSTSUBSCRIPT < italic_t end_POSTSUBSCRIPT ; italic_θ ) , |   
---|---|---  
  
where xtsubscript𝑥𝑡x_{t}italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT is the t𝑡titalic_t-th token, x<tsubscript𝑥absent𝑡x_{<t}italic_x start_POSTSUBSCRIPT < italic_t end_POSTSUBSCRIPT represents all tokens before t𝑡titalic_t, θ𝜃\thetaitalic_θ are the model parameters, and P𝑃Pitalic_P is the probability distribution over the vocabulary [[2](https://arxiv.org/html/2502.10867v1#bib.bib2)]. p⁢(xt∣x<t)𝑝conditionalsubscript𝑥𝑡subscript𝑥absent𝑡p(x_{t}\mid x_{<t})italic_p ( italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT ∣ italic_x start_POSTSUBSCRIPT < italic_t end_POSTSUBSCRIPT ) is the probability of the true token xtsubscript𝑥𝑡x_{t}italic_x start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT given all previous tokens x<tsubscript𝑥absent𝑡x_{<t}italic_x start_POSTSUBSCRIPT < italic_t end_POSTSUBSCRIPT. This loss measures how well the model predicts each token in the sequence.

After pre-training, the model is then fine-tuned on collected additional {Question, Answer} pairs. The objective is to maximise the likelihood of the correct answer given the question:

| ℒfinetune=−∑i=1Nlog⁡P⁢(Ai|Qi;θ),subscriptℒfinetunesuperscriptsubscript𝑖1𝑁𝑃conditionalsubscript𝐴𝑖subscript𝑄𝑖𝜃\mathcal{L}_{\text{finetune}}=-\sum_{i=1}^{N}\log P(A_{i}|Q_{i};\theta),caligraphic_L start_POSTSUBSCRIPT finetune end_POSTSUBSCRIPT = - ∑ start_POSTSUBSCRIPT italic_i = 1 end_POSTSUBSCRIPT start_POSTSUPERSCRIPT italic_N end_POSTSUPERSCRIPT roman_log italic_P ( italic_A start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT | italic_Q start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT ; italic_θ ) , |   
---|---|---  
  
where Qisubscript𝑄𝑖Q_{i}italic_Q start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT and Aisubscript𝐴𝑖A_{i}italic_A start_POSTSUBSCRIPT italic_i end_POSTSUBSCRIPT are the i𝑖iitalic_i-th question and answer pair, respectively [[20](https://arxiv.org/html/2502.10867v1#bib.bib20)].

Next, Reinforcement Learning from Human Feedback (RLHF) [[18](https://arxiv.org/html/2502.10867v1#bib.bib18)] is then applied to further improve the model’s instruction-following ability. This involves constructing a reward model R⁢(x)𝑅𝑥R(x)italic_R ( italic_x ) (by pair-wise training data) that estimates the quality of the model’s outputs. The policy (language model) is then optimised using methods like Proximal Policy Optimisation (PPO) [[21](https://arxiv.org/html/2502.10867v1#bib.bib21)]:

| ℒRLHF=𝔼[R(Q,A)]−β⋅KL(πθ(Q|A)∥πθold(Q|A)),\mathcal{L}_{\text{RLHF}}=\mathbb{E}[R(Q,A)]-\beta\cdot\text{KL}(\pi_{\theta}(% Q|A)\|\pi_{\theta_{\text{old}}}(Q|A)),caligraphic_L start_POSTSUBSCRIPT RLHF end_POSTSUBSCRIPT = blackboard_E [ italic_R ( italic_Q , italic_A ) ] - italic_β ⋅ KL ( italic_π start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT ( italic_Q | italic_A ) ∥ italic_π start_POSTSUBSCRIPT italic_θ start_POSTSUBSCRIPT old end_POSTSUBSCRIPT end_POSTSUBSCRIPT ( italic_Q | italic_A ) ) , |   
---|---|---  
  
where πθsubscript𝜋𝜃\pi_{\theta}italic_π start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT is the current policy, πθoldsubscript𝜋subscript𝜃old\pi_{\theta_{\text{old}}}italic_π start_POSTSUBSCRIPT italic_θ start_POSTSUBSCRIPT old end_POSTSUBSCRIPT end_POSTSUBSCRIPT is the old policy, and β𝛽\betaitalic_β is a hyperparameter controlling the strength of the KL divergence penalty.