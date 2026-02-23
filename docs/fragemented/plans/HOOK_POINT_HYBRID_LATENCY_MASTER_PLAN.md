# Hook Point Hybrid Latency Master Plan

## Objective
Deliver a hybrid hook runtime that combines:
- near-instant interactive responsiveness for high-frequency hook points,
- minimal functional regressions for governance and safety,
- bounded worst-case latencies via hard budgets and deterministic degradation.

Primary target envelope:
- Lane `instant`: <=100ms combined per hook point in all conditions where lane is selected.
- Lane `fast-safe`: <=1.5s p99, <=5s hard cap.
- Lane `full`: exhaustive checks, primarily async; optionally blocking by policy.

## Non-Goals
- No claim that full governance/security/test scans can complete in <=100ms in-band.
- No silent reduction in critical policy coverage.

## Hybrid Lane Model

### Lane A: instant
Purpose: maximal responsiveness for chatty hook points.

Rules:
- no subprocess spawning,
- no shell-script execution,
- no network calls,
- no tree-wide scans,
- no heavyweight parsers initialized cold.

Allowed checks:
- in-memory prompt/guard patterns,
- low-cost policy checks over pre-indexed delta metadata,
- immediate blocklist checks,
- enqueue async checks with idempotency key.

Budget:
- hard stop at 100ms,
- deterministic degrade behavior at 60ms and 85ms checkpoints.

### Lane B: fast-safe
Purpose: preserve core safety with low-latency UX.

Rules:
- bounded shell/native calls only,
- strict timeout envelope,
- reduced check scope to changed artifacts and precomputed indexes.

Allowed checks:
- stop reconcile,
- critical write-time guards,
- lightweight lint/security probes on changed files only.

Budget:
- target <=1.5s p99, hard cap <=5s.

### Lane C: full
Purpose: full governance and quality certainty.

Rules:
- complete checks: quality gate, security pipeline, spec verification, complexity, test maturity,
- can run asynchronously by default,
- can run blocking for high-risk paths (release/merge/prod).

Budget:
- not constrained to interactive envelope; constrained by explicit mode and policy.

## Hook Point Routing Strategy
For each hook point, select lane by risk, frequency, and intent:

- PromptSubmit: instant by default; fast-safe if sensitive triggers fire.
- PreToolUse Write/Edit: fast-safe by default; instant for low-risk operations with no write-content risk flags.
- PostToolUse: instant by default.
- Stop: fast-safe by default (or instant-reconcile where acceptable), full async always enqueued.
- SessionStart: instant (cache attach/prewarm only).
- TaskCompleted/SubagentStop: instant or fast-safe depending on task criticality.

Escalate to full blocking when:
- release/merge gates,
- security-sensitive files changed,
- dependency/infra manifests changed,
- repeated async critical findings,
- policy override requiring strict mode.

## No-Regression Coverage Contract
- Coverage is preserved by moving heavy checks from sync to async with enforced follow-up policy.
- Critical async findings produce one of:
  - block-next-risky-action,
  - require acknowledgment token,
  - auto-escalate lane for subsequent hook points.

No silent drops:
- every skipped/deferred check emits an artifact with reason and queue ID.
- full-check debt visible in dashboards and CLI status.

## Runtime Architecture

### Sync engine (lane A/B)
- single native dispatcher path,
- in-memory rule engine and hot config generation,
- deadline-aware scheduler with partial evaluation cutoffs,
- bounded lock strategy and low-allocation hot path.

### Async engine (lane C)
- durable queue with priority classes:
  - P1: security-critical,
  - P2: quality/spec,
  - P3: advisory/reporting.
- worker pool with admission control and coalescing.

### State and data
- incremental changed-file index,
- precomputed file classification,
- cache generations keyed by head + config fingerprint,
- async artifact ledger for enforcement and audit.

## SLOs and Error Budgets

Interactive SLOs:
- instant lane: p99 <=100ms, max <=100ms in certified scenarios.
- fast-safe lane: p99 <=1.5s, max <=5s.

Correctness SLOs:
- zero missed critical findings across sync+async combined coverage.
- async critical finding to enforcement latency <=60s (configurable).

## Implementation Plan (Phased WBS + DAG)

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| P0 | P0.1 | Finalize lane contract, budgets, and enforcement semantics | - |
| P0 | P0.2 | Define check inventory and lane assignment matrix | P0.1 |
| P1 | P1.1 | Instrument end-to-end timing by hook point and segment | P0.1 |
| P1 | P1.2 | Add p50/p95/p99/max telemetry + tracing IDs | P1.1 |
| P2 | P2.1 | Implement lane router with risk classifier | P0.2 |
| P2 | P2.2 | Enforce hard budgets with deadline checkpoints | P2.1 |
| P3 | P3.1 | Build async full-check queue and worker pool | P1.2 |
| P3 | P3.2 | Move heavy checks from sync to async lane C | P3.1 |
| P3 | P3.3 | Add async result enforcement (block/ack/escalate) | P3.2 |
| P4 | P4.1 | Optimize sync hot path (no spawn, warm caches, lock minimization) | P2.2 |
| P4 | P4.2 | Add admission control and coalescing for async jobs | P3.1 |
| P5 | P5.1 | Build perf/correctness regression suite + chaos scenarios | P3.3 |
| P5 | P5.2 | Add CI perf gates and policy compliance checks | P5.1 |
| P6 | P6.1 | Shadow rollout (measure-only) | P5.2 |
| P6 | P6.2 | Controlled enforcement rollout by repo/profile | P6.1 |
| P6 | P6.3 | Default-on hybrid mode with escape hatches | P6.2 |

## Mode Profiles
- `instant`: A only, no full blocking, full async required.
- `interactive` (default): A/B sync + C async.
- `strict`: B sync + C blocking for selected points.
- `release`: C blocking mandatory.

## Key Risks and Mitigations
- Risk: hidden regressions from async shift.
  - Mitigation: mandatory async artifacts + block-next enforcement.
- Risk: queue backlog delays security action.
  - Mitigation: P1 priority + queue SLO alerts + forced strict fallback.
- Risk: operator confusion from mixed modes.
  - Mitigation: explicit lane + reason in every hook summary.

## Success Criteria
- Interactive hook points meet latency SLOs.
- Full governance checks still run and enforce policy.
- No net increase in escaped critical defects.
- Operators can switch modes predictably with clear telemetry.

## Research-Backed Principles (to be expanded)
- Tail latency management and variance control.
- Load shedding and graceful degradation.
- Fairness/admission control under overload.
- Bounded retries, backoff, and jitter for async workers.
