# Thegent — Phase 10–12 PRD (Optimization-Depth and Productization Wave)

**Status:** Finalized full-depth execution PRD  
**Date:** 2026-02-15  
**Scope:** Phase 10, 11, and 12 execution architecture focused on optimal design, robustness, and practical operability after Phases 7–9.

This document is designed as the next chunk in the same format as previous phase addenda and maps to `thegent-wbs-phase10-12.md`, `thegent-dag-phase10-12-extension.md`, and `thegent-phase10-12-test-readiness-pack.md`.

---

## 0) Strategic objective for Phase 10–12

1. Convert the system from "feature-complete" into "operator-grade" by maximizing practical ergonomics and correctness under adverse conditions.
2. Make the gent tool surface and contract strategy resilient to external ecosystem evolution while minimizing migration friction.
3. Turn predictive capabilities into reliable, low-noise production actions with explicit governance and rollback.
4. Raise long-term maintainability by standardizing architecture boundaries, testability, and documentation automation.

## 0.1 Execution preconditions

- `thegent-wbs-phase10-12.md` approved by owner and risk council.
- `thegent-dag-phase10-12-extension.md` graph references are canonical for control routing.
- `WBS_TO_ISSUE_IMPORT_MATRIX.md` has owners and issue IDs (or planned IDs) for every WP.
- Baseline gates `M9` and phases 7–9 completion evidence available and signed.
- Dedicated canary lane for control changes with feature flag families:
  - `control.phase10.interface_v2`
  - `control.phase11.autotune`
  - `control.phase12.replay_guard`

## 0.2 Non-negotiable design principles

1. **Determinism first:** Any non-deterministic behavior in control logic must be wrapped in an explicit policy flag and replayed with trace IDs.
2. **Reversible changes:** Any runtime behavior change must have a one-step deterministic rollback path (`gate_version`, `policy_digest`, `evidence_id`).
3. **Schema lockstep:** CLI/MCP/SDK contract paths must remain projection variants of the same envelope schema and policy namespace.
4. **Policy precedence:** No adaptive control action may execute without policy provenance.
5. **Observability completeness:** Every phase-level behavior must generate machine-readable audit evidence within 5 seconds.
6. **Predictive restraint:** No optimization action may execute without confidence threshold, fatigue guard, and owner approval context.
7. **No hidden behavior:** Every new control path exposed via a flag must have documentation and deletion criteria.

## 0.3 Delivery quality contract (phase-wide)

- Every WP must produce:
  - at least one unit test file,
  - one integration test when crossing interfaces or data boundaries,
  - one evidence artifact under `artifacts/phase10`, `artifacts/phase11`, or `artifacts/phase12`.
- All critical-path WPs (`WP-10003`, `WP-11001`, `WP-11004`, `WP-12003`) require a pre-merge readiness review.
- G10/G11/G12 may transition only on signed gate notes containing:
  - execution window,
  - command and rollout IDs,
  - pre/post KPIs,
  - rollback status.

These phases intentionally emphasize `optimization`, `robustness`, and `polish` as first-class delivery targets, not cosmetic add-ons.

---

## 1) Design pillars

### 1.1 Contract intelligence

- Every external boundary (CLI, MCP, operations, and web/API outputs) must use one canonical operation envelope.
- Contract negotiation is no longer only for parser format; it also controls operation schema versions, policy posture, and confidence semantics.
- Fail-safe defaults must always privilege safety and explainability over throughput.

### 1.2 Intelligence without surprise

- Every autonomous action must be accompanied by confidence, cost, time, and reversibility metadata.
- Suggestions must be ranked and explainable by provenance (rule, model signal, historical evidence).
- Any auto-action has a visible and reversible kill switch.

### 1.3 Minimal but composable primitives

- Use few stable primitives with strong typed args and capability-based extensions.
- Replace endpoint proliferation with operation enums plus extension namespaces.
- Keep migration additive and reversible for each release.

---

## 2) Phase 10: Adaptive Interface and Tool Ecosystem Convergence

