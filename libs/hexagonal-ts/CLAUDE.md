# Hexagonal Architecture Library for TypeScript

## Overview

A TypeScript library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Installation

```bash
npm install @phenotype/libs-hexagonal-ts
```

## Usage

```typescript
import { Entity, ValueObject, AggregateRoot } from '@phenotype/libs-hexagonal-ts';

// Define your domain
export class OrderId extends ValueObject {
  constructor(public readonly value: string) {
    super();
  }
}

export class Order extends Entity<OrderId> {
  constructor(
    id: OrderId,
    private items: OrderItem[],
    private status: OrderStatus
  ) {
    super(id);
  }
}

// Define ports
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}
```

## Standards

This library follows the Phenotype coding standards:
- [Solid Principles](https://github.com/phenotype/libs/hexagonal-ts/blob/main/standards/solid.md)
- [Hexagonal Architecture ADR](https://github.com/phenotype/libs/hexagonal-ts/blob/main/governance/adrs/hexagonal-architecture.md)
