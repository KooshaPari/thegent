# Thegent Production Orchestration PRD (Final)

**Status:** Finalized comprehensive PRD
**Date:** 2026-02-14
**Scope:** Complete synthesis of 18 research agents (codebase + industry SOTA) with 42 FRs, 16 NFRs, 114 patterns, MAST taxonomy, TRAFFIC KPIs, and 7-phase roadmap.

---

## 1. Product Summary

Thegent is a production-grade agent orchestration platform that enables deterministic, resilient, auditable, scalable, and operator-intuitive multi-agent execution. The platform bridges the gap between independent agent capabilities and enterprise-grade reliability by providing:

- **Deterministic Routing:** Dependency-aware task routing with multi-agent mode selection and conflict resolution
- **Resilient Execution:** Checkpoint-based recovery, circuit breakers, chaos-verified playbooks, and MAST 14-mode failure taxonomy
- **Governed Decisioning:** OPA/Rego declarative policies, ABAC fine-grained routing, HITL escalation, and immutable audit trails
- **Operator Clarity:** Mission Control cockpit, progressive disclosure, safe fallback actions, and real-time decision replay
- **Cost Optimization:** Per-run tracking, provider scoring, RouteLLM routing, and speculative execution for latency-critical paths
- **Observable Operations:** OTel GenAI telemetry, TRAFFIC 10-metric framework, structured JSON logging, and real-time KPI dashboards

---

## 2. Goals

- Improve orchestration reliability by reducing repeated failures and enabling automated recovery
- Enforce governance and security gates without sacrificing throughput on non-critical paths
- Deliver transparent operator experiences with safe fallback mechanisms for all risky decisions
- Maintain ownership continuity and task state across interruptions and shift handoffs
- Support adaptive load behavior and cost-optimization during burst conditions
- Enable full auditability and compliance for regulated workloads (EU AI Act, SOC 2, GDPR)

---

## 3. Non-Goals

- Replacing external policy providers (OPA/Rego integration, not replacement)
- Rebuilding all existing UI surfaces from scratch (integrate with existing cockpit layer)
- Migrating unrelated business workflows outside thegent scope
- Supporting providers without well-defined contract protocols

---

## 4. Personas

- **Operator:** Executes and monitors orchestration decisions, responds to alerts, approves high-risk actions
- **Incident Lead:** Coordinates recovery under pressure, initiates rollbacks, escalates unresolved issues
- **Platform/SRE:** Ensures stability, SLO compliance, runbook quality, and provider health management
- **Governance/Compliance:** Enforces policy, maintains auditability, and manages retention/retention for regulated domains
- **Product Owner:** Prioritizes features, manages release readiness, and aligns thegent with business strategy

---

## 5. Core User Journeys

**Sunny Path:**
- Chunk ingestion → validation → routing → agent execution → governance gate → promotion → closure

**Policy Hold Path:**
- Policy gate blocks execution → operator reviews evidence + rationale → decision (approve/deny) → audit record

**Recovery Path:**
- Failure detected → classify via MAST taxonomy → select playbook → execute with idempotency → validate → close or escalate

**Burst Load Path:**
- Load surge detected → activate adaptive mode → protect critical lanes with reduced concurrency → defer non-critical → restore normal mode

**Shift Handoff Path:**
- Ownership change → continuity snapshot generated → incoming owner confirms receipt → outgoing owner released

---

## 6. System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         Operator Cockpit                            │
│              (Mission Control: Queue | Roster | Events | Details)  │
└────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  │
                       Governance Gates & Escalation
                                  ↓
┌────────────────────────────────────────────────────────────────────┐
│                   Orchestration Core (MCP Server)                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│  │ Routing Engine  │   │ Execution       │   │ Governance      │  │
│  │ (Deterministic, │   │ Envelope        │   │ Service         │  │
│  │  Multi-Mode)    │   │ (Idempotent)    │   │ (OPA/Rego)      │  │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Contract Registry & Parser Engine (CSM + Fallback Stack)    │  │
│  │ ├─ XML Contract Registry (versioned, namespace-based)       │  │
│  │ ├─ Canonical Structured Message (CSM) normalizer            │  │
│  │ ├─ Incremental XML Parser (XMLPullParser + sloppy-xml)     │  │
│  │ └─ Provider Adapter Conformance Suite (gemini/copilot/...)  │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│  │ Recovery        │   │ Checkpoint      │   │ Provider        │  │
│  │ Service         │   │ Service         │   │ Adapters        │  │
│  │ (Playbooks, DLQ)│   │ (PostgresSaver) │   │ (LiteLLM chains)│  │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Observability & Cost Tracking (OTel + TRAFFIC Dashboard)    │  │
│  │ ├─ OTel GenAI semantic conventions (gen_ai.* spans)         │  │
│  │ ├─ TRAFFIC 10-metric framework (Throughput, Routing, ...)  │  │
│  │ ├─ Per-run cost tracking with budget alerts                 │  │
│  │ └─ Structured JSON logging with machine-queryable fields    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                  ↓
                        ┌──────────────────┐
                        │  External Services│
                        │  (Providers,      │
                        │   OPA/OPAL,       │
                        │   PostgreSQL)     │
                        └──────────────────┘
