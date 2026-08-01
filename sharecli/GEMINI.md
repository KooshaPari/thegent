# GEMINI.md - Development Guidelines for thegent-sharecli

## Project Overview

thegent-sharecli provides CLI tooling for thegent share/directory functionality. This rig is being bootstrapped; explore `pkg/`, `cmd/`, and `internal/` once code is present.

## Key Files

- `pkg/` - Shared packages (TBD)
- `cmd/` - Command entry points (TBD)
- `internal/` - Internal packages (TBD)

## Development Commands

```bash
go build ./...     # Build
go test ./...      # Test
go vet ./...       # Lint
go fmt ./...       # Format
```

## Architecture Principles

- **Modular Go** - Clear package separation
- **CLI Best Practices** - Use cobra or urfave/cli for command structure
- **PoLA** - Principle of Least Astonishment in error handling

## Phenotype Org Rules

- UTF-8 encoding only in all text files
- Worktree discipline: canonical repo stays on `main`
- CI completeness: fix all CI failures before merging
- Never commit agent directories (`.gemini/`, `.claude/`, `.codex/`, `.cursor/`)

## Agent Behavior Guidelines

When working in this repository as a Gemini agent:

1. **GUPP Principle**: Work is on your hook — execute immediately
2. **Commit Frequently**: Push after every meaningful unit of work
3. **Checkpoint**: Call gt_checkpoint after significant milestones
4. **No Destructive Ops**: Never force push, hard reset, or merge to main
5. **Pre-Submission Gates**: Run `go vet` and `go test` before considering work complete

## Communication

- Check mail periodically with gt_mail_check
- Use gt_mail_send for coordination with other agents
- Keep messages concise and actionable
