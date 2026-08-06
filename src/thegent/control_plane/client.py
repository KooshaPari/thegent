"""Canonical ``ControlPlaneConfigProvider`` import path.

Production code uses ``thegent.control_plane.client``; the implementation
historically lived at ``thegent.governance.config_provider_cp``. This module
re-exports the class so the canonical import path points at the same class
whether the legacy governance path or the canonical control-plane path is
taken.

# @trace AUDIT-N+83
"""

from __future__ import annotations

from thegent.governance.config_provider_cp import ControlPlaneConfigProvider

__all__ = ["ControlPlaneConfigProvider"]
