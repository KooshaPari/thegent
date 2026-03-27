# Functional Requirements — thegent

**Version:** 2.0 | **Status:** Active | **Updated:** 2026-03-27
**Traces to:** PRD.md v2.0 (Harmonious Agent Experience — HAX)
**Source:** Derived from `src/thegent/` Python package and `crates/` Rust workspace

---

## Category Index

| Code | Domain | Source Path |
|------|--------|------------|
| BOOT | System bootstrap and environment setup | `src/thegent/install/` |
| DOT | Dotfiles and governance template management | `src/thegent/` templates/ |
| ORCH | Agent orchestration and dispatch | `src/thegent/orchestration/` |
| AGENT | Agent harness and capability index | `src/thegent/agents/` |
| MCP | Model Context Protocol server and tools | `src/thegent/mcp/` |
| ROUTE | Multi-provider routing and cost management | `src/thegent/provider/` |
| SESS | Session management and lifecycle | `src/thegent/session/` |
| GOVERN | Policy engine, cost caps, HITL gates | `src/thegent/governance/` |
| AUDIT | Audit trail and MAIF format | `src/thegent/audit/`, `src/thegent/maif/` |
| CACHE | Response and embedding cache | `crates/thegent-cache/` |
| RUST | Rust-backed performance-critical paths | `crates/thegent-path-resolve/`, `crates/thegent-discovery/` |

---

## FR-BOOT: System Bootstrap

### FR-BOOT-001
**SHALL** expose `thegent install -t <target> --scope <scope>` where `target` is one of `all`, `tools`, `shell`, `runtimes`, `ai`, `mcp`, and `scope` is one of `user`, `system`, `both`.
**Traces to:** E1.S1
**Code:** `src/thegent/install/install_manager.py`, `src/thegent/install.py`

### FR-BOOT-002
**SHALL** read a declarative system manifest (YAML/TOML at a configurable path) listing all tools, runtimes, shell plugins, dotfiles, and MCP servers to install; manifest entries SHALL be idempotent.
**Traces to:** E1.S1
**Code:** `src/thegent/install/install_bundles.py`

### FR-BOOT-003
**SHALL** detect the host OS and architecture and apply platform-specific installation logic for macOS (Homebrew), Linux (apt/dnf/pacman), and Windows/WSL (scoop/winget) without requiring user selection.
**Traces to:** E1.S1
**Code:** `src/thegent/cross_platform/`, `src/thegent/os/`

### FR-BOOT-004
**SHALL** run an interactive setup wizard (`thegent install --wizard`) that prompts for required configuration values (API keys, preferred models, workspace paths) and persists them to the thegent config file.
**Traces to:** E1.S1
**Code:** `src/thegent/install/install_wizard.py`

### FR-BOOT-005
**SHALL** emit structured progress output during install (per-step status: installing / already-installed / failed) and summarize total elapsed time and any failures at the end.
**Traces to:** E1.S1
**Code:** `src/thegent/install/install_system.py`

### FR-BOOT-006
**SHALL** expose `thegent doctor` that audits the current environment for missing dependencies, misconfigured paths, unavailable AI providers, and broken MCP servers, emitting a structured report with remediation hints.
**Traces to:** E1.S2
**Code:** `src/thegent/doctor.py`, `src/thegent/doctor_dependencies.py`, `src/thegent/doctor_setup_checks.py`

---

## FR-DOT: Dotfiles and Governance Templates

### FR-DOT-001
**SHALL** expose `thegent rules sync` that propagates canonical CLAUDE.md / AGENTS.md / hooks to all configured agent environments (Claude Code hooks, Cursor rules, Codex config, thegent global config) atomically.
**Traces to:** E2.S3

### FR-DOT-002
**SHALL** maintain canonical CLAUDE.md and AGENTS.md templates under `templates/governance/` with versioned headers; `thegent templates apply` SHALL copy templates to a target project with merge-aware diff.
**Traces to:** E2.S3
**Code:** `src/thegent/govern/`

### FR-DOT-003
**SHALL** expose `thegent dotfiles push` and `thegent dotfiles pull` to sync shell configs, tool configs, and system preferences to/from a configured backup location (local path or Git remote).
**Traces to:** E2.S4

---

## FR-ORCH: Agent Orchestration

### FR-ORCH-001
**SHALL** define `Plan` and `PlanNode` data classes; a `PlanNode` SHALL have fields: `id`, `task` (str), `capability` (str), `dependencies` (list[str]), `timeout_s` (float), `metadata` (dict).
**Traces to:** E3.S1
**Code:** `src/thegent/agents/plangent.py`

