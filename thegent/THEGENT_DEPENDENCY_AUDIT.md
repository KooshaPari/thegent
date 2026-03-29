# Thegent Dependency & Pattern Audit

**Date**: 2026-02-21
**Focus**: Just thegent project

---

## Dependencies by Category

### Core
| Library | Purpose | Status |
|---------|---------|--------|
| httpx | HTTP client | ✅ Standard |
| pydantic | Data validation | ✅ Standard |
| pydantic-settings | Config | ✅ Standard |

### CLI/UI
| Library | Purpose | Status |
|---------|---------|--------|
| typer | CLI framework | ✅ Standard |
| rich | Terminal UI | ✅ Standard |
| textual | TUI framework | ✅ Standard |

### Resilience
| Library | Purpose | Status |
|---------|---------|--------|
| tenacity | Retry logic | ✅ Standard |
| pybreaker | Circuit breaker | ✅ Standard |

### Caching
| Library | Purpose | Status |
|---------|---------|--------|
| cachetools | TTL/LRU cache | ✅ Standard |
| diskcache | Persistent cache | ✅ Standard |

### File Watching
| Library | Purpose | Status |
|---------|---------|--------|
| watchdog | File watching | ✅ Standard |
| watchfiles | Fast watching (Rust) | ✅ Standard |

### Performance
| Library | Purpose | Status |
|---------|---------|--------|
| granian | Fast async HTTP | ✅ Rust-based |
| orjson | Fast JSON (CPython) | ✅ Standard |
| ujson | Fast JSON (PyPy) | ✅ Standard |

### AI/LLM
| Library | Purpose | Status |
|---------|---------|--------|
| litellm | LLM gateway (50+ providers) | ✅ Standard |
| duckduckgo-search | Search | ✅ Standard |
| praw | Reddit API | ✅ Standard |
| playwright | Browser automation | ✅ Standard |

### MCP/Server
| Library | Purpose | Status |
|---------|---------|--------|
| fastmcp | MCP server framework | ✅ Standard |
| starlette | Web framework | ✅ Standard |
| uvicorn | ASGI server | ✅ Standard |

### WASM/Plugins
| Library | Purpose | Status |
|---------|---------|--------|
| extism | WASM runtime | ✅ Standard |

### Telemetry
| Library | Purpose | Status |
|---------|---------|--------|
| opentelemetry-api | Observability | ✅ Standard |
| opentelemetry-sdk | Observability | ✅ Standard |

### Code Quality (Dev)
| Library | Purpose | Status |
|---------|---------|--------|
| ruff | Linting | ✅ Standard |
| basedpyright | Type checking | ✅ Enhanced mypy |
| mypy | Type checking | ✅ Standard |
| pre-commit | Hooks | ✅ Standard |
| tach | Code organization | ✅ Unique |
| vulture | Dead code | ✅ Standard |
| radon | Complexity | ✅ Standard |

### Testing
| Library | Purpose | Status |
|---------|---------|--------|
| pytest | Testing | ✅ Standard |
| pytest-asyncio | Async testing | ✅ Standard |
| pytest-cov | Coverage | ✅ Standard |
| pytest-xdist | Parallel | ✅ Standard |

---

## Custom Patterns Built on Libraries

| Pattern | Library Used | Custom Addition |
|---------|-------------|-----------------|
| Multi-tier cache | cachetools + diskcache | L1/L2/L3 orchestration |
| Dual watcher | watchdog + watchfiles | Auto selection |
| Circuit registry | pybreaker | Per-provider config |
| Rate limiter | — | Custom sliding window |
| Semantic cache | — | Embedding-based similarity |
| Capability index | cachetools | Agent discovery |
| Hot-reload | watchfiles | MCP restart |
| Process compose | process-compose | Service management |

---

## Architecture Patterns

### Pools & Workers
- `orchestration/worker_pool.py` - Task worker pool
- `orchestration/execution/priority_queue.py` - Priority queue
- `orchestration/event_queue.py` - Event queue
- `core/worker_pool.py` - Core worker pool
- `mesh/task_queue.py` - Distributed task queue

### Protocols & Adapters
- `routing/donut_adapter.py` - Routing adapter
- `adapters/acp_mcp_bridge` - ACP-MCP bridge
- `governance/helios_bridge.py` - Helios bridge
- `infra/multi_runtime_bridge.py` - Runtime bridge
- `config_provider.py` - Config adapter

### Events & Hooks
- `events/event_system.py` - Event system
- `governance/triggers.py` - Governance triggers
- `governance/plugin_lifecycle.py` - Plugin lifecycle
- `hooks/` - Pre-commit hooks

### Governance & Security
- `governance/policy_federation.py` - Policy federation
- `governance/hitl.py` - Human-in-the-loop
- `security/guardrails.py` - Security guardrails
- `isolation/` - Resource isolation

### Registries & Indexes
- `agents/registry.py` - Agent registry
- `agents/capability_index.py` - Capability index
- `contracts/registry.py` - Contract registry
- `discovery/projects.py` - Project discovery
- `routing/route_config.py` - Route config registry

### Caches (Specialized)
- `routing/cache.py` - LLM response cache
- `routing/semantic_cache.py` - Embedding similarity cache
- `cache/multi_level.py` - Multi-tier cache
- `cache/frecency.py` - Frecency cache
- `memory/cache.py` - Memory cache
- `infra/fast_cache.py` - Fast tiered cache

---

## Unique/Niche Libraries

