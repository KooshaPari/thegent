# Unified Worktree & Workflow Governance

**Status:** Active Policy
**Supersedes:** `WORKTREE_SCALE_COMMIT_VERSION_PR_POLICY.md` (still authoritative for commit/PR/merge rules — this doc adds the path schema and system harmonization layer)
**Systems Harmonized:** thegent worktree policy + BMAD lifecycle phases + OpenSpec change anchors
**Last Updated:** 2026-02-24

---

## 1. Purpose

This document establishes a single, unified taxonomy for:

1. **Where** worktrees live on disk (path schema)
2. **What state** a worktree is in (lifecycle state)
3. **How** work in a worktree maps to BMAD phases and OpenSpec change IDs
4. **Which tooling** enforces each layer

It does not replace the commit, versioning, or PR rules in `WORKTREE_SCALE_COMMIT_VERSION_PR_POLICY.md` — those remain authoritative. It extends them with a physical path convention and cross-system vocabulary.

---

## 2. Core Invariants (Non-Negotiable)

1. Primary checkout is always pinned to `main`. Never do feature work there.
2. All non-primary worktrees live under `<repo>/.worktrees/` (or `$THGENT_WORKTREE_ROOT`).
3. Worktree paths are deterministic from their metadata — no ad-hoc naming.
4. Worktrees outside `.worktrees/` (e.g. `/tmp/`, `~/`, stranded from renames) are **non-compliant** and must be migrated or pruned.
5. A worktree's path encodes its full context: repo, domain, scale, change anchor, and state.

---

## 3. Unified Path Schema

```
<repo>/.worktrees/<domain>/<scale>/<change-anchor>/<state>/
```

### 3.1 Schema Segments

| Segment | Source | Values |
|---------|--------|--------|
| `<repo>` | Git repo name | `thegent`, `cliproxy++`, `heliosHarness`, etc. |
| `<domain>` | Task classifier `domain` field | `backend`, `frontend`, `infra`, `data`, `docs`, `research`, `security`, `qa`, `release`, `ops` |
| `<scale>` | Task classifier `scale` field | `xs`, `s`, `m`, `l`, `xl` |
| `<change-anchor>` | OpenSpec change-id (verb-led, kebab-case) | e.g. `fix-mcp-timeout`, `add-dag-tests`, `refactor-config-layer` |
| `<state>` | Lifecycle state (see §4) | `active`, `review`, `blocked`, `integration`, `done` |

### 3.2 Full Example Paths

```
thegent/.worktrees/backend/m/fix-mcp-timeout/active/
thegent/.worktrees/qa/s/add-dag-tests/review/
thegent/.worktrees/infra/xs/bump-lint-config/done/
cliproxy++/.worktrees/security/l/clear-text-logging-v2/blocked/
heliosHarness/.worktrees/infra/m/infra-work/active/
```

### 3.3 Git Branch Name

The git branch name is derived from the path (not the reverse):

```
<domain>/<scale>/<change-anchor>
```

Examples:
- `backend/m/fix-mcp-timeout`
- `qa/s/add-dag-tests`
- `security/l/clear-text-logging-v2`

Legacy branch names (e.g. `thegent-mcp-fix`, `feature/wl-implementation`) are allowed in existing branches but new branches must use this schema.

---

## 4. Lifecycle States

States map to BMAD phases and OpenSpec proposal stages.

| State | Dir Name | BMAD Phase Equivalent | OpenSpec Stage | Meaning |
|-------|----------|----------------------|----------------|---------|
| `active` | `active/` | Phase 4 — Implementation | Apply | Work in progress, agent or human actively committing |
| `review` | `review/` | Phase 4 — Review Story | Apply (pending approval) | PR open or awaiting code review |
| `blocked` | `blocked/` | Phase 3 — Readiness / Solutioning | Propose | Waiting on dependency, decision, or upstream merge |
| `integration` | `integration/` | Phase 4 — Sprint Planning / Merge | Apply (integration train) | Merge train or integration worktree in progress |
| `done` | `done/` | Post Phase 4 — Retrospective | Archive | Branch merged, worktree retained briefly before pruning |

### 4.1 State Transitions

```
[proposed] → active → review → integration → done
                ↓
            blocked → active (when unblocked)
```

