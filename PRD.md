# thegent — Product Requirements Document

**Status:** Active | **Version:** 2.0 | **Updated:** 2026-03-25
**Cross-ref:** [PLAN.md](./PLAN.md) | [ADR.md](./ADR.md) | [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md)

---

## Product Vision

`thegent` is the single tool a developer installs on any machine — macOS, Linux, or Windows/WSL — to
reproduce their complete working environment: shell config, dotfiles, runtimes, AI harnesses, MCP
servers, project scaffolding, agent governance, and multi-provider routing. Beyond environment
bootstrap, `thegent` is the runtime orchestration layer for AI agent swarms: it runs, monitors,
routes, and governs agents across Claude Code, Cursor, Codex, and custom harnesses. The mental model
is Nix-style declarative system management fused with an agent platform.

---

## Target Users

| Persona | Primary Need |
|---------|-------------|
| **Solo Developer** | Reproduce full dev env on a new machine in one command |
| **AI-First Engineer** | Run and govern multi-agent swarms; route tasks across providers cheaply |
| **Platform / DevOps** | Manage agent policies, cost caps, and security across org repos |
| **Researcher / Power User** | Run deep research protocols; access any LLM via a single proxy |

---

## Epics

### E1 — Declarative System Bootstrap

Bootstrap a complete developer environment on any OS from a single manifest. Covers shells, runtimes,
dotfiles, tools, services, and AI harnesses. Inspired by Nix Home Manager but accessible to
non-Nix users.

**E1.S1** — As a developer setting up a new machine, I can run `thegent install -t all --scope both`
once to install every tool, runtime, shell plugin, and dotfile defined in my system manifest, so I
reach a productive state within minutes without manual steps.
*Acceptance:* All targets in `system-manifest.json` are installed; `thegent doctor` reports 0 errors.

**E1.S2** — As a developer, I can define my environment declaratively in `system-manifest.json`
covering harnesses (Claude Code, Cursor, Codex), shells (zsh, bash, fish, PowerShell), tools
(git, mise, starship, atuin, …), runtimes (Python, Node, Go, Rust, Ruby), dotfiles, apps, and
services, so the manifest is the single source of truth for my system state.
*Acceptance:* Schema validates against `$schema: https://schema.thegent.dev/system-manifest/v1`.

**E1.S3** — As a developer, I can run `thegent doctor` to get a structured health report listing
missing tools, misconfigured paths, and version mismatches, with an actionable remediation command
for each finding.
*Acceptance:* Doctor exit code 0 on clean system; non-zero with itemised failures on degraded system.

**E1.S4** — As a Windows/WSL user, I can run the PowerShell bootstrap (`install.ps1`) and reach
the same environment state as a macOS or Linux user, so cross-OS parity is maintained.
*Acceptance:* `thegent doctor` green on WSL2 Ubuntu with same manifest as macOS host.

**E1.S5** — As a developer, I can run `thegent install --dry-run` to preview every action the
installer would take, without modifying the system.
*Acceptance:* Dry-run output matches actual install log; no filesystem mutations occur.

---

### E2 — Shell & Dotfile Management

Manage shell configuration, dotfiles, and per-project environment with version-controlled fidelity.

**E2.S1** — As a developer, I can version-control my dotfiles in a `thegent`-managed repository and
have them symlinked or copied to canonical locations on any machine, so my shell feels identical
everywhere.
*Acceptance:* `~/.zshrc`, `~/.gitconfig`, `~/.ssh/config` (non-secret) are managed; conflict
detection prevents overwrites of untracked files.

**E2.S2** — As a developer, I can use `thegent shell sync` to push updated shell config (zshrc,
aliases, functions, starship prompt, atuin history) to all machines registered in my manifest.
*Acceptance:* Sync completes without data loss; rollback restores previous state.

