---
title: "Simplifying Alignment: From RLHF to Direct Preference Optimization (DPO)"
source: "https://huggingface.co/blog/ariG23498/rlhf-to-dpo"
ingestedAt: "2026-05-22T11:54:17Z"
---
#  Simplifying Alignment: From RLHF to Direct Preference Optimization (DPO) 

Large language models (LLMs) are getting smarter every day, but teaching them to do what 

_we_

want, aligning them with human preferences, is still a tough nut to crack. As deep learning folks, we know that if you want a model to learn something, you give it data, right? So why not gather some examples of what we like and have the model learn those preferences? 

That’s where Reinforcement Learning with Human Feedback (RLHF) comes in. It’s a clever way to teach LLMs to follow human preferences by using feedback data. But RLHF can be a bit of a headache—it brings reinforcement learning into the mix, and optimization gets tricky fast.

Enter Direct Preference Optimization (DPO). DPO skips the RL part while still teaching models to follow preferences. It’s simpler, cleaner, and honestly, who doesn’t love simplicity?

In this blog, we’ll go on a journey from RLHF to DPO, break down the math (don’t worry, we’ll keep it chill), and see why DPO might just be the smarter, easier way forward.

##  Reinforcement Learning with Human Feedback (RLHF) 

RLHF is a framework for aligning language models with human preferences through a structured, three-phase process. Each phase builds on the previous one, refining the model to better understand and produce responses that align with human expectations. Let’s break it down:

###  1\. Supervised Fine-Tuning (SFT) 

We start by taking a pre-trained language model and fine-tuning it on high-quality, task-specific data. This process generates a base policy πSFT(y∣x) \pi_{\text{SFT}}(y \mid x) πSFT​(y∣x), which represents the model's probability of generating an output y y y given an input x x x. 

This base policy serves as a strong starting point, capturing general task-related behavior but still needing refinement to align with human preferences.

###  2\. Preference Sampling & Reward Learning 

This phase focuses on collecting data about human preferences and building a **reward model** to represent those preferences numerically.

####  Preference Sampling 

Here’s how it works:

  1. The supervised fine-tuned model generates **pairs of responses** (y1,y2) (y_1, y_2) (y1​,y2​) for a given input or prompt x x x.
  2. Human annotators compare these responses and select their preferred response, yw y_w yw​ (the "winner"), over the less preferred response, yl y_l yl​ (the "loser").



These human preferences are then used as training data for the next step.

####  Reward Modeling 

We want to create a **reward model** rϕ(x,y) r_\phi(x, y) rϕ​(x,y), which assigns a numerical score (reward) to each response y y y given a prompt x x x. This score reflects how well the response aligns with human preferences.

#####  Modeling Pairwise Preferences 

To train this reward model, we rely on **pairwise comparisons** of responses yw y_w yw​ (winner) and yl y_l yl​ (loser). The preferences are modeled using the **Bradley-Terry framework** , which assigns a probability to the preference:

  1. The probability of yw y_w yw​ being preferred over yl y_l yl​ is: pϕ(yw>yl∣x)=exp⁡rϕ(x,yw)exp⁡rϕ(x,yw)+exp⁡rϕ(x,yl). p_\phi(y_w > y_l \mid x) = \frac{\exp r_\phi(x, y_w)}{\exp r_\phi(x, y_w) + \exp r_\phi(x, y_l)}. pϕ​(yw​>yl​∣x)=exprϕ​(x,yw​)+exprϕ​(x,yl​)exprϕ​(x,yw​)​.

     * rϕ(x,yw) r_\phi(x, y_w) rϕ​(x,yw​) and rϕ(x,yl) r_\phi(x, y_l) rϕ​(x,yl​): Rewards (scores) assigned to the winner and loser, respectively.
     * The numerator exp⁡rϕ(x,yw) \exp r_\phi(x, y_w) exprϕ​(x,yw​): Represents the likelihood of the winner being the preferred choice.
     * The denominator ensures probabilities sum to 1 by including both options: exp⁡rϕ(x,yw)+exp⁡rϕ(x,yl) \exp r_\phi(x, y_w) + \exp r_\phi(x, y_l) exprϕ​(x,yw​)+exprϕ​(x,yl​).
  2. Rearranging, we write the probability in terms of a difference between rewards: pϕ(yw>yl∣x)=11+exp⁡[rϕ(x,yl)−rϕ(x,yw)]. p_\phi(y_w > y_l \mid x) = \frac{1}{1 + \exp \left[ r_\phi(x, y_l) - r_\phi(x, y_w) \right]}. pϕ​(yw​>yl​∣x)=1+exp[rϕ​(x,yl​)−rϕ​(x,yw​)]1​.

     * rϕ(x,yl)−rϕ(x,yw) r_\phi(x, y_l) - r_\phi(x, y_w) rϕ​(x,yl​)−rϕ​(x,yw​): The difference between the scores of the loser and the winner.
     * exp⁡(⋅) \exp(\cdot) exp(⋅): Converts this difference into a scaling factor for the probability.
  3. Using the **sigmoid function** σ(z)=11+e−z \sigma(z) = \frac{1}{1 + e^{-z}} σ(z)=1+e−z1​, the equation becomes: pϕ(yw>yl∣x)=σ(rϕ(x,yw)−rϕ(x,yl)). p_\phi(y_w > y_l \mid x) = \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)). pϕ​(yw​>yl​∣x)=σ(rϕ​(x,yw​)−rϕ​(x,yl​)).

     * rϕ(x,yw)−rϕ(x,yl) r_\phi(x, y_w) - r_\phi(x, y_l) rϕ​(x,yw​)−rϕ​(x,yl​): If the winner's score is much higher than the loser's, the probability approaches 1 (the winner is strongly preferred).



