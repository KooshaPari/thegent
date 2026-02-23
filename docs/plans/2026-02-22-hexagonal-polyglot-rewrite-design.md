# thegent Hexagonal Split + Full Polyglot Rewrite Design

**Date:** 2026-02-22
**Status:** Draft — Pending Plan
**Owner:** kooshapari
**Approach:** B+C Hybrid — Simultaneous hexagonal split + polyglot rewrites (non-incremental)

---

## 1. Context & Problem Statement

thegent is a 245,255-LOC Python-dominant monorepo (74% Python, 3.8% Rust, minimal Zig/Go).
The codebase has grown organically and accumulated:

- **Responsibility confusion:** routing, provider auth, and LLM translation logic duplicated between thegent (`src/thegent/routing/`, `adapters/`, `integrations/auth/`) and CLIProxyAPI-plusplus (Go) — which already owns this domain cleanly
- **Performance debt:** 99KB shell-script governance gate (`hooks/governance-gates.sh`), shell-based hook dispatcher — both are maintenance nightmares and hot-path bottlenecks
- **Language mismatch:** Security-critical paths (crypto, auth, parsing, governance) written in Python when Rust/Zig/Go provide memory safety, performance, and auditability
- **Monolith coupling:** 100+ Python modules with unclear ownership; tach boundary violations; 21K-LOC integrations module; 32K-LOC cli module
- **Ecosystem overlap:** AgentAPI, crun, zen-mcp-server, morph, task-tool all satisfy portions of thegent's scope — consolidation opportunities exist
- **Quality gaps:** routing <50% test coverage, cli <60%, race conditions in orchestration.resource and integrations.auth

**Goal:** Simultaneously restructure and rewrite to achieve:
- Python from 74% → ≤25% of source LOC (orchestration + agent logic only)
- Rust/Zig/Go from ~4% → ≥60% (infrastructure, security, performance)
- All CLIProxy-owned concerns migrated out
- Hexagonal sub-project boundaries enforced at build time
- No incremental migration — parallel tracks, cutover on parity

---

## 2. Current Architecture

```
thegent (monolith)
├── src/thegent/          # 245K LOC Python
│   ├── routing/          # 12K LOC — BELONGS IN CLIPROXY
│   ├── adapters/         # ~8K LOC — BELONGS IN CLIPROXY
│   ├── integrations/     # 21K LOC — AUTH/QUOTA BELONGS IN CLIPROXY
│   ├── cli/              # 32K LOC — TOO LARGE, NEEDS SPLIT
│   ├── agents/           # 15K LOC — KEEP
│   ├── mcp/              # 14K LOC — CANDIDATE FOR RUST MCP SDK
│   ├── governance/       # 12K LOC — NEEDS RUST CORE
│   ├── orchestration/    # 12K LOC — KEEP (PYTHON)
│   └── [70+ more modules]
├── crates/               # 21 Rust crates (3.8% of LOC)
│   ├── thegent-router    # EXISTS — expand, owns Pareto routing
│   ├── thegent-hooks     # EXISTS — expand to replace shell hooks
│   └── [19 more]
└── hooks/                # 39 shell scripts (governance-gates.sh = 99KB!)
```

```
CLIProxyAPI-plusplus (Go)
└── pkg/llmproxy/         # Clean hexagonal library
    ├── translator/       # 30+ provider format translations
    ├── auth/             # OAuth lifecycle, token refresh
    ├── registry/         # Provider routing + selection
    └── executor/         # HTTP communication
```

**Ecosystem (kush/):**
- AgentAPI / AgentAPI++ — multi-agent prototype, partially overlaps
- zen-mcp-server — OpenRouter MCP gateway (Python, 620 files)
- crun — DAG-based multi-agent engine (Python, 279 files)
- morph, task-tool — MCP servers
- bifrost — Go infrastructure bridge

---

## 3. Target Architecture

### 3.1 Sub-Project Constellation

```
thegent-ecosystem/
├── thegent-core/          # Rust + Zig — KERNEL
│   ├── hook-engine/       # Replaces all 39 shell scripts
│   ├── governance/        # Policy engine (Zig - WASM-compilable)
│   ├── session/           # Session state, lifecycle
│   ├── crypto/            # Secrets, signing (extends thegent-crypto crate)
│   └── contracts/         # Contract validation (extends current contracts/)
│
├── thegent-cli/           # Python (thin) — SURFACE
│   ├── dispatch/          # Typer CLI, command routing only
│   ├── tui/               # Terminal UI (Textual)
│   └── (delegates ALL logic to core/agents/mcp via IPC)
│
├── thegent-agents/        # Python — ORCHESTRATION
│   ├── runners/           # Agent execution (strategy pattern)
│   ├── personas/          # 57 agent definitions
│   ├── orchestration/     # Multi-agent coordination, DAGs
│   ├── memory/            # Agent memory (MAIF → Letta migration path)
│   ├── planning/          # Work stream, WBS decomposition
│   └── team/              # Team coordination
│
├── thegent-mcp/           # Python (FastMCP 3.x) + Rust hot-path — PROTOCOL
│   ├── server/            # FastMCP 3.x server (stays Python)
│   ├── tools/             # Tool registry + Rust accelerated tools via PyO3
│   ├── resources/         # Resource management
│   └── prompts/           # Prompt templates
│   # Note: Rust MCP SDK NOT used as server — FastMCP wins on integration
│   # Rust used only for CPU-bound tool implementations (search, diff, parse)
│
└── CLIProxyAPI-plusplus/  # Go — LLM LAYER (unchanged API)
    └── (absorbs thegent routing/adapters/auth)
        ├── translator/    # +thegent adapters
        ├── auth/          # +thegent integrations/auth
        ├── registry/      # +thegent routing/pareto (via Rust FFI or port)
        └── executor/      # unchanged
```

