---
title: "three-tier-permission-system"
summary: ""
sources:
  - claude-code/claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md
createdAt: 2026-07-30T16:49:03.313541+00:00
updatedAt: 2026-07-30T16:49:03.313541+00:00
---
# Three-Tier Permission System

A **Three-Tier Permission System** is a security architecture used in AI agents and autonomous systems to govern what actions the system can take without explicit user authorization. This model categorizes operations into three distinct permission levels based on their potential impact and risk profile.

## Overview

The three-tier permission system provides a structured approach to balancing autonomous operation with user control and safety. It enables AI agents to perform safe operations automatically while requiring explicit approval for potentially dangerous actions and blocking certain operations entirely. This architecture is particularly important in production AI coding agents and other systems that can modify user data or system state. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

## The Three Tiers

### Tier 1: Always Allowed Operations

Tier 1 operations are considered safe and can be performed without user confirmation. These are typically read-only operations that do not modify any system state or user data. Examples include:

- File reads and directory listings
- Web content fetching
- Git status checks (non-destructive)
- Search operations within files or directories
- Database queries (read-only)

These operations are automatically permitted because they cannot cause data loss or system damage, though they may consume computational resources or reveal information. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

### Tier 2: Require Confirmation Operations

Tier 2 operations modify system state or user data and require explicit user approval before execution. The system presents a permission prompt showing exactly what action will be taken, allowing the user to approve, deny, or set persistent permissions. Examples include:

- File creation, modification, or deletion
- Shell command execution
- Database writes or modifications
- Network operations that send data
- Package installations

Users can typically choose "Allow Always" for specific operations or patterns, which stores the permission preference for future use in the same project context. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

### Tier 3: Never Allowed Operations

Tier 3 operations are considered too dangerous to permit under any circumstances through the normal permission system. These operations are blocked regardless of user settings or preferences. Examples include:

- System-level modifications outside the project scope
- Access to sensitive system files or directories
- Network operations to unauthorized endpoints
- Modification of the AI system's own configuration files
- Operations that could compromise system security

These restrictions help prevent accidental or malicious system damage even if the AI agent's reasoning becomes compromised. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

## Implementation Details

### Permission Storage

Permissions are typically stored in configuration files using glob-style patterns for flexible matching. The system maintains both global and project-specific permission settings:

```json
{
  "permissions": {
    "allow": [
      "Edit(*)",
      "Bash(git *)",
      "Bash(npm test)"
    ],
    "deny": [
      "Bash(rm -rf *)"
    ]
  },
  "projects": {
    "/path/to/project": {
      "permissions": {
        "allow": ["Bash(make *)"]
      }
    }
  }
}
```

### Permission Matching

The system uses pattern matching to determine whether an operation requires confirmation. Patterns can include wildcards and specific command prefixes to provide fine-grained control over what operations are automatically permitted. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

### Bypass Mechanisms

For automated environments such as CI/CD pipelines where no user is available to provide confirmation, systems may include bypass flags (such as `--dangerously-skip-permissions`) that disable confirmation prompts. These flags are typically named to discourage casual use and are intended only for non-interactive environments. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

## Benefits

The three-tier permission system provides several key advantages:

- **Safety**: Prevents accidental data loss or system damage by requiring confirmation for risky operations
- **Usability**: Allows safe operations to proceed automatically without interrupting the user
- **Flexibility**: Enables users to customize permission levels based on their trust and project requirements
- **Transparency**: Shows users exactly what actions the system wants to take before execution
- **Auditability**: Creates a clear record of what operations were performed and when they were authorized

## Related Concepts

The three-tier permission system is closely related to other security and AI safety concepts including [[ai-constitution]], [[scalable-oversight]], and [[tool-execution-engine-with-permissions]]. It represents a practical implementation of [[constitutional-ai]] principles in production systems where autonomous agents must balance capability with safety constraints. ^[claude-code-internal-architecture-deep-dive-how-anthropic-built-a-production-ai-coding-agent-dev-note.md]

## See Also

- [[permission-gating-system]]
- [[tool-execution-engine-with-permissions]]
- [[constitutional-ai]]
- [[claude-code-agentic-system]]
