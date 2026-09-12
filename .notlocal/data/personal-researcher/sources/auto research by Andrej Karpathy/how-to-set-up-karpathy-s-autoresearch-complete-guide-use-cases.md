---
title: "How to Set Up Karpathy's Autoresearch: Complete Guide + Use Cases"
source: "https://artificiallyintimidating.com/p/karpathy-autoresearch-setup-guide-use-cases"
ingestedAt: "2026-05-25T15:41:49Z"
---
**[Andrej Karpathy](https://en.wikipedia.org/wiki/Andrej_Karpathy)** left an AI agent running for two days.

It ran 700 experiments. Found 20 genuine improvements. Cut the time to train a GPT-2 quality model by 11% — on code Karpathy had already hand-optimized himself.

One of those improvements? The agent discovered that his attention mechanism was too diffuse because he’d forgotten to add a scalar multiplier. Another: his Value Embeddings needed regularization he wasn’t applying. A banded attention window that was too conservative. Messed-up AdamW betas.

Bugs that one of the most respected ML researchers alive had missed — caught by an AI agent grinding through experiments at 3am while Karpathy slept.

Then Shopify CEO Tobi Lütke pointed the same tool at an internal 0.8 billion parameter model. 37 experiments overnight. 19% improvement in model quality. Eight hours. No human involvement.

This is autoresearch. And it’s not just for ML researchers.

Karpathy himself put it plainly: _"You don't 'use it' directly, it's just a recipe/idea — give it to your agent and apply to what you care about."_

That quote is the whole point. Autoresearch isn’t a product. It’s a pattern. And once you understand the pattern, you can point it at anything.

[](https://substackcdn.com/image/fetch/$s_!B3ax!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2abb8110-7f16-4170-9f67-5671ab82ba9a_1536x1024.webp)The shift from "Brain in a Jar" (scoped intelligence) to "Robotic Hands" (autonomous execution that loops until it wins).

Here’s how the pattern works in four steps:

**1\. You define a goal with a measurable outcome.** Not "make things better." Something specific. A number that goes up or down. Validation loss. Conversion rate. Cost per lead. Open rate.

**2\. You give an AI agent one file it can modify.** In Karpathy’s case, it’s a 630-line training script called `train.py`. In your case, it could be a landing page, an email sequence, a pricing config, or a prompt template.

**3\. The agent runs a loop.** It reads the current state, forms a hypothesis, makes a change, runs an experiment on a fixed time budget (Karpathy uses 5 minutes per experiment), measures the result, and decides: keep or discard?

**4\. It repeats — indefinitely.** As Karpathy’s `program.md` instructions state: _"Do NOT pause to ask the human if you should continue."_ The agent runs until you tell it to stop. It accumulates improvements like compound interest.

That’s it. Goal, file, loop, repeat.

The magic is in the simplicity. There’s no complex orchestration. No multi-model pipeline. It’s one agent, one file, one metric, running in a tight loop — and letting volume do the work.

That’s the shift. The bottleneck moved.

It used to be that running experiments was expensive, slow, and required deep expertise. You’d design an experiment, run it, wait, analyze results, design the next one. A good researcher might run a few experiments a day. A great one might run a dozen.

Autoresearch runs hundreds. Overnight. While you’re asleep.

And Karpathy’s vision goes even bigger. _"The goal is not to emulate a single PhD student,"_ he wrote. _"It’s to emulate a research community of them."_ He’s already building AgentHub — a collaboration platform he describes as "a stripped-down GitHub where there’s no main branch, no PRs, no merges, a sprawling DAG of commits in every direction with a message board for agents to coordinate."

But you don’t need to wait for AgentHub. The pattern works today, right now, on a rented GPU that costs a couple bucks an hour.

[](https://substackcdn.com/image/fetch/$s_!D8pE!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa20682f8-9545-4bf9-b4c4-5a1675fff8c6_1536x1024.webp)Left: The human bottleneck — one brain, one set of hands. Right: The autoresearch pattern — a networked community of agents running experiments in parallel.

Here’s where most people get it wrong. They see "GPU" and "training script" and think this is for ML engineers. It’s not. The autoresearch pattern applies to anything where you can:

  1. Define a measurable metric

  2. Give an agent something to modify

  3. Run a fast evaluation loop




Let me make this concrete with use cases that actually matter for people running businesses:

Your `train.py` is your landing page HTML. Your metric is conversion rate. The agent generates variants of headlines, layouts, CTAs, and offers — pushes them to traffic, measures which converts better, keeps the winner, iterates. This is what tools like Optimizely tried to do, except now the agent designs the variants AND runs the tests. 24/7.

Your file is the email template. Your metric is open rate, click-through rate, or reply rate. The agent tests subject lines, body copy, send times, personalization approaches. It keeps what works, discards what doesn’t. You wake up to your best-performing sequence.

If you’re using AI for customer service, content generation, or internal tools — your prompts are the file, and output quality (measured by a scoring rubric) is the metric. The agent iterates on prompt structure, examples, system instructions. You get optimized prompts without the manual grind.

Your config file defines price points, bundles, and discount structures. Your metric is revenue per visitor or conversion rate at each tier. The agent tests combinations and converges on optimal pricing — the kind of testing most solopreneurs never do because it takes too long manually.

Your ad creative and targeting parameters are the file. Cost per acquisition or ROAS is the metric. The agent tests angles, audiences, and creatives — keeping the combos that lower CAC or raise return on ad spend. This is where autoresearch can literally save (or print) you money.

Your content templates and posting strategies are the file. Engagement rate, subscription conversions, or reach are the metrics. The agent iterates on formats, hooks, posting times, and hashtag strategies.

[](https://substackcdn.com/image/fetch/$s_!ukLw!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff9d0c0c7-0366-4cb1-b22b-5e439659be6b_1536x1024.webp)The core loop: Hypothesis → Experiment → Measurement → Keep or Discard → Repeat.

This is where people psych themselves out. They hear "NVIDIA GPU" and "clone the repo" and assume it’s beyond them. It’s not.

There are three things you need:

**1\. An AI coding agent.** Claude Code is the one Karpathy uses and recommends. It reads the `program.md` instructions and runs the entire loop autonomously.

**2\. A GPU.** Autoresearch needs an NVIDIA GPU — it was tested on H100s but works on other NVIDIA cards. If you don’t have one (most people don’t), you rent one in the cloud. Google Colab, Lambda Labs, Vast.ai, or RunPod all work. Some offer free tiers.

**3\. The repo.** It’s 630 lines of code. Three key files: `prepare.py` (data prep — you don’t touch this), `train.py` (the file the agent modifies), and `program.md` (the instructions you write for the agent).

That’s genuinely it. You clone the repo, set up a cloud GPU, point Claude Code at `program.md`, and walk away.

Let’s get this running. I’m going to walk you through two paths: the original autoresearch repo (for the ML-curious), and the generalized pattern (for applying this to your business).