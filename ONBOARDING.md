# Developer Onboarding

Welcome to the Phenotype ecosystem! This guide will help you get started with development.

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.30+ | Version control |
| Node.js | 18+ | TypeScript development |
| Bun | 1.0+ | JavaScript package manager |
| Python | 3.10+ | Python development |
| Rust | 1.70+ | Rust development |
| Go | 1.21+ | Go development |

### Recommended Tools

| Tool | Purpose |
|------|---------|
| VS Code | IDE with extensions |
| Docker | Containerization |
| Postman | API testing |
| TablePlus | Database GUI |

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kooshapari/phenotype.git
cd phenotype/repos
```

### 2. Install Node.js Dependencies

```bash
# For TypeScript packages
cd packages/phenotype-design
bun install

# For any package
bun install
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e packages/phenotype-agent
```

### 4. Install Rust Dependencies

```bash
# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build a Rust library
cd libs/hexagonal-rs
cargo build
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Follow the coding standards in [governance/standards/](../governance/standards/).

### 3. Run Tests

```bash
# TypeScript
bun test

# Python
pytest

# Rust
cargo test
```

### 4. Run Linting

```bash
# TypeScript
bun run lint

# Python
ruff check .

# Rust
cargo clippy
```

### 5. Commit Changes

Follow conventional commit format:

```
type(scope): description

feat(agent): add new task scheduling algorithm
fix(core): resolve race condition in event handler
docs(readme): update installation instructions
```

### 6. Submit Pull Request

1. Push your branch
2. Open a pull request
3. Ensure CI passes
4. Request review

## Project Structure

### packages/ (Phenotype-Domain)

Packages that are tightly coupled to the Phenotype domain:

- `phenotype-config/` - Configuration management
- `phenotype-design/` - Design tokens and themes
- `phenotype-agent/` - Agent orchestration
- `phenotype-task/` - Task management
- `phenotype-research/` - Research engine
- `phenotype-docs/` - Documentation generation

### libs/ (Extractable Libraries)

Language-specific hexagonal architecture implementations:

- `hexagonal-rs/` - Rust
- `hexagonal-ts/` - TypeScript
- `hexagonal-py/` - Python
- `hexagonal-go/` - Go

### services/

Microservices:

- See `services/` directory

### tools/

Developer tooling:

- `tools/scripts/` - Utility scripts
- `tools/ci-cd/` - CI/CD configurations
- `tools/devcontainers/` - Dev container definitions

## Common Tasks

### Add a New Package

1. Create directory in appropriate location (`packages/` or `libs/`)
2. Follow the standard package structure
3. Add `CLAUDE.md` for AI assistant context
4. Add `README.md` with documentation
5. Add `CHANGELOG.md`

### Add a New Microservice

1. Create directory in `services/<service-name>/`
2. Follow hexagonal architecture
3. Add Dockerfile
4. Add docker-compose.yml
5. Add service documentation

### Update Dependencies

```bash
# TypeScript
bun update

# Python
pip freeze > requirements.txt

# Rust
cargo update
```

## Resources

### Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Coding Standards](../governance/standards/)
- [Architecture Decision Records](../governance/adrs/)

### Getting Help

- Join our Discord community
- Open a GitHub issue
- Check the wiki

## Next Steps

1. Read the [Architecture Overview](ARCHITECTURE.md)
2. Review [Coding Standards](../governance/standards/)
3. Pick a "good first issue" from GitHub issues
4. Make your first contribution!

Welcome aboard!
