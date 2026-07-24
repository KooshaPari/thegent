"""AUDIT-N+55: governance/slo hardening spec (SOTA pass-39).

15 invariants FR-GOV-SLO-001..015 covering SLORegulator init guards,
record_execution validation, is_compliant windowing, reset/metrics
helpers, and canonical ``__all__``.

Source: src/thegent/governance/slo.py

@trace AUDIT-N+55  FR-GOV-SLO-001..015
"""

from __future__ import annotations

import pytest

from thegent.governance import slo as _mod
from thegent.governance.slo import SLORegulator

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# FR-GOV-SLO-001 / FR-GOV-SLO-002 -- init defaults + custom
# ---------------------------------------------------------------------------


class TestSLOInit:
    """FR-GOV-SLO-001/002."""

    def test_default_latency_slo(self) -> None:
        reg = SLORegulator()
        assert reg.latency_slo_ms == 500.0

    def test_default_error_slo(self) -> None:
        reg = SLORegulator()
        assert reg.error_slo_rate == 0.01

    def test_custom_slos(self) -> None:
        reg = SLORegulator(latency_slo_ms=100.0, error_slo_rate=0.05)
        assert reg.latency_slo_ms == 100.0
        assert reg.error_slo_rate == 0.05


# ---------------------------------------------------------------------------
# FR-GOV-SLO-003 / FR-GOV-SLO-004 -- init guards
# ---------------------------------------------------------------------------


class TestSLOInitGuards:
    """FR-GOV-SLO-003/004."""

    def test_rejects_non_positive_latency(self) -> None:
        with pytest.raises(ValueError, match="latency"):
            SLORegulator(latency_slo_ms=0)

    def test_rejects_negative_latency(self) -> None:
        with pytest.raises(ValueError, match="latency"):
            SLORegulator(latency_slo_ms=-1)

    def test_rejects_error_rate_below_zero(self) -> None:
        with pytest.raises(ValueError, match="error"):
            SLORegulator(error_slo_rate=-0.1)

    def test_rejects_error_rate_above_one(self) -> None:
        with pytest.raises(ValueError, match="error"):
            SLORegulator(error_slo_rate=1.5)


# ---------------------------------------------------------------------------
# FR-GOV-SLO-005 / FR-GOV-SLO-006 -- record_execution
# ---------------------------------------------------------------------------


class TestSLORecord:
    """FR-GOV-SLO-005/006."""

    def test_record_appends_metric(self) -> None:
        reg = SLORegulator()
        reg.record_execution(12.0, True)
        assert len(reg.metrics) == 1
        assert reg.metrics[0] == {"latency": 12.0, "success": True}

    def test_rejects_negative_latency(self) -> None:
        reg = SLORegulator()
        with pytest.raises(ValueError, match="latency"):
            reg.record_execution(-1.0, True)


# ---------------------------------------------------------------------------
# FR-GOV-SLO-007 / FR-GOV-SLO-008 / FR-GOV-SLO-009 -- is_compliant
# ---------------------------------------------------------------------------


class TestSLOCompliance:
    """FR-GOV-SLO-007/008/009."""

    def test_empty_metrics_are_compliant(self) -> None:
        assert SLORegulator().is_compliant() is True

    def test_compliant_when_within_slos(self) -> None:
        reg = SLORegulator(latency_slo_ms=100.0, error_slo_rate=0.5)
        reg.record_execution(50.0, True)
        reg.record_execution(60.0, False)
        assert reg.is_compliant() is True

    def test_noncompliant_on_latency(self) -> None:
        reg = SLORegulator(latency_slo_ms=10.0, error_slo_rate=1.0)
        reg.record_execution(50.0, True)
        assert reg.is_compliant() is False

    def test_noncompliant_on_error_rate(self) -> None:
        reg = SLORegulator(latency_slo_ms=1000.0, error_slo_rate=0.1)
        for _ in range(10):
            reg.record_execution(1.0, False)
        assert reg.is_compliant() is False


# ---------------------------------------------------------------------------
# FR-GOV-SLO-010 -- rolling window of 100
# ---------------------------------------------------------------------------


class TestSLOWindow:
    """FR-GOV-SLO-010: compliance considers only the last 100 samples."""

    def test_old_failures_fall_out_of_window(self) -> None:
        reg = SLORegulator(latency_slo_ms=1000.0, error_slo_rate=0.0)
        for _ in range(100):
            reg.record_execution(1.0, False)
        for _ in range(100):
            reg.record_execution(1.0, True)
        assert reg.is_compliant() is True


# ---------------------------------------------------------------------------
# FR-GOV-SLO-011 / FR-GOV-SLO-012 -- reset + metrics copy
# ---------------------------------------------------------------------------


class TestSLOResetAndMetrics:
    """FR-GOV-SLO-011/012."""

    def test_reset_clears_metrics(self) -> None:
        reg = SLORegulator()
        reg.record_execution(1.0, True)
        reg.reset()
        assert reg.metrics == []
        assert reg.is_compliant() is True

    def test_metrics_returns_copy(self) -> None:
        reg = SLORegulator()
        reg.record_execution(1.0, True)
        snap = reg.metrics
        snap.append({"latency": 99.0, "success": False})
        assert len(reg.metrics) == 1


# ---------------------------------------------------------------------------
# FR-GOV-SLO-013 -- sample_count
# ---------------------------------------------------------------------------


class TestSLOSampleCount:
    """FR-GOV-SLO-013."""

    def test_sample_count(self) -> None:
        reg = SLORegulator()
        assert reg.sample_count == 0
        reg.record_execution(1.0, True)
        reg.record_execution(2.0, False)
        assert reg.sample_count == 2


# ---------------------------------------------------------------------------
# FR-GOV-SLO-014 / FR-GOV-SLO-015 -- __all__
# ---------------------------------------------------------------------------


class TestSLOAll:
    """FR-GOV-SLO-014/015."""

    def test_all_exposes_slo_regulator(self) -> None:
        assert "SLORegulator" in _mod.__all__

    def test_module_exports_slo_regulator(self) -> None:
        assert _mod.SLORegulator is SLORegulator
