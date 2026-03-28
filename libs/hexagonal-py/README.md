# Phenotype Python Hexagonal Architecture Kit

A comprehensive Python library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

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
└─────────────────────────────────────────────────────────────────┘
```

## Usage

```python
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4

from phenotype_hexagonal.domain import (
    Entity,
    ValueObject,
    AggregateRoot,
    DomainEvent,
    DomainError,
)
from phenotype_hexagonal.ports import Repository, UseCase
from phenotype_hexagonal.application import DTO

# Define your domain
@dataclass(frozen=True)
class OrderId(ValueObject):
    value: str
    
    def equals(self, other: ValueObject) -> bool:
        return isinstance(other, OrderId) and self.value == other.value

class Order(AggregateRoot):
    def __init__(self, id: OrderId, items: List[OrderItem]):
        super().__init__(id)
        self._items = items
        self._status = OrderStatus.PENDING
    
    @property
    def items(self) -> List[OrderItem]:
        return list(self._items)
    
    def add_item(self, item: OrderItem) -> None:
        self._items.append(item)
        self.add_event(OrderItemAdded(self.id.value, item))

# Define ports
class OrderRepository(Repository[Order, OrderId]):
    pass

# Use case
class CreateOrderUseCase(UseCase[CreateOrderCommand, OrderResult]):
    def __init__(self, repository: OrderRepository):
        self.repository = repository
    
    async def execute(self, input: CreateOrderCommand) -> OrderResult:
        order = Order(OrderId(str(uuid4())), input.items)
        await self.repository.save(order)
        return OrderResult(order_id=order.id)
```

## Installation

```bash
pip install phenotype-hexagonal
```

## License

MIT
