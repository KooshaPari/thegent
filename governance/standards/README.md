# Coding Standards Index

This directory contains language-specific coding standards for the Phenotype ecosystem.

## Standards

| Language | File | Description |
|----------|------|-------------|
| Rust | [rust.md](./rust.md) | Rust conventions, clippy rules |
| Go | [go.md](./go.md) | Go conventions, golangci-lint rules |
| TypeScript | [typescript.md](./typescript.md) | TypeScript conventions, ESLint rules |
| Python | [python.md](./python.md) | Python conventions, pylint rules |

## Quick Reference

### xDD Methodology Enforcement

| Standard | xDD Method | Where Applied |
|----------|-------------|----------------|
| All code MUST have tests | TDD | See language-specific standards |
| Business logic MUST be in domain | DDD | Hexagonal architecture |
| API contracts MUST be tested | Contract Testing | See language-specific standards |
| Property-based tests for core logic | Property-based Testing | See language-specific standards |

### General Principles

1. **KISS** - Keep It Simple, Stupid
2. **DRY** - Don't Repeat Yourself
3. **YAGNI** - You Aren't Gonna Need It
4. **SOLID** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion

### Required Files

Every project MUST include:

| File | Purpose |
|------|---------|
| `README.md` | Quick start, overview |
| `CLAUDE.md` | Claude-specific instructions |
| `AGENTS.md` | Agent conventions |
| `ADR.md` | Link to ADR directory |
| `CHANGELOG.md` | Version history |
| `LICENSE` | License file |

### Quality Gates

| Gate | Requirement |
|------|-------------|
| Lint | Zero warnings |
| Type check | Zero errors |
| Test coverage (libs) | >80% |
| Test coverage (apps) | >60% |
| Mutation score | >50% |
| Docs | All public APIs documented |

## Contributing

To update standards:
1. Propose changes in an ADR
2. Get Architecture Guild approval
3. Update this directory
4. Update all affected projects

---

*Maintained by: Architecture Guild*
