---
title: "What is grouped query attention? | IBM"
source: "https://www.ibm.com/think/topics/grouped-query-attention"
ingestedAt: "2026-07-30T13:37:20Z"
---
In the attention layer, the _Q, K_ and _V_ vectors are used to calculate an _alignment score_ between each token at each position in a sequence. Those alignment scores are then normalized into _attention weights_ using a softmax function.

For each token _x_ in a sequence, alignment scores are calculated by computing the _dot product_ of that token’s query vector _Q x_ with the key vector _K_ of each of the other tokens: in other words, by multiplying them together. If a meaningful relationship between 2 tokens is reflected in similarities between their respective vectors, multiplying them together will yield a large value. If the 2 vectors _aren’t_ aligned, multiplying them together will yield a small or negative value. Most transformer models use a variant called _scaled dot product attention_ , in which QK is _scaled_ —that is, multiplied—by 1dk to improve training stability.

These query-key alignment scores are then typed in to a _[softmax function](https://victorzhou.com/blog/softmax/). _Softmax normalizes all inputs to a value between 0 and 1 such that they all add up to 1. The outputs of the softmax function are the _attention weights_ , each representing the share (out of 1) of token _x_ ’s attention to be paid to each of the other tokens. If a token’s attention weight is close to 0, it will be ignored. An attention weight of 1 would mean that a token receives _x_ ’s entire attention and all others will be ignored.

Finally, the _value vector_ for each token is multiplied by its attention weight. These attention-weighted contributions from each previous token are averaged together and added to the original vector embedding for token _x_. With this, token _x_ ’s embedding is now updated to reflect the context provided by the other tokens in the sequence that are relevant to it.

The updated vector embedding is then sent to another linear layer, with its own weight matrix _W_ Z, where the context-updated vector is normalized back to a consistent number of dimensions and then sent to the next attention layer. Each progressive attention layer captures greater contextual nuance.