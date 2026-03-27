# metrics-registry

Minimal metrics registry with Prometheus-style text export.

## Features

- `MetricsRegistry` — thread-safe in-memory registry
- Counters, gauges, timers (histograms)
- `export_prometheus()` — emit metrics in Prometheus exposition format

## Usage

```rust
use metrics_registry::{MetricsRegistry, Duration};

let registry = MetricsRegistry::new();

registry.increment_counter("http_requests_total", 1.0);
registry.set_gauge("memory_usage_bytes", 512.0);
registry.record_timer("response_time_ms", Duration::from_millis(42));

println!("{}", registry.export_prometheus());
```

## Installation

```toml
[dependencies]
metrics-registry = { git = "https://github.com/phenotype-dev/metrics-registry" }
```

## Relationship to other crates

- `metrics-registry` is the minimal/simple registry implementation.
- `thegent-metrics` is the architected observability core with ports/adapters, richer metric types, and multiple exporters.
- `gauge` is an xDD/testing and reporting crate, not runtime observability.

## License

MIT
