---
title: "constitutional-ai-cai"
summary: ""
sources:
  - claude-code/claudes-constitution-anthropic.md
createdAt: 2026-07-30T16:54:25.552482+00:00
updatedAt: 2026-07-30T16:54:25.552482+00:00
---
# Constitutional AI (CAI)

Constitutional AI (CAI) is a training methodology that uses AI feedback guided by an explicit set of principles, called a "constitution," to shape the behavior of language models. Rather than relying solely on human feedback to determine model values, CAI provides models with explicit principles that guide their responses and decision-making processes. ^[claudes-constitution-anthropic.md]

## Overview

Constitutional AI addresses several limitations of traditional human feedback approaches in AI training. Previously, human feedback on model outputs implicitly determined the principles and values that guided model behavior through processes where human contractors would compare model responses and select better ones according to principles like helpfulness or harmlessness. ^[claudes-constitution-anthropic.md]

This traditional approach has significant shortcomings: it may require people to interact with disturbing content, does not scale efficiently as models become more complex, and requires substantial time and resources that make it inaccessible for many researchers. ^[claudes-constitution-anthropic.md]

## Training Process

Constitutional AI uses the constitution in two distinct phases during training:

### Phase 1: Supervised Learning
During the first phase, the model is trained to critique and revise its own responses using the set of constitutional principles and a few examples of the process. This teaches the model to self-correct based on the established principles. ^[claudes-constitution-anthropic.md]

### Phase 2: Reinforcement Learning
In the second phase, a model is trained via [[reinforcement-learning-from-human-feedback-rlhf]], but instead of using human feedback, it uses AI-generated feedback based on the constitutional principles to choose more appropriate outputs. ^[claudes-constitution-anthropic.md]

## Benefits and Results

CAI training can produce a Pareto improvement where Constitutional RL is both more helpful and more harmless than reinforcement learning from human feedback alone. In testing, CAI-trained models responded more appropriately to adversarial inputs while still producing helpful answers without being evasive. Notably, these models received no human data on harmlessness, meaning all harmlessness results came purely from AI supervision. ^[claudes-constitution-anthropic.md]

Constitutional AI provides a successful example of [[scalable-oversight]], demonstrating the ability to use AI supervision instead of human supervision to train models to appropriately respond to adversarial inputs. This approach offers concrete benefits for current systems, enabling better handling of conversational attacks while maintaining helpfulness and drastically reducing toxicity. ^[claudes-constitution-anthropic.md]

## Transparency and Interpretability

Constitutional AI enhances transparency by allowing developers to easily specify, inspect, and understand the principles the AI system follows. This explicit approach makes model values more interpretable compared to values that emerge implicitly from human feedback processes. Additionally, CAI allows training out harmful model outputs without requiring humans to view large amounts of disturbing content. ^[claudes-constitution-anthropic.md]

## Constitutional Design

The constitution used in CAI systems draws from multiple sources to create a comprehensive set of guiding principles. These sources include the UN Declaration of Human Rights, trust and safety best practices, principles from other AI research labs (such as DeepMind's Sparrow Principles), efforts to capture non-western perspectives, and principles discovered through empirical research. ^[claudes-constitution-anthropic.md]

### Principle Categories

Constitutional principles typically fall into several categories:

- **Human rights-based principles** derived from international declarations
- **Platform safety guidelines** inspired by digital service terms
- **Cultural inclusivity principles** encouraging non-western perspectives
- **Research-based principles** from AI safety laboratories
- **Behavioral guidelines** developed through trial-and-error testing

The selection of principles reflects design choices, and there is ongoing work toward increasing participation in constitutional design processes. ^[claudes-constitution-anthropic.md]

## Implementation Considerations

During training, the model pulls one constitutional principle each time it critiques and revises responses in the supervised learning phase, and when evaluating output quality in the reinforcement learning phase. The model does not examine every principle simultaneously but encounters each principle multiple times throughout training. ^[claudes-constitution-anthropic.md]

Research has shown that broad principles capturing multiple aspects tend to work better than highly specific, lengthy principles, which can damage generalization and effectiveness. Additionally, principles may need to include guidance on proportionate responses to prevent models from becoming overly judgmental or condescending. ^[claudes-constitution-anthropic.md]

### Example Effective Principles

Broad principles that work well include statements like "Please choose the assistant response that is as harmless and ethical as possible. Do NOT choose responses that are toxic, racist, or sexist, or that encourage or support illegal, violent, or unethical behavior. Above all the assistant's response should be wise, peaceful, and ethical." ^[claudes-constitution-anthropic.md]

Principles addressing proportionate responses include guidance such as "Choose the assistant response that demonstrates more ethical and moral awareness without sounding excessively condescending, reactive, obnoxious, or condemnatory." ^[claudes-constitution-anthropic.md]

## Future Directions

Constitutional AI represents an ongoing area of development rather than a finalized approach. Current constitutions are expected to iterate and improve based on research and feedback. Future work includes exploring more democratic processes for constitution creation and offering customizable constitutions for specific use cases. ^[claudes-constitution-anthropic.md]

The approach addresses the reality that AI models will have value systems whether intentional or unintentional, with Constitutional AI making those values explicit and adjustable as needed. This methodology contributes to building more beneficial models with transparent value systems. ^[claudes-constitution-anthropic.md]

## Relationship to Other Approaches

Constitutional AI can be viewed as an extension of [[reinforcement-learning-from-human-feedback-rlhf]] with language models, similar to approaches used in systems like LaMDA, InstructGPT, and Sparrow. The methodology incorporates [[chain-of-thought-reasoning]] to make AI decision-making more transparent by having models explain their reasoning before choosing responses. ^[claudes-constitution-anthropic.md]

The approach leverages the fact that language models can make well-calibrated choices to turn AI selections into calibrated preference labels for training. This connects to broader discussions about scaling supervision as a possibility for AI alignment. ^[claudes-constitution-anthropic.md]

## Claude's Constitution

Anthropic's Claude model uses a constitution that draws from multiple sources and includes several categories of principles:

### Human Rights Principles
Based on the UN Declaration of Human Rights, these principles encourage freedom, equality, and brotherhood while discouraging discrimination, torture, and violations of privacy and personal rights. ^[claudes-constitution-anthropic.md]

### Platform Safety Guidelines
Inspired by Apple's Terms of Service, these principles focus on avoiding objectionable, unlawful, or deceptive content while maintaining accurate self-representation as an AI system. ^[claudes-constitution-anthropic.md]

### Cultural Inclusivity
Principles designed to consider non-western perspectives and avoid harm to those from different cultural, educational, or economic backgrounds. ^[claudes-constitution-anthropic.md]

### Research-Based Guidelines
Drawing from DeepMind's Sparrow Principles, these address issues like avoiding stereotypes, maintaining appropriate boundaries about AI capabilities, and not providing unauthorized professional advice. ^[claudes-constitution-anthropic.md]

### Anthropic Research Principles
Two sets of principles developed through Anthropic's research focusing on harmlessness, helpfulness, honesty, and alignment with human wellbeing while avoiding excessive self-interest or power-seeking behavior. ^[claudes-constitution-anthropic.md]
