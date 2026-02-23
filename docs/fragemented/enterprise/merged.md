# Merged Fragmented Markdown

## Source: enterprise/DECOMMISSIONING_PLAN.md

# Decommissioning and Sunset Plan

**Scope:** Temporary controls and legacy adapters in thegent
**Date:** 2026-02-14
**Related:** WP-6006, `docs/RUNBOOK.md` §5

## 1. Overview

This plan identifies temporary architectural shims, legacy adapters, and transitional controls that should be sunset as the platform matures.

## 2. Target Components for Sunset

| Component | Reason | Sunset Trigger | Target |
|-----------|--------|----------------|--------|
| `GenericOutputAdapter` | Loose normalization | 100% provider coverage with `XMLOutputAdapter` | v1.2 |
| `fallback-plain` policy | Low confidence | 95% normalization success rate over 30 days | v1.2 |
| `--override` flag (unlimited) | Security risk | Implementation of TTL-based policy overrides | v1.1 |
| Static model lists | Brittle | Stable `ModelScraper` performance for all providers | v1.2 |
| `history-legacy` command | Hidden, superseded | Already hidden | v1.1 |

## 3. Migration Path

1. **Deprecation Phase:**
   - Emit warnings via `ContractTelemetry` when sunset components are used.
   - Update `CONTRACT_AUTHORITY.md` to mark versions as `deprecated`.
2. **Dual-Run Phase:**
   - Run legacy and new components in parallel where possible.
   - Log drift via `ContractTelemetry.detect_drift()` and `thegent govern conformance --check-drift`.
3. **Decommission Phase:**
   - Remove code from `src/thegent`.
   - Update conformance tests to ensure no regressions.

## 4. Rollback Strategy

In case of critical failures after sunset:
- Retain code in git history for rapid revert.
- Maintain `v-1` version compatibility in `ContractRegistry` for one major release.

---

## Source: enterprise/OPERATING_MODEL.md

# Program Operating Model and Ownership Map

**Scope:** thegent orchestration platform
**Date:** 2026-02-14
**Related:** WP-0005, `docs/RUNBOOK.md`, `docs/research/GOVERNANCE_WP_GAPS.md`

---

## 1. Overview

This document defines the RACI matrix, ownership assignments, and escalation paths for the thegent orchestration platform. It supports org readiness and clear accountability for operations, governance, and recovery.

---

## 2. RACI Matrix

| Activity | Product Owner | Tech Lead | Operator | Security/Compliance | Stakeholder |
|----------|---------------|-----------|----------|---------------------|-------------|
| **Orchestration (run, bg, dag run)** | A | R | R | I | I |
| **Policy definition & thresholds** | A | R | I | R | C |
| **Override approval (--override)** | A | I | R | C | I |
| **Escalation queue (govern escalate)** | A | I | R | C | I |
| **Drift detection & sweep** | I | R | R | I | I |
| **Audit trail & integrity** | I | R | I | R | C |
| **Recovery (reconcile, rollback)** | I | R | R | I | I |
| **Data protection & retention** | A | R | I | R | C |
| **Contract migration & versioning** | A | R | I | I | C |
| **Post-launch observation** | A | R | R | I | I |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 3. Ownership Assignments

| Domain | Owner | Backup | Scope |
|--------|-------|--------|-------|
| **Orchestration** | Tech Lead | Operator | run, bg, dag, agents, routing |
| **Governance** | Product Owner | Security | policy, override, escalation, data-protection |
| **Recovery** | Tech Lead | Operator | reconcile, rollback, recover, stop |
| **Observability** | Operator | Tech Lead | cockpit, benchmark, drift, KPIs |
| **Contracts** | Tech Lead | Product Owner | conformance, migration, schema versioning |
| **Compliance** | Security/Compliance | Product Owner | audit, retention, evidence |

---

## 4. Escalation Paths

### 4.1 Policy Denial / Blocked Run

1. **T0:** Run blocked by policy (e.g. trust score, critical lane, drift budget).
2. **T0+0:** Run added to escalation queue (`thegent govern escalate list`).
3. **SLA:** Resolve within `THGENT_ESCALATION_SLA_MINUTES` (default 30 min).
4. **T0+SLA:** If past SLA, escalate to Product Owner.
5. **Resolution:** `thegent govern escalate resolve <run_id>` or `--override` with justification.

