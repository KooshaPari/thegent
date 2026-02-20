"""Unit tests for ParetoRouter and RouteCandidate.

Traces to: FR-ROUTER-001 (Pareto-optimal route selection)
"""

import pytest

from thegent.routing import ParetoRouter, RouteCandidate

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _candidate(model: str, cost: float, quality: float, provider: str = "test") -> RouteCandidate:
    return RouteCandidate(model=model, provider=provider, cost_per_1k=cost, quality_score=quality)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRouteCandidateDataclass:
    """RouteCandidate is a plain dataclass with the required fields."""

    def test_fields_accessible(self) -> None:
        c = _candidate("gpt-4o", cost=0.03, quality=0.85)
        assert c.model == "gpt-4o"
        assert c.provider == "test"
        assert c.cost_per_1k == 0.03
        assert c.quality_score == 0.85

    def test_default_provider_not_required(self) -> None:
        c = RouteCandidate(model="m", provider="p", cost_per_1k=0.01, quality_score=0.5)
        assert c.provider == "p"


class TestParetoRouterSingleCandidate:
    """With only one candidate, it is always selected."""

    def test_single_returned(self) -> None:
        router = ParetoRouter()
        c = _candidate("only", cost=1.0, quality=0.9)
        assert router.select([c]) is c

    def test_single_zero_cost(self) -> None:
        router = ParetoRouter()
        c = _candidate("free-model", cost=0.0, quality=0.7)
        assert router.select([c]) is c


class TestParetoRouterEmptyCandidates:
    """Empty candidate list raises ValueError."""

    def test_empty_raises(self) -> None:
        router = ParetoRouter()
        with pytest.raises(ValueError, match="non-empty"):
            router.select([])


class TestParetoRouterDominatedRoutesFiltered:
    """Dominated candidates are excluded from the frontier."""

    def test_dominated_not_selected(self) -> None:
        """cheap-good dominates expensive-bad: same quality, lower cost."""
        router = ParetoRouter()
        expensive_bad = _candidate("expensive-bad", cost=2.0, quality=0.6)
        cheap_good = _candidate("cheap-good", cost=0.5, quality=0.8)
        # cheap-good has lower cost AND higher quality → dominates expensive-bad
        result = router.select([expensive_bad, cheap_good])
        assert result is cheap_good

    def test_all_but_one_dominated(self) -> None:
        """One clearly superior model dominates all others."""
        router = ParetoRouter()
        best = _candidate("best", cost=0.1, quality=0.99)
        mid = _candidate("mid", cost=0.5, quality=0.80)
        worst = _candidate("worst", cost=1.0, quality=0.50)
        result = router.select([worst, mid, best])
        assert result is best

    def test_frontier_excludes_strictly_dominated(self) -> None:
        """Explicitly verify that _pareto_frontier omits dominated candidates."""
        router = ParetoRouter()
        dominated = _candidate("dominated", cost=1.0, quality=0.5)
        dominant = _candidate("dominant", cost=0.5, quality=0.9)
        unrelated = _candidate("unrelated", cost=0.4, quality=0.6)
        # dominant dominates dominated (better on both)
        # unrelated is on the frontier (lower cost than dominant, lower quality)
        frontier = router._pareto_frontier([dominated, dominant, unrelated])
        frontier_models = {c.model for c in frontier}
        assert "dominated" not in frontier_models
        assert "dominant" in frontier_models
        assert "unrelated" in frontier_models


