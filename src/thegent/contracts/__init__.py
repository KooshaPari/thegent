"""Contract registry and canonical schema for thegent orchestration.

Provides:
- ContractRegistry: authoritative contract versioning and compatibility
- CanonicalStructuredMessage (CSM): unified schema for agent outputs
- OutputAdapter: protocol for provider-specific output normalization
- ChunkEvent, EvidenceEvent, PolicyEvent: canonical event schemas (WP-0002)
"""

from thegent.contracts.adapters import (
    ADAPTER_REGISTRY,
    AdapterResult,
    OutputAdapter,
    normalize_output,
)
from thegent.contracts.csm import (
    CanonicalStructuredMessage,
    CSMPhase,
    CSMStatus,
)
from thegent.contracts.events import ChunkEvent, EvidenceEvent, PolicyEvent
from thegent.contracts.registry import (
    CONTRACT_SCHEMA_VERSION,
    ContractRegistry,
    ContractVersion,
    get_registry,
)

__all__ = [
    "ADAPTER_REGISTRY",
    "CONTRACT_SCHEMA_VERSION",
    "AdapterResult",
    "CSMPhase",
    "CSMStatus",
    "CanonicalStructuredMessage",
    "ChunkEvent",
    "ContractRegistry",
    "ContractVersion",
    "EvidenceEvent",
    "OutputAdapter",
    "PolicyEvent",
    "get_registry",
    "normalize_output",
]