**E2.S3** — As a developer, I can use `direnv`-style per-project environment injection managed by
`thegent`, so project-specific `PATH`, API keys, and tool versions activate automatically on `cd`.
*Acceptance:* `.envrc` is generated and activated; `thegent env status` shows active overrides.

**E2.S4** — As a developer, I can manage secrets (API keys, SSH keys, GPG keys) with a pluggable
secrets backend (1Password, Bitwarden, SOPS/age, `pass`), so credentials are never stored in
plaintext dotfiles.
*Acceptance:* Secrets resolved at runtime; plaintext patterns blocked by pre-commit hook.

---

### E3 — Project Scaffolding & Brownfield Onboarding

Scaffold new projects or onboard existing ones to full governance, quality gates, and documentation
standards in a single command.

**E3.S1** — As a developer starting a new project, I can run `thegent scaffold greenfield
./new-project --profile cli_tool` to generate a complete project with Taskfile, linters, test
infrastructure, VitePress docsite, pre-commit hooks, and spec docs for my chosen language stack.
*Acceptance:* `task quality` passes on generated project with 0 errors.

**E3.S2** — As a developer with an existing project, I can run `thegent scaffold brownfield
./existing-project` to analyse the codebase and add missing governance artifacts (CLAUDE.md,
AGENTS.md, FR_TRACKER.md, quality gate scripts) without touching existing source files.
*Acceptance:* Idempotent — re-running on already-scaffolded project adds nothing, changes nothing.

**E3.S3** — As a developer, I can use `thegent scaffold ag-dd ./project` to generate agent-driven
development scaffolding (AgilePlus spec templates, XDD methodology docs, CODE_ENTITY_MAP.md) for
an existing project.
*Acceptance:* Generated docs reference existing source files; no stubs left unfilled.

**E3.S4** — As a developer, I can scaffold projects in 11+ language stacks (Python, TypeScript, Go,
Rust, Ruby, Java, Kotlin, Swift, Zig, Elixir, C/C++) with language-appropriate linting, test
runner, and CI workflow templates pulled from `templates/`.
*Acceptance:* Each profile builds and tests cleanly with language toolchain available on PATH.

---

### E4 — AI Harness & MCP Management

Install, configure, sync, and manage AI coding harnesses (Claude Code, Cursor, Codex, Helios,
custom) and their Model Context Protocol (MCP) servers from a single config surface.

**E4.S1** — As a developer, I can define all MCP servers I use in `thegent` config and have them
provisioned in the correct config file for each harness (Claude Desktop `mcp_servers.json`, Codex
`~/.codex/mcp.json`, etc.) automatically.
*Acceptance:* `thegent mcp sync` writes correct per-harness config; no manual JSON editing needed.

**E4.S2** — As a developer, I can run `thegent mcp up` to start all configured MCP servers as
managed daemon processes, and `thegent mcp status` to inspect health/uptime, without touching the
harness.
*Acceptance:* Daemons survive harness restart; `thegent mcp status` shows PID, port, uptime.

**E4.S3** — As a developer, I can use `thegent rules sync` to propagate a single set of
agent-governance rules (`CLAUDE.md`, `AGENTS.md`, Cursor rules, Codex system prompt) across all
installed harnesses, so policy is consistent everywhere.
*Acceptance:* Rules appear in correct locations for each harness; checksums verified post-sync.

**E4.S4** — As a developer, I can install, update, and remove skills (slash-command scripts) for
Claude Code and Cursor with `thegent skills install <skill>`, pulling from the skill registry or
a local `skills/` directory.
*Acceptance:* Skill available in harness within 5 seconds of install; no harness restart needed.

**E4.S5** — As a developer, I can install hooks for Claude Code (`~/.claude/hooks/`) through
`thegent hooks install`, with hooks organised by event type and validated for correct schema.
*Acceptance:* Hook fires on correct event; `thegent hooks validate` exits 0.

---

### E5 — Multi-Provider LLM Routing

