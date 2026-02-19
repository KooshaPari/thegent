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

---
*Cross-ref: [ARCHITECTURE.md](./docs/plans/05-ARCHITECTURE.md)*
