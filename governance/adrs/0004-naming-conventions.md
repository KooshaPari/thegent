# ADR-004: Naming Conventions

**Date:** 2026-03-25
**Status:** Proposed
**Supersedes:** N/A

---

## Context

The Phenotype ecosystem spans multiple programming languages and has inconsistent naming conventions across repositories. This leads to:
- Confusion when switching between repos
- Difficulty understanding package boundaries
- Inconsistent patterns that hinder code sharing
- Developer friction when onboarding

This ADR establishes **universal naming conventions** that apply across all languages and repositories.

---

## Decision

### 1. Repository Naming

| Type | Convention | Examples |
|------|------------|----------|
| Phenotype-Domain (Type A) | `phenotype-{domain}` | `phenotype-config`, `phenotype-agent` |
| Extractable Library (Type B) | `{library-name}` (no prefix) | `hexagonal-rs`, `event-sourcing` |
| Infrastructure | `{type}-{purpose}` | `terraform-base`, `kubernetes-core` |
| Template | `template-{lang}-{pattern}` | `template-hexagonal-go` |

**Rules:**
- Use kebab-case for repository names
- Avoid generic names like `utils`, `common`, `core`
- Be specific: `retry-policy` not `retry`

### 2. Package/Crate/Module Naming

#### Rust (Crates)

| Type | Convention | Example |
|------|------------|---------|
| Workspace | `phenotype-{domain}` | `phenotype-config` |
| Library crate | `{module-name}` | `http-adapter` |
| Binary crate | `{app-name}` | `phenotype-cli` |
| Internal crate | `{context}-{module}` | `auth-jwt`, `db-postgres` |

**Rules:**
- Use kebab-case for crate names
- Use snake_case for module names
- Use PascalCase for types and traits
- Use SCREAMING_SNAKE_CASE for constants

```rust
// Crate: hexagonal-rs
// Module: hexagonal

pub mod ports;           // snake_case
pub mod domain;         // snake_case

pub struct FooBar { }   // PascalCase
pub trait FooService { } // PascalCase
const MAX_RETRIES: u32 = 3; // SCREAMING_SNAKE_CASE
```

#### TypeScript/Node.js (Packages)

| Type | Convention | Example |
|------|------------|---------|
| Public library | `@lib/{name}` | `@lib/hexagonal-ts` |
| Phenotype package | `@phenotype/{name}` | `@phenotype/config` |
| Internal package | `{scope}/{name}` | `@internal/utils` |
| Application | `{name}` (no scope) | `phenotype-web` |

**Rules:**
- Use kebab-case for file names: `my-component.tsx`
- Use PascalCase for React components: `MyComponent.tsx`
- Use camelCase for functions/variables: `getUserById`
- Use UPPER_CASE for constants: `MAX_RETRY_COUNT`

```typescript
// File: user-repository.ts
// Type: UserRepository (PascalCase)

export class UserRepository { } // PascalCase
export interface IUserService { } // I prefix for interfaces (optional)
export const MAX_RETRY_COUNT = 3; // UPPER_CASE for constants
export function getUserById(id: string) { } // camelCase for functions
```

#### Python

| Type | Convention | Example |
|------|------------|---------|
| Package | `snake_case` | `phenotype_config` |
| Module | `snake_case` | `user_repository` |
| Class | `PascalCase` | `UserRepository` |
| Function | `snake_case` | `get_user_by_id` |
| Constant | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Variable | `snake_case` | `user_id` |

```python
# Package: phenotype_config
# Module: user_repository

class UserRepository:  # PascalCase
    MAX_RETRY_COUNT = 3  # SCREAMING_SNAKE_CASE (class level)

    def get_user_by_id(self, user_id: str) -> User:  # snake_case
        pass
```

#### Go

| Type | Convention | Example |
|------|------------|---------|
| Module | `github.com/org/{name}` | `github.com/phenotype/hexagonal-go` |
| Package | `snake_case` | `user_repository` |
| Type/Interface | `PascalCase` | `UserRepository` |
| Function | `PascalCase` (exported), `camelCase` (unexported) | `GetUserById`, `doInternal` |
| Variable | `camelCase` (exported), `camelCase` (unexported) | `maxRetries` |
| Constant | `PascalCase` (exported), `camelCase` (unexported) | `MaxRetries` |

```go
// Package: user_repository
// Module: github.com/phenotype/user-service

type UserRepository interface { } // PascalCase
type userService struct { }       // unexported - camelCase

func GetUserByID(id string) (*User, error) { } // PascalCase for exported
func getUserByID(id string) (*User, error) { } // camelCase for unexported

const MaxRetries = 3 // PascalCase for exported constants
```

### 3. Domain Naming

#### Entities

| Language | Convention | Example |
|----------|------------|---------|
| Rust | `PascalCase` | `User`, `OrderItem` |
| TypeScript | `PascalCase` | `User`, `OrderItem` |
| Python | `PascalCase` | `User`, `OrderItem` |
| Go | `PascalCase` | `User`, `OrderItem` |

#### Value Objects