### 2.1 Functional requirements

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-069 | Operation schema v2 with transport-agnostic envelopes | CLI/MCP/SDK calls carry equivalent `operation`, `target`, `inputs`, `policy_context`, `expected_output_contract`, and `idempotency_key`. |
| FR-070 | Canonical capability registry for all providers and tools | `list_capabilities` returns stable capabilities, support levels, region constraints, and schema versions; mismatch is surfaced before invocation. |
| FR-071 | Endpoint consolidation to parameterized commands | `orchestrate`, `govern`, `observe`, `replay`, `plan`, `recover` each accept operation enums and route deterministically through one dispatch graph. |
| FR-072 | Deterministic dispatch tracing | Dispatch decisions store `dispatch_path`, `rule_reason`, `latency_budget_ms`, and policy override reason. |
| FR-073 | Plugin-safe extension layer with typed adapters | Third-party adapters register through `register_adapter(entrypoint, contract_version, trust_level)` and pass conformance suite before activation. |
| FR-074 | Operation-level compatibility policy | Unknown operation on a supported adapter fails with explicit migration/error and machine-actionable alternatives. |
| FR-075 | Contract drift budget by operation class | Each operation class has drift threshold and auto-gating when threshold exceeded. |

### 2.2 Non-functional requirements

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-029 | Interface discovery latency | ≤ 60ms p95 for capability discovery in steady state |
| NFR-030 | Dispatch determinism | Given same request + policy + state, dispatch path must be identical across 100 runs |
| NFR-031 | Compatibility error clarity | Every unsupported operation returns `suggested_migration_version` + `suggested_operation_alt` |
| NFR-032 | Security boundary clarity | Adapter trust levels prevent untrusted adapter from critical lanes |

### 2.3 UX requirements

- `thegent tools` displays capability matrix, trust levels, and compatibility by lane.
- Compatibility warnings are rendered with severity and immediate fix path.
- Each operation invocation prints one-line summary + expandable structured evidence.

### 2.4 Scope and boundaries

- Scope: operation dispatch, schema versions, registry, adapter lifecycle.
- Out of scope: adding completely new business domain features not already represented in existing PRD phases.

### 2.5 Phase 10 acceptance

- 100% deterministic dispatch for all core ops under canary.
- Zero critical-lane unhandled-operation incidents.
- Registry-first execution used for ≥ 95% of tool calls.

---

## 3) Phase 11: Autonomous Reliability Optimization and Predictive Resilience

### 3.1 Functional requirements

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-076 | Closed-loop SLO regulator | Live control loop adjusts non-critical throughput based on error, latency, saturation, and quality signals; no critical-lane oscillation > 1/min. |
| FR-077 | Prediction confidence calibration and drift response | Forecast engine tracks calibration; if calibration drops below threshold, auto-pauses non-deterministic optimizations. |
| FR-078 | Multi-provider preemption policy | Auto-avoid predicted provider saturation using forecast window and rolling token budget burn-rate. |
| FR-079 | Policy-aware self-healing suggestions | For each incident cluster, auto-generate top 3 remediations with confidence and rollback assumptions. |
| FR-080 | Adaptive task shaping | Dynamically split/merge tasks when risk score and queue profile cross configured thresholds. |
| FR-081 | Predictive continuity preservation | Before shift and predicted stall windows, enforce continuity checkpoints and ownership freshness rules. |
| FR-082 | Feedback learning loop | Closed-loop updates control parameters only with approved policy and explicit audit record. |

### 3.2 Non-functional requirements

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-033 | Prediction responsiveness | p95 risk forecast available within 120ms for standard plans |
| NFR-034 | Stability | No adaptive loop action unless signal confidence ≥ 0.75 |
| NFR-035 | Governance traceability | Every self-heal recommendation and adjustment includes owner, rationale, and rollback vector |
| NFR-036 | Rollback safety | Any auto-control change is reversible within 1 command/replay action |

### 3.3 UX requirements

- Risk cards show top contributors, confidence, and expected deltas (not just alerts).
- Operators can toggle optimizer mode (`off`/`assist`/`auto`) with an explicit persistence setting.
- Self-heal suggestions have "simulate first" default.

### 3.4 Scope and boundaries

- Scope: risk regulators, adaptive controls, forecast quality governance, continuity-aware orchestration.
- Out of scope: manual re-design of provider ranking core models.

