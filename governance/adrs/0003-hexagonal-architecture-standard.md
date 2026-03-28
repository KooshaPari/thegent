# ADR-003: Hexagonal Architecture Standard

**Date:** 2026-03-25
**Status:** Proposed
**Supersedes:** N/A

---

## Context

The Phenotype ecosystem uses multiple programming languages (Rust, TypeScript, Python, Go, Zig) and needs a consistent architectural pattern for organizing domain logic. Currently, hexagonal architecture patterns exist in multiple repos (`phenotype-hexagonal`, `phenotype-ts-hexagonal`, `phenotype-py-hexagonal`, `phenotype-go-hexagonal`) but they may not follow a consistent structure.

This ADR establishes a **universal hexagonal architecture standard** that:
1. Provides consistent patterns across all languages
2. Defines clear layer boundaries
3. Establishes naming conventions
4. Enables better code sharing between language implementations

---

## Decision

We adopt a **universal hexagonal architecture** with the following principles:

### Universal Layer Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                         APPLICATION                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    DOMAIN CORE                           │    │
│  │                                                          │    │
│  │   ENTITIES ──── VALUE OBJECTS ──── DOMAIN SERVICES     │    │
│  │        │                │                  │            │    │
│  │        └────────────────┼──────────────────┘            │    │
│  │                         │                               │    │
│  │                    AGGREGATES                           │    │
│  │                         │                               │    │
│  │                    DOMAIN EVENTS                        │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ══════════════════════════════════════════════════════════════  │
│                         PORTS                                      │
│  ══════════════════════════════════════════════════════════════  │
│                                                                   │
│   INPUT PORTS              │              OUTPUT PORTS           │
│  (Driving/Primary)         │           (Driven/Secondary)         │
│                                                                   │
│  ┌──────────────────┐      │      ┌──────────────────────────┐  │
│  │ Use Case         │◄─────┼──────│ Repository Interface    │  │
│  │ Commands         │      │      │ Event Publisher          │  │
│  │ Queries          │      │      │ External Service Client  │  │
│  └──────────────────┘      │      └──────────────────────────┘  │
│                                                                   │
│  ══════════════════════════════════════════════════════════════  │
│                        ADAPTERS                                   │
│  ══════════════════════════════════════════════════════════════  │
│                                                                   │
│   PRIMARY (Driving)       │           SECONDARY (Driven)         │
│                                                                   │
│  ┌──────────────────┐      │      ┌──────────────────────────┐  │
│  │ HTTP Controller  │      │      │ Postgres Repository     │  │
│  │ GraphQL Resolver │      │      │ Redis Cache             │  │
│  │ CLI Command      │      │      │ HTTP Client             │  │
│  │ Message Handler  │      │      │ Event Publisher (Kafka) │  │
│  └──────────────────┘      │      └──────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Domain Core
- **Entities**: Domain objects with identity, mutable state
- **Value Objects**: Immutable, self-validating domain concepts
- **Domain Services**: Complex business rules requiring multiple entities
- **Aggregates**: Consistency boundaries, root entity + related objects
- **Domain Events**: Immutable records of things that happened

**Rules:**
- Domain layer MUST NOT depend on any other layer
- Domain layer MUST NOT have external dependencies (frameworks, databases)
- Domain layer MUST contain all business rules
- Domain objects MUST be serializable

#### Ports (Interfaces)
- **Input Ports (Driving)**: Use cases exposed to the outside
- **Output Ports (Driven)**: Interfaces for external dependencies

**Rules:**
- Ports MUST be defined in the domain layer (as interfaces/traits)
- Ports MUST be implemented by adapters
- Ports MUST be technology-agnostic

#### Adapters
- **Primary (Driving)**: Handle incoming requests (controllers, handlers)
- **Secondary (Driven)**: Handle outgoing requests (repositories, clients)

**Rules:**
- Adapters MUST depend on domain (not vice versa)
- Adapters MAY depend on external libraries/frameworks
- One adapter MUST implement exactly one port

### Directory Structure

#### Rust

```
src/
├── domain/                    # Domain layer (zero external deps)
│   ├── mod.rs
│   ├── entities/
│   │   ├── mod.rs
│   │   └── {entity}.rs
│   ├── value_objects/
│   │   ├── mod.rs
│   │   └── {value_object}.rs
│   ├── services/
│   │   ├── mod.rs
│   │   └── {service}.rs
│   ├── aggregates/
│   │   ├── mod.rs
│   │   └── {aggregate}.rs
│   ├── events/
│   │   ├── mod.rs
│   │   └── {event}.rs
│   └── errors.rs
│
├── ports/                     # Port interfaces (in domain crate)
│   ├── mod.rs
│   ├── input/
│   │   ├── mod.rs
│   │   ├── {use_case}.rs     # Trait definitions
│   │   └── commands.rs
│   │   └── queries.rs
│   └── output/
│       ├── mod.rs
│       ├── {repository}.rs   # Trait definitions
│       └── {publisher}.rs
│
├── adapters/                  # Adapter implementations
│   ├── mod.rs
│   ├── primary/
│   │   ├── mod.rs
│   │   ├── http/
│   │   └── cli/
│   └── secondary/
│       ├── mod.rs
│       ├── postgres/
│       ├── redis/
│       └── http/
│
└── lib.rs
```

