# Agent Frameworks Dedup / Interop Plan

**Audit date:** 2026-06-14
**Scope:** `C:/Users/koosh/Dev/thegent` vs `C:/Users/koosh/Dev/Agentora`
**Read-only analysis** — no builds, no git operations.

---

## 1. Executive Summary

| Dimension | thegent | Agentora | Overlap |
|-----------|---------|----------|---------|
| **Language** | Python (primary) + Rust (crates) | Rust (primary) | Bilingual vs monolingual |
| **Skill system** | Markdown-based discovery + MCP registry + prompt injection | Trait-based `Skill` + `SkillRegistry` + daemon sidecar | **Conceptual duplicate** — both have skill registries, discovery, and activation |
| **Plugin model** | Wasm/Extism + Rust plugin-host + Python adapter | **None** — skills ARE the plugin boundary | **thegent only** |
| **Runtime layering** | Python execution → Rust dispatch → Wasm sandbox | Rust async (tokio) → daemon sidecar → process pool | **Different paradigms** |
| **Vendored 2nd runtimes** | Extism Wasm runtime, ZMX session manager, runtime-dispatch binary, plugin-host binary | **None** — pure tokio + std | **thegent only** |

**Bottom line:** The two repos share the *concept* of a skill registry and agent execution pipeline, but implement them in different languages with different architectural assumptions. Thegent is a polyglot heavyweight with multiple embedded runtimes; Agentora is a lean Rust-native framework. The dedup strategy should be **extract shared abstractions, bridge at the protocol layer, and eliminate duplication in skill metadata**.

---

## 2. Skill System vs Plugin Model — Detailed Comparison

### 2.1 thegent Skill System

| Component | Location | Lines | Purpose |
|-----------|----------|-------|---------|
| `SkillDiscovery` | `src/thegent/skills/discovery/__init__.py:54` | ~137 | Scans dirs for `SKILL.md`, `skill.json`, `skill.yaml` |
| `SkillManifest` | `src/thegent/skills/discovery/__init__.py:12` | ~20 | Frozen dataclass: name, description, instructions, tags |
| `SkillActivator` | `src/thegent/skills/discovery/__init__.py:26` | ~30 | Injects skill instructions into base prompts |
| `AgentRunner.activate_skill` | `src/thegent/agents/base.py:86` | ~30 | Per-agent skill activation with prompt suffix injection |
| `MCPSkillRegistry` | `src/thegent/mcp/server/tools_skills.py:98` | ~40 | Global dict-based registry for MCP server exposure |
| `factory_skills_dir` | `src/thegent/config/settings.py:449` | — | Configured path `~/.factory/skills` |

**Key design:** Skills are **static markdown documents** discovered from filesystem paths and injected into LLM prompts. There is no executable skill boundary — skills are purely prompt engineering artifacts.

### 2.2 thegent Plugin Model

| Component | Location | Lines | Purpose |
|-----------|----------|-------|---------|
| `PluginInterface` (Protocol) | `src/thegent/adapters/ports.py:93` | ~15 | `name`, `version`, `initialize()`, `shutdown()` |
| `PluginHost` | `src/thegent/adapters/ports.py:230` | ~55 | In-process plugin lifecycle manager |
| `WasmPlugin` (ABC) | `src/thegent/infra/wasm_plugin.py:178` | ~50 | Abstract base for Wasm plugins |
| `ExtismPlugin` | `src/thegent/infra/wasm_plugin.py:229` | ~135 | Extism-based Wasm execution with resource limits |
| `WasmPluginManager` | `src/thegent/infra/wasm_plugin.py:367` | ~210 | Global singleton manager for Wasm plugins |
| `PluginHostAdapter` | `src/thegent/adapters/plugin_host_adapter.py:61` | ~310 | Python ↔ Rust plugin-host bridge via IPC/socket |
| `thegent-plugin-host` crate | `crates/thegent-plugin-host/src/lib.rs:1` | ~29 | Rust plugin host with hexagonal architecture |
| `thegent-wasm-tools` crate | `crates/thegent-wasm-tools/src/lib.rs:1` | ~270 | Zig SDK for building Wasm tools with Extism |

