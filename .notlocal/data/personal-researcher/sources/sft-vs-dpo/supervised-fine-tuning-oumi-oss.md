---
title: "Supervised Fine-Tuning - Oumi OSS"
source: "https://oumi.ai/docs/en/latest/resources/datasets/sft_datasets.html"
ingestedAt: "2026-05-18T00:50:08Z"
---
# Supervised Fine-Tuning

Supervised Fine-Tuning (SFT) is the most common approach for adapting a pre-trained language model to specific downstream tasks. This involves fine-tuning the modelâs parameters on a labeled dataset of input-output pairs, effectively teaching the model to perform the desired task.

This guide covers datasets used for using SFT datasets in Oumi OSS.

## SFT Datasets

Out-of-the box, we support multiple popular SFT datasets:

## Usage

### Configuration

To use a specific SFT dataset in your Oumi OSS configuration, specify it in the [`TrainingConfig`](../../api/oumi.core.configs.html#oumi.core.configs.TrainingConfig "oumi.core.configs.TrainingConfig").

Hereâs an example:
    
    
    training:
      data:
        train:
          datasets:
            - dataset_name: your_sft_dataset_name
              split: train
              stream: false
          collator_name: text_with_padding
    

In this configuration:

  * [`dataset_name`](../../api/oumi.core.configs.html#oumi.core.configs.DatasetParams.dataset_name "oumi.core.configs.DatasetParams.dataset_name") specifies the name of your SFT dataset

  * [`split`](../../api/oumi.core.configs.html#oumi.core.configs.DatasetParams.split "oumi.core.configs.DatasetParams.split") selects a specific dataset split (e.g., train, validation, test)

  * `stream` enables streaming mode for large datasets

  * [`collator_name`](../../api/oumi.core.configs.html#oumi.core.configs.DatasetSplitParams.collator_name "oumi.core.configs.DatasetSplitParams.collator_name") specifies the collator to use for batching




### Python API

To use a specific SFT dataset in your code, you can use the `build_dataset()` function:
    
    
    from oumi.builders import build_dataset
    from oumi.core.configs import DatasetSplit
    from torch.utils.data import DataLoader
    
    # Assume you have your tokenizer initialized
    tokenizer = ...
    
    # Build the dataset
    dataset = build_dataset(
        dataset_name="your_sft_dataset_name",
        tokenizer=tokenizer,
        dataset_split=DatasetSplit.TRAIN
    )
    
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Now you can use the dataset in your training loop
    for batch in loader:
        # Process your batch
        ...
    

## Adding a New SFT Dataset

All SFT datasets in Oumi OSS are subclasses of [`BaseSftDataset`](../../api/oumi.core.datasets.html#oumi.core.datasets.BaseSftDataset "oumi.core.datasets.BaseSftDataset").

To add a new SFT dataset:

  1. Subclass [`BaseSftDataset`](../../api/oumi.core.datasets.html#oumi.core.datasets.BaseSftDataset "oumi.core.datasets.BaseSftDataset")

  2. Implement the [`transform_conversation()`](../../api/oumi.core.datasets.html#oumi.core.datasets.BaseSftDataset.transform_conversation "oumi.core.datasets.BaseSftDataset.transform_conversation") method to define the dataset-specific transformation logic.

  3. Register your new dataset to the dataset class by adding it to `py` and `py`.




For example:
    
    
    from oumi.core.datasets import BaseSftDataset
    from oumi.core.types.conversation import Conversation, Message, Role
    from oumi.core.registry import register_dataset
    
    @register_dataset("custom_sft_dataset")
    class CustomSftDataset(BaseSftDataset):
        def __init__(self, config: TrainingConfig,
                     tokenizer: BaseTokenizer,
                     dataset_split: DatasetSplit):
            super().__init__(config, tokenizer, dataset_split)
            # Initialize your dataset here
    
        def transform_conversation(self, example: Dict[str, Any]) -> Conversation:
            # Transform the raw example into a Conversation object
            # 'example' represents one row of the raw dataset
            # Structure of 'example':
            # {
            #     'input': str,  # The user's input or question
            #     'output': str  # The assistant's response
            # }
            conversation = Conversation(
                messages=[
                    Message(role=Role.USER, content=example['input']),
                    Message(role=Role.ASSISTANT, content=example['output'])
                ]
            )
    
            return conversation
    

Tip

For more advanced SFT dataset implementations, explore the `oumi.datasets` module, which contains implementations of several [open source datasets](https://github.com/oumi-ai/oumi/tree/main/src/oumi/datasets).

### Using an Unregistered Dataset Whose Format is Identical to a Registered Dataset

Many datasets on Hugging Face share the same format as Oumi OSS registered datasets. It is not necessary to register each dataset explicitly to use it. Instead, you can override the `dataset_name` parameter using a keyword argument; see the code snippet below for an example of how to do this.
    
    
    - dataset_name: registered_hf_dataset_with_compatible_class
      dataset_kwargs:
      - dataset_name_override: hf_dataset_with_data_to_use
    

NOTE: This feature is experimental, and we expect it to change in a future release.

### Using Custom Datasets via the CLI

See [Customizing Oumi OSS](../../user_guides/customization.html) to quickly enable your dataset when using the CLI.