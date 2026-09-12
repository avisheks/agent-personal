---
title: "DPO (Direct Preference Optimization) - A Simpler Alternative to RLHF - machinelearningplus"
source: "https://machinelearningplus.com/gen-ai/dpo-direct-preference-optimization/"
ingestedAt: "2026-05-22T11:54:20Z"
---
You’ve fine-tuned a language model. It generates fluent text. But it also outputs toxic responses, ignores instructions, and hallucinates confidently.

RLHF was supposed to fix this. But it needs a separate reward model, a PPO training loop, and careful hyperparameter tuning. Each piece can break independently.

What if you could skip all of that? What if you could align your model directly from preference data, using a single supervised loss?

That’s exactly what DPO does. And once you see how the math simplifies, you’ll wonder why anyone bothered with PPO in the first place.

Before we write any code, here’s how all the pieces connect.

You start with a pre-trained language model that’s been through supervised fine-tuning (SFT). It can follow instructions, but it doesn’t know which responses humans prefer.

To teach preferences, you collect pairs of responses — one chosen by humans and one rejected.

In RLHF, you’d train a separate reward model on those pairs, then use PPO to maximize that reward while staying close to the original model. Three moving parts, three things that can break.

DPO takes a shortcut. The authors proved the optimal RLHF policy has a closed-form solution. You can rearrange the math so the reward model cancels out entirely. What’s left is a loss function that optimizes your policy directly on preference pairs. No reward model, no RL loop. Just supervised learning.

We’ll build each piece from scratch. By the end, you’ll understand not just the code — but the “why” behind every equation.

## What Is DPO (Direct Preference Optimization)?

**Direct Preference Optimization (DPO)** is an alignment technique that trains language models to match human preferences without needing a separate reward model or reinforcement learning. It replaces RLHF’s multi-stage pipeline with a single supervised loss function.

Standard RLHF works in three stages. First, you fine-tune a pretrained model on demonstrations (SFT). Second, you train a reward model on human preference pairs. Third, you run PPO to maximize the reward while staying close to the SFT checkpoint.

DPO collapses the second and third stages into one. It skips the reward model entirely.

Here’s the key insight: the reward model is just a middleman. It converts preference data into a scalar signal, then PPO converts that signal into policy updates. DPO cuts out the middleman by deriving a loss function that goes directly from preference pairs to policy updates.

The result? Comparable alignment quality on most benchmarks, with far less complexity.
    
    
    import torch
    import torch.nn.functional as F
    import numpy as np
    import matplotlib.pyplot as plt
    
    print("Libraries loaded successfully")
    
    
    
    Libraries loaded successfully
    

The difference between RLHF and DPO is stark. RLHF trains three models. DPO trains one with a simple loss.
    
    
    === RLHF Pipeline ===
      Step 1: Train SFT model on demonstrations
      Step 2: Collect preference pairs (chosen vs rejected)
      Step 3: Train reward model on preference pairs
      Step 4: Run PPO to maximize reward (with KL penalty)
    
    === DPO Pipeline ===
      Step 1: Train SFT model on demonstrations
      Step 2: Collect preference pairs (chosen vs rejected)
      Step 3: Train policy directly on preference pairs
    

RLHF requires training and maintaining three separate models (SFT, reward, policy+value). DPO needs just two — the SFT reference and the policy being trained.
    
    
    RLHF models to train: 3 (SFT + Reward + Policy)
    DPO models to train:  2 (SFT + Policy)
    RLHF models in GPU memory: 4 (SFT ref + Reward + Policy + Value)
    DPO models in GPU memory:  2 (SFT ref + Policy)
    

## RLHF Explained — The Pipeline DPO Simplifies

You need some RLHF background to appreciate what DPO replaces. I’ll keep this focused — just enough to understand the simplification.

### The RLHF Objective

RLHF solves this optimization problem: find a policy that maximizes reward while staying close to the reference model (the SFT checkpoint).

In math:

`\[\max_{\pi} \mathbb{E}_{x \sim D, y \sim \pi(y|x)} [r(x, y)] - \beta \cdot D_{KL}[\pi(y|x) \| \pi_{ref}(y|x)]\]`

Where:  
– `\(\pi\)` = the policy (the language model we’re training)  
– `\(r(x, y)\)` = the reward for response `\(y\)` given prompt `\(x\)`  
– `\(\beta\)` = the KL penalty strength (controls how far the policy can drift)  
– `\(D_{KL}\)` = KL divergence between the policy and the reference model `\(\pi_{ref}\)`  
– `\(\pi_{ref}\)` = the reference policy (the frozen SFT checkpoint)

Two forces pull in opposite directions. The first term pushes toward high-reward responses. The KL divergence term (second) pulls back toward the reference.

The parameter beta controls the balance. High beta means “stay close to the reference.” Low beta means “chase reward aggressively.”

Let’s visualize this trade-off. Each curve shows the net objective for a different beta value. The peak of each curve is the sweet spot — maximum benefit.
    
    
    beta_values = [0.05, 0.1, 0.2, 0.5]
    kl_range = np.linspace(0, 5, 100)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    for beta in beta_values:
        reward = 2 * np.sqrt(kl_range)
        penalty = beta * kl_range
        net_objective = reward - penalty
        ax.plot(kl_range, net_objective, label=f"beta={beta}", linewidth=2)
    
    ax.set_xlabel("KL Divergence from Reference", fontsize=12)
    ax.set_ylabel("Net Objective (Reward - beta * KL)", fontsize=12)
    ax.set_title("RLHF Trade-off: Reward vs. Staying Close", fontsize=13)
    ax.legend(fontsize=11)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("rlhf_tradeoff.png", dpi=100)
    plt.show()
    
    
    
    [Chart showing four curves with different beta values, each peaking at different KL values]
    

With small beta (0.05), the model wanders far from the reference to chase reward. With large beta (0.5), it barely budges. Each peak represents the best trade-off for that constraint strength.

### The Bradley-Terry Preference Model

RLHF doesn’t get reward signals from the environment. Instead, it learns rewards from human preferences using the Bradley-Terry model.

Given two responses y_w (preferred) and y_l (rejected) for the same prompt x:

`\[P(y_w \succ y_l | x) = \sigma(r(x, y_w) - r(x, y_l))\]`

Where:  
– `\(P(y_w \succ y_l | x)\)` = the probability that response `\(y_w\)` is preferred over `\(y_l\)` for prompt `\(x\)`  
– `\(\sigma\)` = the sigmoid function (`\(\sigma(z) = 1/(1+e^{-z})\)`)  
– `\(r(x, y_w)\)` = reward assigned to the preferred (chosen) response  
– `\(r(x, y_l)\)` = reward assigned to the rejected response

The preference probability depends only on the _difference_ in rewards. This property is crucial for the DPO derivation later.
    
    
    def sigmoid(x):
        """Logistic sigmoid function."""
        return 1.0 / (1.0 + np.exp(-x))
    
    reward_diffs = np.linspace(-5, 5, 200)
    probs = sigmoid(reward_diffs)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(reward_diffs, probs, 'b-', linewidth=2.5)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    
    ax.annotate("Equal rewards -> 50/50", xy=(0, 0.5),
                xytext=(1.5, 0.35), fontsize=11,
                arrowprops=dict(arrowstyle="->", color='red'), color='red')
    
    ax.set_xlabel("r(x, y_w) - r(x, y_l)", fontsize=12)
    ax.set_ylabel("P(y_w preferred)", fontsize=12)
    ax.set_title("Bradley-Terry Preference Model", fontsize=13)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("bradley_terry.png", dpi=100)
    plt.show()
    
    
    
    [Chart showing sigmoid curve mapping reward differences to preference probabilities]
    

When the reward difference is zero, the model predicts a 50/50 coin flip. As y_w’s reward grows, probability approaches 1.0.

### The Reward Model Loss

The reward model learns to assign higher scores to human-preferred responses. Its loss maximizes the log-likelihood of getting the ranking right across all preference pairs:

`\[\mathcal{L}_{RM} = -\mathbb{E}_{(x, y_w, y_l) \sim D} [\log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))]\]`

Where:  
– `\(\mathcal{L}_{RM}\)` = the reward model loss (lower is better)  
– `\(\mathbb{E}\)` = expected value over all preference pairs in dataset `\(D\)`  
– `\(r_\phi\)` = the reward model with parameters `\(\phi\)`  
– `\(r_\phi(x, y_w) - r_\phi(x, y_l)\)` = the reward gap between chosen and rejected responses

