# Comprehensive Test Plan Matrix

**Status:** Expanded to include 14 new test categories from mega-synthesis
**Date:** 2026-02-14
**Source:** Thegent Mega Research Synthesis Part 6 + original PRD test plan
**Baseline:** 24 FRs + 8 NFRs from `thegent-prd-final.md`
**Expansion:** 18 new FRs + 8 new NFRs + 14 new test categories from research

---

## Executive Summary

This test plan expands the baseline test matrix from 24 FRs and 8 NFRs to a comprehensive 42 FR + 16 NFR coverage with 14 new test categories discovered during multi-agent research synthesis. The plan includes:

- **225-320 estimated new test cases** across 14 categories
- **3-tier test pyramid**: 70% unit, 20% integration, 10% e2e
- **Chaos engineering scenarios** with fault injection specifications
- **Golden corpus references** for test data locations
- **Cross-linkage** of all tests to FRs, WPs, and patterns

---

## Part 1: Original Functional Requirements → Test Gates

**These 24 FRs remain the core baseline.**

| FR ID | Requirement | Test Type | Acceptance Criteria | Test Location | New Tests |
|-------|-------------|-----------|---------------------|---------------|-----------|
| FR-001 | Dependency-aware deterministic routing | Integration | Same input → same route; deps respected | test_e2e_cli, dag | — |
| FR-002 | Idempotent execution envelopes | Unit, E2E | Duplicate token → reuse; no double exec | test_e2e_cli, idempotency_tests | test_idempotency_key_content_hash |
| FR-003 | Policy pre-check before execution | Integration | Policy block → hold; allow → proceed | policy, execution | test_policy_eval_latency |
| FR-004 | Mandatory evidence collection | E2E | done without evidence → validate fails | test_e2e_cli | test_evidence_collection_completeness |
| FR-005 | Integrity and regression gates | E2E | dag probe detects drift | test_e2e_cli | test_contract_drift_detection |
| FR-006 | Checkpoint rollback | E2E | rollback restores state | test_e2e_cli, checkpoint_tests | test_checkpoint_replay_correctness |
| FR-007 | Retry and circuit-breaker by failure class | Unit | Retry on transient; circuit on sustained | resilience, circuit_breaker_tests | test_circuit_breaker_3state |
| FR-008 | Recovery playbook by known pattern | E2E | dag recover actions work | test_e2e_cli, recovery_tests | test_recovery_playbook_selection |
| FR-009 | Human oversight for repeated failures | Integration | Exhausted retries → oversight path | — | test_human_oversight_escalation |
| FR-010 | Signed action artifacts | Unit | history verify passes | test_e2e_cli | test_artifact_signing |
| FR-011 | Override controls with reason and expiry | E2E | --override with reason works | — | test_override_ttl_revalidation |
| FR-012 | Immutable audit event trail | Integration | Hash chain integrity | history verify | test_audit_trail_immutability |
| FR-013 | Policy drift detection | Integration | Sweep detects drift | — | test_policy_drift_detection |
| FR-014 | Trust boundary validation | Integration | Env transition validated | — | test_trust_boundary_validation |
| FR-015 | Concise and detailed explanation tiers | UX | Rationale visible | cockpit | test_progressive_disclosure_tier_1_2_3 |
| FR-016 | One-click safe fallback | E2E | dag recover fallback works | test_e2e_cli | test_fallback_pause_rollback_escalate |
| FR-017 | Stale-state execution block | Integration | Stale → block | dag validate | test_stale_state_block |
| FR-018 | Continuity snapshot and handoff | Integration | Snapshot has owner, ETA | cockpit | test_handoff_continuity_snapshot |
| FR-019 | Adaptive load controls | Load | Burst → reduce noncritical | — | test_burst_load_smoothing |
| FR-020 | Non-critical deferral with ETA | Integration | Deferral includes ETA | — | test_deferral_eta_accuracy |
| FR-021 | Continuity watchdog | Integration | Stale owner → alert | — | test_continuity_watchdog_stale_owner |
| FR-022 | Decision replay with rationale | UX | Rationale in history | history | test_decision_replay_4capability |
| FR-023 | Role-aware confidence calibration | UX | Feedback stored | feedback | test_calibration_curve_tracking |
| FR-024 | Closure pack generation | Integration | Pack includes evidence | — | test_closure_pack_evidence |

---

## Part 2: New Functional Requirements (FR-025 through FR-042)

**These 18 new FRs from synthesis enable contract management, multi-agent coordination, and advanced routing.**

| FR ID | Requirement | Source | Test Type | Acceptance Criteria | Test Location | Est. Tests |
|-------|-------------|--------|-----------|---------------------|---------------|-----------|
| FR-025 | Contract version negotiation for all structured outputs | Zen, MCP, task-tool | Unit, Integration | Capability negotiation at connection; version mismatch handled | contract_negotiation_tests | 8 |
| FR-026 | Canonical Structured Message normalization across variants | Zen + task-tool cross-analysis | Unit | 18-tag + 26-tag inputs → uniform CSM | csm_normalization_tests | 12 |
| FR-027 | Incremental XML parser with recoverable partial-state | XML streaming research | Unit | XMLPullParser feed/read cycle, sloppy-xml fallback | parser_streaming_tests | 15 |
| FR-028 | Semantic validation with cross-tag invariants | Task-tool, Zen | Unit | STATUS=completed requires ACTIONS; phase-aware rules | semantic_validation_tests | 10 |
| FR-029 | Provider adapter conformance tests + output drift alarms | Pheno-SDK, multi-provider research | Integration | Per-provider test vectors; drift events emitted | provider_conformance_tests | 20 |
| FR-030 | Policy-governed fallback routing with explicit SLOs | Pheno, LiteLLM | Integration | Fallback chain: primary → degraded → fallback → recovered | fallback_policy_tests | 12 |
| FR-031 | Dual-read/dual-write migration for contract upgrades | Zen migration patterns, canary | Integration | Accept old+new, emit both, then deprecate | contract_migration_tests | 10 |
| FR-032 | Multi-agent mode selection (sequential/parallel/hierarchical) | Kagentop, CrewAI | Unit, Integration | Mode-selection policy applied; transitions verified | multi_agent_mode_tests | 15 |
| FR-033 | ABAC policy expressions for fine-grained routing | OPA/Rego research | Unit | Policies: risk_score + domain + urgency + capability match | abac_policy_tests | 12 |
| FR-034 | Dead-letter queue with poison pill detection | Reliability research | Integration | Failed items route to DLQ; poison pill detected after N retries | dlq_poison_pill_tests | 12 |
| FR-035 | Chaos engineering fault injection for recovery testing | Reliability research | Integration, E2E | Inject: partition, timeout, corruption; measure recovery | chaos_injection_tests | 25 |
| FR-036 | Cost tracking per-run with budget alerts | Observability research | Unit, Integration | Per-run cost aggregation, cost-per-quality ratio, budget alerts | cost_tracking_tests | 10 |
| FR-037 | Speculative execution for latency-critical paths | Multi-provider routing | Integration | Send to 2 providers, take first response, cancel other | speculative_execution_tests | 8 |
| FR-038 | Prompt-characteristic routing (complexity/domain/length) | RouteLLM, Martian | Unit | Classify prompt; route to optimal provider; 20-40% cost reduction | prompt_routing_tests | 15 |
| FR-039 | Autonomy gradient control per domain/lane | UX research | UX | Operators adjust autonomy dial real-time; level persisted | autonomy_gradient_tests | 10 |
| FR-040 | Pre-flight simulation ("dry run") before irreversible | UX research (STRATUS) | UX | Simulation shows predicted outcome, affected resources | preflight_simulation_tests | 8 |
| FR-041 | Calibration curve tracking for confidence tuning | UX research | UX | Track: "70% confidence → 85% actual approval rate" | calibration_curve_tests | 8 |
| FR-042 | Hierarchical prompt orchestration (platform/domain/workflow/step) | Smolagents | Unit | 4-level hierarchy; lower inherits/overrides upper within bounds | prompt_hierarchy_tests | 10 |

