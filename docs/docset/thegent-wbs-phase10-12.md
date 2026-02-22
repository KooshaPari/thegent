# Thegent WBS — Phase 10 to Phase 12 (Optimization-Depth and Productization)

**Status:** Finalized execution-ready WBS
**Date:** 2026-02-15
**Scope:** Operational convergence, predictive resilience, and enterprise hardening after closure of Phases 7–9.

## 0) Meta constraints

- Entry criteria:
  - Phase 9 gate (`M9`) achieved.
  - All Phase 10 pre-read evidence packages available and signed.
- Exit criteria:
  - Every WP in Phase 10–12 has deterministic tests and explicit evidence artifacts.
  - All Gates G10/G11/G12 passed in canary and one production shadow.
- Rollback policy:
  - Each WP in Phase 10 and 11 must define a "disable by gate/version" rollback path.
  - All rollback procedures must execute in < 2 min or keep system in safe mode with explicit operator confirmation.

### 0.1 Delivery assumptions

- Teams are expected to work in two-week pods with explicit phase owners.
- Feature flags are required for all phase transitions:
  - `phase10.interface_v2`
  - `phase11.autotune`
  - `phase12.hardening`
- Every WP requires at least one artifact under `artifacts/phase10`, `artifacts/phase11`, or `artifacts/phase12`.

## 1) Phase 10 Work Packages (Adaptive Interface and Ecosystem Convergence)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-10001 | Operation envelope schema v2 | 4d | Platform lead | WP-9001 | Unified `operation_envelope_v2` schema and schema docs | Envelope validates across CLI and MCP with consistent errors |
| WP-10002 | Capability registry service | 3d | Platform lead | WP-10001 | Central registry with health + trust + version metadata | Registry responds under 60ms p95 and blocks unsupported capability combos |
| WP-10003 | Dispatch graph implementation | 6d | Core runtime | WP-10001, WP-10002 | Deterministic dispatch resolver + policy-aware routing path | Same input yields same resolved path across 100 reruns |
| WP-10004 | Adapter admission and trust policy | 5d | Security/Governance | WP-10002 | Adapter manifest, trust score evaluation, denylist behavior | Low-trust adapters prevented from critical lane without approval |
| WP-10005 | Endpoint consolidation and aliases | 4d | Platform lead | WP-10003 | CLI/MCP operation enum completion and alias parity | No divergence in supported operations between CLI and MCP |
| WP-10006 | Unknown-operation migration UX | 3d | UX + Core runtime | WP-10003 | Suggestion engine for unsupported or renamed operations | Every unsupported operation returns actionable migration path |
| WP-10007 | Dispatch traceability and audit context | 4d | Governance | WP-10003 | Trace fields persisted: dispatch_path, reason, policy_version | Traceability queryable and immutable |
| WP-10008 | Plugin lifecycle and conformance checks | 6d | Platform architecture | WP-10002, WP-10007 | Plugin registration lifecycle + conformance test harness | Plugin rejected/held until conformance suite passes |
| WP-10009 | Backward-compatible API evolution controls | 3d | API/Docs | WP-10001, WP-10005 | Version negotiation + compatibility matrix + migration CLI | Breaking schema changes require explicit compatibility flag |
| WP-10010 | Cross-phase operations operator documentation | 2d | Documentation | WP-10003, WP-10005 | Release-note style operation guide + CLI examples | Operators can run one command using each major operation |

### 1.1 Phase 10 gate

- **Gate G10:** Registry-first execution and dispatch determinism in canary.
- **Gate G10:** 100% unknown-op events include `suggested_operation` + migration context.
- **Gate G10:** Evidence package for WP-10001..10010 signed and linked.
### 1.2 Phase 10 control hardening

- **Control G10-1:** Dispatch parity lock before any phase 11 canary change.
- **Control G10-2:** Route hashes and policy digests required in every dispatch trace.
- **Control G10-3:** Unrecognized operations must return migration guidance and fail-open only in non-critical lanes.