#### TypeScript

```
src/
├── domain/
│   ├── entities/
│   ├── value-objects/
│   ├── services/
│   ├── aggregates/
│   ├── events/
│   └── errors.ts
│
├── ports/
│   ├── input/
│   │   ├── use-cases.ts
│   │   ├── commands.ts
│   │   └── queries.ts
│   └── output/
│       ├── repositories.ts
│       └── publishers.ts
│
└── adapters/
    ├── primary/
    │   ├── http/
    │   └── cli/
    └── secondary/
        ├── postgres/
        ├── redis/
        └── http/
```

### Naming Conventions

| Concept | Rust | TypeScript | Python | Go |
|---------|------|------------|--------|-----|
| Input Port Trait | `CreateFooPort` | `CreateFooUseCase` | `CreateFooUseCase` | `FooCreator` |
| Output Port Trait | `FooRepository` | `IFooRepository` | `FooRepository` | `FooRepository` |
| Primary Adapter | `FooController` | `FooController` | `FooController` | `FooHandler` |
| Secondary Adapter | `PostgresFooRepo` | `PostgresFooRepository` | `PostgresFooRepo` | `PostgresFooRepo` |
| Domain Event | `FooCreated` | `FooCreatedEvent` | `FooCreated` | `FooCreatedEvent` |
| Command | `CreateFooCommand` | `CreateFooCommand` | `CreateFooCommand` | `CreateFooCmd` |
| Query | `GetFooQuery` | `GetFooQuery` | `GetFooQuery` | `GetFooQuery` |

### Dependency Rules

```
Domain ──► Ports ──► Adapters
  │         │            │
  │         │            ▼
  │         │      External Dependencies
  │         │      (DB, HTTP, etc.)
  │
  └─► (No dependencies)
```

1. **Domain MUST NOT depend on anything**
2. **Ports MAY depend on Domain**
3. **Adapters MUST depend on Ports (and thus Domain)**

### Testing Strategy

Following **TDD** and **BDD** principles:

| Layer | Test Type | Mock Strategy |
|-------|-----------|---------------|
| Domain | Unit Tests | No mocks - pure domain logic |
| Ports | Unit Tests | Mock adapters |
| Adapters | Integration Tests | Real external services (or test containers) |

**Property-based testing** (via proptest/QuickCheck/Hypothesis):
- Domain entities with generated inputs
- Command validation
- State machine transitions

---

## Consequences

### Positive

1. **Consistency** - Same structure across all languages
2. **Testability** - Clear dependencies make mocking easy
3. **Flexibility** - Swap adapters without touching domain
4. **Reusability** - Domain logic is portable between projects
5. **Onboarding** - Developers familiar with the pattern can work in any language

### Negative

1. **Complexity** - More structure than a simple CRUD app
2. **Learning curve** - Developers unfamiliar with hexagonal need training
3. **Overhead** - Small features require touching multiple files

### Neutral

1. **Not suitable for all projects** - Microservices with simple logic may not need full hexagonal
2. **Multiple implementations** - Keeping patterns in sync across languages requires effort

---

## Alternatives Considered

### Alternative 1: Layered Architecture

**Pros:**
- Simpler than hexagonal
- Well-understood by most developers

**Cons:**
- Tends to become anemic domain
- Business logic leaks into application layer
- Harder to test in isolation

**Why not chosen:** Hexagonal provides better separation and testability for domain-rich applications.

### Alternative 2: No Standard (Per-Project Choice)

**Pros:**
- Maximum flexibility
- No enforced patterns

**Cons:**
- Inconsistency across repos
- Harder to share patterns
- New developers confused by different approaches

**Why not chosen:** Goes against the goal of consistency across the ecosystem.

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- [ADR-002: Package Classification Framework](./0002-package-classification-framework.md)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design (Eric Evans)](https://domainlanguage.com/ddd/)

---

## Implementation

### Libraries to Create/Update

| Language | Library | Location |
|----------|---------|----------|
| Rust | `hexagonal-rs` | `libs/hexagonal-rs` |
| TypeScript | `hexagonal-ts` | `libs/hexagonal-ts` |
| Python | `hexagonal-py` | `libs/hexagonal-py` |
| Go | `hexagonal-go` | `libs/hexagonal-go` |

Each library should:
1. Implement the universal pattern described in this ADR
2. Provide code generation templates (via CLI)
3. Include comprehensive examples
4. Have >80% test coverage

---

*Created: 2026-03-25*
*Maintained by: Architecture Guild*