#####  Training the Reward Model 

To train rϕ r_\phi rϕ​, we optimize it to match human preferences as closely as possible. This is done using **maximum likelihood estimation (MLE)** :

  * The loss function for the reward model is: LR(rϕ,D)=−E(x,yw,yl)∼D[log⁡σ(rϕ(x,yw)−rϕ(x,yl))]. \mathcal{L}_R(r_\phi, \mathcal{D}) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \big[ \log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)) \big]. LR​(rϕ​,D)=−E(x,yw​,yl​)∼D​[logσ(rϕ​(x,yw​)−rϕ​(x,yl​))].

    * D \mathcal{D} D: Dataset of human preferences (pairs yw,yl y_w, y_l yw​,yl​ for each prompt x x x).
    * log⁡σ(⋅) \log \sigma(\cdot) logσ(⋅): Penalizes predictions that assign low probabilities to actual human preferences.
    * The goal is to **minimize the negative log-likelihood** , ensuring the reward model aligns its predictions with the collected human feedback.



###  3\. Reinforcement Learning (RL) Optimization 

The final step involves fine-tuning the policy πϕ(y∣x) \pi_\phi(y \mid x) πϕ​(y∣x) using reinforcement learning to maximize the reward. However, directly maximizing the reward can lead to excessive deviations from the base policy πSFT \pi_{\text{SFT}} πSFT​, causing unnatural or overly optimized behavior. To address this, we add a penalty to constrain the policy:

####  The RL Objective 

The optimization objective is: max⁡πϕ Ex∼D,y∼πϕ(y∣x)[rϕ(x,y)]−βDKL[πϕ(y∣x)∥πref(y∣x)]. \max_{\pi_\phi} \ \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\phi(y \mid x)} \big[ r_\phi(x, y) \big] - \beta \text{D}_{\text{KL}} \big[ \pi_\phi(y \mid x) \Vert \pi_{\text{ref}}(y \mid x) \big]. πϕ​max​ Ex∼D,y∼πϕ​(y∣x)​[rϕ​(x,y)]−βDKL​[πϕ​(y∣x)∥πref​(y∣x)].

  * **First Term** : E[rϕ(x,y)] \mathbb{E}[r_\phi(x, y)] E[rϕ​(x,y)]

    * Encourages the policy to generate responses with higher rewards.
  * **Second Term** : DKL \text{D}_{\text{KL}} DKL​

    * DKL(P∥Q) \text{D}_{\text{KL}}(P \Vert Q) DKL​(P∥Q): The Kullback-Leibler (KL) divergence, a measure of how much P P P differs from Q Q Q.
    * Penalizes the policy πϕ \pi_\phi πϕ​ for straying too far from the reference policy πref \pi_{\text{ref}} πref​ (usually πSFT \pi_{\text{SFT}} πSFT​).
  * β \beta β: A weighting factor controlling the balance between maximizing rewards and staying close to the reference policy.




This process completes the RLHF pipeline, where reinforcement learning ensures the model generates responses that maximize alignment with human preferences while maintaining a natural and task-relevant behavior.

###  Challenges of RLHF 

  1. **Non-Differentiability of Language Outputs** :  
Language generation involves sampling discrete tokens, which breaks the flow of gradients during optimization. This makes it tricky to directly use gradient-based methods (the backbone of deep learning) to adjust the model.

  2. **Reward Model Struggles to Generalize** :  
The reward model learns to predict human preferences, but it’s hard to capture the subtlety and variability of what humans truly prefer. If the reward model fails to generalize, it can lead to misaligned or biased optimization.

  3. **Computational and Implementation Overhead** :  
RL adds significant complexity to the pipeline. From designing the reward function to tuning hyperparameters like the KL penalty, it requires specialized expertise and significantly more compute power compared to simpler fine-tuning methods.




##  From RLHF to Direct Preference Optimization (DPO) 