**Key design:** Plugins are **executable Wasm binaries** (compiled from Zig or other languages) loaded into an Extism runtime. The system supports hot-swapping, resource limits (memory, CPU time), and IPC to a Rust plugin host. This is a full **sandboxed execution model**.

### 2.3 Agentora Skill System

| Component | Location | Lines | Purpose |
|-----------|----------|-------|---------|
| `Skill` trait | `src/domain/skills/mod.rs:10` | ~20 | `name()`, `description()`, `execute(params)` → `SkillResult` |
| `SkillRegistry` | `src/domain/skills/mod.rs:50` | ~35 | `HashMap<String, Box<dyn Skill>>` with register/get/list |
| `Tool` trait | `src/domain/tools/mod.rs:54` | ~25 | `name()`, `description()`, `parameters()`, `call()` |
| `ToolRegistry` | `src/domain/tools/mod.rs:77` | ~40 | Same pattern as SkillRegistry |
| `AgentExecutor` | `src/application/mod.rs:12` | ~55 | Orchestrates agent + skills + tools + memory |
| `phenotype-skills` crate | `crates/pheno-agent/phenotype-skills/src/lib.rs:1` | ~387 | Daemon-side skill types: `SkillId`, `SkillManifest`, `DependencyResolver`, `SkillRegistry` (DashMap-backed) |
| `phenotype-daemon` crate | `crates/pheno-agent/phenotype-daemon/src/main.rs:1` | ~161 | Tokio sidecar daemon with msgpack-RPC over Unix/TCP sockets |

**Key design:** Skills are **trait implementations** compiled into the Rust binary. The `phenotype-daemon` provides a **remote skill registry** with dependency resolution, conflict checking, and circular-dependency detection. There is **no Wasm sandbox** — execution is native Rust code.

### 2.4 Overlap Matrix

| Capability | thegent | Agentora | Merge Recommendation |
|------------|---------|----------|---------------------|
| Skill registry | `MCPSkillRegistry` (dict) + `SkillDiscovery` (filesystem) | `SkillRegistry` (HashMap) + `DashMap` daemon | **Extract shared schema** — both use name→skill mapping |
| Skill manifest | `SkillManifest` (markdown-centric) | `SkillManifest` (JSON/serde with dependencies) | **Merge schemas** — Agentora's is richer (deps, env, config_schema) |
| Skill discovery | Filesystem scan (`~/.factory/skills`) | Daemon RPC + embedded | **Keep both** — thegent's filesystem model is user-facing; Agentora's daemon model is performance-oriented |
| Skill activation | Prompt injection (`AgentRunner.activate_skill`) | Trait execution (`AgentExecutor.run`) | **Different layers** — thegent is LLM-prompt; Agentora is code-execution |
| Plugin/Wasm execution | Extism + `thegent-wasm-tools` | **None** | **Keep in thegent only** — no overlap |
| Dependency resolution | **None** | `DependencyResolver` (`phenotype-skills/src/lib.rs:219`) | **Extract to shared** — thegent lacks this; Agentora has it |

---

## 3. Runtime Layering — Detailed Comparison

### 3.1 thegent Runtime Stack

