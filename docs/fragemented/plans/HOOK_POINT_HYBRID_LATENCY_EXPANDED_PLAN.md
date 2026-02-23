# Hook Point Hybrid Latency Expanded Plan

## Purpose
This document is the canonical expanded blueprint for hybrid hook execution that balances:
- ultra-low-latency interactive behavior,
- minimal-to-no functional regressions,
- robust governance and safety guarantees.

It synthesizes:
- `docs/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md`
- `docs/plans/fragments/LANE_STRATEGY_MATRIX.md`
- `docs/plans/fragments/NO_REGRESSION_ENFORCEMENT.md`
- `docs/plans/fragments/PERF_OPTIMIZATION_PLAYBOOK.md`
- `docs/plans/fragments/ROLLOUT_AND_OPERATIONS.md`

## Executive Strategy
Use a 3-lane runtime with strict profile routing:
- `instant` lane for responsiveness-critical points,
- `fast-safe` lane for bounded sync safety,
- `full` lane for exhaustive checks (primarily async, blocking when required).

Core principle: preserve outcomes by shifting expensive checks in time, not deleting them.

## Lane Options and Sub-Modes

### Lane A: instant
- `A0-guard-only`: in-memory mandatory checks only.
- `A1-guard-plus-enqueue`: guard + async full-check enqueue.
- `A2-instant-reconcile`: bounded reconcile plus full enqueue.

SLO:
- p99 <=100ms, hard cap 100ms.

### Lane B: fast-safe
- `B0-changed-scope`: changed-files bounded checks.
- `B1-critical-write`: stronger write safety checks.
- `B2-strong-gate`: temporary stronger sync gate for elevated risk.

SLO:
- p99 <=1.5s, hard cap <=5s.

### Lane C: full
- `C0-async-standard`: full checks async.
- `C1-async-priority`: full checks async with critical-first scheduling.
- `C2-blocking-release`: full checks blocking for release/strict paths.

SLO:
- correctness-driven; enforced by queue/enforcement latency objectives.

## Routing and Overrides

### Default hook point mapping
- `SessionStart`: `A1`.
- `PromptSubmit`: `A1` (escalate on risk).
- `PreToolUse Write/Edit`: `B1`.
- `PreToolUse non-write`: `A0`.
- `PostToolUse`: `A0`.
- `TaskCompleted`, `SubagentStop`: `A2`.
- `Stop`: `B0` sync + `C0` async always.

### Escalation triggers
- protected files/security domains changed,
- dependency/infra manifests changed,
- unresolved critical finding,
- async queue health degradation,
- strict/release profile.

### De-escalation triggers
- warm caches and healthy queue,
- no unresolved debt,
- low-risk delta and low-risk action class.

### Override precedence
1. hard policy profile (`release`, `strict`, fail-closed states),
2. active critical enforcement state,
3. explicit operator override,
4. default mapping,
5. adaptive optimization heuristics.

## Deterministic Degradation Model

Stages:
- `D0`: no degradation.
- `D1`: drop advisory sync checks.
- `D2`: mandatory-only sync path, defer rest.
- `D3`: hard cap reached; fail closed or deterministic defer with enforcement.

Invariants:
- no silent skip,
- every defer emits artifact + reason + queue ID,
- mandatory policy checks never dropped,
- every terminal async outcome is recorded.

## No-Regression Enforcement

### Artifact contract
Required artifact types:
- `check.deferred`, `check.started`, `check.result`,
- `enforcement.applied`, `ack.issued`, `ack.used`,
- `exception.granted`, `exception.expired`,
- `system.degraded`.

### Block-next policy
- critical async findings can block next risky action classes.
- read-only actions remain available.
- lift conditions are explicit and auditable.

### Acknowledgment flow
- role-scoped, time-bound, finding-scoped ack tokens.
- single-use by default.
- auto-revoke on superseding critical findings.

### Exception policy
- explicit, timeboxed, scoped, and auditable only.
- missing required fields -> invalid.
- expired exception -> immediately ineffective.

### Enforcement latency objective
- async critical finding to active enforcement <=60s.

