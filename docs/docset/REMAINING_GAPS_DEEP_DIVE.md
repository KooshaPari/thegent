# Remaining Gaps — Full Depth Analysis

**Date:** 2026-02-14  
**Source:** `thegent-gaps-and-discovery-2026-02-14.md`  
**Purpose:** Deep-dive analysis of all remaining gaps: what exists, what's missing, implementation options, and acceptance criteria.

---

## 1. Delta Set C: Governance and Quality Gates (XC1–XC3)

### XC1: Semantic Validation Gate Before Promotion

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Requirement** | Block promotion (return success) when semantic validation fails | Research validation §9 |
| **Implementation** | ✅ **Done** | `state_machine.py` lines 142–188 |
| **Flow** | `validate_csm(norm_res.csm)` → `semantic_issues`; if non-empty, we do NOT set `status="success"`; we either fall to next provider or fail | — |
| **Gate logic** | `if not policy_violations and not semantic_issues:` → success; else → fallback or fail | — |

**Conclusion:** XC1 is implemented. Semantic issues block promotion; fallback chain proceeds to next provider or fails if exhausted.

---

### XC2: Contract Drift Alarms; Blocked Promotion on Critical Drift

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Requirement** | Detect drift; block critical lane when drift exceeds budget | Cross-analysis matrix |
| **Drift detection** | ✅ Done | `ContractTelemetry.detect_drift()`, `get_drift_budget_status()` |
| **Block critical lane** | ✅ Done | `execution.py` Policy 2b (lines 412–424) |
| **Flow** | `PolicyEngine.evaluate()` checks `run.lane == "critical"` → `ct.get_drift_budget_status()` → if `not within_budget` → `return "deny"` | — |
| **CLI** | `thegent observe drift`, `thegent govern conformance --check-drift` | — |

**Conclusion:** XC2 is implemented. Drift alarms exist; critical lane is blocked when structural/semantic drift exceeds budget (5%/10%).

---

### XC3: No Critical Lane Action with Unknown Contract Version

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Requirement** | Block runs when contract version is unknown | Cross-analysis matrix |
| **Version check** | ✅ Done | `cli_impl.py` lines 941–949, 1231–1237 |
| **Flow** | `migrator.evaluate_version("csm", requested_version)` → if `not mig_res["allowed"]` (e.g. `status="unknown"`) → return error, exit_code 1 | — |
| **Policy engine** | N/A | Version check happens before policy; run never starts with unknown version |

**Conclusion:** XC3 is implemented. Unknown contract version causes early rejection; run never reaches critical lane.

---

## 2. Functional Requirements (FR-X01, FR-X08)

### FR-X01: Contract Version Negotiation

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Negotiate contract version between client and server | Research validation |
| **Current** | Single version: `CONTRACT_SCHEMA_VERSION = "csm-v1"` | `registry.py` |
| **Gap** | No negotiation protocol (e.g. client advertises supported versions; server picks best) | — |
| **Implementation options** | 1) Add `supported_versions` to task metadata; 2) Server returns `contract_version` in response; 3) MCP resource `thegent://contract/versions` | — |
| **Priority** | P1 | Low impact if only one version exists |

---

### FR-X08: Observability for Parse Quality, Semantic Quality, Fallback

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Unified observability for parse quality, semantic quality, fallback frequency | Research validation §9 |
| **Current** | Partial: `ContractTelemetry`, `thegent observe kpis`, `thegent observe drift`, `get_fallback_kpis` | XB3 done |
| **Gap** | No single dashboard/view; metrics scattered across CLI commands | — |
| **Existing metrics** | `fallback_rate`, `fallback_success`, `structural_drift_pct`, `semantic_drift_pct`, `conformance_rate` | `cli.py`, `telemetry.py` |
| **Implementation options** | 1) `thegent observe summary` aggregating all; 2) Export to OTLP/Prometheus; 3) Dashboard spec in `docs/observability/` | — |
| **Priority** | P2 | KPIs exist; unification is polish |

---

## 3. Delta Set A: Contract and Parser Engineering (XA1, XA3, XA4)

### XA1: Canonical Schema Package `contracts/csm/v1`

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Versioned package layout for canonical schema | Cross-analysis matrix |
| **Current** | `contracts/csm/v1/__init__.py`; `contracts/csm/__init__.py` re-exports | ✅ Done |
| **Gap** | — | — |
| **Implementation** | Created `contracts/csm/v1/` with CanonicalStructuredMessage; `csm/` re-exports for backward compat | — |
| **Priority** | P0 (per matrix) | ✅ Done |

---

### XA3: Streaming Parser with Partial-Commit Safety

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Streaming parser with safe partial commits | Cross-analysis matrix |
| **Current** | `IncrementalXMLParser`, `get_partial_state` exist | V3 done |
| **Gap** | "Partial-commit safety" — unclear if we guarantee no partial writes on stream truncation | — |
| **Implementation** | Document current behavior; add `commit_checkpoint()` that only persists when chunk is complete; add tests for truncation | — |
| **Priority** | P1 | Clarify vs. implement |

---

### XA4: Contract Version Negotiation in Task Metadata

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Task metadata carries contract version for negotiation | Cross-analysis matrix |
| **Current** | `--contract-version` on run/bg; `RunMeta` does not store it | — |
| **Gap** | Task/WBS/DAG nodes don't declare `contract_version` | — |
| **Implementation** | Add `contract_version` to `RunMeta`, WBS node schema, DAG node schema | — |
| **Priority** | P1 | Depends on FR-X01 |