**Total new FR test coverage: 16 categories, ~180 tests**

---

## Part 3: Original Non-Functional Requirements → Test Gates

**These 8 NFRs remain the core baseline.**

| NFR ID | Requirement | Test Type | Acceptance Criteria | Test Location | Est. Tests |
|--------|-------------|-----------|---------------------|---------------|-----------|
| NFR-001 | p95 routing latency within SLO | Performance | p95 < threshold under load (see chaos) | perf_tests | 5 |
| NFR-002 | Stable critical-path latency under burst | Load | Critical lane stable across 10x load | load_tests | 5 |
| NFR-003 | No non-deterministic promotion in replay | Integration | Replay → identical state transitions | replay_tests | 3 |
| NFR-004 | Policy checks available in production | Availability | Policy endpoint uptime >= 99.9% | availability_tests | 2 |
| NFR-005 | Rollback within incident SLA | Integration | Rollback < SLA (target: 5min) | rollback_tests | 3 |
| NFR-006 | Continuity snapshots for open critical | Integration | All open critical work has snapshot | continuity_tests | 2 |
| NFR-007 | Audit query within operational SLA | Performance | Query < SLA (target: 100ms p95) | audit_tests | 2 |
| NFR-008 | Operator rationale within UX latency | UX | Render < target (target: 200ms) | ux_tests | 2 |

---

## Part 4: New Non-Functional Requirements (NFR-009 through NFR-016)

**These 8 new NFRs from synthesis address parser latency, contract stability, and provider reliability.**

| NFR ID | Requirement | Source | Test Type | Acceptance Criteria | Test Location | Est. Tests |
|--------|-------------|--------|-----------|---------------------|---------------|-----------|
| NFR-009 | Parse + normalize latency preserved under p95 routing SLO | XML streaming research | Performance | XMLPullParser + sloppy-xml < 50ms p95 | parser_latency_tests | 5 |
| NFR-010 | Schema drift detection within 60 seconds | Contract research | Integration | Drift events emitted within 60s observability window | drift_detection_tests | 3 |
| NFR-011 | Fallback-induced failure rate < 1% | Reliability research | Integration | Degraded mode failure rate remains low | fallback_reliability_tests | 4 |
| NFR-012 | Zero silent contract downgrade in critical lanes | Contract research | Integration | Critical lane blocks on contract mismatch, never silently degrades | contract_enforcement_tests | 5 |
| NFR-013 | OTel GenAI semantic convention compliance on all spans | Observability research | Integration | All orchestration spans include gen_ai.* attributes | otel_compliance_tests | 4 |
| NFR-014 | Structured JSON logging on all orchestration events | Observability research | Integration | 100% of events are JSON with machine-queryable fields | json_logging_tests | 3 |
| NFR-015 | EU AI Act risk classification tagging on orchestration decisions | Governance research | Integration | Every decision tagged with minimal/limited/high/unacceptable | risk_classification_tests | 5 |
| NFR-016 | Provider routing optimization >= 20% cost reduction at maintained quality | Multi-provider research | Performance, Integration | Cost-per-quality ratio improves 20% on test workload | cost_optimization_tests | 4 |

**Total new NFR test coverage: 8 categories, ~33 tests**

---

## Part 5: New Test Categories (14 Categories, 225-320 Tests)

These test categories were derived from the mega-synthesis research and represent previously unmapped areas.

### Test Category 1: Golden Corpus (18-Tag Task-Tool Payloads)

**Source:** task-tool research (a1a2ca1)
**FR Mapping:** FR-025 (contract negotiation), FR-026 (CSM normalization)
**WP Mapping:** WP-X1, WP-X2
**Pattern Mapping:** P-001, P-002, P-003, P-006
**Priority:** P0
**Est. Test Count:** 20-30

**Purpose:** Establish authoritative reference payloads for the 18-tag task-tool contract.

**Concrete Test Cases:**
1. **test_golden_18tag_complete_payload** - Parse task-tool's canonical 18-tag payload (task_id, task_title, task_objective, task_type, dependencies, acceptance_criteria, status, priority, reasoning, implementation_plan, progress_notes, code_changes, test_results, review_notes, issues_found, suggestions, confidence_level, next_steps). Validate all tags present, exactly-once, no extras.
2. **test_golden_18tag_minimal_required** - Parse minimal valid 18-tag payload (only required fields). Validate structural conformance without semantic context.
3. **test_golden_18tag_status_transitions** - Verify status progression through states (pending → in_progress → completed → reviewed) with corresponding tag mutations (PROGRESS increments, ACTIONS_COMPLETED populates, NEXT_STEPS clears).

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/golden_payloads/task_tool_18tag_*.xml`

---

### Test Category 2: Golden Corpus (26-Tag Zen Rich Protocol)

**Source:** Zen XML research (a2392b7)
**FR Mapping:** FR-025, FR-026
**WP Mapping:** WP-X1, WP-X2
**Pattern Mapping:** P-002, P-010
**Priority:** P0
**Est. Test Count:** 30-40

**Purpose:** Validate Zen's richer 26-tag vocabulary (extends 18-tag with STATUS, PROGRESS, ACTIONS_COMPLETED, ACTIONS_PENDING, FILES_CREATED, FILES_MODIFIED, QUESTIONS, WARNINGS, DEPENDENCIES, SUGGESTIONS, PERFORMANCE_NOTES, TEST_RESULTS, CODE_QUALITY, DOCUMENTATION, ARCHITECTURE_NOTES, SECURITY_CONSIDERATIONS, NEXT_STEPS, BLOCKERS, ASSUMPTIONS, RISKS, ALTERNATIVES_CONSIDERED, DECISION_RATIONALE, CONFIDENCE_LEVEL, ESTIMATED_EFFORT, IMPACT_ASSESSMENT, ROLLBACK_PLAN).

**Concrete Test Cases:**
1. **test_golden_26tag_complete_payload** - Parse Zen's canonical 26-tag payload. Validate all optional extension tags are recognized and typed correctly (e.g., ASSUMPTIONS as list, RISKS as dict, PERFORMANCE_NOTES as string).
2. **test_golden_26tag_confidence_workflow** - CONFIDENCE_LEVEL tag mutation through workflow (initial estimate → revised after issues → final with rationale in DECISION_RATIONALE).
3. **test_golden_26tag_rollback_plan** - Verify ROLLBACK_PLAN tag completeness: lists compensation steps, reversal order, validation checks post-revert.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/golden_payloads/zen_26tag_*.xml`

