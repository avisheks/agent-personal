---
title: "dataset-registration-pattern"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-oumi-oss.md
createdAt: 2026-05-18T18:34:09.978053+00:00
updatedAt: 2026-05-18T18:34:09.978053+00:00
---
# Dataset Registration Pattern

The Dataset Registration Pattern is a software design approach used in machine learning frameworks to enable dynamic discovery and instantiation of dataset classes. This pattern allows developers to register custom datasets with a central registry, making them available for use throughout the system without requiring explicit imports or hardcoded references.

## Overview

In the context of supervised fine-tuning systems, the Dataset Registration Pattern provides a mechanism for extending the available datasets without modifying core framework code. The pattern typically involves a decorator-based registration system that maps string identifiers to dataset class implementations. ^[supervised-fine-tuning-oumi-oss.md]

## Implementation Structure

### Base Class Architecture

The pattern relies on a base class that defines the common interface for all datasets. In [[Supervised Fine-Tuning (SFT)]] contexts, datasets typically inherit from a base class such as [[BaseSftDataset]], which provides standard functionality and defines required methods that subclasses must implement. ^[supervised-fine-tuning-oumi-oss.md]

### Registration Mechanism

Dataset classes are registered using a decorator that associates a string identifier with the class implementation. The `@register_dataset` decorator enables automatic registration of custom dataset classes in the framework's dataset registry. This decorator takes a string parameter that serves as the unique identifier for the dataset class. ^[supervised-fine-tuning-oumi-oss.md]

### Required Method Implementation

Registered datasets must implement specific transformation methods that define how raw data is converted into the expected format. For example, the `transform_conversation()` method converts raw dataset examples into structured [[Conversation Object]] instances with defined roles and content. The transformation method receives a dictionary representing one row of the raw dataset and returns a properly formatted conversation object. ^[supervised-fine-tuning-oumi-oss.md]

## Usage Patterns

### Configuration-Based Selection

The registration pattern enables dataset selection through configuration files, where datasets are specified by their registered names rather than class references. This approach decouples dataset selection from code implementation, allowing for flexible configuration management through the `dataset_name` parameter in training configurations. The configuration system supports additional parameters such as dataset split selection and streaming mode settings. ^[supervised-fine-tuning-oumi-oss.md]

### Programmatic Access

Registered datasets can be instantiated programmatically using builder functions that resolve the string identifier to the appropriate class. The `build_dataset()` function provides a consistent interface for dataset creation regardless of the underlying implementation, accepting parameters such as dataset name, tokenizer, and dataset split. This enables dynamic dataset instantiation in training loops and data processing pipelines. ^[supervised-fine-tuning-oumi-oss.md]

## Extension Mechanisms

### Dataset Name Override

The pattern supports using datasets with compatible formats without explicit registration through a dataset name override mechanism. This allows leveraging existing registered dataset classes with different data sources by specifying a `dataset_name_override` parameter in the dataset configuration. This feature enables reuse of dataset processing logic across multiple data sources with identical formats, particularly useful for datasets on platforms like Hugging Face that share common structures. ^[supervised-fine-tuning-oumi-oss.md]

### Custom Dataset Integration

New datasets can be added to the system by implementing the required interface and registering with the appropriate decorator. The registration process involves subclassing the base dataset class, implementing required transformation methods such as `transform_conversation()`, and using the registration decorator to make the dataset discoverable by the framework. Custom datasets must handle the conversion of raw data examples into the expected conversation format with proper role assignments and content structuring. ^[supervised-fine-tuning-oumi-oss.md]

## Implementation Example

A typical implementation follows this structure:

- Subclass the base dataset class (e.g., [[BaseSftDataset]])
- Apply the `@register_dataset("dataset_identifier")` decorator
- Implement the `transform_conversation()` method to handle data transformation
- Initialize the dataset with required parameters including configuration, tokenizer, and dataset split

The transformation method processes raw examples containing input-output pairs and converts them into conversation objects with user and assistant message roles. ^[supervised-fine-tuning-oumi-oss.md]

## Benefits

The Dataset Registration Pattern provides several advantages for machine learning systems:

- **Modularity**: Datasets can be developed and maintained independently of the core framework
- **Extensibility**: New datasets can be added without modifying existing code
- **Configuration Flexibility**: Dataset selection can be managed through configuration rather than code changes
- **Discoverability**: All available datasets are accessible through a unified interface
- **Reusability**: Compatible datasets can leverage existing processing logic through override mechanisms

The pattern is particularly valuable in frameworks that need to support diverse data sources and formats while maintaining a consistent processing pipeline. It enables both configuration-driven and programmatic dataset selection, supporting various deployment and development workflows. ^[supervised-fine-tuning-oumi-oss.md]
