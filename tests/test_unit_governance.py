"""Unit tests for governance modules (G-GP)."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.execution import PolicyEngine, RunMeta
from thegent.governance.cost import CostAggregator, CostEstimator
from thegent.governance.input_guardrails import (
    GuardrailResult,
    InputGuardrails,
    _guardrails_from_env,
)


class TestCostEstimator:
    """CostEstimator (G-GP-06)."""

    def test_estimate_with_pricing_table(self) -> None:
        """Uses pricing table when model matches."""
        est = CostEstimator()
        cost = est.estimate(model="claude-sonnet-4", tokens_in=1000, tokens_out=500)
        assert cost > 0
        assert cost < 0.1

    def test_estimate_fallback_heuristic(self) -> None:
        """Uses heuristic when model unknown."""
        est = CostEstimator()
        cost = est.estimate(prompt_length=500)
        assert cost >= 0


class TestInputGuardrails:
    """InputGuardrails (G-GP-02)."""

    def test_check_passes_by_default(self) -> None:
        """Empty config passes all."""
        g = InputGuardrails()
        r = g.check(prompt="hello", agent="gemini", cwd="/tmp")
        assert r.passed is True

    def test_check_prompt_length_fails(self) -> None:
        """Exceeding prompt_max_chars fails."""
        g = InputGuardrails(prompt_max_chars=10)
        r = g.check(prompt="x" * 20)
        assert r.passed is False
        assert r.rail_id == "prompt_length"

    def test_check_agent_allowlist_fails(self) -> None:
        """Agent not in allowlist fails."""
        g = InputGuardrails(agent_allowlist=["gemini", "claude"])
        r = g.check(agent="unknown-agent")
        assert r.passed is False
        assert r.rail_id == "agent_allowlist"

    def test_check_agent_allowlist_empty_allows_all(self) -> None:
        """Empty allowlist allows any agent."""
        g = InputGuardrails(agent_allowlist=[])
        r = g.check(agent="anything")
        assert r.passed is True

    def test_check_cwd_restriction_fails(self) -> None:
        """CWD not under allowed prefix fails."""
        g = InputGuardrails(cwd_allowed_prefixes=["/home", "/workspace"])
        r = g.check(cwd="/tmp/other")
        assert r.passed is False
        assert r.rail_id == "cwd_restriction"

    def test_check_cwd_restriction_passes(self, tmp_path: Path) -> None:
        """CWD under prefix passes."""
        allowed = str(tmp_path)
        g = InputGuardrails(cwd_allowed_prefixes=[allowed])
        r = g.check(cwd=tmp_path / "subdir")
        assert r.passed is True

    def test_guardrails_from_env(self) -> None:
        """_guardrails_from_env reads THGENT_PROMPT_MAX_CHARS."""
        with patch.dict(os.environ, {"THGENT_PROMPT_MAX_CHARS": "100"}, clear=False):
            g = _guardrails_from_env()
            assert g.prompt_max_chars == 100


class TestPolicyEngineOPA:
    """G-GP-01: OPA optional client stub."""

    def test_evaluate_without_opa_uses_python_logic(self) -> None:
        """When OPA not configured, PolicyEngine uses Python logic."""
        settings = MagicMock()
        settings.opa_url = ""
        settings.environment = "development"
        settings.trust_score_threshold = 0.8
        engine = PolicyEngine(settings)
        run = RunMeta(agent="gemini", prompt="test", cwd="/tmp", owner="user", lane="standard")
        result, reason = engine.evaluate(run)
        assert result in ("allow", "deny", "warn")
        assert isinstance(reason, str)

    def test_evaluate_with_opa_allow_delegates(self) -> None:
        """When OPA returns allow, PolicyEngine returns allow."""
        settings = MagicMock()
        settings.opa_url = "http://localhost:8181"
        settings.opa_timeout_ms = 500
        settings.opa_fallback_allow = False
        settings.environment = "development"
        settings.trust_score_threshold = 0.8
        engine = PolicyEngine(settings)
        run = RunMeta(agent="gemini", prompt="test", cwd="/tmp", owner="user", lane="standard")

        class MockOPAResponse:
            def read(self):
                return json.dumps({"result": {"allow": True, "reason": "OPA allowed"}}).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def mock_urlopen(req, timeout=None):
            return MockOPAResponse()

        with patch("thegent.execution.urllib.request.urlopen", side_effect=mock_urlopen):
            result, reason = engine.evaluate(run)
        assert result == "allow"
        assert "OPA" in reason or "allowed" in reason

    def test_evaluate_with_opa_deny_delegates(self) -> None:
        """When OPA returns deny, PolicyEngine returns deny."""
        settings = MagicMock()
        settings.opa_url = "http://localhost:8181"
        settings.opa_timeout_ms = 500
        settings.opa_fallback_allow = False
        settings.environment = "development"
        settings.trust_score_threshold = 0.8
        engine = PolicyEngine(settings)
        run = RunMeta(agent="gemini", prompt="test", cwd="/tmp", owner="user", lane="standard")

        class MockOPADenyResponse:
            def read(self):
                return json.dumps({"result": {"allow": False, "reason": "OPA denied"}}).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def mock_urlopen(req, timeout=None):
            return MockOPADenyResponse()

        with patch("thegent.execution.urllib.request.urlopen", side_effect=mock_urlopen):
            result, reason = engine.evaluate(run)
        assert result == "deny"
        assert "OPA" in reason or "denied" in reason

    def test_evaluate_opa_unreachable_fallback_deny(self) -> None:
        """When OPA unreachable and fallback_allow=False, returns deny."""
        settings = MagicMock()
        settings.opa_url = "http://localhost:8181"
        settings.opa_timeout_ms = 500
        settings.opa_fallback_allow = False
        settings.environment = "development"
        settings.trust_score_threshold = 0.8
        engine = PolicyEngine(settings)
        run = RunMeta(agent="gemini", prompt="test", cwd="/tmp", owner="user", lane="standard")

        with patch("thegent.execution.urllib.request.urlopen", side_effect=OSError("connection refused")):
            result, reason = engine.evaluate(run)
        assert result == "deny"
        assert "OPA" in reason or "deny" in reason.lower()

    def test_evaluate_opa_unreachable_fallback_allow(self) -> None:
        """When OPA unreachable and fallback_allow=True, returns allow."""
        settings = MagicMock()
        settings.opa_url = "http://localhost:8181"
        settings.opa_timeout_ms = 500
        settings.opa_fallback_allow = True
        settings.environment = "development"
        settings.trust_score_threshold = 0.8
        engine = PolicyEngine(settings)
        run = RunMeta(agent="gemini", prompt="test", cwd="/tmp", owner="user", lane="standard")

        with patch("thegent.execution.urllib.request.urlopen", side_effect=OSError("connection refused")):
            result, reason = engine.evaluate(run)
        assert result == "allow"
        assert "fallback" in reason.lower()
