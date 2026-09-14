---
title: "internal-thinking-block"
summary: ""
sources:
  - reasoning-llms/openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md
createdAt: 2026-05-29T04:56:08.949521+00:00
updatedAt: 2026-05-29T04:56:08.949521+00:00
---
# Internal Thinking Block

An **Internal Thinking Block** is a hidden computational process used by advanced language models, particularly OpenAI's o1 and o3 models, where the AI maintains an internal dialogue to work through potential solutions step by step before presenting its final answer. This represents a significant departure from traditional language models that generate responses directly without explicit intermediate reasoning steps. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Overview

The Internal Thinking Block functions as a private workspace where the AI can engage in methodical problem-solving without immediately sharing its reasoning process with the user. This approach mirrors how humans might talk themselves through a complex problem, considering multiple approaches and self-correcting before arriving at a solution. The AI works through thoughts like "First I need to understand what they're asking… then I should approach it by… wait, that won't work because… let me try this instead…" ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

Unlike previous models that simply learned to produce answers matching expected statistical outputs, models with Internal Thinking Blocks learn problem-solving methodologies that allow them to handle novel challenges in a structured way. This enables them to break down complex problems, plan intermediate steps, and verify their work along the way. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Relationship to Chain-of-Thought Reasoning

The Internal Thinking Block is closely connected to [[Chain-of-Thought Reasoning]], where AI systems show their work by working through problems methodically rather than jumping directly to conclusions. This is particularly effective for complex code, logic puzzles, and mathematical problems. The approach has led to substantial improvements in mathematical problem-solving, with o3 reaching 96.7% accuracy on the American Invitational Mathematics Examination (AIME). ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Training and Development

### Reinforcement Learning Integration

The development of Internal Thinking Blocks relies heavily on [[Reinforcement Learning from Human Feedback (RLHF)]], where the system receives rewards for steps that lead to correct or useful outcomes. Human feedback providers review thousands of examples, marking when the AI makes logical leaps, misunderstands problems, or arrives at brilliant insights. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

Over time, the model internalizes these lessons, learning which thinking patterns tend to yield successful outcomes. This is similar to how a student gradually develops intuition for solving certain types of problems after practicing many similar examples. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

### Computational Requirements

Training models with Internal Thinking Blocks requires significant computational resources beyond traditional language model training. The model must learn not just language patterns but also methodical reasoning processes. This specialized training demands more time in massive data centers and more sophisticated training data. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Performance Benefits

Models utilizing Internal Thinking Blocks demonstrate improved performance across multiple domains:

- **Mathematical Problem-Solving**: O3 achieved 96.7% accuracy on the AIME benchmark
- **Software Engineering**: O3 scored 71.7% on the SWE-Bench Verified Benchmark, significantly outperforming previous models
- **Conversation Maintenance**: Better focus retention through longer conversation turns compared to earlier models ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Limitations

Despite their advances, Internal Thinking Blocks have several constraints:

- The AI is still making predictions based on learned patterns rather than genuine human-like thinking
- Performance degrades in very extended conversations
- Computational costs grow exponentially as conversations lengthen, creating both technical and financial challenges
- The models can still lose track during extremely long or complicated discussions ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Technical Implementation

Internal Thinking Blocks are built on [[Transformer Architecture]] but are specifically trained to maintain hidden reasoning processes. The system learns to engage in structured problem-solving while keeping this internal dialogue separate from the user-facing response generation. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]

## Future Implications

The Internal Thinking Block represents a step toward AI systems that function as genuine problem-solving assistants rather than sophisticated chatbots. This technology points toward a future where AI can plan, reflect, and strategize in ways that more closely approximate human cognitive processes, though significant limitations remain. ^[openai-o1-and-o3-explained-how-thinking-models-work-blog-le-wagon.md]
