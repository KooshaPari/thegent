"""Tailscale node management for compute offload."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class TailscaleError(Exception):
    """Raised when a Tailscale operation fails."""


@dataclass
class TailscaleNode:
    """Represents a node on the Tailscale network."""

    hostname: str
    ip: str
    os: str
    is_online: bool
    tags: list[str] = field(default_factory=list)


class TailscaleConfig(BaseSettings):
    """Configuration for Tailscale integration.

    Reads from environment variables prefixed with THGENT_TAILSCALE_.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    api_key: str | None = Field(None, alias="THGENT_TAILSCALE_API_KEY")
    tailnet: str = Field("personal", alias="THGENT_TAILSCALE_TAILNET")
    timeout_s: float = 10.0


class TailscaleManager:
    """Manages Tailscale nodes for compute offload.

    Uses the ``tailscale`` CLI binary to discover and interact with nodes
    on the Tailscale network. Falls back to empty results when the binary
    is not installed rather than raising unconditionally, so callers can
    check :meth:`is_available` before proceeding.
    """

    _BINARY = "tailscale"

    def __init__(self, config: TailscaleConfig | None = None) -> None:
        """Initialise the manager.

        Args:
            config: Optional :class:`TailscaleConfig`. If *None*, one is
                constructed from the environment.
        """
        self.config = config or TailscaleConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return *True* if the ``tailscale`` binary is on ``PATH``.

        Returns:
            Whether the Tailscale CLI can be found.
        """
        return shutil.which(self._BINARY) is not None

    def list_nodes(self) -> list[TailscaleNode]:
        """Return all nodes reported by ``tailscale status --json``.

        If the Tailscale binary is not installed the method logs a warning
        and returns an empty list rather than raising.

        Returns:
            Parsed list of :class:`TailscaleNode` objects.

        Raises:
            TailscaleError: If the binary is installed but the command fails
                or its output cannot be parsed.
        """
        if not self.is_available():
            logger.warning("tailscale binary not found; returning empty node list")
            return []

        try:
            result = subprocess.run(
                [self._BINARY, "status", "--json"],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TailscaleError("tailscale status timed out") from exc
        except OSError as exc:
            raise TailscaleError(f"Failed to run tailscale: {exc}") from exc

        if result.returncode != 0:
            raise TailscaleError(f"tailscale status exited with {result.returncode}: {result.stderr.strip()}")

        return self._parse_status(result.stdout)

    def ping_node(self, hostname: str) -> bool:
        """Ping *hostname* via ``tailscale ping``.

        Args:
            hostname: The Tailscale hostname or IP to ping.

        Returns:
            *True* if the ping succeeds, *False* otherwise.

        Raises:
            TailscaleError: If the binary is not available.
        """
        if not self.is_available():
            raise TailscaleError("tailscale binary not found; cannot ping node")

        try:
            result = subprocess.run(
                [self._BINARY, "ping", hostname],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.warning("tailscale ping %s timed out", hostname)
            return False
        except OSError as exc:
            raise TailscaleError(f"Failed to run tailscale ping: {exc}") from exc

        success = result.returncode == 0
        if not success:
            logger.debug("tailscale ping %s failed: %s", hostname, result.stderr.strip())
        return success

    def get_online_nodes(self) -> list[TailscaleNode]:
        """Return only nodes that are currently online.

        Returns:
            Filtered list of :class:`TailscaleNode` objects with
            :attr:`TailscaleNode.is_online` set to *True*.
        """
        return [n for n in self.list_nodes() if n.is_online]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_status(json_output: str) -> list[TailscaleNode]:
        """Parse the JSON output of ``tailscale status --json``.

        Args:
            json_output: Raw stdout from the command.

        Returns:
            List of :class:`TailscaleNode` objects.

        Raises:
            TailscaleError: On JSON decode failure or unexpected schema.
        """
        try:
            data = json.loads(json_output)
        except json.JSONDecodeError as exc:
            raise TailscaleError(f"Could not parse tailscale status output: {exc}") from exc

        if not isinstance(data, dict):
            raise TailscaleError("Unexpected tailscale status schema: root is not an object")

        peers: dict = data.get("Peer", {})
        nodes: list[TailscaleNode] = []

        # The JSON schema from `tailscale status --json`:
        #   "Peer": { "<node_key>": { "HostName": "...", "TailscaleIPs": [...],
        #                              "OS": "...", "Online": true|false,
        #                              "Tags": [...] or null } }
        for peer_key, peer in peers.items():
            if not isinstance(peer, dict):
                logger.debug("Skipping non-dict peer entry %s", peer_key)
                continue

            hostname = peer.get("HostName", peer_key)
            ips: list[str] = peer.get("TailscaleIPs") or []
            ip = ips[0] if ips else ""
            os_name: str = peer.get("OS", "unknown")
            is_online: bool = bool(peer.get("Online", False))
            raw_tags = peer.get("Tags") or []
            tags: list[str] = list(raw_tags) if isinstance(raw_tags, list) else []

            nodes.append(
                TailscaleNode(
                    hostname=hostname,
                    ip=ip,
                    os=os_name,
                    is_online=is_online,
                    tags=tags,
                )
            )

        return nodes