### 3.5 Phase 11 acceptance

- 80%+ forecast/observed alignment sustained across 2 release windows.
- One successful auto-control event per week in pre-production without incident escalation.
- Continuity checkpoint cadence improved under stress tests with no critical rollbacks.

---

## 4) Phase 12: Enterprise-Grade Intuition, Operability, and Hardening

### 4.1 Functional requirements

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-083 | Explainability as API contract | Every event exposes summary/detail/trace through one stable schema version. |
| FR-084 | On-call readiness and fatigue control | Runbook prioritization and incident fatigue dampening prevents repeated non-blocking noise. |
| FR-085 | Deterministic replay + what-if simulation for all major ops | Operators can branch from any decision point in replay mode without state mutation. |
| FR-086 | Human escalation quality floor | Minimum evidence threshold before override escalation closes; all escalations include confidence delta and root-assumption snapshot. |
| FR-087 | Unified operations evidence graph | End-to-end evidence chain links run, task, policy, adapter, and operator action. |
| FR-088 | Compliance-ready artifact packaging | Single command exports PRD-aligned artifacts with digest chain and index manifest. |
| FR-089 | Cross-team operational personas | Separate persona profiles for SRE, Policy, Product, and Security with intent defaults and action limits. |
| FR-090 | Platform documentation compiler | One command compiles docs from schema/events/policies into release-grade PRD/WBS/test pack bundles. |

### 4.2 Non-functional requirements

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-037 | Explainability latency | Summary ≤ 200ms, detail ≤ 500ms, trace ≤ 1200ms |
| NFR-038 | Escalation quality | 99% of escalations include evidence and confidence rationale |
| NFR-039 | Replay safety | Replay mode never writes state unless explicit execute mode set |
| NFR-040 | Packaging reproducibility | Artifact bundle builds reproducibly from git state and manifest digest |

### 4.3 UX requirements

- Progressive UI/CLI: summary defaults, deep dive on demand.
- One-command artifact export includes manifest, checksum, and evidence index.
- Handoff handbooks and operator coaching cards are generated per persona automatically.

### 4.4 Scope and boundaries

- Scope: operator-facing reliability, explainability infrastructure, artifact operations, governance ergonomics.
- Out of scope: changing external compliance standards or domain policy legal language.

### 4.5 Phase 12 acceptance

- New operator persona can complete one critical continuation handoff end-to-end in one runbook pass.
- Replay safety checks catch 100% of mutation attempts in canary tests.
- Packaging export verifies artifact integrity for every PRD-linked requirement.

---

## 5) Cross-phase quality gates and dependencies

### 5.1 Critical dependencies

- Phase 10 gates all operation classes and adapters before any adaptive changes in Phase 11.
- Phase 11 relies on Phase 10 dispatch trace and operation telemetry for control signal quality.
- Phase 12 depends on both Phase 10/11 evidence graph and operation metadata for explainability and packaging.

### 5.2 Hard gates

- **G10:** Deterministic operation dispatch + registry confidence for all canary operations.
- **G11:** Forecast quality and self-heal actions under policy.
- **G12:** Replay safety, escalation evidence quality, and deterministic artifact pack.

### 5.3 Risk and control matrix

| Risk | Control |
|---|---|
| Over-optimization causing instability | Enforced confidence threshold + simulation-first controls. |
| Adapter ecosystem noise | Adapter trust scores and phased admission. |
| Operator overload | Persona-aware defaults + fatigue control heuristics. |
| Audit regressions from auto-heal actions | Immutable ledger + rollback logs + approval policy in Phase 12. |

---

## 6) Delivery pack strategy (chunkable)

### Chunk A
- Implement operation envelope v2, dispatcher registry, and compatibility path (`FR-069..FR-074`).

### Chunk B
- Add deterministic dispatch telemetry and compatibility policy tests.

### Chunk C
- Deploy SLO regulator, forecast calibration loop, and predictive continuity controls (`FR-076..FR-080`).

### Chunk D
- Add recommendation engine + adaptive controls with bounded actions.

### Chunk E
- Implement explainability API contract, replay safety hardening, handoff quality controls.

