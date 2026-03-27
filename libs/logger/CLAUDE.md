# CLAUDE.md — logger

## Overview

`logger` provides structured logging helpers for Rust services: `LoggerConfig`, `log_json!` macro, `LogContext`.

## Package

- **Name**: `logger`
- **Repository**: `https://github.com/phenotype-dev/logger`
- **Language**: Rust
- **Edition**: 2021

## Architecture

Domain utility crate — no hexagonal layers needed for a helpers library. Types are plain domain constructs.

## Dependencies

- `log` — logging facade
- `env_logger` — concrete logger implementation
- `chrono` — timestamp formatting
- `serde_json` — JSON serialization for `log_json!` macro
- `uuid` — correlation ID generation

## Build & Test

```bash
cargo test
cargo clippy
```

## Key Types

| Type | Description |
|------|-------------|
| `LoggerConfig` | Configure level, timestamps, location, correlation ID |
| `LogContext` | Carries correlation ID across log lines |
| `init()` | Initialize env_logger with custom formatting |
| `log_json!` | Emit structured JSON log entries |

## Conventions

- Follows Rust coding standards per `governance/standards/rust.md`
- MIT licensed
- No Phenotype-domain coupling — pure utility crate

## Phase 6 Status

- Source: `phenotype-logger/`
- Canonical location: `libs/logger/`
- Status: Extracted and renamed