| Language | Convention | Example |
|----------|------------|---------|
| Rust | `PascalCase` (newtype pattern) | `Email(String)` |
| TypeScript | `PascalCase` | `Email`, `Money` |
| Python | `PascalCase` | `Email`, `Money` |
| Go | `PascalCase` | `Email`, `Money` |

#### Domain Events

| Language | Convention | Pattern |
|----------|------------|---------|
| Rust | `PascalCase` + past tense | `UserCreated`, `OrderShipped` |
| TypeScript | `PascalCase` + Event suffix | `UserCreatedEvent` |
| Python | `PascalCase` + Event suffix | `UserCreatedEvent` |
| Go | `PascalCase` + Event suffix | `UserCreatedEvent` |

#### Commands and Queries (CQRS)

| Language | Convention | Example |
|----------|------------|---------|
| Rust | `PascalCase` + Command/Query | `CreateUserCommand`, `GetUserQuery` |
| TypeScript | PascalCase + Command/Query | `CreateUserCommand`, `GetUserQuery` |
| Python | `PascalCase` + Command/Query | `CreateUserCommand`, `GetUserQuery` |
| Go | `PascalCase` + Cmd/Qry suffix | `CreateUserCmd`, `GetUserQry` |

### 4. File Naming

| Language | Source Files | Test Files | Config Files |
|----------|--------------|------------|--------------|
| Rust | `snake_case.rs` | `snake_case`.rs | `Cargo.toml` |
| TypeScript | `kebab-case.ts` | `kebab-case.test.ts` | `tsconfig.json` |
| Python | `snake_case.py` | `test_snake_case.py` | `pyproject.toml` |
| Go | `snake_case.go` | `snake_case_test.go` | `go.mod` |

**Special conventions:**
- React components: `PascalCase.tsx`
- Zod schemas: `schema.ts`
- GraphQL: `schema.graphql`
- SQL migrations: `YYYYMMDDHHMMSS_description.sql`

### 5. Database Naming

| Type | Convention | Example |
|------|------------|---------|
| Table | `snake_case`, plural | `user_accounts` |
| Column | `snake_case` | `created_at` |
| Index | `idx_{table}_{columns}` | `idx_users_email` |
| Foreign Key | `fk_{table}_{ref_table}` | `fk_orders_users` |
| Unique Constraint | `uq_{table}_{columns}` | `uq_users_email` |

### 6. API Naming

| Element | Convention | Example |
|---------|------------|---------|
| Endpoint | `kebab-case` | `/user-accounts` |
| HTTP Method | uppercase | `GET`, `POST`, `PUT`, `DELETE` |
| Query Parameter | `camelCase` | `?pageSize=10&sortBy=createdAt` |
| Request Body | `camelCase` | `{"userId": "123"}` |
| Response Body | `camelCase` | `{"data": {...}}` |

---

## Consequences

### Positive

1. **Consistency** - Developers know what to expect
2. **Discoverability** - Patterns are predictable
3. **Tooling** - Linters and formatters can enforce conventions
4. **Cross-language understanding** - Similar patterns in all languages

### Negative

1. **Migration effort** - Existing code needs renaming
2. **Different conventions** - Each language has its own idioms; we may conflict
3. **Learning curve** - Team members need to learn the conventions

### Neutral

1. **Not all conventions are universal** - Some are language-specific by necessity
2. **Tools may not support all conventions** - May need custom linting rules

---

## Alternatives Considered

### Alternative 1: Per-Language Idioms Only

**Pros:**
- Native to each language
- No friction with language tools

**Cons:**
- Inconsistency across the ecosystem
- Harder to move code between languages
- Confusing for developers working in multiple languages

**Why not chosen:** Goes against the goal of cross-language consistency.

### Alternative 2: Strict Universal Naming

**Pros:**
- Maximum consistency
- Easy to find patterns

**Cons:**
- May conflict with language idioms (e.g., Go uses PascalCase for exported)
- May require significant linter configuration

**Why not chosen:** Need to respect language idioms while maintaining cross-language consistency.

---

## Enforcement

### Linting Rules

| Language | Tool | Configuration |
|----------|------|---------------|
| Rust | `clippy` + custom rules | `.clippy.toml` |
| TypeScript | `eslint` + `typescript-eslint` | `.eslintrc.json` |
| Python | `pylint` + `flake8` | `pyproject.toml` |
| Go | `golangci-lint` | `.golangci.yml` |

### Pre-commit Hooks

All repos SHOULD include pre-commit hooks for:
- Linting
- Formatting (rustfmt, prettier, black, gofmt)
- Type checking
- Basic tests

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- [ADR-002: Package Classification Framework](./0002-package-classification-framework.md)
- [Rust Naming Conventions](https://rust-lang.github.io/api-guidelines/naming.html)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Effective Go](https://go.dev/doc/effective_go)

---

## Notes

- This ADR should be reviewed annually for language convention updates
- Language-specific exceptions may be documented in per-language standards
- Naming decisions should consider searchability (avoid very short names)

---

*Created: 2026-03-25*
*Maintained by: Architecture Guild*
