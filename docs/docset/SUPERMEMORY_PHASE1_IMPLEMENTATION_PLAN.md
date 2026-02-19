# Supermemory Integration — Phase 1 Implementation Plan

**Session**: 2026-02-18
**Status**: Planning (Option A) — Full plan now, start high-impact tasks
**Budget**: ~260 tool calls (~600s). Plan + start high-impact tasks.
**Owner**: claude-code, continued from prior session

---

## Executive Summary

Phase 1 delivers a **working, isolated Supermemory integration** with:
1. **Rust client** (supermemory-rs) connecting to Supermemory.ai APIs
2. **Python L1/L2 cache** layer (SQLite/LRU for fast local access)
3. **Configuration & setup** (env, connection management, tests)

**Success Criteria**:
- [ ] `crates/supermemory-rs` compiles and passes unit tests
- [ ] L1/L2 cache (Python) stores/retrieves embeddings, metadata, sessions
- [ ] Configuration tested with live Supermemory.ai sandbox
- [ ] Documentation + quick-start guide

**Timeline**: 9-12 days wall-clock (3 independent work packages, ~4-5 days each with parallelization)

---

## Phase 1 Decomposition

### P1.1: Supermemory Client (Rust) — 4-5 days

**Deliverables**:
- `crates/supermemory-rs/Cargo.toml` with deps (reqwest, serde, uuid, tokio)
- `crates/supermemory-rs/src/lib.rs` (client structure, public API)
- `crates/supermemory-rs/src/client.rs` (HTTP/REST client methods)
- `crates/supermemory-rs/src/types.rs` (request/response types, serde)
- `crates/supermemory-rs/src/memory.rs` (high-level memory operations: store, retrieve, search)
- `crates/supermemory-rs/src/error.rs` (error types + display)
- Tests: unit tests for client, type serialization, error handling

**Key Tasks**:
1. **Scaffold Cargo project** (P1.1.1 — 30 min)
   - Create `Cargo.toml` with reqwest, serde_json, tokio, uuid, thiserror
   - Add dev-dependencies: mockito, tokio-test
   - Verify `cargo build` passes

2. **Define client types** (P1.1.2 — 1-2 hours)
   - `SupremoryClient { api_key, base_url, http_client }`
   - `MemoryOperation { id, timestamp, operation_type, data }`
   - `MemoryQuery { embedding, session_id, limit, filters }`
   - `MemoryResponse { results, metadata, session_context }`
   - Full serde derive for JSON serialization

3. **Implement client methods** (P1.1.3 — 2-3 hours)
   - `new(api_key, base_url) -> Result<SupremoryClient>`
   - `store_memory(operation: MemoryOperation) -> Result<MemoryId>`
   - `retrieve_memory(id: &str) -> Result<MemoryOperation>`
   - `search(query: MemoryQuery) -> Result<Vec<MemoryOperation>>`
   - `delete_memory(id: &str) -> Result<()>`
   - `health_check() -> Result<()>`

4. **Add error handling** (P1.1.4 — 1 hour)
   - Custom error enum (SupremoryError)
   - HTTP status mapping (401, 403, 404, 429, 500)
   - Serialization/deserialization errors

5. **Unit tests** (P1.1.5 — 1-2 hours)
   - Mock HTTP responses using mockito
   - Test successful operations (store, retrieve, search)
   - Test error conditions (auth, network, invalid input)
   - Test serde round-trips

**Dependencies**: None (greenfield)

**Success Metrics**:
- `cargo build` passes with 0 warnings
- `cargo test` passes all tests (>80% coverage target)
- No unsafe code
- Docs comments on public types/methods

---

### P1.2: L1/L2 Cache Infrastructure (Python) — 3-4 days

**Deliverables**:
- `src/thegent/memory/cache_l1.py` (in-memory LRU, fast access)
- `src/thegent/memory/cache_l2.py` (SQLite persistent cache)
- `src/thegent/memory/cache_manager.py` (unified L1/L2 interface)
- `src/thegent/memory/types.py` (cache entry types, TTL, metadata)
- Tests: unit tests for both layers, integration tests

**Key Tasks**:

1. **L1 Cache (In-Memory)** (P1.2.1 — 1 hour)
   - Use `cachetools.LRUCache(maxsize=1000)`
   - Store: embeddings, metadata, session contexts
   - TTL support: entries expire after N seconds
   - Methods: `get(key) -> Optional[CacheEntry]`, `put(key, value)`, `invalidate(key)`
   - Thread-safe with locks

2. **L2 Cache (SQLite)** (P1.2.2 — 1-2 hours)
   - Schema:
     ```sql
     CREATE TABLE cache_entries (
       key TEXT PRIMARY KEY,
       embedding BLOB,  -- gzip'd JSON
       metadata JSON,
       session_id TEXT,
       created_at TIMESTAMP,
       expires_at TIMESTAMP,
       accessed_at TIMESTAMP
     );
     ```
   - Methods: `get()`, `put()`, `delete()`, `cleanup()` (TTL eviction)
   - Connection pooling (sqlite3 thread-safe usage)
   - Automatic schema creation

