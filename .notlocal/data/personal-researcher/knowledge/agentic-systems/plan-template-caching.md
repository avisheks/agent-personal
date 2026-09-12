---
title: "plan-template-caching"
summary: ""
sources:
  - agentic-systems/agentic-systems-ref.md
createdAt: 2026-05-28T19:57:12.379882+00:00
updatedAt: 2026-05-28T19:57:12.379882+00:00
---
# Plan Template Caching

Plan Template Caching is an optimization technique for [[Agentic Cost Optimization]] that reduces computational overhead in multi-step agent systems by pre-computing and storing common planning patterns. Rather than generating plans from scratch for each task, agents classify incoming requests and retrieve appropriate templates that can be personalized with specific parameters. ^[agentic-systems-ref.md]

## Overview

In production agentic systems, a significant portion of tasks follow predictable patterns. Plan Template Caching exploits this regularity by identifying recurring task structures and caching their optimal execution plans. When a new task arrives, the system first attempts to match it against existing templates before falling back to full planning. ^[agentic-systems-ref.md]

The technique addresses the fundamental cost scaling challenge in [[Multi-Agent Orchestration]] systems, where each planning step requires expensive LLM calls. By converting planning from a generation problem to a retrieval and personalization problem, systems can achieve 4-5x cost reduction for template-matching tasks. ^[agentic-systems-ref.md]

## Architecture

Plan Template Caching operates through a three-stage pipeline:

### Task Classification
Incoming requests are classified to determine if they match known patterns. This classification can be rule-based (keyword matching), embedding-based (semantic similarity), or learned (trained classifier). The classifier routes tasks to either the template path or full planning path. ^[agentic-systems-ref.md]

### Template Retrieval and Personalization
For template-matching tasks, the system retrieves the appropriate plan template and personalizes it with task-specific parameters. For example, a "suggest keywords for existing campaign" template might be personalized with the specific advertiser ID, campaign type, and performance metrics. ^[agentic-systems-ref.md]

### Execution
The personalized template is executed directly, bypassing the planning phase entirely. This reduces the typical 7-8 LLM calls per task to 3-4 calls focused on execution and synthesis. ^[agentic-systems-ref.md]

## Implementation Patterns

### Template Structure
Templates are typically stored as structured plans with parameterized slots. Each template defines a sequence of actions with variable parameters that can be filled at runtime based on the specific task context. ^[agentic-systems-ref.md]

### Template Discovery
Templates are typically discovered through analysis of production trajectories. Systems log successful task executions and identify common patterns through clustering or manual analysis. Templates are validated by ensuring they maintain high task completion rates when applied to similar requests. ^[agentic-systems-ref.md]

## Performance Characteristics

Plan Template Caching provides significant performance improvements across multiple dimensions:

### Cost Reduction
Template-based execution reduces per-task costs from approximately $0.04-$0.05 to $0.01-$0.015, representing a 70-80% cost reduction for matching tasks. The savings come primarily from eliminating planning LLM calls while maintaining execution quality. ^[agentic-systems-ref.md]

### Latency Improvement
By skipping the planning phase, template-based execution reduces task completion time by 30-50%. This improvement is particularly valuable for [[Human-in-the-Loop Agent Design]] systems where users expect responsive interactions. ^[agentic-systems-ref.md]

### Reliability
Templates represent proven execution paths that have succeeded in production. This reduces the risk of planning errors or suboptimal tool selection that can occur with novel plan generation. ^[agentic-systems-ref.md]

## Production Considerations

### Template Coverage
The effectiveness of Plan Template Caching depends on achieving high template coverage of production workloads. Systems typically aim for 60-80% template coverage, with the remaining 20-40% of novel tasks handled through full planning. Coverage analysis helps identify opportunities for new template creation. ^[agentic-systems-ref.md]

### Template Maintenance
Templates require ongoing maintenance as underlying tools, APIs, or business logic evolve. Systems must implement template versioning and validation to ensure cached plans remain effective. Automated testing can detect when templates begin failing and trigger updates. ^[agentic-systems-ref.md]

### Fallback Mechanisms
Robust implementations include fallback to full planning when template execution fails or when confidence in template matching is low. This ensures system reliability while maintaining the performance benefits of caching for well-understood tasks. ^[agentic-systems-ref.md]

## Integration with Other Patterns

Plan Template Caching works synergistically with other optimization techniques:

- **[[ReAct Pattern]]**: Templates can incorporate ReAct-style reasoning traces for auditability while caching the overall structure
- **[[Tool Selection as Contextual Bandit]]**: Template parameters can include learned tool preferences based on historical performance
- **[[Trajectory-Level Evaluation]]**: Template effectiveness is measured through trajectory evaluation metrics rather than individual step accuracy

## Limitations

Plan Template Caching is most effective for systems with recurring task patterns and may provide limited benefit for highly novel or exploratory workloads. The technique requires upfront investment in template discovery and maintenance infrastructure. Additionally, over-reliance on templates can reduce system adaptability to changing requirements or novel edge cases. ^[agentic-systems-ref.md]

Systems must balance template coverage with flexibility, ensuring that the pursuit of optimization doesn't constrain the system's ability to handle genuinely novel tasks that require creative planning approaches. ^[agentic-systems-ref.md]
