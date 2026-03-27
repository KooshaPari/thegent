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

```text
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

## CI/CD Scripts and Workflows

- Local scripts
  - `tools/scripts/build-all-libs.sh`
  - `tools/scripts/test-all-libs.sh`
  - `tools/scripts/verify-libs.sh`
  - `tools/scripts/test-tools.sh`
  - `tools/scripts/build-tools.sh`
- GitHub workflows
  - `.github/workflows/test-libs.yml`
  - `.github/workflows/build-libs.yml`
  - `.github/workflows/test-tools.yml`
  - `.github/workflows/build-tools.yml`
  - `.github/workflows/test-libs-tools.yml` (combined libs+tools checks)
  - `.github/workflows/build-release.yml` (release artifacts)

### Usage

```bash
# Run everything for libs
bash tools/scripts/test-all-libs.sh
bash tools/scripts/build-all-libs.sh
bash tools/scripts/verify-libs.sh

# Run everything for tools
bash tools/scripts/test-tools.sh
bash tools/scripts/build-tools.sh
```

Current CI workflow for libs and tools is also available via `.github/workflows/test-libs-tools.yml` for combined checks.

## CI/CD

CI/CD automation is defined in `.github/workflows/` and is driven by the scripts above.

```bash
# Available workflows:
# - test-libs.yml, build-libs.yml
# - test-tools.yml, build-tools.yml
# - test-libs-tools.yml
# - build-release.yml
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