```
┌─────────────────────────────────────────────┐
│  Python Application Layer                    │
│  - CLI (Typer/Rich)                         │
│  - ExecutionOrchestrator                    │  src/thegent/use_cases/execute_task.py:26
│  - PolicyEngine / RunRegistry / Auditor     │  src/thegent/execution/__init__.py:140
│  - ConcurrencyController (lane-based)       │  src/thegent/execution/__init__.py:706
├─────────────────────────────────────────────┤
│  Python Agent Layer                          │
│  - AgentRunner (base class)                │  src/thegent/agents/base.py:35
│  - Skill activation / prompt injection     │  src/thegent/agents/base.py:86
│  - Sub-agent dispatcher                     │  src/thegent/agents/base.py:49
├─────────────────────────────────────────────┤
│  Adapter / Port Layer                        │
│  - PluginHostAdapter (Python ↔ Rust IPC)  │  src/thegent/adapters/plugin_host_adapter.py:61
│  - AdapterRegistry (global decorators)     │  src/thegent/adapters/ports.py:145
├─────────────────────────────────────────────┤
│  Rust Crate Layer (28 crates)              │
│  - thegent-runtime: unified dispatch binary │  crates/thegent-runtime/src/main.rs:1
│  - thegent-plugin-host: Wasm plugin lifecycle│  crates/thegent-plugin-host/src/lib.rs:1
│  - thegent-wasm-tools: Zig SDK for Extism   │  crates/thegent-wasm-tools/src/lib.rs:1
│  - thegent-zmx: session manager wrapper   │  crates/thegent-zmx/src/lib.rs:1
│  - thegent-zmx-interop: C ABI FFI          │  crates/thegent-zmx-interop/src/lib.rs:1
│  - thegent-offload: remote server          │  crates/thegent-offload/src/main.rs:1
│  - thegent-hooks: hook runtime core        │  crates/thegent-hooks/Cargo.toml:1
│  - thegent-router: routing logic           │  crates/thegent-router/Cargo.toml:1
│  - ... (20 more crates)                    │
├─────────────────────────────────────────────┤
│  Vendored / External Runtimes               │
│  - Extism Wasm runtime (Python bindings)  │  src/thegent/infra/wasm_plugin.py:97
│  - ZMX session manager (C library / binary)│  crates/thegent-zmx-interop/build.rs:1
│  - runtime-dispatch binary (execv shim)     │  crates/thegent-runtime/src/main.rs:79
└─────────────────────────────────────────────┘
```

**Key characteristic:** Thegent is a **polyglot layered system** with Python at the top, Rust in the middle, and external runtimes (Extism, ZMX) at the bottom. There are ~28 Rust crates in the workspace (`crates/Cargo.toml:1`), many of which are small, single-purpose modules.

### 3.2 Agentora Runtime Stack

```
┌─────────────────────────────────────────────┐
│  Rust Application Layer                      │
│  - AgentExecutor (use cases)               │  src/application/mod.rs:12
│  - SimpleAgent (echo implementation)        │  src/application/mod.rs:61
├─────────────────────────────────────────────┤
│  Domain Layer                                │
│  - Agent trait + AgentConfig                 │  src/domain/agents/mod.rs:8
│  - Skill trait + SkillRegistry             │  src/domain/skills/mod.rs:10
│  - Tool trait + ToolRegistry                │  src/domain/tools/mod.rs:54
│  - Context + Output + ExecutionMetrics      │  src/domain/context/mod.rs:8
│  - MemoryEntry + ShortTermMemory            │  src/domain/memory/mod.rs:7
├─────────────────────────────────────────────┤
│  Infrastructure Layer                        │
│  - Error / Result types                     │  src/infrastructure/error.rs:1
│  - (LLM adapters stub)                      │  src/adapters/llm/mod.rs:1
│  - (Memory adapters stub)                   │  src/adapters/memory/mod.rs:1
├─────────────────────────────────────────────┤
│  Sidecar Daemon (phenotype-daemon)          │
│  - Tokio async server (Unix + TCP)         │  crates/pheno-agent/phenotype-daemon/src/main.rs:1
│  - Msgpack-RPC protocol                     │  crates/pheno-agent/phenotype-daemon/src/protocol.rs:1
│  - DashMap skill registry                   │  crates/pheno-agent/phenotype-daemon/src/rpc.rs:52
│  - Buffer pooling                            │  crates/pheno-agent/phenotype-daemon/src/rpc.rs:19
├─────────────────────────────────────────────┤
│  Process Runtime (pheno-proc-runtime)         │
│  - ProcessPool (mutex-guarded HashMap)      │  crates/pheno-proc-runtime/pheno-proc-core/src/lib.rs:226
│  - SharedRuntime (node/bun pooling)        │  crates/pheno-proc-runtime/pheno-proc-core/src/lib.rs:157
│  - ProjectLimits / ProjectResources        │  crates/pheno-proc-runtime/pheno-proc-core/src/lib.rs:82
└─────────────────────────────────────────────┘
```

**Key characteristic:** Agentora is a **pure Rust hexagonal architecture** with clean domain/application/infrastructure layers. It uses tokio as the sole async runtime and has a sidecar daemon for remote skill management. The `pheno-proc-runtime` manages Node/Bun process pools (suggesting it was designed for JS-heavy agent workloads).

### 3.3 Overlap Matrix — Runtime

