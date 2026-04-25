# thegent — Canonical Spec ID Mapping

**Last Updated:** 2026-04-25  
**Audit:** W-56 Spec-to-Reality Alignment

## Spec Numbering Scheme

thegent adopts the AgilePlus canonical numbering: `thegent-NNN` (zero-padded, 3-digit IDs).

Root-level domain plans (.md files) are mapped to numeric IDs for cross-repo consistency.

---

## Spec Matrix

| Spec ID | Name | Type | Status | File | Evidence |
|---------|------|------|--------|------|----------|
| **thegent-001** | Core Platform | ROOT | **DONE** | `PRD.md` | Vision + scope defined (commit 2589828, 2026-03); feature list in SPEC.md |
| **thegent-002** | Specification + Feature Inventory | ROOT | **DONE** | `SPEC.md` | Current (commit 93404b6, 2026-04); comprehensive feature list |
| **thegent-003** | High-Level Roadmap | ROOT | **CURRENT** | `PLAN.md` | Updated (commit 93404b6, 2026-04); tracks quarterly phases |
| **thegent-004** | Architecture Decisions | ROOT | **CURRENT** | `ADR.md` | Updated (commit 5e5a054, 2026-04); hexagonal + polyrepo decisions recorded |
| **thegent-005** | Desktop Agent (Cursor) Implementation | DOMAIN-PLAN | **DONE** | `DESKTOP_AGENT_CURSOR_PLAN.md` | Cursor agent implementation complete (2026-03); agent framework active |
| **thegent-006** | Go-to-Rust Migration | DOMAIN-PLAN | **IN_PROGRESS** | `RUST_MIGRATION_PLAN.md` | Go→Rust path active (commits: fa0ee8d, 05e5a28, 2026-04); gRPC codegen stabilized |
| **thegent-007** | Library Audit + Dependency Review | DOMAIN-PLAN | **DONE** | `LIBRARY_AUDIT_PLAN.md` | Audit completed (2026-03); dependency decisions documented |
| **thegent-008** | LOC Reduction Phase 1 | DOMAIN-PLAN | **DONE** | `LOC_REDUCTION_PLAN.md` | Phase 1 complete (2,350 LOC reduction, 4 shared crates); zero warnings (commit c06cd22, 2026-04); see memory session 2026-03-29 |
| **thegent-009** | Test-First Development (Track 3) | DOMAIN-PLAN | **IN_PROGRESS** | `TRACK_3_TDD_PLAN.md` | TDD mandate active (commits: 165+ test fixes, 2026-03); test coverage expanding |
| **thegent-010** | Phase 4 Repository Consolidation | DOMAIN-PLAN | **IN_PROGRESS** | `PHASE4_CONSOLIDATION_PLAN.md` | Consolidation phase active (commits: 93404b6, 5e5a054, 2026-04) |
| **thegent-011** | Code Extraction + Modularization | DOMAIN-PLAN | **IN_PROGRESS** | `EXTRACTION_PLAN.md` | Extraction phase active (2026-04); phenotype-shared crates integrated |
| **thegent-012** | Mobile Automation Framework | DOMAIN-PLAN | **IN_PROGRESS** | `THEGENT_MOBILE_AUTOMATION_PRD.md` | Mobile agent spec (commit 2026-03); framework design documented |

---

## Status Legend

| Status | Definition | Next Action |
|--------|-----------|-------------|
| **DONE** | Feature shipped, plan archived, tests passing, or domain complete | Archive to `docs/specs/archive/` if obsolete; maintain in CHANGELOG |
| **CURRENT** | Root-level spec actively maintained; reflects current architecture | Keep updated with quarterly reviews |
| **IN_PROGRESS** | Active commits in past 2 weeks; work packages advancing | Link to active PR/branch; target release version |
| **DEFERRED** | Planned; no active commits in past 30 days | Document reason; target release date |
| **OBSOLETE** | No longer needed; feature cancelled or migrated to separate repo | Archive in `docs/specs/archive/` with handoff notes |

---

## Root-Level Docs with Status Markers

### PRD.md
```yaml
---
title: thegent — Product Requirements
spec_id: thegent-001
status: DONE
version: current
last_updated: 2026-04-25
evidence:
  - commit: 2589828
    message: "docs(prd): core vision + personas"
  - commit: 93404b6
    message: "docs(prd): quarterly roadmap update"
---
```

### SPEC.md
```yaml
---
title: thegent — Specification
spec_id: thegent-002
status: DONE
version: current
last_updated: 2026-04-25
evidence:
  - commit: 93404b6
    message: "docs(spec): feature inventory refresh"
---
```

### PLAN.md
```yaml
---
title: thegent — Roadmap
spec_id: thegent-003
status: CURRENT
version: Q2-2026
last_updated: 2026-04-25
notes: |
  Quarterly roadmap. Maps to active domain plans (thegent-005 through thegent-012).
  Next review: Q3-2026.
---
```

### ADR.md
```yaml
---
title: thegent — Architectural Decisions
spec_id: thegent-004
status: CURRENT
version: current
last_updated: 2026-04-25
evidence:
  - commit: 5e5a054
    message: "docs(adr): hexagonal + polyrepo decisions"
---
```

---

## Domain Plans (Root-Level Organization)

thegent consolidates domain-specific plans at the repo root. These should migrate to `docs/specs/` over time (see migration plan in recommendations section).

### Migration Path (Optional)

When consolidating documentation, move domain plans to `docs/specs/` with this structure:

```
docs/specs/
  thegent-005-desktop-agent/
    spec.md (archived, DONE)
    plan.md (historical)
  thegent-006-rust-migration/
    spec.md (active)
    plan.md (milestones)
  ...
```

Preserve root-level `PRD.md`, `PLAN.md`, `ADR.md`, `SPEC.md` as navigation hubs.

---

## Integration with AgilePlus

When creating new thegent specs in AgilePlus, use the prefix `thegent-NNN`:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify --title "thegent-013: <feature>" --description "..."
```

Extend the mapping above when new domain plans are created.

---

## Cross-Repo Reference

- **AgilePlus:** eco-series (eco-001 through eco-012) + numbered series (001–022)
- **FocalPoint:** FocalPoint-001 through FocalPoint-010 (see `docs/spec_id_map.md`)
- **thegent:** thegent-001 through thegent-012 (this file)

For multi-repo features, use hyphenated IDs: `thegent-006:Rust-FFI-Entrypoints` or `cross-repo:Polyrepo-Build-Coordination`.

---

## Test Traceability

To link tests to specs, use prefix markers in test names/files:

```rust
// Traces to: thegent-009 (TDD mandate)
#[test]
fn test_agent_skill_system_integration() {
    // test body
}
```

When adding new tests for domain plans, include the spec ID in:
1. Test function name or
2. File path prefix (e.g., `tests/thegent_009_tdd_*.rs`)
3. Comment block above test

---

**Updated by:** W-56 Spec-to-Reality Alignment Agent  
**Audit Link:** `/repos/docs/org-audit-2026-04/spec_reality_reconciliation_2026_04_25.md`
