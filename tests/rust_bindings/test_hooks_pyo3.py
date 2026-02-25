"""Test PyO3 binding for thegent-hooks Rust crate."""

import pytest


def test_thegent_hooks_import():
    try:
        import thegent_hooks  # noqa: F401
    except ImportError as exc:
        pytest.skip(f"thegent_hooks not built: {exc}")


def test_policy_engine_from_rules():
    try:
        from thegent_hooks import PolicyRule, PolicyEngine

        rule = PolicyRule(
            "r1",
            "max-cost",
            "Reject high cost",
            "cost",
            "cost < 10.0",
            "error",
            True,
        )
        engine = PolicyEngine([rule])
        outcomes = engine.evaluate('{"cost": 5.0}')
        assert outcomes[0].passed
    except ImportError as exc:
        pytest.skip(f"thegent_hooks not built: {exc}")


def test_cost_estimate_api():
    try:
        from thegent_hooks import CostCalculator

        calculator = CostCalculator()
        estimate = calculator.calculate("claude-haiku-4.5", 1000, 500)
        assert estimate.total_cost_usd > 0.0
        assert estimate.model == "claude-haiku-4.5"
    except ImportError as exc:
        pytest.skip(f"thegent_hooks not built: {exc}")
