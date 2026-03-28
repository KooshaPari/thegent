# Hexkit - Hexagonal Architecture Toolkit for Rust

![Rust](https://img.shields.io/badge/rust-1.75+-orange.svg)
[![Crates.io](https://img.shields.io/crates/v/hexkit)](https://crates.io/crates/hexkit)
[![Documentation](https://img.shields.io/docsrs/hexkit)](https://docs.rs/hexkit)
[![License](https://img.shields.io/crates/l/hexkit)](LICENSE)

> **Ports & Adapters made simple.** A comprehensive Rust library for building applications following Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Overview

Hexkit provides a comprehensive foundation for building Rust applications following Hexagonal Architecture principles. It offers type-safe abstractions for:

- **Domain Layer**: Pure business logic with entities, value objects, aggregates, and domain events
- **Ports Layer**: Abstract interfaces for input (commands/queries) and output (repositories, services)
- **Application Layer**: Use cases, DTOs, and handlers
- **Adapters Layer**: Concrete implementations (REST, persistence, messaging)

## Quick Start

```rust
use hexkit::domain::*;
use hexkit::ports::*;
use hexkit::adapters::*;

// Define your domain entity
#[derive(Debug, Clone, PartialEq)]
struct OrderId(String);

impl EntityId for OrderId {}
impl std::fmt::Display for OrderId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, Entity)]
struct Order {
    #[entity_id]
    id: OrderId,
    customer_id: String,
    total: f64,
}

impl Order {
    fn new(customer_id: String) -> Self {
        Self {
            id: OrderId(uuid::Uuid::new_v4().to_string()),
            customer_id,
            total: 0.0,
        }
    }
}

// Define repository port (output)
#[async_trait::async_trait]
trait OrderRepository: OutputPort {
    async fn save(&self, order: Order) -> HexResult<()>;
    async fn find_by_id(&self, id: &OrderId) -> HexResult<Option<Order>>;
}

// Use in-memory adapter for testing
#[tokio::main]
async fn main() {
    let repo = InMemoryRepository::<Order>::new();

    let order = Order::new("customer-123".to_string());
    repo.save(order.clone()).await.unwrap();

    let found = repo.find_by_id(order.id()).await.unwrap();
    println!("Found: {:?}", found);
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ADAPTERS LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   REST     │  │  GraphQL   │  │  Messaging  │              │
│  │   Adapter  │  │   Adapter  │  │   Adapter   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          PORTS LAYER                            │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │   INPUT PORTS       │  │        OUTPUT PORTS             │  │
│  │   (Commands/Queries)│  │   (Repositories, Services)      │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Use Cases │  │    DTOs    │  │   Mappers   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Entities  │  │Value Objects│  │ Aggregates  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │   Events   │  │  Services   │                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **Domain Primitives** | Entity, ValueObject, AggregateRoot, DomainEvent |
| **Port Traits** | InputPort, OutputPort, CommandHandler, QueryHandler |
| **Adapters** | In-memory repository, REST adapter, Event bus |
| **CQRS Support** | Command/Query separation |
| **Event Sourcing** | Event bus and domain events |
| **Async Ready** | First-class async/await support |
| **Feature Gates** | Pay only for what you use |

## Feature Flags

```toml
[dependencies]
hexkit = { version = "1.0", features = ["full"] }

# Or selectively
hexkit = { version = "1.0", features = ["serde", "uuid", "chrono"] }
```

| Flag | Description | Default |
|------|-------------|---------|
| `std` | Standard library support | ✓ |
| `serde` | Serialization support | ✗ |
| `uuid` | UUID identifier support | ✗ |
| `chrono` | Date/time support | ✗ |
| `metrics` | Metrics collection | ✗ |
| `tracing` | Distributed tracing | ✗ |
| `validation` | Input validation | ✗ |
| `full` | All features | ✗ |

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
hexkit = "1.0"
```

## Examples

### Basic Domain Entity

```rust
use hexkit::domain::*;
use hexkit::Entity;

#[derive(Debug, Clone, PartialEq)]
struct UserId(String);

impl EntityId for UserId {}
impl std::fmt::Display for UserId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, Entity)]
struct User {
    #[entity_id]
    id: UserId,
    email: String,
}
```

### Repository Pattern

```rust
use hexkit::ports::*;
use hexkit::adapters::*;

#[async_trait]
trait UserRepository: OutputPort {
    async fn save(&self, user: User) -> HexResult<()>;
    async fn find_by_email(&self, email: &str) -> HexResult<Option<User>>;
}

let repo = InMemoryRepository::<User>::new();
```

### Command Handler (CQRS)

```rust
use hexkit::ports::*;
use async_trait::async_trait;

#[derive(Debug, Clone)]
struct CreateUserCommand {
    email: String,
}

#[async_trait]
impl CommandHandler<CreateUserCommand> for CreateUserHandler {
    type Output = User;

    async fn handle(&self, cmd: CreateUserCommand) -> HexResult<User> {
        let user = User::new(cmd.email)?;
        self.repository.save(user.clone()).await?;
        Ok(user)
    }
}
```

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use hexkit::adapters::*;

    #[tokio::test]
    async fn test_order_repository() {
        let repo = InMemoryRepository::<Order>::new();
        let order = Order::new("customer-1".to_string());

        repo.save(order.clone()).await.unwrap();
        assert_eq!(repo.len().await, 1);

        let found = repo.find_by_id(order.id()).await.unwrap();
        assert_eq!(found, Some(order));
    }
}
```

## Design Principles

Hexkit enforces these design principles:

1. **Single Responsibility**: Each module has one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes can replace their base types
4. **Interface Segregation**: Small, focused interfaces
5. **Dependency Inversion**: Depend on abstractions, not concretions

## Related Crates

| Crate | Description |
|-------|-------------|
| `xdtest` | xDD testing utilities (TDD, BDD, Property-based) |
| `clikit` | CLI application framework |
| `midframe` | Python middleware patterns |

## License

Licensed under either of:
- Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE))
- MIT license ([LICENSE-MIT](LICENSE-MIT))

at your option.
