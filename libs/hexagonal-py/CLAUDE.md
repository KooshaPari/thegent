# Hexagonal Architecture Library for Python

## Overview

A Python library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Installation

```bash
pip install hexagonal-py
```

## Usage

```python
from hexagonal_py import Entity, ValueObject, AggregateRoot

# Define your domain
@dataclass
class OrderId(ValueObject):
    value: str

class Order(Entity[OrderId]):
    def __init__(self, id: OrderId, items: list[OrderItem], status: OrderStatus):
        super().__init__(id)
        self._items = items
        self._status = status

# Define ports
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, id: OrderId) -> Order | None: ...
```

## Standards

This library follows the Phenotype coding standards:
- [Solid Principles](https://github.com/phenotype/libs/hexagonal-py/blob/main/standards/solid.md)
- [Hexagonal Architecture ADR](https://github.com/phenotype/libs/hexagonal-py/blob/main/governance/adrs/hexagonal-architecture.md)