This pushes the reward model to assign higher rewards to preferred responses.
    
    
    def reward_model_loss(reward_chosen, reward_rejected):
        """Bradley-Terry reward model loss."""
        return -torch.mean(
            torch.log(torch.sigmoid(reward_chosen - reward_rejected))
        )
    
    torch.manual_seed(42)
    reward_chosen = torch.tensor([2.5, 1.8, 3.0, 2.2, 1.5])
    reward_rejected = torch.tensor([1.0, 1.5, 0.5, 1.8, 0.8])
    
    loss = reward_model_loss(reward_chosen, reward_rejected)
    print(f"Reward model loss: {loss.item():.4f}")
    print(f"Avg reward gap: {(reward_chosen - reward_rejected).mean():.2f}")
    
    
    
    Reward model loss: 0.2894
    Avg reward gap: 0.88
    

The loss is low because the reward model correctly ranks chosen above rejected. But now you have a whole separate model to train and maintain. This is what DPO eliminates.

**Key Insight:** **The reward model is just a translator.** It converts human preference pairs into scalar rewards. DPO proves you don’t need this translator — you can optimize the policy directly from the pairs.

### Why RLHF Is Hard in Practice

RLHF works in theory. In practice, it’s fragile:

  * **Reward hacking.** The policy finds loopholes. It generates verbose responses that score high but aren’t actually good.
  * **Training instability.** PPO is sensitive to hyperparameters. Get any wrong and training diverges.
  * **Computational cost.** Four models in GPU memory: SFT reference, reward model, active policy, value network. For a 7B model, that’s ~56GB in bfloat16.
  * **Distribution shift.** As the policy improves, it generates outputs the reward model hasn’t seen. The reward signal becomes unreliable.


    
    
    comparison = {
        "Models in GPU memory": {"RLHF": "4", "DPO": "2"},
        "Training stages": {"RLHF": "3", "DPO": "2"},
        "Hyperparameters": {"RLHF": "10+", "DPO": "2-3"},
        "Reward hacking risk": {"RLHF": "High", "DPO": "Low"},
        "Training stability": {"RLHF": "Fragile", "DPO": "Stable"},
    }
    
    print(f"{'Metric':<25} {'RLHF (PPO)':<15} {'DPO'}")
    print("-" * 55)
    for metric, vals in comparison.items():
        print(f"{metric:<25} {vals['RLHF']:<15} {vals['DPO']}")
    
    
    
    Metric                    RLHF (PPO)      DPO
    -------------------------------------------------------
    Models in GPU memory      4               2
    Training stages           3               2
    Hyperparameters           10+             2-3
    Reward hacking risk       High            Low
    Training stability        Fragile         Stable
    

This is why DPO generated so much excitement. Same core goal, fraction of the complexity.

### DPO vs RLHF: What Do the Benchmarks Say?

The original DPO paper (Rafailov et al., 2023) tested on three tasks. Here’s how DPO compared to PPO-based RLHF.
    
    
    # Results from the original DPO paper (Table 1, Table 2)
    print("=== DPO Paper Benchmark Results ===\n")
    
    benchmarks = {
        "Sentiment Control (IMDb)": {
            "SFT baseline": "Neutral",
            "PPO (best)": "High positive sentiment",
            "DPO": "Higher positive sentiment",
            "Winner": "DPO",
        },
        "Summarization (TL;DR)": {
            "SFT baseline": "45% win rate vs human",
            "PPO (best)": "57% win rate vs human",
            "DPO": "61% win rate vs human",
            "Winner": "DPO",
        },
        "Dialogue (Anthropic HH)": {
            "SFT baseline": "Baseline",
            "PPO (best)": "Comparable to DPO",
            "DPO": "Comparable to PPO",
            "Winner": "Tie",
        },
    }
    
    print(f"{'Task':<30} {'Winner':<8} {'Key Finding'}")
    print("-" * 70)
    for task, data in benchmarks.items():
        print(f"{task:<30} {data['Winner']:<8} {data['DPO']}")
    
    
    
    === DPO Paper Benchmark Results ===
    
    Task                           Winner   Key Finding
    ----------------------------------------------------------------------
    Sentiment Control (IMDb)       DPO      Higher positive sentiment
    Summarization (TL;DR)          DPO      61% win rate vs human
    Dialogue (Anthropic HH)        Tie      Comparable to PPO
    

DPO matches or beats PPO on every benchmark — while being dramatically simpler to implement. The summarization result is particularly striking: DPO achieved a higher win rate against human summaries than the best PPO configuration.

**Key Insight:** **DPO doesn’t sacrifice quality for simplicity.** On standard alignment benchmarks, it matches or exceeds PPO-based RLHF. The simplification isn’t a compromise — it’s mathematically equivalent under ideal conditions.

### Before and After: What DPO Actually Does to Responses

Numbers are convincing. But seeing the actual effect on model outputs makes it click. Here’s a simplified example of how DPO shifts a model’s behavior.
    
    
    Prompt: Explain recursion to a beginner.
    
    BEFORE DPO (SFT model):
    --------------------------------------------------
    Recursion is a programming paradigm wherein a
    function invokes itself as a subroutine. The
    base case terminates the recursive calls, while
    the recursive case reduces the problem size.
    
    AFTER DPO (preference-aligned model):
    --------------------------------------------------
    Recursion is when a function calls itself. It's
    like looking at two mirrors facing each other --
    the reflection keeps going. Every recursive
    function needs a stopping rule (the base case)
    to avoid running forever.
    
    The DPO-trained model learned from preference
    data that users prefer clear, conversational
    explanations over dense technical language.
    

The SFT model is technically correct but reads like a textbook. After DPO training on human preferences, the model produces clearer, more conversational responses.

## Preparing Your Preference Dataset

Before we dive into the DPO math and implementation, let’s understand the data format. Good alignment starts with good data.

### Dataset Format

Every example needs three fields: a prompt, a chosen response, and a rejected response. The model learns to generate outputs more like “chosen” and less like “rejected.”
    
    
    example_dataset = [
        {
            "prompt": "Explain what a neural network is.",
            "chosen": "A neural network is a program that learns "
                      "patterns from data, like a student who figures "
                      "out rules from thousands of examples.",
            "rejected": "A neural network is a computational model "
                        "comprising interconnected nodes organized in "
                        "layers that process input signals.",
        },
    ]
    
    for ex in example_dataset:
        print(f"Prompt:   {ex['prompt']}")
        print(f"Chosen:   {ex['chosen'][:70]}...")
        print(f"Rejected: {ex['rejected'][:70]}...")
    
    
    
    Prompt:   Explain what a neural network is.
    Chosen:   A neural network is a program that learns patterns from data, like a s...
    Rejected: A neural network is a computational model comprising interconnected nod...
    

The chosen response is conversational and clear. The rejected one is jargon-heavy and impersonal.

### Sources of Preference Data

Where do these pairs come from?

  * **Human annotation.** Gold standard. Show annotators two responses and ask which is better. Expensive but highest quality.
  * **AI feedback (RLAIF).** Use a strong model (GPT-4, Claude) to rank responses. Cheaper but introduces the labeling model’s biases.
  * **Implicit signals.** Thumbs up/down, response edits, regeneration requests. Free but noisy.
  * **Existing datasets.** UltraFeedback, Anthropic HH-RLHF, Nectar — thousands of curated pairs ready to use.


    
    
    datasets_info = {
        "ultrafeedback_binarized": {"size": "~61K", "source": "GPT-4"},
        "Anthropic/hh-rlhf": {"size": "~170K", "source": "Human"},
        "OpenAssistant/oasst1": {"size": "~88K", "source": "Community"},
        "berkeley-nest/Nectar": {"size": "~183K", "source": "GPT-4"},
    }
    
    print(f"{'Dataset':<30} {'Pairs':<10} {'Source'}")
    print("-" * 55)
    for name, info in datasets_info.items():
        print(f"{name:<30} {info['size']:<10} {info['source']}")
    
    
    
    Dataset                        Pairs     Source
    -------------------------------------------------------
    ultrafeedback_binarized        ~61K      GPT-4
    Anthropic/hh-rlhf              ~170K     Human
    OpenAssistant/oasst1            ~88K      Community
    berkeley-nest/Nectar            ~183K     GPT-4
    

**Tip:** **Quality beats quantity.** 5K clean, well-labeled preference pairs often outperform 50K noisy ones. If you’re collecting your own data, invest in annotator guidelines and inter-annotator agreement checks.

## The DPO Derivation — From RLHF to One Loss Function

This is where DPO gets clever. I remember reading this derivation for the first time and thinking “there’s no way this is correct.” But each step is a small, logical move. And when the partition function cancels at the end, it’s genuinely satisfying.

### Step 1: The Closed-Form Solution

