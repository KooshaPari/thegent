# logger

Structured logging helpers for Rust services: `LoggerConfig`, `log_json!` macro, `LogContext`.

## Features

- `LoggerConfig` — configure level, timestamps, location, correlation ID
- `init()` — initialize `env_logger` with custom formatting
- `log_json!` macro — emit structured JSON log entries
- `LogContext` — correlation ID tracking across log lines

## Usage

```rust
use logger::{init, LoggerConfig, LogContext, info};

// Initialize
init(LoggerConfig::default());

// Structured JSON log
log_json!(Info, event = "request_received", path = "/api/users");

// Contextual logging
let ctx = LogContext::new(None);
info!(ctx.correlation_id = %ctx.correlation_id, "Processing request");
```

## Installation

```toml
[dependencies]
logger = { git = "https://github.com/phenotype-dev/logger" }
```

## License

MIT
