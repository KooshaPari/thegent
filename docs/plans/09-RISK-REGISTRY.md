# 09 — Risk Registry & Anti-Patterns

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [05-ARCH](./05-ARCHITECTURE.md) | [03-DAG](./03-UNIFIED-DAG.md)

---

## Anti-Patterns to Prevent (15)

These anti-patterns were identified across 11 codebase explorations and 7 research streams. Each has a documented prevention strategy.

| # | Anti-Pattern | Prevention | WP |
|---|-------------|------------|-----|
| AP-01 | Schema-last development (contracts defined after code) | Contract-first mandate: CSM schema before implementation | WP-X2 |
| AP-02 | Doc-code mismatch (docs say PascalCase, code uses snake_case) | Code-is-contract; generate docs from schema; conformance tests | WP-X1 |
| AP-03 | Regex-only XML parsing (fragile under malformed LLM output) | XMLPullParser with sloppy-xml fallback; incremental parser; streaming validation | WP-X3 |
| AP-04 | Single-provider routing (no fallback on failure) | Provider chains with cost/time bounds; circuit breaker per provider; ordered fallback with SLA | WP-1001 |
| AP-05 | Flat failure taxonomy (7 classes too coarse for targeted recovery) | MAST 14-mode with mapped playbooks per mode; per-mode SLA and retry budget | WP-2005 |
| AP-06 | Infinite retry without DLQ (retry loops consume resources) | DLQ + poison pill detection after 3 identical failures; cost tracking; mandatory escalation | WP-Y2 |
| AP-07 | Code-embedded policy (policies hardcoded in business logic) | Declarative OPA/Rego policies; Git-versioned; OPAL auto-deployment; CI testing of policy rules | WP-3001 |
| AP-08 | Confidence without calibration (reported confidence unreliable) | Calibration curves per adapter type; windowed accuracy tracking; policy gates use calibrated_confidence field | WP-4008 |
| AP-09 | Recovery within failing agent (agent tries to self-recover) | External recovery service; separate Recovery DAG; escalation gate if recovery fails | WP-2004 |
| AP-10 | Alert storm without correlation (every event triggers alert) | Correlation-first alerting with dedup windows and ceiling (5/hr/operator); event grouping by root cause | WP-4004 |
| AP-11 | All-or-nothing rollback (roll back entire execution) | Graduated rollback: selective revert to last good checkpoint per failed component | WP-2001 |
| AP-12 | Implicit state changes (transitions without guards) | Explicit state machine with typed transition guards; pre-transition validation; immutable state snapshots | WP-1004 |
| AP-13 | One-size-fits-all display (same detail level for all roles) | Persona-based progressive disclosure (3 tiers: operator/incident/audit); role-aware APIs | WP-4002 |
| AP-14 | Hardcoded resilience logic (retry/fallback mixed into business) | DI-composed resilience stack: retry → fallback → CB → budget; declarative config per failure mode | WP-2003 |
| AP-15 | Endpoint explosion (one tool per operation) | Consolidated tools with operation enums and typed constraints | — |

---

## Risk Registry (17 Risks)

### R-001: Over-Gating Slows Execution
- **Likelihood**: Medium | **Impact**: High
- **Description**: Too many policy gates introduce latency and friction
- **Mitigation**: Risk-tiered gates — low-risk gets fast lane (no gate), medium gets async gate, high gets sync gate
- **Monitoring**: Gate latency KPI; escalation count per risk tier
- **WP**: WP-3001, WP-1002

### R-002: Adaptive Scaling Oscillation
- **Likelihood**: Medium | **Impact**: Medium
- **Description**: Cap adjustments oscillate between normal and adaptive mode
- **Mitigation**: Hysteresis with minimum dwell time; damped cap adjustments
- **Monitoring**: Mode transition frequency; oscillation detection alert
- **WP**: WP-5001, WP-5002

### R-003: Operator Alert Overload
- **Likelihood**: High | **Impact**: Medium
- **Description**: Too many alerts from multiple subsystems overwhelm operators
- **Mitigation**: Correlation-first alerting; dedup windows; per-operator ceiling (5/hr)
- **Monitoring**: Alerts-per-hour metric; snooze frequency
- **WP**: WP-4004

### R-004: Continuity Drift Across Shifts
- **Likelihood**: Medium | **Impact**: High
- **Description**: Critical tasks lose context when ownership changes
- **Mitigation**: Mandatory continuity snapshots; incoming-owner confirmation; watchdog escalation
- **Monitoring**: Snapshot coverage; stale-owner incidents
- **WP**: WP-4006, WP-5005, WP-5006

