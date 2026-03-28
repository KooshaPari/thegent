# Hexagonal Architecture Library for Go

## Overview

A Go library implementing Hexagonal Architecture (Ports & Adapters) with Clean Architecture principles.

## Installation

```bash
go get github.com/phenotype/libs/hexagonal-go
```

## Usage

```go
package main

import (
    "github.com/phenotype/libs/hexagonal-go/domain"
    "github.com/phenotype/libs/hexagonal-go/ports"
)

// Define your domain
type OrderID struct {
    value string
}

type Order struct {
    id     OrderID
    items  []OrderItem
    status OrderStatus
}

func (o *Order) ID() domain.EntityID {
    return o.id
}

// Define ports
type OrderRepository interface {
    Save(ctx context.Context, order *Order) error
    FindByID(ctx context.Context, id OrderID) (*Order, error)
}
```

## Standards

This library follows the Phenotype coding standards:
- [Solid Principles](https://github.com/phenotype/libs/hexagonal-go/blob/main/standards/solid.md)
- [Hexagonal Architecture ADR](https://github.com/phenotype/libs/hexagonal-go/blob/main/governance/adrs/hexagonal-architecture.md)