| Capability | thegent | Agentora | Merge Recommendation |
|------------|---------|----------|---------------------|
| Async runtime | Python asyncio + Rust tokio (in crates) | Rust tokio (sole) | **Agentora wins** — single runtime is simpler; thegent's split is historical debt |
| Execution orchestrator | `ExecutionOrchestrator` (static methods, pure logic) | `AgentExecutor` (struct with skills/tools) | **Conceptually duplicate** — both coordinate agent + skills + tools; merge into shared trait |
| Concurrency control | `ConcurrencyController` (lane-based: standard/critical) | **None** (implicit tokio limits) | **Keep in thegent** — Agentora doesn't need this complexity yet |
| Process pool | **None** (Python subprocess per agent) | `ProcessPool` (node/bun harness) | **Keep in Agentora** — thegent doesn't have this |
| Run registry | `RunRegistry` (JSONL with hash chain) | **None** | **Keep in thegent** — audit/compliance feature |
| Policy engine | `PolicyEngine` (circuit breaker, OPA, confidence) | **None** | **Keep in thegent** — governance feature |
| Sidecar daemon | **None** (plugin-host is binary, not daemon) | `phenotype-daemon` (msgpack-RPC) | **Keep in Agentora** — remote skill registry is its unique feature |
| Buffer pooling | **None** | `BytesPool` (phenotype-daemon) | **Extract to shared if daemon is adopted** |
| Session management | `ZmxClient` / `thegent-zmx` | **None** | **Keep in thegent** — terminal session management |

---

## 4. Vendored / Second Runtimes — Detailed Inventory

### 4.1 thegent — 4 Vendored/Embedded Runtimes

| Runtime | Crate/Module | Type | Integration | File Ref |
|---------|-------------|------|-------------|----------|
| **Extism Wasm runtime** | `thegent.infra.wasm_plugin` | Python bindings to C library | `extism` package imported at runtime; singleton `ExtismRuntime` | `src/thegent/infra/wasm_plugin.py:97` |
| **ZMX session manager** | `thegent-zmx` + `thegent-zmx-interop` | C ABI FFI OR subprocess | `build.rs` searches for `libzmx`; falls back to `zmx` binary | `crates/thegent-zmx-interop/build.rs:1` |
| **runtime-dispatch binary** | `thegent-runtime` | Standalone Rust binary | Symlinked as `git`, `grep`, `ls`, etc. Intercepts and caches tool calls | `crates/thegent-runtime/src/main.rs:1` |
| **plugin-host binary** | `thegent-plugin-host` | Rust lib + cdylib + staticlib | Python `PluginHostAdapter` spawns binary and talks via Unix socket | `crates/thegent-plugin-host/src/lib.rs:1` |

**Additional notes:**
- `thegent-wasm-tools` is a **Zig SDK** (not a runtime) for building tools that run in the Extism runtime.
- `thegent-offload` is a **remote compute server** (TCP listener) for distributed agent execution.
- `thegent-hooks` is a **hook runtime core** (Rust binary for git-like hooks).

### 4.2 Agentora — 0 Vendored/Embedded Runtimes

| Runtime | Status | Notes |
|---------|--------|-------|
| **Extism/Wasm** | Not present | No sandboxed plugin model |
| **External session manager** | Not present | No ZMX equivalent |
| **Tool dispatch binary** | Not present | No `runtime-dispatch` equivalent |
| **Plugin host** | Not present | Skills are native Rust code |
| **tokio** | External dependency | Standard async runtime, not vendored |

### 4.3 Overlap & Dedup

| Runtime | thegent | Agentora | Action |
|---------|---------|----------|--------|
| Extism Wasm | Yes | No | **Keep in thegent** — no equivalent in Agentora; migrating would require full Wasm toolchain |
| ZMX | Yes | No | **Keep in thegent** — terminal session management is niche; Agentora has no TUI/terminal focus |
| runtime-dispatch | Yes | No | **Evaluate** — if Agentora needs tool interception, the Rust binary is portable; but Agentora's current design doesn't need it |
| plugin-host | Yes | No | **Evaluate** — if Agentora wants Wasm plugins, the `thegent-plugin-host` crate is reusable; but currently no use case |

---

## 5. Dedup / Interop Plan