```

---

## 7. Functional Requirements

### Original Functional Requirements (FR-001 through FR-024)

| ID | Requirement | Acceptance Criteria | WP Mapping | Pattern | Priority |
|----|----|----|----|----|----|
| FR-001 | Dependency-aware deterministic routing | Routes respect all declared task dependencies; replay produces identical routing | WP-1001 | P-023 | P0 |
| FR-002 | Idempotent execution envelopes for action safety | Same (run_id, step, action_type, content_hash) always produces same side effects or error | WP-1003 | P-036 | P0 |
| FR-003 | Policy pre-check before execution | Every task checked against governance rules before execution; blocked tasks escalate | WP-3001 | P-066, P-078 | P0 |
| FR-004 | Mandatory evidence collection for promotion | All evidence present before promotion gate; hash verification passes | WP-4001, WP-3004 | P-019, P-076 | P0 |
| FR-005 | Integrity and regression gates before release | All integrity checks pass; no behavioral regression vs baseline | WP-1004 | P-065 | P0 |
| FR-006 | Checkpoint rollback for failed promotions | Failed promotion triggers checkpoint rollback; state restored to last good checkpoint | WP-2001 | P-038 | P1 |
| FR-007 | Retry and circuit-breaker strategy by failure class | Each failure class has mapped retry strategy; per-provider circuit breakers active | WP-2002, WP-2003 | P-034, P-035, P-041 | P1 |
| FR-008 | Recovery playbook selection by known failure pattern | Failure classified then auto-matched to playbook; playbook executes within SLA | WP-2004 | P-041 | P1 |
| FR-009 | Human oversight path for repeated/unknown failures | Repeated failures (3+ attempts) or unknown failure classes escalate to operator | WP-4004 | P-071 | P1 |
| FR-010 | Signed action artifacts for critical operations | Critical operations produce cryptographically signed artifacts; signatures verify | WP-3002 | P-076 | P1 |
| FR-011 | Override controls with reason code and expiry | Overrides require: reason_code, approver, TTL; auto-expire after TTL | WP-3003 | P-075 | P1 |
| FR-012 | Immutable audit event trail | All events append-only, never deleted; vector-clock ordering for causality | WP-3004 | P-069 | P1 |
| FR-013 | Policy drift detection and governance sweep | Detect missing/modified/new policies; periodic reconciliation scheduled; drift alerts | WP-3005 | P-074 | P2 |
| FR-014 | Trust boundary validation for environment transitions | Policies re-evaluated at target environment; no implicit trust inheritance | WP-3007 | P-077 | P2 |
| FR-015 | Concise and detailed explanation tiers | Tier 1 (summary, always visible), Tier 2 (detail, click to expand), Tier 3 (trace, deep dive) | WP-4002 | P-092 | P2 |
| FR-016 | One-click safe fallback for risky choices | Pause/Rollback/Escalate actions always visible; no menu nesting | WP-4003 | P-096 | P2 |
| FR-017 | Stale-state execution block | Tasks using state older than threshold blocked with staleness warning | WP-4005 | P-114 | P2 |
| FR-018 | Continuity snapshot and owner handoff for open critical tasks | Snapshot contains active work, blocked items, recent decisions, action items; incoming owner confirms | WP-4006 | P-111 | P2 |
| FR-019 | Adaptive load controls with critical lane protection | Surge detection → reduce concurrency in non-critical lanes → protect critical SLOs | WP-5001 | P-045 | P2 |
| FR-020 | Non-critical deferral with explicit ETA and rationale | Deferred tasks show ETA and reason; resume when load normalizes | WP-5002 | P-026 | P2 |
| FR-021 | Continuity watchdog for stale ownership | Track ownership age; alert if stale (> 4 hours); escalate at TTL expiry | WP-5005 | P-109 | P2 |
| FR-022 | Decision replay with rationale snapshot | Replay execution timeline; what-if mode at any decision point; pre-flight simulation | WP-4007 | P-099 | P3 |
| FR-023 | Role-aware confidence calibration | Track "when 70% confidence, approve 85% of time"; dynamically tune thresholds by role | WP-4008 | P-098 | P3 |
| FR-024 | Closure pack generation for launch and audit | Generate closure pack with execution summary, evidence, audit trail, compliance sign-off | WP-6001 | P-119 (planning artifact) | P3 |

### New Functional Requirements (FR-025 through FR-042)

| ID | Requirement | Acceptance Criteria | WP Mapping | Pattern | Priority |
|----|----|----|----|----|----|
| FR-025 | Contract version negotiation for all structured agent outputs | All agent outputs declare contract version via namespace; parser selects version-specific handler | WP-X1 | P-004, P-062 | P0 |
| FR-026 | Canonical Structured Message (CSM) normalization across XML variants | All provider outputs normalize to canonical CSM; cross-provider payload heterogeneity transparent to downstream | WP-X2 | P-001, P-002 | P0 |
| FR-027 | Incremental XML parser with recoverable partial-state model | Parser handles streaming chunks; maintains parse state across chunks; partial states never treated as final | WP-X3 | P-013, P-014, P-015 | P0 |
| FR-028 | Semantic validation with cross-tag invariants and phase-aware rules | Validator enforces: STATUS=completed ⟹ non-empty ACTIONS, cross-tag coherence, phase-specific rule sets | WP-X4 | P-007, P-011 | P1 |
| FR-029 | Provider adapter conformance tests and output drift alarms | Every provider (gemini/copilot/codex/claude) passes conformance suite; drift detected within 60s | WP-X5 | P-020, P-008 | P1 |
| FR-030 | Policy-governed fallback routing with explicit SLO budgets | Fallback state machine (Primary → Degraded → Fallback → Recovered); SLO budgets enforced per lane | WP-X6 | P-018, P-016 | P1 |
| FR-031 | Dual-read/dual-write migration support for contract upgrades | Dual-read accepts v1 + v2; dual-write emits both; canary ramp enables zero-downtime contract migrations | WP-X8 | P-047, P-048 | P1 |
| FR-032 | Multi-agent orchestration mode selection (sequential/parallel/hierarchical) | Mode selection policy routes to: sequential delegation, parallel consensus, hierarchical planning, or review loop | WP-Y1 | P-050, P-052, P-053, P-054, P-060 | P1 |
| FR-033 | ABAC policy expressions for fine-grained routing decisions | Policies support: risk_score < 0.5 AND domain == "non-financial" AND confidence > 0.8 | WP-3001 | P-068 | P1 |
| FR-034 | Dead-letter queue with poison pill detection for permanently failing items | Failed items routed to DLQ after retries exhausted; poison pill (same content_hash fails in 2+ contexts) flagged | WP-Y2 | P-042 | P2 |
| FR-035 | Chaos engineering fault injection framework for recovery testing | Framework injects: network partition, provider timeout, malformed response, state corruption; automated test scenarios | WP-Y3 | P-043 | P2 |
| FR-036 | Cost tracking per-run with budget alerts and cost-per-quality optimization | Track cost per successful outcome; alert on budget breach; optimize cost-per-quality ratio | WP-Y4 | P-083, P-025 | P2 |
| FR-037 | Speculative execution for latency-critical paths | Send request to 2 providers simultaneously; use first successful response; only for designated critical lanes | WP-5001 | P-027 | P3 |
| FR-038 | Prompt-characteristic routing (complexity/domain/length classification) | Classify prompts by (complexity, domain, length, required_capability); route to optimal provider per classification | WP-1007, WP-Y8 | P-024 | P3 |
| FR-039 | Autonomy gradient control per domain/lane in operator cockpit | Operators adjust autonomy dial per domain; real-time toggles show agent-initiated vs human-approved actions | WP-4001 | P-091 | P3 |
| FR-040 | Pre-flight simulation ("dry run") before irreversible actions | Simulate predicted outcome before execution; show affected resources and reversibility; operator confirms | WP-4003 | P-097 | P3 |
| FR-041 | Calibration curve tracking for confidence threshold tuning | Track: "when system reports X% confidence, operators approve Y% of the time"; dynamically tune thresholds | WP-4008 | P-098 | P3 |
| FR-042 | Hierarchical prompt orchestration (platform/domain/workflow/step) | 4-level hierarchy: platform policy → domain rules → workflow instructions → step objectives; lower levels inherit + bounded override | WP-Y5 | P-059 | P3 |

---

## 8. Non-Functional Requirements

### Original Non-Functional Requirements (NFR-001 through NFR-008)

| ID | Requirement | Target Metric | Alert Threshold | Measurement |
|----|----|----|----|----|
| NFR-001 | P95 routing latency within defined SLO under normal load | < 250ms p95 | > 300ms p95 | Span traces from routing service |
| NFR-002 | Stable critical-path latency under burst load | < 350ms p95 (burst) vs < 250ms p95 (normal) | > 450ms p95 | Load test with 5x baseline traffic |
| NFR-003 | No non-deterministic promotion behavior in replay tests | 100% replay consistency | Any divergence | Determinism test suite on 1000+ runs |
| NFR-004 | Policy checks available and reliable in production windows | 99.95% uptime for policy evaluation | < 99% | OPA uptime monitoring + SLO tracking |
| NFR-005 | Rollback completion within incident SLA targets | < 60s p95 rollback time | > 90s | Rollback execution traces + incident logs |
| NFR-006 | Continuity snapshots complete for all open critical work | 100% coverage of open critical tasks | < 95% | Snapshot generation audit trail |
| NFR-007 | Audit query retrieval within operational SLA | < 500ms p95 for audit queries | > 750ms | Audit read-path latency SLO |
| NFR-008 | Operator rationale rendering within UX latency targets | < 100ms for progressive disclosure render | > 150ms | Cockpit rendering traces |

### New Non-Functional Requirements (NFR-009 through NFR-016)

| ID | Requirement | Target Metric | Alert Threshold | Measurement |
|----|----|----|----|----|
| NFR-009 | Parse + normalize latency preserved under p95 routing SLO | CSM normalization < 50ms p95 | > 75ms p95 | Parser + normalizer span times |
| NFR-010 | Schema drift detection within 60 seconds | Drift event emitted within 60s of occurrence | > 90s detection latency | Schema drift event monitoring |
| NFR-011 | Fallback-induced failure rate below 1% | Fallback execution success rate >= 99% | > 1% fallback failures | Fallback state machine analytics |
| NFR-012 | Zero silent contract downgrade in critical lanes | Degraded mode events logged in critical lanes | Any silent downgrade | Contract telemetry audit |
| NFR-013 | OTel GenAI semantic convention compliance on all spans | 100% of orchestration spans emit gen_ai.* attributes | < 99% compliance | Trace attribute validation on sample |
| NFR-014 | Structured JSON logging on all orchestration events | 100% of events include: run_id, step_id, provider, latency_ms, cost_usd, confidence | < 99% structured | Log format validation |
| NFR-015 | EU AI Act risk classification tagging on orchestration decisions | Every decision tagged with risk category (minimal/limited/high/unacceptable) | Any untagged decision in critical lanes | Compliance audit + audit trail scan |
| NFR-016 | Provider routing optimization achieving >= 20% cost reduction at maintained quality | Cost per successful outcome reduced by >= 20% vs baseline | < 15% cost reduction | Provider scoring model A/B test |

---

## 9. API and Event Model

### 7 Orchestration Tools (MCP Protocol)

```
thegent.orchestrate(operation, **kwargs) -> Result
  ├─ operation="route" -> Routing decision with lane + provider selection
  ├─ operation="execute" -> Execution envelope invocation with idempotency
  ├─ operation="rollback" -> Checkpoint-based rollback with recovery
  ├─ operation="recover" -> Recovery playbook selection + execution
  ├─ operation="observe" -> Telemetry + TRAFFIC KPI snapshot
  ├─ operation="plan" -> Multi-agent mode selection + decomposition
  └─ operation="adapt" -> Provider scoring + routing model updates

