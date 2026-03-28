# Global Agent Contract

This file defines global rules for all AI agents (Claude, Gemini, Cursor, etc.) across all projects.

## Safety and Delivery Policy

### Non-Destructive Operations
- NEVER run `git reset --hard` without explicit user instruction.
- NEVER run `git push --force` to main/master.
- NEVER delete files; prefer `.archive/` over removal.
- Prefer branch + PR + merge over direct commits to default branch.

### Git Discipline
- Always create NEW commits rather than amending, unless explicitly asked.
- Stage specific files by name — never `git add -A` or `git add .` without review.
- Separate commits by provenance (user work / pre-existing WIP / generated artifacts).

### Billing Constraints
- GitHub Actions CI will NOT run on KooshaPari account — billing exhausted.
- Do NOT wait for CI checks, do NOT treat CI failures as blocking bugs.
- Verify quality locally instead.

## Delegation Policy

- Use child agents as default for: file exploration (>3 files), pattern searches, multi-file implementation, long command sequences, test execution.
- Parent agent direct edits: synthesis, integration, finalization ONLY.
- Parallel subagents for independent work; sequential only when dependent.

## Quality Governance

- Zero new lint suppressions without inline justification.
- Test-first mandate: tests BEFORE implementation.
- All test functions MUST reference a FR ID.
- Quality gate runs on every Stop event.

## AgilePlus Integration

All work tracked in AgilePlus. Reference: `agileplus <command>`.
No code without corresponding AgilePlus spec.

## Worktree Commandments

- Canonical folders (main) are read/write only for integration.
- All feature work in worktrees: `repos/<repo>-wtrees/<topic>/...`
- Never author feature work directly in canonical repos.

## Communication Style

- No emojis in file content (except when explicitly requested).
- Absolute file paths in all responses (never relative).
- Clear, concise descriptions — no filler text.
