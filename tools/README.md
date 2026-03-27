# Tools

Developer tooling, scripts, and automation for the Phenotype ecosystem.

## Overview

This directory contains:
- Build and deployment scripts
- CI/CD configurations
- Dev containers
- Developer utilities

## Current Tools

### CLI Tools

| Tool | Language | Status | Description |
|------|----------|--------|-------------|
| [forge](./forge/) | Rust | ✅ Production | Code generation CLI |
| [dep-guard](./dep-guard/) | Python | ✅ Production | Dependency guard |

### Infrastructure

| Directory | Description |
|-----------|-------------|
| [ci-cd](./ci-cd/) | CI/CD pipeline configurations |
| [devcontainers](./devcontainers/) | Dev container definitions |
| [scripts](./scripts/) | Utility scripts |

## Directory Structure

```
tools/
├── forge/               # Code generation CLI (Rust)
├── dep-guard/           # Dependency guard (Python)
├── ci-cd/              # CI/CD pipeline configurations
│   └── github-actions/  # GitHub Actions workflows
├── devcontainers/       # Dev container definitions
└── scripts/             # Shell and utility scripts
```

## Using Tools

### Forge CLI

```bash
# Build and run
cargo run --manifest-path forge/Cargo.toml -- --help

# Or install
cargo install --path forge
forge --help
```

### Dep Guard

```bash
# Install
cd dep-guard && pip install -e .

# Run
dep-guard --help
dep-guard check ./libs
```

## CI/CD

GitHub Actions workflows for testing and building:

```bash
# Workflows are in tools/ci-cd/github-actions/
# Run via: .github/workflows/*.yml (symlinked or copied to repos)
```

## Dev Containers

Development container definitions for consistent environments.

```bash
# Open in VS Code
code --remote container .

# Or use Docker directly
docker build -f tools/devcontainers/base.Dockerfile .
```

## Adding a Tool

1. Create directory in `tools/`
2. Add `CLAUDE.md` with tool documentation
3. Add appropriate manifest (Cargo.toml, setup.py, etc.)
4. Update this README
5. Add to CI/CD pipeline

## References

- [ADR-0005: Top-Level Directory Structure](../governance/adrs/0005-top-level-directory-structure.md)
