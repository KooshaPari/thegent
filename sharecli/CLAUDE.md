# CLAUDE.md - Development Guidelines for thegent-sharecli

## Project Overview

**thegent-sharecli** provides CLI tooling for thegent share/directory functionality.

- **Stack**: Go (CLI tooling)
- **Directory Structure**: `pkg/` (shared packages), `cmd/` (command entry points), `internal/` (internal packages)
- **Status**: Bootstrapping — structure may evolve as code is added

## Code Conventions

### Python Standards

- Use `pydantic` for data validation
- Use `pytest` for testing
- Follow PEP 8 style guide
- Use `ruff` for linting

### Quality Gates

Before calling `gt_done`:

```bash
python -m pytest tests/
ruff check src/
```

### File Encoding

All text files must use UTF-8 encoding.

### Git Discipline

- Feature branches follow convoy naming: `convoy/{description}/{convoy_id}/gt/{agent}/{bead_id}`
- Do not switch branches within a worktree
- Push after every commit (container disk is ephemeral)
- Never force push or hard reset to remote

## Agent Behavior Rules

### GUPP Principle

Work is on your hook — execute immediately. Do not announce what you will do; just do it.

### Pre-Submission Gates

1. `task quality` — Run all quality gates
2. If any gate fails, fix and re-run until all pass
3. Call `gt_done` only when all gates pass

### Communication

- Check mail periodically with `gt_mail_check`
- Use `gt_mail_send` for coordination with other agents
- Keep messages concise and actionable
- Call `gt_status` at meaningful phase transitions

### Crash Recovery

- Call `gt_checkpoint` after significant milestones
- Push frequently — container disk is ephemeral

### Delegation

Use `gt_sling` or `gt_sling_batch` to delegate work to other polecats in this rig or across the town.

## Kilo Gastown Integration

This rig participates in Kilo Gastown (town `78a8d430-a206-4a25-96c0-5cd9f5caf984`).

### Bead Lifecycle

1. **Open** → **In Progress**: Agent picks up bead
2. **In Progress** → **In Review**: Agent calls `gt_done`
3. **In Review** → **Merged**: Refinery merges branch
4. **In Review** → **Rework**: Reviewer requests changes; bead returns to **In Progress**

### Convoys

Convoys track groups of beads spanning multiple rigs. Use `gt_list_convoys` to track progress.

Naming: `convoy/{short-description}/{convoy_id}/head`

### Agent Identity

Polecat agents follow: `{moniker}-{species}-{rig-hash}@{town-id}`

Example: `coral-polecat-03e7d736@78a8d430`

## Commit Messages

Format: `{type}: {short description}`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Example: `docs: add CLAUDE.md methodology guide`

## Build & Test

```bash
go build ./...     # Build all packages
go test ./...      # Run tests
go vet ./...       # Lint
go fmt ./...       # Format
```

## Architecture Principles

- **Modular Go** — Clear package separation
- **CLI Best Practices** — Use established CLI framework
- **PoLA** — Principle of Least Astonishment in error handling

## Phenotype Org Rules

- UTF-8 encoding only in all text files
- Worktree discipline: canonical repo stays on `main`
- CI completeness: fix all CI failures before merging
- Never commit agent directories (`.gemini/`, `.claude/`, `.codex/`, `.cursor/`)