State is changed by renaming the worktree directory:
```bash
# move from active to review
git worktree move .worktrees/backend/m/fix-mcp-timeout/active \
                  .worktrees/backend/m/fix-mcp-timeout/review
```

Or via the governance script (see §7):
```bash
./scripts/worktree_governance.sh state <change-anchor> review
```

---

## 5. BMAD Phase → Worktree Mapping

BMAD defines 5 phases (0–4) plus a parallel testing track. Each maps to a worktree state or signals that no worktree is needed yet.

| BMAD Phase | Name | Worktree Needed? | State |
|------------|------|-----------------|-------|
| 0 | Documentation / Brownfield Capture | No | — (docs only) |
| 1 | Analysis (research, brainstorm) | No | — (docs only) |
| 2 | Planning (PRD, UX, tech-spec) | No | — (docs only) |
| 3 | Solutioning (architecture, epics, stories) | No until approved | `blocked` if pre-approved work queued |
| 4 — Story Creation | Dev story scaffold | Yes | `active` |
| 4 — Implementation | Active coding | Yes | `active` |
| 4 — Review | PR / code review | Yes | `review` |
| 4 — Integration | Merge train | Yes | `integration` |
| 4 — Retrospective | Post-merge | Optional | `done` |
| Testing (parallel) | ATDD, CI, coverage | Yes (parallel to Phase 4) | `active` under `qa/` domain |

**Rule:** Do not create a worktree during BMAD Phases 0–2. Create the worktree at the start of Phase 4 (when a dev story exists and work is approved).

---

## 6. OpenSpec Change Anchor Integration

Every worktree's `<change-anchor>` segment **is** (or maps 1:1 to) an OpenSpec `change-id`.

This means:
- Every worktree has a corresponding `openspec/changes/<change-anchor>/` directory in the repo
- `proposal.md` in that change dir is the source-of-truth for what the worktree is doing
- `tasks.md` drives the commit sequence inside the worktree
- When the worktree reaches `done`, run `openspec archive <change-anchor> --yes`

### 6.1 Exceptions (no OpenSpec proposal required)

Per OpenSpec policy, skip the proposal for:
- Bug fixes (typos, formatting, dependency bumps, config changes)
- Tests for existing behavior

For these, use a descriptive `<change-anchor>` that starts with `fix-` or `test-` and omit the `openspec/changes/` scaffold. The worktree path schema still applies.

### 6.2 Worktree ↔ OpenSpec Mapping Example

```
thegent/.worktrees/backend/m/fix-mcp-timeout/active/
  ↕
thegent/openspec/changes/fix-mcp-timeout/
  ├── proposal.md
  ├── tasks.md
  └── specs/mcp-client/spec.md
```

---

## 7. Tooling

### 7.1 Existing Script (extended)

`./scripts/worktree_governance.sh` already supports `new`, `check`, `path`. It must be extended to support:

```bash
# Create a policy-compliant worktree
./scripts/worktree_governance.sh new <domain> <scale> <change-anchor> [start-point]

# Check all worktrees comply with schema
./scripts/worktree_governance.sh check

# Print expected path for a change anchor
./scripts/worktree_governance.sh path <domain> <scale> <change-anchor> <state>

# Transition a worktree's state
./scripts/worktree_governance.sh state <change-anchor> <new-state>

# List all worktrees with their metadata
./scripts/worktree_governance.sh list

# Prune done/broken worktrees
./scripts/worktree_governance.sh prune [--dry-run]
```

### 7.2 `thg_new_worktree` Wrapper

The existing `thg_new_worktree` shell helper should be updated to call the governance script's new signature:

```bash
thg_new_worktree <domain> <scale> <change-anchor> [start-point]
```

### 7.3 BMAD Integration Point

When starting BMAD Phase 4 (dev story), the first action after story approval is:
```bash
./scripts/worktree_governance.sh new <domain> <scale> <change-anchor>
```

If using an OpenSpec proposal, run `openspec validate <change-anchor> --strict` first.

---

## 8. Legacy Worktree Migration Plan

The following worktrees are non-compliant (broken gitdir pointers from `/temp-PRODVERCEL/` rename, or misplaced in `~/` or `/tmp/`). They must be migrated or pruned.

### 8.1 Broken (gitdir pointer to missing path) — Prune After Salvage

