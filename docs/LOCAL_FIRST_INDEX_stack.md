# Local-First Stack Index

**Status:** Active consolidation
**Purpose:** Canonical local-first summary for messaging, cache, graph, object storage, and orchestration choices.
**Source pointers:** Consolidated from the stack recommendation material in
`docs/reports/cli-libraries-2026/06_rolling-recommendations.md` and
`docs/reports/rust-cli-new-packages-2026/06_ops_serving_utility_cli.md`.

## Decision principle

Prefer local-first primitives until a problem clearly requires shared infrastructure.

- Keep state close to the operator or service that owns it.
- Make sync boundaries explicit and observable.
- Prefer append-only or idempotent operations where possible.
- Add remote services only when the local contract is no longer sufficient.

## 1) Messaging

### Summary

Use messaging for durable work coordination, not as a default distributed-computing layer.
In a local-first stack, messaging should remain inspectable, replayable, and easy to run from
the terminal.

### Recommended shape

- Prefer a local queue or job runner as the first implementation.
- Model messages as small, typed records with explicit ownership and retry semantics.
- Keep the producer/consumer boundary narrow so local commands can be traced end to end.
- Use a richer broker only when multiple machines or teams need to share the same event stream.

### Operational recommendation

- For command orchestration, a local queue such as `pueue` is the right baseline.
- For long-lived or cross-service messaging, keep the broker behind an adapter and retain a
  local replay path for debugging.

### Guardrails

- Define retention and replay rules up front.
- Make deduplication or idempotency explicit.
- Keep queue state visible in logs or a queryable file-backed store.

## 2) Cache layer

### Summary

Cache should accelerate local workflows, not hide correctness problems. If invalidation is hard
to reason about, the cache contract is too loose.

### Recommended shape

- Prefer a filesystem or SQLite-backed cache for local-first workflows.
- Version cache keys and include the data contract version in the key or record payload.
- Treat invalidation as part of the API, not as an implementation detail.
- Keep the cached artifact format human-inspectable when possible.

### Operational recommendation

- Use a short TTL for volatile data and explicit purge hooks for changing schemas.
- When object storage is involved, validate the cache invalidation path before broad rollout.

### Guardrails

- Do not introduce shared cache layers until the single-node contract is stable.
- Make stale-cache behavior obvious in logs and diagnostics.
- Rebuild from source data when the cache cannot be validated.

## 3) Graph database

### Summary

Use a graph database only when traversal-heavy relationships are the primary workload. For
most local-first systems, an adjacency table or relational model is simpler, faster to ship,
and easier to debug.

### Recommended shape

- Keep core records in a relational store first.
- Promote to a graph database only when path traversal, neighborhood queries, or ranking logic
  become dominant and expensive.
- Put graph access behind an adapter so the rest of the system does not depend on the engine.

### Operational recommendation

- Start with relational storage plus explicit relationship tables.
- Add a graph backend later if the query pattern justifies the extra operational surface.

### Guardrails

- Require an export path from the graph model back to relational-friendly artifacts.
- Budget for schema evolution and query plan review.
- Avoid mixing graph-specific query language into application code outside the adapter boundary.

## 4) Object storage

### Summary

Object storage is the durable artifact layer. In a local-first stack it should complement, not
replace, the working directory and should be synchronized through an explicit path.

### Recommended shape

- Keep a local working copy as the source of truth for active edits.
- Sync artifacts to object storage on a controlled schedule or event boundary.
- Use checksums, manifests, and retention rules so stored artifacts remain auditable.

### Operational recommendation

- For object storage-backed serving, use an explicit sync path and validate cache invalidation.
- Prefer object storage for snapshots, evidence bundles, and immutable artifacts rather than
  live-edit state.

### Guardrails

- Scan retained artifacts for sensitive content before long-term storage.
- Define lifecycle rules for cleanup, archival, and access control.
- Keep the local and remote artifact names stable so resyncs stay deterministic.

## 5) Local orchestration

### Summary

Local orchestration coordinates commands, jobs, and developer workflows without requiring a
full distributed scheduler. It is the control plane for a local-first stack.

### Recommended shape

- Prefer `pueue` or a comparable local queue for command execution.
- Use `systemd --user` for long-running helpers that need restart semantics.
- Keep `just`, `mise`, or similar task wrappers for deterministic entrypoints.
- Use small wrapper scripts for common flows rather than ad hoc shell history.

### Operational recommendation

- Local orchestration should expose `add`, `status`, `pause`, `resume`, and cleanup operations.
- Make it trivial to inspect the current queue, the last run, and the next action.

### Guardrails

- Avoid hidden background state.
- Keep logs and output paths explicit.
- Make cleanup and cancellation first-class operations.

## Cross-stack recommendations

1. Default to local-first primitives for each new capability.
2. Add remote services only when a local queue, local cache, relational store, or file-backed
   artifact path is no longer sufficient.
3. Treat object storage sync and cache invalidation as a single contract.
4. Keep the graph database behind an adapter until traversal-heavy queries prove the need.
5. Prefer explicit orchestration primitives over opaque background daemons.

## Roll-forward recommendation

- **Messaging:** local durable queue first, broker later.
- **Cache layer:** filesystem or SQLite cache with explicit invalidation.
- **Graph database:** relational baseline, graph backend only when traversal workload demands it.
- **Object storage:** explicit sync path, checksums, and retention rules.
- **Local orchestration:** `pueue` plus task wrappers, with `systemd --user` only where restart
  semantics are needed.

## Related references

- `docs/reports/cli-libraries-2026/06_rolling-recommendations.md`
- `docs/reports/rust-cli-new-packages-2026/06_ops_serving_utility_cli.md`
