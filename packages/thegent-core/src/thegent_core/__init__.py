"""thegent-core: Foundation layer for thegent.

This package contains the core domain primitives, ports (hexagonal architecture
interfaces), configuration management, constants, contracts, and models.

Modules migrated from thegent monolith src/thegent/:
- domain/      : Pure domain entities and value objects (no I/O or side effects)
- ports/       : Hexagonal architecture port interfaces (driven/driving)
- config/      : Configuration management (ThegentSettings and sub-configs)
- constants    : Global constants
- contracts/   : Contract registry, CSM schema, canonical event schemas
- models/      : Model catalog, routing, and scraper infrastructure
"""

from thegent_core.config.settings import ThegentSettings, get_settings
from thegent_core.config.model_config import ModelConfig
from thegent_core.config.path_config import PathConfig
from thegent_core.config.runtime_config import RuntimeConfig

from thegent_core.contracts.csm import (
    CanonicalStructuredMessage,
    CSMPhase,
    CSMStatus,
)
from thegent_core.contracts.events import ChunkEvent, EvidenceEvent, PolicyEvent
from thegent_core.contracts.registry import (
    CONTRACT_SCHEMA_VERSION,
    ContractRegistry,
    ContractVersion,
    get_registry,
)

__all__ = [
    # config
    "ThegentSettings",
    "get_settings",
    "ModelConfig",
    "PathConfig",
    "RuntimeConfig",
    # contracts
    "CONTRACT_SCHEMA_VERSION",
    "CSMPhase",
    "CSMStatus",
    "CanonicalStructuredMessage",
    "ChunkEvent",
    "ContractRegistry",
    "ContractVersion",
    "EvidenceEvent",
    "PolicyEvent",
    "get_registry",
]
