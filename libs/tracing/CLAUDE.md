# CLAUDE.md — tracing-helpers

## Overview

`tracing-helpers` provides tracing utilities for Rust services: `TracingConfig`, `TraceContext`, subscriber builders, and ID generation helpers.

## Package

- **Name**: `tracing-helpers`
- **Repository**: `https://github.com/phenotype-dev/tracing-helpers`
- **Language**: Rust
- **Edition**: 2021

## Architecture

Domain utility crate — no hexagonal layers needed for a helpers library. All types are plain domain constructs.

## Dependencies

- `tracing` — tracing core
- `tracing-subscriber` — subscriber layer
- `uuid` — ID generation

## Build & Test

```bash
cargo test
cargo clippy
```

## Key Types

| Type | Description |
|------|-------------|
| `TracingConfig` | Builder-style config for subscriber initialization |
| `TraceContext` | Carries `trace_id` + `span_id` through a request |
| `TraceKey<'a>` | Display wrapper for trace key strings |
| `init_tracing()` | Initialize subscriber from config |
| `build_subscriber()` | Build subscriber without initializing |
| `trace_id()` / `span_id()` | UUID-based ID generation |
| `level_as_str()` | Map `tracing::Level` to string |

## Conventions

- Follows Rust coding standards per `governance/standards/rust.md`
- MIT licensed
- No Phenotype-domain coupling — pure utility crate

## Phase 6 Status

- Source: `phenotype-tracing/`
- Canonical location: `libs/tracing/`
- Status: Extracted and renamed