### R-005: Contract Version Fragmentation
- **Likelihood**: Medium | **Impact**: High
- **Description**: Multiple contract versions in production cause normalization failures
- **Mitigation**: Version negotiation at connection time; compatibility matrix; migration controller
- **Monitoring**: Active version count; normalization failure rate per version
- **WP**: WP-X1, WP-X8

### R-006: Provider Output Shape Drift
- **Likelihood**: High | **Impact**: Medium
- **Description**: AI providers change output format without notice
- **Mitigation**: Snapshot drift tests; adapter conformance suite; drift alarms within 60s
- **Monitoring**: Adapter confidence scores; drift event frequency
- **WP**: WP-X5, WP-X7

### R-007: Audit Trail Corruption
- **Likelihood**: Low | **Impact**: Critical
- **Description**: Audit trail modified or corrupted, compromising compliance
- **Mitigation**: Hash-chained events with WORM storage; integrity verification on read
- **Monitoring**: Hash chain integrity check (periodic); write-once policy enforcement
- **WP**: WP-3004

### R-008: Cascade Failure from Provider Outage
- **Likelihood**: Medium | **Impact**: High
- **Description**: Single provider outage cascades to all routing
- **Mitigation**: Per-provider circuit breakers; bulkhead isolation; independent state
- **Monitoring**: Circuit breaker state dashboard; provider health probes
- **WP**: WP-2003

### R-009: Silent Contract Downgrade
- **Likelihood**: Medium | **Impact**: Critical
- **Description**: Critical lane uses fallback/degraded contract without operator awareness
- **Mitigation**: Contract downgrade blocked in critical lanes (DAG invariant 6); audit alert
- **Monitoring**: Fallback rate per lane; zero-tolerance in critical paths
- **WP**: WP-X6, NFR-012

### R-010: Governance Policy Drift
- **Likelihood**: Medium | **Impact**: Medium
- **Description**: Active policies diverge from intended baseline over time
- **Mitigation**: Policy drift detection sweep; blocked promotion on critical drift
- **Monitoring**: Drift score; policy version delta
- **WP**: WP-3005

### R-011: Cost Runaway from Speculative Execution
- **Likelihood**: Low | **Impact**: Medium
- **Description**: Speculative dual-provider calls double cost without proportional benefit
- **Mitigation**: Cost tracking with budget alerts; speculative mode only for latency-critical
- **Monitoring**: Cost per task; speculative hit rate
- **WP**: WP-Y4, WP-5001

### R-012: Multi-Agent Deadlock
- **Likelihood**: Low | **Impact**: High
- **Description**: Multi-agent modes deadlock on conflicting outputs with no resolution
- **Mitigation**: Timeout-bounded consensus; majority vote fallback; escalation on tie
- **Monitoring**: Mode completion time; deadlock timeout count
- **WP**: WP-Y1

### R-013: Regex-Based Failure Classification Fragility
- **Likelihood**: Medium | **Impact**: Medium
- **Description**: Resilience layer uses regex patterns to classify failures (rate limit vs transient vs usage); patterns drift as providers change error messaging
- **Mitigation**: Maintain versioned failure pattern ruleset with provider-specific overrides; CI test suite validates classification against provider samples; alert on classification mismatches
- **Monitoring**: Classification accuracy per provider; unrecognized error pattern frequency; provider-specific error rate variance
- **WP**: WP-1001, WP-2003
- **Code Reference**: `src/thegent/agents/resilience.py` lines 35-60 (_RETRYABLE_PATTERNS, _USAGE_LIMIT_PATTERNS)

### R-014: Provider Exhaustion Without Bounded Cost
- **Likelihood**: Medium | **Impact**: High
- **Description**: State machine attempts all configured providers sequentially without time/cost budget enforcement; cascade of failures can consume significant resources before terminating
- **Mitigation**: Add per-run cost budget tracker; halt provider loop if cost exceeds threshold; per-provider timeout (not just retry delay); maximum wall-clock time for full provider chain
- **Monitoring**: Total run cost distribution; provider-chain completion time p99; cost overage incidents
- **WP**: WP-2003, WP-5001
- **Code Reference**: `src/thegent/agents/state_machine.py` lines 88-207 (run loop has no cost/time bounds)