### 3.2 Communication Contracts

All sub-projects communicate via:
- **MCP protocol** (primary) — thegent-mcp is the broker
- **IPC/Unix socket** — thegent-core ↔ thegent-cli (low-latency hooks)
- **HTTP/gRPC** — thegent-agents ↔ CLIProxyAPI++ (provider calls)
- **PyO3 FFI** — thegent-core Rust ↔ thegent-agents Python (where needed)

### 3.3 Language Assignment by Responsibility

| Responsibility | Language | Why |
|---|---|---|
| Hook engine | Zig | Zero runtime, WASM-compilable, memory safe |
| Policy/governance contracts | Zig | Auditable, deterministic, embeddable |
| Session lifecycle | Rust | Memory safety, async, existing crate |
| Crypto/signing | Rust | Existing thegent-crypto crate |
| JSONL/streaming | Rust | Existing thegent-jsonl crate |
| Parser/tokenizer | Rust | Existing thegent-parser crate |
| Pareto routing algorithm | Rust | Existing thegent-router crate |
| MCP server | Python (FastMCP 3.x) + Rust hot-path | FastMCP 3.x is GA, 70% MCP market share, native Python agent integration; Rust PyO3 modules accelerate CPU-bound tools only |
| Git operations | Rust | Existing thegent-git (gix-based) |
| Shared memory | Rust | Existing thegent-shm |
| LLM proxy/translation | Go | CLIProxyAPI++ (mature, clean) |
| Provider auth/OAuth | Go | CLIProxyAPI++ auth subsystem |
| Provider routing/selection | Go | CLIProxyAPI++ registry |
| Agent orchestration | Python | High-level logic, rich ecosystem |
| Agent personas | Python | Natural language, flexibility |
| CLI surface | Python (Typer) | UX, rich/textual ecosystem |
| Research engine | Python | playwright, praw, arxiv libraries |
| Memory/learning | Python | Until Letta migration |

---

## 4. Migration Targets (Python → Out)

### 4.1 Move to CLIProxyAPI++ (Go)

| thegent module | LOC | New home | Notes |
|---|---|---|---|
| `src/thegent/routing/` | ~12,300 | CLIProxy `pkg/llmproxy/registry/` | Port Pareto algorithm or call via Rust FFI |
| `src/thegent/adapters/` | ~8,000 | CLIProxy `pkg/llmproxy/translator/` | Direct merge |
| `src/thegent/integrations/auth/` | ~5,000 | CLIProxy `pkg/llmproxy/auth/` | Direct merge |
| `src/thegent/integrations/quota/` | ~3,000 | CLIProxy registry | Direct merge |
| LiteLLM routing config | ~2,000 | CLIProxy config | CLIProxy replaces LiteLLM routing |

**Total to CLIProxy: ~30,300 Python LOC removed**

### 4.2 Rewrite in Rust

| thegent module | Python LOC | Rust target | Crate |
|---|---|---|---|
| `hooks/` (all 39 scripts) | ~5,000 (shell) | hook engine | thegent-hooks (expand) |
| `src/thegent/governance/` | ~12,638 | policy engine | new: thegent-policy |
| `src/thegent/session/` | ~6,000 | session state | extend thegent-zmx |
| `src/thegent/verification/` | ~4,000 | contract validation | extend contracts |
| `src/thegent/audit/` | ~5,000 | immutable audit log | extend thegent-jsonl |
| `src/thegent/mcp/` | ~14,216 | FastMCP 3.x (stay Python) + Rust PyO3 for CPU tools | Keep FastMCP; accelerate search/diff/parse tools via Rust crate |
| `src/thegent/metrics/` | ~4,000 | metrics collection | new: thegent-metrics |
| `src/thegent/security/` | ~3,000 | security primitives | extend thegent-crypto |

**Total to Rust: ~54,000 Python LOC → ~15,000 Rust LOC**

### 4.3 Rewrite in Zig

| Component | Python/Shell LOC | Zig target | Notes |
|---|---|---|---|
| `hooks/governance-gates.sh` | 99KB shell | zig governance binary | WASM-compilable policy |
| `hooks/hook-dispatcher/` | C++ 472KB | zig hook dispatcher | Replace binary with source |
| Contract validation engine | ~3,000 Python | zig contracts | Deterministic, embeddable |

