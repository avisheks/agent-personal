---
title: "AI Agent Sandboxing: 3 Isolation Patterns for 2026"
source: "https://www.digitalapplied.com/blog/ai-agent-sandboxing-isolation-patterns-2026"
ingestedAt: "2026-06-15T11:11:12Z"
---
AI agent sandboxing is the discipline of constraining what an autonomous agent can actually do — not just what it's instructed to do. Five distinct isolation tiers exist in production as of May 2026, each covering a different slice of the attack surface: from Seatbelt and bubblewrap at the OS process level, all the way to dedicated hardware VMs with full kernel separation.

The stakes are concrete. A runaway or prompt-injected agent can delete files, exfiltrate environment variables, make outbound network calls, or escalate privileges — all without triggering a single permissions dialog. The sandbox tier you pick determines which of those threats you are actually defended against, and which you are merely trusting the model not to exploit.

This guide surveys all five tiers in technical depth, maps each tier against a concrete threat matrix, covers what Claude Code 1.3, Vercel Sandbox, E2B, Codex CLI, and Cursor ship by default, and closes with a decision tree so you can match the right isolation layer to your actual workload — without over-engineering or under-protecting.

## 01 — Threat ModelWhat can a runaway agent _actually_ do?

Before choosing a sandbox tier, it helps to enumerate what you are defending against. The threat model for an AI coding agent running arbitrary bash commands is materially different from the threat model for a web-based code-generation service that executes user-submitted snippets. Both need isolation — but not the same isolation.

The five concrete threats that sandbox tiers cover are: filesystem read and write outside the intended scope, network egress to arbitrary domains, exposure of the host kernel's syscall surface to agent-executed code, cross-tenant data leakage in multi-tenant environments, and secret exfiltration via environment variables or the `/proc` filesystem. A key insight from Anthropic's own security documentation is that isolation does not protect against all of these — data leakage through network egress remains a live risk in any sandbox that permits outbound connections, code modification remains possible in any sandbox with a writable project directory mount, and no sandbox prevents a compromised prompt from reaching the API. The goal of sandboxing is to constrain the blast radius, not to make agents trustworthy.

Filesystem threat

##### Read/write outside scope

An agent with unrestricted filesystem access can read .env files, SSH keys, ~/.ssh/id_rsa, or any secret on the machine. It can also modify source files in parent directories. Claude Code restricts writes to the started folder and below by default — but this is policy, not OS enforcement.

Tier: OS sandbox minimum

Network threat

##### Egress to arbitrary domains

An agent that can make outbound HTTP requests can exfiltrate data, receive instructions from a remote attacker, or call external APIs without authorization. Claude Code blocks curl and wget by default as part of its command blocklist. MicroVMs add network namespace isolation for stronger guarantees.

Tier: microVM for untrusted

Kernel threat

##### Syscall surface exposure

Docker containers share the host kernel — a container escape via a kernel vulnerability exposes the entire host. gVisor interposes a user-space kernel so agent code never touches host kernel syscalls directly. Firecracker microVMs go further with a dedicated kernel per sandbox.

Tier: gVisor or microVM

Multi-tenant threat

##### Cross-tenant data leakage

In multi-tenant platforms (SaaS, code playgrounds), one user's agent workload must not be able to read another user's data. Container-based solutions share a kernel and rely on namespace isolation — adequate for low-risk workloads, insufficient for compliance-sensitive multi-tenancy. MicroVMs are the industry standard for this threat class.

Tier: microVM mandatory

There is one more threat that no sandbox tier addresses: a compromised system prompt. If an attacker can inject instructions into the agent's context window — via a poisoned code comment, a malicious file read, or an adversarial tool response — the agent will execute those instructions with whatever permissions the sandbox allows. Sandboxing shrinks the impact radius of a successful prompt injection; it does not prevent the injection itself. Layered defenses — input validation, tool call allowlists, and output auditing — are required alongside isolation.

## 02 — OS Process SandboxSeatbelt on macOS, bubblewrap on Linux — what _Claude Code 1.3_ ships.

The lightest-weight isolation tier is the OS process sandbox. Apple's Seatbelt (implemented via the`sandbox-exec` subsystem on macOS) and bubblewrap (the `bwrap` user-namespace tool on Linux and WSL2) both work at the process level — they restrict what a spawned subprocess can do without creating a separate OS or kernel boundary.

