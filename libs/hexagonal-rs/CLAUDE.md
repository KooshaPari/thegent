# Hexagonal Architecture Library (hexagonal-rs)

## Overview

A comprehensive Rust library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles, SOLID compliance, and domain-driven design.

> **Note**: This library has pre-existing compilation errors that need to be fixed before release. See [ISSUES.md](./ISSUES.md) for details.

## Architecture

```
Adapters → Ports → Domain
                  ↓
              Application
```

### Layers

1. **Domain** - Pure business logic, no external dependencies
2. **Ports** - Abstract interfaces (input/output)
3. **Application** - Use cases and orchestration
4. **Adapters** - Infrastructure implementations

## Adding to a Project

```toml
# Cargo.toml
[dependencies]
hexagonal_rs = { git = "https://github.com/phenotype/libs", package = "hexagonal_rs" }
```

Or from crates.io (when published):
```toml
hexagonal_rs = "0.2"
```

## Key Traits

- `Entity` - Objects with identity
- `ValueObject` - Immutable objects without identity
- `AggregateRoot` - Cluster of related entities
- `DomainEvent` - Significant business occurrences
- `InputPort` - Commands/queries from outside
- `OutputPort` - Calls to external systems

## Development

```bash
# Build
cargo build

# Test
cargo test

# Lint
cargo clippy

# Format
cargo fmt
```

## Standards

This library follows the Phenotype coding standards:
- [Solid Principles](https://github.com/phenotype/libs/hexagonal-rs/blob/main/standards/solid.md)
- [Hexagonal Architecture ADR](https://github.com/phenotype/libs/hexagonal-rs/blob/main/governance/adrs/hexagonal-architecture.md)
