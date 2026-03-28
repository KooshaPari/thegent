---
title: phenotype-gauge
description: Property-based testing and mutation analysis framework in Rust.
draft: false
---

**Status**: Active

## Overview

phenotype-gauge is the Phenotype property-based testing and mutation analysis framework. Written in Rust, it provides strategies for generating test inputs, contract definitions for specifying invariants, and mutation operators for verifying that test suites can catch real bugs.

## Tech Stack

- **Language**: Rust
- **Build**: Cargo
- **Testing**: Property-based strategies + mutation operators

## Key Features

- Property-based test strategy generation with shrinking support
- Contract system for pre/post-condition specification
- Mutation operators: value, boundary, and structural mutations
- Spec module for defining and verifying behavioral contracts
- Integrates with the Phenotype QA governance pipeline

## Quick Start

```bash
# Clone and build
git clone https://github.com/KooshaPari/phenotype-gauge
cd phenotype-gauge
cargo build

# Run tests
cargo test

# Run with mutation analysis
cargo test --features mutation
```

## Links

- **GitHub**: [KooshaPari/phenotype-gauge](https://github.com/KooshaPari/phenotype-gauge)
- **Docs**: See `libs/gauge/` in the monorepo for library usage
