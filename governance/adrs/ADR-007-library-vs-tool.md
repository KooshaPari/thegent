# ADR-007: Library vs Tool Distinction

> **Status**: Accepted  
> **Date**: 2026-03-26  
> **Deciders**: Platform Team  

## Context

We maintain multiple types of packages: libraries (publishable to crates.io/npm), tools (CLI binaries), and documentation hubs. This ADR defines clear criteria for distinguishing between them.

## Decision

We will use three distinct hierarchies:

### 1. `helix-*` — Publishable Libraries

Market-neutral packages with no Phenotype-specific dependencies.

**Criteria**:
- No Phenotype-specific imports or integrations
- Could exist independently as a general-purpose library
- Useful to the broader Rust/Go/TypeScript ecosystem

**Examples**:
- `helix-logging` — Structured logging (no Phenotype deps)
- `helix-tracing` — Distributed tracing (no Phenotype deps)
- `helix-crypto` — Cryptography primitives (no Phenotype deps)

**Rule**: If a package has zero Phenotype imports and could be published to crates.io/npm today, use `helix-`.

### 2. `phenotype-*` — Product-Bound Packages

Packages tightly coupled to Phenotype-specific systems.

**Criteria**:
- Depends on other Phenotype packages
- Contains Phenotype-specific integrations
- Not useful outside the Phenotype ecosystem

**Examples**:
- `phenotype-cli-core` — CLI foundation (Go deps on Phenotype infra)
- `phenotype-config` — Config system (Phenotype-specific)
- `phenotype-task-engine` — Task/orchestration (Phenotype-specific)

**Rule**: If a package imports or depends on another Phenotype package, use `phenotype-`.

### 3. `phenotype-<hub>` — Documentation/Reference Hubs

Documentation hubs and skills repositories.

**Criteria**:
- Primarily Markdown/documentation content
- No buildable code, or code is example/reference only
- Serves as a knowledge base

**Examples**:
- `phenotype-xdd` — x-DD methodology compendium
- `phenotype-forge` — CLI tool runner (standalone binary)
- `phenotype-skills-clone` — Skills catalog

**Rule**: If the repo is primarily documentation or the binary is the product itself, use `phenotype-`.

## Library Extraction Process

To extract a `phenotype-*` package as `helix-*`:

1. Remove all Phenotype-specific imports
2. Create new GitHub repo under `helix-*` naming
3. Publish to crates.io/npm
4. Update `phenotype-*` to depend on `helix-*`
5. Add ARCHIVED.md redirect notice

## Consequences

### Positive

- Clear distinction between product and market-neutral packages
- Easier ecosystem contribution (helix-* can be forked)
- Consistent naming across 28+ repositories

### Negative

- Existing packages need migration
- Two naming schemes to maintain

## References

- [Naming Conventions](../standards/NAMING.md)
- [Package Inventory](../standards/PACKAGE_INVENTORY.md)
- [Phase 6 Productization Plan](../../plans/2026-03-26-phenotype-phase6-productization-plan.md)
