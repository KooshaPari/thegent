# Global Agent Instructions

These rules apply to ALL agents across ALL projects unless a project-level AGENTS.md overrides them.

---

## Core Principles

### Autonomy
Agents MUST operate with **maximum autonomy**. Pause only for:
- Missing credentials/secrets that cannot be inferred
- External service access permissions
- Genuine product ambiguity (behavior not determinable from specs/code/tests)
- Destructive operations (production data deletion, forced pushes)

Default behavior: **Research -> Decide -> Implement -> Validate -> Continue**

### Research-First Development
Before implementing ANY feature or fix, agents MUST conduct comprehensive research:
1. Search codebase for similar patterns with ripgrep/glob
2. Trace call chains to understand full impact
3. Check existing abstractions before inventing new ones
4. Document findings before implementing

### Forward-Only Progression
- NO `git revert` or `git reset` (fix forward instead)
- NO haphazard delete-and-rewrite cycles
- NO backwards compatibility shims for legacy patterns
- Push forward to clean, working states via incremental fixes

---

## Delegation Policy

- Use child agents as the default for high-context, multi-file, or parallelizable work.
- Delegate exploration, audits, and long-running analysis to subagents before the parent agent edits.
- Keep parent-agent direct edits narrowly scoped to synthesis, integration, and finalization.
- Reserve parent-agent direct writes for the narrowest, final decision layer.

### Delegation Quick Reference

| Need | Delegate To |
|------|-------------|
| File exploration (>3 files) | subagent with `Explore` prompt |
| Pattern searches across codebase | subagent with `Grep` prompt |
| Multi-file implementations | `general-purpose` subagent |
| Long command sequences | `Bash` subagent |
| Design approach | `Plan` subagent |
| Quick isolated fix | Handle directly |

### Async Swarm Pattern
If swarm capabilities are available:
- Fire tasks async so each completion reawakens the parent
- Run up to 50 concurrent task agents for independent work
- Use your own context for planning/monitoring while tasks run

---

## Git and Delivery Protocol

### Branch Discipline
- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only
- Return to `main` for merge/integration checkpoints
- Prefer stacked PRs for multi-part changes

### Dirty-Tree Commit Discipline
In dirty worktrees, separate commits by provenance:
- `MODE 1`: user-requested implementation changes
- `MODE 2`: pre-existing work and WIP from other actors
- `MODE 3`: generated or temporary artifacts

Never mix modes in one commit.

### Safety Rules
- NEVER run destructive git commands (push --force, reset --hard, checkout ., restore ., clean -f) unless explicitly requested
- NEVER skip hooks (--no-verify) unless explicitly requested
- NEVER force push to main/master without user confirmation
- Create NEW commits rather than amending, unless explicitly requested

---

## Code Quality Standards

### File Size Limits
- Max module size: 500 lines (hard limit), 350 lines (target)
- When approaching 350+ lines, decompose immediately

### No Code Without Tests
- Write tests BEFORE implementation (TDD mandate)
- For bug fixes: write failing test first, then fix
- All test functions MUST reference an FR ID

### Suppression Policy
- **Zero new suppressions** without inline justification
- Format: `# noqa: E501 -- line is a long URL`
- Suppression requires: specific rule, concrete reason, tracking reference

---

## Documentation Rules

### Naming Conventions
- NO `FINAL`, `COMPLETE`, `V2`, `_NEW`, `_OLD`, `_DRAFT` suffixes
- NO temporal markers in filenames
- Use canonical names describing the concern, not the phase

### Organization
- Session docs: `docs/sessions/<YYYYMMDD-name>/`
- Canonical docs: `docs/` root (README, ARCHITECTURE, API_REFERENCE)
- Never create floating `.md` files outside these structures

---

## CI and Billing Policy

**CRITICAL**: GitHub Actions billing is a hard constraint for KooshaPari account.
- Jobs fail immediately with billing error -- do NOT treat as code bug
- Do NOT wait for CI checks to pass
- Verify quality locally: build, lint, test
- Proceed with merge if local checks pass and billing failures are the only CI failures

---

## Phenotype Workspace Rules

### Canonical vs Worktree
- Canonical repos (`repos/<project>/`) are READ for main-branch verification only
- All feature work uses worktrees: `repos/worktrees/<project>/<topic>/`
- Canonical folders should always be on `main`

### Service Management
- Never start/stop the entire dev stack (user manages their TUI)
- Use per-service CLI manipulation only
- Assume services use hot reload -- do not restart services after file saves

### Decision Frameworks (consult before architectural changes)
- Architectural Modernization: `thegent/docs/governance/23_ARCHITECTURAL_GOVERNANCE.md`
- Language/Framework selection: `docs/engineering/language_governance_framework.md`
- Project decomposition: `docs/governance/project_decomposition_governance.md`
- Plugin architecture: `docs/governance/plugin_architecture_governance.md`
