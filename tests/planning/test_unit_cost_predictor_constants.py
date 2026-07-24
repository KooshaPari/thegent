"""Regression coverage for cost predictor class constants."""

from typing import ClassVar, get_type_hints

from thegent.planning.cost_predictor import CostPredictor


def test_cost_tables_are_class_constants_and_instance_shadowing_is_isolated() -> None:
    """AUDIT-LANE-RUFF-PRESERVATION-001: preserve class-level cost tables."""
    model_costs = CostPredictor._MODEL_COSTS
    action_multipliers = CostPredictor._ACTION_MULTIPLIERS

    assert isinstance(model_costs, dict)
    assert set(model_costs) == {
        "claude-sonnet-4.5",
        "gpt-4o-mini",
        "gemini-3-flash",
        "claude-haiku-4",
        "default",
    }
    assert isinstance(action_multipliers, dict)
    assert set(action_multipliers) == {"learning", "inference", "default"}

    annotations = get_type_hints(CostPredictor)
    assert annotations["_MODEL_COSTS"] == ClassVar[dict[str, float]]
    assert annotations["_ACTION_MULTIPLIERS"] == ClassVar[dict[str, float]]

    predictor = CostPredictor()
    predictor._MODEL_COSTS = {"instance-only": 0.0}
    predictor._ACTION_MULTIPLIERS = {"instance-only": 0.0}

    assert CostPredictor._MODEL_COSTS is model_costs
    assert CostPredictor._ACTION_MULTIPLIERS is action_multipliers
