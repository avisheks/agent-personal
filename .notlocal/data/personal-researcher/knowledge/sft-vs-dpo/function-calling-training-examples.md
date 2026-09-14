---
title: "function-calling-training-examples"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-openai-api.md
createdAt: 2026-05-20T03:41:50.588062+00:00
updatedAt: 2026-05-20T03:41:50.588062+00:00
---
# Function Calling Training Examples

Function calling training examples are structured datasets used in [[Supervised Fine-Tuning (SFT)]] to teach language models how to properly invoke external functions or tools. These examples demonstrate the correct format and behavior for function calls within conversational contexts. ^[supervised-fine-tuning-openai-api.md]

## JSONL Format Structure

Function calling training data is typically formatted as JSONL (JSON Lines), where each line represents a complete training example. Each example contains several key components that define the interaction pattern between user queries and assistant responses with function calls. ^[supervised-fine-tuning-openai-api.md]

### Core Components

The training examples include the following essential elements:

- **Messages array**: Contains the conversation flow between user and assistant
- **Tool calls**: Specifies the function to be called with proper parameters
- **Tools definition**: Describes available functions, their parameters, and requirements
- **Parallel tool calls flag**: Controls whether multiple functions can be called simultaneously

^[supervised-fine-tuning-openai-api.md]

### Example Structure

A typical function calling training example follows this pattern:

- User provides a natural language request
- Assistant responds with a structured tool call containing function name and arguments
- The tool definition specifies the function schema, including parameter types and requirements

^[supervised-fine-tuning-openai-api.md]

## Weather Function Example

The source material demonstrates a weather querying function called `get_current_weather`. This function accepts location and format parameters, where location specifies the city and country, and format determines the temperature unit (celsius or fahrenheit). The training examples show consistent patterns across different cities, teaching the model to extract location information from user queries and format it appropriately for the function call. ^[supervised-fine-tuning-openai-api.md]

## Training Data Characteristics

Function calling training examples exhibit several important characteristics:

- **Consistency**: All examples follow the same structural pattern and parameter formatting
- **Variation**: Different input queries (various cities) demonstrate generalization across similar use cases  
- **Completeness**: Each example includes both the conversational context and the complete tool definition

^[supervised-fine-tuning-openai-api.md]

## Tool Schema Definition

Each training example includes a comprehensive tool schema definition that specifies the function's interface. The schema defines the function name, description, parameter types, and required fields. In the weather example, the schema specifies that the location parameter must be a string describing "the city and country" and the format parameter must be an enum with values "celsius" or "fahrenheit". Both parameters are marked as required, ensuring the model learns to provide complete function calls. ^[supervised-fine-tuning-openai-api.md]

## Training Pattern Consistency

The training data demonstrates remarkable consistency across multiple examples. Each weather query follows identical formatting patterns: the location is always formatted as "City, Country" (e.g., "San Francisco, USA"), and the format is consistently set to "celsius". This repetitive structure helps the model learn reliable patterns for parameter extraction and formatting from natural language queries. ^[supervised-fine-tuning-openai-api.md]

## Dataset Composition

The provided examples showcase training data for a single function across multiple geographic locations including San Francisco, Minneapolis, San Diego, Memphis, Atlanta, Sunnyvale, Chicago, Boston, Honolulu, and San Antonio. Each example maintains identical structure while varying only the specific city name, creating a comprehensive dataset that teaches the model to generalize location extraction patterns across different urban contexts. ^[supervised-fine-tuning-openai-api.md]

These training examples enable models to learn the mapping between natural language requests and structured function calls, which is essential for building AI systems that can interact with external tools and APIs effectively.
