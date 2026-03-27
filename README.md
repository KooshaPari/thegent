# Phenotype Ecosystem

A polyglot monorepo for the Phenotype agent development platform, built on hexagonal architecture principles.

## Directory Structure

```
repos/
├── libs/                    # Reusable libraries (extractable/marketable)
│   ├── cipher/              # Cryptographic utilities (Rust)
│   ├── tracing/             # Distributed tracing helpers (Rust)
│   ├── logger/              # Structured logging (Rust)
│   ├── metrics/             # Metrics registry (Rust)
│   ├── nexus/               # State management (Rust)
│   ├── gauge/               # Benchmarking + xDD framework (Rust)
│   ├── clikit/              # CLI toolkit (Go)
│   ├── auth-ts/             # Authentication (TypeScript)
│   ├── config-ts/           # Configuration (TypeScript)
│   ├── evaluation/           # Evaluation framework (Python)
│   ├── logging-zig/          # Logging (Zig)
│   └── hexagonal-*/         # Hexagonal architecture patterns
├── tools/                   # Developer tooling
│   ├── forge/               # Code generation CLI (Rust)
│   ├── dep-guard/           # Dependency guard (Python)
│   ├── ci-cd/               # CI/CD configurations
│   └── devcontainers/       # Dev container definitions
├── packages/                # Phenotype-domain packages
├── services/                # Microservices
├── apps/                    # End-user applications
├── governance/               # Architecture decisions, standards
├── infrastructure/           # Deployment & IaC
└── plans/                   # Planning documents
```

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Rust | 1.70+ | Libraries, CLI tools |
| Go | 1.21+ | CLI tools |
| Node.js | 18+ | TypeScript packages |
| Python | 3.11+ | Python packages |
| Zig | 0.11+ | Zig library |

### Building Libraries

```bash
# Rust libraries
cd libs/cipher && cargo build

# TypeScript packages
cd libs/auth-ts && npm install && npm test

# Python packages
cd libs/evaluation && pip install -e . && pytest

# Go libraries
cd libs/clikit && go build ./...
```

### Running Tools

```bash
# Forge CLI
cargo run --manifest-path tools/forge/Cargo.toml -- --help

# Dep Guard
cd tools/dep-guard && pip install -e . && dep-guard --help
```

## Architecture

Phenotype follows hexagonal (ports and adapters) architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Adapters (Driving)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │   CLI   │  │   API   │  │   Web   │  │  Tests  │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
└───────┼────────────┼────────────┼────────────┼────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Ports (Inbound)                         │
│                     Use Cases / Commands                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Core                              │
│              Entities │ Value Objects │ Events               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Ports (Outbound)                         │
│           Repository │ EventPublisher │ External API         │
└─────────────────────────────────────────────────────────────┘
```

## Package Classification

Packages are classified per [ADR-002](../governance/adrs/0002-package-classification-framework.md):

| Type | Location | Naming | Publishing |
|------|----------|--------|------------|
| A: Domain | `packages/` | `phenotype-*` | Internal only |
| B: Library | `libs/` | No prefix | Public registries |
| C: Tool | `tools/` | No prefix | Optional |
| D: Service | `services/` | `phenotype-*` | Internal only |

## Development

### Running Tests

```bash
# All Rust libraries
cargo test --manifest-path libs/cipher/Cargo.toml
cargo test --manifest-path libs/tracing/Cargo.toml
# ... etc

# TypeScript
cd libs/auth-ts && npm test

# Python
cd libs/evaluation && pytest
```

### Adding a New Library

1. Create directory in `libs/`
2. Add `CLAUDE.md` with architecture documentation
3. Update `libs/README.md`
4. Add to CI/CD pipeline

### Governance

- **ADRs**: `governance/adrs/` - Architecture decision records
- **Standards**: `governance/standards/` - Coding and naming standards
- **Processes**: `governance/processes/` - Workflow documentation

## Reference Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture details
- [PHENOTYPE_WBS_300.md](./PHENOTYPE_WBS_300.md) - Work breakdown structure
- [plans/](./plans/) - Planning documents for all phases

## License

Varies by package. See individual `LICENSE` or `package.json` files.
