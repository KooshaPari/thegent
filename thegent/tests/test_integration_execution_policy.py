"""Integration tests for execution policy engine with RunRegistry.

Tests PolicyEngine evaluation with RunRegistry calibration,
TrustBoundaryValidator environment transitions, and the full
registration + policy evaluation flow.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from tests.conftest_factories import make_run_meta
from thegent.execution import (
    Auditor,
    PolicyEngine,
    RunRegistry,
    TrustBoundaryValidator,
)


def _make_settings(**overrides: Any) -> SimpleNamespace:
    """Build a minimal settings object for PolicyEngine."""
    defaults = {
        "environment": "development",
        "trust_score_threshold": 0.8,
        "opa_url": "",
        "opa_timeout_ms": 500,
        "opa_fallback_allow": False,
        "session_dir": Path("/tmp/test-session"),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.mark.integration
class TestPolicyEngineWithRegistry:
    """Tests PolicyEngine.evaluate with RunRegistry calibration."""

    def test_calibration_adjusts_confidence_from_registry(
        self,
        tmp_path: Path,
    ) -> None:
        # @trace FR-EXE-008
        """When registry has feedback data, calibration should adjust run confidence."""
        registry = RunRegistry(tmp_path)

        # Register a run with known confidence
        run1 = make_run_meta(agent="claude", confidence=0.9)
        registry.register_start(run1)
        registry.register_end(
            run_id=run1.run_id,
            exit_code=0,
            status="completed",
            ended_at_utc="2025-01-01T00:00:00+00:00",
            duration_s=10.0,
        )
        # Register feedback that is lower than confidence (overconfident)
        registry.register_feedback(run_id=run1.run_id, score=0.6)

        # Now evaluate a new run -- calibration should lower effective confidence
        settings = _make_settings(session_dir=tmp_path)
        engine = PolicyEngine(settings)
        run2 = make_run_meta(agent="claude", confidence=0.95)
        result, _reason = engine.evaluate(run2, registry=registry)

        # The calibration factor should be < 1.0 (0.6/0.9 ~ 0.67)
        # so confidence is lowered but should still allow in dev environment
        assert result == "allow"

    def test_critical_lane_denied_below_confidence_threshold(
        self,
        tmp_path: Path,
    ) -> None:
        # @trace FR-EXE-008
        """Critical lane should be denied when confidence is below 0.9."""
        settings = _make_settings(session_dir=tmp_path)
        engine = PolicyEngine(settings)
        run = make_run_meta(agent="claude")
        run.lane = "critical"
        run.confidence = 0.7

        result, reason = engine.evaluate(run)
        assert result == "deny"
        assert "confidence" in reason.lower()

    def test_critical_lane_allowed_with_high_confidence(
        self,
        tmp_path: Path,
    ) -> None:
        # @trace FR-EXE-008
        """Critical lane with high confidence should be allowed."""
        settings = _make_settings(session_dir=tmp_path)
        engine = PolicyEngine(settings)
        run = make_run_meta(agent="claude")
        run.lane = "critical"
        run.confidence = 0.95

        result, _reason = engine.evaluate(run)
        assert result == "allow"

    def test_production_env_denied_below_trust_threshold(
        self,
        tmp_path: Path,
    ) -> None:
        # @trace FR-EXE-009
        """Production environment should deny runs below trust_score_threshold."""
        settings = _make_settings(environment="production", session_dir=tmp_path)
        engine = PolicyEngine(settings)
        run = make_run_meta(agent="claude")
        run.confidence = 0.5

        result, reason = engine.evaluate(run)
        assert result == "deny"
        assert "trust score" in reason.lower()

    def test_unknown_agent_denied_in_production(self, tmp_path: Path) -> None:
        # @trace FR-EXE-009
        """Unknown agents should be blocked in production environment."""
        settings = _make_settings(environment="production", session_dir=tmp_path)
        engine = PolicyEngine(settings)
        run = make_run_meta(agent="unknown")
        run.confidence = 0.99

        result, reason = engine.evaluate(run)
        assert result == "deny"
        assert "unknown" in reason.lower()


@pytest.mark.integration
class TestTrustBoundaryValidatorTransitions:
    """Tests TrustBoundaryValidator with real environment state transitions."""

    def test_valid_promotion_dev_to_staging(self, tmp_path: Path) -> None:
        # @trace FR-EXE-009
        """dev -> staging is a valid single-level promotion."""
        validator = TrustBoundaryValidator(tmp_path)
        validator.record_environment("development")

        last_env = validator.get_last_environment()
        assert last_env == "development"

        allowed, reason = validator.validate_transition("development", "staging")
        assert allowed is True
        assert "Valid promotion" in reason

    def test_skip_level_promotion_denied(self, tmp_path: Path) -> None:
        # @trace FR-EXE-009
        """dev -> production (skip staging) should be denied."""
        validator = TrustBoundaryValidator(tmp_path)
        validator.record_environment("development")

        allowed, reason = validator.validate_transition("development", "production")
        assert allowed is False
        assert "Skip-level" in reason

    def test_full_promotion_chain(self, tmp_path: Path) -> None:
        # @trace FR-EXE-009
        """dev -> staging -> production should succeed step by step."""
        validator = TrustBoundaryValidator(tmp_path)

        validator.record_environment("development")
        allowed1, _ = validator.validate_transition("development", "staging")
        assert allowed1 is True

        validator.record_environment("staging")
        last = validator.get_last_environment()
        assert last == "staging"

        allowed2, _ = validator.validate_transition("staging", "production")
        assert allowed2 is True


@pytest.mark.integration
class TestRegistrationPolicyFlow:
    """Tests the full register -> evaluate -> record-end flow."""

    def test_register_evaluate_and_complete(self, tmp_path: Path) -> None:
        # @trace FR-EXE-008
        """Full lifecycle: register start, evaluate policy, register end."""
        registry = RunRegistry(tmp_path)
        settings = _make_settings(session_dir=tmp_path)
        engine = PolicyEngine(settings)

        run = make_run_meta(agent="claude")
        run.confidence = 0.85

        # 1. Register start
        registry.register_start(run)

        # 2. Evaluate policy
        result, _reason = engine.evaluate(run, registry=registry)
        assert result == "allow"

        # 3. Register end
        registry.register_end(
            run_id=run.run_id,
            exit_code=0,
            status="completed",
            ended_at_utc="2025-01-01T00:01:00+00:00",
            duration_s=60.0,
            cost_usd=0.05,
        )

        # 4. Verify run is persisted and retrievable
        runs = registry.list_runs()
        assert len(runs) >= 1
        assert any(r["run_id"] == run.run_id for r in runs)

    def test_registry_hash_chain_integrity(self, tmp_path: Path) -> None:
        # @trace FR-EXE-009
        """Multiple records should form a valid hash chain verified by Auditor."""
        registry = RunRegistry(tmp_path)

        run1 = make_run_meta(agent="claude")
        registry.register_start(run1)
        registry.register_end(
            run_id=run1.run_id,
            exit_code=0,
            status="completed",
            ended_at_utc="2025-01-01T00:01:00+00:00",
            duration_s=30.0,
        )

        run2 = make_run_meta(agent="gemini")
        registry.register_start(run2)
        registry.register_end(
            run_id=run2.run_id,
            exit_code=0,
            status="completed",
            ended_at_utc="2025-01-01T00:02:00+00:00",
            duration_s=45.0,
        )

        auditor = Auditor(registry.registry_path)
        report = auditor.verify_registry()

        assert report["status"] == "passed"
        assert report["corrupt_count"] == 0
        assert report["chain_broken"] is False
