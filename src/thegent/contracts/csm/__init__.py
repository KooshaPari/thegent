"""Canonical Structured Message (CSM) versioned package.

Re-exports the current schema version for convenience.
"""

from thegent.contracts.csm.v1 import (
    CanonicalStructuredMessage,
    CSMPhase,
    CSMStatus,
)

__all__ = ["CSMPhase", "CSMStatus", "CanonicalStructuredMessage"]
