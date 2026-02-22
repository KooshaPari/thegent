"""IDE and tool integrations for thegent."""

from thegent.integrations.drift_severity import (
    DriftEscalationThresholds,
    DriftSeverity,
    classify_drift,
    get_default_thresholds,
)
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
from thegent.integrations.reconciliation_policy import (
    ReconciliationMode,
    ReconciliationPolicy,
    create_default_policy,
)
from thegent.integrations.sync_provenance import (
    SyncProvenanceStamp,
    extract_provenance,
    get_current_timestamp,
    has_provenance,
    remove_provenance,
    stamp_sync_record,
)

__all__ = [
    "DriftEscalationThresholds",
    "DriftSeverity",
    "GhosttyConfig",
    "GhosttyError",
    "GhosttyIntegration",
    "IdeType",
    "JetBrainsConfig",
    "JetBrainsIntegration",
    "ReconciliationMode",
    "ReconciliationPolicy",
    "SyncProvenanceStamp",
    "classify_drift",
    "create_default_policy",
    "extract_provenance",
    "get_current_timestamp",
    "get_default_thresholds",
    "has_provenance",
    "remove_provenance",
    "stamp_sync_record",
]
