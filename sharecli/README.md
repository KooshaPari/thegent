<!-- work-state: active | [========8/10] Block B consolidation in progress -->

# thegent-sharecli

CLI share system for multi-agent orchestration - command deduplication, task queue, smart merge, and coordination.

## Architecture

This crate follows **Hexagonal Architecture** (Ports & Adapters) with **Clean Architecture** layers.

## xDD Methodologies Applied

- **TDD**: Tests with pytest
- **DDD**: Domain-driven design with bounded contexts
- **SOLID**: Single responsibility per module
- **CQRS**: Separate commands and queries
- **EDA**: Event-driven architecture

## Installation

```bash
pip install thegent-sharecli
```

## Python API

```python
from thegent_cli_share.adapters.dedup import InMemoryLockAdapter

adapter = InMemoryLockAdapter()
lock = adapter.acquire("cmd_hash", 1234)
```

## License

MIT