**What Claude Code 1.3 ships.** The Sandboxed Bash tool, introduced in Claude Code 1.3, uses Seatbelt on macOS and bubblewrap on Linux/WSL2 to isolate bash commands and their child processes. This covers the most common agent action: running shell commands. The scope is intentionally narrow: the Sandboxed Bash tool does not sandbox file tools (Read, Write, Edit), MCP servers, or hooks — those run with the full permissions of the Claude Code process itself.

**The sandbox runtime beta.** Anthropic also ships an opt-in `@anthropic-ai/sandbox-runtime` package that wraps the _entire_ Claude Code process — including file tools, MCP servers, and hooks — in Seatbelt or bubblewrap. This is configured via `~/.srt-settings.json` with filesystem and network allowlists. It is not enabled by default; teams that need whole-process isolation must opt in explicitly. Claude Code on the web uses a different approach: Anthropic-managed VMs with default-deny networking, branch-restricted git push, secure-proxy GitHub tokens, full audit logging, and automatic VM teardown after each session.

**Threat coverage.** OS process sandboxes do well against filesystem scope violations (configurable allowlists for read/write paths) and partial network egress blocking (deny-list specific commands). They do not provide meaningful protection against kernel exploits — both Seatbelt and bubblewrap run in the same kernel as the host process. For in-house agents running on trusted machines with known code, this tier is appropriate. For agents executing user-supplied or AI-generated code from untrusted sources, a stronger tier is required.

Claude Code defaults — two distinct layers

The Sandboxed Bash tool isolates bash commands only. File tools, MCP servers, and hooks run with _full process permissions_ unless you additionally enable the `@anthropic-ai/sandbox-runtime` beta. Always verify which layer is active for your deployment before trusting the sandbox as your primary control.

## 03 — User-Space KernelgVisor's _application kernel_ — the third approach.

gVisor is Google's user-space kernel for container workloads, written in Go and open-sourced under Apache 2.0. It runs as an OCI container runtime called `runsc` and describes itself as a "distinct third approach" to container security — sitting between syscall filtering (seccomp-bpf) and full hardware virtualization.

**How it works.** When agent code inside a gVisor container makes a syscall, `runsc` intercepts it before it reaches the host kernel and handles it inside a Go-implemented Linux-compatible kernel called the Sentry. The Sentry re-implements a Linux-like syscall interface, so most container workloads run unmodified. Critically, the Sentry itself has a very limited footprint of syscalls it makes to the host kernel — the attack surface exposed to host-kernel vulnerabilities is dramatically smaller than a standard Docker container.

**Build support.** gVisor builds on x86_64 and ARM64. It provides, in Google's own framing, "security benefits of VMs while maintaining the lower resource footprint, fast startup, and flexibility of regular userspace applications." The GitHub repository has 18.4k stars as of May 2026.

**Where gVisor fits.** gVisor is well-suited to multi-tenant container platforms where kernel-escape risk is real but microVM overhead is unacceptable. It is reportedly used inside Google Cloud Run sandboxes for workloads that need stronger isolation than standard containers. For AI agent execution, gVisor is a reasonable choice when you need meaningful kernel-surface reduction but cannot absorb the provisioning latency of a full microVM. Its primary limitation relative to microVMs: it still operates within the host kernel's VM layer, so a hypervisor-level escape remains theoretically possible — a gap that Firecracker closes with KVM-level separation.

## 04 — Firecracker microVMsVercel Sandbox GA, E2B, and the _microVM_ standard.

Firecracker is an open-source virtual machine monitor built by AWS in Rust, backed by Linux KVM, and open-sourced in November 2018 at re:Invent to power AWS Lambda and AWS Fargate. It is now at v1.15.1 (released April 7, 2026) with 34.5k GitHub stars. The project describes its primary security model as "secure, multi-tenant, minimal-overhead execution of container and function workloads."

The minimalist design is intentional: Firecracker excludes unnecessary virtual devices — no USB, no GPU pass-through, no PCI hot-plug — to reduce both memory footprint and attack surface. Each microVM gets a dedicated Linux kernel. This is the key distinction from Docker: a Docker container shares the host kernel; a Firecracker microVM does not. A kernel exploit inside a Firecracker sandbox cannot reach the host kernel by construction.