### 5.1 What Should Merge (Consolidate into Shared)

| # | Component | Source | Target | Rationale |
|---|-----------|--------|--------|-----------|
| 1 | **Skill manifest schema** | Agentora's `SkillManifest` (`phenotype-skills/src/lib.rs:88`) + thegent's `SkillManifest` (`skills/discovery/__init__.py:12`) | Shared JSON schema | Agentora's manifest is richer (dependencies, environment, config_schema). Thegent's markdown model is simpler. Merge: JSON schema as canonical, markdown as fallback rendering. |
| 2 | **Dependency resolver** | Agentora's `DependencyResolver` (`phenotype-skills/src/lib.rs:219`) | Shared Rust crate + Python bindings | Thegent has **no** dependency resolution for skills. This is a clear gap. Extract Agentora's resolver into a standalone crate with PyO3 bindings for thegent. |
| 3 | **Skill registry trait** | Both | Shared trait definition | Both have `register`/`get`/`list`/`has`. Define a language-agnostic trait (OpenAPI or gRPC) so both implementations can satisfy it. |
| 4 | **Execution orchestrator interface** | Both | Shared trait / gRPC contract | Thegent's `ExecutionOrchestrator` (`use_cases/execute_task.py:26`) and Agentora's `AgentExecutor` (`application/mod.rs:12`) do the same thing: run agent with skills + tools + memory. Define a shared `AgentExecutor` trait with language bindings. |
| 5 | **Msgpack-RPC protocol** | Agentora's `phenotype-daemon` (`protocol.rs:1`) | Shared protocol spec | Thegent's plugin-host uses IPC but no formal protocol. Agentora's msgpack-RPC is well-defined. Extract as shared protocol for all inter-process skill communication. |
| 6 | **Tool router schema** | Thegent's `ToolRouter` (`utils/routing_impl/tool_router.py:1`) | Shared schema | Both have tool routing. Thegent's `ToolRouter` supports `protocol: 'wasm', 'mcp', 'rest', 'python', 'cli'`. Agentora's `ToolRegistry` is in-process. Unify the tool descriptor schema. |

### 5.2 What Should Stay Separate (Intentional Divergence)

| # | Component | thegent | Agentora | Rationale |
|---|-----------|---------|----------|-----------|
| 1 | **Language runtime** | Python + Rust | Rust only | Thegent's Python layer is massive (~2,500 .py files). Agentora is a clean-slate Rust framework. Do not merge language stacks. |
| 2 | **Wasm plugin execution** | Extism + `thegent-wasm-tools` | None | Agentora's design philosophy is native Rust execution. Adding Wasm would contradict its simplicity. |
| 3 | **Terminal session management** | `thegent-zmx` | None | Agentora has no TUI/terminal focus. ZMX is specific to thegent's shell-oriented workflow. |
| 4 | **Runtime dispatch binary** | `thegent-runtime` | None | Agentora doesn't intercept system tools. The dispatch binary is specific to thegent's "shim everything" strategy. |
| 5 | **Policy engine / governance** | `PolicyEngine` + `RunRegistry` | None | Agentora is a framework, not a governed platform. Policy is a thegent concern. |
| 6 | **Process pool (node/bun)** | None | `pheno-proc-runtime` | Thegent doesn't manage JS runtimes. Agentora's process pool is for its specific use case. |
| 7 | **Prompt-based skill activation** | `AgentRunner.activate_skill` | None | Agentora executes skills as code; thegent injects them as prompts. These are fundamentally different paradigms. |
| 8 | **Filesystem skill discovery** | `SkillDiscovery` | None | Agentora's daemon model is registry-based. Filesystem discovery is a thegent UX choice. |

### 5.3 What Should Extract to Shared (New Repo / Crate)

