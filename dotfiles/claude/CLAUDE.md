# Global Claude Code Instructions

These rules apply to ALL projects. Project-level CLAUDE.md files supplement (and may override) these.

## Child-Agent and Delegation Policy

- Use child agents as the default for high-context, multi-file, or parallelizable work.
- Delegate exploration, audits, and long-running analysis to subagents before the parent agent edits.
- Keep parent-agent direct edits narrowly scoped to synthesis, integration, and finalization.

## Dependency & Technology Preferences (ENFORCED)

**Bleeding-edge first**: Always prefer the newest stable versions of libraries, frameworks, and tools.
- Use latest major versions, not LTS unless explicitly required
- Prefer cutting-edge CSS/JS/UI tools over mature but stagnant ones
- Flag any dep that is >1 major version behind latest

**Wrap/Fork/Integrate over Hand-Roll**:
- Before writing any utility, search for an existing OSS library that does it
- Prefer wrapping a well-maintained OSS package over reimplementing
- Document the wrapped library in comments: `// wraps: <lib-name> <version>`

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- CLI: `agileplus <command>`
- Check for spec before implementing
- Create spec for new work: `agileplus specify --title "<feature>" --description "<desc>"`

## Branch Discipline

- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only

## GitHub Actions Billing

- GitHub Actions CI will NOT run — billing is exhausted.
- Do NOT wait for CI checks. Verify quality locally (build, lint, test).
- Use `gh pr merge --admin` if branch protection blocks merge.

## Worktree Rules

- Canonical repos: read/write for `main` and verification only.
- Feature work MUST use worktrees: `repos/<repo>-wtrees/<topic>/...`
- `git status --short --branch` should show `main` in canonical folders.

## Quality Enforcement

- Enforce opinionated styling to a strict degree.
- Never bypass linters (no `# noqa` without justification comment).
- Use project linters, formatters, and type checkers.
- Write tests BEFORE implementation (TDD mandate).

## Documentation Organization

- Root-level: README.md, CHANGELOG.md, AGENTS.md, CLAUDE.md, PRD.md, ADR.md only.
- All other docs → `docs/` subdirectories (guides/, reports/, research/, reference/).

## Optionality and Failure Behavior

- Fail clearly, not silently. Explicit failures, not reduced functionality.
- If a service or config is required for correctness, treat it as required.

## Planner Agents: No Code in Docs

- Planner agents must NEVER write code in documentation or plans.
- Write specs, acceptance criteria, architecture decisions, and clear handoffs.