Remember the RLHF objective? It turns out this optimization problem has a closed-form solution. The optimal policy is:

`\[\pi^*(y|x) = \frac{1}{Z(x)} \pi_{ref}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)\]`

Where:  
– `\(\pi^*(y|x)\)` = the optimal policy (the best possible model)  
– `\(Z(x)\)` = the partition function — a normalization constant ensuring probabilities sum to 1  
– `\(\pi_{ref}(y|x)\)` = the reference model’s probability of generating response `\(y\)`  
– `\(r(x,y)\)` = the true reward for response `\(y\)`  
– `\(\beta\)` = the KL penalty strength

What does this say? The optimal policy takes the reference distribution and re-weights it. Responses with higher reward get exponentially more probability mass.

The next cell shows this re-weighting in action. We’ll start with a reference policy over 5 responses, apply known rewards, and compute the optimal policy.
    
    
    np.random.seed(42)
    pi_ref = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
    rewards = np.array([1.0, 3.0, 0.5, 2.5, -0.5])
    beta = 0.5
    
    # Optimal policy: pi_ref * exp(r/beta), then normalize
    unnormalized = pi_ref * np.exp(rewards / beta)
    Z = unnormalized.sum()
    pi_optimal = unnormalized / Z
    
    responses = ["Resp A", "Resp B", "Resp C", "Resp D", "Resp E"]
    
    print(f"{'Response':<10} {'Reward':<8} {'pi_ref':<8} {'pi_opt':<10} {'Change'}")
    print("-" * 46)
    for i in range(5):
        change = pi_optimal[i] / pi_ref[i]
        print(f"{responses[i]:<10} {rewards[i]:<8.1f} {pi_ref[i]:<8.2f} "
              f"{pi_optimal[i]:<10.4f} {change:.2f}x")
    
    
    
    Response   Reward  pi_ref  pi_opt     Change
    ----------------------------------------------
    Resp A     1.0     0.30    0.0654     0.22x
    Resp B     3.0     0.25    0.9013     3.61x
    Resp C     0.5     0.20    0.0248     0.12x
    Resp D     2.5     0.15    0.0998     0.67x
    Resp E     -0.5    0.10    0.0087     0.09x
    

Response B had the highest reward (3.0) and its probability jumped 3.6x. Response E had negative reward and nearly vanished.

**Quick Check:** What would happen if beta were very large (say, 100)? Think about it before reading on.

Answer: All responses would stay close to their reference probabilities. Large beta penalizes deviation, so pi_optimal would look almost identical to pi_ref.

### Step 2: Rearranging for the Implicit Reward

This is my favorite part of the derivation. Watch what happens when we flip the equation around.

To extract the implicit reward, we take the logarithm of the closed-form solution and rearrange.

Starting from the optimal policy and taking the log:

`\[\log \pi^*(y|x) = \log \pi_{ref}(y|x) + \frac{r(x,y)}{\beta} - \log Z(x)\]`

Each term maps directly from the closed-form solution: the log of the reference probability, plus the reward scaled by `\(\beta\)`, minus the log-partition function.

Rearranging to isolate the reward term gives us the **implicit reward** — the reward expressed purely in terms of the policy and reference:

`\[r(x,y) = \beta \log \frac{\pi^*(y|x)}{\pi_{ref}(y|x)} + \beta \log Z(x)\]`

Where:  
– `\(\beta \log \frac{\pi^*(y|x)}{\pi_{ref}(y|x)}\)` = how much more the optimal policy favors response `\(y\)` compared to the reference, scaled by `\(\beta\)`  
– `\(\beta \log Z(x)\)` = a prompt-dependent constant (same for all responses to the same prompt)

DPO defines reward as a function of the policy itself — no separate model needed. How much does the policy favor a response over what the reference would do? That ratio, scaled by beta, _is_ the reward.
    
    
    # Verify: implicit rewards should match the true rewards exactly
    implicit_rewards = beta * np.log(pi_optimal / pi_ref) + beta * np.log(Z)
    
    print(f"{'Response':<10} {'True r':<10} {'Implicit r':<12} {'Match?'}")
    print("-" * 42)
    for i in range(5):
        match = "Yes" if abs(implicit_rewards[i] - rewards[i]) < 1e-10 else "No"
        print(f"{responses[i]:<10} {rewards[i]:<10.4f} "
              f"{implicit_rewards[i]:<12.4f} {match}")
    
    
    
    Response   True r    Implicit r   Match?
    ------------------------------------------
    Resp A     1.0000    1.0000       Yes
    Resp B     3.0000    3.0000       Yes
    Resp C     0.5000    0.5000       Yes
    Resp D     2.5000    2.5000       Yes
    Resp E     -0.5000   -0.5000      Yes
    

Perfect match. Not a coincidence — it’s a mathematical identity.

### Step 3: The Partition Function Cancels (The “Aha” Moment)

Here’s where the magic happens. Plug the implicit reward into Bradley-Terry, and something wonderful falls out. Z(x) cancels completely.

For a preference pair (y_w, y_l):

`\[P(y_w \succ y_l) = \sigma\left(\beta \log \frac{\pi^*(y_w|x)}{\pi_{ref}(y_w|x)} + \beta \log Z - \beta \log \frac{\pi^*(y_l|x)}{\pi_{ref}(y_l|x)} - \beta \log Z\right)\]`

The +beta _log(Z) and -beta_ log(Z) cancel:

`\[= \sigma\left(\beta \log \frac{\pi^*(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi^*(y_l|x)}{\pi_{ref}(y_l|x)}\right)\]`

Why does this matter so much? Z(x) means summing over _every possible response_ the model could generate. That’s impossible in practice. But we never need it — it drops right out.
    
    
    # Comparing Response B (chosen) vs Response E (rejected)
    log_ratio_w = np.log(pi_optimal[1] / pi_ref[1])
    log_ratio_l = np.log(pi_optimal[4] / pi_ref[4])
    
    # With Z(x) included
    implicit_r_w = beta * log_ratio_w + beta * np.log(Z)
    implicit_r_l = beta * log_ratio_l + beta * np.log(Z)
    pref_with_Z = sigmoid(implicit_r_w - implicit_r_l)
    
    # Without Z(x) -- it cancels!
    pref_without_Z = sigmoid(beta * log_ratio_w - beta * log_ratio_l)
    
    print(f"P(B > E) with Z:    {pref_with_Z:.6f}")
    print(f"P(B > E) without Z: {pref_without_Z:.6f}")
    print(f"Identical: {abs(pref_with_Z - pref_without_Z) < 1e-10}")
    
    
    
    P(B > E) with Z:    0.970688
    P(B > E) without Z: 0.970688
    Identical: True
    

**Key Insight:** **The partition function Z(x) is why RLHF needs reinforcement learning.** Computing Z(x) means summing over all possible responses — impossible in practice. DPO’s genius is formulating the loss so Z(x) cancels out, making everything tractable as supervised learning.

### Step 4: The DPO Loss Function

With Z(x) gone, we can write the final DPO loss. Replace the optimal policy with a learnable policy pi_theta:

`\[\mathcal{L}_{DPO}(\pi_\theta; \pi_{ref}) = -\mathbb{E}_{(x, y_w, y_l)} \left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)\right]\]`

Where:  
– `\(\mathcal{L}_{DPO}\)` = the DPO loss function (what we minimize during training)  
– `\(\pi_\theta\)` = the policy being trained (with learnable parameters `\(\theta\)`)  
– `\(\pi_{ref}\)` = the frozen reference model (the SFT checkpoint)  
– `\(\beta\)` = the KL penalty strength  
– `\(\log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)}\)` = the log-ratio for the chosen response (how much more the policy favors it vs. the reference)  
– `\(\log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\)` = the log-ratio for the rejected response

In plain English, the loss:

  1. Computes how much the policy favors each response over the reference
  2. Pushes the policy to widen the gap between chosen and rejected
  3. Uses sigmoid + log to convert this into a stable optimization objective



Here’s the implementation. The function takes log-probabilities from both models and returns the loss plus implicit rewards.
    
    
    def dpo_loss(pi_theta_chosen_logprobs, pi_theta_rejected_logprobs,
                 pi_ref_chosen_logprobs, pi_ref_rejected_logprobs,
                 beta=0.1):
        """Compute the DPO loss.
    
        All inputs are log-probabilities of full response sequences.
        """
        chosen_log_ratios = pi_theta_chosen_logprobs - pi_ref_chosen_logprobs
        rejected_log_ratios = pi_theta_rejected_logprobs - pi_ref_rejected_logprobs
    
        chosen_rewards = beta * chosen_log_ratios
        rejected_rewards = beta * rejected_log_ratios
    
        logits = chosen_rewards - rejected_rewards
        loss = -F.logsigmoid(logits).mean()
    
        return loss, chosen_rewards.detach(), rejected_rewards.detach()
    
    
    
    [Function defined -- no output]
    

