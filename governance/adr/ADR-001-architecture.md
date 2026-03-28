# ADR-001: Architecture Decision - Hexagonal CLI Core

## Status
Accepted

## Context
Building a Go CLI core library following hexagonal architecture principles for maximum testability and extensibility.

## Decision
We will use hexagonal (ports & adapters) architecture with:

- **Domain Layer**: Pure business logic with no external dependencies
- **Port Interfaces**: Abstract interfaces for all external dependencies (ABC in Python equivalent for Go: interfaces)
- **Adapters**: Concrete implementations for CLI frameworks (cobra), config (viper), etc.
- **Application Layer**: Use cases that orchestrate domain logic via ports

## Consequences
### Positive
- Domain logic is fully testable without external dependencies
- Easy to swap adapters (e.g., viper → standard JSON decoding)
- Clear separation of concerns

### Negative
- More abstraction layers to navigate
- Interface definitions add boilerplate

## xDD Methodologies Applied
- TDD: Tests drive interface design
- BDD: Scenario-based acceptance tests
- DDD: Domain model with entities and value objects
- CDD: Contract tests verify adapter compliance
- SOLID: Interface segregation, dependency inversion
