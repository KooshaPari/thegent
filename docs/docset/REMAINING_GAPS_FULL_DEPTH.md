# Remaining Gaps — Full Depth Analysis

**Date:** 2026-02-14 (updated)  
**Source:** `thegent-gaps-and-discovery-2026-02-14.md`, `GOVERNANCE_WP_GAPS.md`  
**Purpose:** Comprehensive analysis of all remaining gaps with implementation options, acceptance criteria, and current state.

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| **Done (this session)** | 12+ | WP-3006 A/C, WP-3008 A/B, FR-X08, XC2, domain tagging, retention_by_domain, escalate add |
| **Remaining actionable** | 8 | FR-X01, XA3, XA4, FR-X08 summary, WP-0002, XK3, XK4, WP-3006 B |
| **Manual / deferred** | 5 | F2/F3/F4 (API keys), F19 (icons), WP-3008 C (DLQ) |

---

## 1. Contract and Parser Engineering

### XA1: Canonical Schema Package `contracts/csm/v1` ✅ DONE

| Aspect | Status |
|--------|--------|
| **Requirement** | Versioned package layout |
| **Current** | `contracts/csm/v1/__init__.py` with CanonicalStructuredMessage; `contracts/csm/` re-exports |
| **Conclusion** | Implemented. csm.py exists as legacy; imports use csm package. |

---

### XA3: Streaming Parser Partial-Commit Safety (P1)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Safe partial commits on stream truncation |
| **Current** | IncrementalXMLParser, get_partial_state exist |
| **Gap** | No explicit commit_checkpoint(); truncation behavior undocumented |
| **Implementation** | 1) Document in CONTRACT_AUTHORITY.md; 2) Add truncation tests; 3) Optional: commit_checkpoint() for explicit safe points |
| **Effort** | 1–2 days |

---

### XA4: Contract Version in Task Metadata (P1)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | RunMeta, WBS, DAG nodes carry contract_version |
| **Current** | --contract-version on run/bg; passed to MigrationController; RunMeta does not store it |
| **Gap** | RunMeta lacks contract_version field; DAG task schema lacks it |
| **Implementation** | Add contract_version to RunMeta; optional: add to DAG task schema |
| **Effort** | 0.5 day |

---

### FR-X01: Contract Version Negotiation (P1)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Client advertises supported versions; server picks best |
| **Current** | Single version csm-v1; --contract-version accepts explicit version |
| **Gap** | No negotiation protocol (e.g. supported_versions in request, server response) |
| **Implementation** | 1) MCP resource thegent://contract/versions; 2) Task metadata supported_versions; 3) Server returns negotiated version |
| **Effort** | 1–2 days |
| **Priority** | Low while only one version exists |

---

## 2. Observability (FR-X08)

### FR-X08: Unified Observability Dashboard (P2)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Single view aggregating parse quality, fallback, drift |
| **Current** | observe kpis, observe drift, closure_pack telemetry; metrics scattered |
| **Gap** | No `observe summary` aggregating all |
| **Implementation** | Add `thegent observe summary` — calls get_fallback_kpis + get_drift_budget_status + escalate list count |
| **Effort** | 0.5 day |

---

## 3. Event Schemas (WP-0002)

### WP-0002: Canonical Schemas for Chunk/Evidence/Policy Events (P2)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Formal Pydantic/JSON Schema for audit events |
| **Current** | Run registry uses ad-hoc dicts (finish, feedback, pause, etc.) |
| **Gap** | No ChunkEvent, EvidenceEvent, PolicyEvent schemas |
| **Implementation** | Add `contracts/events.py` with ChunkEvent, EvidenceEvent, PolicyEvent |
| **Effort** | 1 day |

---

## 4. Kush Docs and CI (XK3, XK4)

### XK3: Contract Authority Publication (P2)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Doc/impl sync; CI checks |
| **Current** | CONTRACT_AUTHORITY.md, task_graph aligned |
| **Gap** | No CI job verifying doc/impl sync |
| **Implementation** | CI: `thegent govern conformance` + optional doc hash check |
| **Effort** | 0.5 day |

---

### XK4: CI Architecture Boundary Checks (P2)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | tach/grimp-style layer enforcement |
| **Current** | None |
| **Gap** | No automated boundary checks (contracts/ vs execution/, etc.) |
| **Implementation** | Add script or tach: contracts/ must not import execution/; layer rules |
| **Effort** | 1 day |

---

## 5. Governance (Completed)

### WP-3003, WP-3006, WP-3008 ✅ DONE

- **WP-3003:** Override TTL, revalidation on expiry
- **WP-3006:** Domain tagging (run/bg --domain), THGENT_RETENTION_BY_DOMAIN, govern archive --domain
- **WP-3008:** EscalationQueue, govern escalate add/list/resolve, auto-add on policy deny

### WP-3006 Option B: Tiered Storage (Deferred)

| Aspect | Status | Notes |
|--------|--------|------|
| **Requirement** | Hot (30d) vs cold (1yr) storage paths |
| **Gap** | No --tier hot|cold; no cold storage path |
| **Implementation** | Define cold path; govern archive --tier cold moves to cold |
| **Effort** | 2–3 days |
| **When** | When cold storage path is defined |

---

## 6. Migration (V7 / FR-X07)

### Dual-Read/Dual-Write Pipeline (Partial)

| Aspect | Status | Notes |
|--------|--------|------|
| **Current** | MigrationController, evaluate_version, govern migration |
| **Gap** | Pipeline does not dual-read/write during migration window |
| **Implementation** | Wire normalization pipeline to read both versions; write to both during window |
| **Effort** | 2–3 days |
| **Priority** | Deferred until multi-version rollout |

---

## 7. FastMCP Verification (Manual)

| ID | Item | Blocker |
|----|------|---------|
| F2 | thegent_run with gemini/cursor-agent | API key |
| F3 | thegent_bg / thegent_ps | API key |
| F4 | Progress updates during long run | Manual |
| F19 | Icons/UX hints | Optional |

**Action:** Run `scripts/verify-fastmcp.py --no-skip-api` when keys available.

---

## 8. Implementation Priority

| Priority | Items | Effort |
|----------|-------|--------|
| **P1 (immediate)** | XA4 (RunMeta contract_version), FR-X08 (observe summary), WP-0002 (events.py) | 2 days |
| **P2 (short)** | XA3 (partial-commit doc/tests), XK3 (CI doc check), XK4 (boundary script) | 2–3 days |
| **P2 (deferred)** | FR-X01, WP-3006 B, V7 dual-read/write | 4–6 days |
| **Manual** | F2, F3, F4 | — |

---

## References

- `docs/docset/thegent-gaps-and-discovery-2026-02-14.md`
- `docs/research/GOVERNANCE_WP_GAPS.md`
- `docs/docset/REMAINING_GAPS_DEEP_DIVE.md` (legacy; superseded by this doc)
