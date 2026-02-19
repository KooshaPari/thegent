"""WP-43001: Relativistic Clock Sync Protocol.
Simulates clock synchronization across agents located in different gravitational wells or moving
at high relative velocities. Adjusts for time dilation using Lorentz transformations.
"""

import logging
import math
from dataclasses import dataclass

_log = logging.getLogger(__name__)


@dataclass
class RelativisticNode:
    """A node in the relativistic network."""

    node_id: str
    velocity_c: float = 0.0  # Velocity as fraction of light speed (0.0 - 1.0)
    gravity_potential: float = 1.0  # Gravity relative to Earth (1.0)


class RelativisticClockSync:
    """Manages time dilation compensation for interstellar agent coordination."""

    def __init__(self, base_node: RelativisticNode) -> None:
        self.base = base_node
        self.peers: dict[str, RelativisticNode] = {}

    def calculate_dilation_factor(self, peer_id: str) -> float:
        """WP-43001: Calculate the time dilation factor (Gamma) for a peer."""
        peer = self.peers.get(peer_id)
        if not peer:
            return 1.0

        # 1. Kinematic Dilation (Lorentz Factor)
        # gamma = 1 / sqrt(1 - v^2/c^2)
        relative_v = abs(self.base.velocity_c - peer.velocity_c)
        gamma = 1.0 / math.sqrt(1.0 - (relative_v**2) + 1e-15)  # Avoid div by zero

        # 2. Gravitational Dilation (Simplified)
        # t_0 = t_f * sqrt(1 - 2GM/rc^2) -> mapped to relative gravity potential
        gravity_factor = math.sqrt(peer.gravity_potential / self.base.gravity_potential)

        dilation_factor = gamma * gravity_factor
        _log.info(
            "Dilation factor for %s: %.6f (Gamma: %.6f, Gravity: %.6f)", peer_id, dilation_factor, gamma, gravity_factor
        )
        return dilation_factor

    def sync_timestamp(self, peer_id: str, remote_ts: float) -> float:
        """Convert a remote timestamp to the local base node's time frame."""
        factor = self.calculate_dilation_factor(peer_id)
        # Adjusted time = Base Start + (Delta * Factor)
        # This is a simulation of the reconciliation logic.
        return remote_ts * factor

    def add_peer(self, node: RelativisticNode):
        """Register a peer with its physical parameters."""
        self.peers[node.node_id] = node
        _log.info(
            "Relativistic peer registered: %s (v=%.2fc, g=%.2f)", node.node_id, node.velocity_c, node.gravity_potential
        )
