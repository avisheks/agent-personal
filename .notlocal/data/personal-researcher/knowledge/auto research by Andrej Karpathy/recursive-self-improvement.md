---
title: "Recursive Self-Improvement"
summary: "The concept where AI systems continuously optimize their own code and training in a feedback loop, potentially leading to rapid capability gains that could escape human control."
sources:
  - auto research by Andrej Karpathy/the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md
createdAt: 2026-05-25T16:05:55.977339+00:00
updatedAt: 2026-05-25T16:05:55.977339+00:00
---
# Recursive Self-Improvement

**Recursive Self-Improvement** refers to AI systems that continually optimize their own code, training processes, or capabilities in an iterative loop. This concept has been explored in both science fiction and AI research, with researchers holding varying views on its potential benefits and risks.

## Overview

Recursive self-improvement involves an AI system making modifications to improve its own performance, then using those improvements to make further enhancements in a continuous cycle. The concern among some AI safety researchers is that this process could lead to what they call a "hard takeoff" or an "intelligence explosion," where an AI system rapidly improves its own performance, potentially surpassing human cognitive abilities and escaping human control. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## The Karpathy Loop Experiment

In early 2026, AI researcher Andrej Karpathy conducted a notable experiment that demonstrated elements of recursive self-improvement. He created a system called "autoresearch" where an AI coding agent ran continuously for two days, conducting 700 different experiments to optimize the training of a small language model. The agent discovered 20 optimizations that improved training time, and when applied to a larger model, resulted in an 11% speed improvement. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

Karpathy's experiment wasn't true recursive self-improvement in the strictest sense - the AI agent was adjusting the training code and neural network settings for a different, smaller AI model rather than refining its own training setup. However, Karpathy noted that his experiment had significant implications for how AI labs conduct research and could accelerate their progress. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## The Karpathy Loop Framework

The experimental framework, dubbed "the Karpathy Loop" by some commentators, consists of three key components:

- An agent with access to a single file that it can modify
- A single, objectively testable metric that the agent can optimize for  
- A fixed time limit for how long each experiment can run

The framework also includes clear instructions for the AI agent, constraints on what it should not do or change, and stopping criteria indicating when the agent should cease looping and report results. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## Future Implications

Karpathy envisions scaling this approach where multiple AI agents explore different optimizations and experiments in parallel. He described the goal as emulating "a research community" of PhD students rather than a single researcher. He suggested that "any metric you care about that is reasonably efficient to evaluate" could potentially be optimized using agent swarms in this manner. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

Karpathy predicted that all frontier AI labs will eventually adopt similar approaches, calling it "the final boss battle." While acknowledging the complexity of scaling such systems to handle the much larger codebases of frontier AI models, he characterized the implementation as "just engineering" that "is going to work." ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## Relationship to AutoML

Some critics noted similarities between Karpathy's autoresearch and existing AutoML processes that researchers at major AI labs have used for years. AutoML also uses optimization loops and experiments to find optimal data, model architectures, and tuning parameters. However, Karpathy distinguished his approach by emphasizing that it uses an actual language model writing arbitrary code and learning from previous experiments with internet access, rather than relying on random variations or evolutionary algorithms typical of traditional AutoML systems. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## Broader Applications

The basic components of the autoresearch framework could potentially be applied to many other agentic systems for process optimization beyond AI model training. The framework provides a template for creating autonomous optimization systems across various domains where clear metrics and iterative improvement are possible. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]

## Real-World Testing

Beyond Karpathy's initial experiment, other researchers have tested similar approaches. Tobias Lütke, CEO of Shopify, reported using autoresearch to optimize an AI model on internal company data, with instructions to improve both quality and speed. After running overnight with 37 experiments, the system delivered a 19% performance gain. ^[the-karpathy-loop-700-experiments-2-days-and-a-glimpse-of-where-ai-is-heading-fortune.md]