thegent.govern(operation, **kwargs) -> PolicyDecision
  ├─ operation="evaluate" -> Policy evaluation via OPA/Rego
  ├─ operation="override" -> Apply time-bounded override with reason
  ├─ operation="sign" -> Generate cryptographic signature for critical action
  └─ operation="audit" -> Record audit event with causal ordering

thegent.recover(operation, **kwargs) -> RecoveryResult
  ├─ operation="classify" -> MAST 14-mode failure classification
  ├─ operation="playbook" -> Select recovery playbook
  ├─ operation="dlq" -> Route permanently failing items to dead-letter queue
  └─ operation="chaos" -> Inject fault for testing recovery paths

thegent.observe(operation, **kwargs) -> ObservabilityData
  ├─ operation="metrics" -> TRAFFIC KPI snapshot (10 metrics)
  ├─ operation="trace" -> Retrieve trace by run_id with parent-child spans
  ├─ operation="cost" -> Per-run cost aggregation + budget status
  └─ operation="logs" -> Query structured JSON logs with machine-readable fields

thegent.plan(operation, **kwargs) -> PlanResult
  ├─ operation="mode_select" -> Select multi-agent mode based on task characteristics
  ├─ operation="decompose" -> Hierarchical task decomposition
  └─ operation="schedule" -> PERT-based scheduling with confidence bands

