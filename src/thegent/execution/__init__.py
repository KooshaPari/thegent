"""Execution module - organizes execution.py classes by domain.

This module re-exports all classes from execution.py for backward compatibility.
The execution.py file contains 35+ classes spanning multiple domains:

- State & Metadata: RunState, RunMeta, CheckpointMeta, etc.
- Concurrency: ConcurrencyController, IdempotencyManager, LaneController
- Resilience: DLQManager, DeferralQueue, ReplayManager, CircuitBreakerRegistry
- Policy: PolicyEngine, ProviderScorer, TrustBoundaryValidator
- Audit: AuditRegistry, CheckpointRegistry, RunRegistry
- History: ChatHistory, MessageRegistry
- Diagnostics: get_execution_diagnostics, reset_execution_diagnostics

For a full modular refactor, consider splitting into:
- execution/state.py - RunState, RunMeta, CheckpointMeta
- execution/resilience.py - DLQManager, DeferralQueue, CircuitBreakerRegistry
- execution/policy.py - PolicyEngine, ProviderScorer
- execution/audit.py - AuditRegistry, CheckpointRegistry
- execution/history.py - ChatHistory, MessageRegistry
"""

from thegent.execution import (
    # State Enums
    AgentSource,
    InteractivityMode,
    RunState,
    # Metadata Models
    CheckpointMeta,
    ContinuityPacket,
    MAIFArtifact,
    RunMeta,
    # Concurrency
    ConcurrencyController,
    IdempotencyManager,
    LaneController,
    LoadClassifier,
    # Resilience
    CircuitBreakerRegistry,
    DeferralQueue,
    DLQManager,
    EscalationQueue,
    HandoffManager,
    ReplayManager,
    # Tracking
    CalibrationRegistry,
    ContinuityWatchdog,
    FreshnessValidator,
    InterruptionTracker,
    KPIManager,
    # Policy
    EvidenceLinter,
    OverrideRegistry,
    PolicyEngine,
    ProviderScorer,
    TrustBoundaryValidator,
    # History
    AuditEntry,
    AuditRegistry,
    ChatEntry,
    ChatHistory,
    CheckpointRegistry,
    MessageEntry,
    MessageRegistry,
    RunRegistry,
    # Diagnostics
    get_execution_diagnostics,
    reset_execution_diagnostics,
)

__all__ = [
    # State Enums
    "AgentSource",
    "InteractivityMode",
    "RunState",
    # Metadata Models
    "CheckpointMeta",
    "ContinuityPacket",
    "MAIFArtifact",
    "RunMeta",
    # Concurrency
    "ConcurrencyController",
    "IdempotencyManager",
    "LaneController",
    "LoadClassifier",
    # Resilience
    "CircuitBreakerRegistry",
    "DeferralQueue",
    "DLQManager",
    "EscalationQueue",
    "HandoffManager",
    "ReplayManager",
    # Tracking
    "CalibrationRegistry",
    "ContinuityWatchdog",
    "FreshnessValidator",
    "InterruptionTracker",
    "KPIManager",
    # Policy
    "EvidenceLinter",
    "OverrideRegistry",
    "PolicyEngine",
    "ProviderScorer",
    "TrustBoundaryValidator",
    # History
    "AuditEntry",
    "AuditRegistry",
    "ChatEntry",
    "ChatHistory",
    "CheckpointRegistry",
    "MessageEntry",
    "MessageRegistry",
    "RunRegistry",
    # Diagnostics
    "get_execution_diagnostics",
    "reset_execution_diagnostics",
]