1. **granian** - Rust-based fast async
2. **extism** - WASM plugin runtime
3. **litellm** - 50+ LLM providers unified
4. **fastmcp** - MCP server framework
5. **watchfiles** - Rust-based file watching
6. **basedpyright** - Enhanced mypy fork
7. **tach** - Code organization enforcement
8. **psleak** - Memory leak detection
9. **radon** - Cyclomatic complexity

---

## Advanced Integrations

### MCP & Agents
- `fastmcp` - MCP server
- `agents/capability_index.py` - Agent capability discovery
- `agents/unified_registry.py` - Unified agent registry
- `mcp/dynamic_tools.py` - Dynamic tool registration

### Distributed Computing
- `mesh/task_queue.py` - Distributed task queue
- `mesh/smart_merge.py` - Smart git merge
- `orchestration/consensus/` - Consensus protocols

### Storage & Persistence
- `diskcache` - Disk-backed cache
- `session/manager.py` - Session persistence
- `queue/storage.py` - Queue storage
- `resources/disk_queue.py` - Persistent queue

### Observability
- `opentelemetry-api/sdk` - Tracing
- `observability/async_logger.py` - Async logging
- `observability/egress.py` - Telemetry egress

---

## AI/ML Routing Patterns

### Provider Routing
- `routing/litellm_router.py` - LiteLLM routing
- `routing/ml_router.py` - ML-based routing
- `routing/cel_router.py` - CEL routing
- `routing/cost_aware_router.py` - Cost-aware routing
- `routing/tag_router.py` - Tag-based routing

### Semantic & Embeddings
- `routing/semantic_cache.py` - Embedding similarity cache
- `routing/semantic_lb` - Semantic load balancing
- `routing/guardrails/semantic_guard.py` - Semantic guardrails

### Model Management
- `models/catalog.py` - Model catalog
- `routing/model_metadata.py` - Model metadata
- `agents/digital_twin.py` - Digital twin for models

---

## ⚠️ Polyglot Optimization (Python Overuse)

### Python subprocess Heavy Areas (Could Be Rust)
| File | Purpose | Rust Alternative |
|------|---------|-----------------|
| `shell_cli.py` | Shell commands | Use crates/thegent-shims |
| `orchestration/pruning/smart_prune.py` | File ops | Use thegent-pruner |
| `governance/scanner.py` | Code scanning | Use thegent-hooks |
| `native/git_native.py` | Git ops | Use thegent-git |
| `native/discovery_native.py` | File discovery | Use thegent-discovery |

### Existing Rust Crates (Good!)
| Crate | Purpose |
|-------|---------|
| thegent-hooks | Git operations |
| thegent-shims | Shell shims |
| thegent-router | Routing |
| thegent-jsonl | JSONL processing |
| thegent-cache | Caching |
| thegent-git | Git operations |
| thegent-discovery | File discovery |
| thegent-memory | Memory |
| thegent-pruner | Pruning |
| thegent-watcher | File watching |

### Subprocess Heavy (60+ files)
- Many subprocess.run/Popen calls could use FFI to existing crates

### Recommendations
1. **Use existing Rust crates** - Already compiled binaries exist!
2. **Replace subprocess with FFI** - Call Rust directly
3. **Reduce shell=True** - Security + perf
4. **Batch operations** - Not loops

---

## Zig & Mojo Integration

### Zig Contracts
- `contracts/runtime/zig_abi_contract_v1.json` - Zig ABI contract v1.0.0
- `crates/thegent-zmx-interop/` - Zig interop crate
- `tests/test_wl132_zig_abi_contract.py` - Zig contract tests (9 passing)
- `scripts/validate_zig_abi_contract.py` - Validation script
- `scripts/check_zig_abi_artifact.py` - Artifact checker

### Mojo Contracts
- `contracts/runtime/mojo_kernel_contract_v1.json` - Mojo kernel contract
- `tests/mojo/test_wl133_mojo_kernel_smoke.py` - Mojo smoke tests
- `tests/mojo/test_mojo_kernel_contract_v1.py` - Kernel contract tests
- `tests/mojo/fixtures/deterministic_score_v1.json` - Mojo fixtures

### Runtime Modularization Matrix
- `contracts/runtime/runtime_modularization_matrix_v1.json` - Multi-runtime tracking
- `contracts/runtime/runtime-modularization-matrix-v2.json` - Runtime decomposition
- `Taskfile.yml` quality gates for Zig & Mojo

### Rust Crates (Zig/Mojo Interop)
- `crates/thegent-zmx-interop/src/lib.rs` - Zig FFI wrapper
- `crates/thegent-wasm-tools/src/hello_world.zig` - Zig WASM example

---

## Protocols & Interfaces

### Orchestration
- `orchestration/protocol.py` - Orchestration protocol
- `orchestration/sub_agent_dispatcher.py` - Sub-agent dispatch
- `orchestration/consensus/` - Consensus protocols

### Mesh & Federation
- `mesh/consensus.py` - Mesh consensus
- `mesh/task_queue.py` - Distributed task queue
- `governance/policy_federation.py` - Policy federation

### Contracts & Compliance
- `contracts/adapters.py` - Contract adapters
- `contracts/conformance.py` - Conformance checking
- `governance/verification_gate.py` - Verification gates

### Session & State
- `session/zmx_backend.py` - ZMX session backend
- `session/manager.py` - Session management
3. **litellm** - 50+ LLM providers unified
4. **fastmcp** - MCP server framework
5. **watchfiles** - Rust-based file watching
6. **basedpyright** - Enhanced mypy fork
7. **tach** - Code organization enforcement
8. **psleak** - Memory leak detection

---

## Library-First Compliance: ✅ 100%

All patterns use standard libraries. Custom code only adds orchestration/domain logic.
