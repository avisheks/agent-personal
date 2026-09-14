---
title: "parallel-tool-calls-configuration"
summary: ""
sources:
  - sft-vs-dpo/supervised-fine-tuning-openai-api.md
createdAt: 2026-05-20T03:42:17.849458+00:00
updatedAt: 2026-05-20T03:42:17.849458+00:00
---
# Parallel Tool Calls Configuration

**Parallel Tool Calls Configuration** is a parameter used in [[Supervised Fine-Tuning (SFT)]] training data to control whether a language model should execute multiple tool calls simultaneously or sequentially. This configuration appears as a boolean field in training examples and influences how models handle function calling behavior during inference.

## Configuration Structure

The parallel tool calls configuration is specified as a boolean field within training data examples. In [[JSONL Training Data Format]] training files, it appears as `"parallel_tool_calls": false` or `"parallel_tool_calls": true` alongside the messages, tool definitions, and tool calls. ^[supervised-fine-tuning-openai-api.md]

## Training Data Integration

When preparing [[Supervised Fine-Tuning (SFT)]] datasets for function calling capabilities, each training example includes the parallel tool calls setting. This allows the model to learn appropriate behavior patterns for different scenarios where tools should be called sequentially versus simultaneously. The configuration works in conjunction with [[Tool Schema Definition]] and assistant responses that demonstrate the desired calling pattern. ^[supervised-fine-tuning-openai-api.md]

## Sequential Execution Pattern

In the provided training examples, all instances use `"parallel_tool_calls": false`, indicating that the model should execute tool calls one at a time rather than concurrently. This sequential approach is demonstrated across various weather query examples, where each assistant response contains a single tool call for retrieving weather information for a specific location. ^[supervised-fine-tuning-openai-api.md]

## Function Calling Training Context

The parallel tool calls configuration operates alongside [[Function Calling Training Examples]] that specify function parameters, descriptions, and required fields. While the tool definitions describe what functions are available and how to call them, the parallel configuration determines the execution strategy when multiple tools might be invoked in response to a single user request. ^[supervised-fine-tuning-openai-api.md]

## Training Data Format Structure

Each training example in the JSONL format includes the parallel tool calls configuration as part of a complete training record that contains:

- Messages array with user requests and assistant responses
- Tool calls with function names and arguments  
- Tool definitions with schemas and descriptions
- The parallel tool calls boolean setting

This comprehensive structure enables models to learn both the mechanics of tool calling and the appropriate execution patterns for different scenarios. The weather function examples demonstrate consistent use of sequential execution across multiple training instances, each targeting different geographic locations while maintaining the same tool schema and execution pattern. ^[supervised-fine-tuning-openai-api.md]

## Behavioral Implications

The parallel tool calls configuration directly impacts model inference behavior during function calling scenarios. When set to `false`, the model learns to process tool calls sequentially, which can be important for scenarios where tool outputs may depend on each other or where system resources need to be managed carefully. This training approach ensures that fine-tuned models respect the intended execution pattern specified in the training data. ^[supervised-fine-tuning-openai-api.md]

## Example Implementation

The weather function training examples consistently demonstrate the sequential execution pattern across ten different cities including San Francisco, Minneapolis, San Diego, Memphis, Atlanta, Sunnyvale, Chicago, Boston, Honolulu, and San Antonio. Each example follows the identical structure with `"parallel_tool_calls": false` and the same `get_current_weather` function definition, showing how the configuration maintains consistency across diverse geographic queries while teaching the model the appropriate execution behavior. ^[supervised-fine-tuning-openai-api.md]
