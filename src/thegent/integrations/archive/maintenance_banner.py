"""Maintenance banner propagation system.

Manages maintenance mode banners for CLI output and report artifacts.

FR traceability: WL-229 (Maintenance Banner Propagation)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MaintenanceBanner:
    """Represents a maintenance mode banner.

    # @trace WL-229
    """

    message: str
    """The maintenance mode message to display."""

    active: bool = False
    """Whether the banner is currently active."""

    severity: str = "info"
    """Severity level: 'info', 'warning', or 'critical'."""


class MaintenanceBannerPropagator:
    """Manages maintenance mode banners for propagation to CLI and artifacts.

    # @trace WL-229
    """

    def __init__(self) -> None:
        """Initialize the propagator with no active banner."""
        self._banner: MaintenanceBanner | None = None

    def set_banner(self, message: str, severity: str = "info") -> MaintenanceBanner:
        """Set or update the maintenance banner message.

        Args:
            message: The banner message to display.
            severity: Severity level ('info', 'warning', 'critical'). Defaults to 'info'.

        Returns:
            The created/updated MaintenanceBanner.

        Raises:
            ValueError: If severity is not a valid level.
        """
        valid_severities = {"info", "warning", "critical"}
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}. Must be one of {valid_severities}")

        self._banner = MaintenanceBanner(message=message, active=False, severity=severity)
        logger.debug(f"Set maintenance banner (severity={severity}): {message}")
        return self._banner

    def activate(self) -> None:
        """Activate the current maintenance banner.

        Raises:
            RuntimeError: If no banner has been set yet.
        """
        if self._banner is None:
            raise RuntimeError("No banner has been set. Call set_banner() first.")

        self._banner.active = True
        logger.info(f"Activated maintenance banner (severity={self._banner.severity})")

    def deactivate(self) -> None:
        """Deactivate the current maintenance banner.

        Raises:
            RuntimeError: If no banner has been set yet.
        """
        if self._banner is None:
            raise RuntimeError("No banner has been set. Call set_banner() first.")

        self._banner.active = False
        logger.info("Deactivated maintenance banner")

    def is_active(self) -> bool:
        """Check if a maintenance banner is currently active.

        Returns:
            True if a banner is set and active, False otherwise.
        """
        return self._banner is not None and self._banner.active

    def current(self) -> MaintenanceBanner | None:
        """Get the current maintenance banner.

        Returns:
            The current MaintenanceBanner, or None if not set.
        """
        return self._banner