### 4.2 Contract Drift / Adapter Failure

1. **T0:** Drift detected (`thegent observe drift`, `thegent govern conformance --check-drift`).
2. **T0+0:** Critical lane blocked (XC2); DAG run with `--check-drift` exits 2.
3. **SLA:** Investigate within 60 min; remediate within 4 hours.
4. **Escalation:** Tech Lead → Product Owner if adapter change required.

### 4.3 Audit / Integrity Failure

1. **T0:** `thegent history verify` fails or hash chain broken.
2. **T0+0:** Escalate immediately to Security/Compliance.
3. **SLA:** Root cause within 2 hours; remediation per incident severity.

### 4.4 Post-Launch Incident

See `docs/POST_LAUNCH_OBSERVATION_PLAYBOOK.md` for severity→SLA mapping.

---

## 5. Handoff and Continuity

- **Shift handoff:** Operator documents active escalations and running sessions in continuity log.
- **Ownership transfer:** Incoming owner confirms escalation queue and past-SLA items via `thegent govern escalate list --past-sla`.
- **Runbook reference:** All procedures in `docs/RUNBOOK.md`; escalation links in §3.

---

## 6. Configuration (Code Enforcement)

The operating model is enforced via config. These settings map to the escalation paths above:

| Config / Env | Default | Maps To |
|--------------|---------|---------|
| `escalation_sla_minutes` / `THGENT_ESCALATION_SLA_MINUTES` | 30 | §4.1 Policy Denial SLA |
| `escalation_sla_breach_alert` | true | §4.1 Past-SLA alert in `govern sweep` |
| `override_ttl_seconds` | 86400 (24h) | §4.1 Override validity |

**Source:** `src/thegent/config.py` — `ThegentSettings`

---

## 7. References

- `docs/RUNBOOK.md` — On-call procedures, recovery, escalation
- `docs/research/GOVERNANCE_WP_GAPS.md` — WP-3008 escalation queue
- `docs/plans/09-RISK-REGISTRY.md` — Risk-based SLA targets

---

## Source: enterprise/SECURITY_COMPLIANCE_SIGNOFF.md

# Security and Compliance Signoff Package

**Version:** 1.0
**Status:** PROVISIONAL
**Date:** 2026-02-14

## 1. Executive Summary

Thegent orchestration layer provides a unified control plane for agent execution. This document details the security controls, compliance posture, and risk mitigation strategies implemented in the system.

## 2. Security Architecture

- **Identity & Access Management:**
  - Local execution uses OS-level permissions.
  - Proxy execution uses Fernet-encrypted API keys.
  - MCP server supports tool-approval loops for sensitive operations.
- **Data Protection:**
  - All session logs stored in `~/.factory/sessions` with 0700 permissions.
  - API keys managed via `thegent.config` with sensitive field masking in logs.
  - Evidence set hashes (SHA-256) ensure audit trail integrity.
- **Network Security:**
  - FastMCP server defaults to localhost (127.0.0.1).
  - Outbound agent calls restricted to configured provider endpoints.

## 3. Compliance Framework

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Audit Trail | RunRegistry hash-chaining | ✓ Compliant |
| Immutable Logs | WORM-simulated storage | ✓ Compliant |
| Policy Gating | PolicyEngine pre-check | ✓ Compliant |
| Access Control | Env-scoped owner tags | ✓ Compliant |

## 4. Threat Model & Mitigations

- **Threat:** Agent prompt injection to leak API keys.
  - *Mitigation:* System prompt constraints + tool-call budget injection.
- **Threat:** Unauthorized access to session logs.
  - *Mitigation:* OS-level isolation + ownership-tagged scopes.
- **Threat:** Replay attacks on governance artifacts.
  - *Mitigation:* RUN_ID correlation + timestamped hash chains.

## 5. Signoff

- **Architecture:** ✓ Approved 2026-02-14
- **Security:** [PENDING]
- **Compliance:** [PENDING]


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

---