### R-015: Silent Degradation on Provider Exhaustion
- **Likelihood**: Medium | **Impact**: Critical
- **Description**: When all providers exhausted, state machine accepts output "despite violations" without operator visibility; violations are logged but action proceeds with reduced contract fidelity
- **Mitigation**: Explicit acceptance gate with human approval required for any degraded output; raise non-retryable error instead of silent acceptance; audit alert for acceptance-despite-violations
- **Monitoring**: Acceptance-despite-violations count; fallback-acceptance rate per lane; audit log of all acceptances
- **WP**: WP-3001, WP-4004
- **Code Reference**: `src/thegent/agents/state_machine.py` lines 196-205 (silent acceptance logic)

### R-016: Missing Adapter Registration and Provider Detection
- **Likelihood**: Low | **Impact**: High
- **Description**: New providers can be added to routing without registered adapters; runtime discovery fails with generic errors instead of early detection
- **Mitigation**: Provider registry with mandatory adapter registration; CI lint rule that blocks provider references without adapters; startup validation of adapter availability
- **Monitoring**: Adapter-provider mismatch events; unregistered provider usage attempts
- **WP**: WP-X1, WP-X5
- **Code Reference**: `src/thegent/contracts/adapters.py` (no registry enforcement), `src/thegent/agents/registry.py`

### R-017: Fallback Confidence Score Calibration Drift
- **Likelihood**: Medium | **Impact**: Medium
- **Description**: Confidence scores from different adapter normalizations (XMLAdapter vs fallback-plain) are not on same scale; policy gates use uncalibrated scores for approval decisions
- **Mitigation**: Calibration curve per adapter type; windowed accuracy tracking against actual outcomes; policy gates reference calibrated_confidence, not raw confidence; recalibration alert if divergence detected
- **Monitoring**: Calibration factor per adapter; prediction vs actual accuracy delta; policy decision distribution by confidence tier
- **WP**: WP-4008, WP-X5
- **Code Reference**: `src/thegent/contracts/adapters.py` (confidence 0.0-1.0 arbitrary), `src/thegent/contracts/policy.py` lines 40-43 (uses uncalibrated confidence)

---

## Failure Mode Mapping

Map from MAST 14-mode failure taxonomy to recovery strategy:

| Mode | Category | Detection | Recovery | Escalation | Prevention |
|------|----------|-----------|----------|------------|-----------|
| F-01 | Infra: Network | Timeout/ConnectionError | Retry + exponential backoff (max 3 attempts, max 60s) | Circuit breaker → DLQ | Provider-specific network guards (timeout per provider config) |
| F-02 | Infra: Storage | IOError/PermissionError | Failover to replica; checkpoint recovery | Checkpoint replay from last valid state | Pre-flight storage availability check; replica health monitoring |
| F-03 | Infra: Rate limit | 429/RateLimitError; regex pattern match | Backpressure + provider rotation; wait Retry-After header if present | Provider rotation with cost tracking | Global rate limit budget per provider; preemptive throttle at 80% |
| F-04 | Model: Hallucination | Validation failure (semantic or structural) | Re-prompt with grounding context (previous outputs, constraints) | Human review with evidence context | Confidence calibration; semantic validation gates |
| F-05 | Model: Refusal | Safety filter trigger (provider-specific patterns) | Rephrase prompt; fallback to alternative provider | Skip action with audit reason code | Content policy pre-check; rephrase attempt before fallback |
| F-06 | Model: Context overflow | Token limit error (explicit or inferred) | Summarize context window; retry with chunked input | Chunking strategy with recursive aggregation | Per-provider token limit tracking; proactive summarization |
| F-07 | Model: Format violation | Schema validation fail; parse errors | Re-prompt with schema example; fallback parser with confidence reduction | Accept fallback-plain if no alt provider (audit alert) | Provider conformance tests; adapter regression suite |
| F-08 | Tool: Execution failure | Exception in tool invocation; non-zero exit code | Retry same tool (2 attempts); fallback to alternative tool | Manual fallback with escalation | Tool pre-flight checks; sandbox capability validation |
| F-09 | Tool: Misuse | Capability check fail; insufficient args | Re-plan with corrected tool selection | Agent role swap to higher capability | Capability matrix per agent; pre-execution validation |
| F-10 | Logic: Goal drift | Semantic divergence from original objective (NLP check) | Checkpoint rollback to last valid state; re-plan | Re-plan from scratch with new decomposition | Periodic goal consistency check; intermediate validation |
| F-11 | Logic: Loop/oscillation | Step counter exceeded (default 50); repeated state detection | Force termination of current attempt | DLQ + alert + manual investigation | Loop detection with early bail at 60% of max; state transition tracking |
| F-12 | Logic: Conflicting agents | Conflict detection via output diff | Majority vote if N≥3 agents; consensus resolution | Human arbitration if tie or N<3 | Consensus algorithm pre-configuration; conflict scoring |
| F-13 | Security: Prompt injection | Pattern detection (regex rules + NLP) | Quarantine action + full audit trail + incident notification | Incident response team activation | Input sanitization layer; prompt validation before execution |
| F-14 | Security: Data exfiltration | Egress monitoring (network policies, log scanning) | Block + audit; disable agent if repeated | Incident response + credential rotation | Network segmentation; egress whitelisting; data loss prevention scanning |