3. **Cache Manager** (P1.2.3 — 1-2 hours)
   - L1 hits first (fast path)
   - L1 miss → L2 check (promote back to L1)
   - L2 miss → callback to fetch from Supermemory.ai
   - Lazy eviction: on access, check TTL

4. **Integration Tests** (P1.2.4 — 1 hour)
   - Test L1 hit, L1 miss/L2 hit, double miss scenarios
   - Verify TTL eviction
   - Test concurrent access
   - Measure hit rate / latency improvements

**Dependencies**: cachetools, sqlite3 (stdlib)

**Success Metrics**:
- `pytest tests/memory/test_cache*.py` passes (>80% coverage)
- L1 hit latency < 1ms
- L2 hit latency < 10ms
- TTL eviction verified

---

### P1.3: Configuration & Integration Tests — 2-3 days

**Deliverables**:
- `src/thegent/memory/config.py` (Pydantic settings, env loading)
- `src/thegent/memory/adapter.py` (thin wrapper for thegent integration)
- `.env.example` with all required keys
- `tests/memory/test_integration_supermemory.py` (live sandbox tests)
- Quick-start guide: `docs/guides/SUPERMEMORY_QUICKSTART.md`

**Key Tasks**:

1. **Configuration** (P1.3.1 — 30 min)
   - Pydantic `SupremoryConfig`:
     - `api_key` (required, from env `SUPERMEMORY_API_KEY`)
     - `base_url` (default: `https://api.supermemory.ai`, overridable)
     - `cache_max_size` (L1 maxsize, default 1000)
     - `cache_ttl` (seconds, default 3600)
     - `db_path` (L2 SQLite, default `~/.cache/thegent/supermemory.db`)
   - Settings class with validation

2. **Adapter Integration** (P1.3.2 — 1 hour)
   - Thin layer: `SupremoryMemoryAdapter`
   - Methods: `store()`, `retrieve()`, `search()`, `invalidate()`
   - Wraps Rust client + Python cache
   - Exposes via `orchestration/memory.py` interface

3. **Integration Tests** (P1.3.3 — 1 hour)
   - Set up test Supermemory.ai sandbox account
   - Test store → cache (L1 + L2)
   - Test retrieve (via cache)
   - Test search (full-text queries)
   - Error handling: invalid keys, network timeouts

4. **Documentation** (P1.3.4 — 1 hour)
   - Quick-start: Install + configure + first memory store/retrieve
   - Architecture diagram (L1/L2/Supermemory.ai layers)
   - API reference (adapter methods)
   - Troubleshooting (common errors, sandbox setup)

**Dependencies**: pydantic, live Supermemory.ai sandbox (free tier)

**Success Metrics**:
- Config loads from env and validates correctly
- Integration tests pass against live sandbox
- Documentation is clear and complete

---

## Implementation Sequence

### Day 1: Scaffolding (P1.1.1 + P1.2.1)
- [ ] Scaffold `crates/supermemory-rs` Cargo project (30 min)
- [ ] Scaffold L1 cache module (30 min)
- **Parallel work possible**: Independent Rust/Python tasks

### Day 2: Core Implementation (P1.1.2–P1.1.3 + P1.2.2)
- [ ] Define Rust client types + HTTP client methods (2-3 hours)
- [ ] Implement L2 SQLite cache with schema (1-2 hours)
- **Checkpoint**: Both compile without errors

### Day 3: Testing + Error Handling (P1.1.4–P1.1.5 + P1.2.3)
- [ ] Add error handling (Rust) (1 hour)
- [ ] Unit tests (Rust) (1-2 hours)
- [ ] Cache integration tests (Python) (1 hour)
- **Checkpoint**: All tests pass

### Day 4: Integration + Config (P1.3.1–P1.3.2)
- [ ] Configuration layer (30 min)
- [ ] Adapter integration (1 hour)
- **Checkpoint**: Adapter can call Rust client through Python

### Day 5: Final Testing + Docs (P1.3.3–P1.3.4)
- [ ] Integration tests (live sandbox) (1 hour)
- [ ] Documentation + quick-start (1 hour)
- **Final Checkpoint**: Phase 1 complete + documented

---

## Work Breakdown Structure (WBS)

| Task ID | Title | Deliverable | Est. Time | Depends |
|---------|-------|-------------|-----------|---------|
| P1.1.1 | Scaffold Cargo project | Cargo.toml + lib.rs | 30 min | — |
| P1.1.2 | Define client types | types.rs + serde | 1-2 h | P1.1.1 |
| P1.1.3 | Implement client methods | client.rs + memory.rs | 2-3 h | P1.1.2 |
| P1.1.4 | Error handling | error.rs | 1 h | P1.1.3 |
| P1.1.5 | Unit tests | test_*.rs | 1-2 h | P1.1.4 |
| P1.2.1 | L1 cache (LRU) | cache_l1.py | 1 h | — |
| P1.2.2 | L2 cache (SQLite) | cache_l2.py | 1-2 h | — |
| P1.2.3 | Cache manager | cache_manager.py | 1-2 h | P1.2.1, P1.2.2 |
| P1.2.4 | Integration tests | test_cache*.py | 1 h | P1.2.3 |
| P1.3.1 | Configuration | config.py | 30 min | — |
| P1.3.2 | Adapter integration | adapter.py | 1 h | P1.1.5, P1.2.4 |
| P1.3.3 | Integration tests (live) | test_integration*.py | 1 h | P1.3.1, P1.3.2 |
| P1.3.4 | Documentation | SUPERMEMORY_QUICKSTART.md | 1 h | P1.3.3 |