Route agent tasks across Claude, Gemini, OpenAI, Cursor, and local models via a unified proxy with
cost optimisation, latency targets, and automatic failover.

**E5.S1** — As a developer, I can configure provider weights and routing rules in `thegent` config
so that cheap/fast tasks go to small models and complex/critical tasks go to frontier models
automatically.
*Acceptance:* Routing decisions logged with provider, model, cost-estimate, and latency.

**E5.S2** — As a developer, I can run `thegent cliproxy` to start the CLIProxy API+ daemon that
presents a unified OpenAI-compatible endpoint, allowing any tool that speaks OpenAI API to use
any configured provider.
*Acceptance:* Cursor, Claude, and a raw `curl` all resolve through the same proxy endpoint.

**E5.S3** — As a developer, I can set cost caps per-provider and per-session so that runaway agent
swarms cannot exhaust API budgets beyond configured thresholds.
*Acceptance:* Requests above cap return `429`-equivalent; alert logged; cap configurable at runtime.

**E5.S4** — As a developer, I can use `thegent routing status` to see the current provider health,
latency P50/P95, and cost-per-token for each configured provider, so I can make informed
routing adjustments.
*Acceptance:* Status output refreshes in real time (≤2s); includes provider availability booleans.

---

### E6 — Agent Orchestration & Swarm Management

Run, monitor, pause, and coordinate AI agent processes — from single background tasks to 50-agent
swarms — with lifecycle management and shared state.

**E6.S1** — As a developer, I can run `thegent run agent "Task description" --loop` to launch a
background agent that continuously executes the task, logging all actions, until explicitly stopped
with `thegent agent stop <id>`.
*Acceptance:* Agent survives terminal disconnect; logs persisted to `.thegent/logs/`; stop is clean.

**E6.S2** — As a developer, I can run `thegent swarm launch --agents 20 --task "Audit all repos"`
to launch a coordinated swarm that distributes work across agent instances, with shared memory and
voting protocol for conflict resolution.
*Acceptance:* Swarm PID file written; `thegent swarm status` shows per-agent state; result
aggregated on completion.

**E6.S3** — As a developer, I can use the `thegent queue` subsystem to enqueue prompts for later
execution (`$defer` syntax), inspect the queue TUI, and drain items to an agent automatically.
*Acceptance:* Queue persists across restarts in `.thegent/prompt_queue.jsonl`; TUI shows item
status, priority, and assignment.

**E6.S4** — As a developer, I can define agent teams (planner + implementer + reviewer) in
`agents.toml` and launch them as coordinated teammates with `thegent team start`, so complex tasks
are decomposed and executed in parallel without manual coordination.
*Acceptance:* Team-level logs show task decomposition; final artefacts match spec.

**E6.S5** — As a developer, I can use `thegent sitback` mode to run a long-horizon background task
that monitors a project, applies automated fixes, and surfaces decisions that need human input,
without continuous attention.
*Acceptance:* Sitback loop runs for ≥8 hours without crash; decisions queued for review in TUI.

---

### E7 — Governance & Policy Enforcement

Define and enforce agent behaviour policies — cost caps, file access rules, output validation,
audit trails — across all agents and harnesses centrally.

**E7.S1** — As a platform engineer, I can define a `CONSTITUTION.yaml` that specifies which
files/directories agents may read or write, which shell commands are permitted, cost thresholds,
and approval requirements, and have `thegent` enforce this policy across all running agents.
*Acceptance:* Policy violations logged and blocked; override requires explicit `--override-policy`
flag with reason.

**E7.S2** — As a developer, I can use `thegent audit` to generate a structured audit trail of all
agent actions (file writes, shell commands, API calls) in a session, with timestamps, agent IDs,
and outcomes.
*Acceptance:* Audit log is append-only JSONL; `thegent audit report` renders human-readable summary.

