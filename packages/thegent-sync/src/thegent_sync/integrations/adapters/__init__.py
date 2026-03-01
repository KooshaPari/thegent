"""Adapters for workstream autosync.

This package contains extracted adapter modules from workstream_autosync.py
to reduce the main file size and improve maintainability.
"""

from thegent_sync.integrations.adapters.checkpoint_adapter import CheckpointAdapter
from thegent_sync.integrations.adapters.connector_config_adapter import ConnectorConfigAdapter
from thegent_sync.integrations.adapters.encryption_adapter import (
    compute_artifact_key,
    xor_decrypt,
    xor_encrypt,
)
from thegent_sync.integrations.adapters.metrics_adapter import MetricsAdapter
from thegent_sync.integrations.adapters.sla_adapter import SLAAdapter
from thegent_sync.integrations.adapters.state_adapter import StateAdapter
from thegent_sync.integrations.adapters.sync_adapter import SyncAdapter

__all__ = [
    "CheckpointAdapter",
    "ConnectorConfigAdapter",
    "MetricsAdapter",
    "SLAAdapter",
    "StateAdapter",
    "SyncAdapter",
    "compute_artifact_key",
    "xor_decrypt",
    "xor_encrypt",
]