---

### Test Category 3: Adversarial Malformed XML

**Source:** XML streaming research (a89ae4c)
**FR Mapping:** FR-027 (incremental parser), FR-030 (fallback policy)
**WP Mapping:** WP-X3, WP-X6
**Pattern Mapping:** P-013, P-014, P-015, P-016
**Priority:** P1
**Est. Test Count:** 40-50

**Purpose:** Validate parser resilience under malformed LLM output (unclosed tags, nesting violations, mixed case, truncation mid-element).

**Concrete Test Cases:**
1. **test_parser_unclosed_tag** - Input: `<STATUS>pending<PROGRESS>50%</PROGRESS>` (STATUS never closed). Expected: sloppy-xml fallback extracts STATUS=pending, PROGRESS=50%, emits confidence=0.8 degradation event.
2. **test_parser_truncated_mid_element** - Input: `<CODE_CHANGES><file name="app.py"><change>def hello...` (stream terminates mid-value). Expected: partial-state buffer preserves CHANGE context, allows resume on next chunk, never treats partial as final.
3. **test_parser_duplicate_tags** - Input: `<STATUS>pending</STATUS><STATUS>completed</STATUS>`. Expected: tag cardinality violation detected, second tag rejected, conformance event emitted, governance hold triggered in critical lanes.
4. **test_parser_mixed_case** - Input: `<status>pending</STATUS>` (lowercase open, uppercase close). Expected: sloppy-xml handles case mismatch, extracts, emits confidence penalty.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/adversarial_xml/malformed_*.xml`

---

### Test Category 4: Semantic Inconsistency

**Source:** Zen + task-tool research (a2392b7, a1a2ca1)
**FR Mapping:** FR-028 (semantic validation)
**WP Mapping:** WP-X4
**Pattern Mapping:** P-007, P-011
**Priority:** P1
**Est. Test Count:** 15-20

**Purpose:** Validate cross-tag semantic rules (e.g., STATUS=completed requires non-empty ACTIONS_COMPLETED, PROGRESS=100 requires STATUS in {completed, done}).

**Concrete Test Cases:**
1. **test_semantic_status_actions_consistency** - Input: `<STATUS>completed</STATUS><ACTIONS_COMPLETED></ACTIONS_COMPLETED>`. Expected: semantic validator rejects (completed requires evidence), governance hold, retry with clarification prompt.
2. **test_semantic_progress_status_mismatch** - Input: `<PROGRESS>75</PROGRESS><STATUS>pending</STATUS>`. Expected: conflict detected, suggests status update, emits semantic-drift event.
3. **test_semantic_confidence_risk_correlation** - Input: `<CONFIDENCE_LEVEL>0.3</CONFIDENCE_LEVEL><RISK_LEVEL>minimal</RISK_LEVEL>`. Expected: semantic validator flags inverse correlation, suggests risk=high, escalation event.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/semantic_inconsistency/bad_*.xml`

---

### Test Category 5: Provider-Specific Output Drift

**Source:** Multi-provider research (acd1989), adapter research (a48285d)
**FR Mapping:** FR-029 (provider conformance)
**WP Mapping:** WP-X5
**Pattern Mapping:** P-008, P-020, P-021
**Priority:** P1
**Est. Test Count:** 20-30

**Purpose:** Validate that each provider (Gemini, Copilot, Codex, Claude) produces output conforming to contract; detect and alarm on drift.

**Concrete Test Cases:**
1. **test_provider_gemini_output_conformance** - Submit identical prompt to Gemini adapter. Validate response parses as 18-tag (or higher) contract. Check: tag presence, cardinality, type conformance. Emit conformance event.
2. **test_provider_copilot_drift_vs_baseline** - Compare Copilot output from today vs baseline (golden snapshot from 30 days ago) on identical prompt. Measure: tag additions, field type changes, optional tag removal. Alert if drift_score > threshold.
3. **test_provider_codex_fallback_chain** - Codex adapter fails (simulated timeout). Verify fallback chain: primary (structured) → degraded (partial XML) → fallback (raw text) with confidence decay. Track latency through fallback transitions.
4. **test_provider_claude_scoring_model** - Track Claude's success rate, latency p95, cost per call, capability match over 100 runs. Compute composite score. Verify score updates routing preferences.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/provider_baselines/gemini_baseline_*.json`, `copilot_drift_*.json`, etc.

---

### Test Category 6: MCP Outage and Fallback Transitions

**Source:** Zen resilience (abeb455), MCP spec research (aa77ba1)
**FR Mapping:** FR-030 (policy-governed fallback)
**WP Mapping:** WP-X6
**Pattern Mapping:** P-016, P-018, P-062, P-063
**Priority:** P2
**Est. Test Count:** 10-15

**Purpose:** Verify fallback state machine transitions when MCP connection fails: primary → degraded → fallback → recovered.

