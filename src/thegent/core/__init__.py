"""Core layer - Domain types, errors, and port interfaces.

This is Layer 0 of the hexagonal architecture. It has NO dependencies
on other thegent modules and NO external dependencies except Python stdlib.

It exports:
- Domain entities (SLA, SLO, compliance contracts)
- Error types (ExecutionError, AgentError, etc.)
- Port interfaces (AgentInterface, ModelInterface, etc.)
"""

from thegent.core.domain import (
    Attestation,
    ComplianceContract,
    ComplianceRequirement,
    ContractRegistry,
    ContractStatus,
    ContractType,
    OutputProtocol,
    ParsedOutput,
    SLAAgreement,
    SLODefinition,
    SLOTarget,
)
from thegent.core.errors import (
    AgentError,
    ConfigurationError,
    ErrorContext,
    ExecutionError,
    ModelError,
    ParseError,
    RouterError,
    TheGentError,
    ValidationError,
)
from thegent.core.ports import (
    AgentInterface,
    EventBusInterface,
    ExecutorInterface,
    LoggerInterface,
    ModelInterface,
    PlannerInterface,
    RouterInterface,
)

__all__ = [
    # Domain
    "SLOTarget",
    "SLODefinition",
    "SLAAgreement",
    "ComplianceRequirement",
    "ComplianceContract",
    "Attestation",
    "ContractRegistry",
    "ContractStatus",
    "ContractType",
    "ParsedOutput",
    "OutputProtocol",
    # Errors
    "TheGentError",
    "ErrorContext",
    "ExecutionError",
    "AgentError",
    "ModelError",
    "RouterError",
    "ValidationError",
    "ConfigurationError",
    "ParseError",
    # Ports
    "AgentInterface",
    "ModelInterface",
    "RouterInterface",
    "LoggerInterface",
    "EventBusInterface",
    "ExecutorInterface",
    "PlannerInterface",
]
