"""WP-40003: Edge-Agent Low-Power Synchronization.
Enables agents running on constrained edge devices (IoT, Mobile) to synchronize state
using delta-compression and adaptive polling to conserve energy.
"""

import json
import logging
import zlib
from typing import Any

_log = logging.getLogger(__name__)


class EdgeSyncController:
    """Manages low-power synchronization between edge agents and the mesh."""

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        self.last_sync_ts = 0.0
        self.base_state = {}

    def compute_delta(self, current_state: dict[str, Any]) -> bytes:
        """WP-40003: Generate a compressed delta between base and current state."""
        _log.info("Computing state delta for edge device: %s", self.device_id)

        # 1. Simple delta (diff keys)
        delta = {k: v for k, v in current_state.items() if self.base_state.get(k) != v}

        # 2. Serialize and Compress
        serialized = json.dumps(delta).encode()
        compressed = zlib.compress(serialized)

        _log.debug("State delta computed. Original: %d bytes, Compressed: %d bytes", len(serialized), len(compressed))
        return compressed

    def apply_remote_delta(self, compressed_delta: bytes):
        """Apply a received delta to the local base state."""
        _log.info("Applying remote delta to edge device...")
        decompressed = zlib.decompress(compressed_delta)
        delta = json.loads(decompressed.decode())

        self.base_state.update(delta)
        _log.info("Edge state synchronized.")

    def get_adaptive_polling_interval(self, battery_level: float) -> int:
        """Adjust sync frequency based on battery (0.0 - 1.0)."""
        if battery_level < 0.2:
            return 3600  # Sync every hour
        if battery_level < 0.5:
            return 600  # Sync every 10 mins
        return 60  # Sync every minute
