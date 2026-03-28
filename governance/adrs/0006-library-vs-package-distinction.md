# ADR-006: Library vs Package Distinction

**Date:** 2026-03-25
**Status:** Proposed
**Supersedes:** N/A

---

## Context

The term "package" is overloaded in software development:
- In Rust: A crate is a package
- In JavaScript: A package is published to npm
- In Python: A package is a directory with `__init__.py`
- In Go: A package is a directory with `.go` files

This ADR clarifies the distinction between:
1. **Library**: A publishable, reusable, domain-agnostic component
2. **Package**: A Phenotype-bound component tied to the domain

This distinction directly maps to ADR-002's Type A vs Type B classification.

---

## Decision

### Definitions

#### Library (Type B)

**Definition:** A standalone, reusable component that provides value independent of the Phenotype domain.

**Characteristics:**
| Attribute | Requirement |
|----------|-------------|
| Reusability | Usable by any project, not just Phenotype |
| Domain coupling | Zero Phenotype-specific assumptions |
| Dependencies | Framework-agnostic or optional framework features |
| Documentation | Comprehensive README, API docs, examples |
| Testing | >80% code coverage required |
| Versioning | Semantic versioning (SemVer) |
| Publishing | Intended for public registries (crates.io, npm, PyPI) |
| Naming | No `phenotype-` prefix |

**Examples:**
- `hexagonal-rs` - Hexagonal architecture patterns
- `xdd-lib` - Testing utilities
- `event-sourcing` - Event sourcing patterns
- `config-lib` - Configuration loading
- `policy-engine` - Policy evaluation

#### Package (Type A)

**Definition:** A component that is bound to Phenotype's business domain and is not intended for external use.

**Characteristics:**
| Attribute | Requirement |
|----------|-------------|
| Reusability | Specific to Phenotype domain |
| Domain coupling | Contains Phenotype-specific logic |
| Dependencies | May depend on Libraries |
| Documentation | README and API docs |
| Testing | >60% code coverage |
| Versioning | Internal versioning (date-based or SemVer) |
| Publishing | Internal registry or not published |
| Naming | MUST have `phenotype-` prefix |

**Examples:**
- `phenotype-config` - Phenotype's configuration schema
- `phenotype-design` - Phenotype's design tokens
- `phenotype-auth` - Phenotype's authentication rules
- `phenotype-agent` - Phenotype's agent logic

### Dependency Rules

