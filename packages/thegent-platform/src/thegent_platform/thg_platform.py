"""Platform detection with DI-ready PlatformService.

This module provides:
- Platform enum (MACOS, LINUX, WINDOWS, UNKNOWN)
- PlatformService class: wraps the formerly module-level _platform_cache
  singleton so that platform detection can be injected and overridden.
- detect_platform() module-level helper: retained for backward compatibility;
  delegates to the module-level PlatformService instance.

Phase 2C DI migration
---------------------
Previously, platform detection was either re-computed on every call or
stored in a bare module-level ``_platform_cache`` variable.  The detection
result is now held inside a ``PlatformService`` instance whose internal
``_cache`` replaces the old global.  Callers that need a mockable platform
can inject their own ``PlatformService``; callers that only need the
convenience function can keep using ``detect_platform()`` unchanged.
"""

from __future__ import annotations

import sys
from enum import StrEnum
from typing import TYPE_CHECKING


class Platform(StrEnum):
    """Enumeration of supported host platforms."""

    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


class PlatformService:
    """Injectable service for host-platform detection.

    Wraps the formerly global ``_platform_cache`` so the detection result
    is encapsulated and overridable for testing.

    Attributes:
        _cache: Cached Platform value; None until first detection.
    """

    def __init__(self) -> None:
        self._cache: Platform | None = None

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def detect(self) -> Platform:
        """Detect and cache the current host platform.

        Detection order:
        1. ``sys.platform`` == "darwin"  → MACOS
        2. ``sys.platform`` == "win32"   → WINDOWS
        3. ``sys.platform.startswith("linux")`` → LINUX
        4. Anything else                 → UNKNOWN

        Result is cached after first call; call ``reset()`` to re-detect
        (useful in tests that modify ``sys.platform``).

        Returns:
            Platform enum value for the current host.
        """
        if self._cache is None:
            self._cache = self._do_detect()
        return self._cache

    def reset(self) -> None:
        """Clear the cached platform value, forcing re-detection on next call."""
        self._cache = None

    def override(self, platform: Platform) -> None:
        """Manually set the cached platform value.

        Useful in test fixtures to simulate a different OS without
        modifying ``sys.platform``.

        Args:
            platform: The Platform value to pretend we are running on.
        """
        self._cache = platform

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _do_detect() -> Platform:
        """Perform the actual sys.platform inspection."""
        p = sys.platform
        if p == "darwin":
            return Platform.MACOS
        if p == "win32":
            return Platform.WINDOWS
        if p.startswith("linux"):
            return Platform.LINUX
        return Platform.UNKNOWN


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compat shim
# ---------------------------------------------------------------------------

#: Module-level PlatformService instance.
#: Callers that cannot accept injection may use this directly:
#:   from thegent_platform.thg_platform import _platform_service
#: but prefer passing a PlatformService instance where possible.
_platform_service: PlatformService = PlatformService()


def detect_platform() -> Platform:
    """Return the current host Platform.

    Backward-compatible function; delegates to the module-level
    ``_platform_service``.  For injectable usage, create a
    ``PlatformService`` instance and call ``.detect()`` on it.

    Returns:
        Platform enum for the current OS.
    """
    return _platform_service.detect()


__all__ = [
    "Platform",
    "PlatformService",
    "_platform_service",
    "detect_platform",
]
