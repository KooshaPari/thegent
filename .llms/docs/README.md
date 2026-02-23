# Documentation Architecture

> **Last Updated:** 2026-02-23

## Canonical Documentation

The following documentation files in the root of thegent are the **authoritative source of truth**:

### Core Specification Documents
| File | Purpose |
|------|---------|
| `ADR.md` | Architecture Decision Records (001-017) |
| `PRD.md` | Product Requirements Document |
| `FUNCTIONAL_REQUIREMENTS.md` | All Functional Requirements (95 FRs) |
| `docs/reference/FR_TRACKER.md` | FR implementation status tracker |

### Tracking & Planning
| File | Purpose |
|------|---------|
| `docs/WORKLOG.md` | Current sprint and wave tracking |
| `docs/reference/WORK_STREAM.md` | Canonical backlog |
| `PLAN.md` | Master project plan |
| `CHANGELOG.md` | Version history |

## .llms/docs/ vs docs/

**This directory (`.llms/docs/`) is DEPRECATED** in favor of `docs/`.

The `.llms/docs/` folder contains:
- LLM-generated research and analysis (`.llms.txt` files)
- Session-scoped work artifacts
- Temporary working documents

The `docs/` folder contains:
- Human-maintained documentation
- Canonical specifications
- Planning documents

### Migration Status

All important content from `.llms/docs/` should be migrated to `docs/` and the `.llms.txt` files removed.

## Updating Documentation

1. **Core specs**: Edit root `ADR.md`, `PRD.md`, `FUNCTIONAL_REQUIREMENTS.md`
2. **FR Status**: Edit `docs/reference/FR_TRACKER.md`
3. **Work tracking**: Edit `docs/WORKLOG.md` and `docs/reference/WORK_STREAM.md`
4. **Release notes**: Edit `CHANGELOG.md`

## Tools

- `docs_engine/` - Documentation generation system
- `contracts/items-generated/` - JSON contract items for specs
