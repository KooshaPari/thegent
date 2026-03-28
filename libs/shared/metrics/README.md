# Phenotype Shared Metrics

**Status:** `Implemented`  
**Type:** Shared Library Interface  
**Language:** Rust (Python/TypeScript ports pending)

## Overview

Provides a language-agnostic metrics interface for the Phenotype ecosystem, enabling consistent observability across all services and applications.

## Metric Types

| Type | Description | Use Case |
|-------|-------------|----------|
| `Counter` | Incremental values | Request counts, error counts |
| `Gauge` | Point-in-time values | Memory usage, connection count |
| `Histogram` | Value distributions | Response sizes, latencies |
| `Timer` | Duration measurements | Request latency |

## Architecture

```
┌─────────────────────────────────────────────┐
│           Application Code                   │
│  MetricsPort trait (interface/port)         │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Prometheus│ │  StatsD  │ │ CloudWatch│
│ Adapter  │ │  Adapter │ │  Adapter  │
└─────────┘ └─────────┘ └─────────┘
```

## Usage

```rust
use phenotype_metrics::prelude::*;

let registry = MetricsRegistry::new();

// Counters
registry.increment_counter("http_requests_total", 1.0);

// Gauges
registry.set_gauge("memory_bytes", 1024.0);

// Timers
registry.record_timer("request_duration", Duration::from_millis(50));

// Export
let prometheus_output = registry.export_prometheus();
```

## Extracting from phenotype-metrics

The `phenotype-metrics` package in `packages/phenotype-metrics/` contains the production implementation. This shared interface defines the port/trait that implementations must follow.

## Next Steps

- [x] Extract production implementation from `packages/phenotype-metrics/`
- [ ] Create Python port (`libs/shared/metrics-python/`)
- [ ] Create TypeScript port (`libs/shared/metrics-ts/`)
- [x] Add OpenTelemetry adapter
- [ ] Add Datadog adapter
