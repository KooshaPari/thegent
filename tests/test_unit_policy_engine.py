"""Unit tests for the governance-layer PolicyEngine (WP-3001, WP-3003, OPT-008)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from thegent.config.settings import ThegentSettings
from thegent.governance.policy_engine import (
    PolicyContext,
    PolicyDecision,
    PolicyEngine,
    ReasonCode,
    Verdict,
    evaluate_pre_check,
)


# All tests in this module are unit tests.
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def settings(tmp_path: Path) -> ThegentSettings:
    """Override-managed settings with isolated session/override dirs."""
    return ThegentSettings(environment="development", session_dir=tmp_path)


@pytest.fixture
def engine(settings: ThegentSettings) -> PolicyEngine:
    return PolicyEngine(settings=settings, use_federation=False)


@pytest.fixture
def federated_engine(settings: ThegentSettings) -> PolicyEngine:
    return PolicyEngine(settings=settings, use_federation=True)


# ---------------------------------------------------------------------------
# Sanity / dataclass shape
# ---------------------------------------------------------------------------


class TestSanity:
    """Imported names and basic dataclass structure are correct."""

    def test_public_api(self) -> None:
        """Module exports the documented public surface."""
        # All major symbols are accessible and non-None.
        assert Verdict.ALLOW.value == "allow"
        assert Verdict.DENY.value == "deny"
        assert Verdict.WARN.value == "warn"
        assert ReasonCode.OVERRIDE_ACTIVE.value == "override_active"
        assert ReasonCode.CRITICAL_LANE_LOW_CONFIDENCE.value == "critical_lane_low_confidence"
        assert ReasonCode.TRUST_BOUNDARY_VIOLATION.value == "trust_boundary_violation"
        assert ReasonCode.FEDERATED_POLICY_BLOCK.value == "federated_policy_block"

    def test_policy_context_frozen(self) -> None:
        """PolicyContext is frozen — mutating fields raises."""
        ctx = PolicyContext(agent="cursor", environment="production")
        with pytest.raises(Exception):
            ctx.agent = "gemini"  # type: ignore[misc]

    def test_policy_decision_admissibility(self) -> None:
        d = PolicyDecision(
            verdict=Verdict.ALLOW,
            reason="ok",
            reason_code=ReasonCode.ALLOWED,
        )
        assert d.is_admissible() is True
        d2 = d.to_dict()
        assert d2["verdict"] == "allow"
        assert d2["reason_code"] == "allowed"

    def test_denied_decision_not_admissible(self) -> None:
        d = PolicyDecision(
            verdict=Verdict.DENY,
            reason="no",
            reason_code=ReasonCode.UNKNOWN_AGENT_CRITICAL,
        )
        assert d.is_admissible() is False


# ---------------------------------------------------------------------------
# Default and local-rule behaviour
# ---------------------------------------------------------------------------


class TestLocalRules:
    """WP-3001: local default policy mirrors execution-layer checks (FR-003)."""

    def test_default_allows_when_no_rules_fire(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="cursor", environment="development", confidence=0.95))
        assert d.verdict == Verdict.ALLOW
        assert d.reason_code == ReasonCode.ALLOWED

    def test_critical_lane_low_confidence_denied(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="cursor", lane="critical", confidence=0.5))
        assert d.verdict == Verdict.DENY
        assert d.reason_code == ReasonCode.CRITICAL_LANE_LOW_CONFIDENCE
        assert d.rule_id == "local.critical.confidence"

    def test_unknown_agent_in_critical_denied(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="unknown", lane="critical", confidence=0.99))
        assert d.verdict == Verdict.DENY
        assert d.reason_code == ReasonCode.UNKNOWN_AGENT_CRITICAL
        assert d.rule_id == "local.critical.unknown_agent"

    def test_recovery_lane_no_confidence_warns(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="cursor", lane="recovery", confidence=None))
        assert d.verdict == Verdict.WARN
        assert d.reason_code == ReasonCode.RECOVERY_NO_CONFIDENCE

    def test_production_low_confidence_denied(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="cursor", environment="production", confidence=0.1))
        assert d.verdict == Verdict.DENY
        assert d.reason_code == ReasonCode.CRITICAL_LANE_LOW_CONFIDENCE

    def test_unknown_agent_in_production_denied(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(PolicyContext(agent="unknown", environment="production", confidence=0.95))
        assert d.verdict == Verdict.DENY
        assert d.reason_code == ReasonCode.UNKNOWN_AGENT_PRODUCTION


# ---------------------------------------------------------------------------
# Trust boundary
# ---------------------------------------------------------------------------


class TestTrustBoundary:
    """Sensitive-keyword prompts must not flow to EXTERNAL agents."""

    def test_sensitive_prompt_to_external_agent_denied(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(
            PolicyContext(
                agent="gemini",
                environment="production",
                prompt="here is my api_key=sk-abc12345",
                confidence=0.9,
            )
        )
        assert d.verdict == Verdict.DENY
        assert d.reason_code == ReasonCode.TRUST_BOUNDARY_VIOLATION
        assert d.rule_id == "trust.boundary"

    def test_safe_prompt_to_internal_agent_allowed(self, engine: PolicyEngine) -> None:
        d = engine.evaluate(
            PolicyContext(
                agent="cursor",
                environment="production",
                prompt="hello world",
                confidence=0.9,
            )
        )
        assert d.verdict == Verdict.ALLOW


# ---------------------------------------------------------------------------
# Federated rule + override path (WP-3003)
# ---------------------------------------------------------------------------


class TestFederatedAndOverride:
    """Federated scope rules and override path combine correctly."""

    def test_federated_rule_deny_with_metadata_match(self, federated_engine: PolicyEngine) -> None:
        federated_engine.register_rule(
            rule_id="no-cursor-prod",
            when={"agent": "cursor", "environment": "production"},
            verdict="deny",
            reason="r1",
            priority=10,
        )
        d = federated_engine.evaluate(PolicyContext(agent="cursor", environment="production", confidence=0.95))
        assert d.verdict == Verdict.DENY
        assert d.rule_id == "no-cursor-prod"
        assert d.reason_code == ReasonCode.FEDERATED_POLICY_BLOCK

    def test_federated_rule_does_not_match_other_env(self, federated_engine: PolicyEngine) -> None:
        federated_engine.register_rule(
            rule_id="no-cursor-prod",
            when={"agent": "cursor", "environment": "production"},
            verdict="deny",
            reason="r1",
        )
        d = federated_engine.evaluate(PolicyContext(agent="cursor", environment="development", confidence=0.95))
        assert d.verdict == Verdict.ALLOW

    def test_override_flips_deny_to_allow(self, federated_engine: PolicyEngine) -> None:
        federated_engine.register_rule(
            rule_id="no-cursor-prod",
            when={"agent": "cursor", "environment": "production"},
            verdict="deny",
            reason="r1",
        )
        federated_engine.register_override(
            "no-cursor-prod",
            reason="hotfix approval",
            by="sre-team",
            duration_minutes=2,
        )
        d = federated_engine.evaluate(PolicyContext(agent="cursor", environment="production", confidence=0.95))
        assert d.verdict == Verdict.ALLOW
        assert d.reason_code == ReasonCode.OVERRIDE_ACTIVE
        assert d.override_applied is True

    def test_register_rule_ignored_when_federation_off(self, engine: PolicyEngine) -> None:
        # No exception: rule registration is silently ignored.
        engine.register_rule(
            rule_id="noop",
            when={"agent": "cursor"},
            verdict="deny",
            reason="r",
        )
        d = engine.evaluate(PolicyContext(agent="cursor", environment="production"))
        assert d.verdict == Verdict.ALLOW  # federation disabled, not active

    def test_load_rules_from_file_no_federation(self, engine: PolicyEngine) -> None:
        """Loading rules does nothing when federation is disabled."""
        count = engine.load_rules_from_file(Path("/nonexistent.json"))
        assert count == 0


# ---------------------------------------------------------------------------
# OPT-008 decision cache
# ---------------------------------------------------------------------------


class TestDecisionCache:
    """OPT-008: repeated evaluations are sub-50ms via TTLCache."""

    def test_cache_returns_fresh_instance_with_cached_flag(self, federated_engine: PolicyEngine) -> None:
        federated_engine.register_rule(
            rule_id="c1",
            when={"agent": "cursor", "environment": "production"},
            verdict="allow",
            reason="ok",
        )
        ctx = PolicyContext(agent="cursor", environment="production", confidence=0.95)
        d1 = federated_engine.evaluate(ctx)
        d2 = federated_engine.evaluate(ctx)
        assert d1.cached is False
        assert d2.cached is True
        assert federated_engine.cache_size() >= 1
        # returns a fresh dataclass instance (no aliasing).
        assert d1 is not d2
        d1d = d1.to_dict()
        d2d = d2.to_dict()
        # All fields equal except ``cached`` which flips True on the cached hit.
        for k in d1d:
            if k == "cached":
                assert d1d[k] is False and d2d[k] is True
            else:
                assert d1d[k] == d2d[k], f"{k}: {d1d[k]} vs {d2d[k]}"

    def test_invalidate_cache_clears(self, federated_engine: PolicyEngine) -> None:
        federated_engine.register_rule(
            rule_id="c1",
            when={"agent": "cursor"},
            verdict="allow",
            reason="ok",
        )
        federated_engine.evaluate(PolicyContext(agent="cursor"))
        assert federated_engine.cache_size() >= 1
        federated_engine.invalidate_cache()
        assert federated_engine.cache_size() == 0


# ---------------------------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------------------------


class TestHelper:
    """evaluate_pre_check is a thin wrapper around PolicyEngine.evaluate."""

    def test_helper_default_returns_allow(self) -> None:
        d = evaluate_pre_check(agent="cursor", environment="development", confidence=0.9)
        assert d.verdict == Verdict.ALLOW

    def test_helper_returns_object(self) -> None:
        d = evaluate_pre_check(agent="cursor", environment="production", confidence=0.95)
        assert isinstance(d, PolicyDecision)
        assert d.verdict in (Verdict.ALLOW, Verdict.DENY, Verdict.WARN)