| Directory | Last Known Branch | Action |
|-----------|------------------|--------|
| `repos/thegent-dag-tests` | unknown | Salvage any unique commits → prune |
| `repos/thegent-flaky-tests` | unknown | Salvage → prune |
| `repos/thegent-lint-fix` | unknown | Salvage → prune |
| `repos/thegent-mcp-fix` | unknown | Salvage → prune |
| `repos/thegent-mcp-fix2` | unknown | Salvage → prune |
| `repos/thegent-mcp-fix3` | unknown | Salvage → prune |
| `repos/thegent-mcp-fix4` | unknown | Salvage → prune |
| `repos/thegent-merge` | unknown | Salvage → prune |
| `repos/thegent-output-tests` | unknown | Salvage → prune |
| `repos/thegent-skips-v2` | unknown | Salvage → prune |
| `repos/thegent-v2` | main (empty) | Prune (empty) |
| `repos/cliproxy++-config-fix` | fix/config-build | Salvage → prune |
| `repos/cliproxy++-security` | fix/security-clear-text-logging-v2 | Salvage → prune |
| `repos/heliosHarness-orchestration` | feature/sub-agent-orchestration | Salvage → prune |

### 8.2 Active but Misplaced — Migrate to Schema

| Directory | Branch | Target Path |
|-----------|--------|-------------|
| `/private/tmp/wl-impl` | `feature/wl-implementation` | `thegent/.worktrees/backend/m/wl-impl/active/` |
| `~/cliproxy++-security` | `main` (standalone clone) | Evaluate: merge to `repos/cliproxy++` or discard |
| `~/cliproxy++-security-work` | `security-fix` | `cliproxy++/.worktrees/security/m/clear-text-logging-v2/blocked/` |
| `temp-PRODVERCEL-485/kush/heliosHarness-infra` | `feature/infra-work` | `heliosHarness/.worktrees/infra/m/infra-work/active/` |

### 8.3 Migration Steps (per worktree)

1. Run `git log --oneline -10` in the worktree dir to identify unique commits.
2. If unique commits exist: cherry-pick or create a patch. If no unique commits: skip to step 4.
3. Create a compliant worktree: `./scripts/worktree_governance.sh new <domain> <scale> <change-anchor>`
4. Apply any salvaged commits to the new worktree.
5. Remove the old worktree directory: `git worktree remove --force <path>` then `git worktree prune`.

---

## 9. Vocabulary Cross-Reference

| This System | BMAD Term | OpenSpec Term | Task Classifier Field |
|-------------|-----------|---------------|----------------------|
| `<domain>` | Agent persona domain (backend, QA, etc.) | capability folder | `domain` |
| `<scale>` | Story size / sprint scope | — (not used) | `scale` (XS/S/M/L/XL) |
| `<change-anchor>` | Story ID / epic slug | `change-id` | `task_id` |
| `active` | Phase 4 — Implementation | Apply stage | — |
| `review` | Phase 4 — Review Story | Apply (pending) | — |
| `blocked` | Phase 3 — Readiness | Propose (approved, not started) | — |
| `integration` | Phase 4 — Sprint Planning / merge train | Apply (integration) | `worktree_mode: integration` |
| `done` | Retrospective | Archive | — |
| XS worktree mode | Single-story, shared lane | skip proposal | `worktree_mode: shared_lane` |
| M worktree mode | Lane-dedicated | proposal required | `worktree_mode: lane_dedicated` |
| L/XL worktree mode | Integration worktree | proposal required | `worktree_mode: integration` |

---

## 10. Governance Checklist (New Work)

Before starting any new worktree:

- [ ] Task classified: domain, scale, risk, coupling filled in
- [ ] If M/L/XL: OpenSpec proposal scaffolded and validated (`openspec validate --strict`)
- [ ] BMAD phase confirmed ≥ Phase 4 (story approved)
- [ ] Worktree created via `./scripts/worktree_governance.sh new <domain> <scale> <change-anchor>`
- [ ] Worktree path verified: `<repo>/.worktrees/<domain>/<scale>/<change-anchor>/active/`
- [ ] `openspec/changes/<change-anchor>/tasks.md` drives commit sequence
- [ ] State transitions done by renaming dir or via `worktree_governance.sh state`
- [ ] On merge: `openspec archive <change-anchor> --yes` then `git worktree prune`
