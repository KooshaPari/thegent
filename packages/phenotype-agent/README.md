# @phenotype/agent

Phenotype agent core library - provides agent orchestration, task management, and execution capabilities.

## Overview

`@phenotype/agent` provides the core agent infrastructure for the Phenotype ecosystem:
- Agent orchestration and lifecycle management
- Task creation, assignment, and tracking
- Hook-based plugin system
- Domain-driven design with entities for Tasks and Runs

## Installation

```bash
# Python
pip install @phenotype/agent

# Or from source
pip install -e .
```

## Architecture

Based on hexagonal architecture:

```
src/
├── domain/           # Core entities: Task, Run
├── application/      # Use cases
├── ports/           # Interface definitions
├── adapters/        # Infrastructure implementations
└── cli.py           # CLI interface
```

## Modules

| Module | Description |
|--------|-------------|
| `domain.task` | Task entity and value objects |
| `domain.run` | Run entity for execution tracking |
| `hook_registrar` | Hook-based plugin system |
| `renderer` | Output rendering |
| `spec` | Specification utilities |
| `cli` | Command-line interface |

## Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run tests |
| `pip install -e .` | Install in development mode |

## Notes

- This is a Phenotype-domain package
- Version: 0.1.0
