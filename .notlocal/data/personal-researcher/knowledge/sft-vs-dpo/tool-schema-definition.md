---
title: "tool-schema-definition"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-openai-api.md
createdAt: 2026-05-20T03:42:05.561467+00:00
updatedAt: 2026-05-20T03:42:05.561467+00:00
---
# Tool Schema Definition

Tool Schema Definition refers to the structured specification that defines how language models can interact with external functions or tools. The schema provides a standardized format for describing function parameters, types, and requirements that enables models to make appropriate tool calls during conversations.

## Structure and Components

A tool schema consists of several key components that define the function interface. The schema includes a function name, description, and detailed parameter specifications. The parameters section uses JSON Schema format to define the expected input structure, including property types, descriptions, and required fields ^[supervised-fine-tuning-openai-api.md].

The schema follows a hierarchical structure where the top-level `tools` array contains function definitions. Each function definition includes metadata such as the function name and description, along with a `parameters` object that specifies the expected input format. Properties within the parameters object define individual arguments, their data types, descriptions, and validation constraints ^[supervised-fine-tuning-openai-api.md].

## Core Schema Elements

The tool schema definition includes several essential elements that work together to create a complete function specification. The `type` field indicates the tool category, typically set to "function" for callable operations. The `function` object contains the core definition with a `name` field for the function identifier and a `description` field that explains the function's purpose ^[supervised-fine-tuning-openai-api.md].

Within the `parameters` object, the schema defines the expected input structure using standard JSON Schema format. The `type` field specifies the overall parameter structure (commonly "object"), while the `properties` field contains individual parameter definitions. Each property includes its own type specification, description, and any applicable constraints such as enumerated values ^[supervised-fine-tuning-openai-api.md].

## Parameter Definition Format

Parameters in tool schemas use JSON Schema conventions to specify data types and constraints. String parameters can include enumerated values to restrict valid inputs, while object parameters can define nested properties with their own type specifications. The `required` array explicitly lists which parameters must be provided when calling the function ^[supervised-fine-tuning-openai-api.md].

For example, a weather function schema might define a `location` parameter as a string with a description indicating the expected format, and a `format` parameter as an enumerated string with specific allowed values like "celsius" or "fahrenheit". This structure ensures the model understands both what information to provide and how to format it correctly ^[supervised-fine-tuning-openai-api.md].

## Training Data Integration

Tool schemas are integrated into [[Supervised Fine-Tuning (SFT)]] datasets to teach models proper tool usage patterns. Training examples include the complete schema definition alongside example conversations that demonstrate correct tool calling behavior. This approach allows models to learn both the technical interface and the contextual application of tools ^[supervised-fine-tuning-openai-api.md].

The training format typically includes the schema definition in a `tools` field, paired with conversation examples that show appropriate tool calls. Each training example demonstrates how the model should interpret user requests and translate them into properly formatted function calls with the correct arguments ^[supervised-fine-tuning-openai-api.md].

## Parallel Tool Calls Configuration

Tool schemas can include configuration options that control how multiple tools are handled within a single interaction. The `parallel_tool_calls` field determines whether the model can invoke multiple functions simultaneously or must process them sequentially. This configuration affects both the training behavior and the runtime execution of tool-enabled models ^[supervised-fine-tuning-openai-api.md].

## Implementation Considerations

Tool schemas must balance specificity with flexibility to ensure reliable function calling while maintaining usability. Clear descriptions and well-defined parameter constraints help models make accurate tool calls, while overly restrictive schemas may limit the model's ability to handle varied user inputs effectively ^[supervised-fine-tuning-openai-api.md].

The schema design also impacts the model's ability to handle edge cases and parameter validation. Proper enumeration of allowed values and clear specification of required versus optional parameters helps prevent errors during tool execution and improves the overall reliability of tool-based interactions ^[supervised-fine-tuning-openai-api.md].
