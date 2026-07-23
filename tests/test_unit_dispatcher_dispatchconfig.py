"""Regression test: ``DispatchConfig`` must be importable from
``thegent.orchestration.dispatcher``.

AUDIT-LANE-DISPATCHCONFIG-001 — fixes the pre-existing
``ImportError: cannot import name 'DispatchConfig'`` that blocks
pytest collection of ``tests/test_wl681x_lane_d.py``.

@trace AUDIT-N+39
@trace AUDIT-LANE-DISPATCHCONFIG-001
"""

from __future__ import annotations

from thegent.orchestration.dispatcher import DispatchConfig


def test_dispatch_config_is_importable() -> None:
    """The ``DispatchConfig`` symbol must resolve from the dispatcher package."""
    assert DispatchConfig is not None


def test_dispatch_config_hitl_enabled_default_is_false() -> None:
    """``DispatchConfig()`` defaults to ``hitl_enabled=False``."""
    cfg = DispatchConfig()
    assert cfg.hitl_enabled is False


def test_dispatch_config_hitl_enabled_true() -> None:
    """``DispatchConfig(hitl_enabled=True)`` round-trips the boolean."""
    cfg = DispatchConfig(hitl_enabled=True)
    assert cfg.hitl_enabled is True