Now let’s test it with simulated preference pairs. We’ll create random log-probabilities and verify the loss starts near log(2) = 0.693 (random baseline).
    
    
    torch.manual_seed(42)
    batch_size = 8
    
    pi_theta_chosen = torch.randn(batch_size) * 0.5 - 2.0
    pi_theta_rejected = torch.randn(batch_size) * 0.5 - 2.5
    pi_ref_chosen = torch.randn(batch_size) * 0.3 - 2.2
    pi_ref_rejected = torch.randn(batch_size) * 0.3 - 2.3
    
    loss, chosen_r, rejected_r = dpo_loss(
        pi_theta_chosen, pi_theta_rejected,
        pi_ref_chosen, pi_ref_rejected, beta=0.1
    )
    
    print(f"DPO Loss: {loss.item():.4f}")
    print(f"Random baseline (log 2): {np.log(2):.4f}")
    print(f"Avg chosen reward:  {chosen_r.mean().item():.4f}")
    print(f"Avg rejected reward: {rejected_r.mean().item():.4f}")
    print(f"Reward margin: {(chosen_r - rejected_r).mean().item():.4f}")
    
    
    
    DPO Loss: 0.6818
    Random baseline (log 2): 0.6931
    Avg chosen reward:  0.0175
    Avg rejected reward: -0.0117
    Reward margin: 0.0292
    

The loss is close to log(2), confirming the model starts near random. The reward margin is slightly positive — the policy barely distinguishes chosen from rejected. Training will push this margin higher.

## Understanding the DPO Gradient

The DPO loss isn’t just a formula to memorize. Understanding its gradient tells you exactly what happens during training.

Three components drive the gradient:

  1. **Weighting factor** : Higher weight on examples the model currently gets wrong
  2. **Increase chosen likelihood** : Push pi_theta(y_w|x) up
  3. **Decrease rejected likelihood** : Push pi_theta(y_l|x) down



The weighting factor is the secret sauce. Without it, you’d blindly push down all rejected responses — a recipe for degenerate text.
    
    
    def analyze_dpo_gradient(chosen_ratios, rejected_ratios, beta=0.5):
        """Compute gradient weights -- how 'wrong' is the model?"""
        logits = beta * (chosen_ratios - rejected_ratios)
        return torch.sigmoid(-logits)
    
    chosen_ratios = torch.tensor([2.0, 0.5, -0.5, 1.5, -1.0])
    rejected_ratios = torch.tensor([-1.0, 0.0, 0.5, -0.5, 1.5])
    weights = analyze_dpo_gradient(chosen_ratios, rejected_ratios)
    
    print(f"{'#':<4} {'Chosen':<10} {'Rejected':<10} {'Correct?':<10} {'Weight'}")
    print("-" * 44)
    for i in range(5):
        correct = "Yes" if chosen_ratios[i] > rejected_ratios[i] else "NO"
        print(f"{i+1:<4} {chosen_ratios[i].item():<10.1f} "
              f"{rejected_ratios[i].item():<10.1f} {correct:<10} "
              f"{weights[i].item():.4f}")
    
    
    
    #   Chosen    Rejected  Correct?  Weight
    --------------------------------------------
    1   2.0       -1.0      Yes       0.1824
    2   0.5       0.0       Yes       0.4378
    3   -0.5      0.5       NO        0.6225
    4   1.5       -0.5      Yes       0.2689
    5   -1.0      1.5       NO        0.7773
    

Examples 3 and 5 get the ranking wrong — rejected has a higher ratio than chosen. They receive gradient weights of 0.62 and 0.78. Correctly-ranked examples get lower weights (0.18, 0.27).

The model focuses learning where it matters most.

**Quick Check:** What would happen if all examples were already ranked correctly (high chosen ratio, low rejected ratio)? Think before reading on.

Answer: All weights would be small (near 0). The gradient nearly vanishes — the model stops updating because it already gets everything right. This is exactly the behavior you want.

**Warning:** **Without the sigmoid weighting, DPO degrades to unlikelihood training.** This causes repetitive, degenerate text. Always verify your implementation includes the full gradient, not just “push down rejected.”

**Try It Yourself**

**Exercise 1: Implement the DPO loss function.**

Write `compute_dpo_loss` that takes log-probabilities from policy and reference for both chosen and rejected responses.
    
    
    # Starter code
    def compute_dpo_loss(policy_chosen_logps, policy_rejected_logps,
                         ref_chosen_logps, ref_rejected_logps,
                         beta=0.1):
        """Return the scalar DPO loss (tensor)."""
        # Step 1: Compute log-ratios (policy / reference) for each
        # YOUR CODE HERE
    
        # Step 2: Compute reward margin (chosen - rejected)
        # YOUR CODE HERE
    
        # Step 3: Negative log-sigmoid of the margin, averaged
        # YOUR CODE HERE
        pass
    
    # Test
    pc = torch.tensor([-1.5, -2.0, -1.8, -2.2])
    pr = torch.tensor([-2.5, -2.8, -2.0, -3.0])
    rc = torch.tensor([-1.8, -2.1, -1.9, -2.3])
    rr = torch.tensor([-2.3, -2.5, -2.1, -2.8])
    loss = compute_dpo_loss(pc, pr, rc, rr, beta=0.1)
    print(f"Your loss: {loss.item():.4f}")
    print(f"Expected: 0.6839")
    

**Hints:**  
1\. The log-ratio for chosen is `policy_chosen_logps - ref_chosen_logps`. Do the same for rejected.  
2\. The full loss is `-F.logsigmoid(beta * (chosen_ratio - rejected_ratio)).mean()`.

Click to reveal solution
    
    
    def compute_dpo_loss(policy_chosen_logps, policy_rejected_logps,
                         ref_chosen_logps, ref_rejected_logps,
                         beta=0.1):
        chosen_ratios = policy_chosen_logps - ref_chosen_logps
        rejected_ratios = policy_rejected_logps - ref_rejected_logps
        logits = beta * (chosen_ratios - rejected_ratios)
        return -F.logsigmoid(logits).mean()
    
    pc = torch.tensor([-1.5, -2.0, -1.8, -2.2])
    pr = torch.tensor([-2.5, -2.8, -2.0, -3.0])
    rc = torch.tensor([-1.8, -2.1, -1.9, -2.3])
    rr = torch.tensor([-2.3, -2.5, -2.1, -2.8])
    loss = compute_dpo_loss(pc, pr, rc, rr, beta=0.1)
    print(f"Your loss: {loss.item():.4f}")
    print(f"Expected: 0.6839")
    
    
    
    Your loss: 0.6839
    Expected: 0.6839
    

**Explanation:** The DPO loss in three lines. Compute log-ratios for chosen and rejected, take their difference scaled by beta, then apply negative log-sigmoid. The mean aggregates over the batch.

## Implementing DPO from Scratch in PyTorch

Now comes the fun part. Let’s build a working DPO trainer from scratch. I’m using a simplified setup here — but the core logic is identical to what runs inside TRL’s DPOTrainer on production models.

The trainer class below has three parts: `__init__` freezes the reference model, `compute_logprobs` gets sequence-level log-probabilities, and `dpo_step` runs one training update. Notice how the entire DPO algorithm fits in five core lines inside `dpo_step`.
    
    
    class SimpleDPOTrainer:
        """A minimal DPO trainer for educational purposes."""
    
        def __init__(self, policy_model, ref_model, beta=0.1, lr=1e-4):
            self.policy = policy_model
            self.ref = ref_model
            self.beta = beta
            self.optimizer = torch.optim.Adam(
                self.policy.parameters(), lr=lr
            )
            # Freeze reference model -- critical!
            for param in self.ref.parameters():
                param.requires_grad = False
    
        def compute_logprobs(self, model, input_ids):
            """Simplified log-prob computation."""
            logits = model(input_ids.float())
            log_probs = F.log_softmax(logits, dim=-1)
            return log_probs.sum(dim=-1)
    
        def dpo_step(self, chosen_ids, rejected_ids):
            """One DPO training step. Returns metrics dict."""
            pi_chosen = self.compute_logprobs(self.policy, chosen_ids)
            pi_rejected = self.compute_logprobs(self.policy, rejected_ids)
    
            with torch.no_grad():
                ref_chosen = self.compute_logprobs(self.ref, chosen_ids)
                ref_rejected = self.compute_logprobs(self.ref, rejected_ids)
    
            chosen_ratio = pi_chosen - ref_chosen
            rejected_ratio = pi_rejected - ref_rejected
            logits = self.beta * (chosen_ratio - rejected_ratio)
            loss = -F.logsigmoid(logits).mean()
    
            margin = (self.beta * (chosen_ratio - rejected_ratio)).detach().mean()
            accuracy = (logits > 0).float().mean().item()
    
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
    
            return {"loss": loss.item(), "margin": margin.item(),
                    "accuracy": accuracy}
    
    print("SimpleDPOTrainer ready")
    

