---
title: "Single-File Modification Strategy"
summary: "A constraint-based approach where AI agents are limited to modifying only one file (like train.py) to focus optimization efforts and prevent system complexity."
sources:
  - auto research by Andrej Karpathy/how-to-set-up-karpathy-s-autoresearch-complete-guide-use-cases.md
createdAt: 2026-05-25T16:02:55.183736+00:00
updatedAt: 2026-05-25T16:02:55.183736+00:00
---
# Single-File Modification Strategy

The **Single-File Modification Strategy** is an autonomous optimization pattern where an AI agent iteratively improves a system by modifying a single file while measuring performance against a defined metric. The strategy was popularized by Andrej Karpathy's autoresearch project, where an AI agent ran 700 experiments over two days and achieved an 11% improvement in training time for a GPT-2 quality model. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Core Pattern

The Single-File Modification Strategy operates through a four-step process:

1. **Define a measurable goal** - Establish a specific metric that can be quantified, such as validation loss, conversion rate, or cost per lead
2. **Designate a single modifiable file** - Restrict the agent's modifications to one file, such as a training script, landing page, or configuration file  
3. **Execute an optimization loop** - The agent reads the current state, forms a hypothesis, makes a change, runs an experiment within a fixed time budget, measures results, and decides whether to keep or discard the change
4. **Repeat indefinitely** - The process continues autonomously without human intervention until manually stopped ^[karpathy-autoresearch-setup-guide-use-cases.md]

The strategy emphasizes volume over individual experiment sophistication, allowing agents to run hundreds of experiments while humans sleep. The magic lies in the simplicity - there is no complex orchestration or multi-model pipeline, just one agent, one file, one metric, running in a tight loop and letting volume do the work. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Technical Implementation

The original implementation requires three components:

- **An AI coding agent** (such as Claude Code) that can read instructions and execute the optimization loop autonomously
- **A GPU environment** (typically NVIDIA GPUs, tested on H100s but compatible with other NVIDIA cards)
- **The core repository** consisting of approximately 630 lines of code with three key files: `prepare.py` for data preparation, `train.py` as the modifiable target file, and `program.md` containing agent instructions ^[karpathy-autoresearch-setup-guide-use-cases.md]

The agent operates on a fixed time budget per experiment - Karpathy uses 5 minutes per experiment - and follows explicit instructions to not pause to ask humans if it should continue. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Business Applications

The strategy extends beyond machine learning to various business optimization scenarios:

### Marketing Optimization
Landing page HTML serves as the target file with conversion rate as the metric. The agent generates variants of headlines, layouts, calls-to-action, and offers, testing them against traffic to identify optimal combinations. This approach automates what tools like Optimizely attempted to do, with the agent both designing variants and running tests continuously. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Email Campaign Optimization  
Email templates become the modifiable file with open rates, click-through rates, or reply rates as metrics. The agent tests subject lines, body copy, send times, and personalization approaches. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### [[Prompt Template Encoding|Prompt Engineering]]
For AI-powered applications, prompt templates serve as the target file with output quality scores as the metric. The agent iterates on prompt structure, examples, and system instructions to optimize performance. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Pricing Strategy
Configuration files defining price points, bundles, and discount structures become the target, with revenue per visitor or conversion rates as metrics. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Advertising Optimization
Ad creative and targeting parameters serve as the modifiable file, with cost per acquisition or return on ad spend as the metric. The agent tests angles, audiences, and creatives to identify combinations that lower customer acquisition costs or increase returns. ^[karpathy-autoresearch-setup-guide-use-cases.md]

### Content Strategy
Content templates and posting strategies become the target file, with engagement rates, subscription conversions, or reach as metrics. The agent iterates on formats, hooks, posting times, and hashtag strategies. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Advantages and Limitations

The strategy's primary advantage lies in its ability to overcome the traditional bottleneck of experiment design and execution. Where human researchers might run a few experiments per day, the Single-File Modification Strategy can execute hundreds overnight. The bottleneck has shifted from running experiments to designing the optimization framework itself. ^[karpathy-autoresearch-setup-guide-use-cases.md]

The approach requires three prerequisites for effective application:
1. A clearly defined, measurable metric
2. A system component that can be isolated to a single modifiable file
3. A fast evaluation loop that provides timely feedback on changes ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Real-World Results

Beyond Karpathy's original results, Shopify CEO Tobi Lütke applied the same pattern to an internal 0.8 billion parameter model, achieving a 19% improvement in model quality through 37 experiments run overnight with no human involvement. The agent discovered issues including incorrect attention mechanism scaling, missing regularization in value embeddings, overly conservative attention windows, and misconfigured AdamW beta parameters. ^[karpathy-autoresearch-setup-guide-use-cases.md]

## Future Development

Karpathy envisions expanding the concept beyond single-agent optimization to "emulate a research community" through AgentHub, described as a collaboration platform with no main branch or pull requests, allowing agents to coordinate across a sprawling directed acyclic graph of commits. The goal is not to emulate a single PhD student, but rather an entire research community working in parallel. ^[karpathy-autoresearch-setup-guide-use-cases.md]
