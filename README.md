# Hexagonal Architecture for phenotype-skills-clone

This module implements hexagonal (ports and adapters) architecture for the skills clone project.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              (Adapters: CLI, API, Web UI)                   │
├─────────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                          │
│          (Commands, Queries, Use Cases, Handlers)           │
├─────────────────────────────────────────────────────────────┤
│                     DOMAIN LAYER                            │
│    (Entities, Value Objects, Domain Events, Services)        │
├─────────────────────────────────────────────────────────────┤
│                     PORTS LAYER                             │
│     (Inbound: Commands/Queries, Outbound: Repository)       │
├─────────────────────────────────────────────────────────────┤
│                  ADAPTERS LAYER                             │
│        (Primary: CLI, Secondary: DB, Cache, API)            │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
arch/hexagonal/
├── domain/                    # Pure business logic (no dependencies)
│   ├── entities/              # Domain entities (Skill, Agent, Task)
│   │   ├── __init__.py
│   │   └── skill.py
│   ├── value_objects/         # Value objects (Identifier, etc.)
│   │   └── __init__.py
│   ├── events/                # Domain events (SkillCreated, etc.)
│   │   └── __init__.py
│   ├── services/              # Domain services (Specifications)
│   │   └── __init__.py
│   └── __init__.py
│
├── ports/                    # Interface definitions
│   ├── inbound/              # Driving ports (Command, Query, Handler)
│   │   └── __init__.py
│   └── outbound/             # Driven ports (Repository, Cache, EventBus)
│       └── __init__.py
│
├── application/               # Use cases and orchestration
│   ├── commands/              # Command definitions
│   │   ├── __init__.py
│   │   └── skill_commands.py
│   ├── queries/               # Query definitions
│   │   └── __init__.py
│   ├── handlers/              # Command and Query handlers
│   │   ├── __init__.py
│   │   └── skill_handler.py
│   └── __init__.py
│
└── adapters/                  # Infrastructure implementations
    ├── primary/               # Driving adapters (CLI, API)
    │   └── __init__.py
    └── secondary/             # Driven adapters (DB, Redis, HTTP)
        └── __init__.py
```

## Key Concepts

### Domain Layer
- **Entities**: Objects with identity (Skill, Agent, Task)
- **Value Objects**: Immutable objects defined by attributes
- **Domain Events**: Things that happen in the domain
- **Domain Services**: Operations that don't belong to entities

### Ports Layer
- **Inbound Ports**: Define how external actors interact with the system
- **Outbound Ports**: Define how the system interacts with external services

### Application Layer
- **Commands**: Intent to perform an action (Create, Update, Delete)
- **Queries**: Intent to read data
- **Handlers**: Execute commands and queries

### Adapters Layer
- **Primary Adapters**: Translate external requests to commands
- **Secondary Adapters**: Implement outbound ports (Repository, Cache, etc.)

## Usage Example

```python
from hexagonal.domain.entities import Skill
from hexagonal.application.commands import CreateSkillCommand
from hexagonal.application.handlers import SkillCommandHandler
from hexagonal.ports.outbound import Repository, EventBus

# Create adapters
skill_repository = PostgresSkillRepository(connection_string)
event_bus = RedisEventBus(connection_string)

# Create handler with dependencies
handler = SkillCommandHandler(skill_repository, event_bus)

# Execute command
command = CreateSkillCommand(
    name="Code Review",
    description="Reviews code changes",
    category="quality",
)
result = await handler.handle(command)

if result.success:
    print(f"Created skill: {result.data['skill_id']}")
```

## Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **SOLID** | Interfaces for all dependencies |
| **DRY** | Shared port abstractions |
| **KISS** | Simple, focused modules |
| **DDD** | Domain entities, value objects, events |
| **CQRS** | Separate Command and Query handlers |
| **Hexagonal** | Ports/Adapters separation |
| **Event Sourcing** | Domain events for state changes |
