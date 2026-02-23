"""IDE and tool integrations for thegent."""

# Auth and quota modules migrated to CLIProxy (Go)
from thegent.integrations.alert_routing import (
    AlertRoutingConfig,
    route_alert,
)
from thegent.integrations.artifact_redaction import (
    redact_artifact,
    RedactionConfig,
)
from thegent.integrations.artifact_versioning import (
    ArtifactVersion,
    get_artifact_version,
    version_artifact,
)
from thegent.integrations.autopilot_doctor import (
    AutopilotDoctorConfig,
    run_autopilot_diagnosis,
)
from thegent.integrations.compliance_snapshot import (
    ComplianceSnapshot,
    take_compliance_snapshot,
)
from thegent.integrations.board_id_migration import (
    migrate_board_ids,
    BoardIdMigrationConfig,
)
from thegent.integrations.auth_expiry import (
    AuthExpiryConfig,
    check_auth_expiry,
    is_auth_valid,
)
from thegent.integrations.beads import (
    BeadsConfig,
    get_beads_client,
)
from thegent.integrations.chunkhound import (
    ChunkHoundConfig,
    get_chunkhound_client,
)
from thegent.integrations.context7 import (
    Context7Config,
    Context7Provider,
    get_context7_provider,
)
from thegent.integrations.cognee import (
    CogneeConfig,
    get_cognee_client,
)
from thegent.integrations.cycle_metrics import (
    CycleMetrics,
    get_cycle_metrics,
)
from thegent.integrations.connector_capability_discovery import (
    ConnectorCapability,
    discover_connector_capabilities,
)
from thegent.integrations.connector_chaos import (
    ChaosConfig,
    inject_chaos,
)
from thegent.integrations.connector_circuit_breaker import (
    CircuitBreakerConfig,
    get_circuit_breaker,
)
from thegent.integrations.connector_cost_accounting import (
    CostAccountingConfig,
    track_connector_cost,
)
from thegent.integrations.connector_quota import (
    ConnectorQuota,
    check_quota,
)
from thegent.integrations.connector_sandbox import (
    SandboxConfig,
    get_sandbox,
)
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

__all__ = [
    # Alert Routing
    "AlertRoutingConfig",
    "route_alert",
    # Artifact Redaction
    "redact_artifact",
    "RedactionConfig",
    # Artifact Versioning
    "ArtifactVersion",
    "get_artifact_version",
    "version_artifact",
    # Autopilot Doctor
    "AutopilotDoctorConfig",
    "run_autopilot_diagnosis",
    # Board ID Migration
    "migrate_board_ids",
    "BoardIdMigrationConfig",
    # Compliance Snapshot
    "ComplianceSnapshot",
    "take_compliance_snapshot",
    # Auth & Expiry
    "AuthExpiryConfig",
    "check_auth_expiry",
    "is_auth_valid",
    # Beads
    "BedsConfig",
    "get_beads_client",
    # ChunkHound
    "ChunkHoundConfig",
    "get_chunkhound_client",
    # Context7
    "Context7Config",
    "Context7Provider",
    "get_context7_provider",
    # Cognee
    "CogneeConfig",
    "get_cognee_client",
    # Cycle Metrics
    "CycleMetrics",
    "get_cycle_metrics",
    # Connector Capability Discovery
    "ConnectorCapability",
    "discover_connector_capabilities",
    # Connector Chaos
    "ChaosConfig",
    "inject_chaos",
    # Connector Circuit Breaker
    "CircuitBreakerConfig",
    "get_circuit_breaker",
    # Connector Cost Accounting
    "CostAccountingConfig",
    "track_connector_cost",
    # Connector Quota
    "ConnectorQuota",
    "check_quota",
    # Connector Sandbox
    "SandboxConfig",
    "get_sandbox",
    # Drift
    "DriftEscalationThresholds",
    "DriftSeverity",
    "classify_drift",
    "get_default_thresholds",
    # Ghostty
    "GhosttyConfig",
    "GhosttyError",
    "GhosttyIntegration",
    # JetBrains
    "IdeType",
    "JetBrainsConfig",
    "JetBrainsIntegration",
    # Reconciliation
    "ReconciliationMode",
    "ReconciliationPolicy",
    "create_default_policy",
    # Sync Auditor
    "SyncAuditor",
    "SyncPolicyAudit",
    # Sync Provenance
    "SyncProvenanceStamp",
    "extract_provenance",
    "get_current_timestamp",
    "has_provenance",
    "remove_provenance",
    "stamp_sync_record",
]
