# ADR-006: Deployment Topology, Multi-Region, and Data Residency

**Status**: Proposed (pending review) — 2026-06-08

## Context

Thegent is a federated agent orchestration platform in the Phenotype ecosystem. Production deployment must address availability, durability, latency, and regulatory constraints:

- **Availability**: Operator workflows cannot tolerate extended downtime
- **Latency**: Interactive agent dispatches need sub-second response in primary regions
- **Durability**: Configuration and audit state must survive regional failures
- **Compliance**: User data may be subject to residency requirements (GDPR, CCPA)
- **Cost**: Egress and idle regional capacity must be bounded

Forces: native services preferred; single primary region `us-east-1`; read-only secondary `eu-west-1`; active-passive failover with manual promotion; stateful stores colocated with compute in primary region.

---

## Decision

### Topology

Single primary (`us-east-1`) with warm-standby secondary (`eu-west-1`). Stateless services run as containers behind a regional load balancer. Stateful stores stay in the primary region with async cross-region replication for durability. The standby drains writes until promoted.

### RTO and RPO

Stateless API: RTO 60s, RPO 0 (redeploy from image). State writes: RTO 5 min, RPO 15s (async WAL streaming). Object store: RTO 10 min, RPO 1 min (versioned buckets). Audit chain: RTO 15 min, RPO 30s (replicated append-only).

### Data Residency

User-identifying data and audit records stay in the region of origin. Cross-region replication carries administrative metadata only (schema, configuration). A `residency:strict` tag on workspaces disables replication entirely; these workspaces are pinned to their home region with no failover path.

---

## Consequences

**Positive**: Bounded cost, simple operational model, clear residency boundaries.
**Negative**: Manual failover requires runbook discipline; cross-region latency for replicated state.
**Mitigations**: Quarterly failover drills; ChaosDay exercises.

---

## Alternatives Considered

- **Active-Active Multi-Region**: Rejected — write conflicts and cost outweigh benefits at current scale.
- **Single-Region Only**: Rejected — does not meet RTO for stateful tier.
- **Edge Connectors**: Deferred — viable later, out of scope for v1.

---

## Related

- [ADR-001](./ADR-001-architecture-overview.md), [ADR-003](./ADR-003-data-persistence.md)
- SRE Book (DR); AWS Well-Architected (Reliability); GDPR Art. 44

Changelog: 2026-06-08 — initial draft (Platform Team).
