---
title: "native-sandboxing"
summary: ""
sources:
  - claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md
createdAt: 2026-07-30T17:01:18.889073+00:00
updatedAt: 2026-07-30T17:01:18.889073+00:00
---
# Native Sandboxing

Native Sandboxing is a security isolation mechanism built into Claude Code that uses operating system-level primitives to restrict the execution environment of shell commands and tools. Unlike container-based solutions, native sandboxing leverages kernel-level security frameworks to provide process-level isolation with minimal overhead. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Architecture

Native sandboxing operates through a layered security model that enforces restrictions at the system call level: ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### OS-Level Enforcement

The sandboxing system uses different kernel mechanisms depending on the operating system:

- **macOS**: Seatbelt (TrustedBSD MAC framework) provides built-in, kernel-level system call filtering
- **Linux/WSL2**: bubblewrap with namespaces and seccomp for process isolation
- **WSL1**: Not supported due to missing kernel features
- **Windows**: Planned but not yet available

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Isolation Boundaries

Native sandboxing enforces three primary isolation boundaries:

**Filesystem Isolation**:
- Read access: Entire computer (except explicitly denied paths)
- Write access: Current working directory only (configurable)
- Blocked operations: Modifications outside CWD, access to credentials directories (`~/.ssh`, `~/.aws`)

**Network Isolation**:
- All connections routed through SOCKS5 proxy
- Domain filtering with allowlist/denylist modes
- Default blocking of private CIDRs and localhost ranges

**Process Isolation**:
- Shared kernel with host system
- Child processes inherit same sandbox restrictions
- Escape hatch available via `dangerouslyDisableSandbox` parameter

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Security Model

### Permission Integration

Native sandboxing integrates with Claude Code's [[permission-gating-system]] through two operational modes:

- **Auto-allow mode**: Bash commands automatically approved when sandboxed (recommended for daily development)
- **Regular permissions mode**: All commands require explicit approval (high-security environments)

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Security Limitations

While native sandboxing provides significant protection, it has several known limitations:

- **Domain fronting**: CDNs like Cloudflare and Akamai can bypass domain filtering
- **Unix sockets**: Misconfigured `allowUnixSockets` settings can grant privilege escalation
- **Filesystem scope**: Overly broad write permissions enable attacks on `$PATH` directories
- **Kernel vulnerabilities**: Shared kernel remains vulnerable to kernel exploits (unlike Docker microVM isolation)

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Implementation Details

### Setup Requirements

Native sandboxing requires minimal setup on most platforms:

| Platform | Requirements | Installation |
|----------|-------------|--------------|
| macOS | Built-in Seatbelt | None required |
| Linux/WSL2 | bubblewrap, socat | `sudo apt-get install bubblewrap socat` |
| WSL1 | Not supported | N/A |
| Windows | Not available | Planned |

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Performance Characteristics

Native sandboxing introduces minimal overhead compared to container-based alternatives:

| Aspect | Native Sandbox | Docker Sandboxes |
|--------|---------------|------------------|
| Kernel isolation | Shared kernel | Separate kernel per VM |
| Setup overhead | 0-2 packages | Docker Desktop 4.58+ |
| Runtime overhead | ~1-3% CPU | ~5-10% CPU |
| Use case | Daily dev, trusted code | Untrusted code, max security |

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Integration with Claude Code

### Tool Execution

Native sandboxing wraps all [[claude-code-agentic-system]] tool executions, particularly the Bash tool which serves as Claude's universal adapter for system operations. The sandbox wrapper intercepts system calls before they reach the kernel, enforcing the configured security policies. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

### Configuration Options

The sandboxing system can be configured through various parameters:

- Filesystem write boundaries (default: current working directory only)
- Network proxy settings and domain filtering rules
- Process isolation levels and child process inheritance
- Emergency escape mechanisms for incompatible tools

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Comparison with Container Sandboxing

Native sandboxing represents a different trade-off compared to container-based isolation:

**Advantages**:
- Minimal setup and maintenance overhead
- Lower runtime performance impact
- Direct integration with host development environment
- Suitable for trusted code and daily development workflows

**Disadvantages**:
- Shared kernel vulnerability surface
- Less isolation than microVM-based containers
- Platform-dependent implementation details
- Limited protection against sophisticated kernel exploits

^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]

## Related Concepts

Native sandboxing works in conjunction with several other Claude Code security mechanisms:

- [[permission-gating-system]] for user consent workflows
- [[ai-constitution]] principles that guide Claude's behavior
- [[constitutional-ai]] training that reduces the likelihood of harmful requests
- [[tool-selection-as-contextual-bandit]] for intelligent tool routing

The combination of these approaches provides defense-in-depth, where native sandboxing serves as the final enforcement layer after behavioral and permission-based controls. ^[claude-code/how-claude-code-works-architecture-internals-claude-code-guide.md]
