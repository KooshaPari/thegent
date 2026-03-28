# Phenotype Go Hexagonal Architecture Kit

A comprehensive Go library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Adapters Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   REST API │  │    gRPC    │  │   CLI       │              │
│  │   Handler  │  │   Handler  │  │   Handler   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Ports Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Input    │  │   Output   │  │   Domain    │              │
│  │   Port     │  │   Port     │  │   Events    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Entities   │  │Value Objects│  │ Aggregates  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Domain    │  │  Services   │  │  Events     │              │
│  │             │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Use Cases │  │    DTOs    │  │  Handlers  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. Dependency Rule
- Dependencies point inward only
- Domain has zero external dependencies
- Adapters depend on ports, not domain

### 2. Single Responsibility
- Each package has one reason to change
- Ports define contracts
- Adapters implement contracts

### 3. Interface Segregation
- Small, focused interfaces
- No fat interfaces
- Role-based ports

### 4. Pure Domain
- No framework dependencies
- No database calls
- No external I/O

## Quick Start

```go
package main

import (
    "context"
    
    "github.com/kooshapari/phenotype-go-hexagonal/domain"
    "github.com/kooshapari/phenotype-go-hexagonal/ports"
    "github.com/kooshapari/phenotype-go-hexagonal/application"
)

func main() {
    // Define your domain
    type Order struct {
        ID     domain.EntityID
        Items  []OrderItem
        Status OrderStatus
    }
    
    // Define ports
    type OrderRepository interface {
        Save(ctx context.Context, order *Order) error
        FindByID(ctx context.Context, id domain.EntityID) (*Order, error)
    }
    
    // Create use case
    createOrder := application.NewUseCase[CreateOrderCommand, OrderResult](
        func(ctx context.Context, cmd CreateOrderCommand) (OrderResult, error) {
            // Business logic here
            return OrderResult{OrderID: domain.NewEntityID()}, nil
        },
    )
}
```

## Modules

- `domain/` - Core business logic (entities, value objects, aggregates, events)
- `ports/` - Interface definitions (input, output, domain events)
- `application/` - Use cases and application services
- `adapters/` - Infrastructure implementations (REST, gRPC, CLI, persistence)

## Testing

```bash
go test ./...
go test -cover ./...
go vet ./...
gofmt -l .
```

## License

MIT