---

## Known Technical Debt

This section catalogs current code-level risks that must be resolved before production launch.

### Category 1: Resilience and Failure Classification

| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-01 | `src/thegent/agents/resilience.py:35-60` | Failure classification uses hard-coded regex patterns; no versioning or provider-specific overrides | Implement versioned failure pattern ruleset with provider profiles; add CI validation tests | WP-1001 gate |
| TD-02 | `src/thegent/agents/state_machine.py:88-207` | Provider loop has no time or cost bounds; could exhaust budget on cascading failures | Add per-run cost budget tracker and wall-clock timeout enforcement | WP-2003 gate |
| TD-03 | `src/thegent/agents/state_machine.py:196-205` | Silent acceptance of violations when all providers exhausted; minimal logging | Raise explicit error requiring manual gate approval for any degraded output | WP-3001 gate |

### Category 2: Adapter and Contract Management

| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-04 | `src/thegent/contracts/adapters.py` | No mandatory adapter registration for new providers; runtime discovery fails late | Implement provider registry with CI lint rule blocking unregistered providers | WP-X1 gate |
| TD-05 | `src/thegent/contracts/adapters.py:15-23` | Confidence scores from different adapters not calibrated to same scale | Add calibration curves per adapter type; track accuracy vs predicted confidence | WP-4008 gate |
| TD-06 | `src/thegent/contracts/policy.py:40-43` | Policy gates use uncalibrated raw confidence scores | Change policy decision gates to use calibrated_confidence field from adapter result | WP-3001 gate |

### Category 3: State and Audit Trail

| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-07 | `src/thegent/execution.py:78-210` | Hash chain only covers runs; governance events/overrides not in chain | Extend hash chain to all audit events; implement WORM storage for immutable trail | WP-3004 gate |
| TD-08 | `src/thegent/agents/state_machine.py:140-200` | Semantic validation failures are logged but not committed to audit trail | Make semantic validation failures immutable audit events; block transition on failure in critical lanes | WP-1004 gate |
| TD-09 | `src/thegent/contracts/telemetry.py` (not yet read) | Fallback rate tracking is per-invocation; no windowed trend detection | Implement sliding window fallback rate tracking with upward-trend alerts | WP-4004 gate |

### Category 4: Recovery and Orchestration

| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-10 | `src/thegent/agents/state_machine.py` (recovery path) | Recovery from partial execution state is implicit; no formal state recovery protocol | Document and implement explicit recovery state machine with checkpoint replay | WP-2004 gate |
| TD-11 | `src/thegent/contracts/validation.py:20-52` | Semantic validation checks are static rules; no provider-specific or context-aware validation | Add validation context parameter; support provider-specific validation profiles | WP-X5 gate |

**Total Technical Debt Items**: 11
**Critical Path Items (WP gates)**: 7
**Target Resolution**: All items resolved before phase 3 governance gate (WP-3001)

---

## Operational Safeguards

### Pre-Launch Checklist

#### Resilience & Failure Handling
- [ ] All circuit breakers configured per provider with per-provider thresholds (not defaults)
- [ ] Failure classification patterns tested against 50+ real provider errors per adapter
- [ ] Cost tracking implemented; per-run and per-provider cost budgets enforced with alerts
- [ ] Provider loop time bounds set (max 5 min wall-clock per full chain attempt)
- [ ] Chaos tests pass for all MAST modes F-01 through F-14 with recovery validation
- [ ] Poison pill detection (3 consecutive identical errors) tested and logged
- [ ] All provider fallback chains tested end-to-end with circuit breaker trips

#### Policy, Governance & Audit
- [ ] All policy gates tested with bypass attempts and tamper tests
- [ ] OPA policy rules tested in CI (100% rule coverage with valid/invalid inputs)
- [ ] Hash chain integrity verified (test file modification detection)
- [ ] Immutable audit trail generates events for: policy gate, override, rollback, semantic validation
- [ ] Audit chain integrity check endpoint tested and monitored
- [ ] Override TTL mechanism tested; expired overrides correctly rejected
- [ ] Policy drift detection sweep runs and produces alerts on detected drift