**Concrete Test Cases:**
1. **test_mcp_primary_mode_normal** - MCP connection healthy. Structured output response parsed, confidence=1.0, no fallback event.
2. **test_mcp_outage_degrade_to_xml_extraction** - MCP timeout/connection refused. Fall back to raw response XML extraction, confidence=0.8, emit degradation event.
3. **test_mcp_extraction_failure_degrade_to_text** - Raw response is malformed XML. Fall back to text extraction with regex, confidence=0.5, emit secondary degradation.
4. **test_mcp_recovery_restored_to_primary** - After fallback, new MCP request succeeds. Automatic recovery to primary mode, emit recovery event, reset fallback counter.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/mcp_scenarios/outage_*.json`

---

### Test Category 7: Circuit Breaker State Transitions

**Source:** Reliability research (a5ad944), Kimaki DI patterns (ae9b319)
**FR Mapping:** FR-007 (circuit breaker)
**WP Mapping:** WP-2003, WP-2002
**Pattern Mapping:** P-034, P-035, P-044, P-045
**Priority:** P2
**Est. Test Count:** 15-20

**Purpose:** Validate 3-state circuit breaker (CLOSED → OPEN → HALF-OPEN) per provider with configurable thresholds.

**Concrete Test Cases:**
1. **test_circuit_breaker_closed_normal** - Provider healthy. Circuit CLOSED. Requests pass through. Success counter increments.
2. **test_circuit_breaker_closed_to_open** - Provider fails 5 times in 60s (threshold). Circuit transitions CLOSED → OPEN. Subsequent requests fail fast (not sent to provider).
3. **test_circuit_breaker_open_timeout_half_open** - Circuit OPEN for 30s (reset_timeout). Transition OPEN → HALF-OPEN. Next request is probe (sent to provider).
4. **test_circuit_breaker_half_open_success_closed** - 3 consecutive successes in HALF-OPEN. Transition HALF-OPEN → CLOSED. Circuit recovers.
5. **test_circuit_breaker_half_open_failure_open** - Failure during HALF-OPEN probe. Transition HALF-OPEN → OPEN. Reset timer.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/circuit_breaker/state_*.json`

---

### Test Category 8: DLQ and Poison Pill Detection

**Source:** Reliability research (a5ad944)
**FR Mapping:** FR-034 (DLQ)
**WP Mapping:** WP-Y2
**Pattern Mapping:** P-042
**Priority:** P2
**Est. Test Count:** 10-15

**Purpose:** Validate DLQ routing of permanently failing items and poison pill detection.

**Concrete Test Cases:**
1. **test_dlq_route_after_retries_exhausted** - Task fails 10 times (exhausts retry budget). Route to DLQ, emit dlq_entry_created event.
2. **test_dlq_poison_pill_detection** - Same task content_hash appears in DLQ across 3 runs (different contexts). Poison pill detected, flag for manual review, prevent auto-replay.
3. **test_dlq_manual_review_interface** - Operator views DLQ item, reads failure history, clicks "Retry". Task replayed, routed back to normal execution path.
4. **test_dlq_scheduled_sweep** - DLQ sweep job runs hourly, identifies poison pills, generates digest for on-call engineer.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/dlq/poison_pill_*.json`

---

### Test Category 9: Chaos Engineering Fault Injection

**Source:** Reliability research (a5ad944)
**FR Mapping:** FR-035 (chaos)
**WP Mapping:** WP-Y3
**Pattern Mapping:** P-043
**Priority:** P3
**Est. Test Count:** 20-30

**Purpose:** Inject faults systematically; measure recovery correctness and time.

**Chaos Scenario 1: Network Partition**
```
Fault: Inject 5s network partition to provider endpoint
Injection: Block TCP packets to provider IP:port via iptables/tc
Recovery Expected: Timeout triggered, circuit breaker opens, fallback activates, automatic recovery after partition resolves
Test: test_chaos_network_partition_recovery
Metrics: Time-to-detect (target: <1s), fallback activation latency, recovery time (target: <5s)
```

**Chaos Scenario 2: Provider Timeout**
```
Fault: Provider responds after 30s (SLO timeout: 5s)
Injection: Mock provider sleeps 30s before responding
Recovery Expected: Timeout error, retry with backoff, fallback after N attempts
Test: test_chaos_provider_timeout_retry_fallback
Metrics: Timeout detection latency, retry count, fallback activation
```

**Chaos Scenario 3: Malformed Response**
```
Fault: Provider returns invalid XML (missing closing tags)
Injection: Mock provider returns malformed XML
Recovery Expected: XML parser fails, sloppy-xml fallback engaged, confidence penalty applied
Test: test_chaos_malformed_response_parser_fallback
Metrics: Parse failure detection time, fallback latency, confidence degradation
```

**Chaos Scenario 4: State Corruption**
```
Fault: Checkpoint state corrupted (random byte flip)
Injection: Corrupt checkpoint data before rollback
Recovery Expected: Rollback detects corruption, moves to next checkpoint, audit event
Test: test_chaos_checkpoint_corruption_recovery
Metrics: Corruption detection time, recovery latency
```

**Concrete Test Cases:**
1. **test_chaos_network_partition** - See scenario above.
2. **test_chaos_provider_timeout** - See scenario above.
3. **test_chaos_malformed_response** - See scenario above.
4. **test_chaos_state_corruption** - See scenario above.
5. **test_chaos_rate_limit_exceeded** - Provider returns 429. Backpressure engaged, burst smoothing activated.
6. **test_chaos_partial_stream_termination** - Stream closes mid-element. Partial-state buffer preserves context, no silent loss.
7. **test_chaos_multiple_simultaneous_faults** - Network partition + provider timeout + malformed response (cascade). Verify recovery doesn't cascade.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/chaos/scenarios_*.json`

---

### Test Category 10: Multi-Agent Conflict Resolution

**Source:** Kagentop research (ac56cc8), CrewAI patterns (a723262)
**FR Mapping:** FR-032 (multi-agent mode)
**WP Mapping:** WP-Y1
**Pattern Mapping:** P-052, P-053, P-054, P-055, P-060
**Priority:** P3
**Est. Test Count:** 10-15

**Purpose:** Validate mode selection and conflict resolution in multi-agent orchestration.

**Concrete Test Cases:**
1. **test_mode_sequential_delegation** - Task decomposed into [plan, implement, test]. Step 1 → agent A (planner). Step 2 → agent B (implementer). Step 3 → agent C (tester). Results flow forward in order.
2. **test_mode_parallel_consensus** - Task sent to agents A, B, C simultaneously. Agent A: approve. Agent B: approve. Agent C: reject. Majority vote = approve. Confidence scores weighted.
3. **test_mode_hierarchical_planning** - Task decomposed into subtasks [subtask-1, subtask-2, subtask-3]. Distributed to agents. Aggregated results merged. Recursive for deep hierarchies.
4. **test_conflict_resolution_majority_vote** - Agents A, B vote to approve; agent C votes reject. Majority (2/3) wins. Outcome: approve. Conflict event logged.
5. **test_conflict_resolution_tie_escalation** - Agents A, B vote approve; agent C abstains. Tie (unclear majority). Escalate to human. Escalation event with context.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/multi_agent/scenarios_*.json`

---

### Test Category 11: Policy Evaluation Under Load

**Source:** Governance research (aeca587), OPA/Rego patterns (P-066, P-067)
**FR Mapping:** FR-033 (ABAC policy), FR-003 (policy pre-check)
**WP Mapping:** WP-3001, WP-Y5
**Pattern Mapping:** P-066, P-067, P-068, P-071
**Priority:** P3
**Est. Test Count:** 10-15

**Purpose:** Validate policy engine performance under orchestration load; verify ABAC expressions.

**Concrete Test Cases:**
1. **test_policy_eval_latency_baseline** - Single policy evaluation (risk_score > 0.5 → hold). Latency: < 5ms p99 (OPA compiled partial evaluation). Emit timing event.
2. **test_policy_eval_abac_complex** - Policy: (risk_score < 0.3) AND (domain == "non-financial") AND (confidence > 0.8) AND (urgency < 3) → auto-approve. Complex ABAC expression evaluated < 10ms p99.
3. **test_policy_eval_under_load** - 1000 concurrent policy evaluations (different inputs). All complete within p99 < 5ms. No queue buildup.
4. **test_policy_drift_detection_live** - Policy changes deployed via OPAL. Live distribution to all enforcement points. Evaluation immediately uses new policy. No manual restart.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/policy/abac_*.json`

