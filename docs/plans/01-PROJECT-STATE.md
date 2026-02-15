# 01 — Project State

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [02-WBS](./02-UNIFIED-WBS.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

---

## Current Codebase Metrics

| Metric | Value |
|--------|-------|
| Python source files | 39 (src/) |
| Test files | 20 |
| Lines of Python | ~13,847 |
| CLI commands | 50+ |
| MCP tools | 12 |
| MCP resources | 7 |
| Supported providers | 12+ |
| Documentation files | 44 |

---

## Completed Subsystems

### 1. FastMCP MCP Server (85% complete)

**Done**: Phases 1-4, 6-7
- 19 tools: run, bg, ps, status, logs, wait, stop, list-agents, list-droids, list-models, list-modes, list-operations, resolve-model-route, dag-list, inspect, session-contracts, session-contract-health-gate, session-contract-health-report, session-contract-health-trend, suggest-prompt
- 14 resources: sessions, session/meta, session/logs, session/run, dag, agents, models, droids, meta, operations, modes, route-info, contract-metadata, contract-validation
- 3 prompts: run_agent, create_wbs, bg_task
- Middleware: timing, logging, caching (30s TTL), rate limiting (10/s, burst 20), response limiting (500KB)
- Progress streaming, background tasks, elicitation, sampling, structured output

**Not Done**: Phase 5 (Production Readiness)
- Auth (Bearer/OAuth)
- Stateless mode
- Redis backend for task persistence
- Session state store (distributed)

**Key Files**: `src/thegent/mcp_server.py`, `src/thegent/mcp_manage.py`

### 2. Distributed Model Routing (100% complete)

All 12 phases done:
- Model catalog (static + dynamic scraping)
- Model-first run (`-M <model>`)
- Provider failover (`run_with_failover`)
- Routing policies (prefer_direct, prefer_proxy, failover)
- Scraping adapters for all 8+ providers
- Canonicalization and alias expansion
- Configurable cache TTL
- ModelScraper Protocol

**Key Files**: `src/thegent/models/catalog.py`, `src/thegent/models/scrapers.py`

### 3. Provider Parity (100% complete)

All 6 phases done for 9 providers:
- Cursor (token-file, cursor-api)
- MiniMax (OAuth, API key)
- Roo Code (token-file, API key)
- Kilo (token-file, API key)
- Claude, Gemini, Copilot, Codex (native)
- CLIProxyAPIPlus (local proxy)

**Key Files**: `src/thegent/agents/cliproxy_manager.py`, `src/thegent/agents/direct_agents.py`

### 4. Contract/Health System (100% complete)

261 implementation chunks:
- Route contract metadata with schema versioning
- Contract-aware model listing
- Session contract health gate and reports
- Health trend tracking with snapshots
- Export formats: JSON, MD, CSV, JSONL
- Deterministic payload signatures (SHA-256)
- RunRegistry with unified run IDs

**Key Files**: `src/thegent/execution.py`, `src/thegent/output_parser.py`, `src/thegent/cli_impl.py`

### 5. Contract Governance Foundation (partial)

**Done**:
- CSM v1 schema (`contracts/csm.py`)
- Contract registry (`contracts/registry.py`)
- Incremental XML parser (`contracts/parser.py`)
- Semantic validation (`contracts/validation.py`)
- Provider adapter interface (`contracts/adapters.py`)
- Conformance testing (`contracts/conformance.py`)
- Fallback policy evaluation (`contracts/policy.py`)
- Contract migration controller (`contracts/migration.py`)
- Contract telemetry with drift detection (`contracts/telemetry.py`)
- Fallback state machine (`agents/state_machine.py` - manages provider fallbacks and retry logic)

**Not Done**:
- Contract version negotiation (FR-X01)
- Canonical normalization pipeline wired end-to-end (FR-X02)
- Observability for parse quality (FR-X08)

**Key Files**: `src/thegent/contracts/` (10 files) + `src/thegent/agents/state_machine.py`

---

## Not Started Subsystems

### 1. Orchestration Platform (Phase 0-6 WBS)

The core PRD — 48 original work packages across 7 phases. None started.
- DAG execution engine with dependency satisfaction
- Checkpoint/rollback service
- Policy pre-check and gate evaluator
- Operator cockpit
- Adaptive concurrency controller
- Enterprise readiness

### 2. Cross-Cutting Enhancements (Phase Y)

8 new work packages from research synthesis. None started.
- Multi-agent mode runtime (WP-Y1)
- Dead-letter queue service (WP-Y2)
- Chaos engineering framework (WP-Y3)
- Cost tracking and optimization (WP-Y4)
- Hierarchical prompt orchestration (WP-Y5)
- OTel GenAI instrumentation (WP-Y6)
- TRAFFIC KPI dashboard (WP-Y7)
- Provider scoring with learning (WP-Y8)

### 3. State-Aware Orchestration

**Partially Done**:
- Run state tracking (running/paused/completed/failed) — RunState enum in execution.py
- Pause/resume registry events (register_pause, register_resume, get_run_state)
- Pause/resume CLI commands (pause_cmd, resume_cmd in cli.py)

**Not Done**:
- MCP pause/resume tools (planned for Phase 1)
- ContinuityPacket dataclass (design draft only)
- Checkpoint continuity snapshots (checkpoint infrastructure exists, but snapshots not fully wired)

---

## Existing Test Coverage

| Category | Files | Tests | Status |
|----------|-------|-------|--------|
| Unit: CLI | test_unit_cli.py | ~10 | Passing |
| Unit: Config | test_unit_config.py | ~5 | Passing |
| Unit: Contracts | test_unit_contracts.py | ~8 | Passing |
| Unit: Execution | test_unit_execution.py | ~5 | Passing |
| Unit: Health | test_unit_health_*.py | 13 | Passing |
| Unit: MCP | test_unit_mcp.py | ~5 | Passing |
| Unit: Models | test_unit_models.py | ~5 | Passing |
| Unit: Output Parser | test_unit_output_parser.py | 13 | Passing |
| Unit: Providers | test_unit_providers_comprehensive.py | ~10 | Passing |
| Unit: Registry | test_unit_registry.py | ~5 | Passing |
| Unit: Runners | test_unit_runners.py | ~5 | Passing |
| Integration | test_integration_agent.py | ~3 | Passing |
| E2E | test_e2e_cli.py | 100+ | Passing |
| E2E Health | test_e2e_health_trend_cli.py | ~5 | Passing |
| Resilience | test_resilience.py | ~5 | Passing |
| Conformance | test_contract_conformance.py | ~5 | Passing |
| Validation | test_agent_sync_async_validation.py | ~3 | Passing |

**Total**: ~200+ tests, all passing
**Gap**: No tests for orchestration, governance, adaptive scaling, or UX subsystems (not yet built)

---

## Configuration State

| Config | Value | File |
|--------|-------|------|
| Python | >=3.12 | pyproject.toml |
| Package manager | uv | uv.lock |
| Build | hatchling | pyproject.toml |
| Linter | ruff (line-length 120) | pyproject.toml |
| Type checker | mypy | pyproject.toml |
| MCP host | 127.0.0.1:3847 | .env.example |
| Process orchestrator | process-compose | process-compose.yaml |
| Entry point | `thegent` | pyproject.toml |

---

## Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| THGENT_SESSION_DIR | ~/.thegent/sessions | Session storage |
| THGENT_MCP_HOST | 127.0.0.1 | MCP bind address |
| THGENT_MCP_PORT | 3847 | MCP HTTP port |
| THGENT_CLIPROXY_URL | http://localhost:8317 | CLIProxy URL |
| THGENT_CLIPROXY_API_KEY | — | CLIProxy auth |
| THGENT_CURSOR_AGENT_CMD | cursor-agent | Cursor CLI path |
| THGENT_DEFAULT_ROUTING | failover | Routing policy |
| THGENT_MODELS_CACHE_TTL_SEC | 300 | Model cache TTL |
| FASTMCP_DOCKET_URL | memory:// | Task backend URL |
