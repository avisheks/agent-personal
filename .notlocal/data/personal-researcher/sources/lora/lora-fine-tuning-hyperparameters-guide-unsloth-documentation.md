---
title: "LoRA fine-tuning Hyperparameters Guide | Unsloth Documentation"
source: "https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide"
ingestedAt: "2026-05-28T19:15:43Z"
---
Copy
    
    
    class UnslothVisionDataCollator:
    def __init__(
        self,
        ...
        # from unsloth.chat_templates import train_on_responses_only
        # trainer = train_on_responses_only(
        #     trainer,
        #     instruction_part = "<|start_header_id|>user<|end_header_id|>\n\n",
        #     response_part = "<|start_header_id|>assistant<|end_header_id|>\n\n",
        # )
        train_on_responses_only = False, # EQUIVALENT to train_on_responses_only for LLMs
        instruction_part = None, # EQUIVALENT to train_on_responses_only(instruction_part = ...)
        response_part    = None, # EQUIVALENT to train_on_responses_only(response_part = ...)
        force_match      = True, # Match newlines as well!
    )