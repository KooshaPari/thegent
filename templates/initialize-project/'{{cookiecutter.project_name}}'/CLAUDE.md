# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

---

## Development Philosophy

### Extend, Never Duplicate
- NEVER create a v2 file. Refactor the original.
- NEVER create a new class if an existing one can be made generic.
- NEVER create custom implementations when an OSS library exists.
- Before writing ANY new code: search the codebase for existing patterns.

### Primitives First
- Build generic building blocks before application logic.
- A provider interface + registry is better than N isolated classes.
- Template strings > hardcoded messages. Config-driven > code-driven.

### Research Before Implementing
- Check project deps (pyproject.toml, package.json, go.mod) for existing libraries.
- Search PyPI/npm before writing custom code.
- For non-trivial algorithms: check GitHub for 80%+ implementations to fork/adapt.

---

## Library Preferences (DO NOT REINVENT)

| Need | Use | NOT |
|------|-----|-----|
| Retry/resilience | tenacity | Custom retry loops |
| HTTP client | httpx | Custom wrappers |
| Logging | structlog | print() or logging.getLogger |
| Config | pydantic-settings | Manual env parsing |
| CLI | typer | argparse |
| Validation | pydantic | Manual if/else |
{% if cookiecutter.language == "python" -%}
| Rate limiting | tenacity + asyncio.Semaphore | Custom rate limiter class |
{% elif cookiecutter.language == "typescript" -%}
| Rate limiting | Bottleneck | Custom rate limiter class |
{% endif -%}

---

## Code Quality Non-Negotiables

- Zero new lint suppressions without inline justification
- All new code must pass: ruff check, type checker, tests
- Max function: 40 lines. Max cognitive complexity: 15.
- No placeholder TODOs in committed code

---

## Quick Start

```bash
# Install dependencies
{% if cookiecutter.language == "python" -%}
uv sync
{% elif cookiecutter.language == "typescript" -%}
pnpm install
{% elif cookiecutter.language == "go" -%}
go mod download
{% endif -%}

# Run tests
task test

# Run linting
task lint

# Build docs (if enabled)
{% if cookiecutter.include_docs -%}
task docs:build
{% endif -%}
```

---

## Project Structure

```
{{cookiecutter.project_name}}/
├── src/                    # Source code
├── tests/                  # Test files
{% if cookiecutter.include_docs -%}
├── docs/                   # Documentation
│   └── .vitepress/        # VitePress docsite
{% endif -%}
├── hooks/                  # Pre-commit hooks
├── Taskfile.yml            # Build automation
├── CLAUDE.md               # This file
{% if cookiecutter.include_ci -%}
└── .github/workflows/     # CI workflows
{% endif -%}
```
