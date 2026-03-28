"""
Phenotype Python Hexagonal Architecture Kit

A comprehensive implementation of Hexagonal Architecture (Ports & Adapters)
with Clean Architecture principles, SOLID compliance, and domain-driven design.
"""

from .domain import (
    Entity,
    ValueObject,
    AggregateRoot,
    DomainEvent,
    DomainService,
    DomainError,
    EntityId,
)
from .ports import (
    InputPort,
    OutputPort,
    Repository,
    UseCase,
)
from .application import (
    DTO,
    Command,
    Query,
    ApplicationError,
)

__version__ = "1.0.0"
__all__ = [
    # Domain
    "Entity",
    "ValueObject",
    "AggregateRoot",
    "DomainEvent",
    "DomainService",
    "DomainError",
    "EntityId",
    # Ports
    "InputPort",
    "OutputPort",
    "Repository",
    "UseCase",
    # Application
    "DTO",
    "Command",
    "Query",
    "ApplicationError",
]