---

### Test Category 12: Progressive Disclosure Rendering

**Source:** UX research (abcd83c, a90e599)
**FR Mapping:** FR-015 (explanation tiers), FR-039 (autonomy), FR-040 (pre-flight), FR-041 (calibration)
**WP Mapping:** WP-4001, WP-4002, WP-4008
**Pattern Mapping:** P-092, P-091, P-098, P-099
**Priority:** P3
**Est. Test Count:** 15-20

**Purpose:** Validate 3-tier progressive disclosure with persona-based defaults and correct rendering.

**Concrete Test Cases:**
1. **test_progressive_tier_1_always_visible** - Tier 1 (summary: status badge, confidence, one-line rationale) always visible. Occupies < 100px height. Color-coded (green >= 85%, yellow 60-84%, red < 60%).
2. **test_progressive_tier_2_expand_detail** - Click expand. Tier 2 (detail: policy gates, evidence, retry history) appears. Shows which gates blocked/approved action. Displays past attempt count and reasons.
3. **test_progressive_tier_3_deep_trace** - Click "View Full Trace". Tier 3 (trace: full event timeline, raw payloads, checkpoint diffs, audit trail) loads. Allows JSON export, time-travel replay.
4. **test_persona_operator_defaults_tier_1** - Operator user logs in. Cockpit shows Tier 1 by default (summary mode). Settings allow personalization.
5. **test_persona_sre_defaults_tier_2** - SRE user logs in. Cockpit shows Tier 2 by default (detail mode). Can collapse to Tier 1 for quick scan.
6. **test_persona_incident_lead_tier_2_plus_3** - Incident lead logs in. Tier 2 + one-click Tier 3 visible. Can compare before/after diffs, replay incidents.
7. **test_autonomy_dial_real_time_toggle** - Operator adjusts autonomy from 30% (mostly manual) to 80% (mostly automatic). Toggle applies immediately. Subsequent actions respect new autonomy level.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/progressive_disclosure/tier_*.json`

---

### Test Category 13: Calibration Curve Tracking

**Source:** UX research (a90e599)
**FR Mapping:** FR-023 (calibration), FR-041 (calibration curves)
**WP Mapping:** WP-4008
**Pattern Mapping:** P-098
**Priority:** P4
**Est. Test Count:** 5-10

**Purpose:** Track historical accuracy of confidence scores; dynamically tune thresholds.

**Concrete Test Cases:**
1. **test_calibration_curve_baseline** - System reports 70% confidence on 100 past decisions. Operator approved 85 of them (85% true approval rate). Calibration curve point: (70%, 85%). Record as baseline.
2. **test_calibration_curve_refinement** - After 1000 new decisions, recompute calibration curve. System learns confidence thresholds map to different approval rates at different confidence levels. Thresholds auto-tune.
3. **test_calibration_display_confidence_risk_dual_indicator** - Cockpit displays both confidence (system's self-assessment) and risk (environmental danger). Dual colors: green (both low-risk/high-confidence), yellow (mixed), red (high-risk/low-confidence).
4. **test_calibration_curve_per_domain** - Separate calibration curves per domain (financial, non-financial, scheduling, etc.). Each domain's confidence thresholds tuned independently.

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/calibration/curve_*.json`

---

### Test Category 14: Speculative Execution Correctness

**Source:** Multi-provider routing research (acd1989)
**FR Mapping:** FR-037 (speculative execution)
**WP Mapping:** WP-5001
**Pattern Mapping:** P-027, P-033
**Priority:** P4
**Est. Test Count:** 5-10

**Purpose:** Validate speculative execution (send to 2 providers, take first response, cancel other).

**Concrete Test Cases:**
1. **test_speculative_execution_first_wins** - Send request to provider A and B simultaneously. Provider A responds in 100ms, provider B in 500ms. A's response returned, B's request cancelled. Cost = 2x, latency = 1x (optimal).
2. **test_speculative_execution_both_fail** - Both providers timeout. First timeout triggers fallback. Second timeout detected and cancelled.
3. **test_speculative_execution_response_quality_differ** - Provider A returns in 100ms (lower quality). Provider B returns in 150ms (higher quality). Test parameter controls quality-vs-latency tradeoff. If quality threshold fails, accept B despite higher latency.
4. **test_speculative_execution_cost_tracking** - Speculative execution costs are tracked (2 provider calls for 1 result). Verify cost-per-quality ratio still makes sense (2x cost for < 2x latency improvement).

**Golden Corpus Location:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/speculative/scenarios_*.json`

---

## Part 6: Test Pyramid Breakdown

**Target Test Distribution**

| Level | Coverage | Count | Examples |
|-------|----------|-------|----------|
| **Unit** | Contracts, parsers, validators, policy evaluation, error handling | 70% | Idempotency key hashing, semantic validation rules, circuit breaker state machine, ABAC expression evaluation |
| **Integration** | Provider adapters, fallback chains, checkpoint/recovery, multi-agent modes, policy gates, observability | 20% | Provider conformance, DLQ poison pill detection, MCP outage fallback, policy drift, cost tracking aggregation |
| **E2E** | Full DAG execution, end-to-end rollback, chaos recovery, operator cockpit interaction, decision replay | 10% | Complete task execution with obstacles, full infrastructure failure recovery, operator approval workflow |

**Estimated Test Counts by Level**

| Category | Unit | Integration | E2E | Total |
|----------|------|-------------|-----|-------|
| Original FRs (24) | 35 | 25 | 10 | 70 |
| Original NFRs (8) | 8 | 15 | 5 | 28 |
| New FRs (18) | 90 | 70 | 20 | 180 |
| New NFRs (8) | 15 | 15 | 3 | 33 |
| **Total** | **148** | **125** | **38** | **311** |

**Pyramid Verification**: 148/311 = 47% unit (target 70% ← need more unit tests)

---

## Part 7: Chaos Test Scenarios with Fault Specifications

**Scenario Set 1: Network Failures**

```
Scenario: Network Partition to Provider
Duration: 5-30s
Injection: iptables DROP to provider IP:port
Detection: Timeout at 5s SLO → circuit breaker OPEN
Recovery: Fallback to secondary provider or cached result
Metrics:
  - Detection latency: < 1s (target)
  - Fallback activation: < 2s
  - Error rate spike: < 5%
  - Recovery time: < 5s after partition resolves
