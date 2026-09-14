---
title: "Cold-Start Recommendation with LLMs"
summary: "The application of large language models to recommendation scenarios with limited user history, where LLMs can outperform traditional trained models through zero-shot reasoning and world knowledge."
sources:
  - genai-search-ads/llm-user-behavior-modeling-quality.md
createdAt: 2026-06-15T11:51:18.317040+00:00
updatedAt: 2026-06-15T11:51:18.317040+00:00
---
# Cold-Start Recommendation with LLMs

Cold-start recommendation refers to the challenge of providing personalized recommendations when there is limited or no historical data about users or items. Large Language Models (LLMs) have emerged as a promising approach to address this fundamental problem in recommendation systems, leveraging their pre-trained knowledge and zero-shot capabilities.

## Overview

Cold-start scenarios occur in three primary contexts: new users with no interaction history, new items with no user feedback, and new domains where existing models cannot transfer effectively. Traditional collaborative filtering and sequential recommendation models struggle in these situations due to their reliance on historical interaction patterns. LLMs offer a potential solution by utilizing their extensive pre-training on diverse textual data to make informed recommendations without requiring specific user-item interaction histories. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

## LLM Advantages in Cold-Start Settings

### Zero-Shot Performance

LLMs demonstrate notable success in cold-start recommendation scenarios through their ability to perform zero-shot inference. GPT-3 with 3-step prompting has been shown to outperform some trained sequential models on MovieLens 100K datasets, indicating that pre-trained language models can leverage their world knowledge for recommendation tasks without domain-specific training. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

### World Knowledge Utilization

The effectiveness of LLMs in cold-start scenarios stems from their pre-training on diverse textual content including product reviews, shopping guides, forum discussions, and cultural knowledge. This extensive exposure provides LLMs with "world knowledge" about preferences, demographics, and item popularity that can be applied to new users or items without requiring specific interaction data. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

### Conversational Capabilities

LLMs excel in conversational recommendation settings, where they can interact with users to elicit preferences and provide explanations. Research shows that LLMs outperform fine-tuned conversational recommendation models even without domain-specific fine-tuning, making them particularly valuable for cold-start scenarios where direct user interaction can compensate for lack of historical data. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

## Technical Approaches

### Self-Inspiring Planning

RecMind, presented at NAACL 2024, demonstrates a zero-shot approach that achieves performance comparable to P5 through Self-Inspiring planning techniques. This method allows LLMs to generate recommendations without requiring extensive training on recommendation-specific datasets. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

### Re-ranking Strategies

LLMs show particular strength in re-ranking small candidate sets, making them effective for hybrid recommendation systems where traditional methods generate initial candidates and LLMs provide final ranking based on contextual understanding and user preferences. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

## Limitations and Challenges

### Behavioral vs. Declared Preferences

A fundamental limitation of LLMs in recommendation tasks is their training on declared preferences (what people say) rather than revealed preferences (what people do). LLMs lack exposure to actual behavioral sequences such as click logs, session data, impression records, and purchase histories, which limits their ability to model real user behavior patterns accurately. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

### Bias and Popularity Effects

LLMs exhibit strong position and popularity biases that can affect recommendation quality. They demonstrate a "strong primacy effect" where first items are disproportionately selected, and they can be biased by item popularity independent of personalization fit. These biases may be particularly problematic in cold-start scenarios where limited context makes bias correction more difficult. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

### Hallucination Issues

LLMs may recommend non-existent items, requiring post-processing pipelines to ensure recommendation validity. This hallucination problem can be particularly challenging in cold-start scenarios where there may be insufficient context to validate recommendations against known item catalogs. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

## Performance Comparison

While LLMs show promise for cold-start recommendation, they consistently underperform specialized sequential models by 5-20% NDCG on fine-grained behavioral prediction tasks when sufficient historical data is available. However, their zero-shot capabilities and ability to handle conversational interactions make them valuable for scenarios where traditional methods fail due to data sparsity. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]

## Future Directions

The effectiveness of LLMs in cold-start recommendation may improve through direct behavioral fine-tuning, though this approach would compromise their zero-shot advantages. The structural gap between world knowledge and behavioral knowledge represents a fundamental challenge that may require hybrid approaches combining LLM capabilities with specialized recommendation techniques. ^[llm-quality-for-user-behavior-modeling-and-sequence-prediction.md]
