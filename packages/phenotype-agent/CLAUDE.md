# @phenotype/agent

## Overview

Phenotype agent core library - provides agent orchestration, task management, and execution capabilities.

## Quick Start

```bash
# Install
pip install -e .

# Run tests
pytest
```

## Architecture

Based on hexagonal architecture with the following layers:
- **Domain**: Agent entities, Task, Run
- **Application**: Agent workflows, execution pipelines
- **Ports**: Inbound and outbound interfaces
- **Adapters**: CLI, hook system implementations

## Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run tests |
| `pip install -e .` | Install in development mode |

## Dependencies

- Python 3.10+
- pytest (dev)
- pydantic (validation)

## Notes

- This is a Phenotype-domain package (stays in `packages/`)
- Version: 0.1.0
