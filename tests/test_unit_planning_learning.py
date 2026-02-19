"""Unit tests for Phase 14: Autonomous Learning and Cost Sensing."""

from thegent.planning.learning import LearningRegistry
from thegent.planning.selector import ObjectiveSelector, get_objective_profile
from thegent.planning.tuning import RunbookTuner


def test_wp_14001_objective_selector():
    """WP-14001: Selector should pick best model based on weights."""
    selector = ObjectiveSelector(get_objective_profile("cheapest"))
    # Candidate models from models_meta.py
    best = selector.select_best_model(["claude-opus-4.6", "gemini-2.0-flash"])
    assert best == "gemini-2.0-flash"

    selector_best = ObjectiveSelector(get_objective_profile("best"))
    best_high_qual = selector_best.select_best_model(["claude-opus-4.6", "gemini-2.0-flash"])
    assert best_high_qual == "claude-opus-4.6"


def test_wp_14002_learning_registry(tmp_path):
    """WP-14002: Registry tracks canary performance."""
    registry_path = tmp_path / "learning.json"
    mgr = LearningRegistry(registry_path)

    mgr.add_canary("test-model")
    mgr.record_outcome("test-model", success=True, latency_ms=500, cost_usd=0.01)

    models = mgr.list_models()
    assert len(models) == 1
    assert models[0].id == "test-model"
    assert models[0].metrics.success_count == 1
    assert models[0].metrics.success_rate == 1.0


def test_wp_14003_promotion_flow(tmp_path):
    """WP-14003: Promotion requires candidate status and approval."""
    registry_path = tmp_path / "learning.json"
    mgr = LearningRegistry(registry_path)

    mgr.add_canary("candidate-model")
    # Not enough runs for candidate status
    assert mgr.promote_to_candidate("candidate-model") is False

    # Simulate 50 successful runs
    for _ in range(50):
        mgr.record_outcome("candidate-model", success=True, latency_ms=100, cost_usd=0.001)

    assert mgr.promote_to_candidate("candidate-model") is True
    assert mgr.finalize_promotion("candidate-model", approver="admin-1") is True

    models = mgr.list_models()
    assert models[0].status == "promoted"
    assert models[0].approved_by == "admin-1"


def test_wp_14004_runbook_tuning():
    """WP-14004: Tuner generates recommendations based on breaches."""
    # Latency breach case
    metrics = {"consecutive_breaches": 5, "current_ms": 150.0}
    tuner = RunbookTuner(metrics)
    recs = tuner.generate_recommendations()
    assert any(r.id == "TUNE-LAT-001" for r in recs)

    # Budget pressure case
    metrics_cost = {"budget_utilization": 0.9}
    tuner_cost = RunbookTuner(metrics_cost)
    recs_cost = tuner_cost.generate_recommendations()
    assert any(r.id == "TUNE-COST-001" for r in recs_cost)
