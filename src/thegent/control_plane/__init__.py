"""L20 hardening: control_plane package re-exporting the canonical CP provider.

The canonical import path for ``ControlPlaneConfigProvider`` is
``thegent.control_plane.client``. This package marker ensures that path
resolves, while the implementation lives at
``thegent.governance.config_provider_cp``.
"""

from __future__ import annotations

from thegent.control_plane.client import ControlPlaneConfigProvider

__all__ = ["ControlPlaneConfigProvider"]
