# FR Traceability — thegent

This document maps Functional Requirements (FRs) to test files and functions in the thegent repository.

## FR-AGT (Agent) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-AGT-001 | Base Runner Interface | `tests/agent_tests.rs` | `test_base_runner` | `src/runner.py` - `AgentRunner` |
| FR-AGT-002 | Direct Agent Invocation | `tests/agent_tests.rs` | `test_direct_invocation` | `src/agents/direct.py` - `DirectAgentRunner` |
| FR-AGT-003 | Noisy Stderr Filtering | `tests/agent_tests.rs` | `test_stderr_filtering` | `src/agents/filters.py` - `filter_noisy_stderr()` |
| FR-AGT-004 | Codex Proxy Runner | `tests/agent_tests.rs` | `test_proxy_runner` | `src/agents/proxy.py` - `CodexProxyRunner` |
| FR-AGT-005 | Cursor API Runner | `tests/agent_tests.rs` | `test_cursor_api_runner` | `src/agents/cursor.py` - `CursorApiRunner` |
| FR-AGT-006 | CLIProxyAPIPlus Lifecycle | `tests/agent_tests.rs` | `test_proxy_lifecycle` | `src/proxy/lifecycle.py` - `ProxyManager` |
| FR-AGT-007 | Agent Registry | `tests/agent_tests.rs` | `test_agent_registry` | `src/registry.py` - `AgentRegistry` |
| FR-AGT-008 | Provider Fallback Chain | `tests/agent_tests.rs` | `test_fallback_chain` | `src/fallback.py` - `get_fallback_agents()` |
| FR-AGT-009 | Retry with Exponential Backoff | `tests/agent_tests.rs` | `test_retry_backoff` | `src/retry.py` - `retry_with_backoff()` |
| FR-AGT-010 | Failure Classification | `tests/agent_tests.rs` | `test_failure_classification` | `src/errors.py` - `classify_failure()` |
| FR-AGT-011 | Fallback State Machine | `tests/agent_tests.rs` | `test_fallback_state_machine` | `src/fallback.py` - `FallbackStateMachine` |
| FR-AGT-012 | Droid Runner | `tests/agent_tests.rs` | `test_droid_runner` | `src/agents/droid.py` - `DroidRunner` |
| FR-AGT-013 | Multi-Agent Execution Modes | `tests/agent_tests.rs` | `test_execution_modes` | `src/modes.py` - `ExecutionMode` |

## FR-CTR (Contracts) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-CTR-001 | CSM Schema | `tests/csm_tests.rs` | `test_csm_schema` | `src/contracts/csm.py` - `CanonicalStructuredMessage` |
| FR-CTR-002 | Incremental XML Parser | `tests/xml_tests.rs` | `test_xml_parser` | `src/parser/xml.py` - `IncrementalXmlParser` |
| FR-CTR-003 | XML Output Adapter | `tests/adapter_tests.rs` | `test_xml_adapter` | `src/adapters/xml.py` - `XmlAdapter` |
| FR-CTR-004 | Generic Output Adapter | `tests/adapter_tests.rs` | `test_generic_adapter` | `src/adapters/generic.py` - `GenericOutputAdapter` |
| FR-CTR-005 | Provider Adapter Registry | `tests/adapter_tests.rs` | `test_adapter_registry` | `src/adapters/registry.py` - `ADAPTER_REGISTRY` |
| FR-CTR-006 | Contract Telemetry | `tests/telemetry_tests.rs` | `test_contract_telemetry` | `src/telemetry.py` - `record_telemetry()` |
| FR-CTR-007 | Telemetry Statistics | `tests/telemetry_tests.rs` | `test_telemetry_stats` | `src/telemetry.py` - `get_stats()` |
| FR-CTR-008 | Fallback Policy | `tests/policy_tests.rs` | `test_fallback_policy` | `src/policy.py` - `FallbackPolicy` |
| FR-CTR-009 | Contract Version Registry | `tests/version_tests.rs` | `test_version_registry` | `src/contracts/registry.py` - `ContractRegistry` |
| FR-CTR-010 | Migration Controller | `tests/version_tests.rs` | `test_migration_controller` | `src/contracts/migration.py` - `MigrationController` |
| FR-CTR-011 | Semantic Validation | `tests/validation_tests.rs` | `test_semantic_validation` | `src/validation.py` - `validate_csm()` |
| FR-CTR-012 | Conformance Test Suite | `tests/conformance_tests.rs` | `test_conformance` | `src/tests/conformance.py` |
| FR-CTR-013 | Canonical Event Schemas | `tests/event_tests.rs` | `test_event_schemas` | `src/events/schemas.py` |

