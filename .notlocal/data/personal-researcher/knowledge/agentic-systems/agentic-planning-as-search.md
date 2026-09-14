---
title: "agentic-planning-as-search"
summary: ""
sources:
  - agentic-systems/agentic-systems-ref.md
createdAt: 2026-05-28T19:56:43.026878+00:00
updatedAt: 2026-05-28T19:56:43.026878+00:00
---
# Agentic Planning as Search

Agentic planning can be formalized as a search problem over a tree of possible action sequences, where each node represents a state and each edge represents an action. This computational framework provides a structured approach to understanding and optimizing how [[Multi-Agent Orchestration]] systems make decisions in complex, multi-step tasks. ^[agentic-systems-ref.md]

## Core Formulation

In the search formulation, an agent must navigate through a state space where each decision point branches into multiple possible actions. The challenge lies in the exponential growth of possibilities: a 10-step agent with 5 possible actions per step has 5^10 ≈ 10 million possible trajectories, making exhaustive search computationally intractable. ^[agentic-systems-ref.md]

The search problem is defined by:
- **State space**: All possible configurations of the agent's working memory and environment
- **Action space**: Available tools and operations at each decision point  
- **Transition function**: How actions change the current state
- **Reward function**: Quality assessment of final outcomes or intermediate progress ^[agentic-systems-ref.md]

## Search Algorithms for Planning

### Monte Carlo Tree Search (MCTS)

MCTS applies to agentic planning by simulating multiple random rollouts from each decision node. At each node, the algorithm simulates future action sequences, scores each rollout by final reward (task completion quality), and back-propagates scores to inform future exploration. The selection policy uses UCB1: mean_reward + C * sqrt(ln(parent_visits) / child_visits). ^[agentic-systems-ref.md]

For agents, each simulation requires LLM calls, making MCTS expensive but practical when action spaces are small and task value justifies the computational cost, particularly for high-stakes decisions. ^[agentic-systems-ref.md]

### Beam Search

Beam search maintains K candidate plans in parallel. At each step, it expands all K plans with possible next actions, generating K*B candidates, then prunes back to the top-K by score. The scoring function typically combines LLM confidence in the plan with heuristic quality assessment. ^[agentic-systems-ref.md]

This approach proves more practical than MCTS for production [[Agentic Cost Optimization]], as it keeps 3-5 candidate plans, scores them, and eliminates low-quality plans early in the process. ^[agentic-systems-ref.md]

### Tree of Thought (ToT)

Tree of Thought provides explicit tree decomposition where the LLM generates multiple thought branches at each step. Each branch is evaluated with a value function (typically another LLM call asking "Is this thought path promising?"), and the system performs breadth-first or depth-first search through the thought tree. ^[agentic-systems-ref.md]

ToT naturally fits multi-step planning where intermediate steps can be evaluated, though it requires 3-5x more LLM calls than greedy single-path planning. The cost is justified when wrong plans have high consequences. ^[agentic-systems-ref.md]

## Practical Bounding Strategies

### Action Space Reduction

The most effective optimization involves pre-filtering tools by task type before search begins. If a task involves "report generation," the system excludes bid-modification tools entirely, reducing the action space from 50 to 5-10 options. This transforms the complexity from 5^10 to approximately 3*4*3*2*3*2*3*2*2*2 ≈ 5,184 trajectories. ^[agentic-systems-ref.md]

### Hierarchical Decomposition

Complex tasks can be decomposed into sub-goals, with independent search within each sub-goal. A 10-step task becomes 3 sub-goals of 3-4 steps each, reducing complexity from 5^10 = 10M to 3 * (5^3) = 375 possible paths. The trade-off involves sub-optimal transitions between sub-goals, as inter-sub-goal transitions aren't globally optimized. ^[agentic-systems-ref.md]

### Plan Templates

For recurring task patterns, systems can pre-compute optimal plan templates and reduce runtime planning to template matching. This approach handles 60-80% of tasks through classification and template retrieval, reserving full search for truly novel requests. ^[agentic-systems-ref.md]

## Search vs. Execution Trade-offs

The choice between search algorithms depends on task characteristics and constraints:

- **Greedy with look-ahead**: Suitable for simple tasks (1-3 steps) where one plan execution is sufficient
- **Beam search with K=3**: Appropriate for medium tasks (3-7 steps) requiring multiple candidate evaluation  
- **Tree of Thought with explicit evaluation**: Justified for complex/high-stakes tasks where wrong plans have significant consequences ^[agentic-systems-ref.md]

## Verification in Search Context

When search identifies wrong tool selection or generates hallucinated tool calls, the system requires validation at each search node. [[Tool Selection as Contextual Bandit]] approaches can complement search by providing learned priors that narrow the search space to high-probability tools, converting a 50-wide tree into an effectively 3-5-wide tree at each level. ^[agentic-systems-ref.md]

The search formulation also enables systematic handling of [[Agent State Space Explosion]] through bounded search strategies that maintain tractability while preserving solution quality for production [[Multi-Agent Orchestration]] systems. ^[agentic-systems-ref.md]