class TestParetoRouterFrontierSelection:
    """Among non-dominated candidates, select highest quality/cost ratio."""

    def test_highest_ratio_selected(self) -> None:
        """Two non-dominated candidates: the one with better quality/cost wins."""
        router = ParetoRouter()
        # Neither dominates the other (a has higher quality, b has lower cost)
        a = _candidate("a", cost=2.0, quality=0.9)   # ratio = 0.45
        b = _candidate("b", cost=0.5, quality=0.6)   # ratio = 1.20
        result = router.select([a, b])
        # b has higher ratio (0.6/0.5 = 1.2 vs 0.9/2.0 = 0.45)
        assert result is b

    def test_pareto_frontier_with_trade_off(self) -> None:
        """Classic three-way trade-off: low-cost-low-qual, mid, high-cost-high-qual."""
        router = ParetoRouter()
        cheap = _candidate("cheap", cost=0.1, quality=0.6)    # ratio = 6.0
        mid = _candidate("mid", cost=0.5, quality=0.8)        # ratio = 1.6
        premium = _candidate("premium", cost=2.0, quality=0.95)  # ratio = 0.475
        # None dominates any other (each trades cost for quality)
        result = router.select([cheap, mid, premium])
        # cheap has the best ratio (0.6/0.1 = 6.0)
        assert result is cheap

    def test_equal_quality_lower_cost_wins(self) -> None:
        """Equal quality: lower cost gives higher ratio."""
        router = ParetoRouter()
        expensive = _candidate("expensive", cost=1.0, quality=0.8)
        cheap = _candidate("cheap", cost=0.2, quality=0.8)
        # cheap dominates expensive (same quality, lower cost)
        result = router.select([expensive, cheap])
        assert result is cheap


class TestParetoRouterZeroCostFallback:
    """When all candidates have cost_per_1k == 0, select highest quality_score."""

    def test_all_zero_cost_highest_quality_wins(self) -> None:
        router = ParetoRouter()
        a = _candidate("a", cost=0.0, quality=0.7)
        b = _candidate("b", cost=0.0, quality=0.9)
        c = _candidate("c", cost=0.0, quality=0.5)
        result = router.select([a, b, c])
        assert result is b

    def test_single_zero_cost_returned(self) -> None:
        router = ParetoRouter()
        only = _candidate("free", cost=0.0, quality=0.85)
        assert router.select([only]) is only

    def test_mixed_zero_and_nonzero_cost(self) -> None:
        """Zero-cost candidate is treated as infinite ratio → wins over any positive-cost."""
        router = ParetoRouter()
        free = _candidate("free", cost=0.0, quality=0.6)
        paid = _candidate("paid", cost=0.01, quality=0.9)
        # free has quality=0.6; paid has quality=0.9 → paid dominates free? No:
        # paid has higher quality AND higher cost, so it does NOT dominate free.
        # Both are on the frontier. free has ratio=inf → free wins.
        result = router.select([free, paid])
        assert result is free


class TestParetoRouterIntegration:
    """End-to-end routing scenarios matching real model catalogues."""

    def test_realistic_model_pool(self) -> None:
        """Realistic mix: one model should emerge as clearly best value."""
        router = ParetoRouter()
        candidates = [
            RouteCandidate("gpt-5.3-codex", "copilot", 0.30, 0.82),
            RouteCandidate("claude-haiku-4.5", "claude", 0.025, 0.75),
            RouteCandidate("claude-sonnet-4.6", "claude", 0.30, 0.88),
            RouteCandidate("gemini-3-flash", "gemini", 0.00, 0.78),
            RouteCandidate("claude-opus-4.6", "claude", 2.50, 0.95),
        ]
        result = router.select(candidates)
        # gemini-3-flash is free (cost=0) → infinite ratio → must win
        assert result.model == "gemini-3-flash"

    def test_no_free_tier_best_ratio_wins(self) -> None:
        """Without free-tier model, claude-haiku wins on ratio."""
        router = ParetoRouter()
        candidates = [
            RouteCandidate("gpt-5.3-codex", "copilot", 0.30, 0.82),
            RouteCandidate("claude-haiku-4.5", "claude", 0.025, 0.75),
            RouteCandidate("claude-sonnet-4.6", "claude", 0.30, 0.88),
            RouteCandidate("claude-opus-4.6", "claude", 2.50, 0.95),
        ]
        result = router.select(candidates)
        # claude-haiku ratio = 0.75/0.025 = 30.0 (highest)
        # gpt-5.3-codex ratio = 0.82/0.30 ≈ 2.73
        # claude-sonnet ratio = 0.88/0.30 ≈ 2.93
        # claude-opus ratio = 0.95/2.50 = 0.38
        assert result.model == "claude-haiku-4.5"
