# Agents

## Key Commands

```bash
# Development
task install    # Install dependencies
task lint       # Lint all source
task test       # Run test suite
task quality    # Full quality gate (lint + test + type check)
task dev        # Start development server with hot reload
task dev:tui    # Start services with interactive TUI dashboard
```

## Stack

- **Core**: Python (src/thegent/)
- **CLI**: Typer, Rich
- **Agent Integration**: BlackBoxProxy, Agent Discovery & Registration
- **Dotfiles**: Managed via `src/thegent/dotfiles/`

## Conventions

- Max function length: 40 lines. Cognitive complexity ≤ 15.
- No placeholder TODOs in committed code.
- All new code must pass: `ruff check .`, `ruff format .`, `pytest -q`.
- AGENTS.md symlink removed — file is now repo-native.

## Do Not Touch

- `apps/byteport/backend/api/.archive/thegent-test-deduplication/**` — Go work in progress, not ported
- `apps/byteport/**/auth_handlers*.go` — security refactor in flight
- `apps/byteport/**/*_test.go` in any .archive/ subdir