```

```
Scenario: DNS Failure for Provider
Duration: 2-10s
Injection: Return NXDOMAIN for provider hostname
Detection: DNS resolution timeout
Recovery: Retry with exponential backoff, fallback after N attempts
Metrics:
  - Detection latency: < 100ms
  - Fallback activation: < 500ms
  - Total request latency increase: < 3x
```

**Scenario Set 2: Provider Response Anomalies**

```
Scenario: Malformed Response Body
Injection: Return invalid XML (unclosed tags, mixed case, duplicate tags)
Recovery: Parser fallback chain (structured → sloppy-xml → text extraction)
Test: test_chaos_malformed_response_fallback_chain
Metrics:
  - Fallback latency: < 100ms
  - Confidence degradation: from 1.0 → 0.8 → 0.5
  - Silent failure: 0 (must emit event)
```

```
Scenario: Response Timeout (Slow Provider)
Duration: 10-60s (beyond 5s SLO)
Injection: Mock provider sleeps 30s before responding
Recovery: Client timeout triggered, retry with different provider
Test: test_chaos_slow_provider_timeout_rotation
Metrics:
  - Timeout detection: at 5s SLO boundary
  - Failover latency: < 500ms
  - Request redirection to next provider: < 1s
```

**Scenario Set 3: State Corruption**

```
Scenario: Checkpoint Corruption
Injection: Flip random byte in stored checkpoint state
Recovery: Checksum validation fails, move to previous checkpoint
Test: test_chaos_checkpoint_corruption_automatic_rollback
Metrics:
  - Corruption detection: < 500ms
  - Rollback to valid checkpoint: < 2s
  - No data loss verification: audit trail unchanged
```

**Scenario Set 4: Policy Engine Failures**

```
Scenario: Policy Service Down
Duration: 30-60s
Injection: Policy endpoint returns 503 Service Unavailable
Recovery: Fallback to permissive or cached policy
Test: test_chaos_policy_engine_unavailable_fallback
Metrics:
  - Failover latency: < 1s
  - Fallback mode KPI impact: < 10% throughput reduction
  - Service recovery: automatic when policy endpoint recovers
```

```
Scenario: Policy Evaluation Timeout
Injection: Policy endpoint responds after 30s (policy evaluation SLO: 5ms)
Recovery: Timeout escalation, fallback decision
Test: test_chaos_policy_eval_timeout
Metrics:
  - Timeout detection: at SLO boundary
  - Fallback application: < 100ms
  - Request completion: within 10s global timeout
```

**Scenario Set 5: Rate Limit Cascades**

```
Scenario: Provider Rate Limit Hit
Injection: Provider returns 429 Too Many Requests
Recovery: Proactive backpressure, burst smoothing, provider rotation
Test: test_chaos_rate_limit_cascade
Metrics:
  - Rate limit detection: < 100ms
  - Request queue smoothing: spread across 60s window
  - No queue overflow: max queue depth < 1000
  - Auto-rotation to next provider: < 1s
```

**Scenario Set 6: Multi-Fault Cascade**

```
Scenario: Network Partition + Provider Timeout + Policy Engine Slow
Duration: 60s, three simultaneous faults
Injection:
  1. Partition to primary provider (5s)
  2. Secondary provider timeout (10s response time)
  3. Policy evaluation slow (30s response time)
Recovery: Cascading fallbacks without cascade
Test: test_chaos_multi_fault_cascade_no_recovery_loop
Metrics:
  - First fault detection: < 1s
  - Secondary fault handled: without retrying first
  - No circular fallback (fallback → fallback → fallback): max 2 levels
  - Total request latency: < 15s (not infinite)
  - Error rate: < 10%
```

---

## Part 8: Golden Corpus File References

**Baseline Golden Data Locations**

```
/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/tests/fixtures/
├── golden_payloads/
│   ├── task_tool_18tag_complete.xml          # FR-025, FR-026
│   ├── task_tool_18tag_minimal.xml
│   ├── zen_26tag_complete.xml                # FR-025, FR-026
│   ├── zen_26tag_rich_extensions.xml
│   └── csm_canonical_normalized.xml          # FR-026
├── adversarial_xml/
│   ├── malformed_unclosed_tags.xml           # FR-027
│   ├── malformed_truncated_mid_element.xml
│   ├── malformed_duplicate_tags.xml
│   ├── malformed_mixed_case.xml
│   └── malformed_nesting_violation.xml
├── semantic_inconsistency/
│   ├── bad_status_completed_empty_actions.xml  # FR-028
│   ├── bad_progress_100_status_pending.xml
│   ├── bad_confidence_risk_inverse.xml
│   └── good_status_progress_consistent.xml
├── provider_baselines/
│   ├── gemini_baseline_2026_02_14.json       # FR-029
│   ├── copilot_baseline_2026_02_14.json
│   ├── codex_baseline_2026_02_14.json
│   ├── claude_baseline_2026_02_14.json
│   ├── gemini_drift_recent_30d.json
│   └── provider_scoring_historical.json
├── mcp_scenarios/
│   ├── outage_primary_degrade.json           # FR-030
│   ├── outage_extraction_fallback.json
│   ├── outage_recovery_restored.json
│   └── outage_state_transitions.json
├── circuit_breaker/
│   ├── state_closed_normal.json              # FR-007, WP-2003
│   ├── state_closed_to_open_threshold.json
│   ├── state_open_to_half_open_timeout.json
│   ├── state_half_open_success_closed.json
│   └── state_half_open_failure_open.json
├── dlq/
│   ├── poison_pill_same_hash_3runs.json      # FR-034
│   ├── dlq_entry_created_after_retries.json
│   ├── dlq_manual_review_interface.json
│   └── dlq_scheduled_sweep_results.json
├── chaos/
│   ├── scenarios_network_partition_5s.json   # FR-035
│   ├── scenarios_provider_timeout_30s.json
│   ├── scenarios_malformed_response.json
│   ├── scenarios_state_corruption.json
│   ├── scenarios_rate_limit_cascade.json
│   ├── scenarios_policy_engine_down.json
│   └── scenarios_multi_fault_cascade.json
├── multi_agent/
│   ├── scenarios_sequential_delegation.json  # FR-032
│   ├── scenarios_parallel_consensus.json
│   ├── scenarios_hierarchical_planning.json
│   ├── scenarios_conflict_majority_vote.json
│   └── scenarios_conflict_tie_escalation.json
├── policy/
│   ├── abac_risk_score_domain_confidence.json  # FR-033
│   ├── abac_urgency_financial_constraint.json
│   ├── policy_eval_latency_baseline.json
│   └── policy_drift_live_update.json
├── progressive_disclosure/
│   ├── tier_1_summary_visible.json           # FR-015, FR-039
│   ├── tier_2_detail_expanded.json
│   ├── tier_3_trace_deep.json
│   ├── persona_operator_tier_1_default.json
│   ├── persona_sre_tier_2_default.json
│   ├── persona_incident_tier_2_plus_3.json
│   └── autonomy_dial_real_time_toggle.json
├── calibration/
│   ├── curve_baseline_70pct_confidence.json  # FR-041
│   ├── curve_refined_1000_decisions.json
│   ├── curve_display_confidence_risk_dual.json
│   └── curve_per_domain_financial_nonfinancial.json
└── speculative/
    ├── scenarios_first_wins_100ms_500ms.json  # FR-037
    ├── scenarios_both_fail_timeout.json
    ├── scenarios_quality_tradeoff.json
    └── scenarios_cost_tracking_2x_investment.json