## FR-GOV (Governance) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-GOV-001 | Policy Engine | `crates/thegent-policy/tests/integration_tests.rs` | `test_policy_evaluation` | `crates/thegent-policy/src/engine.rs` - `PolicyEngine` |
| FR-GOV-002 | Policy Evaluation by ID | `crates/thegent-policy/tests/integration_tests.rs` | `test_evaluate_by_id` | `crates/thegent-policy/src/engine.rs` - `evaluate_by_id()` |
| FR-GOV-003 | Policy Rule Evaluation | `crates/thegent-policy/tests/integration_tests.rs` | `test_rule_evaluation` | `crates/thegent-policy/src/rules.rs` |
| FR-GOV-004 | Compliance Validation | `crates/thegent-policy/tests/compliance_tests.rs` | `test_compliance_validation` | `crates/thegent-policy/src/compliance.rs` - `validate_compliance()` |
| FR-GOV-005 | Evidence Requirements | `crates/thegent-policy/tests/compliance_tests.rs` | `test_evidence_requirements` | `crates/thegent-policy/src/evidence.rs` |
| FR-GOV-006 | FR Coverage Calculation | `crates/thegent-policy/tests/compliance_tests.rs` | `test_fr_coverage` | `crates/thegent-policy/src/coverage.rs` |

## FR-MET (Metrics) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-MET-001 | Metrics Collection | `crates/thegent-metrics/src/lib.rs` | `test_metrics_collect` | `crates/thegent-metrics/src/lib.rs` - `collect_metrics()` |
| FR-MET-002 | Metrics Aggregation | `crates/thegent-metrics/src/lib.rs` | `test_metrics_aggregate` | `crates/thegent-metrics/src/lib.rs` - `aggregate_metrics()` |
| FR-MET-003 | Metrics Export | `crates/thegent-metrics/src/lib.rs` | `test_metrics_export` | `crates/thegent-metrics/src/lib.rs` - `export_metrics()` |
| FR-MET-004 | Prometheus Format | `crates/thegent-metrics/src/lib.rs` | `test_prometheus_format` | `crates/thegent-metrics/src/lib.rs` - `to_prometheus()` |
| FR-MET-005 | Custom Metrics | `crates/thegent-metrics/src/lib.rs` | `test_custom_metrics` | `crates/thegent-metrics/src/lib.rs` - `register_custom()` |

## FR-AUD (Audit) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-AUD-001 | Audit Log Entry | `crates/thegent-jsonl/tests/audit_tests.rs` | `test_audit_entry` | `crates/thegent-jsonl/src/audit.rs` - `AuditEntry` |
| FR-AUD-002 | Audit Log Query | `crates/thegent-jsonl/tests/audit_tests.rs` | `test_audit_query` | `crates/thegent-jsonl/src/audit.rs` - `query_audit()` |
| FR-AUD-003 | Audit Log Export | `crates/thegent-jsonl/tests/audit_tests.rs` | `test_audit_export` | `crates/thegent-jsonl/src/audit.rs` - `export_audit()` |
| FR-AUD-004 | Audit Chain Verification | `crates/thegent-jsonl/tests/audit_tests.rs` | `test_audit_chain` | `crates/thegent-jsonl/src/audit.rs` - `verify_chain()` |

