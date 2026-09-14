---
title: "OpenAI o1 and o3 Explained: How “Thinking” Models Work | Blog Le Wagon"
source: "https://blog.lewagon.com/skills/openai-o1-and-o3-explained-how-thinking-models-work/"
ingestedAt: "2026-05-28T19:53:00Z"
---
_This article is written by Andrei Danila, a Machine Learning Engineer._

* * *

## **Introduction: A new chapter after ChatGPT 4o**

Remember when ChatGPT first appeared and blew everyone’s minds? [In our previous article](https://blog.lewagon.com/skills/how-chatgpt-works-a-guide-for-all-levels-of-curiosity/), we broke down how these large language models work—from basic neural networks to complex transformer architectures. Well, OpenAI has done it again with their models called o1 and o3.

These “thinking” models are creating quite a buzz in the AI community because they solve problems differently. While ChatGPT made AI accessible to everyone, o1/o3 represent the next big leap—moving us closer to AI systems that don’t just respond cleverly but can actually follow multi-step plans and adapt along the way. They’re so popular that every other AI provider rushed to put out their own versions of “reasoning”/ “thinking” models.

For clarity, we will be referring to o1 and o3 interchangeably throughout the article. While o3 is newer and smarter, they both work in a very similar manner. In high level concepts, they operate under a very similar architecture.

## **Chain-of-thought reasoning: When AI shows its work**

Think about how you solve a difficult math problem. You don’t just write down the answer—you work through steps, crossing things out, double-checking your logic. That’s essentially what o1 is doing behind the scenes with something called “chain-of-thought reasoning.”

Remember those math teachers who always insisted you “show your work”? They were onto something. By forcing you to write out each step, they could see your reasoning process—not just your final answer. o1 does the same thing internally. It doesn’t just jump to conclusions; it works through problems methodically, especially when tackling complex code, logic puzzles, or math problems.

This approach has led to substantial improvements in mathematical problem-solving. On the American Invitational Mathematics Examination (AIME),[ o3 reached 96.7% accuracy](https://wandb.ai/byyoung3/ml-news/reports/OpenAI-Introduces-o3-Pushing-the-Boundaries-of-AI-Reasoning--VmlldzoxMDY3OTUxMA), beating all previous LLM results.

## **Reinforcement learning: More than just more data**

OpenAI didn’t simply feed o1 more information and more computational power and call it a day. The real innovation lies in how they fine-tuned and aligned the model using an innovative technique.

Like previous versions of ChatGPT, o1 uses a transformer architecture that decides which parts of a conversation deserve attention. But o1 has been specifically trained to maintain an internal dialogue—a hidden “thinking block” where it works through potential solutions step by step before presenting its answer.

This isn’t unlike how you might talk yourself through a problem: “First I need to understand what they’re asking… then I should approach it by… wait, that won’t work because… let me try this instead…”

The AI gets better at this through reinforcement learning, where the system is rewarded for steps that lead to correct or useful outcomes—similar to receiving points for each correct step in your homework, not just for the final answer. This training involves human feedback providers who essentially “grade” the AI’s reasoning process. They review thousands of examples, marking when the AI makes logical leaps, misunderstands a problem, or arrives at a brilliant insight.

Over time, the model internalizes these lessons, learning which thinking patterns tend to yield successful outcomes. Just as a student gradually develops intuition for solving certain types of problems after practicing many similar examples, the AI builds internal patterns that guide its reasoning. The difference from previous models is striking—instead of simply learning to produce answers that statistically match expected outputs, o1 and o3 learn problem-solving methodologies that allow them to handle novel challenges in a structured way.

## **The processing power behind the scenes**

Training a model to think this way requires serious computational muscle. We mentioned in our ChatGPT article how developing advanced language models can take weeks or months of processing time—well, o1 pushes this even further.

The model needs to learn not just language patterns but also how to reason methodically. This means teaching it to break down complex problems, plan intermediate steps, and verify its work along the way. All this requires more specialized training data and more time spent refining the model in massive data centers.

On the SWE-Bench Verified Benchmark, which assesses real-world software engineering problem-solving, [o3 scored 71.7%](https://wandb.ai/byyoung3/ml-news/reports/OpenAI-Introduces-o3-Pushing-the-Boundaries-of-AI-Reasoning--VmlldzoxMDY3OTUxMA), significantly outperforming DeepSeek R1 (49.2%) and o1 (48.9%). This proves that OpenAI’s latest models are not just better at theoretical reasoning but also excel in practical applications like debugging and software design.

## **Practical benefits: An AI that (mostly) stays on track**

If you’ve ever tried using earlier models as personal assistants, you’ve probably noticed how they often forget what you initially asked for or start repeating themselves. With o1, these issues are less common—though not entirely eliminated.

The model maintains focus through more conversation turns before losing track. Developers experimenting with o1 report that while it still gets confused during extremely long or complicated conversations, it’s notably better at staying on task. It’s like the difference between working with someone who needs constant reminders versus a colleague who can follow a complex discussion without constantly asking, “Wait, what were we talking about again?”

Additionally, OpenAI introduced o3-mini, a more cost-effective and efficient reasoning model, designed for frequent, everyday tasks. Despite being 15 times cheaper and five times faster than o1, it maintains comparable performance levels.

## **Keeping it real: What o1 still can’t do**

Despite these advances, o1 isn’t some all-knowing digital oracle. Like its predecessors, it’s still making predictions based on patterns it learned during training. Though it uses chain-of-thought reasoning, it’s not actually “thinking” the way humans do.

Even with its methodical approach, o1 will eventually lose track in very extended conversations. And the computational cost of maintaining this elaborate “internal dialogue” grows exponentially as conversations lengthen—creating both technical and financial challenges.

## **The Future: From chatbots to problem-solving partners**

What makes o1 fascinating is how it points toward a future where AI systems become genuine problem-solving assistants rather than just sophisticated chatbots. If ChatGPT showed us that AI could chat like a human, o1 demonstrates that AI can plan, reflect, and strategize—at least to some degree.

## **What this means for you**

While thinking models don’t solve every AI challenge, it pushes us closer to a world where these systems function more like skilled collaborators. The future of AI remains unwritten, but models like o1 and o3 suggest we’re gradually filling in the pages of something remarkable. Stay curious and keep learning—this technology isn’t slowing down anytime soon.

PS: Wondering why there’s no o2 model? OpenAI reportedly skipped that name to avoid trademark disputes with the British telecommunications provider (and namesake of London’s O2 Arena).