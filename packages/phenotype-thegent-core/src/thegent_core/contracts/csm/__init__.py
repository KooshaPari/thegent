"""Canonical Structured Message (CSM) versioned package.

Re-exports the current schema version for convenience.
"""

from thegent_core.contracts.csm.v1 import (
    CanonicalStructuredMessage,
    CSMPhase,
    CSMStatus,
)

__all__ = ["CSMPhase", "CSMStatus", "CanonicalStructuredMessage"]
