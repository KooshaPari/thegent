# Engineering Quick Reference Card

> **For all Phenotype/DinoForge repos** | Last Updated: 2026-03-25

## Core Principles (CRUST)

| Mnemonic | Full Form | Meaning |
|---------|----------|---------|
| **C** | **C**orrectness | Code does what it should |
| **R** | **R**eadability | Clear, expressive code |
| **U** | **U**tility | Solves real problem |
| **S** | **S**implicity | Minimal complexity |
| **T** | **T**estability | Easy to verify |

## Design Principles (SOLID)

| Letter | Principle | One-Liner |
|--------|-----------|-----------|
| **S** | Single Responsibility | One reason to change |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes must be substitutable |
| **I** | Interface Segregation | Many small interfaces |
| **D** | Dependency Inversion | Depend on abstractions |

## Other Essential Principles

| Short | Full Form |
|-------|-----------|
| KISS | Keep It Simple, Stupid |
| DRY | Don't Repeat Yourself |
| YAGNI | You Aren't Gonna Need It |
| POLA | Principle of Least Astonishment |
| SOC | Separation of Concerns |
| WET | Write Everything Twice (avoid) |
| AAA | Arrange, Act, Assert |

## Architecture Patterns (HEXAGONAL)

```
┌─────────────────────────────────────────────────────────┐
│                    Primary Adapters                      │
│  ┌─────────────────────────────────────────────┐      │
│  │              Ports (Inbound)                 │      │
│  └──────────────────┬──────────────────────────┘      │
│                     │                                │
│  ┌─────────────────▼──────────────────────────┐      │
│  │              Application Layer              │      │
│  │         (Use Cases / Services)            │      │
│  └─────────────────┬──────────────────────────┘      │
│                     │                                │
│  ┌─────────────────▼──────────────────────────┐      │
│  │               Domain Layer                │      │
│  │    (Entities, Value Objects, Events)     │      │
│  └─────────────────┬──────────────────────────┘      │
│                     │                                │
│  ┌─────────────────▼──────────────────────────┐      │
│  │              Ports (Outbound)              │      │
│  └─────────────────────────────────────────────┘      │
│                    Secondary Adapters                   │
└─────────────────────────────────────────────────────────┘
```

## Test-Driven Development Cycle

```
    ┌─────────┐
    │  RED    │  Write failing test
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  GREEN  │  Write minimal code
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ REFACTOR│  Improve code
    └────┬────┘
         │
         └────────► (repeat)
```

## Testing Quadrants

```
                    ┌─────────────────┐
                    │   E2E / UAT     │
                    │   (User tests)   │
     ┌──────────────┴─────────────────┴──────────────┐
     │                                             │
  Business                                      Technology
  Tests                                        Tests
     │                                             │
     ├──────────────────┬─────────────────────────┤
     │                  │                         │
     │  ┌───────────────▼───────────────┐        │
     │  │        BDD / Examples         │        │
     │  │      (Specification)          │        │
     │  └───────────────┬───────────────┘        │
     │                  │                         │
     │  ┌───────────────▼───────────────┐        │
     │  │      Unit / Component        │        │
     │  │        (Isolation)           │        │
     │  └─────────────────────────────┘        │
     └─────────────────────────────────────────┘
```

## Quality Gates

| Gate | Tool | Threshold |
|------|------|-----------|
| Lint | `golangci-lint`, `clippy` | 0 errors |
| Types | `go vet`, `mypy` | 0 errors |
| Tests | `go test`, `cargo test` | >80% coverage |
| Security | `trivy`, `snyk` | 0 critical/high |
| Complexity | `gocyclo` | <15 per function |

## Git Workflow (Trunk-Based)

```bash
# Feature branch
git checkout -b feature/my-feature main
git commit -m "feat: add my feature"
git push origin feature/my-feature

# After PR merged
git checkout main
git pull origin main
git branch -d feature/my-feature
```

## API Design Checklist

- [ ] RESTful naming (nouns, not verbs)
- [ ] Proper HTTP methods (GET/POST/PUT/DELETE)
- [ ] Pagination for lists
- [ ] Standardized errors (RFC 7807)
- [ ] Versioning strategy
- [ ] OpenAPI/Swagger docs

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Go files | snake_case | `user_repository.go` |
| Rust files | snake_case | `user_repository.rs` |
| TypeScript files | camelCase | `userService.ts` |
| Python files | snake_case | `user_repository.py` |
| Packages | singular | `domain/user/` |
| Collections | plural | `users []User` |

## Common Code Smells

| Smell | Quick Fix |
|-------|-----------|
| Long Method | Extract function |
| Large Class | Extract class |
| Magic Numbers | Named constant |
| Deep Nesting | Early return |
| Duplicate Code | Extract to function |

## Security Checklist

- [ ] Input validation
- [ ] Output encoding
- [ ] Parameterized queries
- [ ] HTTPS only
- [ ] Secure headers
- [ ] Secrets in env vars

## Logging Levels

| Level | Use When |
|-------|----------|
| DEBUG | Detailed debugging info |
| INFO | Normal operation |
| WARN | Recoverable issues |
| ERROR | Failed operations |

## Metric Names (Four Golden Signals)

| Signal | Metric Type | Example |
|--------|-------------|---------|
| Latency | Histogram | `request_duration_seconds` |
| Traffic | Counter | `requests_total` |
| Errors | Counter | `error_requests_total` |
| Saturation | Gauge | `cpu_usage_percent` |

## Quick Command Reference

```bash
# Run tests
go test ./... -cover
cargo test --coverage

# Lint
golangci-lint run
cargo clippy

# Format
gofmt -w .
cargo fmt

# Security scan
trivy fs .
snyk test
```

---

## Related engineering docs (Phenotype / DinoForge)

| Document | Purpose |
|----------|---------|
| [100-PRACTICES.md](./100-PRACTICES.md) | 180+ numbered practices, patterns, and xDD-style disciplines |
| [WRAP_AND_ROLL_GOVERNANCE.md](./WRAP_AND_ROLL_GOVERNANCE.md) | Merge vs rollback, stash policy, CI billing alignment, audit prompts |
| [TOP_LEVEL_REPO_LAYOUT.md](./TOP_LEVEL_REPO_LAYOUT.md) | Root directory hygiene, hexagonal folders, polyrepo extraction |
| [PACKAGE_REPO_NAMING_TAXONOMY.md](./PACKAGE_REPO_NAMING_TAXONOMY.md) | When to use `phenotype-*` vs neutral productized repo/crate names |
| [../research/PHENOTYPE_PREFIX_REPO_INVENTORY_2026-03-25.md](../research/PHENOTYPE_PREFIX_REPO_INVENTORY_2026-03-25.md) | Tier A/B inventory of every `phenotype-*` clone under `repos/` |
| [../changes/phenotype-prefix-migration/proposal.md](../changes/phenotype-prefix-migration/proposal.md) | Rename waves + ADR pointers for neutral crate/repo names |
| [../changes/phenotype-prefix-migration/GITHUB_RENAME_RUNBOOK.md](../changes/phenotype-prefix-migration/GITHUB_RENAME_RUNBOOK.md) | Checklist for GitHub repo rename, remotes, CI, registries |
| [../plans/xdd-hexagonal-reference-architecture.md](../../plans/xdd-hexagonal-reference-architecture.md) | Reference architecture plan, roll rules, phased delivery |

---

*Print this card and keep it handy!*
