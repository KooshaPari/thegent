# ADR-012: xDD Methodology Standards

**Date**: 2026-03-25
**Status**: Proposed
**Deciders**: Phenotype Team

## Context

We need to establish consistent development methodologies across all Phenotype projects to ensure:
- Quality through testing
- Maintainability through documentation
- Collaboration through shared practices

## Decision

We will adopt the following xDD methodologies as standards:

### Mandatory Practices (P0)

| Practice | Description | When Applied |
|----------|-------------|--------------|
| **TDD** | Write failing test first | All new features |
| **DDD** | Domain-driven design with bounded contexts | All domain logic |
| **ADD** | Architecture Decision Records | All architectural changes |
| **ADR** | Architecture Decision Records | All significant decisions |
| **SPEC-DD** | Specification-driven development | Complex features |
| **BDD** | Behavior-driven development with Gherkin | User-facing features |

### Recommended Practices (P1)

| Practice | Description | When Applied |
|----------|-------------|--------------|
| **Contract Testing** | Pact/Contract tests for APIs | Microservices |
| **Property-Based Testing** | Randomized input testing | Complex algorithms |
| **ATDD** | Acceptance test-driven development | Integration features |
| **CDD** | Contract-driven development | API-first design |

### Implementation Requirements

#### 1. TDD Cycle
```
1. Write a failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor (BLUE)
4. Repeat
```

#### 2. Test Coverage Requirements

| Layer | Minimum Coverage |
|-------|------------------|
| Domain | 90% |
| Application | 80% |
| Adapters | 60% |

#### 3. Documentation Standards

- All public APIs require doc comments
- Complex logic requires inline comments
- Architecture decisions require ADRs
- User-facing features require BDD scenarios

### Tooling Requirements

| Language | Test Framework | Coverage | Linting |
|----------|---------------|----------|---------|
| Rust | `#[test]` + `cargo test` | `cargo tarpaulin` | `clippy` + `rustfmt` |
| Go | `testing` + `testify` | `go cover` | `golangci-lint` |
| TypeScript | `jest` | `nyc` | `eslint` + `prettier` |
| Python | `pytest` | `pytest-cov` | `ruff` + `mypy` |

## Consequences

### Positive
- Consistent quality standards
- Clear testing expectations
- Better collaboration
- Reduced bugs in production

### Negative
- Learning curve for team
- Initial slowdown in velocity
- Tooling maintenance overhead
