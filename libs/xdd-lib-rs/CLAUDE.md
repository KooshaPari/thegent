# xDD Testing Library for Rust

## Overview

A Rust library providing cross-cutting xDD (eXtreme Development Driven) testing utilities:
- **Property-based testing** (PBT)
- **Contract testing** (design by contract)
- **Mutation coverage**

## Installation

```toml
[dependencies]
xdd_lib_rs = { git = "https://github.com/phenotype/libs", package = "xdd_lib_rs" }
```

## Usage

```rust
use xdd_lib_rs::{Property, Contract, Invariant};

// Property-based test
fn test_order_idempotence() {
    Property::new(|order: Order| {
        assert_eq!(order.clone(), order.clone().clone())
    }).quickcheck();
}

// Contract test
#[test]
fn test_order_creation() {
    let order = Order::new(OrderId::new(), vec![item]);
    Contract::invariant(&order, |o| o.is_valid());
}

// Mutation testing
Mutation::new(&order)
    .mutate(|m| m.field("status").to(OrderStatus::Cancelled))
    .verify(|m| m.fails_precondition());
```

## xDD Methodologies Covered

- **TDD** - Test-Driven Development
- **BDD** - Behavior-Driven Development
- **DDD** - Domain-Driven Design
- **ADD** - Architecture-Driven Design
- **FDD** - Feature-Driven Development
- **CDD** - Contract-Driven Development
- **MDD** - Model-Driven Development
- **PrD** - Property-Driven Development
- **SDD** - Specification-Driven Development
- **PDD** - Pattern-Driven Development

## Standards

This library follows the Phenotype coding standards:
- [xDD Methodology Compendium](https://github.com/phenotype/libs/blob/main/plans/xdd-methodology-compendium.md)
- [Testing Strategy ADR](https://github.com/phenotype/libs/xdd-lib-rs/blob/main/adr/testing-strategy.md)