thegent.adapt(operation, **kwargs) -> AdaptResult
  ├─ operation="score_provider" -> Update provider scoring model from historical quality
  ├─ operation="route_optimize" -> RouteLLM cost-quality optimization
  └─ operation="confidence_tune" -> Calibration curve update

thegent.audit(operation, **kwargs) -> AuditData
  ├─ operation="query" -> Immutable audit trail retrieval
  ├─ operation="verify" -> Verify signed artifact integrity
  └─ operation="retention" -> Apply retention policy by domain
```

### Event Taxonomy (Minimum 10 Types)

```
chunk.ingested                    # Chunk received, initial validation
chunk.routed                      # Routing decision made, provider + lane selected
chunk.blocked.policy              # Policy gate blocked execution, escalated
chunk.executed                    # Execution envelope completed successfully
chunk.failed                      # Execution failure, classified via MAST
chunk.recovered                   # Recovery playbook executed, recovered
chunk.rollbacked                  # Checkpoint rollback completed
chunk.promoted                    # Promotion gate passed, ready for release
governance.signature.validated    # Signed artifact verified
governance.override.applied       # Time-bounded override applied
governance.policy.drifted         # Policy drift detected + alert
recovery.playbook.run             # Recovery playbook execution started
recovery.dlq.routed               # Item routed to dead-letter queue
continuity.snapshot.created       # Continuity snapshot for shift handoff
continuity.snapshot.confirmed     # Incoming owner confirmed receipt
observability.cost.budget_breach  # Per-run cost exceeded budget
observability.confidence.degraded # Confidence score fell below threshold
multi_agent.conflict.detected     # Multi-agent outputs conflicted
multi_agent.mode.selected         # Orchestration mode selected
schema.drift.structural           # Contract structural drift detected
schema.drift.semantic             # Contract semantic drift detected
```

### Canonical Structured Message (CSM) Schema

```yaml
version: "urn:thegent:csm:v2"
metadata:
  run_id: "run-uuid-12345"
  step_id: 1
  provider: "claude"
  timestamp: "2026-02-14T10:30:00Z"
  idempotency_key: "hash(run_id, step_id, action_type, content_hash)"
  contract_version: "v2"
  confidence: 0.92
  risk_score: 0.15
execution:
  status: "COMPLETED" | "FAILED" | "PENDING"
  progress: 0-100
  actions_completed: [...]
  actions_pending: [...]
tags:
  task_id: "..."
  task_title: "..."
  acceptance_criteria: "..."
  priority: "HIGH" | "MEDIUM" | "LOW"
  reasoning: "..."
  decision_reason_code: "DR-001"
