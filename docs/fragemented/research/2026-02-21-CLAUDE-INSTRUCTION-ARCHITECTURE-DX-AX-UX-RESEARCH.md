# CLAUDE Instruction Architecture Research (DX/AX/UX)

**Date:** 2026-02-21
**Status:** Active
**Scope:** Standardize global vs project instruction architecture with high readability and maintainability.

---

## Objective

Define a clean instruction architecture that:

1. prevents instruction sprawl and duplication,
2. clarifies global vs project ownership,
3. improves developer experience (DX), agent experience (AX), and reader experience (UX).

---

## Current Friction

1. Global and project concerns are often mixed, reducing scanability.
2. Long instruction files hide operationally critical rules.
3. Instruction entry points are not always obvious for new contributors/agents.
4. Cross-doc navigation exists but is not consistently codified as an explicit doc map.

---

## DX/AX/UX Polish Scope

### DX (Developer Experience)

1. Fast “where do I edit this rule?” clarity.
2. Stable global baseline with minimal churn.
3. Explicit placement rules for governance vs plans vs reports.

### AX (Agent Experience)

1. Deterministic precedence order (system/dev -> global -> project -> task artifacts).
2. Single instruction index with predictable links.
3. Reduced token waste from repeated policy duplication.

### UX (Reader Experience)

1. Top-of-file architecture section with role definitions.
2. Doc map links for immediate navigation.
3. Short index + deep linked detail (progressive disclosure).

---

## Architecture Recommendation

1. Keep `CLAUDE.md` as a concise global index + critical guardrails.
2. Keep long-form policy in `docs/reference/CLAUDE_CORE_GUIDELINES.md`.
3. Keep thegent runtime specifics in `docs/reference/CLAUDE_THEGENT_RUNTIME_APPENDIX.md`.
4. Keep execution cadence in `docs/reference/WORK_STREAM.md`.
5. Keep change-specific context in dated research/plan/report docs.

---

## Success Criteria

1. `CLAUDE.md` has explicit “Instruction Architecture (Global vs Project)” section.
2. Governance summary and polyglot matrix reference the same architecture model.
3. One research + one plan + one report/worklog doc exists for this upgrade.
4. Work stream has a completed item entry with a new incremental ID.
