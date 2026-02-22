# Scaffolder Questionnaire DX/AX/UX Implementation Plan

Date: 2026-02-21
Status: Completed
Planning Mode: Agent-led execution

## Goal

Upgrade `templates/initialize-project` into a production-grade questionnaire and instruction scaffold with clear project-type delineation and strong defaults.

## Phased WBS

### Phase 1: Audit

- SQ-01 Audit current Copier configuration and template variable conventions.
- SQ-02 Identify runtime validation failures via real Copier smoke run.

### Phase 2: Design

- SQ-03 Define questionnaire schema and field constraints.
- SQ-04 Define generated `CLAUDE.md` structure with DX/AX/UX sections.

### Phase 3: Implement

- SQ-05 Update `templates/initialize-project/copier.yml` with expanded questions and validators.
- SQ-06 Normalize template path/variables to Copier-native expressions.
- SQ-07 Update `templates/initialize-project/README.md` with matrix guidance.
- SQ-08 Update `templates/initialize-project/{{ project_name }}/CLAUDE.md` and `templates/claude/CLAUDE.md.template`.

### Phase 4: Validate

- SQ-09 Run Copier smoke render and verify no unresolved template tokens.
- SQ-10 Validate generated `CLAUDE.md` reflects questionnaire selections.

### Phase 5: Record

- SQ-11 Write research/plan/report artifacts and update work stream completion ledger.

## DAG

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| Audit | SQ-01 | Audit current template and syntax model | none |
| Audit | SQ-02 | Execute baseline Copier smoke and capture failures | SQ-01 |
| Design | SQ-03 | Finalize questionnaire schema | SQ-02 |
| Design | SQ-04 | Finalize generated CLAUDE structure | SQ-03 |
| Implement | SQ-05 | Implement Copier question set and validation | SQ-04 |
| Implement | SQ-06 | Migrate path/variables to Copier-native format | SQ-05 |
| Implement | SQ-07 | Update README questionnaire guidance | SQ-05 |
| Implement | SQ-08 | Update CLAUDE templates | SQ-06 |
| Validate | SQ-09 | Re-run Copier smoke and check token expansion | SQ-07, SQ-08 |
| Validate | SQ-10 | Validate rendered profile alignment | SQ-09 |
| Record | SQ-11 | Write docs and update work stream | SQ-10 |

## Runtime Estimate

10-18 tool calls, ~6-15 minutes wall-clock with one validation rerun loop.