In this section, we’ll reframe the RLHF objective and introduce a key variable transformation. This reformulation will pave the way to understanding how Direct Preference Optimization (DPO) works and why it’s a simpler, more efficient alternative to RLHF.

###  Reformulating the RLHF Objective 

The RLHF objective begins as:

max⁡π Ex∼D,y∼π(y∣x)[r(x,y)]−βDKL[π(y∣x)∥πref(y∣x)]. \max_{\pi} \ \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi(y \mid x)} \big[ r(x, y) \big] - \beta \text{D}_{\text{KL}} \big[ \pi(y \mid x) \Vert \pi_{\text{ref}}(y \mid x) \big]. πmax​ Ex∼D,y∼π(y∣x)​[r(x,y)]−βDKL​[π(y∣x)∥πref​(y∣x)].

This objective balances two goals:

  1. **Maximizing reward** : Encourage the model π(y∣x) \pi(y \mid x) π(y∣x) to generate outputs y y y that align with human preferences, as captured by the reward r(x,y) r(x, y) r(x,y).
  2. **Constraining deviation** : Prevent the model from diverging too far from a reference policy πref(y∣x) \pi_{\text{ref}}(y \mid x) πref​(y∣x) (usually the supervised fine-tuned model), which ensures stability and avoids overly aggressive changes.



####  Expanding the KL Divergence Term 

The KL divergence measures the "distance" between the current policy π(y∣x) \pi(y \mid x) π(y∣x) and the reference policy πref(y∣x) \pi_{\text{ref}}(y \mid x) πref​(y∣x). Expanding it gives:

DKL[π(y∣x)∥πref(y∣x)]=Ey∼π(y∣x)[log⁡π(y∣x)−log⁡πref(y∣x)]. \text{D}_{\text{KL}}\big[\pi(y \mid x) \Vert \pi_{\text{ref}}(y \mid x)\big] = \mathbb{E}_{y \sim \pi(y \mid x)} \big[ \log \pi(y \mid x) - \log \pi_{\text{ref}}(y \mid x) \big]. DKL​[π(y∣x)∥πref​(y∣x)]=Ey∼π(y∣x)​[logπ(y∣x)−logπref​(y∣x)].

This term penalizes π \pi π for deviating from πref \pi_{\text{ref}} πref​. Substituting it back into the original objective gives:

max⁡π Ex∼D,y∼π(y∣x)[r(x,y)−βlog⁡π(y∣x)+βlog⁡πref(y∣x)]. \max_{\pi} \ \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi(y \mid x)} \big[ r(x, y) - \beta \log \pi(y \mid x) + \beta \log \pi_{\text{ref}}(y \mid x) \big]. πmax​ Ex∼D,y∼π(y∣x)​[r(x,y)−βlogπ(y∣x)+βlogπref​(y∣x)].

####  Switching to a Minimization Form 

For simplicity, we rewrite the objective as a minimization problem (minimizing the negative of the maximization objective):

min⁡π Ex∼D,y∼π(y∣x)[log⁡π(y∣x)−log⁡πref(y∣x)−r(x,y)β]. \min_{\pi} \ \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi(y \mid x)} \big[ \log \pi(y \mid x) - \log \pi_{\text{ref}}(y \mid x) - \frac{r(x, y)}{\beta} \big]. πmin​ Ex∼D,y∼π(y∣x)​[logπ(y∣x)−logπref​(y∣x)−βr(x,y)​].

This highlights the trade-offs:

  * The log⁡π(y∣x) \log \pi(y \mid x) logπ(y∣x) term encourages the policy to focus on likely outputs.
  * The −log⁡πref(y∣x) -\log \pi_{\text{ref}}(y \mid x) −logπref​(y∣x) term ensures outputs remain close to the reference model.
  * The −r(x,y)β \frac{-r(x, y)}{\beta} β−r(x,y)​ term biases the policy toward high-reward responses.



###  Introducing the Partition Function 

Let's introduce a function Z(x) Z(x) Z(x)

Z(x)=∑yπref(y∣x)exp⁡[r(x,y)β]. Z(x) = \sum_y \pi_{\text{ref}}(y \mid x) \exp\big[ \frac{r(x, y)}{\beta} \big]. Z(x)=y∑​πref​(y∣x)exp[βr(x,y)​].

Using Z(x) Z(x) Z(x), we can express π(y∣x) \pi(y \mid x) π(y∣x) as:

π(y∣x)=1Z(x)πref(y∣x)exp⁡[r(x,y)β]. \pi(y \mid x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y \mid x) \exp\big[ \frac{r(x, y)}{\beta} \big]. π(y∣x)=Z(x)1​πref​(y∣x)exp[βr(x,y)​].

