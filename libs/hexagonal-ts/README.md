# Phenotype TypeScript Hexagonal Architecture Kit

A comprehensive TypeScript/Node.js library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Adapters Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   REST API │  │   GraphQL  │  │   CLI       │              │
│  │   Adapter  │  │   Adapter  │  │   Adapter   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Ports Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Input Port  │  │ Output Port │  │  Domain     │              │
│  │ (Commands)  │  │ (Queries)   │  │  Events     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Entities   │  │ Value Objs  │  │ Aggregates  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Domain    │  │  Services   │  │  Events     │              │
│  │             │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Usage

```typescript
import {
  Entity,
  ValueObject,
  AggregateRoot,
  DomainEvent,
  Repository,
  UseCase,
  InputPort,
  OutputPort,
} from '@phenotype/ts-hexagonal';

// Define your domain
class OrderId extends ValueObject<OrderId> {
  constructor(public readonly value: string) {
    super();
  }

  equals(other: OrderId): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}

class Order extends AggregateRoot<Order, OrderId> {
  constructor(
    id: OrderId,
    private items: OrderItem[],
    private status: OrderStatus,
  ) {
    super(id);
  }

  // Business logic here
}

// Define ports
interface OrderRepository extends Repository<Order, OrderId> {
  findByStatus(status: OrderStatus): Promise<Order[]>;
}

// Use case
class CreateOrderUseCase implements UseCase<CreateOrderCommand, OrderResult> {
  constructor(private readonly repository: OrderRepository) {}

  async execute(input: CreateOrderCommand): Promise<OrderResult> {
    // Business logic
    return { orderId: new OrderId(uuid()) };
  }
}
```

## License

MIT
