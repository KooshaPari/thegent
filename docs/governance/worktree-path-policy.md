# Worktree path policy (Phenotype org)

**Goal:** One predictable layout so agents, scripts, and humans do not fork duplicate conventions (`repo-wtrees`, `.worktrees`, ad-hoc names).

## Canonical rule

- **Feature / PR / analysis work:** `repos/worktrees/<project>/<category>/<branch-or-topic>/`
  - Example: `repos/worktrees/heliosApp/fix/ci-workflow-fix`
- **Canonical clone:** `<project>/` at repo root stays on **`main`** for pull/merge only (see `AGENTS.md` / `CLAUDE.md` in hub and each repo).

## Legacy paths (read-only migration)

- `*-wtrees/`, `PROJECT-wtrees/`, `.worktrees/` at legacy locations: **do not create new work** there; migrate into `repos/worktrees/...` when touching a lane.
- Do **not** delete legacy trees without merge/finalization per worktree governance scripts.

## Category segment

Use a **category** folder (`fix/`, `feat/`, `chore/`, `upstream-pr/`, `exp/`) so parallel work sorts cleanly:

- Good: `worktrees/thegent/upstream-pr/pr-123`
- Avoid: `worktrees/thegent/pr123` with no category when multiple PR lanes exist.

## Autofix / disposable sandboxes

- Prefix or nest under `exp/` or `_archive/` after merge to avoid clutter next to canonical repos.

## Cross-reference

- Hub: `CLAUDE.md`, `AGENTS.md` (Phenotype/repos)
- ADR: `governance/adrs/0005-top-level-directory-structure.md`
