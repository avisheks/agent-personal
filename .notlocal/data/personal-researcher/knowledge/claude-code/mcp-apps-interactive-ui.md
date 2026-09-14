---
title: "mcp-apps-interactive-ui"
summary: ""
sources:
  - claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md
createdAt: 2026-07-30T17:00:39.073460+00:00
updatedAt: 2026-07-30T17:00:39.073460+00:00
---
# MCP Apps Interactive UI

MCP Apps Interactive UI is the **first official extension** to the [[Model Context Protocol (MCP)]], enabling MCP servers to deliver interactive user interfaces alongside traditional tool responses. Released as stable on January 26, 2026, it addresses the "context gap" problem where exploration workflows require multiple prompt cycles for each interaction (sort, filter, drill-down). ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Overview

MCP Apps eliminates friction in workflows requiring exploration by rendering interactive UIs directly in the conversation. Instead of text-based responses that create round-trip delays, users can interact with dashboards, forms, and visualizations in real-time within their AI assistant interface. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

The extension was co-authored by OpenAI, Anthropic, and MCP-UI creators as SEP-1865 on GitHub, providing a unified specification that standardizes patterns pioneered by earlier community projects like MCP-UI and OpenAI Apps SDK. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Architecture

### Core Primitives

MCP Apps introduces two fundamental primitives to the [[Model Context Protocol (MCP)]]:

**Tools with UI metadata** that specify interactive capabilities:
```json
{
  "name": "query_database",
  "description": "Query customer database",
  "ui": {
    "resourceUri": "ui://dashboard/customers"
  }
}
```

**UI Resources** using the `ui://` scheme that contain server-side HTML/JavaScript bundles rendered in sandboxed iframes by the host application. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

### Communication Flow

The architecture establishes bidirectional JSON-RPC communication between MCP clients, servers, and rendered UIs through a secure messaging layer. The MCP Client (Claude/IDE) communicates with the MCP Server via JSON-RPC, while the server provides UI resources that render in sandboxed iframes. These iframes communicate back to the host through postMessage and JSON-RPC protocols. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Security Model

MCP Apps implements multi-layered protection to ensure safe execution of interactive components:

- **Iframe sandbox**: Restricted permissions preventing direct system access
- **Pre-declared templates**: Hosts review HTML/JS before rendering  
- **Auditable messaging**: All UI-to-host communication logged via JSON-RPC
- **User consent**: Optional requirement for UI-initiated tool calls
- **Content blocking**: Hosts can reject suspicious resources pre-render ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Implementation

### Core API

The framework-agnostic API provides essential capabilities for UI development:

```javascript
import { App } from '@modelcontextprotocol/ext-apps';

// Establish communication with host
const app = new App();

// Receive tool results from host
app.ontoolresult = (result) => {
  updateDashboard(result.data);
};

// Call server tools from UI
await app.callServerTool('fetch_analytics', {
  metrics: ['users', 'revenue']
});

// Update model context asynchronously
await app.updateModelContext({
  selectedFilters: ['region:EU', 'status:active']
});
```

Additional capabilities include debug logging, browser link opening, and follow-up message sending, all operating over standard `postMessage` communication without framework lock-in. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

### Installation

MCP Apps can be installed via npm:
```bash
npm install @modelcontextprotocol/ext-apps
```

## Platform Support

Platform support varies across different AI development environments:

| Platform | Support Status | Notes |
|----------|---------------|-------|
| **Claude Desktop** | ✅ Available | claude.ai/directory (Pro/Max/Team/Enterprise) |
| **VS Code** | ✅ Insiders build | Official blog post available |
| **ChatGPT** | 🔄 Rolling out | Week of Jan 26, 2026 |
| **Goose** | ✅ Available | Open-source CLI with UI support |
| **[[Claude Code CLI Tool]]** | ❌ N/A | Terminal text-only (no iframe rendering) |

^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Use Cases and Applications

### Decision Framework

For MCP server developers, the decision tree for implementing MCP Apps includes:

- Users need to SELECT from 50+ options → MCP Apps (dropdown, multi-select UI)
- Users need to VISUALIZE data patterns → MCP Apps (charts, maps, graphs)  
- Users need MULTI-STEP workflows with conditional logic → MCP Apps (wizard forms)
- Users need REAL-TIME updates → MCP Apps (live dashboards)
- Simple data retrieval or actions only → Traditional MCP tools (sufficient) ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

### Production Examples

Official example servers in the `ext-apps` repository demonstrate various capabilities:

- **threejs-server**: 3D visualization and manipulation
- **map-server**: Interactive geographic data exploration
- **pdf-server**: Document viewing with inline highlights
- **system-monitor-server**: Real-time metrics dashboards
- **sheet-music-server**: Music notation rendering ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

Production adoption as of January 2026 includes tools from Asana (project timelines), Slack (message drafting), Figma (flowcharts), Amplitude (analytics charts), Box (file search), Canva (presentation design), Clay (company research), Hex (data analysis), and monday.com (work management boards). ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Relationship to Claude Code

While [[claude-code-agentic-system]] operates as a terminal-only text interface and cannot directly render MCP Apps, there are several indirect benefits for CLI users:

1. **Ecosystem understanding**: MCP Apps represents the future direction of agentic workflows
2. **MCP server development**: When building custom MCP servers, Apps becomes a design option
3. **Hybrid workflows**: Use Claude Desktop for data exploration with Apps, then switch to [[Claude Code CLI Tool]] for implementation
4. **Configuration context**: MCP servers may advertise UI capabilities in metadata ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

## Technical Limitations

The trade-off for MCP Apps involves increased UI complexity and implementation effort versus user experience improvement. The extension requires careful consideration of when interactive interfaces provide sufficient value over traditional text-based tool responses. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]

MCP Apps standardizes the interactive UI extension pattern while maintaining compatibility with existing MCP infrastructure, providing a migration path for existing MCP-UI and Apps SDK implementations. ^[how-claude-code-works-architecture-internals-claude-code-guide.md]