governance:
  policy_gate_id: "pg-12345"
  policy_decision: "APPROVED" | "BLOCKED" | "ESCALATED"
  evidence_set_hash: "sha256:..."
  signed_artifact: "base64(...signature...)"
  eu_ai_act_risk: "MINIMAL" | "LIMITED" | "HIGH" | "UNACCEPTABLE"
telemetry:
  latency_ms: 245
  cost_usd: 0.0032
  tokens_input: 1200
  tokens_output: 450
  fallback_level: 0 | 1 | 2 | 3
  drift_events: [...]
```

---

## 10. MAST 14-Mode Failure Taxonomy

Replaces the original 7-class taxonomy with comprehensive failure classification covering infrastructure, model, tool, logic, and security failure modes.

| Mode | Category | Description | Recovery Strategy | Playbook |
|------|----------|-------------|-------------------|----------|
| F-01 | Infrastructure | Network partition / timeout | Retry with exponential backoff + circuit breaker | PB-Infrastructure-Retry |
| F-02 | Infrastructure | Storage failure (DB, cache, DLQ) | Failover to replica + checkpoint recovery | PB-Infrastructure-Failover |
| F-03 | Infrastructure | Rate limit exceeded | Backpressure + provider rotation | PB-RateLimit-Backpressure |
| F-04 | Model | Hallucination / factual error | Re-prompt with grounding data + semantic validation | PB-Hallucination-Regrounding |
| F-05 | Model | Refusal / safety filter | Rephrase prompt + alternative provider + escalation | PB-Refusal-Rephrase |
| F-06 | Model | Context overflow | Summarize context + retry with reduced input | PB-ContextOverflow-Summarize |
| F-07 | Model | Output format violation | Re-prompt with schema example + validation retry | PB-FormatViolation-Validate |
| F-08 | Tool | Tool execution failure | Retry + alternative tool + manual fallback | PB-ToolFailure-Fallback |
| F-09 | Tool | Tool misuse (wrong tool for task) | Re-plan with tool capability check | PB-ToolMisuse-Replan |
| F-10 | Logic | Goal drift (agent diverges from objective) | Checkpoint rollback + re-plan from last good state | PB-GoalDrift-Rollback |
| F-11 | Logic | Infinite loop / oscillation | Detect via step counter + force termination | PB-InfiniteLoop-Terminate |
| F-12 | Logic | Conflicting sub-agent outputs | Conflict resolution protocol (majority vote + confidence weight) | PB-Conflict-Resolve |
| F-13 | Security | Prompt injection detected | Quarantine + audit + human review | PB-PromptInjection-Quarantine |
| F-14 | Security | Data exfiltration attempt | Block + audit + incident response | PB-DataExfiltration-Block |

---

## 11. TRAFFIC 10-Metric KPI Framework

Comprehensive observability framework capturing orchestration health across throughput, routing, accuracy, freshness, fallback, interruption, cost, retention, rollback, and continuity dimensions.

| KPI | Full Name | Definition | Target | Alert | Cadence |
|-----|-----------|-----------|--------|-------|---------|
| **T** | Throughput | Chunks processed per minute (baseline normalized) | >= baseline | < 80% baseline | 1 min |
| **R** | Routing Accuracy | Correct provider/lane selection rate | >= 95% | < 90% | 5 min |
| **A** | Accuracy of Decisions | Orchestration decisions producing desired outcome | >= 90% | < 85% | 5 min |
| **F-Fresh** | Freshness of State | Age of data used in routing decisions (seconds) | < 30s p95 | > 60s p95 | 1 min |
| **F-Fall** | Fallback Rate | Percentage of requests hitting fallback path | < 5% | > 10% | 5 min |
| **I** | Interruption Burden | Operator interruptions per hour | < 5/hr | > 10/hr | 1 min |
| **C** | Cost Efficiency | Cost per successful orchestration outcome | < budget | > 120% budget | 1 hr |
| **K** | Knowledge Retention | Recovery playbook hit rate for known failures | >= 80% | < 60% | 1 hr |
| **R-Rbk** | Rollback Success Rate | Percentage of rollbacks completing within SLA | >= 99% | < 95% | 1 hr |
| **+** | Continuity Coverage | Percentage of open critical work with valid snapshots | 100% | < 95% | 1 hr |

---

## 12. Data Contracts

### IdempotencyKey Schema

```python
IdempotencyKey = hash(
    run_id: str,              # Run identifier
    step_index: int,          # Step position in execution sequence
    action_type: str,         # Type of action (EXECUTE, PROMOTE, ROLLBACK, etc.)
    content_hash: str         # SHA256 hash of action payload
)
# Two invocations with same IdempotencyKey always produce same result or error
```

### Checkpoint Schema

```yaml
checkpoint:
  thread_id: "run-12345"
  thread_ts: "2026-02-14T10:30:00.000Z"    # Point-in-time snapshot
  state_hash: "sha256:..."
  execution_state:
    step_index: 42
    routing_decision: {...}
    agent_outputs: {...}
    policy_evaluations: {...}
  last_successful_action: {...}
  open_rollback_windows: [...]
  timestamp: "2026-02-14T10:30:15.123Z"