### Chunk F
- Build evidence graph packaging and command compiler for PRD/WBS/test bundle exports.

### Chunk G
- Final readiness review with gate audits (`G10`, `G11`, `G12`) and production enablement note.

---

## 7) PRD mapping to existing artifacts

- Base PRD for product context: `docs/docset/thegent-prd-final.md`
- Earlier addendum baseline: `docs/docset/thegent-phase7-9-next-wave-prd.md`
- WBS source for gates and ownership patterns: `docs/docset/thegent-wbs-final.md`
- Cross-analysis and research basis: `docs/docset/thegent-cross-analysis-matrix-2026-02-14.md`, `docs/docset/OPTIMIZATION_POLISH_ADDENDUM.md`

---

## 8) Feature-level design depth (FR → WP → Gate)

| FR | Target WP(s) | Gate | Hard controls |
|---|---|---|---|
| FR-069 | WP-10001 | G10 | Envelope migration compatibility + v2 fallback |
| FR-070 | WP-10001, WP-10002 | G10 | Capability policy + trust score gating |
| FR-071 | WP-10003, WP-10005 | G10 | Endpoint parity tests + deterministic route hashing |
| FR-072 | WP-10003, WP-10007 | G10 | Decision reason codified and replayed |
| FR-073 | WP-10008 | G10 | Plugin lifecycle lock and trust assertion |
| FR-074 | WP-10006, WP-10009 | G10 | Migration alternatives + explicit compatibility response |
| FR-075 | WP-10007, WP-10009 | G10 | Drift budgets + alert escalation |
| FR-076 | WP-11001 | G11 | Oscillation suppression and bounded actuation |
| FR-077 | WP-11002, WP-11003 | G11 | Confidence recalibration and optimization pause |
| FR-078 | WP-11004, WP-11007 | G11 | Saturation policy and continuity pre-check |
| FR-079 | WP-11005 | G11 | Ranked recommendation with rollback metadata |
| FR-080 | WP-11006 | G11 | Policy-mediated task split/merge |
| FR-081 | WP-11007 | G11 | Continuity predictor pre-shift enforcement |
| FR-082 | WP-11008 | G11 | Policy approval for parameter changes |
| FR-083 | WP-12001 | G12 | Schema-stable explanation projection |
| FR-084 | WP-12002 | G12 | Fatigue control and alert suppression budget |
| FR-085 | WP-12003, WP-12004 | G12 | Replay read-only mode and safe branching |
| FR-086 | WP-11001, WP-12007 | G12 | Escalation confidence floor + confirmation |
| FR-087 | WP-12006 | G12 | Evidence graph closure and index integrity |
| FR-088 | WP-12009 | G12 | Deterministic export and checksum |
| FR-089 | WP-12007 | G12 | Persona policy and action constraints |
| FR-090 | WP-12009, WP-12010 | G12 | One-command release pack and final approvals |

## 9) Failure-mode assumptions and handling plan

- **Control instability:** If phase 11 loops show sustained oscillation or policy violation, phase 11 control nodes pause to safe values and remain in assist-only mode until 2 approval events and one full regression cycle.
- **Dispatcher inconsistency:** If `dispatch_path` diverges between CLI and MCP for the same input, freeze mutation by forcing registry strict mode + fallback and emit owner review action.
- **Replay mutation attempts:** Any write path from replay mode triggers an immediate hard fail, evidence event, and optional rollback for previous mutation in flight.
- **Evidence pack incompleteness:** G12 cannot pass until 100% required artifacts are signed, checksummed, and validated against manifest schema.
- **Adapter trust breach:** Incomplete or unknown adapter trust metadata auto-classifies provider as untrusted and blocks critical-lane operation until remediation.

## 10) Completion criteria for exit from this PRD chunk

1. WBS entries `WP-10001`–`WP-12010` have at least one linked issue record and evidence ticket.
2. G10, G11, and G12 have signed gate notes with reproducible evidence IDs.
3. PRD/test/wbs/docset consistency check completed:
   - 102 WPs, 64 FRs, 28 NFRs represented across active docs.
4. One production shadow window completes with zero critical control incidents and zero replay safety violations.
