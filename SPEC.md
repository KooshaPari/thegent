# thegent Specification

> Procurement workflow platform — agent-driven intake, routing, and approval.

## Scope

thegent is a procurement workflow platform: structured request intake, policy-driven routing, multi-stage approval, and auditable fulfillment. The agent layer orchestrates these workflows; humans approve at policy-defined gates. Scope covers request lifecycle (intake → validation → routing → approval → fulfillment → audit) and excludes payment execution, supplier onboarding, and ERP write-back (deferred to v2).

## ADR Summary (5)

| ID | Title | Status | Decision |
|----|-------|--------|----------|
| [ADR-001](docs/specs/argisroute/adr/ADR-001-architecture-overview.md) | Architecture Overview | Accepted | Layered modular (presentation / application / domain / infrastructure), hexagonal ports, event-driven inter-module. |
| [ADR-002](docs/specs/argisroute/adr/ADR-002-technology-stack.md) | Technology Stack | Accepted | Polyglot aligned with Phenotype ecosystem; sub-100ms p99, 10k+ concurrent, 99.9% SLA. |
| [ADR-003](docs/specs/argisroute/adr/ADR-003-data-persistence.md) | Data Persistence | Accepted | Polyglot persistence: relational for transactional state, document/append-only for audit, cache for hot reads. |
| [ADR-004](docs/specs/argisroute/adr/ADR-004-error-handling.md) | Error Handling | Accepted | Classify by origin/severity/recoverability; explicit failure surfaces, no silent degradation. |
| [ADR-005](docs/specs/argisroute/adr/ADR-005-integration-api.md) | Integration & API | Accepted | Versioned APIs, event streams, webhooks, multi-language SDKs; observable by default. |

## Deployment Topology

See [ADR-006](docs/specs/argisroute/adr/006-deployment-topology.md). Single primary (`us-east-1`) + warm-standby (`eu-west-1`); stateless APIs as containers behind regional LBs; stateful stores colocated in primary with async cross-region replication. RTO 60s stateless / 5min stateful; RPO 15s writes, 30s audit. `residency:strict` workspaces pin to home region.

## Health Endpoints

`apps/landing/src/pages/health.json.ts` exposes `GET /health.json` returning `{status:"ok", version}` (200, `must-revalidate`). Single canonical route per service tier; see worklog gap on per-service `/health` coverage.

## Key Invariants

- Approvals are explicit human gates — never auto-bypass.
- Audit chain is append-only and replicated.
- Required dependencies fail loud, not silent.
- Workflow state transitions are versioned and replayable.

## Top Gaps

- `apps/api/` is intentionally deferred; only `apps/landing/` and `apps/byteport/` exist.
- `/health.json` exists for landing only; BytePort already owns `/api/v1/health`, and other service-tier crates still lack health routes.
- `release-drafter.yml` workflow missing.
- ADR-006 still Proposed, not Accepted.
