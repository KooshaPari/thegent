"""Execution run metadata and registry for thegent orchestration.

This module has been migrated to execution_v2 package.
Import from there for full implementations.
"""

import warnings
warnings.warn(
    "execution module migrated to execution_v2. Import from there.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from v2
from thegent.execution_v2 import (
    RunRegistry,
    RunMeta,
    CheckpointMeta,
    ChatHistory,
    ChatEntry,
    MessageRegistry,
    MessageEntry,
    AuditRegistry,
    AuditEntry,
    CheckpointRegistry,
    PolicyEngine,
    TrustBoundaryValidator,
    EscalationQueue,
    DLQManager,
    CircuitBreakerRegistry,
    OverrideRegistry,
)

__all__ = [
    "RunRegistry",
    "RunMeta", 
    "CheckpointMeta",
    "ChatHistory",
    "ChatEntry",
    "MessageRegistry", 
    "MessageEntry",
    "AuditRegistry",
    "AuditEntry",
    "CheckpointRegistry",
    "PolicyEngine",
    "TrustBoundaryValidator",
    "EscalationQueue",
    "DLQManager",
    "CircuitBreakerRegistry",
    "OverrideRegistry",
]
