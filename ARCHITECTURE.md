# Architecture Overview

## System Architecture

This document describes the high-level architecture of the Phenotype ecosystem.

## Overview

Phenotype is built on hexagonal (ports and adapters) architecture principles, with a clear separation between:

1. **Domain Core** - Pure business logic, no external dependencies
2. **Application Layer** - Use cases and orchestration
3. **Ports** - Interfaces defining how the domain interacts with the outside world
4. **Adapters** - Infrastructure implementations

## Hexagonal Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Adapters (Driving)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │   CLI   │  │   API   │  │   Web   │  │  Tests  │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
└───────┼────────────┼────────────┼────────────┼────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Ports (Inbound)                         │
│                     Use Cases / Commands                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Core                              │
│              Entities │ Value Objects │ Events               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Ports (Outbound)                         │
│           Repository │ EventPublisher │ External API         │
└────┬────────────┬────────────┬────────────┬─────────────────┘
     │            │            │            │
     ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Adapters (Driven)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Postgres│  │   Redis │  │   HTTP  │  │  Files  │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
repos/
├── libs/                  # Extracted hexagonal libraries
│   │                       # Type B: Extractable/marketable
│   ├── cipher/           # Cryptographic utilities (Rust)
│   ├── tracing/          # Distributed tracing (Rust)
│   ├── logger/           # Structured logging (Rust)
│   ├── metrics/          # Metrics registry (Rust)
│   ├── nexus/            # State management (Rust)
│   ├── gauge/            # Benchmarking + xDD (Rust)
│   ├── clikit/           # CLI toolkit (Go)
│   ├── auth-ts/          # Authentication (TypeScript)
│   ├── config-ts/        # Configuration (TypeScript)
│   ├── evaluation/       # Evaluation framework (Python)
│   ├── logging-zig/      # Logging (Zig)
│   ├── hexagonal-rs/     # Rust hexagonal patterns
│   ├── hexagonal-ts/      # TypeScript hexagonal patterns
│   ├── hexagonal-py/      # Python hexagonal patterns
│   ├── hexagonal-go/     # Go hexagonal patterns
│   └── xdd-lib-rs/       # xDD utilities (Rust)
├── tools/                # Developer tooling
│   │                       # Type C: CLI tools
│   ├── forge/            # Code generation CLI (Rust)
│   ├── dep-guard/        # Dependency guard (Python)
│   ├── ci-cd/            # CI/CD configurations
│   └── devcontainers/    # Dev container definitions
├── packages/              # Phenotype-domain packages
│   │                       # Type A: Domain-specific
├── services/              # Microservices
│   │                       # Type D: Services
├── apps/                  # End-user applications
├── infrastructure/        # Deployment & IaC
├── governance/            # ADRs, standards, processes
└── plans/                # Planning documents
```

## Layer Descriptions

### Domain Core (`src/domain/`)

Contains:
- **Entities** - Objects with identity
- **Value Objects** - Immutable objects without identity
- **Aggregates** - Clusters of entities and value objects
- **Domain Events** - Significant business events
- **Domain Services** - Operations that don't belong to entities

Rules:
- No external dependencies
- No framework imports
- Pure business logic
- Fully tested

### Application Layer (`src/application/`)

Contains:
- **Use Cases** - Application-specific business rules
- **Commands** - Requests that modify state
- **Queries** - Requests that read state
- **Command Handlers** - Execute commands
- **Query Handlers** - Execute queries

### Ports (`src/ports/`)

**Inbound Ports (Driving)**
- Define how external actors interact with the application
- Typically use case interfaces
- Protocol-agnostic

**Outbound Ports (Driven)**
- Define how the application interacts with external systems
- Repository interfaces
- Event publisher interfaces
- External service interfaces

### Adapters (`src/adapters/`)

**Driving Adapters**
- CLI adapters
- HTTP/REST adapters
- GraphQL adapters
- WebSocket adapters
- Test adapters

**Driven Adapters**
- Database adapters (PostgreSQL, MongoDB, Redis)
- Message queue adapters
- HTTP client adapters
- File system adapters

## Package Structure

Each package follows a consistent structure:

```
package/
├── src/
│   ├── domain/           # Domain entities, value objects, events
│   ├── application/      # Use cases, command/query handlers
│   ├── ports/           # Port interfaces
│   │   ├── inbound/     # Driving port interfaces
│   │   └── outbound/    # Driven port interfaces
│   ├── adapters/        # Infrastructure implementations
│   │   ├── driving/     # CLI, API, etc.
│   │   └── driven/      # Database, HTTP, etc.
│   └── main.ts          # Entry point
├── tests/
│   ├── domain/
│   ├── application/
│   └── adapters/
├── package.json
├── tsconfig.json
└── README.md
```

## Design Principles

### SOLID Principles

| Principle | Application |
|-----------|-------------|
| **S**ingle Responsibility | Each class has one reason to change |
| **O**pen/Closed | Open for extension, closed for modification |
| **L**iskov Substitution | Subtypes can replace their base types |
| **I**nterface Segregation | Many specific interfaces over one general |
| **D**ependency Inversion | Depend on abstractions, not concretions |

### Domain-Driven Design

- **Bounded Contexts** - Clear boundaries between domains
- **Ubiquitous Language** - Shared language across team
- **Aggregates** - Consistency boundaries
- **Domain Events** - Capture significant occurrences
- **Anti-Corruption Layer** - Translate external models

### Testing Strategy

| Layer | Test Type | Focus |
|-------|-----------|-------|
| Domain | Unit | Business rules, invariants |
| Application | Unit | Use case logic |
| Ports | Integration | Interface contracts |
| Adapters | Integration | External system integration |

## Technology Stack

### Languages

| Language | Primary Use |
|----------|-------------|
| TypeScript | Frontend, Node.js services |
| Python | Research, agent core |
| Rust | Performance-critical libraries |
| Go | CLI tools, microservices |

### Frameworks & Libraries

| Category | Technologies |
|----------|-------------|
| API | Express, FastAPI, Actix-web |
| Database | PostgreSQL, Redis, MongoDB |
| Testing | Vitest, Pytest, Cargo test |
| CI/CD | GitHub Actions |

## References

- [ADR-0003: Hexagonal Architecture Standard](../governance/adrs/0003-hexagonal-architecture-standard.md)
- [xDD Methodology Compendium](../plans/xdd-methodology-compendium.md)
