"""Contract registry and canonical schema for thegent orchestration.

Provides:
- ContractRegistry: authoritative contract versioning and compatibility
- CanonicalStructuredMessage (CSM): unified schema for agent outputs
- OutputAdapter: protocol for provider-specific output normalization
- ChunkEvent, EvidenceEvent, PolicyEvent: canonical event schemas (WP-0002)
"""

from thegent.contracts.events import ChunkEvent, EvidenceEvent, PolicyEvent
from thegent.contracts.registry import (
    CONTRACT_SCHEMA_VERSION,
    ContractRegistry,
    ContractVersion,
    get_registry,
)
from thegent.contracts.csm import (
    CanonicalStructuredMessage,
    CSMStatus,
    CSMPhase,
)
from thegent.contracts.adapters import (
    OutputAdapter,
    AdapterResult,
    ADAPTER_REGISTRY,
    normalize_output,
)

__all__ = [
    "CONTRACT_SCHEMA_VERSION",
    "ContractRegistry",
    "ContractVersion",
    "get_registry",
    "CanonicalStructuredMessage",
    "CSMStatus",
    "CSMPhase",
    "OutputAdapter",
    "AdapterResult",
    "ADAPTER_REGISTRY",
    "normalize_output",
    "ChunkEvent",
    "EvidenceEvent",
    "PolicyEvent",
]
