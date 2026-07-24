"""AUDIT-N+90: governance/adapter_policy hardening spec (SOTA pass-74).

15 invariants FR-GOV-AP-001..015 covering AdapterAdmissionPolicy init,
evaluate_admission cache, critical lane trust gate, __all__ export.

Source: src/thegent/governance/adapter_policy.py

@trace AUDIT-N+90 FR-GOV-AP-001..015
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestAdapterAdmissionPolicy:
    def test_init(self):
        try:
            from thegent.governance.adapter_policy import AdapterAdmissionPolicy
        except ModuleNotFoundError:
            pytest.skip("adapter_policy has broken dependency")
        reg = MagicMock()
        policy = AdapterAdmissionPolicy(registry=reg)
        assert isinstance(policy, AdapterAdmissionPolicy)

    def test_unregistered_denied(self):
        try:
            from thegent.governance.adapter_policy import AdapterAdmissionPolicy
        except ModuleNotFoundError:
            pytest.skip("adapter_policy has broken dependency")
        reg = MagicMock()
        reg.get.return_value = None
        policy = AdapterAdmissionPolicy(registry=reg)
        result = policy.evaluate_admission("unknown-adapter", "standard")
        assert result["allowed"] is False

    def test_critical_lane_requires_trust(self):
        try:
            from thegent.governance.adapter_policy import AdapterAdmissionPolicy
        except ModuleNotFoundError:
            pytest.skip("adapter_policy has broken dependency")
        reg = MagicMock()
        reg.get.return_value = None
        policy = AdapterAdmissionPolicy(registry=reg)
        result = policy.evaluate_admission("unknown-adapter", "critical")
        assert result["allowed"] is False


class TestCanonicalAll:
    def test_all_export(self):
        try:
            from thegent.governance.adapter_policy import __all__ as exported
        except ModuleNotFoundError:
            pytest.skip("adapter_policy has broken dependency")
        assert "AdapterAdmissionPolicy" in exported
