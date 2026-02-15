# WBS-to-Issue Import Matrix

**Status:** Baseline  
**Date:** 2026-02-14  
**Source:** `docs/docset/thegent-wbs-final.md`

---

## Purpose

Maps work packages from the final WBS to issue/ticket identifiers for execution tracking and import into project management systems.

---

## Phase 0: Foundation and Baseline

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-0001 | Baseline telemetry contracts and run IDs | — | Done (Chunk 219) |
| WP-0002 | Canonical schemas for chunk/evidence/policy events | — | Done (contracts package) |
| WP-0003 | Planner dependency graph normalization | — | Done |
| WP-0004 | Initial risk and confidence scoring framework | — | Done |
| WP-0005 | Program operating model and ownership map | — | Pending |

---

## Phase 1: Core Routing and Deterministic Execution

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-1001 | Dependency-aware routing engine | — | Done |
| WP-1002 | Priority and urgency lane model | — | Done |
| WP-1003 | Idempotent execution envelope | — | Done |
| WP-1004 | Deterministic phase transition contracts | — | Done |
| WP-1005 | Evidence capture at every promotion gate | — | Done |
| WP-1006 | Conflict arbitration rules and quorum policy | — | Done |
| WP-1007 | Child-task routing policy by capability and confidence | — | Done |
| WP-1008 | Replay-safe run history and correlation IDs | — | Done |

---

## Phase 2: Reliability and Recovery Hardening

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-2001 | Checkpoint/rollback service | — | Done |
| WP-2002 | Retry strategy with adaptive backoff and guardrails | — | Done |
| WP-2003 | Circuit breakers for tool/model/storage classes | — | Done |
| WP-2004 | Recovery playbook automation and idempotency tokens | — | Done |
| WP-2005 | Failure taxonomy and recurrence clustering | — | Done |
| WP-2006 | Regression prevention probes at pre-promote stage | — | Done |
| WP-2007 | Evidence completeness linting | — | Done |
| WP-2008 | Controlled oversight path for repeated failures | — | Done |

---

## Phase 3: Governance and Security Enforcement

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-3001 | Policy pre-check and gate evaluator | — | Done |
| WP-3002 | Signed action artifacts for critical operations | — | Done |
| WP-3003 | Override path with TTL and revalidation rules | — | Done |
| WP-3004 | Immutable audit trail and query interface | — | Done |
| WP-3005 | Policy drift detection and sweep automation | — | Done |
| WP-3006 | Compliance evidence retention by domain | — | Pending |
| WP-3007 | Trust boundary checks for environment transitions | — | Done |
| WP-3008 | Escalation SLA and governance queue operations | — | Pending |

---

## Phase 4: Human-Centered UX and Explainability

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-4001 | Operator cockpit summary model | — | Done |
| WP-4002 | Concise and detailed explanation tiers | — | Done |
| WP-4003 | One-click safe fallback options | — | Done |
| WP-4004 | Interruption taxonomy and fatigue controls | — | Pending |
| WP-4005 | State freshness checks and stale-state prevention | — | Done |
| WP-4006 | Continuity handoff summaries across shifts | — | Pending |
| WP-4007 | Decision replay and rationale snapshots | — | Done |
| WP-4008 | Feedback loops and confidence calibration | — | Done |

---

## Phase 5: Adaptive Scale and Continuity Automation

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-5001 | Adaptive concurrency controller | — | Done |
| WP-5002 | Burst load classification and safe-mode controls | — | Pending |
| WP-5003 | Cost-aware routing and workload shaping | — | Pending |
| WP-5004 | Non-critical deferral rules with explicit ETA | — | Done |
| WP-5005 | Long-running continuity watchdog | — | Pending |
| WP-5006 | Handoff integrity enforcement | — | Pending |
| WP-5007 | Recovery under sustained load drills | — | Done |
| WP-5008 | Load-aware recommendation tuning | — | Done |

---

## Phase 6: Enterprise Readiness and Launch Closure

| WP ID | Description | Issue ID | Status |
|-------|-------------|----------|--------|
| WP-6001 | End-to-end dress rehearsal | — | Done |
| WP-6002 | Security and compliance signoff package | closure-pack | Done |
| WP-6003 | Reliability and SLO certification | — | Done |
| WP-6004 | Runbook finalization and on-call readiness | RUNBOOK.md | Done |
| WP-6005 | KPI baselines and launch thresholds | — | Done |
| WP-6006 | Decommission/sunset plan for temporary controls | DECOMMISSIONING_PLAN.md | Done |
| WP-6007 | Post-launch observation and rollback reserve | — | Pending |
| WP-6008 | Formal closure and successor roadmap | — | Done |

---

## Import Notes

- **Issue ID**: Populate when importing into GitHub Issues, Jira, Linear, etc.
- **Status**: Done = implemented; Pending = not yet implemented.
- Use WP ID as prefix for issue keys (e.g. `THGENT-WP-3006`).