| # | Extracted Component | Contents | Consumers | Form |
|---|---------------------|----------|-----------|------|
| 1 | **`agentkit-core`** | `Skill` trait, `Tool` trait, `Agent` trait, `Context`, `Output`, `ExecutionMetrics` | Agentora (native), thegent (via PyO3 or gRPC) | Rust crate + gRPC/protobuf definitions |
| 2 | **`skill-registry-protocol`** | Msgpack-RPC protocol, `SkillManifest` schema, `DependencyResolver` interface | `phenotype-daemon`, thegent plugin-host, any future sidecar | Rust crate + OpenAPI spec |
| 3 | **`agent-executor-trait`** | `AgentExecutor` interface, `run(agent, input) → Output` | Agentora's `AgentExecutor`, thegent's `ExecutionOrchestrator` | Rust trait + Python Protocol class |
| 4 | **`wasm-plugin-bridge`** | `PluginHostAdapter` IPC protocol, `WasmPlugin` metadata schema | thegent (existing), any future Wasm-enabled framework | Rust crate + JSON schema |
| 5 | **`process-runtime-core`** | `ProcessPool`, `SharedRuntime`, `ProjectLimits` | Agentora's `pheno-proc-runtime`, thegent if it wants process pools | Rust crate |

### 5.4 Migration Path

**Phase 1 — Schema alignment (weeks 1-2)**
1. Unify `SkillManifest` schema between thegent's `SkillManifest` dataclass and Agentora's `SkillManifest` struct.
2. Add `dependencies`, `environment`, `config_schema` fields to thegent's manifest.
3. Make thegent's `SkillDiscovery` emit the unified schema.

**Phase 2 — Protocol extraction (weeks 3-4)**
1. Extract Agentora's `phenotype-daemon` protocol (`protocol.rs`) into `skill-registry-protocol` crate.
2. Add gRPC fallback to the msgpack-RPC protocol for broader compatibility.
3. Make thegent's `PluginHostAdapter` speak the same protocol (replace ad-hoc IPC).

**Phase 3 — Rust core extraction (weeks 5-6)**
1. Extract Agentora's domain layer (`domain/skills`, `domain/tools`, `domain/agents`, `domain/context`, `domain/memory`) into `agentkit-core` crate.
2. Add PyO3 bindings so thegent's Python code can import `agentkit_core` as a native module.
3. Replace thegent's `AdapterRegistry` and `PluginHost` with traits from `agentkit-core`.

**Phase 4 — Dependency resolver bridge (weeks 7-8)**
1. Package Agentora's `DependencyResolver` as a standalone crate with Python bindings.
2. Integrate into thegent's `SkillDiscovery` so skills can declare dependencies and be validated.

**Phase 5 — Runtime evaluation (weeks 9-10)**
1. Evaluate whether thegent's `runtime-dispatch` or `thegent-plugin-host` should be reused by Agentora.
2. If yes, move them to shared crates; if no, keep them thegent-only.

---

## 6. File:Line Reference Index

### thegent — Key Files

| File | Lines | Role |
|------|-------|------|
| `src/thegent/skills/discovery/__init__.py` | 1-191 | Skill discovery, manifest, activation |
| `src/thegent/agents/base.py` | 1-182 | Agent runner base, skill activation, deferral |
| `src/thegent/mcp/server/tools_skills.py` | 1-139 | MCP skill registry, tool implementations |
| `src/thegent/adapters/ports.py` | 1-310 | Plugin interface, driver/router registry, plugin host |
| `src/thegent/adapters/plugin_host_adapter.py` | 1-372 | Python ↔ Rust plugin host bridge |
| `src/thegent/infra/wasm_plugin.py` | 1-578 | Extism Wasm plugin manager |
| `src/thegent/use_cases/execute_task.py` | 1-173 | Execution orchestrator (pure logic) |
| `src/thegent/execution/__init__.py` | 1-1696 | Run registry, policy engine, circuit breaker, concurrency |
| `src/thegent/core/ports/__init__.py` | 1-170 | Hexagonal port interfaces (Agent, Model, Router, Executor) |
| `crates/thegent-runtime/src/main.rs` | 1-838 | Unified runtime dispatch binary |
| `crates/thegent-plugin-host/src/lib.rs` | 1-29 | Rust plugin host (hexagonal) |
| `crates/thegent-plugin-host/Cargo.toml` | 1-50 | Plugin host crate config |
| `crates/thegent-wasm-tools/src/lib.rs` | 1-270 | Zig SDK for Wasm tools |
| `crates/thegent-zmx/src/lib.rs` | 1-614 | ZMX session manager wrapper |
| `crates/Cargo.toml` | 1-50 | Workspace definition (28 crates) |
| `src/thegent/config/settings.py` | 449 | `factory_skills_dir` config |