**Vercel Sandbox (GA January 2026).** [Vercel's Sandbox](https://vercel.com/docs/vercel-sandbox) is described as "a compute primitive designed to safely run untrusted or user-generated code on Vercel" supporting "dynamic, real-time workloads for AI agents, code generation, and developer experimentation." Each sandbox runs in its own Firecracker microVM on Amazon Linux 2023 with Node.js (node26, node24, node22) and Python 3.13 runtimes pre-installed. Default timeout is 5 minutes; persistent sandboxes auto-snapshot on stop. Provisioning runs in the `iad1` region and is covered by Vercel's SOC 2 Type II.

**E2B.** [E2B](https://github.com/e2b-dev/E2B) is an open-source infrastructure platform (Apache 2.0) that describes itself as infrastructure for running AI-generated code in "secure isolated sandboxes in the cloud." E2B maintains its own fork of Firecracker for its sandbox infrastructure. The SDK has 12.3k GitHub stars; the latest CLI release is `@e2b/cli@2.10.2` (May 22, 2026). E2B's org on GitHub maintains 56 repositories including a `code-interpreter` (2.3k stars), `fragments` (6.3k stars), and a `desktop` (1.4k stars) sandbox for GUI agent workloads.

Vercel Sandbox docs — on Docker isolation

"Unlike Docker containers, each sandbox runs in its own 

[Firecracker](https://firecracker-microvm.github.io/)

microVM with a dedicated kernel. This provides stronger isolation than container-based solutions, which makes sandboxes ideal for running untrusted code." — 

[Vercel — Understanding Sandboxes](https://vercel.com/docs/vercel-sandbox/concepts)

, February 17, 2026.

The broader ecosystem around Firecracker is growing. Fly.io, Modal, and Docker Desktop's sandbox feature also use microVM-grade isolation with Firecracker or Firecracker-compatible VMMs. Anthropic recommends VM-grade isolation in its own documentation when "evaluating untrusted code repositories" or when "kernel-level separation is required by security policy." For engineering teams building AI coding services where users submit prompts that generate code, microVM is increasingly the baseline expectation — not a premium option.

One pattern worth noting: the [Alibaba OpenSandbox project](/blog/alibaba-opensandbox-open-source-ai-agent-execution) brings a similar microVM-backed sandbox approach to self-hosted environments, which is relevant for teams that cannot route workloads through Vercel or AWS. As agentic systems proliferate, the question is shifting from "should we sandbox?" to "which microVM provider fits our latency and cost profile?"

> The sandbox tier you pick determines which threats you are actually defended against — and which you are merely trusting the model not to exploit.Digital Applied synthesis, May 17, 2026

## 05 — Dev ContainersCodespaces, _devcontainer.json_ , and their limits.

Dev containers (the `devcontainer.json` specification, used by GitHub Codespaces, VS Code Remote Containers, and Cursor) provide a reproducible, containerized development environment. From a sandboxing perspective, they are Docker containers with a structured configuration layer on top.

**What they give you.** Dev containers enforce a well-defined filesystem layout, pre-installed tooling, and a consistent OS image. For agent workloads, they provide reasonable filesystem isolation (the container root cannot see the host filesystem unless volumes are mounted), predictable dependency environments, and easy reset semantics (destroy and recreate the container to undo agent-caused changes).

**What they do not give you.** Dev containers share the host kernel — exactly the same limitation as standard Docker. A container escape via a kernel vulnerability exposes the host. Dev containers also tend to be long-lived rather than ephemeral: the same container is reused across sessions, which means agent-caused state accumulates rather than being wiped. For multi-tenant use cases or agent workloads that execute arbitrary user-supplied code, dev containers are not an appropriate isolation layer on their own.

**When dev containers are the right call.** For single-developer or small-team workflows where the agent is executing code written by a known team — not arbitrary user input — dev containers provide a strong repeatability story at low operational overhead. The [Claude Code 1.3 deep dive](/blog/claude-code-1-3-deep-dive-features-shortcuts-config-2026) covers how to configure Claude Code inside a dev container with explicit filesystem and network allowlists for a tighter security posture. Combine a dev container with custom seccomp profiles and iptables rules for additional hardening when you cannot move to microVMs.

## 06 — Full VMsHardware virtualization — the _compliance_ tier.

Full virtual machines — KVM-backed VMs on bare metal, AWS EC2 instances, or Google Cloud Compute Engine VMs — represent the strongest widely-deployed isolation primitive. Each VM has a dedicated kernel, dedicated virtual hardware, and hardware-enforced memory isolation at the hypervisor boundary. A bug in one VM cannot read memory from another VM running on the same host.

**Why this matters for compliance-driven teams.** For regulated industries — financial services, healthcare, government — compliance frameworks often mandate audit logging, immutable infrastructure, and demonstrable compute isolation. Full VMs satisfy those requirements in ways that containers and even microVMs sometimes do not, primarily because the VM abstraction has a longer audit history and is better understood by compliance teams and auditors.

**The operational trade-off.** Full VMs take seconds to minutes to provision, whereas Firecracker microVMs boot in under a second and gVisor containers start in milliseconds. For AI agent workloads where a new isolated environment must be created per request or per session, full VMs are often too slow and too expensive. The emerging pattern is to use full VMs as the outer boundary (the host the microVM hypervisor runs on) and microVMs as the per-request execution unit inside — which is exactly the architecture Vercel, AWS Lambda, and E2B use.

Our [AI transformation engagements](/services/ai-transformation) regularly help teams navigate the compliance-vs-latency trade-off: the answer is almost always microVMs with full-VM outer boundaries and structured audit logging, rather than legacy full-VM-per-request architectures.

Process sandbox

##### Startup overhead

~0ms

Seatbelt and bubblewrap wrap existing processes — no VM boot required. Negligible overhead for interactive agent workflows. Does not provide kernel isolation.

Claude Code default

Firecracker microVM

##### Boot time (reported)

<1s

Firecracker microVMs boot in sub-second time according to AWS design documentation. Dedicated kernel per sandbox. Used by Vercel Sandbox, E2B, AWS Lambda, and Fargate.

Vercel Sandbox · E2B

Full VM

##### Typical provision time

30s+

Hardware VMs take 30 seconds to several minutes to provision. Maximum isolation — dedicated kernel, hardware memory boundaries, strong compliance story. Too slow for per-request agent sandboxing.

Compliance tier

## 07 — Codex CLI Sandbox ModesThree modes — read-only to _danger-full-access_.

Codex CLI ([github.com/openai/codex](https://github.com/openai/codex)) ships three sandbox modes that map directly onto the threat tiers described above. Older auto-everything flags from earlier Codex CLI releases have been retired; current versions use the `--sandbox` flag with one of three named modes. OpenAI recommends `workspace-write` for most development workflows. For a deeper treatment of Codex CLI configuration, see our [Codex CLI sandbox deep dive](/blog/codex-cli-deep-dive-config-profiles-sandbox-2026).

Restricted

#####  _read-only_ mode

\--sandbox read-only

Agent can read files and run commands that produce output but cannot write to the filesystem or make network calls. Use for code review, audit, and analysis tasks where no changes should be made. Highest security posture — minimal blast radius.

Audit / review tasks

Recommended

#####  _workspace-write_ mode

\--sandbox workspace-write

Agent can read and write within the project workspace directory but is restricted from modifying system files or making arbitrary network calls. This is the OpenAI-recommended default for active development. Balances productivity against containment.

OpenAI recommended default

Unrestricted

#####  _danger-full-access_ mode

\--sandbox danger-full-access

Agent has full filesystem and network access — no restrictions. Appropriate only inside an already-isolated environment (a dedicated VM or microVM) where the OS-level damage is contained. Never use on a developer machine without an outer isolation boundary.

Use inside microVM only

The three-mode design reflects a deliberate philosophy: Codex CLI itself does not attempt to provide the isolation layer — it delegates that to the environment it runs inside. In`danger-full-access` mode, the expectation is that the caller has already wrapped Codex in a Firecracker microVM or equivalent. This is a sensible separation of concerns: the tool focuses on agent capability; the platform focuses on isolation.

## 08 — Cursor Cloud AgentsIsolated worktrees and _parallel VM_ execution.

Cursor's cloud agents, introduced in Cursor 3.0, run in isolated VMs rather than local process sandboxes. Two primitives are central to the architecture: `/worktree`, which creates a one-off isolated worktree for a single agent task, and `/best-of-n`, which runs multiple agent attempts in parallel across separate isolated worktrees and returns the best result.

The `/worktree` primitive is particularly relevant for sandboxing: each invocation gets its own isolated environment, changes are contained to that environment, and the worktree can be discarded or merged independently. This provides both isolation (a runaway agent in one worktree cannot affect the main branch or other worktrees) and auditability (the diff from the worktree is the complete record of what the agent changed).

For teams already using Cursor for development, the cloud agent architecture provides a meaningful isolation upgrade over running agents locally without process sandboxing. The [Cursor cloud agents guide](/blog/cursor-cloud-agents-isolated-vms-guide) covers the full architecture including how VM isolation interacts with Cursor's multi-model routing.

**What this means in practice.** Cursor's approach trades some of the raw capability of a fully unrestricted local agent for meaningful isolation guarantees. For production agent workflows running on user-provided repositories or AI-generated code, the isolated VM per worktree model is substantially safer than local process-level sandboxing — and the `/best-of-n` pattern adds a layer of redundancy that pure sandboxing does not. Our [AI coding agents comparison](/blog/ai-coding-agents-claude-code-cursor-codex-replit-2026) covers Cursor against Claude Code and Codex in more depth.

## 09 — Decision TreeWhich sandbox tier for _which_ workload?

Choosing a sandbox tier requires matching the threat model to the operational constraints. The matrix below is a synthesis of vendor documentation from Vercel, Anthropic, Google, and AWS — not a marketing claim. Cells reflect coverage as documented by the respective projects; independently verified gaps are noted.

#### Isolation strength by tier — composite across 5 threat vectors

Digital Applied synthesis — vendor docs: Vercel, Anthropic, AWS, Google, May 2026

Firecracker microVMVercel Sandbox · E2B · AWS Lambda/Fargate

Strongest

gVisor (runsc)Google — user-space kernel interposition

Strong

Full VM (KVM/EC2)Compliance tier — slow provision

Maximum

Dev container (Docker + seccomp)Codespaces · devcontainer.json

Moderate

OS process sandboxSeatbelt (macOS) · bubblewrap (Linux)

Baseline

The bars above rank overall isolation strength as a composite across the five threat vectors. Full VM scores highest in raw isolation but lowest in provision speed — which is why it ranks below Firecracker for AI agent workloads in practice. The "correct" tier depends on the workload profile:

  * **Trusted in-house agent, known codebase:** OS process sandbox (Claude Code default) is appropriate. The agent is running code written by your team, on your machine, with known permissions. Process-level containment provides meaningful protection against accidental filesystem or network damage without operational overhead.
  * **Multi-user platform or agent executing AI-generated code:** Firecracker microVM is the 2026 baseline. Vercel Sandbox and E2B both provide production-ready managed microVM infrastructure with sub-second provisioning. This tier eliminates the kernel-sharing risk that makes Docker insufficient for untrusted workloads.
  * **Compliance-driven, regulated sector:** Full VM outer boundary with microVM inner execution and structured audit logging. The VM provides the compliance story; the microVM provides the per-request isolation speed.
  * **High-performance multi-tenant with kernel-escape risk:** gVisor is the pragmatic middle ground — stronger than containers, faster than microVMs, well-understood operationally from Google's production use.



For teams building AI-powered web applications or developer tools, the [web development practice](/services/web-development) at Digital Applied integrates sandbox architecture from the initial system design rather than retrofitting it later — a distinction that matters significantly for multi-tenant SaaS where kernel-sharing risks are most acute.

Conclusion

### Match the sandbox tier to the threat model — microVM is the 2026 baseline for untrusted code.

The five isolation tiers covered in this guide are not a progression from bad to good — they are tools for different jobs. For trusted in-house agents running on known codebases, the process-level sandbox that Claude Code 1.3 ships by default is appropriate and operationally free. The Sandboxed Bash tool provides meaningful protection against accidental filesystem and network damage; the sandbox runtime beta extends that coverage to the entire process for teams that need it.

For any agent acting on user-supplied prompts, executing AI-generated code, or running in a multi-tenant context, the minimum acceptable tier in 2026 is a Firecracker microVM. Vercel Sandbox's GA in January 2026 made managed microVM infrastructure production-ready for teams without the operational budget to run their own Firecracker fleet. E2B provides the open-source alternative for self-hosted deployments. Both are meaningfully stronger than Docker — Vercel's own documentation says so explicitly.

The broader trend is clear: as agentic systems move from experimental to production, sandbox architecture is becoming a first-class engineering concern — not an afterthought. The teams building the next generation of AI coding tools and developer platforms are treating isolation tier selection as a design decision, not an operational detail. Pick the tier that matches your actual threat model, verify the coverage gaps for that tier, and layer complementary controls — prompt validation, tool allowlists, output auditing — on top. Isolation shrinks the blast radius; defense in depth is what actually closes the loop.