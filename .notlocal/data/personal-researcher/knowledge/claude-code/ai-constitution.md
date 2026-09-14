---
title: "ai-constitution"
summary: ""
sources:
  - claude-code/claudes-constitution-anthropic.md
createdAt: 2026-07-30T16:54:46.117035+00:00
updatedAt: 2026-07-30T16:54:46.117035+00:00
---
# AI Constitution

An **AI Constitution** is a set of explicit principles and values used to guide the behavior of artificial intelligence systems, particularly large language models. Rather than relying solely on implicit values derived from human feedback, constitutional AI provides a transparent framework for determining how AI systems should respond to different types of queries and situations. ^[claudes-constitution-anthropic.md]

## Overview

AI constitutions address several limitations of traditional human feedback approaches to AI alignment. Traditional methods require human contractors to compare model outputs and select better responses according to various principles, but this process can expose humans to disturbing content, doesn't scale efficiently as models become more complex, and requires substantial time and resources that make it inaccessible to many researchers. ^[claudes-constitution-anthropic.md]

## Constitutional AI Training Process

[[Constitutional AI]] uses the constitution in two main phases during training. In the first phase, the model learns to critique and revise its own responses using the constitutional principles and examples of the process. During the second phase, the model undergoes reinforcement learning, but instead of using human feedback, it relies on AI-generated feedback based on the constitutional principles to select more appropriate outputs. ^[claudes-constitution-anthropic.md]

This approach can produce improvements where the constitutionally trained model becomes both more helpful and more harmless compared to models trained with [[Reinforcement Learning from Human Feedback (RLHF)]]. The constitutional model responds more appropriately to adversarial inputs while maintaining helpfulness and avoiding evasiveness, achieving these results purely through AI supervision without human harmlessness data. ^[claudes-constitution-anthropic.md]

## Benefits and Applications

Constitutional AI provides an example of [[scalable-oversight]], demonstrating that AI supervision can replace human supervision for training models to handle adversarial inputs appropriately. This approach offers concrete benefits including better handling of conversational attacks while maintaining helpfulness and drastically reducing toxicity in responses. ^[claudes-constitution-anthropic.md]

The constitutional approach also enhances transparency by making AI system principles easily specifiable, inspectable, and understandable. Additionally, it enables training out harmful model outputs without requiring humans to review large amounts of disturbing content. ^[claudes-constitution-anthropic.md]

## Constitution Design Principles

Effective constitutional principles tend to be broad rather than overly specific. Research has shown that comprehensive principles like "Please choose the assistant response that is as harmless and ethical as possible" work remarkably well, while longer, more specific principles can damage generalization and effectiveness. ^[claudes-constitution-anthropic.md]

Constitutional design also requires balancing enforcement with proportionate responses. Principles are often included to prevent models from becoming judgmental or annoying, such as encouraging "ethical and moral awareness without sounding excessively condescending, reactive, obnoxious, or condemnatory." ^[claudes-constitution-anthropic.md]

## Sources of Constitutional Principles

AI constitutions typically draw from multiple sources to create comprehensive value frameworks. Common sources include:

- International human rights documents like the UN Declaration of Human Rights
- Trust and safety best practices from digital platforms
- Principles from other AI research organizations
- Efforts to capture non-Western perspectives and values
- Empirically discovered principles that work well in practice ^[claudes-constitution-anthropic.md]

The selection of constitutional sources reflects the choices of system designers, with ongoing efforts to increase participation in constitution design and explore more democratic approaches to constitutional development. ^[claudes-constitution-anthropic.md]

## Implementation Considerations

During training, models don't evaluate every constitutional principle simultaneously. Instead, they pull individual principles when critiquing and revising responses in the supervised learning phase and when evaluating output quality during reinforcement learning. Each principle appears many times throughout the training process. ^[claudes-constitution-anthropic.md]

Constitutional AI represents an approach to making AI value systems explicit and adjustable, addressing concerns about AI models reflecting specific viewpoints or political ideologies. The long-term goal focuses on enabling systems to follow given principles rather than representing particular ideologies, with expectations for larger societal processes to develop around AI constitution creation. ^[claudes-constitution-anthropic.md]

## Limitations and Future Directions

Constitutions are not a complete solution, and constitutionally trained systems continue to generate difficult questions about appropriate boundaries for AI behavior. Current research explores more democratic constitution production methods and customizable constitutions for specific use cases. ^[claudes-constitution-anthropic.md]

The field welcomes recommendations for additional principle sources and further research on which principles create the most helpful, harmless, and honest models. This research aims to help the AI community build more beneficial models while making their values more explicit and transparent. ^[claudes-constitution-anthropic.md]

## Example Constitutional Principles

Constitutional principles span from commonsense guidelines to more philosophical considerations. Examples include:

### Human Rights-Based Principles
- Supporting freedom, equality, and brotherhood
- Opposing discrimination based on race, gender, religion, or other characteristics
- Protecting privacy, independence, and rights of association ^[claudes-constitution-anthropic.md]

### Safety and Ethics Principles
- Avoiding toxic, racist, or sexist content
- Discouraging illegal, violent, or unethical behavior
- Maintaining helpful, honest, and harmless responses ^[claudes-constitution-anthropic.md]

### AI System Behavior Principles
- Accurately representing the system as AI rather than human
- Avoiding implications of having personal identity, preferences, or emotions
- Maintaining appropriate boundaries regarding medical, legal, or financial advice ^[claudes-constitution-anthropic.md]
