"""Contract registry and canonical schema for thegent orchestration.

Provides:
- ContractRegistry: authoritative contract versioning and compatibility
- CanonicalStructuredMessage (CSM): unified schema for agent outputs
- OutputAdapter: protocol for provider-specific output normalization
- ChunkEvent, EvidenceEvent, PolicyEvent: canonical event schemas (WP-0002)

OPT-006: Lazy adapter loading (import on first use) - Reduce startup time ~200ms.
"""

# OPT-006: Lazy import adapters to reduce startup time
_adapters_module = None


def _lazy_import_adapters():
    """Lazy import adapter module (only when first accessed)."""
    global _adapters_module
    if _adapters_module is None:
        import thegent.contracts.adapters as _adapters_module
    return _adapters_module


# OPT-006: Lazy-loaded adapter exports (imported on first access)
def __getattr__(name: str):
    """Lazy import adapter symbols on first access."""
    if name in ("ADAPTER_REGISTRY", "AdapterResult", "OutputAdapter", "normalize_output"):
        adapters = _lazy_import_adapters()
        return getattr(adapters, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Import adapters lazily - only when explicitly accessed
# This defers adapter registration until first use, reducing startup time
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

# OPT-006: Adapters are lazy-loaded via __getattr__ above
# Import them here for backward compatibility, but they'll be lazy-loaded on first access
# This allows existing code to work while deferring adapter registration until needed

__all__ = [
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
