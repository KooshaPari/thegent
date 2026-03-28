---
title: Standards
description: Language and tooling standards for the Phenotype ecosystem.
draft: false
---

## Language Standards

| Language | Linter | Formatter | Test Runner |
|----------|--------|-----------|-------------|
| Rust | clippy | rustfmt | cargo test |
| TypeScript | oxlint | prettier | vitest |
| Go | golangci-lint | gofumpt | go test |
| Python | ruff | ruff format | pytest |

## Architecture Standard

All services follow hexagonal architecture (ports and adapters). See [ADR-003](/governance/adrs/) for rationale.

## Naming Standard

See [ADR-004](/governance/adrs/) for naming conventions across all languages and layers.
