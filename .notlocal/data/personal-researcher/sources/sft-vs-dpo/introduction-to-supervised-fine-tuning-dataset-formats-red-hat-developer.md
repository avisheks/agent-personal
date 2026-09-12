---
title: "Introduction to supervised fine-tuning dataset formats | Red Hat Developer"
source: "https://developers.redhat.com/articles/2025/08/18/introduction-supervised-fine-tuning-dataset-formats"
ingestedAt: "2026-05-18T01:09:34Z"
---
Large language models (LLMs) are conventionally trained in two phases. In the first pre-training phase, the model sees gigantic corpuses of unlabeled text from the internet and is trained to predict only the next singular token. In the second post-training phase, the model sees data that resembles the behavior of a chatbot and learns to predict subsequent tokens that align with that behavior. Supervised fine-tuning (SFT) is the most common post-training technique used to improve the alignment of large language models after pre-training. 

SFT uses datasets of formatted prompt response pairs, or simulated conversations to familiarize the model with chat/assistant style interactions. You can format these datasets in many ways for various purposes, which we will explore in this article.

Unfortunately, there isn't much consistency in the input formats. Some standards have emerged (particularly for chat conversation datasets), but data keys often have different names or datasets will include extra fields which may or may not be relevant to the text generation task. Nevertheless, we can group these dataset formats into general buckets. However, it is useful to first understand how these formats are used to produce model training samples.

## What the model sees

As with pre-training, during SFT the model loss is simply a measure of next-token prediction error compared to the ground truth next-token. Therefore, we need our model inputs to consist of flat tokenized sequences and their corresponding labels, which is usually the same sequence with some tokens masked out. If our dataset consists of prompt and response pairs, then we need to format these to produce concatenated strings, typically using a template with special tokens to denote which sections are part of the user prompt versus the chatbot response.

This is where the Jinja templating library comes in. It defines a templating language that allows developers to create chat/prompt templates and then later fill them with inputs. It looks something like this:
    
    
    {% for message in messages %}
      {% if message['role'] == 'user' %}
        {{ '<|user|>\n' + message['content'] + eos_token }}
      {% elif message['role'] == 'system' %}
        {{ '<|system|>\n' + message['content'] + eos_token }}
      {% elif message['role'] == 'assistant' %}
        {{ '<|assistant|>\n'  + message['content'] + eos_token }}
      {% endif %}
    {% endfor %}
    {% if add_generation_prompt %}
      {{ '<|assistant|>' }}
    {% endif %}

This template is applied to the following data as follows:
    
    
    [
      {
        "role": "system",
        "content": "You are a helpful assistant who answers questions respectfully and honestly."
      },
      {
        "role": "user",
        "content": "How are language model inputs formatted?"
      },
    ]

Then it will produce the following formatted sequence:
    
    
    <|system|>
    You are a helpful assistant who answers questions respectfully and honestly.</s>
    <|user|>
    How are language model inputs formatted?</s>
    <|assistant|>

If you'd like to verify this yourself or play around with these templates, you can visit this [playground](https://huggingface.co/spaces/Xenova/jinja-playground). If you are fine-tuning a model that has already been instruct/chat tuned, it is likely that this template will already exist and be available through the models tokenizer. For example, the entry `"chat_template"` at the bottom of granite-3.2-8b-instruct's [tokenizer_config.json](https://huggingface.co/ibm-granite/granite-3.2-8b-instruct/blob/main/tokenizer_config.json) defines the template for this instruct model. When the template exists and is accessible, it is important to reuse it for further training so that the model sees only a single consistent template format.

These templates may also be simpler for a prompt-response style dataset which may only wrap the prompt in "start prompt" and "end prompt" special tokens and append the response.

After templating, the final data transformation step is to split the templated sequence into tokens, which are mapped to corresponding token indices. These indices are then used to select the token embedding (typically a floating point vector) for each token.

## What we see

Starting at the file level, SFT datasets are often stored in JSON or [JSONL](https://jsonlines.org) files. Some datasets may also be compressed or stored in parquet files, which is an efficient column-based data storage format.

Within these files, there are a few general types of dataset formats:

  1. **Chat formats:** Entries are lists of dicts containing "content" and "role" values forming a conversation.

  2. **Instruct formats:** Entries consist of "prompt" and "response" pairs. In some cases, the "prompt" is actually made up of two values "instruction" and "input."

  3. **Text only:** You can think of these as datasets where the prompt/response/chat has already been processed into the template and now entries just consist of a single formatted string, with pre-established separators between parts of speech.




Examples of each type are shown below. However, for each of these there are many datasets that are similar but use different key names, have extra metadata, and in some cases, include extra data fields with additional context for the prompt.

Take a look at these examples of various chat formats:

OpenAI:
    
    
    {
        "messages": [
            {
                "role": "system" or "user" or "assistant",
                "content": "...",
            },
            ...
        ]
    },
    ...

ShareGPT:
    
    
    {
        "conversations": [
            {
                "from": "system" or "human" or "gpt",
                "value": "...",
            },
            ...
        ]
    },
    ...

Likewise, here are a few examples of instruct formats:

Alpaca:
    
    
    [
        {
            "instruction": "...",
            "input": "..." or an empty string "",
            "output": "...",
        },
        ...
    ]

Prompt-response:
    
    
    {
        "prompt": "...",
        "response": "...",
    },
    ...

The templates for text datasets can vary substantially, but the important thing is that they have already been pre-processed and use special tokens to separate the different components.

For example, with start and end prompt tokens:
    
    
    {
        "text": "<INST> ... </INST>: ...",
    },

Or with different tokens to indicate different speakers:
    
    
    {
        "text": "<human> ... <bot>: ...",
    },

## Final thoughts

While there is no single dataset format in use, the [AI](https://developers.redhat.com/aiml) community has begun to establish a few standards, particularly for chat-style datasets. This standardization makes it easier to train different model-dataset combinations. At Red Hat, we use Jinja templating and standardized dataset formats in our InstructLab training library to ensure that models are always fine-tuned with consistent prompting templates. To learn more about LLM post-training at Red Hat, visit [InstructLab](https://instructlab.ai/).