Here’s the intuition:

  * πref(y∣x) \pi_{\text{ref}}(y \mid x) πref​(y∣x): Acts as a baseline distribution (our starting point).
  * exp⁡[r(x,y)β] \exp\big[\frac{r(x, y)}{\beta}\big] exp[βr(x,y)​]: Scales outputs y y y based on their reward, making high-reward outputs more likely.
  * Z(x) Z(x) Z(x): Normalizes the distribution so probabilities sum to 1.



This formulation enables us to reweight the reference policy by incorporating preferences encoded in the reward model, without requiring direct reinforcement learning.

###  Derivation of DPO Loss 

The key trick of **Direct Preference Optimization (DPO)** is focusing on pairwise preferences, which simplifies optimization. Let’s break it down:

####  Pairwise Preferences 

For two completions y1 y_1 y1​ (winner) and y2 y_2 y2​ (loser), we care about the probability that humans prefer y1 y_1 y1​ over y2 y_2 y2​. Using the Bradley-Terry model, this probability is:

p(y1>y2∣x)=σ(βlog⁡π(y1∣x)πref(y1∣x)−βlog⁡π(y2∣x)πref(y2∣x)), p(y_1 > y_2 \mid x) = \sigma\big(\beta \log \frac{\pi(y_1 \mid x)}{\pi_{\text{ref}}(y_1 \mid x)} - \beta \log \frac{\pi(y_2 \mid x)}{\pi_{\text{ref}}(y_2 \mid x)}\big), p(y1​>y2​∣x)=σ(βlogπref​(y1​∣x)π(y1​∣x)​−βlogπref​(y2​∣x)π(y2​∣x)​),

where σ(z)=11+e−z \sigma(z) = \frac{1}{1 + e^{-z}} σ(z)=1+e−z1​ is the sigmoid function.

####  Simplifying π(y∣x) \pi(y \mid x) π(y∣x)

Substituting π(y∣x) \pi(y \mid x) π(y∣x) from the earlier reformulation:

π(y∣x)=1Z(x)πref(y∣x)exp⁡[r(x,y)β]. \pi(y \mid x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y \mid x) \exp\big[ \frac{r(x, y)}{\beta} \big]. π(y∣x)=Z(x)1​πref​(y∣x)exp[βr(x,y)​].

When comparing two outputs y1 y_1 y1​ and y2 y_2 y2​, the partition function Z(x) Z(x) Z(x) cancels out (since it’s the same for both), leaving:

p(y1>y2∣x)=σ(r(x,y1)−r(x,y2)). p(y_1 > y_2 \mid x) = \sigma\big(r(x, y_1) - r(x, y_2)\big). p(y1​>y2​∣x)=σ(r(x,y1​)−r(x,y2​)).

This simplifies the computation, as we no longer need to compute Z(x) Z(x) Z(x) explicitly. The sigmoid function ensures that higher rewards correspond to higher probabilities.

####  DPO Loss 

To train πθ \pi_\theta πθ​ (the parameterized policy), we use **maximum likelihood estimation (MLE)** over human preferences. The DPO loss becomes:

LDPO(πθ,πref)=−E(x,yw,yl)∼D[log⁡σ(βlog⁡πθ(yw∣x)πref(yw∣x)−βlog⁡πθ(yl∣x)πref(yl∣x))]. \mathcal{L}_{\text{DPO}}(\pi_\theta, \pi_{\text{ref}}) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \big[ \log \sigma\big(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\big) \big]. LDPO​(πθ​,πref​)=−E(x,yw​,yl​)∼D​[logσ(βlogπref​(yw​∣x)πθ​(yw​∣x)​−βlogπref​(yl​∣x)πθ​(yl​∣x)​)].

###  Why Does This Trick Work? 

  1. **No Reinforcement Learning Required** :  
By reframing the problem in terms of pairwise preferences and reweighting the reference policy, DPO eliminates the need for complex reinforcement learning.

  2. **Simpler Optimization** :  
The partition function Z(x) Z(x) Z(x) cancels out in pairwise comparisons, reducing computational overhead. Training focuses directly on aligning with human preferences.

  3. **Improved Stability** :  
The KL constraint from πref(y∣x) \pi_{\text{ref}}(y \mid x) πref​(y∣x) ensures that πθ \pi_\theta πθ​ remains grounded, avoiding extreme behavior changes often seen in RL.

  4. **Focus on Human Preferences** :  
By directly optimizing for pairwise preference probabilities, DPO centers the learning process around human-labeled data, aligning outputs more naturally with human expectations.




##  Conclusion 

Direct Preference Optimization simplifies the alignment of large language models by replacing the RL phase of RLHF with a direct optimization framework. By working with pairwise preferences and avoiding reinforcement learning, DPO achieves alignment with reduced computational and implementation overhead, making it a compelling alternative for aligning large-scale models.

As alignment techniques evolve, DPO exemplifies how simplifying assumptions can lead to practical and effective solutions for real-world challenges in AI.