**E7.S3** — As a developer, I can define quality-gate contracts in `contracts/` that specify
required checks (lint, test, coverage, security) and have `thegent` refuse to deliver agent output
that fails any gate.
*Acceptance:* Failed gate halts agent output delivery; reasons listed in structured output.

**E7.S4** — As a developer, I can use `thegent governance check` to verify that all repos in a
project collection have required governance files (CLAUDE.md, AGENTS.md, SECURITY.md, ADR.md) and
compliant branch protection rules.
*Acceptance:* Missing files and non-compliant rules listed by repo; `--fix` flag applies remediations.

---

### E8 — Memory & Context Synthesis

Maintain persistent, cross-session, cross-project memory for agents so knowledge is never
re-discovered, documentation stays current, and context windows stay lean.

**E8.S1** — As a developer, I can use `thegent memory garden` to trigger the Gardener agent, which
reads recent session logs and synthesises updates to `CLAUDE.md`, `ADR.md`, `PRD.md`, and tracker
files so documentation reflects actual code state.
*Acceptance:* Gardener diffs are reviewable before commit; no destructive overwrites.

**E8.S2** — As a developer, I can query the shared memory store (`thegent memory search "topic"`)
to retrieve decisions, code patterns, and prior research relevant to my current task, across all
projects and sessions.
*Acceptance:* Search returns top-5 results with source, timestamp, and confidence score in ≤200ms.

**E8.S3** — As a developer, I can configure a cloud memory backend (Supermemory.ai or self-hosted
graph store) so memory persists across machines and is available to any agent in any session.
*Acceptance:* Memory survives machine wipe; latency ≤100ms on read for cloud backend.

**E8.S4** — As a developer, I can use `thegent memory snapshot` to create a portable `.thgmem`
bundle of all project memory, suitable for sharing with collaborators or archiving.
*Acceptance:* Bundle restores cleanly to a fresh install; checksums verified.

---

### E9 — Deep Research Protocol

Run structured, multi-source research investigations (web, GitHub, Reddit, documentation) and
persist results as reusable knowledge artefacts.

**E9.S1** — As a developer, I can run `thegent research "<question>"` to launch a multi-source
investigation that queries web search, GitHub, package registries, and local codebase, then
produces a structured Markdown report in `docs/research/`.
*Acceptance:* Report includes sources, confidence ratings, and recommended actions; no hallucinated
URLs.

**E9.S2** — As a developer, I can run `thegent research library "<lib-name>"` to get a
structured audit of a dependency covering: latest stable version, breaking changes, security
advisories, alternatives, and adoption metrics.
*Acceptance:* Report matches live PyPI/npm/crates.io data; generated within 60 seconds.

**E9.S3** — As a developer, I can configure research agents to run on a schedule (e.g., nightly
dependency audit) and surface findings in the TUI dashboard.
*Acceptance:* Scheduled run completes without user interaction; findings available in `thegent tui`.

---

### E10 — TUI Dashboard & Observability

Provide a rich terminal UI for monitoring agents, queues, costs, and system health in real time.

**E10.S1** — As a developer, I can run `thegent tui` to open a full-screen terminal dashboard
showing: running agents (with task, cost, duration), queue depth, provider health, recent errors,
and system resource usage.
*Acceptance:* Dashboard refreshes ≤1s; all data sourced from live process state, not stubs.

**E10.S2** — As a developer, I can view an OpenTelemetry trace for any agent run in the TUI,
showing span tree, tool call latencies, and error annotations.
*Acceptance:* Traces available within 5s of agent completion; exportable to OTLP collector.

**E10.S3** — As a developer, I can see per-session and cumulative cost breakdowns by provider,
model, and project in the TUI, so spend is visible and actionable.
*Acceptance:* Cost data accurate to within 1% of provider-reported usage.

**E10.S4** — As a developer, I can configure alert thresholds (cost, error rate, queue depth) and
receive inline TUI alerts plus optional desktop notifications when thresholds are breached.
*Acceptance:* Alert fires within 10s of threshold breach; snooze and dismiss work correctly.

