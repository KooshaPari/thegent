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

---
*Cross-ref: [ARCHITECTURE.md](./docs/plans/05-ARCHITECTURE.md)*