## Performance and Optimization Strategy

### Hot path rules
- no subprocess/shell/network in `instant`.
- bounded, allowlisted checks in `fast-safe`.
- heavy checks only in `full`.

### Budget partitioning (reference)
- `instant`: route(10ms) + checks(45ms) + state(15ms) + serialize(10ms) + guard band(20ms).
- `fast-safe`: route(80ms) + checks(900ms) + state(220ms) + serialize(120ms) + guard band(180ms).

### Queue/admission
- priority queues `P1/P2/P3`,
- coalescing by repo/checkset fingerprint,
- backpressure and shedding from `P3` upward,
- fail-closed escalation when `P1` backlog age breaches threshold.

### Cache strategy
- `L1` in-process hot policy/routing cache,
- `L2` local persistent metadata cache,
- `L3` immutable audit/enforcement ledger.

### Contention controls
- snapshot-and-swap for read-heavy data,
- lock sharding by repo and data class,
- no locks across I/O,
- lock wait SLOs tracked and gated.

## Rollout and Operations

### Phased rollout
- R0 baseline and rollback drills,
- R1 shadow routing,
- R2 canary with limited enforcement,
- R3 progressive expansion,
- R4 default interactive profile,
- R5 hardening and optimization.

### Kill switches
- global hybrid enable/disable,
- instant-lane disable,
- async-enforcement disable,
- force-profile pinning (`fast`/`release`),
- strict fail-closed mode.

### Incident model
- SEV-1 correctness risk: rollback first,
- SEV-2 latency breach: disable instant lane,
- SEV-3 local degradation: freeze rollout and tune.

### Exit criteria per phase
- latency SLOs green for two windows,
- no increase in escaped critical defects,
- enforcement latency objective met,
- rollback drills passing.

## Research-Backed Design Inputs

1. Tail latency dominates user-perceived responsiveness at scale:
- Dean, Barroso, “The Tail at Scale”
- https://cacm.acm.org/research/the-tail-at-scale/

2. Cascading failures and overload mitigation with load shedding, graceful degradation, and backoff/jitter:
- Google SRE, Addressing Cascading Failures
- https://sre.google/sre-book/addressing-cascading-failures/

3. Overload management as an explicit operational discipline:
- Google SRE Workbook, Operational Overload
- https://sre.google/workbook/overload/

4. Practical overload control and goodput-centric behavior in production services:
- AWS Builders’ Library, Using load shedding to avoid overload
- https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/

5. Scale mismatch and controlling call pace from smaller control planes:
- AWS Builders’ Library, putting the smaller service in control
- https://aws.amazon.com/builders-library/avoiding-overload-in-distributed-systems-by-putting-the-smaller-service-in-control/

6. Deadline and timeout discipline:
- gRPC Deadlines Guide
- https://grpc.io/docs/guides/deadlines/
- AWS Well-Architected timeout best practice
- https://docs.aws.amazon.com/wellarchitected/2022-03-31/framework/rel_mitigate_interaction_failure_client_timeouts.html

7. Adaptive timeout scaling under load:
- Envoy timeout and overload-manager docs
- https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts.html

## Implementation DAG (condensed)

| Phase | Task | Depends On |
|---|---|---|
| P0 | finalize lane contracts, enforcement semantics, risk model | - |
| P1 | instrumentation and baseline telemetry | P0 |
| P2 | lane router + budget checkpoints + degrade engine | P1 |
| P3 | async queue + artifact ledger + enforcement engine | P2 |
| P4 | hot-path optimization + cache/lock tuning | P2, P3 |
| P5 | CI perf/correctness gates + chaos/perf suites | P3, P4 |
| P6 | shadow rollout -> canary -> progressive -> default | P5 |

## Immediate Next Actions (recommended)
1. Keep `fast` profile as default interactive baseline while hybrid routing ships.
2. Implement lane router and artifact contracts first (minimal behavior risk).
3. Enable shadow mode and compare decisions before enforcement activation.
4. Turn on `P1` async enforcement in canary only.
5. Promote by objective metrics, not fixed dates.