---

### E11 — SDK & Extension API

Expose a stable Python and TypeScript SDK so developers and third-party tools can integrate with
`thegent` routing, memory, governance, and agent lifecycle.

**E11.S1** — As a developer, I can `import thegent` in Python or `from "@thegent/sdk"` in
TypeScript to use the routing, memory, and governance APIs in my own scripts and services.
*Acceptance:* SDK published to PyPI and npm; typed; 100% of public API covered by tests.

**E11.S2** — As an extension author, I can register a custom MCP tool server with `thegent` via
the plugin API and have it appear in all configured harnesses automatically after `thegent mcp sync`.
*Acceptance:* Third-party server registers without modifying `thegent` source; unregister is clean.

**E11.S3** — As an integrator, I can call `thegent` as an HTTP service (the MCP server endpoint)
from external tools, so the routing and governance layer is accessible beyond the CLI.
*Acceptance:* MCP endpoint responds to standard MCP JSON-RPC; auth via configured API key.

---

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-01 | Performance | Rust-backed tool detection and PATH resolution: P99 ≤ 1ms |
| NFR-02 | Performance | MCP server startup: ≤ 500ms cold start |
| NFR-03 | Performance | Queue enqueue/dequeue operations: ≤ 10ms |
| NFR-04 | Performance | Routing resolution (provider selection): ≤ 100ms |
| NFR-05 | Reliability | Bootstrap script idempotent: safe to re-run N times with same output |
| NFR-06 | Reliability | Agent daemons restart automatically on crash (max 3 retries with backoff) |
| NFR-07 | Reliability | Config schema validated on load; bad config produces structured error, never silent failure |
| NFR-08 | Security | Secrets never written to disk in plaintext; secrets backend required for credentials |
| NFR-09 | Security | All agent shell commands pass through policy gate before execution |
| NFR-10 | Security | Audit log is append-only; tampering detectable via checksum chain |
| NFR-11 | Portability | Full feature parity on macOS 13+, Ubuntu 22.04+, Debian 11+, WSL2 (Windows 11) |
| NFR-12 | Portability | Minimum dependencies for bootstrap: `curl` or `irm` only; all else self-installed |
| NFR-13 | Observability | All agent actions emit OpenTelemetry spans; exportable to any OTLP collector |
| NFR-14 | Maintainability | Cyclomatic complexity ≤ 10 per function; cognitive complexity ≤ 15 |
| NFR-15 | Maintainability | Test coverage ≥ 80%; FR traceability ≥ 80% at Level 4 maturity |
| NFR-16 | Scalability | Swarm mode supports ≥ 50 concurrent agents without degradation |

---

## Out of Scope

- **GUI application**: `thegent` is a CLI and TUI tool. A native desktop GUI is not planned.
- **Cloud hosting / SaaS**: `thegent` runs locally. Cloud memory backends are optional third-party
  integrations, not hosted by the Phenotype org.
- **Container image management**: Docker/Podman tool installation is in scope; image build and
  registry management is not.
- **CI/CD pipeline authoring**: `thegent scaffold` generates workflow YAML templates; it does not
  run or manage CI infrastructure.
- **Code review**: Agent-assisted code review (e.g., CodeRabbit) is an MCP integration target,
  not a built-in feature.
- **Human-in-the-loop workflow tools**: Jira, Linear, Notion integrations are research targets
  only; primary workflow is AgilePlus-driven.
- **Mobile app**: A mobile companion app (`thegent mobile`) is tracked in a separate PRD
  (`THEGENT_MOBILE_AUTOMATION_PRD.md`).
- **Windows (non-WSL) native support**: PowerShell bootstrap is provided; Win32 native toolchain
  management is out of scope for v2.

---

*Epics: E1–E11 | Stories: 43 total | Cross-ref: [PLAN.md](./PLAN.md) | [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md)*