```

### Audit Entry Schema

```yaml
audit_entry:
  event_id: "uuid"
  actor: "operator-id" | "system"
  action: "POLICY_EVALUATE" | "OVERRIDE_APPLY" | "ROLLBACK_INITIATE" | "SIGNED_ACTION" | "CHUNK_EXECUTED"
  resource: "run-12345" | "policy-gate-5" | "checkpoint-42"
  outcome: "SUCCESS" | "FAILURE" | "PARTIAL"
  timestamp: "2026-02-14T10:30:00.000Z"
  vector_clock: {...}                     # Causal ordering for distributed
  evidence_hash: "sha256:..."             # Hash of evidence supporting action
  policy_version: "v2-stable"
  compliance_tags: ["GDPR", "SOC2-CC7.1"]  # Relevant compliance frameworks
  immutable: true                         # Append-only, never deleted
```

### Provider Score Schema

```yaml
provider_score:
  provider: "claude" | "gemini" | "copilot" | "codex"
  timestamp: "2026-02-14T10:30:00Z"
  metrics:
    reliability_score: 0.98                # Success rate, last 7 days
    latency_p95_ms: 245
    cost_per_call_usd: 0.0032
    capability_match: 0.92                 # Task-domain fit
    quality_score: 0.89                    # Output quality vs baseline
  composite_score: 0.94                   # Weighted: 40% reliability, 25% quality, 20% latency, 15% cost
  trend: "improving" | "stable" | "degrading"
  historical_quality: [...]               # Historical quality data for model training
```

---

## 13. Rollout Strategy (7 Phases + Phase X)

```
Phase 0: Foundation and Baseline (WP-0001..0005, WP-Y6)
├─ Core telemetry (OTel GenAI instrumentation)
├─ Baseline contracts (existing routing/execution/governance)
├─ Session management persistence
├─ MCP server hardening
└─ Gate A: Foundation validated

Phase X: Contract and Adapter Hardening (WP-X1..X8) [NEW INSERT]
├─ XML Contract Registry with versioning + capability negotiation
├─ Canonical Structured Message (CSM) normalization
├─ Incremental XML Parser (XMLPullParser + sloppy-xml)
├─ Semantic Validation Layer with cross-tag invariants
├─ Provider Adapter Conformance Suite (all providers)
├─ Fallback Reliability Policy with SLO budgets
├─ Contract Telemetry and Drift Detection
├─ Contract Migration Controller (dual-read/dual-write)
└─ Gate A+: Contract infrastructure live in canary

Phase 1: Core Routing and Deterministic Execution (WP-1001..1008, WP-Y1)
├─ LiteLLM function_with_fallbacks provider chains
├─ Multi-agent orchestration modes (sequential/parallel/hierarchical)
├─ Ensemble routing with 7 methods
├─ Phase-gated lifecycle (Planner/Operator/Reviewer)
├─ MCP Tasks primitive for async execution
├─ Middleware-as-orchestration-contract execution envelope
├─ Child-task routing with capability matching
├─ Traffic rate limiting + adaptive mode selection
└─ Gate B: Deterministic routing + multi-agent modes in canary

Phase 2: Reliability and Recovery Hardening (WP-2001..2008, WP-Y2, WP-Y3)
├─ PostgresSaver checkpoint service with thread_ts
├─ Exponential backoff + jitter retry strategy
├─ 3-state circuit breaker per provider
├─ IdempotencyKey (run_id, step_index, action_type, content_hash)
├─ Recovery playbook selection engine (MAST taxonomy)
├─ Dead-Letter Queue with poison pill detection
├─ Chaos Engineering Fault Injection Framework
├─ Bulkhead isolation + turn-taking strategies
└─ Gate C: Recovery hardening + DLQ + chaos verified under drills

Phase 3: Governance and Security Enforcement (WP-3001..3008, WP-Y5)
├─ OPA/Rego declarative policy engine + OPAL distribution
├─ RBAC + ABAC hybrid access control
├─ Signed action artifacts for critical operations
├─ Override controls with TTL + revalidation
├─ Trust boundary checks across environments
├─ Policy drift detection + governance sweep automation
├─ EU AI Act risk classification tagging
├─ Hierarchical prompt orchestration (4-level hierarchy)
└─ Gate D: Governance/security gates enforced, policy version tracked

Phase 4: Human-Centered UX and Explainability (WP-4001..4008, WP-Y7)
├─ Mission Control 4-pane operator cockpit (Queue|Roster|Events|Details)
├─ Progressive disclosure 3-tier with persona-based defaults
├─ Safe fallback 3-action model (Pause/Rollback/Escalate)
├─ Correlation-first alerting with dedup + per-operator ceiling
├─ State freshness checks (last updated timestamps)
├─ Automated continuity snapshots with incoming-owner confirmation
├─ Decision replay 4-capability model (Replay/What-If/Pre-Flight/Training)
├─ TRAFFIC KPI dashboard (10-metric visualization)
└─ Gate E: UX cockpit + TRAFFIC dashboard adopted by operators

Phase 5: Adaptive Scale and Continuity Automation (WP-5001..5008, WP-Y4, WP-Y8)
├─ Speculative execution for latency-critical paths
├─ Non-critical deferral with ETA + rationale
├─ Continuity watchdog for stale ownership
├─ Cost tracking per-run with budget alerts
├─ RouteLLM cost-quality optimization model
├─ Provider scoring with continuous learning
├─ Prompt-characteristic routing (complexity/domain/length)
├─ Graduated rollback + Rubrik Agent Rewind selective revert
└─ Gate F: Adaptive scale + cost optimization + provider scoring stable