**Total**: ~13–15 hours wall-clock (9–12 days with daily sprints)

---

## Parallelization Strategy

**Independent Work Packages** (can run in parallel):

1. **P1.1** (Rust client) — entirely independent
   - Can be built and tested without Python
   - Single owner recommended

2. **P1.2** (L1/L2 cache) — entirely independent
   - Can be built and tested without Rust
   - Single owner recommended

3. **P1.3** (Config + integration) — depends on P1.1 + P1.2
   - Can start scaffolding (config) early
   - Full integration tests require both P1.1 and P1.2

**Recommended team structure** (if multi-agent):
- **Agent 1**: P1.1 (Rust) — 4-5 days
- **Agent 2**: P1.2 (Python) — 3-4 days (can start immediately)
- **Agent 3**: P1.3 (Config + integration) — 2-3 days (starts after P1.1 + P1.2 checkpoints)

**Single-agent approach**: Sequential: P1.1 → P1.2 → P1.3 (total ~9 days)

---

## High-Impact First Tasks (Start Now)

### Task A: Scaffold Supermemory Rust Client (P1.1.1)
**Effort**: 30 min
**Impact**: Unblocks all P1.1 work; gives team a buildable project
**Completeness criteria**:
- [ ] `crates/supermemory-rs/Cargo.toml` created with all deps
- [ ] `crates/supermemory-rs/src/lib.rs` with module structure
- [ ] `cargo build` passes with 0 errors

**Do this now**: Immediate win, sets up foundation.

---

### Task B: Define Rust Client Types (P1.1.2)
**Effort**: 1-2 hours
**Impact**: Unblocks P1.1.3 (implementation); provides API contract
**Completeness criteria**:
- [ ] `types.rs` with SupremoryClient, MemoryOperation, MemoryQuery, MemoryResponse
- [ ] Full serde derives, doc comments
- [ ] No compilation errors
- [ ] Unit tests for type serialization pass

**Do this next**: Flows naturally from P1.1.1; enables rest of client work.

---

### Task C: Scaffold Python Cache Modules (P1.2.1 + P1.2.2)
**Effort**: 1-2 hours (parallel with P1.1)
**Impact**: Unblocks all P1.2 work; independent from Rust
**Completeness criteria**:
- [ ] `cache_l1.py` with LRUCache wrapper, thread-safe
- [ ] `cache_l2.py` with SQLite schema + basic get/put
- [ ] Both modules importable without errors
- [ ] Unit tests for basic operations pass

**Do this in parallel**: Doesn't depend on Rust work.

---

## Definition of Done (Phase 1 Complete)

- [ ] P1.1.1–P1.1.5 all tasks completed; Rust code compiles + passes tests
- [ ] P1.2.1–P1.2.4 all tasks completed; Python cache tested
- [ ] P1.3.1–P1.3.4 all tasks completed; integration tests pass against Supermemory.ai sandbox
- [ ] Documentation: quick-start guide + API reference complete
- [ ] All code reviewed for safety (no panics/unwraps in production paths)
- [ ] Coverage: >80% for all modules
- [ ] Zero high-severity issues from linters (ruff, clippy)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Supermemory.ai API changes | High | Use versioned SDK; pin API version in tests; sandbox account for early testing |
| SQLite schema migrations | Medium | Script schema creation; test with fresh DB on each run; store schema version |
| L1/L2 cache coherence | Medium | Timestamp-based invalidation; test concurrent access; short TTLs during dev |
| Rust/Python bridge issues | Medium | Mock both sides independently first; defer FFI until after unit tests pass |
| Configuration complexity | Low | Use Pydantic validation; provide `.env.example`; clear docs |

---

## Next Steps (Session End)

1. **Immediately start Task A** (Scaffold Rust client) — 30 min, unblocks everything
2. **Immediately start Task B** (Define types) — 1-2 hours, follows naturally
3. **In parallel, start Task C** (Cache scaffolding) — can't be blocked
4. **End of day**: Check P1.1.1 + P1.1.2 + P1.2.1 + P1.2.2 compiled; move to P1.1.3

---

## Success Metrics (Phase 1 Close)

- [ ] `cargo build` passes for supermemory-rs; `cargo test` all green
- [ ] `pytest tests/memory/` passes with >80% coverage
- [ ] Integration tests against Supermemory.ai sandbox succeed
- [ ] Documentation complete and reviewed
- [ ] All work items moved from BACKLOG → COMPLETED in WORK_STREAM.md