#### Contracts & Adapters
- [ ] All registered providers have adapters; unregistered provider reference blocks CI build
- [ ] Adapter confidence calibration validated (ECE < 0.15 for each adapter type)
- [ ] Schema drift tests pass for all adapter outputs (structural + semantic validation)
- [ ] Fallback-plain path tested with confidence thresholds; low-confidence outputs logged
- [ ] Provider-specific error patterns documented and versioned in resilience module

#### Operations & Monitoring
- [ ] Alert ceiling configured (5/hr/operator) with dedup and correlation rules
- [ ] Alerting tested for: circuit breaker trips, fallback rate >10%, cost overage, hash chain breaks
- [ ] Continuity snapshots verified at shift boundaries; stale-owner watchdog armed
- [ ] Rollback tested for each critical lane (selective rollback, not all-or-nothing)
- [ ] Cost budget alerts configured at 80% and 95% thresholds
- [ ] Runbook reviewed and certified by platform/SRE and governance teams
- [ ] On-call rotation established with escalation SLA per risk tier
- [ ] Observability dashboards deployed and tested (latency, throughput, error rates by mode)

#### Pre-Flight & Deployment
- [ ] Load test on critical lanes passes (maintain p95 latency within SLO under normal+burst)
- [ ] Canary deployment validated in low-criticality domain before stage 1 rollout
- [ ] Replay test suite passes (deterministic routing, no non-deterministic promotion)
- [ ] Manual intervention paths tested end-to-end (human-in-the-loop scenarios)
- [ ] Compliance evidence retention policies verified (GDPR/SOC2/SOX/PCI timelines)
- [ ] Security: no secrets in audit trails; all PII redacted in logs
- [ ] All technical debt items (TD-01 through TD-11) resolved and gate-signed

### Runtime Guardrails

| Guardrail | Threshold | Action | SLA | Monitoring |
|-----------|-----------|--------|-----|-----------|
| Fallback rate | > 10% global (7-day window) | Alert + investigation trigger | 30 min investigation SLA | Hourly trend dashboard; alert on 2-std upward spike |
| Fallback rate per provider | > 30% per provider | Page on-call; provider rotation if sustained | 15 min response | Provider-specific fallback rate tracked independently |
| Circuit breaker OPEN state | Any critical provider CB open | Page on-call immediately | 5 min response; 30 min recovery SLA | Circuit state dashboard; per-provider health probes every 10s |
| Audit chain hash break | Any detected integrity failure | Critical alert + STOP all writes; incident response | Immediate escalation | Integrity check job runs every 5 min; cryptographic verification on read |
| Semantic validation failure | In critical lane | Reject action + escalate to human gate | 15 min escalation SLA | All semantic failures to audit trail; blocked in critical lanes by default |
| Stale ownership | > 4 hours | Watchdog escalation to next owner or incident lead | 30 min escalation SLA | Ownership timestamp checked every 30 min; alert at 3.5 hours |
| Policy evaluation latency | > 100ms p95 (last 100 runs) | Cache warm + investigate rule complexity | Latency SLA <100ms p95 | Per-rule latency breakdown in metrics; slow-rule detection |
| DLQ depth | > 50 items | Alert + manual review queue | 4 hour manual review SLA | DLQ depth metrics; automatic escalation if >100 items |
| Cost per hour | > 120% of daily budget / 24 | Alert + throttle non-critical concurrency | Cost alert SLA <15 min | Per-hour cost tracking; daily carryover rules |
| Cost per run (max) | > 50 USD (anti-runaway) | Terminate execution + escalate | Hard limit at 50 USD per run | Per-run cost tracking; budget enforcement at gate |
| Provider error rate | > 20% error rate (last 100 runs) | Page on-call; begin provider fallback | 10 min response SLA | Error rate per provider; alert on threshold breach |
| Mode deadlock | > 5 min timeout in multi-agent | Force resolution + alert | Timeout hard-enforced at 5 min | Mode completion time tracked; timeout count alerted daily |
| Rollback failure | Any rollback that fails | Incident response + manual intervention | 30 min response SLA | All rollback attempts logged; failure escalates immediately |
| Recovery exhaustion | > 3 failed recovery attempts | Human escalation to incident lead | 10 min escalation SLA | Recovery attempt count per run; escalation trigger at 3 |
| Confidence below threshold | < 0.3 calibrated confidence in critical lane | Block action + escalate | Blocking enforced at policy layer | Confidence distribution metrics; below-threshold rate tracked |

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](./00-MASTER-INDEX.md) — plan index
- [03-UNIFIED-DAG.md](./03-UNIFIED-DAG.md) — DAG and recovery
