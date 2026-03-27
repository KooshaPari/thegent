# CLAUDE.md — metrics-registry

## Overview

`metrics-registry` is a minimal metrics registry with Prometheus-style text export: counters, gauges, timers.

## Package

- **Name**: `metrics-registry`
- **Repository**: `https://github.com/phenotype-dev/metrics-registry`
- **Language**: Rust
- **Edition**: 2021

## Architecture

Domain utility crate — `MetricsRegistry` is the core type; `MetricValue` and `MetricType` are plain domain constructs. No hexagonal layers needed.

## Dependencies

- None (pure std + thread-safe mutex via `Arc`)

## Build & Test

```bash
cargo test
cargo clippy
```

## Key Types

| Type | Description |
|------|-------------|
| `MetricType` | Enum: Counter, Gauge, Histogram, Timer |
| `MetricValue` | Single metric: name, value, type, timestamp, labels |
| `MetricsRegistry` | Thread-safe in-memory registry |
| `MetricsRegistry::increment_counter()` | Record counter increments |
| `MetricsRegistry::set_gauge()` | Set gauge value |
| `MetricsRegistry::record_timer()` | Record timer/duration |
| `MetricsRegistry::export_prometheus()` | Emit Prometheus text format |

## Relationship to Other Crates

- `metrics-registry` is the minimal/simple registry implementation.
- `thegent-metrics` is the architected observability core with ports/adapters, richer metric types, and multiple exporters.
- `gauge` is an xDD/testing and reporting crate, not runtime observability.

## Conventions

- Follows Rust coding standards per `governance/standards/rust.md`
- MIT licensed
- No Phenotype-domain coupling — pure utility crate

## Phase 6 Status

- Source: `phenotype-metrics/`
- Canonical location: `libs/metrics/`
- Status: Extracted and renamed
