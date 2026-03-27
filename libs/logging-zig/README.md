# logging-zig

Zig structured logging with minimal allocations: log levels, string conversion, and tests aligned with xDD practices.

## Features

- Structured logging with log levels (debug, info, warn, error, fatal)
- Minimal allocations for embedded/systems programming
- String conversion utilities
- Integration-friendly API
- xDD-aligned test patterns

## Installation

Add to your `build.zig.zon`:

```zig
.logging_zig = .{
    .url = "https://github.com/phenotype-dev/logging-zig/archive/main.tar.gz",
    .hash = "your-hash-here",
},
```

## Usage

```zig
const logging = @import("logging-zig");

pub fn main() void {
    var logger = logging.Logger.init();
    logger.info("Application started", .{});
    logger.warn("This is a warning", .{});
    logger.err("An error occurred", .{});
}
```

## Build & Test

Validated on **Zig 0.15.x**:

```bash
zig build test
# or, without the build graph:
zig test src/lib.zig
```

## Architecture

```
src/
├── lib.zig           # Main logging API
├── level.zig         # Log level definitions
├── formatter.zig     # String formatting utilities
└── writer.zig        # Output writer interface
```

## Scope

This is a neutral Zig logging crate with no Phenotype-specific dependencies. Intended for embedded systems and performance-critical applications.

## License

MIT
