# Architecture Decision Records (ADR)

This document tracks the "Why" behind the core architectural shifts in `thegent`.

---

## ADR-001: Model-First Task Routing
- **Context**: Agent tasks were previously tied to hardcoded models or providers.
- **Decision**: All task execution now goes through a `TaskRouter` that resolves `model_id` → `provider_id` → `model_alias` based on cost, quality, and speed benchmarks (Terminal Bench 2.0).
- **Status**: **ACCEPTED**
- **Consequence**: Execution layer must now accept `TaskMetadata` instead of just a model string.

## ADR-002: Multi-Tenant Single Process (MTSP)
- **Context**: High resource usage from N×LSP and N×MCP subprocesses.
- **Decision**: Consolidate short-lived tools into persistent background daemons managed by `process-compose`. Use HTTP/SSE multiplexing instead of `uvx` shell-outs.
- **Status**: **ACCEPTED**
- **Consequence**: `thegent serve` becomes the mandatory foundation for all interactive sessions.

## ADR-003: 4-Tier Memory with Supermemory.ai
- **Context**: L3/L4 memory was limited to local file system, leading to knowledge silos.
- **Decision**: Adopt Supermemory.ai as the L3 (Knowledge Graph) and L4 (Archival) provider.
- **Status**: **ACCEPTED**
- **Consequence**: Cross-project knowledge sharing is now possible; L3 persistence no longer depends on local `.thegent` folders.

## ADR-004: Unified Cross-Platform Protocol (HAX)
- **Context**: Claude Code, Codex, and Cursor have incompatible hooks and syntaxes ($defer, rules).
- **Decision**: Unify on a single syntax and storage backend (`.thegent/`). The `thegent` wrapper handles translation for each platform.
- **Status**: **ACCEPTED**
- **Consequence**: Unified `$defer`, `$block`, and `$idea` syntax works across all 6+ supported platforms.

## ADR-005: Hash-Chained Immutable Audit Trail (Superseded by ADR-015)
- **Context**: Agent actions must be tamper-evident for governance compliance and forensic replay.
- **Decision**: Hash-chained append-only logs with tiered storage (hot → warm → cold).
- **Status**: **SUPERSEDED** by ADR-015 (Immutable Audit Ledger)
- **Consequence**: See ADR-015 for current implementation.

## ADR-006: Three-State Circuit Breaker per Subsystem
- **Context**: Subsystem failures could cascade across the entire agent orchestration system.
- **Decision**: Implement CLOSED → OPEN (on failure threshold) → HALF-OPEN (probe) → CLOSED/OPEN circuit breaker pattern, per-provider and per-subsystem (model, tool, storage).
- **Status**: **ACCEPTED**
- **Consequence**: Prevents cascade failures; enables graceful degradation. Each subsystem has independent circuit breaker state.

## ADR-007: Multi-Agent Orchestration Modes
- **Context**: Different tasks require different coordination patterns; single mode insufficient.
- **Decision**: Support Sequential Delegation, Parallel Consensus, Review Loop, Arbitration Quorum, and Solo modes. Mode selection based on risk/complexity classification with conflict resolution via majority vote + confidence weighting.
- **Status**: **ACCEPTED**
- **Consequence**: FR-AGT-013 defines execution modes. `get_mode_capability()` and `list_modes()` provide runtime mode selection.

## ADR-015: Immutable Audit Ledger
- **Context**: Agent actions must be tamper-evident for governance compliance and forensic replay. Plain JSONL files are mutable and undetectably alterable.
- **Decision**: All audit records are stored in append-only JSONL files with SHA-256 hash chaining. Each entry contains `prev_hash` (hash of the previous record) and `hash` (hash of the current record), forming a cryptographically linked chain. `EvidenceLedger` is the canonical implementation; `IncidentLedger` applies the same pattern for governance/omega-safety events.
- **Status**: **ACCEPTED**
- **Consequence**: Tampering is detectable via `verify_chain()` in O(n) time. No database or external service dependency. No concurrent-writer safety (single writer per session dir). Full detail: [ADR-015-immutable-audit-ledger.md](./docs/reference/ADR-015-immutable-audit-ledger.md)

## ADR-016: Two Python Surfaces (Core Runtime vs Tooling/Test)
- **Context**: WL-120/WL-136 identified mixed-purpose Python surfaces that increased runtime coupling and slowed decomposition progress.
- **Decision**: Ratify two explicit Python surfaces and require command domains to import extracted implementation modules directly (for example, `dag_impl.py`, `work_stream_impl.py`) instead of routing through `impl.py` where extraction exists.
- **Status**: **ACCEPTED**
- **Consequence**: Core/runtime paths can be measured and reduced independently, while tooling/test surfaces remain isolated from fast-lane runtime checks. Full detail: [ADR-016-two-python-surfaces.md](./docs/reference/ADR-016-two-python-surfaces.md)

## ADR-017: Unified Quality Control Plane (GitHub SARIF-Native First)
- **Context**: Unified quality work introduced multiple new checkers and hook artifacts, but no explicit long-term control-plane choice existed between Sonar-backed hybrid vs GitHub-native SARIF.
- **Decision**: Adopt **GitHub+SARIF-native** as the default control plane for 2026 rollout, with optional Sonar bridge as a non-default adapter.
- **Status**: **ACCEPTED**
- **Consequence**: All quality/security/perf checkers must emit machine-readable artifacts (JSON and/or SARIF), and CI policy decisions are derived from contract-backed artifacts. Full detail: [ADR-017-unified-quality-control-plane.md](./docs/reference/ADR-017-unified-quality-control-plane.md)

---
*Cross-ref: [ARCHITECTURE.md](./docs/plans/05-ARCHITECTURE.md)*
