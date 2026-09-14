---
title: "The layers (attention weights) typically targeted for LoRA application."
source: "https://blog.truegeometry.com/api/exploreHTML/25b9fd121c9343ef1cfa5304dab26647.exploreHTML"
ingestedAt: "2026-05-28T19:15:43Z"
---
# The layers (attention weights) typically targeted for LoRA application.

## Search Model Trained on March 2025 | Vector Size: 1024 | Vocab Size: 153496 

Okay, let's break down the layers typically targeted for LoRA (Low-Rank Adaptation) application in large language models (LLMs). It's not _every_ layer, and certain layers yield much better results than others. Here's a comprehensive overview, categorized for clarity:

**1\. The Core Targets: Attention Layers**

This is where LoRA shines and where you'll get the most bang for your buck. Specifically, within the attention mechanism, these are the key matrices:

  * **Q (Query) Matrix:** Transforms the input into a query representation.
  * **K (Key) Matrix:** Transforms the input into a key representation.
  * **V (Value) Matrix:** Transforms the input into a value representation.
  * **O (Output Projection) Matrix:** Projects the attention-weighted values back into the original dimension. (Sometimes called `proj` in some implementations)



**Why these?**

  * **High Dimensionality:** These matrices are often very large, contributing significantly to the model's parameter count. LoRA's low-rank approximation is most effective on these high-dimensional layers.
  * **Expressiveness:** The attention mechanism is crucial for capturing relationships between tokens, and adapting these matrices directly impacts the model's ability to understand and generate text.
  * **Empirical Results:** Extensive experimentation has shown that LoRA applied to these attention weights consistently delivers the best performance gains for a given number of trainable parameters.



**2\. Also Commonly Targeted: Feedforward (FFN) Layers**

These layers come _after_ the attention mechanism within each transformer block. They add non-linearity and further process the information.

  * **W1 (First Layer of FFN):** The initial linear transformation in the feedforward network. Often a large matrix.
  * **W2 (Second Layer of FFN):** The output projection layer of the feedforward network. Also typically large.



**Why target FFN layers?**

  * **Additional Capacity:** FFN layers provide additional capacity for the model to learn complex patterns.
  * **Complementary to Attention:** Adapting FFN layers can complement the changes made to the attention layers, leading to more nuanced and effective adaptation.
  * **Good for Specific Tasks:** Sometimes, adapting FFN layers is particularly helpful for tasks that require more complex reasoning or knowledge application.



**3\. Less Common, But Sometimes Useful: Embedding Layer**

  * **Word Embeddings:** The matrix that maps tokens to their vector representations.



**Why sometimes target the embedding layer?**

  * **Vocabulary Adaptation:** If you're working with a specialized vocabulary or domain, adapting the embedding layer can help the model better understand the nuances of those terms.
  * **Out-of-Vocabulary (OOV) Tokens:** Can be useful for handling new tokens not seen during pre-training.
  * **Generally Less Impactful:** Compared to attention and FFN layers, adapting the embedding layer usually has a smaller impact on overall performance. It's often considered a secondary target.



**4\. Layers Generally _Not_ Targeted with LoRA**

  * **Layer Normalization (LayerNorm) Weights:** These are generally left untouched. LoRA doesn't typically provide significant benefits when applied to LayerNorm. They are often sensitive and can destabilize training if modified.
  * **Residual Connections:** The weights in residual connections are also usually not adapted.
  * **Positional Embeddings:** While theoretically possible, adapting positional embeddings is less common and often doesn't yield substantial improvements.



**Which Combination to Use?**

The best combination of layers to target depends on the specific model, dataset, and task. Here are some common strategies:

  * **LoRA on Q, K, V, O (Attention Only):** This is the most common and often the most effective starting point. It provides a good balance between performance and efficiency. Often referred to as "QLOra" when combined with 4-bit quantization.
  * **LoRA on Q, K, V, O + W1, W2 (Attention + FFN):** This can lead to further performance gains, but it also increases the number of trainable parameters. Useful for more complex tasks.
  * **LoRA on Q, K, V, O + Embedding:** Consider this if you have a specialized vocabulary or need to handle OOV tokens.
  * **Selective Layer Targeting:** Some implementations allow you to specify which layers within each transformer block to target. This can be useful for fine-tuning the adaptation process.



**Important Considerations:**

  * **Rank (r):** The rank of the low-rank matrices is a crucial hyperparameter. Higher ranks allow for more expressiveness but also increase the number of trainable parameters. Common values are 8, 16, 32, 64.
  * **Alpha (Î±):** A scaling factor that controls the magnitude of the LoRA updates. It's often set to a value proportional to the rank (e.g., Î± = 2 * r).
  * **Target Modules:** The specific names of the layers may vary depending on the model architecture (e.g., Llama, Mistral, GPT). You'll need to inspect the model's structure to identify the correct target modules.
  * **Libraries:** Popular libraries like `peft` (Parameter-Efficient Fine-Tuning) from Hugging Face make it easy to apply LoRA to various LLMs.



**In summary:** Focus on the attention layers (Q, K, V, O) first. Then, consider adding the FFN layers (W1, W2) if you need more capacity. The embedding layer is a less common target, but it can be useful in specific scenarios. Experimentation is key to finding the optimal configuration for your task.

## More questions on topic

## TrueGeometry Embedding Results

## Enhance understanding with following blogs:

Google Play Store [Get Free App](https://play.google.com/store/apps/details?id=com.ionicframework.gear225190&referrer=utm_source%3Dgoogle%26utm_medium%3Dcpc%26utm_campaign%3Dapp_install)

Google Play Store [Get Pro App](https://play.google.com/store/apps/details?id=com.manojky.GearIonicPro&referrer=utm_source%3Dgoogle%26utm_medium%3Dcpc%26utm_campaign%3Dapp_install)