# AGENTS.md

> Agent and AI assistant guidance for this repository

## Purpose

This file provides guidance for AI assistants (Claude Code, Codex, etc.) working in this repository.

## Development Workflow

### Local Development

```bash
# Install dependencies
just install

# Run tests
just test

# Run with live reload
just dev

# Run pre-push checks (REQUIRED before pushing)
just prepush-ci
```

### Pre-Push Requirements

**ALL pre-push checks MUST pass before pushing:**

1. **Local quality gate** (`just prepush-ci`):
   - Format check (ruff, black, prettier)
   - Lint check (ruff, mypy, eslint)
   - Type check (mypy, tsc --noEmit)
   - Unit tests (pytest, jest)
   - Security scan (bandit, safety)

2. **Git hook installation**:
   ```bash
   just install-hooks
   ```

## Architecture

### Hexagonal / Ports & Adapters

This repository follows hexagonal architecture:

```
src/
├── domain/           # Core business logic (no external dependencies)
│   ├── entities/    # Domain entities
│   ├── services/    # Domain services
│   └── value_objects/ # Value objects
├── ports/           # Interface definitions
│   ├── inbound/     # Driving adapters (API, CLI)
│   └── outbound/    # Driven adapters (DB, cache, external)
├── application/      # Use cases and orchestration
│   ├── commands/   # Write operations
│   └── queries/    # Read operations
└── adapters/        # Interface implementations
    ├── inbound/     # API, CLI adapters
    └── outbound/   # DB, cache, external service adapters
```

### Dependency Rule

- **Domain** has NO dependencies on external libraries
- **Ports** depend only on Domain
- **Application** depends on Domain and Ports
- **Adapters** depend on Domain and Ports (injected)

## Code Quality Standards

### SOLID Principles

- **S**ingle Responsibility: One reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable
- **I**nterface Segregation: Many specific interfaces over one general
- **D**ependency Inversion: Depend on abstractions

### xDD Methodologies

Use the appropriate methodology:

| Methodology | Use Case |
|------------|----------|
| **TDD** | Core business logic, domain services |
| **BDD** | User-facing features, acceptance criteria |
| **DDD** | Complex domain, bounded contexts |
| **SDD** | Algorithm-heavy code, data processing |
| **ADD** | Architectural decisions, system design |

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E  │  ← Few, slow, high confidence
        ├─────────┤
        │Integrtn │  ← Some, medium speed
        ├─────────┤
        │  Unit  │  ← Many, fast, isolated
        └─────────┘
```

### Test Naming

```python
# Pattern: test_<unit>_<scenario>_<expected>
def test_order_service_cancel_pending_order_raises_error():
    ...

def test_payment_processor_charge_valid_card_succeeds():
    ...
```

## Security

### Never Do

- ❌ Commit secrets, tokens, keys
- ❌ Hardcode credentials
- ❌ Skip validation for "simplicity"
- ❌ Commit to main directly (always PR)

### Always Do

- ✅ Use environment variables for secrets
- ✅ Validate all inputs
- ✅ Use established crypto libraries
- ✅ Review before committing large changes

## CI/CD

### Merge Requirements

All of these MUST pass:

1. ✅ CI pipeline (Ubuntu only - no macOS/Windows billed runners)
2. ✅ Code review approval
3. ✅ Pre-push checks locally
4. ✅ No billing-related CI failures blocking (expected on this account)

### Local Pre-Push Gate

The local pre-push gate is the **source of truth** for code quality.

GitHub Actions CI provides validation and telemetry, but the local gate determines merge readiness.

## Help

For questions about this repository:
- See `docs/` for architecture and process documentation
- See `ADR/` for architectural decision records
- Check `plans/` for active work items
