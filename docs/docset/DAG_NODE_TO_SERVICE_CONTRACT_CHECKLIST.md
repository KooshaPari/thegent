# DAG Node-to-Service Contract Checklist

**Status:** Baseline  
**Date:** 2026-02-14  
**Source:** `docs/docset/thegent-dag-final.md`

---

## Purpose

Defines service contracts and invariants for each DAG node. Use when implementing or validating orchestration flow.

---

## Core Execution DAG

| Node | ID | Service Contract | Invariants | Implementation |
|------|-----|------------------|------------|----------------|
| Intake Request | A0 | Creates run_id, owner_id, correlation context | run_id unique; owner_id non-empty | cli_impl.run_impl, bg_impl |
| Classify Scope/Risk/Cost | A1 | Returns scope, risk_score, cost_tier | risk_score in [0,1] | execution.RunMeta |
| Schema Valid? | A2 | Validates input schema | Fail fast on invalid | dag validate |
| Hydrate Dependency Graph | A4 | Returns DAG with deps | No cycles; deps exist | _parse_dag_session |
| Compute Priority and Confidence | A5 | Returns priority, confidence | confidence in [0,1] | execution |
| Policy Pre-check Pass? | A6 | OPA/policy evaluation | Allow/deny/hold | PolicyEngine |
| Route to Execution Lane | A8 | Selects lane (critical/standard) | Lane exists | cli_impl |
| Execute in Bounded Envelope | A10 | Runs with timeout, idempotency | Idempotency token checked | run_impl |
| Evidence Complete? | A11 | Validates evidence bundle | evidence_set_hash present | dag validate |
| Integrity and Regression Gate | A13 | Checks integrity, regression | No drift from baseline | dag probe |
| Promote Phase + Publish Summary | A16 | Updates state, emits summary | Audit event emitted | _dag_update_task |
| Close with Audit Artifact | A18 | Final audit record | Immutable; signed | history verify |

---

## Recovery DAG

| Node | ID | Service Contract | Invariants | Implementation |
|------|-----|------------------|------------|----------------|
| Failure Detected | R0 | Emits failure event | failure_class set | run_impl, dag |
| Classify Failure Type | R1 | Returns failure_class | Known taxonomy | resilience |
| Select Recovery Playbook | R3 | Returns playbook_id | Playbook exists | dag recover |
| Run Recovery with Idempotency Token | R6 | Retries with token | Token prevents duplicate | dag run |
| Rollback + Oversight Queue | R9 | Queues for human | Owner assigned | dag recover |
| Update Learning Registry | R12 | Stores recovery outcome | Non-mutable append | — |

---

## Governance DAG

| Node | ID | Service Contract | Invariants | Implementation |
|------|-----|------------------|------------|----------------|
| Action Proposed | G0 | Structured action payload | action_type, risk_score | PolicyEngine |
| Policy Scope Resolution | G1 | Resolves applicable policies | Policy IDs returned | policy show |
| Require Signature + Reason Code | G3 | Signature + reason required | reason_code non-empty | run --override |
| Standard Gate | G4 | Policy evaluation | Allow/deny | PolicyEngine |
| Approve and Emit Audit Event | G8 | Audit record created | Immutable; hash-chained | history verify |
| Block + Governance Queue | G6 | Queues for review | SLA tracked | — |

---

## Adaptive Scale DAG

| Node | ID | Service Contract | Invariants | Implementation |
|------|-----|------------------|------------|----------------|
| Ingress Rate Monitor | S0 | Tracks request rate | Rate metric exposed | — |
| Normal Scheduling | S2 | Standard concurrency | Within cap | dag run |
| Reduce Noncritical Concurrency | S4 | Lowers noncritical cap | Critical lane protected | — |
| Protect Critical Lane Capacity | S5 | Reserves critical capacity | Critical never starved | — |
| Issue Continuity Snapshot | S6 | Captures owner, ETA | Snapshot immutable | cockpit |

---

## Event Contract (Required on Every Transition)

| Field | Required | Description |
|-------|----------|-------------|
| run_id | Yes | Run correlation ID |
| chunk_id | Yes | Chunk identifier |
| policy_gate_id | Yes (if governance) | Policy gate ID |
| evidence_set_hash | Yes | SHA-256 of evidence bundle |
| owner_id | Yes | Session/task owner |
| decision_reason_code | Yes | Rationale code |

---

## Checklist for New Node Implementation

- [ ] Service contract documented in this checklist
- [ ] Invariants defined and enforced
- [ ] Implementation path identified
- [ ] Audit event emitted (if state transition)
- [ ] Failure class mapped (if failure path)

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
- [03-UNIFIED-DAG.md](../plans/03-UNIFIED-DAG.md) — DAG specification