### FR-ORCH-002
**SHALL** define `SubAgentDispatcher` that dispatches a `Plan`'s nodes with `asyncio.gather` under a configurable semaphore (`max_concurrency`, default 7); each node SHALL be wrapped in `asyncio.wait_for` with `default_timeout` (default 120 s).
**Traces to:** E3.S1
**Code:** `src/thegent/orchestration/dispatcher.py`

### FR-ORCH-003
**SHALL** define `DispatchResult` with fields: `node_id`, `output` (str), `success` (bool), `error` (str | None), `runner` (str | None), `elapsed_s` (float), `metadata` (dict).
**Traces to:** E3.S1
**Code:** `src/thegent/orchestration/dispatcher.py`

### FR-ORCH-004
**SHALL** raise `RunnerNotFoundError` (subclass of `LookupError`) when `CapabilityIndex.recommend()` returns no candidate runner for a node's declared capability.
**Traces to:** E3.S1
**Code:** `src/thegent/orchestration/dispatcher.py`

### FR-ORCH-005
**SHALL** support hierarchical dispatch via `HierarchicalDispatcher` that decomposes high-level objectives into sub-plans before dispatching leaf nodes.
**Traces to:** E3.S2
**Code:** `src/thegent/orchestration/hierarchical_dispatcher.py`

### FR-ORCH-006
**SHALL** expose a `budget_tracker` that records accumulated cost per dispatch run and aborts further dispatches when the configured cost cap is exceeded.
**Traces to:** E3.S3, E4.S2
**Code:** `src/thegent/orchestration/budget_tracker.py`

---

## FR-AGENT: Agent Harness and Capability Index

### FR-AGENT-001
**SHALL** define `CapabilityIndex` that maintains a registry of available agent runners keyed by capability name; `recommend(capability: str) -> AgentRecommendation` SHALL return the highest-ranked runner or raise `RunnerNotFoundError`.
**Traces to:** E3.S1
**Code:** `src/thegent/agents/capability_index.py`

### FR-AGENT-002
**SHALL** support the following named agent runners: `claude` (Claude Code), `codex` (OpenAI Codex), `cursor` (Cursor CLI), `aider`, `gemini`, `goose`, `black-box` (generic proxy).
**Traces to:** E3.S1
**Code:** `src/thegent/agents/`, `src/thegent/agents/black_box_proxy.py`

### FR-AGENT-003
**SHALL** expose `thegent run agent "<task>"` that plans, dispatches, and streams the result of a single agent task to stdout with optional `--loop` flag for continuous autonomy.
**Traces to:** E3.S4

### FR-AGENT-004
**SHALL** define `autopoiesis` mode where agents can spawn child agents up to a configured depth limit to complete subtasks; depth SHALL default to 3 and SHALL be configurable.
**Traces to:** E3.S3
**Code:** `src/thegent/agents/autopoiesis.py`

---

## FR-MCP: Model Context Protocol

### FR-MCP-001
**SHALL** expose an MCP server (`src/thegent/mcp/server/`) implementing the MCP protocol; all MCP tools SHALL be registered via a tool registry with capability declarations.
**Traces to:** E3.S5
**Code:** `src/thegent/mcp/`, `src/thegent/mcp_server.py`

### FR-MCP-002
**SHALL** support dynamic tool loading via `DynamicTools` that loads tool definitions from YAML/JSON at runtime without server restart.
**Traces to:** E3.S5
**Code:** `src/thegent/mcp/dynamic_tools.py`

### FR-MCP-003
**SHALL** implement MCP ACL (`src/thegent/mcp/acl.py`) enforcing tool-level access control; tools not in the allowed list SHALL return an MCP error response.
**Traces to:** E4.S1
**Code:** `src/thegent/mcp/acl.py`

### FR-MCP-004
**SHALL** expose `rest_to_mcp` bridge that adapts arbitrary REST endpoints into MCP tools, enabling external APIs to be consumed by agents via the MCP protocol.
**Traces to:** E3.S5
**Code:** `src/thegent/mcp/rest_to_mcp.py`

### FR-MCP-005
**SHALL** support LSP tools integration (`lsp_tools.py`) exposing language-server capabilities (go-to-definition, find-references, diagnostics) as MCP tools.
**Traces to:** E3.S5
**Code:** `src/thegent/mcp/lsp_tools.py`

---

