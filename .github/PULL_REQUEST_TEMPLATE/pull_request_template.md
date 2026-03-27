## Summary

<!-- What does this PR do? One paragraph summary -->

## Type of Change

- [ ] **feat** - New feature
- [ ] **fix** - Bug fix
- [ ] **refactor** - Code refactoring (no functional change)
- [ ] **docs** - Documentation only
- [ ] **test** - Adding/updating tests
- [ ] **chore** - Maintenance, deps, tooling
- [ ] **arch** - Architecture change

## Architecture (if applicable)

This PR follows [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/):

- [ ] **Domain Layer** - Pure business logic, zero external dependencies
- [ ] **Ports** - Interface definitions added/updated
- [ ] **Adapters** - Infrastructure implementations
- [ ] **Application Layer** - Use case orchestration

## x-DD Practices Applied

<!-- Check all that apply -->

| Practice | Applied |
|----------|---------|
| **SOLID** (Single Responsibility, O/C/L/I/D) | [ ]
| **DRY** (Don't Repeat Yourself) | [ ]
| **KISS** (Keep It Simple) | [ ]
| **YAGNI** (You Aren't Gonna Need It) | [ ]
| **GRASP** (Controller, Creator, etc.) | [ ]
| **TDD** (Test-Driven Development) | [ ]
| **BDD** (Behavior-Driven Development) | [ ]
| **CQRS** (Command Query Separation) | [ ]
| **Event Sourcing** | [ ]

## Changes

<!-- List the changes made -->

### Files Changed
```
<!-- List files -->
```

### New Files
```
<!-- List new files -->
```

### Deleted Files
```
<!-- List deleted files -->
```

## Testing

- [ ] **Unit tests** added/updated for domain logic
- [ ] **Integration tests** added/updated for adapters
- [ ] **E2E tests** added/updated (if applicable)
- [ ] All existing tests pass
- [ ] Test coverage maintained or improved

## Quality Checklist

- [ ] Code follows project style guidelines
- [ ] No linting errors
- [ ] Type safety maintained (types/typescripts)
- [ ] No hardcoded secrets or credentials
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Backward compatibility maintained (or documented breaking change)

## Observability

- [ ] **Structured logging** added (JSON format)
- [ ] **Metrics** added for key operations
- [ ] **Health endpoints** updated (if applicable)
- [ ] **Distributed tracing** context propagation (if applicable)

## Documentation

- [ ] README updated (if applicable)
- [ ] API documentation updated
- [ ] Architecture Decision Record (ADR) created
- [ ] Inline comments added for complex logic

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes documented (describe below)

<!-- If breaking changes exist, describe them -->

## Related Issues

<!-- Link to issues: Closes #123, Fixes #456 -->

## Additional Context

<!-- Any other context reviewers should know -->

---

**Reviewer Checklist:**
- [ ] Architecture follows hexagonal/clean architecture principles
- [ ] Domain layer has zero external dependencies
- [ ] Ports (interfaces) are properly defined
- [ ] Tests are meaningful and not just for coverage
- [ ] Error handling follows PoLA (Principle of Least Astonishment)
- [ ] Code is simple, readable, and maintainable
