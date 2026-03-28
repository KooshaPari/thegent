# Phenotype Hexagonal Architecture Library

A framework for building applications following Hexagonal Architecture (Ports & Adapters) principles.

## Overview

This library provides primitives and abstractions for implementing Hexagonal Architecture in Rust, Go, and TypeScript projects within the Phenotype ecosystem.

## Core Principles

1. **Domain Core**: Pure business logic with zero external dependencies
2. **Ports**: Interface definitions that decouple domain from infrastructure
3. **Adapters**: Implementations of ports (database, cache, external APIs)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Primary Adapters                      │
│              (REST, gRPC, CLI, UI)                     │
└─────────────────────┬─────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│                    Inbound Ports                        │
│                 (Use Case Interfaces)                  │
└─────────────────────┬─────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│                      Domain Core                       │
│     (Entities, Services, Events, Value Objects)        │
└─────────────────────┬─────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│                    Outbound Ports                      │
│            (Repository, External APIs)                  │
└─────────────────────┬─────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│                   Secondary Adapters                   │
│           (DB, Cache, External APIs)                    │
└─────────────────────────────────────────────────────────┘
```

## Modules

### Domain Layer (`src/domain/`)

- **Entities**: Domain objects with identity
- **Value Objects**: Immutable objects without identity
- **Services**: Domain operations
- **Events**: Domain events
- **Ports**: Interface definitions

### Application Layer (`src/application/`)

- **Commands**: Write operations
- **Queries**: Read operations
- **Handlers**: Port implementations

### Adapters Layer (`src/adapters/`)

- **Primary**: REST, CLI, UI
- **Secondary**: Persistence, Cache, Messaging

### Infrastructure Layer (`src/infrastructure/`)

- Configuration
- Dependency injection

## Usage

```rust
use phenotype_hexagonal::{
    domain::{Entity, Identifier},
    ports::outbound::RepositoryPort,
};

// Define an entity
#[derive(Debug)]
pub struct Order {
    id: OrderId,
    items: Vec<OrderItem>,
    status: OrderStatus,
}

impl Entity for Order {
    type Id = OrderId;
    fn id(&self) -> &Self::Id {
        &self.id
    }
}

// Use the repository port
#[async_trait]
impl RepositoryPort<Order, OrderId> for PostgresOrderRepository {
    // Implementation
}
```

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn order_calculates_total_correctly() {
        // Arrange
        let order = Order::new();
        
        // Act
        let total = order.calculate_total();
        
        // Assert
        assert_eq!(total, Money::usd(1000).unwrap());
    }
}
```

## Related

- [xDD Methodologies Encyclopedia](../docs/governance/xdd-methodologies-encyclopedia.md)
- [Rolling Hand Rules](../docs/governance/rolling-hand-rules.md)
- [Architecture Decision Tree](../docs/governance/architecture-decision-tree.md)
