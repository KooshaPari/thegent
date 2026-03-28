# Hexagonal Architecture Library

A comprehensive Rust library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Adapters Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   REST API │  │    gRPC    │  │   CLI       │              │
│  │   Adapter  │  │   Adapter  │  │   Adapter   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Ports Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Input Port  │  │ Output Port │  │  Domain     │              │
│  │ (Commands)  │  │ (Queries)   │  │  Events     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Entities   │  │ Value Objs  │  │   Domain    │              │
│  │             │  │             │  │   Services  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Aggregates  │  │  Events    │  │ Repository  │              │
│  │             │  │             │  │   Traits    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Use Cases │  │   DTOs     │  │  Handlers  │              │
│  │  (Services)│  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. Dependency Rule
- Dependencies point inward only
- Domain has zero external dependencies
- Adapters depend on ports, not domain

### 2. Single Responsibility
- Each module has one reason to change
- Ports define contracts
- Adapters implement contracts

### 3. Interface Segregation
- Small, focused ports
- No fat interfaces
- Role-based ports

### 4. Pure Domain
- No framework dependencies
- No database calls
- No external I/O

## Usage

```rust
use hexagonal_rs::{
    domain::{Entity, ValueObject, Aggregate},
    ports::{InputPort, OutputPort},
    application::UseCase,
};

// Define your domain
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OrderId(String);

impl ValueObject for OrderId {}

pub struct Order {
    id: OrderId,
    items: Vec<OrderItem>,
    status: OrderStatus,
}

impl Entity for Order {
    type Id = OrderId;
}

// Define ports
pub trait OrderRepository: Send + Sync {
    fn save(&self, order: Order) -> Result<(), Error>;
    fn find_by_id(&self, id: &OrderId) -> Result<Option<Order>, Error>;
}

// Use cases
pub struct CreateOrderUseCase<R: OrderRepository> {
    repository: Arc<R>,
}

impl<R: OrderRepository> UseCase for CreateOrderUseCase<R> {
    type Input = CreateOrderCommand;
    type Output = OrderResult;
    
    fn execute(&self, input: Self::Input) -> Result<Self::Output, UseCaseError> {
        // Business logic here
    }
}
```

## Modules

- `domain` - Core business logic (entities, value objects, aggregates, events)
- `ports` - Interface definitions (input, output, domain events)
- `application` - Use cases and application services
- `adapters` - Infrastructure implementations (REST, gRPC, CLI, persistence)

## Testing

```bash
cargo test
cargo test --doc
cargo clippy
cargo fmt --check
```

## License

MIT
