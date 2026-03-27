# tracing-helpers

Tracing utilities for Rust services: `TracingConfig`, `TraceContext`, subscriber builders, and ID generation helpers.

## Features

- `TracingConfig` — builder-style configuration for `tracing-subscriber`
- `init_tracing()` / `build_subscriber()` — subscriber initialization
- `TraceContext` — carries `trace_id` + `span_id` through a request
- `trace_id()` / `span_id()` — UUID-based ID generation
- `level_as_str()` — map `tracing::Level` to string

## Usage

```rust
use tracing_helpers::{init_tracing, TracingConfig};

init_tracing(TracingConfig::new("debug")).ok();
```

## Installation

```toml
[dependencies]
tracing-helpers = { git = "https://github.com/phenotype-dev/tracing-helpers" }
```

## License

MIT
