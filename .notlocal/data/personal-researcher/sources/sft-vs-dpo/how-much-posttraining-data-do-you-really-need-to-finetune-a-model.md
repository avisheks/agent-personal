---
title: "How much post‑training data do you really need to fine‑tune a model?"
source: "https://www.linkedin.com/pulse/how-much-posttraining-data-do-you-really-need-finetune-sumit-khedkar-gh2bf"
ingestedAt: "2026-05-18T00:28:23Z"
---
We all know that models pretrained on freely available internet data is of no use. The main issue is in the “entropy” of the internet data. The data is either biased or so neutral that the model cannot figure out what is right and what is wrong. 

That’s where post-training comes in. Techniques like Supervised Fine-Tuning (SFT) or Reinforcement Learning with Human Feedback (RLHF) are what really bring a model into shape, making it useful in real-world scenarios. But here’s the million-dollar question: how much SFT or RLHF data does it take to get there?

Plenty of researchers have tried to pin this down, and the results? Honestly, they’re pretty surprising.

##  The era of SFT (Superwise Fine Tuning) is over !

In mythology, we often hear stories where gods created humans — only to be astonished by what their creations could achieve. Fast-forward to today, and history seems to be repeating itself. This time, it’s us who created Large Language Models (LLMs), and every day these models continue to surprise us with their capabilities.

Not too long ago, many researchers were skeptical about the future of LLMs. The common belief was that, at such massive scales, these models would collapse under the weight of overfitting. But reality turned out to be very different. Instead of breaking down, LLMs thrived. Their accuracy improved as they scaled up — and now the leading state-of-the-art (SOTA) models boast trillions of parameters.

The logic says that bigger models need more training data. That’s certainly true when it comes to pretraining. This concept was explained in detail in this research paper : [[2203.15556] Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556?utm_source=chatgpt.com&trk=article-ssr-frontend-pulse_little-text-block)

But when it comes to post-training with SFT data, the story takes a fascinating turn.

### Multiplicative Scaling Laws:

In a breakthrough [ICLR 2024 paper](https://arxiv.org/pdf/2402.17193?trk=article-ssr-frontend-pulse_little-text-block), researchers from Google DeepMind introduced multiplicative scaling laws for calculating the amount of fine-tuning data required for LLMs.

Explaining these laws in detail is beyond the scope of this article, but in short, the scaling laws show that: “At equal quality, the amount of SFT data required drops as the model gets bigger.”

SFT-Data Calculation

Where X = model size ( params), D = SFT tokens, and r is a task/method exponent. The study shows that for the full-mode SFT Exponent range: r∈[2.3, 2.8, 3.5] (conservative → typical → aggressive).

To make the calculations easier to follow, let’s pick a few reference points and work through the dataset sizes step by step.

Starting with a baseline — a 100B model trained on 20,000 SFT samples — here’s how many SFT samples would be required for larger models (200B, 400B, and 1.7T) under the standard scaling rule:

### SFT data samples requirement:

So, according to the multiplicative scaling laws, for a 1.7T parameter model, the aggressive estimate suggests you’d need just one good SFT sample to fine-tune it. Of course, that’s purely theoretical — in practice, we know that fine-tuning still requires at least some high-quality SFT data to make the model useful.

But the moral of the story is clear: as LLMs grow larger, the amount of SFT data required to fine-tune them shrinks dramatically.

##  How much RL ( Reinforcement Learning ) data is required for fine-tuning?

As models grow larger, they also become smarter — and that means they need less data during fine-tuning. The same trend is predicted for RL: as model size increases, the amount of RL data required will be significantly lower compared to today’s needs.

Here’s the formula for calculating the RL data size for a given model:

RL-Data Calculation

Where P0: baseline data set size, d-target / d0 is the ratio calculated using baseline model and target model sizes. 

To make the calculations easier to follow, let’s pick a few reference points and work through the dataset sizes step by step.

Using baseline—100B model with 100,000 RL samples—here’s how many RL samples we would need for 200B, 400B, and 1.7T models under the standard scaling rule:

### RL data samples requirement:

So, to summarize: if we go with the conservative estimates, larger models would require more RL data. The typical estimates suggest that RL data requirements remain constant, regardless of model size. But the most intriguing — and perhaps concerning — are the aggressive estimates, which predict that RL data requirements will actually shrink as models grow larger.

And since everyone is eager to optimize costs, it’s likely that the trend in the industry will lean toward the shrinking-RL-data view sooner rather than later.

##  The Future of Fine-Tuning: Quality over Quantity

The research is clear: as LLMs scale, their hunger for massive post-training datasets diminishes. Both SFT and RL data requirements shrink in surprising ways, challenging the long-held belief that bigger models always demand more data.

This shift carries big implications. Instead of chasing sheer data volume, the focus will increasingly move toward quality over quantity — curating the right data, not just more of it. For companies and researchers, this means reduced costs, faster iteration cycles, and a new competitive edge built on efficiency.

In short, the story of LLM fine-tuning is being rewritten. The future won’t be about feeding models endless amounts of data — it will be about making every sample count.