```
┌─────────────────────────────────────────────────────┐
│                      APP                             │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │               Package (Type A)                │   │
│  │                                               │   │
│  │   depends on: Package (Type A) ✓             │   │
│  │   depends on: Library (Type B) ✓             │   │
│  │   depends on: External ✓                     │   │
│  │                                               │   │
│  └─────────────────────────────────────────────┘   │
│                        │                            │
│                        ▼                            │
│  ┌─────────────────────────────────────────────┐   │
│  │               Library (Type B)                │   │
│  │                                               │   │
│  │   depends on: Library (Type B) ✓             │   │
│  │   depends on: External (minimal) ✓           │   │
│  │   depends on: Package (Type A) ✗             │   │
│  │                                               │   │
│  └─────────────────────────────────────────────┘   │
│                        │                            │
│                        ▼                            │
│  ┌─────────────────────────────────────────────┐   │
│  │              External Libraries               │   │
│  │                                               │   │
│  │   stdlib                                      │   │
│  │   Standard external crates/npm packages      │   │
│  │                                               │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Rules:**
1. Packages MAY depend on Packages
2. Packages MAY depend on Libraries
3. Packages MAY depend on External libraries
4. **Libraries MUST NOT depend on Packages**
5. Libraries MAY depend on Libraries
6. Libraries MAY depend on minimal External libraries

### Repository Structure

#### Library Repository

```
libs/{library-name}/
├── Cargo.toml              # or package.json, go.mod, etc.
├── README.md               # With examples
├── LICENSE
├── CHANGELOG.md
├── ADR.md
├── CLAUDE.md
├── AGENTS.md
├── src/
│   └── ...
├── tests/                  # or __tests__, test/, etc.
├── examples/               # Usage examples
└── benches/                # Benchmarks (Rust)
```

#### Package Repository

```
packages/phenotype-{domain}/
├── Cargo.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── ADR.md
├── CLAUDE.md
├── AGENTS.md
├── src/
│   └── ...
└── tests/
```

### Versioning Strategy

#### Libraries

| Version | Meaning | When to Use |
|---------|---------|-------------|
| `1.0.0` | Major | Breaking changes |
| `1.1.0` | Minor | New features, backward compatible |
| `1.1.1` | Patch | Bug fixes |

**Additional rules:**
- All releases MUST have changelog entries
- Breaking changes MUST have migration guides
- Preview versions MAY be used (`1.0.0-alpha.1`)

#### Packages

| Version | Meaning | When to Use |
|---------|---------|-------------|
| `0.1.0` | Initial | Pre-1.0 for internal use |
| `1.0.0` | Stable | Ready for production use |
| `date-based` | Snapshot | `2026.03.25.0` |

**Additional rules:**
- Internal packages MAY remain at 0.x until stable
- Date-based versioning for rapid iteration
- Semantic versioning once API is stable

### Publishing Strategy

#### Libraries

| Registry | Package | Visibility |
|----------|---------|------------|
| crates.io | `hexagonal-rs` | Public |
| npm | `@lib/hexagonal-ts` | Public |
| PyPI | `hexagonal-py` | Public |
| GitHub Packages | `@phenotype/*` | Private or Public |

**Rules:**
- Libraries MUST be tested before publishing
- Libraries MUST have >80% test coverage
- Libraries MUST have valid LICENSE
- Libraries SHOULD have CI/CD for all supported versions

#### Packages

| Registry | Package | Visibility |
|----------|---------|------------|
| GitHub Packages | `@phenotype/config` | Private |
| crates.io | NOT PUBLISHED | Internal only |
| npm | NOT PUBLISHED | Internal only |

**Rules:**
- Packages MAY be published to internal registries
- Packages MUST NOT be published to public registries without review
- Packages MUST be versioned and tagged

---

## Consequences

### Positive

1. **Clear boundaries** - Developers know what can be reused
2. **Clean architecture** - Dependency rules enforce good structure
3. **Community potential** - Libraries are designed for external use
4. **Quality gates** - Libraries have higher quality requirements

### Negative

1. **Additional overhead** - Libraries require more documentation and tests
2. **Naming discipline** - Must carefully choose what gets `phenotype-` prefix
3. **Migration effort** - Existing code needs review and potential extraction

### Neutral

1. **Classification judgment** - Some packages may be borderline
2. **Re-evaluation** - Classifications may change over time

---

## Decision Matrix

Use this matrix to decide if something should be a Library or Package:

| Question | If Yes | If No |
|----------|--------|-------|
| Is it useful outside Phenotype? | **Library** | Package |
| Does it contain Phenotype business logic? | Package | Library |
| Does it depend on Phenotype packages? | Package | Library |
| Should it be published publicly? | Library | Package |
| Does it need >80% test coverage? | Library | Package |

**If answers conflict**, default to Package (more restrictive) and extract later if needed.

---

## Examples

### Example 1: Configuration Library

**Case:** A configuration loading library that Phenotype-config uses.

**Decision:** **Library** (`config-lib`)

**Rationale:**
- Configuration loading is useful for any project
- No Phenotype-specific assumptions
- Can be published to crates.io/npm
- Independent versioning

### Example 2: Auth Logic

**Case:** Phenotype-specific authentication rules and token handling.

**Decision:** **Package** (`phenotype-auth`)

**Rationale:**
- Contains Phenotype-specific auth rules
- Depends on Phenotype's user model
- Not useful outside Phenotype context
- Should remain internal

### Example 3: HTTP Adapter

**Case:** An HTTP client wrapper with retry logic.

**Decision:** **Library** (`http-adapter`)

**Rationale:**
- Generic HTTP client wrapper
- Retry logic is applicable anywhere
- Can be published
- Minimal dependencies

### Example 4: Domain Event Schema

**Case:** Phenotype-specific event schemas for domain events.

**Decision:** **Package** (`phenotype-domain-events`)

**Rationale:**
- Contains Phenotype-specific event types
- Tied to Phenotype's domain model
- Not reusable outside Phenotype
- Should be internal

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- [ADR-002: Package Classification Framework](./0002-package-classification-framework.md)
- [ADR-003: Hexagonal Architecture Standard](./0003-hexagonal-architecture-standard.md)
- [ADR-004: Naming Conventions](./0004-naming-conventions.md)
- [ADR-005: Top-Level Directory Structure](./0005-top-level-directory-structure.md)

---

## Review Process

1. **New package creation**: Must classify before creation
2. **Reclassification**: Requires ADR if renaming involved
3. **Annual review**: Architecture Guild reviews classifications quarterly

---

*Created: 2026-03-25*
*Maintained by: Architecture Guild*
