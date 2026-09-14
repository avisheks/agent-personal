---
title: "checkpoint-based-file-safety"
summary: ""
sources:
  - claude-code/how-claude-code-works-claude-code-docs.md
createdAt: 2026-07-30T17:02:30.631822+00:00
updatedAt: 2026-07-30T17:02:30.631822+00:00
---
# Checkpoint-Based File Safety

Checkpoint-Based File Safety is a safety mechanism in [[claude-code-agentic-system]] that automatically creates reversible snapshots of files before any modifications are made. This system ensures that all file edits can be undone, providing a safety net for agentic AI operations that modify code and documents.

## How It Works

Before Claude edits any file, the system automatically snapshots the current contents of that file. These snapshots are stored locally and are tied to the specific session, operating independently from version control systems like git. The checkpointing mechanism only covers file changes and does not extend to actions that affect remote systems such as databases, APIs, or deployments. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Recovery Mechanisms

Users can recover from unwanted changes through multiple methods. Pressing the Escape key twice allows rewinding to a previous state, effectively undoing recent file modifications. Alternatively, users can ask Claude directly to undo changes through natural language commands. These checkpoints remain available throughout the session, enabling recovery at any point during the conversation. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Scope and Limitations

Checkpoint-Based File Safety has specific boundaries in its coverage. The system only protects file modifications and cannot checkpoint actions with external side effects. This limitation is why Claude requests permission before running commands that could affect remote systems, databases, or external services. The checkpoints are session-local, meaning they exist only within the current Claude Code session and are separate from any git history or other version control mechanisms. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Integration with Permission Systems

The checkpoint system works in conjunction with [[permission-gating-system]] to provide comprehensive safety controls. While checkpoints handle the recovery aspect of file safety, the permission system controls what actions Claude can perform without explicit user approval. This dual-layer approach ensures both preventive and corrective safety measures are in place for agentic file operations. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Session Management

Checkpoints are managed within the broader context of [[session-persistence-and-management]], where each conversation is saved locally as a plaintext JSONL file. The checkpoint data is stored alongside session information under the `~/.claude/projects/` directory, enabling persistent recovery capabilities across session interruptions and resumptions. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Safety Architecture

The checkpoint system represents one component of Claude Code's multi-layered safety architecture. It provides the "undo" capability that complements the "ask first" approach of the permission system. This combination allows users to work confidently with an agentic system, knowing that file changes can always be reversed while maintaining control over what actions the system can perform autonomously. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## Technical Implementation

The checkpoint mechanism operates at the file level, creating snapshots before any modification occurs. These snapshots are stored locally and tied to the specific session context, ensuring that recovery operations are available throughout the entire working session. The system maintains these checkpoints independently of any existing version control systems, providing an additional layer of safety specifically designed for agentic operations. ^[claude-code/how-claude-code-works-claude-code-docs.md]

## User Experience

The checkpoint system is designed to be transparent to users during normal operation while providing immediate recovery options when needed. Users can trigger recovery through keyboard shortcuts (pressing Escape twice) or through conversational commands to Claude. This dual interface ensures that recovery is accessible both through direct user action and through the same conversational interface used for other Claude Code operations. ^[claude-code/how-claude-code-works-claude-code-docs.md]
