"""Integrations module for thegent.

This module exports all wired integrations. Unwired implementations are in archive/.
"""

# === Conflict Management ===
from thegent.integrations.conflict_guardrails import (
    ConflictGrowthGuardrail,
    ConflictLimitExceeded,
)
from thegent.integrations.conflict_queue import (
    ConflictEntry,
    ConflictQueue,
    classify_conflict,
)
from thegent.integrations.conflict_ttl import (
    ConflictRecord,
    ConflictTTLManager,
)

# === Connector Management ===
from thegent.integrations.connector_timeout import (
    ConnectorTimeoutConfig,
    ConnectorTimeoutRegistry,
)
from thegent.integrations.connector_sla import (
    ConnectorSLAConfig,
    ConnectorSLARegistry,
)
from thegent.integrations.connector_toggle import (
    ConnectorToggle,
    ToggleState,
)

# === Cache & Storage ===
from thegent.integrations.lmcache import (
    CacheResult,
    LMCacheBackend,
    LMCacheConfig,
    LMCacheError,
    LMCacheStatus,
)
from thegent.integrations.signed_capability_cache import (
    SignedCapabilityCache,
    SignedCapabilityConfig,
)
from thegent.integrations.nats_event_bus import (
    NATSEventBus,
    NATSConfig,
)
from thegent.integrations.graphiti import (
    GraphitiClient,
    GraphitiConfig,
)
from thegent.integrations.cycle_benchmark import (
    CycleBenchmark,
    BenchmarkResult,
)
from thegent.integrations.cycle_manifest import (
    CycleManifest,
    ManifestEntry,
)

# === Drift & Severity ===
from thegent.integrations.drift_severity import (
    DriftEscalationThresholds,
    DriftSeverity,
    classify_drift,
    get_default_thresholds,
)

# === IDE Integrations ===
from thegent.integrations.ghostty import (
    GhosttyConfig,
    GhosttyError,
    GhosttyIntegration,
)
from thegent.integrations.jetbrains import (
    IdeType,
    JetBrainsConfig,
    JetBrainsIntegration,
)

# === Policy ===
from thegent.integrations.reconciliation_policy import (
    ReconciliationMode,
    ReconciliationPolicy,
    create_default_policy,
)

# === Sync & Auditing ===
from thegent.integrations.sync_auditor import (
    SyncAuditor,
    SyncPolicyAudit,
)
from thegent.integrations.sync_provenance import (
    SyncProvenanceStamp,
    extract_provenance,
    get_current_timestamp,
    has_provenance,
    remove_provenance,
    stamp_sync_record,
)

# === Full API ===
__all__ = [
    # Conflict
    "BenchmarkResult",
    "CacheResult",
    "ConflictEntry",
    "ConflictGrowthGuardrail",
    "ConflictLimitExceeded",
    "ConflictQueue",
    "ConflictRecord",
    "ConflictTTLManager",
    "CycleBenchmark",
    "CycleManifest",
    "GraphitiClient",
    "GraphitiConfig",
    "LMCacheBackend",
    "LMCacheConfig",
    "LMCacheError",
    "LMCacheStatus",
    "ManifestEntry",
    "NATSConfig",
    "NATSEventBus",
    "SignedCapabilityCache",
    "SignedCapabilityConfig",
    "ToggleState",
    # Connector
    "ConnectorSLAConfig",
    "ConnectorSLARegistry",
    "ConnectorTimeoutConfig",
    "ConnectorTimeoutRegistry",
    "ConnectorToggle",
    # Drift
    "DriftEscalationThresholds",
    "DriftSeverity",
    "classify_conflict",
    "classify_drift",
    "get_default_thresholds",
    # IDE
    "GhosttyConfig",
    "GhosttyError",
    "GhosttyIntegration",
    "IdeType",
    "JetBrainsConfig",
    "JetBrainsIntegration",
    # Policy
    "ReconciliationMode",
    "ReconciliationPolicy",
    "create_default_policy",
    # Sync
    "SyncAuditor",
    "SyncPolicyAudit",
    "SyncProvenanceStamp",
    "extract_provenance",
    "get_current_timestamp",
    "has_provenance",
    "remove_provenance",
    "stamp_sync_record",
]
