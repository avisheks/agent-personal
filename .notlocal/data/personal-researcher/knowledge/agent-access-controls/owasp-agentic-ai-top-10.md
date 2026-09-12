---
title: "OWASP Agentic AI Top 10"
summary: "A security framework that classifies the top 10 risks for agentic AI systems, including ASI05 (Unexpected Code Execution) which explicitly requires sandboxing as a mandatory control."
sources:
  - agent-access-controls/ai-agent-sandboxing-enterprise-security-guide-2026-beyondscale.md
createdAt: 2026-06-15T11:35:22.949720+00:00
updatedAt: 2026-06-15T11:35:22.949720+00:00
---
# OWASP Agentic AI Top 10

The **OWASP Agentic AI Top 10** is a security framework published by the Open Web Application Security Project (OWASP) in December 2025 that identifies and categorizes the top ten security risks specific to autonomous AI agents and agentic systems. This framework represents the first comprehensive security taxonomy specifically designed for AI systems that can execute code, call APIs, and perform actions without human approval at every step.

## Overview

The OWASP Agentic AI Top 10 addresses a fundamentally different threat model from traditional web applications or static LLM deployments. Unlike conventional systems where security controls focus on what attackers can send to an application, agentic systems require controls that limit what the AI agent can do to infrastructure when it has been instructed to perform unexpected actions. The framework emerged in response to data showing that 1 in 8 AI security breaches now involves an agentic system, according to HiddenLayer's 2026 AI Threat Landscape Report. ^[ai-agent-sandboxing-enterprise-security-guide.md]

The framework explicitly requires [[AI Agent Sandboxing]] as a mandatory control rather than a recommendation, recognizing that application-level security policies cannot adequately govern AI systems that execute shell commands, spawn subprocesses, and interact with external APIs autonomously. ^[ai-agent-sandboxing-enterprise-security-guide.md]

## Key Risk Categories

### ASI01: Indirect Prompt Injection
This risk category addresses attacks where malicious instructions are embedded in data sources that AI agents process, leading to unintended actions. The framework requires network egress controls and input validation as primary mitigations. ^[ai-agent-sandboxing-enterprise-security-guide.md]

### ASI02: Tool Misuse  
ASI02 covers scenarios where AI agents use legitimate tools in unintended ways or access tools beyond their authorized scope. The framework mandates network egress allowlists and tool access controls to limit the impact of this risk category. ^[ai-agent-sandboxing-enterprise-security-guide.md]

### ASI03: Identity and Privilege Abuse
This category addresses the risk of AI agents operating with excessive privileges or accessing credentials beyond their task requirements. The framework requires per-task credential provisioning and secrets scoping rather than inheriting full host environment credentials. ^[ai-agent-sandboxing-enterprise-security-guide.md]

### ASI05: Unexpected Code Execution
ASI05 is classified as a top-tier risk and states explicitly: "Never execute agent-generated code without strict sandboxing, input validation, and allowlisting." The framework requires that code execution sandboxes run in isolated containers with no network access and minimal system privileges. This risk category directly addresses vulnerabilities like CVE-2025-59528, where unsandboxed execution led to arbitrary code execution on host systems. ^[ai-agent-sandboxing-enterprise-security-guide.md]

### ASI10: Rogue Agents
This category covers AI agents that operate outside their intended parameters or exhibit unexpected autonomous behavior. The framework requires behavioral telemetry, kill switches, and circuit breakers as mandatory controls for rogue agent detection and containment. ^[ai-agent-sandboxing-enterprise-security-guide.md]

## Technical Requirements

The OWASP Agentic AI Top 10 establishes specific technical requirements for secure agentic deployments:

**Isolation Requirements**: The framework mandates kernel-level process isolation rather than application-level controls, recognizing that subprocesses spawned by native tool invocations can execute before security restrictions are evaluated. Standard Docker containers are explicitly deemed insufficient for AI agents that execute LLM-generated code. ^[ai-agent-sandboxing-enterprise-security-guide.md]

**Network Controls**: All agentic systems must implement network egress restrictions through explicit allowlists of required external endpoints, enforced at the network layer rather than through application logic. ^[ai-agent-sandboxing-enterprise-security-guide.md]

**Filesystem Protection**: The framework requires write protection for configuration directories, dotfiles, and auto-executing configuration files, as these can be exploited for privilege escalation and persistence. ^[ai-agent-sandboxing-enterprise-security-guide.md]

## Industry Adoption and Integration

The framework has been integrated into major enterprise AI governance toolkits. [[Microsoft Agent Governance Toolkit]] maps explicitly to all 10 OWASP Agentic risks and provides implementation guidance for LangChain, CrewAI, and Google ADK environments. NVIDIA's 2026 practical sandboxing guidance aligns with the OWASP requirements, establishing three mandatory controls that directly address ASI02, ASI03, and ASI05. ^[ai-agent-sandboxing-enterprise-security-guide.md]

## Relationship to CVE Disclosures

The framework's development was informed by real-world vulnerabilities in agentic systems. CVE-2025-59528 (CVSS 10.0) in Flowise AI Agent Builder, the Google Antigravity sandbox escape, and CVE-2025-59536 in Claude Code all demonstrate attack patterns that the OWASP Agentic Top 10 specifically addresses through its sandboxing and isolation requirements. ^[ai-agent-sandboxing-enterprise-security-guide.md]

## Assessment and Compliance

Security teams can use the framework as a pre-deployment checklist, with each control mapping to specific OWASP Agentic risks. The framework emphasizes that partial implementation creates false security, noting that an attacker who cannot call unauthorized network endpoints can still write malicious hook files or extract over-privileged credentials if other controls are missing. ^[ai-agent-sandboxing-enterprise-security-guide.md]

The complete taxonomy and implementation guidance is available at genai.owasp.org, providing detailed technical specifications for each risk category and its associated controls. ^[ai-agent-sandboxing-enterprise-security-guide.md]