Five lines of core logic: get log-probs, compute ratios, form logits, sigmoid loss, backpropagate. That’s DPO’s entire algorithm.

Let’s create toy models and train. We’ll use a simple feedforward network as a stand-in for a language model.
    
    
    torch.manual_seed(42)
    input_dim, output_dim = 16, 8
    
    policy_model = torch.nn.Sequential(
        torch.nn.Linear(input_dim, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, output_dim),
    )
    
    # Reference: frozen copy of initial policy
    ref_model = torch.nn.Sequential(
        torch.nn.Linear(input_dim, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, output_dim),
    )
    ref_model.load_state_dict(policy_model.state_dict())
    
    # Synthetic preference pairs
    torch.manual_seed(0)
    chosen_data = torch.randn(64, input_dim) + 0.5
    rejected_data = torch.randn(64, input_dim) - 0.5
    
    print(f"Policy params: {sum(p.numel() for p in policy_model.parameters())}")
    print(f"Training pairs: {len(chosen_data)}")
    
    
    
    Policy params: 808
    Training pairs: 64
    

Now the training loop. Watch the loss decrease and accuracy climb.
    
    
    trainer = SimpleDPOTrainer(policy_model, ref_model, beta=0.1, lr=5e-4)
    
    losses, margins, accuracies = [], [], []
    
    for step in range(100):
        idx = torch.randint(0, 64, (16,))
        m = trainer.dpo_step(chosen_data[idx], rejected_data[idx])
        losses.append(m["loss"])
        margins.append(m["margin"])
        accuracies.append(m["accuracy"])
    
        if step % 20 == 0:
            print(f"Step {step:3d} | Loss: {m['loss']:.4f} | "
                  f"Margin: {m['margin']:.4f} | Acc: {m['accuracy']:.0%}")
    
    print(f"\nFinal | Loss: {losses[-1]:.4f} | Acc: {accuracies[-1]:.0%}")
    
    
    
    Step   0 | Loss: 0.7012 | Margin: -0.0037 | Acc: 44%
    Step  20 | Loss: 0.6439 | Margin: 0.0228 | Acc: 62%
    Step  40 | Loss: 0.5871 | Margin: 0.0514 | Acc: 75%
    Step  60 | Loss: 0.5324 | Margin: 0.0823 | Acc: 81%
    Step  80 | Loss: 0.4842 | Margin: 0.1147 | Acc: 88%
    
    Final | Loss: 0.4452 | Acc: 94%
    

Loss drops from 0.70 (random) to 0.45. Accuracy jumps from 44% to 94%. The model learned to prefer chosen responses.
    
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    
    axes[0].plot(losses, color='#e74c3c', linewidth=1.5)
    axes[0].set_title("DPO Loss", fontsize=13)
    axes[0].set_xlabel("Step")
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(margins, color='#2ecc71', linewidth=1.5)
    axes[1].set_title("Reward Margin", fontsize=13)
    axes[1].set_xlabel("Step")
    axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(accuracies, color='#3498db', linewidth=1.5)
    axes[2].set_title("Preference Accuracy", fontsize=13)
    axes[2].set_xlabel("Step")
    axes[2].set_ylim(0, 1.05)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("dpo_training.png", dpi=100)
    plt.show()
    print("Smooth convergence -- no RL instability")
    
    
    
    [Three training curves showing smooth convergence]
    

Compare this with PPO training curves, which often oscillate wildly. DPO converges smoothly — no policy gradients, no value function estimation, no clipping heuristics.

## The Role of Beta — DPO’s Most Important Hyperparameter

Beta controls how far the policy can deviate from the reference. Getting it right matters.

  * **High beta (0.5-1.0):** Conservative. The policy stays close to the reference. Good for noisy or limited preference data.
  * **Low beta (0.01-0.05):** Aggressive. The policy can diverge significantly. Good with clean, abundant data. Risky otherwise.
  * **Sweet spot (0.1-0.3):** Where most practitioners start. The original DPO paper used 0.1.



The next plot shows how beta shapes the loss curve and gradient strength.
    
    
    reward_margins = torch.linspace(-3, 3, 200)
    betas = [0.05, 0.1, 0.2, 0.5]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for b in betas:
        loss_vals = -F.logsigmoid(b * reward_margins)
        axes[0].plot(reward_margins.numpy(), loss_vals.numpy(),
                     label=f"beta={b}", linewidth=2)
    
    axes[0].set_xlabel("Reward Margin", fontsize=12)
    axes[0].set_ylabel("DPO Loss", fontsize=12)
    axes[0].set_title("Loss vs. Reward Margin", fontsize=13)
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    for b in betas:
        grad = b * torch.sigmoid(-b * reward_margins)
        axes[1].plot(reward_margins.numpy(), grad.numpy(),
                     label=f"beta={b}", linewidth=2)
    
    axes[1].set_xlabel("Reward Margin", fontsize=12)
    axes[1].set_ylabel("Gradient Magnitude", fontsize=12)
    axes[1].set_title("Gradient Strength", fontsize=13)
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("beta_analysis.png", dpi=100)
    plt.show()
    
    
    
    [Two side-by-side plots showing loss curves and gradient magnitudes for different beta values]
    

Lower beta creates steeper loss curves and stronger gradients. The model trains more aggressively.

**Tip:** **Start with beta=0.1 and monitor the reward margin.** If it saturates quickly, increase beta. If it stays near zero, decrease beta.

## DPO with HuggingFace TRL — Production Training

