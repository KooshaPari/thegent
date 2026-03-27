# Libraries

Reusable, extractable libraries for the Phenotype ecosystem.

## Classification

See [ADR-002: Package Classification Framework](../governance/adrs/0002-package-classification-framework.md)

- **Type B** - Extractable Libraries
- **Naming** - No `phenotype-` prefix (neutral names)
- **Publishing** - Intended for public registries (crates.io, npm, PyPI)
- **Quality** - >80% test coverage required

## Contents

### Rust Libraries

| Library | Status | Description |
|---------|--------|-------------|
| [cipher](./cipher/) | ✅ Production | Cryptographic utilities |
| [tracing](./tracing/) | ✅ Production | Distributed tracing helpers |
| [logger](./logger/) | ✅ Production | Structured logging |
| [metrics](./metrics/) | ✅ Production | Metrics registry |
| [nexus](./nexus/) | ✅ Production | State management |
| [gauge](./gauge/) | ✅ Production | Benchmarking + xDD framework |
| [hexagonal-rs](./hexagonal-rs/) | ✅ Production | Hexagonal architecture patterns |
| [xdd-lib-rs](./xdd-lib-rs/) | ✅ Production | xDD utilities |

### Go Libraries

| Library | Status | Description |
|---------|--------|-------------|
| [clikit](./clikit/) | ✅ Production | CLI toolkit |
| [hexagonal-go](./hexagonal-go/) | ✅ Production | Hexagonal architecture patterns |

### TypeScript Libraries

| Library | Status | Description |
|---------|--------|-------------|
| [auth-ts](./auth-ts/) | ✅ Production | Authentication |
| [config-ts](./config-ts/) | ✅ Production | Configuration |
| [hexagonal-ts](./hexagonal-ts/) | ✅ Production | Hexagonal architecture patterns |

### Python Libraries

| Library | Status | Description |
|---------|--------|-------------|
| [evaluation](./evaluation/) | ✅ Production | Evaluation framework |
| [hexagonal-py](./hexagonal-py/) | ✅ Production | Hexagonal architecture patterns |

### Zig Libraries

| Library | Status | Description |
|---------|--------|-------------|
| [logging-zig](./logging-zig/) | ✅ Production | Logging |

### Placeholder Libraries

These directories contain scaffolded or pattern libraries:

| Library | Status | Description |
|---------|--------|-------------|
| [event-sourcing](./event-sourcing/) | Placeholder | Event sourcing patterns |
| [state-machine](./state-machine/) | Placeholder | State machine implementation |
| [policy-engine](./policy-engine/) | Placeholder | Policy evaluation |
| [cache-adapter](./cache-adapter/) | Placeholder | Caching patterns |
| [observability](./observability/) | Placeholder | Logging/metrics/tracing |
| [config-lib](./config-lib/) | Placeholder | Configuration loading |

## Building

```bash
# Rust
cd libs/cipher && cargo build

# TypeScript
cd libs/auth-ts && npm install && npm test

# Python
cd libs/evaluation && pip install -e . && pytest

# Go
cd libs/clikit && go build ./...

# Zig
cd libs/logging-zig && zig build
```

## Adding a Library

1. Create directory in `libs/`
2. Add `CLAUDE.md` with architecture documentation
3. Add `Cargo.toml`, `package.json`, or `setup.py` as appropriate
4. Update this README
5. Add to CI/CD pipeline in `tools/ci-cd/`

## Contributing

See [Contributing Guide](../governance/CONTRIBUTING.md)

## License

Each library specifies its own license. Default: MIT