### Agentora — Key Files

| File | Lines | Role |
|------|-------|------|
| `src/lib.rs` | 1-25 | Crate root, prelude, re-exports |
| `src/domain/skills/mod.rs` | 1-129 | Skill trait, SkillRegistry, SkillResult |
| `src/domain/tools/mod.rs` | 1-187 | Tool trait, ToolRegistry, ToolCall/Response |
| `src/domain/agents/mod.rs` | 1-110 | Agent trait, AgentConfig, ExecutionStep |
| `src/domain/context/mod.rs` | 1-126 | Context, Output, OutputContent, ExecutionMetrics |
| `src/domain/memory/mod.rs` | 1-187 | MemoryEntry, ShortTermMemory, MemoryStore, LongTermMemory |
| `src/application/mod.rs` | 1-72 | AgentExecutor, SimpleAgent |
| `src/infrastructure/error.rs` | 1-3 | Error re-export |
| `src/adapters/llm/mod.rs` | 1 | LLM adapter stub |
| `src/adapters/memory/mod.rs` | 1 | Memory adapter stub |
| `crates/pheno-agent/phenotype-skills/src/lib.rs` | 1-387 | Daemon skill types: SkillId, SkillManifest, DependencyResolver, SkillRegistry |
| `crates/pheno-agent/phenotype-daemon/src/main.rs` | 1-161 | Tokio daemon (Unix + TCP) |
| `crates/pheno-agent/phenotype-daemon/src/protocol.rs` | 1-188 | Msgpack-RPC protocol definitions |
| `crates/pheno-agent/phenotype-daemon/src/rpc.rs` | 1-371 | RPC handler with DashMap + buffer pooling |
| `crates/pheno-agent/phenotype-daemon/Cargo.toml` | 1-72 | Daemon crate config |
| `crates/pheno-proc-runtime/pheno-proc-core/src/lib.rs` | 1-506 | ProcessPool, SharedRuntime, ProjectLimits |
| `crates/pheno-proc-runtime/pheno-proc-core/Cargo.toml` | 1-18 | Process runtime crate config |
| `Cargo.toml` | 1-60 | Package config (name: `agentkit`) |

---

## 7. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| thegent's Python layer is too large to refactor safely | High | Do not rewrite thegent in Rust. Bridge at protocol layer only. |
| Agentora's `phenotype-daemon` protocol is immature (TODOs for sandbox tracking, uptime) | Medium | Stabilize protocol before extraction. Complete TODOs in `rpc.rs:126`, `rpc.rs:128`. |
| Skill manifest schema incompatibility (markdown vs structured JSON) | Medium | Define a canonical JSON schema; markdown is a render target. |
| PyO3 binding complexity for `agentkit-core` | Medium | Start with gRPC bridge; add PyO3 only if performance requires it. |
| Duplicate crate names / workspace conflicts | Low | Use namespaced crate names: `agentkit-core`, `agentkit-protocol`. |
| Loss of thegent's governance features (PolicyEngine, RunRegistry) if merged incorrectly | Low | Keep governance thegent-only. Do not move to shared layer. |

---

## 8. Conclusion

The two frameworks are **complementary, not redundant**. Thegent is a mature, feature-rich Python platform with extensive governance, sandboxing, and runtime interception. Agentora is a lean Rust-native framework with a clean domain model and a high-performance sidecar daemon.

**The highest-value dedup actions are:**
1. **Unify skill manifest schemas** — Agentora's schema is richer; adopt it as canonical.
2. **Extract the dependency resolver** — Thegent has no skill dependency management; Agentora does.
3. **Standardize the sidecar protocol** — Agentora's msgpack-RPC daemon is well-designed; make it the interop standard.
4. **Define shared domain traits** — `Skill`, `Tool`, `Agent`, `Context`, `Output` should live in a shared Rust crate with multi-language bindings.

**What should NOT be merged:**
- Thegent's Python CLI/application layer
- Thegent's Wasm/Extism plugin stack (unless Agentora explicitly wants sandboxed plugins)
- Thegent's ZMX session manager
- Agentora's process pool (unless thegent wants JS runtime management)
- Either's governance/policy layer (platform-specific)

---

*End of audit.*
