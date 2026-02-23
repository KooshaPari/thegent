# Unified Workspace Project Master Index

## Purpose
This is the single source of truth for all project documentation structure, maintenance guidance, and canonical file locations.

## Project Canonical Files

Each project MUST maintain:

### Required Canonical Files
| File | Purpose | Location |
|------|---------|------------|
| CHANGELOG.md | Release history | Project root |
| MASTER_INDEX.md | This file | docs/ or root |
| WORK_STREAM.md | Current work tracking | docs/reference/ |
| PLAN.md | Current roadmap | docs/planning/ |

### Required Spec Types
| Type | Location | Pattern |
|------|----------|----------|
| PRD | docs/ | `PRD_*.md` |
| ADR | docs/adr/ or docs/reference/ | `ADR-*.md` |
| SPEC | docs/specs/ or docs/features/ | `SPEC.md` or `*_SPEC.md` |

### Required Tracking Files
| Type | Purpose |
|------|----------|
| FR_TRACKER.md | Feature requests |
| PRD_TRACKER.md | PRD items |
| PLAN_STATUS.md | Implementation status |

### Documentation Taxonomy
See `DOCUMENTATION_TAXONOMY.md` for complete type system including:
- Human-facing docs (guides, tutorials, runbooks)
- Technical specs (SPEC, PROTOCOL, CONTRACT)
- Planning (ROADMAP, RESEARCH, VALIDATION)
- Operational (PLAYBOOK, OBSERVATION)

---

## Project Inventory

### 1. CLIPROXYAPI PlusPlus
**Root**: `cliproxyapi-plusplus/`

| Canonical File | Status | Lines |
|--------------|--------|-------|
| CHANGELOG.md | Active | - |
| docs/planning/MASTER_PLANNING_BOARD.md | Active | - |
| docs/planning/*BOARD*.csv | 2 boards | 2,000 items |

**Specs**: PRD, ADR, SPEC in `docs/features/*/`

### 2. THEGENT
**Root**: `thegent/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/reference/WORK_STREAM.md | Active |
| docs/plans/MASTER_PLAN.md | Active |
| docs/adr/ | 15+ ADRs |

**Specs**: 13+ SPEC files in docs/

### 3. TRACE
**Root**: `trace/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/reference/PRD.md | Active |
| docs/adr/ | 15+ ADRs |
| docs/reference/SPEC*.md | 82 specs |

### 4. 4SGM
**Root**: `4sgm/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/reference/PLAN_STATUS.md | Active |
| docs/reference/PRD_TRACKER.md | Active |
| docs/architecture/adr/ | 4 ADRs |

### 5. HELIOS HARNESS
**Root**: `heliosHarness/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/reference/PLAN_STATUS.md | Active |
| docs/reference/PRD_TRACKER.md | Active |

### 6. PARPOUR
**Root**: `parpour/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/reference/WORK_STREAM.md | Active |
| docs/adr/ | 3 ADRs |

### 7. CIV
**Root**: `civ/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Active |
| docs/SPEC*.md | 2 specs |
| docs/adr/ | 3 ADRs |

### 8. PLANGENT
**Root**: `plangent/`

| Canonical File | Status |
|--------------|--------|
| CHANGELOG.md | Missing |
| docs/planning/PHASE_*.md | 6 phases |

---

## Maintenance Guidance

### For Project Maintainers

#### Changelog Format
```markdown
# Changelog

## [Unreleased]

### Added
- Feature description

### Changed
- Breaking change description

### Fixed
- Bug fix

## [Version] - YYYY-MM-DD
```

#### WORK_STREAM.md Format
```markdown
# Work Stream

## Current Sprint
- Item #ID - Description | Status | Owner

## Backlog
- Item #ID - Description | Priority
```

#### ADR Format
```markdown
# ADR-XXX: Title

## Status: Proposed|Accepted|Deprecated

## Context
## Decision
## Consequences
```

### Canonical Locations
- Planning: `docs/planning/`
- Specs: `docs/adr/` or `docs/reference/`
- Research: `docs/research/`
- Reports: `docs/reports/`

---

## Quick Reference

| Project | Root CHANGELOG | Planning | Specs | ADRs |
|---------|-----------------|----------|-------|------|
| CLIPROXYAPI++ | ✓ | ✓ | ✓ | ✓ |
| THEGENT | ✓ | ✓ | ✓ | ✓ |
| TRACE | ✓ | ✓ | ✓ | ✓ |
| 4SGM | ✓ | ✓ | - | ✓ |
| HELIOS | ✓ | - | - | - |
| PARPOUR | ✓ | - | ✓ | ✓ |
| CIV | ✓ | - | ✓ | ✓ |
| PLANGENT | ✗ | ✓ | ✓ | - |

---

*Last Updated: 2026-02-23*