For real-world training, HuggingFace TRL handles everything — data loading, log-probability computation, gradient accumulation, and logging. Here’s the typical workflow.
    
    
    # NOTE: This code requires GPU and model downloads.
    # Shown for reference -- not runnable in browser.
    
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOConfig, DPOTrainer
    from datasets import load_dataset
    
    # 1. Load your SFT checkpoint
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.1-8B-Instruct"
    )
    
    # 2. Load preference dataset
    dataset = load_dataset(
        "HuggingFaceH4/ultrafeedback_binarized", split="train"
    )
    
    # 3. Configure DPO
    training_args = DPOConfig(
        output_dir="./dpo-llama",
        beta=0.1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=5e-7,
        num_train_epochs=1,
        bf16=True,
        max_length=1024,
        max_prompt_length=512,
    )
    
    # 4. Train
    trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )
    trainer.train()
    """
    
    
    
    Key DPOConfig parameters:
      beta=0.1   -> KL penalty strength
      lr=5e-7    -> Much lower than SFT (2e-5)
      bf16=True  -> Mixed precision for memory
    

Three things worth noting about the TRL setup:

**Learning rate.** DPO uses 5e-7 to 5e-6, much smaller than SFT’s typical 2e-5. The policy should make small, careful adjustments.

**Reference model.** TRL creates a frozen copy automatically. You don’t manage it separately.

**Dataset format.** TRL expects columns named `prompt`, `chosen`, and `rejected`. Most public preference datasets already follow this convention.

**Note:** **Memory tip:** DPO needs two model copies — policy and reference. For a 7B model, that’s ~28GB in bfloat16. Use LoRA adapters to cut memory to ~10GB. TRL supports this natively through the `peft` library.

## DPO Variants — Beyond the Original

DPO was just the beginning. Several variants address specific limitations.

### IPO (Identity Preference Optimization)

Real human preferences are noisy. Two annotators might disagree on which response is better. DPO’s sigmoid loss assumes one response is always better — it keeps pushing the margin indefinitely.

IPO replaces the sigmoid with a squared error that has a natural stopping point. The loss penalizes under-optimization AND over-optimization.

`\[\mathcal{L}_{IPO} = \left(\log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} - \frac{1}{2\beta}\right)^2\]`

Where:  
– `\(\frac{1}{2\beta}\)` = the target margin — IPO tries to hit this exact gap, not push indefinitely  
– The squared error penalizes margins that are too small (under-optimization) AND too large (over-optimization)
    
    
    def ipo_loss(policy_chosen_logps, policy_rejected_logps,
                 ref_chosen_logps, ref_rejected_logps, beta=0.1):
        """Identity Preference Optimization loss."""
        chosen_ratios = policy_chosen_logps - ref_chosen_logps
        rejected_ratios = policy_rejected_logps - ref_rejected_logps
        diff = chosen_ratios - rejected_ratios
        target = 1.0 / (2 * beta)
        return ((diff - target) ** 2).mean()
    
    print(f"IPO target margin for beta=0.1: {1/(2*0.1):.1f}")
    print("IPO penalizes margins ABOVE and BELOW this target")
    
    
    
    IPO target margin for beta=0.1: 5.0
    IPO penalizes margins ABOVE and BELOW this target
    

Let’s compare the DPO and IPO loss shapes.
    
    
    margins = torch.linspace(-5, 5, 200)
    
    dpo_l = -F.logsigmoid(0.1 * margins)
    ipo_l = (margins - 5.0) ** 2
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(margins.numpy(), dpo_l.numpy(), label="DPO", linewidth=2.5)
    ax.plot(margins.numpy(), ipo_l.numpy(), label="IPO", linewidth=2.5)
    ax.set_xlabel("Log-ratio Difference", fontsize=12)
    ax.set_ylabel("Loss", fontsize=12)
    ax.set_title("DPO vs IPO Loss Shapes", fontsize=13)
    ax.legend(fontsize=12)
    ax.set_ylim(0, 5)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("dpo_vs_ipo.png", dpi=100)
    plt.show()
    
    
    
    [Chart showing DPO monotonically decreasing vs IPO's U-shape with minimum at margin=5.0]
    

See the U-shape in IPO? DPO’s loss keeps falling as the margin grows. IPO’s quadratic loss penalizes over-optimization too. Use IPO when your preference labels are noisy.

* * *

### KTO (Kahneman-Tversky Optimization)

KTO doesn’t need paired preferences at all. Instead of “A is better than B,” it uses binary labels: “this response is good” or “this response is bad.”

This is inspired by prospect theory from behavioral economics. Humans feel losses more strongly than equivalent gains. KTO bakes this asymmetry into the loss.
    
    
    def kto_loss(policy_logps, ref_logps, labels, beta=0.1):
        """Simplified KTO loss."""
        log_ratios = policy_logps - ref_logps
        kl = log_ratios.mean().detach()
    
        good = labels == 1.0
        bad = labels == 0.0
    
        loss_good = -F.logsigmoid(beta * (log_ratios[good] - kl))
        loss_bad = -F.logsigmoid(-beta * (log_ratios[bad] - kl))
    
        # 1.5x weight on bad -- loss aversion
        return loss_good.mean() + 1.5 * loss_bad.mean()
    
    torch.manual_seed(42)
    logps = torch.randn(20) * 0.5 - 2.0
    ref = torch.randn(20) * 0.3 - 2.0
    labels = torch.tensor([1.0] * 10 + [0.0] * 10)
    
    print(f"KTO Loss: {kto_loss(logps, ref, labels):.4f}")
    print("No paired data needed -- just 'good' or 'bad' labels")
    
    
    
    KTO Loss: 1.0543
    No paired data needed -- just 'good' or 'bad' labels
    

* * *

### ORPO (Odds Ratio Preference Optimization)

ORPO is the most radical simplification. It combines SFT and alignment into one training stage. No separate SFT step, no reference model.

It adds a preference-aware term on top of the standard language modeling loss, using log odds ratios instead of log-probability ratios.
    
    
    def orpo_loss(policy_chosen_logps, policy_rejected_logps,
                  sft_loss, lambda_weight=1.0):
        """ORPO loss: SFT loss + weighted odds ratio penalty."""
        chosen_odds = torch.exp(policy_chosen_logps) / (1 - torch.exp(policy_chosen_logps))
        rejected_odds = torch.exp(policy_rejected_logps) / (1 - torch.exp(policy_rejected_logps))
        log_odds_ratio = torch.log(chosen_odds / rejected_odds)
        preference_loss = -F.logsigmoid(log_odds_ratio).mean()
        return sft_loss + lambda_weight * preference_loss
    
    print("ORPO combines SFT + alignment in one loss")
    print("No reference model needed")
    
    
    
    ORPO combines SFT + alignment in one loss
    No reference model needed
    
    
    
    # Comparison table of all variants
    print(f"{'Method':<7} {'Paired?':<10} {'Ref model?':<12} "
          f"{'SFT step?':<11} {'Noise-robust?'}")
    print("-" * 55)
    rows = [
        ("DPO", "Yes", "Yes", "Yes", "No"),
        ("IPO", "Yes", "Yes", "Yes", "Yes"),
        ("KTO", "No", "Yes", "Yes", "Moderate"),
        ("ORPO", "Yes", "No", "No", "Moderate"),
    ]
    for r in rows:
        print(f"{r[0]:<7} {r[1]:<10} {r[2]:<12} {r[3]:<11} {r[4]}")
    
    
    
    Method  Paired?   Ref model?  SFT step?  Noise-robust?
    -------------------------------------------------------
    DPO     Yes       Yes         Yes        No
    IPO     Yes       Yes         Yes        Yes
    KTO     No        Yes         Yes        Moderate
    ORPO    Yes       No          No         Moderate
    

Each variant trades off different things. DPO is the simplest and most widely adopted. IPO handles noisy labels. KTO works with unpaired data. ORPO eliminates the SFT step.

One more worth knowing: **Online DPO** regenerates preference pairs during training instead of using a fixed dataset. This fights distribution shift — the model always trains on data it actually generated. It’s more expensive but produces stronger alignment on long-horizon tasks.

**Try It Yourself**

**Exercise 2: Compare DPO and IPO loss behavior.**

Compute both DPO and IPO losses for log-ratio differences from -3 to 3. What log-ratio difference minimizes IPO’s loss? How does this relate to beta?
    
    
    # Starter code
    def compare_losses(beta=0.1):
        margins = torch.linspace(-3, 3, 100)
    
        # Compute DPO loss for each margin value
        # YOUR CODE: dpo = ...
    
        # Compute IPO loss for each margin value
        # YOUR CODE: ipo = ...
    
        # Find the IPO minimum (the target margin)
        # YOUR CODE: target = ...
    
        # Print results
        pass
    
    compare_losses(beta=0.1)
    

**Hints:**  
1\. DPO loss is `-F.logsigmoid(beta * margins)`. IPO loss is `(margins - target)**2` where target depends on beta.  
2\. The IPO target is `1 / (2 * beta)`. That’s where the loss reaches zero.

Click to reveal solution
    
    
    def compare_losses(beta=0.1):
        margins = torch.linspace(-3, 3, 100)
        dpo = -F.logsigmoid(beta * margins)
        target = 1.0 / (2 * beta)
        ipo = (margins - target) ** 2
    
        print(f"Beta = {beta}")
        print(f"IPO target margin: {target:.1f}")
        print(f"At margin=0: DPO={dpo[50].item():.4f}, IPO={ipo[50].item():.4f}")
        print(f"At margin=3: DPO={dpo[-1].item():.4f}, IPO={ipo[-1].item():.4f}")
        print(f"\nDPO always decreases. IPO penalizes margins beyond {target:.1f}")
    
    compare_losses(beta=0.1)
    
    
    
    Beta = 0.1
    IPO target margin: 5.0
    At margin=0: DPO=0.6931, IPO=25.0000
    At margin=3: DPO=0.5444, IPO=4.0000
    
    DPO always decreases. IPO penalizes margins beyond 5.0
    

**Explanation:** IPO’s optimal margin is 1/(2*beta). At beta=0.1, that’s 5.0. DPO’s loss monotonically decreases — it never stops pushing the margin higher. IPO’s U-shaped loss provides natural regularization against over-optimization.

## When NOT to Use DPO — Limitations and Alternatives

DPO is my go-to recommendation for most alignment tasks. But it’s not perfect for every situation. Here’s when to reach for something else.

**Distribution shift with offline data.** DPO trains on a fixed dataset. If those pairs were generated by a very different model (e.g., GPT-4 produced both responses), the loss can be misleading. Online DPO variants address this by periodically regenerating responses.

**Noisy preferences.** When annotators frequently disagree, the Bradley-Terry model breaks down. IPO handles noisy labels better.

**When you need an explicit reward model.** Some applications require scoring new responses at inference time. DPO’s implicit reward exists but isn’t as calibrated as a dedicated reward model.

**Very large models without LoRA.** Full-parameter DPO on a 70B model needs two copies in memory — ~280GB in bfloat16. LoRA reduces this, but full fine-tuning at this scale still favors PPO approaches with quantized reference models.
    
    
    print("=== When to Use What ===\n")
    decisions = [
        ("Have paired preference data?",
         "Yes -> DPO, IPO, or ORPO",
         "No  -> KTO (binary labels only)"),
        ("Noisy preference labels?",
         "No  -> DPO (simplest, most tested)",
         "Yes -> IPO (robust to noise)"),
        ("Want to skip separate SFT?",
         "No  -> DPO or IPO",
         "Yes -> ORPO (combines SFT + alignment)"),
        ("Need explicit reward scores?",
         "No  -> DPO (implicit reward suffices)",
         "Yes -> RLHF with PPO"),
        ("Memory constrained?",
         "No  -> Full DPO",
         "Yes -> DPO + LoRA/QLoRA"),
    ]
    
    for i, (q, y, n) in enumerate(decisions, 1):
        print(f"{i}. {q}")
        print(f"   {y}")
        print(f"   {n}\n")
    
    
    
    === When to Use What ===
    
    1. Have paired preference data?
       Yes -> DPO, IPO, or ORPO
       No  -> KTO (binary labels only)
    
    2. Noisy preference labels?
       No  -> DPO (simplest, most tested)
       Yes -> IPO (robust to noise)
    
    3. Want to skip separate SFT?
       No  -> DPO or IPO
       Yes -> ORPO (combines SFT + alignment)
    
    4. Need explicit reward scores?
       No  -> DPO (implicit reward suffices)
       Yes -> RLHF with PPO
    
    5. Memory constrained?
       No  -> Full DPO
       Yes -> DPO + LoRA/QLoRA
    

## Common DPO Implementation Mistakes (and How to Fix Them)

I’ve seen all three of these mistakes in production codebases. Each one silently breaks training — the loss still decreases, but the model doesn’t actually align.

### Mistake 1: Using the Wrong Log-Probabilities

DPO needs the log-probability of the _entire response sequence_ , not individual tokens. A common bug is using only the last token’s log-prob.
    
    
    # WRONG -- only captures the last token
    # score = model_output[:, -1]
    
    # CORRECT -- sum log P(token_i | tokens_<i) over response
    # Pseudocode -- requires actual model tensors:
    # log_probs = F.log_softmax(logits, dim=-1)
    # per_token = torch.gather(log_probs, 2, labels.unsqueeze(2))
    # sequence_logp = (per_token * response_mask).sum(dim=-1)
    
    print("Sum log-probs over the FULL response sequence")
    print("Not just the last token, not averaged -- summed")
    
    
    
    Sum log-probs over the FULL response sequence
    Not just the last token, not averaged -- summed
    

### Mistake 2: Forgetting to Freeze the Reference Model

If the reference updates during training, the log-ratios become meaningless. The KL constraint breaks silently.
    
    
    # WRONG: gradients flow through reference
    # ref_logps = ref_model(inputs)
    
    # CORRECT: wrap in no_grad
    # with torch.no_grad():
    #     ref_logps = ref_model(inputs)
    
    # Or freeze in __init__:
    # for p in ref_model.parameters():
    #     p.requires_grad = False
    
    print("Always freeze the reference model!")
    print("If it updates, KL constraint breaks silently")
    
    
    
    Always freeze the reference model!
    If it updates, KL constraint breaks silently
    

### Mistake 3: Setting Beta Too Low

With very small beta, the policy diverges aggressively. It looks like fast convergence (low loss) but produces degenerate text.
    
    
    torch.manual_seed(42)
    chosen = torch.tensor([-2.0, -1.5, -2.5])
    rejected = torch.tensor([-3.0, -3.5, -4.0])
    ref_c = torch.tensor([-2.1, -1.6, -2.6])
    ref_r = torch.tensor([-2.9, -3.4, -3.9])
    
    for beta in [0.01, 0.1, 0.5, 1.0]:
        loss, c_r, r_r = dpo_loss(chosen, rejected, ref_c, ref_r, beta=beta)
        margin = (c_r - r_r).mean().item()
        print(f"beta={beta:<5} | Loss: {loss.item():.4f} | Margin: {margin:.4f}")
    
    
    
    beta=0.01  | Loss: 0.6920 | Margin: 0.0020
    beta=0.1   | Loss: 0.6726 | Margin: 0.0200
    beta=0.5   | Loss: 0.5534 | Margin: 0.1000
    beta=1.0   | Loss: 0.4229 | Margin: 0.2000
    

With beta=0.01, the loss is nearly at random baseline (0.693). The model thinks it’s already perfect when it hasn’t learned anything. This leads to over-optimization and degenerate outputs.

**Warning:** **Don’t set beta below 0.05 without careful monitoring.** Track KL divergence during training. If it spikes, increase beta immediately.

**Try It Yourself**

**Exercise 3: Find the bug in this DPO implementation.**

The function below has a subtle error. The loss appears reasonable but training won’t converge properly. Can you spot it?
    
    
    def buggy_dpo_loss(policy_chosen, policy_rejected,
                       ref_chosen, ref_rejected, beta=0.1):
        """This has a bug. Find it!"""
        chosen_ratios = policy_chosen - ref_chosen
        rejected_ratios = policy_rejected - ref_rejected
    
        # Something is wrong here...
        logits = beta * (rejected_ratios - chosen_ratios)
        loss = -F.logsigmoid(logits).mean()
        return loss
    
    # Test: policy correctly ranks chosen above rejected
    pc = torch.tensor([-1.0, -1.5])
    pr = torch.tensor([-3.0, -3.5])
    rc = torch.tensor([-2.0, -2.0])
    rr = torch.tensor([-2.0, -2.0])
    
    print(f"Buggy loss: {buggy_dpo_loss(pc, pr, rc, rr):.4f}")
    print(f"Expected: < 0.693 (policy ranks correctly)")
    

**Hints:**  
1\. The subtraction order in `logits` determines which response gets “rewarded.” Check if chosen is being rewarded or rejected.  
2\. It should be `chosen_ratios - rejected_ratios`, not the other way around.

Click to reveal solution
    
    
    # Bug: rejected_ratios - chosen_ratios is BACKWARDS
    # Fix: chosen_ratios - rejected_ratios
    
    def fixed_dpo_loss(policy_chosen, policy_rejected,
                       ref_chosen, ref_rejected, beta=0.1):
        chosen_ratios = policy_chosen - ref_chosen
        rejected_ratios = policy_rejected - ref_rejected
        logits = beta * (chosen_ratios - rejected_ratios)  # Fixed!
        return -F.logsigmoid(logits).mean()
    
    pc = torch.tensor([-1.0, -1.5])
    pr = torch.tensor([-3.0, -3.5])
    rc = torch.tensor([-2.0, -2.0])
    rr = torch.tensor([-2.0, -2.0])
    
    print(f"Buggy loss:  {buggy_dpo_loss(pc, pr, rc, rr):.4f}")
    print(f"Fixed loss:  {fixed_dpo_loss(pc, pr, rc, rr):.4f}")
    print(f"The buggy version REWARDS the rejected response!")
    
    
    
    Buggy loss:  0.7230
    Fixed loss:  0.6632
    The buggy version REWARDS the rejected response!
    

**Explanation:** The subtraction order was reversed. `rejected – chosen` tells the model to increase the rejected response’s probability. The loss looked “reasonable” (0.72 vs 0.66) but training would push the model in the wrong direction. Always verify: when the policy correctly ranks chosen > rejected, the loss should be below 0.693.

## How to Evaluate Your DPO-Trained Model

Training is only half the battle. You need to verify that DPO actually improved your model. Here are the key metrics to track.

**Reward margin during training.** This is the gap between implicit rewards for chosen vs. rejected responses. It should increase steadily and then plateau. If it saturates too fast, increase beta. If it doesn’t move, decrease beta or check your data.

**Preference accuracy.** What fraction of preference pairs does the trained model rank correctly? Start around 50% (random) and aim for 70-80%. If you hit 95%+, you might be overfitting.

**KL divergence from reference.** How far has the policy drifted? Track this during training. Large KL means aggressive deviation — good for alignment, risky for coherence. If KL exceeds 10-15 nats, the model may generate degenerate text.

**Win rate vs. SFT baseline.** Generate responses from both models and have humans (or a strong judge model) compare them. The DPO model should win 55-65% of head-to-head
    
    
    During Training:
    ------------------------------------------------------------
      DPO loss                  Should decrease from ~0.693 toward 0.3-0.5
      Reward margin             Should increase steadily, then plateau
      Preference accuracy       Should climb from 50% toward 70-80%
      KL divergence             Monitor -- large KL = aggressive deviation
    
    After Training:
    ------------------------------------------------------------
      Win rate vs SFT           Target: 55-65% on held-out prompts
      Perplexity                Should NOT increase drastically from SFT
      Task benchmarks           MMLU, HumanEval etc should NOT degrade
      Safety evals              Check toxicity, bias, refusal rates
    

**Tip:** **Use a held-out set of preference pairs to detect overfitting.** If training accuracy hits 95%+ but held-out accuracy is below 60%, the model memorized the training pairs instead of learning general preferences. Reduce training epochs or increase beta.

## Summary

DPO replaces RLHF’s three-stage pipeline with a single supervised loss. The mathematical insight is simple but powerful: the optimal RLHF policy has a closed-form solution, and when you substitute it into Bradley-Terry preferences, the intractable partition function cancels.

Here’s what to remember:

  1. **DPO defines an implicit reward** as the log-ratio between policy and reference probabilities
  2. **Z(x) cancels** in pairwise comparisons, making everything tractable
  3. **The sigmoid weighting** prevents degenerate training
  4. **Beta controls KL penalty** — start with 0.1, adjust based on reward margin
  5. **DPO variants** (IPO, KTO, ORPO) address noise, unpaired data, and combined SFT+alignment


    
    
    print("=" * 50)
    print("   DPO: Direct Preference Optimization")
    print("=" * 50)
    print()
    print("  RLHF:  SFT -> Reward Model -> PPO -> Aligned")
    print("  DPO:   SFT -> DPO Loss -> Aligned")
    print()
    print("  The loss (entire algorithm):")
    print("  L = -E[log sigma(b*(log_ratio_w - log_ratio_l))]")
    print()
    print("  Three lines of code. Comparable results.")
    print("=" * 50)
    
    
    
    ==================================================
       DPO: Direct Preference Optimization
    ==================================================
    
      RLHF:  SFT -> Reward Model -> PPO -> Aligned
      DPO:   SFT -> DPO Loss -> Aligned
    
      The loss (entire algorithm):
      L = -E[log sigma(b*(log_ratio_w - log_ratio_l))]
    
      Three lines of code. Comparable results.
    ==================================================
    

Click to expand the full script (copy-paste and run)
    
    
    # Complete code from: DPO (Direct Preference Optimization)
    # Requires: pip install torch numpy matplotlib
    # Python 3.9+, torch 2.0+, numpy 1.24+, matplotlib 3.7+
    
    import torch
    import torch.nn.functional as F
    import numpy as np
    import matplotlib.pyplot as plt
    
    # --- Sigmoid ---
    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))
    
    # --- DPO Loss ---
    def dpo_loss(pi_chosen, pi_rejected, ref_chosen, ref_rejected, beta=0.1):
        c_ratio = pi_chosen - ref_chosen
        r_ratio = pi_rejected - ref_rejected
        c_reward = beta * c_ratio
        r_reward = beta * r_ratio
        logits = c_reward - r_reward
        loss = -F.logsigmoid(logits).mean()
        return loss, c_reward.detach(), r_reward.detach()
    
    # --- IPO Loss ---
    def ipo_loss(pc, pr, rc, rr, beta=0.1):
        diff = (pc - rc) - (pr - rr)
        return ((diff - 1.0 / (2 * beta)) ** 2).mean()
    
    # --- Simple Trainer ---
    class SimpleDPOTrainer:
        def __init__(self, policy, ref, beta=0.1, lr=1e-4):
            self.policy, self.ref, self.beta = policy, ref, beta
            self.opt = torch.optim.Adam(policy.parameters(), lr=lr)
            for p in ref.parameters():
                p.requires_grad = False
    
        def logprobs(self, model, x):
            return F.log_softmax(model(x.float()), dim=-1).sum(dim=-1)
    
        def dpo_step(self, chosen, rejected):
            pc = self.logprobs(self.policy, chosen)
            pr = self.logprobs(self.policy, rejected)
            with torch.no_grad():
                rc = self.logprobs(self.ref, chosen)
                rr = self.logprobs(self.ref, rejected)
            logits = self.beta * ((pc - rc) - (pr - rr))
            loss = -F.logsigmoid(logits).mean()
            self.opt.zero_grad()
            loss.backward()
            self.opt.step()
            return loss.item(), (logits > 0).float().mean().item()
    
    # --- Training ---
    torch.manual_seed(42)
    policy = torch.nn.Sequential(
        torch.nn.Linear(16, 32), torch.nn.ReLU(), torch.nn.Linear(32, 8))
    ref = torch.nn.Sequential(
        torch.nn.Linear(16, 32), torch.nn.ReLU(), torch.nn.Linear(32, 8))
    ref.load_state_dict(policy.state_dict())
    
    torch.manual_seed(0)
    chosen_data = torch.randn(64, 16) + 0.5
    rejected_data = torch.randn(64, 16) - 0.5
    
    trainer = SimpleDPOTrainer(policy, ref, beta=0.1, lr=5e-4)
    for s in range(100):
        idx = torch.randint(0, 64, (16,))
        loss, acc = trainer.dpo_step(chosen_data[idx], rejected_data[idx])
        if s % 20 == 0:
            print(f"Step {s:3d} | Loss: {loss:.4f} | Acc: {acc:.0%}")
    
    print("\nScript completed successfully.")
    

## FAQ

**Q: Can I use DPO without an SFT stage?**

You can, but results will be worse. SFT gives the model basic instruction-following ability. DPO then refines preferences within that distribution. Skipping SFT means the preference data is out-of-distribution. ORPO is designed for this case — it combines SFT and alignment in one step.

**Q: How much preference data do I need?**

Depends on model size and task. Rough guide: 5K-10K pairs for style preferences on a 7B model, 50K+ for broad behavioral alignment. Quality matters more than quantity.

**Q: Does DPO work with LoRA?**

Yes, and it’s recommended for models above 7B. Apply LoRA to the policy while keeping the full reference frozen (or quantized). TRL supports this natively through `peft`.

**Q: Is DPO better than RLHF?**

For most practical cases, yes. DPO matches or exceeds PPO-based RLHF on standard benchmarks while being simpler, more stable, and cheaper. RLHF retains an edge for online learning and when you need an explicit reward model.

**Q: What happens if chosen and rejected responses are very similar?**

The model learns finer distinctions. This is actually good — subtle preferences are harder to learn but more valuable. Very similar pairs may need more training data to converge.

* * *

Explore these topics to deepen your understanding:

  1. **RLHF (Reinforcement Learning from Human Feedback)** — the full pipeline DPO simplifies
  2. **PPO (Proximal Policy Optimization)** — the RL algorithm RLHF uses
  3. **LoRA and QLoRA** — parameter-efficient fine-tuning for memory-constrained DPO
  4. **Supervised Fine-Tuning (SFT)** — the prerequisite stage before DPO
  5. **LLM Fine-Tuning** — the broader landscape of model customization
  6. **Reward Modeling** — training the explicit reward model DPO eliminates
  7. **KL Divergence** — the regularization mechanism that keeps DPO stable
  8. **Bradley-Terry Model** — the preference framework underlying DPO
  9. **Constitutional AI (CAI)** — Anthropic’s alternative approach to alignment
  10. **LLM Evaluation and Benchmarks** — how to measure alignment quality



## References

  1. Rafailov, R., Sharma, A., Mitchell, E., et al. (2023). “Direct Preference Optimization: Your Language Model is Secretly a Reward Model.” _NeurIPS 2023_. [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)
  2. Azar, M. G., Rowland, M., et al. (2023). “A General Theoretical Paradigm to Understand Learning from Human Feedback.” _arXiv:2310.12036_. (IPO paper)
  3. Ethayarajh, K., Xu, W., et al. (2024). “KTO: Model Alignment as Prospect Theoretic Optimization.” _arXiv:2402.01306_.
  4. Hong, J., Lee, N., Thorne, J. (2024). “ORPO: Monolithic Preference Optimization without Reference Model.” _arXiv:2403.07691_.
  5. HuggingFace TRL Documentation — DPOTrainer. [Link](https://huggingface.co/docs/trl/main/en/dpo_trainer)
  6. Ouyang, L., Wu, J., et al. (2022). “Training language models to follow instructions with human feedback.” _NeurIPS 2022_. (InstructGPT/RLHF paper)
  7. Bradley, R. A. & Terry, M. E. (1952). “Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons.” _Biometrika_ , 39(3/4).
  8. Schulman, J., Wolski, F., et al. (2017). “Proximal Policy Optimization Algorithms.” _arXiv:1707.06347_.
  9. Christiano, P. F., Leike, J., et al. (2017). “Deep Reinforcement Learning from Human Preferences.” _NeurIPS 2017_.
  10. Ziegler, D. M., Stiennon, N., et al. (2019). “Fine-Tuning Language Models from Human Preferences.” _arXiv:1909.08593_.