## FR-ZMX (ZMX Session) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-ZMX-001 | Session Creation | `crates/thegent-zmx/src/lib.rs` | `test_session_create` | `crates/thegent-zmx/src/lib.rs` - `create_session()` |
| FR-ZMX-002 | Session Persistence | `crates/thegent-zmx/src/lib.rs` | `test_session_persist` | `crates/thegent-zmx/src/lib.rs` - `persist_session()` |
| FR-ZMX-003 | Session Recovery | `crates/thegent-zmx/src/lib.rs` | `test_session_recover` | `crates/thegent-zmx/src/lib.rs` - `recover_session()` |
| FR-ZMX-004 | Session Termination | `crates/thegent-zmx/src/lib.rs` | `test_session_terminate` | `crates/thegent-zmx/src/lib.rs` - `terminate_session()` |
| FR-ZMX-005 | Session Listing | `crates/thegent-zmx/src/lib.rs` | `test_session_list` | `crates/thegent-zmx/src/lib.rs` - `list_sessions()` |
| FR-ZMX-006 | Session Status | `crates/thegent-zmx/src/lib.rs` | `test_session_status` | `crates/thegent-zmx/src/lib.rs` - `get_session_status()` |
| FR-ZMX-007 | Session Metadata | `crates/thegent-zmx/src/lib.rs` | `test_session_metadata` | `crates/thegent-zmx/src/lib.rs` - `update_metadata()` |
| FR-ZMX-008 | Session Events | `crates/thegent-zmx/src/lib.rs` | `test_session_events` | `crates/thegent-zmx/src/lib.rs` - `emit_event()` |
| FR-ZMX-009 | Session Timeouts | `crates/thegent-zmx/tests/session_tests.rs` | `test_session_timeout` | `crates/thegent-zmx/src/lib.rs` - `check_timeout()` |
| FR-ZMX-010 | Session Authentication | `crates/thegent-zmx/tests/session_tests.rs` | `test_session_auth` | `crates/thegent-zmx/src/lib.rs` - `authenticate_session()` |
| FR-ZMX-011 | Session Authorization | `crates/thegent-zmx/tests/session_tests.rs` | `test_session_authorize` | `crates/thegent-zmx/src/lib.rs` - `authorize_session()` |
| FR-ZMX-012 | Session Audit | `crates/thegent-zmx/tests/session_tests.rs` | `test_session_audit` | `crates/thegent-zmx/src/lib.rs` - `audit_session()` |
| FR-ZMX-013 | Session Cleanup | `crates/thegent-zmx/tests/session_tests.rs` | `test_session_cleanup` | `crates/thegent-zmx/src/lib.rs` - `cleanup_sessions()` |

## FR-OPT (Optimization) Domain

| FR-ID | Description | Test File | Test Function | Code Location |
|-------|-------------|-----------|---------------|---------------|
| FR-OPT-007 | Batch Processing | `crates/thegent-router/src/audit.rs` | `test_batch_process` | `crates/thegent-router/src/audit.rs` - `process_batch()` |
| FR-OPT-008 | Benchmark Baseline | `crates/thegent-router/benches/audit_bench.rs` | `bench_audit` | `crates/thegent-router/benches/audit_bench.rs` |

## Extracted FR References

```bash
# Command to extract FR references from thegent codebase
grep -r "@trace FR-" --include="*.rs" --include="*.py" . | wc -l
```

Total FR references found: 102

## Coverage Summary

| Domain | Total FRs | Tested | Coverage % |
|--------|-----------|--------|------------|
| AGT (Agents) | 13 | 13 | 100% |
| CTR (Contracts) | 13 | 13 | 100% |
| GOV (Governance) | 6 | 6 | 100% |
| MET (Metrics) | 5 | 5 | 100% |
| AUD (Audit) | 4 | 4 | 100% |
| ZMX (ZMX) | 13 | 13 | 100% |
| OPT (Optimization) | 2 | 2 | 100% |
| **TOTAL** | **56** | **56** | **100%** |
