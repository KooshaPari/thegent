# {{project_name}} - Quick Start Guide

Get started with {{project_name}} in minutes. This guide covers setup, basic workflow, and quality gates.

## Prerequisites

{% if language == "python" -%}
- Python 3.14+ (via `uv`)
- `uv` package manager

{% elif language == "typescript" -%}
- Node.js 18+
- `pnpm` package manager

{% elif language == "go" -%}
- Go 1.22+
- `go` toolchain

{% else -%}
- Bash 4.0+

{% endif -%}

## Installation

### 1. Clone and Install Dependencies

{% if language == "python" -%}
```bash
git clone <repository-url>
cd {{project_name}}
uv sync
```

### 2. Run Development Server

```bash
uv run python -m {{project_name}}
```

### 3. Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov={{project_name}}

# Specific test file
uv run pytest tests/test_core.py
```

{% elif language == "typescript" -%}
```bash
git clone <repository-url>
cd {{project_name}}
pnpm install
```

### 2. Run Development Server

```bash
pnpm dev
```

### 3. Run Tests

```bash
# All tests
pnpm test

# Watch mode
pnpm test:watch

# Coverage
pnpm test:coverage
```

{% elif language == "go" -%}
```bash
git clone <repository-url>
cd {{project_name}}
go mod download
```

### 2. Run Development Server

```bash
go run main.go
```

### 3. Run Tests

```bash
# All tests
go test ./...

# Verbose
go test -v ./...

# Coverage
go test -cover ./...
```

{% else -%}
```bash
git clone <repository-url>
cd {{project_name}}
# No dependencies for bash projects
```

### 2. Run

```bash
./main.sh
```

### 3. Run Tests

```bash
./tests/run.sh
```

{% endif -%}

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Edit source files in `src/` (or project structure)
- Follow [CLAUDE.md](../../CLAUDE.md) guidelines
- Reference the [PLAN.md](../../PLAN.md) for project architecture

### 3. Run Quality Gates (Before Commit)

```bash
task quality
```

This runs:
- Linting
- Type checking
- Tests
- Coverage validation
- Code complexity checks

### 4. Commit and Push

```bash
git add .
git commit -m "feat: description of change"
git push origin feature/my-feature
```

## Quality Gates

All code must pass these checks before merging:

| Gate | Command | Notes |
|------|---------|-------|
| Lint | `task lint` | Enforced style and best practices |
| Type Check | `task typecheck` | Static type validation |
| Test | `task test` | Unit and integration tests (70%+ coverage) |
| Coverage | `task coverage` | Minimum coverage thresholds |
| Complexity | `task complexity` | Max function complexity: 15 |
| Security | `task security` | SAST, dependency scanning |

## Project Structure

```
{{project_name}}/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
│   ├── guides/            # Implementation guides (this file)
│   ├── reference/         # Quick references, trackers
│   ├── research/          # Research summaries, analysis
│   ├── reports/           # Completion reports
│   ├── changes/           # Change documentation
│   └── governance/        # Governance and policy
├── CLAUDE.md              # Governance and instructions
├── PLAN.md                # Project plan and phasing
├── PRD.md                 # Product requirements
└── Taskfile.yml           # Task automation
```

## Common Commands

{% if language == "python" -%}
```bash
# Format code
uv run ruff format src/

# Check formatting
uv run ruff check src/

# Type check
uv run mypy src/

# Run specific test
uv run pytest tests/test_core.py::test_something

# Debug mode
uv run pytest -vv --pdb
```

{% elif language == "typescript" -%}
```bash
# Format code
pnpm format

# Lint
pnpm lint

# Type check
pnpm typecheck

# Run specific test
pnpm test -- test_something

# Debug mode
pnpm test:debug
```

{% elif language == "go" -%}
```bash
# Format code
go fmt ./...

# Lint
golangci-lint run

# Vet
go vet ./...

# Run specific test
go test -run TestSomething ./...

# Benchmark
go test -bench=. ./...
```

{% else -%}
```bash
# Lint
shellcheck *.sh

# Format
shfmt -i 2 -w *.sh
```

{% endif -%}

## Documentation

- [Architecture Decisions](../reference/ADR.md) - Design decisions and rationale
- [Work Stream](../reference/WORK_STREAM.md) - Active tasks and FR tracking
- [Governance](../../CLAUDE.md) - Rules, guidelines, and policies
- [Project Plan](../../PLAN.md) - Phased WBS with dependencies

## Getting Help

- Check [FAQ section in PLAN.md](../../PLAN.md#faq)
- Review existing issues and discussions
- Consult [CLAUDE.md](../../CLAUDE.md) for governance questions
- Run `task help` for available Taskfile commands

## Next Steps

1. Read [PLAN.md](../../PLAN.md) for project roadmap
2. Check the [Work Stream](../reference/WORK_STREAM.md) for current priorities
3. Start with a small task from the `TODO` section
4. Submit your first PR with a descriptive commit message
