# Governance

**Purpose:** The canonical multi-agent orchestration runtime — the core dispatch/agent framework for the Phenotype portfolio.

## AgilePlus Integration

All work MUST be tracked in AgilePlus:
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`
- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- Create spec before implementing: `agileplus specify --title "<feature>" --description "<desc>"`
- Update work package status: `agileplus status <feature-id> --wp <wp-id> --state <state>`

## Branch Discipline

- `main` — integration baseline, always clean
- Feature branches in worktrees under `.claude/worktrees/` (per-project subdirs: `<project>/<category>/<branch>`)
- Canonical repo tracks `main` only
- Return to main for merge/integration checkpoints

## Dirty Tree Handling

Per MODE convention (referenced in project docs):
- **MODE 1**: Commit dirty trees as-is (allowed in worktrees)
- **MODE 2**: Stash dirty changes before merge
- **MODE 3**: Clean before merge (preferred for `main`)
- All worktrees may have uncommitted changes — this is intentional

## Commit Conventions

- `chore:` — maintenance, dependency updates, CI/CD
- `feat:` — new features
- `fix:` — bug fixes
- `docs:` — documentation only
- `refactor:` — code restructuring
- `test:` — adding/updating tests
- `wip:` — work-in-progress (allowed in worktrees, not on main)

## Session & Worktree Management

- Worktrees live at `.claude/worktrees/`
- 33 orphaned worktrees currently exist (no active session) — audit weekly
- No long-running agents on `main`
- Orphaned worktrees should be cleaned up after work completion or session abandonment

## Quality Gates

From repo root:
- `task quality` — Tach boundaries, Vale (Markdown), Ruff (`src/` + `tests/`), phenotype CLIProxy model-check unit tests
- `task quality:full` — same plus `ruff format --check`

## CI/CD Constraints

- GitHub Actions usage should be tracked — billing implications
- All workflows must be pinned to specific action SHAs (see `chore/pin-actions` branches)
- Security scanning: trufflehog, trivy, cargo-deny on all PRs

## Delegation Policy

- Use subagents for parallel repo audits, dependency updates, and multi-repo operations
- Keep 10+ background agents running during active consolidation sessions
- Each agent should focus on one repo or one concern

## Orphaned Worktrees (Current)

33 worktrees at `.claude/worktrees/` with no active session. See agent audit results for triage:
- **Abandoned** (clean up): Check each worktree's git status and session transcript
- **In-progress** (continue): Identify mid-task worktrees
- **Ready-to-merge** (PR): Identify worktrees with clean, complete branches

## Related Governance

- Parent governance anchor: `/Users/kooshapari/CodeProjects/Phenotype/cursor-reset-tools/GOVERNANCE.md`
- AgilePlus project: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
