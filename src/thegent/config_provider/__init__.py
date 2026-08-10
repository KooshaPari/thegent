"""Legacy import path for ``thegent.config_provider``.

The canonical implementation lives at
``thegent.governance.config_provider`` (and ``thegent.governance.config_provider_cp``).
This module re-exports the public surface so older imports — e.g.
``from thegent.config_provider import get_config_provider`` — continue to work
while pointing at the canonical, fully-tested implementation.

The previous stub here was incomplete (missing ``import os``, lacked
``provider_metadata`` contract, missing ``_attach_provider_metadata`` helper)
and caused ``NameError`` on every ``resolve()`` call. See
``tests/test_unit_config_provider.py`` for the contract this module now
satisfies.

# @trace AUDIT-N+86
"""

from __future__ import annotations

from thegent.governance.config_provider import (
    ConfigProvider,
    EnvConfigProvider,
    _attach_provider_metadata,
    get_config_provider,
    get_last_provider_metadata,
)
from thegent.governance.config_provider_cp import ControlPlaneConfigProvider

__all__ = [
    "ConfigProvider",
    "ControlPlaneConfigProvider",
    "EnvConfigProvider",
    "get_config_provider",
    "get_last_provider_metadata",
    "_attach_provider_metadata",
]