Phase 6: Enterprise Readiness and Launch Closure (WP-6001..6008)
├─ Compliance sign-offs (EU AI Act, SOC 2, GDPR)
├─ Incident runbook certification
├─ Launch readiness criteria validation
├─ Closure pack generation (execution summary, audit trail, evidence)
├─ Handoff to long-term owners + SRE runbook
├─ Deprecation of temporary controls per sunset plan
├─ Post-launch stabilization (28-day observation)
└─ Gate G: Enterprise launch readiness approved, production release

Phases 1-6 are sequential. Phase X inserts between Phase 0 and Phase 1.
Total wall-clock: 126-187 min (20-29 parallel subagent batches)
```

---

## 14. Launch Readiness Criteria

All of the following must be satisfied before production release:

- **Gates A, A+, B, C, D, E, F, G** all passed with documented evidence
- **Critical incidents** recover within defined SLA in live drills (no sim)
- **Governance and compliance signoff** complete (legal, security, audit)
- **KPI thresholds met** in two stable release cycles (canary + shadow)
- **Deterministic replay** test suite passes on 1000+ runs (100% consistency)
- **All FRs 1-24 + all new FRs 25-42** demonstrated in production behavior
- **All NFRs 1-8 + all new NFRs 9-16** measured within 5% of target
- **Policy bypass and signature tamper tests** pass
- **Burst load simulations** validate adaptive cap correctness
- **Shift handoff continuity drills** pass (snapshots created, confirmed, no stale ownership)
- **Operator comprehension study** shows 85%+ action correctness on trained cohort

---

## 15. Post-Launch Criteria

Success metrics for the first 90 days of production:

- **No unresolved critical risks** without explicit business acceptance (risk register)
- **Temporary controls deprecated** per published sunset plan on schedule
- **Handoff to long-term owners** complete with runbook certification by SRE team
- **TRAFFIC KPI targets sustained** for 28 consecutive days
- **Operator burden** reduced vs baseline (alert dedup validated, interruption count measured)
- **Cost optimization** shows >= 15% cost reduction from RouteLLM (conservative target)
- **Rollback success rate** >= 99% measured on production rollbacks (not just drills)
- **Zero silent contract downgrades** in audit trail (all degradations logged)
- **Provider scoring model** continuously updated with >= 80% replay accuracy
- **Continuity watchdog** activations < 1 per week (stale ownership is rare)

---

## 16. Traceability Matrix

### FR → Work Package → Pattern → Test Category

| FR ID | Requirement | WP(s) | Primary Pattern(s) | Test Category | Status |
|-------|-----------|-----|----|----|----|
| FR-001 | Dependency-aware deterministic routing | WP-1001 | P-023, P-065 | Routing correctness, determinism | Design |
| FR-002 | Idempotent execution envelopes | WP-1003 | P-036 | Idempotency, retry safety | Design |
| FR-003 | Policy pre-check before execution | WP-3001 | P-066, P-078 | Policy evaluation latency, correctness | Phase 3 |
| FR-004 | Mandatory evidence collection | WP-3004 | P-019, P-076 | Evidence completeness audit | Phase 3 |
| FR-025 | Contract version negotiation | WP-X1 | P-004, P-062 | Contract registry, versioning | Phase X |
| FR-026 | CSM normalization | WP-X2 | P-001, P-002 | Schema normalization, adapter tests | Phase X |
| FR-027 | Incremental XML parser | WP-X3 | P-013, P-014, P-015 | Parser stress, streaming, malformed XML | Phase X |
| FR-028 | Semantic validation | WP-X4 | P-007, P-011 | Cross-tag invariants, phase rules | Phase X |
| FR-029 | Provider conformance | WP-X5 | P-020, P-008 | Golden corpus (gemini/copilot/codex/claude) | Phase X |
| FR-030 | Fallback SLO budgets | WP-X6 | P-018, P-016 | Fallback state machine, SLO adherence | Phase X |
| FR-031 | Dual-read/dual-write migration | WP-X8 | P-047, P-048 | Canary ramp, zero-downtime migration | Phase X |
| FR-032 | Multi-agent mode selection | WP-Y1 | P-050, P-052, P-053, P-054 | Mode selection, conflict resolution | Phase 1 |
| FR-033 | ABAC policy expressions | WP-3001 | P-068 | Fine-grained policy evaluation | Phase 3 |
| FR-034 | DLQ poison pill detection | WP-Y2 | P-042 | DLQ correctness, poison pill detection | Phase 2 |
| FR-035 | Chaos framework | WP-Y3 | P-043 | Chaos injection (partition, timeout, corruption) | Phase 2 |
| FR-036 | Cost tracking per-run | WP-Y4 | P-083, P-025 | Cost aggregation, budget alerts, RouteLLM | Phase 5 |
| FR-037 | Speculative execution | WP-5001 | P-027 | Dual-provider, take-first correctness | Phase 5 |
| FR-038 | Prompt-characteristic routing | WP-Y8 | P-024, P-087 | Complexity/domain/length classification | Phase 5 |
| FR-039 | Autonomy gradient dial | WP-4001 | P-091, P-114 | Autonomy control, agent-vs-human labeling | Phase 4 |
| FR-040 | Pre-flight simulation | WP-4003 | P-097 | Dry-run correctness, reversibility prediction | Phase 4 |
| FR-041 | Calibration curves | WP-4008 | P-098 | Confidence/approval correlation, threshold tuning | Phase 4 |
| FR-042 | Hierarchical prompt orchestration | WP-Y5 | P-059 | 4-level hierarchy, inheritance + bounded override | Phase 3 |

### NFR → Measurement Method → SLO Target → Alert Threshold

| NFR ID | Requirement | Measurement | Target | Alert |
|--------|----|----|----|----|
| NFR-001 | P95 routing latency | Span traces from routing service | < 250ms | > 300ms |
| NFR-009 | Parse + normalize latency | CSM normalizer span times | < 50ms p95 | > 75ms |
| NFR-010 | Schema drift detection | Drift event latency | < 60s | > 90s |
| NFR-011 | Fallback success rate | Fallback state machine analytics | >= 99% | > 1% failure |
| NFR-013 | OTel GenAI compliance | Trace attribute validation | 100% | < 99% |
| NFR-014 | Structured JSON logging | Log format validation | 100% | < 99% |
| NFR-015 | EU AI Act risk tagging | Compliance audit + audit scan | 100% in critical | Any untagged |
| NFR-016 | Cost reduction @ quality | Provider scoring A/B test | >= 20% | < 15% |

---

## 17. Cross-References

- **WBS Details:** `thegent-wbs-final.md` (complete work package catalog)
- **DAG Dependencies:** `thegent-dag-final.md` (phase dependency graph + critical paths)
- **Research Synthesis:** `thegent-mega-research-synthesis-2026-02-14.md` (114 patterns, codebase exploration, SOTA research)
- **Orchestration Reference:** `thegent-orchestration-optimization-prd.md` (legacy monolith PRD for historical context)
- **Pattern Catalog:** All 114 transferable patterns cross-referenced in mega-synthesis Part 5

---

## 18. Compliance and Governance

### Frameworks Addressed

- **EU AI Act:** Risk classification tagging (NFR-015), transparency requirements, explainability mandates, human oversight paths
- **SOC 2:** Controls mapped to trust service criteria (P-073), evidence collection aligned with audit requirements
- **GDPR:** Data residency respected, right to explanation implemented, retention policies enforced by domain (P-079)

### Audit Trail Properties

- **Immutable append-only** with vector-clock ordering (P-069)
- **Causal tracing** via vector clocks or Lamport timestamps in distributed execution
- **Evidence hashing** for tamper detection (SHA256 content hash)
- **Policy version tracking** on every evaluation (enables replay + compliance review)
- **Compliance tagging** by framework (GDPR, SOC 2, EU AI Act, etc.)

---

## 19. Key Success Factors

1. **Contract Integrity:** Phase X hardening ensures no provider output drift corrupts downstream systems
2. **Observable Failure Recovery:** MAST 14-mode taxonomy + TRAFFIC KPIs enable surgical recovery without over-gating
3. **Operator Empowerment:** Mission Control + progressive disclosure + calibration curves enable confident decision-making
4. **Cost-Quality Balance:** Per-run tracking + RouteLLM optimization enable data-driven provider routing without sacrificing quality
5. **Governance Automation:** OPA/Rego + OPAL distribution + EU AI Act tagging enable compliance without manual overhead
6. **Continuous Learning:** Provider scoring, calibration curves, and chaos drills ensure system adapts to production reality

---

## 20. Known Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Over-gating slows execution | Throughput degradation | Medium | Risk-tiered gates + low-risk fast lanes (P-078, WP-3001) |
| Adaptive scaling oscillation | Stability instability | Medium | Hysteresis + damped cap adjustments (WP-5002) |
| Alert fatigue overwhelms ops | Operator burnout, missed alerts | High | Correlation-first + per-operator ceiling (P-094, P-095) |
| Continuity drift across shifts | Loss of ownership chain | Medium | Mandatory snapshots + watchdog escalation (P-111, WP-4006) |
| Schema drift silent failures | Data corruption, unreproducibility | Medium | Contract telemetry + drift detection (P-019, WP-X7) |
| Provider outage cascades | Total system failure | Low | LiteLLM chains + per-provider circuit breakers (P-022, P-034) |
| Recovery mechanism corruption | Inability to recover | Very Low | External recovery service (P-100, WP-2001) |

---

## 21. Document Metadata

- **Version:** 2.0 (Comprehensive Rewrite)
- **Synthesis Date:** 2026-02-14
- **Research Basis:** 18 research agents (11 codebase explorations + 7 industry research streams)
- **Total Patterns Extracted:** 114 (organized across 9 domains)
- **Total Work Packages:** 64 (8 phases including new Phase X)
- **Total Functional Requirements:** 42 (24 original + 18 new)
- **Total Non-Functional Requirements:** 16 (8 original + 8 new)
- **Total Test Categories:** 14 (225-320 estimated new tests)
- **Estimated Implementation Effort:** 440-655 tool calls, 126-187 min wall clock (20-29 parallel subagent batches)
- **Critical Leverage Points:** 22 ranked by impact and implementation order (Rank 1-22)

---

**This PRD is frozen and ready for implementation. All research gaps closed. All leverage points mapped. Production launch phase gates defined. Compliance frameworks addressed. Success metrics quantified.**
