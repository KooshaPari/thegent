# ARCHIVED — phenotype-metrics

**Status:** This repository has been archived.

## What happened

The crate has been extracted and productized under a neutral name.

## Canonical location

```
https://github.com/phenotype-dev/metrics-registry
```

Package name: `metrics-registry`

## Migration

Replace in `Cargo.toml`:

```toml
# Old
phenotype-metrics = { path = "path/to/phenotype-metrics" }

# New
metrics-registry = { git = "https://github.com/phenotype-dev/metrics-registry" }
```

Replace in source code:

```rust
// Old
use phenotype_metrics::{MetricsRegistry, MetricType};

// New
use metrics_registry::{MetricsRegistry, MetricType};
```

## Timeline

- Archived: 2026-03-26
- Phase 6 productization
