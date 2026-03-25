"""Execution module - organized into logical domains.

This package contains:
- execution/state.py: RunState, RunMeta, CheckpointMeta, etc.
- execution/resilience.py: DLQManager, DeferralQueue, etc.
- execution/concurrency.py: IdempotencyManager, ConcurrencyController, etc.
- execution/policy.py: PolicyEngine, ProviderScorer, KPIManager, etc.
- execution/registry.py: RunRegistry, ChatHistory, etc.

Import from here or directly from submodules:
    from thegent.execution import RunState
    from thegent.execution.state import RunState
"""

from __future__ import annotations

from typing import Any

# Import all from modular subpackages
from .state import (
    AgentSource,
    CalibrationRegistry,
    CheckpointMeta,
    ContinuityPacket,
    InteractivityMode,
    MAIFArtifact,
    RunMeta,
    RunState,
)
from .resilience import (
    CircuitBreakerRegistry,
    ContinuityWatchdog,
    DeferralQueue,
    DLQManager,
    EscalationQueue,
    FreshnessValidator,
    HandoffManager,
    InterruptionTracker,
    OverrideRegistry,
    ReplayManager,
)
from .concurrency import (
    ConcurrencyController,
    IdempotencyManager,
    LaneController,
    LoadClassifier,
)
from .policy import (
    Auditor,
    EvidenceLinter,
    KPIManager,
    PolicyEngine,
    ProviderScorer,
    TrustBoundaryValidator,
)
from .registry import (
    AuditEntry,
    AuditRegistry,
    CheckpointRegistry,
    ChatEntry,
    ChatHistory,
    MessageEntry,
    MessageRegistry,
    RunRegistry,
    get_last_poll_session_messages_meta,
    poll_session_messages,
)

# Combined exports
__all__ = [
    # State
    "AgentSource",
    "get_last_poll_session_messages_meta",
    "poll_session_messages",
    # Registry
    "AuditEntry",
    "AuditRegistry",
    # Policy
    "Auditor",
    "CalibrationRegistry",
    "ChatEntry",
    "ChatHistory",
    "CheckpointMeta",
    "CheckpointRegistry",
    # Resilience
    "CircuitBreakerRegistry",
    # Concurrency
    "ConcurrencyController",
    "ContinuityPacket",
    "ContinuityWatchdog",
    "DLQManager",
    "DeferralQueue",
    "EscalationQueue",
    "EvidenceLinter",
    "FreshnessValidator",
    "HandoffManager",
    "IdempotencyManager",
    "InteractivityMode",
    "InterruptionTracker",
    "KPIManager",
    "LaneController",
    "LoadClassifier",
    "MAIFArtifact",
    "MessageEntry",
    "MessageRegistry",
    "OverrideRegistry",
    "PolicyEngine",
    "ProviderScorer",
    "ReplayManager",
    "RunMeta",
    "RunRegistry",
    "RunState",
    "TrustBoundaryValidator",
]

# Lazy-load flat module for backward compatibility only
_flat = None

def _get_flat():
    global _flat
    if _flat is None:
        import importlib
        import importlib.util
        import sys
        from pathlib import Path

        _EXECUTION_PY = Path(__file__).parent.parent / "execution.py"
        _MODULE_NAME = "thegent._execution_flat"

        if _MODULE_NAME not in sys.modules:
            _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _EXECUTION_PY)
            if _spec is None or _spec.loader is None:
                raise ImportError(f"Cannot load {_EXECUTION_PY}")
            _mod = importlib.util.module_from_spec(_spec)
            sys.modules[_MODULE_NAME] = _mod
            _spec.loader.exec_module(_mod)

        _flat = sys.modules[_MODULE_NAME]
    return _flat


def __getattr__(name: str) -> Any:
    # Check modular exports first
    modular_exports = {
        "AgentSource": AgentSource,
        "CalibrationRegistry": CalibrationRegistry,
        "CheckpointMeta": CheckpointMeta,
        "ContinuityPacket": ContinuityPacket,
        "InteractivityMode": InteractivityMode,
        "MAIFArtifact": MAIFArtifact,
        "RunMeta": RunMeta,
        "RunState": RunState,
        "CircuitBreakerRegistry": CircuitBreakerRegistry,
        "ConcurrencyController": ConcurrencyController,
        "ContinuityWatchdog": ContinuityWatchdog,
        "DeferralQueue": DeferralQueue,
        "DLQManager": DLQManager,
        "EscalationQueue": EscalationQueue,
        "FreshnessValidator": FreshnessValidator,
        "HandoffManager": HandoffManager,
        "IdempotencyManager": IdempotencyManager,
        "InterruptionTracker": InterruptionTracker,
        "LaneController": LaneController,
        "LoadClassifier": LoadClassifier,
        "Auditor": Auditor,
        "EvidenceLinter": EvidenceLinter,
        "KPIManager": KPIManager,
        "OverrideRegistry": OverrideRegistry,
        "PolicyEngine": PolicyEngine,
        "ProviderScorer": ProviderScorer,
        "TrustBoundaryValidator": TrustBoundaryValidator,
        "AuditEntry": AuditEntry,
        "AuditRegistry": AuditRegistry,
        "CheckpointRegistry": CheckpointRegistry,
        "ChatEntry": ChatEntry,
        "ChatHistory": ChatHistory,
        "MessageEntry": MessageEntry,
        "MessageRegistry": MessageRegistry,
        "RunRegistry": RunRegistry,
        "get_last_poll_session_messages_meta": get_last_poll_session_messages_meta,
        "poll_session_messages": poll_session_messages,
    }
    if name in modular_exports:
        return modular_exports[name]
    # Fall back to flat module (lazy load)
    try:
        return getattr(_get_flat(), name)
    except (AttributeError, ImportError):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