## FR-ROUTE: Multi-Provider Routing

### FR-ROUTE-001
**SHALL** expose a provider routing layer that selects the optimal AI provider (Claude, Gemini, OpenAI, local proxies) for each request based on task classification, cost model, and configured preferences.
**Traces to:** E4.S3
**Code:** `src/thegent/provider/`, `src/thegent/provider_model_manager.py`

### FR-ROUTE-002
**SHALL** implement `ProviderModelManager` that scores candidate models on dimensions: cost-per-token, latency, capability match, and subscription-bucket preference; the highest-scoring model SHALL be selected.
**Traces to:** E4.S3
**Code:** `src/thegent/provider_model_manager_sorting.py`, `src/thegent/provider_model_scoring.py`

### FR-ROUTE-003
**SHALL** route through `cliproxy` (local CLIProxyAPI instance) when configured; `ClipRoxyAdapter` SHALL translate standard LLM requests to the cliproxy wire format.
**Traces to:** E4.S3
**Code:** `src/thegent/cliproxy_adapter.py`, `src/thegent/provider_model_manager_cliproxy.py`

### FR-ROUTE-004
**SHALL** expose `thegent provider list` and `thegent provider add <name> --api-key <key>` CLI commands for managing provider credentials.
**Traces to:** E4.S3
**Code:** `src/thegent/provider_crud.py`, `src/thegent/provider_forms.py`

---

## FR-GOVERN: Policy Engine and Cost Caps

### FR-GOVERN-001
**SHALL** define `PolicyEngine` with `await_approval(node: PlanNode) -> bool` that checks HITL gate conditions; when `DispatchConfig.hitl_enabled=True`, high-risk tasks SHALL require explicit approval before dispatch.
**Traces to:** E4.S1
**Code:** `src/thegent/governance/hitl.py`

### FR-GOVERN-002
**SHALL** enforce per-session and per-day cost caps via the `budget_tracker`; when a cap is exceeded, further requests SHALL fail with a structured `CostCapExceededError` rather than silently degrading.
**Traces to:** E4.S2
**Code:** `src/thegent/orchestration/budget_tracker.py`

### FR-GOVERN-003
**SHALL** apply the role-tool allowlist matrix from `src/thegent/governance/` enforcing which tools each agent role is permitted to call.
**Traces to:** E4.S1
**Code:** `src/thegent/governance/`

---

## FR-AUDIT: Audit Trail

### FR-AUDIT-001
**SHALL** record all agent actions in MAIF (Machine-Actionable Interchange Format) entries stored in `src/thegent/maif/`; each entry SHALL include: agent_id, action_type, input_hash, output_hash, timestamp, cost_tokens.
**Traces to:** E5.S1
**Code:** `src/thegent/maif/`, `src/thegent/audit/`

### FR-AUDIT-002
**SHALL** expose `thegent audit list [--feature <id>] [--agent <name>]` CLI command reading from the MAIF log and rendering a tabular summary.
**Traces to:** E5.S1

### FR-AUDIT-003
**SHALL** persist JSONL-format execution logs via `thegent-jsonl` crate (`crates/thegent-jsonl/`) with append-only semantics.
**Traces to:** E5.S1
**Code:** `crates/thegent-jsonl/`

---

## FR-RUST: Rust Extension Paths

### FR-RUST-001
**SHALL** implement `thegent-path-resolve` Rust crate that resolves tool binaries in PATH in < 1 ms using compiled lookup tables; Python code SHALL call this via FFI wrappers in `src/thegent/rust_wrappers.py`.
**Traces to:** E6.S1
**Code:** `crates/thegent-path-resolve/`, `src/thegent/rust_wrappers.py`

### FR-RUST-002
**SHALL** implement `thegent-discovery` Rust crate that scans project directories for tool manifests (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`) in < 50 ms for directories with up to 10,000 entries.
**Traces to:** E6.S1
**Code:** `crates/thegent-discovery/`

### FR-RUST-003
**SHALL** implement `thegent-crypto` Rust crate providing SHA-256 hashing and BLAKE3 hashing for content-addressable caching; bindings SHALL be exposed to Python via `rust_wrappers`.
**Traces to:** E6.S1
**Code:** `crates/thegent-crypto/`

### FR-RUST-004
**SHALL** implement `thegent-cache` Rust crate providing an LRU cache with configurable capacity and TTL; the cache SHALL be shared across Python threads via thread-safe Rust internals.
**Traces to:** E6.S2
**Code:** `crates/thegent-cache/`