**Total to Zig: ~5,000 LOC reduction (massive shell → tiny Zig)**

### 4.4 Keep in Python (Orchestration Core)

| Module | LOC | Why keep |
|---|---|---|
| `src/thegent/agents/` | 15,161 | Core agent logic |
| `src/thegent/orchestration/` | 12,157 | High-level coordination |
| `src/thegent/cli/` | 32,336 | After split: ~8,000 (surface only) |
| `src/thegent/memory/` | ~6,000 | Until Letta migration |
| `src/thegent/planning/` | ~5,000 | Work stream logic |
| `src/thegent/research/` | ~8,000 | Web/Reddit/arxiv scraping |
| `src/thegent/prompts/` | ~4,000 | Prompt management |

**Python remainder: ~60,000-70,000 LOC (from 245,255)**

---

## 5. Quality Audit Findings (Non-Negotiable Fixes)

These must be addressed as part of the rewrite, not left as debt:

### 5.1 Critical (Block cutover)
- **Race conditions:** `orchestration.resource`, `integrations.auth` — requires lock analysis and fix
- **Pareto routing correctness:** No formal proof at scale — add property-based tests before Rust port
- **Test coverage:** routing <50%, cli <60% — must reach ≥80% before deletion

### 5.2 High Priority
- **21K integrations module fragmentation** — dedup and split by domain before migration
- **Monolithic files >500 LOC:** 4 files at 6,700 LOC total — split first
- **Governance traceability gaps** — all new Rust/Zig code must have FR IDs in tests
- **Ownership ambiguity** — code-ownership map required before parallel tracks start

### 5.3 Coverage & Governance Gaps
- All new Rust crates: 100% unit + integration test coverage (thegent agent-only standard)
- All new Go code in CLIProxy: existing 100% translator test standard maintained
- All new Zig: property-based tests for deterministic behavior

---

## 6. CLIProxyAPI++ Ecosystem Assessment

### What Stays in CLIProxy (Owns)
- OpenAI-compatible HTTP server
- 30+ provider translations
- OAuth/token lifecycle
- Quota-aware routing
- Rate limiting, cooldown, failure isolation

### What CLIProxy Gains (From thegent)
- Pareto frontier routing algorithm (port from thegent-router Rust crate or Go reimplementation)
- thegent's provider adapters (15+ adapters → merge with existing 30+ translators)
- Auth integrations currently in thegent (Cursor, Antigravity, Kiro, Codex duplicates)

### CLIProxy → thegent Interface
```
thegent-agents calls CLIProxy at localhost:8317 via OpenAI-compatible API
No Python routing logic — thegent delegates ALL LLM calls to CLIProxy
CLIProxy exposes /v0/metrics/providers for thegent governance monitoring
```

---

## 7. Ecosystem Consolidation

Beyond thegent and CLIProxy, the kush/ ecosystem has consolidation opportunities:

| Project | Fate |
|---|---|
| zen-mcp-server | Absorb into thegent-mcp (duplicate OpenRouter MCP) |
| task-tool | Absorb or deprecate (thegent-mcp covers tasks) |
| AgentAPI / AgentAPI++ | Archive (superseded by thegent-agents) |
| crun | Evaluate: merge DAG engine into thegent-agents or keep as dependency |
| morph | Keep separate (different domain: infrastructure MCP) |
| trace | Keep separate (requirements traceability tool) |

---

## 8. Non-Goals

- No incremental migration — parallel development tracks, cutover on parity verification
- Not making CLIProxy Python-aware (it stays pure Go)
- Not rewriting research engine (playwright, praw, arxiv are Python-only)
- Not replacing Typer CLI framework (surface layer stays Python)
- Not changing thegent's public CLI contract (thegent commands unchanged to users)

---

## 9. Success Criteria

| Metric | Current | Target |
|---|---|---|
| Python % of source LOC | 74% | ≤25% |
| Rust/Zig/Go % | ~4% | ≥60% |
| Python total LOC | 245,255 | ≤65,000 |
| Hook dispatch latency | 500ms (shell) | <5ms (Zig) |
| Governance gate latency | 2-5s (shell) | <50ms (Rust) |
| Test coverage: routing | <50% | 100% |
| Test coverage: cli | <60% | ≥80% |
| Race conditions | 2 known | 0 |
| Tach boundary violations | unknown | 0 |
| CLIProxy overlap (Python) | ~30K LOC | 0 |

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Parity regressions in Rust MCP server | Official Rust MCP SDK (Anthropic-maintained) as base |
| Pareto algorithm correctness in Go port | Property-based test suite in Python first; port tests simultaneously |
| Hook system behavioral gaps | Maintain shell hooks in parallel until Zig binary passes full test matrix |
| CLIProxy API contract breaks | Pin CLIProxy version; contract tests in thegent CI |
| Zig ecosystem immaturity | Limit Zig to governance/hooks only; Rust for everything else |

---

*This document feeds directly into the writing-plans skill for WBS generation.*