```

---

## Part 9: Cross-Linkage Matrix (FRs → WPs → Patterns → Tests)

**Example: FR-027 (Incremental XML Parser) → Complete Linkage**

| Dimension | Value | Reference |
|-----------|-------|-----------|
| **FR** | FR-027 | Incremental XML parser with recoverable partial-state model |
| **WP** | WP-X3 | Incremental XML Parser Engine (Phase X) |
| **Patterns** | P-013, P-014, P-015, P-017 | XMLPullParser feed/read, sloppy-xml fallback, streaming buffer, multi-level extraction |
| **Test Categories** | 3, 6, 9 | Adversarial Malformed XML, MCP Outage, Chaos Injection |
| **Concrete Tests** | test_parser_unclosed_tag, test_parser_truncated_mid_element, test_parser_duplicate_tags, test_parser_mixed_case, test_chaos_malformed_response_parser_fallback | See Part 5 Test Category 3, 6, 9 |
| **Golden Corpus** | `/tests/fixtures/adversarial_xml/malformed_*.xml` | Section 8 |
| **Acceptance Criteria** | XMLPullParser + sloppy-xml handles malformed LLM output; partial-state buffer never treats partial as final; confidence penalties applied on fallback | FR-027 definition |
| **NFR** | NFR-009, NFR-012 | Parse latency preserved p95 SLO; zero silent contract downgrade |

---

## Part 10: Test Execution Order and Dependencies

**Phase 0: Unit Tests (Foundation)**

1. Contract registry, schema versioning (P-001-006)
2. Semantic validation rules (P-007)
3. Error normalization (P-008)
4. Parser (XMLPullParser, sloppy-xml fallback) (P-013-015)
5. Idempotency key hashing (P-036)
6. OTel semantic conventions (P-080)
7. Circuit breaker state machine (P-034)
8. Policy evaluation (OPA/Rego) (P-066)
9. ABAC expressions (P-068)

**Depends On:** None (foundation)

**Phase 1: Integration Tests (Contract + Provider)**

1. Provider adapter conformance (P-020, P-029)
2. Fallback chain validation (P-016, P-018)
3. MCP outage recovery (P-062-063)
4. Contract migration (P-010, P-031)
5. Provider scoring model (P-021, P-025)
6. Checkpoint recovery (P-038-039)
7. Compensation handlers (P-037)

**Depends On:** Phase 0 unit tests passing

**Phase 2: Integration Tests (Orchestration + Policy)**

1. Multi-agent modes (P-050-060)
2. Conflict resolution (P-055)
3. Policy drift detection (P-067, P-074)
4. OPAL live distribution (P-067)
5. Governance gates (P-056, P-078)
6. Cost tracking (P-083)
7. Continuity snapshots (P-111)

**Depends On:** Phase 0 + Phase 1

**Phase 3: E2E Tests (Full Execution)**

1. Complete DAG with obstacles (test_e2e_cli)
2. End-to-end rollback (test_rollback_restores_state)
3. Operator cockpit interaction (test_progressive_disclosure_*_*)
4. Decision replay and what-if (test_decision_replay_4capability)
5. Autonomy gradient (test_autonomy_dial_*)

**Depends On:** Phase 0, 1, 2

**Phase 4: Chaos Tests (Failure Recovery)**

1. Network partition recovery
2. Provider timeout retry
3. Malformed response fallback
4. Checkpoint corruption recovery
5. Rate limit cascade
6. Multi-fault cascade

**Depends On:** All unit/integration/e2e baseline passing (Phase 0, 1, 2, 3)

**Phase 5: Performance Tests (Load + Latency)**

1. Parser latency under load (NFR-009)
2. Policy evaluation latency (NFR-003, NFR-004)
3. Routing latency p95 SLO (NFR-001)
4. Critical-path latency under burst (NFR-002)
5. Cost-per-quality ratio (NFR-016)

**Depends On:** Phase 3 + Phase 4 (recovery validated)

---

## Part 11: Traceability Matrix (Condensed)

**Complete FR → WP → Pattern → Test Mapping**

| FR | WP | Patterns | Test Categories | Est. Tests |
|----|----|---------|----|--------|
| FR-001 | WP-1001 | P-023, P-030 | Routing | 5 |
| FR-002 | WP-1003 | P-036 | Idempotency | 8 |
| FR-003 | WP-3001 | P-066, P-078 | Policy evaluation, governance | 10 |
| FR-004 | WP-0002 | P-080 | Telemetry, evidence | 5 |
| FR-005 | WP-1004 | P-019 | Contract drift | 5 |
| FR-006 | WP-2001 | P-038, P-039 | Checkpoint/rollback | 8 |
| FR-007 | WP-2003 | P-034, P-035 | Circuit breaker (Test Cat 7) | 20 |
| FR-008 | WP-2004 | P-041 | Recovery playbooks | 8 |
| FR-009 | WP-3001 | P-071 | Escalation on low confidence | 5 |
| FR-010 | WP-3002 | P-076 | Signed artifacts | 5 |
| FR-011 | WP-3003 | P-075 | Override TTL | 5 |
| FR-012 | WP-3004 | P-069 | Audit trail immutability | 5 |
| FR-013 | WP-3005 | P-074 | Policy drift detection | 5 |
| FR-014 | WP-3007 | P-077 | Trust boundaries | 5 |
| FR-015 | WP-4002 | P-092 | Progressive disclosure (Test Cat 12) | 20 |
| FR-016 | WP-4003 | P-096 | Safe fallback 3-action | 8 |
| FR-017 | WP-1004 | P-065 | Stale-state block | 5 |
| FR-018 | WP-4006 | P-111 | Handoff continuity | 8 |
| FR-019 | WP-5001 | P-026 | Load controls/burst smoothing | 8 |
| FR-020 | WP-5002 | — | Non-critical deferral | 5 |
| FR-021 | WP-5005 | P-109 | Continuity watchdog | 5 |
| FR-022 | WP-4007 | P-099 | Decision replay 4-capability | 8 |
| FR-023 | WP-4008 | P-098 | Calibration curve (Test Cat 13) | 10 |
| FR-024 | WP-6001 | — | Closure pack | 5 |
| **FR-025** | **WP-X1** | **P-004, P-062** | **Contract negotiation** | **8** |
| **FR-026** | **WP-X2** | **P-001, P-002** | **Golden corpus task-tool, zen (Test Cat 1, 2)** | **70** |
| **FR-027** | **WP-X3** | **P-013, P-014** | **Adversarial XML, chaos malformed (Test Cat 3, 9)** | **65** |
| **FR-028** | **WP-X4** | **P-007, P-011** | **Semantic inconsistency (Test Cat 4)** | **15** |
| **FR-029** | **WP-X5** | **P-020, P-008** | **Provider drift (Test Cat 5)** | **25** |
| **FR-030** | **WP-X6** | **P-016, P-018** | **MCP outage, fallback (Test Cat 6)** | **12** |
| **FR-031** | **WP-X8** | **P-010, P-031** | **Contract migration** | **10** |
| **FR-032** | **WP-Y1** | **P-050-060** | **Multi-agent conflict (Test Cat 10)** | **15** |
| **FR-033** | **WP-3001+** | **P-068** | **Policy evaluation load (Test Cat 11)** | **15** |
| **FR-034** | **WP-Y2** | **P-042** | **DLQ poison pill (Test Cat 8)** | **12** |
| **FR-035** | **WP-Y3** | **P-043** | **Chaos injection (Test Cat 9)** | **30** |
| **FR-036** | **WP-Y4** | **P-083** | **Cost tracking** | **10** |
| **FR-037** | **WP-5001** | **P-027** | **Speculative execution (Test Cat 14)** | **8** |
| **FR-038** | **WP-Y8** | **P-024, P-087** | **Prompt routing** | **15** |
| **FR-039** | **WP-4001** | **P-091** | **Autonomy gradient (Test Cat 12)** | **8** |
| **FR-040** | **WP-4003** | **P-097** | **Pre-flight simulation (Test Cat 12)** | **8** |
| **FR-041** | **WP-4008** | **P-098** | **Calibration curves (Test Cat 13)** | **8** |
| **FR-042** | **WP-Y5** | **P-059** | **Prompt hierarchy** | **10** |
| **TOTAL** | **64** | **114** | **14** | **~340** |

---

## Part 12: Compliance and Audit Gates

**SOC 2 Compliance Mapping**

| Control | Test Category | Evidence Location | Automation |
|---------|---------------|------------------|------------|
| Confidentiality (C1: Authorized access) | Policy evaluation, ABAC | Policy test suite, audit trail | test_policy_eval_under_load, audit_trail_immutability |
| Availability (A1: System uptime) | Resilience, chaos | Circuit breaker, DLQ, recovery | chaos_injection_tests |
| Processing Integrity (PI1: Complete/accurate processing) | Idempotency, semantic validation | Semantic tests, checksums | test_idempotency_key_*, test_semantic_* |
| Confidentiality (C2: Data confidentiality) | Trust boundaries, EU AI Act tagging | Trust boundary validation, risk classification | test_trust_boundary_validation |
| Availability (A2: Service continuity) | Checkpoint/rollback, handoff | Continuity tests | test_checkpoint_replay_*, test_handoff_continuity |

**GDPR Compliance Mapping**

| Requirement | Test Category | Evidence |
|-------------|---------------|----------|
| Right to explanation | Progressive disclosure, decision replay | test_progressive_disclosure_*, test_decision_replay_4capability |
| Data minimization | Evidence collection, policy gates | test_evidence_collection_completeness |
| Data residency | Trust boundaries | test_trust_boundary_validation |
| Audit trail | Immutable audit events | test_audit_trail_immutability |

**EU AI Act Compliance Mapping**

| Risk Classification | Test Category | Evidence |
|---------------------|---------------|----------|
| Minimal risk | Policy evaluation (low-risk fast path) | test_policy_eval_latency_baseline |
| Limited risk | Progressive disclosure, human oversight | test_progressive_disclosure_*, test_human_oversight_escalation |
| High risk | Pre-flight simulation, manual review | test_preflight_simulation_*, dlq manual review interface |
| Unacceptable risk | Governance block, policy denial | test_policy_eval_abac_complex (policy denies) |

---

## Part 13: Summary and Next Steps

### Test Expansion Summary

| Metric | Baseline | After Synthesis | Growth |
|--------|----------|-----------------|--------|
| FRs | 24 | 42 | +75% |
| NFRs | 8 | 16 | +100% |
| Test Categories | 1 (unified) | 14 specific | +13x |
| Est. Test Count | 70-100 | 225-320 | +2.8x |
| Golden Corpus Files | ~5 | ~50 | +10x |
| Chaos Scenarios | 0 | 6 scenario sets | New |
| Patterns Covered | ~20 | 114 | +5.7x |

### Next Actions

1. **Implement Phase 0 unit tests** (Part 1 baseline: 70 tests)
2. **Build golden corpus files** (Section 8: 50 fixture files)
3. **Implement test harness** for chaos injection (Part 7)
4. **Deploy CI gates** for test pyramid enforcement (Part 6)
5. **Link tests to FRs** via test name conventions (Part 11)
6. **Track test execution** in Phase milestones (Part 4, Synthesis Section 4.4)

### Validation Checkpoints

- **Checkpoint 1 (After Phase 0)**: Unit test pyramid at 70%+ coverage, all contracts tested, parser resilience validated
- **Checkpoint 2 (After Phase X)**: Provider adapters conformant, contract migration validated, fallback chains working
- **Checkpoint 3 (After Phase 2)**: Multi-agent orchestration tested, policy evaluation < 5ms p99, chaos recovery validated
- **Checkpoint 4 (Launch)**: All 42 FRs + 16 NFRs have passing test suites, golden corpus complete, chaos scenarios pass

---

## References

- **Synthesis:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/docset/thegent-mega-research-synthesis-2026-02-14.md` (Part 6)
- **PRD:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/docset/thegent-prd-final.md`
- **WBS:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/docset/thegent-wbs-final.md`
- **DAG:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/docset/thegent-dag-final.md`
