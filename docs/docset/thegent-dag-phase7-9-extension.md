# thegent DAG Extension — Phases 7, 8, 9

**Status:** Draft  
**Date:** 2026-02-15  
**Purpose:** Add explicit execution nodes for contract convergence, predictive reliability, and operation productization.

## 1) Added node set

```mermaid
flowchart TD
  %% Phase 7
  N7001[contract_version_invoke] --> N7002[contract_negotiate]
  N7002 --> N7003[stream_parser_bootstrap]
  N7003 --> N7004[stream_partial_state]
  N7004 --> N7005[semantic_validate_core]
  N7005 --> N7006[adapter_conformance_batch]
  N7006 --> N7007[fallback_confidence_gate]
  N7007 --> N7008[migration_dual_read_write]
  N7008 --> N7009[contract_health_emit]
  N7009 --> N7010[drift_alarm_gate]

  %% Phase 8
  N7003 --> N8001[plan_graph_extract]
  N8001 --> N8002[pert_monte_carlo]
  N8002 --> N8003[bottleneck_detect]
  N8003 --> N8004[reschedule_advice]
  N8004 --> N8005[continuity_risk_profile]
  N8005 --> N8006[surge_predict]
  N8006 --> N8007[adaptive_safety_mode]
  N8007 --> N8008[runbook_playbook_sim]
  N8008 --> N8009[intervention_policy]
  N8009 --> N8010[forecast_calibration]

  %% Phase 9
  N8009 --> N9001[operations_api_v1]
  N9001 --> N9002[explainability_stack]
  N9002 --> N9003[replay_sandbox]
  N9003 --> N9004[handoff_guard]
  N9004 --> N9005[universal_adapter_layer]
  N9005 --> N9006[what_if_simulation]
  N9006 --> N9007[confidence_escalation]
  N9007 --> N9008[fallback_controls_visible]
  N9008 --> N9009[audit_linkage]
  N9009 --> N9010[phase7_9_documentation]
```

## 2) Gate nodes

- `G7` after `N7010`: block critical-lane release on unresolved drift.
- `G8` after `N8010`: block go-live if forecast quality below target.
- `G9` after `N9010`: block rollout if replay can mutate state or evidence links are missing.

## 3) Recovery and escalation nodes

- From `N7007` any fallback confidence breach routes to `N-R1`.
- From `N8006` if surge exceeds threshold routes to `N-R2`.
- From `N9003` if replay mode enters execution context routes to `N-R3`.

```mermaid
flowchart TD
  N-R1[fallback_confidence_breach] --> N-R1A[log_confidence_penalty]
  N-R1A --> N-R1B[owner_notify]
  N-R1B --> N-R1C[policy_gate_review]

  N-R2[surge_threshold_breach] --> N-R2A[activate_safe_mode]
  N-R2A --> N-R2B[defer_non_critical_lanes]
  N-R2B --> N-R2C[continue_critical_flow]

  N-R3[replay_mutation_attempt] --> N-R3A[force_read_only]
  N-R3A --> N-R3B[manual_enablement_required]
```

## 4) Data contracts per node

| Node | Inputs | Outputs | Schema intent |
|---|---|---|---|
| N7001 | session context | version list | `contract_support_list` |
| N7003 | stream chunks | parser state | `stream_parser_state` |
| N7004 | parser state | commit events | `partial_state_checkpoint` |
| N7005 | normalized payload | validation result | `validator_report` |
| N7008 | migration window config | cutover metrics | `migration_rollout_report` |
| N8002 | critical path + perturbations | duration bands | `risk_distribution` |
| N8004 | risk bands + workload | recommended edits | `reschedule_advice` |
| N8007 | surge score | safe-mode decision | `safety_mode_decision` |
| N9001 | operation request | op result | `operation_envelope` |
| N9006 | replay request | timeline + diff | `replay_plan` |

## 5) Execution policy

1. Any node in Phase 7 must complete before dependent Phase 8 nodes execute.
2. `G7` and `G8` are hard gates; if failed, only stabilization nodes continue.
3. `N9001` requires both contract negotiation and parser health checks as preconditions.
4. `G9` must record explicit owner signoff for replay safety and explainability.



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

