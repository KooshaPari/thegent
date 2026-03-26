"""
Hexagonal Architecture Package for phenotype-skills-clone

This package implements the hexagonal (ports and adapters) architecture pattern
following Clean Architecture principles.

Architecture Layers:
- domain: Pure business logic (entities, value objects, events, services)
- ports: Interface definitions (inbound: commands/queries, outbound: repositories)
- application: Use cases, command/query handlers
- adapters: Infrastructure implementations
"""

__version__ = "0.1.0"

# Re-export from submodules for convenient access
from .domain.entities import Entity
from .domain.value_objects import ValueObject, Identifier
from .domain.events import DomainEvent
from .ports.inbound import Command, Query
from .ports.outbound import Repository, EventBus

__all__ = [
    # Domain
    "Entity",
    "ValueObject",
    "Identifier",
    "DomainEvent",
    # Ports
    "Command",
    "Query",
    "Repository",
    "EventBus",
]