---

## 4. Kush Docs: Contract Authority and CI (XK3, XK4)

### XK3: Contract Authority Publication

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | Resolve task-tool docs vs impl mismatch | Kush deep-dive |
| **Current** | `CONTRACT_AUTHORITY.md`, `task_graph`/`snake_case` aligned | Gaps doc P0 done |
| **Gap** | "Publication" — ensure docs are single source; CI checks doc/impl sync | — |
| **Implementation** | 1) Doc generation from schema; 2) CI job: `thegent govern conformance` + doc hash check | — |
| **Priority** | P2 | Maintenance |

---

### XK4: CI Architecture Boundary Checks (tach/grimp/deply style)

| Aspect | Status | Notes |
|--------|--------|-------|
| **Requirement** | CI enforces architecture boundaries (e.g. no cross-layer imports) | Kush deep-dive |
| **Current** | No tach/grimp/deply tooling | — |
| **Gap** | No automated boundary checks | — |
| **Implementation** | Add `tach` or custom script: `contracts/` must not import `execution/`; `orchestrate/` must not import `govern/` | — |
| **Priority** | P2 | Quality |

---

## 5. Governance WP Gaps (WP-3003, WP-3006, WP-3008)

### WP-3003: Override Path with TTL — Revalidation on Expiry

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | `--override` flag; `OverrideRegistry` with `override_ttl_seconds`; cached override within TTL | `execution.py`, `config.py` |
| **Gap** | "Revalidation on expiry" — when TTL expires, next run must re-justify | — |
| **Actual behavior** | `OverrideRegistry.has_unexpired()` returns False after TTL; policy re-evaluates; if deny, user must supply `--override` again | `cli_impl.py` 1001–1005 |
| **Conclusion** | ✅ Effectively done: expiry forces re-justification | — |

---

### WP-3006: Compliance Evidence Retention — Tiered Storage, Domain Tagging

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | `THGENT_RETENTION_DAYS_SESSIONS`; `govern archive`; `govern data-protection` | `config.py`, `cli.py` |
| **Gap** | Tiered storage (hot 30d, cold 1yr); domain tagging for compliance domains | IMPLEMENTATION_STATUS |
| **Implementation** | 1) `govern archive --tier hot|cold`; 2) Add `domain` tag to sessions; 3) Retention policy per domain | — |
| **Priority** | P2 | Compliance-heavy orgs |

---

### WP-3008: Escalation SLA — Governance Queue Operations

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | RUNBOOK.md has escalation links; no formal queue | — |
| **Gap** | Escalation queue schema; SLA tracking; priority dispatch | GOVERNANCE_WP_VERIFICATION |
| **Implementation** | `governance/escalation.py`: queue schema, SLA timers, `thegent govern escalate` | — |
| **Priority** | P2 | HITL / enterprise |

---

## 6. Orchestration WBS Gaps (WP-0002, WP-0005, WP-6007)

### WP-0002: Canonical Schemas for Chunk/Evidence/Policy Events

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | `contracts/events.py` with ChunkEvent, EvidenceEvent, PolicyEvent (Pydantic) | ✅ Done |
| **Gap** | — | — |
| **Implementation** | Added `contracts/events.py` with Pydantic models | — |
| **Priority** | P2 | ✅ Done |

---

### WP-0005: Program Operating Model and Ownership Map

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | Unclear | Gaps doc |
| **Gap** | RACI matrix; ownership assignments; escalation paths | SUBAGENT-DISPATCH |
| **Implementation** | Create `docs/enterprise/OPERATING_MODEL.md` | — |
| **Priority** | P2 | Org readiness |

---

### WP-6007: Post-Launch Observation and Rollback Reserve

| Aspect | Status | Notes |
|--------|--------|-------|
| **Current** | `POST_LAUNCH_OBSERVATION_PLAYBOOK.md` drafted; rollback reserve defined | IMPLEMENTATION_STATUS |
| **Gap** | Incident severity classification; escalation SLA mapping; finalize playbook | — |
| **Implementation** | Complete playbook; add severity→SLA table; rollback capacity checklist | — |
| **Priority** | P2 | Launch readiness |

---

## 7. FastMCP Verification (F2, F3, F4, F19)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| F2 | `thegent_run` with gemini/cursor-agent | [ ] | Requires API key; run `scripts/verify-fastmcp.py --no-skip-api` |
| F3 | `thegent_bg` / `thegent_ps` | [ ] | Requires API key |
| F4 | Progress updates during long run | [ ] | Manual verification |
| F19 | Icons/UX hints for tools | Not implemented | Optional |

---

## 8. Summary: Remaining Work by Priority

| Priority | Items | Effort |
|----------|-------|--------|
| **P0** | XA1 (canonical schema package) | 1–2 days |
| **P1** | FR-X01, XA3, XA4 (version negotiation, partial-commit, task metadata) | 2–4 days |
| **P2** | FR-X08, XK3, XK4, WP-3006, WP-3008, WP-0002, WP-0005, WP-6007 | 4–8 days |
| **Manual** | F2, F3, F4 (FastMCP with API keys) | — |
| **Optional** | F19 (icons) | — |

---

## 9. References

- `docs/docset/thegent-gaps-and-discovery-2026-02-14.md`
- `docs/docset/thegent-research-validation-2026-02-14.md`
- `docs/docset/thegent-cross-analysis-matrix-2026-02-14.md`
- `docs/GOVERNANCE_WP_VERIFICATION.md`
- `docs/docset/IMPLEMENTATION_STATUS.md`