## 2) Phase 11 Work Packages (Autonomous Optimization and Predictive Resilience)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-11001 | SLO regulator loop controller | 7d | SRE + Operations | WP-10003, WP-10007 | Control loop with hysteresis and anti-oscillation guard | No more than one critical-path loop transition per 10 minutes |
| WP-11002 | Forecasting engine hardening | 6d | Data/Planning | WP-11001 | p50/p80/p95 runtime forecasts + calibration tracking | Forecast quality drift ≤ threshold over 14 days |
| WP-11003 | Predictor confidence calibration | 4d | QA + Governance | WP-11002 | Calibration dashboard + threshold enforcement | Confidence miscalibration triggers controlled pause |
| WP-11004 | Preemption and saturation avoidance policies | 5d | Core routing | WP-11001, WP-11002 | Provider preemption decisions with rollback assumptions | Saturation risk reduced with bounded service impact |
| WP-11005 | Self-healing recommendation engine | 5d | Governance | WP-11003 | Top-3 ranked suggestions with confidence and expected outcomes | Recommendations include assumptions + owner + rollback |
| WP-11006 | Adaptive task shaping | 4d | Orchestration | WP-11004 | Task split/merge engine with audit trail | No task split occurs without rationale and owner trace |
| WP-11007 | Continuity risk predictor | 4d | Product + SRE | WP-11006 | Shift/freeze risk alerts + continuity pre-check scheduler | Warnings raise before continuity breaks |
| WP-11008 | Learning loop and policy guardrails | 4d | Governance | WP-11003, WP-10007 | Approved parameter update flow + rollback manifests | No auto-change without policy approval and audit |
| WP-11009 | Safe-mode action governance | 3d | Security | WP-11008 | Safe-mode policy templates and emergency revert path | Safe-mode changes require explicit owner and expire safely |
| WP-11010 | Forecast and control evidence pack | 2d | QA/Docs | WP-11001, WP-11002, WP-11005 | Evidence NDJSON + control runbooks | G11 gate evidence complete and reproducible |

### 2.1 Phase 11 gate

- **Gate G11:** Closed-loop control runs without unsafe oscillation for 7 consecutive days.
- **Gate G11:** Auto-optimization events include confidence and rollback evidence.
- **Gate G11:** FR-076..FR-082 readiness package complete and simulation-verified.
### 2.2 Phase 11 control hardening

- **Control G11-1:** Confidence < 0.75 triggers optimization pause.
- **Control G11-2:** All self-heal actions require owner-signed recommendation notes.
- **Control G11-3:** Safe-mode entry and exit must be idempotent with audit evidence.

## 3) Phase 12 Work Packages (Enterprise Intuition, Explainability, and Hardening)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-12001 | Explainability contract implementation | 6d | Product + UX | WP-11010, WP-9002 | Single `explanation_bundle` schema and renderer | Summary/detail/trace always consistent |
| WP-12002 | Escalation fatigue and noise control | 4d | SRE | WP-12001 | Fatigue score and suppression rules with override | Alert storms reduced without masking critical alerts |
| WP-12003 | Replay sandbox hardening | 5d | Core runtime | WP-12001 | Read-only-by-default replay isolation and diff engine | Mutation attempts are blocked outside execute mode |
| WP-12004 | What-if simulation and branch governance | 5d | Product + Governance | WP-12003 | Branch simulation UI/CLI and approval workflow | Operator can safely branch and compare outcomes |
| WP-12005 | Handoff confidence and continuity envelope | 4d | Governance + UX | WP-12003 | Ownership checkpoints + mandatory handoff confirmation | Continuity handoff cannot proceed without explicit confirm |
| WP-12006 | Evidence graph and export bundling | 6d | Compliance | WP-12005, WP-10007 | Evidence DAG packager with index manifest | One-command export passes checksum and schema validation |
| WP-12007 | Persona profiles and access constraints | 3d | Product + Security | WP-12005 | Persona-specific defaults + action matrix | Persona-specific restrictions enforced at policy boundary |
| WP-12008 | Operational learning assets | 3d | Documentation | WP-12007 | Runbooks, checklists, anti-fatigue coaching cards | New operator can complete onboarding drill in one session |
| WP-12009 | Automation of release docs packaging | 4d | Documentation | WP-12006, WP-12008 | PRD/WBS/test pack compile command and output | Release docs export includes all current phase artifacts |
| WP-12010 | Phase 10–12 closure and handoff note | 2d | Program lead | WP-12009 | Closure summary with signed owner approvals | Final gate M12 with complete artifact inventory |

### 3.1 Phase 12 gate

- **Gate G12:** Explainability, replay safety, evidence bundling completeness verified.
- **Gate G12:** All high-risk actions have escalation + confidence rationale.
- **Gate G12:** Release artifact export deterministic from repository state and metadata.
### 3.2 Phase 12 control hardening

