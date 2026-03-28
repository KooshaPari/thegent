# Phenotype Shared Logging

**Status:** `Implemented`  
**Type:** Shared Library Interface  
**Language:** Rust (Python/TypeScript ports pending)

Shared structured logging interface for the Phenotype ecosystem.

## Architecture

```
┌─────────────────────────────────────────────┐
│           Application Code                   │
│  Logger trait (interface/port)              │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Env    │ │  JSON   │ │ Custom  │
│ Adapter │ │ Adapter │ │ Adapter │
└─────────┘ └─────────┘ └─────────┘
```

## Usage

```rust
use phenotype_shared_logging::{init, LoggerConfig, log_json, LogContext, Level};

fn main() {
    let config = LoggerConfig {
        level: Level::Info,
        include_timestamps: true,
        include_location: true,
        correlation_id: None,
    };
    init(config);
    
    log_json!(Level::Info, "event" = "user_login", "user_id" = "123");
}
```

## Features

- Structured JSON logging
- Correlation ID tracking
- Log level filtering
- Metadata attachment
- Backend-agnostic interface
- Env var configuration adapter

## Extracting from phenotype-logger

The `phenotype-logger` package in `packages/phenotype-logger/` contains the production implementation. This shared interface defines the port/trait that implementations must follow.

## Next Steps

- [ ] Extract production implementation from `packages/phenotype-logger/`
- [ ] Create Python port (`libs/shared/logging-python/`)
- [ ] Create TypeScript port (`libs/shared/logging-ts/`)
- [ ] Add file-based adapter
- [ ] Add syslog adapter
