---
title: "jsonl-training-data-format"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-openai-api.md
createdAt: 2026-05-20T03:41:38.197707+00:00
updatedAt: 2026-05-20T03:41:38.197707+00:00
---
# JSONL Training Data Format

JSONL (JSON Lines) is a text format used for training data where each line contains a separate, complete JSON object. This format is commonly used in machine learning applications, particularly for [[Supervised Fine-Tuning (SFT)]] of language models.

## Structure

In JSONL format, each line represents a single training example as a valid JSON object. The lines are not comma-separated, and the file does not require wrapping brackets like a standard JSON array. Each JSON object contains the complete information needed for one training instance.

## Training Data Components

### Messages Array
The core component of JSONL training data is the `messages` array, which contains the conversation structure. Each message object includes a `role` field (such as "user" or "assistant") and a `content` field containing the actual text or structured data for that turn in the conversation. ^[supervised-fine-tuning-openai-api.md]

### Tool Integration
JSONL training data can include tool calling capabilities through `tool_calls` arrays within assistant messages. These contain structured information about function calls, including the function name and arguments formatted as JSON strings. The training data also includes a `tools` array that defines the available functions with their descriptions, parameters, and required fields. ^[supervised-fine-tuning-openai-api.md]

### Configuration Fields
Additional fields control training behavior, such as `parallel_tool_calls` which determines whether multiple tools can be called simultaneously. These configuration options allow fine-tuning of model behavior during training. ^[supervised-fine-tuning-openai-api.md]

## Function Calling Training Examples

JSONL format is particularly effective for training models on function calling tasks. Each training example includes the user's natural language request, the assistant's structured tool call response with proper function names and JSON-formatted arguments, and comprehensive tool schemas that define available functions with their descriptions, parameter types, and required fields. ^[supervised-fine-tuning-openai-api.md]

The format supports complex scenarios where models need to learn both natural language understanding and structured output generation. Training examples demonstrate how user requests like "What is the weather in San Francisco?" are mapped to structured function calls with specific parameters including location and temperature format arguments. ^[supervised-fine-tuning-openai-api.md]

## Example Structure

A typical JSONL training example for function calling includes the user's query, the assistant's structured response with tool calls, and the complete tool definitions. Each line contains a complete training interaction with all necessary components: the conversation messages, tool call specifications with unique identifiers and function details, and function definitions with their parameters and requirements. ^[supervised-fine-tuning-openai-api.md]

Weather function examples show how each JSONL line contains a complete training case with the user's location query, the assistant's tool call with properly formatted location and temperature format arguments, and the full function schema including parameter types, descriptions, and required fields. The `get_current_weather` function demonstrates standard patterns with location parameters requiring city and country format, and format parameters offering celsius or fahrenheit options. ^[supervised-fine-tuning-openai-api.md]

## Tool Schema Definition

The `tools` array in JSONL training data provides comprehensive function definitions including the function type, name, description, and detailed parameter specifications. Parameters are defined with type information, descriptions, enumerated values where applicable, and required field lists. This structured approach enables models to learn proper function calling patterns and parameter validation. ^[supervised-fine-tuning-openai-api.md]

## Applications

JSONL format is particularly useful for training models on specific tasks like function calling, where the training data needs to demonstrate both natural language understanding and structured output generation. This format supports complex training scenarios while maintaining readability and ease of processing for machine learning pipelines. The format's line-by-line structure makes it efficient for streaming and processing large datasets during training. ^[supervised-fine-tuning-openai-api.md]