- **Control G12-1:** Replay mutation attempts are blocked in read-only mode and must produce safety events.
- **Control G12-2:** Evidence graph includes continuity handoff edge for every critical run.
- **Control G12-3:** Release pack exports are deterministic with checksum + manifest verification.

## 4) Cross-phase dependencies

- `WP-10003` requires `WP-10001` and gates all Phase 11 and 12 runtime control changes.
- `WP-11001` depends on `WP-10007` to avoid blind-looping due to missing dispatch context.
- `WP-12001` depends on `WP-9002` and `WP-10007` for schema and evidence consistency.
- `WP-12006` and `WP-12009` depend on all evidence and artifact nodes in Phase 10 and 11.
- `WP-12010` closes only after G10, G11, and G12 evidence checks.

## 5) Sequencing and timeline

- Weeks 1–2: WP-10001 through WP-10005 (core interface convergence)
- Weeks 3–4: WP-10006 through WP-10010 + G10
- Weeks 5–7: WP-11001 through WP-11005
- Weeks 8–9: WP-11006 through WP-11010 + G11
- Weeks 10–11: WP-12001 through WP-12005
- Weeks 12–13: WP-12006 through WP-12010 + G12

## 6) Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Looping control behavior causes instability | Critical SLA regressions | Hysteresis, confidence floor, simulation-only rollout mode |
| Adapter ecosystem fragmentation | Inconsistent behavior across interfaces | Strong registry + adapter conformance + deny-by-default for unknown adapters |
| Explainability drift and UI/API mismatches | Operator confusion | Shared schema IDs + dual-view consistency validation |
| Replay mode abuse | Unintended state changes | Immutable read-only default + explicit execute mode and audit controls |

## 7) Ownership map

- Core runtime: `WP-10001`, `WP-10003`, `WP-11001`, `WP-11006`, `WP-12003`
- Platform/API: `WP-10002`, `WP-10004`, `WP-10005`, `WP-10007`, `WP-10009`
- SRE/Operations: `WP-11001`, `WP-11002`, `WP-11004`, `WP-11007`, `WP-11008`, `WP-12002`
- Governance/Compliance: `WP-12001`, `WP-12004`, `WP-12005`, `WP-12006`, `WP-12010`
- Product/UX: `WP-12007`, `WP-12008`, `WP-12009`

## 8) Immediate next implementation slice

1. Implement `WP-10001` and `WP-10002` (operation envelope + capability registry).
2. Add deterministic dispatch scaffolding (`WP-10003`) and unknown-op migration UX (`WP-10006`).
3. Add phase-10 acceptance checks and telemetry (`WP-10007`, `WP-10010`).
4. Deliver first forecast integration checkpoint for `WP-11001` and `WP-11002`.

## 9) Execution-ready wave matrix

| Wave | Calendar window | Primary gates | WPs |
|---|---|---|---|
| Wave A | W1–W2 | Build to dispatch parity | WP-10001, WP-10002, WP-10003 |
| Wave B | W2–W3 | G10 readiness | WP-10004, WP-10005, WP-10006, WP-10007 |
| Wave C | W3–W4 | G10 close | WP-10008, WP-10009, WP-10010 |
| Wave D | W5–W6 | Autonomous stability | WP-11001, WP-11002, WP-11003, WP-11004 |
| Wave E | W6–W7 | Self-heal + continuity controls | WP-11005, WP-11006, WP-11007, WP-11008, WP-11009 |
| Wave F | W7–W9 | Predictive evidence close | WP-11010, WP-12001, WP-12002, WP-12003 |
| Wave G | W9–W10 | Explainability and packaging | WP-12004, WP-12005, WP-12006 |
| Wave H | W10–W11 | Persona and closure | WP-12007, WP-12008, WP-12009, WP-12010 |

## 10) Artifact registry

### Phase 10
- `artifacts/phase10/dispatch_trace_schema.ndjson`
- `artifacts/phase10/compatibility_matrix.ndjson`
- `artifacts/phase10/operations_consolidation.ndjson`

### Phase 11
- `artifacts/phase11/slo_regulator_events.ndjson`
- `artifacts/phase11/forecast_quality.ndjson`
- `artifacts/phase11/self_heal_recommendations.ndjson`
- `artifacts/phase11/continuity_risk.ndjson`

### Phase 12
- `artifacts/phase12/explainability_bundle.ndjson`
- `artifacts/phase12/replay_safety.ndjson`
- `artifacts/phase12/evidence_graph.ndjson`
- `artifacts/phase12/release_pack_summary.ndjson`


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
