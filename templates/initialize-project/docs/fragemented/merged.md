# Merged Fragmented Markdown

## Source: /Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/templates/initialize-project/docs
## Source: governance/POLYGLOT_RUNTIME_DECISION_MATRIX.md

# Polyglot Runtime Decision Matrix

This template doc is the project-level baseline for runtime/testing and conversion decisions.

## Runtime Matrix

| Language | Primary | Secondary | Fallback | Required Gates |
|---|---|---|---|---|
| Python | CPython 3.14 (`uv`) | PyPy 3.11 | CPython 3.13 | tests + lint + type checks on primary lane |
| Rust | stable | nightly (optional) | n/a | `fmt --check`, `clippy -D warnings`, `test` |
| Go | latest supported | prior minor | n/a | `go test ./...`, `go vet ./...` |
| Zig | pinned stable | preview | n/a | `zig test` |
| Mojo | pinned version | n/a | Python/Rust parity lane | parity + integration checks |

## Conversion Decision Matrix

| Situation | Action |
|---|---|
| SLOs meet target + good velocity | Keep stack |
| Hot-path performance issue | Refactor/optimize in place |
| Repeated SLO misses after optimization | Convert critical module |
| Ecosystem/library blockers | Convert to stack with required library support |

## Required Pre-Conversion Checklist

1. Baseline performance and reliability metrics.
2. API/behavior parity tests.
3. Phased cutover plan with rollback.
4. Governance and `CLAUDE.md` updates.

## Frontmatter and Backmatter

1. Frontmatter required in governance/spec docs: `title`, `date`, `status`, `owner`, `tags`.
2. Backmatter required: decisions, validation commands, residual risks, next review date.

## CLAUDE File Normalization

1. Canonical file is `CLAUDE.md`.
2. Merge typo files like `calude.md` into canonical `CLAUDE.md`.
3. If `CLAUDE.md` grows beyond ~20k tokens, split details into `docs/docsets/claude/` and keep canonical file as index.

---

## Source: guides/quick-start.md

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

---

## Source: index.md

# {{project_name}}

{{project_description}}

## Getting Started

```bash
# Install dependencies
{% if language == "python" -%}
uv sync
{% elif language == "typescript" -%}
pnpm install
{% elif language == "go" -%}
go mod download
{% endif -%}

# Run development server
{% if language == "python" -%}
uv run python -m app
{% elif language == "typescript" -%}
pnpm dev
{% elif language == "go" -%}
go run main.go
{% endif -%}
```

## Documentation

- [API Reference](./api/)
- [Guides](./guides/)
- [Governance Matrix](./governance/POLYGLOT_RUNTIME_DECISION_MATRIX.md)
- [Changelog](../CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## Source: reference/WORK_STREAM.md

# {{project_name}} - Active Work Stream

Canonical work stream for {{project_name}}. All active tasks claim a row before starting; mark COMPLETED when done.

**Last Updated:** [DATE]

## Active Tasks

| Task ID | Description | Status | Owner | Notes |
|---------|-------------|--------|-------|-------|
| WS-001  | [Task description] | CLAIMED | [Name] | [Progress notes] |
| WS-002  | [Task description] | TODO   | Unassigned | [Requirements] |

## Functional Requirements Tracking

| FR ID | Category | Description | Test Status | Docs |
|-------|----------|-------------|------------|------|
| FR-CORE-001 | [Category] | [Requirement description] | PENDING | [Link] |

## Open Questions

- Question 1: [Details and context]
- Question 2: [Details and context]

## Completed

| Task ID | Description | Completed | Owner | Delivery |
|---------|-------------|-----------|-------|----------|
| WS-001-DONE | [Task description] | [Date] | [Name] | [Link to PR/release] |

## Related Documentation

- Architecture Decisions: [Link to ADR.md]
- PRD: [Link to PRD.md]
- Plan: [Link to PLAN.md]
- Governance: [Link to CLAUDE.md]

---
